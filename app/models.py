from app import db
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

usuario_segmento = db.Table('usuario_segmento',
    db.Column('usuario_id', db.Integer, db.ForeignKey('usuario.id'), primary_key=True),
    db.Column('segmento_id', db.Integer, db.ForeignKey('segmento.id'), primary_key=True)
)

class Conta(UserMixin, db.Model):
    __tablename__ = 'conta'
    id            = db.Column(db.Integer, primary_key=True)
    nome          = db.Column(db.String(120), nullable=False)
    email         = db.Column(db.String(120), unique=True, nullable=False)
    senha_hash    = db.Column(db.String(255), nullable=False)
    role          = db.Column(db.String(10), nullable=False, default='B2C')  # Admin, B2B, B2C
    ativo         = db.Column(db.Boolean, default=True)
    company       = db.Column(db.String(100))          # para B2B
    usuario_id    = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=True)  # vínculo B2C
    criado_em     = db.Column(db.DateTime, default=datetime.utcnow)

    usuario = db.relationship('Usuario', backref=db.backref('conta', uselist=False))

    # Flask-Login usa is_active para checar se a conta está habilitada
    @property
    def is_active(self):
        return self.ativo

    @property
    def is_admin(self):
        return self.role == 'Admin'

    @property
    def is_b2b(self):
        return self.role == 'B2B'

    @property
    def is_b2c(self):
        return self.role == 'B2C'

    def set_password(self, senha):
        self.senha_hash = generate_password_hash(senha)

    def check_password(self, senha):
        return check_password_hash(self.senha_hash, senha)

    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'email': self.email,
            'role': self.role,
            'ativo': self.ativo,
            'company': self.company or '',
            'usuario_id': self.usuario_id,
            'criado_em': self.criado_em.strftime('%d/%m/%Y') if self.criado_em else '',
        }


class Usuario(db.Model):
    id            = db.Column(db.Integer, primary_key=True)
    nome          = db.Column(db.String(120), nullable=False)
    email         = db.Column(db.String(120), unique=True, nullable=False)
    score         = db.Column(db.Integer, default=0)
    faixa         = db.Column(db.String(20), default='Médio')
    risco         = db.Column(db.String(30), default='Sem Risco')
    engajamento   = db.Column(db.String(20), default='Médio')
    pontos        = db.Column(db.Float, default=0.0)
    plano         = db.Column(db.String(30), default='Essencial')
    tempo_cliente = db.Column(db.Integer, default=0)
    criado_em     = db.Column(db.DateTime, default=datetime.utcnow)

    segmentos = db.relationship('Segmento', secondary=usuario_segmento, back_populates='usuarios')
    eventos   = db.relationship('Evento', backref='usuario', lazy=True)
    riscos    = db.relationship('RiscoAtraso', backref='usuario', lazy=True)

    @property
    def segmento_principal(self):
        return self.segmentos[0].nome if self.segmentos else '—'

    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'email': self.email,
            'score': self.score,
            'faixa': self.faixa,
            'risco': self.risco,
            'engajamento': self.engajamento,
            'pontos': self.pontos,
            'plano': self.plano,
            'tempo_cliente': self.tempo_cliente,
            'segmento': self.segmento_principal,
        }


class Segmento(db.Model):
    id               = db.Column(db.Integer, primary_key=True)
    nome             = db.Column(db.String(100), nullable=False)
    tipo             = db.Column(db.String(50), default='Automático')
    criterios        = db.Column(db.Text)
    descricao        = db.Column(db.Text)
    score_min        = db.Column(db.Integer)
    score_max        = db.Column(db.Integer)
    risco_alvo       = db.Column(db.String(30))
    engajamento_alvo = db.Column(db.String(30))
    prioritario      = db.Column(db.Boolean, default=False)
    atualizado_em    = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    usuarios  = db.relationship('Usuario', secondary=usuario_segmento, back_populates='segmentos')
    campanhas = db.relationship('Campanha', backref='segmento', lazy=True)

    @property
    def tamanho(self):
        return len(self.usuarios)

    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'tipo': self.tipo,
            'criterios': self.criterios,
            'tamanho': self.tamanho,
            'prioritario': self.prioritario,
            'atualizado_em': self.atualizado_em.strftime('%d/%m/%Y') if self.atualizado_em else '',
        }


