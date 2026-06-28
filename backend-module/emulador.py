"""
emulador.py — geração de dados sintéticos da cadeia produtiva da castanha.

Módulo SEM efeitos colaterais e sem dependências externas (só biblioteca
padrão). Produz listas de eventos no MESMO contrato que o index.html envia
para POST /mine_event/. É reutilizado por:
  - main.py            -> endpoint POST /emular/ (mineração server-side)
  - emulador_dados.py  -> CLI que envia via HTTP

As 7 etapas oficiais e os domínios fechados (tamanho, status) espelham o
backend e os <select> do formulário.
"""
import random
from datetime import datetime

# As 7 etapas oficiais, na ordem do fluxo (devem casar com o backend).
ETAPAS = [
    "coleta_in_natura",
    "inspecao_entrada",
    "limpeza_lavagem",
    "classificacao_ia_pre",
    "quebra_extracao",
    "classificacao_ia_pos",
    "empacotamento_final",
]

# Domínios fechados (iguais aos <select> do index.html).
TAMANHOS = ["Pequena", "Média", "Grande"]
STATUS = ["Coletado", "Em processamento", "Aprovado"]

# Chaves exatas esperadas pelo mine_event (para validação/instrumentação).
CHAVES_CONTRATO = {
    "id_produto", "origem_coleta", "comunidade_fornecedora", "peso_lote",
    "tamanho", "umidade", "status_produto", "id_etapa", "evento",
    "usuario_responsavel", "dispositivo_origem", "localizacao",
    "nivel_confiabilidade",
}

ORIGENS = [
    "Seringal Cachoeira", "Reserva Chico Mendes", "Floresta Nacional do Tapajós",
    "Ramal do Brasileirinho", "Comunidade do Tumbira", "Castanhal do Rio Negro",
]
COMUNIDADES = [
    "Cooperativa Chico Mendes", "Associação de Castanheiros do Amazonas",
    "Cooperativa Agroextrativista do Médio Juruá", "COOPMAS",
    "Associação Comunitária Nova Esperança",
]
COLETORES = ["João Silva", "Maria dos Santos", "Raimundo Nonato", "Antônia Pereira",
             "Francisco Lima", "Benedita Souza"]
TECNICOS = ["Ana Beltrão", "Carlos Mendes", "Júlia Farias", "Pedro Albuquerque"]
OPERADORES = ["Op. Esteira 01", "Op. Esteira 02", "Op. Linha A", "Op. Linha B"]
LOCAL_FABRICA = ["Fábrica – Manaus, AM (Setor de Recepção)",
                 "Fábrica – Manaus, AM (Linha de Processamento)",
                 "Fábrica – Manaus, AM (Setor de Empacotamento)"]

# Perfil por etapa: como evoluem peso/umidade/confiança + dispositivo/responsável.
PERFIL_ETAPA = {
    "coleta_in_natura": dict(
        dispositivo=lambda r: f"Coletor-Mobile-{r.randint(1, 6):02d}",
        responsavel=lambda r: r.choice(COLETORES),
        status="Coletado", fator_peso=1.0, delta_umidade=0.0, confianca=(100, 100),
        evento=["Coleta in natura realizada no castanhal",
                "Ouriços coletados e ensacados na floresta",
                "Castanha recolhida do solo da mata"],
    ),
    "inspecao_entrada": dict(
        dispositivo=lambda r: "Esteira-Scanner-01",
        responsavel=lambda r: r.choice(OPERADORES),
        status="Em processamento", fator_peso=(0.97, 0.99), delta_umidade=0.0,
        confianca=(96, 100),
        evento=["Triagem inicial na esteira de entrada",
                "Inspeção de entrada e remoção de impurezas grosseiras",
                "Conferência de lote na recepção da fábrica"],
    ),
    "limpeza_lavagem": dict(
        dispositivo=lambda r: f"Lavadora-Industrial-{r.randint(1, 3):02d}",
        responsavel=lambda r: r.choice(OPERADORES),
        status="Em processamento", fator_peso=(0.95, 0.98), delta_umidade=(-8.0, -4.0),
        confianca=(97, 100),
        evento=["Limpeza e lavagem concluídas; lote encaminhado à secagem",
                "Lavagem industrial e pré-secagem do lote"],
    ),
    "classificacao_ia_pre": dict(
        dispositivo=lambda r: f"Cam-VisaoComp-{r.randint(1, 4):02d}",
        responsavel=lambda r: "Sistema IA (Visão Computacional)",
        status="Em processamento", fator_peso=1.0, delta_umidade=0.0, confianca=(88, 99),
        evento=["Classificação por IA (pré-quebra): triagem por tamanho",
                "Visão computacional avaliou tamanho e integridade antes da quebra"],
    ),
    "quebra_extracao": dict(
        dispositivo=lambda r: "Quebradora-Automatizada-01",
        responsavel=lambda r: r.choice(TECNICOS),
        status="Em processamento", fator_peso=(0.38, 0.5), delta_umidade=(-2.0, 0.0),
        confianca=(95, 100),
        evento=["Quebra e extração da amêndoa concluídas",
                "Extração física da amêndoa; casca separada como resíduo"],
    ),
    "classificacao_ia_pos": dict(
        dispositivo=lambda r: f"Cam-VisaoComp-{r.randint(1, 4):02d}",
        responsavel=lambda r: "Sistema IA (Visão Computacional)",
        status="Em processamento", fator_peso=1.0, delta_umidade=0.0, confianca=(85, 99),
        evento=["Classificação por IA (pós-quebra): qualidade e calibre",
                "Visão computacional separou amêndoas por qualidade e tamanho"],
    ),
    "empacotamento_final": dict(
        dispositivo=lambda r: f"Empacotadora-{r.randint(1, 3):02d}",
        responsavel=lambda r: r.choice(TECNICOS),
        status="Aprovado", fator_peso=(0.97, 1.0), delta_umidade=(-4.0, -2.0),
        confianca=(99, 100),
        evento=["Empacotamento final e selagem do pacote pronto para distribuição",
                "Lote aprovado e embalado para expedição"],
    ),
}


