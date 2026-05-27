"""Dashboard widgets: stat cards, sparklines, heatmaps."""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Sequence


@dataclass
class Widget:
    """Base widget class."""

    id: str
    title: str = ""

    def render(self) -> str:
        return ""

    def to_dict(self) -> dict[str, Any]:
        return {"id": self.id, "title": self.title, "type": type(self).__name__}


@dataclass
class StatCardWidget(Widget):
    """A stat card displaying a single metric with optional trend.

    Attributes:
        value: Current value.
        unit: Display unit (e.g. "%", "ms", "GB").
        trend: Change indicator — positive, negative, or zero.
        trend_value: Numeric trend delta.
        icon: Optional icon/emoji.
        color: Display color hint.
    """

    value: float = 0.0
    unit: str = ""
    trend: str = "neutral"  # "up", "down", "neutral"
    trend_value: float = 0.0
    icon: str = ""
    color: str = ""

    @classmethod
    def create(
        cls,
        id: str,
        title: str,
        value: float,
        *,
        unit: str = "",
        trend_value: float = 0.0,
        icon: str = "",
    ) -> "StatCardWidget":
        if trend_value > 0:
            trend = "up"
        elif trend_value < 0:
            trend = "down"
        else:
            trend = "neutral"
        return cls(
            id=id, title=title, value=value, unit=unit,
            trend=trend, trend_value=trend_value, icon=icon,
        )

    def render(self) -> str:
        trend_arrow = {"up": "▲", "down": "▼", "neutral": "─"}[self.trend]
        trend_sign = "+" if self.trend_value > 0 else ""
        icon_str = f"{self.icon} " if self.icon else ""
        val_str = f"{self.value:.1f}" if isinstance(self.value, float) else str(self.value)

        lines = [
            f"┌─ {icon_str}{self.title} {'─' * max(30 - len(self.title), 0)}┐",
            f"│  {val_str}{self.unit:>6}",
            f"│  {trend_arrow} {trend_sign}{self.trend_value:.1f}{self.unit}",
            f"└{'─' * 46}┘",
        ]
        return "\n".join(lines)

    def to_dict(self) -> dict[str, Any]:
        d = super().to_dict()
        d.update({
            "value": self.value,
            "unit": self.unit,
            "trend": self.trend,
            "trend_value": self.trend_value,
        })
        return d


@dataclass
class SparklineWidget(Widget):
    """A compact inline sparkline chart.

    Renders a small character-based trend line suitable for embedding in dashboards.
    """

    values: Sequence[float] = ()
    width: int = 20

    _CHARS = "▁▂▃▄▅▆▇█"

    @classmethod
    def create(
        cls, id: str, title: str, values: Sequence[float], *, width: int = 20
    ) -> "SparklineWidget":
        return cls(id=id, title=title, values=list(values), width=width)

    def render(self) -> str:
        vals = list(self.values)
        if not vals:
            return f"  {self.title}: (no data)"

        mn = min(vals)
        mx = max(vals)
        span = mx - mn or 1
        chars = self._CHARS
        indices = [int((v - mn) / span * (len(chars) - 1)) for v in vals]

        # Downsample if needed
        if len(indices) > self.width:
            step = len(indices) / self.width
            indices = [indices[int(i * step)] for i in range(self.width)]

        sparkline = "".join(chars[i] for i in indices)
        return f"  {self.title}: {sparkline}  {vals[-1]:.1f}"

    def to_dict(self) -> dict[str, Any]:
        d = super().to_dict()
        d["values"] = list(self.values)
        d["width"] = self.width
        return d


@dataclass
class HeatmapWidget(Widget):
    """A grid-based heatmap visualization.

    Renders a 2D grid of values as characters of varying density.
    """

    rows: int = 7
    cols: int = 24
    data: Sequence[Sequence[float]] = ()
    row_labels: Sequence[str] = ()
    col_labels: Sequence[str] = ()
    threshold: float = 0.0

    _CHARS = " ░▒▓█"

    @classmethod
    def create(
        cls,
        id: str,
        title: str,
        data: Sequence[Sequence[float]],
        *,
        row_labels: Sequence[str] = (),
        col_labels: Sequence[str] = (),
    ) -> "HeatmapWidget":
        rows = len(data)
        cols = max(len(r) for r in data) if data else 0
        return cls(
            id=id, title=title, data=data,
            rows=rows, cols=cols,
            row_labels=row_labels, col_labels=col_labels,
        )

    def render(self) -> str:
        if not self.data:
            return f"  {self.title}: (no data)"

        flat = [v for row in self.data for v in row]
        mn = min(flat)
        mx = max(flat)
        span = mx - mn or 1
        chars = self._CHARS

        lines: list[str] = []
        if self.title:
            lines.append(f"  {self.title}")
            lines.append("")

        for r_idx, row in enumerate(self.data):
            label = self.row_labels[r_idx] if r_idx < len(self.row_labels) else str(r_idx)
            cells = "".join(
                chars[min(int((v - mn) / span * (len(chars) - 1)), len(chars) - 1)]
                for v in row
            )
            lines.append(f"  {label:>8} │{cells}")

        return "\n".join(lines)

    def to_dict(self) -> dict[str, Any]:
        d = super().to_dict()
        d["rows"] = self.rows
        d["cols"] = self.cols
        d["data"] = [list(r) for r in self.data]
        return d
