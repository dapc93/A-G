"""Crea el usuario dueno inicial si no existe ninguno. Uso: python -m app.seed"""

from app.core.security import hash_password
from app.db.session import Base, SessionLocal, engine
from app.models.user import User


def run():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(User).count() > 0:
            print("Ya existen usuarios, no se crea ninguno nuevo.")
            return
        owner = User(
            username="admin",
            full_name="Administrador A&G",
            hashed_password=hash_password("cambiar123"),
            role="owner",
        )
        db.add(owner)
        db.commit()
        print("Usuario 'admin' creado con contrasena temporal 'cambiar123'. Cambiala despues del primer login.")
    finally:
        db.close()


if __name__ == "__main__":
    run()
