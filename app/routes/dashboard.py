from flask import Blueprint, render_template, jsonify, redirect, url_for
from flask_login import current_user
from app.models import Usuario, Segmento, Campanha, Reward, Evento, RiscoAtraso
from app import db
from app.utils import login_required, staff_required
from sqlalchemy import func

bp = Blueprint('dashboard', __name__)


@bp.route('/')
@login_required
def index():
    if current_user.is_b2c:
        return redirect(url_for('dashboard.b2c'))
    return render_template('dashboard/index.html')


@bp.route('/meu-painel')
@login_required
def b2c():
    if not current_user.is_b2c:
        return redirect(url_for('dashboard.index'))
    return render_template('dashboard/b2c.html')


# ---------- APIs do Dashboard (Admin + B2B) ----------

@bp.route('/api/dashboard/kpis')
@staff_required
def kpis():
    total_usuarios = Usuario.query.count()
    saldo_medio    = db.session.query(func.avg(Usuario.pontos)).scalar() or 0
    score_medio    = db.session.query(func.avg(Usuario.score)).scalar() or 0
    em_risco       = Usuario.query.filter(Usuario.risco.in_(['Alto', 'Crítico'])).count()
    taxa_risco     = (em_risco / total_usuarios * 100) if total_usuarios else 0
    faturamento    = db.session.query(func.sum(Usuario.pontos)).scalar() or 0
    return jsonify({
        'total_usuarios': total_usuarios,
        'saldo_medio':    round(saldo_medio, 0),
        'score_medio':    round(score_medio, 0),
        'taxa_risco':     round(taxa_risco, 1),
        'faturamento_total': round(faturamento, 2),
    })


@bp.route('/api/dashboard/distribuicao-score')
@staff_required
def distribuicao_score():
    faixas = ['Muito Alto', 'Alto', 'Médio', 'Baixo', 'Muito Baixo']
    return jsonify([{'faixa': f, 'total': Usuario.query.filter_by(faixa=f).count()} for f in faixas])


@bp.route('/api/dashboard/distribuicao-risco')
@staff_required
def distribuicao_risco():
    niveis = ['Sem Risco', 'Baixo', 'Moderado', 'Alto', 'Crítico']
    return jsonify([{'nivel': n, 'total': Usuario.query.filter_by(risco=n).count()} for n in niveis])


@bp.route('/api/dashboard/distribuicao-engajamento')
@staff_required
def distribuicao_engajamento():
    niveis = ['Muito Alto', 'Alto', 'Médio', 'Baixo', 'Cancelado']
    return jsonify([{'nivel': n, 'total': Usuario.query.filter_by(engajamento=n).count()} for n in niveis])


@bp.route('/api/dashboard/top-performers')
@staff_required
def top_performers():
    top = Usuario.query.order_by(Usuario.score.desc()).limit(5).all()
    return jsonify([u.to_dict() for u in top])


@bp.route('/api/dashboard/resumo-segmentos')
@staff_required
def resumo_segmentos():
    total   = Segmento.query.count()
    em_risco = Segmento.query.filter(Segmento.risco_alvo.in_(['Alto', 'Crítico'])).count()
    return jsonify({'total': total, 'em_risco': em_risco})


@bp.route('/api/dashboard/resumo-campanhas')
@staff_required
def resumo_campanhas():
    tipos = ['Engajamento', 'Retenção', 'Recuperação', 'Upgrade', 'Ativação']
    return jsonify([{'tipo': t, 'total': Campanha.query.filter_by(tipo=t, status='Ativa').count()} for t in tipos])


@bp.route('/api/dashboard/eventos-recentes')
@staff_required
def eventos_recentes():
    eventos = Evento.query.order_by(Evento.data.desc()).limit(10).all()
    return jsonify([e.to_dict() for e in eventos])
