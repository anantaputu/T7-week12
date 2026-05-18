from __future__ import annotations

from pathlib import Path

import pandas as pd


class DataLoaderError(Exception):
    """Akan di panggil ketika dataset tidak dapat di load atau valid"""


class DataLoader:

    REQUIRED_COLUMNS = [
        "Invoice ID",
        "Branch",
        "City",
        "Customer type",
        "Gender",
        "Product line",
        "Unit price",
        "Quantity",
        "Tax 5%",
        "Sales",
        "Date",
        "Time",
        "Payment",
        "cogs",
        "gross income",
        "Rating",
    ]

    NUMERIC_COLUMNS = [
        "Unit price",
        "Quantity",
        "Tax 5%",
        "Sales",
        "cogs",
        "gross margin percentage",
        "gross income",
        "Rating",
    ]

    @classmethod
    def load_data(cls, file_path: str | Path) -> pd.DataFrame:
        path = Path(file_path)
        if not path.exists():
            raise DataLoaderError(f"CSV file not found: {path}")

        try:
            dataframe = pd.read_csv(path, encoding="utf-8-sig")
        except Exception as error:
            raise DataLoaderError(f"Failed to read CSV file: {error}") from error

        if dataframe.empty:
            raise DataLoaderError("Dataset is empty.")

        missing_columns = [
            column for column in cls.REQUIRED_COLUMNS if column not in dataframe.columns
        ]
        if missing_columns:
            raise DataLoaderError(
                "Invalid CSV format. Missing columns: "
                + ", ".join(missing_columns)
            )

        for column in cls.NUMERIC_COLUMNS:
            if column in dataframe.columns:
                dataframe[column] = pd.to_numeric(
                    dataframe[column], errors="coerce"
                )

        dataframe["Date"] = pd.to_datetime(dataframe["Date"], errors="coerce")
        dataframe["Time"] = dataframe["Time"].astype(str)

        if dataframe["Date"].isna().all():
            raise DataLoaderError("Date column could not be parsed.")

        dataframe = dataframe.dropna(subset=["Date"]).reset_index(drop=True)
        if dataframe.empty:
            raise DataLoaderError("Dataset has no valid rows after parsing.")

        return dataframe
