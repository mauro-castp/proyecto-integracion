# Microservicio productos · puerto 5103
# Productos: catálogo comercial con su categoría (PostgreSQL + caché Redis).
#
# Contexto de construcción: la RAÍZ del repositorio (docker-compose.integrado.yml lo indica), porque la
# imagen incluye los XSD y ejemplos oficiales del contrato v1 y la base común servicios/comun.
#   docker build -f servicios/productos/Dockerfile -t microhubs-productos .
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PYTHONPATH=/app SERVICIO=productos PUERTO=5103
WORKDIR /app

COPY servicios/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Contrato v1: XSD (validación XML) y ejemplos oficiales JSON y XML (Swagger).
COPY app_escritorio/contratos /app/contratos
COPY app_movil/app/src/test/resources/contratos /app/ejemplos_json
COPY servicios/comun /app/comun
COPY servicios/pruebas /app/pruebas
COPY servicios/migrar.py /app/migrar.py
COPY servicios/productos /app/servicio

# Sin privilegios de administrador dentro del contenedor.
RUN useradd --uid 10001 --no-create-home servicio
USER servicio

EXPOSE 5103
HEALTHCHECK --interval=15s --timeout=4s --retries=5 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:5103/health', timeout=3)"

CMD ["gunicorn", "-b", "0.0.0.0:5103", "-w", "2", "--timeout", "60", "--access-logfile", "-", "servicio.app:app"]
