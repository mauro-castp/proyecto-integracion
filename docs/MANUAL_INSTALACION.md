# Manual de instalación · Plataforma de Microhubs

Codex Innovations · Equipo 04 · Entrega final

Hay cuatro formas de instalar o usar la plataforma. Cada una tiene su sección:

1. **Local con Docker.** Toda la plataforma en una computadora. Es la forma de desarrollar y ensayar.
2. **En Google Cloud.** La VM con Nginx, el bucket y los registros. Es la forma de producción y de la presentación.
3. **App Android.** Para el repartidor.
4. **App de escritorio.** Para el planeador, el administrador y el auditor.

Hay un anexo para quien no puede usar Docker.

---

## 1. Local con Docker

**Requisitos:** Docker Desktop o Docker Engine con Compose v2, unos 8 GB de RAM libres y los puertos 5000 y 5101–5126 libres.

```bash
git clone <repositorio> && cd proyecto-integracion-main
docker compose -f docker-compose.integrado.yml up --build -d     # la primera vez construye 27 imágenes (~10 min)
docker compose -f docker-compose.integrado.yml ps -a             # todo «healthy»; «migraciones» en Exited (0)
```

| Qué | Dónde |
|---|---|
| Portal web | http://localhost:5000 |
| Panel de monitoreo | http://localhost:5000/web/servicios/monitoreo |
| Swagger de cada servicio | http://localhost:51XX/api/v1/docs (5101 auth … 5126 auditoria-monitoreo) |
| Salud de cada servicio | http://localhost:51XX/api/v1/salud |

**Cuentas de demostración**, todas con la clave `Codex#2026` (solo en local):

| Correo | Perfil |
|---|---|
| `admin@codex.mx` | administrador |
| `operador.mh01@codex.mx` | operador del MH-01 |
| `planeador@codex.mx` | planeador |
| `auditor@codex.mx` | auditor |
| `repartidor1@codex.mx`, `repartidor2@codex.mx` | repartidores |

**La base de datos se crea sola** al primer arranque. PostgreSQL ejecuta `bloque_c/sql/01` a `14` y MongoDB ejecuta `bloque_c/mongo/01` a
`03`. Si ya existía un volumen de una versión anterior, el contenedor `migraciones` aplica de la 06 a la 14 sin borrar datos. MongoDB no
vuelve a correr sus scripts sobre un volumen existente. Para tomar el nuevo tipo de referencia `orden_compra` hay que correr una vez (en la nube lo hace el instalador):

```bash
docker compose -f docker-compose.integrado.yml exec -T mongo mongosh microhubs_eventos < bloque_c/mongo/03_documentos_nube.js
```

**Datos para ensayar:**

```bash
C="docker compose -f docker-compose.integrado.yml"
$C exec entregas python pruebas/preparar_entregas.py --cantidad 3        # entregas en ruta para la app Android
$C exec entregas python -m pruebas.preparar_listos --cantidad 6          # pedidos listos para planear rutas
# (opcional) 100 000 pedidos y 1.4 millones de puntos GPS para medir rendimiento (ver evidencias/volumen/LEEME.md):
$C cp bloque_c/scripts/generar_volumen.py entregas:/tmp/ && $C exec -w /tmp entregas python /tmp/generar_volumen.py --pedidos 100000
$C exec -w /tmp entregas python /tmp/generar_volumen.py --borrar        # quitarlos
```

**Detener la plataforma:**

- `$C down` conserva los datos.
- `$C down -v` borra los volúmenes. Se usa para empezar desde cero.

**Variables de entorno** (todas tienen un valor por omisión en el compose). Las más importantes:

| Variable | Para qué sirve |
|---|---|
| `SECRET_KEY` | Firma de los JWT. Es la misma en el web y en los servicios. |
| `POSTGRES_PASSWORD` | Clave de PostgreSQL. |
| `ALMACEN`, `GCS_BUCKET` | `local` (carpeta del contenedor) o `gcs` (bucket). |
| `URL_FIRMADA_SEGUNDOS` | Vigencia de las URL firmadas. Por omisión, 300. |
| `VERSION_DESPLEGADA` | La versión que informa `/salud`. |
| `DETRAS_DE_PROXY` | `1` si hay un Nginx delante: la IP real sale de `X-Forwarded-For`. |
| `LIMITE_POR_MINUTO`, `LIMITE_LOGIN_POR_MINUTO` | Límite de consumo por IP (240 y 30). |
| `MICROSERVICIOS_TIEMPO` | Segundos que un servicio espera a otro (4). |

---

## 2. Google Cloud Platform

Lo que ya existe y cómo se creó está en [`deploy/gcp/LEEME.md`](../deploy/gcp/LEEME.md):

- la VM e2-standard-4 en `northamerica-south1-c`;
- la IP fija;
- el firewall que solo abre 80 y 443;
- el bucket privado;
- la cuenta de servicio sin llaves;
- el Ops Agent.

**Desplegar o actualizar**, desde la raíz del repositorio en tu computadora:

