from flask import Flask, request, url_for, send_file
from flask_login import LoginManager, current_user

app = Flask(__name__, static_path='/static')
app.config.from_object('config')

login_manager = LoginManager()
login_manager.init_app(app)

from mod_auth.controllers import mod_auth as auth_module
app.register_blueprint(auth_module)

from mod_api.controllers import mod_api as api_module
app.register_blueprint(api_module)

@app.route("/", methods=["GET", "POST"])
def index():
    return send_file('templates/index.html')

if __name__ == '__main__':
    app.run()
