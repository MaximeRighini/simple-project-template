"""
Hardcoding environment parameters (file paths, feature flags, credentials) breaks
pipelines when switching contexts. `config.py` handles multi-environment
configurations — local, staging, prod, or country-specific variants.

Core logic never reads environment variables directly; it uses the config module.
"""
