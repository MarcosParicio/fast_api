# Usa una imagen base oficial de Debian o similar
FROM debian:bullseye-slim

# Instala las dependencias necesarias para construir Python desde el código fuente
RUN apt-get update && apt-get install -y \
    wget \
    build-essential \
    libssl-dev \
    zlib1g-dev \
    libncurses5-dev \
    libncursesw5-dev \
    libreadline-dev \
    libsqlite3-dev \
    libgdbm-dev \
    libdb5.3-dev \
    libbz2-dev \
    libexpat1-dev \
    liblzma-dev \
    tk-dev \
    libffi-dev \
    git \
    && apt-get clean

# Descarga y construye Python 3.12
RUN wget https://www.python.org/ftp/python/3.12.0/Python-3.12.0.tgz \
    && tar xzf Python-3.12.0.tgz \
    && cd Python-3.12.0 \
    && ./configure --enable-optimizations \
    && make altinstall \
    && cd .. \
    && rm -rf Python-3.12.0 Python-3.12.0.tgz

# Usa la nueva versión de Python
RUN ln -s /usr/local/bin/python3.12 /usr/local/bin/python

# Instala pip para Python 3.12
RUN /usr/local/bin/python3.12 -m ensurepip \
    && /usr/local/bin/python3.12 -m pip install --upgrade pip

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Instala pipenv
RUN /usr/local/bin/python3.12 -m pip install pipenv

# Copia los archivos Pipfile y Pipfile.lock a /app en el contenedor
COPY Pipfile Pipfile.lock ./

# Instala las dependencias del proyecto
RUN pipenv install --deploy --ignore-pipfile

# Copia el resto del código de la aplicación al contenedor
COPY . .

# Especifica que el contenedor debe ejecutarse como un entorno virtual de pipenv
CMD ["pipenv", "run", "start"]


# COMANDO PARA CREAR LA IMAGEN EN DOCKER DESKTOP: docker build -t nombre-de-tu-imagen .

