import polars as pl
import polars.selectors as cs
from polars.testing import assert_frame_equal


def assert_frames_equivalent(actual: pl.DataFrame, expected: pl.DataFrame) -> None:
    """Compares two Polars DataFrames independently of row order and extra columns.

    Automatically identifies sortable columns (excludes List/Struct types).
    Float tolerance is enabled for numerical comparisons.

    Column filtering: only columns present in `expected` are checked in `actual`,
    allowing the pipeline to add extra columns without breaking tests.
    """
    # 1. Restrict actual to the expected columns only
    actual_aligned = actual.select(expected.columns)

    # 2. Dynamically extract sortable columns (List/Struct crash polars.sort)
    sort_cols = expected.select(~cs.by_dtype(pl.List, pl.Struct)).columns

    # 3. Sort both DataFrames to prevent order-based test flakiness
    actual_sorted = actual_aligned.sort(sort_cols)
    expected_sorted = expected.sort(sort_cols)

    # 4. Compare with float tolerance for numerical columns
    assert_frame_equal(actual_sorted, expected_sorted, check_exact=False)
