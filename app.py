from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Any

import streamlit as st


# -----------------------------------------------------------------------------
# Configuração
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Quiz de Mitologias",
    page_icon="✦",
    layout="centered",
    initial_sidebar_state="collapsed",
)

BASE_DIR = Path(__file__).resolve().parent
DATA_GLOB = "mitologias_parte_*.json"

PALETTE = {
    "taupe": "#93827F",
    "cream": "#F3F9D2",
    "sage": "#BDC4A7",
    "charcoal": "#2F2F2F",
    "mint": "#92B4A7",
}


# -----------------------------------------------------------------------------
# Estilo
# -----------------------------------------------------------------------------
st.markdown(
    f"""
    <style>
        :root {{
            --taupe: {PALETTE['taupe']};
            --cream: {PALETTE['cream']};
            --sage: {PALETTE['sage']};
            --charcoal: {PALETTE['charcoal']};
            --mint: {PALETTE['mint']};
        }}

        html, body, [class*="css"] {{
            font-family: Inter, ui-sans-serif, -apple-system, BlinkMacSystemFont,
                         "Segoe UI", sans-serif;
        }}

        .stApp {{
            background:
                radial-gradient(circle at 10% 0%, rgba(146,180,167,.28), transparent 32%),
                radial-gradient(circle at 95% 10%, rgba(147,130,127,.16), transparent 26%),
                var(--cream);
            color: var(--charcoal);
        }}

        .block-container {{
            max-width: 860px;
            padding-top: 2.2rem;
            padding-bottom: 4rem;
        }}

        #MainMenu, footer, header {{ visibility: hidden; }}

        .eyebrow {{
            color: var(--taupe);
            font-weight: 800;
            letter-spacing: .14em;
            text-transform: uppercase;
            font-size: .78rem;
            margin-bottom: .35rem;
        }}

        .hero-title {{
            font-size: clamp(2.2rem, 6vw, 4.2rem);
            line-height: .98;
            letter-spacing: -.055em;
            color: var(--charcoal);
            font-weight: 900;
            margin: 0;
        }}

        .hero-subtitle {{
            color: rgba(47,47,47,.72);
            max-width: 650px;
            font-size: 1.02rem;
            margin-top: .9rem;
            margin-bottom: 1.7rem;
        }}

        .surface {{
            background: rgba(255,255,255,.68);
            border: 1px solid rgba(147,130,127,.28);
            box-shadow: 0 16px 45px rgba(47,47,47,.06);
            border-radius: 24px;
            padding: 1.2rem 1.25rem;
            margin: .8rem 0 1.2rem 0;
            backdrop-filter: blur(8px);
        }}

        .question-card {{
            background: rgba(255,255,255,.80);
            border: 1px solid rgba(146,180,167,.45);
            border-radius: 28px;
            padding: 1.45rem 1.55rem 1.2rem 1.55rem;
            box-shadow: 0 22px 60px rgba(47,47,47,.08);
            margin-top: 1rem;
            margin-bottom: .9rem;
        }}

        .category-chip {{
            display: inline-flex;
            align-items: center;
            gap: .4rem;
            background: rgba(146,180,167,.23);
            color: var(--charcoal);
            border: 1px solid rgba(146,180,167,.48);
            border-radius: 999px;
            padding: .35rem .68rem;
            font-size: .78rem;
            font-weight: 800;
            margin-bottom: 1rem;
        }}

        .question-text {{
            font-size: clamp(1.22rem, 2.8vw, 1.72rem);
            line-height: 1.35;
            font-weight: 800;
            letter-spacing: -.02em;
            color: var(--charcoal);
            margin-bottom: .2rem;
        }}

        .mini-label {{
            color: rgba(47,47,47,.62);
            font-size: .82rem;
            font-weight: 700;
        }}

        div[data-testid="stMultiSelect"] > div {{
            border-radius: 16px !important;
        }}

        div[data-baseweb="select"] > div {{
            background: rgba(255,255,255,.75) !important;
            border-color: rgba(147,130,127,.35) !important;
            min-height: 50px;
        }}

        .stButton > button {{
            min-height: 48px;
            border-radius: 16px;
            border: 1px solid rgba(47,47,47,.13);
            font-weight: 800;
            transition: transform .12s ease, box-shadow .12s ease, border-color .12s ease;
        }}

        .stButton > button:hover {{
            transform: translateY(-1px);
            border-color: var(--taupe);
            box-shadow: 0 8px 20px rgba(47,47,47,.08);
        }}

        div[data-testid="stMetric"] {{
            background: rgba(255,255,255,.58);
            border: 1px solid rgba(189,196,167,.65);
            border-radius: 18px;
            padding: .8rem 1rem;
        }}

        div[data-testid="stMetricLabel"] {{
            color: rgba(47,47,47,.62);
        }}

        .feedback-correct {{
            background: rgba(146,180,167,.25);
            border: 1px solid rgba(146,180,167,.8);
            border-radius: 18px;
            padding: .9rem 1rem;
            font-weight: 800;
            margin: .65rem 0;
        }}

        .feedback-wrong {{
            background: rgba(147,130,127,.14);
            border: 1px solid rgba(147,130,127,.55);
            border-radius: 18px;
            padding: .9rem 1rem;
            font-weight: 750;
            margin: .65rem 0;
        }}

        @media (max-width: 640px) {{
            .block-container {{
                padding: 1.25rem .9rem 3rem .9rem;
            }}
            .question-card {{
                padding: 1.15rem 1rem;
                border-radius: 22px;
            }}
            .surface {{
                padding: 1rem;
                border-radius: 20px;
            }}
        }}
    </style>
    """,
    unsafe_allow_html=True,
)


