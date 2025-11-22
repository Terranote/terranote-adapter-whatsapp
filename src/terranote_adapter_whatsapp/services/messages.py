"""Multi-language message templates for WhatsApp."""

from typing import Literal

Language = Literal["es", "en"]


class MessageTemplates:
    """Message templates in multiple languages."""

    MESSAGES = {
        "es": {
            "welcome": {
                "body": "¡Hola! 👋 Bienvenido a *Terranote*.\n\n"
                "Puedes crear notas enviándome un mensaje de texto y luego tu ubicación.\n\n"
                "¿Cómo puedo ayudarte?",
                "quick_replies": [
                    {"id": "cmd_crear", "title": "Crear nota"},
                    {"id": "cmd_ayuda", "title": "Ver ayuda"},
                    {"id": "cmd_info", "title": "Más info"},
                ],
            },
            "help": {
                "body": "📝 *Terranote - Comandos disponibles:*\n\n"
                "• Envía un *mensaje de texto* seguido de tu *ubicación* para crear una nota\n"
                "• `/ayuda` o `/help` - Mostrar esta ayuda\n"
                "• `/info` - Información sobre Terranote\n\n"
                "*Ejemplo:*\n"
                "1. Envía: \"Hoy visité el parque\"\n"
                "2. Comparte tu ubicación\n"
                "3. ¡Listo! Tu nota será creada en OpenStreetMap",
                "quick_replies": [
                    {"id": "cmd_crear", "title": "Crear nota"},
                    {"id": "cmd_info", "title": "Más info"},
                ],
            },
            "info": {
                "body": "ℹ️ *Sobre Terranote*\n\n"
                "Terranote te permite crear notas en OpenStreetMap directamente desde WhatsApp.\n\n"
                "*Cómo funciona:*\n"
                "1. Envía un mensaje describiendo lo que quieres reportar\n"
                "2. Comparte tu ubicación\n"
                "3. Tu nota se creará automáticamente en OSM\n\n"
                "Para más información, visita: https://terranote.org",
            },
        },
        "en": {
            "welcome": {
                "body": "Hello! 👋 Welcome to *Terranote*.\n\n"
                "You can create notes by sending me a text message and then your location.\n\n"
                "How can I help you?",
                "quick_replies": [
                    {"id": "cmd_create", "title": "Create note"},
                    {"id": "cmd_help", "title": "Help"},
                    {"id": "cmd_info", "title": "More info"},
                ],
            },
            "help": {
                "body": "📝 *Terranote - Available commands:*\n\n"
                "• Send a *text message* followed by your *location* to create a note\n"
                "• `/help` or `/ayuda` - Show this help\n"
                "• `/info` - Information about Terranote\n\n"
                "*Example:*\n"
                "1. Send: \"Today I visited the park\"\n"
                "2. Share your location\n"
                "3. Done! Your note will be created in OpenStreetMap",
                "quick_replies": [
                    {"id": "cmd_create", "title": "Create note"},
                    {"id": "cmd_info", "title": "More info"},
                ],
            },
            "info": {
                "body": "ℹ️ *About Terranote*\n\n"
                "Terranote allows you to create notes in OpenStreetMap directly from WhatsApp.\n\n"
                "*How it works:*\n"
                "1. Send a message describing what you want to report\n"
                "2. Share your location\n"
                "3. Your note will be automatically created in OSM\n\n"
                "For more information, visit: https://terranote.org",
            },
        },
    }

    @classmethod
    def get_welcome_message(cls, lang: Language = "es") -> dict:
        """Get welcome message template for the specified language."""
        return cls.MESSAGES.get(lang, cls.MESSAGES["es"])["welcome"]

    @classmethod
    def get_help_message(cls, lang: Language = "es") -> dict:
        """Get help message template for the specified language."""
        return cls.MESSAGES.get(lang, cls.MESSAGES["es"])["help"]

    @classmethod
    def get_info_message(cls, lang: Language = "es") -> dict:
        """Get info message template for the specified language."""
        return cls.MESSAGES.get(lang, cls.MESSAGES["es"])["info"]

    @classmethod
    def detect_language(cls, text: str) -> Language:
        """Detect language from text (simple heuristic)."""
        text_lower = text.lower()
        # Simple detection based on common words
        english_words = {"hello", "hi", "help", "create", "note", "the", "and", "is"}
        spanish_words = {"hola", "ayuda", "crear", "nota", "el", "la", "y", "es"}

        english_count = sum(1 for word in english_words if word in text_lower)
        spanish_count = sum(1 for word in spanish_words if word in text_lower)

        return "en" if english_count > spanish_count else "es"

