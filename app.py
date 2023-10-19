from flask import Flask, request, render_template, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
import hashlib
import secrets

app = Flask(__name__)

app.secret_key = secrets.token_hex(16)

# Configura la URL de conexión para MySQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root@localhost/flask-reports'
db = SQLAlchemy(app)


# ---------------- MODELO DB APP
class UserType(db.Model):
    __tablename__ = 'user_type'
        
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50), unique=True, nullable=False)
    id_cargo = db.Column(db.Integer, nullable=False)


class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    id_user = db.Column(db.String(10), unique=True, nullable=False)
    nombre_usuario = db.Column(db.String(100), nullable=False)
    primer_nombre = db.Column(db.String(50), nullable=False)
    segundo_nombre = db.Column(db.String(50))
    primer_apellido = db.Column(db.String(50), nullable=False)
    segundo_apellido = db.Column(db.String(50))
    fecha_ingreso = db.Column(db.String(10), nullable=False)
    fecha_reti = db.Column(db.String(10))
    estado_empleado = db.Column(db.String(10), nullable=False)
    tipo_ingreso = db.Column(db.String(10))
    salariovariable = db.Column(db.String(10))
    ciudad_residencia = db.Column(db.String(50))
    tipo_salario = db.Column(db.String(10))
    area_funcional = db.Column(db.String(50))
    ciudad_labora = db.Column(db.String(50))
    id_cargo = db.Column(db.String(10))
    password = db.Column(db.String(100))

class Deal(db.Model):
    __tablename__ = 'deals'

    id = db.Column(db.Integer, primary_key=True)
    Nombre = db.Column(db.String(255))
    Etapa = db.Column(db.String(255))
    Responsable = db.Column(db.String(255))
    id_user = db.Column(db.Integer)
    Tipo = db.Column(db.String(255))
    Producto = db.Column(db.String(255))
    Cantidad_Productos = db.Column(db.Integer)
    Creado_El = db.Column(db.DateTime)
    Fecha_Inicio = db.Column(db.DateTime)
    Modificado_El = db.Column(db.DateTime)
    Fecha_Cierre = db.Column(db.DateTime)
    Total = db.Column(db.Numeric(10, 2))
    Moneda = db.Column(db.String(3))
    Pais_Operacion = db.Column(db.String(255))
    Ciudad_Operacion = db.Column(db.String(255))
    Id_Prospecto = db.Column(db.Integer)
    Id_Compañia = db.Column(db.Integer)
    Fuente = db.Column(db.String(255))
    Plataforma = db.Column(db.String(255))
    Actividad_Economica = db.Column(db.String(255))


# ---------------- RUTAS APP
@app.route('/')
def index():
    return render_template("login.html")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        id_user = request.form['id_user']
        password = request.form['password']

        # Verifica si el usuario ya existe en la base de datos
        user_exists = User.query.filter_by(id_user=id_user).first()

        if user_exists:
            # Si el usuario ya tiene una contraseña, redirige a la página de inicio de sesión
            if user_exists.password:
                return "Usuario ya cuenta con contraseña creada"
            else:
                # Hashea la contraseña antes de guardarla en la base de datos
                hashed_password = hashlib.sha256(password.encode()).hexdigest()
                user_exists.password = hashed_password
                db.session.commit()
                return redirect(url_for('login'))
        else:
            return "Usuario no creado en la Base de datos"

    return render_template('register.html')



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        id_user = request.form['id_user']
        password = request.form['password']

        user = User.query.filter_by(id_user=id_user).first()

        if user and user.password:
            # Si el usuario existe y tiene una contraseña, verifica la contraseña
            hashed_password = hashlib.sha256(password.encode()).hexdigest()

            if hashed_password == user.password:
                # Inicio de sesión exitoso, establece una sesión para el usuario
                session['user_id'] = user.id
                return redirect(url_for('dashboard'))
            else:
                flash('Contraseña incorrecta. Inténtalo de nuevo', 'error')
        else:
            flash('Usuario no encontrado o no tiene contraseña creada.', 'error')

    return render_template('login.html')



@app.route('/dashboard')
def dashboard():
    if 'user_id' in session:
        # Obtiene el ID de usuario almacenado en la sesión
        user_id = session['user_id']

        # Recupera los datos del usuario desde la base de datos
        user = db.session.get(User, user_id)

        if user:
            # Consulta el tipo de rango de usuario del usuario actual
            user_type = UserType.query.filter_by(id_cargo=user.id_cargo).first()
            
            return render_template("dashboard.html", user=user, user_type=user_type)
    
    # Si el usuario no ha iniciado sesión, redirígelo a la página de inicio de sesión
    return redirect(url_for('login'))


@app.route('/sells/<int:id_user>')
def sells(id_user):
    if 'user_id' in session:
        # Verifica que un usuario haya iniciado sesión en tu aplicación Flask.
        # Esto es importante para asegurarse de que solo los usuarios autenticados tengan acceso.

        # Comprueba que el `id_user` en la URL coincida con el usuario autenticado.
        if id_user == session['user_id']:
            user = User.query.get(id_user)

            if not user:
                return jsonify({'error': 'Usuario no encontrado'}), 404

            # Utiliza `user.id_user` como el valor para filtrar las ventas en lugar de `user.id_cargo`
            ventas = Deal.query.filter(Deal.id_user == user.id_user).all()

            # Convierte los resultados a un formato JSON
            ventas_data = []
            for venta in ventas:
                venta_data = {
                    'id': venta.id,
                    'Nombre': venta.Nombre,
                    'Etapa': venta.Etapa,
                    'Responsable': venta.Responsable,
                    'id_user': venta.id_user,
                    'Tipo': venta.Tipo,
                    'Producto': venta.Producto,
                    'Cantidad_Productos': venta.Cantidad_Productos,
                    'Creado_El': venta.Creado_El.strftime('%Y-%m-%d %H:%M:%S'),
                    'Fecha_Inicio': venta.Fecha_Inicio.strftime('%Y-%m-%d %H:%M:%S'),
                    'Modificado_El': venta.Modificado_El.strftime('%Y-%m-%d %H:%M:%S'),
                    'Fecha_Cierre': venta.Fecha_Cierre.strftime('%Y-%m-%d %H:%M:%S'),
                    'Total': str(venta.Total),
                    'Moneda': venta.Moneda,
                    'Pais_Operacion': venta.Pais_Operacion,
                    'Ciudad_Operacion': venta.Ciudad_Operacion,
                    'Id_Prospecto': venta.Id_Prospecto,
                    'Id_Compañia': venta.Id_Compañia,
                    'Fuente': venta.Fuente,
                    'Plataforma': venta.Plataforma,
                    'Actividad_Economica': venta.Actividad_Economica
                }
                ventas_data.append(venta_data)

            return jsonify(ventas_data)

    # Si el usuario no ha iniciado sesión o el `id_user` en la URL no coincide con el usuario autenticado, puedes devolver un error o redirigir a una página de inicio de sesión, según tus necesidades.
    return jsonify({'error': 'Acceso no autorizado'}), 401

@app.route('/logout')
def logout():
    # Elimina la información de sesión
    session.pop('user_id', None)  # Elimina la clave 'user_id' de la sesión

    # Redirige al usuario a la página de inicio de sesión (o a otra página)
    return redirect(url_for('login'))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
