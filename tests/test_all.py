"""Comprehensive tests for activelog_pages."""

import pytest

from activelog_pages import (
    ChartBuilder,
    ChartType,
    Dashboard,
    DashboardConfig,
    HeatmapWidget,
    LayoutEngine,
    Panel,
    PanelType,
    SparklineWidget,
    StatCardWidget,
)


# ── ChartBuilder ──────────────────────────────────────────────────────────


class TestChartBuilder:
    def test_empty_chart(self):
        cb = ChartBuilder()
        result = cb.render()
        assert "│" in result

    def test_bar_chart(self):
        cb = ChartBuilder()
        cb.add_series("test", [10, 20, 30])
        result = cb.render(ChartType.BAR)
        assert "10.0" in result
        assert "20.0" in result
        assert "30.0" in result

    def test_line_chart(self):
        cb = ChartBuilder()
        cb.add_series("temp", [1, 5, 3, 8, 2])
        result = cb.render(ChartType.LINE)
        assert "•" in result

    def test_stacked_bar(self):
        cb = ChartBuilder()
        cb.add_series("a", [10, 20])
        cb.add_series("b", [5, 15])
        result = cb.render(ChartType.STACKED_BAR)
        assert "█" in result

    def test_pie_chart(self):
        cb = ChartBuilder()
        cb.add_series("a", [40, 30, 30])
        result = cb.render(ChartType.PIE)
        assert "%" in result
        assert "40.0%" in result

    def test_title_centering(self):
        cb = ChartBuilder()
        cb.set_config(title="My Chart")
        cb.add_series("x", [1])
        result = cb.render()
        assert "My Chart" in result

    def test_config_chaining(self):
        cb = ChartBuilder()
        ret = cb.set_config(width=80, height=10, title="Test")
        assert ret is cb  # fluent API

    def test_clear(self):
        cb = ChartBuilder()
        cb.add_series("a", [1, 2, 3])
        cb.clear()
        result = cb.render()
        assert "1.0" not in result

    def test_legend_with_multiple_series(self):
        cb = ChartBuilder()
        cb.set_config(show_legend=True)
        cb.add_series("alpha", [1])
        cb.add_series("beta", [2])
        result = cb.render(ChartType.LINE)
        assert "alpha" in result
        assert "beta" in result

    def test_to_dict(self):
        cb = ChartBuilder()
        cb.set_config(title="T")
        cb.add_series("s", [1, 2])
        d = cb.to_dict()
        assert d["config"]["title"] == "T"
        assert len(d["series"]) == 1

    def test_zero_values(self):
        cb = ChartBuilder()
        cb.add_series("z", [0, 0, 0])
        result = cb.render(ChartType.BAR)
        assert "0.0" in result

    def test_negative_values(self):
        cb = ChartBuilder()
        cb.add_series("neg", [-5, -10, -3])
        result = cb.render(ChartType.BAR)
        assert "█" in result


# ── Panel ─────────────────────────────────────────────────────────────────


