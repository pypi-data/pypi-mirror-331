from .core import SQLAlchemy

db = SQLAlchemy()

def query_to_dict(query):
    """Convierte una consulta de SQLAlchemy en un diccionario."""
    return [row._asdict() for row in query]