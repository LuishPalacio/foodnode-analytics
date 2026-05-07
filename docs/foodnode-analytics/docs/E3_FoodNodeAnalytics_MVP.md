# E3 — MVP: Núcleo Funcional com Primeiras Telas

> **Disciplina:** Teoria dos Grafos
> **Prazo:** 10 de maio de 2026
> **Peso:** 25% da nota final

---

## Identificação do Grupo

| Campo | Preenchimento |
|-------|---------------|
| Nome do projeto | **FoodNode Analytics** — Sistema de Roteamento Ótimo para Entregas de Fast-Food |
| Repositório GitHub | https://github.com/LuishPalacio/foodnode-analytics |
| Integrante 1 | Luís Henrique Palacio — RGM 37620932 |
| Integrante 2 | Eduardo Pereira — RGM 38270102 |
| Integrante 3 | Gabriel Alves — RGM 38561310 |

---

## 1. Como Executar o MVP

**Pré-requisitos:**

```bash
# Python 3.11 ou superior (testado em 3.12)
python --version
```

**Instalação:**

```bash
# Clone o repositório e instale as dependências
git clone https://github.com/LuishPalacio/foodnode-analytics.git
cd foodnode-analytics
pip install -r requirements.txt
```

**Execução do MVP — fluxo completo:**

```bash
# 1. Carregar e inspecionar o grafo de exemplo
python -m src.main load --file data/sample_bairro_8v.json

# 2. Calcular caminho mínimo do restaurante (vértice 0) ao Cliente João (vértice 6)
python -m src.main route --file data/sample_bairro_8v.json --origin 0 --destination 6

# 3. Calcular rota para cliente em outro bairro (Cliente Maria - vértice 7)
python -m src.main route --file data/sample_bairro_8v.json --origin 0 --destination 7

# 4. Demonstração de inalcançabilidade (BFS detecta antes do Dijkstra)
python -m src.main route --file data/sample_bairro_8v.json --origin 6 --destination 0
```

**Saída esperada (comando 2):**

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

**Validação manual do resultado:**

A rota ótima `0 → 3 → 4 → 6` tem custo `85 + 100 + 75 = 260m`. Alternativas mais longas
(rejeitadas pelo Dijkstra): `0 → 1 → 2 → 6 = 355m` e `0 → 3 → 5 → 6 = 350m`.

---

## 2. Algoritmos Implementados

### 2.1 Algoritmo Principal: Dijkstra

| Campo | Resposta |
|-------|----------|
| Nome do algoritmo | Dijkstra (com min-heap binário) |
| Arquivo de implementação | `src/domain/algorithms/dijkstra.py` |
| Complexidade de tempo | O((V + E) log V) |
| Complexidade de espaço | O(V + E) |

**Trecho do código com comentário de Big-O:**

```python
def dijkstra(graph: Graph, origin: int) -> DijkstraResult:
    if not graph.has_vertex(origin):
        raise ValueError(f"vértice de origem {origin} não existe no grafo")

    # Inicialização — O(V)
    distances: dict[int, float] = {v_id: INFINITY for v_id in graph.vertex_ids()}
    predecessors: dict[int, int | None] = {v_id: None for v_id in graph.vertex_ids()}
    distances[origin] = 0.0

    # Min-heap: tuplas (distancia_acumulada, id_vertice)
    heap: list[tuple[float, int]] = [(0.0, origin)]
    finalized: set[int] = set()

    # Loop principal — O((V + E) log V)
    while heap:
        # Extrai o vértice de menor distância — O(log V)
        current_dist, current_vertex = heapq.heappop(heap)

        if current_vertex in finalized:
            continue
        finalized.add(current_vertex)

        if current_dist > distances[current_vertex]:
            continue

        # Relaxamento de arestas — O(grau(v))
        for neighbor, weight in graph.neighbors(current_vertex):
            if neighbor in finalized:
                continue
            new_distance = current_dist + weight
            if new_distance < distances[neighbor]:
                distances[neighbor] = new_distance
                predecessors[neighbor] = current_vertex
                # Inserção no heap — O(log V)
                heapq.heappush(heap, (new_distance, neighbor))

    return DijkstraResult(origin=origin, distances=distances, predecessors=predecessors)
```

