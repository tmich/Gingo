from flask import Flask
from gingo.utils import get_instance_folder_path
from gingo.api.controllers import api
from gingo.admin.controllers import admin
from gingo.config import configure_app
from gingo.data.models import db

app = Flask(__name__,
            instance_path=get_instance_folder_path(),
            instance_relative_config=True,
            template_folder='templates')

configure_app(app)
db.init_app(app)
app.jinja_env.add_extension('jinja2.ext.loopcontrols')

app.register_blueprint(api, url_prefix='/api/v1.0')
app.register_blueprint(admin, url_prefix='/admin')
