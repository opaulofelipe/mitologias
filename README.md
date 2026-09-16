# Quiz de Mitologias

App em Python/Streamlit com 50 categorias e 800 perguntas.

## Arquivos

- `app.py` — interface e lógica do quiz
- `mitologias_parte_1.json` a `mitologias_parte_5.json` — banco completo, dividido em 5 partes (800 perguntas)
- `requirements.txt` — dependência do projeto

## Executar localmente

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Funcionalidades

- seleção de uma, várias ou todas as categorias;
- botão para selecionar todas e limpar seleção;
- sorteio aleatório sem repetição até esgotar o conjunto escolhido;
- alternativas embaralhadas a cada pergunta;
- feedback imediato;
- pontuação e aproveitamento da sessão;
- layout responsivo para computador e celular;
- paleta: `#93827F`, `#F3F9D2`, `#BDC4A7`, `#2F2F2F`, `#92B4A7`.