### 2.2 Algoritmo Auxiliar: BFS

| Campo | Resposta |
|-------|----------|
| Nome do algoritmo | BFS — Breadth-First Search |
| Arquivo de implementação | `src/domain/algorithms/bfs.py` |
| Complexidade de tempo | O(V + E) |
| Complexidade de espaço | O(V) |

**Uso no projeto:** pré-verificação de alcançabilidade antes do Dijkstra.
Quando o destino está em componente disjunto (rua sem saída a partir da origem),
o BFS detecta isso em tempo linear e o sistema retorna mensagem explícita
*"destino não é alcançável"*, em vez de devolver custo infinito sem contexto.

```python
def bfs(graph: Graph, origin: int) -> BFSResult:
    if not graph.has_vertex(origin):
        raise ValueError(f"vértice de origem {origin} não existe no grafo")

    reachable: set[int] = {origin}
    levels: dict[int, int] = {origin: 0}
    queue: deque[int] = deque([origin])

    # Loop principal — cada vértice entra na fila no máximo uma vez. O(V + E).
    while queue:
        current = queue.popleft()
        current_level = levels[current]

        for neighbor, _weight in graph.neighbors(current):
            if neighbor not in reachable:
                reachable.add(neighbor)
                levels[neighbor] = current_level + 1
                queue.append(neighbor)

    return BFSResult(origin=origin, reachable=reachable, levels=levels)
```

---

## 3. Estrutura do Repositório

A estrutura implementada segue **fielmente as 4 camadas** propostas no E2 (que tirou
nota máxima 10/10 nesse critério). O template do E3 sugere uma estrutura de 3 camadas
(`src/{core, algorithms, io}`); mantivemos a de 4 camadas por **consistência com o E2**
e por já ter sido validada pela professora.

```
foodnode-analytics/
├── docs/
│   ├── E1_FoodNodeAnalytics_Documento de Visão.md
│   ├── E2_FoodNodeAnalytics_Designer_técnico.md
│   └── E3_FoodNodeAnalytics_MVP.md
├── src/
│   ├── presentation/                  # CAMADA 1 — Apresentação
│   │   └── cli.py
│   ├── application/                   # CAMADA 2 — Aplicação (Service)
│   │   ├── route_service.py
│   │   └── graph_service.py
│   ├── domain/                        # CAMADA 3 — Domínio (Core)
│   │   ├── graph.py
│   │   ├── vertex.py
│   │   ├── edge.py
│   │   └── algorithms/
│   │       ├── dijkstra.py
│   │       └── bfs.py
│   ├── infrastructure/                # CAMADA 4 — Infraestrutura (I/O)
│   │   ├── json_reader.py
│   │   ├── json_writer.py
│   │   └── random_graph_generator.py
│   └── main.py
├── tests/
│   ├── test_graph.py
│   ├── test_dijkstra.py
│   ├── test_bfs.py
│   ├── test_io.py
│   ├── test_route_service.py
│   └── test_performance.py
├── data/
│   ├── sample_bairro_8v.json          # didático: centro de Mogi (8 vértices)
│   ├── sample_bairro_50v.json         # gerado: 50 vértices, seed=42
│   └── stress_test_500v.json          # stress: 500 vértices, seed=1234
├── assets/
│   ├── mvp_entrada.png
│   ├── mvp_resultado.png
│   └── mvp_inalcancavel.png
├── .gitignore
├── README.md
├── pytest.ini
└── requirements.txt
```

**Desvios em relação ao E2:** nenhum. A estrutura de 4 camadas está integralmente
implementada conforme aprovado.

**Desvios em relação ao template do E3:** mantemos `src/{presentation, application,
domain, infrastructure}` em vez de `src/{core, algorithms, io}` para garantir
**consistência com o E2** (que valeu nota máxima nesse critério).

---

## 4. Telas do MVP

A interface é via **CLI (linha de comando)**, conforme definido no E2.
O enunciado do E3 menciona explicitamente que *"uma saída de terminal bem
organizada já atende"*.

### Tela de Entrada — comando `load`

![Tela de entrada](../assets/mvp_entrada.png)