```bash
git -c core.autocrlf=false archive --format=tar.gz -o microhubs.tgz HEAD \
  docker-compose.integrado.yml .dockerignore servicios sistema_web bloque_c app_escritorio/contratos \
  app_movil/app/src/test/resources/contratos deploy/gcp rendimiento pruebas_carga
gcloud compute instances start microhubs-vm --zone northamerica-south1-c
gcloud compute scp microhubs.tgz microhubs-vm:/tmp/ --zone northamerica-south1-c
gcloud compute ssh microhubs-vm --zone northamerica-south1-c --command \
  "mkdir -p ~/microhubs && tar xzf /tmp/microhubs.tgz -C ~/microhubs && cd ~/microhubs && VERSION_DESPLEGADA=$(git rev-parse --short HEAD) bash deploy/gcp/instalar_vm.sh"
```

El instalador hace lo siguiente y se puede repetir sin riesgo:

1. Crea el `.env` con secretos aleatorios (permiso 600) e incluye `DETRAS_DE_PROXY=1`.
2. Levanta los contenedores.
3. Cambia la clave de las cuentas de demostración (queda en `MICROHUBS_CLAVE` dentro del `.env`).
4. Pone al día el esquema de `documentos` en MongoDB.
5. Configura Nginx.

**HTTPS (obligatorio para las apps instalables):**

```bash
bash deploy/gcp/instalar_vm.sh --sin-construir --https <correo>
```

Pide un certificado de Let's Encrypt para `34-51-89-253.sslip.io` y deja la redirección de 80 a 443.

**Comprobar el despliegue:**

```bash
curl -s https://34-51-89-253.sslip.io/servicios/auth/api/v1/salud | jq
cd ~/microhubs && set -a && . ./.env && set +a && RED_EXTRA=microhubs-integrado_publica servicios/pruebas/correr.sh test pruebas.test_nube -v
```

**Apagar al terminar:** `gcloud compute instances stop microhubs-vm --zone northamerica-south1-c`. Cuesta unos 0.13 USD por hora encendida.

---

## 3. App Android (repartidor)

**Requisitos:** JDK 17 o 21 y Android SDK 35.

```powershell
cd app_movil
./build.ps1                                   # debug: pruebas, lint y app/build/outputs/apk/debug/app-debug.apk
./build.ps1 -DebugHttpHost 192.168.1.20       # debug en un teléfono contra la PC (HTTP solo a ese host)
```

**APK instalable para la entrega (release, firmada).** Se necesita HTTPS en la VM, porque el release no permite HTTP.

```powershell
keytool -genkeypair -v -keystore microhubs-release.jks -alias microhubs -keyalg RSA -keysize 2048 -validity 3650   # NO subir a Git
gradle assembleRelease "-Pandroid.injected.signing.store.file=$PWD\microhubs-release.jks" `
  "-Pandroid.injected.signing.store.password=<clave>" "-Pandroid.injected.signing.key.alias=microhubs" "-Pandroid.injected.signing.key.password=<clave>"
# → app/build/outputs/apk/release/app-release.apk
```

En la pantalla de acceso de la app se escribe el servidor `https://34-51-89-253.sslip.io/servicios`. La cuenta es
`repartidor1@codex.mx` con la clave `MICROHUBS_CLAVE` de la VM.

---

## 4. App de escritorio (Windows)

**Requisitos:** Windows y el SDK de .NET 8.

```powershell
cd app_escritorio
dotnet run                                                                            # desarrollo (host http://localhost)
dotnet publish Microhubs.csproj -c Release -r win-x64 --self-contained true -o bin/Publicacion
Compress-Archive bin/Publicacion/* Microhubs-Escritorio-win-x64.zip                   # instalable: descomprimir y ejecutar Microhubs.exe
```

Contra la nube se usa el host `https://34-51-89-253.sslip.io/servicios`. Fuera de `localhost` la app solo acepta HTTPS.

---

## Anexo · Sin Docker (como se corrieron las pruebas de rendimiento)

Con PostgreSQL 16, MongoDB 7 y Redis 7 instalados en la máquina:

```bash
python -m venv .venv && .venv/bin/pip install -r servicios/requirements.txt -r sistema_web/requirements.txt locust psutil
createdb microhubs_p1 && for f in bloque_c/sql/*.sql; do psql -d microhubs_p1 -v ON_ERROR_STOP=1 -f $f; done
for f in bloque_c/mongo/0*.js; do mongosh microhubs_eventos $f; done
export PG_DSN="host=127.0.0.1 dbname=microhubs_p1 user=… password=…" REDIS_URL=redis://127.0.0.1:6379 \
       MONGO_URL=mongodb://127.0.0.1:27017/microhubs_eventos MICROSERVICIOS_URL="http://127.0.0.1:{puerto}"
# cada servicio: carpeta con enlaces servicio → servicios/<nombre>, comun → servicios/comun; luego
SERVICIO=pedidos PYTHONPATH=<carpeta> gunicorn -b 127.0.0.1:5104 -w 2 servicio.app:app
```
