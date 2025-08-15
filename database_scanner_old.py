"""
Database scanner for metadata extraction
"""
from typing import List, Dict  # removed unused Any
from sqlalchemy import create_engine, text  # removed unused Engine
from sqlalchemy.exc import SQLAlchemyError
import pandas as pd

from models import DatabaseSchema, TableInfo, ColumnInfo, ForeignKeyInfo
from config import DatabaseConfig


class DatabaseScanner:
    """Scans and extracts database metadata"""

    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.engine = create_engine(config.url)
        self._schema_queries = self._get_schema_queries()

    def _get_schema_queries(self) -> Dict[str, str]:
        """Return DB-specific schema queries"""
        queries = {
            "postgresql": (
                """
                SELECT
                    t.table_name,
                    c.column_name,
                    c.data_type,
                    c.is_nullable,
                    CASE
                        WHEN tc.constraint_type = 'PRIMARY KEY'
                            THEN 'PRIMARY KEY'
                        WHEN tc.constraint_type = 'FOREIGN KEY'
                            THEN 'FOREIGN KEY'
                        ELSE NULL
                    END as constraint_type,
                    CASE
                        WHEN tc.constraint_type = 'PRIMARY KEY'
                            THEN c.column_name
                        ELSE NULL
                    END as pk_column,
                    CASE
                        WHEN tc.constraint_type = 'FOREIGN KEY'
                            THEN ccu.table_name
                        ELSE NULL
                    END as fk_ref_table,
                    CASE
                        WHEN tc.constraint_type = 'FOREIGN KEY'
                            THEN ccu.column_name
                        ELSE NULL
                    END as fk_ref_column,
                    c.ordinal_position AS ordinal_position
                FROM information_schema.tables t
                LEFT JOIN information_schema.columns c
                    ON t.table_name = c.table_name
                    AND t.table_schema = c.table_schema
                LEFT JOIN information_schema.key_column_usage kcu
                    ON t.table_name = kcu.table_name
                    AND c.column_name = kcu.column_name
                    AND t.table_schema = kcu.table_schema
                LEFT JOIN information_schema.table_constraints tc
                    ON kcu.constraint_name = tc.constraint_name
                    AND kcu.table_schema = tc.table_schema
                LEFT JOIN information_schema.constraint_column_usage ccu
                    ON tc.constraint_name = ccu.constraint_name
                    AND tc.table_schema = ccu.table_schema
                WHERE t.table_schema = 'public'
                    AND t.table_type = 'BASE TABLE'
                ORDER BY t.table_name, c.ordinal_position
                """
            ),
            "mysql": (
                """
                SELECT DISTINCT
                    t.table_name,
                    c.column_name,
                    c.data_type,
                    c.is_nullable,
                    CASE
                        WHEN kcu.constraint_name = 'PRIMARY'
                            THEN 'PRIMARY KEY'
                        WHEN tc.constraint_type = 'FOREIGN KEY'
                            THEN 'FOREIGN KEY'
                        ELSE NULL
                    END as constraint_type,
                    CASE
                        WHEN kcu.constraint_name = 'PRIMARY'
                            THEN c.column_name
                        ELSE NULL
                    END as pk_column,
                    kcu.referenced_table_name as fk_ref_table,
                    kcu.referenced_column_name as fk_ref_column
                FROM information_schema.tables t
                LEFT JOIN information_schema.columns c
                    ON t.table_name = c.table_name
                    AND t.table_schema = c.table_schema
                LEFT JOIN information_schema.key_column_usage kcu
                    ON t.table_name = kcu.table_name
                    AND c.column_name = kcu.column_name
                    AND t.table_schema = kcu.table_schema
                LEFT JOIN information_schema.table_constraints tc
                    ON kcu.constraint_name = tc.constraint_name
                    AND kcu.table_schema = tc.table_schema
                WHERE t.table_schema = DATABASE()
                    AND t.table_type = 'BASE TABLE'
                ORDER BY t.table_name, c.ordinal_position
                """
            ),
            "sqlite": (
                """
                SELECT
                    m.name as table_name,
                    p.name as column_name,
                    p.type as data_type,
                    CASE WHEN p."notnull" = 0 THEN 'YES' ELSE 'NO' END
                        as is_nullable,
                    CASE WHEN p.pk = 1 THEN 'PRIMARY KEY' ELSE NULL END
                        as constraint_type,
                    CASE WHEN p.pk = 1 THEN p.name ELSE NULL END
                        as pk_column,
                    NULL as fk_ref_table,
                    NULL as fk_ref_column
                FROM sqlite_master m
                LEFT JOIN pragma_table_info(m.name) p
                WHERE m.type = 'table'
                    AND m.name NOT LIKE 'sqlite_%'
                ORDER BY m.name, p.cid
                """
            ),
        }
        return queries

    def get_table_names(self) -> List[str]:
        """Return list of table names"""
        try:
            with self.engine.connect() as conn:
                if self.config.type == "sqlite":
                    query = (
                        """
                        SELECT name FROM sqlite_master
                        WHERE type = 'table' AND name NOT LIKE 'sqlite_%'
                        """
                    )
                else:
                    query = (
                        """
                        SELECT table_name
                        FROM information_schema.tables
                        WHERE table_type = 'BASE TABLE'
                        """
                    )
                    if self.config.type == "postgresql":
                        query += " AND table_schema = 'public'"
                    elif self.config.type == "mysql":
                        query += " AND table_schema = DATABASE()"
                result = conn.execute(text(query))
                return [row[0] for row in result.fetchall()]
        except SQLAlchemyError as e:
            raise RuntimeError(f"Error getting table names: {e}")

    def scan_database(self) -> DatabaseSchema:
        """Scan the database and return full schema"""
        if self.config.type not in self._schema_queries:
            raise ValueError(f"Unsupported DB type: {self.config.type}")
        query = self._schema_queries[self.config.type]
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(query))
                rows = result.fetchall()
        except SQLAlchemyError as e:
            raise RuntimeError(f"Error scanning database: {e}")
        # Organize data by table
        tables_data: Dict[str, Dict] = {}
        for row in rows:
            table_name = row[0]
            if table_name not in tables_data:
                tables_data[table_name] = {
                    "columns": {},
                    "primary_keys": set(),
                    "foreign_keys": [],
                }
            column_name = row[1]
            if (
                column_name
                and column_name not in tables_data[table_name]["columns"]
            ):
                tables_data[table_name]["columns"][column_name] = ColumnInfo(
                    name=column_name,
                    data_type=row[2] or "unknown",
                    is_nullable=row[3] == "YES",
                    is_primary_key=row[4] == "PRIMARY KEY",
                )
            if row[4] == "PRIMARY KEY" and row[5]:
                tables_data[table_name]["primary_keys"].add(row[5])
            if (
                row[4] == "FOREIGN KEY" and row[6] and row[7] and row[1]
            ):  # fk_ref_table, fk_ref_column, column
                fk = ForeignKeyInfo(
                    column=row[1],
                    references_table=row[6],
                    references_column=row[7],
                )
                if fk not in tables_data[table_name]["foreign_keys"]:
                    tables_data[table_name]["foreign_keys"].append(fk)
        # Convert to TableInfo objects
        tables: List[TableInfo] = []
        for table_name, data in tables_data.items():
            table = TableInfo(
                name=table_name,
                columns=list(data["columns"].values()),
                primary_keys=list(data["primary_keys"]),
                foreign_keys=data["foreign_keys"],
            )
            tables.append(table)
        return DatabaseSchema(tables=tables)

    def _sanitize_table_name(self, table_name: str) -> str:
        """Validate and sanitize table name to prevent SQL injection"""
        if not table_name or not isinstance(table_name, str):
            raise ValueError("Table name must be a non-empty string")
        
        # Remove espaços em branco
        table_name = table_name.strip()
        
        if not table_name:
            raise ValueError("Table name must be a non-empty string")
        
        # Verificar se contém caracteres perigosos
        dangerous_chars = [";", "--", "/*", "*/", "'", '"', "\\", "\n", "\r", "\t"]
        for char in dangerous_chars:
            if char in table_name:
                raise ValueError(f"Table name contém caracteres inválidos: {char}")
        
        # Verificar se a tabela existe na base de dados
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
        """Return a sample of table data"""
        try:
            # Validar e sanitizar o nome da tabela
            try:
                sanitized_table = self._sanitize_table_name(table_name)
            except ValueError as e:
                raise ValueError(f"Erro de validação: {e}")
            
            # Validar limit
            if not isinstance(limit, int) or limit <= 0:
                raise ValueError("Limit must be a positive integer")
            
            # Usar identifier para escapar nomes de tabela de forma segura
            # Note: Para SQLAlchemy, usamos text() com bind parameters seguros
            with self.engine.connect() as conn:
                # Para nomes de tabela, usamos quoted identifier do SQLAlchemy
                # que é seguro contra SQL injection
                from sqlalchemy import MetaData, Table
                metadata = MetaData()
                
                # Carregar a definição da tabela de forma segura
                try:
                    table_obj = Table(sanitized_table, metadata, autoload_with=conn)
                    # Construir query usando SQLAlchemy Core (seguro)
                    query = table_obj.select().limit(limit)
                    return pd.read_sql(query, conn)
                except Exception:
                    # Fallback usando quoted identifier manual (ainda seguro)
                    # Usar aspas para escapar o identifier
                    quoted_table = f'"{sanitized_table}"' if self.config.type == "postgresql" else f"`{sanitized_table}`"
                    query = text(f"SELECT * FROM {quoted_table} LIMIT :limit")
                    return pd.read_sql(query, conn, params={"limit": limit})
                    
        except SQLAlchemyError as e:
            raise RuntimeError(f"Error querying table {table_name}: {e}")

    def close(self):
        """Dispose SQLAlchemy engine"""
        if hasattr(self, "engine"):
            self.engine.dispose()
