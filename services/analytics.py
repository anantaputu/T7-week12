from __future__ import annotations

from typing import Any

import pandas as pd


class DashboardAnalytics:

    @staticmethod
    def filter_dataframe(
        dataframe: pd.DataFrame,
        city: str = "All",
        branch: str = "All",
        gender: str = "All",
        customer_type: str = "All",
    ) -> pd.DataFrame:
        filtered = dataframe.copy()

        filters = {
            "City": city,
            "Branch": branch,
            "Gender": gender,
            "Customer type": customer_type,
        }

        for column, value in filters.items():
            if value and value != "All":
                filtered = filtered[filtered[column] == value]

        return filtered.reset_index(drop=True)

    @staticmethod
    def aggregate_sales_by_city(dataframe: pd.DataFrame) -> pd.Series:
        return dataframe.groupby("City")["Sales"].sum().sort_values(ascending=False)

    @staticmethod
    def aggregate_sales_by_product_line(dataframe: pd.DataFrame) -> pd.Series:
        return (
            dataframe.groupby("Product line")["Sales"]
            .sum()
            .sort_values(ascending=False)
        )

    @staticmethod
    def aggregate_quantity_by_product_line(dataframe: pd.DataFrame) -> pd.Series:
        return (
            dataframe.groupby("Product line")["Quantity"]
            .sum()
            .sort_values(ascending=True)
        )

    @staticmethod
    def aggregate_sales_trend(dataframe: pd.DataFrame) -> pd.Series:
        return dataframe.groupby("Date")["Sales"].sum().sort_index()

    @staticmethod
    def payment_distribution(dataframe: pd.DataFrame) -> pd.Series:
        return dataframe["Payment"].value_counts()

    @staticmethod
    def customer_type_distribution(dataframe: pd.DataFrame) -> pd.Series:
        return dataframe["Customer type"].value_counts()

    @staticmethod
    def summary_metrics(dataframe: pd.DataFrame) -> dict[str, Any]:
        if dataframe.empty:
            return {
                "total_revenue": 0.0,
                "total_transactions": 0,
                "average_rating": 0.0,
                "best_selling_product": "-",
            }

        best_selling = (
            dataframe.groupby("Product line")["Quantity"]
            .sum()
            .sort_values(ascending=False)
        )

        return {
            "total_revenue": float(dataframe["Sales"].sum()),
            "total_transactions": int(dataframe["Invoice ID"].nunique()),
            "average_rating": float(dataframe["Rating"].mean()),
            "best_selling_product": best_selling.index[0] if not best_selling.empty else "-",
        }
