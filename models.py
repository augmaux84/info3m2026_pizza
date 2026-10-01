from utils import db
from flask_login import UserMixin

class Usuario(db.Model, UserMixin):
    __tablename__= "usuario"
    id = db.Column(db.Integer, primary_key = True)
    nome = db.Column(db.String(100))
    email = db.Column(db.String(100))
    senha = db.Column(db.String(200))
    caminho_foto = db.Column(db.String(500))
    administrador = db.Column(db.Boolean, default=False, nullable=False)
    pedidos = db.relationship("Pedido", back_populates="usuario")

    def __init__(self, nome, email, senha, caminho_foto, administrador=False):
        self.nome = nome
        self.email = email
        self.senha = senha
        self.caminho_foto = caminho_foto
        self.administrador = administrador
    
    def __repr__(self):
        return "<Usuario {}>".format(self.nome)

class Pizza(db.Model):
    __tablename__= "pizza"
    id = db.Column(db.Integer, primary_key = True)
    sabor = db.Column(db.String(100))
    preco = db.Column(db.Float)
    imagem = db.Column(db.String(500))
    pedidos = db.relationship("Pedido", secondary="pizza_pedido", back_populates="pizzas")

    def __init__(self, sabor, preco, imagem=None):
        self.sabor = sabor
        self.preco = preco
        self.imagem = imagem
    
    def __repr__(self):
        return "<Pizza {}>".format(self.sabor)

class Pedido(db.Model):
    __tablename__ = "pedido"
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=True)
    usuario = db.relationship("Usuario", back_populates="pedidos")
    pizzas = db.relationship("Pizza", secondary="pizza_pedido", back_populates="pedidos")

    def __repr__(self):
        return "<Pedido {}>".format(self.id)

class PizzaPedido(db.Model):
    __tablename__ = "pizza_pedido"
    pedido_id = db.Column(db.Integer, db.ForeignKey("pedido.id"), primary_key=True)
    pizza_id = db.Column(db.Integer, db.ForeignKey("pizza.id"), primary_key=True)