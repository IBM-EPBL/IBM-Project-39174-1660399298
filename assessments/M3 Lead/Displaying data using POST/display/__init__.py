from flask import Flask # Flask object

from .views import blue # blue print

def create_app():
    app = Flask(__name__)

    # registering the blueprint with the app
    app.register_blueprint(blue, url_prefix='/')

    return app