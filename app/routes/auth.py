from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from flask_login import login_user, logout_user, current_user
from app.models import Conta, Usuario, Reward
from app import db
from app.utils import admin_required, login_required

bp = Blueprint('auth', __name__)


def _redirecionar_por_role(conta):
    if conta.role == 'B2C':
        return redirect(url_for('dashboard.b2c'))
    return redirect(url_for('dashboard.index'))


# ---------- Login / Logout ----------

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return _redirecionar_por_role(current_user)

    erro = None
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        senha = request.form.get('senha', '')
        conta = Conta.query.filter_by(email=email).first()

        if conta and conta.ativo and conta.check_password(senha):
            login_user(conta)
            return _redirecionar_por_role(conta)

        erro = 'E-mail ou senha inválidos.' if conta else 'Conta não encontrada.'
        if conta and not conta.ativo:
            erro = 'Conta desativada. Contate o administrador.'

    return render_template('auth/login.html', erro=erro)


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


# ---------- Admin: gerenciar contas ----------

@bp.route('/admin/contas')
@admin_required
def contas():
    lista = Conta.query.order_by(Conta.criado_em.desc()).all()
    usuarios_sem_conta = Usuario.query.filter(~Usuario.id.in_(
        db.session.query(Conta.usuario_id).filter(Conta.usuario_id.isnot(None))
    )).all()
    return render_template('auth/contas.html', contas=lista, usuarios=usuarios_sem_conta)


@bp.route('/api/admin/contas', methods=['POST'])
@admin_required
def criar_conta():
    data = request.json
    email = data.get('email', '').strip().lower()
    if not email or not data.get('nome') or not data.get('senha'):
        return jsonify({'error': 'Nome, e-mail e senha são obrigatórios'}), 400
    if Conta.query.filter_by(email=email).first():
        return jsonify({'error': 'E-mail já cadastrado'}), 400

    c = Conta(
        nome=data['nome'],
        email=email,
        role=data.get('role', 'B2B'),
        company=data.get('company', ''),
        ativo=True,
        usuario_id=data.get('usuario_id') or None,
    )
    c.set_password(data['senha'])
    db.session.add(c)
    db.session.commit()
    return jsonify(c.to_dict()), 201


@bp.route('/api/admin/contas/<int:conta_id>', methods=['PUT'])
@admin_required
def editar_conta(conta_id):
    c = Conta.query.get_or_404(conta_id)
    data = request.json
    for campo in ['nome', 'role', 'ativo', 'company']:
        if campo in data:
            setattr(c, campo, data[campo])
    if data.get('senha'):
        c.set_password(data['senha'])
    if 'usuario_id' in data:
        c.usuario_id = data['usuario_id'] or None
    db.session.commit()
    return jsonify(c.to_dict())


@bp.route('/api/admin/contas/<int:conta_id>', methods=['DELETE'])
@admin_required
def deletar_conta(conta_id):
    c = Conta.query.get_or_404(conta_id)
    if c.id == current_user.id:
        return jsonify({'error': 'Não é possível excluir a própria conta'}), 400
    db.session.delete(c)
    db.session.commit()
    return jsonify({'ok': True})


# ---------- API: meu perfil (B2C) ----------

@bp.route('/api/meu-perfil')
@login_required
def meu_perfil():
    if not current_user.is_b2c or not current_user.usuario_id:
        return jsonify({'error': 'Sem perfil vinculado'}), 404
    u = Usuario.query.get_or_404(current_user.usuario_id)
    data = u.to_dict()
    eventos = [e.to_dict() for e in sorted(u.eventos, key=lambda x: x.data, reverse=True)[:5]]
    data['eventos'] = eventos
    return jsonify(data)


@bp.route('/api/meu-perfil/rewards')
@login_required
def meu_rewards():
    rewards = Reward.query.filter_by(status='Ativo').order_by(Reward.resgates.desc()).all()
    return jsonify([r.to_dict() for r in rewards])