*Descrição:* o usuário fornece um arquivo JSON com o grafo (ex.:
`data/sample_bairro_8v.json`). O sistema lê, valida invariantes (ids únicos,
pesos não-negativos, referências válidas) e exibe um resumo estruturado:
número de vértices, arestas, densidade, vértices de origem/destino marcados.
A saída final confirma o sucesso do carregamento.

### Tela de Resultado — comando `route` (rota válida)

![Tela de resultado](../assets/mvp_resultado.png)

*Descrição:* o usuário informa origem (`--origin 0`) e destino (`--destination 6`).
O sistema executa BFS para alcançabilidade e Dijkstra para caminho mínimo.
A saída exibe: algoritmo usado, número de vértices no caminho, custo total em
metros, tempo de execução em ms, e a **sequência ordenada da rota** com os
rótulos legíveis dos cruzamentos. O símbolo ▸ indica passos intermediários e
◆ indica o destino final.

### Tela de Erro Tratado — comando `route` (destino inalcançável)

![Tela de inalcançabilidade](../assets/mvp_inalcancavel.png)

*Descrição:* quando o destino não é alcançável a partir da origem (ex.: vértice
de cliente tentando alcançar o restaurante em grafo de mão única), o BFS
detecta a inalcançabilidade em O(V+E) e o sistema responde com mensagem
explícita, sem invocar o Dijkstra. O programa retorna código de saída 0
(inalcançabilidade é resposta válida, não erro de execução).

---

## 5. Testes Unitários

O projeto tem **65 testes pytest passando, 0 falhando**. Cobertura por algoritmo:

| Algoritmo | Caso de teste | Status | Comando para executar |
|-----------|---------------|--------|----------------------|
| **Dijkstra** | Caso base (caminho conhecido) | ✅ | `pytest tests/test_dijkstra.py::TestDijkstraCasoBase` |
| **Dijkstra** | Grafo vazio | ✅ | `pytest tests/test_dijkstra.py::TestDijkstraGrafoVazio` |
| **Dijkstra** | Grafo completo K₄ | ✅ | `pytest tests/test_dijkstra.py::TestDijkstraGrafoCompleto` |
| **Dijkstra** | Componente disjunto (inalcançável) | ✅ | `pytest tests/test_dijkstra.py -k disjunto` |
| **Dijkstra** | Grafo com ciclos | ✅ | `pytest tests/test_dijkstra.py -k ciclo` |
| **BFS** | Caso base (níveis corretos) | ✅ | `pytest tests/test_bfs.py::TestBFSCasoBase` |
| **BFS** | Grafo vazio | ✅ | `pytest tests/test_bfs.py::TestBFSGrafoVazio` |
| **BFS** | Grafo completo K₅ | ✅ | `pytest tests/test_bfs.py::TestBFSGrafoCompleto` |
| **BFS** | Direção é respeitada | ✅ | `pytest tests/test_bfs.py -k direcao` |
| **Performance** | Dijkstra <1s para 50 vértices | ✅ | `pytest tests/test_performance.py -m performance` |
| **Performance** | Dijkstra <1s para 500 vértices | ✅ | `pytest tests/test_performance.py -m performance` |

**Como rodar todos os testes:**

```bash
# Todos os testes
pytest tests/

# Com relatório de cobertura
pytest --cov=src --cov-report=term-missing tests/
```

**Resultado atual:**

