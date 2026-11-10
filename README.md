# Besouro mecânico e drone

Trabalho de Computação Gráfica. A cena tem um besouro mecânico e um drone de quatro hélices. O besouro avança com as antenas oscilando, o drone se aproxima por trás e o acompanha, o besouro vira o corpo para inspecionar o drone e desvia para abrir passagem e a ultrapassagem termina com uma explosão fora do quadro. Um clarão na borda indica a explosão e o besouro é arremessado para a frente.

## 1. Executar no Windows

1. Extraia o ZIP por completo.
2. No Explorador de Arquivos, entre na pasta que contém `main.py` e `requirements.txt`. Digite `powershell` na barra de endereços e pressione Enter.
3. Confira se o Python 3.12 está disponível com `py -3.12 --version`. Ele foi usado na validação. A aplicação também precisa de um driver com suporte a OpenGL 3.2.
4. Execute os comandos abaixo, um por vez. Eles criam um ambiente virtual local, instalam as dependências nele e abrem a cena.

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe main.py
```

O primeiro e o segundo comandos são necessários na primeira instalação. Para rodar de novo, abra o PowerShell na mesma pasta e execute o último comando.

| Dependência | Função |
|---|---|
| Pygame | Cria a janela, lê o teclado e mede o tempo entre quadros |
| PyOpenGL | Permite que o Python envie instruções ao OpenGL |
| NumPy | Representa as matrizes de transformação e calcula vetores e normais |

Se `py -3.12` falhar, confira se o Python 3.12 e o launcher estão instalados. Se aparecer `ModuleNotFoundError`, instale as dependências usando o mesmo `python.exe` do ambiente virtual. Se a janela falhar ao criar o contexto OpenGL, registre a mensagem de erro e teste com o driver gráfico atualizado. A validação foi feita em Linux com OpenGL por software. Façam um teste no computador da apresentação.

### Se a janela apresentar listras verdes

Quando a captura feita pela tecla S está limpa, teste a exibição alternativa. No PyCharm, abra Run > Edit Configurations, selecione main e coloque `--compat-display` em Parameters (parâmetros do script). Se preferir, execute no terminal da pasta do projeto com o ambiente virtual ativado.

```powershell
python main.py --compat-display
```

O modo alternativo renderiza a cena em OpenGL numa janela oculta e copia o quadro final para uma janela SDL por software. Isso preserva os shaders, a iluminação e a sombra, com custo adicional pela cópia de cada quadro. O título termina em [compatibilidade]. Este modo foi verificado em Linux. O teste no notebook com Windows verifica se o contorno funciona para as listras observadas.

## 2. Controles

| Tecla | Ação |
|---|---|
| Espaço | Pausar ou retomar a animação |
| Setas | Alterar a orientação da câmera, inclusive em pausa |
| C | Voltar ao enquadramento baixo inicial |
| R | Reiniciar o tempo da sequência |
| S | Salvar captura em capturas/resultado.png |
| Esc | Sair |

A sequência dura 11 segundos e para na pose final. Use R para rever.

## 3. O que acontece na cena

| Tempo aproximado | Ação |
|---|---|
| 0 a 3 s | O besouro caminha. O drone se aproxima por trás com as quatro hélices girando. |
| 3 a 4 s | O drone mantém uma posição próxima ao besouro e acompanha seu avanço. O besouro direciona o corpo e as antenas para o drone. |
| 4 a 5,8 s | O besouro vira e desvia lateralmente para liberar a rota do drone. |
| 5,8 a 8 s | Com o desvio concluído, o drone acelera, ultrapassa o besouro e sai pela direita no enquadramento inicial. |
| 8 a 9,25 s | O clarão indica a explosão. O besouro recebe o impulso, é lançado para trás, dá uma volta no ar e aterrissa. |
| 9,25 a 11 s | O besouro dá um pequeno rebote até 9,60 s e fica em repouso na pose final. |

A sequência usa o mesmo enquadramento baixo durante a ação. O ajuste manual serve para examinar a cena e demonstrar o requisito de controle pelo teclado.

## 4. Onde está cada parte

| Recurso | Código |
|---|---|
| Perspectiva, teclado e pausa | Battlefield.update em main.py e Camera em core/camera.py |
| Hierarquia, escala e montagem | Battlefield.build_beetle, build_drone e part em main.py, usando Object3D, Mesh, BoxGeometry e OctagonalPrism |
| Interação, caminhada, antenas, voo e hélices | Battlefield.animate em main.py. O tempo da cena avança pelo deltaTime em segundos |
| Imagem do chão | Battlefield.build_environment, RectangleGeometry e Texture. Os UV da geometria são multiplicados por repeatUV no shader |
| Luz direcional e normais | lighting.py, shaders/scene.vert e shaders/scene.frag |
| Shadow mapping | ShadowRenderer.render em lighting.py e shaders/depth.vert, depth.frag e scene.frag |

### Como ler o código em ordem

1. **Comece pelo final de `main.py`.** `Battlefield(...).run()` abre a janela e chama `initialize()` uma vez. A classe `Base` mede o intervalo entre quadros em `deltaTime` e chama `update()` a cada quadro.
2. **Leia `initialize()`.** Ela cria a câmera, a cena e os materiais. Depois monta o ambiente, o besouro e o drone.
3. **Compare `node()` e `part()`.** `node()` cria um ponto de articulação com uma posição local. `part()` cria uma malha visível e dimensiona a caixa em largura, altura e profundidade. No drone, cada rotor é filho do corpo e a hélice é filha do rotor.
4. **Leia `update()` antes de `animate()`.** `update()` lê o teclado, atualiza a câmera, soma `deltaTime` ao relógio quando a cena está em execução e chama a animação e o renderizador. Em pausa, a câmera e a renderização continuam respondendo ao teclado.
5. **Leia `animate()` com a tabela de tempos ao lado.** `progress()` converte um intervalo de tempo em um valor de 0 a 1. `smooth()` suaviza o começo e o fim da mudança. O drone acompanha o besouro porque seu X é calculado a partir do X do besouro com um deslocamento que muda conforme a fase. As pernas alternam o movimento por fase e as hélices giram conforme o tempo acumulado. O arremesso usa um arco que começa e termina no chão.

### Como o besouro foi modelado

O chassi sustenta duas placas facetadas inspiradas nos élitros de um besouro. A cabeça tem duas lentes de inspeção e duas antenas segmentadas. As seis pernas têm pivôs octogonais, hastes metálicas e atuadores aparentes. As caixas e o prisma são geometrias procedurais integradas às malhas do framework. Os atuadores são peças visuais presas às pernas e acompanham as articulações.

O tema 29 é demonstrado pela marcha, pela oscilação das antenas e pelo desvio coordenado. Em `animate()`, `CLEAR_PATH_END` marca tanto o fim do desvio do besouro quanto o início da ultrapassagem do drone. O movimento é coreografado pelo relógio da cena.

### Transformações na prática

- **Translação** posiciona o corpo no mundo ou desloca uma peça em relação ao seu pai.
- **Rotação** gira a hélice em torno do rotor e movimenta as articulações do besouro. O ponto de articulação é o pivô.
- **Escala** transforma a caixa unitária em peças com proporções diferentes, como a carapaça e uma lâmina de hélice.
- **Hierarquia** combina a matriz do pai com a matriz local do filho. Quando o corpo do drone voa, as hélices viajam com ele e continuam girando nos seus eixos locais.

### O que explicar sobre os shaders

O atributo vertexPosition contém a posição local de cada vértice. O passe de profundidade usa apenas esse atributo. O passe da câmera também usa vertexNormal para iluminação e vertexUV para consultar a imagem da superfície.

modelMatrix transforma da posição local para o mundo. viewMatrix leva do mundo à câmera e projectionMatrix aplica a perspectiva. lightMatrix leva do mundo ao espaço da luz. Os demais uniforms controlam a cor base, a direção para a luz, a repetição dos UV, as duas texturas e a distância entre amostras do mapa de sombra.

No primeiro passe, o framebuffer grava a profundidade dos modelos vistos pela luz direcional. No segundo, o shader compara a profundidade de cada fragmento com esse mapa. Uma superfície voltada de lado para o sol recebe menos luz pelo produto escalar com a normal. Uma superfície bloqueada por outro objeto recebe menos luz pela comparação de profundidade. O mapa é recalculado a cada quadro.

A explosão e o arremesso são movimentos programados por tempo. A explosão aparece como um clarão geométrico. O besouro segue um arco com uma cambalhota completa. O clarão e o arremesso começam no mesmo instante (`EXPLOSION`). O primeiro contato com o chão (`LANDING`) inicia um rebote curto até `SETTLE`.

## 5. Conferência do trabalho

| Requisito do enunciado | O que demonstrar |
|---|---|
| Dois objetos reconhecíveis em um ambiente | Aponte a carapaça, as antenas, as pernas e os quatro rotores no campo de batalha. |
| Animação dependente do tempo e interação | Mostre a aproximação, a abertura de passagem e o arremesso. Explique `deltaTime` e as fases em `animate()`. |
| Translação, rotação, escala e hierarquia | Use uma hélice e uma perna como exemplos de partes ligadas ao corpo. |
| Perspectiva, teclado e pausa | Pause com Espaço, gire a câmera com as setas e volte com C. |
| Textura visível com UV | Mostre o chão, identifique `images/terra.png` e explique `vertexUV` e `repeatUV`. |
| Luz direcional, materiais e normais | Mostre como faces com orientações diferentes recebem intensidades diferentes da mesma luz. |
| Sombra animada com shadow mapping | Pause no arremesso para mostrar a sombra separada do besouro no chão. Explique os dois passes. |

## 6. Roteiro sugerido para os 10 minutos

1. **0–2 min.** Apresentem a dupla, os temas e mostrem a sequência inteira. Reiniciem com R.
2. **2–4 min.** Cada integrante mostra a estrutura do seu modelo e explica uma articulação ou um rotor.
3. **4–6 min.** Expliquem juntos o relógio da cena, a interação, a câmera e a pausa.
4. **6–8 min.** Mostrem a textura, a iluminação e a sombra. Apontem os shaders e os dados que eles recebem.
5. **8–10 min.** Respondam às perguntas individuais e expliquem a contribuição de cada integrante.

Para ensaiar, cada integrante deve conseguir responder como o drone acompanha o besouro, por que o movimento depende de segundos e como o shader descobre se um ponto do chão está na sombra. A nota é dividida em 70% para o projeto e 30% para o domínio individual.

## 7. Fontes e declaração de IA

- Base Python/OpenGL de pygame-main.zip, Aula_Texturas/alunos. O projeto reaproveita core/, geometry/ e a classe Material da atividade. A hierarquia segue o conceito praticado na Aula de Grafo de Cena.
- Stemkoski, Lee e Pascale, Michael. Developing Graphics Frameworks with Python and OpenGL. CRC Press, 2022. DOI 10.1201/9781003181378. Referência para o framework e para a técnica de shadow mapping da seção 6.9. A implementação usa uma textura de profundidade com câmera ortográfica para a luz.
- terra.png e branco.png foram criados para esta cena.
- ChatGPT/Codex foi usado para elaborar a primeira implementação de main.py, lighting.py, dos shaders e deste README, com reaproveitamento da base fornecida. Revisar a declaração conforme as alterações feitas pela dupla.

## 8. Identificação para preencher antes da entrega

- João Alberto Madeira Soares Filho — tema sorteado e contribuições a preencher.
- Segundo integrante — nome, tema sorteado e contribuições a preencher.

Os dois integrantes devem revisar os arquivos indicados acima e conseguir explicar como os seus modelos se integram na mesma sequência.
