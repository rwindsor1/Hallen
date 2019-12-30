from app.models import User
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length

class LoginForm(FlaskForm):
    username    = StringField(  'Username',  validators=[DataRequired()])
    password    = PasswordField('Password',  validators=[DataRequired()])
    remember_me = BooleanField( 'Remember Me')

    submit      = SubmitField(  'Sign In')

class RegisterForm(FlaskForm):
    username  = StringField(  'Username',        validators=[DataRequired()])
    email     = StringField(  'Email',           validators=[DataRequired(), Email()])
    password  = PasswordField('Password',        validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])

    submit = SubmitField('Register')



    def check_username_is_unique(self, username_suggestion):
        user = User.query.filter_by(username = username_suggestion.data).first()
        if user is not None:
            raise ValidationError('This Username already exists!')

    def check_email_is_unique(self, email_suggestion):
        user = User.query.filter_by(email = email_suggestion.data).first()
        if user is not None:
            raise ValidationError('An account with this email already exists!')

    def validate_email(self, email_suggestion):
        self.check_email_is_unique(email_suggestion)

    def validate_username(self, username_suggestion):
        self.check_username_is_unique(username_suggestion)
    
class CreateGroupForm(FlaskForm):
    groupname        = StringField(  'Group Name',        validators = [DataRequired()])    
    groupdescription = TextAreaField('Group Description', validators = [Length(min=0, max=300)])

    submit = SubmitField('Create')

class CreatePostForm(FlaskForm):
    postcontent = TextAreaField( 'Post Content', validators = [DataRequired(), Length(min=0, max=300)])

    submit = SubmitField('Create')