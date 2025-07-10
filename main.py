from datetime import datetime, timezone
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import (
    create_engine, Column, Integer, Float, String, ForeignKey, DateTime,
    UniqueConstraint
)
from sqlalchemy.orm import declarative_base, relationship, Session, select
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from typing import Annotated
from fastapi import status

from pydantic import BaseModel
from sqlalchemy import Date, Time

# --- Configuración conexión a PostgreSQL (ajusta usuario, pass, host, puerto, dbname)
#DATABASE_URL = "postgresql+psycopg2://mtNUViyTddNAbZhAVZP6R23G9k0BFcJY:mtNUViyTddNAbZhAVZP6R23G9k0BFcJY@host:5432/laburantes_db"
DATABASE_URL = "postgresql://laburantes_db_user:mtNUViyTddNAbZhAVZP6R23G9k0BFcJY@dpg-d1m3kqa4d50c738f4a7g-a/laburantes_db"

engine = create_engine(DATABASE_URL, echo=True)  # echo=True para logs SQL

Base = declarative_base()
from sqlalchemy import MetaData

meta = MetaData()
meta.reflect(bind=engine)  # Trae todas las tablas existentes
meta.drop_all(bind=engine) # Borra todas las tablas
# --- MODELOS

class Servicios_Trabajadores(Base):
    __tablename__ = 'servicios_trabajadores'
    id = Column(Integer, primary_key=True, autoincrement=True)  # <-- ID autoincremental
    servicio_id = Column(ForeignKey('servicios.id'), nullable=False)
    trabajador_id = Column(ForeignKey('trabajadores.id'), nullable=False)
    precioxhora = Column(Integer)
from pydantic import BaseModel, Field
from sqlmodel import SQLModel, Field

class TrabajadorBase(SQLModel):
    nombre: str = Field(index=True)
class ServicioTrabajadorBase(BaseModel):
    precioxhora: int = Field(..., description="Precio por hora", example=1500)
    class Config:
        orm_mode = True
        
class UsuarioServicioTrabajador(Base):
    __tablename__ = 'usuarios_servicios_trabajadores'
    usuario_id = Column(ForeignKey('usuarios.id'), primary_key=True)
    servicio_trabajador_id = Column(ForeignKey('servicios_trabajadores.id'), primary_key=True)

class Servicio(Base):
    __tablename__ = 'servicios'
    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String, nullable=False, unique=True)  # único por título
    servicios_trabajadores = relationship("Servicios_Trabajadores", back_populates="servicio")
    trabajadores = relationship("Trabajador", secondary="servicios_trabajadores", back_populates="servicios")


class Trabajador(Base):
    __tablename__ = 'trabajadores'
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    dni = Column(String, nullable=False, unique=True)  # DNI único
    correoElec = Column(String, nullable=False)
    direccion = Column(String, nullable=False)
    localidad = Column(String, nullable=False)
    latitud = Column(Float)
    longitud = Column(Float)
    wsapp = Column(String, nullable=False)
    foto = Column(String, nullable=False)
    penales = Column(String, nullable=False)
    servicios_trabajadores = relationship("Servicios_Trabajadores", back_populates="trabajador")
    servicios = relationship("Servicio", secondary="servicios_trabajadores", back_populates="trabajadores")


class Opinion(Base):
    __tablename__ = 'opiniones'
    id = Column(Integer, primary_key=True, index=True)
    trabajador_id = Column(Integer, ForeignKey("trabajadores.id"), nullable=False)
    comentario = Column(String, nullable=False)
    calificacion = Column(Integer, nullable=False)  # 1 a 5
    fecha = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))

    trabajador = relationship("Trabajador")


class Usuario(Base):
    __tablename__ = 'usuarios'
    id = Column(Integer, primary_key=True)
    nombre = Column(String, nullable=False)
    dni = Column(String, nullable=False, unique=True)
    correoElec = Column(String, nullable=False)
    direccion = Column(String, nullable=False)
    localidad = Column(String, nullable=False)
    wsapp = Column(String, nullable=False)

class Tracking(Base):
    __tablename__ = "tracking"
    id = Column(Integer, primary_key=True)
    fecha = Column(Date)
    hora = Column(Time)
    nroAndroid = Column(String)
    lati = Column(String)
    loni = Column(String)

class TrackingIn(BaseModel):
    fecha: str
    hora: str
    nroAndroid: str
    lati: str
    loni: str

    class Config:
        orm_mode = True


# --- FastAPI app y dependencias

app = FastAPI()

#app.mount("/static", StaticFiles(directory="fotos"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_session():
    with Session(engine) as session:
        yield session

db_dependency = Annotated[Session, Depends(get_session)]


# --- Crear tablas (solo la primera vez o migrar con alembic)