# -----------------------------------------------------------------------------
# Dados
# -----------------------------------------------------------------------------
@st.cache_data(show_spinner=False)
def carregar_banco() -> dict[str, list[dict[str, Any]]]:
    arquivos = sorted(BASE_DIR.glob(DATA_GLOB))
    if not arquivos:
        raise FileNotFoundError(
            "Nenhum arquivo de perguntas foi encontrado. "
            f"Mantenha os arquivos {DATA_GLOB} na mesma pasta do app.py."
        )

    banco: dict[str, list[dict[str, Any]]] = {}
    for caminho in arquivos:
        with caminho.open("r", encoding="utf-8") as arquivo:
            bloco = json.load(arquivo)

        if not isinstance(bloco, dict):
            raise ValueError(f"Formato inválido em {caminho.name}.")

        duplicados = set(banco).intersection(bloco)
        if duplicados:
            raise ValueError(
                f"Categorias duplicadas em {caminho.name}: {', '.join(sorted(duplicados))}"
            )
        banco.update(bloco)

    if not banco:
        raise ValueError("O banco de perguntas está vazio.")

    return banco


try:
    BANCO = carregar_banco()
except (FileNotFoundError, json.JSONDecodeError, ValueError) as erro:
    st.error(str(erro))
    st.stop()

CATEGORIAS = list(BANCO.keys())


# -----------------------------------------------------------------------------
# Estado
# -----------------------------------------------------------------------------
def inicializar_estado() -> None:
    defaults = {
        "categorias_widget": CATEGORIAS.copy(),
        "pergunta_atual": None,
        "respondida": False,
        "resposta_escolhida": None,
        "historico_ids": set(),
        "acertos": 0,
        "respondidas": 0,
        "ciclo_reiniciado": False,
    }

    for chave, valor in defaults.items():
        if chave not in st.session_state:
            st.session_state[chave] = valor


def resetar_pergunta_atual() -> None:
    st.session_state.pergunta_atual = None
    st.session_state.respondida = False
    st.session_state.resposta_escolhida = None


def selecionar_todas() -> None:
    st.session_state.categorias_widget = CATEGORIAS.copy()
    resetar_pergunta_atual()


def limpar_selecao() -> None:
    st.session_state.categorias_widget = []
    resetar_pergunta_atual()


def categorias_alteradas() -> None:
    resetar_pergunta_atual()


def zerar_sessao() -> None:
    st.session_state.historico_ids = set()
    st.session_state.acertos = 0
    st.session_state.respondidas = 0
    st.session_state.ciclo_reiniciado = False
    resetar_pergunta_atual()


inicializar_estado()


# -----------------------------------------------------------------------------
# Sorteio e resposta
# -----------------------------------------------------------------------------
def montar_pool(categorias_selecionadas: list[str]) -> list[dict[str, Any]]:
    pool: list[dict[str, Any]] = []

    for tema in categorias_selecionadas:
        for indice, pergunta in enumerate(BANCO[tema]):
            pool.append(
                {
                    "id": f"{tema}::{indice}",
                    "tema": tema,
                    "pergunta": pergunta["pergunta"],
                    "opcoes": pergunta["opcoes"],
                    "correta": pergunta["correta"],
                }
            )

    return pool


def sortear_pergunta() -> None:
    selecionadas = st.session_state.categorias_widget

    if not selecionadas:
        resetar_pergunta_atual()
        return

    pool = montar_pool(selecionadas)
    disponiveis = [
        item for item in pool if item["id"] not in st.session_state.historico_ids
    ]

    # Quando todas as perguntas das categorias selecionadas já tiverem aparecido,
    # inicia automaticamente um novo ciclo sem afetar pontuação.
    if not disponiveis:
        ids_do_pool = {item["id"] for item in pool}
        st.session_state.historico_ids -= ids_do_pool
        disponiveis = pool
        st.session_state.ciclo_reiniciado = True
    else:
        st.session_state.ciclo_reiniciado = False

    escolhida = random.choice(disponiveis).copy()
    opcoes_embaralhadas = escolhida["opcoes"].copy()
    random.shuffle(opcoes_embaralhadas)
    escolhida["opcoes"] = opcoes_embaralhadas

    st.session_state.pergunta_atual = escolhida
    st.session_state.respondida = False
    st.session_state.resposta_escolhida = None
    st.session_state.historico_ids.add(escolhida["id"])


