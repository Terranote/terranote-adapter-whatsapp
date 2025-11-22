# Usar terranote-infra para Gestionar el Servicio

## ✅ El servicio ya está en terranote-infra

El servicio `terranote-adapter-whatsapp.service` ya está en `/home/angoca/github/terranote-infra/systemd/` y el script `install-services.sh` ya lo incluye.

## Cómo Gestionar el Servicio desde terranote-infra

### Instalar/Actualizar todos los servicios

```bash
cd /home/angoca/github/terranote-infra
git pull
bash systemd/install-services.sh
```

Este script:
- ✅ Copia todos los servicios a `/etc/systemd/system/`
- ✅ Recarga systemd
- ✅ Habilita los servicios para inicio automático
- ✅ Inicia los servicios

### Gestionar el servicio de WhatsApp

```bash
# Ver estado
sudo systemctl status terranote-adapter-whatsapp

# Iniciar
sudo systemctl start terranote-adapter-whatsapp

# Detener
sudo systemctl stop terranote-adapter-whatsapp

# Reiniciar
sudo systemctl restart terranote-adapter-whatsapp

# Ver logs
sudo journalctl -u terranote-adapter-whatsapp -f
```

## Ventajas de Usar terranote-infra

- ✅ **Centralizado**: Todos los servicios en un solo lugar
- ✅ **Sincronizado**: Un solo `git pull` actualiza todo
- ✅ **Consistente**: Mismo proceso para todos los servicios
- ✅ **Mantenible**: Cambios en un solo repositorio

## Próximos Pasos

1. **Detener el proceso manual** del adaptador (si está corriendo)
2. **Instalar el servicio desde terranote-infra:**
   ```bash
   cd /home/angoca/github/terranote-infra
   git pull
   bash systemd/install-services.sh
   ```
3. **Verificar que funciona:**
   ```bash
   sudo systemctl status terranote-adapter-whatsapp
   curl http://localhost:3001/health
   ```

¡Todo centralizado en terranote-infra! 🎉