class TestPanel:
    def test_chart_factory(self):
        p = Panel.chart("cpu", "CPU", values=[10, 20, 30])
        assert p.panel_type == PanelType.CHART
        assert p.data["values"] == [10, 20, 30]

    def test_table_factory(self):
        p = Panel.table("t1", "My Table", columns=["a", "b"], rows=[[1, 2]])
        assert p.panel_type == PanelType.TABLE
        rendered = p.render()
        assert "a" in rendered
        assert "1" in rendered

    def test_gauge_factory(self):
        p = Panel.gauge("g1", "Temp", value=75, unit="°C", warning=70, critical=90)
        assert p.panel_type == PanelType.GAUGE
        rendered = p.render()
        assert "75.0" in rendered

    def test_timeline_factory(self):
        events = [
            {"time": "10:00", "label": "start"},
            {"time": "10:05", "label": "error"},
        ]
        p = Panel.timeline("tl", "Events", events=events)
        assert p.panel_type == PanelType.TIMELINE
        rendered = p.render()
        assert "start" in rendered
        assert "error" in rendered

    def test_gauge_critical(self):
        p = Panel.gauge("g", "CPU", value=95, critical=90)
        rendered = p.render()
        assert "█" in rendered

    def test_gauge_warning(self):
        p = Panel.gauge("g", "CPU", value=75, warning=70, critical=90)
        rendered = p.render()
        assert "▓" in rendered

    def test_empty_table(self):
        p = Panel.table("t", "Empty", columns=[], rows=[])
        rendered = p.render()
        assert "empty" in rendered

    def test_empty_timeline(self):
        p = Panel.timeline("t", "Empty", events=[])
        rendered = p.render()
        assert "no events" in rendered

    def test_to_dict(self):
        p = Panel.chart("c", "Chart", values=[1])
        d = p.to_dict()
        assert d["id"] == "c"
        assert d["type"] == "chart"

    def test_panel_dimensions(self):
        p = Panel.chart("c", "C", width=3, height=2)
        assert p.width == 3
        assert p.height == 2


# ── Widget ────────────────────────────────────────────────────────────────


class TestStatCard:
    def test_basic(self):
        w = StatCardWidget.create("s1", "CPU", 45.2, unit="%", trend_value=5.3)
        rendered = w.render()
        assert "45.2" in rendered
        assert "▲" in rendered

    def test_down_trend(self):
        w = StatCardWidget.create("s1", "Disk", 80, trend_value=-10)
        assert w.trend == "down"
        rendered = w.render()
        assert "▼" in rendered

    def test_neutral_trend(self):
        w = StatCardWidget.create("s1", "Idle", 50, trend_value=0)
        assert w.trend == "neutral"
        rendered = w.render()
        assert "─" in rendered

    def test_to_dict(self):
        w = StatCardWidget(id="s", title="T", value=42.0, unit="%")
        d = w.to_dict()
        assert d["value"] == 42.0
        assert d["type"] == "StatCardWidget"

    def test_icon(self):
        w = StatCardWidget.create("s", "Status", 99, icon="🔥")
        rendered = w.render()
        assert "🔥" in rendered


class TestSparkline:
    def test_basic(self):
        w = SparklineWidget.create("sp", "Load", [1, 3, 5, 7, 9])
        rendered = w.render()
        assert "▁" in rendered or "█" in rendered
        assert "9.0" in rendered

    def test_empty(self):
        w = SparklineWidget.create("sp", "Empty", [])
        rendered = w.render()
        assert "no data" in rendered

    def test_downsample(self):
        vals = list(range(100))
        w = SparklineWidget.create("sp", "Big", vals, width=10)
        rendered = w.render()
        assert len(rendered) > 0

    def test_constant_values(self):
        w = SparklineWidget.create("sp", "Flat", [5, 5, 5, 5])
        rendered = w.render()
        assert "5.0" in rendered


class TestHeatmap:
    def test_basic(self):
        data = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
        w = HeatmapWidget.create("h", "Heat", data, row_labels=["A", "B", "C"])
        rendered = w.render()
        assert "A" in rendered
        assert "█" in rendered

    def test_empty(self):
        w = HeatmapWidget.create("h", "Empty", [])
        rendered = w.render()
        assert "no data" in rendered

    def test_to_dict(self):
        data = [[1, 2], [3, 4]]
        w = HeatmapWidget.create("h", "H", data)
        d = w.to_dict()
        assert d["rows"] == 2
        assert d["cols"] == 2


# ── LayoutEngine ──────────────────────────────────────────────────────────


