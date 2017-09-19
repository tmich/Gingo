import os


class BaseConfig(object):
	DEBUG = True
	TESTING = False
	# sqlite :memory: identifier is the default if no filepath is present
	#SQLALCHEMY_DATABASE_URI = 'sqlite:////var/www/gingo/data/gingo.db'
	SQLALCHEMY_DATABASE_URI = 'sqlite:////home/tiziano/gingo.db'
	SECRET_KEY  = "weorpworipwoeirpweirpoweipro234982039480239!!"


class DevelopmentConfig(BaseConfig):
	DEBUG = True
	TESTING = True
	SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/gingo.db'
	SECRET_KEY  = "weorpworipwoeirpweirpoweipro234982039480239!!"


class TestingConfig(BaseConfig):
	DEBUG = False
	TESTING = True
	SQLALCHEMY_DATABASE_URI = 'sqlite://'
	SECRET_KEY  = "weorpworipwoeirpweirpoweipro234982039480239!!"

config = {
	"development": "gingo.config.DevelopmentConfig",
	"testing": "gingo.config.TestingConfig",
	"default": "gingo.config.BaseConfig"
}


def configure_app(app):
	config_name = os.getenv('FLAKS_CONFIGURATION', 'default')
	app.config.from_object(config[config_name])
	app.config.from_pyfile('config.cfg', silent=True)

