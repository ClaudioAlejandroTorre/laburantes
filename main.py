from datetime import datetime, timezone
from fastapi import FastAPI, Depends
from sqlalchemy import (
    create_engine, Column, Integer, Float, String, ForeignKey, DateTime,
    UniqueConstraint
)
from sqlalchemy.orm import declarative_base, relationship, Session
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from typing import Annotated

# --- Configuración conexión a PostgreSQL (ajusta usuario, pass, host, puerto, dbname)
#DATABASE_URL = "postgresql+psycopg2://mtNUViyTddNAbZhAVZP6R23G9k0BFcJY:mtNUViyTddNAbZhAVZP6R23G9k0BFcJY@host:5432/laburantes_db"
DATABASE_URL = "postgresql://laburantes_db_user:mtNUViyTddNAbZhAVZP6R23G9k0BFcJY@dpg-d1m3kqa4d50c738f4a7g-a/laburantes_db"

engine = create_engine(DATABASE_URL, echo=True)  # echo=True para logs SQL

Base = declarative_base()

# --- MODELOS

class Servicios_Trabajadores(Base):
    __tablename__ = 'servicios_trabajadores'
    id = Column(Integer, primary_key=True, autoincrement=True)  # NUEVO
    servicio_id = Column(ForeignKey('servicios.id'))
    trabajador_id = Column(ForeignKey('trabajadores.id'))
    precioxhora = Column(Integer)


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
        'Albañil','Informático','Mozo','Programador Web','Programador Front End','Programador Back End','Vendedor' ,'Vendedor Ambulante' ,'Ayudante de Cocina' ,'Chapista' ,'Membranas', 'Zinguero','Empleada Doméstica' ,'Enfermera - Enfermero', 'Perforaciones','Taxista','Electricista','Electricista del Automotor' ,'Plomero', 'Gasista matriculado', 'Carpintero', 'Pintor',
        'Cerrajero', 'Techista', 'Colocador de cerámicos', 'Colocador de durlock', 'Soldador',
        'Mecánico automotor','Delyvery','Remisse', 'Mecánico de motos', 'Reparador de electrodomésticos', 'Herrero',
        'Jardinero', 'Podador', 'Cuidadores de adultos mayores', 'Niñera', 'Maestra particular',
        'Cocinero a domicilio', 'Delivery con moto', 'Mudanzas y fletes', 'Peluquero/a',
        'Manicuría y pedicuría', 'Estética y depilación', 'Masajista', 'Personal trainer',
        'Entrenador deportivo', 'Profesor de música', 'Profesor de inglés','Profesor de Matemáticas' ,' Profesor de Gimnasia','Profesor de Danzas' ,'Profesor de Música' ,'Clases de apoyo escolar',
        'Diseñador gráfico', 'Diseñador web', 'Fotógrafo', 'Videógrafo', 'Community manager',
        'Desarrollador de software', 'Técnico en computación', 'Armado y reparación de PC',
        'Instalador de cámaras de seguridad', 'Instalador de redes', 'Servicio de limpieza',
        'Limpieza de vidrios', 'Limpieza final de obra', 'Cuidado de mascotas', 'Paseador de perros',
        'Adiestrador canino', 'Yesero', 'Parquero', 'Servicio de catering', 'DJ para eventos',
        'Animador de fiestas infantiles', 'Mozo para eventos', 'Bartender', 'Diseño de interiores',
        'Montador de muebles', 'Costurera', 'Modista', 'Sastre', 'Tapicero', 'Tornero',
        'Gomería móvil', 'Lavado de autos a domicilio', 'Reparación de bicicletas',
        'Maquinista rural', 'Peón rural', 'Cuidador de campo', 'Apicultor', 'Viverista',
        'Cortador de leña', 'Operario de maquinaria pesada', 'Zanellero', 'Herrador',
        'Pintura artística', 'Diseño de tatuajes', 'Tatuador', 'Estilista canino'
    ]

    for titulo in oficios:
        db.add(Servicio(titulo=titulo))
    db.commit()
    return {"mensaje": f"Se insertaron {len(oficios)} oficios"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
