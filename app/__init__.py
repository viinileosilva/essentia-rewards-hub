from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from sqlalchemy.pool import StaticPool
from config import Config

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Faça login para continuar.'

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    if Config.USE_TURSO:
        import libsql_experimental as libsql

        def _turso_creator():
            return libsql.connect(
                database=Config.TURSO_DATABASE_URL,
                auth_token=Config.TURSO_AUTH_TOKEN,
            )

        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
            'creator': _turso_creator,
            'poolclass': StaticPool,
        }

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    from app.routes.dashboard import bp as dashboard_bp
    from app.routes.usuarios  import bp as usuarios_bp
    from app.routes.risco     import bp as risco_bp
    from app.routes.segmentos import bp as segmentos_bp
    from app.routes.rewards   import bp as rewards_bp
    from app.routes.auth      import bp as auth_bp

    app.register_blueprint(dashboard_bp)
    app.register_blueprint(usuarios_bp)
    app.register_blueprint(risco_bp)
    app.register_blueprint(segmentos_bp)
    app.register_blueprint(rewards_bp)
    app.register_blueprint(auth_bp)

    return app


@login_manager.user_loader
def load_user(user_id):
    from app.models import Conta
    return Conta.query.get(int(user_id))
