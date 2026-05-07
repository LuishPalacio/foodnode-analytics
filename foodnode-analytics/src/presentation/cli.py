"""
CLI — interface de linha de comando do FoodNode Analytics.

Camada: Apresentação (UI/CLI)
Responsabilidade: parsing de argumentos, formatação de saída.
NÃO contém lógica de negócio nem conhece estruturas de grafo diretamente —
apenas delega para a camada de Aplicação (Services).

Subcomandos:
    load     — carrega um grafo e exibe informações.
    route    — calcula caminho mínimo entre dois vértices.
    generate — gera um grafo aleatório e salva em arquivo.
    info     — exibe estatísticas detalhadas de um grafo.
"""

import argparse
import sys
from pathlib import Path

from src.application.graph_service import GraphService
from src.application.route_service import RouteService
from src.infrastructure.json_writer import JSONWriter


# ----------------------------------------------------------------------
# Formatação de saída — strings reutilizáveis
# ----------------------------------------------------------------------

SEPARATOR = "═" * 60
SUB_SEPARATOR = "─" * 60


def _print_header(title: str) -> None:
    print(SEPARATOR)
    print(f"  {title}")
    print(SEPARATOR)


def _print_kv(label: str, value: object) -> None:
    print(f"  {label:.<35} {value}")


# ----------------------------------------------------------------------
# Subcomandos
# ----------------------------------------------------------------------

def cmd_load(args: argparse.Namespace) -> int:
    """Subcomando 'load' — carrega um grafo e exibe resumo."""
    try:
        graph = GraphService.load_from_file(args.file)
    except FileNotFoundError as e:
        print(f"❌ Erro: {e}", file=sys.stderr)
        return 1
    except (ValueError, KeyError) as e:
        print(f"❌ Erro ao carregar grafo: {e}", file=sys.stderr)
        return 1

    info = GraphService.graph_info(graph)

    _print_header("FoodNode Analytics — Grafo carregado")
    _print_kv("Arquivo", args.file)
    _print_kv("Vértices", info["vertex_count"])
    _print_kv("Arestas", info["edge_count"])
    _print_kv("Dirigido", info["directed"])
    _print_kv("Densidade", f"{info['density']:.2%}")
    _print_kv("Vértices de origem", info["origin_vertices"])
    _print_kv("Vértices de destino", info["destination_vertices"])
    print(SEPARATOR)
    print(
        f"✅ Grafo carregado: {info['vertex_count']} vértices, "
        f"{info['edge_count']} arestas, dirigido={info['directed']}"
    )
    return 0


def cmd_route(args: argparse.Namespace) -> int:
    """Subcomando 'route' — calcula caminho mínimo entre dois vértices."""
    try:
        graph = GraphService.load_from_file(args.file)
    except FileNotFoundError as e:
        print(f"❌ Erro: {e}", file=sys.stderr)
        return 1
    except (ValueError, KeyError) as e:
        print(f"❌ Erro ao carregar grafo: {e}", file=sys.stderr)
        return 1

    service = RouteService(graph)
    response = service.shortest_route(args.origin, args.destination)

    _print_header("FoodNode Analytics — Cálculo de Rota")
    _print_kv("Origem", f"{args.origin} ({_label_of(graph, args.origin)})")
    _print_kv("Destino", f"{args.destination} ({_label_of(graph, args.destination)})")
    print(SUB_SEPARATOR)

    if not response.success:
        print(f"  ⚠️  {response.message}")
        print(SEPARATOR)
        # Inalcançabilidade não é erro — é resposta válida (exit 0).
        return 0

    _print_kv("Algoritmo", response.algorithm)
    _print_kv("Vértices no caminho", len(response.path))
    _print_kv("Custo total", f"{response.total_cost:.2f} m")
    _print_kv("Tempo de execução", f"{response.time_ms:.3f} ms")
    print(SUB_SEPARATOR)
    print("  Sequência da rota:")
    for i, v_id in enumerate(response.path):
        prefix = "  ▸" if i < len(response.path) - 1 else "  ◆"
        print(f"  {prefix} [{v_id}] {_label_of(graph, v_id)}")
    print(SEPARATOR)
    print(f"✅ {response.message}")

    # Exporta a rota se a flag --export foi passada
    if args.export:
        JSONWriter.write_route(
            path=args.export,
            origin=response.origin,
            destination=response.destination,
            path_vertices=response.path,
            total_cost=response.total_cost,
            algorithm=response.algorithm,
            time_ms=response.time_ms,
        )
        print(f"📄 Rota exportada para: {args.export}")

    return 0


