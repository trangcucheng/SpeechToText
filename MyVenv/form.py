from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms import validators
from wtforms.validators import DataRequired, Length, Email, EqualTo

class RegisterForm(FlaskForm):
    fullname = StringField('Họ và tên: ', validators=[DataRequired(), Length(min=10, max=60)])
    user_name = StringField('Tên đăng nhập: ', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Mật khẩu: ', validators=[DataRequired(), Length(min=6, max=20)])
    confirm_password = PasswordField('Xác nhận lại mật khẩu: ', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Đăng ký')

class LoginForm(FlaskForm):
    user_name = StringField('Tên đăng nhập: ', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField("Đăng nhập")