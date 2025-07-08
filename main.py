from datetime import datetime, timezone
from fastapi import FastAPI, HTTPException, Depends, status
from sqlalchemy import create_engine, Column, Integer, Float, String, ForeignKey, select, DateTime
from sqlalchemy.orm import declarative_base, relationship, joinedload, sessionmaker, Session
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from typing import List, Optional, Annotated
from pydantic import BaseModel

# Configurar acceso a PostgreSQL en Render
DATABASE_URL = "postgresql+psycopg2://laburantes_db_user:mtNUViyTddNAbZhAVZP6R23G9k0BFcJY@dpg-d1m3kqa4d50c738f4a7g-a.virginia-postgres.render.com/laburantes_db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

app = FastAPI()

app.mount("/static", StaticFiles(directory="fotos"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MODELOS SQLALCHEMY
class Usuarios_Servicios_Trabajadores(Base):
    __tablename__ = 'usuarios_servicios_trabajadores'
    usuario_id = Column(ForeignKey('usuarios.id'), primary_key=True)
    servicio_trabajador_id = Column(ForeignKey('servicios_trabajadores.id'), primary_key=True)

class Servicios_Trabajadores(Base):
    __tablename__ = 'servicios_trabajadores'
    id = Column(Integer, primary_key=True)
    servicio_id = Column(ForeignKey('servicios.id'), primary_key=True)
    trabajador_id = Column(ForeignKey('trabajadores.id'), primary_key=True)
    precioxhora = Column(Integer)
    usuarios = relationship("Usuario", secondary="usuarios_servicios_trabajadores", back_populates='servicios_trabajadores')

class Servicio(Base):
    __tablename__ = 'servicios'
    id = Column(Integer, primary_key=True)
    titulo = Column(String, nullable=False)
    trabajadores = relationship("Trabajador", secondary="servicios_trabajadores", back_populates='servicios')

class Trabajador(Base):
    __tablename__ = 'trabajadores'
    id = Column(Integer, primary_key=True)
    nombre = Column(String, nullable=False)
    dni = Column(String, nullable=False)
    correoElec = Column(String, nullable=False)
    direccion = Column(String, nullable=False)
    localidad = Column(String, nullable=False)
    latitud = Column(Float)
    longitud = Column(Float)
    wsapp = Column(String, nullable=False)
    foto = Column(String, nullable=False)
    penales = Column(String, nullable=False)
    servicios = relationship("Servicio", secondary="servicios_trabajadores", back_populates='trabajadores')

class Opinion(Base):
    __tablename__ = 'opiniones'
    id = Column(Integer, primary_key=True, index=True)
    trabajador_id = Column(Integer)
    comentario = Column(String, nullable=False)
    calificacion = Column(Integer, nullable=False)
    fecha = Column(DateTime, default=datetime.now(timezone.utc))

class Usuario(Base):
    __tablename__ = 'usuarios'
    id = Column(Integer, primary_key=True)
    nombre = Column(String, nullable=False)
    dni = Column(String, nullable=False)
    correoElec = Column(String, nullable=False)
    direccion = Column(String, nullable=False)
    localidad = Column(String, nullable=False)
    wsapp = Column(String, nullable=False)
    servicios_trabajadores = relationship("Servicios_Trabajadores", secondary="usuarios_servicios_trabajadores", back_populates='usuarios')

Base.metadata.create_all(engine)

# Pydantic models para entrada/salida
class TrabajadorBase(BaseModel):
    nombre: str
    dni: str
    correoElec: str
    direccion: str
    localidad: str
    latitud: float
    longitud: float
    wsapp: str
    foto: str
    penales: str

class ServicioBase(BaseModel):
    titulo: str

class UsuarioBase(BaseModel):
    nombre: str
    dni: str
    correoElec: str
    direccion: str
    localidad: str
    wsapp: str

class ServicioTrabajadorBase(BaseModel):
    servicio_id: int
    trabajador_id: int
    precioxhora: Optional[int] = None

class OpinionCreate(BaseModel):
    comentario: str
    calificacion: int

class ServicioSchema(ServicioBase):
    trabajadores: List[TrabajadorBase]
    class Config:
        orm_mode = True

class TrabajadorSchema(TrabajadorBase):
    servicios: List[ServicioBase]
    class Config:
        orm_mode = True

# Dependencia

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

# ENDPOINTS
@app.post("/registro/", status_code=status.HTTP_201_CREATED)
async def crear_registro_Trabajador(registro: TrabajadorBase, db: db_dependency):
    db_registro = Trabajador(**registro.dict())
    db.add(db_registro)
    db.commit()
    db.refresh(db_registro)
    return {"mensaje": "Registro exitoso", "id": db_registro.id}

@app.get("/Servicios/")
async def listar_servicios(db: Session = Depends(get_db)):
    servicios = db.query(Servicio).all()
    return {"RegLog": [{"id": s.id, "nombre": s.titulo} for s in servicios]}

@app.post("/Relacionar_Trabajador_Servicio/", status_code=201)
async def crear_relacion(registro: ServicioTrabajadorBase, db: db_dependency):
    db_registro = Servicios_Trabajadores(**registro.dict())
    db_registro.id = int(str(db_registro.servicio_id) + str(db_registro.trabajador_id))
    db.add(db_registro)
    db.commit()
    return {"mensaje": "Relación creada correctamente"}

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

@app.get("/opiniones_por_trabajador/{trabajador_id}")
def opiniones_por_trabajador(trabajador_id: int, db: Session = Depends(get_db)):
    opiniones = db.query(Opinion).filter(Opinion.trabajador_id == trabajador_id).order_by(Opinion.id.desc()).all()
    return opiniones

@app.post("/opiniones/{param}")
def crear_opinion(param: int, opinion: OpinionCreate, db: Session = Depends(get_db)):
    nueva_opinion = Opinion(
        trabajador_id=param,
        comentario=opinion.comentario,
        calificacion=opinion.calificacion,
    )
    db.add(nueva_opinion)
    db.commit()
    db.refresh(nueva_opinion)
    return {"mensaje": "Opinión registrada con éxito", "id": nueva_opinion.id}
