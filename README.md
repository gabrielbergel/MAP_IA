Necessária a instalação do "pygame" e "numpy".

pip install pygame
pip install numpy



Resumo

Nesse projeto desenvolvi uma simulação de tráfego utilizando a biblioteca Pygame e inteligência artificial com  aprendizado por reforço. O objetivo principal foi criar um mapa onde carros (azuis) pudessem navegar em um mapa, aprendendo a encontrar o caminho mais eficiente entre um ponto inicial e um ponto final, levando em consideração o tráfego nas ruas e a distância.

Objetivo

O objetivo deste projeto foi entender conceitos de inteligência artificial e aprendizado por reforço, os aplicando em um cenário "real". A ideia é que, os carros, pudessem se mover em um mapa que simula ruas e quadras, aprendendo a evitar áreas de tráfego pesado e a otimizar seu caminho até o destino sendo penalizados por isso e por ir para um caminho mais longo.

Resultados 

O resultado final é uma simulação onde os carros aprendem a navegar pelo mapa, evitando áreas de tráfego pesado e tentando chegar ao destino o mais rápido possível. A cada iteração, os carros melhoram sua estratégia de movimento com base nas recompensas recebidas. Cada rodada demora muito, dificultando a vizualização da evolução.

Futuras Melhorias

- Fazer com que os carros saibam como é o mapa, mas calculem o caminho.
- Fazer com que o carro entenda se uma das opções da interseção é o endpoint.
- Implementar duas vias e mãos únicas.