Base.metadata.create_all(engine)
def get_db():
    db = Session(bind=engine)
    try:
        yield db
    finally:
        db.close()
@app.post("/cargar_oficios/")
def cargar_oficios(db: Session = Depends(get_db)):
    oficios = [
        'Albañil',#1#
        'Informático',#2#
        'Mozo',#3#
        'Programador Web',#4#
        'Programador Front End',#5#
        'Programador Back End',#6#
        'Vendedor' ,#7#
        'Vendedor Ambulante', #8#
        'Ayudante de Cocina',#9#
        'Chapista',#10#
        'Membranas',#11#
        'Zinguero',#12#
        'Empleada Doméstica',#13#
        'Enfermera - Enfermero',#14#
        'Perforaciones',#15#
        'Taxista',#16#
        'Electricista',#17#
        'Electricista del Automotor',#18#
        'Plomero',#19#
        'Gasista matriculado',#20#
        'Carpintero',#21#
        'Pintor',#22#
        'Cerrajero',#23#
        'Techista',#24#
        'Colocador de cerámicos',#25#
        'Colocador de durlock',#26#
        'Soldador',#27#
        'Mecánico automotor',#28#
        'Delyvery',#29#
        'Remisse',#30#
        'Mecánico de motos',#31#
        'Reparador de electrodomésticos',#32#
        'Herrero',#33#
        'Jardinero',#34#
        'Podador',#35#
        'Cuidadores de adultos mayores',#36#
        'Niñera',#37#
        'Maestra particular',#38#
        'Cocinero a domicilio',#39#
        'Delivery con moto',#40#
        'Mudanzas y fletes',#41#
        'Peluquero/a',#42#
        'Manicuría y pedicuría',#43#
        'Estética y depilación',#44#
        'Masajista',#45#
        'Personal trainer',#46#
        'Entrenador deportivo',#47#
        'Profesor de música',#48#
        'Profesor de inglés',#49#
        'Profesor de Matemáticas',#50#
        'Profesor de Gimnasia',#51#
        'Profesor de Danzas',#52#
        'Profesor de Música',#53#
        'Clases de apoyo escolar',#54#
        'Diseñador gráfico',#55#
        'Diseñador web',#56#
        'Fotógrafo',#57#
        'Videógrafo',#58#
        'Community manager',#59#
        'Desarrollador de software',#60#
        'Técnico en computación',#61#
        'Armado y reparación de PC',#62#
        'Instalador de cámaras de seguridad',#63#
        'Instalador de redes',#64#
        'Servicio de limpieza',#65#
        'Limpieza de vidrios',#66#
        'Limpieza final de obra',#67#
        'Cuidado de mascotas',#68#
        'Paseador de perros',#69#
        'Adiestrador canino',#70#
        'Yesero', 'Parquero',#71#
        'Servicio de catering',#72#
        'DJ para eventos',#73#
        'Animador de fiestas infantiles',#74#
        'Mozo para eventos',#75#
        'Bartender',#76#
        'Diseño de interiores',#77#
        'Montador de muebles',#78#
        'Costurera',#79#
        'Modista',#80#
        'Sastre',#81#
        'Tapicero',#82#
        'Tornero',#83#
        'Gomería móvil',#84#
        'Lavado de autos a domicilio',#85#
        'Reparación de bicicletas',#86#
        'Maquinista rural',#87#
        'Peón rural',#88#
        'Cuidador de campo',#89#
        'Apicultor',#90#
        'Viverista',#91#
        'Cortador de leña',#92#
        'Operario de maquinaria pesada',#93#
        'Zanellero',#94#
        'Herrador',#95#
        'Pintura artística',#96#
        'Diseño de tatuajes',#97#
        'Tatuador',#98#
        'Estilista canino'#99#
    ]

    for titulo in oficios:
        db.add(Servicio(titulo=titulo))
    db.commit()
    return {"mensaje": f"Se insertaron {len(oficios)} oficios"}
##############################################################
@app.post("/tracking/")
def registrar_tracking(datos: TrackingIn, db: Session = Depends(get_db)):
    nuevo = Tracking(**datos.dict())
    db.add(nuevo)
    db.commit()
    return {"ok": True}

##############################################################

@app.get("/ver_servicios_trabajadores/")
def ver_servicios_trabajadores(db: Session = Depends(get_db)):
    filas = db.query(Servicios_Trabajadores).all()
    return [
        {
            "servicio_id": f.servicio_id,
            "trabajador_id": f.trabajador_id,
            "precioxhora": f.precioxhora
        }
        for f in filas
    ]
##############################################################
@app.get("/todos_trabajadores/")
def todos_trabajadores(db: Session = Depends(get_db)):
    return db.query(Trabajador).all()
