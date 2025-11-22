# Configuración de DNS en Cloudflare para WhatsApp

Esta guía explica cómo configurar un dominio personalizado en Cloudflare para usar con WhatsApp Business API.

## ¿Qué es esto?

Facebook/Meta te proporciona un identificador único (target) que debes configurar como registro CNAME en tu DNS de Cloudflare. Esto te permite usar tu propio dominio en lugar de URLs temporales.

## Paso 1: Obtener el Target de Facebook

Facebook te proporciona:
- **Tipo:** CNAME
- **Name:** `terranote-wa` (o el subdominio que elijas)
- **Target:** `1b718247-fe2d-4391-84c0-819c1501e6c2` (el identificador único de Facebook)

## Paso 2: Configurar el Registro CNAME en Cloudflare

1. **Accede a Cloudflare:**
   - Ve a [https://dash.cloudflare.com/](https://dash.cloudflare.com/)
   - Inicia sesión con tu cuenta

2. **Selecciona tu dominio:**
   - Elige el dominio donde quieres configurar el subdominio
   - Ve a la sección **"DNS"** → **"Records"**

3. **Agregar un nuevo registro:**
   - Haz clic en **"Add record"** (Agregar registro)

4. **Configura el registro CNAME:**
   - **Type:** Selecciona `CNAME`
   - **Name:** `terranote-wa` (o el nombre que prefieras)
     - Esto creará el subdominio `terranote-wa.tu-dominio.com`
   - **Target:** `1b718247-fe2d-4391-84c0-819c1501e6c2`
     - ⚠️ **IMPORTANTE:** Copia exactamente el target que te dio Facebook
   - **Proxy status:** 
     - ❌ **Desactiva el proxy** (nube gris - DNS only) - Facebook requiere DNS only, no Proxied
   - **TTL:** Deja en "Auto" o selecciona un valor apropiado

5. **Comentario (opcional):**
   - Puedes agregar un comentario: "Terranote for WhatsApp adapter"

6. **Guardar:**
   - Haz clic en **"Save"** (Guardar)

## Paso 3: Verificar la Configuración

Después de guardar, el registro debería aparecer en tu lista de DNS records:

```
Type    Name         Content/Target                                    Proxy
CNAME   terranote-wa 1b718247-fe2d-4391-84c0-819c1501e6c2             DNS only
```

## Paso 4: Usar el Dominio en Facebook

Una vez configurado el DNS (puede tardar unos minutos en propagarse):

1. **En Facebook Developers:**
   - Ve a tu app → WhatsApp → Configuration
   - En la sección de webhooks, usa tu dominio personalizado:
   - **Callback URL:** `https://terranote-wa.tu-dominio.com/webhook`
     - Reemplaza `tu-dominio.com` con tu dominio real

2. **Verify token:**
   - Usa el mismo token que tienes en tu `.env`: `PXfiE_5U2l7OsfJDa_M-xS7m7XxeXbYZQ3k5JBnbZT8`

## Paso 5: Configurar Cloudflared con Dominio Personalizado (Opcional)

Si quieres usar cloudflared con tu dominio personalizado en lugar de la URL temporal:

### Opción A: Túnel Permanente de Cloudflare

1. **Crear un túnel permanente:**
   ```bash
   cloudflared tunnel create terranote-whatsapp
   ```

2. **Configurar el túnel:**
   ```bash
   cloudflared tunnel route dns terranote-whatsapp terranote-wa.tu-dominio.com
   ```

3. **Crear archivo de configuración:**
   ```bash
   nano ~/.cloudflared/config.yml
   ```

   Contenido:
   ```yaml
   tunnel: <tunnel-id>
   credentials-file: /home/terranote/.cloudflared/<tunnel-id>.json
   
   ingress:
     - hostname: terranote-wa.tu-dominio.com
       service: http://localhost:3001
     - service: http_status:404
   ```

4. **Ejecutar el túnel:**
   ```bash
   cloudflared tunnel run terranote-whatsapp
   ```

### Opción B: Usar Solo el CNAME de Facebook (Más Simple)

Si Facebook ya te dio el target `1b718247-fe2d-4391-84c0-819c1501e6c2`, puedes simplemente:

1. Configurar el CNAME en Cloudflare (como se explica arriba)
2. Usar directamente `https://terranote-wa.tu-dominio.com/webhook` en Facebook
3. **No necesitas cloudflared** si Facebook maneja el routing directamente

## Verificación

### Verificar el DNS:

```bash
# Verifica que el CNAME esté configurado correctamente
dig terranote-wa.tu-dominio.com CNAME

# O con nslookup
nslookup terranote-wa.tu-dominio.com
```

Deberías ver el target de Facebook en la respuesta.

### Verificar el Webhook:

Una vez configurado todo:

```bash
# Verifica que el webhook responda
curl https://terranote-wa.tu-dominio.com/webhook?hub.mode=subscribe&hub.challenge=test&hub.verify_token=PXfiE_5U2l7OsfJDa_M-xS7m7XxeXbYZQ3k5JBnbZT8
```

## Resumen de Valores

| Valor | Dónde está | Ejemplo |
|-------|------------|---------|
| **Tipo DNS** | Cloudflare | CNAME |
| **Name** | Cloudflare | `terranote-wa` |
| **Target** | Facebook/Cloudflare | `1b718247-fe2d-4391-84c0-819c1501e6c2` |
| **Proxy** | Cloudflare | Activado (Proxied) |
| **URL del Webhook** | Facebook | `https://terranote-wa.tu-dominio.com/webhook` |
| **Verify Token** | Facebook y `.env` | `PXfiE_5U2l7OsfJDa_M-xS7m7XxeXbYZQ3k5JBnbZT8` |

## Notas Importantes

- ⚠️ **La propagación DNS puede tardar unos minutos** (hasta 24 horas en casos extremos, pero generalmente es rápido)
- ⚠️ **El proxy de Cloudflare debe estar DESACTIVADO** (DNS only) - Facebook requiere acceso directo al target
- 🔒 **Asegúrate de que el verify token sea exactamente el mismo** en Facebook y en tu `.env`
- 📝 **El subdominio `terranote-wa`** puede ser cualquier nombre que elijas, pero debe coincidir en Cloudflare y Facebook

## Solución de Problemas

### El DNS no resuelve

1. Verifica que el registro CNAME esté guardado en Cloudflare
2. Espera unos minutos para la propagación
3. Verifica con `dig` o `nslookup`

### Facebook no puede verificar el webhook

1. Verifica que el DNS esté propagado
2. Verifica que el verify token coincida exactamente
3. Asegúrate de que tu servidor esté corriendo en el puerto 3001
4. Verifica que el endpoint `/webhook` responda correctamente

### Error 404 en el webhook

1. Verifica que tu servidor esté corriendo
2. Verifica que el puerto sea 3001
3. Prueba el health check: `curl https://terranote-wa.tu-dominio.com/health`

