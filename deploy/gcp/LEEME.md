# Despliegue en Google Cloud Platform

Plataforma de Microhubs desplegada en **Compute Engine** con **Cloud Storage** para los archivos. Proyecto GCP `integracion-sistemas-637044`,
región `northamerica-south1` (Querétaro, México).

```
Internet ──80/443──► Nginx (VM) ─┬─ /                       ► portal web        127.0.0.1:5000
                                 └─ /servicios/<nombre>/    ► 23 microservicios 127.0.0.1:5101…5124
                                       │
              Docker (red interna, sin puertos al host): PostgreSQL · Redis · MongoDB
                                       │
                        Cloud Storage (bucket privado) ◄── cuenta de servicio de la VM (sin llaves)
```

## Recursos creados

| Recurso | Nombre | Detalle |
|---|---|---|
| VM | `microhubs-vm` | e2-standard-4 (4 vCPU, 16 GB), Ubuntu 24.04, disco pd-balanced de 80 GB, zona `northamerica-south1-c`, etiqueta `microhubs` |
| IP externa fija | `microhubs-ip` | 34.51.89.253 (nombre `34-51-89-253.sslip.io`) |
| Firewall | `microhubs-web` | Solo TCP 80 y 443 hacia la etiqueta `microhubs`. Los puertos 5000 y 5101–5124 NO tienen regla: además se publican solo en 127.0.0.1 |
| Cuenta de servicio | `microhubs-vm@…iam.gserviceaccount.com` | `objectAdmin` **solo sobre su bucket** y `serviceAccountTokenCreator` sobre sí misma (para firmar URLs con IAM). Sin llaves descargadas |
| Bucket | `gs://microhubs-evidencias-637044` | Privado: acceso uniforme a nivel de bucket y **prevención de acceso público activa** |

## Cómo se despliega

Desde tu computadora (el código viaja como archivo comprimido; el `.env` se crea en la VM y nunca sale de ella):

```bash
tar czf microhubs.tgz --exclude=.venv --exclude=__pycache__ --exclude='*.db' --exclude=node_modules \
  docker-compose.integrado.yml .dockerignore servicios sistema_web bloque_c app_escritorio/contratos \
  app_movil/app/src/test/resources/contratos deploy/gcp
gcloud compute scp microhubs.tgz microhubs-vm:/tmp/ --zone northamerica-south1-c
gcloud compute ssh microhubs-vm --zone northamerica-south1-c --command 'mkdir -p ~/microhubs && tar xzf /tmp/microhubs.tgz -C ~/microhubs && cd ~/microhubs && bash deploy/gcp/instalar_vm.sh'
```

`instalar_vm.sh` crea el `.env` con secretos aleatorios (permiso 600), verifica que no queden los valores por defecto del repositorio,
levanta los contenedores y configura Nginx. HTTPS opcional: `bash deploy/gcp/instalar_vm.sh --sin-construir --https tu@correo`.
`python deploy/gcp/generar.py` regenera `docker-compose.gcp.yml` y `nginx-microhubs.conf` cuando cambian los servicios.

## Archivos y URLs firmadas

La base de datos **no guarda archivos**. El servicio `documentos` sube el archivo al bucket y MongoDB conserva solo su id, ruta, tipo, tamaño,
propietario, fecha, SHA-256, privacidad (`privado` | `interno`), estado (`activo` | `eliminado`) y metadatos. Para descargar:

`GET /servicios/documentos/api/v1/documentos/{id}/enlace` → URL **firmada V4**, de un solo método (GET) y con caducidad (300 s por omisión),
que el cliente usa para bajar el archivo directo de Cloud Storage. Cada enlace emitido queda en la auditoría.
Los documentos anteriores (con el archivo dentro de MongoDB) se mueven con `python -m servicio.migrar_a_almacen`.

## Salud

`GET /servicios/<nombre>/api/v1/salud` informa servicio, versión desplegada, estado de PostgreSQL, Redis, MongoDB y bucket y el tiempo de
respuesta (`tiempo_ms`). `bucket` solo se comprueba en los servicios que guardan archivos; en los demás es `no_aplica` para que una falla del
bucket no los marque como degradados.

## Costo y apagado

Aproximadamente 0.13 USD/hora encendida (e2-standard-4) + disco ~8 USD/mes + IP ~4 USD/mes. Apagar al terminar:
`gcloud compute instances stop microhubs-vm --zone northamerica-south1-c`. Los datos (volúmenes de Docker) y el bucket se conservan.
