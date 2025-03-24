from flask import Flask, render_template, request, redirect, url_for, session
from flask import flash
from flask_wtf.csrf import CSRFProtect
from config import DevelopmentConfig
from flask import g
from form import PizzaForm, ClienteForm
from models import db
from models import Venta, DetallePizza, IngredientePizza, User
from flask_login import LoginManager, login_user, logout_user, login_required
import json


from ModelUser import ModelUser


from User import User

app = Flask(__name__)
app.config.from_object(DevelopmentConfig)
csrf = CSRFProtect()
db.init_app(app)
login_manager_app = LoginManager(app)
login_manager_app.login_view = 'login'  
login_manager_app.login_message = "Debes iniciar sesión para acceder a esta página."
login_manager_app.login_message_category = "warning"  
login_manager_app = LoginManager(app)
with app.app_context():
    db.create_all()


PRECIOS = {
    'pequena': 40,
    'mediana': 80,
    'grande': 120
}

COSTO_INGREDIENTE = 10


def agregarPizza(tamano, cantidad, ingredientes):
    ingredientes_lista = ",".join(ingredientes)
    with open("pedidos.txt", "a", encoding="utf-8") as archivo:
        archivo.write(f"{tamano}|{cantidad}|{ingredientes_lista}\n")


def cargarCompra():
    compra = []
    try:
        with open("pedidos.txt", "r", encoding="utf-8") as archivo:
            for linea in archivo:
                datos = linea.strip().split("|")
                if len(datos) >= 3:
                    compra.append({
                        "tamano": datos[0],
                        "cantidad": datos[1],
                        "ingredientes": datos[2].split(",") if datos[2] else []
                    })
    except FileNotFoundError:
        with open("pedidos.txt", "w", encoding="utf-8") as archivo:
            pass
    return compra


def eliminarPizzaEspecifica(indice):
    compra = cargarCompra()
    if 0 <= indice < len(compra):
        compra.pop(indice)
        with open("pedidos.txt", "w", encoding="utf-8") as archivo:
            for pizza in compra:
                ingredientes_lista = ",".join(pizza["ingredientes"])
                archivo.write(
                    f"{pizza['tamano']}|{pizza['cantidad']}|{ingredientes_lista}\n")
        return True
    return False


def vaciarCompra():
    open("pedidos.txt", "w").close()


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@login_manager_app.user_loader
def load_user(id):
    return ModelUser.get_by_id(db, id)


@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User(0, request.form['username'], request.form['password'])
        logged_user = ModelUser.login(db, user)
        if logged_user != None:
            if logged_user.password:
                login_user(logged_user)
                return redirect(url_for('home'))
            else:
                flash("Invalid password...")
                return render_template('auth/login.html')
        else:
            flash("User not found...")
            return render_template('auth/login.html')
    else:
        return render_template('auth/login.html')


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))  


@app.route("/home", methods=['GET', 'POST'])
@login_required
def home():
    pizza_form = PizzaForm()
    cliente_form = ClienteForm()

    if 'cliente_data' in session:
        cliente_form.nombre.data = session['cliente_data'].get('nombre', '')
        cliente_form.direccion.data = session['cliente_data'].get(
            'direccion', '')
        cliente_form.telefono.data = session['cliente_data'].get(
            'telefono', '')

    if request.method == 'POST' and pizza_form.validate_on_submit():
        session['cliente_data'] = {
            'nombre': cliente_form.nombre.data,
            'direccion': cliente_form.direccion.data,
            'telefono': cliente_form.telefono.data
        }

        if not pizza_form.ingredientes.data:
            flash('Debes seleccionar al menos un ingrediente', 'danger')
            return redirect(url_for('home'))

        agregarPizza(pizza_form.tamano.data, pizza_form.numPizzas.data,
                     pizza_form.ingredientes.data)
        flash('Pizza agregada a la compra', 'success')
        return redirect(url_for('home'))

    compra = cargarCompra()

    ventas_hoy = []
    try:
        ventas_hoy = Venta.query.filter(db.func.date(
            Venta.fecha) == db.func.current_date()).all()
    except:
        ventas_hoy = []

    return render_template('index.html',
                           pizza_form=pizza_form,
                           cliente_form=cliente_form,
                           compra=compra,
                           ventas_hoy=ventas_hoy)


