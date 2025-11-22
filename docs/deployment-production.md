# Guía de Despliegue en Producción

Esta guía describe cómo desplegar el adaptador de WhatsApp en un servidor de producción.

## Requisitos del Servidor

- **Sistema Operativo:** Linux (Debian/Ubuntu recomendado)
- **Python:** 3.11 o superior
- **Usuario del servicio:** `terranote` (usuario que ejecutará el servicio, sin acceso SSH)
- **Usuario de acceso:** El usuario con acceso SSH (ej: `angoca`)
- **Permisos:** Acceso SSH al servidor y permisos sudo
- **Puerto:** 8000 (o el que configures) debe estar disponible y accesible desde Internet
- **Repositorio:** Debe estar en `/home/terranote/terranote-adapter-whatsapp`

## Paso 1: Preparar el Servidor

### 1.1. Conectarse al servidor

```bash
ssh angoca@192.168.0.7
# O el usuario que tengas configurado para SSH
```

### 1.2. Verificar Python

```bash
python3 --version
# Debe ser 3.11 o superior
```

Si no está instalado Python 3.11+, instálalo:

```bash
# En Debian/Ubuntu
sudo apt update
sudo apt install -y python3 python3-venv python3-pip
```

### 1.3. Instalar dependencias del sistema (si es necesario)

```bash
sudo apt install -y rsync git
```

## Paso 2: Clonar o Transferir el Repositorio

### Opción A: Clonar desde Git (recomendado)

```bash
cd ~
git clone https://github.com/Terranote/terranote-adapter-whatsapp.git
cd terranote-adapter-whatsapp
```

### Opción B: Transferir desde tu máquina local

Desde tu máquina local (si el repositorio no está ya en el servidor):

```bash
# Desde el directorio del proyecto
# Nota: El repositorio debe estar en /home/terranote/terranote-adapter-whatsapp
# Puedes transferirlo temporalmente a tu usuario y luego moverlo con sudo
rsync -av --exclude='.git' --exclude='.venv' --exclude='__pycache__' \
  ./ angoca@192.168.0.7:~/terranote-adapter-whatsapp-temp/

# Luego en el servidor, moverlo al home de terranote:
# sudo mv ~/terranote-adapter-whatsapp-temp /home/terranote/terranote-adapter-whatsapp
# sudo chown -R terranote:terranote /home/terranote/terranote-adapter-whatsapp
```

## Paso 3: Configurar el Repositorio

Como el repositorio está en el home de `terranote` y no tienes acceso SSH directo a ese usuario, necesitas usar `sudo` para ejecutar el script de configuración:

```bash
# Acceder al directorio del repositorio (está en /home/terranote)
cd /home/terranote/terranote-adapter-whatsapp

# Opción 1: Usar el script automatizado (recomendado)
sudo ./deploy/install-on-server.sh

# Opción 2: Configurar manualmente
sudo chmod +x deploy/setup-local.sh
sudo -u terranote ./deploy/setup-local.sh
```

El script configurará el entorno virtual e instalará las dependencias directamente en el repositorio, sin copiar a otra ubicación.

El script:
- Creará el directorio de instalación
- Copiará los archivos del proyecto
- Creará un entorno virtual
- Instalará las dependencias
- Creará el archivo `.env` desde el template

## Paso 4: Configurar Variables de Entorno

Edita el archivo `.env` con tus valores de producción:

```bash
# Opción 1: Con sudo y nano
sudo nano /home/terranote/terranote-adapter-whatsapp/.env

# Opción 2: Cambiar propiedad temporalmente para editar
sudo chown $USER:$USER /home/terranote/terranote-adapter-whatsapp/.env
nano /home/terranote/terranote-adapter-whatsapp/.env
sudo chown terranote:terranote /home/terranote/terranote-adapter-whatsapp/.env
```

Configura al menos estas variables:

```env
APP_ENV=production
CORE_API_BASE_URL=https://tu-core-api.com
CORE_API_TIMEOUT_SECONDS=5.0
CORE_API_TOKEN=tu-token-si-es-necesario

WHATSAPP_VERIFY_TOKEN=tu-token-de-verificacion
WHATSAPP_ACCESS_TOKEN=tu-access-token-de-facebook
WHATSAPP_PHONE_NUMBER_ID=tu-phone-number-id
WHATSAPP_API_BASE_URL=https://graph.facebook.com/v19.0

NOTIFIER_SECRET_TOKEN=tu-secret-token-opcional
```

**Importante:** Asegúrate de que el archivo `.env` tenga permisos restrictivos:

```bash
sudo chmod 600 /opt/terranote-adapter-whatsapp/.env
sudo chown terranote:terranote /opt/terranote-adapter-whatsapp/.env
```

## Paso 5: Configurar el Servicio Systemd

### 5.1. Copiar el archivo de servicio

```bash
sudo cp /opt/terranote-adapter-whatsapp/deploy/terranote-adapter-whatsapp.service /etc/systemd/system/
```

### 5.2. Verificar el servicio

El servicio está configurado para ejecutarse desde `/home/terranote/terranote-adapter-whatsapp`. Si el repositorio está en otra ubicación, edita el archivo:

```bash
sudo nano /etc/systemd/system/terranote-adapter-whatsapp.service
```

Ajusta las rutas:
- `WorkingDirectory`
- `ExecStart`
- `ReadWritePaths`

### 5.3. Recargar systemd y habilitar el servicio

