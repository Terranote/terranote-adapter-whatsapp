# Configuración de Cloudflared para el Webhook

Esta guía explica cómo configurar cloudflared para exponer tu servidor de WhatsApp a Internet.

## Paso 1: Instalar Cloudflared

### En Linux (Debian/Ubuntu):
```bash
# Descargar e instalar
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb -o cloudflared.deb
sudo dpkg -i cloudflared.deb
```

### En macOS:
```bash
brew install cloudflared
```

### En Windows:
Descarga desde: https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/

## Paso 2: Iniciar Cloudflared

Una vez que tu servidor esté corriendo en el puerto 3001:

```bash
cloudflared tunnel --url http://localhost:3001
```

Verás una salida como:
```
+--------------------------------------------------------------------------------------------+
|  Your quick Tunnel has been created! Visit it at (it may take some time to be reachable):  |
|  https://abc123-def456-ghi789.trycloudflare.com                                           |
+--------------------------------------------------------------------------------------------+
```

## Paso 3: Copiar la URL

Copia la URL HTTPS que te da cloudflared (ejemplo: `https://abc123-def456-ghi789.trycloudflare.com`)

## Paso 4: Configurar el Webhook en Facebook

Usa esta URL en Facebook Developers:

**Callback URL:** `https://tu-url-cloudflared/webhook`

Ejemplo completo:
```
https://abc123-def456-ghi789.trycloudflare.com/webhook
```

## Paso 5: Verificar

1. **Verifica que tu servidor local responda:**
   ```bash
   curl http://localhost:3001/health
   ```
   Debería responder: `{"status":"ok"}`

2. **Verifica a través de cloudflared:**
   ```bash
   curl https://tu-url-cloudflared/health
   ```
   También debería responder: `{"status":"ok"}`

3. **Configura el webhook en Facebook** con la URL completa + `/webhook`

## Notas Importantes

- ⚠️ **La URL de cloudflared cambia cada vez que reinicias el túnel**
  - Si reinicias cloudflared, obtendrás una nueva URL
  - Deberás actualizar el webhook en Facebook con la nueva URL

- ⚠️ **Para producción, considera usar un túnel permanente de Cloudflare**
  - Los túneles temporales son solo para desarrollo
  - Para producción, configura un túnel permanente con un dominio fijo

- ✅ **Mantén cloudflared corriendo mientras uses el webhook**
  - Si cierras cloudflared, el webhook dejará de funcionar
  - Considera ejecutarlo como servicio o en una terminal separada

## Ejecutar Cloudflared como Servicio (Opcional)

Para que cloudflared se ejecute automáticamente:

```bash
# Crear servicio systemd
sudo nano /etc/systemd/system/cloudflared-tunnel.service
```

Contenido del servicio:
```ini
[Unit]
Description=Cloudflared tunnel for WhatsApp adapter
After=network.target

[Service]
Type=simple
User=terranote
ExecStart=/usr/local/bin/cloudflared tunnel --url http://localhost:3001
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Activar el servicio:
```bash
sudo systemctl daemon-reload
sudo systemctl enable cloudflared-tunnel
sudo systemctl start cloudflared-tunnel
```

