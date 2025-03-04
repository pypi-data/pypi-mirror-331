import os
import sys
from typing import Union

from flask import Flask, redirect, url_for

from ivoryos.config import Config, get_config
from ivoryos.routes.auth.auth import auth, login_manager
from ivoryos.routes.control.control import control
from ivoryos.routes.database.database import database
from ivoryos.routes.design.design import design, socketio
from ivoryos.routes.main.main import main
from ivoryos.routes.monitor.monitor import monitor
from ivoryos.utils import utils
from ivoryos.utils.db_models import db
from ivoryos.utils.global_config import GlobalConfig
from ivoryos.utils.script_runner import ScriptRunner
from ivoryos.version import __version__ as ivoryos_version

global_config = GlobalConfig()

url_prefix = os.getenv('URL_PREFIX', "/ivoryos")
app = Flask(__name__, static_url_path=f'{url_prefix}/static', static_folder='static')


def create_app(config_class=None):
    # url_prefix = os.getenv('URL_PREFIX', "/ivoryos")
    # app = Flask(__name__, static_url_path=f'{url_prefix}/static', static_folder='static')
    app.config.from_object(config_class or 'config.get_config()')

    # Initialize extensions
    socketio.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    db.init_app(app)

    # Create database tables
    with app.app_context():
        db.create_all()

    # Additional setup
    utils.create_gui_dir(app.config['OUTPUT_FOLDER'])

    # logger_list = app.config["LOGGERS"]
    logger_path = os.path.join(app.config["OUTPUT_FOLDER"], app.config["LOGGERS_PATH"])
    logger = utils.start_logger(socketio, 'gui_logger', logger_path)

    @app.before_request
    def before_request():
        """
        Called before

        """
        from flask import g
        g.logger = logger
        g.socketio = socketio

    @app.route('/')
    def redirect_to_prefix():
        return redirect(url_for('main.index', version=ivoryos_version))  # Assuming 'index' is a route in your blueprint

    return app


def run(module=None, host="0.0.0.0", port=None, debug=None, llm_server=None, model=None,
        config: Config = None,
        logger: Union[str, list] = None,
        logger_output_name: str = None,
        enable_design=True, stream_address=None
        ):
    """
    Start ivoryOS app server.

    :param module: module name, __name__ for current module
    :param host: host address, defaults to 0.0.0.0
    :param port: port, defaults to None, and will use 8000
    :param debug: debug mode, defaults to None (True)
    :param llm_server: llm server, defaults to None.
    :param model: llm model, defaults to None. If None, app will run without text-to-code feature
    :param config: config class, defaults to None
    :param logger: logger name of list of logger names, defaults to None
    :param logger_output_name: log file save name of logger, defaults to None, and will use "default.log"
    :param enable_design:
    :param stream_address:
    """
    app = create_app(config_class=config or get_config())  # Create app instance using factory function
    enable_monitor = stream_address is not None

    def inject_nav_config():
        """Make NAV_CONFIG available globally to all templates."""
        return dict(
            enable_design=enable_design,
            enable_monitor=enable_monitor,
        )

    # todo modular page
    app.context_processor(inject_nav_config)
    app.register_blueprint(main, url_prefix=url_prefix)
    app.register_blueprint(auth, url_prefix=url_prefix)
    if enable_design:
        app.register_blueprint(design, url_prefix=url_prefix)
        app.register_blueprint(database, url_prefix=url_prefix)
    if enable_monitor:
        app.register_blueprint(monitor, url_prefix=url_prefix)
    app.register_blueprint(control, url_prefix=url_prefix)

    port = port or int(os.environ.get("PORT", 8000))
    debug = debug if debug is not None else app.config.get('DEBUG', True)

    app.config["LOGGERS"] = logger
    app.config["LOGGERS_PATH"] = logger_output_name or app.config["LOGGERS_PATH"]  # default.log
    logger_path = os.path.join(app.config["OUTPUT_FOLDER"], app.config["LOGGERS_PATH"])

    if module:
        app.config["MODULE"] = module
        app.config["OFF_LINE"] = False
        global_config.deck = sys.modules[module]
        global_config.deck_snapshot = utils.create_deck_snapshot(global_config.deck,
                                                                 output_path=app.config["DUMMY_DECK"], save=True)
        # global_config.runner = ScriptRunner(globals())
    else:
        app.config["OFF_LINE"] = True
    if model:
        app.config["ENABLE_LLM"] = True
        app.config["LLM_MODEL"] = model
        app.config["LLM_SERVER"] = llm_server
        utils.install_and_import('openai')
        from ivoryos.utils.llm_agent import LlmAgent
        global_config.agent = LlmAgent(host=llm_server, model=model,
                                       output_path=app.config["OUTPUT_FOLDER"] if module is not None else None)
    else:
        app.config["ENABLE_LLM"] = False
    if logger and type(logger) is str:
        utils.start_logger(socketio, log_filename=logger_path, logger_name=logger)
    elif type(logger) is list:
        for log in logger:
            utils.start_logger(socketio, log_filename=logger_path, logger_name=log)
    socketio.run(app, host=host, port=port, debug=debug, use_reloader=False, allow_unsafe_werkzeug=True)
    # return app
