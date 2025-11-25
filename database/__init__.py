"""
Módulo de banco de dados para o Sistema de Biblioteca.
Gerencia persistência de dados usando SQLite.
"""

from .db_manager import DatabaseManager
from .repositories import (
    UsuarioRepository,
    ItemRepository,
    EmprestimoRepository,
    ReservaRepository,
    MultaRepository
)

__all__ = [
    'DatabaseManager',
    'UsuarioRepository',
    'ItemRepository',
    'EmprestimoRepository',
    'ReservaRepository',
    'MultaRepository'
]
