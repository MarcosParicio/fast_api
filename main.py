from fastapi import FastAPI, Body, Path, Query, Request, HTTPException, Depends

from fastapi.responses import HTMLResponse, JSONResponse, Response

from fastapi.staticfiles import StaticFiles

from fastapi.security import HTTPBearer

from fastapi.encoders import jsonable_encoder

from pydantic import BaseModel, Field
from typing import Optional, List

from jwt_config import dame_token, validar_token

from dotenv import load_dotenv
import os

from config.base_de_datos import sesion, motor, base
from modelos.ventas import Ventas as VentasModelo

load_dotenv()  # carga las variables de entorno del archivo .env

EMAIL = os.getenv('FAST_API_EMAIL')
CLAVE = os.getenv('FAST_API_CLAVE')

# crear instancia de fastapi
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
app.title = 'Aplicación de ventas'
app.version = '1.0.1'

base.metadata.create_all(bind=motor)

# ventas_lista = [
#     {
#         "id": 1,
#         "fecha": "01/01/23",
#         "tienda": "Tienda01",
#         "importe": 2500
#     },
#     {
#         "id": 2,
#         "fecha": "22/01/23",
#         "tienda": "Tienda02",
#         "importe": 4500
#     }
# ]

# modelo para la autenticación
class Usuario(BaseModel):
    email: str
    clave: str
    
# portador del token
class Portador(HTTPBearer):
    async def __call__(self, request: Request):
        autorizacion = await super().__call__(request)
        dato = validar_token(autorizacion.credentials)
        if dato['email'] != EMAIL:
            raise HTTPException(status_code=403, detail='No autorizado') # código de respuesta el acceso solicitado está restringido
        
"""
EXPLICACIÓN CLASS PORTADOR

Método asíncrono: async def significa que este método es asíncrono.
Los métodos asíncronos permiten realizar tareas que pueden tomar tiempo (como leer un archivo o hacer una solicitud de red) sin bloquear el programa.
En este caso, se usa porque las solicitudes HTTP pueden tardar.
await: Dado que super().__call__(request) es una operación que puede tomar tiempo (porque maneja la autenticación), usamos await para esperar a que termine.
await solo se puede usar dentro de métodos async.

Imagina que tienes una puerta que solo se abre con una tarjeta de acceso.
Aquí, Portador es el guardia de seguridad en la puerta, y el método __call__ es lo que hace el guardia cada vez que alguien intenta entrar.

Alguien llega a la puerta con una tarjeta (request).
El guardia llama a su supervisor para verificar la tarjeta (super().call(request)) y espera la respuesta (await).
El supervisor verifica la tarjeta y responde con la información de la tarjeta (autorizacion).
El guardia toma esa información y la pasa por un escáner (validar_token(autorizacion.credentials)) para leer los detalles (dato).
El guardia verifica que el nombre en la tarjeta sea el de una persona autorizada.

"""

# creamos el modelo
class Ventas(BaseModel):
    #id: int = Field(ge=0, le=20)
    id: Optional[int] = None
    fecha: str
    tienda : str = Field(min_length=4, max_length=10)
    importe: float
    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "fecha": "01/02/23",
                "tienda": "Tienda09",
                "importe": 131
            }
        }

# crear punto de entrada o endpoint con decoradores @
@app.get('/', tags=['Inicio']) # cambio de etiqueta en documentación
def mensaje():
    return HTMLResponse('<h2>Titulo html desde FastAPI</h2>')

# Test endpoint to verify that the favicon is accessible
@app.get("/test_favicon", tags=['Favicon'])
def test_favicon():
    with open("static/favicon.ico", "rb") as f:
        content = f.read()
    return Response(content, media_type="image/x-icon")

@app.get('/ventas', tags=['Ventas'], response_model=List[Ventas], status_code=200, dependencies=[Depends(Portador())]) # código de respuesta ok
def dame_ventas() -> List[Ventas]:
    db = sesion()
    resultado = db.query(VentasModelo).all()
    return JSONResponse(content=jsonable_encoder(resultado), status_code=200)

@app.get('/ventas/{id}', tags=['Ventas'], response_model=Ventas, status_code=200)
def dame_ventas(id: int = Path(ge=1, le=1000)) -> Ventas:
    db = sesion()
    resultado = db.query(VentasModelo).filter(VentasModelo.id == id).first()
    if not resultado:
        return JSONResponse(content={'mensaje': f'No existe la venta {id}, por lo tanto no puede ser mostrada'}, status_code=404)  # código de respuesta se pidió de manera correcta al servidor pero no está
    # for elem in ventas_lista:
    #     if elem['id'] == id:
    #          return JSONResponse(content=elem, status_code=200)
    return JSONResponse(content=jsonable_encoder(resultado), status_code=200)

