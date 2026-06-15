from functools import wraps
from flask import redirect, url_for, jsonify, request
from flask_login import current_user


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated:
            if request.path.startswith('/api/'):
                return jsonify({'error': 'Não autenticado'}), 401
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    """Somente Admin."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        if not current_user.is_admin:
            if request.path.startswith('/api/'):
                return jsonify({'error': 'Acesso restrito a administradores'}), 403
            return redirect(url_for('dashboard.index'))
        return f(*args, **kwargs)
    return decorated


def staff_required(f):
    """Admin ou B2B — bloqueia B2C."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated:
            if request.path.startswith('/api/'):
                return jsonify({'error': 'Não autenticado'}), 401
            return redirect(url_for('auth.login'))
        if current_user.is_b2c:
            return redirect(url_for('dashboard.b2c'))
        return f(*args, **kwargs)
    return decorated