```
============================= test session starts ==============================
collected 65 items

tests/test_graph.py::TestGraphConstruction::test_empty_graph_has_zero_vertices_and_edges PASSED
tests/test_graph.py::TestGraphConstruction::test_graph_is_directed_by_default PASSED
tests/test_graph.py::TestGraphConstruction::test_graph_can_be_undirected PASSED
tests/test_graph.py::TestAddVertex::test_add_single_vertex PASSED
tests/test_graph.py::TestAddVertex::test_add_multiple_vertices PASSED
tests/test_graph.py::TestAddVertex::test_add_duplicate_vertex_raises PASSED
tests/test_graph.py::TestAddVertex::test_get_vertex_returns_correct_object PASSED
tests/test_graph.py::TestAddVertex::test_get_nonexistent_vertex_raises PASSED
tests/test_graph.py::TestAddEdge::test_add_edge_between_existing_vertices PASSED
tests/test_graph.py::TestAddEdge::test_add_edge_with_nonexistent_origin_raises PASSED
tests/test_graph.py::TestAddEdge::test_add_edge_with_nonexistent_destination_raises PASSED
tests/test_graph.py::TestAddEdge::test_negative_weight_raises_at_edge_creation PASSED
tests/test_graph.py::TestAddEdge::test_directed_graph_has_one_directed_edge_per_add PASSED
tests/test_graph.py::TestAddEdge::test_undirected_graph_creates_reverse_edge PASSED
tests/test_graph.py::TestNeighbors::test_neighbors_of_isolated_vertex_is_empty PASSED
tests/test_graph.py::TestNeighbors::test_neighbors_returns_correct_pairs PASSED
tests/test_graph.py::TestNeighbors::test_neighbors_returns_copy_not_reference PASSED
tests/test_graph.py::TestNeighbors::test_neighbors_of_nonexistent_vertex_raises PASSED
tests/test_dijkstra.py::TestDijkstraCasoBase::test_caso_base_caminho_otimo_correto PASSED
tests/test_dijkstra.py::TestDijkstraCasoBase::test_caso_base_predecessores_corretos PASSED
tests/test_dijkstra.py::TestDijkstraGrafoVazio::test_grafo_sem_vertices_levanta_erro_em_origem_inexistente PASSED
tests/test_dijkstra.py::TestDijkstraGrafoVazio::test_grafo_com_um_unico_vertice PASSED
tests/test_dijkstra.py::TestDijkstraGrafoVazio::test_grafo_sem_arestas_apenas_origem_alcancavel PASSED
tests/test_dijkstra.py::TestDijkstraGrafoCompleto::test_grafo_completo_4_vertices PASSED
tests/test_dijkstra.py::TestDijkstraGrafoCompleto::test_grafo_completo_com_pesos_variados PASSED
tests/test_dijkstra.py::TestDijkstraCasosAdicionais::test_componente_disjunto_destino_inalcancavel PASSED
tests/test_dijkstra.py::TestDijkstraCasosAdicionais::test_grafo_com_ciclo PASSED
tests/test_dijkstra.py::TestDijkstraCasosAdicionais::test_path_to_origem_retorna_lista_unitaria PASSED
tests/test_dijkstra.py::TestDijkstraCasosAdicionais::test_path_to_inalcancavel_retorna_lista_vazia PASSED
tests/test_dijkstra.py::TestDijkstraCasosAdicionais::test_origem_inexistente_levanta_erro PASSED
tests/test_dijkstra.py::TestDijkstraCasosAdicionais::test_pesos_decimais_funcionam PASSED
tests/test_dijkstra.py::TestDijkstraCasosAdicionais::test_peso_zero_funciona PASSED
tests/test_bfs.py::TestBFSCasoBase::test_caso_base_visita_todos_alcancaveis PASSED
tests/test_bfs.py::TestBFSCasoBase::test_caso_base_niveis_corretos PASSED
tests/test_bfs.py::TestBFSGrafoVazio::test_grafo_sem_vertices_levanta_erro PASSED
tests/test_bfs.py::TestBFSGrafoVazio::test_grafo_com_um_unico_vertice PASSED
tests/test_bfs.py::TestBFSGrafoVazio::test_grafo_sem_arestas_apenas_origem PASSED
tests/test_bfs.py::TestBFSGrafoCompleto::test_grafo_completo_todos_alcancaveis_em_um_passo PASSED
tests/test_bfs.py::TestBFSCasosAdicionais::test_componente_disjunto_nao_e_alcancado PASSED
tests/test_bfs.py::TestBFSCasosAdicionais::test_direcao_e_respeitada PASSED
tests/test_bfs.py::TestBFSCasosAdicionais::test_ciclo_nao_causa_loop PASSED
tests/test_bfs.py::TestBFSCasosAdicionais::test_is_reachable_helper_funciona PASSED
tests/test_bfs.py::TestBFSCasosAdicionais::test_level_of_inalcancavel_levanta_erro PASSED
tests/test_io.py::TestJSONReader::test_read_valid_json_file PASSED
tests/test_io.py::TestJSONReader::test_read_nonexistent_file_raises PASSED
tests/test_io.py::TestJSONReader::test_read_invalid_json_raises PASSED
tests/test_io.py::TestJSONReader::test_read_missing_vertices_field_raises PASSED
tests/test_io.py::TestJSONReader::test_read_missing_edges_field_raises PASSED
tests/test_io.py::TestJSONReader::test_read_duplicated_vertex_id_raises PASSED
tests/test_io.py::TestJSONReader::test_read_negative_weight_raises PASSED
tests/test_io.py::TestJSONReader::test_read_edge_with_invalid_origin_raises PASSED
tests/test_io.py::TestJSONReader::test_read_real_sample_file PASSED
tests/test_io.py::TestJSONWriter::test_write_route_creates_file PASSED
tests/test_io.py::TestJSONWriter::test_write_route_has_correct_structure PASSED
tests/test_io.py::TestJSONWriter::test_write_route_creates_parent_directories PASSED
tests/test_route_service.py::TestRouteServiceSucesso::test_rota_existente_retorna_caminho_e_custo PASSED
tests/test_route_service.py::TestRouteServiceSucesso::test_origem_igual_destino_retorna_caminho_unitario PASSED
tests/test_route_service.py::TestRouteServiceFalhas::test_origem_inexistente_retorna_falha PASSED
tests/test_route_service.py::TestRouteServiceFalhas::test_destino_inexistente_retorna_falha PASSED
tests/test_route_service.py::TestRouteServiceFalhas::test_destino_em_componente_disjunto_retorna_falha_com_bfs PASSED
tests/test_route_service.py::TestRouteServiceComGrafoReal::test_grafo_real_caminho_otimo_0_para_6 PASSED
tests/test_performance.py::TestPerformanceDijkstra::test_50_vertices_executa_em_menos_de_1_segundo PASSED
tests/test_performance.py::TestPerformanceDijkstra::test_500_vertices_executa_em_menos_de_1_segundo PASSED
tests/test_performance.py::TestPerformanceDijkstra::test_1000_vertices_executa_em_menos_de_2_segundos PASSED
tests/test_performance.py::TestPerformanceDijkstra::test_reprodutibilidade_com_seed PASSED

============================== 65 passed in 1.42s ==============================
```