def responder(opcao: str) -> None:
    if st.session_state.respondida or not st.session_state.pergunta_atual:
        return

    st.session_state.respondida = True
    st.session_state.resposta_escolhida = opcao
    st.session_state.respondidas += 1

    if opcao == st.session_state.pergunta_atual["correta"]:
        st.session_state.acertos += 1


# -----------------------------------------------------------------------------
# Cabeçalho
# -----------------------------------------------------------------------------
st.markdown('<div class="eyebrow">Banco com 800 perguntas</div>', unsafe_allow_html=True)
st.markdown('<h1 class="hero-title">Quiz de Mitologias</h1>', unsafe_allow_html=True)
st.markdown(
    '<div class="hero-subtitle">Escolha uma, várias ou todas as mitologias. '
    'As perguntas são sorteadas sem repetição até o conjunto selecionado se esgotar.</div>',
    unsafe_allow_html=True,
)


# -----------------------------------------------------------------------------
# Seleção de categorias
# -----------------------------------------------------------------------------
st.markdown('<div class="surface">', unsafe_allow_html=True)

cab1, cab2 = st.columns([3, 2])
with cab1:
    st.markdown("### Categorias")
    st.caption("Você pode combinar quantas quiser.")
with cab2:
    c1, c2 = st.columns(2)
    with c1:
        st.button(
            "Selecionar todas",
            use_container_width=True,
            on_click=selecionar_todas,
        )
    with c2:
        st.button(
            "Limpar",
            use_container_width=True,
            on_click=limpar_selecao,
        )

selecionadas = st.multiselect(
    "Mitologias selecionadas",
    options=CATEGORIAS,
    key="categorias_widget",
    label_visibility="collapsed",
    placeholder="Escolha uma ou mais mitologias…",
    on_change=categorias_alteradas,
)

quantidade_perguntas = sum(len(BANCO[c]) for c in selecionadas)
st.caption(
    f"{len(selecionadas)} de {len(CATEGORIAS)} categorias selecionadas"
    f" · {quantidade_perguntas} perguntas disponíveis"
)

st.markdown('</div>', unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# Métricas da sessão
# -----------------------------------------------------------------------------
if st.session_state.respondidas:
    precisao = round((st.session_state.acertos / st.session_state.respondidas) * 100)
else:
    precisao = 0

m1, m2, m3 = st.columns(3)
with m1:
    st.metric("Respondidas", st.session_state.respondidas)
with m2:
    st.metric("Acertos", st.session_state.acertos)
with m3:
    st.metric("Aproveitamento", f"{precisao}%")


# -----------------------------------------------------------------------------
# Área do quiz
# -----------------------------------------------------------------------------
if not selecionadas:
    st.info("Selecione pelo menos uma categoria para começar.")
    st.stop()

if st.session_state.pergunta_atual is None:
    sortear_pergunta()

if st.session_state.ciclo_reiniciado:
    st.toast("Todas as perguntas selecionadas já apareceram. Um novo ciclo foi iniciado.")
    st.session_state.ciclo_reiniciado = False

pergunta = st.session_state.pergunta_atual

st.markdown(
    f"""
    <div class="question-card">
        <div class="category-chip">✦ {pergunta['tema']}</div>
        <div class="mini-label">PERGUNTA ALEATÓRIA</div>
        <div class="question-text">{pergunta['pergunta']}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

letras = ["A", "B", "C", "D"]

for letra, opcao in zip(letras, pergunta["opcoes"]):
    desabilitado = st.session_state.respondida
    st.button(
        f"{letra}   {opcao}",
        key=f"opcao_{pergunta['id']}_{letra}",
        use_container_width=True,
        disabled=desabilitado,
        on_click=responder,
        args=(opcao,),
    )


# -----------------------------------------------------------------------------
# Feedback e ações
# -----------------------------------------------------------------------------
if st.session_state.respondida:
    acertou = st.session_state.resposta_escolhida == pergunta["correta"]

    if acertou:
        st.markdown(
            '<div class="feedback-correct">✓ Resposta correta.</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f'<div class="feedback-wrong">Resposta correta: '
            f'<strong>{pergunta["correta"]}</strong></div>',
            unsafe_allow_html=True,
        )

    a1, a2 = st.columns([3, 2])
    with a1:
        st.button(
            "Próxima pergunta →",
            type="primary",
            use_container_width=True,
            on_click=sortear_pergunta,
        )
    with a2:
        st.button(
            "Zerar sessão",
            use_container_width=True,
            on_click=zerar_sessao,
        )
else:
    a1, a2 = st.columns([3, 2])
    with a1:
        st.button(
            "Sortear outra pergunta",
            use_container_width=True,
            on_click=sortear_pergunta,
        )
    with a2:
        st.button(
            "Zerar sessão",
            use_container_width=True,
            on_click=zerar_sessao,
        )

st.caption("As alternativas são embaralhadas a cada sorteio para evitar padrões de posição da resposta correta.")
