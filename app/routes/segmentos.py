from flask import Blueprint, render_template, jsonify, request
from app.models import Segmento, Campanha, Reward
from app import db
from app.utils import staff_required, admin_required
from datetime import datetime

bp = Blueprint('segmentos', __name__)


@bp.route('/segmentos')
@staff_required
def index():
    return render_template('segmentos/index.html')


@bp.route('/api/segmentos')
@staff_required
def listar():
    nome = request.args.get('nome', '')
    tipo = request.args.get('tipo', '')
    query = Segmento.query
    if nome: query = query.filter(Segmento.nome.ilike(f'%{nome}%'))
    if tipo: query = query.filter_by(tipo=tipo)
    segmentos = query.order_by(Segmento.prioritario.desc(), Segmento.nome).all()
    return jsonify([s.to_dict() for s in segmentos])


@bp.route('/api/segmentos/prioritarios')
@staff_required
def prioritarios():
    segs = Segmento.query.filter_by(prioritario=True).all()
    return jsonify([s.to_dict() for s in segs])


@bp.route('/api/segmentos', methods=['POST'])
@staff_required
def criar():
    data = request.json
    s = Segmento(
        nome=data['nome'], tipo=data.get('tipo', 'Manual'),
        criterios=data.get('criterios', ''), descricao=data.get('descricao', ''),
        score_min=data.get('score_min'), score_max=data.get('score_max'),
        risco_alvo=data.get('risco_alvo'), engajamento_alvo=data.get('engajamento_alvo'),
        prioritario=data.get('prioritario', False),
    )
    db.session.add(s)
    db.session.commit()
    return jsonify(s.to_dict()), 201


@bp.route('/api/segmentos/<int:seg_id>', methods=['DELETE'])
@admin_required
def deletar(seg_id):
    s = Segmento.query.get_or_404(seg_id)
    db.session.delete(s)
    db.session.commit()
    return jsonify({'ok': True})


# Campanhas

@bp.route('/api/campanhas')
@staff_required
def listar_campanhas():
    status = request.args.get('status', '')
    tipo   = request.args.get('tipo', '')
    query  = Campanha.query
    if status: query = query.filter_by(status=status)
    if tipo:   query = query.filter_by(tipo=tipo)
    campanhas = query.order_by(Campanha.criado_em.desc()).all()
    return jsonify([c.to_dict() for c in campanhas])


@bp.route('/api/campanhas/stats')
@staff_required
def stats_campanhas():
    status_list = ['Rascunho', 'Agendada', 'Ativa', 'Pausada', 'Encerrada']
    tipos       = ['Engajamento', 'Retenção', 'Recuperação', 'Upgrade', 'Ativação']
    por_status  = {s: Campanha.query.filter_by(status=s).count() for s in status_list}
    por_tipo    = {t: Campanha.query.filter_by(tipo=t).count() for t in tipos}
    return jsonify({'por_status': por_status, 'por_tipo': por_tipo})


@bp.route('/api/campanhas', methods=['POST'])
@staff_required
def criar_campanha():
    data = request.json
    c = Campanha(
        nome=data['nome'], tipo=data['tipo'],
        status=data.get('status', 'Rascunho'),
        segmento_id=data.get('segmento_id'),
        reward_id=data.get('reward_id'),
        vigencia_inicio=datetime.strptime(data['vigencia_inicio'], '%Y-%m-%d').date() if data.get('vigencia_inicio') else None,
        vigencia_fim=datetime.strptime(data['vigencia_fim'], '%Y-%m-%d').date() if data.get('vigencia_fim') else None,
        usuarios_alcancados=data.get('usuarios_alcancados', 0),
        engajamento_pct=data.get('engajamento_pct', 0.0),
    )
    db.session.add(c)
    db.session.commit()
    return jsonify(c.to_dict()), 201


@bp.route('/api/campanhas/<int:camp_id>', methods=['DELETE'])
@admin_required
def deletar_campanha(camp_id):
    c = Campanha.query.get_or_404(camp_id)
    db.session.delete(c)
    db.session.commit()
    return jsonify({'ok': True})
