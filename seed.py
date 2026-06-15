"""
Popula o banco de dados com dados de exemplo.
Execute: python seed.py
"""
from app import create_app, db
from app.models import Usuario, Segmento, Reward, Campanha, Evento, RiscoAtraso, Conta
from datetime import date, datetime, timedelta
import random

app = create_app()

NOMES = [
    "Maria Almeida","Fernanda Carvalho","Igor Nascimento","Priscila Duarte","Gustavo Oliveira",
    "Sandra Freitas","Diego Fonseca","Beatriz Moreira","Rodrigo Gomes","Camila Faria",
    "Douglas Santos","Silvia Costa","Rafael Pereira","Ana Lima","Carlos Rocha",
    "Juliana Martins","Thiago Barbosa","Larissa Souza","Felipe Nunes","Mariana Castro",
    "Bruno Ferreira","Tatiane Ribeiro","Lucas Mendes","Patricia Andrade","Marcos Dias",
    "Vanessa Cardoso","Eduardo Teixeira","Renata Vieira","André Monteiro","Cristina Lopes",
    "Roberto Correia","Fernanda Silva","Paulo Costa","Aline Nascimento","Ricardo Melo",
    "Simone Ramos","Henrique Alves","Daniela Pinto","Fábio Carvalho","Luciana Moura",
    "Alexandre Cunha","Tatiana Borges","Flávio Santos","Adriana Reis","Jorge Lima",
    "Camila Araujo","Renato Brito","Vanessa Torres","Leonardo Gomes","Priscila Siqueira",
]

EMAILS = [n.lower().replace(' ','.')+f'@email.com' for n in NOMES]

PLANOS = ['Essencial', 'Standard', 'Premium']
FAIXAS = ['Muito Alto', 'Alto', 'Médio', 'Baixo', 'Muito Baixo']
RISCOS = ['Sem Risco', 'Baixo', 'Moderado', 'Alto', 'Crítico']
ENGAJAMENTOS = ['Muito Alto', 'Alto', 'Médio', 'Baixo', 'Cancelado']
TIPOS_EVENTO = ['Pagamento Efetuado', 'Login', 'Resgate de Pontos', 'Upgrade de Plano', 'Acesso ao App', 'Contato Suporte']
PRODUTOS = ['Plano Básico', 'Plano Standard', 'Plano Gold', 'Plano Premium']
NIVEIS_RISCO = ['Baixo', 'Moderado', 'Alto', 'Crítico']

def score_para_faixa(score):
    if score >= 850: return 'Muito Alto'
    if score >= 700: return 'Alto'
    if score >= 500: return 'Médio'
    if score >= 300: return 'Baixo'
    return 'Muito Baixo'

def score_para_risco(score):
    if score >= 750: return 'Sem Risco'
    if score >= 600: return 'Baixo'
    if score >= 450: return 'Moderado'
    if score >= 300: return 'Alto'
    return 'Crítico'

