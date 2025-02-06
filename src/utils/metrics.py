"""Prometheus metrics configuration."""

from prometheus_client import Counter

# Counter for table creation operations
table_creation_counter = Counter(
    "duckdb_table_creations_total",
    "Total number of DuckDB tables created",
    ["status"],  # 'success' or 'failed'
)
