# Scripts de Despliegue

Este directorio contiene los scripts y archivos necesarios para desplegar el adaptador de WhatsApp en producción.

## Archivos

- **`production-install.sh`**: Script de instalación automatizada en el servidor
- **`terranote-adapter-whatsapp.service`**: Archivo de servicio systemd para ejecutar como servicio del sistema

## Uso Rápido

### En el servidor (192.168.0.7)

```bash
# 1. Conectarse al servidor (con el usuario que tenga SSH, ej: angoca)
ssh angoca@192.168.0.7

# 2. Ir al repositorio (está en /home/terranote/terranote-adapter-whatsapp)
cd /home/terranote/terranote-adapter-whatsapp

# 3. Ejecutar el script de configuración (con sudo)
sudo ./deploy/install-on-server.sh

# O manualmente:
# sudo chmod +x deploy/setup-local.sh
# sudo -u terranote ./deploy/setup-local.sh

# 4. Configurar .env
sudo nano /home/terranote/terranote-adapter-whatsapp/.env
# Edita con tus valores de producción
sudo chown terranote:terranote /home/terranote/terranote-adapter-whatsapp/.env

# 5. Configurar y activar el servicio
sudo cp deploy/terranote-adapter-whatsapp.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable terranote-adapter-whatsapp
sudo systemctl start terranote-adapter-whatsapp

# 6. Verificar
sudo systemctl status terranote-adapter-whatsapp
curl http://localhost:8000/health
```

Para más detalles, consulta `docs/deployment-production.md`.

