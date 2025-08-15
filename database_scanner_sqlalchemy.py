#!/usr/bin/env python3
"""
Nova versão do DatabaseScanner usando introspecção SQLAlchemy
"""
from typing import List, Dict, Any
from sqlalchemy import MetaData, create_engine, inspect
from sqlalchemy.exc import SQLAlchemyError
import pandas as pd
from config import DatabaseConfig
from models import DatabaseSchema, TableInfo, ColumnInfo, ForeignKeyInfo


class DatabaseScannerSQLAlchemy:
    """Scanner usando introspecção nativa do SQLAlchemy"""

    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.engine = create_engine(config.url)
        # Usar inspect() em vez do método deprecated
        self.inspector = inspect(self.engine)
        self.metadata = MetaData()

    def get_table_names(self) -> List[str]:
        """Return list of table names using SQLAlchemy introspection"""
        try:
            # Usar Inspector que é a forma oficial do SQLAlchemy
            return self.inspector.get_table_names()
        except SQLAlchemyError as e:
            raise RuntimeError(f"Error getting table names: {e}")

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
                # SQLAlchemy retorna foreign keys como lista de colunas
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
        
        # Verificar se a tabela existe usando introspection
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
            # Validar nome da tabela
            sanitized_table = self._sanitize_table_name(table_name)
            
            # Validar limit
            if not isinstance(limit, int) or limit <= 0:
                raise ValueError("Limit must be a positive integer")
            
            with self.engine.connect() as conn:
                # Usar SQLAlchemy Table object para construção segura
                from sqlalchemy import Table
                
                # Autoload da tabela usando metadados
                table_obj = Table(
                    sanitized_table,
                    self.metadata,
                    autoload_with=conn
                )
                
                # Construir query usando SQLAlchemy Core (100% seguro)
                query = table_obj.select().limit(limit)
                
                return pd.read_sql(query, conn)
                
        except SQLAlchemyError as e:
            raise RuntimeError(f"Error querying table {table_name}: {e}")

    def get_table_stats(self, table_name: str) -> Dict[str, Any]:
        """Get table statistics using SQLAlchemy"""
        try:
            sanitized_table = self._sanitize_table_name(table_name)
            
            with self.engine.connect() as conn:
                from sqlalchemy import Table, func
                
                table_obj = Table(
                    sanitized_table,
                    self.metadata,
                    autoload_with=conn
                )
                
                # Count usando SQLAlchemy
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


def test_new_scanner():
    """Teste da nova implementação"""
    print("=== TESTE DO NOVO SCANNER SQLALCHEMY ===\n")
    
    from config import DatabaseConfig
    from dotenv import load_dotenv
    import os
    
    load_dotenv()
    
    # Configurar database
    db_config = DatabaseConfig(
        url=os.getenv("DATABASE_URL", "sqlite:///test.db"),
        type=os.getenv("DATABASE_TYPE", "sqlite")
    )
    
    scanner = DatabaseScannerSQLAlchemy(db_config)
    
    try:
        print("1. Listando tabelas...")
        tables = scanner.get_table_names()
        print(f"   Encontradas {len(tables)} tabelas: {tables}")
        
        print("\n2. Escaneando schema completo...")
        schema = scanner.scan_database()
        print(f"   Schema escaneado com {len(schema.tables)} tabelas")
        
        for table in schema.tables[:2]:  # Mostrar apenas 2 primeiras
            print(f"\n   Tabela: {table.name}")
            print(f"   - Colunas: {len(table.columns)}")
            print(f"   - Primary Keys: {table.primary_keys}")
            print(f"   - Foreign Keys: {len(table.foreign_keys)}")
        
        print("\n3. Testando query de sample...")
        if tables:
            first_table = tables[0]
            sample = scanner.query_table_sample(first_table, limit=3)
            print(f"   Sample de {first_table}: {len(sample)} linhas")
            
        print("\n4. Testando estatísticas...")
        if tables:
            stats = scanner.get_table_stats(first_table)
            print(f"   Estatísticas de {first_table}:")
            print(f"   - Linhas: {stats['row_count']}")
            print(f"   - Colunas: {stats['column_count']}")
        
        print("\n✅ TESTE CONCLUÍDO COM SUCESSO!")
        
    except Exception as e:
        print(f"\n❌ ERRO NO TESTE: {e}")


if __name__ == "__main__":
    test_new_scanner()
