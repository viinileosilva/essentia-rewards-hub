from flask import Blueprint, render_template, jsonify, request
from app.models import Reward
from app import db
from app.utils import staff_required, admin_required

bp = Blueprint('rewards', __name__)


@bp.route('/rewards')
@staff_required
def index():
    return render_template('rewards/index.html')


@bp.route('/api/rewards')
@staff_required
def listar():
    nome     = request.args.get('nome', '')
    tipo     = request.args.get('tipo', '')
    status   = request.args.get('status', '')
    parceiro = request.args.get('parceiro', '')
    query    = Reward.query
    if nome:     query = query.filter(Reward.nome.ilike(f'%{nome}%'))
    if tipo:     query = query.filter_by(tipo=tipo)
    if status:   query = query.filter_by(status=status)
    if parceiro: query = query.filter(Reward.parceiro.ilike(f'%{parceiro}%'))
    rewards = query.order_by(Reward.resgates.desc()).all()
    return jsonify([r.to_dict() for r in rewards])


@bp.route('/api/rewards/stats')
@staff_required
def stats():
    tipos = ['Benefício', 'Cashback', 'Troca por Serviço', 'Troca por Assinatura', 'Cupom/Desconto']
    return jsonify([{'tipo': t, 'total': Reward.query.filter_by(tipo=t).count()} for t in tipos])


@bp.route('/api/rewards', methods=['POST'])
@admin_required
def criar():
    data = request.json
    r = Reward(
        nome=data['nome'], tipo=data['tipo'],
        status=data.get('status', 'Ativo'),
        custo_cashback=data.get('custo_cashback', 0),
        parceiro=data.get('parceiro', ''),
        resgates=data.get('resgates', 0),
    )
    db.session.add(r)
    db.session.commit()
    return jsonify(r.to_dict()), 201


@bp.route('/api/rewards/<int:reward_id>', methods=['PUT'])
@admin_required
def editar(reward_id):
    r    = Reward.query.get_or_404(reward_id)
    data = request.json
    for campo in ['nome', 'tipo', 'status', 'custo_cashback', 'parceiro']:
        if campo in data:
            setattr(r, campo, data[campo])
    db.session.commit()
    return jsonify(r.to_dict())


@bp.route('/api/rewards/<int:reward_id>', methods=['DELETE'])
@admin_required
def deletar(reward_id):
    r = Reward.query.get_or_404(reward_id)
    db.session.delete(r)
    db.session.commit()
    return jsonify({'ok': True})
