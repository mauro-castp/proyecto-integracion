# Imagen de UN microservicio. Se construye una vez por servicio con
#   --build-arg SERVICIO=<auth|usuarios|catalogos|pedidos|entregas|planeacion|documentos|notificaciones>
# y cada servicio corre en su propio contenedor (docker-compose.integrado.yml).
#
# Contexto de construcción: la RAÍZ del repositorio, porque la imagen lleva:
#   · los XSD y ejemplos oficiales del contrato v1 (una sola fuente: las carpetas de las apps);
#   · los cálculos de planeación del sistema web (no se duplican fórmulas).
FROM python:3.12-slim

ARG SERVICIO
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PYTHONPATH=/app SERVICIO=${SERVICIO} PUERTO=8000
WORKDIR /app

COPY servicios/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app_escritorio/contratos /app/contratos
COPY app_movil/app/src/test/resources/contratos /app/ejemplos_json
COPY sistema_web/nucleo.py sistema_web/planeacion.py sistema_web/planeacion_calc.py /app/web/
COPY servicios/comun /app/comun
COPY servicios/pruebas /app/pruebas
COPY servicios/migrar.py /app/migrar.py
COPY servicios/${SERVICIO} /app/servicio

# Sin privilegios de administrador dentro del contenedor.
RUN useradd --system --uid 10001 servicio
USER servicio

HEALTHCHECK --interval=15s --timeout=4s --retries=5 \
  CMD python -c "import os,urllib.request; urllib.request.urlopen(f'http://127.0.0.1:{os.environ[\"PUERTO\"]}/salud', timeout=3)"

CMD ["sh", "-c", "exec gunicorn -b 0.0.0.0:${PUERTO} -w 2 --timeout 60 --access-logfile - servicio.app:app"]
