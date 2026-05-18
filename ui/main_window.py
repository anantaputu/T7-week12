from __future__ import annotations

from pathlib import Path

import pandas as pd
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from services.analytics import DashboardAnalytics
from services.data_loader import DataLoader, DataLoaderError
from services.exporter import ChartExporter
from ui.dashboard_widget import DashboardRenderError, DashboardWidget
from ui.summary_cards import SummaryCardsWidget
from ui.table_widget import DataTableWidget


class MainWindow(QMainWindow):
    CHART_OPTIONS = [
        "Sales by City",
        "Sales by Product Line",
        "Sales Trend",
        "Quantity by Product Line",
    ]

    def __init__(self, dataset_path: str | Path, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.dataset_path = Path(dataset_path)
        self.dataframe = pd.DataFrame()
        self.filtered_dataframe = pd.DataFrame()

        self.setWindowTitle("Supermarket Sales Dashboard")
        self.resize(1400, 900)

        self.title_label = QLabel("Supermarket Sales Dashboard")
        self.title_label.setObjectName("pageTitle")

        self.city_filter = self._build_combo_box()
        self.branch_filter = self._build_combo_box()
        self.gender_filter = self._build_combo_box()
        self.customer_filter = self._build_combo_box()
        self.chart_filter = self._build_combo_box(self.CHART_OPTIONS, include_all=False)

        self.refresh_button = QPushButton("Refresh")
        self.export_button = QPushButton("Export PNG")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search data...")
        self.search_input.setClearButtonEnabled(True)
        self.search_input.setObjectName("searchInput")

        self.summary_cards = SummaryCardsWidget()
        self.dashboard_widget = DashboardWidget()
        self.table_widget = DataTableWidget()

        self._build_ui()
        self._connect_signals()
        self.load_dashboard_data()

    def _build_combo_box(
        self,
        values: list[str] | None = None,
        include_all: bool = True,
    ) -> QComboBox:
        combo_box = QComboBox()
        combo_box.setObjectName("filterCombo")
        combo_box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        items: list[str] = []
        if include_all:
            items.append("All")
        if values:
            items.extend(values)
        combo_box.addItems(items)
        return combo_box

    def _build_ui(self) -> None:
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        root_layout = QVBoxLayout(central_widget)
        root_layout.setContentsMargins(24, 20, 24, 20)
        root_layout.setSpacing(18)

        root_layout.addWidget(self.title_label)
        root_layout.addWidget(self._build_filter_section())
        root_layout.addWidget(self.summary_cards)
        root_layout.addWidget(self.dashboard_widget, stretch=3)
        root_layout.addWidget(self.table_widget, stretch=4)

    def _build_filter_section(self) -> QWidget:
        container = QWidget()
        container.setObjectName("panel")
        layout = QGridLayout(container)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setHorizontalSpacing(12)
        layout.setVerticalSpacing(12)

        controls = [
            ("City", self.city_filter, 0, 0),
            ("Branch", self.branch_filter, 0, 1),
            ("Gender", self.gender_filter, 0, 2),
            ("Customer", self.customer_filter, 0, 3),
            ("Chart", self.chart_filter, 0, 4),
        ]

        for label_text, widget, row, column in controls:
            field = self._build_labeled_field(label_text, widget)
            layout.addWidget(field, row, column)

        button_row = QWidget()
        button_layout = QHBoxLayout(button_row)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(12)
        button_layout.addWidget(self.refresh_button)
        button_layout.addWidget(self.export_button)
        button_layout.addStretch(1)

        search_field = self._build_labeled_field("Search", self.search_input)

        layout.addWidget(button_row, 1, 0, 1, 2)
        layout.addWidget(search_field, 1, 2, 1, 3)
        return container

    def _build_labeled_field(self, text: str, widget: QWidget) -> QWidget:
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        label = QLabel(text)
        label.setObjectName("fieldLabel")
        layout.addWidget(label)
        layout.addWidget(widget)
        return container

    def _connect_signals(self) -> None:    
        for combo_box in (
            self.city_filter,
            self.branch_filter,
            self.gender_filter,
            self.customer_filter,
            self.chart_filter,
        ):
            combo_box.currentIndexChanged.connect(self.apply_filters)

        self.refresh_button.clicked.connect(self.refresh_dashboard)
        self.export_button.clicked.connect(self.export_chart)
        self.search_input.textChanged.connect(self.apply_search)

    def load_dashboard_data(self) -> None:
        try:
            self.dataframe = DataLoader.load_data(self.dataset_path)
        except DataLoaderError as error:
            QMessageBox.critical(self, "Data Loading Error", str(error))
            self.dataframe = pd.DataFrame()
            self.filtered_dataframe = pd.DataFrame()
            return

        self.populate_filters()
        self.apply_filters()

    def populate_filters(self) -> None:
        self._set_combo_values(self.city_filter, sorted(self.dataframe["City"].dropna().unique()))
        self._set_combo_values(
            self.branch_filter,
            sorted(self.dataframe["Branch"].dropna().unique()),
        )
        self._set_combo_values(
            self.gender_filter,
            sorted(self.dataframe["Gender"].dropna().unique()),
        )
        self._set_combo_values(
            self.customer_filter,
            sorted(self.dataframe["Customer type"].dropna().unique()),
        )

    def _set_combo_values(self, combo_box: QComboBox, values: list[str]) -> None:
        combo_box.blockSignals(True)
        combo_box.clear()
        combo_box.addItem("All")
        combo_box.addItems(values)
        combo_box.blockSignals(False)

    def get_filter_values(self) -> dict[str, str]:
        return {
            "city": self.city_filter.currentText(),
            "branch": self.branch_filter.currentText(),
            "gender": self.gender_filter.currentText(),
            "customer_type": self.customer_filter.currentText(),
            "chart_type": self.chart_filter.currentText(),
        }

    def apply_filters(self) -> None:
        if self.dataframe.empty:
            self.summary_cards.update_metrics({})
            self.table_widget.load_dataframe(pd.DataFrame())
            return

        values = self.get_filter_values()
        self.filtered_dataframe = DashboardAnalytics.filter_dataframe(
            self.dataframe,
            city=values["city"],
            branch=values["branch"],
            gender=values["gender"],
            customer_type=values["customer_type"],
        )

        metrics = DashboardAnalytics.summary_metrics(self.filtered_dataframe)
        self.summary_cards.update_metrics(metrics)
        self.table_widget.load_dataframe(self.filtered_dataframe)
        self.apply_search(self.search_input.text())

        try:
            self.dashboard_widget.update_dashboard(
                self.filtered_dataframe,
                values["chart_type"],
            )
        except DashboardRenderError as error:
            QMessageBox.critical(self, "Chart Rendering Error", str(error))

    def apply_search(self, text: str) -> None:
        self.table_widget.set_search_text(text)

    def refresh_dashboard(self) -> None:        
        for combo_box in (
            self.city_filter,
            self.branch_filter,
            self.gender_filter,
            self.customer_filter,
        ):
            combo_box.setCurrentIndex(0)

        self.chart_filter.setCurrentIndex(0)
        self.search_input.clear()
        self.load_dashboard_data()

    def export_chart(self) -> None:
        suggested_name = "supermarket_dashboard.png"
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Dashboard Chart",
            suggested_name,
            "PNG Files (*.png)",
        )

        if not file_path:
            return

        try:
            ChartExporter.export_figure(self.dashboard_widget.get_figure(), file_path)
        except Exception as error:
            QMessageBox.critical(self, "Export Error", f"Failed to export chart:\n{error}")
            return

        QMessageBox.information(
            self,
            "Export Success",
            f"Chart exported successfully to:\n{file_path}",
        )
