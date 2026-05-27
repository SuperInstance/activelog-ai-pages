"""activelog-pages: Log visualization and dashboard page builder."""

from .chart import ChartBuilder, ChartType
from .dashboard import Dashboard, DashboardConfig
from .layout import LayoutEngine
from .panel import Panel, PanelType
from .widget import HeatmapWidget, SparklineWidget, StatCardWidget, Widget

__version__ = "0.1.0"
__all__ = [
    "ChartBuilder",
    "ChartType",
    "Dashboard",
    "DashboardConfig",
    "LayoutEngine",
    "Panel",
    "PanelType",
    "StatCardWidget",
    "SparklineWidget",
    "HeatmapWidget",
    "Widget",
]
