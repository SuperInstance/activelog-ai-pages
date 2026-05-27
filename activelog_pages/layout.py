"""Layout engine arranging panels in a grid."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence

from .panel import Panel


@dataclass
class GridCell:
    """A cell in the layout grid."""

    row: int
    col: int
    panel: Panel


@dataclass
class LayoutResult:
    """Result of a layout computation."""

    cells: list[GridCell] = field(default_factory=list)
    grid_width: int = 0
    grid_height: int = 0

    def render(self) -> str:
        if not self.cells:
            return "(empty dashboard)"

        # Build grid
        grid: dict[tuple[int, int], Panel] = {}
        for cell in self.cells:
            grid[(cell.row, cell.col)] = cell.panel

        lines: list[str] = []
        for r in range(self.grid_height):
            row_panels = sorted(
                [c for c in self.cells if c.row == r], key=lambda c: c.col
            )
            if row_panels:
                for cell in row_panels:
                    lines.append(cell.panel.render())
                lines.append("")  # blank line between rows

        return "\n".join(lines)

    def to_dict(self) -> dict:
        return {
            "grid_width": self.grid_width,
            "grid_height": self.grid_height,
            "cells": [
                {"row": c.row, "col": c.col, "panel": c.panel.id}
                for c in self.cells
            ],
        }


class LayoutEngine:
    """Arrange panels in a responsive grid layout.

    The engine places panels row-by-row, wrapping when the row width
    exceeds the maximum columns.

    Usage::

        engine = LayoutEngine(max_columns=12)
        panels = [
            Panel.chart("cpu", "CPU", width=6),
            Panel.chart("mem", "Memory", width=6),
            Panel.table("logs", "Recent Logs", width=12),
        ]
        layout = engine.layout(panels)
        print(layout.render())
    """

    def __init__(self, max_columns: int = 12) -> None:
        self.max_columns = max_columns

    def layout(self, panels: Sequence[Panel]) -> LayoutResult:
        cells: list[GridCell] = []
        row = 0
        col = 0
        max_row = 0

        for panel in panels:
            # Honor explicit position if set
            if panel.position is not None:
                pr, pc = panel.position
                cells.append(GridCell(row=pr, col=pc, panel=panel))
                max_row = max(max_row, pr + panel.height)
                continue

            # Wrap if panel doesn't fit
            if col + panel.width > self.max_columns:
                row += 1
                col = 0

            cells.append(GridCell(row=row, col=col, panel=panel))
            max_row = max(max_row, row + panel.height)
            col += panel.width

        return LayoutResult(
            cells=cells,
            grid_width=self.max_columns,
            grid_height=max_row,
        )

    def layout_vertical(self, panels: Sequence[Panel]) -> LayoutResult:
        """Stack all panels vertically (1 column)."""
        cells: list[GridCell] = []
        row = 0
        for panel in panels:
            cells.append(GridCell(row=row, col=0, panel=panel))
            row += panel.height
        return LayoutResult(cells=cells, grid_width=1, grid_height=row)
