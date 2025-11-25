"""
Arquivo de entrada principal para o Sistema de Biblioteca
Execute este arquivo para iniciar a interface gráfica do sistema.
"""

# Garantir dados padrão no banco de dados
import importlib.util
from pathlib import Path

script_path = Path(__file__).parent / 'inicializar_dados.py'
if script_path.exists():
    spec = importlib.util.spec_from_file_location('inicializar_dados', script_path)
    init_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(init_mod)
    init_mod.inicializar()

from interface.app import SistemaBiblioteca

if __name__ == "__main__":
    app = SistemaBiblioteca()
    app.mainloop()