"""
Testes unitários para JSONReader e JSONWriter (camada de Infraestrutura).
"""

import json
from pathlib import Path

import pytest

from src.infrastructure.json_reader import JSONReader
from src.infrastructure.json_writer import JSONWriter


@pytest.fixture
def sample_graph_dict():
    """Dict de grafo válido para uso em testes."""
    return {
        "metadata": {
            "name": "Grafo de teste",
            "vertices_count": 3,
            "edges_count": 2,
            "directed": True,
            "weighted": True,
            "weight_unit": "meters"
        },
        "vertices": [
            {"id": 0, "label": "Origem", "type": "origin"},
            {"id": 1, "label": "Meio", "type": "intersection"},
            {"id": 2, "label": "Destino", "type": "destination"}
        ],
        "edges": [
            {"origem": 0, "destino": 1, "peso": 10.0},
            {"origem": 1, "destino": 2, "peso": 20.0}
        ]
    }


class TestJSONReader:

    def test_read_valid_json_file(self, tmp_path, sample_graph_dict):
        path = tmp_path / "valid.json"
        path.write_text(json.dumps(sample_graph_dict), encoding="utf-8")

        graph = JSONReader.read(path)
        assert graph.vertex_count == 3
        assert graph.edge_count == 2
        assert graph.has_vertex(0)
        assert graph.has_vertex(2)

    def test_read_nonexistent_file_raises(self, tmp_path):
        path = tmp_path / "missing.json"
        with pytest.raises(FileNotFoundError):
            JSONReader.read(path)

    def test_read_invalid_json_raises(self, tmp_path):
        path = tmp_path / "invalid.json"
        path.write_text("{ not valid json", encoding="utf-8")
        with pytest.raises(ValueError, match="JSON inválido"):
            JSONReader.read(path)

    def test_read_missing_vertices_field_raises(self, tmp_path):
        path = tmp_path / "no_vertices.json"
        path.write_text(json.dumps({"edges": []}), encoding="utf-8")
        with pytest.raises(KeyError, match="vertices"):
            JSONReader.read(path)

    def test_read_missing_edges_field_raises(self, tmp_path):
        path = tmp_path / "no_edges.json"
        path.write_text(json.dumps({"vertices": []}), encoding="utf-8")
        with pytest.raises(KeyError, match="edges"):
            JSONReader.read(path)

    def test_read_duplicated_vertex_id_raises(self, tmp_path):
        path = tmp_path / "dup.json"
        bad = {
            "vertices": [
                {"id": 0, "label": "A"},
                {"id": 0, "label": "B"},  # duplicado
            ],
            "edges": []
        }
        path.write_text(json.dumps(bad), encoding="utf-8")
        with pytest.raises(ValueError, match="duplicado"):
            JSONReader.read(path)

    def test_read_negative_weight_raises(self, tmp_path):
        path = tmp_path / "neg.json"
        bad = {
            "vertices": [
                {"id": 0, "label": "A"},
                {"id": 1, "label": "B"},
            ],
            "edges": [{"origem": 0, "destino": 1, "peso": -5.0}]
        }
        path.write_text(json.dumps(bad), encoding="utf-8")
        with pytest.raises(ValueError, match="peso de aresta deve ser >= 0"):
            JSONReader.read(path)

    def test_read_edge_with_invalid_origin_raises(self, tmp_path):
        path = tmp_path / "bad_origin.json"
        bad = {
            "vertices": [{"id": 0, "label": "A"}],
            "edges": [{"origem": 99, "destino": 0, "peso": 1.0}]
        }
        path.write_text(json.dumps(bad), encoding="utf-8")
        with pytest.raises(ValueError, match="origem"):
            JSONReader.read(path)

    def test_read_real_sample_file(self):
        """Lê o arquivo de exemplo real do projeto."""
        path = Path(__file__).parent.parent / "data" / "sample_bairro_8v.json"
        if path.exists():
            graph = JSONReader.read(path)
            assert graph.vertex_count == 8
            assert graph.edge_count == 12
            assert graph.is_directed is True


class TestJSONWriter:

    def test_write_route_creates_file(self, tmp_path):
        out = tmp_path / "route.json"
        JSONWriter.write_route(
            path=out,
            origin=0,
            destination=6,
            path_vertices=[0, 3, 4, 6],
            total_cost=260.0,
            algorithm="dijkstra",
            time_ms=1.234,
        )
        assert out.exists()

    def test_write_route_has_correct_structure(self, tmp_path):
        out = tmp_path / "route.json"
        JSONWriter.write_route(
            path=out,
            origin=0,
            destination=6,
            path_vertices=[0, 3, 4, 6],
            total_cost=260.0,
            algorithm="dijkstra",
            time_ms=1.234,
        )
        data = json.loads(out.read_text(encoding="utf-8"))
        assert data["origem"] == 0
        assert data["destino"] == 6
        assert data["caminho"] == [0, 3, 4, 6]
        assert data["custo_total_metros"] == 260.0
        assert data["algoritmo"] == "dijkstra"
        assert data["tempo_ms"] == 1.234

    def test_write_route_creates_parent_directories(self, tmp_path):
        out = tmp_path / "subdir" / "nested" / "route.json"
        JSONWriter.write_route(
            path=out,
            origin=0,
            destination=1,
            path_vertices=[0, 1],
            total_cost=10.0,
            algorithm="dijkstra",
            time_ms=0.5,
        )
        assert out.exists()
