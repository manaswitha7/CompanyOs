from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd


class StructuredDataService:
    """
    Service for ingesting and querying structured data.

    Supported:
    - CSV
    - Excel / XLSX
    - JSON

    The service provides:
    - file inspection
    - table/schema detection
    - filtering
    - aggregation
    - simple natural-language-style operations
    """

    SUPPORTED_EXTENSIONS = {
        ".csv",
        ".xlsx",
        ".xls",
        ".json",
    }

    # ---------------------------------------------------------
    # FILE LOADING
    # ---------------------------------------------------------

    def load_file(
        self,
        file_path: str,
        sheet_name: str | None = None,
    ) -> pd.DataFrame:
        """
        Load a structured file into a pandas DataFrame.
        """

        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(
                f"File not found: {file_path}"
            )

        extension = path.suffix.lower()

        if extension not in self.SUPPORTED_EXTENSIONS:
            raise ValueError(
                f"Unsupported file type: {extension}"
            )

        if extension == ".csv":
            return pd.read_csv(path)

        if extension in {".xlsx", ".xls"}:
            return pd.read_excel(
                path,
                sheet_name=sheet_name or 0,
            )

        if extension == ".json":
            with open(
                path,
                "r",
                encoding="utf-8",
            ) as file:
                data = json.load(file)

            if isinstance(data, list):
                return pd.DataFrame(data)

            if isinstance(data, dict):
                return pd.DataFrame(data)

            raise ValueError(
                "JSON must contain an object or array."
            )

        raise ValueError(
            f"Unsupported file type: {extension}"
        )

    # ---------------------------------------------------------
    # SCHEMA
    # ---------------------------------------------------------

    def get_schema(
        self,
        file_path: str,
        sheet_name: str | None = None,
    ) -> dict[str, Any]:
        """
        Return information about the structured dataset.
        """

        df = self.load_file(
            file_path,
            sheet_name,
        )

        columns = []

        for column in df.columns:
            series = df[column]

            columns.append(
                {
                    "name": str(column),
                    "dtype": str(series.dtype),
                    "nullable": bool(
                        series.isna().any()
                    ),
                    "unique_values": int(
                        series.nunique(
                            dropna=True
                        )
                    ),
                }
            )

        return {
            "rows": int(len(df)),
            "columns": int(len(df.columns)),
            "column_details": columns,
        }

    # ---------------------------------------------------------
    # PREVIEW
    # ---------------------------------------------------------

    def preview(
        self,
        file_path: str,
        limit: int = 20,
        sheet_name: str | None = None,
    ) -> dict[str, Any]:
        """
        Return a preview of the dataset.
        """

        if limit < 1:
            limit = 1

        if limit > 100:
            limit = 100

        df = self.load_file(
            file_path,
            sheet_name,
        )

        data = (
            df.head(limit)
            .where(pd.notnull(df.head(limit)), None)
            .to_dict(orient="records")
        )

        return {
            "rows": int(len(df)),
            "columns": [
                str(column)
                for column in df.columns
            ],
            "preview": data,
        }

    # ---------------------------------------------------------
    # FILTER
    # ---------------------------------------------------------

    def filter_data(
        self,
        file_path: str,
        filters: dict[str, Any],
        sheet_name: str | None = None,
        limit: int = 100,
    ) -> dict[str, Any]:
        """
        Filter rows using exact-match filters.

        Example:

        {
            "department": "Engineering",
            "status": "active"
        }
        """

        df = self.load_file(
            file_path,
            sheet_name,
        )

        for column, value in filters.items():

            if column not in df.columns:
                raise ValueError(
                    f"Column not found: {column}"
                )

            df = df[
                df[column].astype(str)
                == str(value)
            ]

        result = (
            df.head(limit)
            .where(pd.notnull(df.head(limit)), None)
            .to_dict(orient="records")
        )

        return {
            "count": int(len(df)),
            "results": result,
        }

    # ---------------------------------------------------------
    # SEARCH
    # ---------------------------------------------------------

    def search(
        self,
        file_path: str,
        query: str,
        sheet_name: str | None = None,
        limit: int = 50,
    ) -> dict[str, Any]:
        """
        Search across all columns for a text query.
        """

        df = self.load_file(
            file_path,
            sheet_name,
        )

        query = query.lower().strip()

        if not query:
            return {
                "count": 0,
                "results": [],
            }

        mask = df.astype(str).apply(
            lambda column: column.str.lower()
            .str.contains(
                query,
                na=False,
            )
        ).any(axis=1)

        results_df = df[mask].head(limit)

        results = (
            results_df
            .where(pd.notnull(results_df), None)
            .to_dict(orient="records")
        )

        return {
            "count": int(mask.sum()),
            "results": results,
        }

    # ---------------------------------------------------------
    # AGGREGATION
    # ---------------------------------------------------------

    def aggregate(
        self,
        file_path: str,
        column: str,
        operation: str,
        sheet_name: str | None = None,
    ) -> dict[str, Any]:
        """
        Perform an aggregation.

        Supported:
        - sum
        - average
        - min
        - max
        - count
        """

        df = self.load_file(
            file_path,
            sheet_name,
        )

        if column not in df.columns:
            raise ValueError(
                f"Column not found: {column}"
            )

        operation = operation.lower().strip()

        series = pd.to_numeric(
            df[column],
            errors="coerce",
        )

        if operation == "sum":
            value = series.sum()

        elif operation in {
            "average",
            "avg",
            "mean",
        }:
            value = series.mean()

        elif operation == "min":
            value = series.min()

        elif operation == "max":
            value = series.max()

        elif operation == "count":
            value = df[column].count()

        else:
            raise ValueError(
                f"Unsupported operation: {operation}"
            )

        if pd.isna(value):
            value = None
        else:
            value = float(value)

        return {
            "column": column,
            "operation": operation,
            "value": value,
        }

    # ---------------------------------------------------------
    # GROUP BY
    # ---------------------------------------------------------

    def group_by(
        self,
        file_path: str,
        group_column: str,
        aggregation_column: str,
        operation: str = "sum",
        sheet_name: str | None = None,
    ) -> dict[str, Any]:
        """
        Group records and aggregate a numeric column.
        """

        df = self.load_file(
            file_path,
            sheet_name,
        )

        if group_column not in df.columns:
            raise ValueError(
                f"Column not found: {group_column}"
            )

        if aggregation_column not in df.columns:
            raise ValueError(
                f"Column not found: {aggregation_column}"
            )

        operation = operation.lower()

        numeric_column = pd.to_numeric(
            df[aggregation_column],
            errors="coerce",
        )

        df = df.copy()

        df["_numeric_value"] = numeric_column

        if operation == "sum":
            grouped = (
                df.groupby(group_column)["_numeric_value"]
                .sum()
            )

        elif operation in {
            "average",
            "avg",
            "mean",
        }:
            grouped = (
                df.groupby(group_column)["_numeric_value"]
                .mean()
            )

        elif operation == "count":
            grouped = (
                df.groupby(group_column)["_numeric_value"]
                .count()
            )

        elif operation == "min":
            grouped = (
                df.groupby(group_column)["_numeric_value"]
                .min()
            )

        elif operation == "max":
            grouped = (
                df.groupby(group_column)["_numeric_value"]
                .max()
            )

        else:
            raise ValueError(
                f"Unsupported operation: {operation}"
            )

        results = []

        for key, value in grouped.items():

            results.append(
                {
                    "group": key,
                    "value": (
                        None
                        if pd.isna(value)
                        else float(value)
                    ),
                }
            )

        return {
            "group_by": group_column,
            "column": aggregation_column,
            "operation": operation,
            "results": results,
        }


structured_data_service = StructuredDataService()
