"""
Arquivo de entrada principal para o Sistema de Biblioteca
Execute este arquivo para iniciar a interface gráfica do sistema.
"""

if __name__ == "__main__":
    from interface.app import SistemaBiblioteca
    
    app = SistemaBiblioteca()
    app.mainloop()


