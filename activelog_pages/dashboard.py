"""Dashboard: top-level container for panels with layout and refresh settings."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Sequence

from .layout import LayoutEngine, LayoutResult
from .panel import Panel


@dataclass
class DashboardConfig:
    """Dashboard-level configuration.

    Attributes:
        title: Dashboard title.
        description: Optional description.
        refresh_interval: Global refresh interval in seconds (0 = manual).
        max_columns: Grid column count.
        theme: Visual theme hint (e.g. "dark", "light").
    """

    title: str = "Dashboard"
    description: str = ""
    refresh_interval: int = 0
    max_columns: int = 12
    theme: str = "dark"


class Dashboard:
    """Top-level dashboard container.

    Aggregates panels, applies layout, and renders the full dashboard view.

    Usage::

        dash = Dashboard("System Monitor")
        dash.add_panel(Panel.chart("cpu", "CPU Usage", values=[30, 55, 80]))
        dash.add_panel(Panel.table("logs", "Logs", columns=["time","msg"], rows=[]))
        print(dash.render())
    """

    def __init__(
        self,
        title: str = "Dashboard",
        config: DashboardConfig | None = None,
    ) -> None:
        self.config = config or DashboardConfig(title=title)
        self._panels: list[Panel] = []

    @property
    def title(self) -> str:
        return self.config.title

    @property
    def panels(self) -> list[Panel]:
        return list(self._panels)

    def add_panel(self, panel: Panel) -> "Dashboard":
        self._panels.append(panel)
        return self

    def remove_panel(self, panel_id: str) -> bool:
        before = len(self._panels)
        self._panels = [p for p in self._panels if p.id != panel_id]
        return len(self._panels) < before

    def get_panel(self, panel_id: str) -> Panel | None:
        for p in self._panels:
            if p.id == panel_id:
                return p
        return None

    def set_layout(self, panel_id: str, row: int, col: int) -> bool:
        panel = self.get_panel(panel_id)
        if panel is None:
            return False
        panel.position = (row, col)
        return True

    def layout(self) -> LayoutResult:
        engine = LayoutEngine(max_columns=self.config.max_columns)
        return engine.layout(self._panels)

    def render(self) -> str:
        result = self.layout()
        lines: list[str] = []

        # Header
        lines.append(f"╔{'═' * 60}╗")
        title_pad = max(60 - len(self.config.title), 0)
        lines.append(f"║ {self.config.title}{' ' * title_pad}║")

        if self.config.description:
            desc_pad = max(60 - len(self.config.description), 0)
            lines.append(f"║ {self.config.description}{' ' * desc_pad}║")

        if self.config.refresh_interval > 0:
            info = f"  ↻ Refresh: {self.config.refresh_interval}s  |  {len(self._panels)} panels"
        else:
            info = f"  Manual refresh  |  {len(self._panels)} panels"
        info_pad = max(60 - len(info), 0)
        lines.append(f"║ {info}{' ' * info_pad}║")
        lines.append(f"╚{'═' * 60}╝")
        lines.append("")

        lines.append(result.render())
        return "\n".join(lines)

    def to_dict(self) -> dict[str, Any]:
        return {
            "config": {
                "title": self.config.title,
                "description": self.config.description,
                "refresh_interval": self.config.refresh_interval,
                "max_columns": self.config.max_columns,
                "theme": self.config.theme,
            },
            "panels": [p.to_dict() for p in self._panels],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Dashboard":
        cfg_data = data.get("config", {})
        config = DashboardConfig(
            title=cfg_data.get("title", "Dashboard"),
            description=cfg_data.get("description", ""),
            refresh_interval=cfg_data.get("refresh_interval", 0),
            max_columns=cfg_data.get("max_columns", 12),
            theme=cfg_data.get("theme", "dark"),
        )
        dash = cls(config=config)
        for pdata in data.get("panels", []):
            from .panel import PanelType

            panel = Panel(
                id=pdata["id"],
                title=pdata["title"],
                panel_type=PanelType(pdata["type"]),
                data=pdata.get("data", {}),
                width=pdata.get("width", 1),
                height=pdata.get("height", 1),
            )
            dash.add_panel(panel)
        return dash
