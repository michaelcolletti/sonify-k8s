import os
import pytest
import types
from src import main


def test_get_color_in_bounds():
    colors = ["#111111", "#222222", "#333333"]
    assert main.get_color(colors, 1) == "#222222"


def test_get_color_out_of_bounds():
    colors = ["#111111", "#222222", "#333333"]
    assert main.get_color(colors, 10) == "#333333"


def test_get_color_empty():
    assert main.get_color([], 0) == "#808080"


@pytest.mark.parametrize(
    "value,notes_length,min_value,max_value,expected",
    [
        (0, 8, 0, 100, 0),
        (100, 8, 0, 100, 7),
        (50, 8, 0, 100, 3),
        (-10, 8, 0, 100, 0),
        (110, 8, 0, 100, 7),
        (5, 4, 0, 10, 1),
    ],
)
def test_calculate_index(value, notes_length, min_value, max_value, expected):
    assert main.calculate_index(value, notes_length, min_value, max_value) == expected


def test_calculate_index_max_le_min():
    assert main.calculate_index(10, 5, 10, 10) == 0


def test_get_k8s_data_cpu_usage():
    value, extra = main.get_k8s_data("cpu_usage")
    assert 0 <= value <= 100
    assert isinstance(extra, dict)


def test_get_k8s_data_memory_usage():
    value, extra = main.get_k8s_data("memory_usage")
    assert 0 <= value <= 100
    assert isinstance(extra, dict)


def test_get_k8s_data_pod_status():
    value, extra = main.get_k8s_data("pod_status")
    assert value in main.SOUND_MAP["pod_status"]["status_map"].values()
    assert "status" in extra


def test_get_k8s_data_http_latency():
    value, extra = main.get_k8s_data("http_latency")
    assert value >= 0
    assert isinstance(extra, dict)


def test_get_k8s_data_errors_per_second():
    value, extra = main.get_k8s_data("errors_per_second")
    assert 0 <= value <= 5
    assert isinstance(extra, dict)


def test_get_k8s_data_replicas():
    value, extra = main.get_k8s_data("replicas")
    assert 1 <= value <= 5
    assert isinstance(extra, dict)


def test_get_k8s_data_node_pressure():
    value, extra = main.get_k8s_data("node_pressure")
    assert value in [0, 1]
    assert "pressure" in extra


def test_get_k8s_data_invalid():
    assert main.get_k8s_data("not_a_metric") is None


def test_play_note_test_mode(monkeypatch, caplog):
    monkeypatch.setenv("TEST_MODE", "true")
    with caplog.at_level("INFO"):
        main.play_note(440, 0.1)
        assert "Playing note at 440 Hz" in caplog.text


def test_play_note_normal(monkeypatch):
    # Should not raise even if not in TEST_MODE
    monkeypatch.delenv("TEST_MODE", raising=False)
    main.play_note(440, 0.01)  # Very short duration for test


def test_sonify_k8s_metrics_keyboard_interrupt(monkeypatch):
    # Patch time.sleep to raise KeyboardInterrupt after first call
    calls = {"count": 0}

    def fake_sleep(_):
        if calls["count"] == 0:
            calls["count"] += 1
        else:
            raise KeyboardInterrupt()

    monkeypatch.setattr(main, "play_note", lambda *a, **kw: None)
    monkeypatch.setattr(main, "get_k8s_data", lambda m: (0, {}))
    monkeypatch.setattr(main, "calculate_index", lambda v, l, mi, ma: 0)
    monkeypatch.setattr(main, "get_color", lambda l, i: "#000000")
    monkeypatch.setattr(main, "time", types.SimpleNamespace(sleep=fake_sleep))
    # Should exit cleanly
    main.sonify_k8s_metrics()
