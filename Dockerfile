# Dockerfile para PMBOK Tracker Flask
FROM python:3.9

# Crear usuario no root
RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:$PATH"

WORKDIR /app

# Copiar requirements y dependencias
COPY --chown=user ./requirements.txt requirements.txt
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copiar el resto del código
COPY --chown=user . /app

# Permisos de lectura y escritura para todo el contenido (solo para desarrollo/MVP)
RUN chmod -R 777 /app

# Exponer el puerto Flask por defecto
EXPOSE 7860

# Comando para iniciar Flask (no uvicorn, ya que es Flask, no FastAPI)
CMD ["python", "app.py"]