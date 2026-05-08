"""
GUI — Interface gráfica desktop do FoodNode Analytics (Tkinter).

Camada: Apresentação
Responsabilidade: parsing de inputs do usuário (cliques, formulários),
visualização do grafo no Canvas e exibição da rota calculada.

Tkinter vem na biblioteca padrão do Python — sem dependências externas.

Layout:
    ┌────────────────────────────────────────────────────────┐
    │  Barra de Título: FoodNode Analytics                   │
    ├────────────────────────────┬───────────────────────────┤
    │                            │  PAINEL DE CONTROLE       │
    │                            │                           │
    │      CANVAS DO GRAFO       │  • Carregar arquivo       │
    │   (vértices + arestas      │  • Gerar grafo aleatório  │
    │    + rota destacada)       │  • Origem (combobox)      │
    │                            │  • Destino (combobox)     │
    │                            │  • [Calcular Rota]        │
    │                            │                           │
    │                            │  RESULTADO:               │
    │                            │  - Caminho                │
    │                            │  - Custo total            │
    │                            │  - Tempo de execução      │
    ├────────────────────────────┴───────────────────────────┤
    │  Barra de Status                                       │
    └────────────────────────────────────────────────────────┘
"""

import math
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from pathlib import Path

from src.application.graph_service import GraphService
from src.application.route_service import RouteService, RouteResponse


# ---------- Constantes visuais ----------

# Paleta de cores — tons sóbrios, alto contraste
BG_COLOR = "#f5f5f5"
PANEL_BG = "#ffffff"
CANVAS_BG = "#fafafa"
TITLE_BG = "#2c3e50"
TITLE_FG = "#ffffff"

# Cores dos vértices por tipo
VERTEX_COLOR_ORIGIN = "#27ae60"        # verde — restaurante
VERTEX_COLOR_DESTINATION = "#e74c3c"   # vermelho — cliente
VERTEX_COLOR_INTERSECTION = "#3498db"  # azul — cruzamento

# Cores das arestas
EDGE_COLOR_NORMAL = "#bdc3c7"          # cinza claro
EDGE_COLOR_PATH = "#f39c12"            # laranja — destaque da rota
EDGE_TEXT_COLOR = "#7f8c8d"

# Tamanhos
VERTEX_RADIUS = 18
ARROW_SIZE = 10


