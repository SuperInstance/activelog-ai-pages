"""Chart builder with ASCII-art representations."""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Sequence


class ChartType(Enum):
    BAR = "bar"
    LINE = "line"
    STACKED_BAR = "stacked_bar"
    PIE = "pie"


@dataclass
class Series:
    """A named data series."""

    name: str
    values: Sequence[float]
    color: str = ""


@dataclass
class ChartConfig:
    """Configuration for chart rendering."""

    width: int = 60
    height: int = 20
    title: str = ""
    x_label: str = ""
    y_label: str = ""
    show_legend: bool = True
    show_axis: bool = True
    bar_char: str = "█"
    line_char: str = "•"
    fill_char: str = "░"


class ChartBuilder:
    """Build ASCII chart representations from data series.

    Usage::

        builder = ChartBuilder()
        builder.set_config(title="CPU Usage", width=50, height=15)
        builder.add_series("cpu", [30, 55, 80, 45, 60])
        output = builder.render(ChartType.BAR)
    """

    def __init__(self, config: ChartConfig | None = None) -> None:
        self.config = config or ChartConfig()
        self._series: list[Series] = []

    def set_config(
        self,
        *,
        width: int | None = None,
        height: int | None = None,
        title: str | None = None,
        x_label: str | None = None,
        y_label: str | None = None,
        show_legend: bool | None = None,
        show_axis: bool | None = None,
    ) -> "ChartBuilder":
        if width is not None:
            self.config.width = width
        if height is not None:
            self.config.height = height
        if title is not None:
            self.config.title = title
        if x_label is not None:
            self.config.x_label = x_label
        if y_label is not None:
            self.config.y_label = y_label
        if show_legend is not None:
            self.config.show_legend = show_legend
        if show_axis is not None:
            self.config.show_axis = show_axis
        return self

    def add_series(
        self, name: str, values: Sequence[float], color: str = ""
    ) -> "ChartBuilder":
        self._series.append(Series(name=name, values=list(values), color=color))
        return self

    def clear(self) -> "ChartBuilder":
        self._series.clear()
        return self

    def render(self, chart_type: ChartType = ChartType.BAR) -> str:
        if not self._series:
            return self._empty_chart()

        dispatch = {
            ChartType.BAR: self._render_bar,
            ChartType.LINE: self._render_line,
            ChartType.STACKED_BAR: self._render_stacked_bar,
            ChartType.PIE: self._render_pie,
        }
        renderer = dispatch.get(chart_type, self._render_bar)
        lines: list[str] = []

        if self.config.title:
            lines.append(self._center(self.config.title))
            lines.append("")

        lines.append(renderer())
        lines.append(self._render_legend())

        return "\n".join(lines)

    # -- bar chart --------------------------------------------------------

    def _render_bar(self) -> str:
        cfg = self.config
        series = self._series[0]
        values = series.values
        if not values:
            return "(no data)"

        max_val = max(abs(v) for v in values) or 1
        bar_width = max(1, (cfg.width - 8) // max(len(values), 1))
        rows: list[str] = []

        for v in values:
            bar_len = int(abs(v) / max_val * bar_width)
            bar = cfg.bar_char * bar_len
            rows.append(f"{v:>7.1f} │{bar}")
        return "\n".join(rows)

    # -- line chart -------------------------------------------------------

    def _render_line(self) -> str:
        cfg = self.config
        series = self._series[0]
        values = series.values
        if not values:
            return "(no data)"

        h = cfg.height
        w = cfg.width - 8
        min_v = min(values)
        max_v = max(values)
        span = max_v - min_v or 1

        grid: list[list[str]] = [[" " for _ in range(w)] for _ in range(h)]
        for i, v in enumerate(values):
            col = int(i / max(len(values) - 1, 1) * (w - 1))
            row = h - 1 - int((v - min_v) / span * (h - 1))
            if 0 <= row < h and 0 <= col < w:
                grid[row][col] = cfg.line_char

        rows = []
        for r in range(h):
            y_val = min_v + (h - 1 - r) / max(h - 1, 1) * span
            rows.append(f"{y_val:>7.1f} │{''.join(grid[r])}")
        return "\n".join(rows)

    # -- stacked bar chart ------------------------------------------------

    def _render_stacked_bar(self) -> str:
        cfg = self.config
        n_bars = max(len(s.values) for s in self._series) if self._series else 0
        if n_bars == 0:
            return "(no data)"

        bar_width = max(1, (cfg.width - 8) // max(n_bars, 1))
        rows: list[str] = []

        for i in range(n_bars):
            total = sum(abs(s.values[i]) for s in self._series if i < len(s.values)) or 1
            bar = ""
            for s in self._series:
                if i < len(s.values):
                    seg_len = int(abs(s.values[i]) / total * bar_width)
                    bar += cfg.bar_char * seg_len
            rows.append(f"{total:>7.1f} │{bar}")

        return "\n".join(rows)

    # -- pie chart --------------------------------------------------------

    def _render_pie(self) -> str:
        series = self._series[0]
        values = series.values
        if not values:
            return "(no data)"

        total = sum(abs(v) for v in values) or 1
        chars = "░▒▓█"
        width = self.config.width
        bar = ""
        for v in values:
            pct = abs(v) / total
            seg = int(pct * width)
            idx = min(int(pct * len(chars)), len(chars) - 1)
            bar += chars[idx] * seg

        lines = [f"  ┌{'─' * width}┐", f"  │{bar:<{width}}│", f"  └{'─' * width}┘"]
        for i, v in enumerate(values):
            name = self._series[i].name if i < len(self._series) else f"Slice {i+1}"
            pct = abs(v) / total * 100
            lines.append(f"  {name}: {pct:.1f}%")

        return "\n".join(lines)

    # -- helpers ----------------------------------------------------------

    def _render_legend(self) -> str:
        if not self.config.show_legend or len(self._series) <= 1:
            return ""
        parts = [f"  ─ {s.name}" for s in self._series]
        return "\n".join(parts)

    def _center(self, text: str) -> str:
        pad = max(self.config.width - len(text), 0) // 2
        return " " * pad + text

    def _empty_chart(self) -> str:
        h = self.config.height
        w = self.config.width
        lines = []
        if self.config.title:
            lines.append(self._center(self.config.title))
            lines.append("")
        for _ in range(h):
            lines.append(" " * 8 + "│" + " " * (w - 8))
        lines.append(" " * 8 + "└" + "─" * (w - 8))
        return "\n".join(lines)

    def to_dict(self) -> dict:
        return {
            "config": {
                "width": self.config.width,
                "height": self.config.height,
                "title": self.config.title,
            },
            "series": [{"name": s.name, "values": s.values} for s in self._series],
        }
