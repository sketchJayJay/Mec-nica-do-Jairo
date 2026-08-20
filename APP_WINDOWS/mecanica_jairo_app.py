from pathlib import Path
import sys
import webview

BASE = Path(__file__).resolve().parent
URL_FILE = BASE / 'url_oficina.txt'

class Api:
    def __init__(self):
        self.window = None

    def fechar(self):
        if self.window:
            self.window.destroy()
        return True


def carregar_url():
    if not URL_FILE.exists():
        return None
    url = URL_FILE.read_text(encoding='utf-8').strip()
    return url or None

url = carregar_url()
if not url:
    # Não abre console quando iniciado via pythonw. Mostra uma janela simples de erro.
    import tkinter as tk
    from tkinter import messagebox
    root = tk.Tk(); root.withdraw()
    messagebox.showerror('Mecânica do Jairo', 'Endereço do sistema não configurado. Execute CONFIGURAR_ENDERECO.bat.')
    root.destroy()
    sys.exit(1)

api = Api()
window = webview.create_window(
    'Mecânica do Jairo',
    url,
    js_api=api,
    fullscreen=True,
    frameless=True,
    easy_drag=False,
    text_select=True,
)
api.window = window
webview.start(debug=False, private_mode=False)
