from flask import Blueprint, render_template, request, redirect, url_for, session
from functools import wraps
import os

from config import Config
from services.ai_manager import AIManager

admin_bp = Blueprint('admin', __name__, template_folder='../templates/admin')


def login_required(view_func):
    """Decorator to require login for admin routes."""
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if not session.get('admin_authenticated'):
            return redirect(url_for('admin.login'))
        return view_func(*args, **kwargs)
    return wrapped


@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Admin login page"""
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        config = Config()
        if username == config.ADMIN_USERNAME and password == config.ADMIN_PASSWORD:
            session['admin_authenticated'] = True
            return redirect(url_for('admin.dashboard'))
        error = 'Invalid credentials'
    return render_template('admin/login.html', error=error)


@admin_bp.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    """Admin dashboard with provider management"""
    if request.method == 'POST':
        # Update API keys
        for provider in ['openai', 'gemini', 'openrouter']:
            key = request.form.get(f'{provider}_key')
            if key is not None:
                os.environ[f'{provider.upper()}_API_KEY'] = key.strip()
        # Store active provider in session
        active = request.form.get('active_provider')
        if active:
            session['active_provider'] = active
        else:
            session.pop('active_provider', None)

    ai_manager = AIManager()
    providers = ai_manager.get_provider_status()
    active_provider = session.get('active_provider', '')
    return render_template('admin/dashboard.html',
                           providers=providers,
                           active_provider=active_provider)

