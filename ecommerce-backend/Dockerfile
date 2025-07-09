#FROM arm64v8/python:3.10-slim-bullseye
# Dockerfile

# --- Etapa de construcción ---
# Usamos una imagen completa de Python para instalar dependencias y compilar paquetes si es necesario
FROM python:3.10-slim-buster as builder

# Establecemos el directorio de trabajo
WORKDIR /usr/src/app

# Variables de entorno para Python
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Instalamos las dependencias
COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /usr/src/app/wheels -r requirements.txt


# --- Etapa final ---
# Usamos una imagen slim para reducir el tamaño final
FROM python:3.10-slim-buster

# Creamos un usuario no-root para mejorar la seguridad
RUN addgroup --system app && adduser --system --group app

# Establecemos el directorio de trabajo
WORKDIR /home/app

# Copiamos las dependencias pre-compiladas de la etapa anterior
COPY --from=builder /usr/src/app/wheels /wheels
COPY --from=builder /usr/src/app/requirements.txt .
RUN pip install --no-cache /wheels/*

# Copiamos el código de la aplicación
COPY . .

# Cambiamos el propietario de los archivos al usuario no-root
RUN chown -R app:app /home/app

# Cambiamos al usuario no-root
USER app

# Exponemos el puerto en el que Gunicorn escuchará
EXPOSE 8000

# Comando para iniciar la aplicación usando Gunicorn
# Apunta a la instancia 'app' dentro del archivo 'wsgi.py'
# Usa el archivo de configuración gunicorn.conf.py
CMD ["gunicorn", "--config", "gunicorn.conf.py", "wsgi:app"]
