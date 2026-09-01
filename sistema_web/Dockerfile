FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# No corre como root: si alguien logra ejecutar código en el contenedor,
# no debe encontrarse con privilegios de administrador.
RUN useradd --create-home --shell /bin/false microhubs && chown -R microhubs /app
USER microhubs

EXPOSE 5000
HEALTHCHECK --interval=20s --timeout=4s --start-period=15s --retries=3 \
  CMD python -c "import urllib.request;urllib.request.urlopen('http://127.0.0.1:5000/salud')"

CMD ["gunicorn", "-b", "0.0.0.0:5000", "-w", "3", "--timeout", "60", "app:app"]
