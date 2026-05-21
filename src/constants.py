"""
Data pipelines fail silently when upstream column names change.
If `productID` becomes `product_id`, searching and replacing across 15 files
is error-prone. By centralizing field names as constants (`c.PRODUCT_ID = "productID"`),
a schema change is a single-line fix — and the entire codebase follows naturally.

If this file exceeds ~100 lines or mixes too many responsibilities, consider
splitting into constants.py (field name mappings) and schemas.py (Pydantic models).
"""