def cmd_generate(args: argparse.Namespace) -> int:
    """Subcomando 'generate' — gera grafo aleatório e salva em JSON."""
    try:
        graph = GraphService.generate_random(
            n_vertices=args.vertices,
            density=args.density,
            weight_min=args.weight_min,
            weight_max=args.weight_max,
            seed=args.seed,
            force_connected=args.force_connected,
            output_path=args.output,
        )
    except ValueError as e:
        print(f"❌ Erro: {e}", file=sys.stderr)
        return 1

    info = GraphService.graph_info(graph)

    _print_header("FoodNode Analytics — Grafo aleatório gerado")
    _print_kv("Vértices", info["vertex_count"])
    _print_kv("Arestas", info["edge_count"])
    _print_kv("Densidade real", f"{info['density']:.2%}")
    _print_kv("Densidade alvo", f"{args.density:.2%}")
    _print_kv("Faixa de pesos", f"[{args.weight_min}, {args.weight_max}]")
    _print_kv("Seed", args.seed if args.seed is not None else "aleatória")
    _print_kv("Conectividade forçada", args.force_connected)
    _print_kv("Arquivo de saída", args.output)
    print(SEPARATOR)
    print(f"✅ Grafo salvo em: {args.output}")
    return 0


def cmd_info(args: argparse.Namespace) -> int:
    """Subcomando 'info' — exibe estatísticas detalhadas do grafo."""
    try:
        graph = GraphService.load_from_file(args.file)
    except FileNotFoundError as e:
        print(f"❌ Erro: {e}", file=sys.stderr)
        return 1
    except (ValueError, KeyError) as e:
        print(f"❌ Erro ao carregar grafo: {e}", file=sys.stderr)
        return 1

    info = GraphService.graph_info(graph)

    _print_header("FoodNode Analytics — Informações do Grafo")
    for k, v in info.items():
        _print_kv(k, v)

    print(SUB_SEPARATOR)
    print("  Vértices:")
    for v in graph.vertices():
        print(f"  • [{v.id:3d}] {v.label} ({v.type})")
    print(SEPARATOR)
    return 0


# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------

def _label_of(graph, vertex_id: int) -> str:
    """Retorna o label do vértice ou '?' se não existir."""
    if graph.has_vertex(vertex_id):
        return graph.get_vertex(vertex_id).label
    return "?"


# ----------------------------------------------------------------------
# Parser principal
# ----------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="foodnode",
        description=(
            "FoodNode Analytics — Sistema de roteamento ótimo para "
            "entregas de fast-food. Calcula caminhos mínimos em grafos "
            "dirigidos ponderados (Dijkstra + BFS)."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Exemplos:\n"
            "  foodnode load --file data/sample_bairro_8v.json\n"
            "  foodnode route --file data/sample_bairro_8v.json --origin 0 --destination 6\n"
            "  foodnode generate --vertices 100 --density 0.15 --seed 42 --output data/gerado.json\n"
            "  foodnode info --file data/sample_bairro_8v.json\n"
        ),
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
        help="subcomando a executar",
    )

    # --- load ---
    p_load = subparsers.add_parser(
        "load", help="carrega um grafo e exibe resumo"
    )
    p_load.add_argument(
        "--file", "-f", required=True, help="caminho do arquivo JSON do grafo"
    )
    p_load.set_defaults(func=cmd_load)

    # --- route ---
    p_route = subparsers.add_parser(
        "route", help="calcula caminho mínimo entre dois vértices"
    )
    p_route.add_argument(
        "--file", "-f", required=True, help="arquivo JSON do grafo"
    )
    p_route.add_argument(
        "--origin", "-o", type=int, required=True, help="id do vértice de origem"
    )
    p_route.add_argument(
        "--destination", "-d", type=int, required=True, help="id do vértice de destino"
    )
    p_route.add_argument(
        "--export", "-e", help="arquivo JSON para exportar a rota calculada"
    )
    p_route.set_defaults(func=cmd_route)

    # --- generate ---
    p_gen = subparsers.add_parser(
        "generate", help="gera grafo aleatório parametrizável"
    )
    p_gen.add_argument(
        "--vertices", "-v", type=int, default=50, help="número de vértices (default: 50)"
    )
    p_gen.add_argument(
        "--density", "-D", type=float, default=0.15,
        help="densidade [0.0-1.0] (default: 0.15)"
    )
    p_gen.add_argument(
        "--weight-min", type=float, default=30.0, help="peso mínimo (default: 30)"
    )
    p_gen.add_argument(
        "--weight-max", type=float, default=2000.0, help="peso máximo (default: 2000)"
    )
    p_gen.add_argument(
        "--seed", "-s", type=int, default=None, help="semente para reprodutibilidade"
    )
    p_gen.add_argument(
        "--force-connected", action="store_true",
        help="garante conectividade fraca via árvore geradora"
    )
    p_gen.add_argument(
        "--output", "-o", required=True, help="arquivo JSON de saída"
    )
    p_gen.set_defaults(func=cmd_generate)

    # --- info ---
    p_info = subparsers.add_parser(
        "info", help="exibe estatísticas detalhadas de um grafo"
    )
    p_info.add_argument(
        "--file", "-f", required=True, help="arquivo JSON do grafo"
    )
    p_info.set_defaults(func=cmd_info)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
