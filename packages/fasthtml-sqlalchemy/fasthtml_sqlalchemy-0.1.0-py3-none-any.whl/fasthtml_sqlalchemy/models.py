from .core import SQLAlchemy

db = SQLAlchemy()

class BaseModel(db.Model):
    __abstract__ = True

    def save(self):
        """Guarda el objeto en la base de datos."""
        db.session.add(self)
        db.session.commit()

    def delete(self):
        """Elimina el objeto de la base de datos."""
        db.session.delete(self)
        db.session.commit()