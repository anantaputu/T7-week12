# Nama: I Putu Ananta Sugiartha
# NIM: 113
# Kelas: PemVis D

"""Dashboard Supermarket Sales"""

from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication, QMessageBox

from ui.main_window import MainWindow


def load_stylesheet(app: QApplication, stylesheet_path: Path) -> None:
    if stylesheet_path.exists():
        app.setStyleSheet(stylesheet_path.read_text(encoding="utf-8"))


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("Dashboard Supermarket Sales")

    project_root = Path(__file__).resolve().parent
    stylesheet_path = project_root / "assets" / "style.qss"
    dataset_path = project_root / "data" / "supermarket_sales.csv"

    load_stylesheet(app, stylesheet_path)

    try:
        window = MainWindow(dataset_path)
        window.show()
    except Exception as error:
        message = (
            "Aplikasi gagal dijalankan.\n\n"
            f"Detail error:\n{error}"
        )
        QMessageBox.critical(None, "Application Error", message)
        return 1

    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
