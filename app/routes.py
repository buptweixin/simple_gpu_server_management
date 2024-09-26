from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User, Server, gpu_usage_history, gpu_info
from app.forms import LoginForm, RegistrationForm, ServerForm, OccupyServerForm, UserManagementForm, ServerManagementForm
from flask import current_app as app
import re
from app.utils import update_server_gpu_info
from datetime import datetime, timedelta
from operator import attrgetter
from sqlalchemy import desc
from app.tasks import update_all_servers_gpu_info
import pytz

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            # 登录成功后更新所有服务器的 GPU 信息
            # update_all_servers_gpu_info()
            return redirect(url_for('dashboard'))
        else:
            flash('登录失败。请检查用户名和密码。', 'danger')
    return render_template('login.html', title='登录', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('注册成功！请登录。', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='注册', form=form)

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    servers = Server.query.all()
    for server in servers:
        if update_server_gpu_info(server):
            db.session.commit()
    
    # 对服务器进行排序
    def server_sort_key(server):
        if not server.is_occupied and (server.gpu_usage is None or server.gpu_usage < 10):
            return (0, server.gpu_usage if server.gpu_usage is not None else 0)
        return (1, server.gpu_usage if server.gpu_usage is not None else 100)

    servers = sorted(servers, key=server_sort_key)
    
    # 计算服务器统计信息
    total_servers = len(servers)
    free_servers = sum(1 for server in servers if not server.is_occupied)
    occupied_servers = total_servers - free_servers
    
    form = OccupyServerForm()
    form.servers.choices = [(s.id, s.name) for s in servers if not s.is_occupied]
    
    if form.validate_on_submit():
        for server_id in form.servers.data:
            server = Server.query.get(server_id)
            if server:
                server.is_occupied = True
                server.occupied_by = current_user
                server.note = form.note.data
                server.release_time = form.release_time.data
                db.session.add(server)
        try:
            db.session.commit()
            flash('服务器已成功占用', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'占用服务器发生错误: {str(e)}', 'danger')
        return redirect(url_for('dashboard'))
    
    # 获取最后一次更新时间
    last_update = gpu_usage_history.query.order_by(gpu_usage_history.timestamp.desc()).first()
    shanghai_tz = pytz.timezone('Asia/Shanghai')
    if last_update:
        last_update_time = last_update.timestamp.replace(tzinfo=pytz.UTC).astimezone(shanghai_tz)
        next_update_time = (last_update_time + timedelta(minutes=10)).astimezone(shanghai_tz)
    else:
        last_update_time = None
        next_update_time = None

    return render_template('dashboard.html', 
                           title='仪表板', 
                           servers=servers, 
                           form=form,
                           total_servers=total_servers,
                           free_servers=free_servers,
                           occupied_servers=occupied_servers,
                           last_update_time=last_update_time,
                           next_update_time=next_update_time)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/server_management', methods=['GET', 'POST'])
@login_required
def server_management():
    form = ServerManagementForm()
    if form.validate_on_submit():
        name = form.name.data
        ip = form.ip.data
        
        # 检查是否是多服务器注册
        ip_range_match = re.match(r'(\d+\.\d+\.\d+\.)(\d+)-(\d+)$', ip)
        if ip_range_match:
            base_ip = ip_range_match.group(1)
            start = int(ip_range_match.group(2))
            end = int(ip_range_match.group(3))
            for i in range(start, end + 1):
                server_name = f"{name}{i}" if start != end else name
                server_ip = f"{base_ip}{i}"
                new_server = Server(name=server_name, ip=server_ip)
                db.session.add(new_server)
                update_server_gpu_info(new_server)
        else:
            new_server = Server(name=name, ip=ip)
            db.session.add(new_server)
            update_server_gpu_info(new_server)
        
        try:
            db.session.commit()
            flash('服务器添加成功！', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'添加服务器时发生错误: {str(e)}', 'danger')
        return redirect(url_for('server_management'))

    servers = Server.query.all()
    return render_template('server_management.html', title='服务器管理', form=form, servers=servers)

@app.route('/delete_server/<int:server_id>')
@login_required
def delete_server(server_id):
    server = Server.query.get_or_404(server_id)
    db.session.delete(server)
    db.session.commit()
    flash('服务器已删除', 'success')
    return redirect(url_for('server_management'))

@app.route('/user_management', methods=['GET', 'POST'])
@login_required
def user_management():
    print(f"Current user: {current_user.username}, Is admin: {current_user.is_admin}")
    if not current_user.is_admin:
        flash('只有管理员可以访问此页面。', 'danger')
        return redirect(url_for('dashboard'))

    form = UserManagementForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            user.is_admin = form.is_admin.data
            flash(f'用户 {user.username} 已更新。', 'success')
        else:
            new_user = User(username=form.username.data, is_admin=form.is_admin.data)
            new_user.set_password(form.password.data)
            db.session.add(new_user)
            flash(f'新用户 {new_user.username} 已添加。', 'success')
        db.session.commit()
        return redirect(url_for('user_management'))

    users = User.query.all()
    return render_template('user_management.html', title='用户管理', form=form, users=users)

@app.route('/delete_user/<int:user_id>')
@login_required
def delete_user(user_id):
    if not current_user.is_admin:
        flash('只有管理员可以删除用户。', 'danger')
        return redirect(url_for('dashboard'))

    user = User.query.get_or_404(user_id)
    if user == current_user:
        flash('不能删除当前登录的用户。', 'danger')
    else:
        db.session.delete(user)
        db.session.commit()
        flash(f'用户 {user.username} 已被删除。', 'success')
    return redirect(url_for('user_management'))

@app.route('/release_server/<int:server_id>')
@login_required
def release_server(server_id):
    server = Server.query.get_or_404(server_id)
    if current_user.is_admin or current_user == server.occupied_by:
        server.is_occupied = False
        server.occupied_by = None
        server.note = None
        server.release_time = None
        db.session.commit()
        flash('服务器已释放', 'success')
    else:
        flash('您没有权限释放此服务器', 'danger')
    return redirect(url_for('dashboard'))

@app.route('/update_server/<int:server_id>', methods=['POST'])
@login_required
def update_server(server_id):
    server = Server.query.get_or_404(server_id)
    if current_user.is_admin or current_user == server.occupied_by:
        server.note = request.form.get('note')
        release_time = request.form.get('release_time')
        if release_time:
            server.release_time = datetime.strptime(release_time, '%Y-%m-%d %H:%M')
        db.session.commit()
        flash('服务器信息已更新', 'success')
    else:
        flash('您没有权限更新此服务器信息', 'danger')
    return redirect(url_for('dashboard'))

@app.route('/server_detail/<int:server_id>')
@login_required
def server_detail(server_id):
    server = Server.query.get_or_404(server_id)
    
    # 获取最新的 GPU 信息
    gpu_info_list = gpu_info.query.filter_by(server_id=server_id).order_by(gpu_info.id.desc()).limit(server.gpu_count).all()
    
    # 获取 GPU 使用率历史数据
    usage_history = gpu_usage_history.query.filter_by(server_id=server_id).order_by(gpu_usage_history.timestamp.desc()).limit(100).all()
    
    # 准备图表数据
    shanghai_tz = pytz.timezone('Asia/Shanghai')
    timestamps = [h.timestamp.replace(tzinfo=pytz.UTC).astimezone(shanghai_tz).strftime('%Y-%m-%d %H:%M:%S') for h in reversed(usage_history)]
    usage_data = [h.usage for h in reversed(usage_history)]

    return render_template('server_detail.html', 
                           title='服务器详情', 
                           server=server, 
                           gpu_info=gpu_info_list,
                           timestamps=timestamps,
                           usage_data=usage_data)