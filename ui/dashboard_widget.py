from __future__ import annotations

import pandas as pd
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from PySide6.QtWidgets import QVBoxLayout, QWidget

from services.analytics import DashboardAnalytics


class DashboardRenderError(Exception):
    """AKan di panggil ketika rendering chart error"""


class DashboardWidget(QWidget):

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self.figure = Figure(figsize=(12, 5), tight_layout=True)
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.current_dataframe = pd.DataFrame()
        self.current_chart_type = "Sales by City"

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.canvas)

    def update_dashboard(
        self,
        dataframe: pd.DataFrame,
        chart_type: str,
    ) -> None:
        self.current_dataframe = dataframe.copy()
        self.current_chart_type = chart_type

        try:
            self.render_charts()
        except Exception as error:
            raise DashboardRenderError(f"Failed to render charts: {error}") from error

    def render_charts(self) -> None:
        self.figure.clear()
        axis_left = self.figure.add_subplot(1, 2, 1)
        axis_right = self.figure.add_subplot(1, 2, 2)

        axis_left.set_facecolor("#ffffff")
        axis_right.set_facecolor("#ffffff")

        if self.current_dataframe.empty:
            axis_left.text(0.5, 0.5, "No data available", ha="center", va="center")
            axis_right.text(0.5, 0.5, "No data available", ha="center", va="center")
            axis_left.set_axis_off()
            axis_right.set_axis_off()
            self.canvas.draw()
            return

        if self.current_chart_type == "Sales by City":
            data = DashboardAnalytics.aggregate_sales_by_city(self.current_dataframe)
            axis_left.bar(data.index, data.values, color="#1f77b4")
            axis_left.set_title("Total Sales by City")
            axis_left.set_ylabel("Sales")
            axis_left.tick_params(axis="x", rotation=20)
        elif self.current_chart_type == "Sales by Product Line":
            data = DashboardAnalytics.aggregate_sales_by_product_line(
                self.current_dataframe
            )
            axis_left.bar(data.index, data.values, color="#2a9d8f")
            axis_left.set_title("Total Sales by Product Line")
            axis_left.set_ylabel("Sales")
            axis_left.tick_params(axis="x", rotation=35)
        elif self.current_chart_type == "Sales Trend":
            data = DashboardAnalytics.aggregate_sales_trend(self.current_dataframe)
            axis_left.plot(data.index, data.values, color="#e76f51", marker="o")
            axis_left.set_title("Sales Trend by Date")
            axis_left.set_ylabel("Sales")
            axis_left.tick_params(axis="x", rotation=35)
        else:
            data = DashboardAnalytics.aggregate_quantity_by_product_line(
                self.current_dataframe
            )
            axis_left.barh(data.index, data.values, color="#f4a261")
            axis_left.set_title("Quantity by Product Line")
            axis_left.set_xlabel("Quantity")

        if self.current_chart_type in {"Sales by City", "Sales by Product Line"}:
            pie_data = DashboardAnalytics.payment_distribution(self.current_dataframe)
            pie_title = "Payment Method Distribution"
        else:
            pie_data = DashboardAnalytics.customer_type_distribution(
                self.current_dataframe
            )
            pie_title = "Customer Type Distribution"

        axis_right.pie(
            pie_data.values,
            labels=pie_data.index,
            autopct="%1.1f%%",
            startangle=90,
            wedgeprops={"edgecolor": "white", "linewidth": 1},
        )
        axis_right.set_title(pie_title)

        for axis in (axis_left, axis_right):
            for spine in axis.spines.values():
                spine.set_visible(False)

        self.canvas.draw()

    def get_figure(self) -> Figure:
        return self.figure
