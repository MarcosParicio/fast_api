import os
from sqlalchemy import create_engine
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

fichero = "../datos.sqlite"
# leemos el directorio del archivo de la bd
directorio = os.path.dirname(os.path.realpath(__file__))
# dirección de la bd, uniendo las dos variables anteriores
ruta = f"sqlite:///{os.path.join(directorio, fichero)}" # ya tenemos la ruta a la bd
# creamos el motor
motor = create_engine(ruta, echo=True)
# creamos la sesión pasándole el motor
sesion = sessionmaker(bind=motor)
# creamos la base para manejar las tablas
base = declarative_base()
