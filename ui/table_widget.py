from __future__ import annotations

import pandas as pd
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


class DataTableWidget(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self.original_dataframe = pd.DataFrame()
        self.current_dataframe = pd.DataFrame()
        self.search_text = ""

        self.info_label = QLabel("Rows: 0")
        self.info_label.setObjectName("tableInfoLabel")

        self.table = QTableWidget()
        self.table.setSortingEnabled(True)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.setWordWrap(False)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        layout.addWidget(self.info_label)
        layout.addWidget(self.table)

    def load_dataframe(self, dataframe: pd.DataFrame) -> None:
        self.original_dataframe = dataframe.copy()
        self.apply_search(self.search_text)

    def set_search_text(self, text: str) -> None:    
        self.search_text = text.strip()
        self.apply_search(self.search_text)

    def apply_search(self, search_text: str) -> None:
        if self.original_dataframe.empty:
            self.current_dataframe = self.original_dataframe.copy()
            self.populate_table(self.current_dataframe)
            return

        if not search_text:
            filtered = self.original_dataframe.copy()
        else:
            mask = self.original_dataframe.apply(
                lambda row: row.astype(str).str.contains(
                    search_text, case=False, na=False
                ).any(),
                axis=1,
            )
            filtered = self.original_dataframe[mask].reset_index(drop=True)

        self.current_dataframe = filtered
        self.populate_table(filtered)

    def populate_table(self, dataframe: pd.DataFrame) -> None:
        self.table.setSortingEnabled(False)
        self.table.clear()
        self.table.setRowCount(len(dataframe))
        self.table.setColumnCount(len(dataframe.columns))
        self.table.setHorizontalHeaderLabels([str(col) for col in dataframe.columns])

        for row_index, (_, row) in enumerate(dataframe.iterrows()):
            for column_index, value in enumerate(row):
                if pd.isna(value):
                    display_value = ""
                elif hasattr(value, "strftime"):
                    display_value = value.strftime("%Y-%m-%d")
                else:
                    display_value = str(value)

                item = QTableWidgetItem(display_value)
                item.setFlags(item.flags() ^ Qt.ItemIsEditable)
                self.table.setItem(row_index, column_index, item)

        self.table.resizeColumnsToContents()
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSortingEnabled(True)
        self.info_label.setText(f"Rows: {len(dataframe)}")
