from flask import Flask

def create_app():
    app = Flask(__name__)

    from views import views # changed line
    app.register_blueprint(views, url_prefix="/")

    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