```bash
sudo systemctl daemon-reload
sudo systemctl enable terranote-adapter-whatsapp
sudo systemctl start terranote-adapter-whatsapp
```

### 5.4. Verificar que el servicio está corriendo

```bash
sudo systemctl status terranote-adapter-whatsapp
```

Deberías ver algo como:

```
● terranote-adapter-whatsapp.service - Terranote WhatsApp Adapter
     Loaded: loaded (/etc/systemd/system/terranote-adapter-whatsapp.service; enabled)
     Active: active (running) since ...
```

### 5.5. Ver los logs

```bash
# Ver logs en tiempo real
sudo journalctl -u terranote-adapter-whatsapp -f

# Ver últimos logs
sudo journalctl -u terranote-adapter-whatsapp -n 50
```

## Paso 6: Configurar el Firewall

Si tienes un firewall activo, abre el puerto 8000:

```bash
# UFW (Ubuntu)
sudo ufw allow 8000/tcp

# firewalld (CentOS/RHEL)
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --reload

# iptables (genérico)
sudo iptables -A INPUT -p tcp --dport 8000 -j ACCEPT
```

## Paso 7: Configurar Reverse Proxy (Recomendado)

Para producción, es recomendable usar un reverse proxy como Nginx o Traefik para:
- Terminación SSL/TLS
- Balanceo de carga
- Rate limiting
- Logging centralizado

### Ejemplo con Nginx

Crea `/etc/nginx/sites-available/terranote-adapter-whatsapp`:

```nginx
server {
    listen 80;
    server_name tu-dominio.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Habilita el sitio:

```bash
sudo ln -s /etc/nginx/sites-available/terranote-adapter-whatsapp /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

Para SSL, usa Let's Encrypt:

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d tu-dominio.com
```

## Paso 8: Verificar la Instalación

### 8.1. Health Check

```bash
curl http://localhost:8000/health
```

Debería responder: `{"status":"ok"}`

### 8.2. Verificar desde fuera del servidor

```bash
curl http://192.168.0.7:8000/health
```

O si configuraste un dominio:

```bash
curl https://tu-dominio.com/health
```

## Paso 9: Configurar el Webhook en Facebook

1. Ve a [Facebook Developers](https://developers.facebook.com/)
2. Selecciona tu app
3. Ve a WhatsApp → Configuración → Webhooks
4. Configura la URL: `https://tu-dominio.com/webhook` (o `http://192.168.0.7:8000/webhook` si no tienes dominio)
5. Usa el mismo `WHATSAPP_VERIFY_TOKEN` que configuraste en `.env`
6. Suscríbete a `messages`

## Comandos Útiles

### Gestión del Servicio

```bash
# Iniciar
sudo systemctl start terranote-adapter-whatsapp

# Detener
sudo systemctl stop terranote-adapter-whatsapp

# Reiniciar
sudo systemctl restart terranote-adapter-whatsapp

# Ver estado
sudo systemctl status terranote-adapter-whatsapp

# Ver logs
sudo journalctl -u terranote-adapter-whatsapp -f
```

### Actualizar la Aplicación

```bash
# 1. Detener el servicio
sudo systemctl stop terranote-adapter-whatsapp

# 2. Actualizar el código (si usas git)
cd /opt/terranote-adapter-whatsapp
git pull

# O transferir nuevos archivos con rsync

# 3. Actualizar dependencias
source .venv/bin/activate
pip install -e . --no-dev

# 4. Reiniciar el servicio
sudo systemctl start terranote-adapter-whatsapp
```

### Verificar Configuración

```bash
# Activar el entorno virtual y probar
cd /opt/terranote-adapter-whatsapp
source .venv/bin/activate
python3 -c "from terranote_adapter_whatsapp.settings import get_settings; print(get_settings())"
```

## Solución de Problemas

### El servicio no inicia

1. Verifica los logs:
   ```bash
   sudo journalctl -u terranote-adapter-whatsapp -n 100
   ```

2. Verifica que el archivo `.env` existe y tiene los valores correctos:
   ```bash
   sudo cat /opt/terranote-adapter-whatsapp/.env
   ```

3. Verifica permisos:
   ```bash
   ls -la /opt/terranote-adapter-whatsapp/.env
   ```

### El servicio se reinicia constantemente

1. Revisa los logs para ver el error
2. Verifica que todas las variables de entorno estén configuradas
3. Prueba ejecutar manualmente:
   ```bash
   cd /opt/terranote-adapter-whatsapp
   source .venv/bin/activate
   uvicorn terranote_adapter_whatsapp.main:app --host 0.0.0.0 --port 8000
   ```

### El webhook no recibe mensajes

1. Verifica que el servicio esté corriendo
2. Verifica que el puerto esté abierto y accesible desde Internet
3. Revisa los logs del servicio
4. Verifica la configuración del webhook en Facebook Developers

## Seguridad

- ✅ Nunca subas el archivo `.env` al repositorio
- ✅ Usa tokens seguros y únicos
- ✅ Configura SSL/TLS en producción
- ✅ Limita el acceso al servidor con firewall
- ✅ Mantén el sistema y las dependencias actualizadas
- ✅ Revisa los logs regularmente

## Monitoreo

Considera configurar:
- **Logs centralizados:** Envía los logs a un sistema centralizado (ELK, Loki, etc.)
- **Métricas:** Expone métricas de Prometheus si es necesario
- **Alertas:** Configura alertas para cuando el servicio falle
- **Backups:** Haz backup del archivo `.env` de forma segura

