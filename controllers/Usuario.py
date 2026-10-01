from flask import render_template, request, redirect, url_for, flash, abort
from werkzeug.security import check_password_hash, generate_password_hash
from models import Usuario
from utils import db, lm
from flask import Blueprint
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename

EXTENSOES_PERMITIDAS = {'png', 'jpg', 'jpeg', 'webp'}

bp_usuario = Blueprint("usuario", __name__, template_folder='templates')

@bp_usuario.route('/get')
#@login_required
def get():
	if current_user.administrador:
		usuarios = Usuario.query.all()
		return render_template('usuario_get.html', usuarios=usuarios)
	else:
		abort(403)  # Acesso negado
		#flash('Acesso restrito.', 'error')
		#return redirect(url_for('admin'))

@bp_usuario.route('/add', methods=['GET', 'POST'])
def add():
	if request.method=="GET":
		return render_template('usuario_add.html')

	arquivo = request.files.get('imagem')
	caminho_imagem = None

	if arquivo and arquivo.filename != '':
		nome = secure_filename(arquivo.filename)
		extensao = arquivo.filename.split('.')[-1].lower()
		if extensao not in EXTENSOES_PERMITIDAS:
			flash('Formato de imagem inválido. Formatos permitidos: PNG, JPG, JPEG, WEBP.', 'error')
			return redirect(url_for('.add'))

		novo_nome = f"{uuid.uuid4().hex}.{extensao}"
		caminho = os.path.join(current_app.config['UPLOAD_FOLDER'], novo_nome)
		arquivo.save(caminho)
		caminho_imagem = f"uploads/users/{novo_nome}"  # Caminho relativo para uso no HTML
		
	user = Usuario(
		request.form.get('nome'), 
		request.form.get('email'), 
		generate_password_hash(request.form.get('senha')), 
		caminho_imagem,
		request.form.get('administrador') == 'on'
	)
		
	db.session.add(user)
	db.session.commit()
	flash('Dados adicionados com sucesso', 'success')
	return redirect(url_for('.get'))

@bp_usuario.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
	u = Usuario.query.get(id)
	if request.method=="GET":
		return render_template('usuario_update.html', u=u)
	elif request.method=="POST":
		arquivo = request.files.get('imagem')
		caminho_imagem = None

		if arquivo and arquivo.filename != '':
			nome = secure_filename(arquivo.filename)
			extensao = arquivo.filename.split('.')[-1].lower()
			if extensao not in EXTENSOES_PERMITIDAS:
				flash('Formato de imagem inválido. Formatos permitidos: PNG, JPG, JPEG, WEBP.', 'error')
				return redirect(url_for('.add'))

			novo_nome = f"{uuid.uuid4().hex}.{extensao}"
			caminho = os.path.join(current_app.config['UPLOAD_FOLDER'], novo_nome)
			arquivo.save(caminho)
			caminho_imagem = f"uploads/users/{novo_nome}"  # Caminho relativo para uso no HTML
			
		user = Usuario(
			request.form.get('nome'), 
			request.form.get('email'), 
			generate_password_hash(request.form.get('senha')), 
			caminho_imagem,
			request.form.get('administrador') == 'on'
		)

		db.session.add(u)
		db.session.commit()
		flash('Dados atualizados com sucesso', 'success')
		return redirect(url_for('.get'))

@bp_usuario.route('/alterar-senha', methods=['GET', 'POST'])
def alterar_senha():
	if request.method == 'POST':
		email = request.form.get('email')
		senha_atual = request.form.get('senha_atual')
		nova_senha = request.form.get('nova_senha')
		confirmacao = request.form.get('confirmacao')
		u = Usuario.query.filter_by(email=email).first()

		if not u or not check_password_hash(u.senha, senha_atual):
			flash('E-mail ou senha atual inválidos.', 'error')
		elif nova_senha != confirmacao:
			flash('A confirmação da nova senha não confere.', 'error')
		else:
			u.senha = generate_password_hash(nova_senha)
			db.session.commit()
			flash('Senha alterada com sucesso.', 'success')
			return redirect(url_for('login'))

	return render_template('usuario_senha.html')

@bp_usuario.route('/delete/<int:id>')
def delete(id):
	u = Usuario.query.get(id)
	db.session.delete(u)
	db.session.commit()
	flash('Dados excluídos com sucesso', 'success')
	return redirect(url_for('.get'))

@lm.user_loader
def load_user(id):
	usuario = Usuario.query.filter_by(id=id).first()
	return usuario

@bp_usuario.route('/logout')
def logout():
	logout_user()
	flash('Você saiu do sistema.', 'success')
	return redirect(url_for('login'))

@bp_usuario.route('/autenticar', methods=['POST'])
def autenticar():
	email = request.form.get('email')
	senha = request.form.get('senha')
	usuario = Usuario.query.filter_by(email=email).first()
	if usuario and check_password_hash(usuario.senha, senha):
		login_user(usuario)
		return redirect(url_for('admin'))
	else:
		flash('Usuário ou senha inválidos')
		return redirect(url_for('login'))
	
@bp_usuario.errorhandler(403)
def acesso_negado(error):
    return render_template('acesso_negado.html'), 403