from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Server(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    ip = db.Column(db.String(15), unique=True, nullable=False)
    gpu_count = db.Column(db.Integer)
    gpu_usage = db.Column(db.Float)
    is_occupied = db.Column(db.Boolean, default=False)
    occupied_by_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    occupied_by = db.relationship('User', backref='occupied_servers')
    note = db.Column(db.Text)
    release_time = db.Column(db.DateTime)

class gpu_usage_history(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    server_id = db.Column(db.Integer, db.ForeignKey('server.id'))
    timestamp = db.Column(db.DateTime, nullable=False)
    usage = db.Column(db.Float, nullable=False)

class gpu_info(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    server_id = db.Column(db.Integer, db.ForeignKey('server.id'))
    gpu_index = db.Column(db.Integer, nullable=False)
    memory_usage = db.Column(db.Float)
    utilization = db.Column(db.Float)
    process_name = db.Column(db.String(128))
    process_id = db.Column(db.Integer)