from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QGridLayout, QLabel, QVBoxLayout, QWidget


class SummaryCard(QFrame):
    def __init__(self, title: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("summaryCard")

        self.title_label = QLabel(title)
        self.title_label.setObjectName("summaryCardTitle")
        self.value_label = QLabel("-")
        self.value_label.setObjectName("summaryCardValue")
        self.value_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(8)
        layout.addWidget(self.title_label)
        layout.addWidget(self.value_label)

    def set_value(self, value: str) -> None:        
        self.value_label.setText(value)


class SummaryCardsWidget(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self.cards = {
            "total_revenue": SummaryCard("Total Revenue"),
            "total_transactions": SummaryCard("Total Transactions"),
            "average_rating": SummaryCard("Average Rating"),
            "best_selling_product": SummaryCard("Best Selling Product"),
        }

        layout = QGridLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setHorizontalSpacing(12)
        layout.setVerticalSpacing(12)

        positions = [
            ("total_revenue", 0, 0),
            ("total_transactions", 0, 1),
            ("average_rating", 0, 2),
            ("best_selling_product", 0, 3),
        ]
        for key, row, column in positions:
            layout.addWidget(self.cards[key], row, column)

    def update_metrics(self, metrics: dict[str, object]) -> None:
        self.cards["total_revenue"].set_value(
            f"${metrics.get('total_revenue', 0.0):,.2f}"
        )
        self.cards["total_transactions"].set_value(
            str(metrics.get("total_transactions", 0))
        )
        self.cards["average_rating"].set_value(
            f"{metrics.get('average_rating', 0.0):.2f}"
        )
        self.cards["best_selling_product"].set_value(
            str(metrics.get("best_selling_product", "-"))
        )
