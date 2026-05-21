"""
Generic, stateless operations live here, isolated from any business logic.
They are independently unit-tested and reusable across modules.

If this file grows too large, split into utils/text.py, utils/validation.py, etc.
"""

from typing import Any, TypeVar

import polars as pl
from pydantic import BaseModel, ValidationError

T = TypeVar("T", bound=BaseModel)


def normalize_text(column_name: str) -> pl.Expr:
    """
    Returns a Polars expression that lowercases and strips whitespace from a string col.
    """
    return pl.col(column_name).str.to_lowercase().str.strip_chars()


def validate_rows(
    df: pl.DataFrame, schema: type[T]
) -> tuple[pl.DataFrame, list[dict[str, Any]]]:
    """Validates each row of a Polars DataFrame against a Pydantic schema.

    Automatically selects only the columns defined in the schema.
    Raises ValueError if columns required by the schema are missing from the DataFrame.
    Returns (valid_df, rejected_rows) — invalid rows are never silently dropped.
    """
    valid_dicts: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []

    # Fail fast if columns are missing
    schema_columns = set(schema.model_fields.keys())
    available_columns = set(df.columns)
    missing_columns = schema_columns - available_columns
    if missing_columns:
        raise ValueError(
            f"DataFrame is missing columns required by {schema.__name__}: "
            f"{missing_columns}. Available: {available_columns}"
        )

    df_filtered = df.select(list(schema_columns))

    for row in df_filtered.to_dicts():
        try:
            # 1. Validate and clean via Pydantic
            validated_model = schema(**row)

            # 2. Dump back to dict (handles defaults and type coercions)
            valid_dicts.append(validated_model.model_dump())
        except ValidationError as e:
            rejected.append({"row": row, "errors": e.errors()})

    # 3. Re-create a clean Polars DataFrame from valid rows
    # If no rows are valid, return an empty DataFrame preserving the expected schema
    if valid_dicts:
        valid_df = pl.DataFrame(valid_dicts)
    else:
        valid_df = pl.DataFrame(
            schema={k: df_filtered.schema[k] for k in schema_columns}
        )

    return valid_df, rejected