##############################################################
@app.post("/registro/", status_code=status.HTTP_201_CREATED)
############### podificado por gpt
async def crear_registro_Trabajador(registro: TrabajadorBase, db: db_dependency):
    db_registro = Trabajador(**registro.dict())
    db.add(db_registro)
    db.commit()
    db.refresh(db_registro)
    return {"mensaje": "Registro exitoso", "id": db_registro.id}
##############################################################

@app.get("/Servicios_React/")
async def Servicios(db: Session = Depends(get_db)):

    # Cuento los registros de servicios_trabajadores existentes
    db_servicios = db.query(Servicio.id).all()
    tags = [row[0] for row in db_servicios] 
    # Selecciono las columnas a listar: Joint de las 3 tablas de 
    db_stmt = select(Servicio.titulo).select_from (Servicio) 
    
    # ejecuto la consulta
    result = db.execute(db_stmt)
    # asigno los valores a los 4 campos seleccionados
    servicio =  [row[0] for row in result]

    a=''
    #genero tantos strings al front como registros existen de servicios_trabajadores
    for i in range(0, len(tags)):
        a = a +str(tags[i])+' '+str(servicio[i])+'---'
    a = a.split(sep='---', maxsplit=-1)
    a.pop()
    a = [
    #{int(linea.split(' ', 1)[0]), linea.split(' ', 1)[1]}
    {"id": int(linea.split(' ', 1)[0]), "nombre": linea.split(' ', 1)[1]}
    
    for linea in a]
    return {'RegLog': a }
####################################################

@app.get("/Servicios/")
async def Servicios(db: Session = Depends(get_db)):

    # Cuento los registros de servicios_trabajadores existentes
    db_servicios = db.query(Servicio.id).all()
    tags = [row[0] for row in db_servicios] 
    # Selecciono las columnas a listar: Joint de las 3 tablas de 
    db_stmt = select(Servicio.titulo).select_from (Servicio) 
    
    # ejecuto la consulta
    result = db.execute(db_stmt)
    # asigno los valores a los 4 campos seleccionados
    servicio =  [row[0] for row in result]

    a=''
    #genero tantos strings al front como registros existen de servicios_trabajadores
    for i in range(0, len(tags)):
        a = a +str(servicio[i])+'---'
    a = a.split(sep='---', maxsplit=-1)
    a.pop()
    return {'RegLog': a }
####################################################
### ahora opiniones
from fastapi import Request

@app.post("/opiniones/{param}")
async def crear_opinion(param: int, request: Request, db: Session = Depends(get_db)):
    data = await request.json()
    comentario = data.get("comentario")
    calificacion = data.get("calificacion")
    if comentario is None or calificacion is None:
        raise HTTPException(status_code=400, detail="Faltan campos requeridos")
    nueva_opinion = Opinion(
        trabajador_id=param,
        comentario=comentario,
        calificacion=calificacion,
    )
    db.add(nueva_opinion)
    db.commit()
    db.refresh(nueva_opinion)
    return {"mensaje": "Opinión registrada con éxito", "id": nueva_opinion.id}

####################################################
@app.get("/opiniones_por_trabajador/{trabajador_id}")
def opiniones_por_trabajador(trabajador_id: int, db: Session = Depends(get_db)):
    opiniones = db.query(Opinion).filter(Opinion.trabajador_id == trabajador_id).order_by(Opinion.id.desc()).all()
    return opiniones
####################################################
@app.get("/Listo_trabajadoresPorServicio/{titulo_servicio}")
def listar_trabajadores_por_servicio(titulo_servicio: str, db: Session = Depends(get_db)):
    consulta = (
        db.query(Servicio.titulo, Trabajador.id, Trabajador.nombre, Trabajador.penales, Trabajador.foto, Trabajador.wsapp, Trabajador.latitud, Trabajador.longitud)
        .join(Servicios_Trabajadores, Servicio.id == Servicios_Trabajadores.servicio_id)
        .join(Trabajador, Trabajador.id == Servicios_Trabajadores.trabajador_id)
        .filter(Servicio.titulo == titulo_servicio)
        .all()
    )

    resultado = [
        {
            "servicio": row[0],
            "id": row[1],
            "nombre": row[2],
            "penales": row[3],
            "foto": row[4],
            "wsapp": row[5],
            "Latitud": row[6],
            "Longitud": row[7]
        }
        for row in consulta
    ]

    return {"trabajadores": resultado}
####################################################
##################################################
@app.post("/Relacionar_Trabajador_Servicio/", status_code=201)
async def crear_Relacion_Trabajador_Servicio(registro: ServicioTrabajadorBase, db: db_dependency):
    db_registro = Servicios_Trabajadores(**registro.dict())
    db_registro.id = int(str(db_registro.servicio_id) + str(db_registro.trabajador_id))
    db.add(db_registro)
    db.commit()
    return {"mensaje": "Relación creada correctamente"}
####################################################
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