class FoodNodeGUI:
    """Janela principal do FoodNode Analytics."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("FoodNode Analytics — Sistema de Roteamento de Entregas")
        self.root.geometry("1200x720")
        self.root.configure(bg=BG_COLOR)
        self.root.minsize(900, 600)

        # Estado da aplicação
        self.graph = None  # Graph | None
        self.route_service = None  # RouteService | None
        self.last_response: RouteResponse | None = None
        self.vertex_positions: dict[int, tuple[float, float]] = {}
        self.highlighted_path: list[int] = []

        self._build_ui()
        self._set_status("Pronto. Carregue um grafo para começar.")

    # ------------------------------------------------------------------
    # Construção da UI
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        # ===== CABEÇALHO =====
        header = tk.Frame(self.root, bg=TITLE_BG, height=60)
        header.pack(side=tk.TOP, fill=tk.X)
        header.pack_propagate(False)
        tk.Label(
            header,
            text="🍔 FoodNode Analytics",
            font=("Segoe UI", 18, "bold"),
            bg=TITLE_BG, fg=TITLE_FG,
        ).pack(side=tk.LEFT, padx=20, pady=12)
        tk.Label(
            header,
            text="Sistema de Roteamento Ótimo para Entregas de Fast-Food",
            font=("Segoe UI", 10),
            bg=TITLE_BG, fg="#bdc3c7",
        ).pack(side=tk.LEFT, padx=0, pady=18)

        # ===== ÁREA PRINCIPAL: Canvas + Painel de Controle =====
        main_area = tk.Frame(self.root, bg=BG_COLOR)
        main_area.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Canvas (esquerda)
        canvas_frame = tk.Frame(main_area, bg=PANEL_BG, relief=tk.SOLID, borderwidth=1)
        canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        canvas_title = tk.Label(
            canvas_frame, text="Visualização do Grafo",
            font=("Segoe UI", 11, "bold"),
            bg=PANEL_BG, anchor="w", padx=10, pady=8,
        )
        canvas_title.pack(side=tk.TOP, fill=tk.X)

        self.canvas = tk.Canvas(
            canvas_frame, bg=CANVAS_BG, highlightthickness=0,
        )
        self.canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))
        self.canvas.bind("<Configure>", self._on_canvas_resize)

        # Legenda
        legend = tk.Frame(canvas_frame, bg=PANEL_BG)
        legend.pack(side=tk.TOP, fill=tk.X, padx=10, pady=(0, 8))
        self._add_legend_item(legend, VERTEX_COLOR_ORIGIN, "Origem (Restaurante)")
        self._add_legend_item(legend, VERTEX_COLOR_DESTINATION, "Destino (Cliente)")
        self._add_legend_item(legend, VERTEX_COLOR_INTERSECTION, "Cruzamento")
        self._add_legend_item(legend, EDGE_COLOR_PATH, "Rota calculada", line=True)

        # Painel de controle (direita)
        control_frame = tk.Frame(main_area, bg=PANEL_BG, width=340,
                                 relief=tk.SOLID, borderwidth=1)
        control_frame.pack(side=tk.RIGHT, fill=tk.Y)
        control_frame.pack_propagate(False)

        self._build_control_panel(control_frame)

        # ===== BARRA DE STATUS =====
        self.status_bar = tk.Label(
            self.root, text="", font=("Segoe UI", 9),
            bg="#34495e", fg="#ecf0f1", anchor="w", padx=10, pady=4,
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def _add_legend_item(self, parent, color: str, text: str, line: bool = False) -> None:
        item = tk.Frame(parent, bg=PANEL_BG)
        item.pack(side=tk.LEFT, padx=8)
        if line:
            indicator = tk.Canvas(item, width=20, height=12, bg=PANEL_BG, highlightthickness=0)
            indicator.create_line(0, 6, 20, 6, fill=color, width=3)
        else:
            indicator = tk.Canvas(item, width=12, height=12, bg=PANEL_BG, highlightthickness=0)
            indicator.create_oval(0, 0, 12, 12, fill=color, outline="")
        indicator.pack(side=tk.LEFT, pady=2)
        tk.Label(item, text=text, font=("Segoe UI", 8), bg=PANEL_BG, fg="#555").pack(side=tk.LEFT, padx=4)

    def _build_control_panel(self, parent: tk.Frame) -> None:
        # ----- Seção 1: Carregar Grafo -----
        self._section_title(parent, "1. Carregar Grafo")

        btn_frame = tk.Frame(parent, bg=PANEL_BG)
        btn_frame.pack(fill=tk.X, padx=15, pady=4)

        tk.Button(
            btn_frame, text="📁 Abrir arquivo JSON...",
            command=self._on_open_file,
            font=("Segoe UI", 10), bg="#ecf0f1", relief=tk.FLAT,
            padx=10, pady=6, cursor="hand2",
        ).pack(fill=tk.X, pady=2)

        tk.Button(
            btn_frame, text="🏙️  Carregar exemplo (Mogi 8v)",
            command=self._on_load_sample,
            font=("Segoe UI", 10), bg="#ecf0f1", relief=tk.FLAT,
            padx=10, pady=6, cursor="hand2",
        ).pack(fill=tk.X, pady=2)

        tk.Button(
            btn_frame, text="🎲 Gerar grafo aleatório...",
            command=self._on_generate_random,
            font=("Segoe UI", 10), bg="#ecf0f1", relief=tk.FLAT,
            padx=10, pady=6, cursor="hand2",
        ).pack(fill=tk.X, pady=2)

        # ----- Seção 2: Informações do Grafo -----
        self._section_title(parent, "2. Informações")

        info_frame = tk.Frame(parent, bg=PANEL_BG)
        info_frame.pack(fill=tk.X, padx=15, pady=4)
        self.info_label = tk.Label(
            info_frame,
            text="(nenhum grafo carregado)",
            font=("Consolas", 9), bg=PANEL_BG, fg="#555",
            anchor="w", justify=tk.LEFT,
        )
        self.info_label.pack(fill=tk.X, pady=2)

        # ----- Seção 3: Calcular Rota -----
        self._section_title(parent, "3. Calcular Rota")

        route_frame = tk.Frame(parent, bg=PANEL_BG)
        route_frame.pack(fill=tk.X, padx=15, pady=4)

        tk.Label(route_frame, text="Origem:", font=("Segoe UI", 9), bg=PANEL_BG).pack(anchor="w")
        self.combo_origin = ttk.Combobox(route_frame, state="readonly", font=("Segoe UI", 9))
        self.combo_origin.pack(fill=tk.X, pady=(2, 6))

        tk.Label(route_frame, text="Destino:", font=("Segoe UI", 9), bg=PANEL_BG).pack(anchor="w")
        self.combo_destination = ttk.Combobox(route_frame, state="readonly", font=("Segoe UI", 9))
        self.combo_destination.pack(fill=tk.X, pady=(2, 6))

        self.btn_calculate = tk.Button(
            route_frame, text="🧭  Calcular Rota Ótima",
            command=self._on_calculate_route,
            font=("Segoe UI", 10, "bold"), bg="#3498db", fg="white",
            relief=tk.FLAT, padx=10, pady=8, cursor="hand2",
            state=tk.DISABLED,
        )
        self.btn_calculate.pack(fill=tk.X, pady=6)

        # ----- Seção 4: Resultado -----
        self._section_title(parent, "4. Resultado")

        self.result_frame = tk.Frame(parent, bg=PANEL_BG)
        self.result_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=4)

        self.result_text = tk.Text(
            self.result_frame, font=("Consolas", 9), bg="#f8f9fa",
            relief=tk.FLAT, height=12, wrap=tk.WORD,
            padx=8, pady=6,
        )
        self.result_text.pack(fill=tk.BOTH, expand=True)
        self.result_text.insert("1.0", "Calcule uma rota para ver o resultado aqui.")
        self.result_text.config(state=tk.DISABLED)

    def _section_title(self, parent, text: str) -> None:
        tk.Label(
            parent, text=text, font=("Segoe UI", 10, "bold"),
            bg=PANEL_BG, fg="#2c3e50", anchor="w",
        ).pack(fill=tk.X, padx=15, pady=(12, 4))
        tk.Frame(parent, bg="#bdc3c7", height=1).pack(fill=tk.X, padx=15)

    # ------------------------------------------------------------------
    # Callbacks
    # ------------------------------------------------------------------

    def _on_open_file(self) -> None:
        path = filedialog.askopenfilename(
            title="Abrir arquivo de grafo",
            filetypes=[("JSON", "*.json"), ("Todos os arquivos", "*.*")],
            initialdir=str(Path("data").absolute() if Path("data").exists() else Path.cwd()),
        )
        if path:
            self._load_graph_from_path(path)

    def _on_load_sample(self) -> None:
        sample_path = Path("data/sample_bairro_8v.json")
        if not sample_path.exists():
            messagebox.showerror(
                "Exemplo não encontrado",
                f"O arquivo {sample_path} não foi encontrado. "
                f"Certifique-se de executar a aplicação a partir da raiz do projeto.",
            )
            return
        self._load_graph_from_path(str(sample_path))

    def _on_generate_random(self) -> None:
        n = simpledialog.askinteger(
            "Gerar grafo aleatório",
            "Número de vértices (entre 5 e 200):",
            minvalue=5, maxvalue=200, initialvalue=15,
            parent=self.root,
        )
        if n is None:
            return
        try:
            self._set_status(f"Gerando grafo aleatório com {n} vértices...")
            self.root.update()
            graph = GraphService.generate_random(
                n_vertices=n, density=0.20, seed=42, force_connected=True,
            )
            self._set_graph(graph, source=f"aleatório (n={n}, seed=42)")
        except Exception as e:
            messagebox.showerror("Erro ao gerar grafo", str(e))
            self._set_status("Erro ao gerar grafo.")

    def _on_calculate_route(self) -> None:
        if self.route_service is None:
            return

        origin_str = self.combo_origin.get()
        destination_str = self.combo_destination.get()
        if not origin_str or not destination_str:
            messagebox.showwarning(
                "Selecione origem e destino",
                "Você precisa escolher um vértice de origem e um de destino.",
            )
            return

        origin_id = self._extract_id(origin_str)
        destination_id = self._extract_id(destination_str)

        self._set_status(f"Calculando rota de {origin_id} para {destination_id}...")
        response = self.route_service.shortest_route(origin_id, destination_id)
        self.last_response = response

        if response.success:
            self.highlighted_path = response.path
            self._show_result_success(response)
            self._set_status(
                f"✓ Rota calculada: {len(response.path)} vértices, "
                f"{response.total_cost:.2f} m em {response.time_ms:.2f} ms"
            )
        else:
            self.highlighted_path = []
            self._show_result_failure(response)
            self._set_status(f"⚠ {response.message}")

        self._redraw_canvas()

    def _on_canvas_resize(self, event) -> None:
        # Recalcula posições e redesenha quando a janela é redimensionada
        if self.graph is not None:
            self._compute_layout()
            self._redraw_canvas()

    # ------------------------------------------------------------------
    # Lógica de carga e exibição
    # ------------------------------------------------------------------

    def _load_graph_from_path(self, path: str) -> None:
        try:
            self._set_status(f"Carregando {path}...")
            self.root.update()
            graph = GraphService.load_from_file(path)
            self._set_graph(graph, source=path)
        except Exception as e:
            messagebox.showerror("Erro ao carregar grafo", str(e))
            self._set_status("Erro ao carregar.")

    def _set_graph(self, graph, source: str) -> None:
        self.graph = graph
        self.route_service = RouteService(graph)
        self.highlighted_path = []
        self.last_response = None

        # Atualiza informações
        info = GraphService.graph_info(graph)
        self.info_label.config(
            text=(
                f"Fonte: {Path(source).name if Path(source).exists() else source}\n"
                f"Vértices:    {info['vertex_count']}\n"
                f"Arestas:     {info['edge_count']}\n"
                f"Densidade:   {info['density']:.2%}\n"
                f"Dirigido:    {'Sim' if info['directed'] else 'Não'}\n"
                f"Origens:     {info['origin_vertices']}\n"
                f"Destinos:    {info['destination_vertices']}"
            )
        )

        # Atualiza comboboxes
        labels = [
            f"[{v.id}] {v.label[:40]}" + ("…" if len(v.label) > 40 else "")
            for v in sorted(graph.vertices(), key=lambda x: x.id)
        ]
        self.combo_origin["values"] = labels
        self.combo_destination["values"] = labels

        # Pré-seleciona: origem = primeiro "origin" ou vértice 0; destino = último vértice
        origin_default = next(
            (v.id for v in graph.vertices() if v.type == "origin"),
            next(iter(graph.vertex_ids()), None),
        )
        destination_default = next(
            (v.id for v in graph.vertices() if v.type == "destination"),
            list(graph.vertex_ids())[-1] if graph.vertex_count > 0 else None,
        )
        if origin_default is not None:
            for label in labels:
                if label.startswith(f"[{origin_default}]"):
                    self.combo_origin.set(label)
                    break
        if destination_default is not None:
            for label in labels:
                if label.startswith(f"[{destination_default}]"):
                    self.combo_destination.set(label)
                    break

        self.btn_calculate.config(state=tk.NORMAL)

        # Layout e redesenho
        self._compute_layout()
        self._redraw_canvas()
        self._clear_result_text()
        self._set_status(
            f"Grafo carregado: {info['vertex_count']} vértices, "
            f"{info['edge_count']} arestas. Selecione origem e destino."
        )

    def _compute_layout(self) -> None:
        """Calcula as posições (x, y) dos vértices no canvas (layout circular)."""
        if self.graph is None:
            return
        self.canvas.update_idletasks()
        w = max(self.canvas.winfo_width(), 400)
        h = max(self.canvas.winfo_height(), 300)
        cx, cy = w / 2, h / 2
        radius = min(w, h) / 2 - 50

        vertices = sorted(self.graph.vertices(), key=lambda v: v.id)
        n = len(vertices)
        if n == 0:
            return

        # Layout circular — bom para grafos pequenos/médios
        # Coloca a origem (se houver) no topo
        origin_idx = next(
            (i for i, v in enumerate(vertices) if v.type == "origin"), 0
        )

        for i, vertex in enumerate(vertices):
            # Ajusta o ângulo para que o origin fique no topo (-π/2)
            angle = 2 * math.pi * ((i - origin_idx) % n) / n - math.pi / 2
            x = cx + radius * math.cos(angle)
            y = cy + radius * math.sin(angle)
            self.vertex_positions[vertex.id] = (x, y)

    def _redraw_canvas(self) -> None:
        """Limpa e redesenha o grafo inteiro."""
        self.canvas.delete("all")
        if self.graph is None:
            self.canvas.create_text(
                self.canvas.winfo_width() / 2,
                self.canvas.winfo_height() / 2,
                text="Carregue um grafo para visualizar",
                font=("Segoe UI", 12), fill="#95a5a6",
            )
            return

        # Constrói o conjunto de arestas do caminho destacado
        path_edges: set[tuple[int, int]] = set()
        if self.highlighted_path and len(self.highlighted_path) > 1:
            for i in range(len(self.highlighted_path) - 1):
                path_edges.add(
                    (self.highlighted_path[i], self.highlighted_path[i + 1])
                )

        # 1. Desenha as arestas (primeiro normais, depois destacadas por cima)
        for u in self.graph.vertex_ids():
            for v, weight in self.graph.neighbors(u):
                is_path = (u, v) in path_edges
                self._draw_edge(u, v, weight, is_path)

        # 2. Desenha os vértices (por cima das arestas)
        for vertex in self.graph.vertices():
            self._draw_vertex(vertex)

    def _draw_edge(self, origin_id: int, destination_id: int,
                   weight: float, is_path: bool) -> None:
        if origin_id not in self.vertex_positions:
            return
        if destination_id not in self.vertex_positions:
            return

        x1, y1 = self.vertex_positions[origin_id]
        x2, y2 = self.vertex_positions[destination_id]

        # Calcula o ponto onde a seta deve terminar (na borda do círculo do destino)
        dx, dy = x2 - x1, y2 - y1
        dist = math.sqrt(dx * dx + dy * dy) or 1.0
        ux, uy = dx / dist, dy / dist

        # Encurta a linha para não sobrepor os círculos
        x1_adj = x1 + ux * VERTEX_RADIUS
        y1_adj = y1 + uy * VERTEX_RADIUS
        x2_adj = x2 - ux * VERTEX_RADIUS
        y2_adj = y2 - uy * VERTEX_RADIUS

        color = EDGE_COLOR_PATH if is_path else EDGE_COLOR_NORMAL
        width = 3 if is_path else 1

        self.canvas.create_line(
            x1_adj, y1_adj, x2_adj, y2_adj,
            fill=color, width=width,
            arrow=tk.LAST, arrowshape=(ARROW_SIZE, ARROW_SIZE + 2, ARROW_SIZE / 2),
        )

        # Label do peso (no meio da aresta, com pequeno deslocamento perpendicular)
        mx, my = (x1_adj + x2_adj) / 2, (y1_adj + y2_adj) / 2
        # Perpendicular para não sobrepor a linha
        px, py = -uy * 8, ux * 8
        text_color = "#d35400" if is_path else EDGE_TEXT_COLOR
        self.canvas.create_text(
            mx + px, my + py,
            text=f"{weight:.0f}",
            font=("Segoe UI", 8, "bold" if is_path else "normal"),
            fill=text_color,
        )

    def _draw_vertex(self, vertex) -> None:
        if vertex.id not in self.vertex_positions:
            return
        x, y = self.vertex_positions[vertex.id]

        # Cor por tipo
        if vertex.type == "origin":
            fill = VERTEX_COLOR_ORIGIN
        elif vertex.type == "destination":
            fill = VERTEX_COLOR_DESTINATION
        else:
            fill = VERTEX_COLOR_INTERSECTION

        # Destaque se está no caminho
        is_in_path = vertex.id in self.highlighted_path
        outline = "#d35400" if is_in_path else "#2c3e50"
        outline_width = 3 if is_in_path else 1

        # Círculo
        self.canvas.create_oval(
            x - VERTEX_RADIUS, y - VERTEX_RADIUS,
            x + VERTEX_RADIUS, y + VERTEX_RADIUS,
            fill=fill, outline=outline, width=outline_width,
        )
        # Id
        self.canvas.create_text(
            x, y, text=str(vertex.id),
            font=("Segoe UI", 11, "bold"), fill="white",
        )
        # Label fora do círculo (abaixo)
        label_short = vertex.label[:24] + ("…" if len(vertex.label) > 24 else "")
        self.canvas.create_text(
            x, y + VERTEX_RADIUS + 12,
            text=label_short,
            font=("Segoe UI", 8), fill="#34495e",
        )

    # ------------------------------------------------------------------
    # Resultado
    # ------------------------------------------------------------------

    def _show_result_success(self, response: RouteResponse) -> None:
        path_str = self._format_path(response.path)
        text = (
            f"✓ ROTA ENCONTRADA\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"Algoritmo:    {response.algorithm}\n"
            f"Vértices:     {len(response.path)}\n"
            f"Custo total:  {response.total_cost:.2f} m\n"
            f"Tempo:        {response.time_ms:.3f} ms\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"SEQUÊNCIA DA ROTA:\n\n"
            f"{path_str}\n"
        )
        self._write_result(text)

    def _show_result_failure(self, response: RouteResponse) -> None:
        text = (
            f"⚠ ROTA NÃO ENCONTRADA\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"Algoritmo:    {response.algorithm}\n"
            f"Tempo:        {response.time_ms:.3f} ms\n\n"
            f"Motivo:\n{response.message}\n"
        )
        self._write_result(text)

    def _format_path(self, path: list[int]) -> str:
        if not path or self.graph is None:
            return "(vazio)"
        lines = []
        for i, v_id in enumerate(path):
            label = self.graph.get_vertex(v_id).label
            label_short = label[:30] + ("…" if len(label) > 30 else "")
            prefix = "▸" if i < len(path) - 1 else "◆"
            lines.append(f"  {prefix} [{v_id}] {label_short}")
        return "\n".join(lines)

    def _write_result(self, text: str) -> None:
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete("1.0", tk.END)
        self.result_text.insert("1.0", text)
        self.result_text.config(state=tk.DISABLED)

    def _clear_result_text(self) -> None:
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete("1.0", tk.END)
        self.result_text.insert("1.0", "Calcule uma rota para ver o resultado aqui.")
        self.result_text.config(state=tk.DISABLED)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_id(combo_text: str) -> int:
        # Formato: "[N] label"
        end = combo_text.index("]")
        return int(combo_text[1:end])

    def _set_status(self, msg: str) -> None:
        self.status_bar.config(text=msg)


def run() -> None:
    """Inicia a aplicação GUI."""
    root = tk.Tk()
    app = FoodNodeGUI(root)
    root.mainloop()


if __name__ == "__main__":
    run()
