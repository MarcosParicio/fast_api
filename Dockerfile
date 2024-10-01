# Imagen base de Python
FROM python:3.12

# Establecer el directorio de trabajo en la imagen
WORKDIR /app

# Copiar el Pipfile y el Pipfile.lock al contenedor
COPY Pipfile Pipfile.lock /app/

# Instalar pipenv y dependencias
RUN pip install pipenv && pipenv install --system --deploy

# Copiar el resto del proyecto al contenedor
COPY . /app

# Exponer el puerto 8000
EXPOSE 8000

# Comando para ejecutar la aplicación FastAPI
CMD ["pipenv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]


# se ejecuta para crear la imagen: docker build -t fastapi-ventas .
# se ejecuta para para iniciar el contenedor y mapear el puerto 8000 del contenedor al puerto 8000 de mi máquina local: docker run -d -p 8000:8000 fastapi-ventas
# verifico que el contenedor está corriendo: docker ps
# accedo a mi aplicación FastAPI abriendo mi navegador y navegando a http://localhost:8000 y http://localhost:8000/docs o bien  http://127.0.0.1:8000 y  http://127.0.0.1:8000/docs

