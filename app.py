from flask import Flask, render_template
import json
from utils import db, lm
import os
from flask_migrate import Migrate
from models import Usuario, Pizza, Pedido, PizzaPedido
from controllers.Usuario import bp_usuario
from controllers.Pizza import bp_pizza
from controllers.Pedido import bp_pedido

app = Flask(__name__)
app.register_blueprint(bp_usuario, url_prefix='/usuario')
app.register_blueprint(bp_pizza, url_prefix='/pizza')
app.register_blueprint(bp_pedido, url_prefix='/pedido')

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'chave-de-desenvolvimento-local')
app.config['UPLOAD_FOLDER'] = os.path.join(app.static_folder, 'uploads')

db_usuario = os.getenv('DB_USERNAME')
db_senha = os.getenv('DB_PASSWORD')
db_mydb = os.getenv('DB_DATABASE')
db_host = os.getenv('DB_HOST')
db_port = os.getenv('DB_PORT')

conexao = f"mysql+pymysql://{db_usuario}:{db_senha}@{db_host}:{db_port}/{db_mydb}"
print(conexao)
app.config['SQLALCHEMY_DATABASE_URI'] = conexao
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024

db.init_app(app)
lm.init_app(app)
migrate = Migrate(app, db)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/cardapio')
def cardapio():
    pizzas = Pizza.query.all()
    return render_template('cardapio.html', pizzas=pizzas)

@app.route('/faleconosco')
def faleconosco():
    return render_template('faleconosco.html')

@app.route('/avaliacoes')
def avaliacoes():
    return render_template('avaliacoes.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html')


@app.route('/teste_insert') 
def teste_insert():
    user = Usuario("Gabriel", "gabriel@ifrn.edu.br", "54321")
    db.session.add(user) #Insert into Usuario(nome, email, senha) values ('Alba Lopes', 'alba.lopes@ifrn.edu.br', '12345')
    db.session.commit()
    return 'Dados inseridos com sucesso!'

@app.route('/teste_select')
def teste_select():
    users = Usuario.query.all()
    #print(users)
    for u in users:
        print (u.nome)

    user = Usuario.query.get(2)
    print (f"O email do usuário de id 2 é {user.email}")

    return 'dados recuperados'

@app.route('/teste_update')
def teste_update():
    user = Usuario.query.get(1)
    user.nome = "Alba L."
    user.senha = "753951"
    db.session.add(user)
    db.session.commit()
    return 'dados alterados com sucesso!'

@app.errorhandler(403)
def acesso_negado(error):
    return render_template('acesso_negado.html'), 403

@app.errorhandler(404)
def pagina_nao_encontrada(error):  
    return render_template('pagina_nao_encontrada.html'), 404