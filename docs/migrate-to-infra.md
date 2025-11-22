# Migración del Servicio a terranote-infra

Esta guía describe cómo migrar el servicio systemd del adaptador de WhatsApp a `terranote-infra` para mantener todo centralizado.

## Estado Actual

- ✅ Servicio corriendo desde: `/home/terranote/terranote-adapter-whatsapp/deploy/terranote-adapter-whatsapp.service`
- ✅ Instalado en: `/etc/systemd/system/terranote-adapter-whatsapp.service`
- ✅ Ejecutándose como usuario: `terranote`

## Pasos para Migrar a terranote-infra

### Paso 1: Copiar el servicio a terranote-infra

```bash
# Desde el directorio de terranote-adapter-whatsapp
cp deploy/terranote-adapter-whatsapp.service ../terranote-infra/systemd/
```

### Paso 2: Actualizar install-services.sh

Editar `/home/angoca/github/terranote-infra/systemd/install-services.sh` para incluir el servicio de WhatsApp.

Agregar algo como:

```bash
# WhatsApp Adapter
echo "Installing terranote-adapter-whatsapp service..."
cp "$SCRIPT_DIR/terranote-adapter-whatsapp.service" /etc/systemd/system/
systemctl daemon-reload
systemctl enable terranote-adapter-whatsapp
```

### Paso 3: Actualizar el README de terranote-infra

Editar `/home/angoca/github/terranote-infra/README.md` para mencionar el servicio de WhatsApp en la sección de Systemd Services.

### Paso 4: Verificar que el servicio sigue funcionando

```bash
# Verificar estado
sudo systemctl status terranote-adapter-whatsapp

# Verificar que responde
curl http://localhost:3001/health
```

### Paso 5: Commit y Push

```bash
cd /home/angoca/github/terranote-infra
git add systemd/terranote-adapter-whatsapp.service
git add systemd/install-services.sh
git add README.md
git commit -m "Add WhatsApp adapter systemd service"
git push
```

## Notas Importantes

- El servicio seguirá funcionando durante la migración (no hay downtime)
- Una vez migrado, el servicio se puede reinstalar usando el script de terranote-infra
- Mantener ambos archivos sincronizados hasta confirmar que todo funciona

## Checklist de Migración

- [ ] Copiar servicio a terranote-infra
- [ ] Actualizar install-services.sh
- [ ] Actualizar README.md
- [ ] Verificar que el servicio sigue funcionando
- [ ] Commit y push a terranote-infra
- [ ] Documentar en terranote-infra cómo usar el servicio

