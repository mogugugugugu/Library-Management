from flask import Flask
from controllers.auth_controller import auth_blueprint
from controllers.library_controller import library_blueprint

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Register Blueprints
app.register_blueprint(auth_blueprint)
app.register_blueprint(library_blueprint)

if __name__ == "__main__":
    app.run(debug=True)