with app.app_context():
    db.drop_all()
    db.create_all()

    # Segmentos
    segmentos = [
        Segmento(nome='VIP Sem Risco', tipo='Automático', criterios='Score: Muito Alto | Risco: Sem Risco',
                 score_min=850, risco_alvo='Sem Risco', prioritario=True),
        Segmento(nome='Alta Renda em Observação', tipo='Automático', criterios='Pontos: Alto | Risco: Moderado',
                 score_min=600, risco_alvo='Moderado', prioritario=True),
        Segmento(nome='Novos Campeões', tipo='Automático', criterios='Score: Alto | Tempo < 12 meses',
                 score_min=700, prioritario=True),
        Segmento(nome='Recuperação Crítica', tipo='Automático', criterios='Risco: Crítico | Engajamento: Baixo',
                 risco_alvo='Crítico', engajamento_alvo='Baixo', prioritario=True),
        Segmento(nome='Engajamento Médio', tipo='Manual', criterios='Engajamento: Médio',
                 engajamento_alvo='Médio', prioritario=False),
        Segmento(nome='Plano Premium', tipo='Manual', criterios='Plano: Premium', prioritario=False),
    ]
    for s in segmentos:
        db.session.add(s)
    db.session.flush()

    # Rewards
    rewards = [
        Reward(nome='Cashback 5% Fatura', tipo='Cashback', status='Ativo', custo_cashback=50.0, parceiro='Banco Parceiro', resgates=342),
        Reward(nome='Mês Grátis Premium', tipo='Troca por Assinatura', status='Ativo', custo_cashback=99.0, parceiro='Essentia', resgates=87),
        Reward(nome='Desconto 20% Loja', tipo='Cupom/Desconto', status='Ativo', custo_cashback=30.0, parceiro='Loja Parceira', resgates=215),
        Reward(nome='Instalação Gratuita', tipo='Troca por Serviço', status='Ativo', custo_cashback=120.0, parceiro='Técnicos Parceiros', resgates=43),
        Reward(nome='Pontos em Dobro', tipo='Benefício', status='Ativo', custo_cashback=0.0, parceiro='Essentia', resgates=189),
        Reward(nome='Cashback 10% Recarga', tipo='Cashback', status='Ativo', custo_cashback=80.0, parceiro='Operadora', resgates=156),
        Reward(nome='Upgrade Temporário', tipo='Troca por Assinatura', status='Ativo', custo_cashback=49.0, parceiro='Essentia', resgates=72),
        Reward(nome='Cupom R$50 Parceiro', tipo='Cupom/Desconto', status='Inativo', custo_cashback=50.0, parceiro='Shopping Parceiro', resgates=98),
    ]
    for r in rewards:
        db.session.add(r)
    db.session.flush()

    # Campanhas
    campanhas = [
        Campanha(nome='Engajamento Verde', tipo='Engajamento', status='Ativa',
                 segmento_id=segmentos[0].id, reward_id=rewards[0].id,
                 vigencia_inicio=date(2026,1,1), vigencia_fim=date(2026,6,30),
                 usuarios_alcancados=490, engajamento_pct=45.2),
        Campanha(nome='Boas-vindas Novos Clientes', tipo='Ativação', status='Ativa',
                 segmento_id=segmentos[2].id, reward_id=rewards[4].id,
                 vigencia_inicio=date(2026,2,1), vigencia_fim=date(2026,12,31),
                 usuarios_alcancados=150, engajamento_pct=62.1),
        Campanha(nome='Upgrade para Plano Gold', tipo='Upgrade', status='Agendada',
                 segmento_id=segmentos[1].id, reward_id=rewards[6].id,
                 vigencia_inicio=date(2026,7,1), vigencia_fim=date(2026,9,30),
                 usuarios_alcancados=245, engajamento_pct=0.0),
        Campanha(nome='Recuperação Engajamento Premium', tipo='Recuperação', status='Ativa',
                 segmento_id=segmentos[3].id, reward_id=rewards[1].id,
                 vigencia_inicio=date(2026,3,1), vigencia_fim=date(2026,6,30),
                 usuarios_alcancados=80, engajamento_pct=18.9),
        Campanha(nome='Retenção Alto Risco', tipo='Retenção', status='Pausada',
                 segmento_id=segmentos[3].id, reward_id=rewards[5].id,
                 vigencia_inicio=date(2026,1,15), vigencia_fim=date(2026,5,31),
                 usuarios_alcancados=80, engajamento_pct=31.5),
    ]
    for c in campanhas:
        db.session.add(c)
    db.session.flush()

    # Usuários
    usuarios_criados = []
    for i, nome in enumerate(NOMES):
        score = random.randint(100, 980)
        faixa = score_para_faixa(score)
        risco = score_para_risco(score)
        engajamento = random.choice(ENGAJAMENTOS)
        pontos = round(random.uniform(50, 12000), 0)
        plano = random.choice(PLANOS)
        tempo = random.randint(1, 84)

        u = Usuario(
            nome=nome,
            email=EMAILS[i],
            score=score,
            faixa=faixa,
            risco=risco,
            engajamento=engajamento,
            pontos=pontos,
            plano=plano,
            tempo_cliente=tempo,
        )
        # Vincular a segmento
        if score >= 850:
            u.segmentos.append(segmentos[0])
        elif score >= 700:
            u.segmentos.append(segmentos[2])
        elif risco == 'Crítico':
            u.segmentos.append(segmentos[3])
        else:
            u.segmentos.append(segmentos[4])

        db.session.add(u)
        usuarios_criados.append(u)

    db.session.flush()

    # Eventos
    for u in usuarios_criados:
        n_eventos = random.randint(1, 8)
        for _ in range(n_eventos):
            tipo = random.choice(TIPOS_EVENTO)
            valor = round(random.uniform(10, 500), 2) if tipo in ('Pagamento Efetuado', 'Resgate de Pontos') else None
            evento = Evento(
                usuario_id=u.id,
                tipo=tipo,
                descricao=f'{tipo} realizado pelo usuário',
                valor=valor,
                data=datetime.utcnow() - timedelta(days=random.randint(0, 90)),
            )
            db.session.add(evento)

    # Risco de atraso (para usuários com risco Alto/Crítico + alguns Moderado)
    usuarios_risco = [u for u in usuarios_criados if u.risco in ('Alto', 'Crítico', 'Moderado')]
    random.shuffle(usuarios_risco)
    for u in usuarios_risco[:30]:
        nivel = 'Crítico' if u.risco == 'Crítico' else ('Alto' if u.risco == 'Alto' else 'Moderado')
        risco_rec = RiscoAtraso(
            usuario_id=u.id,
            nivel_risco=nivel,
            valor_em_risco=round(random.uniform(500, 50000), 2),
            produto_plano=random.choice(PRODUTOS),
            data_vencimento=date.today() + timedelta(days=random.randint(-10, 30)),
            dias_atraso=random.randint(0, 45) if nivel in ('Alto', 'Crítico') else 0,
            tipo_pagamento=random.choice(['Débito Automático', 'Boleto', 'Cartão de Crédito', 'PIX']),
        )
        db.session.add(risco_rec)

    db.session.commit()

    # --- Contas de acesso ---
    primeiro_usuario = usuarios_criados[0]  # Maria Almeida → conta B2C de exemplo

    contas_seed = [
        ('Admin Essentia',  'admin@essentia.com',          'admin123',   'Admin', None,             None),
        ('Gestor Comercial', 'gestor@essentia.com',         'gestor123',  'B2B',  'Essentia Corp',  None),
        (primeiro_usuario.nome, primeiro_usuario.email,    'cliente123', 'B2C',  None,             primeiro_usuario.id),
    ]
    for nome, email, senha, role, company, uid in contas_seed:
        c = Conta(nome=nome, email=email, role=role, company=company, usuario_id=uid)
        c.set_password(senha)
        db.session.add(c)

    db.session.commit()
    print("Banco de dados populado com sucesso!")
    print(f"  - {Usuario.query.count()} usuarios")
    print(f"  - {Segmento.query.count()} segmentos")
    print(f"  - {Campanha.query.count()} campanhas")
    print(f"  - {Reward.query.count()} rewards")
    print(f"  - {Evento.query.count()} eventos")
    print(f"  - {RiscoAtraso.query.count()} registros de risco")
    print(f"  - {Conta.query.count()} contas de acesso")
    print()
    print("Contas criadas:")
    print("  Admin  → admin@essentia.com       / admin123")
    print("  B2B    → gestor@essentia.com      / gestor123")
    print(f"  B2C    → {primeiro_usuario.email} / cliente123")
