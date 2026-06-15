from flask import Blueprint, render_template, jsonify, request
from app.models import Usuario, Evento
from app import db
from app.utils import staff_required, admin_required
from sqlalchemy import func

bp = Blueprint('usuarios', __name__)


@bp.route('/usuarios')
@staff_required
def index():
    return render_template('usuarios/index.html')


@bp.route('/api/usuarios')
@staff_required
def listar():
    q           = request.args.get('q', '')
    faixa       = request.args.get('faixa', '')
    risco       = request.args.get('risco', '')
    engajamento = request.args.get('engajamento', '')
    page        = int(request.args.get('page', 1))
    per_page    = int(request.args.get('per_page', 15))

    query = Usuario.query
    if q:
        query = query.filter(
            (Usuario.nome.ilike(f'%{q}%')) | (Usuario.email.ilike(f'%{q}%'))
        )
    if faixa:       query = query.filter_by(faixa=faixa)
    if risco:       query = query.filter_by(risco=risco)
    if engajamento: query = query.filter_by(engajamento=engajamento)

    total    = query.count()
    usuarios = query.order_by(Usuario.score.desc()).offset((page - 1) * per_page).limit(per_page).all()

    return jsonify({
        'total': total, 'page': page, 'per_page': per_page,
        'pages': (total + per_page - 1) // per_page,
        'data': [u.to_dict() for u in usuarios],
    })


@bp.route('/api/usuarios/stats')
@staff_required
def stats():
    faixas = ['Muito Alto', 'Alto', 'Médio', 'Baixo', 'Muito Baixo']
    distribuicao = [{'faixa': f, 'total': Usuario.query.filter_by(faixa=f).count()} for f in faixas]
    scores = db.session.query(
        func.avg(Usuario.score).label('media'),
        func.min(Usuario.score).label('minimo'),
        func.max(Usuario.score).label('maximo'),
    ).first()
    return jsonify({
        'distribuicao': distribuicao,
        'score_medio': round(scores.media or 0, 0),
        'score_min':   scores.minimo or 0,
        'score_max':   scores.maximo or 0,
    })


@bp.route('/api/usuarios/<int:usuario_id>')
@staff_required
def detalhe(usuario_id):
    u      = Usuario.query.get_or_404(usuario_id)
    eventos = Evento.query.filter_by(usuario_id=usuario_id).order_by(Evento.data.desc()).limit(10).all()
    data   = u.to_dict()
    data['eventos'] = [e.to_dict() for e in eventos]
    return jsonify(data)


@bp.route('/api/usuarios', methods=['POST'])
@admin_required
def criar():
    data = request.json
    u = Usuario(
        nome=data['nome'], email=data['email'],
        score=data.get('score', 500), faixa=data.get('faixa', 'Médio'),
        risco=data.get('risco', 'Sem Risco'), engajamento=data.get('engajamento', 'Médio'),
        pontos=data.get('pontos', 0), plano=data.get('plano', 'Essencial'),
        tempo_cliente=data.get('tempo_cliente', 0),
    )
    db.session.add(u)
    db.session.commit()
    return jsonify(u.to_dict()), 201


@bp.route('/api/usuarios/<int:usuario_id>', methods=['PUT'])
@admin_required
def editar(usuario_id):
    u    = Usuario.query.get_or_404(usuario_id)
    data = request.json
    for campo in ['nome', 'email', 'score', 'faixa', 'risco', 'engajamento', 'pontos', 'plano', 'tempo_cliente']:
        if campo in data:
            setattr(u, campo, data[campo])
    db.session.commit()
    return jsonify(u.to_dict())


@bp.route('/api/usuarios/<int:usuario_id>', methods=['DELETE'])
@admin_required
def deletar(usuario_id):
    u = Usuario.query.get_or_404(usuario_id)
    db.session.delete(u)
    db.session.commit()
    return jsonify({'ok': True})
