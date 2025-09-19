from flask import Flask, render_template , request, flash, redirect, url_for
import fdb
from flask_bcrypt import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'sua_chave_secreta_aqui'

host = 'localhost'
database = r'C:\Users\Aluno\Desktop\isadora\LIVRO.FDB'
user = 'SYSDBA'
password = 'sysdba'
con = fdb.connect(host=host, database=database, user=user, password=password)

@app.route('/')
def index():
    cursor = con.cursor()
    cursor.execute("select id_livro, titulo, autor, ano_publicacao from livro")
    livros = cursor.fetchall()
    cursor.close()

    return render_template('livros.html', livros=livros)

@app.route('/novo')
def novo():
    return render_template('novo.html', titulo='Novo Livro')

@app.route('/criar', methods=['POST'])
def criar():
    titulo = request.form['titulo']
    autor = request.form['autor']
    ano_publicacao= request.form['ano_publicacao']

    cursor = con.cursor()
    try:
        cursor.execute('SELECT 1 FROM livro WHERE livro.titulo = ?', (titulo,))
        if cursor.fetchone():
            flash('Esse livro já está cadastrado')
            return redirect(url_for('novo'))
        cursor.execute("insert into livro(titulo, autor, ano_publicacao) values(?, ?, ?)",
                       (titulo, autor, ano_publicacao))
        con.commit()
    finally:
        cursor.close()
    flash('O livro foi cadastrado com sucesso!')
    return redirect(url_for('index'))

@app.route('/atualizar')
def atualizar():
    return render_template('editar.html', titulo='Editar Livro')

@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    cursor = con.cursor()
    cursor.execute("SELECT id_livro, titulo, autor, ano_publicacao FROM livro WHERE id_livro = ?", (id,))
    livro = cursor.fetchone()

    if not livro:
        cursor.close()
        flash("Livro não foi encontrado")
        return redirect(url_for('index'))
    if request.method == 'POST':
        titulo = request.form['titulo']
        autor = request.form['autor']
        ano_publicacao = request.form['ano_publicacao']

        cursor.execute("UPDATE livro SET titulo = ?, autor = ?, ano_publicacao = ? WHERE id_livro = ? ",
                       (titulo, autor, ano_publicacao, id))
        con.commit()
        flash("Livro atualizado com sucesso")
        return redirect(url_for('index'))
    cursor.close()
    return render_template('editar.html', livro=livro, titulo='Editar livro')

@app.route('/deletar/<int:id>', methods=('POST',))
def deletar(id):
    cursor = con.cursor()
    try:
        cursor.execute('DELETE FROM livro WHERE id_livro = ?', (id,))
        con.commit()
        flash('Livro excluído com sucesso!', 'success')
    except Exception as e:
        con.rollback()
        flash('Erro ao excluir o livro.', 'error')
    finally:
        cursor.close()
    return redirect(url_for('index'))


@app.route('/lista_usuario')
def lista_usuario():
    cursor = con.cursor()
    cursor.execute("select id_usuario, nome, email, senha from usuario")
    usuarios = cursor.fetchall()
    cursor.close()

    return render_template('usuarios.html', usuarios=usuarios)

@app.route('/novo_usuario')
def novo_usuario():
    return render_template('novo_usuario.html', titulo='Novo Usuário')


@app.route('/criar_usuario', methods=['GET', 'POST'])
def criar_usuario():
    if  request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha= request.form['senha']
        senha_cripto = generate_password_hash(senha).decode('utf-8')

        cursor = con.cursor()
        try:
            cursor.execute('SELECT 1 FROM usuario WHERE nome = ?', (nome,))
            if cursor.fetchone():
                flash('Esse usuario já está cadastrado')
                return redirect(url_for('novo_usuario'))
            cursor.execute("insert into usuario(nome, email, senha) values(?, ?, ?)",
                           (nome, email, senha_cripto))
            con.commit()
        finally:
            cursor.close()
        flash('O usuario foi cadastrado com sucesso!')
        return redirect(url_for('lista_usuario'))
    return render_template('novo_usuario.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        cursor = con.cursor()
        cursor.execute('SELECT u.SENHA FROM USUARIO u WHERE u.EMAIL  =  ?', (email,))
        login = cursor.fetchone()
        if not login:
            flash('Email não encontrado')
            cursor.close()
        if check_password_hash(login[0], senha):
            flash('Login com sucesso')
            cursor.close()
            return redirect(url_for('lista_usuario'))
        return render_template('login.html')
    return render_template('login.html')


@app.route('/editar_usuario/<int:id>', methods=['GET', 'POST'])
def editar_usuario(id):
    cursor = con.cursor()
    cursor.execute("SELECT id_usuario, nome, email, senha FROM usuario WHERE id_usuario = ?", (id,))
    usuario = cursor.fetchone()

    if not usuario:
        cursor.close()
        flash("Usuário não foi encontrado")
        return redirect(url_for('index'))
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']

        senha_cripto = generate_password_hash(senha).decode('utf-8')

        cursor.execute("UPDATE usuario SET nome = ?, email = ?, senha = ? WHERE id_usuario = ? ",
                       (nome, email, senha_cripto, id))
        con.commit()
        flash("Usuário atualizado com sucesso")
        return redirect(url_for('index'))
    cursor.close()
    return render_template('editar_usuario.html', usuario=usuario, titulo='Editar usuario')


@app.route('/deletar_usuario/<int:id>', methods=('POST',))
def deletar_usuario(id):
    cursor = con.cursor()
    try:
        cursor.execute('DELETE FROM usuario WHERE id_usuario = ?', (id,))
        con.commit()
        flash('Usuário excluído com sucesso!', 'success')
    except Exception as e:
        con.rollback()
        flash('Erro ao excluir o usuário', 'error')
    finally:
        cursor.close()
    return redirect(url_for('lista_usuario'))



if __name__ == '__main__':
    app.run(debug=True)