@app.route('/finalizarPedido', methods=['GET', 'POST'])
@login_required
def finalizarPedido():
    cliente_form = ClienteForm()
    pizzas = cargarCompra()

    if not pizzas:
        flash("No hay pizzas en la compra", "danger")
        return redirect(url_for('home'))

    if request.method == 'POST':
        if cliente_form.validate_on_submit():
            nombre = cliente_form.nombre.data
            direccion = cliente_form.direccion.data
            telefono = cliente_form.telefono.data

            session['cliente_data'] = {
                'nombre': nombre,
                'direccion': direccion,
                'telefono': telefono
            }
        elif 'cliente_data' in session:
            nombre = session['cliente_data'].get('nombre')
            direccion = session['cliente_data'].get('direccion')
            telefono = session['cliente_data'].get('telefono')
        else:
            flash("Por favor complete los datos del cliente", "danger")
            return redirect(url_for('home'))

        if not nombre or not direccion or not telefono:
            flash("Por favor complete todos los datos del cliente", "danger")
            return redirect(url_for('home'))

        subtotal_total = 0
        for pizza in pizzas:
            precio_inicial = PRECIOS[pizza["tamano"]]
            precio_ingredientes = len(
                pizza["ingredientes"]) * COSTO_INGREDIENTE
            subtotal_pieza = precio_inicial + precio_ingredientes
            subtotal_total += subtotal_pieza * int(pizza["cantidad"])

        nueva_venta = Venta(
            nombre_cliente=nombre,
            direccion_cliente=direccion,
            telefono_cliente=telefono,
            total_venta=subtotal_total
        )

        db.session.add(nueva_venta)
        db.session.flush()

        for pizza in pizzas:
            precio_inicial = PRECIOS[pizza["tamano"]]
            precio_ingredientes = len(
                pizza["ingredientes"]) * COSTO_INGREDIENTE
            subtotal_pieza = precio_inicial + precio_ingredientes
            subtotal_total_pizza = subtotal_pieza * int(pizza["cantidad"])

            detalle = DetallePizza(
                venta_id=nueva_venta.id,
                tamano=pizza["tamano"],
                cantidad=pizza["cantidad"],
                subtotal=subtotal_total_pizza
            )

            db.session.add(detalle)
            db.session.flush()

            for ingrediente in pizza["ingredientes"]:
                ing = IngredientePizza(
                    detalle_pizza_id=detalle.id,
                    nombre_ingrediente=ingrediente
                )
                db.session.add(ing)

        try:
            db.session.commit()
            vaciarCompra()
            session.pop('cliente_data', None)
            flash("Pedido finalizado correctamente", "success")
            return redirect(url_for('home'))
        except Exception as e:
            db.session.rollback()
            flash(f"Error al procesar el pedido: {str(e)}", "danger")
            return redirect(url_for('home'))

    return redirect(url_for('home'))


@app.route('/eliminar_pizza/<int:indice>', methods=['POST'])
@login_required
def eliminar_pizza(indice):
    if eliminarPizzaEspecifica(indice):
        flash("Pizza eliminada de la compra", "success")
    else:
        flash("No se pudo eliminar la pizza", "danger")
    return redirect(url_for('home'))


@app.route('/eliminar_compra', methods=['POST'])
@login_required
def eliminar_compra():
    vaciarCompra()
    flash("Compra vaciada correctamente", "info")
    return redirect(url_for('home'))


if __name__ == '__main__':
    csrf.init_app(app)
    app.run()