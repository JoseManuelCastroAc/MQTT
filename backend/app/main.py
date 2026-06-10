from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from . import models, schemas, auth, database

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="SMAT API - Unidad I")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/token", tags=["Seguridad"])
def login():
    return {
        "access_token": auth.crear_token({"sub": "admin_fisi"}),
        "token_type": "bearer",
    }


@app.get("/estaciones/", response_model=list[schemas.Estacion], tags=["SMAT"])
def listar_estaciones(db: Session = Depends(database.get_db)):
    estaciones = db.query(models.EstacionDB).all()
    resultado = []

    for estacion in estaciones:
        ultima_lectura = (
            db.query(models.LecturaDB)
            .filter(models.LecturaDB.estacion_id == estacion.id)
            .order_by(models.LecturaDB.id.desc())
            .first()
        )

        resultado.append(
            {
                "id": estacion.id,
                "nombre": estacion.nombre,
                "ubicacion": estacion.ubicacion,
                "ultimo_valor": ultima_lectura.valor if ultima_lectura else None,
            }
        )

    return resultado


@app.post("/estaciones/", status_code=201, tags=["SMAT"])
def crear_estacion(
    estacion: schemas.EstacionCreate,
    db: Session = Depends(database.get_db),
    user=Depends(auth.validar_token),
):
    nueva = models.EstacionDB(**estacion.dict())
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return nueva


@app.put("/estaciones/{id}", tags=["SMAT"])
def editar_estacion(
    id: int,
    estacion: schemas.EstacionUpdate,
    db: Session = Depends(database.get_db),
    user=Depends(auth.validar_token),
):
    estacion_db = (
        db.query(models.EstacionDB)
        .filter(models.EstacionDB.id == id)
        .first()
    )

    if not estacion_db:
        raise HTTPException(status_code=404, detail="Estación no encontrada")

    estacion_db.nombre = estacion.nombre
    estacion_db.ubicacion = estacion.ubicacion

    db.commit()
    db.refresh(estacion_db)

    return estacion_db


@app.delete("/estaciones/{id}", tags=["SMAT"])
def eliminar_estacion(
    id: int,
    db: Session = Depends(database.get_db),
    user=Depends(auth.validar_token),
):
    estacion_db = (
        db.query(models.EstacionDB)
        .filter(models.EstacionDB.id == id)
        .first()
    )

    if not estacion_db:
        raise HTTPException(status_code=404, detail="Estación no encontrada")

    db.delete(estacion_db)
    db.commit()

    return {"mensaje": "Estación eliminada correctamente"}


@app.post("/lecturas/", status_code=201, tags=["Telemetría"])
def registrar_lectura(
    lectura: schemas.LecturaCreate,
    db: Session = Depends(database.get_db),
    user=Depends(auth.validar_token),
):
    estacion = (
        db.query(models.EstacionDB)
        .filter(models.EstacionDB.id == lectura.estacion_id)
        .first()
    )

    if not estacion:
        raise HTTPException(status_code=404, detail="Estación no encontrada")

    nueva_lectura = models.LecturaDB(**lectura.dict())
    db.add(nueva_lectura)
    db.commit()
    db.refresh(nueva_lectura)

    return {"status": "Lectura registrada con éxito"}