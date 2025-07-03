from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo
from werkzeug.security import generate_password_hash
import re
from datetime import datetime

from models.user import User
from utils.database import db

auth_bp = Blueprint('auth', __name__)

# Forms
class LoginForm(FlaskForm):
    username_or_email = StringField('Username or Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(), 
        Length(min=3, max=20, message="Username must be between 3 and 20 characters")
    ])
    email = StringField('Email', validators=[DataRequired(), Email()])
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=50)])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=6, message="Password must be at least 6 characters long")
    ])
    password2 = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message="Passwords must match")
    ])
    submit = SubmitField('Create Account')

class ProfileForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    current_password = PasswordField('Current Password')
    new_password = PasswordField('New Password', validators=[Length(min=6)])
    confirm_password = PasswordField('Confirm New Password', validators=[
        EqualTo('new_password', message="Passwords must match")
    ])
    submit = SubmitField('Update Profile')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    form = RegisterForm()
    
    if form.validate_on_submit():
        # Additional validation
        errors = []
        
        # Check username format
        if not re.match(r'^[a-zA-Z0-9_]+$', form.username.data):
            errors.append('Username can only contain letters, numbers, and underscores')
        
        # Check if user already exists
        if User.query.filter_by(username=form.username.data).first():
            errors.append('Username already exists')
        
        if User.query.filter_by(email=form.email.data.lower()).first():
            errors.append('Email already registered')
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('auth/register.html', form=form)
        
        # Create new user
        user = User(
            username=form.username.data,
            email=form.email.data.lower(),
            first_name=form.first_name.data,
            last_name=form.last_name.data
        )
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        
        login_user(user, remember=True)
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': True, 'redirect': url_for('dashboard.index')})
        
        flash('Welcome to Task Tracker Pro X! Your account has been created successfully.', 'success')
        return redirect(url_for('dashboard.index'))
    
    return render_template('auth/register.html', form=form)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        username_or_email = form.username_or_email.data.strip()
        password = form.password.data
        
        # Try to find user by username or email
        user = User.query.filter(
            (User.username == username_or_email) | 
            (User.email == username_or_email.lower())
        ).first()
        
        if user and user.check_password(password):
            if not user.is_active:
                flash('Account is deactivated', 'error')
                return render_template('auth/login.html', form=form)
            
            login_user(user, remember=form.remember_me.data)
            user.last_login_at = datetime.utcnow()
            db.session.commit()
            
            next_page = request.args.get('next')
            if not next_page or not next_page.startswith('/'):
                next_page = url_for('dashboard.index')
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': True, 'redirect': next_page})
            
            flash(f'Welcome back, {user.full_name}!', 'success')
            return redirect(next_page)
        else:
            flash('Invalid username/email or password', 'error')
    
    return render_template('auth/login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully', 'info')
    return redirect(url_for('index'))

@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm(obj=current_user)
    
    if form.validate_on_submit():
        # Check if email is taken by another user
        existing_user = User.query.filter_by(email=form.email.data.lower()).first()
        if existing_user and existing_user.id != current_user.id:
            flash('Email is already taken by another user', 'error')
            return render_template('auth/profile.html', form=form)
        
        # Update basic info
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.email = form.email.data.lower()
        
        # Handle password change
        if form.current_password.data and form.new_password.data:
            if not current_user.check_password(form.current_password.data):
                flash('Current password is incorrect', 'error')
                return render_template('auth/profile.html', form=form)
            
            current_user.set_password(form.new_password.data)
            flash('Password updated successfully', 'success')
        
        db.session.commit()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': True, 'message': 'Profile updated successfully'})
        
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('auth.profile'))
    
    return render_template('auth/profile.html', form=form)
