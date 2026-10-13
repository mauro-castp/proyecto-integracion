# Microservicio auth · puerto 5101
# Autenticación: login, renovación, validación y cierre de sesión (JWT + Redis).
#
# Contexto de construcción: la RAÍZ del repositorio (docker-compose.integrado.yml lo indica), porque la
# imagen incluye los XSD y ejemplos oficiales del contrato v1 y la base común servicios/comun.
#   docker build -f servicios/auth/Dockerfile -t microhubs-auth .
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PYTHONPATH=/app SERVICIO=auth PUERTO=5101
WORKDIR /app

COPY servicios/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Contrato v1: XSD (validación XML) y ejemplos oficiales JSON y XML (Swagger).
COPY app_escritorio/contratos /app/contratos
COPY app_movil/app/src/test/resources/contratos /app/ejemplos_json
COPY servicios/comun /app/comun
COPY servicios/pruebas /app/pruebas
COPY servicios/migrar.py /app/migrar.py
COPY servicios/auth /app/servicio

# Sin privilegios de administrador dentro del contenedor.
RUN useradd --uid 10001 --no-create-home servicio
USER servicio

EXPOSE 5101
HEALTHCHECK --interval=15s --timeout=4s --retries=5 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:5101/health', timeout=3)"

CMD ["gunicorn", "-b", "0.0.0.0:5101", "-w", "2", "--timeout", "60", "--access-logfile", "-", "servicio.app:app"]
