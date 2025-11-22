import httpx
import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status

from ..clients.core import TerranoteCoreClient
from ..clients.whatsapp import WhatsAppClient
from ..schemas.webhook import WebhookEvent, WebhookVerificationResponse
from ..services.message_processor import MessageProcessor
from ..services.messages import MessageTemplates
from ..settings import Settings, get_settings

router = APIRouter(prefix="/webhook", tags=["whatsapp"])
logger = structlog.get_logger(__name__)

# Track seen users (in production, use Redis or database)
_seen_users: set[str] = set()


@router.get(
    "",
    summary="WhatsApp webhook verification handshake",
)
async def verify_webhook(
    hub_mode: str = Query(alias="hub.mode"),
    hub_challenge: str = Query(alias="hub.challenge"),
    hub_verify_token: str = Query(alias="hub.verify_token"),
    settings: Settings = Depends(get_settings),
) -> Response:
    """Respond to the Facebook webhook verification challenge.
    
    Facebook expects the challenge to be returned as plain text, not JSON.
    """
    if hub_mode != "subscribe" or hub_verify_token != settings.whatsapp_verify_token:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Verification failed")

    # Facebook expects plain text response, not JSON
    return Response(content=hub_challenge, media_type="text/plain")


@router.post("", status_code=status.HTTP_202_ACCEPTED, summary="Process WhatsApp inbound events")
async def receive_webhook(
    event: WebhookEvent,
    request: Request,
    settings: Settings = Depends(get_settings),
) -> dict[str, int | str]:
    """Handle incoming WhatsApp events from Meta."""
    # Log when webhook is received
    logger.info("webhook_received", event_object=event.object, entries_count=len(event.entry))
    
    processor = MessageProcessor()
    core_client = TerranoteCoreClient(settings)
    whatsapp_client = WhatsAppClient(settings)

    processed = 0
    for entry in event.entry:
        for change in entry.changes:
            logger.info("processing_change", field=change.field, messages_count=len(change.value.messages))
            for message in change.value.messages:
                user_id = message.from_
                logger.info("processing_message", message_id=message.id, message_type=message.type, from_user=user_id)

                # Check if user is new and send welcome message
                if user_id not in _seen_users:
                    _seen_users.add(user_id)
                    # Detect language from message if available
                    lang = "es"  # Default to Spanish
                    if message.type == "text" and message.text:
                        lang = MessageTemplates.detect_language(message.text.body)
                    
                    # Send welcome message
                    try:
                        welcome_msg = MessageTemplates.get_welcome_message(lang)
                        await whatsapp_client.send_text_message_with_quick_replies(
                            user_id, welcome_msg["body"], welcome_msg["quick_replies"]
                        )
                        logger.info("welcome_message_sent", user_id=user_id, lang=lang)
                    except Exception as exc:
                        logger.error("failed_to_send_welcome", user_id=user_id, error=str(exc))

                # Check if message is a command
                if message.type == "text" and message.text:
                    text = message.text.body
                    command = processor.get_command(text)
                    
                    if command:
                        # Detect language for command response
                        lang = MessageTemplates.detect_language(text)
                        
                        try:
                            if command in ("ayuda", "help"):
                                help_msg = MessageTemplates.get_help_message(lang)
                                await whatsapp_client.send_text_message_with_quick_replies(
                                    user_id, help_msg["body"], help_msg["quick_replies"]
                                )
                                logger.info("help_message_sent", user_id=user_id, lang=lang)
                                processed += 1
                                continue  # Don't send to core
                            
                            elif command in ("info", "informacion", "information"):
                                info_msg = MessageTemplates.get_info_message(lang)
                                await whatsapp_client.send_text_message(user_id, info_msg["body"])
                                logger.info("info_message_sent", user_id=user_id, lang=lang)
                                processed += 1
                                continue  # Don't send to core
                            
                            # Other commands can be handled here
                            else:
                                logger.info("unknown_command", user_id=user_id, command=command)
                                # Continue processing as normal message
                        except Exception as exc:
                            logger.error("failed_to_send_command_response", user_id=user_id, command=command, error=str(exc))
                            # Continue processing as normal message

                # Process normal message (text or location)
                try:
                    interaction = processor.to_interaction(user_id=user_id, message=message)
                    logger.info("interaction_created", user_id=interaction.user_id, channel=interaction.channel)
                except ValueError as exc:
                    logger.warning(
                        "unsupported_message",
                        message_type=message.type,
                        message_id=message.id,
                        error=str(exc),
                    )
                    continue

                try:
                    logger.info("sending_to_core", user_id=interaction.user_id, core_url=str(core_client._base_url))
                    response = await core_client.send_interaction(interaction)
                    response.raise_for_status()
                    logger.info("core_response_received", status_code=response.status_code, user_id=interaction.user_id)
                except httpx.HTTPStatusError as exc:
                    logger.error(
                        "core_rejected_interaction",
                        status_code=exc.response.status_code,
                        body=exc.response.text,
                        user_id=interaction.user_id,
                    )
                    raise HTTPException(
                        status_code=status.HTTP_502_BAD_GATEWAY,
                        detail="core_error",
                    ) from exc
                except httpx.HTTPError as exc:
                    logger.error(
                        "core_unreachable",
                        error=str(exc),
                        user_id=interaction.user_id,
                    )
                    raise HTTPException(
                        status_code=status.HTTP_502_BAD_GATEWAY,
                        detail="core_unreachable",
                    ) from exc

                processed += 1
                logger.info(
                    "interaction_forwarded",
                    user_id=interaction.user_id,
                    message_id=message.id,
                )

    return {"status": "accepted", "processed": processed}
