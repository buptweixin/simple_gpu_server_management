from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, DateTimeField, SelectMultipleField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError, IPAddress
from app.models import User
import re

class LoginForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired()])
    password = PasswordField('密码', validators=[DataRequired()])
    submit = SubmitField('登录')

class RegistrationForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('密码', validators=[DataRequired()])
    confirm_password = PasswordField('确认密码', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('注册')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('该用户名已被使用，请选择其他用户名。')

class ServerForm(FlaskForm):
    name = StringField('服务器名', validators=[DataRequired()])
    ip = StringField('IP地址', validators=[DataRequired()])
    submit = SubmitField('添加服务器')

class OccupyServerForm(FlaskForm):
    servers = SelectMultipleField('选择服务器', coerce=int, validators=[DataRequired()])
    note = StringField('备注')
    release_time = DateTimeField('预计释放时间', format='%Y-%m-%dT%H:%M')
    submit = SubmitField('占用服务器')

class UserManagementForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('密码', validators=[DataRequired()])
    is_admin = BooleanField('管理员权限')
    submit = SubmitField('添加/更新用户')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user and self.password.data:
            raise ValidationError('该用户名已存在，如果要更新用户，请留空密码字段。')

class ServerManagementForm(FlaskForm):
    name = StringField('服务器名', validators=[DataRequired()])
    ip = StringField('IP地址', validators=[DataRequired()])
    submit = SubmitField('添加服务器')

    def validate_ip(self, ip):
        # 检查是否是单个IP地址
        single_ip_pattern = r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$'
        # 检查是否是IP地址范围
        ip_range_pattern = r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}-\d{1,3}$'
        
        if not (re.match(single_ip_pattern, ip.data) or re.match(ip_range_pattern, ip.data)):
            raise ValidationError('无效的IP地址格式。请使用单个IP地址（如192.168.1.1）或IP地址范围（如192.168.1.1-10）。')
        
        # 如果是单个IP地址，验证每个部分是否在0-255之间
        if re.match(single_ip_pattern, ip.data):
            parts = ip.data.split('.')
            for part in parts:
                if not 0 <= int(part) <= 255:
                    raise ValidationError('IP地址的每个部分必须在0-255之间。')
        
        # 如果是IP地址范围，验证范围的有效性
        if re.match(ip_range_pattern, ip.data):
            base_ip, end = ip.data.rsplit('.', 1)[0], ip.data.split('-')[1]
            if not 1 <= int(end) <= 255:
                raise ValidationError('IP地址范围的结束值必须在1-255之间。')
            
            start = ip.data.rsplit('.', 1)[0].split('.')[-1]
            if int(start) >= int(end):
                raise ValidationError('IP地址范围的起始值必须小于结束值。')