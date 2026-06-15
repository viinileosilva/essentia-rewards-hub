from flask import Blueprint, render_template, jsonify, request
from app.models import RiscoAtraso, Usuario
from app import db
from app.utils import staff_required
from sqlalchemy import func

bp = Blueprint('risco', __name__)


@bp.route('/risco')
@staff_required
def index():
    return render_template('risco/index.html')


@bp.route('/api/risco/kpis')
@staff_required
def kpis():
    total       = RiscoAtraso.query.count()
    valor_total = db.session.query(func.sum(RiscoAtraso.valor_em_risco)).scalar() or 0
    atencao     = RiscoAtraso.query.filter_by(nivel_risco='Crítico').count()
    monitoramento = RiscoAtraso.query.filter_by(nivel_risco='Alto').count()
    return jsonify({
        'total_em_risco': total,
        'valor_total': round(valor_total, 2),
        'atencao_imediata': atencao,
        'monitoramento_ativo': monitoramento,
    })


@bp.route('/api/risco/usuarios')
@staff_required
def listar():
    nivel    = request.args.get('nivel', '')
    plano    = request.args.get('plano', '')
    page     = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 12))

    query = RiscoAtraso.query
    if nivel: query = query.filter_by(nivel_risco=nivel)
    if plano: query = query.filter_by(produto_plano=plano)

    total     = query.count()
    registros = query.order_by(RiscoAtraso.valor_em_risco.desc()).offset((page - 1) * per_page).limit(per_page).all()

    return jsonify({
        'total': total, 'page': page,
        'pages': (total + per_page - 1) // per_page,
        'data': [r.to_dict() for r in registros],
    })


@bp.route('/api/risco/distribuicao-categoria')
@staff_required
def distribuicao_categoria():
    niveis = ['Baixo', 'Moderado', 'Alto', 'Crítico']
    return jsonify([{'nivel': n, 'total': RiscoAtraso.query.filter_by(nivel_risco=n).count()} for n in niveis])


@bp.route('/api/risco/por-plano')
@staff_required
def por_plano():
    planos = ['Plano Básico', 'Plano Standard', 'Plano Gold', 'Plano Premium']
    data = []
    for p in planos:
        count = RiscoAtraso.query.filter_by(produto_plano=p).count()
        valor = db.session.query(func.sum(RiscoAtraso.valor_em_risco)).filter_by(produto_plano=p).scalar() or 0
        data.append({'plano': p, 'total': count, 'valor': round(valor, 2)})
    return jsonify(data)


@bp.route('/api/risco/top-criticos')
@staff_required
def top_criticos():
    top = RiscoAtraso.query.filter_by(nivel_risco='Crítico').order_by(RiscoAtraso.valor_em_risco.desc()).limit(10).all()
    return jsonify([r.to_dict() for r in top])