@app.get('/ventas/', tags=['Ventas'], response_model=List[Ventas], status_code=200)
def dame_ventas_por_tienda(tienda: str = Query(min_length=4, max_length=20)) -> List[Ventas]:
    db = sesion()
    resultado = db.query(VentasModelo).filter(VentasModelo.tienda == tienda).all()
    if not resultado:
        return JSONResponse(content={'mensaje': f'No existe la tienda {tienda}, por lo tanto no puede ser mostrada'}, status_code=404)
    # datos = [elem for elem in ventas_lista if elem['tienda'] == tienda]
    return JSONResponse(content=jsonable_encoder(resultado), status_code=200)

@app.post('/ventas', tags=['Ventas'], response_model=dict, status_code=201) # código de respuesta la solicitud se procesa correctamente y se crea el recurso
def crea_venta(venta: Ventas) -> dict:
    db = sesion()
    
    # extraemos los atributos y los pasamos como parámetros
    nueva_venta_db = VentasModelo(**venta.model_dump())
    
    # añadir a la db y hacemos un commit para actualizar
    db.add(nueva_venta_db)
    db.commit()
    
    # ventas_lista inicialmente contiene diccionarios pero luego estamos añadiendo objetos de tipo Ventas
    # para asegurarnos de que la lista ventas_lista siempre contiene diccionarios hacemos lo siguiente
    # pongo nueva_venta = venta.dict() pero me pone:
    # The method "dict" in class "BaseMode1" is deprecated; use model_dunp() instead, por lo que cambio dict() por model_dump():
    #nueva_venta = venta.model_dump()
    #ventas_lista.append(nueva_venta)
    return JSONResponse(content={'mensaje': 'Nueva venta registrada', 'Parámetros de la nueva venta registrada': venta.model_dump()}, status_code=201)

@app.put('/ventas/{id}', tags=['Ventas'], response_model=dict, status_code=201)
def actualiza_venta(id: int, venta: Ventas) -> dict:
    db = sesion()
    resultado = db.query(VentasModelo).filter(VentasModelo.id == id).first()
    if not resultado:
        return JSONResponse(content={'mensaje': f'No existe la venta {id}, por lo tanto no puede ser actualizada'}, status_code=404)
    resultado.fecha = venta.fecha
    resultado.tienda = venta.tienda
    resultado.importe = venta.importe
    db.commit()
    # recorrer los elementos de la lista
    # for elem in ventas_lista:
    #     if elem["id"] == id:
    #         elem['fecha'] = venta.fecha
    #         elem['tienda'] = venta.tienda
    #         elem['importe'] = venta.importe
    #         return JSONResponse(content={'mensaje': 'Venta modificada', 'Parámetros de la venta modificada': elem}, status_code=201)
    return JSONResponse(content={'mensaje': f'La venta {id} se ha actualizado', 'actualización': venta.model_dump()}, status_code=200)

@app.delete('/ventas/{id}', tags=['Ventas'], response_model=dict, status_code=200)
def borra_ventas(id: int = Path(ge=1, le=1000)) -> dict:
    db = sesion()
    resultado = db.query(VentasModelo).filter(VentasModelo.id == id).first()
    if not resultado:
        return JSONResponse(content={'mensaje': f'No existe la venta {id}, por lo tanto no puede ser borrada'}, status_code=404)
    db.delete(resultado)
    db.commit()
    # recorrer los elementos de la lista
    # for elem in ventas_lista:
    #      if elem["id"] == id:
    #         ventas_lista.remove(elem)
    #         return JSONResponse(content={'mensaje': f'Venta {id} eliminada'}, status_code=200)
    return JSONResponse(content={'mensaje': f'La venta {id} ha sido eliminada'}, status_code=200)

# creamos ruta para el login
@app.post('/login', tags=['Autenticación'])
def login(usuario: Usuario):
    if usuario.email == EMAIL and usuario.clave == CLAVE:
        # obtenemos el token con la función pasándole el diccionario de usuario
        token: str = dame_token(usuario.model_dump()) # he puesto dict() pero me dice que está deprecado en FastAPI y que se debe usar model_dump()
        return JSONResponse(content=token, status_code=200)
    else:
        return JSONResponse({'mensaje': 'Los credenciales no son correctos, acceso denegado'}, status_code=404)
    