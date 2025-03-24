from wtforms import Form
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, RadioField, SelectMultipleField, widgets
from wtforms import validators


class ClienteForm(FlaskForm):
    nombre = StringField('Nombre', [
        validators.DataRequired(message='El nombre es requerido'),
        validators.length(
            min=4, max=25, message='El nombre debe contener 4 y 25 caracteres')
    ])
    direccion = StringField('Dirección', [
        validators.DataRequired(message='La dirección es necesaria'),
        validators.length(
            min=4, max=100, message='La dirección debe contener 4 y 100 caracteres')
    ])
    telefono = StringField('Teléfono', [
        validators.DataRequired(message='El teléfono es  necesaria'),
        validators.length(
            min=7, max=12, message='El teléfono debe contener 7 y 12 caracteres')
    ])


class PizzaForm(FlaskForm):
    tamano = RadioField(
        'Tamaño',
        choices=[('pequena', 'Pequeña $40'),
                 ('mediana', 'Mediana $80'),
                 ('grande', 'Grande $120')],
        default='mediana',
        validators=[validators.DataRequired(message='El tamaño es necesario')])

    ingredientes = SelectMultipleField(
        'Ingredientes $10 extra por cada uno',
        choices=[
            ('jamon', 'Jamón'),
            ('pina', 'Piña'),
            ('champinones', 'Champiñones')
        ],
        default=['jamon'],
        option_widget=widgets.CheckboxInput(),
        widget=widgets.ListWidget(prefix_label=False)
    )

    numPizzas = IntegerField('Número de pizzas', [
        validators.DataRequired(message='La cantidad de pizzas es necesario'),
        validators.NumberRange(
            min=1, max=50, message='Puedes pedir  entre 1 y 50')
    ], default=1)
