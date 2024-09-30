from jwt import encode, decode

from dotenv import load_dotenv
import os

load_dotenv()  # carga las variables de entorno del archivo .env

JWT_SECRET = os.getenv('FAST_API_JWT_SECRET')

def dame_token(dato: dict) -> str:
    token: str = encode(payload=dato, key=JWT_SECRET, algorithm='HS256')
    return token

def validar_token(token: str) -> dict:
    dato: dict = decode(token, key=JWT_SECRET, algorithms=['HS256'])
    return dato
