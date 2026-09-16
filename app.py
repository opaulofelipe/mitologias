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
DATA_FILE = BASE_DIR / "mitologias_completo_50_temas_800_perguntas.json"

PALETTE = {
    "taupe": "#93827F",
    "cream": "#F3F9D2",
    "sage": "#BDC4A7",
    "charcoal": "#2F2F2F",
    "mint": "#92B4A7",
}


# -----------------------------------------------------------------------------
# CSS mínimo — o tema principal fica em .streamlit/config.toml
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

        #MainMenu, footer {{ visibility: hidden; }}

        .block-container {{
            max-width: 780px;
            padding-top: 1.8rem;
            padding-bottom: 3rem;
        }}

        .kicker {{
            margin: 0 0 .35rem 0;
            color: var(--taupe);
            font-size: .78rem;
            font-weight: 800;
            letter-spacing: .12em;
            text-transform: uppercase;
        }}

        .title {{
            margin: 0;
            color: var(--charcoal);
            font-size: clamp(2rem, 7vw, 3.7rem);
            line-height: 1.02;
            letter-spacing: -.045em;
            font-weight: 850;
        }}

        .subtitle {{
            margin: .75rem 0 1.5rem 0;
            max-width: 640px;
            color: #4D4D4D;
            font-size: 1rem;
            line-height: 1.55;
        }}

        .question-shell {{
            margin-top: 1rem;
            padding: 1.35rem 1.35rem 1.1rem 1.35rem;
            background: #FFFFFF;
            border: 1px solid #B8B8B0;
            border-radius: 18px;
            box-shadow: 0 8px 24px rgba(47, 47, 47, .06);
        }}

        .category-badge {{
            display: inline-flex;
            align-items: center;
            margin-bottom: .85rem;
            padding: .34rem .65rem;
            border-radius: 999px;
            background: var(--mint);
            color: var(--charcoal);
            font-size: .78rem;
            font-weight: 800;
        }}

        .question-label {{
            margin-bottom: .28rem;
            color: #686868;
            font-size: .75rem;
            font-weight: 800;
            letter-spacing: .08em;
            text-transform: uppercase;
        }}

        .question-text {{
            margin: 0;
            color: var(--charcoal);
            font-size: clamp(1.28rem, 3vw, 1.65rem);
            line-height: 1.4;
            font-weight: 800;
            letter-spacing: -.015em;
        }}

        .feedback-ok, .feedback-no {{
            margin: .85rem 0;
            padding: .9rem 1rem;
            border-radius: 14px;
            color: var(--charcoal);
            line-height: 1.45;
            font-weight: 750;
        }}

        .feedback-ok {{
            background: #DCEAE5;
            border: 1px solid var(--mint);
        }}

        .feedback-no {{
            background: #ECE6E4;
            border: 1px solid var(--taupe);
        }}

        /* Alternativas: área confortável e texto sempre escuro. */
        div[role="radiogroup"] {{
            gap: .35rem;
        }}

        div[role="radiogroup"] label {{
            min-height: 48px;
            padding: .55rem .65rem;
            border-radius: 12px;
        }}

        div[role="radiogroup"] label p {{
            color: var(--charcoal) !important;
            font-size: 1rem !important;
            line-height: 1.35 !important;
        }}

        /* Garante legibilidade de todos os botões, inclusive secundários. */
        .stButton button {{
            min-height: 46px;
            font-weight: 750 !important;
        }}

        .stButton button[kind="secondary"] {{
            color: var(--charcoal) !important;
            background: #FFFFFF !important;
            border-color: #8A8A83 !important;
        }}

        .stButton button[kind="secondary"] p,
        .stButton button[kind="tertiary"] p {{
            color: var(--charcoal) !important;
        }}

        div[data-testid="stMetric"] {{
            background: #FFFFFF;
            border: 1px solid #C6C6BD;
            border-radius: 14px;
            padding: .75rem .9rem;
        }}

        div[data-testid="stMetric"] label p {{
            color: #666666 !important;
        }}

        div[data-testid="stMetricValue"] {{
            color: var(--charcoal) !important;
        }}

        @media (max-width: 640px) {{
            .block-container {{
                padding: 1.15rem .85rem 2.4rem .85rem;
            }}
            .question-shell {{
                padding: 1.05rem;
                border-radius: 16px;
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
    if not DATA_FILE.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {DATA_FILE.name}.")

    with DATA_FILE.open("r", encoding="utf-8") as arquivo:
        banco = json.load(arquivo)

    if not isinstance(banco, dict) or not banco:
        raise ValueError("O banco de perguntas está vazio ou em formato inválido.")

    return banco


try:
    BANCO = carregar_banco()
except (FileNotFoundError, json.JSONDecodeError, ValueError) as erro:
    st.error(str(erro))
    st.stop()

CATEGORIAS = list(BANCO.keys())
TOTAL_PERGUNTAS = sum(len(v) for v in BANCO.values())


# -----------------------------------------------------------------------------
# Estado
# -----------------------------------------------------------------------------
def inicializar_estado() -> None:
    defaults = {
        "modo_todas": True,
        "categorias_widget": [],
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
    st.session_state.modo_todas = True
    st.session_state.categorias_widget = []
    resetar_pergunta_atual()


def limpar_selecao() -> None:
    st.session_state.modo_todas = False
    st.session_state.categorias_widget = []
    resetar_pergunta_atual()


def categorias_alteradas() -> None:
    st.session_state.modo_todas = False
    resetar_pergunta_atual()


def zerar_sessao() -> None:
    st.session_state.historico_ids = set()
    st.session_state.acertos = 0
    st.session_state.respondidas = 0
    st.session_state.ciclo_reiniciado = False
    resetar_pergunta_atual()


inicializar_estado()


def categorias_ativas() -> list[str]:
    if st.session_state.modo_todas:
        return CATEGORIAS.copy()
    return st.session_state.categorias_widget.copy()


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
    selecionadas = categorias_ativas()
    if not selecionadas:
        resetar_pergunta_atual()
        return

    pool = montar_pool(selecionadas)
    disponiveis = [
        item for item in pool if item["id"] not in st.session_state.historico_ids
    ]

    if not disponiveis:
        ids_do_pool = {item["id"] for item in pool}
        st.session_state.historico_ids -= ids_do_pool
        disponiveis = pool
        st.session_state.ciclo_reiniciado = True
    else:
        st.session_state.ciclo_reiniciado = False

    escolhida = random.choice(disponiveis).copy()
    opcoes = escolhida["opcoes"].copy()
    random.shuffle(opcoes)
    escolhida["opcoes"] = opcoes

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
st.markdown(
    f'<div class="kicker">{len(CATEGORIAS)} categorias · {TOTAL_PERGUNTAS} perguntas</div>',
    unsafe_allow_html=True,
)
st.markdown('<h1 class="title">Quiz de Mitologias</h1>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Escolha os temas, marque uma alternativa e confirme. '
    'As perguntas não se repetem até o conjunto selecionado se esgotar.</div>',
    unsafe_allow_html=True,
)


# -----------------------------------------------------------------------------
# Configuração das categorias — compacta e fora do fluxo principal
# -----------------------------------------------------------------------------
selecionadas = categorias_ativas()
quantidade_perguntas = sum(len(BANCO[c]) for c in selecionadas)

if st.session_state.modo_todas:
    resumo_categorias = f"Todas as {len(CATEGORIAS)} categorias"
else:
    resumo_categorias = f"{len(selecionadas)} categorias selecionadas"

with st.expander(f"Categorias · {resumo_categorias}", expanded=False):
    st.write("Selecione uma ou várias mitologias. Para usar o banco inteiro, escolha **Selecionar todas**.")

    b1, b2 = st.columns(2)
    with b1:
        st.button(
            "Selecionar todas",
            use_container_width=True,
            on_click=selecionar_todas,
        )
    with b2:
        st.button(
            "Limpar seleção",
            use_container_width=True,
            on_click=limpar_selecao,
        )

    st.multiselect(
        "Categorias específicas",
        options=CATEGORIAS,
        key="categorias_widget",
        placeholder="Busque e selecione uma ou mais categorias",
        on_change=categorias_alteradas,
        help="Ao escolher uma categoria aqui, o modo 'todas' é desativado automaticamente.",
    )

    st.caption(
        f"Ativas agora: {len(selecionadas)} categoria(s) · {quantidade_perguntas} pergunta(s)."
    )


# -----------------------------------------------------------------------------
# Métricas
# -----------------------------------------------------------------------------
precisao = (
    round((st.session_state.acertos / st.session_state.respondidas) * 100)
    if st.session_state.respondidas
    else 0
)

m1, m2, m3 = st.columns(3)
with m1:
    st.metric("Respondidas", st.session_state.respondidas)
with m2:
    st.metric("Acertos", st.session_state.acertos)
with m3:
    st.metric("Aproveitamento", f"{precisao}%")


# -----------------------------------------------------------------------------
# Quiz
# -----------------------------------------------------------------------------
if not selecionadas:
    st.warning("Selecione pelo menos uma categoria no painel acima para começar.")
    st.stop()

if st.session_state.pergunta_atual is None:
    sortear_pergunta()

if st.session_state.ciclo_reiniciado:
    st.toast("O conjunto selecionado foi concluído. Um novo ciclo começou.")
    st.session_state.ciclo_reiniciado = False

pergunta = st.session_state.pergunta_atual

st.markdown(
    f"""
    <section class="question-shell">
        <div class="category-badge">{pergunta['tema']}</div>
        <div class="question-label">Pergunta</div>
        <p class="question-text">{pergunta['pergunta']}</p>
    </section>
    """,
    unsafe_allow_html=True,
)

radio_key = f"resposta_{pergunta['id']}"
resposta = st.radio(
    "Escolha uma alternativa",
    options=pergunta["opcoes"],
    index=None,
    key=radio_key,
    disabled=st.session_state.respondida,
)

if not st.session_state.respondida:
    c1, c2 = st.columns([2.2, 1])
    with c1:
        if st.button(
            "Responder",
            type="primary",
            use_container_width=True,
            disabled=resposta is None,
        ):
            responder(resposta)
            st.rerun()
    with c2:
        st.button(
            "Pular",
            use_container_width=True,
            on_click=sortear_pergunta,
        )
else:
    acertou = st.session_state.resposta_escolhida == pergunta["correta"]
    if acertou:
        st.markdown(
            '<div class="feedback-ok">✓ Correto.</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f'<div class="feedback-no">Resposta correta: <strong>{pergunta["correta"]}</strong></div>',
            unsafe_allow_html=True,
        )

    c1, c2 = st.columns([2.2, 1])
    with c1:
        st.button(
            "Próxima pergunta",
            type="primary",
            use_container_width=True,
            on_click=sortear_pergunta,
        )
    with c2:
        st.button(
            "Zerar sessão",
            use_container_width=True,
            on_click=zerar_sessao,
        )

st.caption("As alternativas são embaralhadas a cada nova pergunta.")
