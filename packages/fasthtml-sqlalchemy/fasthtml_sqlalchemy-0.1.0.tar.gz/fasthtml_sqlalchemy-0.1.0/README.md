# fasthtml-sqlalchemy
Integración de SqlAlchemy con el framework fastHTML

## Instalación
pip install fasthtml-sqlalchemy

## Ejemplo de uso:

```python:
from fasthtml import FastHTML
from fasthtml_sqlalchemy import SQLAlchemy, BaseModel

app = FastHTML()
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'

db = SQLAlchemy(app)

class User(BaseModel):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)

db.create_all()

@app.route("/")
def get():
    users = db.session.query(User).all()
    return str(users)

@app.route("/add/<username>")
def add(username):
    user = User(username=username)
    user.save()
    return f"User {username} added!"

if __name__ == "__main__":
    app.serve()
```

y la ayuda sigue por aquí ...