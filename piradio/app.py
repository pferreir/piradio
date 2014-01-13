import logging
import os
from logging import Formatter, FileHandler

from flask import Flask, render_template
from flask.ext.assets import Environment
from .models import db


# Configs

def create_app():
    app = Flask(__name__)
    app.config.from_object('config')

    from .views import views
    app.register_blueprint(views)

    cur_dir = os.path.join(os.path.dirname(__file__))

    # webassets config

    app.config.update({
        'PYSCSS_STATIC_ROOT': 'static/scss',
        'PYSCSS_STATIC_URL': '/static/',
        'PYSCSS_LOAD_PATHS': [os.path.join(cur_dir, 'static/scss'),
                             os.path.join(cur_dir, 'static/scss/lib')]
    })

    assets = Environment(app)
    assets.from_yaml(os.path.join(cur_dir, 'bundles.yaml'))

    # Logging setup!

    scss_logger = logging.getLogger('scss')

    db.init_app(app)

    # HACKY!
    for handler in app.logger.handlers:
        scss_logger.addHandler(handler)

    if not app.debug:
        file_handler = FileHandler('error.log')
        file_handler.setFormatter(Formatter('%(asctime)s %(levelname)s: %(message)s '
                                            '[in %(pathname)s:%(lineno)d]'))
        app.logger.setLevel(logging.INFO)
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.info('errors')

    return app

app = create_app()


@app.errorhandler(500)
def internal_error(error):
    #db_session.rollback()
    return render_template('errors/500.html'), 500


@app.errorhandler(404)
def not_found(error):
    return render_template('errors/404.html'), 404
