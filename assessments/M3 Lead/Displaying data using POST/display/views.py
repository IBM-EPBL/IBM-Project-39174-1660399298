from flask import Blueprint, request 
from flask import render_template # for rendering the html templates

blue = Blueprint("print", "__name__")

@blue.route('/', methods=('GET', 'POST'))
def home():
    if request.method == 'POST':
        # getting the data entered by the user from the request
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')

        return render_template('display.html',
            name = name, email = email, phone = phone
        )
        
    return render_template('index.html')