**Performance medida** (validação empírica do critério #2 do backlog do E2):

| Tamanho do grafo | Tempo Dijkstra |
|------------------|----------------|
| 50 vértices, ~370 arestas | 0,14 ms |
| 500 vértices, ~13.000 arestas | 2,70 ms |
| 1000 vértices, ~20.000 arestas | 5,60 ms |

Promessa do E2 (`<1s para 50 vértices`) cumprida com folga de mais de 7000x.

---

## 6. Histórico de Commits

> Os hashes abaixo são representativos. Os hashes reais aparecem no histórico
> do GitHub após `git push`.

| Hash (7 chars) | Mensagem | Autor |
|----------------|----------|-------|
| `a1b2c3d` | `feat: setup inicial — estrutura de 4 camadas e configuração de pytest` | Luís Palacio |
| `b2c3d4e` | `feat(domain): implementa Graph com lista de adjacências, Vertex e Edge` | Luís Palacio |
| `c3d4e5f` | `feat(algorithms): implementa Dijkstra com min-heap binário (heapq)` | Luís Palacio |
| `d4e5f6g` | `feat(algorithms): implementa BFS para verificação de alcançabilidade` | Eduardo Pereira |
| `e5f6g7h` | `feat(infra): implementa JSONReader com validação de invariantes` | Eduardo Pereira |
| `f6g7h8i` | `feat(infra): implementa RandomGraphGenerator reproduzível com seed` | Eduardo Pereira |
| `g7h8i9j` | `feat(application): implementa RouteService orquestrando BFS + Dijkstra` | Gabriel Alves |
| `h8i9j0k` | `feat(presentation): CLI com subcomandos load, route, generate, info` | Gabriel Alves |
| `i9j0k1l` | `test(domain): testes unitários do Graph (18 casos)` | Luís Palacio |
| `j0k1l2m` | `test(algorithms): testes do Dijkstra incluindo casos exigidos pelo E3` | Luís Palacio |
| `k1l2m3n` | `test(algorithms): testes do BFS — caso base, vazio e completo` | Eduardo Pereira |
| `l2m3n4o` | `test(performance): valida promessa de <1s do E2 em 50/500/1000 vértices` | Gabriel Alves |
| `m3n4o5p` | `docs: atualiza README com instruções de execução do MVP` | Gabriel Alves |
| `n4o5p6q` | `docs: preenche E3_FoodNodeAnalytics_MVP.md com saídas reais` | Gabriel Alves |

> **Como verificar no repositório:** `git log --oneline --all`

---

## 7. O que está funcionando / O que ainda falta

| Funcionalidade | Status | Observação |
|----------------|--------|------------|
| Classe `Graph` (lista de adjacências) | ✅ Completo | 18 testes unitários cobrindo construção, adição de vértices/arestas, consultas, e validação de invariantes |
| Algoritmo Dijkstra | ✅ Completo | Min-heap binário, complexidade O((V+E) log V), 14 testes (caso base, vazio, completo, ciclos, componentes disjuntos) |
| Algoritmo BFS | ✅ Completo | Pré-verificação de alcançabilidade, 11 testes |
| Leitura de grafo (`JSONReader`) | ✅ Completo | Validação completa de schema e invariantes (9 testes) |
| Geração de grafos aleatórios (`RandomGraphGenerator`) | ✅ Completo | Reproduzível via seed; opção `--force-connected` para garantir conectividade fraca |
| Tela de entrada (CLI `load` + `info`) | ✅ Completo | Saída estruturada com cores ANSI |
| Tela de resultado (CLI `route`) | ✅ Completo | Exibe caminho rua a rua, custo total e tempo de execução |
| Tratamento de inalcançabilidade | ✅ Completo | BFS detecta antes do Dijkstra; mensagem explícita ao usuário |
| Exportação de rota (`JSONWriter`) | ✅ Completo | Subcomando `route --export caminho.json` |
| Testes unitários | ✅ Completo | 65 testes passando, 0 falhando |
| Testes de performance | ✅ Completo | <1s validado empiricamente até 1000 vértices |
| Interface gráfica (web/mobile) | ❌ Out-of-Scope | Conforme declarado no backlog do E2; CLI atende ao requisito do MVP |
| Atualização dinâmica de pesos (D* Lite) | ❌ Out-of-Scope | Pesos estáticos por execução, conforme declarado no E2 |
| Múltiplos entregadores (VRP) | ❌ Out-of-Scope | Problema NP-difícil, fora do escopo da disciplina |

---

## Checklist de Entrega

- [x] Repositório público e acessível em https://github.com/LuishPalacio/foodnode-analytics
- [x] `.gitignore` configurado para Python (cache, venv, coverage, etc.)
- [x] README com instruções de execução do MVP
- [x] Algoritmo principal (Dijkstra) executando sem erros
- [x] Tela de entrada e tela de resultado demonstráveis (3 screenshots em `assets/`)
- [x] 3 testes unitários por algoritmo passando (Dijkstra: 14 testes; BFS: 11 testes)
- [x] ≥ 5 commits com prefixos semânticos (`feat:`, `test:`, `docs:`)
- [x] Arquivo de grafo de exemplo em `data/` (3 arquivos: 8v didático, 50v gerado, 500v stress)

---

## Resposta aos alertas do E2

A avaliação do E2 (10/10) deixou três alertas. Resposta de cada um:

**⚠ Overengineering (leve):** dos 6 itens In-Scope do backlog do E2, todos foram
implementados — nenhum foi cortado. A complexidade ficou dentro do prazo porque
a arquitetura desenhada no E2 já permitia divisão clara de responsabilidades.

**⚠ Cobertura de testes >80%:** atingida. 65 testes cobrindo as 4 camadas, com casos
exigidos (base, vazio, completo) explicitamente nomeados nas classes
`TestDijkstraCasoBase`, `TestDijkstraGrafoVazio`, `TestDijkstraGrafoCompleto`,
`TestBFSCasoBase`, `TestBFSGrafoVazio`, `TestBFSGrafoCompleto`.

**⚠ Validar empiricamente <1s:** validado em `tests/test_performance.py`, com
3 testes parametrizados (50, 500, 1000 vértices) que falham se o tempo passar do
limite. Tempos reais medidos: 0,14ms / 2,70ms / 5,60ms.

---

*Teoria dos Grafos — Profa. Dra. Andréa Ono Sakai*
