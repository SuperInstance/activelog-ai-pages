"""Dashboard panel types and configuration."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class PanelType(Enum):
    CHART = "chart"
    TABLE = "table"
    GAUGE = "gauge"
    TIMELINE = "timeline"


@dataclass
class Panel:
    """A single dashboard panel.

    Attributes:
        id: Unique panel identifier.
        title: Display title.
        panel_type: Type of panel (chart, table, gauge, timeline).
        data: Panel-specific data payload.
        width: Grid width in columns (default 1).
        height: Grid height in rows (default 1).
        refresh_interval: Auto-refresh interval in seconds (0 = off).
        position: Optional (row, col) grid position override.
    """

    id: str
    title: str
    panel_type: PanelType
    data: dict[str, Any] = field(default_factory=dict)
    width: int = 1
    height: int = 1
    refresh_interval: int = 0
    position: tuple[int, int] | None = None

    # -- factory helpers --------------------------------------------------

    @classmethod
    def chart(
        cls,
        id: str,
        title: str,
        *,
        values: list[float] | None = None,
        labels: list[str] | None = None,
        chart_type: str = "bar",
        width: int = 1,
        height: int = 1,
    ) -> "Panel":
        return cls(
            id=id,
            title=title,
            panel_type=PanelType.CHART,
            data={
                "values": values or [],
                "labels": labels or [],
                "chart_type": chart_type,
            },
            width=width,
            height=height,
        )

    @classmethod
    def table(
        cls,
        id: str,
        title: str,
        *,
        columns: list[str] | None = None,
        rows: list[list[Any]] | None = None,
        width: int = 1,
        height: int = 1,
    ) -> "Panel":
        return cls(
            id=id,
            title=title,
            panel_type=PanelType.TABLE,
            data={"columns": columns or [], "rows": rows or []},
            width=width,
            height=height,
        )

    @classmethod
    def gauge(
        cls,
        id: str,
        title: str,
        *,
        value: float = 0.0,
        min_val: float = 0.0,
        max_val: float = 100.0,
        unit: str = "",
        warning: float | None = None,
        critical: float | None = None,
    ) -> "Panel":
        return cls(
            id=id,
            title=title,
            panel_type=PanelType.GAUGE,
            data={
                "value": value,
                "min": min_val,
                "max": max_val,
                "unit": unit,
                "warning": warning,
                "critical": critical,
            },
            width=1,
            height=1,
        )

    @classmethod
    def timeline(
        cls,
        id: str,
        title: str,
        *,
        events: list[dict[str, Any]] | None = None,
        start: str = "",
        end: str = "",
        width: int = 2,
        height: int = 1,
    ) -> "Panel":
        return cls(
            id=id,
            title=title,
            panel_type=PanelType.TIMELINE,
            data={"events": events or [], "start": start, "end": end},
            width=width,
            height=height,
        )

    # -- rendering --------------------------------------------------------

    def render(self) -> str:
        renderers = {
            PanelType.CHART: self._render_chart,
            PanelType.TABLE: self._render_table,
            PanelType.GAUGE: self._render_gauge,
            PanelType.TIMELINE: self._render_timeline,
        }
        body = renderers[self.panel_type]()
        return f"┌─ {self.title} {'─' * max(40 - len(self.title), 0)}┐\n{body}\n└{'─' * 50}┘"

    def _render_chart(self) -> str:
        from .chart import ChartBuilder, ChartType

        builder = ChartBuilder()
        builder.set_config(title=self.title)
        if self.data.get("values"):
            builder.add_series("data", self.data["values"])
        ct = self.data.get("chart_type", "bar")
        chart_type = ChartType(ct)
        return builder.render(chart_type)

    def _render_table(self) -> str:
        columns = self.data.get("columns", [])
        rows = self.data.get("rows", [])
        if not columns:
            return "  (empty table)"

        col_widths = [len(c) for c in columns]
        for row in rows:
            for i, cell in enumerate(row):
                if i < len(col_widths):
                    col_widths[i] = max(col_widths[i], len(str(cell)))

        header = " │ ".join(str(c).ljust(col_widths[i]) for i, c in enumerate(columns))
        sep = "─┼─".join("─" * w for w in col_widths)
        lines = [f"  {header}", f"  {sep}"]
        for row in rows:
            cells = []
            for i in range(len(columns)):
                val = str(row[i]) if i < len(row) else ""
                cells.append(val.ljust(col_widths[i]))
            lines.append(f"  {' │ '.join(cells)}")

        return "\n".join(lines)

    def _render_gauge(self) -> str:
        val = self.data.get("value", 0)
        mn = self.data.get("min", 0)
        mx = self.data.get("max", 100)
        unit = self.data.get("unit", "")
        span = mx - mn or 1
        pct = (val - mn) / span
        bar_width = 40
        filled = int(pct * bar_width)

        if self.data.get("critical") is not None and val >= self.data["critical"]:
            fill_char = "█"
        elif self.data.get("warning") is not None and val >= self.data["warning"]:
            fill_char = "▓"
        else:
            fill_char = "▒"

        bar = fill_char * filled + "░" * (bar_width - filled)
        return f"  [{bar}] {val:.1f}{unit} ({pct:.0%})"

    def _render_timeline(self) -> str:
        events = self.data.get("events", [])
        if not events:
            return "  (no events)"
        lines = []
        for evt in events:
            ts = evt.get("time", "?")
            label = evt.get("label", "")
            marker = evt.get("marker", "●")
            lines.append(f"  {marker} {ts} — {label}")
        return "\n".join(lines)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "type": self.panel_type.value,
            "data": self.data,
            "width": self.width,
            "height": self.height,
            "refresh_interval": self.refresh_interval,
            "position": self.position,
        }
