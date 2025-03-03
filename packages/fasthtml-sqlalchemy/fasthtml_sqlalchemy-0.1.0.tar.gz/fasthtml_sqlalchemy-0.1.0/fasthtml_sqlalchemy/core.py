from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from fasthtml import FastHTML

class SQLAlchemy:
    def __init__(self, app: FastHTML = None):
        self.app = app
        self.engine = None
        self.session = None
        self.Model = declarative_base()

        if app is not None:
            self.init_app(app)

    def init_app(self, app: FastHTML):
        """Inicializa SQLAlchemy con la aplicación FastHTML."""
        self.app = app
        database_uri = app.config.get('SQLALCHEMY_DATABASE_URI', 'sqlite:///:memory:')
        self.engine = create_engine(database_uri)
        self.session = scoped_session(sessionmaker(bind=self.engine))

        # Añadir un manejador para cerrar la sesión al final de cada solicitud
        @app.before_request
        def before_request():
            self.session()

        @app.after_request
        def after_request(response):
            self.session.remove()
            return response

    def create_all(self):
        """Crea todas las tablas en la base de datos."""
        self.Model.metadata.create_all(bind=self.engine)

    def drop_all(self):
        """Elimina todas las tablas de la base de datos."""
        self.Model.metadata.drop_all(bind=self.engine)