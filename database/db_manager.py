"""
Gerenciador de conexão e operações com o banco de dados SQLite.
"""

import sqlite3
import os
from pathlib import Path


class DatabaseManager:
    """Gerencia a conexão e operações com o banco de dados SQLite."""
    
    def __init__(self, db_path='biblioteca.db'):
        """
        Inicializa o gerenciador do banco de dados.
        
        Args:
            db_path: Caminho para o arquivo do banco de dados
        """
        self.db_path = db_path
        self.connection = None
        self._connect()
    
    def _connect(self):
        """Estabelece conexão com o banco de dados."""
        try:
            # Adiciona um timeout para evitar erros 'database is locked' quando múltiplas
            # conexões tentam escrever concorrentemente durante os testes.
            # Habilita também o WAL (Write-Ahead Logging) para melhorar concorrência.
            self.connection = sqlite3.connect(self.db_path, timeout=30.0)
            try:
                self.connection.execute('PRAGMA journal_mode = WAL')
            except sqlite3.Error:
                # Se o PRAGMA não puder ser aplicado, não interrompemos a execução
                pass
            self.connection.row_factory = sqlite3.Row  # Permite acesso por nome de coluna
            # Habilitar foreign keys
            self.connection.execute("PRAGMA foreign_keys = ON")
        except sqlite3.Error as e:
            raise Exception(f"Erro ao conectar ao banco de dados: {e}")
    
    def get_connection(self):
        """Retorna a conexão ativa com o banco de dados."""
        if self.connection is None:
            self._connect()
        return self.connection
    
    def close(self):
        """Fecha a conexão com o banco de dados."""
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def create_tables(self):
        """Cria as tabelas do banco de dados a partir do schema.sql."""
        schema_path = Path(__file__).parent / 'schema.sql'
        
        if not schema_path.exists():
            raise FileNotFoundError(f"Arquivo schema.sql não encontrado em {schema_path}")
        
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        
        try:
            self.connection.executescript(schema_sql)
            self.connection.commit()
        except sqlite3.Error as e:
            raise Exception(f"Erro ao criar tabelas: {e}")
    
    def execute_query(self, query, params=None):
        """
        Executa uma query SQL (INSERT, UPDATE, DELETE).
        
        Args:
            query: Query SQL a ser executada
            params: Parâmetros da query (tuple ou dict)
            
        Returns:
            Cursor com o resultado
        """
        try:
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor
        except sqlite3.Error as e:
            raise Exception(f"Erro ao executar query: {e}")
    
    def execute_many(self, query, params_list):
        """
        Executa múltiplas queries com diferentes parâmetros.
        
        Args:
            query: Query SQL a ser executada
            params_list: Lista de parâmetros
        """
        try:
            cursor = self.connection.cursor()
            cursor.executemany(query, params_list)
            return cursor
        except sqlite3.Error as e:
            raise Exception(f"Erro ao executar queries: {e}")
    
    def fetch_one(self, query, params=None):
        """
        Executa uma query e retorna um único resultado.
        
        Args:
            query: Query SQL SELECT
            params: Parâmetros da query
            
        Returns:
            Uma linha do resultado ou None
        """
        cursor = self.execute_query(query, params)
        return cursor.fetchone()
    
    def fetch_all(self, query, params=None):
        """
        Executa uma query e retorna todos os resultados.
        
        Args:
            query: Query SQL SELECT
            params: Parâmetros da query
            
        Returns:
            Lista de linhas do resultado
        """
        cursor = self.execute_query(query, params)
        return cursor.fetchall()
    
    def commit(self):
        """Confirma as mudanças no banco de dados."""
        if self.connection:
            self.connection.commit()
    
    def rollback(self):
        """Reverte as mudanças não confirmadas."""
        if self.connection:
            self.connection.rollback()
    
    def __enter__(self):
        """Suporte para context manager (with statement)."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Fecha a conexão ao sair do context manager."""
        if exc_type is not None:
            self.rollback()
        else:
            self.commit()
        self.close()
