# Guia geral do código — Cena Besouro Mecânico e Drone

Este documento explica, de forma geral, como o projeto funciona e como as partes do código se conectam. A ideia é ajudar você a entender e apresentar o projeto sem precisar entrar em todos os detalhes técnicos.

## 1. Visão geral do projeto

O projeto mostra uma cena 3D animada de um **campo de batalha**, com dois personagens principais:

- **Besouro mecânico:** anda pelo terreno, inspeciona a área e interage com o ambiente.
- **Drone:** voa, se aproxima, acompanha o besouro e depois avança.

A animação segue um roteiro com tempo definido (cerca de 11 segundos). Em determinado momento ocorre uma **explosão**: o drone some do quadro e o besouro é **desmontado**, com suas peças sendo arremessadas e caindo no chão.

## 2. Estrutura da pasta (o que é cada coisa)

- **`main.py`**: arquivo principal. É ele que monta a cena, cria os objetos, controla a animação, lê o teclado e roda o programa.
- **`core/`**: base do “motor” da cena (câmera, cena, objetos 3D, malhas/meshes, matrizes, transformações, texturas, etc.). É o que permite posicionar, girar e organizar os objetos.
- **`geometry/`**: formas geométricas usadas para construir os modelos (por exemplo, caixas/prismas/retângulos).
- **`material/`** e **`shaders/`**: definem aparência visual e como a cena é desenhada (cores, materiais, iluminação/sombra conforme o renderizador).
- **`lighting.py`**: configuração/renderização de luz e sombra da cena.
- **`images/`**: imagens/texturas usadas no projeto (ex.: textura do chão).
- **`README.md`**: instruções e informações gerais do projeto.
- **`requirements.txt`**: lista de dependências Python necessárias para rodar.

> Em geral, para entender a lógica da cena e da animação, o arquivo mais importante é o `main.py`.

## 3. Como executar

1. Abra a pasta do projeto (`D:\Cena_Besouro_Drone`) no VS Code.
2. Use um ambiente Python com as dependências instaladas (`requirements.txt`: `pygame`, `PyOpenGL`, `numpy`).
3. Execute o arquivo **`main.py`** (não os arquivos das pastas internas).

### Controles principais
- **Espaço:** pausa/retoma a animação
- **R:** reinicia a sequência
- **C:** volta ao enquadramento inicial da câmera
- **Setas:** ajustam a câmera
- **S:** salva captura em `capturas/resultado.png`
- **Esc:** fecha a aplicação

## 4. Como o `main.py` está organizado

O `main.py` concentra a maior parte do comportamento da cena, normalmente em uma classe principal (ex.: `Battlefield`) e em funções auxiliares. De forma geral:

### 4.1 Constantes e tempo da animação
No início do arquivo ficam valores como:
- tempos de cada fase (início do desvio, explosão, pouso, duração total),
- caminhos de imagens,
- funções utilitárias para controlar progresso no tempo (`progress`, `smooth` etc.).

Isso define **quando** cada evento acontece.

### 4.2 Inicialização (`initialize`)
Prepara tudo que a cena precisa:
- cria o renderizador, a cena e a câmera;
- carrega/cria materiais e geometrias básicas;
- define variáveis de estado (tempo atual, pausa, se houve explosão, lista de destroços etc.);
- monta o ambiente, o besouro, o drone e efeitos (ex.: clarão);
- chama a animação inicial.

### 4.3 Montagem dos objetos
Métodos como `build_environment`, `build_beetle`, `build_drone` (nomes podem variar) são responsáveis por:
- **Ambiente:** chão e elementos do cenário.
- **Besouro:** corpo e partes (placas, cabeça, olhos, antenas, pernas) organizadas de forma hierárquica (partes ligadas a outras).
- **Drone:** corpo, braços/suportes e hélices/rotores.

Os objetos são posicionados e dimensionados com transformações (posição, rotação, escala).

