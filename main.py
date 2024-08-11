from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
from bs4 import BeautifulSoup
from bson.objectid import ObjectId
from datetime import datetime

def crear_app():
        app = Flask(__name__)
        app.secret_key = 'your_secret_key'

        app.config['MONGO_URI'] = "mongodb+srv://badjuan453:Badillo12@cluster0.roexaww.mongodb.net/Integradora"
        mongo = PyMongo(app)

        # Cargar el contenido estático en una variable
        def load_static_content():
            content = ""
            files = ['templates/informacion.html', 'templates/datos_curiosos.html', 'templates/que_es_ciberseguridad.html',
                     'templates/info_ciberseguridad.html']
            for file in files:
                with open(file, 'r', encoding='utf-8') as f:
                    content += f.read().lower()
            return content

        content = load_static_content()

        @app.route('/')
        def index():
            if 'user_id' in session:
                return render_template('inicio.html')
            return redirect(url_for('login'))

        @app.route('/login', methods=['GET', 'POST'])
        def login():
            if request.method == 'POST':
                username = request.form['username']
                password = request.form['password']
                user = mongo.db.InicioSesion.find_one({'username': username})
                if user and check_password_hash(user['password'], password):
                    session['user_id'] = str(user['_id'])
                    return redirect(url_for('index'))
                else:
                    flash('Login fallido. Por favor, verifica tu nombre de usuario y contraseña', 'danger')
            return render_template('login.html')

        @app.route('/register', methods=['GET', 'POST'])
        def register():
            if request.method == 'POST':
                try:
                    username = request.form['username']
                    email = request.form['email']
                    password = request.form['password']

                    if not username or not email or not password:
                        flash('Todos los campos son obligatorios', 'error')
                        return redirect(url_for('register'))

                    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
                    mongo.db.InicioSesion.insert_one({
                        'username': username,
                        'email': email,
                        'password': hashed_password
                    })

                    flash('Cuenta creada exitosamente', 'success')
                    return redirect(url_for('login'))
                except Exception as e:
                    flash(f'Ocurrió un error: {str(e)}', 'error')
                    return redirect(url_for('register'))
            return render_template('register.html')

        @app.route('/logout')
        def logout():
            session.pop('user_id', None)
            return redirect(url_for('login'))

        @app.route('/add', methods=['POST'])
        def add_data():
            try:
                data = request.json
                if data:
                    mongo.db.InicioSesion.insert_one(data)
                    return jsonify({"message": "Datos agregados exitosamente"}), 201
                return jsonify({"error": "No se proporcionaron datos"}), 400
            except Exception as e:
                return jsonify({"error": str(e)}), 500

        @app.route('/informacion')
        def informacion():
            if 'user_id' not in session:
                return redirect(url_for('login'))
            return render_template('informacion.html')

        @app.route('/datos_curiosos')
        def datos_curiosos():
            if 'user_id' not in session:
                return redirect(url_for('login'))
            return render_template('datos_curiosos.html')

        @app.route('/que_es_ciberseguridad')
        def que_es_ciberseguridad():
            if 'user_id' not in session:
                return redirect(url_for('login'))
            return render_template('que_es_ciberseguridad.html')

        @app.route('/info_ciberseguridad')
        def info_ciberseguridad():
            if 'user_id' not in session:
                return redirect(url_for('login'))
            return render_template('info_ciberseguridad.html')

        @app.route('/nosotros')
        def nosotros():
            if 'user_id' not in session:
                return redirect(url_for('login'))
            return render_template('nosotros.html')

        @app.route('/mejores_practicas')
        def mejores_practicas():
            return render_template('mejores_practicas.html')

        @app.route('/consejos_seguridad')
        def consejos_seguridad():
            if 'user_id' not in session:
                return redirect(url_for('login'))
            return render_template('consejos_seguridad.html')

        @app.route('/recursos')
        def recursos():
            if 'user_id' not in session:
                return redirect(url_for('login'))
            return render_template('recursos.html')

        @app.route('/search_static')
        def search_static():
            if 'user_id' not in session:
                return redirect(url_for('login'))
            query = request.args.get('query', '').lower()
            results = []

            if query:
                files = [
                    'templates/informacion.html', 'templates/datos_curiosos.html', 'templates/que_es_ciberseguridad.html',
                    'templates/info_ciberseguridad.html', 'templates/index.html', 'templates/login.html',
                    'templates/register.html', 'templates/inicio.html', 'templates/search_results_static.html'
                ]

                for file in files:
                    with open(file, 'r', encoding='utf-8') as f:
                        content = f.read().lower()
                        soup = BeautifulSoup(content, 'html.parser')
                        text = soup.get_text()
                        if query in text:
                            start_idx = text.find(query)
                            snippet = text[start_idx:start_idx + 200]
                            results.append({'file': file, 'snippet': snippet})

                return render_template('search_results_text.html', query=query, results=results)
            return jsonify({'error': 'No query provided'}), 400

        @app.route('/discusiones')
        def listar_discusiones():
            if 'user_id' not in session:
                return redirect(url_for('login'))

            page = int(request.args.get('page', 1))
            per_page = 10
            total = mongo.db.discusiones.count_documents({})
            discusiones = mongo.db.discusiones.find().skip((page - 1) * per_page).limit(per_page)
            autores = {str(user['_id']): user['username'] for user in mongo.db.InicioSesion.find()}

            return render_template(
                'listar_discusiones.html',
                discusiones=discusiones,
                autores=autores,
                page=page,
                total=total,
                per_page=per_page
            )

        @app.route('/discusiones/nueva', methods=['GET', 'POST'])
        def nueva_discusion():
            if 'user_id' not in session:
                return redirect(url_for('login'))
            if request.method == 'POST':
                titulo = request.form['titulo']
                contenido = request.form['contenido']
                autor_id = session.get('user_id')
                autor = mongo.db.InicioSesion.find_one({'_id': ObjectId(autor_id)})
                autor_nombre = autor['username'] if autor else 'Desconocido'
                fecha_creacion = datetime.utcnow()

                if not titulo or not contenido or not autor_nombre:
                    flash('Todos los campos son obligatorios', 'error')
                    return redirect(url_for('nueva_discusion'))

                mongo.db.discusiones.insert_one({
                    'titulo': titulo,
                    'contenido': contenido,
                    'autor': str(autor['_id']),
                    'fecha_creacion': fecha_creacion
                })
                flash('Discusión creada exitosamente', 'success')
                return redirect(url_for('listar_discusiones'))
            return render_template('nueva_discusion.html')

        @app.route('/discusiones/<id>')
        def ver_discusion(id):
            if 'user_id' not in session:
                return redirect(url_for('login'))

            discusion = mongo.db.discusiones.find_one({'_id': ObjectId(id)})
            if discusion:
                comentarios = list(mongo.db.comentarios.find({'discusion_id': ObjectId(id)}))
                autores = {str(user['_id']): user['username'] for user in mongo.db.InicioSesion.find()}
                return render_template('ver_discusion.html', discusion=discusion, comentarios=comentarios, autores=autores)
            else:
                flash('Discusión no encontrada', 'error')
                return redirect(url_for('listar_discusiones'))

        @app.route('/discusiones/<id>/comentar', methods=['POST'])
        def agregar_comentario(id):
            if 'user_id' not in session:
                return redirect(url_for('login'))
            contenido = request.form['contenido']
            autor_id = session.get('user_id')
            autor = mongo.db.InicioSesion.find_one({'_id': ObjectId(autor_id)})
            autor_nombre = autor['username'] if autor else 'Desconocido'
            fecha_creacion = datetime.utcnow()

            if not contenido or not autor_nombre:
                flash('Todos los campos son obligatorios', 'error')
                return redirect(url_for('ver_discusion', id=id))

            mongo.db.comentarios.insert_one({
                'discusion_id': ObjectId(id),
                'contenido': contenido,
                'autor': str(autor['_id']),
                'fecha_creacion': fecha_creacion
            })
            flash('Comentario agregado exitosamente', 'success')
            return redirect(url_for('ver_discusion', id=id))
        return app
if __name__ == '_main_':
    app = crear_app()
    app.run(host="localhost", debug=True, port=3000)