"""
Arquivo de entrada principal para o Sistema de Biblioteca
Execute este arquivo para iniciar a interface gráfica do sistema.
"""

# Garantir dados padrão no banco de dados
import importlib.util
import subprocess
import sys
from pathlib import Path


init_db_script = Path(__file__).parent / 'database' / 'init_db.py'

# Executa apenas o `database/init_db.py` para criar tabelas e popular dados de exemplo
# Esse script já é idempotente: se o banco já contém dados ele pula a inserção.
if init_db_script.exists():
    # Preferir o mesmo interpretador que está executando este script (sys.executable)
    try:
        subprocess.run([sys.executable, str(init_db_script)], check=True)
    except FileNotFoundError:
        # Em cenários estranhos onde sys.executable não existe, tentar `python3`
        try:
            subprocess.run(['python3', str(init_db_script)], check=True)
        except Exception as e:
            print(f"Aviso: falha ao executar {init_db_script} com 'python3': {e}")
    except subprocess.CalledProcessError as e:
        # Não interromper a inicialização da aplicação caso o script retorne erro
        print(f"Aviso: '{init_db_script}' retornou erro (código {e.returncode}). Continuando...")
    except Exception as e:
        print(f"Aviso: falha ao executar {init_db_script}: {e}")

# Observação: `database/init_db.py` é idempotente — se o banco já contém dados,
# ele pula a inserção de exemplo. Não modificamos o banco em execuções subsequentes.

from interface.app import SistemaBiblioteca


if __name__ == "__main__":
    app = SistemaBiblioteca()
    app.mainloop()