### 4.4 Animação (`animate`)
É o “roteiro em código”. A cada atualização:
- calcula o tempo atual (`t`) e em que fase a cena está;
- move o besouro (caminhada, desvio, reação) e anima pernas/antenas;
- move o drone (aproximação, acompanhamento, ultrapassagem) e gira as hélices;
- controla o momento da explosão e efeitos visuais (clarão);
- decide o que fica visível (ex.: drone some após a explosão).

### 4.5 Explosão e desmontagem do besouro
Quando chega o tempo da explosão:
- o código marca que a explosão ocorreu (para não repetir);
- separa partes do besouro e as transforma em “destroços”;
- aplica velocidades e rotações iniciais para lançar as peças para longe;
- a cada quadro, atualiza a física simples dos destroços (gravidade, movimento, colisão com o chão, quique e desaceleração).

Isso cria o efeito de o besouro se **desmontar** durante a explosão.

### 4.6 Atualização e controle (`update`)
Executado continuamente durante a execução:
- lê entradas do teclado (pausar, reiniciar, câmera);
- atualiza o tempo da animação (se não estiver pausada);
- chama `animate()` e manda renderizar a cena.

Também há lógica de **reinício** (`R`) para remontar os objetos e voltar ao início da sequência.

## 5. Conceitos importantes (de forma simples)

- **Cena e câmera:** a cena reúne todos os objetos; a câmera define o ponto de vista de quem “assiste”.
- **Hierarquia de objetos:** uma parte pode ser “filha” de outra (ex.: hélice ligada ao drone, segmentos ligados à perna). Quando o objeto pai se move, os filhos acompanham.
- **Transformações:** mover (translação), girar (rotação) e mudar tamanho (escala) são operações aplicadas aos objetos para posicioná-los e animá-los.
- **Animação por tempo:** em vez de depender da velocidade do computador, os movimentos são calculados com base no tempo decorrido, para manter o ritmo do roteiro.
- **Materiais, luz e sombra:** definem a aparência dos objetos (cores/superfícies) e como são iluminados na cena.
- **Física simples (destroços):** após a explosão, as peças seguem regras básicas (velocidade, gravidade, colisão com o chão) para parecerem arremessadas.

## 6. Fluxo resumido da execução

1. O programa inicia pelo `main.py`.
2. A cena é criada e os objetos são montados (ambiente, besouro, drone).
3. Entra em um laço contínuo: lê teclado → atualiza tempo → anima objetos → desenha a cena.
4. Nos tempos definidos do roteiro, ocorrem as ações (movimentos, ultrapassagem, explosão e desmontagem).
5. Ao final, a sequência chega ao estado final (ou pode ser reiniciada com `R`).

## 7. Dicas para explicar o código a outra pessoa

- Comece pelo **objetivo da cena** (o que acontece na animação) antes de falar de código.
- Mostre o **`main.py`** como centro do projeto e explique que as pastas `core/`, `geometry/`, `material/`, `shaders/` dão suporte.
- Explique o fluxo: **inicializa → monta → atualiza/anima → renderiza**.
- Destaque o controle por **tempo/fases** para justificar quando cada movimento acontece.
- Ao falar da explosão, foque na ideia: **desmontar em partes + aplicar movimento/física simples**.
- Se a pessoa for menos técnica, evite detalhes de matrizes/shaders e foque em “o que cada parte faz”. Se for mais técnica, você pode aprofundar em hierarquia, transformações e renderização.

## 8. Onde alterar se quiser mudar algo

- **Tempo/ritmo das fases:** constantes de tempo no início do `main.py` (ex.: início/fim de eventos, explosão, duração).
- **Posição e movimento:** lógica dentro de `animate()` e posições iniciais na montagem.
- **Tamanho do besouro:** escala aplicada na construção do besouro (`build_beetle`/inicialização).
- **Força e comportamento da desmontagem:** função que dispara a explosão e a que atualiza os destroços (velocidades, giros, gravidade, quique).
- **Aparência/cenário:** materiais, cores e montagem do ambiente/objetos.
- **Controles e câmera:** tratamento de teclado e atualização da câmera em `update()`.