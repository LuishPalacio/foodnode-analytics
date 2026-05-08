# FoodNode Analytics

> Sistema de roteamento ótimo para entregas de fast-food.
> Calcula caminhos mínimos em grafos dirigidos ponderados usando **Dijkstra** + **BFS**.
> Interface gráfica desktop construída com **Tkinter**.

Projeto da disciplina **Teoria dos Grafos** — Profa. Dra. Andréa Ono Sakai.

## Integrantes

| Integrante | RGM |
|------------|-----|
| Luís Henrique Palacio | 37620932 |
| Eduardo Pereira | 38270102 |
| Gabriel Alves | 38561310 |

## Documentação

- [E1 — Documento de Visão](docs/E1_FoodNodeAnalytics_Documento_de_Visao.md)
- [E2 — Design Técnico](docs/E2_FoodNodeAnalytics_Designer_tecnico.md)
- [E3 — MVP (esta entrega)](docs/E3_FoodNodeAnalytics_MVP.md)

---

## Como executar

### Pré-requisitos

- **Python 3.11 ou superior** (testado em 3.12).
- Tkinter (já incluído na biblioteca padrão do Python — sem instalação adicional).

### Instalação

```bash
git clone https://github.com/LuishPalacio/foodnode-analytics.git
cd foodnode-analytics
pip install -r requirements.txt
```

### Iniciar a interface gráfica (modo principal)

```bash
python -m src.main
```

Abre a janela do FoodNode Analytics. No painel de controle à direita:

1. Clique em **"Carregar exemplo (Mogi 8v)"** para carregar o grafo de demonstração
2. Selecione **Origem** (ex: vértice 0 - Restaurante) e **Destino** (ex: vértice 6 - Cliente João) nos comboboxes
3. Clique em **"Calcular Rota Ótima"**
4. A rota aparece destacada em laranja no canvas e o painel de resultado mostra o caminho passo a passo

Você também pode:
- **Abrir arquivo JSON...** — carrega qualquer grafo no formato documentado
- **Gerar grafo aleatório...** — cria um grafo sintético reproduzível para testes

### Modo CLI (alternativa para automação)

```bash
# Carregar e inspecionar um grafo
python -m src.presentation.cli load --file data/sample_bairro_8v.json

# Calcular caminho mínimo
python -m src.presentation.cli route --file data/sample_bairro_8v.json --origin 0 --destination 6

# Gerar grafo aleatório
python -m src.presentation.cli generate --vertices 100 --density 0.15 --seed 42 --output data/gerado.json

# Ajuda completa
python -m src.presentation.cli --help
```

---

## Como rodar os testes

```bash
python -m pytest tests/

# Com cobertura
python -m pytest --cov=src --cov-report=term-missing tests/
```

**Status atual:** 65 testes passando, 0 falhando.

---

## Arquitetura

O projeto segue arquitetura em **4 camadas** com dependências unidirecionais:

```
┌────────────────────────────────────────────────────────┐
│  CAMADA 1 — Apresentação                               │
│  src/presentation/gui.py  (GUI Tkinter — principal)    │
│  src/presentation/cli.py  (CLI — alternativa)          │
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

A camada de **Domínio** é 100% livre de I/O e de UI. Detalhes completos em [docs/E2_FoodNodeAnalytics_Designer_tecnico.md](docs/E2_FoodNodeAnalytics_Designer_tecnico.md).

---

## Algoritmos implementados

| Algoritmo | Tempo | Espaço | Uso |
|-----------|-------|--------|-----|
| **Dijkstra** (com min-heap) | O((V+E) log V) | O(V+E) | Caminho mínimo principal |
| **BFS** | O(V+E) | O(V) | Pré-verificação de alcançabilidade |

O **BFS roda antes do Dijkstra** para detectar quando o destino está em um componente disjunto, permitindo respostas explícitas como *"destino não é alcançável"*.

---

## Performance

| Vértices | Arestas | Tempo médio |
|----------|---------|-------------|
| 50 | ~370 | 0,11 ms |
| 500 | ~13.000 | 2,55 ms |
| 1000 | ~20.000 | 5,32 ms |

Promessa do E2 (`<1s para 50 vértices`) cumprida com folga de mais de 9000x.

---

## Licença

Projeto acadêmico — uso restrito à disciplina de Teoria dos Grafos.
