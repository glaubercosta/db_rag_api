"""
Database scanner for extracting metadata from different database systems.
Refactored to use SQLAlchemy introspection instead of manual SQL queries.
"""
from typing import List, Dict, Any
from sqlalchemy import MetaData, create_engine, inspect, Table, func
from sqlalchemy.exc import SQLAlchemyError
import pandas as pd
from config import DatabaseConfig
from models import DatabaseSchema, TableInfo, ColumnInfo, ForeignKeyInfo


class DatabaseScanner:
    """Database scanner using SQLAlchemy introspection"""

    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.engine = create_engine(config.url)
        # Use inspect() instead of deprecated Inspector.from_engine()
        self.inspector = inspect(self.engine)
        self.metadata = MetaData()
        # Cache table names to avoid repeated introspection calls
        self._cached_table_names = None

    def get_table_names(self) -> List[str]:
        """Return list of table names using SQLAlchemy introspection"""
        if self._cached_table_names is None:
            try:
                self._cached_table_names = self.inspector.get_table_names()
            except SQLAlchemyError as e:
                raise RuntimeError(f"Error getting table names: {e}")
        return self._cached_table_names

    def _invalidate_table_cache(self):
        """Invalidate cached table names (useful if schema changes)"""
        self._cached_table_names = None

    def refresh_schema(self):
        """Refresh schema information by invalidating caches"""
        self._invalidate_table_cache()
        # Force reload of metadata
        self.metadata.clear()
        return self.get_table_names()

    def _get_column_info(self, table_name: str) -> List[ColumnInfo]:
        """Get column information using SQLAlchemy introspection"""
        try:
            columns = self.inspector.get_columns(table_name)
            pk_constraint = self.inspector.get_pk_constraint(table_name)
            pk_columns = set(pk_constraint.get('constrained_columns', []))
            
            column_info_list = []
            for col in columns:
                column_info = ColumnInfo(
                    name=col['name'],
                    data_type=str(col['type']),
                    is_nullable=col['nullable'],
                    is_primary_key=col['name'] in pk_columns
                )
                column_info_list.append(column_info)
            
            return column_info_list
        except SQLAlchemyError as e:
            raise RuntimeError(f"Error getting columns for {table_name}: {e}")

    def _get_primary_keys(self, table_name: str) -> List[str]:
        """Get primary key columns using SQLAlchemy introspection"""
        try:
            pk_constraint = self.inspector.get_pk_constraint(table_name)
            return pk_constraint.get('constrained_columns', [])
        except SQLAlchemyError as e:
            raise RuntimeError(
                f"Error getting primary keys for {table_name}: {e}"
            )

    def _get_foreign_keys(self, table_name: str) -> List[ForeignKeyInfo]:
        """Get foreign key information using SQLAlchemy introspection"""
        try:
            fk_constraints = self.inspector.get_foreign_keys(table_name)
            foreign_keys = []
            
            for fk in fk_constraints:
                # SQLAlchemy returns foreign keys as list of columns
                for i, col in enumerate(fk['constrained_columns']):
                    fk_info = ForeignKeyInfo(
                        column=col,
                        references_table=fk['referred_table'],
                        references_column=fk['referred_columns'][i]
                    )
                    foreign_keys.append(fk_info)
            
            return foreign_keys
        except SQLAlchemyError as e:
            raise RuntimeError(
                f"Error getting foreign keys for {table_name}: {e}"
            )

    def scan_database(self) -> DatabaseSchema:
        """Scan database using SQLAlchemy introspection"""
        try:
            table_names = self.get_table_names()
            tables = []
            
            for table_name in table_names:
                columns = self._get_column_info(table_name)
                primary_keys = self._get_primary_keys(table_name)
                foreign_keys = self._get_foreign_keys(table_name)
                
                table = TableInfo(
                    name=table_name,
                    columns=columns,
                    primary_keys=primary_keys,
                    foreign_keys=foreign_keys
                )
                tables.append(table)
            
            return DatabaseSchema(tables=tables)
            
        except SQLAlchemyError as e:
            raise RuntimeError(f"Error scanning database: {e}")

    def _sanitize_table_name(self, table_name: str) -> str:
        """Validate table name against known tables"""
        if not table_name or not isinstance(table_name, str):
            raise ValueError("Table name must be a non-empty string")
        
        table_name = table_name.strip()
        if not table_name:
            raise ValueError("Table name must be a non-empty string")
        
        # Verify table exists using introspection (safer than manual queries)
        try:
            valid_tables = self.get_table_names()
            if table_name not in valid_tables:
                raise ValueError(f"Invalid table: {table_name}")
        except Exception as e:
            raise ValueError(f"Error validating table: {e}")
        
        return table_name

    def query_table_sample(
        self, table_name: str, limit: int = 100
    ) -> pd.DataFrame:
        """Return a sample of table data using SQLAlchemy Table object"""
        try:
            # Validate table name
            sanitized_table = self._sanitize_table_name(table_name)
            
            # Validate limit
            if not isinstance(limit, int) or limit <= 0:
                raise ValueError("Limit must be a positive integer")
            
            with self.engine.connect() as conn:
                # Use SQLAlchemy Table object for safe construction
                table_obj = Table(
                    sanitized_table,
                    self.metadata,
                    autoload_with=conn
                )
                
                # Build query using SQLAlchemy Core (100% safe)
                query = table_obj.select().limit(limit)
                
                return pd.read_sql(query, conn)
                
        except SQLAlchemyError as e:
            raise RuntimeError(f"Error querying table {table_name}: {e}")

    def get_table_stats(self, table_name: str) -> Dict[str, Any]:
        """Get table statistics using SQLAlchemy"""
        try:
            sanitized_table = self._sanitize_table_name(table_name)
            
            with self.engine.connect() as conn:
                table_obj = Table(
                    sanitized_table,
                    self.metadata,
                    autoload_with=conn
                )
                
                # Count using SQLAlchemy
                count_query = table_obj.select().with_only_columns(
                    func.count().label('total_rows')
                )
                
                result = conn.execute(count_query)
                row_count = result.scalar()
                
                return {
                    'table_name': sanitized_table,
                    'row_count': row_count,
                    'column_count': len(table_obj.columns)
                }
                
        except SQLAlchemyError as e:
            raise RuntimeError(f"Error getting stats for {table_name}: {e}")

    def close(self):
        """Dispose SQLAlchemy engine and clear caches"""
        if hasattr(self, "engine"):
            self.engine.dispose()
        self._invalidate_table_cache()
