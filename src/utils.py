"""
Generic, stateless operations live here, isolated from any business logic.
They are independently unit-tested and reusable across modules.

If this file grows too large, split into utils/text.py, utils/validation.py, etc.
"""

import functools
import logging
import time
from collections.abc import Callable
from typing import Any, TypeVar

import polars as pl
from pydantic import BaseModel, ValidationError

T = TypeVar("T", bound=BaseModel)

_DEFAULT_LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
_DEFAULT_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logging(level: int = logging.INFO) -> None:
    """
    Configures the root logger with a standard format.

    Call once at the top of run.py before instantiating any pipeline.

    Parameters
    ----------
    level:
        Logging level. Defaults to logging.INFO.
    """
    logging.basicConfig(
        level=level,
        format=_DEFAULT_LOG_FORMAT,
        datefmt=_DEFAULT_DATE_FORMAT,
    )


def timer(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    Logs the execution time of a function at DEBUG level.

    Logs to the logger of the module where the decorated function is defined,
    so log output is clearly attributed to the right file.
    """

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        module_logger = logging.getLogger(func.__module__)
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        module_logger.debug(f"[{func.__name__}] {elapsed:.3f}s")
        return result

    return wrapper


def log_df_info(df: pl.DataFrame, name: str = "df") -> None:
    """
    Logs shape and column info for a DataFrame at DEBUG level.

    Useful for quick sanity checks inside node functions or modules
    without adding print statements.

    Parameters
    ----------
    df:
        DataFrame to inspect.
    name:
        Label used in the log message. Defaults to "df".
    """
    module_logger = logging.getLogger(__name__)
    col_info = ", ".join(
        f"{col} ({dtype})" for col, dtype in zip(df.columns, df.dtypes, strict=True)
    )
    module_logger.debug(
        f"[{name}] shape=({df.height}, {df.width}) | columns: {col_info}"
    )


def normalize_text(column_name: str) -> pl.Expr:
    """
    Returns a Polars expr that lowercases and strips whitespace from a string column.

    Parameters
    ----------
    column_name:
        Name of the column to normalize.
    """
    return pl.col(column_name).str.to_lowercase().str.strip_chars()


def validate_rows(
    df: pl.DataFrame, schema: type[T]
) -> tuple[pl.DataFrame, list[dict[str, Any]]]:
    """
    Validates each row of a Polars DataFrame against a Pydantic schema.

    Automatically selects only the columns defined in the schema.
    Raises ValueError if columns required by the schema are missing from the DataFrame.
    Returns (valid_df, rejected_rows) -- invalid rows are never silently dropped.

    Parameters
    ----------
    df:
        Input DataFrame to validate.
    schema:
        Pydantic model class to validate each row against.

    Returns
    -------
    tuple[pl.DataFrame, list[dict[str, Any]]]
        A tuple of (valid_df, rejected_rows). valid_df contains only rows
        that passed validation. rejected_rows contains dicts with the
        original row and the Pydantic validation errors.

    Raises
    ------
    ValueError
        If the DataFrame is missing columns required by the schema.
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

    # 3. Re-create a clean Polars DataFrame from valid rows.
    # If no rows are valid, return an empty DataFrame preserving the expected schema.
    if valid_dicts:
        valid_df = pl.DataFrame(valid_dicts)
    else:
        valid_df = pl.DataFrame(
            schema={k: df_filtered.schema[k] for k in schema_columns}
        )

    return valid_df, rejected
