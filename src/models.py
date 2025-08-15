"""
Data models for the database RAG system
"""
from dataclasses import dataclass
from typing import List, Dict, Any, Optional


@dataclass
class ColumnInfo:
    """Database column information"""
    name: str
    data_type: str
    is_nullable: bool
    is_primary_key: bool = False


@dataclass
class ForeignKeyInfo:
    """Foreign key information"""
    column: str
    references_table: str
    references_column: str


@dataclass
class TableInfo:
    """Database table information"""
    name: str
    columns: List[ColumnInfo]
    primary_keys: List[str]
    foreign_keys: List[ForeignKeyInfo]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to plain dictionary"""
        return {
            "name": self.name,
            "columns": [
                {
                    "name": col.name,
                    "type": col.data_type,
                    "nullable": col.is_nullable,
                    "primary_key": col.is_primary_key,
                }
                for col in self.columns
            ],
            "primary_keys": self.primary_keys,
            "foreign_keys": [
                {
                    "column": fk.column,
                    "references_table": fk.references_table,
                    "references_column": fk.references_column,
                }
                for fk in self.foreign_keys
            ],
        }


@dataclass
class DatabaseSchema:
    """Complete database schema representation"""
    tables: List[TableInfo]

    def get_table(self, table_name: str) -> Optional[TableInfo]:
        """Return a specific table metadata if exists"""
        for table in self.tables:
            if table.name == table_name:
                return table
        return None

    def get_table_names(self) -> List[str]:
        """Return all table names"""
        return [table.name for table in self.tables]

    def to_text(self) -> str:
        """Render schema as human-readable text"""
        schema_parts = []
        for table in self.tables:
            schema_parts.append(f"Table: {table.name}")
            schema_parts.append("Columns:")
            for col in table.columns:
                pk_marker = " (PK)" if col.is_primary_key else ""
                nullable = "nullable" if col.is_nullable else "not null"
                schema_parts.append(
                    f"  - {col.name} ({col.data_type}, {nullable}){pk_marker}"
                )
            if table.primary_keys:
                schema_parts.append(
                    f"Primary Keys: {', '.join(table.primary_keys)}"
                )
            if table.foreign_keys:
                schema_parts.append("Foreign Keys:")
                for fk in table.foreign_keys:
                    schema_parts.append(
                        f"  - {fk.column} -> {fk.references_table}."
                        f"{fk.references_column}"
                    )
            schema_parts.append("")
        return "\n".join(schema_parts)
