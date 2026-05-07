# FoodNode Analytics

> Sistema de roteamento ótimo para entregas de fast-food.
> Calcula caminhos mínimos em grafos dirigidos ponderados usando **Dijkstra** + **BFS**.

Projeto da disciplina **Teoria dos Grafos** — Profa. Dra. Andréa Ono Sakai.

## Integrantes

| Integrante | RGM |
|------------|-----|
| Luís Henrique Palacio | 37620932 |
| Eduardo Pereira | 38270102 |
| Gabriel Alves | 38561310 |

## Documentação

- [E1 — Documento de Visão](docs/E1_FoodNodeAnalytics_Documento%20de%20Visão.md)
- [E2 — Design Técnico](docs/E2_FoodNodeAnalytics_Designer_técnico.md)
- [E3 — MVP](docs/E3_FoodNodeAnalytics_MVP.md)

---

## Como executar o MVP

### Pré-requisitos

- **Python 3.11 ou superior** (testado em 3.12).
- `pip` para instalar dependências de teste.

### Instalação

```bash
git clone https://github.com/LuishPalacio/foodnode-analytics.git
cd foodnode-analytics
pip install -r requirements.txt
```

### Execução — exemplos rápidos

**1. Carregar um grafo e ver suas estatísticas:**

```bash
python -m src.main load --file data/sample_bairro_8v.json
```

**2. Calcular o caminho mínimo entre dois vértices (Dijkstra):**

```bash
python -m src.main route --file data/sample_bairro_8v.json --origin 0 --destination 6
```

Saída esperada:

```
════════════════════════════════════════════════════════════
  FoodNode Analytics — Cálculo de Rota
════════════════════════════════════════════════════════════
  Origem............................. 0 (Restaurante FoodNode (origem))
  Destino............................ 6 (Cliente João - Vila Industrial)
────────────────────────────────────────────────────────────
  Algoritmo.......................... dijkstra
  Vértices no caminho................ 4
  Custo total........................ 260.00 m
  Tempo de execução.................. 0.041 ms
────────────────────────────────────────────────────────────
  Sequência da rota:
    ▸ [0] Restaurante FoodNode (origem)
    ▸ [3] Rua XV de Novembro x Rua Dom Pedro
    ▸ [4] Rua XV de Novembro x Av. Cândido
    ◆ [6] Cliente João - Vila Industrial
════════════════════════════════════════════════════════════
✅ Rota encontrada com 4 vértices, custo total 260.00 m.
```

**3. Gerar um grafo aleatório reproduzível:**

```bash
python -m src.main generate --vertices 100 --density 0.15 --seed 42 --force-connected --output data/gerado.json
```

**4. Ver detalhes de um grafo carregado:**

```bash
python -m src.main info --file data/sample_bairro_8v.json
```

**5. Ajuda completa:**

```bash
python -m src.main --help
python -m src.main route --help
```

---

## Como rodar os testes

```bash
# Todos os testes
pytest tests/

# Com relatório de cobertura
pytest --cov=src --cov-report=term-missing tests/

# Pulando os testes de performance (mais lentos)
pytest -m "not performance" tests/
```

**Status atual:** 65 testes passando, 0 falhando.

---

## Arquitetura

O projeto segue uma arquitetura em **4 camadas** com dependências unidirecionais (camadas superiores conhecem inferiores; o inverso nunca acontece).

```
┌────────────────────────────────────────────────────────┐
│  CAMADA 1 — Apresentação (CLI)                         │
│  src/presentation/cli.py                               │
└─────────────────────────┬──────────────────────────────┘
                          ▼
┌────────────────────────────────────────────────────────┐
│  CAMADA 2 — Aplicação (Service)                        │
│  src/application/{route_service, graph_service}.py     │
└─────────────────────────┬──────────────────────────────┘
                          ▼
┌────────────────────────────────────────────────────────┐
│  CAMADA 3 — Domínio (Core)                             │
│  src/domain/{graph, vertex, edge}.py                   │
│  src/domain/algorithms/{dijkstra, bfs}.py              │
└─────────────────────────┬──────────────────────────────┘
                          ▼
┌────────────────────────────────────────────────────────┐
│  CAMADA 4 — Infraestrutura (I/O)                       │
│  src/infrastructure/{json_reader, json_writer,         │
│                       random_graph_generator}.py       │
└────────────────────────────────────────────────────────┘
```

A camada de **Domínio** é 100% livre de I/O — não lê arquivos, não imprime, não faz logging.
Isso garante que os algoritmos sejam testáveis isoladamente e reutilizáveis.

Detalhes completos da arquitetura, com diagrama Mermaid, em [docs/E2_FoodNodeAnalytics_Designer_técnico.md](docs/E2_FoodNodeAnalytics_Designer_técnico.md).

---

## Algoritmos implementados

| Algoritmo | Tempo | Espaço | Uso |
|-----------|-------|--------|-----|
| **Dijkstra** (com min-heap) | O((V+E) log V) | O(V+E) | Caminho mínimo principal |
| **BFS** | O(V+E) | O(V) | Pré-verificação de alcançabilidade |

O **BFS roda antes do Dijkstra** para detectar quando o destino está em um componente disjunto (rua sem saída a partir da origem). Isso permite respostas explícitas como *"destino não é alcançável"* em vez de simplesmente retornar custo infinito.

---

## Estrutura do projeto

```
foodnode-analytics/
├── README.md                          
├── requirements.txt
├── pytest.ini
├── .gitignore
├── docs/                              
│   ├── E1_FoodNodeAnalytics_Documento de Visão.md
│   ├── E2_FoodNodeAnalytics_Designer_técnico.md
│   └── E3_FoodNodeAnalytics_MVP.md
├── src/                               
│   ├── main.py
│   ├── presentation/cli.py
│   ├── application/
│   │   ├── route_service.py
│   │   └── graph_service.py
│   ├── domain/
│   │   ├── graph.py
│   │   ├── vertex.py
│   │   ├── edge.py
│   │   └── algorithms/
│   │       ├── dijkstra.py
│   │       └── bfs.py
│   └── infrastructure/
│       ├── json_reader.py
│       ├── json_writer.py
│       └── random_graph_generator.py
├── tests/                             
│   ├── test_graph.py
│   ├── test_dijkstra.py
│   ├── test_bfs.py
│   ├── test_io.py
│   ├── test_route_service.py
│   └── test_performance.py
├── data/                              
│   ├── sample_bairro_8v.json          
│   ├── sample_bairro_50v.json         
│   └── stress_test_500v.json          
└── assets/                            
    ├── mvp_entrada.png
    ├── mvp_resultado.png
    └── mvp_inalcancavel.png
```

---

## Performance

Testada empiricamente em `tests/test_performance.py`:

| Vértices | Arestas | Tempo médio |
|----------|---------|-------------|
| 50 | ~370 | 0,14 ms |
| 500 | ~13.000 | 2,70 ms |
| 1000 | ~20.000 | 5,60 ms |

Promessa do E2 (`<1s para 50 vértices`) cumprida com folga de mais de **7000x**.

---

## Licença

Projeto acadêmico 
