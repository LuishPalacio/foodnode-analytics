# E1 — Proposta e Definição do Projeto

> **Disciplina:** Teoria dos Grafos
> **Prazo:** 19 de março de 2026
> **Peso:** 10% da nota final

---

## Identificação do Grupo

| Campo | Preenchimento |
|-------|---------------|
| Nome do projeto | FoodNode Analytics |
| Integrante 1 | Luís Henrique Palacio — RGM: 37620932 |
| Integrante 2 | Eduardo Pereira — RGM: 38270102 |
| Integrante 3 | Gabriel Alves — RGM: 38561310 |
| Domínio de aplicação | Logística de entregas — roteamento de fast-food |

---

## 1. Contexto e Motivação

O setor de alimentação rápida (fast-food) enfrenta um desafio logístico crítico e diário: garantir que os pedidos cheguem aos clientes no menor tempo possível, preservando a qualidade e a temperatura do produto. Em cenários urbanos, a malha viária apresenta diversas variáveis complexas, como ruas de mão única, bloqueios e distâncias irregulares. Rotas ineficientes geram gargalos operacionais no despacho de mercadorias, aumento de custos com combustível e insatisfação do consumidor.

O problema do mundo real a ser resolvido é a ineficiência no sequenciamento e roteamento de entregas saindo de um ponto central (o restaurante) para múltiplos endereços geográficos distintos, um cenário onde o planejamento manual falha diante do volume de variáveis.

---

## 2. Objetivo Geral

Desenvolver um sistema computacional de roteamento capaz de calcular e sugerir a trajetória mais rápida e eficiente para entregadores, minimizando o tempo total de deslocamento e otimizando a fila de despachos de um sistema de lanchonete.

---

## 3. Objetivos Específicos

- [x] Mapear e converter dados geográficos de uma região urbana local (centro de Mogi das Cruzes) em uma estrutura de dados baseada em um grafo ponderado e direcionado.
- [x] Representar intersecções de ruas como vértices (nós) e os trechos de vias navegáveis como arestas.
- [x] Atribuir os pesos das arestas utilizando uma métrica de custo que considere a distância física em metros entre os cruzamentos.
- [x] Implementar o algoritmo de Dijkstra para processar o grafo e identificar de forma autônoma o caminho de custo mínimo entre a origem (restaurante) e o destino (cliente).
- [x] Estruturar a saída de dados gerada pelo algoritmo de forma que possa ser consumida e exibida por uma interface de gestão.

---

## 4. Público-Alvo / Caso de Uso Principal

A solução destina-se a estabelecimentos do setor alimentício, especificamente para uso de gerentes de operação e entregadores (motoboys).

O cenário de uso principal ocorre na finalização do preparo: ao agrupar pedidos prontos na tela — rodando perfeitamente em conjunto com a interface visual do sistema de gestão de pedidos de fast-food —, o back-end processa os endereços no grafo do bairro, define a rota ótima e fornece o trajeto sequencial rua a rua para a equipe de entrega seguir, reduzindo o tempo de ociosidade na loja.

---

## 5. Justificativa Técnica — Por que Grafos?

A modelagem utilizando a Teoria dos Grafos constitui a abordagem mais robusta e cientificamente embasada para este problema pois a topologia de uma cidade é, de forma intrínseca, um grafo. Tentar resolver rotas viárias utilizando estruturas de dados convencionais resultaria em algoritmos ineficientes e de alta complexidade temporal.

Ao abstrair o mapa para um sistema de vértices e arestas, o sistema viabiliza a aplicação direta de algoritmos clássicos de otimização de caminhos (*Shortest Path*). Isso garante matematicamente a descoberta da rota de menor peso, permitindo que a solução seja escalável e computacionalmente leve, mesmo para mapas contendo centenas de cruzamentos.

---

## 6. Tipo de Grafo

| Característica | Escolha | Justificativa breve |
|----------------|---------|---------------------|
| Dirigido ou não-dirigido | **Dirigido** | Fundamental para respeitar o sentido de trânsito das vias urbanas (ruas de mão única, conversões proibidas). |
| Ponderado ou não-ponderado | **Ponderado** | Permite atribuir um custo computacional a cada aresta, representando a distância física do trecho em metros. |
| Conectado / bipartido / geral | **Geral** | Malhas viárias urbanas reais podem conter ruas sem saída ou componentes fracamente conectados. O sistema tratará explicitamente vértices não alcançáveis via BFS prévio. |
| Representação interna pretendida | **Lista de Adjacência** | Malhas viárias são tipicamente grafos esparsos (E ≈ 2V a 4V), garantindo maior otimização de processamento e memória em comparação à matriz de adjacência. |

---

## 7. Diagrama Conceitual

![Diagrama da Malha Viária](E1_FoodNodeAnalytics_Grafo.Jpeg)

**Legenda:** Figura 1 — Modelagem conceitual da malha viária do centro de Mogi das Cruzes. O vértice destacado representa a lanchonete FoodNode (ponto de origem), conectado aos cruzamentos de ruas (demais vértices) por meio de arestas dirigidas e ponderadas, representando os trechos de vias navegáveis. O diagrama ilustra a abstração do mapa geográfico real para a estrutura de grafo que será processada pelo algoritmo de Dijkstra.

---

## Checklist de Entrega

Antes de submeter, confirme:

- [x] Texto entre 300 e 600 palavras (seções 1 a 5)
- [x] Todos os campos da tabela de identificação preenchidos
- [x] Tipo de grafo especificado com justificativa
- [x] Diagrama presente e referenciado no texto
- [x] Arquivo nomeado como `E1_FoodNodeAnalytics_Documento de Visão.md`

---

*Teoria dos Grafos — Profa. Dra. Andréa Ono Sakai*