def _faixa(r, v):
    """Retorna v se escalar, ou um sorteio uniforme se v for (min, max)."""
    if isinstance(v, tuple):
        return r.uniform(v[0], v[1])
    return v


def gerar_eventos_lote(r, id_produto, prob_descarte=0.0):
    """Lista ordenada de eventos (um por etapa) de um único lote."""
    origem = r.choice(ORIGENS)
    comunidade = r.choice(COMUNIDADES)
    coletor = r.choice(COLETORES)
    tamanho = r.choice(TAMANHOS)
    peso = round(r.uniform(50, 500), 2)
    umidade = round(r.uniform(18, 28), 1)
    lat = -3.1 + r.uniform(-1.5, 1.5)
    lon = -60.0 + r.uniform(-1.5, 1.5)
    coord_coleta = f"{lat:.4f}, {lon:.4f} ({origem})"

    descartado = r.random() < prob_descarte
    eventos = []

    for etapa in ETAPAS:
        perfil = PERFIL_ETAPA[etapa]
        peso = round(peso * _faixa(r, perfil["fator_peso"]), 2)
        umidade = round(max(3.0, umidade + _faixa(r, perfil["delta_umidade"])), 1)
        confianca = round(r.uniform(*perfil["confianca"]), 1)
        evento_txt = r.choice(perfil["evento"])

        if etapa == "coleta_in_natura":
            local, responsavel = coord_coleta, coletor
        else:
            local, responsavel = r.choice(LOCAL_FABRICA), perfil["responsavel"](r)

        if descartado and etapa == "inspecao_entrada":
            evento_txt = "Lote REPROVADO na triagem (ramo NÃO): castanhas descartadas"
            confianca = round(r.uniform(40, 70), 1)

        eventos.append({
            "id_produto": id_produto,
            "origem_coleta": origem,
            "comunidade_fornecedora": comunidade,
            "peso_lote": peso,
            "tamanho": tamanho,
            "umidade": umidade,
            "status_produto": perfil["status"],
            "id_etapa": etapa,
            "evento": evento_txt,
            "usuario_responsavel": responsavel,
            "dispositivo_origem": perfil["dispositivo"](r),
            "localizacao": local,
            "nivel_confiabilidade": confianca,
        })

        if descartado and etapa == "inspecao_entrada":
            break  # ramo "NÃO": fluxo interrompido na triagem

    return eventos


def montar_fila(n_lotes, intercalar=False, prob_descarte=0.0, seed=None, ano=None):
    """
    Sequência de eventos de N lotes.
      - intercalar=False: completa um lote antes do próximo.
      - intercalar=True : round-robin entre lotes (testa o isolamento por lote).
    """
    r = random.Random(seed)
    ano = ano or datetime.now().year
    lotes = [gerar_eventos_lote(r, f"LOTE-{ano}-{n:03d}", prob_descarte)
             for n in range(1, n_lotes + 1)]

    if not intercalar:
        return [ev for lote in lotes for ev in lote]

    fila, restantes = [], [list(l) for l in lotes]
    while any(restantes):
        for bloco in restantes:
            if bloco:
                fila.append(bloco.pop(0))
    return fila
