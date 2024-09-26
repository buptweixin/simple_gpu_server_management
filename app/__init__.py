from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate
from config import Config
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime, timedelta

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()
migrate = Migrate()
scheduler = BackgroundScheduler()

def create_app(config_class=Config):
    app = Flask(__name__, template_folder='templates')
    app.config.from_object(config_class)

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    migrate.init_app(app, db)

    login_manager.login_view = 'login'

    with app.app_context():
        from app import routes, models
        db.create_all()

        # 添加默认管理员用户
        admin_user = models.User.query.filter_by(username='admin').first()
        if not admin_user:
            admin_user = models.User(username='admin', is_admin=True)
            admin_user.set_password('admin')
            db.session.add(admin_user)
            db.session.commit()
            print("Default admin user created.")
        else:
            print("Admin user already exists.")

        # 启动后台任务调度器
        from app.tasks import update_all_servers_gpu_info
        from app.models import gpu_usage_history

        def scheduled_update():
            with app.app_context():
                if gpu_usage_history.query.first() is None:
                    print("gpu_usage_history is empty. Running immediate update.")
                    update_all_servers_gpu_info()
                else:
                    last_update = gpu_usage_history.query.order_by(gpu_usage_history.timestamp.desc()).first().timestamp
                    if datetime.utcnow() - last_update > timedelta(minutes=10):
                        print("Running scheduled update.")
                        update_all_servers_gpu_info()
                    else:
                        print("Skipping update. Last update was less than 10 minutes ago.")

        scheduler.add_job(
            func=scheduled_update,
            trigger=IntervalTrigger(minutes=1),
            id='update_gpu_info',
            name='Check and update GPU info',
            replace_existing=True)
        scheduler.start()

    @login_manager.user_loader
    def load_user(user_id):
        return models.User.query.get(int(user_id))

    return app