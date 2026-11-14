"""
Authentication and Profile routes.
Handles registration, login, logout, and profile updates.
"""

import os
import secrets
from pathlib import Path
from werkzeug.utils import secure_filename
from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, current_user, login_required
from app.auth import auth_bp
from app.auth.forms import RegistrationForm, LoginForm, UpdateProfileForm
from app.extensions import db
from app.models import User, Post


def save_image(form_picture):
    """Save an uploaded image with a random filename to avoid collisions."""
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(secure_filename(form_picture.filename))
    picture_filename = f"{random_hex}{f_ext.lower()}"
    picture_path = Path(current_app.config['UPLOAD_FOLDER']) / picture_filename

    # Save to uploads directory
    form_picture.save(picture_path)
    return picture_filename


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Register a new user account."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data.strip(),
            email=form.email.data.strip().lower()
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        flash('Your account has been created successfully! You can now log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', form=form)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Authenticate and log in an existing user."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.strip().lower()).first()

        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            flash(f'Welcome back, {user.username}!', 'success')

            # Redirect to originally requested page or home
            next_page = request.args.get('next')
            if not next_page or not next_page.startswith('/'):
                next_page = url_for('main.index')
            return redirect(next_page)
        else:
            flash('Login unsuccessful. Please check your email and password.', 'danger')

    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    """Log out the current user."""
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('main.index'))


@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """View and update user profile, avatar, and authored blogs."""
    form = UpdateProfileForm()

    if form.validate_on_submit():
        # Handle profile picture upload if provided
        if form.profile_image.data:
            picture_file = save_image(form.profile_image.data)
            current_user.profile_image = picture_file

        current_user.username = form.username.data.strip()
        current_user.bio = form.bio.data.strip() if form.bio.data else ''
        db.session.commit()

        flash('Your profile has been updated!', 'success')
        return redirect(url_for('auth.profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.bio.data = current_user.bio

    # Fetch user's own authored posts
    user_posts = Post.query.filter_by(user_id=current_user.id).order_by(Post.created_at.desc()).all()

    return render_template('auth/profile.html', form=form, posts=user_posts)