class TestLayoutEngine:
    def test_single_panel(self):
        engine = LayoutEngine(max_columns=12)
        panels = [Panel.chart("p1", "Chart")]
        result = engine.layout(panels)
        assert len(result.cells) == 1
        assert result.cells[0].row == 0

    def test_wrap(self):
        engine = LayoutEngine(max_columns=6)
        panels = [
            Panel.chart("p1", "A", width=4),
            Panel.chart("p2", "B", width=4),
        ]
        result = engine.layout(panels)
        assert result.cells[0].row == 0
        assert result.cells[1].row == 1

    def test_fit(self):
        engine = LayoutEngine(max_columns=12)
        panels = [
            Panel.chart("p1", "A", width=6),
            Panel.chart("p2", "B", width=6),
        ]
        result = engine.layout(panels)
        assert result.cells[0].row == 0
        assert result.cells[1].row == 0
        assert result.cells[1].col == 6

    def test_explicit_position(self):
        engine = LayoutEngine()
        p = Panel.chart("p1", "C")
        p.position = (3, 5)
        result = engine.layout([p])
        assert result.cells[0].row == 3
        assert result.cells[0].col == 5

    def test_vertical_layout(self):
        engine = LayoutEngine()
        panels = [Panel.chart("a", "A"), Panel.chart("b", "B")]
        result = engine.layout_vertical(panels)
        assert result.cells[0].row == 0
        assert result.cells[1].row == 1

    def test_render_empty(self):
        engine = LayoutEngine()
        result = engine.layout([])
        rendered = result.render()
        assert "empty" in rendered

    def test_render_with_panels(self):
        engine = LayoutEngine()
        panels = [Panel.chart("p", "Test", values=[1, 2, 3])]
        result = engine.layout(panels)
        rendered = result.render()
        assert "Test" in rendered

    def test_to_dict(self):
        engine = LayoutEngine()
        panels = [Panel.chart("p", "X")]
        result = engine.layout(panels)
        d = result.to_dict()
        assert d["grid_width"] == 12
        assert len(d["cells"]) == 1


# ── Dashboard ─────────────────────────────────────────────────────────────


class TestDashboard:
    def test_empty(self):
        d = Dashboard("Empty")
        assert d.title == "Empty"
        assert len(d.panels) == 0

    def test_add_remove(self):
        d = Dashboard("D")
        p = Panel.chart("c", "C")
        d.add_panel(p)
        assert len(d.panels) == 1
        assert d.get_panel("c") is p
        assert d.remove_panel("c")
        assert len(d.panels) == 0

    def test_remove_nonexistent(self):
        d = Dashboard("D")
        assert not d.remove_panel("nope")

    def test_render(self):
        d = Dashboard("Test Dashboard")
        d.add_panel(Panel.chart("cpu", "CPU", values=[30, 50, 70]))
        rendered = d.render()
        assert "Test Dashboard" in rendered
        assert "CPU" in rendered

    def test_config(self):
        cfg = DashboardConfig(title="C", refresh_interval=30, theme="light")
        d = Dashboard(config=cfg)
        assert d.config.refresh_interval == 30
        rendered = d.render()
        assert "30s" in rendered

    def test_set_layout(self):
        d = Dashboard("D")
        d.add_panel(Panel.chart("p1", "A"))
        assert d.set_layout("p1", 2, 3)
        assert d.get_panel("p1").position == (2, 3)
        assert not d.set_layout("nope", 0, 0)

    def test_to_dict(self):
        d = Dashboard("D")
        d.add_panel(Panel.chart("c", "C", values=[1]))
        d_dict = d.to_dict()
        assert d_dict["config"]["title"] == "D"
        assert len(d_dict["panels"]) == 1

    def test_from_dict(self):
        d = Dashboard("D")
        d.add_panel(Panel.chart("c", "C", values=[1, 2]))
        data = d.to_dict()
        restored = Dashboard.from_dict(data)
        assert restored.title == "D"
        assert len(restored.panels) == 1
        assert restored.panels[0].id == "c"

    def test_chaining(self):
        d = Dashboard("D")
        ret = d.add_panel(Panel.chart("a", "A"))
        assert ret is d