class Reward(db.Model):
    id             = db.Column(db.Integer, primary_key=True)
    nome           = db.Column(db.String(120), nullable=False)
    tipo           = db.Column(db.String(30), nullable=False)
    status         = db.Column(db.String(20), default='Ativo')
    custo_cashback = db.Column(db.Float, default=0.0)
    parceiro       = db.Column(db.String(100))
    resgates       = db.Column(db.Integer, default=0)
    criado_em      = db.Column(db.DateTime, default=datetime.utcnow)

    campanhas = db.relationship('Campanha', backref='reward', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'tipo': self.tipo,
            'status': self.status,
            'custo_cashback': self.custo_cashback,
            'parceiro': self.parceiro,
            'resgates': self.resgates,
            'campanhas': len(self.campanhas),
        }


class Campanha(db.Model):
    id                 = db.Column(db.Integer, primary_key=True)
    nome               = db.Column(db.String(120), nullable=False)
    tipo               = db.Column(db.String(30), nullable=False)
    status             = db.Column(db.String(20), default='Rascunho')
    segmento_id        = db.Column(db.Integer, db.ForeignKey('segmento.id'))
    reward_id          = db.Column(db.Integer, db.ForeignKey('reward.id'))
    vigencia_inicio    = db.Column(db.Date)
    vigencia_fim       = db.Column(db.Date)
    usuarios_alcancados = db.Column(db.Integer, default=0)
    engajamento_pct    = db.Column(db.Float, default=0.0)
    criado_em          = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'tipo': self.tipo,
            'status': self.status,
            'segmento': self.segmento.nome if self.segmento else '—',
            'reward': self.reward.nome if self.reward else '—',
            'vigencia_inicio': self.vigencia_inicio.strftime('%d/%m/%Y') if self.vigencia_inicio else '',
            'vigencia_fim': self.vigencia_fim.strftime('%d/%m/%Y') if self.vigencia_fim else '',
            'usuarios_alcancados': self.usuarios_alcancados,
            'engajamento_pct': self.engajamento_pct,
        }


class Evento(db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    tipo       = db.Column(db.String(50), nullable=False)
    descricao  = db.Column(db.Text)
    valor      = db.Column(db.Float)
    data       = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'usuario_id': self.usuario_id,
            'usuario': self.usuario.nome if self.usuario else '—',
            'tipo': self.tipo,
            'descricao': self.descricao,
            'valor': self.valor,
            'data': self.data.strftime('%d/%m/%Y %H:%M') if self.data else '',
        }


class RiscoAtraso(db.Model):
    id              = db.Column(db.Integer, primary_key=True)
    usuario_id      = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    nivel_risco     = db.Column(db.String(30), nullable=False)
    valor_em_risco  = db.Column(db.Float, default=0.0)
    produto_plano   = db.Column(db.String(50))
    data_vencimento = db.Column(db.Date)
    dias_atraso     = db.Column(db.Integer, default=0)
    tipo_pagamento  = db.Column(db.String(30))
    atualizado_em   = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'usuario_id': self.usuario_id,
            'usuario': self.usuario.nome if self.usuario else '—',
            'email': self.usuario.email if self.usuario else '—',
            'score': self.usuario.score if self.usuario else 0,
            'nivel_risco': self.nivel_risco,
            'valor_em_risco': self.valor_em_risco,
            'produto_plano': self.produto_plano,
            'data_vencimento': self.data_vencimento.strftime('%d/%m/%Y') if self.data_vencimento else '',
            'dias_atraso': self.dias_atraso,
            'tipo_pagamento': self.tipo_pagamento,
            'tempo_cliente': self.usuario.tempo_cliente if self.usuario else 0,
        }
