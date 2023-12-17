from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Eventos(db.Model):
    __tablename__ = 'eventos'
    id = db.Column(db.Integer, primary_key=True)

    data_compra = db.Column(db.String(50), nullable=False)
    nome_cliente = db.Column(db.String(50), nullable=False)
    nome_loja = db.Column(db.String(50), nullable=False)
    preco_produto = db.Column(db.String(50), nullable=False)
    metodo_pagamento = db.Column(db.String(50), nullable=False)
    status_pagamento = db.Column(db.String(50), nullable=False)