# Besouro Mecânico e Drone (Cena 3D)

Projeto de Computação Gráfica em Python (Pygame + PyOpenGL + NumPy): cena animada com um besouro mecânico e um drone, incluindo movimentação por tempo, controle de câmera, iluminação/sombras e sons (explosão e passos).

## Requisitos
- Python 3.12 (recomendado)
- Dependências: `pygame`, `PyOpenGL`, `numpy` (ver `requirements.txt`)

## Como executar (Windows / PowerShell)
```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe main.py
```

Execuções seguintes:
```powershell
.\.venv\Scripts\python.exe main.py
```

Alternativa (entrada numerada para apresentação):
```powershell
python etapa01_main.py
```

Modo de compatibilidade de exibição (se necessário):
```powershell
python main.py --compat-display
```

## Controles
- `Espaço`: pausar/retomar animação
- `Z` / `X`: voltar / avançar o tempo
- `Setas`: orientar câmera
- `W` `A` `S` `D`: mover câmera
- `Q` / `E`: descer / subir câmera
- `C`: enquadrar câmera inicial
- `R`: reiniciar sequência
- `S`: salvar captura em `capturas/resultado.png`
- `Esc`: sair

## Ordem do código (apresentação)
1. `etapa01_main.py` — entrada/execução
2. `etapa02_cena_besouro_drone.py` — cena, animação, controles e sons
3. `etapa03_iluminacao_sombras.py` — iluminação e sombras (shadow mapping)

Arquivos de compatibilidade: `main.py`, `lighting.py`.

## Estrutura principal
- `core/`, `geometry/`, `material/`, `shaders/` — base gráfica e renderização
- `images/` — texturas
- `capturas/` — capturas de tela
- `requirements.txt` — dependências

## Observações
- A animação ocorre em fases com tempo definido (aprox. 11s), incluindo explosão/desmontagem do besouro.
- Os sons de explosão e passos são gerados por código (sem arquivos de áudio externos).
