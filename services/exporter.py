from __future__ import annotations

from pathlib import Path

from matplotlib.figure import Figure


class ChartExporter:
    @staticmethod
    def export_figure(figure: Figure, file_path: str | Path) -> None:
        path = Path(file_path)
        if path.suffix.lower() != ".png":
            path = path.with_suffix(".png")

        figure.savefig(path, dpi=200, bbox_inches="tight", facecolor="white")
