# -*- coding: utf-8 -*-
# PATCH_VERSION: MECANICA_DO_JAIRO v1.3 - editar OS / imprimir estoque / editar item
__PATCH_VERSION__ = 'MECANICA_DO_JAIRO v1.3 (editar OS + imprimir estoque + editar item estoque)'



# ===== Modern theme (sv_ttk) =======================================
# Requer: pip install sv-ttk
def init_modern_theme(root, mode="light"):
    try:
        import sv_ttk
        if mode.lower().startswith("d"):
            sv_ttk.set_theme("dark")
        else:
            sv_ttk.set_theme("light")
        # Pequenos ajustes de densidade e botões
        import tkinter.ttk as _ttk
        _style = _ttk.Style()
        P = getattr(root, "palette", {
            'fg':'#0f172a','muted':'#475569','card':'#ffffff','heading_bg':'#eef2f7',
            'accent':'#dc2626','accent_hover':'#b91c1c','table_sel':'#fee2e2'
        })
        _style.configure('TButton', padding=8)
        _style.configure('Accent.TButton', padding=8)
        _style.configure('TNotebook', tabposition='n')
        _style.configure('TNotebook.Tab', padding=(14, 8))
        # Cabeçalhos das tabelas com peso
        _style.configure('Treeview.Heading', font=(getattr(root, 'font_family','Segoe UI'), getattr(root,'font_base',10), 'bold'))
        # Seleção suave na Treeview
        _style.map('Treeview', background=[('selected', P.get('table_sel','#e8eef9'))])
    except Exception as e:
        print('[theme] sv_ttk indisponível:', e)

def toggle_dark_mode(root):
    try:
        import sv_ttk
        # Detecta tema atual
        import tkinter.ttk as _ttk
        s = _ttk.Style()
        theme = s.theme_use()
        sv_ttk.set_theme('light' if 'dark' in theme else 'dark')
    except Exception as e:
        print('[theme] toggle falhou:', e)
# ===================================================================
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Oficina Mecânica — v0.5 (Pro Light 2025) — FIX Cadastro scroll
Correção pontual: a aba "Cadastro rápido" agora é rolável (scroll), evitando que os botões
"Salvar/Excluir/Limpar" fiquem cortados em telas menores ou com escala/DPI alta.

Nenhuma alteração de estilo/cores/fluxo além disso.
"""

import os
import sqlite3
import webbrowser
import sys


# ===== ttkbootstrap (mínimo e estável) ==============================
def init_ttkbootstrap_min(root):
    try:
        import ttkbootstrap as tb  # type: ignore
        tb.Style('pulse')
    except Exception as e:
        print('[ttkbootstrap] não aplicado:', e)
# ===== Polimento moderno (não invasivo) ==============================
def apply_modern_styles(root):
    import tkinter.ttk as ttk
    s = ttk.Style(root)
    try:
        # Abas mais confortáveis
        s.configure('TNotebook', borderwidth=0)
        s.configure('TNotebook.Tab', padding=(16, 10), font=('Segoe UI', 10, 'bold'))
        # Frames e labels com fundos coerentes (mantém tema pulse)
        s.configure('TFrame', background='#f7f8fb')
        s.configure('Card.TFrame', background='#ffffff')
        s.configure('TLabel', background='#f7f8fb')
    except Exception:
        pass
# ====================================================================

# ====================================================================

# ----------------------------- INTRO EMBUTIDA (imageio + Pillow) ----------------------------- #
def play_intro_video(video_path: str, fullscreen: bool = True, duration_limit: float = 13.0):
    import tkinter as tk
    from tkinter import ttk
    import time
    try:
        import imageio.v3 as iio
        from PIL import Image, ImageTk  # type: ignore
    except Exception as e:
        print("[Intro] Dependências ausentes (imageio/Pillow):", e)
        # Splash simples respeitando o limite
        root = tk.Tk(); root.configure(bg="black"); root.title("Intro")
        try:
            root.attributes("-fullscreen", True) if fullscreen else root.geometry("960x540")
        except Exception:
            pass
        tk.Label(root, text="Iniciando...", fg="white", bg="black", font=("Segoe UI", 28, "bold")).pack(expand=True, fill="both")
        root.after(int(duration_limit*1000), root.destroy)
        root.mainloop()
        return

    root = tk.Tk(); root.configure(bg="black"); root.title("Intro")
    try:
        root.attributes("-fullscreen", True) if fullscreen else root.geometry("960x540")
    except Exception:
        pass

    state = {"stop": False, "after_id": None, "t0": time.monotonic(), "cap": float(duration_limit)}

    def skip(event=None):
        if state["stop"]:
            return
        state["stop"] = True
        try:
            if state["after_id"] is not None:
                root.after_cancel(state["after_id"])
        except Exception:
            pass
        try:
            bar.stop()
        except Exception:
            pass
        try:
            root.destroy()
        except Exception:
            pass

    # UI
    btn = tk.Button(root, text="Pular intro (ESC)", command=skip, bg="#111827", fg="#ffffff", bd=0, padx=12, pady=6,
                    activebackground="#1f2937", activeforeground="#ffffff")
    btn.place(relx=1.0, rely=1.0, x=-20, y=-20, anchor="se")
    root.bind("<Escape>", skip)

    tk.Label(root, text="Carregando…", fg="#e5e7eb", bg="black", font=("Segoe UI", 14)).place(relx=0.5, rely=0.92, anchor="s")
    bar = ttk.Progressbar(root, mode="indeterminate", length=420); bar.place(relx=0.5, rely=0.96, anchor="s")
    try:
        bar.start(12)
    except Exception:
        pass

    video_lbl = tk.Label(root, bg="black"); video_lbl.pack(expand=True, fill="both")

    # Metadados + leitor de frames
    try:
        meta = iio.immeta(video_path); fps = float(meta.get("fps", 24.0)) if meta else 24.0
    except Exception:
        fps = 24.0
    delay = max(10, int(1000.0 / max(1.0, fps)))

    try:
        reader = iio.imiter(video_path)  # gera frames (H,W,3)
    except Exception as e:
        print("[Intro] Falha ao abrir vídeo:", e)
        tk.Label(root, text="Oficina Mecânica", fg="white", bg="black", font=("Segoe UI", 28, "bold")).pack(expand=True, fill="both")
        root.after(int(duration_limit*1000), skip)
        root.mainloop()
        return

    sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()

    def render_next():
        if state["stop"]:
            return
        # Corta a intro no tempo-limite
        if time.monotonic() - state["t0"] >= state["cap"]:
            return skip()
        try:
            frame = next(reader)
        except StopIteration:
            return skip()
        except Exception as e:
            print("[Intro] Erro lendo frame:", e); return skip()

        try:
            img = Image.fromarray(frame)
            iw, ih = img.size
            scale = min(sw / max(1, iw), sh / max(1, ih))
            nw, nh = max(1, int(iw*scale)), max(1, int(ih*scale))
            img = img.resize((nw, nh), Image.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            video_lbl.configure(image=photo); video_lbl.image = photo
        except Exception as e:
            print("[Intro] Erro convertendo frame:", e); return skip()

        try:
            state["after_id"] = root.after(delay, render_next)
        except Exception:
            return skip()

    print("[Intro] Embutida (imageio+Pillow):", video_path)
    render_next()
    root.mainloop()

    def skip(event=None):
        if state["stop"]: return
        state["stop"] = True
        try: bar.stop()
        except Exception: pass
        try: root.destroy()
        except Exception: pass

    # UI
    btn = tk.Button(root, text="Pular intro (ESC)", command=skip, bg="#111827", fg="#ffffff", bd=0, padx=12, pady=6,
                    activebackground="#1f2937", activeforeground="#ffffff")
    btn.place(relx=1.0, rely=1.0, x=-20, y=-20, anchor="se")
    root.bind("<Escape>", skip)

    tk.Label(root, text="Carregando…", fg="#e5e7eb", bg="black", font=("Segoe UI", 14)).place(relx=0.5, rely=0.92, anchor="s")
    bar = ttk.Progressbar(root, mode="indeterminate", length=420); bar.place(relx=0.5, rely=0.96, anchor="s")
    try: bar.start(12)
    except Exception: pass

    video_lbl = tk.Label(root, bg="black"); video_lbl.pack(expand=True, fill="both")

    # Metadados + leitor de frames
    try:
        meta = iio.immeta(video_path); fps = float(meta.get("fps", 24.0)) if meta else 24.0
    except Exception:
        fps = 24.0
    delay = max(10, int(1000.0 / max(1.0, fps)))

    try:
        reader = iio.imiter(video_path)  # gera frames (H,W,3)
    except Exception as e:
        print("[Intro] Falha ao abrir vídeo:", e)
        # Splash curto
        tk.Label(root, text="Oficina Mecânica", fg="white", bg="black", font=("Segoe UI", 28, "bold")).pack(expand=True, fill="both")
        root.after(int(duration_limit*1000), skip); root.mainloop(); return

    sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()

    def render_next():
        if state["stop"]: return
        try:
            frame = next(reader)
        except StopIteration:
            return skip()
        except Exception as e:
            print("[Intro] Erro lendo frame:", e); return skip()

        try:
            img = Image.fromarray(frame)
            iw, ih = img.size
            scale = min(sw / max(1, iw), sh / max(1, ih))
            nw, nh = max(1, int(iw*scale)), max(1, int(ih*scale))
            img = img.resize((nw, nh), Image.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            video_lbl.configure(image=photo); video_lbl.image = photo
        except Exception as e:
            print("[Intro] Erro convertendo frame:", e); return skip()

        root.after(delay, render_next)

    print("[Intro] Embutida (imageio+Pillow):", video_path)
    render_next(); root.mainloop(); return




from datetime import datetime
# === PIX QR embutido ===
QR_PIX_MIME = 'image/png'
QR_PIX_B64 = '''iVBORw0KGgoAAAANSUhEUgAABIAAAAVICAIAAABTBjZgAAEAAElEQVR4nOzdd5wkR303/urck/dm9yLoTjoOgUAiZwNCIhhMDjYGE22SMcFgG4wNxvwwGNs8TjwE2/gBkU2wMdEYBAKRBBiEAiAkH9wp3J1ud3Ynd+7fH19fedjd6Z3qna7umf28X/ea195uT3dVd3V1fauqu5U4jhkAAAAAAABkT807AQAAAAAAADsFAjAAAAAAAABJEIABAAAAAABIggAMAAAAAABAEgRgAAAAAAAAkiAAAwAAAAAAkAQBGAAAAAAAgCQIwAAAAAAAACRBAAYAAAAAACAJAjAAAAAAAABJEIABAAAAAABIggAMAAAAAABAEgRgAAAAAAAAkiAAAwAAAAAAkAQBGAAAAAAAgCQIwAAAAAAAACRBAAYAAAAAACAJAjAAAAAAAABJEIABAAAAAABIggAMAAAAAABAEgRgAAAAAAAAkiAAAwAAAAAAkAQBGAAAAAAAgCQIwAAAAAAAACRBAAYAAAAAACAJAjAAAAAAAABJEIABAAAAAABIggAMAAAAAABAEgRgAAAAAAAAkiAAAwAAAAAAkAQBGAAAAAAAgCQIwAAAAAAAACRBAAYAAAAAACAJAjAAAAAAAABJEIABAAAAAABIggAMAAAAAABAEgRgAAAAAAAAkiAAAwAAAAAAkAQBGAAAAAAAgCQIwAAAAAAAACRBAAYAAAAAACAJAjAAAAAAAABJEIABAAAAAABIggAMAAAAAABAEgRgAAAAAAAAkiAAAwAAAAAAkAQBGAAAAAAAgCQIwAAAAAAAACRBAAYAAAAAACAJAjAAAAAAAABJEIABAAAAAABIggAMAAAAAABAEgRgAAAAAAAAkiAAAwAAAAAAkAQBGAAAAAAAgCQIwAAAAAAAACRBAAYAAAAAACAJAjAAAAAAAABJEIABAAAAAABIggAMAAAAAABAEgRgAAAAAAAAkiAAAwAAAAAAkAQBGAAAAAAAgCQIwAAAAAAAACRBAAYAAAAAACAJAjAAAAAAAABJEIABAAAAAABIggAMAAAAAABAEgRgAAAAAAAAkiAAAwAAAAAAkETPOwEAAACwXt/vf/341//rlv/64akfHm8fv6lzU9ftDoNhFEdVs0r/blu/7e2bt7/94u3PWzrvAWc9oG7V8071znVL95avHfva92753o+Xf3y8ffxU71Tf7zuBUzEqdavesBtHmkcu2HPBBXsvuOjsi/ZU9mx/i223fdnPL7vipiuuvvXqY2vHTvRODPyBEziWZlXMyr7qvkONQ+fvOf8+t7nPRedctMvetf0tAsC0KHEc552GHeSG1g23f9vtp7jCCw9deNlzLhv9zY9O/+ge/3APN3THfeULz/jCI273iMk38Sdf+ZM3fu2N4/56Vv2sa158zbqrfopsqopat+oNq9GwG+cunnvP/fe854F7Pujgg2zdnnANEvZt6m2pimpqZs2sNUvNg42Dt1+8/d333f2icy663a7biaYqedN33n3na158TbrvcgkZH6fjdm7z17fpeb3kxe6weIefvOQn20ze5LZ5BL/0rC899JyHTrKh6purfb+/6Z/eeNEbX/vg1/L/Pux9D7v0Z5dOss5tOtQ49PPf/Tn/r8x9m04ulUay5/77c9975XuTl3nmXZ75vie+byqb47zQ+8SPP/G+H77vKz/7SkJNvpGmaPfYf4+LzrnoSec96b63ue82k5Fp9nOsQqduzVl775Xv/eDVH/yvW/4rZhM1qFRFvfeBez/uDo977t2fu7+6X3SLYRz++0/+/R//6x+//LMv+5E/yVd0VX/I2Q95/j2e/6TznqSrYj3vBb9wpFPAVsqml+8itOggIxgBmzd32n2nN178xld98VXjFnjep5539YuvbliNSdb2/RPf//Ov/3nCAv/8+H+eyrkaxdGas7bmrLE2u+rUVR//0ccZY7vsXc+4yzNeeK8X3nn3nbe/iRxFceQEjhM4pwenr1u57otHv0i/v2DPBS+45wued4/nTavJOBVfPfbVa09fK7TP3/fD9215EZ05f3zpHz/0eRMFYJCLTCuNgT/4xI8+seVi//rjf33nY95ZMSrb2Rbnhd47v/fON1/+5lv7t6b4ehiH373lu9+95bt/+Y2/vOPSHZ9912e/9L4vTZe2XLKfoJhVaMftvOXrb/m7K/5u4A+EvhjF0RU3X3HFzVf86WV/+pQ7PeV1F77uvKXzJvzuv/3k3171xVfd0LpBaItBFHzp6Je+dPRLZy+c/RcP+4tfu/OvCX19EnN/4cillTKjLTqYBO4Bm0O/d//fe8BZDxj31xs7N77iP14xyXq80Hv2J58dRMG4BV50rxc9/PDD0yRxMqvO6tu+87a7vvOur/riq4bB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CQIwAAAAAAAASRCAAQAAAAAASIIADAAAAAAAQBIEYAAAAAAAAJIgAAMAAAAAAJAEARgAAAAAAIAkCMAAAAAAAAAkQQAGAAAAAAAgCQIwAAAAAAAASRCAAQAAAAAASIIADAAAAAAAQBIEYAAAAAAAAJIgAAMAAAAAAJAEARgAAAAAAIAkCMAAAAAAAAAkQQAGAAAAAAAgCQIwAAAAAAAASRCAAQAAAAAASIIADAAAAAAAQBIEYAAAAAAAAJIgAAMAAAAAAJAEARgAAAAAAIAkCMAAAAAAAAAkQQAGAAAAAAAgCQIwAAAAAAAASRCAAQAAAAAASIIADAAAAAAAQBIEYAAAAAAAAJIgAAMAAAAAAJAEARgAAAAAAIAkCMAAAAAAAAAkQQAGAAAAAAAgCQIwAAAAAAAASRCAAQAAAAAASIIADAAAAAAAQBIEYAAAAAAAAJIgAAMAAAAAAJAEARgAAAAAAIAkCMAAAAAAAAAkQQAGAAAAAAAgCQIwAAAAAAAASRCAAQAAAAAASIIADAAAAAAAQBIEYAAAAAAAAJIgAAMAAAAAAJAEARgAAAAAAIAkCMAAAAAAAAAkQQAGAAAAAAAgCQIwAAAAAAAASRCAAQAAAAAASIIADAAAAAAAQBIEYAAAAAAAAJIgAAMAAAAAAJAEARgAAAAAAIAkCMAAAAAAAAAkQQAGAAAAAAAgCQIwAAAAAAAASRCAAQAAAAAASIIADAAAAAAAQBIEYAAAAAAAAJIgAAMAAAAAAJAEARgAAAAAAIAkCMAAAAAAAAAkQQAGAAAAAAAgCQIwAAAAAAAASRCAAQAAAAAASIIADAAAAAAAQBIEYAAAAAAAAJIgAAMAAAAAAJAEARgAAAAAAIAkCMAAAAAAAAAkQQAGAAAAAAAgCQIwAAAAAAAASRCAAQAAAAAASIIADAAAAAAAQBIEYAAAAAAAAJIgAAMAAAAAAJAEARgAAAAAAIAkCMAAAAAAAAAkQQAGAAAAAAAgCQIwAAAAAAAASRCAAQAAAAAASIIADAAAAAAAQBIEYAAAAAAAAJIgAAMAAAAAAJAEARgAAAAAAIAkCMAAAAAAAAAkQQAGAAAAAAAgCQIwAAAAAAAASRCAAQAAAAAASIIADAAAAAAAQBIEYAAAAAAAAJIgAAMAAAAAAJAEARgAAAAAAIAkCMAAAAAAAAAkQQAGAAAAAAAgCQIwAAAAAAAASRCAAQAAAAAASIIADAAAAAAAQBIEYAAAAAAAAJLoeScgJeVuD847CQAAAAAAkJv4yq/lnYQ0ZjUA0wyDKRGLVXziE5/4xCc+8YlPfOITnzvxczbNagAWekPGIsZUfOITn/jEJz7xiU984hOfO/JzJilxHOedhjSUu9037yQAAAAAAEBu4iuvyDsJaczqCBhbbeWdAgAAAAAAADGzGoDd9b73yjsJAAAAAAAAYmZ1CuIXrv1J3kkAAAAAAIDc/PKd75h3EtKY1QCsm3cCAAAAAAAgR7W8E5DOrE5BtPJOAAAAAAAAgKhZHQFjMWMKPvGJT3ziE5/4xCc+8YnPnfo5m2Z1BIxFBTjk+MQnPvGJT3ziE5/4xCc+8/pU8w5JUpnZEbAw7wQAAAAAAECOtLwTkMrMjoApeScAAAAAAABAEAIwAAAAAAAASWY1AIsRgAEAAAAA7GAzGhDM5p1rjDHGInziE5/4xCc+8YlPfOITnzv4cxbN7EM48n7mCj7xiU984hOf+MQnPvGJz3w/Z9EMB2AAAAAAAACzZYanIAIAAAAAAMwWBGAAAAAAAACSIAADAAAAAACQBAEYAAAAAACAJAjAAAAAAAAAJEEABgAAAAAAIAkCMAAAAAAAAEkQgAEAAAAAAEiCAAwAAAAAAEASBGAAAAAAAACSIAADAAAAAACQBAEYAAAAAACAJAjAAAAAAAAAJEEABgAAAAAAIAkCMAAAAAAAAEkQgAEAAAAAAEiCAAwAAAAAAEASBGAAAAAAAACSIAADAAAAAACQBAEYAAAAAACAJAjAAAAAAAAAJEEABgAAAAAAIAkCMAAAAAAAAEkQgAEAAAAAAEiCAAwAAAAAAEASBGAAAAAAAACSIAADAAAAAACQBAEYAAAAAACAJAjAAAAAAAAAJEEABgAAAAAAIAkCMAAAAAAAAEkQgAEAAAAAAEiCAAwAAAAAAEASBGAAAAAAAACSIAADAAAAAACQBAEYAAAAAACAJAjAAAAAAAAAJEEABgAAAAAAIAkCMAAAAAAAAEkQgAEAAAAAAEiCAAwAAAAAAEASBGAAAAAAAACSIAADAAAAAACQBAEYAAAAAACAJAjAAAAAAAAAJEEABgAAAAAAIAkCMAAAAAAAAEkQgAEAAAAAAEiCAAwAAAAAAEASBGAAAAAAAACSIAADAAAAAACQBAEYAAAAAACAJAjAAAAAAAAAJEEABgAAAAAAIAkCMAAAAAAAAEkQgAEAAAAAAEiCAAwAAAAAAEASBGAAAAAAAACSIAADAAAAAACQBAEYAAAAAACAJAjAAAAAAAAAJEEABgAAAAAAIAkCMAAAAAAAAEkQgAEAAAAAAEiCAAwAAAAAAEASBGAAAAAAAACSIAADAAAAAACQBAEYAAAAAACAJAjAAAAAAAAAJEEABgAAAAAAIAkCMAAAAAAAAEkQgAEAAAAAAEiCAAwAAAAAAEASBGAAAAAAAACSIAADAAAAAACQBAEYAAAAAACAJAjAAAAAAAAAJEEABgAAAAAAIAkCMAAAAAAAAEkQgAEAAAAAAEiCAAwAAAAAAEASBGAAAAAAAACSIAADAAAAAACQBAEYAAAAAACAJAjAAAAAAAAAJEEABgAAAAAAIAkCMAAAAAAAAEkQgAEAAAAAAEiCAAwAAAAAAEASBGAAAAAAAACSIAADAAAAAACQBAEYAAAAAACAJAjAAAAAAAAAJEEABgAAAAAAIAkCsNkQBAFjbDAYjP7X87w80wRT1e/34zhmjA2HwyiKGGNhGI5bmA49FQN2pmDw/86uGcqX0PHKUa/XY4x5nrdu38Ic4AWPXxp4sRyHXzuoPFDxKJoU+ZpLedWHou2NeS2H8wrnV1HEMCNOnDixuLhIR03TtHK5bJpmvoVn58j64HqeRz+srq42Gg3aqKZp49Jjmma5XOYLLC4unjhxIsV2Zew7EdPKV9ZEj1eODh482G63ecp934+iKKfdtuNkfXB1Xacf6vX62toabdR13XHpiaLI933+33a7ffDgwawTmYJovqYl31xvlGN9KNTemNdyOK/yOr9gHSUuXqUDG8VxrCiKoiiMMVVVqQODfs41XTuFhMGNOI673W69XlcUpdFo9Hq9MAzHHd/RAkA//8/5rChCGy1azDCtfEkgdLzywveh53lhGBqGwS+9IEHW51cURaqqVqvVTqcTx3Gv16tUKlueLEEQ+L6vaZppmvyakmk6RaXL1/ahPiSi7Y15LYfzKq/zC9ZBADYbTp48uW/fPmrq+b5PHfDVarXdbuedtB1Bwmni+75hGIyxjZe9jajFryiKaZqGYdAQBxUSoY0Wrc6dVr4kEDpeeTl06NCxY8fiOHYcxzAMal86jmPbdt5J2xEknF+K8j8XcfrkxXJT/NCHYej7vm3biqJQIck6naKE8jXFjWa9CSF51Ycp2hvzWg7nVS7nF6yDAGyWFO3ysHNkfZoMBgPLsjRNGwwGS0tLw+FQURTLshzHyTSFxS9Rxaygtn+8ZBrdhxQloqdZjqzPr1Kp5DhOHMe2bbdarVKpFEXRcDisVCqbLr/x6BezBhDN17QUc2+MklkfTr435rUczqu8zi9YB9NRZkan0zFNM47jKIosywrD0HVdNKTmQ7lcZmce56DrerlcHgwGjuMkTPmgAIDKgKIonU6nXq+Lbrdo5Wda+cqa6PHKSxRFzWYzDENFUVRV9TxPVVXMQpQm6/IwHA4ZY6VSSdO0KIpoYCGhFaWqahAEQRCYpkm3AjabzVarVbRyK5qvaSnafsixPhRqb8xrOZxXeZ1fsA5GwGYDNaFs246iiO5HUlXVNM1i9rjPn6xPk+FwWCqV6GfeF2hZluu6my5v27bnedSPqGmaqqrUoSV6D0PR+h2nla+siR6vvGiaRvMPVVWlfRhFked5mIIoR9bnl23b/BLA66h+vz+uLeU4jmma1MwNwzCKIpr9VbQHeIrma1pQHxLR9sa8lsN5ldf5BesgAJsNYRhqmqYoCn3GcYyqSiZp94DFcWyaZhAEo1XkOKOFgT5nPQAj28+XBCmOl3yapvF9SDfWF3BPzrGszy+6O8h1XU3T6Lnek9zLMVoY6LNoV5N0+ZrKdrPeRAry60PR9sa8lsN5ldf5BesgAJsNo08l0nU9CIJi3vQ/r7I+TWj9dHwnbARQAaDCwNI+HauADY6p5CtrKY5XLqjxRKkNgkDXdXr+Vd7p2ilklo3RW+oTtksFgAoDLclvxy+mCfM1FQU8l3OpD7fT3pjXcjivZJ5fsA6uxAAAAAAAAJIgAAMAAAAAAJAEARgAAAAAAIAkCMAAAAAAAAAkQQAGAAAAAAAgCQIwAAAAAAAASRCAAQAAAAAASIIAbJ5VKhXTNOlnRVHohRs7Fr28slqtytlcr9djjE34ZskgCBRFCYKg3++Xy2VKasLxMgwjiiL6Cv3X9305L/GgHTjhm0B1XeepMk2zUqls+RV620wQBKVSiX7jeV7KtBYGvXqLv+mSsibhxZe2bdMPrutSccruJWBU1KnYSyB0fs0rOqaappXL5X6/z6uRccv7vq+qahzH9EX+MnEJSRWtN5hIvkZJLocpTH5dzque51VuqVSiTeOlo0VGlxJ+xaT/4n2PxYc3380G0RcjWpYVhiFVnZZl1Wq15eVlNvH1b26EYcgvb3yn2bbtOI7QekRPE8dxbNvm75qkX+q6ntBepEMThqFpmnRkVVUdd62l9ZTL5cFgsLS01Gq1giBwHIdf1yckGpPTruPvBqVfBkEwrlxROpeWlrrdruu6tEVN0+jncUnSdd33fU3TPM+jPS/azs66nIu+iJlaTqO/oX0oms508UYcx1T46bWnqqpOK27RNG20eFOBp8I/lfWPk+L8yoVlWZmuP45jXld4nsfrkHHL0wKDwaBcLi8vLzebTV3XbdsW7eMQ3c+i9UaKfE2lHGYd24hel6dVz4ui9CiKYppmGIaGYQRBMGEALPNFzDutPTNOGIYbG4QbLzqbwouYc7Sjh0TmmOu6zWYzCIJOp2PbNtXy1Wq1yP2CWaA+oeFwSP/dt2/fLbfcIqEzjzqfTp48eeDAAbrADIdD3/d5H9U6URRRqjRNoy5PNtIK2VSlUun3+4wxOrijQ0bZofTQbqTrcalUMgyD7+F1qMgtLy83Gg3Xdev1uq7rrVZr3Poty4rjmMLjMAx37dp1/PjxgwcPzvqFli6ElmVRg2YwGBw+fPiGG26QEDCcddZZKysri4uLjDHTNF3XjeN4WgESHXde8KjAS+h5FT2/8pL18eW9chTM0+mpKErCIej3+zQQvbS0xBjTdX3cyTtFovWGaL7yKoeiUlyXc6nnGWPHjx/ftWvX6uoqO9MtaFlWQsdZLorW4ZIjuqDQ9BnP81zXnST6gnxhBGw2iI6AcaZptlotuuLy3qado9PpVKtVfiXu9/uHDh3qdDqidZPoaeL7fqfTOXToEF07GWOqqlar1U6ns+ny/NpWrVZvueWWWq0Wx7HruuMaytQJGkVRu92mtrWcvivDMOr1+rFjx/hkwiiKer1evV7fdHle5Pr9frPZnLCj3bIs6r1zXXfPnj2nT58W3f9ZV2uiI2ALCwu9Xo93IddqtWPHjtXrddHAMt1RbjabPOjVdb1cLo8rh6Lq9Xqv1+MVUaVSoXxlPbtS9PzKS9bl0HEcy7IURel2uwcOHKB2fEJDmQa7VFVtNBorKyupUyhaDkXrDdF8TascShsBmPC6nFc9ryjK7t27b7311tGqeMLvyhwBQ/OVhGFI9WG326Xf6LperVbX1ta2/C5GwHKEAGw2iAZgVGkuLCx0Op0wDPlkjJ12uKlOdxyHannDMNJVMambKdQC0HXdcRw6iMnrt2271WrxPs5x2x1dT6vVajabdC+BaI9gunzFcUwRbBAEtm0nXDgpnVT8NE2r1+tra2sJUyNG21j8ZpUUtz1kPcgpGoARy7KCIKCBzdHL3uREO/Vpf9IYAk2H830/DMNpXWipSNu2TbGl7/sya5jJz6+8SBgBox+Gw2Gz2eQzq7esZ9iZsJymp4p2BKQbXBKtN5hIvqZSDrMuP6LX5WnV86LiOKZph4qi8Lp0whEwmQEY7kwj/EpEty3ouj71gBmygABsNqQeAWNnptrvwOGvTVH1NOF0dk70NKG9LVSdlcvlIAjorifXdYMgSHhkheu6juM0Gg3f92lSiqIodKuAUDpF0a4T2hu0K0ZvxktA12BN0yhIGL38CynaCNgoyp20BmKKZs12UIM+66omxfmVCwl7vt/v67pO40Wmaeq6nlAJWJZl23a73TYMgyYfxnFMt4QJbVR0z6eoN4TytVG6ciizRE1yXc6rnifUBTZaIU9yBDEClhdFUehICX0LAViOCjdJGqbCNE3qWtM0jXo34zjegROmXdflXUE86JJ2DxgbecqFZVkJd+QrijIYDDzP27t378mTJy3LqlQqyQ9ZqVarw+HQMAzTNFdWVg4fPizhqsyTxHfm6B7eiEcavBzatp1wBzlfmHry6CJdwHs5RJmmyWdD8UaDhPORLqiapvHum1KpNMUnZIyWal7Upd0DxiY+v+ZVFEWVSsWyrJMnT+7du9fzvMFgkNCKcl231+uVSiXf9z3PW1xcPHr0qGj0lS6d9MOE9YZovvIqh6JEr8t51fNU69LdyKqq8qRmvV1IhxchfoyowOSXIpgIRsBmg+gIGHUmmaZJIyo01WGKU49mBb8G01MuUveapx6voEdy8SM1rk1AM8SoRUKXPf6ct02XHwwG9Fhn13Uty/J93zRN0zRFR/ZSjy9RCRzdveOW1DSN8kI92Z7nJfR0Uufu6AK8tAulUMIUHSY4AkZZoJ3Gn+4ouv9Fp4pRhyhNQaTudtq302qbjhZs6s+WPAVxwvMrL1nfB8+f9cePKVUj4/ZDuVwevZ/KMAzP8zzPEx0pSvdQnMnrDdF8TascZn19FL0uT6ueF0XXSr4VSvaEI28yR8B2YJ/ypui8oCssrw8nvLhgBCxHCMBmw3amIO7wEyyXqQ4SjtdU8iWKNkFboU1TMsYtv52pettRwCmI/Bnc1Kyh3Si6Twp4/k4lX6K2c37JhHLIl8+63pi586vI9fx2YAqifGgfzqhi9RcCAAAAAADMMQRgAAAAAAAAkiAAAwAAAAAAkAQBGAAAAAAAgCQIwAAAAAAAACRBAAYAAAAAACAJAjAAAAAAAABJxF6/CPNqMBiUy+XRF6fwt7Xkm7B16E0v9FbKbrdbq9Xo57zTtR7fjXwf0ue4V98oihKGoW3bjuMwxjzPM01zPl5yoigKZYcxRhnUNG1c1ugl1HEc67oehqGqqvQeYdEXboqW29E30rAzr1Whk2LcV0TzxYsBf1URXroiE73Jt1ardbtd+rmA9Rsv7VTydV2nojjJC4vpNxO+iJneym0YBmPM933RFzGL4snjL1Wnz0le4M4Y2/IF7oTWSQszxhL2W/IaspOunqdc8NomxYvUi1bO8yJ6fuWlaC+Uh4wgAAPGGKOGJr8Sq6pKL/IrWkUQRZHv+xRx1Wq1KIoKGH2xM2+Z5D8zxiidrutuurymaYZh0FU5DEPTNB3HUVWVrrizy/f9KIps26YIynEcwzB4NLKRbduKogyHQx5xpbs6pmigjLYIgyAwTTMh+hLNFz/66wpG0c6vOUZhSbfbpZ8Nw4jjuIANL94c1zSNMeY4jqIoFIdsRIWQMXbq1Km9e/eeOnXKdd2EU6bX62maZprmcDjUNK1erx89evTw4cPZ5OZ/jb4Wlso81YTjau8wDH3fp6xpmuZ5nm3bURRRZLURhTF0VvJzilrbQunMujyI1vMUdhqGMboDU3RIARE9vwAyVehXqgOX9ZvOaf10xYrjOEUfmxzUxqU9oGkaDX9FUZRwoaVLMh/foN0oWuxFl6fNCQ1x8EzR8MiWppIvUbQJ2gofI52wqNCgFh//EdqiaDrT7Qcafxs9ESY5gunyFcfx6JjbhAo4aEYVEc8+FY+s0ylaH2qaRp01ruvSKUZFN+sGd7qiK7T3+v2+ruuWZSmKYpqmruuDwWDcwpZl2bbdbrcNw9B1fTgcxnGcPNK7KdHjS8dIaG/QMaIzS2hbFJ+kqwEknF+i9TxHlVIBa4B1JmlvsJyuy0z8/JoJWbcPISMYAQPGGPM8z7IsCmPoZPZ9nzqJ807aL6ChOT41hebeiHZzSsAbDTTJR9d1x3ESqn5qjtPUlCiKOp3OwsICHQJ5ic4AZWFtba1er4/OvUnYD9RJzM4MWYRhSO1moe2Kllsq8HxGCpUoOimmlS/qZ6VWl+/7bKSQQNbCMFQUhY4RP9FY8Roc1KNEU6SozBuGkTC1VVGUSqXCGBsOh5QpPvtu3Ppptb7v12q14XDIzgwfZZQjwoMNKvl0CBIa3IqiUJ1p27aqqvV6fW1tzTAM+vo4lmWtC/NS1ANCy4tKV8/TdNnRtImms2jX8byInl95KVq9BBlBCwAYG5kiRRcDy7JWV1d3795dtIqAkmfbdq/Xq1arruv2+/1ms5l3utbzfb/T6VQqlX6/T/9VVbVWq3U6nU2Xp14rx3EqlUoQBAsLC+xM8DbTKAsLCwue5/G9kTBYVK/XB4MBNY4ZY41Go9VqiUZfLFUDZXV1dc+ePZ7n8VMgYXZrinz1ej1q7zLGKpXKyspKvV6fg0M8K3bt2tXv913XrVardB/Ulg16+ajItdvtZrNJfUxBEHQ6nXq9vunyjuPQ2NfoaGpCh4Vt257nqaraaDRWVlbolxI6AgzDqNfr/X6fwkWar9vtdsfli7Jj2zaN762trbEzwdumFhYWer0ez3WtVltdXa3X66J9c1k3xEXr+bW1tWq1yiuibre7a9euTqeDKYjpiJ5fANmKYRZEURSfuTbw27SEDjHNtxm3fsdxXNfl/221WgcPHsyqzG0DXb8ZY/V6vdvtUmoHg0HCrqPpKL7v039Zqu4l0eNFO/Pmm2/mvxkMBgnp5HlZW1uL47jdbq+srCRvYir5EkWboC3SpikZCVZWVtrtNs/aaGY3Gg6HNFRIlpeXzzrrrKwzRQ4ePNhqtfimXdcdTck287Xu6FPBGD3jJiRnVwihimj0+SUJ9cy0iNaHpVKJfqhWq3TU4jju9XpZpzOF48ePLy4u8pTTpMFx+VLOoD0fnpGw/nW5ltMFQPc4HThwgP+mVCrxg7JRtVqlHxqNBmOsXq9P0stmWVatVqPplEeOHEmRzmwPbap6Po5jx3E6nU6/34/j+Prrr0+x3RS7IjXaYnJ7I87puhwLnl95Ec1U1u1DyAjuAZsNcfZzfIMgoOdi0c3BtGTRZvdRz9/u3bvb7Xav1+t0OqOV6aZymWtOk2f4pumXdEvDpsvTfl5eXq7VatRLFwQBzb4bt4mZuAeMbrmhFLqu2+12l5aW2JnjuBHdq8PXLHof3eh6hJan9MRx7Hmepmk0HTFhZCBFvkaLAe00PpN2ckUbkWYzcg8YWVxc7HQ6vV6v3W7v3r2bjT9e05Ku/qQJeHyvJtzjGp95joiqqlR0WWKmaAG66Wt5ebnZbNJA07iHW4wjut9o0h0vKvRLuhUqYf1LS0vdbpfGtXRdp5t+N11+42AmbUt0/6cYbBciWs9vnJ1IVYfo/pc523nC9kZe94AxkfMrL6L3B0poH0IWEIDNBpkn2HA4LJVKiqKkuPcma/QUo9EcUUdawgUmr4qeJklO+CQuaovQ0aFZcHysb5yZCMBIv983DIM/Q3nCG+tpvr6iKKVSiU/eywgV9TiOqfBP+K10+aIiQcVDNJ0FvEDORABGd/fxMJuns2iPGhKte/kTHSzLuvXWWy3L0nU94Z4ifmcv7TqqZ+TMw6SZnxM+wY/6quhImaZpGAbN8h2Hjj4Pw6jGSDHFNOv6U7Sep9qVH1AqHinuDZZZbxQ5ACty22ZUiv2AAGwWIQCbDRJOsFwa9NtR5IpeghkKwITMa76mooAXyJkIwNZ9lxW1wYF6Pl/zuh8QgPHlU59fMiEA2yEK18IAAAAAAACYVwjAAAAAAAAAJEEABgAAAAAAIAkCMAAAAAAAAEkQgAEAAAAAAEiCAAwAAAAAAEASBGAAAAAAAACSIAADyAR/c6jneVmsX1VVeqUpf7FpAd9bRS9CdRwniiJ6LUnyC1VZTvnim+CbTt5oinwRXhgmXH77+Jte6YXRUxdFEb1qnL9wXNp7degY0XvY4zhOyCC9enU0kUEQFPalN/OaLwn4vtryRfbTknU9v27lxaw3UA4BUihciw1gPlQqFbpY0gUsDEPHcaa1cmr6a5pGb7H0fb+A0RdjzDCMIAhM04zjmFJYqVQSWio55ktVVQqrdF3XNC2KooTjlSJfFNpRYej3+zIbiLQtSp6mabZtT2vltm1TwExvYTYMQ070pShKp9Oh1h4VmDiOE/a/ZVmu67KRqN4wDGlt2cnNa76yZts27TTaV7zulSDren4m6g2UQ4AU9LwTADCHfN83DIPeLu/7Po2TlEqlaTVPbdt2XTcMQ8uyoiiK47harXY6namsfIqoAUEX8n6/r6pqqVQyTXPcfphWvkTDtjAMm82mqqrUa+t5nqqqCQ2OFPkaDoeqqqqqOlowDMMQSqcowzB836dMGYZBCaCUTGX9juNYlqVpmuu6tPd6vV69Xhddj+h5sbq6uri46Pt+rVbr9/vU+CuVSvTDpumkBTRN6/f71JqU0Jad13wVrbvHcRyqXaMoGi3w1KWSHQn1/EzUG3mVQ4CZhgAMYPpc1zUMo1qtMsZGL5ZTbLjQlA92ZtZHAaMvxhjFML1er1qt6rpuWZbv+2EYJnem0g/byVeKBlCr1eLzZyiUiqJo3PFKka9SqcR/poJBhUQ0nUIoYb1ej52ZNkmmOE7FYwPq/E4RfTHx86JcLvON0jBRHMfD4XDc8qVSyXGc4XBIQ3a2bUdRNBwOs24jzmu+pM0yndzoXqICT4U/041KqOdnot7IqxwCzLRi9WMBzIdqtdrtdhlj/X6/1+vFcRwEwRRjpHa7TfO+BoNBu92mX+7bt29a658Wap1blkWDWvTLhCglr3wdOnSIfuBzflRVTZj6JZqvTqcTBEEcx71ej2bmdLtdak5lqtfr1Wo1xlilUqlWq4qi6LqeLkbaVKPRoPmi5XK50WjQL0+ePDmt9Y9TKpVWVlZqtdpgMPB9P45jfhQ2xVvnNFTCGOMDmIUyr/nKWr1e13VdUZRqtUrZr9VqFD9kKut6flbqDZRDgBQUGtSGgovjWFEUmhKg63oQBKqqTtgNSYeYPhPui6X+/iAI6PYb2lyRi4fMfKVYnl/D+KbZ9HqOeQ8rH6WRc7xoE7QVylfCMBFjzPM8unthMBiUy+VOp2PbdsJUvWnlS7QHmtJD99uEYWgYBj9km0qdL14YqCElep96iuV5G5HqjXXp2SaeX14dUfEQTafoeTEYDGjvaZpGs/Won35cvqg40XRWOjcrlYqEhwQUMF9TqQ+LNgWR72deyCkAm5t6vuD1Rl7lMMXyqdtRMsnM14TtKMgCpiACTJ/nebVa7cSJE/v376cLTL/fNwxjWk+i8zwvCAK6/YYxtrKysm/fPgkjD6JM0xwOhzRC0u12qQ+Vpldtuvy08pXimnrw4MFOp8N7eYMg0DRt3AUpRb58369UKlQYqGC4rps8vrF9pml2u939+/efOHGCWlGVSsX3/Wk9sc00TV3X6bY9xtji4uLJkydTjFiKNuhpEICaGmtra/TL0ZbiOvQnOr7tdpsG63gUnZ15zVfR2qymadJTH2hHUYHnT4bIjoR6fibqjbzKIcBMQwAGMH00h/7gwYN09aKmwBQbBKZpep7HW2blcnkwGCQ01PJCt6THcTwYDPbv308T/BLSOa18pRgJpBu6qIVB7YbkYVWhfK0rALquDwaDrFtR7MztIsePH6cGHE/DtDZNbSzejU3jgaNDARMS7Xml/l16TIuqqvTEtoR8UXd7GIau69J9Vv1+n99wlZ15zVfRZkasK9hBEJTL5ayjL5Z9PT8r9UZe5RBgphV6jhlwmIK4UcGnIM7EVAdRolMQR4+OzOkNWZfbFPmiAsCDtHRT9VIsL3S88oJ88eWzzlcu9aEE81rPz2u9Ma/HayowBXGHKNwVCwAAAAAAYF4hAAMAAAAAAJAEARgAAAAAAIAkCMAAAAAAAAAkQQAGAAAAAAAgCQIwAAAAAAAASRCAAQAAAAAASIIADAAAAAAAQBIEYAAAAAAAAJIgAAMAAAAAAJAEARgAAAAAAIAkCMAAAAAAAAAkQQAGAAAAAAAgCQIwAAAAAAAASRCAAQAAAAAASIIADGD6FEXxfV/XdcZYEASWZUVRZFnWuOU1TWOMqapaKpXo65VKRVpqJxfHsWEYQRAwxnRdd11XVVXXdcctHwSBoihhGDqOY1mWqqr0RXkpnliv12OMeZ7neR5jjPI4ThzHiqLEcTwYDCqVCh2+hHxRAahUKkEQqKqqKAqtZMp52CydpmmGYUjJ831fVVXf9xO+0u/3KWHD4TCKIsYYfb1QRMvhrOAFI4oiXdf7/X5yvvgBGgwG9Bt++HYUKgD9fl/X9SiKaA/QzoQUUtQbACCqiC0hgFnnuq5lWcePH9+/fz/9pt/vG4Zhmuamy4dhSI34drt99tlnr62t0fJFu+ZZluW67sGDB0+cOEG/qVQqvu9T0LKRqqrURmw0GidPnmw0GhSPUWazk6LtdfDgwauvvrper/PfUJS16cKqqg6HQ13Xy+XyiRMnarUaGzmIGwVBMBqeUVwqmkKWKma74YYbNE3r9XqmadJGDcMYt7Dv+xT5r62tnX322e12mzGmaVrRYjDRcpiXdLEQjy2JruvjugP4n+r1+vHjxxuNRqVS8TxvXD0zLUWLbdbtIl3Xd2AUmiDregMAUlBQT80EagtSPUgXG960neS7/DPhwhlFkaqqvKVImyty8ZCZrxTL93o9apePNr7HHTJVVcMw7PV6FKLU6/Vut1vAna8oSrVa7Xa77BcbPTS0tdFofnl24jjOOmuibQVKZxzHnueFYWgYRvIwHW/jDgaDcrnc6XRs2zZNM+H4MsZ83+/3+7VaTdM02pN84GJCogE5bXc0kqRQKiEAjuO42+3W63VFURqNRq/XC8Nw3PGdlgmrMk60HOZF9HgNBoNqtaooiqZptVqt3+/TGhLOL1VVq9Vqp9OhOqdSqSRHR1OpD4u2n6n8GIZRqVS63W4YhrQ3yuWy0HpE87Wd6/LkSaLhUCrkVHmKBsCiSUpRb4jK67qc9fGaCpn5mrAdBVnACBjA9PGKjGYEVSoVmiY0OsCy8SuNRoN+7nQ6BRz+YiMXBmrn9ft9TdMoAtl0eboY6Lq+e/fuW265Zffu3dS7n3Vnqug19dChQ8eOHaMvmqZJ7QzHcWzb3nR52g++79O00nq9ntxQZmcGRRcWFhhj3W53cXFxZWVFKJHJ69/UjTfeeNZZZ9E8ScaY53mapiW3ooIg4KW03W7TFovWRhEth3kRPV7VanVlZaVWq3W73bW1NXZmrC9h/8dxzHNdrVZ935cwUlG08sDO7CjaabVabWVlZXFxMe9EFYWEegMARBV6iAM4jIBtVOQRsF6vV61WJ1+ebpFSFGU4HC4tLQ0GA03TLMsSHSHJWrVapXulUpBZlrY/wY9OruSGCx1liqx83w/DcFzAxtcfBIHv++VyWVGUUqk0HA5Tp1CI53mKoqiqmtyKGgwGlmVpmjYYDJaWlobDoaIolmU5jpNuuxnZTjmUSfR4DYfDUqmkKEq5XPZ9PwiC5DWUSiXHceI4tm271WqVSqUoiobDYcIdpDNXz09OURRd1w3DGAwGcRzTzsx0i7MyApbahPVGChgBS4ARsB0CI2AA00cDI9RA930/iqIoiqh5tOny1HAfDAY03Yua5kWLvhhj9DwAav4ahqGqKt0NlTBFanQ6ZRRF3W630Whkfc0T7fGNoqjZbIZhSK0Nz/NUVU2Yheg4ThiGFGMHQUAH1zCMcflyXZca1pqm8WCmXC6LPjcixVSikydP7tu3b7QDO+EeIZqyRY/foDvcBoOB4zhFm4IoWg7zIpqvwWBAMQOVEzprSqXSuHJCAXypVNI0LYoiGrOV8Pyeou1ny7KGw2Ecx6OdINSbILSeouVrWrKuNwAghTnp+pp7GAHbqMgjYKTf7/PGUBiGvu+PGyGhURT6meclxQiJHJVKpd/v08+aphmGseUISaVSOXnyZLValdN9K7oJTdPiOKZIgxocURR5npcwokXnYBzHkzdQXNelO9p9319aWkoxX060HPJc0KPh4jhOvrdtdNCA70Oa3CWaVAlSlEPJUtQbnU5naWnJ931FUUzTTN7ztm3zLPNtjVY7G81cPT85y7I8z6MnZC4vLyfM956WeR0BE6030m0CI2DjYARsh5jP/h6A3PFmED2ZTdO0hNY8n+XFn49nGEbBoy8KNugR8wnL07Mf+/0+zdYr4I1tJIoiunkmCAIah0w4XvSOAZqfQ9e5fr+fEH1Ru5CGKRhjmqZ1Oh05gaht29R00zSN0pxwYS6VSnSAeJPLtu2CR18TlsOZEMdxvV6nBx7Qg3koDBu3PO+44b0A/DmWOwr1a/CnxYRhWK/X5yOqzIVovQEAKcxJ19fcwwjYRsUfARNdP+ViXnuhZPa0ia6figSljYoKFZspJgnlcAcqYE/2zNXzE8plpGheR8AkwAhYggLWG5AFjIABAAAAAABIggAMAAAAAABAEgRgAAAAAAAAkiAAAwAAAAAAkAQBGAAAAAAAgCQIwAAAAAAAACRBAAYAAAAAACAJAjD4H/TWI13X+ft/E14AmhdVVde9qiKKInpvadH0ej3G2IRp2/jeD3r95bjl6WDRi4MZY6VSafS/mapWq2zkxa/JZuV48aI+HA5pt0/yErB+v09v2WaMxXFML+rZlO/7qqrytxv7vm8YhoSXL9FblfkZTf8t4HtvioyKOhX7rCmKQmWDnXknO38/+KaoOGmaVi6X+/0+faWA5ZAJ1huiDMOIoojn3TAM3/clvNSIn/6lUok2PcnJValUeIWjKEpCPZ9XvuYVf1e7ZVmTHy+AjIw982GnCYIgCALDMPg10nXdjK6XqVHbfffu3e122/f9TqezuLiYd6I24ThOtVqNokjTNN4e0nV9XOxB+/n06dONRsMwjHq9vrKykrB+TdOiKKL2NGNsOByqqur7vujxEo2FbNvu9XqqqoZhyNsNQRCM225ex0t0P7iuy78YhqHv+7quJzSM6NSoVCr0c7fbXVpaSji+1IYeDoflcnl5ebnZbAZBUCqVeANuQqLHixpwFJ/zZIRhON13TG9fAeuZ0eKtqmqv17NtmzfgJl+P0PKe59m2HYbh0tLS8vJyqVQaDAYJ5zU1H8MwdBzHtm1ajE7PTZfPqxyK1huiqCak3bW0tNRqtagnMes+RMuy6IcwDDVNMwyDLqMJy4dh2O/36edarba8vJywH6aVr6KdX3nhNSHVgfTOYrpM55sw2KFimAVRFMVn+ikn76EfPcRRFNFKNuU4juu6/L+tVuvgwYNZlbltoCYvY6xer3e7XUrtYDBI2HVhGMZx7Ps+/Zelet276PGinXnzzTfz3wwGg4R09no9+qHdbvO+dn61GIcu4eVymTF25MgR0UylQBf+AwcO8N+USqWEdKY4XlORImsHDx5stVp8Da7rOo6TsImVlZV2ux3H8draGv2GZ3BT/BCTdMOVKXbF9ddfH8dxv9/vdDrJOYp/sZZIkby5sa5UU4FP0ZpPcbzWxUL8DNqUcgZtKzwjYf1TKYeiROuNFNbtKM/zUuz8FI4dO7Zr167RnPKobFPNZrNerzPGGo0G/SZ5cDWvfGUtl+tyHMfHjx8f7QS0LMu2bdHtZk00U1m3DyEjSryzL7SzIo5jfqGlbhtVVSccPadDHE9Qx7muS5NSLMu69dZbd+/eXbTZDnx+Tq/Xq1arruv2+/1ms5nwlSiKVFUNgoAqJtqNosVedHka7Tl06BB1djLGVFWtVqudTmfT5WluCWOsWq32ej3LsiqVSqvVGrf+hYWFXq/Hu1prtdqxY8fq9bpoT57o8aXRuWPHjvFmQRRFvV6PmhQbpTheuYjj+PTp03v27Bk9BSb5oud5zWaTjjKdmJsuZtu253mqqjYaDRrbTFfxih4vTdPoeNVqNfpNEAS9Xm9hYWHT5UdrCZnnftEuQ51Op1qt8kZMv98/dOhQp9PhY86Zor2xsrLSaDRUVaVhsU2XdBzHsixFUbrd7oEDB2jas2VZfER3nbzKoWi9IcpxHNM0oyhqt9vUvJZTehVF2b1796233mpZFtXh4/b8OqZptlot2hv82rTRtPJVtPOL5XRdJq1Wi1+DgiAYDAbTKod5kdM+hKlDADYbsj7BXNflLU4+6Vza7QGTo/TTfBv6De2ZhK/kWNErikLhh67rNPgwLqm0/tE5TpMkkiayxyMdYKLpTDcVLY5jaokGQWDbdkJSUxyvqRDdD3Tvja7rcRzzfTJ6UqxDQdra2hoFvfzAJR9f0mw2aagtxRQs0eV5qaASEgRBcmCZVwBWtDsxqEg7jkOVhmEY6fZGioCZzujRNiIbX575+ofDYbPZHK09Nl1+WuUw63pD1Gh+adfRvVVZ324axzFNO6S79eiXCQEwBWkLCwudTodPHGUTHF+2vXwV7fxiOV2XqUqn+Yd0jOiei2K2cyaHAGxGIQCbDVmfYLR+mshOY6NFu0uE0EA57QFN06g+TZ7DnUtFT5ubvDpTVZUnMgxDuoQn3Msxim5bktOTTXt+8m2lOF45oq6H0RNhkv1Dhyxh+IudmejSbrcNw6C7OOI4HgwGNH10cqn7vylHkyzJ8gjAin8ZooZvwiGeinK5TBN06WEwhmG0223bthPC5n6/r+s6jYOZpqnr+mAwGLdwXuVQtN4QRROGG42G7/t0V5uiKLQzM9riKHquSRzHVBVPeH2hKjFh+ItNL18FPL/y6hiV0wMoGQKwGVXERjbIRydeGIbUU05nbzG7zaimoPDGNE1FUQrYmufhK7+4WpaV0IriTwukZgpN9E+IvkzT5Ddv8IuQhKcL8iLBW6Ku6ybMupmV40WlnRpS/DmNCVcjz/NotIFuuaGFE/Llum6v1yuVSr7ve563uLh49OhR0VZvCjxJPC+UgKy3O+tGSzUv6hLqw8FgcPjw4ZWVFTrBh8NhtVpNqDeiKKpUKpZlnTx5cu/evZ7nDQaDhHKbVzkUrTdEWZZVrVaHw6FhGKZprqysHD58WEL0RR1n1HGjqiqdbglRgWmaNOSlaRpfOKHezitf84oODb9JkjE2HA5Fn6wDMC0YAZsNWfdwUCfoaOcQdU0VLQaj4RQaSOl2u7VaLWGeGP9KjlMQaR/y3ThuXJFSSANftVqt2+0mzGMZXRW1AChgY+JtxHSxEE1bok3Tb8ZtN8XxmgrR/TBaQtiZ0y1hZIAW8DyPQkqagpgwlaVcLo/en2MYhud5nucldH5vSvSRCbQfKKTnxythcDuvEbCivZlgtGBTGU63N0TnEei6TgXDMAx+pvR6vXHlUFVVmsbG5yzwwfNNl59WOcy63hA1GAzoURa003zfN03TNM2sRyz58D79l64sCSNUtIBpmlRj07GjQbNNl59Wvop2frGcrss0EYCmINK0BarJi9bOEa03MAI2oxCAzQacYKnlUtFv53hNiFbIL//UpSd6fFMsz/sOeYhezNmqmUoRqMzE8cIURG4q9YYoCcdrJsphCrkcr+2Y8LqcYwdipuY1X7lA+3BG7biWEwAAAAAAQF4QgAEAAAAAAEiCAAwAAAAAAEASBGAAAAAAAACSIAADAAAAAACQBAEYAAAAAACAJAjAAAAAAAAAJBF7/SLMitEXPjLGtnzh47waffksf+VIMV8esvEtzAkvwuYvVNU0LQgCej+v7/uiL1RN96JY3/cNw6AXWaqqmvCiWNEXMU/rheCi+RJ9QefoC3DpNxO+ALfgx0s0X1EUUVWj6zrfe7QnhdIpSvR45fVC8KIdr1kph7NyvERfxDwrZuX8KtoLlPPCy61pmjvzzZwzCgHYfDIMg67NmqYxxmzb9n2fRyM7h+u6jDHLskbfSzj1dyJPBTWbut0u/WwYRhzH49LZ6/U0TTNNczgcappWr9ePHj16+PBh0Y2K7gfP8w4fPtzpdBYWFizLGg6HpmlWq9WE9fu+T1fiWq0WRVHyVZkaZLxFSCVWwhVFVVXehKVTxnEcRVFs2950+SiK6E+nTp3au3fvqVOnXNdNaKDM0PESypdt24qiDIdDHnElLDxFKY6XUDmclqIdrxkqhzNxvPilhCooijNnPfpis3N+7bT2zDgUMDPGgiCgAmkYBpXGvJMGSQr9qnjgtvOm8yAIqL9TtJtzLimKMtpnOSHR00T0eGmaRhct13X5wYqiaNxXLMuybbvdblM9OxwO4zim4SOhdIqOiFLnbhzHw+FQ13XDMNrttm3b4y63lAXaA5qmUbdoFEV0tdiI9htdTuI4juNY2iV2dNhtEv1+X9d1y7IURTFNU9f1hIbXrBwvJpivTVOY4pqS7iuT7w3RckhfGR02p9M568tl1sdrVsrhrBwvQuFKHMc0ajThdmkZ+kzYn1PJ17yeX2i+jlIUJcXsgwnLIWQBAdhsEG3QG4bh+/7CwkKn0wnDkKapsJ1XYVGd7jgO1fKGYaSrYrIOwNgvtlxt23Ych42vEEfT02w2W61WHMd08RNKZ4rlgyCI47jVajWbzU3TM4rSz4sf2+q6Pjpxhaa30UQp0f0vepRpuzTlhkZNDcOgIDB5/cPhsNls0sFK2O5sHS8mki9N02gmGw3hhmFI/QhC6RQ9vumO1+TlkE2pgShaDiUcL/5z8cth8Y9XHMeGYQRBMDrqOGH5L3IANivnVwFnsuSCdrWiKKqqUhfz5DUwArAcYQB3Pvm+zxhbW1vTdb3f71O1SNeJHaXT6cRxXCqVDMMwDKPf7y8uLlJ7sWh27dpFsUe1WqWGFAUem7JtW1VVXdcXFxdbrRatQdd10f0zbv3j8JHDZrO5srJCEx5odsqmqBzatk13nriuu7q6mrATaA+4rtvr9XzfVxRldXWVR7OTE935tN12u60oim3bdFNNp9MZt37HceiKNTqwbFnWrB8v0XzV63X6Fn2x0WiwM/N+MyV6vETL4bQU7XjNSjmcleOlKMquXbviODYMo1qt8upLQlIzNSvnl2i5nVdhGK6urtLkzzAM6QbyhYUFCYcAtkW0xoFcRFEUn+kc4rfHJB/ZZrNZr9cZY9QqYowlzLmfV6VSqVQq8f8eOHCAMWaapuh6sj5ePJHVarXdbtNKer1ewibW/TVdVCmarziO100rr1QqCevnf63X691ul9ZAk5E25TiO67r8v61W6+DBg3Lydfz48cXFRb4Gmqw1bv38ykfbCs9IWP9MHC/RfA2HQ4oByPLy8llnnSUnX0LHS7QcUt7jOPZ9n/7LUnUPp8hXpscrnpFyOEPH69ixY7t27eJrME1zwtuf6Os0ea+A+ZqJ8wu4I0eOMMbK5XKtVhO6AW/CcghZwBTE2RALTmmj+QPU72hZVq1WW15eZuJTR2YdPcGJfuY7jU/wm5zoaSJ6vMji4mKn0+n1eu12e/fu3ZT+TZek40g3bywvLzebTV3XbdsWvelWtLPW8zzbtnVdbzaby8vL/Hlf48oVpX/37t3tdrvX63U6ndGL+qaCIKBph2EYmqZJ+1C03Ire40cURaFb7+iQJd+rxm++9zyPFkuYfD8rxytFvqIo4rcs0liKUAr5dlN8a/LjlaIcTmWKlGg5lHC82CyUw1k5XpR+RVFM0wzDkKYjTriSuMBTEEnxz6+d1p4ZhyaLrmtg0H0oW353wnIIWUAANhvSNegrlYrv+3RxVRSFJuLLSG4h0f2p1WqVpkkIyToAo+f80mWMV4jx+EdQ0AOd4zPz7H3fp2MtlEiW6sI8ui26ZCZU9Pz2dL4t6vic5Hkww+GwVCopiiLhniLRbfHbzS3LuvXWWy3L0nWdDsqmy8/K8RLN1yi6b0RRlFKpNBwOhRKZ9fFKUQ7zavhmerxmpRzOyvHafpkvZgA2K+cXEDqVeCGk/074nDYEYDlCiZ8N6QIwmBY5I2Cj2yrmhRn5Grct5Av5GrctoeWRr023hXwhX5AFBGA5wkM4AAAAAAAAJEEABgAAAAAAIAkCMAAAAAAAAEkQgAEAAAAAAEiCAAwAAAAAAEASBGAAAAAAAACSIAADAAAAAACQBAHYbOCv4KBXv2uahpeAFZno8aJXXvLlGWNBECS/lENVVXpxM33Sb7ad8B2NdiC9PzSOY9M0ExY2DIMv4Lqu7/sJx8vzPEVR+DGVdvKmqDeE8sVyKocSzq9Zwd+5TPvf87zk5WfieKWAfM2Wec3XTJjj+nC2oMTPjCiK6FobBEEYhqqq2radd6JgLKHjZVmW67ps5GpkGEa/3x+3vOM4URRpmkZvsaTX3k85AzuJoiidToeuRrRj4zhObsv6vu95XqVS6fV6lmXxdvCmTNNUFIWKAWMsDMN6vS7nraOi9YZQvnIsh5meX7OiUqn4vk8/U+nlOd3UrBwvUcjXbJnXfM2Kea0PZ46edwJgIpqmdTodRVGonrIsKwxDx3FQbRWT6PFyHIcxViqVNE3r9/uaptm2XalUxq3ftu0gCIIgoJa9qqoLCwutVgvlgYj2Q6+uri4uLvq+X6vV+v0+XZxKpdK4tmwURfV6vdvt9vv9arUaRVG32200GuO267puqVSyLCuKol6vV6vVOp3O4uLi6uqqaNaEiJZD0XzZtu26bhiGlLU4jqvVaqfTyTBLjLHsz69ZQW0m27Y1Tev1epqmlUol27azPl6i55emaa1Wi7bIGDNNM4oiOihTMa36cF7zVTTzmq9ZMa/14cxR5PTCwlRgjDgv6U6TyY9XqVRyHCeOY9u2W61WqVSKomg4HI6rE6mhMHq5Slc2RPMVx7GiKLQtXdeDIFBVdcJWC22LPhNSG0WRqqpBEFDnKG0uRTqFlh8Oh6VSSVGUcrns+34QBJOvQWjJIAh83y+Xy4qilEql4XAolM6sy+G8bkv0/GI5lUPR86tSqQyHwyiKSqVSq9WybTuOY8dxSqXShFvM63hR3TVJ1TFJvZFXfbhxW/ORr6zr+WnlC9JJUR9CFtDfMBtOnjxJPzQajXK5rOu6pmmNRiPfVME4oseLN8R54ykMw4Ta0PM8PpmNd7geOnRoWunfaUql0srKSq1WGwwGvu/HcUxT5MehRrmu6/v377/llltoGhifDLYp13UVRTEMo1wud7vdxcVF0egrBdFyKJqvdrsdhmEQBIPBoN1u0y/37ds3zTxsJuvza1ZQ7zVjbDgc8plvCdFXXsfr2LFj9AMN1jHGoihKvsdSSF714bzmK2vzmq9ZMa/14czBCNhsGO2RGu2LwpC9HHyq9IREjxd1t9N0oDiOe71epVLZslOQhlM0TaOJHAnrH2c7+SryCJhovgaDQbVaVRRF0zSahUhRR8Lx4j/ztMVxPC6dtB7f9/v9fq1W0zRNUZRqtToYDITSKaEcjn6X/5CcL3bmqLE8RooyOr9mYgSMEkY37MVx3Ol0qtVqwlemdbxEyyHflmmamqbRIPOE352w3mDTqA+T+1A2mpV8FbCeZ9PIF6STrr0BU4d7wGaDoignT55cXFxcWVmhu1ctywqCYMtnXkEuRI8XXeQ6nU69Xm+329SX73neuM7UOI7DMNR1nVqHnU7n4MGDx48fx7MxieiFvFqtsjNHYW1tjX5J/x23ftrVjUZjbW2t0WgoikIHetPlqR1vGMbCwgL9lzHW6/WEEpmCaDkUzZfneUEQWJZFC6ysrOzbt48PT2Un6/NrVpim6Xler9drNBqUO3amsG26/LSOV4qG8vHjx+v1Or/fTNf1MAyn1f87rfpwXvNVNPOar1kxr/XhzMEI2Gyga+pgMCiXy/y/OGEKS/R4UY9UGIau69JX+v0+3SmUvAlqcZqm2ev1KIrI1KyMgImiXNDN9Kqq9vv9SqXiuu64iYi+7xuGEYah7/sLCwu+70dRlBCw0VOnKpVKv99XVTWOY9pc1j2+ouVQNF8UAPAFyuXyYDBIWH4c0eMr4fyaiREwumuRHsVRLpfpARsJX5nW8UqhWq32ej06QKNp2NKE9cZU6sMUgwAzkS9REur5XPIFJEV9CFlAAAYAk5rXAIw2QVuhTSdHR6O5mPCiRTuKt89oc0W74KXI1xS3WygzEYDtBJNPads++WVeTr5EyZmCCLDDYcYtAAAAAACAJAjAAAAAAAAAJEEABgAAAAAAIAkCMAAAAAAAAEkQgAEAAAAAAEiCAAwAAAAAAEASBGAAAAAAAACSIAADAAAAAACQBAEYAAAAAACAJAjAAAAAAAAAJEEABgAAAAAAIAkCMAAAAAAAAEkQgAEAAAAAAEiCAAwAAAAAAEASBGAAAAAAAACSIACbDUEQMMYGg8Hofz3PyzNNeYiiiDEWhiHfFf1+P47jhK/wfUW7q9frZZ/MzFFeKGvsTMHg/y0OVVUZY4qilMvlfr8fhqGiKGEYjlvedV1VVfv9vq7rURTRkVUURV6Ks2EYRhRFpmnSMdI0zfO8AuYrjmNFUeI4HgwGlUpF0zTGmK7r45Y3TXN0gXK5nLz8rKBy6Lou5SUIAsMwkuuZqeAFXlXVIAgqlUoURZZljVueDpCqqqVSib5YqVSyTqQEtNtVVbUsy3EcqjcKWL8BEa3nc7x+UQOAtwe23ChvYAyHQ978GLfwDOULCiGGGXHixInFxUU6apqmlctlav3sKLxtV6/X19bWaM+4rjtup0VR5Ps+/2+73T548GC+WZgK0zTL5TI1vxhji4uLJ06cyLwIxjEPithIIyk5qaVSyTAMxlitVqPf8GRvtK7trut6unSK7k+Khei7VGDCMEzeD7QrhLZlGIZpmtVqlTF25MgR0UQyKdX1YDDwPC+O406nQ78JgmDcwq7r9vt9vsDy8vK+fftS5KtoTNMcjWT279/PGEsIhKZrtMqKzxTITfE9v7a2trCwQF+n0y1T2yxjW6J8RVG0urraaDRoo1tWNbOFcjpakxRH1vX8tK5fKXb7wYMH2+02X4Pv+wn7n2rCOI5Hy+Ec5AsKQomz79WD7YvjWFEUaiaqqko9MWzurklbiqJIVdVqtUqtw16vV6lUthxJCILA931N00zT5PtQSnqzMloA6Of/OZ8zHlQZLYe6rgdBMFoaNzJNkzrkyuXyYDCo1+uO43ieN27/06oMw6hUKt1ul6KgXq9HQyuTS7hGboqGfagyDIKAxt8SCkk8MjQ3yT6n9PCuU9ocEy+HCZ2vU+F5HnXrDAaDcrnc6XRs2zZNc9wh5unnu4uKh+hlpWjnI88vFXLGWK1W6/V6WeerXC7TVsIw7Ha7lUqFGrUJ+z8Mw16v12g0FEWp1+vdblfCNT3rcsgrGfaL51fW5SShKps6OkxxIQf55dTzbNvXL9F6nm/L87wwDA3D2HK4Po7jbrdbr9cVRWk0Gr1eLwzDOcgXFAEO0mw4deoUdS03Gg3f96ljplqtttvtvJMmWxzHnU6Hfq5Wq77vJ/T4Oo5j27au64qi+L5Pvzx06NCxY8dkpDUzdCVQFMU0TcMwqBjwQlIcdOExDMN1XcZYp9NJblAyxizLcl13bW2NMVar1VZWVvjA7+wKw5Dif95M6ff7Z5111o033ph30n4BNQd936fRnnq9TmfNuAZHu92uVqt04fd9nzqJ9+7de/LkSaHtymz4TqJerw8GgzAMbduO47jf77MzO0eIaL56vd7i4mK3263VajSi5bquZVkJgQe1C+lnOr94RZedrAMhqtV93z99+vT+/ftPnz5N3SKYWFVMovX8tK5foucXv/TThHCKc6iRMO4rQRDU63X6ud1uU8mfg3xBEWAEbJYUrZ9MvlKp5DhOHMe2bbdarVKpFEXRcDgcd+cDVWSjzYV53YdyTmTRnlFSrVZ7vR5FVoZhaJrmOE7C8oqi6LpuGMZgMIjjeDgc0i0ukxM9ylmPgBFN01RVVRQl9d2bco5yr9erVqvU9Pd9n+KQCb87r+cXO1OMM91EqVQaDodxHA8GA+rGTt6fjuNYlqUoynA4XFpaGgwGmqZZlsVvkc2IzGbDvJaoeRoBI6L1/Lotpkhnuv02uq2NLYRRg8HAsixN0waDwdLS0nA4VBSF7ktMsa3JZZ0vKAiMgM2MTqdjmmYcx3RbdhiGdKd43umSajgcMsZKpZKmaVEUUR9Pwn3ndC97EAQ0jSqO42az2Wq1Zn2/URnQNI3KgKIonU6Hd9QVh23bmqZRs1XXdVVVh8Oh7/vj9r9lWdQAHW3001VQXqIzQGNfYRjSUBhjbN++fSdPnixaOaQHHtBdakEQRFFEt3YkTIFzXTcMQ8uy6Pyq1+t8gHpyRdsPlHG6P8f3fWpZUu++kBRTEKmKo/JP7bDhcDiu/NM5QoN19CiO4XCYdfTFsh+xVFW13W7XajU+r7VWq3U6nXmagjhPROv5aV2/RMtDFEXNZpOeEaKqKk2STJitR1Pf6fEbuq7TBEvHcWY9X1AQGAGbDXRq2bYdRRHNv1dV1TTNyXti5oNt2zzLvOj2+/1xMZjjOKZpUnUWhmEURdSsyfoehqzZtu15HjUXaFyFBgZF546LStEzSqNJo/ucz8Qbx7IsmmRrGMby8nKKC1gxR8D4M0WoHPIjODkJ1TUd09GyxG8M22iOzy8a+qP/VioVmoUoQb1eX15epocuep6X3PVAo5T0My+HFIZlmkgJ5ZCqml6vt2/fPmk7X6Y5GwETquendf1KcW9VHMcUQdG2oijyPG/cCP/o5Au+LRri23T5WckXFAQCsNlAHeeKotAnDRHknagc0Oxq13U1TaP7AZLvASP0LAe+9zRNm4+9N1oY6LNoARjdyEGXJcZYFEXJbVnTNOlxKZQdesZAipuYixaAUX8k7QRVVWlgNsXDKrKurulsorCKMUavBNjyyebzen6xkUaknBiMn8685Gua5vt+wgNvaRYADfJTn4WEe8AkNBuoC4YmWFLWJORLpnkKwETrebL961eKQIVvi1dZyV+hKjGOY3qJyGgXcMJWip8vKAIEYLMh3Zzs+TbhBYxa0tSqZmmf0lZAVAD4jenFfApiClPJV9ECsGkpYLmd1/MrFyiHo+uXny+Z5ikAS2Fe6/mZyBcUBI4QAAAAAACAJAjAAAAAAAAAJEEABgAAAAAAIAkCMAAAAAAAAEkQgAEAAAAAAEiCAAwAAAAAAEASBGAAAAAAAACSIAADxhijV0bwNxrT29+3fMGxfLqub3zDYMJLaXzfV1U1jmN6SRF/qWK2qcyeYRhRFCmKQi8bofdgSniZjKIo/M3X9CrhKIqmW07obTNBEFiWRb/Z8sWX28dfdDscDqmozMdLVOjdtcPhcPS/W77Pp9/v0wtVGWNxHFMZG7f+uTy/8mLbNv3guu4k5ZDOwSAI+v1+uVymupG+uCVauFqtbjfRE0hXDieX1/WLNkGb4/+dg6oj63o+r+vXvNbzo29g13U9jmNVVRNeXB4EAa+lPc+T8Ip52BTemDkbsn4xIj97OVq/6PvUwzCcVpISLC4udjqdXq/Xbrd3796dsF1K/2AwKJfLy8vLzWZT13Xbtnn7ckZRfsvl8mAwWFpaarVaQRA4jsMvMBnxPM+2bV3Xm83m8vIyJYCd2c/bF4ahqqq8hI9eJ4RM2AYd3S5jLI5jz/M0TfN9X9f1hJXk9aLYhFhoU5qmbXwjJ29abeS6rqZplHHXdbvd7tLSEtt559e0pKsPKejlr7dWVTVhPXQIwjA0TZOuCKqqjiuTYRjyUs0vIrZti/ZxZF0ORc+vaV2/RFF9te5CvDExm5L5ImbRciihnmfTuH7xTjqh7WZaz0/lRcyi1y/TNB3HCYKg1WotLS1Rhcy2qreXl5drtRrtwyAIwjAU3Z+wXTHMgiiK4jMt0ex6bizLqtVqdOoeOXJk6uvfPt7XWK1W2+027Zxer5ew69b9tYDDeulUKpXR/3qel13xG7Wubb0uGdtk2/boNWBxcfH48eMpEpli0wcPHmy1WnwNrus6jjNu/VEU0SmZbluppdgV119/fRzH/X6/0+kk5IhbWVmhM2ttbY1+0+12E5af1/MrL2edddby8jLfn47jDIfDcTs/PCM+01Lk/XSbKpVKvApljB04cICNDAtMbstStJFQOUx3fuVy/aINlctl3pad0MacFkqm9fzGFaa7fqXYbtb1PDXMeAQVn2m8ZZ0vmnrAJTeKeJVOlXy73V5ZWRFNJGwfRsBmQ5zxCNjCwkKv1+P9mrVa7dixY/V6XbTHS8JoQLPZ7Pf7rutWq9Ver8cSexypM15V1UajsbKywhLnK84Q6iyMoqjdbi8uLjK54zC0D1dWVhqNhqqq1F06lTV3Op1yucyvXq1Wq9lsTmXNyeI4Pn369J49e1zXpY755LZUnNMImChN0+r1+rFjx2q1Gv0mCIJer7ewsJD8Rc/z6ERjZyqcTReb1/NrWtKVjWaz2Wq16Gdd18vlcqfT2XRJy7Jc12WMVavVW265pVarxXHsuu6487HT6VSrVd551+/3Dx061Ol0Jhmx2Q7Rcih6fk3r+iUqDMNOp3Po0KFut0u/0XW9Wq2ura1t+d1Y4ghYuvVnV89P6/olWttIqOenMgKWDm1lcXGx3W5HUUTDYpsuyZNXqVRarVbWE2dgHARgsyHrAIxYlkWTvviAm2jxkDCjWlH+t9DyyTPjKrjR9FOzJo7jIAiyvjBnbTS/FKUoiqLretZTQDVNoxKyLjSaVjWiKEoYhtQctCyLJhG5ris6NUI0PXTPA589T79M2G5eAZjotvhZTGf06J11m6JGydraGjVed+z5NS2i9SEFVDRhj46U7/thGG65/23bbrVafHRrXPmnytNxHOrjMAwjXenNuhymO7+2f/0SxVNI0z51Xad4eBIyAzDRciihnuc/b+f6Jbq8hHp+KgGY6H6mqcWKooz23SSkmdZP1Tt1IiwsLCRMCYaMIACbDXICMKJpGp/TIirrCwlvmlAzhe6RoHkCmy5vWZZt2+122zAMXddpMg+fIT27aOJEo9HwfT8IglKppCgKn6mfHdpEHMd0E7NhGO12e928wemS1n3IGKP7wikI1DQtYdOzMgJG4jimHAl9i9pDCcNfbH7Pr2lJUTZGO5gmUS6XgyCgGVyu6wZBIDRbjBq+ovd0pTN5OdzO+bWd61c6iqLQRoW+VeQRsKzr+Wldv9Id5Uzr+VxGwKjKVRSlVCoFQeD7fqPRcBwnoTuAUkiNqEzTBgnm4QkwsH2mafLOD16pyXmihhC6slJrgyoO6n0ct7zrur1er1Qq+b7ved7i4uLRo0fnoHVoWVa1Wh0Oh4ZhmKa5srJy+PDhrKMvxthgMDh8+PDKygoVmOFwWK1Wpxh90R0v7Mx1i98zPa31j0MxPD3QL4oi2m7xI6st8cYuzwudCOOW9zyPhrzoziJ2pnE5bvl5Pb/yQodJ0zTe3VYqlRLmfSmKMhgMPM/bu3fvyZMnLcuqVCoJHXOu6/I2GW94ZdSRN0q0HIrK6/rFN8E3ShVy1tvNWtb1fF7Xr3mt58vl8tGjRxcXFz3P832/VCr1er2E6ItqGDZSzzuOgycnyYcRsNkgYQSMwhhVVWm2NxUM0U1ImHpEw1+1Wq3b7dLPNAi26cLlcpnuE6MlDcPwPM/zPNGnDBXNYDCg50fT9Anf903TNE0z694sXddpBxqGwWdu9Hq9abW56dJIjyem0U7qWhYtV6Lllj9xjv5LaUgYyclrBEx0KhHtB+qzoFM7eSWUcc/zTNNUFIXmqFAn8abLz+v5NS2i5ZaXdir59ATw0elS6/DpAOxMv77jOLZtjyv/fD3UEqVpS0IpXLeeCaUoh0x85IFt+/olijaqKArd0USbm3CjMkfAUox+Z1rPT+v6JXrvooR6fiojYKLlNggC2oG+74/eFzoupqXRP6re6aw0TVPmZBMgCMBmg5wAbPsVRwFP4Bxvis0U9eTxywkVDwn3PNAOZIzx+Z/z8SoVIbMyBVH0eM3KlJtZIXM/TNign4l6Y1bK4Xauy0Wegiihnp9KOcy63KIcQqZ2XMsJAAAAAAAgLwjAAAAAAAAAJEEABgAAAAAAIAkCMAAAAAAAAEkQgAEAAAAAAEiCAAwAAAAAAEASBGAAAAAAAACS4HWZs4G/n4G/dJg+p/VqDv5CVXr7p2EYjDHf90VfqFq0V0LNa74IlQF6iyJjLOGFrclrAHr7bRiGqqqGYajrOr1ZJeGFtvTGW/4iGnr9ZcILc+ktN7qu863QFoXSKXp86YWqvu8bhkH5UlU14YWqcRxrmkZZY4yZpul53pbv56FU0cKMsYT9Ni2iL1RlZ1752u12a7Ua/Uxvy8k0naK28yJm2gmu6ya8iJm/AJcKA73H1jCMrF/gztNDL2KepHjwF4IzxiZ/IXjB63k6mvxMoRMtDMM5eP+S0PmVVzmUI5f6kH6gF4IXrVqDcRCAzYbRk4pOZno5PV16t6/X62maZprmcDjUNK1erx89evTw4cMp0jmV9EzLtPJVNNQsNgxjtDWTokEPRFVV3rbTNI0x5jiOoigUh2wURRH96dSpU3v37j116pTrugkXWtu2FUUZDof8AKW7Kot+xfO8w4cPdzqdhYUFy7KGw6FpmtT02VQYhr7vU9Y0TfM8j1rz1JLYyDTNOI593x+toCiEEEqnKL452iFBEJimmRB9McYsy4qiqFar0c++7yuKUrSWCgXq9DMVFQryHcfZdHmKuBhjVAj37dtHx2tcvqrVahiGnueVSqUwDDudzuHDh48ePZpNbv4Xr5qoC4Ax5vs+HbVNl6cSRcEJY8xxHMMwoigaV/5npZ6nGpuCScaYbdu+76uqWrRymILQ+ZVXOcxaXvUh30QQBHSOGIZBvW+Zbhe2SfjV45AL6u7Nrp/MsizbttvtNp23w+EwjuPkHuVNFa0nb1r5KjKqfOXseerBpUqDyuTc9LfRAMLky/f7fV3XLctSFMU0TV3XB4PB5F/fclhpKsrl8mAwiON4OBzqum4YRrvdtm2bum82RYeVeqaFtkWNbJkXFApXFEWhUyDhCNKoI3XMU9aoe17CiEeKrwjtw3K5HASB53lxHLuuGwRBpVIZt7Druo7jNBoNin9KpZKiKFRIRNOZQhzHKRqjvDQmDI/kVc9TkaOjzAvVhL0kQRDQeJ3oiZaCaDkUredFz69plcOsaxtaP+090X0ovz5UFCVFJyylcDSnIA0CsFlCgx6MMV3XHccRbTImGC0GzWaz1WrFcUxXCKH1ZN3TI2pa+SpmxeS6LoXlqqqmu0iInv7zGoDxpgM1IxhjhmEkTHni+3k4HDabTT5AMW7/09Q+OnlppmIYhnzy2ORSNAKCIIjjuNVqNZvN0fQkrJ9mRtFIwtrammEYNEdoHJpuFMdxFEWjl/PsKIpCE8xGp+fRQRz3ldHaks+xzDqdoqcGFQmagkh58X0/YYoaT79t261Wq1Qqrfv9OqProSKhKApFOELpFMVLBZWQIAgSjhRjjCbNrq2t1et1TdNoCiJLPL/4zzLredEAjE6lhYWFTqcThmFhy2GKel7o/JpWOcx6xk26ACyX+pA+qSWg6/rkVxYEYDnCFMTZ4Pt+p9OpVCr9fp/+q6pqrVbrdDpTWb9t2zQ7v9ForKys0C9T9MwVLZ6fVr6KZm1trVqt8kZMt9vdtWsXXdTzTdiMoj3ZbrebzSY1HYIg6HQ69Xp90+Udx6Gxr9EO7ISAql6vDwYDHqc1Go1Wq5Vi/rDo+cUHDZrN5srKSqPRUFWVJhaOW17Xddu2aXxvbW2NMZYQfS0sLPR6PZ6RWq22urpKjWahdIqK43h1dXXPnj38DjfLspLb9Kurq5VKxbKsXq9HkzDpi5mmUxTtSSoeVFp0Xa/X6+PqeV7k+AARjYONO76O49BdIu12e3FxkX4p4cYbCubpBiF2pl+g1+stLCxsujwdl4WFBc/z+FUvYRBsVup5OpXW1tZM0+z3+zRWKWcQLGtC51de5TBredWHNI2zVqt1u1125s66arVKFTgUFkbAZgPdjnzLLbccOHCAfjMcDhljvMtz+/j1gJimmdztvakCFqd5zRdjzHVdz/M0TSuXyzfccMORI0dE15D11JQZcuONN9797nfnrTeKrxLuvaEfaG/wjthxu4LuKOMRwsrKyt3vfvcbb7xRNJEpyqHv+6N32vDm7Kaq1So9zKDRaLTb7Xq9rut6q9VK3oRlWaZphmE4GAyOHDlyww03iCYyhYMHD1555ZW7du2i/9IcvHEx2HA4pKqy1+vd5ja3oXgmeVfk5ayzzvrBD37AW6Wu68ZxnHAvIv1APd+jxXLc+tfl2vM8OVEoVVCDwSAMQ9M0k6Nlxlir1aLgs91uNxoNxhhv2W8ql3o+xRTEZrNJnTt0irGRk644ROv5FOdXXuVQSOoRMPn1IW2oXC7TvbsYAZsJCMBmA43pUyXIO4qmOHWEemho0vzy8nKz2aSOcNGbOKf1UJBpmVa+itY5t7FzkcqGaHkQ7Xmd4wCMMUaTN6IoorYUPYlu0yV50EUDSrRYws6nSWV8j6W+n1O0HNJgl67rzWZzeXmZ32UxLl+UhaWlpW63y4dWNE0bd15vnJ1IDVAJPb6MsTiOaefTdMQtC/PKykq9Xq9Wq41G4/Tp0yz7KdPp6meaPsef9Jh8XvOyR0MK7EwwlpAeKgZLS0utVisIAhqOSJHOyVH5X1dRJIyQ0DxMOqCu63a73aWlJTZ+f+ZVz4sGYDTPmbZiWVatVlteXmbFK4fp6vnJz69plUMJI+1MJADLsT7cWPC2nDpOEIDlCAHYzKD+v4yeqEPXQj6N2/f9SqUyByNF85ovuhzyFgx1QKaYUoURMEI7kAapJulEoMaWpmmWZd16662WZdHDlCfZ/3SrkqIopVKJxrEnl24EjJd5OnwJF2bq06GtmKZpGEbyGBFd9fkKKUcTXvi3gw4TPVxkklkA9Dx3qjl5c0rC46FF0Q6kaYRbjhGxM/VbEASu6+7Zs8d13eTnVdCh4c/5oOMrYeSB0skPFv13y6qD0sbfsZHwYJi86vl0D+GgtPFnlNOETNGkZkq0nhc9v/Iqh6JEA7C86kPaBL+g0H8nfB4MArAcIQCD/8GH1+giRxVoigtSNqlLb17zNRUIwEi6hhT/LpvgApZLOdxOvopMtBymm0okn4R8UQEYvWcsnt7DnHKE82uKUA7JrNQb24EALEcz33ICAAAAAACYFQjAAAAAAAAAJEEABgAAAAAAIAkCMAAAAAAAAEkQgAEAAAAAAEiCAAwAAAAAAEASBGAAAAAAAACSIACD/6GqKr2fnj7pN7mmaAo8z1MUhV4TyRiT+YYW/gZbeuHmhMtHURRFkeM4jLGEtzdGUcRXG0URf5XKNtO8JV4keFFJLiSUBcdxKF9sZLck47mbcHn5+GtDaVdseZRzOb94gad3pGqaNgcvKUqBKgHGWBzH9J4o27bzTtRYdIx4xZVQtBRF8X2fvzqc3p295cp5YRjdXNEI1Ycs1+sXbYiKVhzH9OboHUX0/DJNk+8uVuCWhqIodHLxJkTy+aWqKj/6qqryV9Jln1IxiqLQe955JcAzCDIVtNyDZNRE1jSNqgx6jXreiZoC0zQVReFxQhiG9XpdzluVK5UKtSGoRg7DkJoRm/I8r1KpMMZUVaVLeBAECXU9VfRBEFBrQ9d1x3Hk5EtVVWoJ6bpODfqEfBmGEQQBXW7pEFQqlYQGpeM4lCPaaf1+n3ZL0VQqFd4cpGuYZVm8HbxRjudXFEVUkKi0qKpa5NgjI8PhkHYCbyk6jkNNkEKJ47her9MpQBGFoijJDXrDMCzL6vV6dGYlRym2bdNqaScYhlHM6Eu0Pszr/FIUpdPpUA1ACYjjeMIet3kien55nhfHMe8P0jSt0+kUMABwXZdqSx4r+r5fKpXGLU8do3RlZIwFQWDbdgHzxa9WvLfCMIzC9nXOMT3vBEAh2LYdBAG1lRVFUVV1YWGh1WqJXsaKdjl3XbdUKlmWFUVRr9er1WqdTmdxcXF1dTXT7fq+bxgGr7KpH7dUKo3bP9TGGg6HURRRy2M4HFL1venynueZpkmtDapD19bW9u3bJ7r/RY9vGIbNZlNVVbqoeJ6X3KCngIpy1O/3VVUtlUqmaY5Lp23bw+FQVVVVVUd34Jb9+pLRtcq2bU3Ter2epmmlUsm27YR8ua4bhiEVxTiOq9Vqp9PJOp28ZUMH2rIs6ggoWvdK1vUGtZmGw2EYhrVaLQzDwWDgum7R9sOuXbtWVlYMw+h2u5VKhZqww+FwXFtWVdVOp1Or1arVar/fVxSFqrhx+aJmsaZplHdFUXq9Xr1eF01n1sdLtD7M6/q1urq6uLjo+36tVuv3+9SoLZVKCX0xuSja+WVZ1nA4pAWq1Wq3263X6ysrK7t27co0naLovBsMBmEYVqvVMAyHw+FwOBy3vGmanudRCEox2MLCwsmTJ4tWz1CfaalU0jSt3+9rmmbbdjH7OuebIqfXHAqOKujRaiJdt00xi1Mcx0EQ+L5fLpcVRSmVSgl16Lg1CC3f6/Wq1erkyzuOo2maYRiu61J/9iRfD8OQWvOpJ71s/yhvLDkbUXYoa77vh2EoNAgjujNTiONYURTaG7quB0GgqmpCq6VSqVDrsFQqtVot27bjOHYcJ6FzdB2Z51cBu2C3SVGUOI5pbwRBoOt6FEUJhXAwGFDgMRgMlpaWhsMhTcJJGLzNBVVNcRwPBgPDMHRdn/zYzVONLVof5nX9Gg6HpVJJUZRyuez7fhAExdyfouScX4qi6LpuGMZgMIjjmHbm9DOzDdRhoSjKcDhcWloaDAaaplmWNRgMEr6laRr1bhR2LLRUKtGUGdu2W60WdQ0Ph0PEYJIVKy6HvNBQBvvFmXKHDh3KNVHT4bquoiiGYZTL5W63u7i4KBp9pUC9eoyxfr/f6/UoAkwY8eABCY1RUMdbcjdqGIZhGBqGYZomDcjceOON08zDZniR4HMFVVVNuMxQFkYzxRJvD+h0OtSI6fV6lKlut5t19JUC9RoyxobDIc9OQuuh3W7TvK/BYNBut+mX+/btyzqdJ0+epB8ajUa5XKa5MY1GI+vtFk25XKY2erlcptNfUZSiRV+MseFwuLi42O12y+WyYRj8FpRxaMKh7/u33HLL/v37aUicPjfVaDRonl65XObFgBeS4hCtD/O6fpVKpZWVlVqtNhgMfN+P47iA81olSHF+WZYVx7Hv+4PBoFarraysFC36YoxRzxpjrFQqUdClquqW0Zemab7v82m0Z511lpzUTo43gXinIZ+oAjJhBAz+Fw0TaZpGEzmY+BS15DsQ5KP0+77f7/drtZqmaYqiVKvV5Dp0Iz5VekIUQtRqNXamB5F+P25QhcIYx3Hq9fpgMCiXy+zMPMOE9PA7aGkAJ2H944hO7aP1030OFP4ltPbYSBYoU51Ox7bthCmIvLzxnUYBWNZjOKIjYIwxRVEqlQpF151Op1qtJnyF54t3JNPmRKvfFMvzfI0mr2hTYkTLrWgPPWMsjmOa6aQoSqPR6PV6Wz5CRr5yuUwlKgxDmoVIZ+i4/cMPLvvFMZ9x+RotAPxc5rXH5LKe0iZaHxL516/BYEC1k6ZpNAuR1lC0clW084vSYxhGpVLpdrthGNIVkw50cdANk71er9FoKIpSr9e73W5CJUxXZN5a4DV8AcsDTf7sdDq05yuVyvxNlJgBMUAcR1FEHXik3W4fPHhwDorTaKbov3JOExrfv+WWW/hver2e67rjlqdhnziOqUL0PI9mZSTzPM91XbokXH/99aKJjFN1vhw8eLDdbvM10B1uCZsYDAZ0yzVlbTSzG7muSw1QQjuQdmamKAuUQQr8ki+ZvCHYaDT43lhX2Ea5rtvv93nGl5eX0w1/pcjaiRMnFhcX6euappXL5Tl4Shu1FUZ3O7XhxqESGMfx6uoqH/nh/RdFs7HWGpcvKlFRFI3mK6HomqZZLpd5xhcXF0+cOJGiUGVNtD7M9/q1rhMquU9qJmR9fm3cY+n2fNZ4OVxbW1tYWKDUbtlrSdNSaOLGkSNHtnEcssL3f71eX1tbozwmtE8gIxgBg/9BHV00ncw0zXQ33hStE4We9kMPJKQHatHzMCT0SNEtZ3Q/LiUj4UF5NOpC98LeeuutdF9BQjrpuRT86RRhGJbL5RQzzlOc/lQweDkZHd/biLIQx/FwONyzZw9NXKTMbrr8uh2l6zrdDCOaSFGx4AgY3fVBkyTL5TI9YCPhK3RzNs94uVweDAYJ+yEhnULL09HhYwj8HC9aDCZab6Tooe/3+3QLKD3Tgvq2ixaDUS7oBhJ6/kS/39+y3qAn1qytrRmGQdOfxp0ydOj5OUsFI/kU3lTW9bxofchyun7RKU/dN6qq0lNbqQYT3XSminZ+0S6i3RVFET03ZctJB/JpmkYVOz01ZLTa3xRdlKm2p68PBoOiVbbsTD0ThqHrunRp4Icv76TtLAjAYJoKeAJTtc4bu//T8VC8KW2j3+WfCemkOpQ3nuRMaRM1mosJ9/nMHS+Z5rW6ltBAnAkS6o2pkFnPFzlfs1IOC5ivqVy/CiiX6xfMqMLVFAAAAAAAAPMKARgAAAAAAIAkCMAAAAAAAAAkQQAGAAAAAAAgCQIwAAAAAAAASRCAAQAAAAAASIIADAAAAAAAQBIEYAAAAAAAAJIgAAMAAAAAAJAEARgAAAAAAIAkCMAAAAAAAAAkQQAGAAAAAAAgCQIwAAAAAAAASRCAAQAAAAAASIIADAAAAAAAQBIEYLMhCALG2GAwGP2v53njlo+iiDEWhiH/Sr/fj+M484QWjGEYURSZpkl7TNM0z/MURck7XeupqsoYUxSlXC73+/0wDBVFCcNw3PKu66qq2u/3dV2PooiOrJx89Xo9xpjneVT8aMeOE8exoihxHA8Gg0qlomkaY0zX9XHLW5YVRZFlWbRaXdd935eQL74DVVUNgqBSqVAyprV+0zTZSMbL5TJL3A+QjIpEHMdRFOm63u/3VVV1XTfvdG2XaDmkIqSqqmVZjuNQvZF8Ss4EypemaZVKZTAY8Gok73StJ1oOU1yX+bWe6luqfrMWx7FhGLwSpsvNFM8vvkI60EEQGIZRwOMriq5flUolCAJVVXnxyDtd66F9WBBFrNRgUydPnjz//PNXVlYYY5qmUSN1XAym6zrVnvV6/fjx441GgzHmeR41BLNTwNiGMWYYhqIopmn2er0jR47ccMMNomsQPU2oxUB7g46FqqpU641TKpWCIPB9v1ardbtdxpimaeNiMH58+X993xdKIUlxvA4ePHj11VfX63X6bxAEmqYlrGc4HOq6bhhGt9ut1WqMsTAMKRLbyPM83/crlQr998SJE/v373ddVzQWSlcOfd8fDYqCIJhWjOR5XhAElmVRxldWVs4///yTJ0+KrgfV9SjeRiTrTorZNXk5pFMpjuN2u3322We3223G2JZVzfZlXQ55FUGVhu/7QRCUSqVMN5ra5OVQ9Locx3EYhvzodzqdCy644Pjx41POwAaWZbmuu3///hMnTtBvKpWK7/sJfb5CTNM0DKPf79N/aUO0UaH1FK0+XHeqUmCZY3rGyat9COsgAJsNow360esrjZxsFEWRqqrVarXT6cRx3Ov1KpWKhOioaAEYXcV5GMO7Ucftt3ESBqM2JRqAmaZJ17ZyuTwYDOr1uuM4nuclHF/GmGEYlUql2+2GYUhHmYZWJid6eaDtxnHseV4YhoZhJIcovE4fDAblcrnT6di2bZrmuF3B88uvZN1ut1qtiparcQHeOOVyudfrUXOn2+1WKhXaM9NqyPJ80YnJGKPikSKwn0p6ikZ0Pw8GAyoVmqbVarV+v08dEKLnddGIlkNeybBfrHuz3g/punsmp6qq53mO49Trdao6mJQGYtblMN11mTrmNE0zTZO3AYTSKZovRVGq1Sr1A47Gk9MqVzw9fOW1Wo1KvtB6RK/LWaP94/t+v9+v1WrUNVmtVvlAU0Hk1T6EdTAHZjacOnVq3759jLFGo0EdUXEcV6tV6vLcVBzHnU6Hfq5Wq77vF7MzJlPUkzoa3vT7/bPOOuvGG2/MO2m/gOo+wzCoC7DT6WwZAFB/4draGmOsVqutrKwsLi6Kblf0wnzo0KFjx47RF03TpDjHcRzbtjddni6ovu/TEFa9Xk9uoHQ6nXK5rGma4ziKotBQWIoLg2i+er3e4uIidbcvLCwwxmjYbVoNjna7Xa1WKXD1fZ96HPfu3ZtiEGwuie7narW6srJCY8V0CtDpkPXIT9ZEyyHV6r7vnz59ev/+/adPn6aei6xHAiUEuoqi0DC7ZVmUTQm9DxLKodB1mapWXdcVReFBL6+Es8N3NbXL+/2+pmnUgzaV9VNcHYahbdtxHNNQWIrjW8AOFzph6eTtdruLi4s0a6lo0D4sAoyAzZLJW6KlUslxnDiObdtutVqlUimKouFwyCd35Z5CmTRNownZqWdQSJiCyBirVqu9Xo8u4YZhUBySsLyiKDS7j26TGA6HorN00h2v0b1BmUq+EPZ6vWq1Slcm3/fpujv55ujrQikUzVepVBoOh3SvGg3rZV2St7/ndzIq6nTPJM1Pm489s51yKLPuzXpvO46jaRp1SFmWlaIGkEO0HIpelzfWrnKOMl2JJGxomxst5lkfxzENWpbLZUVR6KTOO1G/IK/2IayDEbCZ0el0TNOk+30tywrDkO5k3XRhOuFLpZKmaVEUUUfaDjy7aOwrDEN+U8G+fftOnjxZtJ4z27Y1TaPLj67rqqoOh0Pf98el07IsaqiNBjODwUD0XqkUU1mazSbd60/ThFRVTZiFSA8GoMZTEARRFJVKJXoyyrj0DIdDVVVVVTUMgxpeKR6GIZqvcrlMpwztT2rlDIfDaT2Hg+44D8OQ7tKO47her0+rO3kOpJj6RX0N1ElB7bBSqTTrz+EQLYeqqrbb7Vqtxue11mq1TqeTdf2W9Ugj1WnD4ZAudtVqlQZhhDpuUsi6HIpel+lZLEEQ0LTtOI6bzWar1cp6CiKlnyIiwzCoQqaaWWg9CemhRn8URb7v04ZSnLxFG/F2XZcC8tHO03K5XLR6Ce3DgsAI2GygJq9t21EU0bxnVVVN0xw3QmLbNv8TP8T9fn9njoDpuh7HMcWutm17nidacUsYAaPnGY4+/JDPnBzHsiyajGoYxvLyMn8wxuRS3FsVx7HjOKqqUkAbRZHneQkNI8p7HMf8vqyEezkcx6GhP/pv6hKbohzW6/Xl5WWa6eR53hQfgcgYcxzHNE1qvoRhSOUw+UGXm0J1zXU6naWlJXpIpmmaRWvipCZaDqmq6fV6+/bt4081yFrW5XC0iqBrHz1mMNONpiNUDkWvy9OqN9KpVCq8RNGAZPKMjMnZtk1TITZuSEgx60PXdeluPd/3l5aWCtjRllf7ENZBADYbaACHelbo3v3kKphfDDRNo/sB5MzxLVoARuMzFMZQN14QBBIefiAagNGNHBQcMsboUbYJ1yTTNOm2bCoJqqrSczhE93+KAIw2xDeX/LgLKnXUjGCM0aPzJ6nleQss3VUhxX5Ytyc1TfN9f7o3/Y/uNPpEAJYO341RFNHOpEfCTOspbXlJUQ6pC8ayLKrz4zjO+gkZTEo5pBOf6kzq4ingbSqi5TDddXn79UYK/AK0ZT/gdvCVp4vBilYfep5nGAZ1GYyWiqKlM6/2IaxTuJIBm0p3TxH/Lv8s5p0txSfnHjAhtEJ+wz0N8WUdgNG1hPYG3e7PH+tXKAXMF62QP90RT0HcDgnnVy5Ey+ForT5P94DNCgnX5anUG/OqgPth5o6XzPYhrFO4lhMAAAAAAMC8QgAGAAAAAAAgCQIwAAAAAAAASRCAAQAAAAAASIIADAAAAAAAQBIEYAAAAAAAAJIgAAMAAAAAAJAEAdh80nV94xtyi/wyignpus5fVWGa5pav6KVX6PA3DJZKpdH/gqg4jumd0YwxXdfjOFZVNaMXv9LLRnu9XhYrX0dCvqgo6rruui79xrbtKa5/KoIg4LWE53lbvhqVXnnEd9RwOBz9b9FUKhX+RmNFUehFPYXCkzccDil5yS+jC8Nw3VunFEWZ8P11dIGoVqsp0yqCigQVD/7fLd+X1e/3+SuA4zimFx5uSWa9wZNXKpUoecmZEr0u+76vqmocx1QY6G25cq7jVDA2pnbqZJZDCXg9z0t7wlvUp0joeKmquu6VX1EUSXi7N6xT6DfEAZfuhY+Li4udTqfX67Xb7d27d7MzF6fsWJaV6fop/UtLS91ulxqydEnjjdp1eKuao/0mel2Z8NrPzcqLmEXboKZpOo4TBEGr1VpaWhoMBuVymU2vXGmaxnc1fwut4ziisUoB8xVFEX+17mg/ghDRciiKzovl5eVarUbnchAEYRiOO6+pRTj6GzpkovtN9HwUPb8sywrDkPaeZVm1Wm15eTnFdrNG+y2OY8/zNE3zfV/X9S0L88rKSr1er1arjUbj9OnTbHy+wjDka+M7zbZtx3GE0ilaDqn8r4sMNxYeznVdTdMoqa7rdrvdpaUlNv58nFa9ka7cKopimmYYhoZhBEGw5c6Z/LpM66fqaHl5udls6rpu2zYP/CYkmi8qEvwSQ78MgmBa58u0ymEBm69UAAzDCMPQNE2qo0T3W9bHi9a/e/fudrvd6/U6nc7i4qLQFmE6YpgFURTFZ+qaSXpGaaiHMVatVtvtNq2k1+tlnc6siyvvJ2s0Goyxer3ebDa3/BY1uahJfeTIkRTbFd0PoscrBd7TxlNIG836eFEXLDfdQjUYDAaDAf/vzTffHMex67qi6ylavobDoeM4/L/Ly8tnnXVWikROMUmb6na79MPa2locx+12e2VlZctvOY7T6XT6/X4cx9dff32mKSQpzq9ms1mv19mZqoMVtdP94MGDrVaL59R13dGSsw4/WbrdLuWOMZYwL6BUKvFLA2PswIEDLFUPfYpDRgWj3+93Op2EHHErKyt05aKiGI8Uzk33w1TqjRSOHTu2a9cuvmdM00zohUxxXV73VznTN6hIUPHgKR8tOduUYznMlOM4o6Wu1WodPHhwWjstgejx4lVEvV7np9XoGQRyFK4Ew6bSNTjoSsDbGRLq7qz3g+/79EOv15ukvl5YWBjtP67Vaq1Wi+ZZZWpWArB0aIuLi4u6rquqOsWpdPV6fXRHVSqV5eVlz/PmIF+j5XCSXoNc8ERWKpVJ2q+rq6v8lIzjuNPp7Nq1K0U3ueiRSn1+mabJW7SjKS+IKIpOnToVx7HjON1ud8JAhRbjDamE86XdbodhyP/b6/UWFxclXBc0Tdu1a1en0+Gb9n1/dXV1y9y5rssbiwkjgdOqN0TzpSjKnj17GGOWZVWr1UkmgAhdl23bVlVV13U+QCGao3T5MgxjcXFxNPYLw5BHjNs3rXI4rfRM1+jJe+rUKQkdo6LHi58aVGk4jjNJRxtMHaYgzoZYfEqbovzvweWD++kmPk0u6ymOlH6aW6JpWr1eX1tb2zjPcB3Lsijo4u020WIvut9SHC9RU5mCKLofaOqIoijNZrPVavHfT6tcURZs26ZMURM53XqElpeQL03TqIXhui5N0rMsa9zU2XGyPn9pv1F1EYZhp9NZWFhImCpGXNelvcdvLRBNp+ipIXp+URWxsLDQ6XTCMOST04p2+VMUhaYdxnHMIwrXdRNa9qNn/Zb5oouC4zgUzBiGka5EpatneA0cBEFyrEJFbm1trV6va5q25fVrWvWGaDdZHMc07VBRFF78ks9roevyaC6oaqK9J9rHka77L45jurAGQWDb9mjKt2la5bBo5+/oqRpFkaIoNB1RNJ1ZH6/RdhT/btYXF9gIAdhsEG1w0Jx7uhLQ/HiaGT/dGGDTdGa6fsYY5WV0EvmENE2jXreMEjZqVgIwUXQ3gqIodNO57/uNRoPmXWS0RWpwZP28BPn5mmJrZrqoRI3eVDOhMAw1TZPTkNrO+cVzV8CHcBBquimKQrs04bwOw1BVVWr2UZVIu2LyBhw9jCTrewtJHMeUI6Fv8dpeKJHp6o10pZeek0GdLGEYJpzaotdly7Js226324Zh0HMd4jjmd6hOLsW9waPP45EgXTksWhVKpyo/bUe7UYRkfbyoyPGqniqQFPfGwzbhKYjziSINGmimSm3yp2MVGY+gNE2jysK27YS5iKZp8s57Xj3haT+plcvlo0ePLi4uep7n+36pVOr1elOMUizL4j2IvPEkodxmnS/btmlGPjWs+b3701r/tPAIKgxDOk0cx0m44592F/3Ms1PAq7hpmtTXy+sNCgbyTtd61DCiBj1/LllCOaHjRff60/lCXxy3vOu6vFTzxm7WvXJspEjwvPi+n1yuaGiIl0N+1mwqr3qDYl0KmFVV5UVr3PKi12XXdXu9XqlUot21uLh49OhR0egrBV4keCEZLTnbl1c5zBqvPGmkl8qGhHyJHi8+FYhmLlAFUsB6e+4VtBcW1knR40vdbLVardvt0s/U2ZZpOrN+AjX1MtLQOVUcnuclDybQ5Y2ulHTlY+J1fYqpKTMxAiaapCAITNM0TdP3fT7TplqtDgYDofVsmR46Xql7YQuYLyql1J1PUxCpv1xoPVm3Kan7lmZGUUvRNM3kckW7mtoZ/KlfoukU3Q+i5xftfKouaO6Tbds0WCG03axRmR+9sVNRlOQRD+q97na7tVqNfqa9MW799APvAk895iO0PB0aKlF8gC5hJZRxKn40t9BxHBpVSFg/23a9IdoGHa2B2ZliVi6XE+oNoetyuVym5+nTkoZheJ7neV6K2R9CyxOKEkcHVKd1CZtWOSxa85VO1dEKkw9yCq0n6+NF+3xj1ZFio7AdCMBmg4QG/VRkXZxo/UL3meQyVW9WAjBRyNfOMXq3ZHIANho20G5MMaVQdPnUx2vCfM2rqRwvUbQJ2gpvkiYHYCyPer6A5SGXfIkerxRyqTdmRQGPF2QBRwgAAAAAAEASBGAAAAAAAACSIAADAAAAAACQBAEYAAAAAACAJAjAAAAAAAAAJEEABgAAAAAAIAkCMAAAAAAAAEnEXucH84reHTn6Ig7+dh2h9WT96qTRFzEzxiZ5ETM789pHWpgxpihK1i9iTiHdCzo1TQuCwDAMxpjv+6Iv6BTNF38/CU8bfSa8+DUIgo1ZE9poCqmPr2maRX6DSorzUehFsaMvLGaMbfnC4tGX6vJX+hTw5Tyi+ZoWCQVJ6EXMg8GgWq0yxsIw1HXd933GmGEYvIRkRNd1z/N83zcMgzatqmqv1xv3gmlVVekY8bJE9ca4fOVVH0p7EfM28yWK73ZeluhzWtf3vMphCqIvOqe3tAVBoGlaFEWapoVhKPpiZdFyKHp+4UXMBYEXMc8GOS+KNU2TakDeBhXdRNbFKQzDKIroOqTrehiGtm1HUUTtqo1M04zjmOp32mNxHKeoEEWlO16jyxiGQS+2H7ewpmmmaQ6HQ03TFhYWvvOd7xw+fHiKWdgUFQxFUXizg2rtcTGVruuKotD+Z7+YwXFyeREzFQlFUXgKDcNQFGVcuZoV/CymH+g6nbC8aZrU9qUGH2PM931VVcedL3TcqQxQADa6DyeX9YuYRfM1W0a7DHzfp9Nz3MJhGHqeVyqVwjBcW1u7z33uc/ToUQmJPHz48He+852FhQVN04bDoWmaCTuf5+jkyZN3u9vdTp06xc6EN+O+MpX6ULSeET2/+Lck1/Mp8kXXSt6rMnqmT8VUyqGc5uvk55fjOHEcl0olShj/ooQXggudX0EQxHFM7Sj2ixkEmRCAzYasAzC6tlFvDW0o3colFCe6JFA3j9AXKXdyCrzo8aLeMuoQpTYidYuO+4plWbZtt9ttwzB0XR8Oh3EcDwaDcT1e08Ib2RMuTyMk/JDxbuwwDBO+Ij8AI4qiUCGRsC2ZqF929ASf5CygTlzeApvQaHA+uawDsFHp8lVMYRiqqkq911Ql0q4Y15xyXddxnEaj4ft+EASlUklRlOQRm6mgTcRxPBwOdV03DKPdbtu2ndCg7/f7uq5blqUoimmauq4nDytNpT5MV89Mfn7lVc+L5osKUnbXymmVQwkdvkLn16YpTFGoRL8ien5RkaPsaJpGGaTxOtGkwnYgAJsNWQdgoxPD6HJCEwNEK4KsG6+UHpqdomlavV5fW1szDIOPsWyKpg3EcUy9eky84hbdDymO1+hl27Ztx3EStjua/maz2Wq1qLdStAJN1+BQFIUPQlKfX3I6eXbYVt3YbEoBWLrjS6M3FEJImCeZQor9QBN7RrtUEmaB0qm0sLDQ6XTCMORzfcftTzqajuNQMEPDhkIp5OkUXV7o/BLN17RI6DgYPTsmOV7851ar1Ww2qbRnXW9TsBHHMW2U/37LdA6Hw2azOVp7bLr8tOpD0eVFzy+WUz2fbnyDTx4JgsC27Qk7biYxrXKY9S0PTPz8CsOQdhoPaVLM7hM9XunOL54dljZQhG2a+S5AmAo+wYBaKq7r7tq16/Tp01kHKqKoy9C2beofXVtbY4wlRF8LCwu9Xo9fDmu12urqar1eL2BPz65du/r9vuu61WqV5v0nBJa2bXuep6pqo9FYWVmhX0ro0fd9v9PpVCqVfr/PzszjqtVqnU5n0+UpC47jUKYsy6pUKq1WK+t0pug46HQ6dGMGO3NnQrVapQJWHCnOx127dt16662mafJTO6F1SOVtbW3NNM1+v1+pVNiZk27T5TudTrVaLZVK9N9+v7+4uNjpdJI7ROQTzdcMWV1drVQqlmX1ej26r4ZuBdl0Ycdx6C7Hdru9uLhIv5Rw4w3fRLPZXFlZaTQaqqp6nsfbfxvTSWNfo8coIbCZVn2Y9fnFZqSeNwyjXq/zM8UwjCiKut1uvV6fyvrzKocpCJ1fnU6nXC7zUt1ut5vNZop5m6LlUPT8oizYtk2Zcl233++PRm4gSQyzgA/dsDP173Tn7FqWZZom/++uXbuOHTuWIp1TTNKmqAZkjDUaDcZYvV6fpNawLKtWq9G0jSNHjqTYbtbHizdhq9Vqu92mlfR6vYRNrPvruEvCdPPlum4cxzfffDP/zWAwoMkPyYlst9v82PHMborfTcFTSDtTSIpdQQWjXC7XarXC3o4suh/i+P9n712e3MaRfX+A75eoslTutjui7TkO7+6ciLO4cf7/9Wzv2fWE7y1PdLfbLskliu8XfovvFH7qqhJLYJHUo/OzcKhkikQCiUQmkCDEzc3Nq1ev5B0sy+qWbrFYwM1CF2M7ne4xruvutuZPP/2ER4wtVw97qCTXUPRoLyVk19t1juE07+PB/5ZlOXYhwYPNUd2F5PegDpt7Ou5/FHsoFPvXsey8KujC6M6y5N12W5Vj6aESqv3rQdbfcrn8/PnzNEVV6l/yf8Mw3G63D4QlJoNSEM8DMf5LOAzDQNqhruuwhkw9pXBszxXlub6+3m63mGg0DAOr/E9e/3hyEfWmugLWY09Lj/bC6kEcx5vN5vXr12x//aP82Axwe3u7WCywMKj60ghVuZC0gD278rcdqSMo57dv3+bzeRAEYRjKedx9DJKCqDpJjFz/Bw30bGrr9Ki2F+ofu2iapkG6VMdNsNVBvl5lNpvd3t6y/alZu1sxpZLvZpweiOowpNq/VOUaimkm9VerVRiGQRDM5/Nv376xzvZi9ztGrq+v1+t1XddYjhi1hJiMNwxjsVjc3t7K3T77yimEkK9XLcsSl3UMRkPZQ9XEY9X+Baa386rjOLqwNMX4skfqY3d5Xq6H02SyKPUvTdOkReq9j061vVT7F+7/+vXrzWYTx3EURXIdkpgSCsDOgwkCMInrutjs2yN3eewURPj6UFpkfSAXbh+oJelJQ7QejvXYDqJhGEIImEVxv0tNCLFvXh8pBDIyqarK9/0e0UKP7o+khQPfJNm2rawH/IuXDXb4KIMEYKrXQyWgHvLP8bpYb1TbC12Ycy5FOwTokjyzQb45sBu8gUAmVikxdv8C/eR6CWMPr9h9JMMAdr92tK8qoNhyMw/s5zSLKrs2CgXosMPy9QC2bX/9+tW2bUwO7ivqseyhav86lp3vATrySC8lOqIeKqHav3ZBxqwQIsuyYRcPn0Spf8nXxrB7PYRbdQEp2ecFBWDnwQQB2FEc33NhGgdx91n4t6M+5TIUjCYe16OcStersivFgbpBetjBlHo4JSTXS+4/ff/qUc6LtIfnItcJcsS33R4O9S9iVOjd/wRBEARBEARBEBNBARhBEARBEARBEMREUABGEARBEARBEAQxERSAEQRBEARBEARBTAQFYARBEARBEARBEBNBARhBEARBEARBEMREUABGEARBEARBEAQxERSAEf+mbVscOCgP2D3Bc3XOBVl1skqfrUx5DCUOvsRxsR1omoYr5UGZ+07zHBZ58vWzJWSMcc6LomD3J1qyHTFPCnmCiqxDy7I66hNSOI6jaRou831/kpKqoaqHveWyLAsfTrMezqW92Pj96yh2/lLtYQ+5VDmWnR+bs/A3OOdVVaGLMcYsyzrN/kWcKZfQk4mXA9ekaRqcHmiaJlmNF9K2LYx1XddN02ia5jjOvovlGfbs3nDbti3t/mPyPIehx+mcVVVNNir7vg8fET530zR5nu+7uCgKSG0YBo56rKrKdd1pino4nHPHcaD8qNWyLDu6QFVVuIZzjsuSJJFByEmhpIeqcjmOA3WFfyx149Q4o/YatX8d0c5fqj1UkkuVI8o1Kmfkb5imadt2HMe+75dlKdXySc5ILuIUMI5dAOIkyPPcMAz4KEKItm3v7u4Wi4Wq+biM4eExqvWg6/p6vW7bFl6RZVlt23Y4UnC54M7Gcazruuu6juPse67jOEVRNE1j2zaeEgRBFEVKhexBVVWmaUpXr23btm1d191XTtu2GWNpmjZNEwRB0zRZlmVZNnY5VfWwbdurq6svX75wzuVMs2VZ++bd0VJoNd/327bNsqwsy7H1f2w9VJUrz3O0ftu2VVXJRZhuN2V6jtVeqozdv4ay86qciz0cu3+pglmhuq4ty+Kca5p2dXW1Xq9PTW9VyfPctm1d14ui0DSNcx7HcRiGqvcZW281TYuiaDabBUGQJAnnfDabRVHUYQ8HkYv4i8BhOIgTRwjBOZeJUnVda5o2oPWBQdm9YT/FQAkvj5fXxuMa3sX3/SzL4Gyt12vHcYQQ8G57POtwVOWK4zgIgsOvx4DEOc+y7Pr6Ok1TXddt207TdN9PoNhQcpQQyq9Uzt56aFkWHFMZhnUQBEEcx5ibN01T1/UBfa8nGVsPwQvlws+VSqgqVz97ePrtNXb/GsrO9+Py7OHjZx3Sv3afhX/3lRb32XX3aYQ9FlNqVI+n9PYPD9FDYiTOex6FGApM3THGdF2XGRQ3NzdHLdQZI6tO5mi1bduR8pQkCS7LskzWf4e3sdlskOeQpulms8GXb968Gar8+wiCYLvdosBxHAsh6rrumGmG58QYc10XTqGmaR3R17H4+eefGWMyyUTXdZnB/yRYeSiKApOd+HJsb74HqnqoKlcYhoZhcM6DIMCuqtlsphp9TcC5tNfY/etYdv5S7aGqXKrIRdrdTNT3798Pdf9jMZ/PkVfped58PseXX758OW6pHoOV/Kqqfvvtt7dv3yIRFP8+ybnIRZwItAJ2Hoy9AgYMwzBNs2kaJKgw9SX+03zFwstRTanCqMk5tyxL1/WqqrCe0wHn3Pd9eF1RFAVB0NHEck60bVv5LM6Vu3OP6+M4ns1mjLG6ruVQ1FHOpmniOJ7P55zzMAy32233QwdZAesOnx6D8u9WIO6wbx1MZid6npemaRiGeZ5PkNI2th6qyiXbXbYXArAJ9FDJHh6rvQ5ZR91lgv7FhrDzqpyLPVRtrx5ySQ5feajrGrNCSERk55/qL9tRtmk/Oz+23kojw55a5+wozwvlUoVWwM4VQZwDMsuc3U/ADGuCOee78zphGN7c3PQo54BFOil6VMXNzc1u8jcWCvbdX06azufzzWaDO1RVte/mRVEkSVLXNf68vb3tN92rKlSe50KI3377TX4Tx3FRFPuulyW8u7u7urrCQ7ujdCi21EZxr/xK9KiKjx8/MsaCIDjkVVeMMdd1cRncZaYe9fVAtR6Eoh4yRbksy9p9neDbt2/Z/XLTqHL1sIdn0V5j96+h7HwPLtIeqsr1+FnY5rfv5thaKf/cbDbv3r3rIdepYVmW53myAy6Xy99//71H5Y8NNKpt2+/fv8sVrQ5Tcyy5XuIfyjv0GGeJF0IrYOeBGH8FDLfFyFeWZY+NHOwcMrn70WNmCBUo61MuEey7v+d52HrueR42lHc0MWb05T0xr9/9iCfp0V5VVXmehwdhO03HC8p0XYcgtm1nWbYr5j4GWQHrQVmWnudhChzV2/EyCRSSc+667tevX5GAtLtkMRJj66GqXLL1EXTVde15Xo83cKjqoao9PFZ79WDs/jWIne/BWdjDHijJtYs4bOUBWor1W8uyVHcJniZlWVqWJTtgmqbQedX+OPa4IG2LaZp3d3fYOIo35Tx5/VByqfIS//BAPSTGgAKw82CCAGwQLlWdLtUwje349uAoAdi5DGBT6uGBciHpSzoZk6XCnkV7qXIudp54Oaesh+fCCdrDo3Cp9vDiOe9MYoIgCIIgCIIgiDOCAjCCIAiCIAiCIIiJoACMIAiCIAiCIAhiIigAIwiCIAiCIAiCmAgKwAiCIAiCIAiCICaCAjCCIAiCIAiCIIiJoACMIAiCIAiCIAhiIigAIwiCIAiCIAiCmAgKwAiCIAiCIAiCICaCAjCCIAiCIAiCIIiJoACMIAiCIAiCIAhiIigAIwiCIAiCIAiCmAgKwAiCIAiCIAiCICaCAjCCIAiCIAiCIIiJoACMIAiCIAiCIAhiIigAu0w4577v47PnebquM8Y0bW9zW5bFGDMMQ/5k98/xqOuaMZam6e6fZVnuu75tW8ZY0zTyJ0mSCCGefURZlrhtHMfDFH1QVNvrWHDOq6qCYtR1bdt227a2be+7Xgriui77s5gnBVSIc65pWl3Xvu93y4Ua0DTNtu08z5um4ZxD004KlBPdWf6Jzt5x/eFyFUWhaVqSJIZhtG0rq3FYKV4OuhLn3PO8JEkgV9M0xy7XQ1T18FLpYTekbkO9gyAYv5gXi+q4fKmci50nzpTRPWziKJimmSQJY2w+n3/+/DkMQ8ZYXdf7YqqyLOFPY+RbrVZ///vfv3z5MnY5DcP48uXL3//+99VqxRjTdd227bqu99l6wzBg/sIw/Pz583w+932/LMt9PqWMzXBBFEX/+Z//+fnz51GEeQGq7XUsiqKwbfvz589v377FN0mSmKa5r/6bpoFGbTabv/3tb3d3d7i+qqpRy9kvBpCxJeiof8glhNhsNm/evNlsNowxTdMwQXA61HX95s2b//mf/1kul4yxpmmKojAMo7u9DpdL9kf5Z/dsyLFo29Z13bqu0zR9+/btdrtljOm6foIxGFPRw0tF1W7I/o6BIwzD//N//s+7d+9Un3uCcwdHQXVcPhZjW5tj2fnTtKLE4HBq6bNACME5x/AAp+dZK4BZwziOhRBRFAVB0PETudjStq2cLeZcWT16XC/l2i3evsUfFC8IgiiKhBBxHPu+/+yoWdd1VVW6rluWJZ+lVM4JHGul9hoK1XpAnc9mM/Znv7BDr5qmieN4Pp9zzsMw3G633UoCqaVnL4SAkiiVE97b4Xieh5pvmma73fq+b5om2y+XVFr2Z6dt7EVLVX1AF0aFy67dcR9VuXAf0zR9399ut03TQEPkmtuB9NBDJXtoWRZ8R8/z0jQNwzDP87IsT22RWVUPL5UedoMxZhiGaZpN05RlKXVe6bmqduMloISnuWisOi4fiwkm8o5i51Unhnr4h7u/ZaeqhxfPX2te7S+FYRgy3S4MQ3SwfYZjs9kEQSCEKMuyqqr5fM4Y+/HHH8deBPvjjz/evHnDGJvP51VVYeAMggBTTU+C+ASfgyCoqgo+ypPkee44jmEYyJ3Dl+/fv7+5uRlUjgFQaq9jIQ00Mj9930c6KJbs9v0E6sQYi6JoguUvpu54xXG8XC632+1sNru6umL3a3376h9aV1XVt2/f3r59++3bN4Sjp5adIrvwZrPBQiXnHH7tk9f3kMu27aIo7u7uGGOz2Wy1WmG17aSA3pqmWRQFu9dDdnqBjaoeXjBKdsNxnDzP67oWQsjh4Obm5v3791OU9eLoMS4fhbH7xbnYeeJMoRWw80B1hsP3/SzLkHizXq8dxxFC5HmOlPpD6DcX0k+dDn+W67p5ngshHMdZr9eu67Ztm2XZvh0CqKJdM32aczwvb69piONYaXNFnue2bXPOsyy7vr5O0xTZLHJ3wWMGWQFTvd513SzLhBBpmpqmiYh9pGdNz9i9knOOxYc0TYUQWZaNrbf9ZnyDIIjjGBGjaZq6rud5Pmo5VXmJHl4SqnYDFn5XAcbW+Zdz+isPp1mqXaZ0X6fXDaXraQXsHKEVsMsEG4ocx8FmbrhECFeevF7TtKIomqbBaxWEEGEYyoWmUYmiyLIsIQS2m2Obyr6ZrSzLGGOu6+q63rYtFrg69mdD/LquLcuCXIvFYr1en1oKomp7DYVqPeB9AAjDqqpq2xZB475yOo7DGEvTtGkabKnPsqwj+hoKVbk8z4NqNU3jOA7GoSzL9r3/QNO0zWYzm81kvu5sNoui6NRSEBljYRiWZYn3OhRFAUe2ww4oyWXbNgIG1Bu+TNNU9b0RY9eb4zi6rmOF2TAMTdOyLKuq6tRWllT18FJRtRuYsjEMA2mlnPP1er1YLE5thfOMUBqXj8UE4+NR7DzxF4FWwM6DHitg8OnZzmwKwpUnr8/z3LIsmJWmadq2xfDfIxdZ6Xq8VshxnLZt8SxN0yzL2jczjVSTB89KkmRfDDaUXGOj2l7HZbfCm6apqmpfOZFAhc9ydg3u1L6bH2UFjDEWhuHt7a1pmkjEfdblRaniOH7z5o1su1MDO8jzPNc0Dftb2rYty7JDr3rIZds2kpRM07y9ve3IRx2KHjO+eE/jbt+XG8NOClU9vEhU7YbjOGVZQgF0Xdc0DYkSqnu6aAUMqI7Lx2IC9/Uodp5WwP4iUAB2HvToYDJpvq5rXdeLopCvoNgH9tBzznVdx78TBGDyWXhhQPcTOeeWZWEiHw569x4w+ZQXyjUBPdrrKMjoq+Plk7sgjMQiJHz07j1gRwnApO5h9z9ct6qqOgREyIFEKYg2wd42VaDqEE12ge6fKMllWRZeb/Og9sbWW1V7CK2Dm84Ya9t2d8rjdOihh5eKqt1gjO0OIviXArB+qI7Lx2IC9/Uodp4CsL8IFICdBxN0MLwkTb7aDo/rYQhUrz8LuabkkgzirhQHynLEAAylharsvjPwMT3kOgoTyDVIe6nyErtxyqi216VyLnbjJZyynT+X/jX2OH4sO3+CfhQxBn85y04QBEEQBEEQBHEsKAAjCIIgCIIgCIKYCArACIIgCIIgCIIgJoICMIIgCIIgCIIgiImgAIwgCIIgCIIgCGIiKAAjCIIgCIIgCIKYCArACIIgCIIgCIIgJoICMOLf4LQZwzCyLMM3E5z+mec5Pti2jfNbug+v0DTtwVEVbdt2nxF5FLnGBrUkT4SEaBMcEIlHyJrEnyd4PowqUiWyLMN5cd2HLzVN80BqzvmB5zXhcNggCHqWleiL7/uyoTnnaOi/FGQ3iEPgnFdVZZomY6yua85527b4c3CmtIdj6yGGAFlRruvu/jkequ3Vw48ixuAvNwIR+6jruq5r0zRhEBljRVHIzyMBC8UYa5pG0zScIdi27b7nwka8fv16s9lUVRVF0XK57H7EIHKdmm1Cde0aehjcsctpmmbbtrLVUAAUZtTnqqLavkVRyB82TVNVlWEYHQ46/mu1WoVhaFnWfD7/9u2bEKJDb+XdcEpmHMeO48gJCGJUbNtumiZJEnyezWa3t7d1XY9t38hugHOxG5eKavuWZek4TtM019fXt7e3ruumaVpV1VD9ZSh7qCrX2Hqo63rbtrsTHJqm9ai3sdurhx9FjAEFYARjjBVFwTl3HIcxpuv69+/f37179/nz5wkciH/961/L5XK1WjHGyrK0bZtzvs8Q+76fJMm3b9/CMCyKAlYjyzJpUh9wRLlGBSNHURRlWeq67nnep0+fPn78OLZDyRjDg9I0bZrGsizbtieY4VOlR/u+e/fu+/fvr169Yozpul6WZVEUtm0/eTFUbrlcwm/49u0bu1fOJ6+HfsqZ1zdv3vz222+0AjAZRVEsFou6rqMochzn9vaWMRYEQRzHxy7apJDd+Gui2r6u61ZV1bYtekqapjBuQ42bQ9nDHno7qh4i9LJt27KspmnSNP3w4cM///lP1Xobu71U/ShiJLgQ4thlIJ5HCME5x6oxlok0TTvQYKGJ8e+DdecHFEWBhWzbtr9+/fr69evu64divV4vFgt8rus6TdMwDJ+8Uq6zx3EcBEFRFEmSyN/u4+VyTVMP4JD2uru7C4JATiJut9v3799HUTR2YKnrehiGNzc3s9kM39R1Hcfx1dXVk9fvSnFgHUKxoeS4A5R/kPLvQwjx7du3H374YVdVun+yXq9937dtG6rIdpTzMVEUBUEg51mTJEF7jZ39xTlHBTLG6ro2DKNt247p3jNqr3720LIsNBy7r5BRy9nDzii1lypkN7o5NTs/FP3uj7KtVqv5fK5pGpZZBinPsezh2Hp4dXUVxzE0kDE2m81ubm7CMFQNqMZur35+FDE4FICdB2MHYLuT/W3bcs6RtqeqHqqGA89FDgDSwJAruO+5uH+e59KydI+yQ8k1ZaqMUsBsGAZ2Hyk5Ky8vW9u2Qoi6rrsDlWM5Uj30FmmHQgjZ1h0rYOzPiicVskNvhRB5nsP3NU1zGlePAjBgmmZVVVdXVwg2nm2voVC1G2MHYIDsxj4uNQBTVSFd1+u6FkLszo2y4frLUPaw37gwqh6y+w3t8ilMvd5UAzbV9lL1o4iRoBREgrH7lxA0TaPrOowjJkjG7pO2bcudM7uzNfue27Zt27aO42D/hozf9hmsY8k1DRg8dmevJ5tPQatNkLnUjx7ti+0B+CEUpuNlLZgyyPMc6geF1DStw9HhnD9I8JDOIjE2mFm/u7tjjMn2QhBy5JIdA7IbfzVU29eyLJgm5LaZprnZbBzHeTYv4HAGsYe99XZUPcRU8u7Nx55AVG0vVT+KGAnaAkswdm8g8G43LAKgi479XBiapmnkvG+WZR07ceWUEpwny7I45x1W41hyjU1ZljJbQxr3CaynfIR8aFVVZVmO/dyxgVZomoZpS/imHaMm4nmoHyZx8cN91xdFId/zIZ2MC9DDc8GyLLkRFDoshDj3jaA9ILtBHAI2L61WK8uyTNPMsiwIggGjr2PZw7H1ENWFzzKImsDOqLaXqh9FjAStgBGMMZamqed5u5kASOdQtYmqqQ67LzzEm5Ecx8FLVPf9xDRNTNhst9vZbNadJzaUXKeGZVntDnKhb+xUSTmWyAUfXddP8FVmPfR2dwkLgyiUZ99PHishXuD55MW7ebC9C0n0pqoqIYRlWXC2kHvz+CyBi4fsxl8T1ao2DOPTp0/YvFQUBZaq4jjusIdKDGUPVeUaWw/LstR2gLXBqxGV7jNBeyn5UcRI0B6w82Cal3AQ+zjBvQFYsZEvEoB6jN2dL3VP0QRQew3IudjDU3sJByM9fK6cSte/BNJD0sOOcqpeP8HeUWJwqIUIgiAIgiAIgiAmggIwgiAIgiAIgiCIiaAAjCAIgiAIgiAIYiIoACMIgiAIgiAIgpgICsAIgiAIgiAIgiAmggIwgiAIgiAIgiCIiaAAjCAIgiAIgiAIYiLoIObLBOdCPD54dN/5Epqm4bSKuq5xbqCu603TqB6OPvbBpjhhQ/Ug5t2DOOQpGUrPHftIDc550zSO4+R5zhgry9KyrGcPRYEUuJgxJoQYu5yGYZRlWVWVaZo4OFvTtI4DH4UQuq5D/RhjUMhnz3uBFFJ7uw/m7rjD4UDVcSIt5ILODKXPaZoGQcDuTxuvqooxZpomzoo5nNM8OHj69pLdWfZl/LvvPm3b2rZdFAW7P0OsKArHccauzx4H0+MDTnQ9pHhPHgi+77lD6aEqqnZD0zQYDWko0Hz75PI8L45jxpiu63Vd4yD1qqpwxtTpoDouDwXpIegh11HocRCzUv9S9aOIkTgt80QMhWmaGMMQQTmOU1UVTmd/8vo8z4UQruvKiKufNz92ANC2bVVVsBSz2Qx+Vcf1MEByJEYN9DijcGxLreu6aZqIvpqmsSwrz3NN0xBZPQZhDFpZlg0hxKjlLMvyw4cPURRdXV3Ztp1lmWVZGEqfpGmaqqoQfem6XpYlvF74H49B2FlV1W4b9ZgIUAUTEPiMZ+V5zjlHyV9OEARN05Rl6bpu0zRRFH348OHTp0+D3PyIHKu9dh8H/YcdQIj1GERcjLEff/zxjz/+ePPmDfRwAnuldL3swnChGGNVVdV1vc8OMMZs227bdjab4XNVVZzzfXIdSw9V7Ubbtuh6f/zxB5qsKIqOwD6OY13XLcvKskzX9TAMP3369OHDh7Hk6YvquDwUpIegh1xHQbW9evQvJT+KGInRjx4nBgGztpgnwyHrh8/fYFFLHjmv9MSexR2Ntm3lMfO6rmPaBut1T14PKeAR4qj4fkPdBFUhhVKdBYR00zSW53lpmgohsiwzDMM0zc1m4zhOh/mG4mFaTulZGCwnM1CjKnxRFHmez+dzjPeu63LOUZkjPRFgxh11KNd+O7oArkQ9qNbGlO0FWZRK6HleXddlWQohiqKo69r3/fFKCPpplBDiwCAWa7Ywg+hiGBr2NfGx9LCH3UiSxDAM27Y555ZlGYbRUUjbth3H2Ww2pmkahpFlmRAC6Q9K5ZxyyOs3LveD9HCXw+XqYQ/hmKEGcIceI4vq9ar9S9WPIkaCArDzQDUAM02zqqqrq6soipqmkTlg+5obUQoyAWRX7LEqPbY6oQakOOw5v3lXhLZtkWNpmqZqOcc2TCgPUhAxI3h1dYWMgo5fFUUBN1TTtH5OsyrwGIQQ6/V6sVg8KP9jdtsLM9N3d3dQzo6nIH1FCNG2Le6s2l6q9SBdB7gRjDHTNBG0K93nkPKg6jjniEuV7tOjHiYIwKZvL/krdBDDMLCGv+8+sjyO46zXa9d1H3w/Eqp2Q9YearKu62ct8K7Uh9h5+fkleqhKP7vBGMuybLFYIDWA7deT3fssFov1eo3aU63/sVeiVMfloSA9lIVkKnIdKwBT1cOXjMvyyhOccL94KAXxMoGDe3d3Z1lWkiSY6+2YbIuiyPM82Rs3m81iseixKj12H0ZM4jhOHMdBEBRFkSTJrsV5gExMwg9t2/7+/fvr169Vyzn2AAl7nee57/t1XV9dXTHGOqKvu7u7IAhkA22321evXmFQH7WccnVusVisVqv5fK5pGhIL911vGIbjOJjPvru7Y/fK+SRXV1dxHMtEstls9v379zAMxw6AUZNQe8hS13UURWEYDnL/PM8ty2rbdrPZLJdLfDn2hocJOFZ7VVUVRZHv+0mS4E9N02azWRRFT14vN4DtOkbYBjZqOXtM9IRhiF0Z7N6viuMYBuFJvn//7vu+bdswiezeSD558bH0UNVu5HmOta/dMUs24mMcx8Gunvl8vlqt8OWpbQBj6uPyUJAegh5yHQXV9lLtX6p+FDEWgjgH5NQyux9Xnp0jWSwWcB/n8zm+6cgJfrBavVwuP3/+3KOcL9TGZ5FZQzCjeCgW358kz/OiKOSf6/X63bt3PZ7boyqUkLLc3d0JITabzWq1evZXeZ5HUZQkiRDil19+GbWEkgfbt7rzuKTKQQnDMDzEytu2PZvNkD708ePHadrr8+fP0hVg90lNPR69jwcVhVw4VVQfiokG/LaqKiEEsgT3gdQU1WdN317o1L/++qv8Jk3TDjvQ3CPup7RlQsGoqMol7jtykiRRFGFZrwMp8na7lZMF3V1yED3sgZLd2G0g8efm20ccx7t/ducOHBGlcXkoerTXpeqhklw97CEcMxlRi3vnbWyU+peqH0WMBKUgngdCMQUR+VSYF4F7dHt7y/anIiD5St4Zy9k9yjn2TB5WeF6/fr3ZbOI4jqJo12l+krqukXaIl1ugDlVn6PfNvA4FynN7ezubzRAJ13XdNM2+RcjHk4tILZvgJRyO4xiGsVgsbm9vZdZ+h14xxq6vr7fbrVyCQHbrk9c/zk6Enqu2V7/JVKTByASSAXPiUQ+oruvr6/V6jQVP1c3fqv1r7BTEY7UXkmcgi/xtdwoTigQjIF+ZOHYMpmo38AbaBw30bCryarUKwzAIgvl8/u3bN/Zcf3y5HqqiajeEELKNyrKUbbfv/rgAm75ub28XiwUW3ve97GcfY9tP1XF5KEgPgapcqvaQDZSCqKqH/cZlJT+KGAMKwM4D1QAM+L5fVZV8N/SBL3hApocQIssyuVniQCZ4na50KPEvpkUPcUwhDue8I5VlH2N3E2xXQO3hfbLdM1gYReTIAdGeHSAHAWWD2w3/vmNPF3xi1J5lWaZpImdsH9BqeUPXdbMse3bP2GNU2+slunEIEEG+fx/10KOxemzmHjUAO1Z7McaQPHPgZnp0jbqui6L44YcfiqKQrwpQfa4SqnKhnNLw4s+OJqvrGoad7bRax9sCh9LDHqjaDZhE27a/fv1q2zZeVr6vqPgv6enuPusE6TcuvwTSQ6Aq17ECsB4o9a+X+FHEgFAAdh70C8CUOMrbe17CrvnoeK6cJodxQTWqqj11EzCBHg5Cj/a9yP41zUs4Xs7Y/YvkkhzFQXxJ/5rSzl8qpIf9OBe5JuhfxBiM+84fgiAIgiAIgiAIQkIBGEEQBEEQBEEQxERQAEYQBEEQBEEQBDERFIARBEEQBEEQBEFMBAVgBEEQBEEQBEEQE0EBGEEQBEEQBEEQxERQAEYQBEEQBEEQBDERFIBdJjjT0HEcTdNw7E/3wb6MsbZtcZCiPNj0BM936oGmaTj3XZ4u33EO0hHBCcVt27Ztm+c5Y6zjING2bXGOJz7LI0fGLqRUCakqIymJZVn48KzeDggUA+dRCiFkGQbhiP0LD+Kc47xUqTmP4ZzjHGpcye4tyT40TZO1pGmaPIJpwMI/iTzZTNZhWZYd9QnZ2X3jMsYcxxm7kP2QJ5V3NJNEtb3YkfRwArtxLDsvDdSw5uLoXKQeqtJDLoI4nFP0RImXU1WVYRhlWcrT6JMk6RghEKo1TQM3BcfDT1fc0cjzHIYeXldVVacZfZVliYEcR9RbllXXdYeth+Nb1zW8DcMw8jyf5tTRtm1RMDxd07QBfVnHcTAeY9T3fV/6AaPCOY+iCI+GwgghDvE8DuRY/UsIEYYhlAQF4Jx32IGiKNCaCEEZY1VVua6773pMBBiGgaqr69pxnGkCsDzP0alRq5ZldXTtLMugtDISy/Pctu2xy9kDqfNopqZpMB3zJKrtdUQ7P6rdOKKdT5IEphvmQtf1k43tlbhUPVRCVS6CUMI4dgGIUYAjCwPq+37btlmWlWW5b1iCO6LrelEUmqZxzuM4DsNw2lIPj+M4dV3DP+Oca5p2dXW1Xq9Vh+exhwcMclmWtW2L4TzLMrizT15flqVlWdIBZYzd3d29efNGtZyq9aDrehRFqEnGmG3bGJiHcnfyPHddF8uAVVXJSceOxcAnUa2H79+/L5fLqqpms1mSJJj1dF0XH17OUP1LtZ5fvXq1Wq1M09xut77vI+TIsmxf7IHv0zRtmiYIgqZpsizLsmzf/S3LKssSXhRisKurqy9fvozdvzRNg8ILIeQMOjrFk9fDZ8qyrGma2WzWNE2apmgLpeeOTVVVpmlKVw8dAT3iyetV2wtRK+bmhBBt297d3S0Wi7Htm67r6/W6bVuIZlmWXOcfhGPZeZgmaaaQb5Jl2anplSqXqoeqqMpFEErwaWbNiRcihOCcw9AbhlHXtaZpz1qrIAjiOLZtuygK0zR1XT98zOunGBNMfktQQvy777moot3hsF8Jx+4meZ7rum6aZlEUtm3HcRwEwbO/apoGPs3E2S9TtjK7V2Oln6i2V5Zlrutyzj3Pq6qqruuxW3ya/uW6bpZlQog0TU3TNAyj+w4IFDnnWZZdX1+naarrum3baZp2/ErXdUSVvdcMe9c2Fvk1TZNh2JOkaYoAOE3T6+vrLMs457ZtDxgDPImqXAd2fIlqe8ES7g4cUzoAu7r3uCT7mNLOq9LDNB0F0sN+9LCHcMzgpDHGhBBw3kYtZz//UP6WPde/iJE473kaYh+YuSmKApPu+LLD25jP58jf8DxvPp/jyy9fvkxQ1FGRi367GRTv378/aqGeQK50YU1JNl/HT5qmaZrGNE3LsrDU+a9//WvsckqVmM/nnuch90wqzMsJwxBBQhAEWAmczWYTuDiu665Wq9lslqZpVVVCiGHz047Vv7IsWy6X2+3W8zzTNOWWhn04joOR2HVdOBmapj0bfem6XlWVTKP9+eefBxXiCaDqSKs2TRN9oeN6z/PgjniehwlszvnY0VcPgiDYbreMsSRJ4jgWQtR1HUXRvutV2wtLT+zPmXI3NzfDSvEY+QiZY9y27YDTRsey83Ecz2Yzxpjv+0EQcM4Nw7iAzJFL1UNVethDgjgcWgE7D1RnOJAaxBjzPC9N0zAM8zzvSEGUt5K37Tdzc2orYKCu66qqdF1HggpTT+VSTYFTRdO0sizzPA/DME1Tz/NYZ0oV3E056y9bauwUxF093NXAoVJu5A3lDCICMFUz1e2OPyZNU/hPuq4jCxEtPrhcL+xf3es8j/E8D7XXNA2yELEPZ5+eYGNGHMfz+ZxzHobhdrvtqHyUR9Y25/8eUMbuX/J1KbICH/SIxwghttttGIac8/l8HscxdiIpPVcVVT0UQkifvq5r5Biz4doLGIaBqBUJYB33HwrUM/YfIlxH7z6EKe28aj1gqgixijRZPZ47NqSH/eghF62AEQoI4hyQ2fOMMVjDZ02867pwtmBGWad3YlmW53nyguVy+fvvv/co58sV8nBkzaBy9tUbFjTAZrN59+5d72eNB3LehBBRFAkhyrJM0/TZX5VlWRQFhoRffvll1BJKfv/99+VyiWrRdd3zvAFnsi3L2n3t4du3b9n9cu4E7SX9DPDgz5dw3P612wWEEA/+3EXq4d3d3dXVFX7+7Iu/sAyLnKWPHz/2KGGPqoDCb7fboijgwHUgL/j+/btcgVSNZieQC6/S+e233+Q3cRwXRbHvetX2whKN/DMMw5ubG9VC9uPm5mZ3aejZbNgHdTiNnVcFpglmCvi+f4KvQ1RtrAvWQyV62EM4ZlI6ce+8jUoP//CBbnT3L2IkaAXsPBCKMxz4X86567pfv35F4sfuVNYDsNgiL8AiTMf1+zjBFTBIgfVAy7JUs9vB2HKhTZGP8fXrV+xHatt2nxnFJmn8yxhrmsbzvB47cFS7PypTrtHJuh3K58AWOPyL+2NT1iA37wD9BSOQpml4s5ksxssZqn+pAhXCBi283yVJEtTwk9fruo51Idu2sVHK87yOF1FCCeV6OzZZ9VCGHv3LsixsyWCPusOTJEnieR62c9i2jbntCWIwVaqqgm4wxmRfGKq92L2pQRuVZTnZLiY8SD53d72omxO386ZppmmKjvzAfJ01l6qHSvSQi1bAiMOhAOw8OJcOdoIB2CCcoFzwraUTD/VQ7c4n2P0HkUsVPELcny5lGEZH9HtGvMRuHMggDkeP66m9/iKcsp0nPSQeQAEYcThnbykIgiAIgiAIgiDOBQrACIIgCIIgCIIgJoICMIIgCIIgCIIgiImgAIwgCIIgCIIgCGIiKAAjCIIgCIIgCIKYCArACIIgCIIgCIIgJoICMIIgCIIgCIIgiImgAIwgCIIgCIIgCGIiKAAjCIIgCIIgCIKYCArACIIgCIIgCIIgJoICMIIgCIIgCIIgiImgAIwgCIIgCIIgCGIiKAAjCIIgCIIgCIKYCArACIIgCIIgCIIgJoICMIIgCIIgCIIgiImgAIz4N3VdM8bKsizLkjEWx/EEDzUMgzHmed7un5ZldV+vaZpt23meN03DOUfJzxpN0xhjnHPP85IkgVxN0+y7vigKTdOKokCF1HVtmqYQYroSH0ySJChYlmVt2zLGTlAuIYRlWSiYYRhVVWmaVlVVx0+U5EKfkoqapunun+OBEnLONU2r69r3/bZtbdse6v62bbdt6/t+XdeapnHO5UNHRT6obVvDMJIkgdrsu142EGqe7TTfSaHaXrquM8Y0TXNdFz/0fX+y0o4Hur+u677vp2kqhOCcn2B7qerhpbKreJ7nSbXcdz2GeLQyu3cA5J/ny7HsIXGmnL3GE4MgbQQsYxRF//mf//n58+exn1vX9Zs3b/7nf/5nuVwyxpqmgfO9LwZrmkbXdSHEZrN58+bNZrNhjGmaBgfrfGnb1nXduq7TNH379u12u2WM6bq+z6e3LMs0zSRJ8Ofbt2+rqrJt+9TG/qqqMDDf3d397W9/Q3tNIFePMe+f//ynrutxHFuWhYHTNM19F/eQyzCMoihwwXK5/J//+Z83b96oFhIFU6Wqql3npq7roXydB7eq67pfCfv5KKZp7gaxhmHsi2nlf4Vh+Pnz5/l87vt+WZYdcz2DMHZ7wR4yxjabzd/+9re7u7skSUzT7J47eDlj+5RSru1263leVVV1XSPIHJWx9fBYjN1e0mjP5/PPnz+HYcg69bYsy7qubdtGK69Wq7///e9fvnxRfe6pxTbHtYfE2XGKs0rEYzAFiM4M+3541IEmlnOrHVfWdV1Vla7r0gftmMR6EtVACPOaKFvbtvJx++4jK4H9WRbVcqoydoBnWRYWSTzPS9M0DMM8z8uy3CeXLI8c7GezWRzHqt15msWl7XYbhiHnfD6fx3HcNM3YcnUsRj0JyoNetnsH+AdP0k8u2W2h9qrDc0d5nsTzPNRe0zTb7db3fUSVQ+kz5K2qKkmS2Wym6zrnPAgCudB0IKoBQ5qmQRBwznVdn81mSZLgDh31r2laEARRFAkh4jj2fb+fb6TE2O2laVrTNHEcz+dzznkYhtvtdoJOrdq/VNE0rSzLPM/DMEzTFCskEwTMqv1CVQ+PhWp79fA3sAgG7Y2iKAiCjp/sDvQy+6PHIufYeqjKUPZwgvba/S07zD8kBocCsPNg7A6W57njOIyxpmmqqnIch3P+/v37m5ubwWR4ijdv3nz58gUrWqZpIvCDP/Hk9VVVYX7327dv//t//+9v375hzunUZhxVwSKPaZpt28L4dk9jwy9pmsb3fSEEzD3WzZSYoPujydi97nXr7bHk+te//vXzzz8nSYJ1rbIsdV3v9p6V5EKExjnHEt9msxFCfPnyRXURrMcAuVwu/+///b+z2Qx/FkUxYArigxtut9v/+I//WK1WqjfpoYer1eo//uM/pG48u0wq3Tv8K5tvVCZor10Xlj1nN4ZiSrvRNE3btqZpDq66g6Cqh0ehx8Scqr8hFU/2sg7l32w2QRAIIcqyrKoK0wdwBlTLqXT9BBzFHlIAdqZQAHYejN3BcKvdebspu2I/Jbw8YxEEQRzHMhjTdT3Pc9WfKz1x7O6fpinyTNI0vb6+zrKMc479e4ffZEq5yrLEDpzu6Ovlck2j867rZlkmhEjT1DRNwzDG6DVCCCyee57HOcdDVe+gdH2WZa7rYs8k8tO67+C6bp7nQgjHcdbrteu6bdtmWTb2jqmx2yvPc9u2OedZll1fX6dpquu6bduqM+6qjG038jzXdV0GXXEcB0Ew6hP7oaqHx2Jsh973fWyFdV13vV47jiOEyPP88KzRS0rVm94eUgB2ptAeMIIxxrDnu65ry7LathVCLBaL9Xo9dgoiYywMQ+n1FkUBB6IjdWGz2cxmMznpO5vNoig69xREx3GwAYkxZhiGpmlZluFVEPvKAyeybduqqhCinODMK3KHMDYbhoEEyzzPx5ZLtb00TcN61O7CV0fKUw+5ELDhLSOc8yiKsFNCtZxK13ueh7G/aRosa6PYQ60kFEUBB3R3ssDzPNUm65H6Bd8Oz4X34LruvueiElzX1XW9bVss+E/wvoqx2wtpC1g0xqs4siwbO/pik9hDdt+/bNsOgiBJEl3X8f14jK2Hlwo2gDmOA0cCcSks+ZPXY6xvmgZjvRAiDMMoilSfe2p7v4eyh8RfBFoBOw8mSEG0LAvuAlI+MPyPnWONN2rAc4Xj27ZtWZYdAy2qIo7jN2/eyLc1XACGYbRtu1vncmPYYxzHqapKXun7fr+qGLv7YyTGZ6l7HVk6x5JLah28ASFE92sqeshVliU6rK7rmqbBXVPdI9RjhjIMw9vbW7xMsizLMZK4iqJA8nBVVdfX1z0cqR56GEXR9fV1VVVI7Ox2cRzHkf6QfJbMOB2PsdtrN99JPqvHjLsqY9uN3bkPvBIWMx2jPrQfSnp4LCZYAZOGWj5L7mt4zFD+xmm6r9PbQ1oBO1MoADsPpulgTdPgQdg82vFWt6HAI7DpXD66+ydlWQohkHhjWZYQYoI9D2ODBHq46YwxvMr2kNhDBmn9YpXJ9nIIISzLqut61xXuYGK5oHvoVnALyrLEUuS+n/SQC91Kart81dvhqA6Q8nF4WwNCvqqqhnqZQVmWpmnCRcbikpRR6T792mv3iU3TmKa5b8JCOse6rmO/6GnuAevRXnBzkbwghLiYPWAIjzHGYXJkmiZTQlUPj8WUe8DqusZSv3yV1z5e7m+cmvt6XHtIAdjZQQHYeTBBB8NmbvkeVTxubPXgO29BxKN334X4mF0pyFi8nLHb91jtdYJyocPKF8ZA7Xs46KrXK/WvHgxiNy7V4Ri7vS61f50LL9HDKTnB/nUUuzEBZA+Jwzmtl6USBEEQBEEQBEFcMBSAEQRBEARBEARBTAQFYARBEARBEARBEBNBARhBEARBEARBEMREUABGEARBEARBEAQxERSAEQRBEARBEARBTAQFYARBEARBEARBEBNBAdh5IM94tW0b5wh1H/KAMyh0Xfc8L0mSuq5xzuy+66uq0jRNCIEfykNmh5ThKXZPDjUMQwihaVrHQaKPi6TrOsr8JDhCRx7f6bru7p/jgUfgcfLPZ89f8n1fnrjKOe+Q64jEccwYO/DETKl4SZJ4nodzh09QLqhclmW7f3Z0saZpHvwv57yjfU3TbNtW9kHo/ASHrkh1yrIM1X7IIWBJksiTZIUQJ2g3CKCqh7ugMwZBMErJ/oxq/wKH6+EuME0wU2Mji+e67iHjsirHGr/G9jfYvWiGYRRFgW8cxxmk8IOjpIdHkYtzLo8pR+W3bduhJ5qmPRh92rZVPQWbeDl0EPM5AadcHueKc9afvFIIAYupaVpZlriso4PhgjRNPc+7vb1dLBaGYTiOI+3OSFiWled5Xdfr9fr6+hoF6Cgqyvnt27f5fB4EQRiGq9Wq4/4yupPggMJ99TYUTdM8PgnxcWEktm03TQPLbtv2bDa7vb1l9/KOx4E+jSTPc8dx5FmT+NIwjGdVq2kay7KkTo4de8jB70B0XX984q0c0vaxWq3CMAyCYD6ff/v2je1vL9SP53lpml5fX6/X67qu8zyXAdKB2LatdD2eK4SAEaiqyjCMjgC4KAo5o1EUxXa7vb6+Zs/1x5fbDVU9PJeDR6c5OFtJD2Xry0pzHEc63Aei2l6q/auHHu6aIzwLxkqpnKo+KOqZc25ZVtM0pmnWda1aOR0MNX71K9Ko/kbbtlLDDcPo1xPHdl976OEgcqm2V1mWjuMYhrFYLG5vbzHQsOfGo9evX282mziOoyhaLpc9ykm8FEGcCZ8/f97tJLZtd4wu/B40cXNPx/3jON79c4JpNoAp833F2FfIzWYj527lQtM+ENIgtPv48ePoIjEmH+R53mw2O8RvXiwWYRgyxubzOb6ZYHJaVQmLohBC/Prrr/KbNE3TNN13/a7isT+r5UnJJYT45ZdfhBBJkkRRlOd598VS5O12i1ZjjPm+31GkB/9blmWPQvaoinfv3q3Xa3mHoii6pVutVpvNRghxd3cnZey4fhC7oVoPbdvK2jh8ZW/3WW3b4iajoloP0mILIaqqEkJ0G21VPXRdd9da/vTTT2xnmfRwelSFUv8Sinr4wArBQMFYjc3Nzc2rV69kzViWpTpL8iwvH796yDWqv5Fl2a4O3N7e/vzzz9PIpYqSHh5RrgdzXgcORmEYSnE6xnFiJCgAOydWq5X8XFUV7MKTZFkG9yKKIunHdwwMjuNommYYhrS5U8hzD564XC4Nw9A0rcPQS/cOQtm2vVgsOgzN1dXV7nz/bDbD4sPYEmFNbzabyUcbhnF1ddVRVGBZlvRo4YGdFGVZ3t7e7hp3TdOk5/cYqXJBEERRJIRo2zbLsrHL+Ww9P0DX9VevXqGEoKqq79+/dzxitVphrJUDWEdMlWVZ0zRVVd3e3vYrIVCth7Zt//jjDyFEnufb7fYQxxcURSFbuWPF7Fh2gwIwiZIebjab3RvGcbxcLieYa+vRv8CBehiG4a4C+L5/e3vbY45DVS7O+Q8//MAYs207CILBQ69jjV9gPH8jDMNduboH8Q6mqAUhhIoeDiJXP1DU29vbqqqapukYZ2XXgNHI83y3rYnJoBTE86AoCmSpaZqG9CrTNHVd39d8cpEhy7LFYiEzTPYtPuzeZ7FYYMq8rusJUvWwTI+Hyu+7y7mbM4Okne6nIJFd7PhtY6s9yo/9GEjk6E6KQ6rJ1dVVFEVN08jkmWnK2eNXcNoMw4Dz96xeOY6zXq/l7PvYcqnqrdQKaEhd18/6UrtSP9teu/WzXq8XiwW0QjXlSfV67A2QuyvxJYzJk9cjK+zu7i4MQ13XZUcb226o6qGgFMR7VPVQCJHnOdxE0zR7WwCl61X7Vw895Jw7joPcLcSuSiUEh4fx8rlIO8SuG3xp27ZqCnQ3Lx+/VNtrAn9D13UMIkVRaJrWNE2Peht7HOmhh4PIpdpeSMEVQmBw2S1Px/13c3Q7BnFiPCgAOxtUe0iSJIZh2LaNDHXDMJAW/CRIMNhsNqZpGoaBuRO5I2s88AjOOTYxV1U1n8/zPN9nsDRNw+4jOK8wbTBzzz5L13WZCzcNnHM8VOlX8F8h40gF6w1KpaSHnufVdY0pt6Io6rruzo4YhN47CpqmOSR4kK4J3BQZA+xz4JD4N5/Pq6qq69p1Xc65zNRXKqHS9QDv/+CcQ7oDLQm6GETbd82x7AYFYEBVD598YncTD8jh/WuXQ/TwyWf1MKH99AHvoYHz3TTNIXOCPZh4/BrV33hMv0qbcjTvp4cjKcMDMJQIIfCyJdM0N5uN4zj7pjmw/g9ZdF2HAZlgbzzxAHoL4nmAPiyzRxhjyDbed33btr7v27b95cuXH3/8sSzLNE077GlRFHEcu65bVVVZlsvl8tOnT2N7UYwxz/M+ffq0XC7LsqyqynXdOI47povk+xsw3wO3viPCsSxLJthIOzjB237kI+RDTdPs2GthWRbmonRdhxHslutYSMdOeja2bXdMZnPO0zQty/LHH3/88uWLbdu+7w/7orBBkAOP7CPoCB3Xw8+QL6sU99vQnwQZSlmWQQ1Wq9WHDx9Uo68eYKCFgyjfc9VhB8qyhFXBFg52P4mw7/pj2Q0CqOphURTSuko/coL+qNq/VPVw1wpJ06S6nNUDxLqY4NA0TZruoe5/rPFrbH/DcRxkQ2AaRb7LZHhJXoaqHh5LrjRNP3z4sFqtoDBZlnUnxMqlVEynwoBQ9DU9tAJ2HmDiEPOdmIbBBNW+sVO+A0qmHsnFoiev9zwP7+3FZaZplmVZluXYizB1XVuWZVlWVVVypT4Ign2+KZa/cOVsNttut8+u70NkjJQI2Nj4PgceCtMGJ7j7oZgnsywLJUTbYTJ1gnKqIt+OJSXad5+2bWUDwU2R71HsXeZDUN3WgvIgpJcLCN2Vg1nD7XY7m83wGYsPT16cpim2RuDKqqqg9qorDx0nNDyJXC7GnzAaHStUuKAsSwzJSLnpSD0aym70SP2iFTCgpIfyezkF3nvNR+l61f6lqoe7hgg638+xUfVB5TIC/kTz9VjZ7mCQ8Uu1vcb2NzAWCCGwrISn9MgWGdt97aGHg8il2l6GYcDwmqYpM8zjON5n56G3j02H0kOJl0MB2GWy614cOMTCg5HDCfyAsR2UlzhSB3J2ck3pIKpyLnJN4PiqIt/dj+AE1ahqfidwONil2w3Sw5froSqqch1LD0/N3rIj9S9VerTXgM8d+/7Ty6XKBHaDGANqIYIgCIIgCIIgiImgAIwgCIIgCIIgCGIiKAAjCIIgCIIgCIKYCArACIIgCIIgCIIgJoICMIIgCIIgCIIgiImgAIwgCIIgCIIgCGIiKAAjCIIgCIIgCIKYiHGP2SWIUwAHYuCYY8ZYx4GSwz4RDz3kRI7dg5gZYyd+EPPp0++gWMYYDoo9RD1UD8CVB6rKI5h6HGLT4wBWpYOY+0H964j0OxAcp+viXG/TNFUPBFelR/+SB+Ayxg4/EFzX9bqucQ57VVVjHwje4yBmnFA8m8222y0+49SmJy8+llyqBzELIXRdR7di96ZggvPlJrAz8oBpfNN9wPSxwEHMVVWZpon20jSNDmI+fegg5svkr3Cg6iFYliWEgJ+BOwshMLoM9YgnwSM451Ic0zThUuwrJ2w9BlrGWFVVmqaNXU5VLvUAXHgbQgjpzVdVBZe941e7rn9VVZzzfY5RURSMMYxwiIh2deNwVM017i8fVNd1t0SqdoP6VzfTHMR8uB4yxpqmKcvSdd2mae7u7v77v//706dPSoXsgWr/KsuybVsEyZDFNM22bZum6XiEZVlZlum6fnV19Y9//OPDhw+q5VRtL8gihYIffMivZMc3TVMI0READyKXKtBAKRfnPMsyzjniq8c0TdO2LeJDwzCapnEcp23bQ2rj5eUcD1kDX758+a//+q8//viD3XfSUZ/bgw8fPvzjH/+4urrSdT3LMsuyOoxbXddCCLQX+7MBIabkFDWJeDkUgD1GOgFj3PxJOOd4qNKv6rqGm6g6zTkBlxqAgcODB8wNY9YQPiKq4vBhDF6y6spDP+1t2xatBuk6+nUPuyGh/vWYsQMwVT0siiLP8/l8XlVVXdeu63LOu1dsBqRfcA6Hvruz2LbtOM5mszFN0zCMLMuEED1WevvZDU3T0GrQxg4HXdf1tm2xiiKVsG3bfSZ0KLl6oDr6QxYZME/DBNYmSRLDMGzb5pxblmUYxjSdRQl0YSFElmWGYZimudlsHMfZt6gFlUOf0nUdBqRt21Ob8L14KAC7TCgA2wVpOZh/3Q0DxkPWvKZpcLWxBrIP0zSrqrq6uoqiqGkamcsxTTkP51wCMNX5PFk2aEhd18/mY+z2jmfbCz5ZnudyOr9fDah2Dc45EpaEELJOOrJN+gVg1L/2oaqHPVbAVPVQfl6v14vFArWnGsSqotq/kEx1d3cXhqGu60hBZPt1clfexWKxXq/xFFWHUvV6LCPUdb2bnof4at9PdsOzyeRStTYypEd4zxgzTbMjBRT3h/rpuh6G4d3dHTqd0nNVGTsFUdZblmWLxQKNxcYfv1RBMC+EQKeW3x/SXvLKUxPqr8DJTbETxIBcXV3FcSyHw9ls9v37dwzqoz63aZooipDoz+53XARBcHd39+T1GKju7u4sy0qSxPd9du+BjVrOS0XVsYbTgGx4dj+exXF8dXW17yffv3/3fd+27TiOsa8GXuOTF0dRFASB67r4M0mS5XIZRZGqg9IjYP7+/fsPP/wgdwjYtj1grj/1r6OjpId5nmPX3GazWS6X+HLsDWBMvX+h/FdXV2VZ+r6fJAm7n/F58nrHcbC7bD6fr1YrfNmjcVXtBuf81atXX79+tSwL8UZRFN1zAa9evUqSpCiKIAiwv6sjUBlKLlVgIjabzWKxgI9e13UURWEYPnk9upLjOFgvQjccO/pi4wdCeZ5j7WvXVnQH2EdB9ovFYrFarebzuaZpZVnuSxmFiXAcB0ajKIokSXYjN2IiBHGJYIkZnw/UBJnFLhVD3mHUcsoS4tFj5CLbtj2bzZC28fHjx8Hv/yR4kOd5s9nsEJd3sVhgeJvP5/gG7tSoTNle8g4T6FUPfvnlFyFEkiRRFOV53n0x8j2EENvtVjolcOufxHVdGX0xxn766SfGWPd2rKF49+4dJs4BktD2ydXDbjDqX8MBhxL1j11SyOocSg8f/29Zlt2qPhRK/UsIsVqtNpuNEOLu7g7fbLfbjuvjON79c18I2k0PuW5ubl69eiXvYFlWhzZKIxAEAaR7XPITkevz588yRGf3yZD77i+7EjpXGIaX4c3ze9h9Ai3oUZ9j82C73YFGANMiuIM0JsRkUAriZSIoBZEx9tTkIu4/wQz9Y0E6ZjqR74Gahzt7e3vL1FNiVOmxB+ksUhBVU6qwN+NBMNmxkgBWq1UYhkEQzOfzb9++sf3ttbs1QlaaTEBSKqfS9agHIURZlrquIx2xYwZd1W5Q/3q2nErX93sJh5IesvsdI9fX1+v1uq5rLIsplVMV1f6FLVJQ1KIottvt9fU121+fkBebo25vbxeLBRZkVF8Cobqygedid1DTNEhHfNaoYvU7juPNZvP69Ws2vlz9FjmRniq9go5+jfJfX19vt1vUoWEY2FzU47mHM3b/FULI9xjBhDL1Tj0BWOwyDGOxWNze3spdnd3t9fr1681mE8dxFEW7wTYxGRSAXSYUgAHcTXpmrutmWTZBbjoegcfJP58Vzff9qqrku7zlG9vGQ7X7n0sApgp8wSzLMEWNPzt8X+z6kO4Xu58rPaQqsFNfJiCNCrJlhBBStG5U7Qb1r2FRDcBU9RAVJbchmaaZJEm/RRUlVPsXQNkQHAohOl7wgBvKAauqKrS1ajlV7SH2SnHOpSp2g92YclqE3Y+z++rhWHKhpTjnB6bbYRshnoJsTGSNnjvyNRW2bX/9+tW2bRzeMEGXUWVXN9DBO+ywfG0Mu9cNNN8FpGSfFxSAXSYUgBGHQAFYP3r0r6Og6tCfi1yXygTtdRQ7PwGoKLlXB2aqh31TvX5se3h2cl0qpzx+0bh8ptC7/wmCIAiCIAiCICaCAjCCIAiCIAiCIIiJoACMIAiCIAiCIAhiIigAIwiCIAiCIAiCmAgKwAiCIAiCIAiCICaCAjCCIAiCIAiCIIiJoACMIAiCIAiCIAhiIigAI/6NPOdenp4+wbkf8hHy0d0PxQGIjuNomobjcXzfH7uQPZAncsgzfCzL6jjPp7dcOKX08OtfiGp7sXvRGGM4fhTH4J4a8uQlKU5Zlhdw7o1UOVR+0zTdR99yzuXxUDh3yHGcQx40sR5OxlHkguKhLTjnHV2Gc15VlTwqF2fgdtzZsiy0LBS+WxnOiLIsZXWxSUauXVCNsmKlzjyJPFqaMVYUBc7F3nfxceU6nEsdlwliVEjzCMbuTWfTNHC/TNOczNa3bQvzXdc1HMQOn6+qKsMwMCyhhEmSdA94R4Fz7jgOKlPXdZS5o0pV5XIcByEQnDPf95MkGV6Mp1BqL9/3q6rCZxTYtm3pL54OQog8zxFyoBdczMCsaRqawDAMBMx5nu+7OMsyNK6MxPI8t2173/VH1MNROZZcQogwDBEtwyBzzp916G3bjuPY9/2yLGV3e5KyLIUQct5E1/Uoii7g9FXLsjjncn6haZowDFVPH+4B5zyKIqgKZjCFEN1zTFVVlWXp+34cx7ZtPxswH0UuVS51XCaIUTGOXQDiJID3CXskhGjb9u7ubrFYjG2bdF1fr9dt22JQsSyr20GEYwRnyPf9tm2zLCvL8tR85bZtr66uvnz5guETX1qWtW9sVpUrz3PXddu2bdtWzqGaptntfj1ZTqXrVdsLEkG6OI51XXdd13GcUxvzNE27u7t78+YN3FN8WZblqfkQqnreNM1isdA0DRoCjeoImF3XZYxlWdY0zWw2a5omTdOiKMbWw1Prv8eS69WrV6vVyjTN7Xbr+z5C3yzL9sXAmqZFUTSbzYIgSJKEcz6bzaIo2vdc27azLEODBkGw3W7DMFytVq9evVIq56lRFIXrurZtt20bxzEqYblcfv/+Xek+qnbp+/fvy+WyqqrZbJYkCaaWXNfdN8fUtm0YhtvtNkmSIAjatt1ut/P5fN9zh5JrbC51XCaIUeEnOJtCvBw0K/yGQyY4YSh3h4EpFWO3hI9L8pggCDB9WBSFaZq6rnfEAMcFOT9t20pz38EL5cLPlYrXr5UPby/f97Msa9vWdd31eu04Dtaa4OifIJjE1TRNhmFPotq/jstuK6Ol9jlGaZratq3repqm19fXWZZxzm3bHlsPz4IJ5HJdN8syIUSapqZpGoZxuHYpXWkYhmmaaZoKIbIsO9n+qIQQoq7rqqo8z+OcozJV76B0PaqOc+55XlVVdV0ffgelKyeWSwjBOZcJe3Vda5r2bHR6qeMyQB3uWv7ToV97yd+yU5Xr4jmt+QniWGApgzGm67qcIL+5uRn7ufIRMuenbduOZQfMBBdFoeu6nGU8QSv/888/M8ZkUpCu690OvapcYRjCOQuCANn2s9lsAq9Xtb2SJMFlWZZJvTpBb+9f//oXu0+bMU2zaZrDB+ZT5v379/iQ57lMbOuY7vU8D3bA8zw4eZzzE9TDsTmWXFmWLZfL7XbreZ5pmpzz7nxdrMhVVfXbb7+9ffsWObT4dx+2bQshqqpK03Q2m61WqxPsjz0oioJzbpqm53nb7Xa5XKpGKT1wXXe1Ws1mszRNq6oSQnTk67L7pjEM4+3bt7/99ptsvo6fHEUuVS51XCaIUaEVsMuk3ww9pkWbpkEiIht/1y9m4rHPQdd1TCJ2XC+zBTzPS9M0DMM8z08z1YExxvn/379g6Pe59apyyXbBdBe7dxBVu7NqmKHaXrgYGx6EEFEUBUFw+OTcZMht9LKzoGb2Dc/HWgFT1XPUM/alNE2DRZXunwghkJnGOZ/P53Ecd7y6Yyg9PM3+yyaXy/M8PKVpGmQhYo/Qvv4ip73ZU+vSj8F9TNP0fX+73TZNI4SI49jzPKVynhqQt6qqJElms5mu6wie0zRVuo9qimmapkEQcM51XUcWIu7wbH9hO6tSQoh9ejWUXKp2XnVF5VLH5V1OeaWIVsDOFUFcIti9gM+HqAGSUuSfYRje3NxMU9Sbm5swDOWjn826cV0XTslsNsM3pzmJ9fHjR8ZYEATPvpoMKMllWdbua6bevn3L7qchlRi7veTi2Hw+32w2uAOmik+NX375RQix3W6LosAERAeq/euIvHv3Tta8EKKqKlnyx0jBv3//Pp/PcYcJ9PDUOK5cDzpIR39Bzlvbtrvt1eH1Pgi/8da+C+BxjfWr+X5Pf1yr++4vm2Y+n3///h09EY14UnLJXb5SnGdDqUsdlyWyZjrs57Ho0V5nIdfFQytgl4lQn6HHxAk85rIsJ9vIgQfJ58op5yfBvA7y4L9+/YpEuLqun53Xn56yLD3Pw9QaJgg7NvGrylUUBVLt4RTWdY1NCOOJI1FqL+yOwOZsz/OKosByyqmtgDHGLMtK0xROQ1VVaKx9I3SP/jUIPcx1HMdBEGB+2rKsZztLkiTYaoJ3P+BdfPt8qaH08NSGoWPJ1bYtXuSNt8nh7YsdLw6Vs92mad7d3WHjTYfeQqIkSfCmBGx3PM3+qASqCNWlaZq4dyhVV2BU+zKqDp6rpmmoWKk2j0HTNE1TVdXV1RVmQzpM6FByqSIUV1QudVzeRZzwSpFqez34LTtVuS4eCsAuk2M5iFNyyoZjAoOIYVgOcngcded+oOrE/WlghmF0ezlnFICNzSB6SHLJ68lu9AMVJYOZf08wK/bNHtePbTcGkUuVS3XoSa4nf8tOVa6L57QydAmCIAiCIAiCIC4YCsAIgiAIgiAIgiAmggIwgiAIgiAIgiCIiaAAjCAIgiAIgiAIYiIoACMIgiAIgiAIgpgICsAIgiAIgiAIgiAmggIwgiAIgiAIgiCIiaAAjCAIgiAIgiAIYiIoACMIgiAIgiAIgpgICsAIgiAIgiAIgiAmggIwgiAIgiAIgiCIiaAAjCAIgiAIgiAIYiIoACMIgiAIgiAIgpgICsAIgiAIgiAIgiAmggIwgiAIgiAIgiCIiaAA7DIRQnDOhRBpmvq+r+s6Y8wwjH3XW5a1e4Hned3XnxF1XTPGyrIsy5IxFsfxsUv0FwKKp2ma67qMMc657/vdP4HWWZYFnQyCYPxiMiGEZVlN06AAVVVpmlZV1QSPPjWSJBFCMMayLGvbljGGanmSoig0TSuKAq1W17Vpmvj5qKBTp2m6+yc6+JNIQeRPpJgnBYrEOdc0ra5r3/fbtrVte9/1qHZN02zbzvO8aRrOOWrjSY7VXqqo2g3TNNu2tSwLsuu6XpYl53zscuIRQoi2bQ3DSJIE1bvv+rquOedN0+R5btu2pmmsc5y1bbttW9/367rWNE0+bgRRpuZSx+VLlYsYg0vwsInHaJqWZZlhGJ7n/f7777PZjDHWNA0GtseUZVnXtW3buGC1Wv3973//8uXLpIUeATlWwZuPoug///M/P3/+3Ps+F8bYckmV22w2f/vb3+7u7pIkMU1zX2wjfSaMXmEY/p//83/evXs3aiHBP//5T13X4zi2LAvFME1zgueeFFVVwdO9u7v729/+ttlsGGO6ru+LwSzLMk0zSRL8+fbt26qqbNvu8EEHwTCML1++/P3vf1+tViihbdt1Xe+LwQzDgGMUhuHnz5/n87nv+2VZwiyMR78YoKqqXae8rut9Pjr6lxBis9m8efMG7aVpGgLOxwzVXqdmN/A9plEsy4rj+H/9r//1z3/+U/W5/eQyTXM36JXK9hjZNPP5/MuXL/P5HPHYvnH5QdMjfutRwlMbvy51XL5UuYiR4NTSF4n0LdI09TwviiLHcSzL2jcwYyqOMda2LT5zzrGGNlmZVUHZ5Jxxx5V1XVdVpeu69K2lvAfSsQiwr2yoQHY/Hnd4RY9/yw6QCy0lR+h+7aUqlyqapjVNE8cxXI0wDLfb7bOFNAzDNM2macqyxMUHVt1LysnuWw3foGb2OUa7rTPBRPuD5479iO12G4Yh53w+n8dx3DTNvv4i20U6nbPZLI5j1XL2uF72r92e1VFOTdOCIIiiSAgRx7Hv+90NN0j/UrUznueh9pqm2W63vu9jFmCf/stKYH/Ww7Hb69TsBvqpLJVsKdX6V130TtM0CALOua7rs9ksSRLc4dn6Zzs6L4TYJxruU1VVkiSz2UzXdc55EARyIfdATnD8Yhc6LrPLlYsYHFoBu0zQnTC7yRgLw7B7YNhsNkEQCCHKsqyqaj6fM8Z+/PHHc18Ey/PccRzDMDjncnB9//79zc3NcQt2IqgODD2AH4/PURR1TGMzxhzHyfO8rmshhFyAurm5ef/+/aiF/Ne//vXzzz8jX5cxVpalruv7oq/Lpq7rMAzxebPZQEP2jeVhGKZp2jSN4zhCCCytTBAl/vHHH2/evGGMzefzqqoQqAdBgCWgJxFCRFGEz0EQVFU1wQqn6sRBHMfL5XK73c5ms6urK8ZYURQyV+0xkKKqqm/fvr19+/bbt2+IGPetwAzVXqdmN7CIZFkWlkA9z0uS5Oeff/7Xv/6l9FBVuYIgWK1Ws9lsu93e3d0xxrCcuK/d0TSGYbx+/fq33357/fo1Vs86VBEKAGXYbrfL5RKrvmfNpY7LlyoXMRInvcRBvJA4joMggAWvqgrj7oG/Pf25kENmbjAQ7g6r06RwnMsK2NjdH1sdOOdZll1fX6dpimyxfTO4j939iQ0Uto5omtYdfV3qCliapshDTtP0+vo6yzLOOfYXHX6TIAhUdz70k+vwmnddN89zIYTjOOv12nXdtm2zLOvYWTRI/1LFdd0sy7B31zRNeHIH/ra3Hk7WXoejajeAruvYKNWxG7AbVbmyLHNdl3PueV5VVZg5GvxZQggsqniexzmHkiiV89TGr0sdly9VLmIkaAXsMsGGbLzAoK7rtm1d18VO5Sevx9bhpmmw61cIEYahnDA+X+BC1XWN9EshxGKxWK/XE8zgngVjp/Yh4MekO7bUZ1nW4UVhL7thGGVZwpdar9eLxWKCFMQvX768efNmd+Frgj1CpwbevoPXb2AHaZqmeZ53pFQhmGnbtqoquPJjbwADURRZloX3H9i23TQN3jDx5MVwWF3X1XW9bVtMVD/7PpiX0yMFEUXFZBn8oSzL9r2HQ9O0zWYzm81k3vhsNouiaOz2OjW7gbWvpmnkfqo3b958+fJFtf5V5UrTFK8J0XUdET5jzHXdfVXatu1uOmXbttvtdj6f73tuURQI8HB/fOl53jRdbDwudVy+VLmIkaAVsIsFsyBCiEMcyjzPLcuCmWiapm1bDP9j5/q/hENmboaS6wRnpM5iBQyrr/gsZemYwXUcpyxLVBTms+HWjJ0N2LZtWZaO42DUFEJ0vwL0UlfAMKOPz1Kujpc0OI6DpXX86fu+fMGDEj32IHHO0V54uqZplmXtW6lDauuDZyVJcmorYIyxMAxvb2/xcsKyLDtegQhgauI4fvPmzbOVf6z2UkXVbgDDMNB5YeelJTmcHnJFUXR9fV1VFefcsqwDQyPf9798+YK0/2cNSFEU2E1UVdX19XWPidFTG78udVy+VLmIkaC4/DLBe7SQT4V+mCRJx3S+4zjY94zNAx1rZefFpcp1LsjsNfn+LtM0O7yoPM/bttV1HV4vXgc/QTnhzct3WKPv/AVVxXVd+UI5NIHjOB0+JVba2f1bv7pDmmGR5wQYhiHXtfZdLB16GcnL9z2eFJzzKIpQSHQEhGEdP6mqqiiKIAhg4bs3th2xvZRQtRsIv+u6lidJyPWoUUGqiJwCwLxA97K5aZqWZSVJgt0B3a/9wOZGqDdjTNf1KIouwEu+1HH5UuUiRoJWwIh/c6wZ396c8koRrYDt3l9ppQgVJV8kgCntU/M5LnUF7FzkOpf+pQoegafg0fK1tE9yLu3V7/6nL9e56CHJJa8nuZ58Fq2AHQVaASMIgiAIgiAIgpgICsAIgiAIgiAIgiAmggIwgiAIgiAIgiCIiaAAjCAIgiAIgiAIYiIoACMIgiAIgiAIgpgICsAIgiAIgiAIgiAmggIwgiAIgiAIgiCIiaAAjPg3OG3GMAx53mX3gZKDgGNDXdfd/XPYs3ePItcEHEuuOI4ZYzh79Fken2ciD1k+a5qmeXDKCuf8QL3FMbtBEIxSsj+DY16lhuDPCzgbVJ65bNs2zovrFkrTtAdH3LRte6AOT4nswlmWoZt0K9W56OHYQGR5CDUGlO4zqQdhAj2k8euI4JD3B192HNJVVZWmafIU+6qqTNOc4DBVzjmexe7PLm/btkP/z8UeXjxn7wkRQ1HXdV3XpmlKi1MUxWPrMywwWA8cRF3XB/QRjyLXBBxFrjzPgyBo21bXdTgcjDHDMPbZbpTn27dv8/ncNM0wDFer1aglnAaMr6vVKgxDy7Lm8/m3b9+EEPvqv2kaGXbilMw4jh3HkQ7cgaiOkaZptm37YIKjaZph5zimR0oEWXD2KNTyyetRb69fv95sNlVVRVG0XC4nKKdqfyyKQv6waZqqqgzD6JiwOJYenhoYMjB8MMayLNM0raqqse3hBHpI49cRwRi3XC6jKCrLcrPZvH79mnO+zw7DwGZZ5nne7e3tYrGo69p13bIslZ6raufLsnQcp2ma6+vr29tb13XTNO3Q/2PZQ+IhgiCEyPO8KAr553q9fvfu3TQa+PHjR8aY53mz2cy27cN/iKK2bdu27dhyqdYnioTfHjKTfS5y4aG//vqr/CZN0zRN910fxzE+bDYbOdcuvZYnkTOjsoQd9XAspMjb7TYMQxTV9/19Qrmuuyv1Tz/9xHrN+PYo6i+//CKESJIkiqI8z7sv3tU61bK9hB5yff78eddpsG3bcZx995dNE4bhdrvFHTr0VgjRNI0QoqoqWRsP5oxH4t27d+v1WhajKIqOVjsjPVSinx7atj2bzTzPY/fDFDT24gAA1a5JREFUygRyjaqHNH4dVy7ZWYIg2Gw2uIkc1J7kwf/2W4ZVlUsI8SDG6zACrJc9JMaAi2kHWuKUKYoCC9m2bX/9+hWTPaM+sWmaKIrev3+/3W7xjWEYQRDc3d09+1uorjjAN5peLiEE5xxPwbSopmkHLuudslyYLXv//n2SJPhG07QgCKIoevJ60zQxLR0EQRzHtm37vr9erzsegYpCpbH7oWga31eJ9Xrt+75t23EcI7aUSSCPiaIoCAI52CdJ8v79+yiK5Jz9SOi6Hobhzc3NbDbDN3Vdx3F8dXX15PW7Wjdlnfcbhtbr9WKxwOe6rtM0lUHIA2TToLGKokiSRP72Sdq21TStrms4aujOquXscf23b99++OGH3a7d/ZOj6OHYboOqHl5dXcVxLNfkZ7PZzc1NGIbTrKiMqoeMxq/h6CHXYrFIkqQoCgxhbGdQe4zjOGVZapo2n8+R69Gvp/SrBzxrtVrN53NN07As9uSV/fSQGBwKwAjGGCuKQo70bdtyzpEeMLZ6yCEWScmGYcgknGc5xNAPJZeqQRx7ADuWXPJXMN+GYWB6ft99UJ7dHKdnvdhzCcB2S5XnOYa6faJB6jzP4c2bptm75lULyXZWEeu67nbozyUAg/4j7wsWA7lMHfXPdpqJ/bn5nmSQAEw1lRp7OQzDEELIMGm3sz/mKHp4agEYwEYssbPQMbY9HFsPafzqZgK5dnu9HMi6xzuwWCywlF3XtepEQI/rofm7cwGs0w4wRXtIjAEFYARj992vaRoMHrvD/wRwzrHnQelXhxj6Y8k19gB2LLngjx5uqTVNk15s0zS2bRdFoWlaR1ufRQAmXS64X7KJD28FTDfIOftREUJAVQ65kp1DAMYUPQYkRKHCdV1Hw3Xs1WFHWgGTj8bjZAffJ+mx9PA0AzCAoWQyx2ZUPaTxa1hU5cLeQgxbCHIMw0AjPnk9ElA3m41pmni/iBAiTVOkxR6Oqs57nocEQry8xzTNzWbjOM6+iZse9pAYg/Peik0MBTo83qkFa9hhZQZEOuJyvDRNc8C3IR1LrrE5llxymJR7tGzb7piel29bwvxcWZYIBsYu59jous45tywL/iu7X2Xad31RFHJpVzq7E7SXHFDliF5VleqO8BME5gJ+Nj5nWdbxJgm5JILpAzTcCXob6MV4kZp8L1mHN3Yuejg2lmXJrEs5lExgZ8bWQxq/jgtaFsMW+gvvfMtoURRxHLuuCzO7XC4/ffqkGn31IE3TDx8+rFYrdIQsy4Ig6BiXz8UeXjy0AkYwxhgmaXYn8+Rkz6jPhS2DCZAmeMCZtqHkUp2fG3sG8VhyAXh7u0PmvvtgDQEziLPZbLvd4nN3kU5/BYzdZ9Fst9vZbIbPaOUnL5bfy6nHfhKpthcaCD6EXBjpuMm5rIBh7hzrP1j5gZLs03/U+eMm63jEICtgqjHA7hPZvRnpnkE/ih6e4AqY1G3sfsEdxraHY+shjV/dTCDX48Gro5ye52GfGK40TbMsy7IsVU9eUX11h2EYeJBpmlKj4jjeZzd62ENiDCgAI47J2Ib+WJBcvTmXAEyVQRx6VfAIPEW6OBcQgE3AEVMQR+Us5OoXgF2k3TgKNH71ZhA97HG9kp0nTgRqIYIgCIIgCIIgiImgAIwgCIIgCIIgCGIiKAAjCIIgCIIgCIKYCArACIIgCIIgCIIgJoICMIIgCIIgCIIgiImgAIwgCIIgCIIgCGIiKAAjCIIgCIIgCIKYCLXj4YhjcS4HPqoij6rAQczPnlyB8y4syyrLkjGW57njOE3TnNp5I5cqV13XlmWZpllVla7rdV23bRsEQZqmg9x/9zBueZTKBJUwwcG+RAdj2xlVdg+tlkdm9Tj86tTkStM0CALGGJS8qirGmGma6Gjjodq/NE2DDZR1jpNt9xlSeQAujBLOsa2qSvUA3LEPYj4XLnX8UpWLKR7EPNT4paqHOIi5qirTNKGHmqbRQcynDwVg54GmaXIo0nWdMZbnOefccZwnr2/btqoq9KjZbNa2bXfvQkeVIxb8jwnO8sMAxhiDK88YM00T1uTJ603TxNiMXzmOU1WV9JZOh0uVy7KsT58+hWF4d3dXFIXrumVZwvUZBGhpURS7ujeBHo7dv4huTk3Pi6JgjNm2vXtOa48zW09NriAImqYpy9J13aZpoij68OHDp0+fxn5uj/6F//rjjz9+/PHHP/74oyiKjsAmjmNd1y3LyrJM1/UwDD99+vThw4dxpPn/UZXrXLjU8UtVLsYYwv7tdovPpmkKIfbp4VDjl6qdKcvyw4cPURRdXV3Ztp1lmWVZmGrZd38av04BPvaR9sRQKJ2njpkYzMHouo7pjbZtYX323RzmCUeqT2k6OeeYR1T6FUST89MnyOXJhZVSzrnrunVdV1U1n8/zPIfDOgZCiGmqYtT+xe6HYSkL5xzTxsOUfg94BJ4i17Q7ujauRD1MOXt9+sMQ51xOaR/OqclVFEWe5/P5vKqquq5d1+Wce56nuoLdQy6l/sUYS5LEMAzbtjnnlmUZhtFRSNu2HcfZbDbwp7MsE0LAWKmWUxVVuc6Iyxu/wOFy6bqO4KQoCimUXOY6hH7jl6pGoQsLIbIsMwzDNM3NZuM4zr6wqsf4RYwBBWDnAXoIUh3g7JqmiWDpyevRgZEJgG+6x4ndBei2bTnnSOSYwEHEv5qmwcXpduWR/HZ1dRVFUdM0UsBTU+NLlQvpDZzzxWKxXq/l90O5INBSx3Hg6VZVNU0NjN2/GAVgnZxayhbqLc9zNJZpmv1q4wTlkp/X6/VisYB1UnWyVeXq178YY1mWLRaLPM8fl3+X3fvANMHxVXUoVVtZVa5z4VLHL1W52L0pwGfHcaCKHXo4yPilOv2N4FAIgU69W54nr+8xfhFjQAHYObHbu+q6TtM0DMMnr0Q2MGMsjuMgCIqiSJJkt2c+SVEU+KFt21+/fn39+vXYfRJpMO/fv8cSP2PMMIwgCO7u7rp/aFnWer32fZ/de5ajllOVS5ULQCuWy+Vms2nb1rIs6SG9kDAM4ziW7p3v+zc3N2EYQpnHZtT+RQFYB6c2DEVRFASBrKgkSd6/fx9FETZNHc6pyZXnOXa/bDab5XLJ+rZyP7kO7195nmPta7vd/vTTT0hyxkLEk9c7jlOWpaZp8/l8tVr1LmE/DpfrXLjU8auHXIvFIkmSoiiCIIAeItp88uKhxq+X9MrVajWfzzVNK8tyXypsP/+QGB5BnAmfP3/GkAmQdLGvWWEBGWNhGG63W9wBi9RPgiwy+ed6vX737t3oyscYY+zjx4+MMc/zZrPZIYnIi8UCw9t8Psc3HbnOR+RS5cK6qCSO4wGVPE3TXS399ddfhRC7mjkeo/YvIUTTNEIIzImKnThnVPAIPBGPRjH2gdQUWcK/LK7ruq4r//zpp58YY5ZlHa9EgyFVF5Rl+bJ+cyhK/YvfwxgTQjT3dNz/gSHqN2UztlxnxKWOX0pySSMQBMFms3lS03Y54vj1YBvbg27+gB7jFzEGtAJ2TmDRXCbvduTsIqXk9evXm80mjuMoinYHiSep6xpph03TWJaFwW/snGAkbzxIaOmYYUK+B9b3bduezWa3t7cTlFOVS5ULi111Xa/X6+vra7nLQjWFaR9IpcBnuVyzmykxKqP2L1oB6+DU9Byptvhc1zX6skxAOpwTlIvd7xi5vr5er9d1XWNZTOk+/eQ6vH+J+/ccYCIfl3UYGVwAc3R7e7tYLAzDwLKYUgn7vQ3ycLnOhUsdv1TlAsvlMoqiOI43m83r16/ZflUcavxSHU+x2GUYxmKxuL29lbs6Bxy/iDGgAOw8yLIMG6Y70jB2wduZ0Lj4F9OHh6QEqD7rJcD2ua6bZZn889m3jfm+X1UVBldsqB37NcqqXKpcjDHTNJMkwQSzEIJzLvMZhgWvhEGOxOA3f8AE/YsCsDMF+/VlAtJZA0MkFW+3L4+Kav+SrwdAMrxt23hp/r6i4r/E/T6WqqpgS1XLqdofpxwrp+RSxy9VuXCuAMIVae3FYa8om3L8Yn/WeXTwjsDyJf4hMSAUgJ0HGFowumBwOvydyLvdrMOpOoqDSJwXqg79uXCp/YsCMOIBUGz5Rsd/Z8KM3Nbn0r96XN9bLuK8OFAPj8IE/YsYg7P3nAiCIAiCIAiCIM4FCsAIgiAIgiAIgiAmggIwgiAIgiAIgiCIiaAAjCAIgiAIgiAIYiIoACMIgiAIgiAIgpgICsAIgiAIgiAIgiAmggIwgiAIgiAIgiCIiaAAjCAINXDACOe8rmvOOU7eHBZ5zyRJBr/5IMgzYXFM57OVoGkarsS/+GbMAv7pEfLRF3BoWz9832eMaZqmaZrjOGynBU8HeZKPbCbLsjqaDCI4jgO52L2Y+7AsC8et4tifyZRBHkmk6zr+ffaQIqX+VZalNEe7j5sGVKOsWMuypnw6MSqmacoGLYoC55g/+6vTH7+IU+AvOhgTBNEDIUQYhnCJEFFwzgd0OPI8x81xzyRJuh3KY+H7flVV+Ayf0rbtoij2XZ/nedu2uq7jlNiqqibzfTVNQ1ENw4Djm+f5NI8+HSzLgifUti2mDAzDkC14OnDOHcfBEcnQlrIsO8KJqqpwDecclyVJ0tEfy7IUQsj4R9f1KIqmOX21bVvEVHVdYyIAYfCTqPYvy7I453J+oWmaMAzHPuWcMcY5j6IIJUQHF0KMMSFFHIuqqsqy9H0/jmPbtrtnbc5l/CJOBOPYBSAuikudX594SnUyVNvr1atXq9XKNM3tduv7vm3bjLEsy/Dh5TiOk2UZpvNN04QLVVXVqS1WwJt3HEfX9TiOdV13XddxnH164jhOURRN09i23batECIIgiiKVJ+r2l5N0ywWC03T4GSXZdnt+B6Lse0GfGLXdTVNQ9u5rmsYxtixqKpcbdteXV19+fIF4QS+tCxrn08PDYREvu+3bZtlGVr5yett286yrCgKTdOCINhut2EYrlarV69eKZVTFV3X1+s1NJ8xZllW90SAav8qisJ1XXSuOI5ns1kURcvl8vv370rlVLXz379/Xy6XVVXNZrMkSRAiuq7bESsSZ0TbtmEYbrfbJEmCIGjbdrvdzufzDjt/FuMXcSLwCWaJiJcjhOCcywSVuq41TTtwtEAT49+Oyc62bTVNq+sak/R4HKkHsYvrulmWCSHSNDVN0zCMCabP4zgOgmDUR6j2L9/3syxr29Z13fV67TiOECLPc9d1D3ziNMsOYLcXQ6h9DvqulZiyhGPjOE7TNFVVYSElCII4jo9dqC6QK9i2rQzDOoA4EM00TV3XuwNLzrlhGKZppmkqhMiy7HC9fQm7GgUN3NfF+vUvIURd11VVeZ7HOYexUiqh6niHquOce55XVVVd1zRiXiq9W/YEx68Hv2UH+IfEGFzmegVBEGOQZdlyudxut57nmabJOR92rjeKIjgxcRxjFny73Y49evUgSRLkHWVZJheUOrzDzWbTNE1d12mabjYbfPnmzZuxy/n+/Xt8kLkxmqb9BVOkZEBSFIWu61DaoZZtB+Tnn39mjPm+X5ZlVVW6rkPN9gERdoViO8Lu+4kQoqqqNE1ns9lqtZog+rq5ucEHLGoxxtq27UiVVO1fjLGiKDjnpml6nrfdbpfLpWr01QPXdVer1Ww2S9O0qiohxAkqFdEbTEYbhvH27dvffvsNabEdqcvnMn4RJwItcZwH57ICRimI54Vqe3meF8exEKJpGmQhIrliqPqR5ZF6iAFs7Jm5Hv2Lc46NAUKIKIqCIOj4iZQLvYxN1b9QHuxLaZoGi5Yd1x9rBWxsuwF333GcKIo8z0vTlHWm9g1Fv/baVQzEIfvWwaQIECoMwzzPO1IQcX/TNH3f3263TdPAWfQ8T6mcqkidtyxL13UsFnX/pEf/qqoqSZLZbKbrOuc8CAI09OGobgtM0xTWSdd1ZCHiDpc6Dv7V2NU32SWFEPvs9hmNX7u/ZbQCdiRoDxgxJJcaqFwqqu2FxC2MLldXV/hSDjYvBxP/vu/jhr///vvbt2+Loji1eWU4vnEcz+fzKIrCMGSd9VCWZV3Xtm3Dn16tVm/evPny5Yvqc3v0r3fv3skSopBwT1XvMypj2w1d18uyLMtyNpttt1sEohOskPSQ6+PHj//85z+DIMALM7pDgrIsXdfFyio2PjHGdF3fF7DBOauq6u7ujt1P8E8zQ//58+cwDOW+R8MwEP49ebFq/8J/maYJo4TorkeWqWrghKpDraJK5Z+qjyZOEBnGzOfzu7u7+XyOt93sW5c+l/GLOBFoBew8OJcVsEtVp1NzWIdCtb2gJHipQ9u2vu8nSdL9gjIlcCt5Q8MwsNlskJt3oNq/sOsDSSae5+EFGx0/gUMpPTOsV/Rw1Hr0L+xAwDqJZVnd0fKxVsDGthuQummaPM9/+OEH7GM83IT2podcZVl6niffpVaWpWma+8IwiID9Tl+/fkWCX0cTo3Ph5Wz4IbrzBBNn2KiGtMPdvvAkqv0LFgPmSNM0bJ+Tq82Ho6rzKBJeLoL3u/i+Tw73xYD3Z2D76NXVVVVVbdt2qO65jF8PfstoBexIUAB2HlAAdlwu1TD1aN/eengguKEc5JDvccopHFMydv+61ADsXOQ6Fzt/ggxiN3pcLxPSUKU9oj7iZOlhN85u/KIA7IiQpSAIgiAIgiAIgpgICsAIgiAIgiAIgiAmggIwgiAIgiAIgiCIiaAAjCAIgiAIgiAIYiIoACMIgiAIgiAIgpgICsAIgiAIgiAIgiAmggIwgiAIgiAIgiCIiaAAjCAIgiAIgiAIYiIoACMIgiAIgiAIgpgICsAIgiAIgiAIgiAmggIwgiAIgiAIgiCIiaAAjCAIgiAIgiAIYiIoACMIgiAIgiAIgpgICsAIgiAIgiAIgiAmggIwgiAIgiAIgiCIiaAA7DLRNI0xxjn3PC9JkqZpOOdN0+y7vigKTdOKojAMgzFW17VpmkKIsctZ1zVjLE3T3T/Lshz7uWODavQ8b/dPy7L2Xa/rOmNM0zTXdRljnHPf96coqCJQCc65pml1Xfu+37atbdtD3d+2bdwQmmAYRlVVnPOh7r+PseVC00MN2L1iyD+JHsRxzBgryxLmAgqzDyEE51wIkaap7/vobh31f6z2UtVDFEnXdd/30zSVYu67vqoqTdOqqsIPm6axLGsCOz82sBu+79d1rWkaLMYEcskHtW1rGEaSJBhG913fti1jrGkaOeQlSdJdTjkmQs+h9hOg1L96cCy5lKjrGo5Tnue2bcOt6rADx9JD4lwRxDnQtq2478bo/7AFHbiua5omY2w2m+EbuB1PYlnWrsf/9u1bxlgPB7SHaL///vtyuZQl9DyvI1A5I968eXN7ewsZ67pOkqQoin2VUNc1Ptzd3V1dXeEOaL4TpKqq3cI/+PMlFEURx7H887fffhNC5Hmuep8TlCtJEtnKt7e3b9686VHCocqzj7ZtYWrEyTsN796922w2suRVVcmSP0mapmVZCiGiKMI3sjkeM1R79eNwPZQlhFBlWSIM66Ysy6IottutEOKXX3559vrT53GN9av5fk9/4JF3OOjyv8IwvLu7w887xoW2bXdF22w279696yeaKqr9S4kjyqWE9LLm8/n3799RAx1241h62MM/fPCsXctPTEbXbBlxOgghOOeYUDEMA/MrmE57EsuyMLHkeV6apmEY5nleluW+bilvhZszxmazGVxh1XKqXi/l2pXocPMxDR1V/SSYh0ZttG0rxdl3H03TmqaJ43g+n3POwzCEe/TCYj+Laj17ngetaJpmu936vo8oUbV+ni1PXdcYSLbbbRAEqotgHXMNTzKZXFIZoPZj9y9VxP0KjPx3GlT1EO0ihCjLsmka0zS7l6fKssS0TpqmnudFUeQ4jmVZHf1RPugl7TV2/9I0rSzLPM/DMIRobEfYxyAJQvYOmN+O+58LqOeqqpIkmc1muq5zzoMgkAtNB6LqMadpCuuk6/psNkuSBHfoGGc1TQuCAAFzHMe+7z/b0eq6rqpK13XLsuRYqVROVVT7Vz+ml0uV3X4h+74c2R8zlB52JCs9iap/+OC37M+Wn5iOScI84qWoznBg8co0TTnWdi+nhGFoGAaMBZbC5LrZqOr0+++/Q675fO55nmEYuq7P5/Mejz4pMF8uhLi7u8OoXNe1nPJ8kqZp8AF3ONnlr+VyKdcQRK/lqQ42mw2mWrfbLTzR3WcdzqnJdXd3B28jSRKoAbtXEiUGLNKTnMsK2Pv37xljQogsy+SEdJZl++RCa5ZlKS/Gatg+hmqvHqjqoRSkrmt87v5JXddyyQVd7PPnz92POAt2pY6iSGZVKNHjube3t7tj5bNpI9LHxc+79VCqdF3X+MzulX9UVPuXKseSSxX4WoZhvH379tdff0VjdTfZUfSQVsDOFFoBOw9ErxmOIAjiOLZtuygKBGN5nh/+UPxctZxK14NLnXc5vDaQYs45z7Ls+vo6TVNd123bVp05GxvXdTFepmmKadEJ2i6O4yAIlH6iWqrp5ep3/7HNtTjSClg/dmsDxrDb7YAiFUVh23ZVVU3TOI5z4LOmqQ1VPczzXNd10zQh1IE9pWkaOFuXkewtEUIgbPY8j3OOylS9g9L1WZa5rou91phl676D67pw0B3HWa/Xruu2bZtl2b4dv4+1espeqdq/Due4cvXjcN2YXg/7+Ye7zxK0AnYMaBf4ZeI4jq7rCJ8Mw9A0Lcsy7MB+8vq2bTEYIDkboVfHZuIBiaIIG8Gx3bxpGrwRZIJHH06PFJ0wDMuyxH76oigQUO27DxzBNE2bpsGrOLIsmyD66pEihbEEzivsdZZlQ72vAoqqaZqmaaZpwqHscfMTlKsoiqZpoANCiDAMoyga5OYXQI8UxMVigXcLIQ1P07SOLKk8z5umQXBS1zXMnWmaHal9g7TX2HoIu5FlGYxnEARJkui6vi+wRHairuu6riPN6cuXL2/evDn3FMSiKBAI7U4yep6nOoSp1kOapnhtEp4LL9Z13X3PReO6rqvretu2eZ47jtPxviW8i6Wua6TLCiEWi8V6vZ4gBVGpf6lyLLlUadt2dzsAUjPm8/k+PRlKD4m/CLQCdh70mOEwDKNt292XH8qNYY9xHAdTwvjT9/0kSfqVU+l6mHjHcdq2xdM1TbMsS2ml7gTRdV0Ikee5pmnIAm3btizLfY4RJrDxWc5C9Zg5m4AwDG9vb/GSzLIsB3xVIGMsz/PdvNkkSfq9DbLHTN7YclmWBfcC6w9wr3vk+g9Yqn33P/0VMNX+xRiDzRRCSO3q2Cs1VHv1QEkPd0WALcXr+LofgXe7wbfelfTcKYoCu4mqqrq+vu4RMPfoX1EUXV9f42WtlmV1u9qO48ihTT6rw8odSw979C8ljti/+uH7/pcvX4IgEPfbJjuYXg9pBexMoQDsPFDtYKZpVlXlOA4iLrwa9ZCYSgZp/WKwHgEYNqriXyHEyZpgJTDBLO53dkHA7p9gNhSTgkIItOA0pT0c2UZ4awjc2aqqBs9lkp5lvxhMdSCZRq5dZcC/FID1Q7V/VVVlmibcPsaYpmmH6NXL20uVHnoIQTAWwEWGsE9e3LYtLAw+I1o7xKc8ccqyNE0TISgWl+SAonSffo7v7hPxyop9E50ySNN1HS+76mgsyfR62GP86sH0cvXANE3OOfZ9FUWBFtx38XH1kAKws4MCsPPgJR1sSqY0HKcM33kLIl7ot/suxMeci+OrKtex6BeAjSoXbijf7gi1H3tgVoX0UDJIe6lyLv3rBDlK/5rA8b1UPTyKXC9hyvY6QT0kxoAsO0EQBEEQBEEQxERQAEYQBEEQBEEQBDERFIARBEEQBEEQBEFMBAVgBEEQBEEQBEEQE0EBGEEQBEEQBEEQxERQAEYQBEEQBEEQBDERFIARBEEQBEEQBEFMBAVg50Ge5/hg2zYOcLyAw7ImAEeXyJMuXdfd/ZNQZfeEaBzhqmnaSAdG41DOOI7HuPkDJpALqmgYRlEU+MZxnAHvPwiPz5/RdR0H2pwUY7dXVVWapgkhIDtOyz3lQ4oOBKOGrKgsy3b/HA88Ao+Tfz47hCVJIk80FkJg4Nt3/4tsL7ZjN2TtDX7q/VBcXntpmvbgaKy2bbtPiz5Ke3HO5YnedV1zztu27fBzeshFjMHJjazEkyByYIw1TaNpGs7awznrxy3YiYPT6HcdDjhqqvV2qbZJtR4sy8rzXNf129vb6+vrLMs8zzNNc6j60XVdDts4/TMIgjzPVWOVE5SrbVuczinLJkfowxlbD1G2b9++zedz0zTDMFytVqM+cfe5hzN2e8F3wW1vb28Xi0Vd167rSv/yQE7NbmD42J2QgqM2djlN02zbVo5iKAAK8+T1RVHouu77Pj5vt9vr62vDMPaVc6j2OkHquq7r2jRN2UdQOUo3Gbt9L7W9UP7Xr19vNpuqqqIoWi6X3T85SnuVZek4TtM019fXt7e3ruumadrh5/SQixgFQZwJnz9/3u0ktm2f5gy6Em3bivt5L0yG7RuSX4Jt27PZzPM8xtjHjx8Hv/9jML0EGauqEkI0TdNdD6gKcXqzgA/AVKUkjmPVRu8gTdM0TeWfv/76qxCiKArV+5yaXFmW5Xku/7y9vf355597FHLAIj2JlHqz2QRBgIdKv/mkGLW9Ht9wmmVzVbvRjzzPoyhKkkQI8csvvwx+/yfBg5IkiaJoty/sY7VabTYbIcTd3R2+2W63HdcP0l6qQr1k/JJ3kJb/MXme71q/9Xr97t27HnKp0kMPj9JeY4OQkjEWhqEUZ3eEGqm9uqv6SR7ErrLkg8hFjAQXJ+/wEZL1er1YLPC5rus0TcMwPG6RXogQgnMOc49lPU3TBsyuvLq6iuNYLqrMZrObm5swDFVnpB6s1x9yPToYYwzrHm3bdozNuBJPUX3WS+jX/VHC5XK52WzatsVyxCDlCcMwjmOpAL7vo72mdH9HkitNU6mHi8VivV4PcudhkXl9QRDEcWzbtu/7ExT11PTQcZyyLDVNm8/nWAN8SQmVrleyG6rc3d0FQSBzSrfb7fv376MommBlNQzDm5ub2WyGb+q6juP46uqq+4dlWS4WiyRJ2P0A8eRlQ7WXKi8Zv1DCXcu/j6IokGBm2/bXr19fv37dQ69Ur++nhyfeXqrIvL44joMgKIoiSRLpg+1j+vYCqMPVajWfzzVNw7LYk1f2k4sYHArAzoOiKGzbRs4G9pBgjfvUmk/VcIwdgAFsnBM7E5aq9abqA51LAKZa1U3TGIbBOX8QQgxVZuiD4zgYuTH52u8+StdPIJeu6xjziqLQNK1pGtu25X6wAxlbN1BvjuPISAaaPOpD2UnqofyMRwgh6rpWnbgZ2270oygK1J7cCjKNXkkLXNe1bdsd18NBvLu7w2SZVMh95RyqvaYcvw4JwDDu43PbtpxzpLed2vh1rPYaG5R/NwceLb7v+qHaS7UekLovhNido2f7x0FVuYiRoD1g54Ft2/Dh2J/37lOfOQS4ubtGjeoNqNZDWZaYPs+yDKsl8/kceRdDFUkI8WBzFDwApZucoFxN08h1hqZpOOc9bj52LKRpmqZpeZ5j/wZCRF3Xx14hObX2QoL3ZrMxTVNqY1mWSGM+d+Aj7rbpZBN5GMWe9S8xVYH1MV3XoZBwMZ+8/lLbC+9vaJpG13UERaiZUxu/LrW9kCCKCUFd1+U8+D4FHqq9VPujZVmYsnRdF8HwZrNxHGffNIeqXMRI0FsQzwN0SJmHzRjDrpJjl+vUsSxLZq9Jo3ZqO+PPCM/zPn36tFwuy7Ksqsp13TiOB4xSbNuWY4YMusbYFviAseVyHAc7qTBfjnHu1LwotvN2LDhPZVkKIU6wv4zdXkVRxHEMb6Ysy+Vy+enTp1PzDnuA6sJnqX4TeF3yEfKhqNh915dlidFNTlvIXvMkl9peqK6mabByiOW1E3wB8qW2l0yZwYqxZVndch2rvdI0/fDhw2q1gsOTZVkQBB2LzKpyESNBKYjnASYnkIKI9BssGZ+aLVb1lSdIQUSRMLUPh5Kppzz1SGU5ixREVd+6rmvLsizLqqpKZtAFQZCm6SDlke2C9uqYQz3wPgcygVxQCawsoRf3WFkaOxZFnaMGZrPZdrvtkSfZg1PTQ8/zcP4Bbm6aZlmWctntcMa2Gz1A14BfCMeLja9XeChCenTt7odiXCjLEiVESltHyv1Q7TXl+HVICmKapp7n7aaHSa1QKucE49dR2mts2rbFwSG2bW+329lstptk+Jih2kt1z7NhGKhA0zRlCeM43hfTqspFjAQFYMQxmSYAg7nBGv2/Xz5zYpuYz+UlHOfSXqpMsxeR2Mel6uGpvYSDMYYbyrReVOPYbsAE9vDs7MYhAdhQnOD4dZT2OhdO0G4QY0AtRBAEQRAEQRAEMREUgBEEQRAEQRAEQUwEBWAEQRAEQRAEQRATQQEYQRAEQRAEQRDERFAARhAEQRAEQRAEMREUgBEEQRAEQRAEQUwEBWAEQRAEQRAEQRATcVrH3hED8viUPZxS8uTFmqbhFI66rnVdb9sWp8SqHuCoehSPLI9lWeOdXIHbWpZVliVjrMcB1qoFk/fHwaMne6JUvwOLTdOsqkrX9bqu27btOAC338G+L28vVcbWQ8/z0jTdPXBJnho07IMesHvSDrs/LgaF2feTx43V4yDRHuVUur5HeynJhXOK2Z8r8DQPKVKy82maBkHAGGuaxjCMqqoYY6ZpSg0ZCRwUW1WVaZp4tKZpHQfFapqW57njOLK/oMn2ySUP9oVRwjm2VVWNfRDz2Ax1sO8EyIOYGWOHH8Q8cXvBpWmaRtM06CHq9tTqU1Uu1f5FBzGfCHQQ8yWz65pUVcU532fg8jwXQriuC32QPxzb54BB5JzLKMU0TZjyQe5vWZYQAn4GHiGE6BFYqtYDrLwQQtZkVVVCCIxPjzmXg5gZY58+ffrv//7vu7u7pmlc1y3LsmmafRcbhsE5R/2z+ybouPlQ7aXK2HoILMuCpyu1YprAUj4O4/Qhv5IFM01TCDG2g66qh/3a63C54ItgpgAB2G5fPpxpDlQ93M4zxpqmKcvSdd2mae7u7v77v//706dPSoXsx4cPH/7xj39cXV3pup5lmWVZHZ1aSvTly5f/+q//+uOPP9h95ez7ia7rlmVlWabr+tXV1T/+8Y8PHz6MIcgu0xzEXJYlGlTe/NT0sCzLtm0dx4H3zxgzTbNt246h4Vjtxf7s3mRZxjl3HGfsRyvRwwdQ6l8waIh72Z8NCDElFIBdJpjjwawGbCLGhsO72ZTH0nPOEbGM+hQZFPX4bb+qODx4OJcADDOynHPXdeu6rqpqPp/neb5vUQsqhyG8aRo5jX1IW7+kvfoxnh7CocHN4bFNOeeK9e3dAuyrVax+o5kwOQ3fa+zS9u6VB7bXy+VCtKY6Qz+246tq54uiyPN8Pp9XVVXXteu6nPPuFdFBwCOEEFmWGYZhmuZms3Ecp2PSPUkSwzBs2+acW5ZlGEb3sq3jOJvNxjRNwzCyLBNCwFiNI9C/GTsAw/0xiEAx+jnK00wEAJj63YX3xxyrvdi0jk1vVEuo2r9g+tBGuq7DgCDvaYjiE4dCAdjFsmtokM7B9js6sPJYeZBdsceqtKo6yZBD0zRM3D6bn9YDpOVgDnt32DscVcMkn4InIg3v2eunD8BUHWuMrJzzxWKxXq/l9x0OBLvPSJFXPlv5L28vVcbWw93ES4RDSAAbu60xzVnX9W7I150FuttAsuEmWAlXur5HeynJBePpOA6cSCxfK5Vwt5xK16s6vqp2Xn5er9eLxQK1N8HkF3o0Hiq/f7acWZYtFotd6/Hk9bv3gWmC1R0702HsAGx3CG7bFnsEsHirVM4eK2ZKeojkt7u7uzAMdV0/pH/Jz1O2l5yqwLQFY8w0zY5UyWOhWg/9+pc0F+xM4tLLg5YdL5bv37/DxMRxjG4Gh+9JoigSQjiO4zgO53yz2bD7PBwl9t1/H03TfP/+fTabIV0BGzOurq6GqoSrqys4Z03TtG07m82+f/8uVyEORyii6/qrV6+2262mabquI6K4u7sbSq6hUK0HuQKwXq+XyyVyzbFV40mQ5JDnOXae2Lb96tWrjvIM1V6qjK2H6Im2bQdBAP/p1atXXF2vVOGcv3r1Cg0RBMFuZt0+Xr16hcuCIIAXhQKPXc6x20tJrjAMOedZllVVVVWV7/ur1Upm0p4USnY+z/O2beu6Xq1W0lGD6zYqcjFksVisVivsHc3zvKOcYsf7x29t2953f8dxNE0zDGO5XMqJIUwVKTFx2z2L7LBxHKNZv3//LtT7y9jlhJ2/urqq69r3ffQv7LA6qfZCfW42G845vB0hRBRFqs8dm7H7F0yZ4zjYiVcUxffv3wfSBUIF1ZYmzgKsRwshttttGIZoa9/396nBg9Xq5XL5+fPnHs/toYEfP35kjHmeN5vNRtoGatv2bDZDegMep0qPqvjll1+EEEmSRFEEf6IDpAT0rsMpeeC2xnHcIZf8381mgxiMMea6bvcjXt5ePRhVD23b3t3+9+rVq5ubmx5K1YObm5vdoNeyrA7pZNMEQbDZbB404nj0qFKl9lKVK01TaUKFEL/++qsQoiiKseXinLN7a4NlN2ThdpQTHw6084//tyxLVaH68WB7XnchpafI7hO5Qcf9H7Sm3N+ihKpQcomeMSa3aSk9a9fyPwbZ3fLP9Xr97t27HnKpoqqHQojVaoWedXd3h2+2223H9UdpLyHE58+fl8ulvAOSIQeruIHoIZdS/5L/G4ahbKZdi0dMA6UgXjKr1SoMwyAI5vP5t2/f2P6lbSzKyyQKzIn2eKLqHgk890HOBl6y1+Ppj3l8KzxOdYlfNSENe04eDMbI03jyenGkFETVerAsK8/zuq7X6/X19bXM2t+XwoT7f/v2bT6fB0EQhuFqteq4/1DtpcrYesgYMwwDaYe6rsPrZeqpd6qg3jjnlmU1TYN0xGffqLFcLqMoiuN4s9m8fv16gnKqRrz92utwuZDSg88y/2o3Y+dAVPsy77X3RsnOs/sdI9fX1+v1uq7rPM/3vRxoKMqydBzHMIzFYnF7eyt3ne0rpxBCvm2iLEtc1v1GB3a/Q/X29naxWBiG4TiO6kt0VF82I8Z/CQc6LN5uZ1kWrlS1hz1SfJX0EFsrMfoXRbHdbq+vrzuee6z2ApxzSIQmO8G9T6r+hmr/Qru8fv16s9nEcRxF0W5QSkwGBWCXCXZ9SPeL3c8pHjI2YIuIECLLsmcXKx6g6nDAZ3JdN8sy+eeA723HraRnhgf1cKxVuwliLVmB+LNjDDtWANYD0zSTJEEkCf+jI7DEvoVdufDyun0D51DtpcrYergLniKEmODNv3gE51yK1g2yhjA8SwdR9N36fzhj242XyIVXIMRxLJdwD2fsAEzVzqOi+P12uN2+PDbI5ERHRgE6+rV8PYBt21+/frVtG5MX+4qK/xL3+1h2n6WEqp2fIACTYDThnB9ykscL6TcRAF1CMI/utm9C9ljtNWUdvoQebrlS/5KvZZLPwgqn6gQ68UIoALtMejj0GDnky4v+vUKq7kCoF/YMGLubnEsApjown4tcEzBI/1JlSgfxJUypG6cs1wT961L1EBUl94zJvTSq5VS9/izkUqVfAKbE2bXXlJygHhJjQC/hIAiCIAiCIAiCmAgKwAiCIAiCIAiCICaCAjCCIAiCIAiCIIiJoACMIAiCIAiCIAhiIigAIwiCIAiCIAiCmAgKwAiCIAiCIAiCICaCAjCCIAiCIAiCIIiJoADsbEiSBB8OOS2ec45zBnFSJ2NsmtM2VZEnV8gzRizLGvC8EU3TcC4kPssjR4a6fwcX2V6XiqoeonUcx9E0DZf5vt/9iLZtcWAu/sU3Q5T9mYfig3z0sA9t21aqd9u28mipAR8xFPKIWMZYURQ4j/i4RdoH2gjnlXPOOwxID7txLnooBcHx2d1WtCxLWV1sEol2gQXAObZCCKlmj8ERwGyn8mWZO26OGsC/8nETcLgeqnIu7UUQo0IB2Nng+z58etiLpmnyPN93cVEUjuMwxmBiGGNVVbmuO1VhD4Vz7jgO/DZd1w3DKMtyQHMMB9EwDAx4dV07jjON43WR7XWpqOphVVW4hnOOy5Ik6RjIEao1TYNHmKY5mc/Rti182bqum6bRNA2aNgiY4MCdGWOGYeR5fpoBWFVVZVn6vh/HsW3bpznBIYQIwxCVCYXhnHfolardOBc99H2/qip8hum2bRuh5pNYlsU5x20ZY03ThGE4gR5yzqMoQgkR2QohOgIVKYWMpkzTlFN1j8nzHLfF1GFVVdNEX6p6qMq5tBdBjIpx7AIQB1FVlWmacoht27ZtW9d19w2fmGZL07RpmiAImqbJsizLsrHLqTo8tG17dXX15csXmGN8aVnWUDYRt5KONWMMjxt7GDuX9rpUxtZDx3F0XYfn5Pt+27ZZlpVlue+5eZ7btq3relEUmqZxzuM4DsNQqZBMfapY1/X1et22LVTRsqy2bTsmAlQpy9KyLHiHqLe7u7s3b96olnPs/ti2bRiG2+02SZIgCNq23W638/l87PBDVa5Xr16tVivTNLfbre/7MAtZluHDY1TtRp7nhmFg7kAI0bbt3d3dYrEYux5U9RA9C70sjmNd113XdRxnXzmLonBd17bttm3jOJ7NZlEULZfL79+/K5VTtR6+f/++XC6rqprNZkmSILhyXXdfrAiRXdeF9dB13XGcjsVzzArVdY2IRdO0q6ur9Xo9dn9R1UNVzqW9CGJU+GnOVhIPiOM4CILDr4fDxznPsuz6+jpNU13XbdtO03TfTzRNa9vWMAyZRySEUF0s6r24ZFkWHALp/g6IruvwenvHdardZIL2OgqccygGY6yua8Mw2rbt8AZwJbTiZDO+dlHSwyAIsJxSFIVpmrquHx7bTGl4d2sejXWI44IS7rbgPpqmgW/de458St04Vs0fguu6WZYJIdI0NU3TMIzuO6jajcetf5p66Pt+lmWYtFqv147jCCHyPO9OChBC1HVdVZXneZxzVKZSCVVrI8sy13U5557nVVVV13X3HVzXxRKx4zjr9RpTclmW7YvBUD+7BnaanqKqh/04/fY6FqqlgqsmE+nruoY7d/izDrHzxOBQCuJ5EATBdrtljCVJEscxLFcURfuux4jFGHNdF4Oxpmmn5s0zxn7++WfGmO/7ZVlWVaXrukyOHwrcUyYgyYeOyqW216WiqoeYCS6KAota+LIj+prP58gj8jxvPp/jyy9fvgwmwB5ubm7wAYsJjLG2bYfd89A0TdM02GGFhYt//etfA95/ELBGZxjG27dvf/vtN6S3ySS30yHLsuVyud1uPc8zTVNu8dqHqt3A0hNjDGsv+FIqyXio6iFWhxhjWZbJcnZHX0VRcM5N0/Q8b7vdLpfLCTIIXNddrVaz2SxN06qqhBDda0SySDKYbJqmYwVMLqrvZrC/f/9+MAH2l1NJD3twFu1FEKNCK2DngRACK/XsfuUB3++b5EDedhzH8/mcc470m+62HmQFTDV8ktt8Zdlwh6HWwR7cTT5INYVDtTwTtNdROJcVsB4piExFD2V2oud5aZqGYZjneUcKomx3OTHZr3/1S+3D/g1MQ6B3H8IhM6OoH9nrpUSq5Rx7R9aTaz5Sk8dDVS7P8zBf0zQNsr9wh2HthmEYpmk2TYNExI77D0UPPeScY8OeECKKoiAIOib1cf+qqpIkmc1muq5zzoMgUJ3DUo3J0zQNgoBzrus6stpwhw47oGlaEARRFGGM8H3/WSOAZSJd15GI2HH/oVDVQ1XOpb2ORQ9/g1bAzhJBnAPIW/jtt9/kN3EcF0Wx73qsrQsh7u7urq6u0Nbd3gBskAwVhBBIK1KihwZ+/PiRMRYEgWVZI/lhmJ5HTiAep8oJttdRgIFGUTGD2DRNRz1g81tv3ZgSVT10XReXIcxmnbMPlmV5nicvWC6Xv//+u6pS9ePm5mZ3s9nh2USPW3AfZVkWRQHX/5dffulRyEPK8xKkgzWfz79//w6JZKcbj36lRc+SPPhzF1W7wTmXFp4xFobhzc3NuFVwj5IeysWx+Xy+2Wxwh456eFxj/Wq+n2i7Vcp2xtDHyP8Kw/Du7g4/7xgX2rbdFW2z2bx7966faD04XA9VOZf2OhaqEsndlexenMNDSnmHHv4e8UJoBexsQKo0Jg6x7aTjxVC6ruMVQ7ZtZ1mGpOeOty2xgVbAelCWped5mPLBwoJpmkNlB+FWcr1C1/U0Tad57ezY7XUUzmUFrIdZU9JDdBbsW/j69SsSq3aXOh/fHG8LxAVpmkI3VMf+HnWIjWrQebwR9MBFMHHAzCheNoN/GWNN03ie12On5djDEErYNE1VVVdXV3gvzuFV0RtVudCbsGG1bVu8SXVYuwGppT5APZQK2Q8lPdwVxPO8oiggZsdLjIqiQHVpmibuHUrVlQ3V/oUiwXPVNC1JEt/3YeqfvB5FapqmKArP8xhjSZJgB9S+R8BKoE9ZlqW6u7gfqnqoyrm017kgaAXsPKEA7Dx4SQc7kKMEYCTXeXGpAdi5DGDT1+GzckEBZDCJauxR/y8r7EH3v2w9/ItzlJdIqdrDc+FcxmVqL3Au4xfxgLPXPIIgCIIgCIIgiHOBAjCCIAiCIAiCIIiJoACMIAiCIAiCIAhiIigAIwiCIAiCIAiCmAgKwAiCIAiCIAiCICaCAjCCIAiCIAiCIIiJoACMIAiCIAiCIAhiIigAIwiCIAiCIAiCmAgKwAiCIAiCIAiCICaCAjCCIAiCIAiCIIiJoACMIAiCIAiCIAhiIigAIwiCIAiCIAiCmAgKwAiCIAiCIAiCICaCAjCCIAiCIAiCIIiJoACMIAiCIAiCIAhiIigAOw8451VVGYbBGKvr2rbttm1t2953va7rjDFN01zXxc993++4v2mabdtallXXNX5eliXnfGAxHkFyAVW5joUQwrKspmkYY4ZhVFWlaVpVVR3Xc86FEGma+r4PMVEtJ4Vqe+FKTdNs287zvGkazjl07KyBXLqu+76fpqlsvmOX6wniOGaMlWVZliVjbPDKR1VYlmVZFmMsCIJh7/8kqGrOuaZpdV37vn8ZdkOVM7LzjDEhRNu2hmEkSaJpWlEU+65v25Yx1jRNmqb4JkmS7v4FiaSeQ+3HhnNeliVaoa5ry7LatjVNs+N62UCe58nm23c9DKzv+3Vda5omq3FgMR4hhDBNE1VqGEZRFN3tRRDjIohzIM9zIcRvv/0mv4njuCiKfdfXdY0Pd3d3V1dXaOsOAyovsCwLrsbHjx8nUCeS6yVyvRxVuYQQv/zyixBiu90WRVGW5bPXp2mKy6IoeiDs6dCvvdq2/f79+3w+R2V2OBxHbC8lZNOgscqyRBjWQdM0QoiqqvAnu/dKx+bdu3ebzUYWo6qqtm33FbJtW/m/h9ycc747TRCG4c3NTY/67CearEwp2r77n5HdUOJc7Dx4MKPUMcEk/ysMw7u7O/y8w860bbvb+pvN5t27dz3k6gEqMAgCy7KerXlMUjDG5vO57JUdevtYw0eXhzHGGOYy3r59K7/xfV8W/nRQ1UAYN/xWTg4qPWvXQhKTcaKzm8QDhBBxHM9mM8ZYXdfSjmNG7TGapjVNE8fxfD7nnIdhuN1uO9oaU1ZY2WCMyWlvVZ9S3uFASC6gKtdQqMqFehNCSCcbd0A9P6YsSwxvaZp6nhdFkeM4mE99UbkPK+fhqLYX51zWwG68MXYMNranomlaWZZ5nodhiCZjO434JG3bYrkGlYaaUVVd1XpDuwghyrJsmsY0ze5lVbETGR4eHxqGYZpm0zSYQWD79WEfqrGQ53lxHAshmqbZbre+7+MO5243VDmWnVftX2maBkHAOdd1fTabJUmCO+x7LjpLEASY4Ijj2Pf9ZxWyruuqqnRdtywLF49tZ6Bvux35QQ0/Botg0N4oioIg0DStQ28ZY1VVJUkym810XeecB0EgFwaVynk4eMp2u2WMGYYhl80nmDtTooe/IYckyNVR+Y9/y/5sIYnpmCzUI16INNnb7RYTY7sTwI/BzLS4N6DPugKw7/iMdIKff/55AnUiufrJNQiqQn3+/BlC4c+iKLqXs7CyVJalvOyQRbOjoNRekKIsy19//fXt27fw/idIrZygHmQD1XWNz2jEfRxlBez9+/eojSzLpGplWbavkKorYI7j4IOu6/gshPh//+//qVZmD9GWy6VcK3628sWZ2I0enIudv729xcQN6MgXBbJ34Ofd9lCqdF3X+MzulX9UUHUyq9CyrH1TbBLZQCjws8spu4odRdFyuRxVIgkay/d9RM6GYYRhOM2jD0dVCWkF7EyhFbDzII5jpU0IeZ7bts05z7Ls+vo6TVNd123b7p5h0nUdCdlIN++BqjqRXKCfXC+nd/fHFgtN054dmNl9bRRFYdt2VVVN00gH90RQba9dppw1HNtc53mu67ppmmisQ6plkBWwfuw+BdO9+9wOobgChvvsTiH3k0hVN1zXhZ+dpimW9brvcHZ240DOxc5nWea6Lufc87yqqjAX0HG967oIPBzHWa/Xruu2bZtl2b4dbo+1euI1CsuyhBBt23avyfi+n2VZ27au667Xa8dxhBB5nmML3z6EEFjc8zyPcw7lH1qCPxEEwTSb6F6Iqh4KWgE7T05uNzzxJJhXgz+E3Q4wdvv6GBzcNE2bpsFW5izLOkYvy7KQzNM0DVzqN2/efPnyZeyleZILqMo1FKopHJqmffny5c2bN7quy9CrI0UNL6iAE1/XNSoBO+ZfWPJny6l0vWp7aZq22WxmsxkexDmfzWZRFE2TGjQe0EP4UrZtB0GQJIlcBRqPHimIi8UC7z5B2qSmaQOuQOKdCoZh4M6c8/V6vVgsevQXpes9z4MPikkK+ENZlu1bVzkXu6HKsey8qlxpmiLG0HUdkRVjzHXdfe91QOO6rqvretu2eZ47jtPxfhFMbcjXYAghFovFer2ewM6gAlGl+BKV/OT1SZIwxhzHQYERl3bYz6IoELii3vCl53mq78NQbS/cH2GYaZqapmmalmXZqaUgEn8RaAXsnEiSRBrrpmmqqtrnGGECG5/lrMazM0yGYWBhtG1bx3HKslQ1cP3UieTqJ9fLUZWrbduyLB3HkekKz3q9mI0TQhwSsB2Xw9uL3U86xnH85s0b+B8TMLa53m0ahDcIRTp+cpQVMF3XMcUu12ClZj55veoK2K6VwLoK3OtD1nt36TGjHIbh7e2taZpCiLIsu1PazsVuqHJGdj6Kouvr66qqOOeWZXWHEI7jyHhDPmvX7Dwgz3PLshAeNE0DuTjnE+zBsywL/Qs9uvsto77vSxso5UJ42fGroiiwq62qquvr6yiKhip/N7ulxYK/bJQTgVbA/iJQAHY2SDN9oP8K84fJMyGEaZodO4wxf4z5LUwL1XXdw5HqoU4kF1CSayj6GXrYd7gFZVkahrFvBrGqKgxvqAFN0zq8jeOi2l7YvIFEKTTZCbZXD1APGLwR0qAR911/rAAMe4TwL6bSO65XDcDkUyCLfNbYAZh8HN5CgZCvqqoOhTwLu9GDs7DzUvfatoW24JUw+1aKZJCm6zpCmu7OBXaVHP+OHYCh6gzDQC4AYwyv+O/w6WUD1XWt67oMrp68uCxLvN7mQe1NoFcy+upY0Ds6FID9RaAA7DLp53AM9dyx709yDftcQhVqL8lRAjA8Ak/Bo1GMfdf3aC94MPJVaf/eM60eUKleP7Zcg0D2UF4/tuN7xD2W/bhUuabkBPWQGAPKfCUIgiAIgiAIgpgICsAIgiAIgiAIgiAmggIwgiAIgiAIgiCIiaAAjCAIgiAIgiAIYiIoACMIgiAIgiAIgpgICsAIgiAIgiAIgiAmggIwgiAIgiAIgiCIiaAA7DJpmubBKRCc847zZHbBYaNBEIxSsmmByPKkS9d1d/88X85LriRJ5JGXQggcrERMAI5GzbJs988Dz4c5EKiiYRjyKYccY/1Cdk/mNQxDCKFpWsdBvTiWt67rJEk8z4OJwwFE+0At1XVt2za+yfN8SBmG4FLt/ONzkHRd72ivY9lDadZc14VZG7ZzsSP1L1QdqlH+eaBeHchR5FLFMAx5NJZlWb7vd19/LD3knMsTvWHr2rbteK6maQ+O/GrbduzTvYnH0Ml3l8xqtQrDMAiC+Xz+7ds3dj/oPqZpGjm8yVP8HMdR9TlO7YBO6aVJINq+etjH2DHDpcpVFIX0nIqi2G6319fXjLGxbb1qPahyrINiVdtL1/XHJ/nKoXqoItV1bZpm0zSWZaE2xq5/y7LyPK/rer1eX19fp2nqeR7r1CsUCYWEl/zYC5E0TaNpmjzStK7rfpZt7IOYwfR2fmy7gfJ/+/ZtPp8HQRCG4Wq16rh+KHtYFEWPcnLOLctqmsY0TXSHQ3574AG4R+lf0P8HweTjSn6SU5ZLFdiT6+vr7XYL3TAMQ9f1fXpyLD0sy9JxHMMwFovF7e2t53lpmrJOO8AYe/369WazieM4iqLlcqn0RGIYBHGJpGmKD9vtNgxDtHXH/I3runK6izH2008/sV4zUmPL1bZt27b4fHipbNuezWZw0T5+/KgqFMn1Elar1WazEULc3d3hm+12O8FzR6Vfe72cHkX95ZdfhBBJkkRRlOf5kLUgRJ7nRVHIP9fr9bt376apCtM0d0sSx3FHOZt7xL1fCPbd3HEcufDFGFsul58/f+5RP6pCoUj4bVVVKHnH/S/VzsvW3Gw2co1ut+RPchR7eHNz8+rVK3kHy7J2NefZZ+1aksccsX+hAj3Pm81mB0oETlwuJaTuzedzxlgYhovF4tlfHUUP5WIs6F6sk/8bhqEcjqUxISaDVsAulvV67fu+bdtxHMOOdMx8R1EUBIGcak2S5P3791EUHTLjtcvY6iQUVx6urq7iOJZTkrPZ7ObmJgzDU5tpu1S5JGVZLhaLJEkYY1hYGPVxp6aHx0LX9TAMb25uZrMZvqnrOo7jq6urAZ9SFAVsi23bX79+ff369TR1gqcsl8vNZtO2LZbFnrzStm1MKgdB8Ntvv81mMyFEURSO4zx5fRRFnufJxaL1en2I47WvhErXY2BmB6+AHcXOj41cSQiCII5j27Z931+v1/uuH8oe9miv169ff/361bZtlPnwtQtx2EoRO0b/apomiqL3799vt1t8YxhGEAR3d3fP/vaU5VIFfZAxliTJYrF4EOQ85lh6CFDnq9VqPp9rmoZlsSevlCYCRqMoCgjY46HES6AA7GIRQshunOc5uuK+5sbAn+c5zI1pmi8xAePRz/G1bRtJRJiTY+rlHHtguFS5YOjv7u4wCMlkp7GfO/hOjAccKwBTfZbUCmjI7o6mQSiKQt6wbVvss8La1IBPeQxS6Tjni8Vi1y/fVz+yPI7jrNdruZbSYQ+bpkEMYNs2koh2hT2QCQKwo9j5aezhbm4kSt79q5fbQ1VHWQiBtEPsupHFOCQMOyRQOVb/kpYNabqGYQwbWB5LLlVQfnQrTGbd3d09m4o5vR7quo4nPpgq6rADbMdcsD+bEWIyKAC7TJDDDTMHZwUZ/4fvo4XZVV2pOM0ADOi6LnOQTo1LlWsXwzCkKo79rFPWw+kRQjRNM8bqKIZt3ByRw7A79feBTV+cc7z8oKqq+XyOvKZ9P/E8r67rsiyx9lXX9bNb6nfp56CMHYAdy86PDURADTRNg5BG07RD9o6+xB7268uapqHV8OhDYkV2WKByrP4FOOeQSOlXpy+XElIJu9/Z85gp9RCbvoQQWZYZhmGa5mazeZBHvQsSRNHx5dRSj71qxAs5UaUnXoiu69gZjPGV3c+C77u+KArpu8jBeOxlhAmwLEtm40hTeAFv+zkXucqyxBw2duCw+0H92OX6qyCrWo7oVVU9m0hzOLgt3sUHLwpD+1D334fneZ8+fVoul2VZVlXlum4cxx3RF+c8TdOyLH/88ccvX74gpa2jnHme4+Vs8A6huic4x3Gpdl6+HwXz+gibO+zbsewhAkWs4Wiahu42oJ4cq3/JqpOymKY54FsKjyWXKjKC0nUdjes4Tkc9HEsP0zT98OHDarVCAbIsC4KgY7leLs0hjwAGhMbl6aEVsIsFsxrb7XY2m+EzJkefvFh+L6dGLiYFEaJhpMRAztR9jrHn5y5YLs55WZYw8cgpwqznqM8de8w71gqYantBH+DCyoWRARsdK1G7q0Ny3WaoRzxJXdeWZVmWVVXV7v4uvPvrMW3bysvgLiP9Zl85saaBzCi8SRLz2RPsKVJNQTyKnR/bbmD5C002m8222+2zeX2D2EPVt4PKZQT8ieaT76Dr5pCVomP1L1QmXHMZGh340FOWSxWsasJWoDbKsuxe4TyKHhqGUZZlWZamacr0zjiO8SKQx0BvH5sOpYcSL4cCMOLfYKSXu07xljBV9TjNAGx3mIR/c2ppYyTXGM8d+/6nn4LYw6E/C6DqqHmZdzeggzgUEwRgqgxi50+QQezh9DZqGj1U5Vz619gca1w+QbtBjAG1EEEQBEEQBEEQxERQAEYQBEEQBEEQBDERFIARBEEQBEEQBEFMBAVgBEEQBEEQBEEQE0EBGEEQBEEQBEEQxERQAEYQBEEQBEEQBDERFIARBEEQBEEQBEFMhHHsAhAHgTNAm6bRNK1pGsMwcLjEvqM5jnXQ3gQHROJURHlwDQ7o3Hfkhed5cRwzxnRdr+sa5xtWVYUzcJSeq3S9ansdSy5Vdk8QYvfHxeBUzVGfe+7gbNbdA5fk6TqjPhcHdFZVZZom9FDTtI4DOs8FWW84KPbZakTN4xxVxhj6WtM0+87bGeog5n4HZzPGcHD2IeZU6SDmNE2DIGCMQRmqqmKMmaYpjxJWLeeByNpDTdZ1jRYZSv+PZQ9VUdXDYzF2/xq8nAeiOi7vHsTMGDvkIGZZKlkbHffvvsPhqNp5Ooj5RDgt80TsAw4BPsMJyPOccw678Ji2bauqQo+azWZt207Tu8Z2KNu2hch//PHHjz/++McffxRF0WHg4jjWdd2yrCzLdF0Pw/DTp08fPnwYtZCsV3udhVxyMEbB6rq2LOvcvfkJSNOU7Xi6bduiJseesCjL8sOHD1EUXV1d2badZZllWXDBzxoZC9V1jTo0TRNeyJPXm6aJOQ78ynGcqqo0Tdtnr/I8F0K4risjrn7RQr9AhTEGF4oxVlUVetm+n9i23bbtbDbD56qqOOf7ihoEQdM0ZVm6rts0TRRFHz58+PTpk1Ihe9C2rfTFISAmm/I8H+T+x7KHqqjq4bEYu38dC9VxuWmaqqrwv7qul2XpOE7btvvqwbIsIURVVbtRa4+JG1W7oWrnj+UfEg94JpQnTgel89Th4WGWXdd1TG9g9rHjJ7vrG5zzZ2d6niyk0vU9SJLEMAzbtjnnlmUZhgHv9kls23YcZ7PZYPzIskwIMc2KjVJ7sfORi927U5xzDC0dkkIf8L9TzvKOrYeqcqErwb1G1Y0degGsvAkhsiwzDMM0zc1m4zjOZQy3nHMZsRwOTOLuQu4hqHZn0E/nhRAHOm2Yy4d5x8w3lr/2Ob5FUeR5Pp/PEde5rss5h5L0KKcSPUaTwxnKHk5po/rp4ZRM2b8mQ7UjQxB0LqUHoer66byqHqra+R7+ITEGFICdB3KIxXDLGDNNE77vk9ejA8ulc3aA3RkkABvbrZQiZFm2WCzkBGp3AAAWi8V6vRZCwOj0e+6B9GsvNrlcqnDOkdizuyDQkb1AARhAQik+YxYWCWBj1wk8ISHEer1eLBby+3M3+7LmNU3jnCOdpuN60zSrqrq6uoqiqGkaaRg7+iMmv9n9EpN0U5TKqboCgPIIIdq2RY9+9om7hv0QueRnqARqT9XJVtUf6D9SECFRVVUDpqgNZQ/HXrFR1cNjMXb/Grach/MSPworq3d3dxC24ylIA5a9mKnXg6reqtr5Hv4hMQYUgJ0Tu72rrus0TcMwfPJKZAMzxuI4DoKgKIokSXZ75mPOYgUsz3OsEW23259++gl5/7ve7QMcx8Fuivl8vlqtJijhLoe317nIJYT49u3bDz/8UBQFdKzbQaQAbBfbtjF4F0Xxww8/fPv2bbJWY4ytVqv5fK5pGhJpJnjueCB97v3799vtFt8YhhEEwd3dXfcPLctar9e+77P7ue0nL4uiyPM8+b8P3JrDUdV5OHk3NzdIKUQh4zi+urra9xOIY9s2TD3bMf6PyfMcu3o2m81yuexRwpeA0AifDcPwPC+KokHuPJQ9nKw2DtTDYzF2/zouh4/LUgS4T/syDyVXV1dxHMsdlbPZ7ObmJgzDsSd8weF2vod/SIyCIM6Ez58/Y8gESLrY16ywgIyxMAy32y3ugEXqfWC5vKoq/MmmHZsPhN/D7hN1QIdccRzv/rnPNelm7PY6llw9ePfuHSaYAZKa9hUSqQ74PE3xQI/2UkJVLtu2d7fxvHr16ubmZuxCggdOg7QM587Hjx8ZY57nzWazQxamFosF3Kz5fI5vOvZIPMjeWS6Xnz9/nqa9fvnlFyFEkiRRFHX0LCBN+na7lU5kdxM/+N+yLHsU8tnafszPP/98e3sr75DnORIFh+JY9lAVJT08IqP2r6HooSdK47IUAUKFYXhIlGLb9mw2Q/orqnECuZTsfA//kBgDWgE7J5AMIJN3O3J2kVLy+vXrzWYTx3EURbtG50kGWQEbOwVOCIEsR0zw4HEd+TO4AJsBbm9vF4uFYRiYLlV6rupbwsDh7XUsuVRBkf6/9v7tuW1jXxO/G+cDQVCR5ETOKtu7Ur6bvavmZub/v943M1VTczNJpX52asVOLNEiifOp34tnq18uS4TZMAGS8vO5SMkKBKDRje7+djcAKSVOEssRe4Y5JWfAHuBC1XWNh7mxB92lX7owCGrb9uXl5e3trXra59zX+mMR0RcLnnuWBmHdEe5idI9ub2/F7uuA/atHqrC8Z9h5am2PRXpfLITrmdGCu7u7OI6jKFosFp8+fRK96RIPT4xcX18vl8umaTAtpnWew2Y2pJTqeuItI4cq/4eqD8e+H3XL4bGMfX8dytjtMsrD9fX1ZrPBahTbtrEa+cntH18iXEbd69C/4PMx3Xp+QP+QxsAA7DzkeY4HpnuWpW3DcyZya/0xplN6Gs6DBGBjU4+Nep73999/e56HTu2uDgr+l3xY31zX9Ww261/A/STd66CbX8dKly4kR0qJBH51ewZgjwVBgLH/ad78u102cEd/9RmG04ck4Eqqf371rZK4Durd0Hhw4qvH0i3z3wL3tToQ/tnzHnC8zx3dLFUae17xggulKnbHcdI0HTBZdGpl/lj14TDDyuGUpry/vsUE7bJ6kYbrurhferbHJVIVLC7ggPp2QPulVc8P6B/SGE6uh01PQtOC1kWNy+75xovt26yn4TyLAGzblOkasP2zzC8cAkfBofu/EsMATEEBQGEQD4tMxr4m31IOv3NHyS9dxyqHA7bXqjcGOLv2i77dlO3ylE6wv0FjOK2vNBARERERET1jDMCIiIiIiIgmwgCMiIiIiIhoIgzAiIiIiIiIJsIAjIiIiIiIaCIMwIiIiIiIiCbCAIyIiIiIiGgiDMCeLfV5TXz1HJ9H3KWqKsMw8FlPIcQJfhkD8AlFsfWJd3XOu5imiSuA/+I3I5/m///QQgh831BK6bpuz8aO46gNyrLE91L7dz59utQh1KH7D4pCJR4ughDC9/19DqQuxWw2+5YT3pP6QpEq+VVV9dwFA9LVdR0KrSq6J3iXodLwfd80TeTsNNd/bAPSdaz8Ul967a+xwTCMuq7VJ2Xxrdie7V3XVdWRmLwmFHvXG7qO2H6pgtRfvX+xPcohKo0BH8I+QVrpMk1TXS7TNNWn2yY5U712+SzSpQq8qrL6b4EB/SgaAwOw50l9E1083GP9n353XdcwDNUutm0bx/EJfsVSpUJFHf0fpy+KAh0pVIV1XU/T5zAMY71e48rjBKSU/T2quq6rqprNZkmSeJ7X3yofK11CCNM0UbRs20ZFXxTFro3zPEdCVMRSFAWq/if5vo+Lhms1m816MveApJRFUeBitm3bNI3ruj2XdEC6EDBjY8dxTjD6EkLUdW3bNrqzOMM0TffsWZ4y3XQdMb9UmcfptW3bc3/h3DzPS5JkNptVVaWq/SdVVSWlVP0zy7LW6/U0HS+tekPXEduvNE3RR0eVZVlWz1iM67rI3K7rDMOoqsq27f4sOwu66eq6Dtugtm+axvf9Ccqhbrt8LunCodEkNU2DG6GnHOr2o2gk9rFPgEaBewnd2SRJLMsKgsD3/V3diLIsgyDwPK/ruiRJ5vP5er2+urr6/PnztCf+FWizgyCwLCtNU7R2PYPZvu83TYP+tGEYpmleXFwsl0vdcEW3+/X58+erq6u6rufzeZqmqOyCINgVA3ddF8fxZrNJ0zSKoq7rNpvNYrHYdVzf98uybNsWWSaljKJovV5rnaTQHwJv2/by8tI0TTQqVVX1V/RBEAgh8jxv23Y+n7dtm2VZWZa7jlsURRAEXdd1XafmAB3H0e2j6OaXaZr39/c3NzfonuKXVVXt6qMPSJfneZZlYRvDMJIkieNY6yQngBoDtcdsNuu6Ls9z5PKoxx07vNFN17Hyq65rx3EQOdR1jRsBd8ST25umuV6v5/N5FEVpmhqGgap7V7o8z8vzHImKomiz2cRxfHd398MPP4yYqq2ICAkpyxJV96Hy/VDtl+75oGpS1RTmSfI833X90dcPgsA0TZTGIAhs2z5gLPqkse9f3XS5rltVFUY3UN9eXFx8/Pjx1NrlY6VLlxpJwYE8z8PATU/9JnT6UTQS4wRnOegxKaVhGKjobdtumsY0zZ7aZzab5XmOxnu5XPq+jzF+dBx7jtI0TV3XYRgahhEEQZ7nh0/MNwiCoCgKKaXv+8vlEl2TPM931R24RNvV0LDhKN3bJM/zIAgMwwjDsK7rpmn238OwW3LK9QPbZ/j4Cm/Lsgwd2SzLrq+v8zzH4getDkcURUmSDD5DLZgkMU1ThWFP+vZ0TVPx6tYbgAuOUVLHcSzLGruDOI1vSdc0+ZUkSRRFw/52/xrAMAzbth3HybJMSonKaqRjbRv7Gk7ffulWTb7vt21b1zUK4YCa7TQNS5dlWRjd2Ge17ZPGbpfPJV2w/12p24+ikXAJ4vOEUQ0hRJ7naoKiv5Uty9IwDMdxwjDcbDZXV1enFn0JIdQpqWCybdueWkMNcm+v5Hnz5s3Y5xkEwd3d3Xw+z7KsrmspZc/6NCEEFr/Ztv3y5cs///wTEz490z6r1Qrro7IsW61W+OXNzc1BE/EEdemKosDqBdM0e5qZMAzR3Q/DEHlnGEZPrzeOY9u2DcOIogjZOp/PJ+ij/PHHH+JhWZrjOG3bqrUZT9JN12KxwHrRMAwXiwV++fHjx0Om4RBQSjFBoUaFn0H0pZuuY+UXZqWEEGmaJkmCiKJnZltVFH/++efLly9VNdJzCM/zpJR1XWdZNp/P7+7udKOvAVTVtFqtsizDKilVcR3EUdovzLYJIWazWRRFiGx7ZkpVkdsuiv1Nw1kYkC7LsizLUgvvhRCvXr0a+zx12+VzSZeqmhaLRRiGWAOpKq7HdPtRNBLOgJ2HASPZhmHggSIp5Xq9jqKo508QpdR1nabpfD63LAud4CzLxkjOYF3XYfHMer2WUuLJh68O/GBY1LIsLEQU+ksydJfAZVmG9tiyLKx2wB52HXc7X9QtKaXcdXuq/eCCCCFQPHRv52FLPrBuvm1bx3H6e3vYGCudDMNYLBZJkvQ8gq+uAwq5eAjAdNPVHz49ph7LVmUJe+iZBxuWLnUPInPHnrfUrTewhEYIEYZhlmVxHBdF8QyWIOqm64j5pfr0TdOom2vX9VGZK/51/Ls/XY7jzGazzWbTti2OGIah1nn2zw8/eZ6qNlNVljhcvh+q/dI9HxwFMbOqskTv9Xdd1/f99XqNoii2Cud4Jrh/tdKF8qNqadVynWC7fJR06bZf2/X8dg3fk64B/Sg6PEnnAM/5IMvQKvff0urZlcVisVqtsBMM+Tzpi/91so8Fqx5JHMf39/c427Ise67bdtJWq9Xr168HHHdYrn0RnPTEKio3F4vF58+fkd1YIPGksizTNFUb3N7eTjD9Ba9fv1YlCkUFZ/skPPQvpfz8+bMakOvpvbmuuz0O9/LlSzFohHhAZv36669Sys1mU5alOu0DpisMQ7XB1dXVhw8fBpykLt16QwgRBAEe5kYY0J+uM6KVrmPlF9YF/fnnn+o3SZL01G+oAbqu2y6HPVn8uEYadp4Drv/Nzc3t7a06bTyBM+zojx2r/ULVhGoKZrNZz8tdVIlCIXQcZ4LpxwkMSxde/Is1t2/fvh1w3GGlZf92+YzS9eHDh6urK3XaYRj2lEPdfhSNhDNg50FqjmRjlTMeGw3DEC9s6PkTLHHGC7hM05RS4vnvyd6ttyecUtu2ZVli1DZNU6z43/UnGEjGkJXrusOestAdHMKlRvcXz+/OZrOyLHfFEnj4HsvNLy4uENVsD6l+AYNwagMMzvVsv8uA2x8XUF3P7XH6J6kMyvPc8zxk366+Ly6RulBN02Cxvu5JDuC6bpZlODFkB/67a3utdOF9HupaZVkWhuFXL92306038H/x/Mzff/+Nd1dMcJ5jD77qputY+SWEwCNMuJHVvbDrJQEqTx3Hub+/x4NtPeUWe0N1hAuC90aMPQOJ81RzCPjnAWd+DtV+DSiHeJQOBeOL6usxFCGsh//xxx/zPEcDMfb1H7ubp5su1K6qAOBh2gFvWx27XT5WunThPFFNia0+z65DD+hH0RgYgJ0H3Y7UANih6sT/V4DOG1IIoV/Rby+5QW3Y3xvAljjKsV6ncSJwoVRnd9jSSl26+XUuvqXewNXYLpnjmb7MT5MuXRPk11HurwkcpP1iPf8t+9dK13PNL/ajaH9n38MgIiIiIiI6FwzAiIiIiIiIJsIAjIiIiIiIaCIMwIiIiIiIiCbCAIyIiIiIiGgiDMCIiIiIiIgmwgCMiIiIiIhoIgzAiIiIiIiIJsIAjIiIiIiIaCIMwIiIiIiIiCbCAIyIiIiIiGgiDMCIiIiIiIgmwgCMiIiIiIhoIgzAiIiIiIiIJsIAjIiIiIiIaCIMwJ4nwzBmsxl+DsPQsiwhhGnuzG7P87qu8zyvaRohhG3bdV0bhjH2eeJwWZZt/7OqqrGP+wzYti2EcF3XdV0hRBRFxz6jAyjL0jTNsiyRuqZpHMeRUo59XCml67pt24qHwm+aZl3XPX+SpilOLM/zruuEEPjzJ6FIo3iLhwKv/jkenKFhGKZpNk0zm81wm+/aHpfdNE3P84qiaNvWMIye8zxWunCeYRhu/xM3Qs/2lmXNZrMsy6SUhmH0lytVFyGNSZIc7vR3GpZfWuk6C6rBCoJA/Gtz9iTHcbquc10XuWZZVlVVE7RfOISUsus627bTNEX1tWv7pmkMw2jbtigKz/PQIiMTn4QirTZAge/Z/oBQ4FX5P+xNfaz8klI6jqM6Oaq52bW9bn6hHzWbzZqmMU1TFY8RkvJNVIOlul6qOaNJSToHXdfJh9tDdZJ6slX1RRaLxWq1wk7qut61/7IskyRR//zzzz+llEVRjJwsKaX88OHD1dUVztayrDAMezpS50LVvPLhsrdt23MRuq5DFsv9KkHDMLabgTiO3717N+Dij5X+oVzX3e5pvXz5UgjR0wHdZcCl+PXXX6WUm82mLMuqqvo3Vht8/vx5sVjgoOg17kqXGgcRQlxdXX348GHASepeB/jixu+pB5qmkVJ2Xbedrp6q5ojpurm5ub29VaedpmlZlv3pklKu12spZVVVCFd26bpu+yqtVqvXr18POMlhdPNr/3TJh4pI7VM8VFZa+g/x7VS67u/vLy4ucFDHcfrPynEc13UxFPX27Vvt6z40XV/0yHs66OpWWiwWnz9/Rp2vEvtYWZZpmqoNbm9vb25uBqRrgNevX6ueg5SyrmvVQj2m237Bt+eXLjQlaFZgNpv19Dd08+vxnTt2ioZRRTSO4/v7e1XYvlrU6bCew2jZ90BKaRgGWkrbtjG+gmGMXTBqiLBqvV5HUdTzJ6qiaZoGN+dms4miaOxBqe10bZ9ef3g5vf5L/RjGoXFz4ZJ2XdeTKLnVE9r/mtu27ThO27aIBwac51f7NBNT549CLoSYz+cow1r76ZmMehKyBqVxew89MZWUcrPZxHFsGMZisUiSpG3bXVm8XbDx83/Vv5r3V8/5PCkMQ1y9tm03m81sNkOO7yon6mYU/1oOx07XgO3V/bV9Z/XUb1VVFUURx3GWZZhJqKqqf6ynaZq6ri3Lcl1X1VFa56lLN78GpAuXS9XzyPGx7y9dpmm2bZskyWKxMAwjjuPNZtNzkrgv1FmpFOnml26POcsytJKWZc3n8zRNsYev3i9ia2JEleTHtgs2fh6WX7rXQd3LVVW1bes4Tv+0m277daj8GtAuR1G02WzEVhPTc9xh+VXXdZqm8/ncsiwcUU00nQgUpyiKMHCTJMlsNptgBpK+NEpYR4emOwMmtvrW23vYZbVaYYhrs9momG2CdGG8XAixWCzCMLRt27IsNfR+vsaeAfN9Hz9YloWfpZT/3//3/+le//GuwDBxHNu2jUYLU2Hz+XzAfnSvw/v376WUahK4LMueYU5Qk2A4Yv/9uFgsLMuybTsMQxRv+VD4tQy4FFdXV9v3cv+0NhJVVdU///nPly9foqrp6XsdK12YB5BS3t/fo9fbNI0ayu1JmpSyaRr83HMp8jxXG+NnIcSbN28GXH9dWvmlmy55JjNgcqvCxBG/OlSEOBk/o+p49erVBOm6vb3drqP6p+vVDfXy5ct//vOf6nbbtfP7+3uMAqRpiuItHgr/qFDUpZR5nquaUN0Ujw2YATtIfg2AzJrNZoicbduO43jXxrr5Jf/17luv12p1z6lRdz1O9auLPmgMnAE7D1JzBmw2m+HRlCAIlsul7/tSyqIosKR+T0mSTPNk0fMbehl7Bgy7enJ8Tvc8B/zVxKIo0n0CZ3C1hkcRTNPsn2vKsszzPMuysiy7vr7O89wwDDw3NeoZ6uZXEAToNmVZhmHs/fcwrGxMWQ73P1ZRFJZlOY5TlqXneV+t2XBnbd+w09wpuvmlmy5xoBmwsbsNeOTGMIw8z6+vr7MssyzL87z+mQTLsvDgzeCniHXTled5EASGYYRhiFGA/fdw+jX29hk+viMeb6m7guPb80vXgKZE0cpZhM1hGBqGgZt62EFHEgQBAkXf95fLZRAEXdfled7/pCUd3BRPc9L00jQVQvi+j7YW7QRusye3N00zz3PTNE3TdBwHDfmAZ28GWK/XrutKKfG4edu2eDR2gkPvT3epw9jwzLdt21VVoQ1bLpeXl5e653mC1xmlFA/hoL3seUi6Zz9a25um+fHjx5ubG8uyVOjVs5QLa70wxoH5nyzLiqLoWcqCgA1l2zCM9XrdM/Lac55a24dhiLa/bVvf99E3yvN8161tmuZqtZrP52q903w+X6/XY6drgDiOVbRcliU66LvyHbPEyC/P86IoStNUzR4/hmqzaRrXdTG0f3l5uVwuJ1iCqJVfuuk6lLHrQ5x/lmVY1osubE/05bouFsu1bYv79+bm5uPHj2MvacuyDGOalmWhRyuECIJgV5XVdd32ckosOVksFj3tclmWbduibEsp4zher9daJykGLe27vLzEO3iwzNU0zQO+/ONY+YV8QbPiOA46POj57Nq/Vn6VZYmAHOUBvwzDcEATNipUMkEQWJbVdV1RFL7vM/qaHmfAzsOAGTDEYGJr5Aa32ZPbF0XhOI7qeqZpOs3diCre9/2u67Ai3DRN13X3n0k4TWPPgPm+X1UVCgDGEdH86z4jdGozYL7v13Wtng3YLsZadKu1ruuqqkI5RMb19zYwooGf1TX0PG9XQ3vE/Irj+Pb2Fi+TrKrqq6MqqGqSJLm5ufnqxT9WuizLwpS+mqtUOfjk9tuxNOocRM679l8Uheu6uGHbtu26DuHQ2M8+Cc380k2XOJMZMEzo4WdVNr46k2DbNm5e5JcqmfsbkK71en19fY2XBruuu2dXezabffz4MYoi2fvA5LHKoe79NWwG7Nvza5jtZgUTyF/tb+yZX1CWJZ4arev6+vp6QMA8Nt/3VZJVmZ+s10cKA7DzoBuACSEcx8EDwU3TYIhaPUreQ7Xo09yNGADDiBH6ARN0cSYwzUs4ti8a/nvuAZiCIVIxNAYb0KE0DAO3FbKpqirbtnuyrK5r9JLxMuXtJm2X6fNLHQ5vNUBoVNd1z0sa8DAAFoBhavqrbyaYPl2WZaljIe++ekRUaKgz0ZVEDvb8yfbO8d+xa6cB+aWbrrMIwMTDcCEmIaWUqjl7EuZnUGPgFsYLxMdOlyoeXdehkOCVFT1r6hzHwaI7KWVZlrjL+o8yfTnUvb8GLKE/SH4NoBoU1cT008qvqqrwWqwvSsWpdbPVYIFlWXgTyVcrQxrDyZUMetKAAGz7b8W/VpGn41vSdcomCMBwodSrnP7rmc6R3z53Lsau1s4lv55rOdRN1wAHCVR0nUu6TvD+OuBxtbYfu10+i3J4rPya0inn17c45f7hs3daT4AQERERERE9YwzAiIiIiIiIJsIAjIiIiIiIaCIMwIiIiIiIiCbCAIyIiIiIiGgiDMCIiIiIiIgmwgCMiIiIiIhoIgzA6JjwtXh8ARCfYuy6rueDgLZtq09VuK771U9F49MlaodBEGz/czzbXw61bVtKaZpmz4dEH38nxLIsfEjkpODS4TKqf371O0Wz2Ux9vNIwjBNMF7Imz/Ptf/Z8z6dt2y/+r2EYPdfBcZyu6/CtZ/HwkfQJPrqiLnue57jsh/2olHi4Sk3TqFKxz+dNv5Hu/dU0jbrFqqra59PeuFC2batS8dUP5tIuuveXrmPV87ps2378ReOej0TVdW2appQSN6/6+Pu4Z6lfb+jWh+cCabcsKwzDNE3RRUEdvouqN8qyxG9835/gVKMowqnus7Fpml+0Pl3Xjf11b3rs5HpCdNZ07+Gqqnzfb9v2+vr69vY2CIIsy+q63lWPoO67vr7ebDZlWVZVhSZNVXZfwNfoVc8sz3N01PaspwZzXbcoCsuybm9vr6+v8zwPw9BxnF3XB+fz6dOnxWLhOE4cx3d3d6Oe4fZx94cOwRcdKVzkJ7f3PK9tW/R3Pc+bz+e3t7dN04x9/XXLIQKkLwLLtm139SHQMN/d3cVx7LruYrH49OmTlHJXunChULyvr6+XyyV69rp9et3rpu4Ly7Latq3r2rbtwwbA2GFd1+qaI9O1dqKbLt37C0m+vb2dz+ee57mu2zRN27ae5+06RNM0TdM4jqPOrSxL3fN8rn2ase8vXceq53Wh/bq6ulqv11VVrVarFy9eGIax63riQqF4397eXl5eYqRj7DEO3XpDtz48F2jX2rYtisL3fSTHNM2edrzrOnyFWaVdNZfj8X0/SRKcmMqmnnYW5//ixYvValXX9Xq9vrq6Gvsk6QmSzkHXdfJh3Et3JFvtATs5NV+0Jf2TWhjmEUIsFgshRBzHl5eXX70C6PqHYSiEePv27Z7X7RthqFJJkqTnIqj/u1qtVBpVf+VJaqQN/5QPhUTLgHThAoZhiL7sV7e/vLyM41g8ZJnYysTx6F4HKeWvv/4qpUzTdL1eF0XRv3GWZfhhs9kgdeJrRfeL/1tV1YCTHHApXr9+vVwu1R7KsuxJ3XYtsc/OEcyof/7www/v3r2bJl1a99dms8EP9/f3UsrVanV3d9ezfVEUZVmqfy6Xy9evXw84SV0YlsZB67qWUrZtO+B69sAOsXMppTqolgHH1bq/dMshfHs9r5so3XZZVelRFK1WK+xkz6YBJpvW06o3BtSHZ8F4IISQUrYPdl2HPM+3r9Lt7e2rV68mOE9Uwj///LP6TRAEPf0HlTVxHKu6UWUiTcaQ409n07eTUqqKwLbtpmlM09xzCQeyWA5ta7UM2z/O7e7ubrFYmKaJabEnt8TYkhAiTdPLy8uvDgReXFwkSaLWDMzn83fv3sVxPM3IHK7G1dXVarXqug7D9k9uqdZTRVGUJInnebPZbLlc9uwcBQCFQTx0HcbO37Zt1+v1mzdvNpsNfmPbdhRF9/f3/X/ouu5yuUS9rzJxPLrXwbKsOI7fvXs3n8/xm6ZpkiS5uLjY9SdIjud5SZIgpFSLaR8risJ13a7rVqsVxhq/5U7R2v7Tp08//vhjWZY4vf6YebuW2P8MPc9DAS7L8scff8Tgt+55am0P+99f6jbBbbXnxOP2Rfv7778xWTHgDLW2x40sHm6TrusOu5QLO1T3IJqVsbsBuveXbjk8Vj0/oF2+vLxM07QsS1T1Yqvyf8z3/aqqTNNcLBZYEzFNh0233hCa9eG5KIrC8zzDMDabzc8//4z88jxv14qbOI6zLFPl8PLysr8RPxSsmnn37p2KrLquS5JEBcNfUFmDzCrLEh2qCU6VtjEAOw/nEoDp9hUsy8LjGcvlcvv+31Uscf5qPUAcx/f39z0NGHieh6OoAcuxiz1WAhiG8UUVvOv643x831c9yK/2ig4SgOleB9UlwiLy7ZXuT0LWXFxcrNdrtZBjwHF16Xa8VKlACWma5qsdju2r/dV0becLijqunu5SLt3t8YylekoKvyzLclfqdDu+230R9bDKgMfbBlyHwfcXBhEuLi56Oojbl0g9vDfg8Rvd+vBcArBh9cz+99fggYBvrOcHpEu3Xd6+2qrC7y+3gKKOqzd2YKlbbwjN+vBcqBTleX55ebndOj+5vZTSsizUKmVZYk1gT8B2WFJKdISapvF9v+e+3u5Hqb+d4Jlk+gIDsPNwLgGY7v7DMMTENx72dRxntVr5vt//bAZ6rrqzKFjOPk2Bz7IsDEPDMIIgaJqmruvFYoF1TU9ub5qm6hWpKrtnrbk40gwYGIaBi6n1V+g3TDD9Jb5hfqlt2306N3h8BT0SFEXckrv6yljAs1gs6rrGUxyGYaDw656h1vaAEAKPmliW1VNOdDu+aONRGHCIYW9W0E2X7v0lHqpNlMB9zmf7cm13Q7VwBmzb/vfXsAAMpqznddtlPCOE6l1Vhlhv+eT2nuf5vr9arRzHwVOjUkoU/rGStGX/ekO3PjwjaZrato15MNd1bdvWqrSnublwwfc/EIqcqhKRcV3Xnfsze2fn7G8POmtZlv3yyy93d3eu6zqOk+d5FEU90ZdqWS3LQmXh+37PgiLsFj+r6mmCJ+PDMPz999+vrq6qqqrrOgiCJEl6eofqrUSoRvGA0Ak+wa9OSV1Mx3H6rz/G2FR+nWa6VMOjehh1XfcscLUsC+2x8fBSR4y779re87woivI8x+W6u7v75ZdfdKOvAdDQYm5KvefqgFG6uhlRgHGsCXpduvcX8ksIgUc4hBBFUfTkr9oYcynoVR/wrX3fG937S9ex6nldaL9QvWMgwOh9W2BZlkmSBEGAy3V1dfX7779PEH3p1hu69eG56LoO6yo/fvz4008/VVWVZVnPdfB9H09eIXBFsZ9gVFRdajW6VJZlT32opoixjgAZx+hrepwBOw/nMgOmew/btl1VVVVVjuOoFQ5JkuxqYzDcjqlzVBxVVfUPMqF5Q78QLZ846BuQn9Q0jeu6ruvWda1WIERRtKvPjTFpbDmfzzebzVfXLRxkBkz3OuBi4sqrLmnPTpA1yCYpJTIOsyVax9Wl++wBkoC+kQoh+gMJFNfNZjOfz/Ez7sonN86yDM9FYMu6rlE89pmN2da/1Pax7bkO8VCN9Iyg6848YBJv+wZUtZPWeeqmS/f+wig+Vnwhl13X7blfcIm2N1CTFVrnqVsfnssMmO4p6d5fA2bADlLP66ZrQLv8uJLvKVdhGG4/d+Q4DprLsRcR6NYbQrM+PBemaaLNUnPganHKk9tjzhArsTEriMnDacYCENVvD4HtKlfoOTzOsglOkrYxADsP5xKAjb3kZljDPP1SvW/Jrz2dXbqeUzkc4CAd37Gr629Z+vXtx9XanuVwmKMsQWQ9P9gRl5rTsepDXRPUGzQG5hAREREREdFEGIARERERERFNhAEYERERERHRRBiAERERERERTYQBGBERERER0UQYgBEREREREU2EARgREREREdFExv2cHx2K+gaF+mgj/tvzQUD1fVJ8NqQsS9/3d32iBN+8NwyjaRrLsrquw9cDdT8kOuwDnUIIfKBzpO8j46zwOWAhhGEYY3+IWV0HfLB4n8ui9YHO7Y8gq0/EDPhQyeAPle6frqOYoBxqfXh0++Oz6hNMAz6+NCC/dD+oahgGvlMshMCXiy3LGvs7Uc+1HE5g2AfB27a1bRvfv3YcR/eD4Lps266qqq5rx3FwaNM0kyTZVQ63P4CL3/R/AFd9sNiyrKZp8B32uq51P1isW5B022Xcj4+r+n3OauL2S7fe0HKoD52PTbccHovu/cUPMZ8Ifoj5PKCTYRiG6m3jbtlVd6tva/7000//+3//75ubG7WTJ7cvikJKGQQB/kptOeBDolrbI8yTUqoj1nUtpUT/7zHdDyO6riulRD8DHWsp5YDAUhcOYRiG6s07joOubc9fbXf9HcfBh+2f3HI791Ektq/heIalC075A7i65RC2L3hd17g9n9wSOYVcQ1dj+xruT7e6Vt1B/NA0TX+Kqqrqus73fbTiQgjHcbqua9tW67i6dNP1XMvhsA+q7l8OhRBt21ZVFQRB27b39/f/83/+z99//13rJIf55Zdf/vM///Pi4sKyrDzPXdftqYRVij5+/Pjf//t//+uvv8RWo/Yky7Jc183z3LKsi4uL//zP//zll1/GSMjj89y/XcaNj/ZI/GuF/6RjtV+69cYwVVWhoKoDnVpgM6AcHovW/YUOA8YpRG/PkEZ1iiWJHlOdtv3/JAzDpmmqqpJSlmXZNM1sNtv/z7dHp/Y3rEOzf6PyLV+mV53sAWc4jGEYOOhXt8SsI0bXMIiLvtf+HXREa7ojvsPsn65tp9zxhf3LYdu2pmli1BCxCqYd9m/GtjttWmeotT10XWcYhmEYSN2et7Zt2yppAw6qZVi6nl851A3AdMthWZZFUSwWi7qum6YJgsAwjDAMsyzTOk9dOISUMs9z27Ydx1mtVr7v9wy6p2lq27bneYZhuK5r23bPSXqe5/v+arVyHMe27TzPpZQHnLHZRbddRtbgr9q2VdMpe7YRE7dfw+qNfWBXardSypMNALTK4bHo3l/oWqC6sCwLFQjWPU185t85BmDnxDAMDFrYto05q10VospW3/eXy2UQBF/8/vGe27bFSJu6FQfMSutWo6ozhLE9LM/46va6ARiW5aijiKEdvv2pM1Tjo19dZ7I9roalX2J3GpH1vu+jc4zpmgHnqftXA9L1xbGm6fiOXQ7Fv45QYJmK6L2/pJRFUahppWFXQHfGDMPttm1vd3F67mssYrm/v4/j2LKsr5bDQ9ENos6lHE4wA6ZbDtXPy+Xy8vISV2/sGU4MKkkpcVD1+6+eZ57nl5eXKISitz5UP19eXi6XS9zFuh3KYeVBt11Wt5XYbzrlKO2XVr2ha3tXCPOwcPTUuqO65fBYht1fqroQQwfc6Rud6KgDfaGu67u7u9lsVtd1Xdd5nhuGEcex3EHVbmoAG/0/Y4f1ei2l9H3f933DMFarlXhYTaFl1/nsYlnWDz/8sNlsTNO0LAstzf39/aGu28XFBTpnbdt2XTefzz9//ty27a7rcCht237+/Hk+n2P5Fh7ouri46DnVH374ARc8iiJU9GiQnhTHsWEYeZ6jPMxms7u7O7WyZX8TpOsoJiiHnz9/Rqc/SRI0Y1j99STcX0EQOI7jOE6apldXV2oFyP5080tK+fnzZ8Mw6rpOkmR7JeSTcEoXFxeYMEc5RD9sVM+1HE5AqxwWRdF1XdM0d3d3qqOGrtuo1CTq5eXl3d1d0zRd1/W0RwhjxEMUir/1PG/X/n3fN03Ttu2rq6vlcontMTelRffi67bLuL+KosCTeJ7n/fDDDz37P1b7JTXrDV1qoWaSJCiunz9/lvr1wNh0y+Gx6N5f6Cr4vo8nJ8uy/Pz586EylzQcu+TQXsqylFL+85//VL/JsgyTzk9qH8iHgV7YVQy+mK2+urp6//79BOmSUv76669SyjRN1+s16rsemDrHz/sXcs/z5vM5lqO8ffv2G24XDThQGIbz+fyrTZeaooyiaLVaIYFJkuy6Dl/kPgoGComWsdO17XEOnhStcqgu/mazieMYCexZ4hsEgcpiIcTPP/8shBjjsYrHXr9+jQkBwCK0nqTd3d2hBN7f36s0fsuF3ceAdJ1FOdRNFKpo/C2mtVGH76JbDh//X6xRn8AXj+f1n+R2gyX/tTnb5YvacsDohtDvDum2y+okV6sVYjCxVfnvcpT2S7fe0FIUxXZrtVwuX79+PU26tAwoh8eidX+p/xvHsaree8otjYRLEM8DJouxHEWNdvQvHcHqi7Zt8aIwIQSW6zy5MZ4lUI8QYEx0wHnqLmXBs09frLHBOqgnt5eaSxAdx/liXgjP+07wEo7HD1g/PpkvXF1drdfrJElWq9WLFy/E7uuJJQf4Wa1T2l5RsCfdZ8aGpQvkhEu/xi6HcHd3F8dxFEWLxeLTp0/i4aZ78nzUpcYthnddqDUt+5+n1va4DlLKqqosy8Kyop5MxyOI2KAsy81mc319LfSvpy7dwfVzKYe6+zcGvYRDqxyKhydGrq+vl8tl0zRFUYw9FlBVle/7tm1fXl7e3t6qp852naeUUrVZKLqitxBiAzz0dXt7e3l5adu27/v7vJRlm+7jjrrtMs7z06dPi8UiiqI4ju/u7nr2f8T2S+jUGwM0TYNlh+ii4E45tWeQdMvhsejeX0jCixcvVqtVkiTr9frq6mrSMyYhBJ8BOyNJkkRRtOdLAtB3bJqmLMsff/wRaxj2fJ4eTwZLKfM8/+rg3DfCeaoD4Z89fQ7dAAzNlWrGgiDI83zPjtq3wCFwOPXPnndeYZWXavbEw1jsPs8yoUigeOiep24HUTdd26bs+OrSLYdN0xiGgTtRlUZjv9dD42H6KIqw/GNUw+7lNE0dx0GnHMVy7Je7PNdyOHYAplsOcaGMh+eOsBp22GSRLqyURsWLE+iph9XrATzP+/vvvz3Pw0vzd50q/pd8eI5l+1haBnSHtNpl9VoL8ZBfeJnnrnb5WO3XlH0AHMIwjH3eyD8x3XJ4RFr3Fz47tF0TYlpvmpd4kcIA7HnSDVTEQ12//cyYPL3nMgek6+yccgfxW5xyAKbrXMrhsBmV6T3Xcjh2AHYu9bx8eLxHPHRq9/8Gw575paah0InE4XS7N2N3h1hvKAfJrymdcvs1wf1FYzi5lpiIiIiIiOi5YgBGREREREQ0EQZgREREREREE2EARkRERERENBEGYERERERERBNhAEZERERERDQRBmBEREREREQTYQBG/6XrOnxKUn1Qcs/vSHwL9aURdayqqnqOq75ZqT4a6Pv+2Cc5zGw2ww/4oO1XqU/fCiHKssT3Usc6uaHUl0bUN2Fc1z3B70rpmqwcqixWxWNUKmvwje+2bfszCx/uLIqi6zokP03T8U9zCurbqbgUVVUd9XT64MqjjBmG0XOqhmHUda0+X+u6bv8nYl3XRYlFgZ/szlW3kmpiDt64mKapCrn6zWEP8dgzbr+ETjnUVVWV2q2YpKdBdILOvudEB+H7PhowNA+O40xTJ0opi6JAU4Sj93fo8zxHD0O1ZEVReJ43wanqStMUnWy0W5Zl9be1dV1XVTWbzZIk8TyvvyN1LIZh+L6PK29Zlm3b/R2OczF2OfR9H11PFIbZbDZZYGOaJsIq27bR8S2KYtfGjuMg7VJKJH82m51yrLKn2WyGiyAeYgDP81TccjqklHEcI4RAhWwYRv8IjuM4nuclSYKcUsl8UlVVUkoV/1iWtV6vpxno6boOt0zTNBgIOGDsgSED1EhCiLqup4ktn2v7NaAcanFd1zAMNR7Utm0cx6f8FWaiMdjHPgE6CWhF0J+WUnZdd39/f3l5OXbf2jTN+/v7m5sbdAvwy6qqdtX1QRAIIfI8b9t2Pp+3bZtlWVmWYze3utfBcRw1heU4jmmapmnmeb7rPLuui+N4s9mkaRpFUdd1m81msVhMcP21tu+67uLi4uPHj2g+8UvXdU+tj6573cYuh0VRBEGAaaXtgtHfXX7yPLW2b9v28vLSNE0csaqq/o5vURRt22LgIE1T0zSDIHBd99xjbIS7CIOTJLEsKwgC3/dP7f764Ycf7u7uHMfZbDaz2Qxd8zzPd/XRTdNcr9fz+TyKojRNDcOYz+fr9XrXcT3Py/McBTWKos1mE8fx3d3dDz/8oJs0LZZlLZfLruvQyUaJ6hkI0IVRIcQ/hmGYpnlxcbFcLgfUb1rbn0v7pUu3HOoqyzIIAs/zuq5LkgSF9urq6vPnz1r7Ofd6ib5zBkcdniVkK3pd+wxwogHYrs4mLhhYk2CapmrGnpRlmed5lmVlWXZ9fZ3nuWEYnucdsC0/iCiKkiQZ9rdTXvnBg9+YJOm6ToVhX4V0bZfMEzRlOfyWQqJlu0ThHu/v8CVJEkVRWZae59V13bbt2Aulxi4Ps9ksz/Ou64IgWC6Xvu9j7gId4vHopisIgjzPpZRZljmOY9v2/nvQ2tK2bcdxsiyTUuZ5PvZ1UMdVPz9ucXbZp954XKqHlajBde8za7++pRzuT0rZNE1d12EYGoaBgx78KIdyyu2XlNIwDPWAQNM0pmnuGZ2ecrqevdMad6FjUYPc2yvl3r17N/Zx//jjDyFEmqZ4eqFt2/4OfRiGOM8wDFFZG4Zxaq2XEAKjekKI2WwWRRF6PHEc79oei1hs23758uWff/6JiRHd6ZEJvHr1SjwsS6vr2rKs/g7HuRi7HMZxjE5MFEWYX5rP5xNEX2/evMEPmNoSQpim2TNdiVV5nue1batGu0/5MZU9pWmKgprnuUrONFGHljzPr66uNptNGIaO4xiG0b9OUlUUf/7558uXL1U10vMnnudJKeu6zrJsPp/f3d1NcB1UU6LW4nZdd8AlbZjaFUK0batuQ1X4x/Nc2y/dcjhAWZaGYTiOE4bhZrO5uro65eiLaAycAXuedGfAAMOibdtiIaIYf4ofrSbGb/AbNGA93XopJVbOGIaxWCySJPnqqwW+ne51QFd7s9mIhxEp/L5nCaL6Wd2SUsqxb0/dJ83UY9nqxJBT+8yDTTnSNmApkRizHKrzUYUBAZhu/g5bUiWlrKqqbVsMZvdsr1ZPZVkWhuF6vfZ9f4IliBOE8YZh4AFLKeV6vY6iaP9B4sF0768wDHGGbdti9Rf2sOs81bC3eGp+6THsx3Gc2Wy22WzatpVSJkkShqHWeerC+eA5Isuy6rpWVeJX7V9vYDrFsiwsRBT698uwJcGn337p0i2HupDeuq7TNJ3P55ZlocXMskxrP1MuQTzlmSLOgJ0pPgNGQghhGIZlWVhGL4SI4/j9+/evX7+eoGH47bff3r59myQJWs3+Lktd147jxHF8f3+/WCxWq5UQwrKs/RfCTcN13c1m8/Llyw8fPuCS4jUAuyYfVHW5WCyQNMMw1HspxzOgAXv79u1vv/0WRRGi9BOcphODXoA2ajnEAHmapigMKBgD3gMxIL9ev369Xq/V7GvTNOju7DrPPM9t28awNP6qbdtzn+fEY4pJkiwWC3U1mqbpD0e/nW5+YVIUJ3ZxcYFf9pwnskZKuVqtVDns6Xuhc1bX9f39vXiYK4uiSOskh3n//n0cx+v1Wp0Jwr+D7ByhAh5jFkKs1+vXr1+/f/9+2ECMlmfZfumWQ13YleM42DlqxWnWYxOdDs6APU8DZsDQNmP8u6qqyR5QcV03yzL08NA+4b+7tk/TFEvG8Uww3tE0dgdxwMgQHrFAi4XHafDfJzdGktu2rev64uKiruuu67anzkYy4PavqioMQ/QY0K/d82USU460Ddj/qOXwiwLQNE0YhgNi1wH5hQe6EPm7rtvfi+q6zjRNPBf0448/YuHiBOVwbIZhhGGIV3GEYViWJaYdxh5B180vXH+8NKXrOrwtsydQV6PdjuPc3987joP5pV3lFiUQL2jtug6PLU1wHcTDE4+qfdm/UO1Zb6Bgq3KOYq97kqdWbxyLbjnUhV1ht6hw8IIi3QB4yhmbU54p4gzYmWIA9jwNW4I4PSxmU19TsW17QC08Ad1rqJuuY+WX7u1/LhX92Pk1AHao4h9cxgHX/4CntGv/p19vnIsTvL8OUg6n9J3XG0fxLeVwT9ihisNxGQdc/wOeUr9TDlTOpV2mL5x9TUFERERERHQuGIARERERERFNhAEYERERERHRRBiAERERERERTYQBGBERERER0UQYgBEREREREU2EARgREREREdFEGIARERERERFNhAEYERERERHRRBiAERERERERTYQBGBERERER0UQYgBEREREREU2EARgREREREdFEGIARERERERFNhAEYERERERHRRBiAnYemaYQQWZZt/7Oqql3bt21rGEbbtmmahmFoGIYQwjRPLrullK7rtm0rhLBtu65r0zTruj7gIdS1wuVKkuSAOz8U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fhVFIaUMguDxgQ6y/13wSijTNNW7udR7275D6rILIeq6xrP4xz2liR2rHD5Xw+6v/csh8+uwnms9rwtvB1EL87YL5DPw/Or5551fZ4QB2HnAUCjGYzASg5Ewvox+GrrV09j5ZZomdogRLIxd4aBa+9E9H7yJSzU/OIcsy8Iw1NrPM4BRw81mM5/P8TMGR499XpM6Vjl8rgbcX1rl8FD5RfBc63ldmE55XBRHPeg0nmU9/4zz67wwACMiIiIiIprIecfxREREREREZ4QBGBERERER0UQYgBEREREREU2EARgREREREdFEGIARERERERFNhAEYERERERHRRBiAERERERERTYQBGBERERER0UQYgBEREREREU2EARgREREREdFEGIARERERERFNhAEYERERERHRRBiAERERERERTYQBGBERERER0UQYgBEREREREU2EARgREREREdFEGIARERERERFNhAEYERERERHRRBiAERERERERTYQBGBERERER0UQYgBEREREREU2EARgREREREdFEGIARERERERFNhAEYERERERHRRBiAERERERERTYQBGBERERER0UQYgBEREREREU2EARgREREREdFEGIARERERERFNhAEYERERERHRRBiAERERERERTYQBGBERERER0UQYgBEREREREU2EARgREREREdFEGIARERERERFNhAEYERERERHRRBiAERERERERTYQBGBERERER0UQYgBEREREREU2EARgREREREdFEGIARERERERFNhAEYERERERHRRBiAERERERERTYQBGBERERER0UQYgBEREREREU2EARgREREREdFEGIARERERERFNhAEYERERERHRRBiAERERERERTYQBGBERERER0UQYgBEREREREU2EARgREREREdFEGIARERERERFNhAEYERERERHRRBiAERERERERTYQBGBERERER0UQYgBEREREREU2EARgREREREdFEGIARERERERFNhAEYERERERHRRBiAERERERERTYQBGBERERER0UQYgBEREREREU2EARgREREREdFEGIARERERERFNhAEYERERERHRRBiAERERERERTYQBGBERERER0UQYgBEREREREU2EARgREREREdFEGIARERERERFNhAEYERERERHRRBiAERERERERTYQBGBERERER0UQYgBEREREREU2EARgREREREdFEGIARERERERFNhAEYERERERHRRBiAERERERERTYQBGBERERER0UQYgBEREREREU2EARgREREREdFEGIARERERERFNhAEYERERERHRRBiAERERERERTYQBGBERERER0UQYgBEREREREU2EARgREREREdFEGIARERERERFNhAEYERERERHRRBiAERERERERTYQBGBERERER0UQYgBEREREREU2EARgREREREdFEGIARERERERFNhAEYERERERHRRBiAERERERERTYQBGBERERER0UQYgBEREREREU2EARgREREREdFEGIARERERERFNhAEYERERERHRRBiAERERERERTYQBGBERERER0UQYgBEREREREU2EARgREREREdFEGIARERERERFNhAEYERERERHRRBiAERERERERTYQBGBERERER0UQYgBEREREREU2EARgREREREdFEGIARERERERFNhAEYERERERHRRBiAERERERERTYQBGBERERER0UQYgBEREREREU2EARgREREREdFEGIARERERERFNhAEYERERERHRRBiAERERERERTYQBGBERERER0UQYgBEREREREU2EARgREREREdFEGIARERERERFNhAEYERERERHRRBiAERERERERTYQBGBERERER0UQYgBEREREREU2EARgREREREdFEGIARERERERFNhAEYERERERHRRBiAERERERERTYQBGBERERER0UQYgBEREREREU2EARgREREREdFE/n/46OawlOpU1gAAAABJRU5ErkJggg=='''

from typing import Optional, List, Dict, Any

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import tkinter.font as tkfont

# ======================= MARCA D'ÁGUA — FEATURE =======================
# Permite configurar logo, opacidade, tamanho, posição, texto e link.
# Não interfere com a intro: cria a marca d'água 200ms depois da janela principal abrir.

import json as _json
import tkinter as _tk
from tkinter import filedialog as _filedialog, messagebox as _msg

def _resolve_logo_path():
    """Resolve caminho da logo priorizando assets/logo_watermark_nobg.png (dev e exe)."""
    import os, sys
    from pathlib import Path
    base_dir = Path(__file__).resolve().parent

    # 0) Prioridade máxima
    p0 = (base_dir / "assets" / "logo_watermark_nobg.png").resolve()
    if p0.exists():
        return str(p0)

    # 1) LOGO_PATH
    try:
        p = Path(LOGO_PATH)
        if not p.is_absolute():
            p = base_dir / p
        p = p.resolve()
        if p.exists():
            return str(p)
    except Exception:
        pass

    # 2) Candidatos comuns
    for cand in ["logo_watermark.png","logo.png","logo.jpg","logo.jpeg","logo.webp"]:
        q = (base_dir / "assets" / cand).resolve()
        if q.exists():
            return str(q)

    # 3) PyInstaller (_MEIPASS)
    try:
        meipass = getattr(sys, "_MEIPASS", None)
        if meipass:
            meipass = Path(meipass)
            p0 = (meipass / "assets" / "logo_watermark_nobg.png").resolve()
            if p0.exists():
                return str(p0)
            for cand in ["assets/logo_watermark.png","assets/logo.png","assets/logo.jpg","assets/logo.jpeg","assets/logo.webp"]:
                q = (meipass / cand).resolve()
                if q.exists():
                    return str(q)
    except Exception:
        pass

    return None




def _wm_base_dir():
    return _app_base_dir()

def _wm_assets_dir():
    import os
    d = os.path.join(_wm_base_dir(), "assets")
    os.makedirs(d, exist_ok=True)
    return d

def _wm_config_path():
    import os
    return os.path.join(_wm_assets_dir(), "watermark.json")

def wm_load_config():
    cfg = {
        "enabled": True,
        "logo_path": os.path.join(_wm_assets_dir(), "logo_watermark_nobg.png"),
        "text": "Mecânica do Jairo",
        "height": 42,
        "opacity": 0.30,
        "position": "bottom-right",
        "click_url": ""
    }
    try:
        with open(_wm_config_path(), "r", encoding="utf-8") as f:
            loaded = _json.load(f)
            cfg.update(loaded or {})
    except Exception:
        pass
    return cfg

def wm_save_config(cfg: dict):
    try:
        with open(_wm_config_path(), "w", encoding="utf-8") as f:
            _json.dump(cfg, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print("[Watermark] não foi possível salvar config:", e)

_wm_holder = {"frame": None}



# --- Watermark helpers: notebook-aware container & bg -----------------
def _wm_find_notebook(root):
    try:
        import tkinter.ttk as _ttk
        # BFS over widget tree to find a ttk.Notebook
        queue = [root]
        while queue:
            w = queue.pop(0)
            try:
                if isinstance(w, _ttk.Notebook):
                    return w
            except Exception:
                pass
            try:
                queue.extend(w.winfo_children())
            except Exception:
                pass
    except Exception:
        pass
    return None

def _wm_active_container_and_bg(root):
    import tkinter as _tk
    import tkinter.ttk as _ttk
    style = _ttk.Style()
    nb = _wm_find_notebook(root)
    container = root
    bg = None
    if nb is not None:
        try:
            sel = nb.select()
            if sel:
                container = root.nametowidget(sel)
        except Exception:
            container = root
    # try to read bg from container or style
    try:
        if "background" in container.keys():
            bg = container.cget("background")
    except Exception:
        bg = None
    if not bg:
        try:
            bg = style.lookup(container.winfo_class(), "background")
        except Exception:
            bg = None
    if not bg:
        try:
            bg = root.cget("bg")
        except Exception:
            bg = "#f6f7fb"
    return container, bg
# ---------------------------------------------------------------------

def wm_apply(root, cfg=None):
    # Cria/atualiza a marca d'água, acoplada à aba ativa.
    try:
        if cfg is None:
            cfg = wm_load_config()
        try:
            if _wm_holder["frame"] is not None and _wm_holder["frame"].winfo_exists():
                _wm_holder["frame"].destroy()
        except Exception:
            pass
        _wm_holder["frame"] = None
        if not cfg.get("enabled", True):
            return

        container, bg = _wm_active_container_and_bg(root)

        holder = _tk.Frame(container, bg=bg, highlightthickness=0, bd=0)
        _wm_holder["frame"] = holder

        pos = (cfg.get("position") or "bottom-right").lower()
        anchor = {"bottom-right":"se","bottom-left":"sw","top-right":"ne","top-left":"nw"}.get(pos, "se")
        relx = 1.0 if "right" in pos else 0.0
        rely = 1.0 if "bottom" in pos else 0.0
        try:
            holder.place(in_=container, relx=relx, rely=rely, anchor=anchor)
        except Exception:
            holder.place(relx=relx, rely=rely, anchor=anchor)

        photo = None
        try:
            from PIL import Image, ImageTk  # type: ignore
            import os as _os
            lp = cfg.get("logo_path") or ""
            if _os.path.isabs(lp):
                logo_abs = lp
            else:
                logo_abs = _os.path.join(_wm_base_dir(), lp)
            if _os.path.exists(logo_abs):
                img = Image.open(logo_abs).convert("RGBA")
                h = int(cfg.get("height", 42) or 42)
                scale = h / max(1, img.height)
                img = img.resize((max(1, int(img.width*scale)), h), Image.LANCZOS)
                r,g,b,a = img.split()
                a = a.point(lambda p: int(p * float(cfg.get("opacity", 0.3))))
                img = Image.merge("RGBA", (r,g,b,a))
                photo = ImageTk.PhotoImage(img)
        except Exception as e:
            print("[Watermark] aviso (logo):", e)

        if photo:
            lbl_logo = _tk.Label(holder, image=photo, bd=0, bg=bg, cursor=("hand2" if cfg.get("click_url") else "arrow"))
            lbl_logo.image = photo
            lbl_logo.grid(row=0, column=0, sticky=anchor, padx=(0,6), pady=(4,0))
            lbl_text = _tk.Label(holder, text=cfg.get("text",""), bd=0, fg="#7a7a7a", bg=bg, font=("Segoe UI", 9))
            lbl_text.grid(row=1, column=0, sticky=("e" if "right" in pos else "w"), padx=(0,10), pady=(2,6))
        else:
            lbl_text = _tk.Label(holder, text=cfg.get("text",""), bd=0, fg="#7a7a7a", bg=bg, font=("Segoe UI", 9))
            lbl_text.grid(row=0, column=1, sticky=("e" if "right" in pos else "w"), padx=(0,10), pady=(4,6))

        url = (cfg.get("click_url") or "").strip()
        if url:
            import webbrowser as _wb
            def _open(_e=None):
                try: _wb.open(url)
                except Exception as e: print("[Watermark] não abriu URL:", e)
            for w in holder.winfo_children():
                w.bind("<Button-1>", _open)
                w.configure(cursor="hand2")

        holder.lift()
        root.bind("<Configure>", lambda e: holder.lift())
    except Exception as e:
        print("[Watermark] falhou:", e)

def wm_apply_later(root, delay_ms=200):
    try:
        root.after(delay_ms, lambda: wm_apply(root))
    except Exception as e:
        print("[Watermark] after() falhou:", e)

class WatermarkSettings(_tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Marca d'água")
        self.resizable(False, False)
        try:
            self.transient(master)
        except Exception:
            pass
        self.cfg = wm_load_config()
        pad = {"padx":10, "pady":6}
        self.var_enabled = _tk.BooleanVar(value=self.cfg.get("enabled", True))
        _tk.Checkbutton(self, text="Ativar marca d'água", variable=self.var_enabled).grid(row=0, column=0, sticky="w", **pad, columnspan=3)
        _tk.Label(self, text="Logo:").grid(row=1, column=0, sticky="w", **pad)
        self.var_logo = _tk.StringVar(value=self.cfg.get("logo_path",""))
        ent_logo = _tk.Entry(self, textvariable=self.var_logo, width=44)
        ent_logo.grid(row=1, column=1, sticky="we", **pad)
        def _sel_logo():
            fp = _filedialog.askopenfilename(title="Escolher logo",
                                             filetypes=[("Imagens","*.png;*.jpg;*.jpeg;*.webp;*.bmp")])
            if fp:
                import os
                try:
                    base = _wm_base_dir()
                    rel = os.path.relpath(fp, base)
                    self.var_logo.set(rel)
                except Exception:
                    self.var_logo.set(fp)
        _tk.Button(self, text="Escolher…", command=_sel_logo).grid(row=1, column=2, **pad)
        _tk.Label(self, text="Texto:").grid(row=2, column=0, sticky="w", **pad)
        self.var_text = _tk.StringVar(value=self.cfg.get("text",""))
        _tk.Entry(self, textvariable=self.var_text, width=44).grid(row=2, column=1, columnspan=2, sticky="we", **pad)
        _tk.Label(self, text="URL (opcional):").grid(row=3, column=0, sticky="w", **pad)
        self.var_url = _tk.StringVar(value=self.cfg.get("click_url",""))
        _tk.Entry(self, textvariable=self.var_url, width=44).grid(row=3, column=1, columnspan=2, sticky="we", **pad)
        _tk.Label(self, text="Altura da logo:").grid(row=4, column=0, sticky="w", **pad)
        self.var_h = _tk.IntVar(value=int(self.cfg.get("height",42)))
        _tk.Scale(self, from_=24, to=120, orient="horizontal", variable=self.var_h).grid(row=4, column=1, columnspan=2, sticky="we", **pad)
        _tk.Label(self, text="Opacidade:").grid(row=5, column=0, sticky="w", **pad)
        self.var_op = _tk.DoubleVar(value=float(self.cfg.get("opacity",0.30)))
        _tk.Scale(self, from_=0.05, to=1.0, resolution=0.05, orient="horizontal", variable=self.var_op).grid(row=5, column=1, columnspan=2, sticky="we", **pad)
        _tk.Label(self, text="Posição:").grid(row=6, column=0, sticky="w", **pad)
        self.var_pos = _tk.StringVar(value=self.cfg.get("position","bottom-right"))
        _tk.OptionMenu(self, self.var_pos, "bottom-right", "bottom-left", "top-right", "top-left").grid(row=6, column=1, sticky="w", **pad)
        btns = _tk.Frame(self); btns.grid(row=7, column=0, columnspan=3, sticky="e", **pad)
        def _save_apply():
            self.cfg.update({
                "enabled": bool(self.var_enabled.get()),
                "logo_path": self.var_logo.get().strip(),
                "text": self.var_text.get(),
                "height": int(self.var_h.get() or 42),
                "opacity": float(self.var_op.get() or 0.30),
                "position": self.var_pos.get(),
                "click_url": self.var_url.get().strip(),
            })
            wm_save_config(self.cfg)
            try:
                wm_apply(self.master, self.cfg)
            except Exception as e:
                _msg.showerror("Marca d'água", f"Falhou ao aplicar: {e}")
                return
            self.destroy()
        _tk.Button(btns, text="Salvar e aplicar", command=_save_apply).pack(side="right", padx=6)
        _tk.Button(btns, text="Cancelar", command=self.destroy).pack(side="right", padx=6)

def wm_init_feature(app_root):
    # Menu 'Exibir' para modo escuro
    try:
        import tkinter as _tk
        m = app_root.nametowidget(app_root['menu']) if app_root['menu'] else None
        if m is None:
            m = _tk.Menu(app_root); app_root.config(menu=m)
        view_menu = _tk.Menu(m, tearoff=0)
        m.add_cascade(label='Exibir', menu=view_menu)
        view_menu.add_command(label='Alternar modo escuro', command=lambda: toggle_dark_mode(app_root))
    except Exception as _e:
        print('[theme] menu exibir indisponível:', _e)
    wm_apply_later(app_root, 200)
    wm_apply_later_overlay(app_root, 200)
    # Atualiza ao trocar de aba
    try:
        _nb = _wm_find_notebook(app_root)
        if _nb is not None:
            _nb.bind('<<NotebookTabChanged>>', lambda e: wm_apply(app_root))
    except Exception:
        pass
    try:
        current_menu = app_root.nametowidget(app_root["menu"]) if app_root["menu"] else None
    except Exception:
        current_menu = None
    if current_menu is None:
        m = _tk.Menu(app_root)
        app_root.config(menu=m)
    else:
        m = current_menu
    try:
        cfg_menu = _tk.Menu(m, tearoff=0)
        m.add_cascade(label="Configurações", menu=cfg_menu)
    except Exception:
        cfg_menu = None
    def _open_settings(_e=None):
        try:
            WatermarkSettings(app_root)
        except Exception as e:
            print("[Watermark] não abriu settings:", e)
    if cfg_menu:
        cfg_menu.add_command(label="Marca d'água…", command=_open_settings)
    app_root.bind_all("<Control-Shift-w>", _open_settings)


# ================= Overlay Watermark (Windows only, transparentcolor) =================
# Evita "retângulo de fundo" sobre as abas: o conteúdo continua visível por baixo.
# Requer Tk 8.6+ no Windows. Em outros SOs, cai no modo normal (wm_apply).
_wm_overlay = {"top": None, "width": 0, "height": 0}

def wm_apply_overlay(root, cfg=None):
    import sys
    try:
        if sys.platform != "win32":
            # fallback para modo normal se não for Windows
            return wm_apply(root, cfg)
        import tkinter as _tk
        from tkinter import ttk as _ttk
        import os, webbrowser as _wb
        from PIL import Image, ImageTk  # type: ignore
    except Exception as e:
        print("[Watermark][overlay] dependências ausentes:", e); 
        return wm_apply(root, cfg)

    if cfg is None:
        cfg = wm_load_config()
    if not cfg.get("enabled", True):
        # fecha overlay se existir
        try:
            if _wm_overlay["top"] is not None and _wm_overlay["top"].winfo_exists():
                _wm_overlay["top"].destroy()
        except Exception: pass
        _wm_overlay["top"] = None
        return

    # cria overlay se necessário
    top = _wm_overlay.get("top")
    if top is None or not top.winfo_exists():
        top = _tk.Toplevel(root)
        top.overrideredirect(True)
        MASK = "#00ff00"
        try:
            top.wm_attributes("-transparentcolor", MASK)
        except Exception:
            # sem suporte -> fallback
            return wm_apply(root, cfg)
        try:
            top.attributes("-topmost", True)
        except Exception:
            pass
        top.configure(bg=MASK, highlightthickness=0, bd=0)
        _wm_overlay["top"] = top

        # ao fechar app, destruir overlay
        def _on_root_destroy(_e=None):
            try:
                if _wm_overlay["top"] is not None: _wm_overlay["top"].destroy()
            except Exception: pass
        root.bind("<Destroy>", _on_root_destroy, add="+")

    # cria conteúdo (frame com bg=MASK para ficar total transparente)
    MASK = "#00ff00"
    for w in list(top.children.values()):
        try: w.destroy()
        except Exception: pass
    import tkinter as _tk
    frm = _tk.Frame(top, bg=MASK, highlightthickness=0, bd=0)
    frm.pack(fill="both", expand=True)

    # carregar logo
    photo = None
    try:
        lp = cfg.get("logo_path") or ""
        import os
        if os.path.isabs(lp): logo_abs = lp
        else: logo_abs = os.path.join(_wm_base_dir(), lp)
        if os.path.exists(logo_abs):
            img = Image.open(logo_abs).convert("RGBA")
            h = int(cfg.get("height",42) or 42)
            scale = h / max(1, img.height)
            img = img.resize((max(1,int(img.width*scale)), h), Image.LANCZOS)
            r,g,b,a = img.split()
            a = a.point(lambda p: int(p * float(cfg.get("opacity",0.3))))
            img = Image.merge("RGBA", (r,g,b,a))
            photo = ImageTk.PhotoImage(img)
    except Exception as e:
        print("[Watermark][overlay] aviso (logo):", e)

    # componentes com bg=MASK (transparente)
    lbl_logo = None
    if photo:
        lbl_logo = _tk.Label(frm, image=photo, bd=0, bg=MASK)
        lbl_logo.image = photo
        lbl_logo.grid(row=0, column=0, sticky="se", padx=(0,6), pady=(4,0))

    lbl_text = _tk.Label(frm, text=cfg.get("text",""), bd=0, fg="#7a7a7a", bg=MASK, font=("Segoe UI", 9))
    if photo:
        lbl_text.grid(row=1, column=0, sticky="e", padx=(0,10), pady=(2,6))
    else:
        lbl_text.grid(row=0, column=1, sticky="e", padx=(0,10), pady=(4,6))

    url = (cfg.get("click_url") or "").strip()
    if url:
        def _open(_e=None):
            try: _wb.open(url)
            except Exception as e: print("[Watermark] não abriu URL:", e)
        for w in (lbl_logo, lbl_text):
            if w is not None:
                w.bind("<Button-1>", _open)
                w.configure(cursor="hand2")

    # medir tamanho para posicionar
    top.update_idletasks()
    w = top.winfo_width(); h = top.winfo_height()
    if w == 1 or h == 1:
        # dimensiona conforme conteúdo
        bbox = frm.bbox("all")
        if bbox:
            w = max(1, bbox[2] + 14); h = max(1, bbox[3] + 14)
            top.geometry(f"{w}x{h}")

    # posicionar no canto solicitado em relação à janela principal
    pos = (cfg.get("position") or "bottom-right").lower()
    def _reposition(_e=None):
        try:
            rx, ry = root.winfo_rootx(), root.winfo_rooty()
            rw, rh = root.winfo_width(), root.winfo_height()
            tw, th = top.winfo_width(), top.winfo_height()
            if "right" in pos: x = rx + rw - tw - 6
            else: x = rx + 6
            if "bottom" in pos: y = ry + rh - th - 6
            else: y = ry + 6
            top.geometry(f"+{x}+{y}")
        except Exception as e:
            print("[Watermark][overlay] reposição falhou:", e)
    _reposition()
    root.bind("<Configure>", _reposition, add="+")

def wm_apply_later_overlay(root, delay_ms=200):
    try:
        root.after(delay_ms, lambda: wm_apply_overlay(root))
    except Exception as e:
        print("[Watermark][overlay] after() falhou:", e)
# =============================================================================
# =================== FIM — MARCA D'ÁGUA FEATURE ===================


APP_TITLE = "Oficina Mecânica — v0.5 (Pro Light 2025) — FIX"
DB_NAME = "oficina.db"
# === DB PATH (writable) ============================================
# Em instalador (Program Files) a pasta do app NAO e gravavel.
# Salve o banco no LOCALAPPDATA\MecanicaDoJairo\data\oficina.db
APP_DATA_ROOT = os.environ.get('LOCALAPPDATA') or os.path.expanduser(r'~\\AppData\\Local')
APP_VENDOR = "MecanicaDoJairo"
def _get_db_path():
    base = os.path.join(APP_DATA_ROOT, APP_VENDOR, "data")
    try:
        os.makedirs(base, exist_ok=True)
    except Exception:
        # fallback para home se der erro
        base = os.path.join(os.path.expanduser("~"), "." + APP_VENDOR.lower(), "data")
        os.makedirs(base, exist_ok=True)
    dbp = os.path.join(base, DB_NAME)
    # migra banco antigo (ao lado do script) se existir e se o novo ainda nao existir
    try:
        old = os.path.join(os.path.dirname(os.path.abspath(__file__)), DB_NAME)
        if os.path.exists(old) and not os.path.exists(dbp):
            import shutil
            shutil.copy2(old, dbp)
    except Exception as _e:
        print("[DB][migracao] falhou:", _e)
    return dbp

DB_PATH = _get_db_path()
# ===================================================================
# === PATH HELPERS (work in dev & PyInstaller onedir/onefile) ===
def _app_base_dir():
    import os, sys
    try:
        if getattr(sys, "frozen", False):
            # onefile extracts to _MEIPASS; onedir runs from install dir
            meipass = getattr(sys, "_MEIPASS", None)
            if meipass:
                return meipass
            return os.path.dirname(sys.executable)
        return os.path.dirname(os.path.abspath(__file__))
    except Exception:
        # ultimate fallback: cwd
        return os.getcwd()

def res_path(*parts):
    # Return absolute path for a resource inside 'assets' or alongside the app.
    import os, sys
    base = _app_base_dir()
    p1 = os.path.join(base, *parts)
    if os.path.exists(p1):
        return p1
    # Try _MEIPASS explicitly (some PyInstaller contexts)
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        p2 = os.path.join(meipass, *parts)
        if os.path.exists(p2):
            return p2
    return p1

ASSETS_DIR = os.path.join(_app_base_dir(), "assets")
LOGO_PATH = os.path.join(ASSETS_DIR, "logo.png")  # opcional

# ----------------------------- CATÁLOGOS ----------------------------- #
BRANDS: Dict[str, List[str]] = {
    'Volkswagen': ['Gol', 'Voyage', 'Saveiro', 'Saveiro Cross', 'Parati', 'Santana', 'Polo', 'Virtus', 'T-Cross', 'Nivus', 'Fox', 'SpaceFox', 'Jetta', 'Golf', 'Bora', 'Amarok', 'Kombi'],
    'Chevrolet': ['Celta', 'Corsa', 'Classic', 'Prisma', 'Onix', 'Onix Plus', 'Montana', 'S10', 'Tracker', 'Spin', 'Cruze', 'Astra', 'Vectra', 'Meriva', 'Zafira', 'Agile', 'Cobalt'],
    'Fiat': ['Uno', 'Mobi', 'Palio', 'Siena', 'Strada', 'Toro', 'Argo', 'Cronos', 'Punto', 'Idea', 'Grand Siena', 'Fiorino', 'Doblo', 'Linea', 'Pulse', 'Fastback'],
    'Ford': ['Ka', 'Fiesta', 'Focus', 'Fusion', 'EcoSport', 'Ranger', 'Maverick', 'Courier', 'F-250', 'Edge', 'Territory'],
    'Hyundai': ['HB20', 'HB20S', 'Creta', 'Tucson', 'ix35', 'Santa Fe', 'Azera', 'i30', 'HR'],
    'Toyota': ['Etios', 'Yaris', 'Corolla', 'Corolla Cross', 'Hilux', 'SW4', 'RAV4', 'Camry', 'Bandeirante'],
    'Honda': ['Fit', 'City', 'Civic', 'HR-V', 'WR-V', 'CR-V', 'Accord'],
    'Renault': ['Kwid', 'Sandero', 'Logan', 'Duster', 'Oroch', 'Captur', 'Clio', 'Fluence', 'Megane', 'Kangoo', 'Master'],
    'Peugeot': ['206', '207', '208', '2008', '3008', '307', '308', '408', 'Partner', 'Boxer'],
    'Citroën': ['C3', 'C4', 'C4 Cactus', 'Aircross', 'Xsara Picasso', 'Berlingo', 'Jumper'],
    'Nissan': ['March', 'Versa', 'Kicks', 'Frontier', 'Sentra', 'Livina', 'Tiida', 'X-Trail'],
    'Jeep': ['Renegade', 'Compass', 'Commander', 'Cherokee', 'Wrangler'],
    'Mitsubishi': ['L200 Triton', 'Pajero', 'ASX', 'Outlander', 'Eclipse Cross'],
    'Kia': ['Picanto', 'Cerato', 'Soul', 'Sportage', 'Sorento', 'Bongo'],
    'Mercedes-Benz': ['Classe A', 'Classe B', 'Classe C', 'Sprinter', 'Accelo', 'Atego', 'Axor'],
    'BMW': ['Série 1', 'Série 3', 'Série 5', 'X1', 'X3', 'X5'],
    'Audi': ['A1', 'A3', 'A4', 'A5', 'Q3', 'Q5'],
    'Volvo': ['XC40', 'XC60', 'XC90', 'S60', 'FH', 'VM'],
    'RAM': ['Rampage', '1500', '2500', '3500'],
    'Caoa Chery': ['QQ', 'Tiggo 2', 'Tiggo 3x', 'Tiggo 5x', 'Tiggo 7', 'Tiggo 8', 'Arrizo 5', 'Arrizo 6'],
    'BYD': ['Dolphin', 'Dolphin Mini', 'Song Plus', 'Yuan Plus', 'Seal', 'Han'],
    'GWM': ['Haval H6', 'Ora 03', 'Poer'],
    'Jac': ['J2', 'J3', 'J5', 'T40', 'T50', 'T60', 'T80'],
    'Land Rover': ['Discovery', 'Discovery Sport', 'Range Rover Evoque', 'Range Rover Sport', 'Defender'],
    'Subaru': ['Forester', 'Impreza', 'XV', 'Outback'],
    'Suzuki': ['Jimny', 'Vitara', 'Grand Vitara', 'S-Cross'],
    'Iveco': ['Daily', 'Tector', 'Stralis'],
    'Scania': ['P', 'G', 'R', 'S'],
    'MAN': ['Constellation', 'Delivery'],
    'Agrale': ['Marruá', 'A7500', 'A8700'],
    'Outros': ['Modelo não listado', 'Carro não listado', 'Caminhonete não listada', 'Caminhão não listado']
}

CATALOGO: Dict[str, List[str]] = {
    'Óleos & Filtros': [
        'Troca de óleo 5W30', 'Troca de óleo 5W40', 'Filtro de óleo', 'Filtro de ar',
        'Filtro de combustível', 'Aditivo do radiador', 'Troca de óleo 0W16', 'Troca de óleo 0W20',
        'Troca de óleo 0W30', 'Troca de óleo 0W40', 'Troca de óleo 5W20', 'Troca de óleo 10W30',
        'Troca de óleo 10W40', 'Troca de óleo 15W40', 'Troca de óleo 20W50', 'Troca de óleo 15W40 Diesel',
        'Troca de óleo 5W30 C3 (Low SAPS)', 'Troca de óleo 5W40 C3 (Low SAPS)', 'Óleo 0W16 Sintético 1L (Castrol)', 'Óleo 0W16 Sintético 4L (Castrol)',
        'Óleo 0W16 Sintético 1L (Mobil)', 'Óleo 0W16 Sintético 4L (Mobil)', 'Óleo 0W16 Sintético 1L (Motul)', 'Óleo 0W16 Sintético 4L (Motul)',
        'Óleo 0W16 Sintético 1L (Shell)', 'Óleo 0W16 Sintético 4L (Shell)', 'Óleo 0W16 Sintético 1L (Ipiranga)', 'Óleo 0W16 Sintético 4L (Ipiranga)',
        'Óleo 0W20 Sintético 1L (Castrol)', 'Óleo 0W20 Sintético 4L (Castrol)', 'Óleo 0W20 Sintético 1L (Mobil)', 'Óleo 0W20 Sintético 4L (Mobil)',
        'Óleo 0W20 Sintético 1L (Motul)', 'Óleo 0W20 Sintético 4L (Motul)', 'Óleo 0W20 Sintético 1L (Shell)', 'Óleo 0W20 Sintético 4L (Shell)',
        'Óleo 0W20 Sintético 1L (Ipiranga)', 'Óleo 0W20 Sintético 4L (Ipiranga)', 'Óleo 0W30 Sintético 1L (Castrol)', 'Óleo 0W30 Sintético 4L (Castrol)',
        'Óleo 0W30 Sintético 1L (Mobil)', 'Óleo 0W30 Sintético 4L (Mobil)', 'Óleo 0W30 Sintético 1L (Motul)', 'Óleo 0W30 Sintético 4L (Motul)',
        'Óleo 0W30 Sintético 1L (Shell)', 'Óleo 0W30 Sintético 4L (Shell)', 'Óleo 0W30 Sintético 1L (Ipiranga)', 'Óleo 0W30 Sintético 4L (Ipiranga)',
        'Óleo 0W40 Sintético 1L (Castrol)', 'Óleo 0W40 Sintético 4L (Castrol)', 'Óleo 0W40 Sintético 1L (Mobil)', 'Óleo 0W40 Sintético 4L (Mobil)',
        'Óleo 0W40 Sintético 1L (Motul)', 'Óleo 0W40 Sintético 4L (Motul)', 'Óleo 0W40 Sintético 1L (Shell)', 'Óleo 0W40 Sintético 4L (Shell)',
        'Óleo 0W40 Sintético 1L (Ipiranga)', 'Óleo 0W40 Sintético 4L (Ipiranga)', 'Óleo 5W20 Sintético 1L (Castrol)', 'Óleo 5W20 Sintético 4L (Castrol)',
        'Óleo 5W20 Sintético 1L (Mobil)', 'Óleo 5W20 Sintético 4L (Mobil)', 'Óleo 5W20 Sintético 1L (Motul)', 'Óleo 5W20 Sintético 4L (Motul)',
        'Óleo 5W20 Sintético 1L (Shell)', 'Óleo 5W20 Sintético 4L (Shell)', 'Óleo 5W20 Sintético 1L (Ipiranga)', 'Óleo 5W20 Sintético 4L (Ipiranga)',
        'Óleo 5W30 Sintético 1L (Castrol)', 'Óleo 5W30 Sintético 4L (Castrol)', 'Óleo 5W30 Sintético 1L (Mobil)', 'Óleo 5W30 Sintético 4L (Mobil)',
        'Óleo 5W30 Sintético 1L (Motul)', 'Óleo 5W30 Sintético 4L (Motul)', 'Óleo 5W30 Sintético 1L (Shell)', 'Óleo 5W30 Sintético 4L (Shell)',
        'Óleo 5W30 Sintético 1L (Ipiranga)', 'Óleo 5W30 Sintético 4L (Ipiranga)', 'Óleo 5W30 C3 (Low SAPS) Sintético 1L (Castrol)', 'Óleo 5W30 C3 (Low SAPS) Sintético 4L (Castrol)',
        'Óleo 5W30 C3 (Low SAPS) Sintético 1L (Mobil)', 'Óleo 5W30 C3 (Low SAPS) Sintético 4L (Mobil)', 'Óleo 5W30 C3 (Low SAPS) Sintético 1L (Motul)', 'Óleo 5W30 C3 (Low SAPS) Sintético 4L (Motul)',
        'Óleo 5W30 C3 (Low SAPS) Sintético 1L (Shell)', 'Óleo 5W30 C3 (Low SAPS) Sintético 4L (Shell)', 'Óleo 5W30 C3 (Low SAPS) Sintético 1L (Ipiranga)', 'Óleo 5W30 C3 (Low SAPS) Sintético 4L (Ipiranga)',
        'Óleo 5W40 Sintético 1L (Castrol)', 'Óleo 5W40 Sintético 4L (Castrol)', 'Óleo 5W40 Sintético 1L (Mobil)', 'Óleo 5W40 Sintético 4L (Mobil)',
        'Óleo 5W40 Sintético 1L (Motul)', 'Óleo 5W40 Sintético 4L (Motul)', 'Óleo 5W40 Sintético 1L (Shell)', 'Óleo 5W40 Sintético 4L (Shell)',
        'Óleo 5W40 Sintético 1L (Ipiranga)', 'Óleo 5W40 Sintético 4L (Ipiranga)', 'Óleo 5W40 C3 (Low SAPS) Sintético 1L (Castrol)', 'Óleo 5W40 C3 (Low SAPS) Sintético 4L (Castrol)',
        'Óleo 5W40 C3 (Low SAPS) Sintético 1L (Mobil)', 'Óleo 5W40 C3 (Low SAPS) Sintético 4L (Mobil)', 'Óleo 5W40 C3 (Low SAPS) Sintético 1L (Motul)', 'Óleo 5W40 C3 (Low SAPS) Sintético 4L (Motul)',
        'Óleo 5W40 C3 (Low SAPS) Sintético 1L (Shell)', 'Óleo 5W40 C3 (Low SAPS) Sintético 4L (Shell)', 'Óleo 5W40 C3 (Low SAPS) Sintético 1L (Ipiranga)', 'Óleo 5W40 C3 (Low SAPS) Sintético 4L (Ipiranga)',
        'Óleo 10W30 Semissintético 1L (Castrol)', 'Óleo 10W30 Semissintético 4L (Castrol)', 'Óleo 10W30 Semissintético 1L (Mobil)', 'Óleo 10W30 Semissintético 4L (Mobil)',
        'Óleo 10W30 Semissintético 1L (Motul)', 'Óleo 10W30 Semissintético 4L (Motul)', 'Óleo 10W30 Semissintético 1L (Shell)', 'Óleo 10W30 Semissintético 4L (Shell)',
        'Óleo 10W30 Semissintético 1L (Ipiranga)', 'Óleo 10W30 Semissintético 4L (Ipiranga)', 'Óleo 10W40 Semissintético 1L (Castrol)', 'Óleo 10W40 Semissintético 4L (Castrol)',
        'Óleo 10W40 Semissintético 1L (Mobil)', 'Óleo 10W40 Semissintético 4L (Mobil)', 'Óleo 10W40 Semissintético 1L (Motul)', 'Óleo 10W40 Semissintético 4L (Motul)',
        'Óleo 10W40 Semissintético 1L (Shell)', 'Óleo 10W40 Semissintético 4L (Shell)', 'Óleo 10W40 Semissintético 1L (Ipiranga)', 'Óleo 10W40 Semissintético 4L (Ipiranga)',
        'Óleo 15W40 Mineral 1L (Castrol)', 'Óleo 15W40 Mineral 4L (Castrol)', 'Óleo 15W40 Mineral 1L (Mobil)', 'Óleo 15W40 Mineral 4L (Mobil)',
        'Óleo 15W40 Mineral 1L (Motul)', 'Óleo 15W40 Mineral 4L (Motul)', 'Óleo 15W40 Mineral 1L (Shell)', 'Óleo 15W40 Mineral 4L (Shell)',
        'Óleo 15W40 Mineral 1L (Ipiranga)', 'Óleo 15W40 Mineral 4L (Ipiranga)', 'Óleo 15W40 Diesel Mineral 1L (Castrol)', 'Óleo 15W40 Diesel Mineral 4L (Castrol)',
        'Óleo 15W40 Diesel Mineral 1L (Mobil)', 'Óleo 15W40 Diesel Mineral 4L (Mobil)', 'Óleo 15W40 Diesel Mineral 1L (Motul)', 'Óleo 15W40 Diesel Mineral 4L (Motul)',
        'Óleo 15W40 Diesel Mineral 1L (Shell)', 'Óleo 15W40 Diesel Mineral 4L (Shell)', 'Óleo 15W40 Diesel Mineral 1L (Ipiranga)', 'Óleo 15W40 Diesel Mineral 4L (Ipiranga)',
        'Óleo 20W50 Mineral 1L (Castrol)', 'Óleo 20W50 Mineral 4L (Castrol)', 'Óleo 20W50 Mineral 1L (Mobil)', 'Óleo 20W50 Mineral 4L (Mobil)',
        'Óleo 20W50 Mineral 1L (Motul)', 'Óleo 20W50 Mineral 4L (Motul)', 'Óleo 20W50 Mineral 1L (Shell)', 'Óleo 20W50 Mineral 4L (Shell)',
        'Óleo 20W50 Mineral 1L (Ipiranga)', 'Óleo 20W50 Mineral 4L (Ipiranga)',
    ],
    'Suspensão': [
        'Amortecedor dianteiro', 'Amortecedor traseiro',
        'Kit amortecedor dianteiro', 'Kit amortecedor traseiro',
        'Coxim superior do amortecedor', 'Batente do amortecedor', 'Coifa do amortecedor',
        'Mola helicoidal dianteira', 'Mola helicoidal traseira',
        'Bieleta da barra estabilizadora', 'Barra estabilizadora', 'Bucha da barra estabilizadora',
        'Bandeja de suspensão', 'Bucha da bandeja', 'Pivô (pivot) de suspensão',
        'Bucha do eixo traseiro', 'Coxim do agregado (subframe)',
        'Rolamento do cubo', 'Cubo de roda', 'Manga de eixo'
    ],
    'Freios': [
        'Pastilha dianteira', 'Pastilha traseira', 'Disco de freio', 'Tambores', 'Fluido de freio', 'Sangria do sistema'
    ],
    'Elétrica': [
        'Bateria', 'Alternador', 'Motor de partida', 'Lâmpada H7', 'Sensor ABS'
    ],
    'Arrefecimento': [
        'Radiador', 'Bomba d’água', 'Válvula termostática', 'Reservatório', 'Mangueira do radiador'
    ],
    'Transmissão': [
        'Embreagem (kit)', 'Óleo de câmbio', 'Cabo de embreagem'
    ],
    'Pneus & Geometria': [
        'Pneu 175/65R14', 'Pneu 205/55R16', 'Alinhamento', 'Balanceamento', 'Cambagem'
    ],
    'Limpeza & Ar': [
        'Higienização do ar-condicionado', 'Filtro de cabine', 'Limpeza de bicos'
    ],
    'Outros': [
        'Diagnóstico via scanner', 'Mão de obra geral'
    ],
}
# --- Categoria adicionada: Correias (serviços e itens relacionados a correias do veículo) ---
CATALOGO.update({
    'Correias': [
        'Correia dentada (kit)',
        'Correia dentada (apenas correia)',
        'Tensor da correia dentada',
        'Esticador da correia dentada',
        'Correia do alternador (poly V)',
        'Tensor da correia do alternador',
        'Correia do ar-condicionado',
        'Tensor da correia do ar-condicionado',
        'Correia da direção hidráulica',
        'Tensor da correia da direção hidráulica',
        'Kit correias auxiliares (alternador/ar/direção)',
        'Polia guia',
        'Polia do alternador',
        'Verificação e ajuste de tensionamento das correias'
    ]
})




# --- Categoria adicionada: Motor (peças e sensores do conjunto do motor) ---
CATALOGO.update({
    'Motor': [
        'Vela de ignição',
        'Jogo de velas',
        'Cabo de vela',
        'Bobina de ignição',
        'Junta da tampa de válvulas',
        'Junta do cárter',
        'Jogo de juntas (motor)',
        'Retentor do virabrequim (dianteiro)',
        'Retentor do virabrequim (traseiro)',
        'Retentor do comando de válvulas',
        'Bomba de óleo',
        'Bico injetor',
        'Sensor MAP',
        'Sensor MAF',
        'Sensor TPS',
        'Sonda lambda (pré)',
        'Sonda lambda (pós)',
        'Válvula PCV',
        'Coxim do motor',
        'Junta do coletor de admissão',
        'Junta do coletor de escape'
    ]
})

# Itens seed de estoque


ESTOQUE_BASICO = [
    ('Óleo 5W30 (Petronas)', 'Lubrificantes', 0, 0),
    ('Óleo 5W40 (Elaion)', 'Lubrificantes', 0, 0),
    ('Óleo 0W20 (Uni)', 'Lubrificantes', 0, 0),
    ('Óleo 15W40 (Petronas)', 'Lubrificantes', 0, 0),
    ('Óleo 20W50', 'Lubrificantes', 0, 0),
    ('Óleo 5W40 (Castrol)', 'Lubrificantes', 0, 0),
    ('Óleo 0W20 700xs (Petronas)', 'Lubrificantes', 0, 0),
    ('Óleo 5W30 Nexo 1 (Petronas)', 'Lubrificantes', 0, 0),
    ('Óleo 5W20 (Havoline)', 'Lubrificantes', 0, 0),
    ('Óleo 0W20 (Elaion)', 'Lubrificantes', 0, 0),
    ('Óleo 5W30 (I9lub)', 'Lubrificantes', 0, 0),
    ('Óleo 5W30 Nexo 2', 'Lubrificantes', 0, 0),
    ('TM 1', 'Filtros lubrificantes', 0, 0),
    ('TM 2', 'Filtros lubrificantes', 0, 0),
    ('TM 3', 'Filtros lubrificantes', 0, 0),
    ('TM 4', 'Filtros lubrificantes', 0, 0),
    ('TM 5', 'Filtros lubrificantes', 0, 0),
    ('Psh 560', 'Filtros lubrificantes', 0, 0),
    ('Psh 545', 'Filtros lubrificantes', 0, 0),
    ('Psh 45', 'Filtros lubrificantes', 0, 0),
    ('Psh 56', 'Filtros lubrificantes', 0, 0),
    ('Psh 129', 'Filtros lubrificantes', 0, 0),
    ('PEL 803', 'Filtros lubrificantes', 0, 0),
    ('PEL 119', 'Filtros lubrificantes', 0, 0),
    ('WO 132', 'Filtros lubrificantes', 0, 0),
    ('Psh 47', 'Filtros lubrificantes', 0, 0),
    ('Psh 55', 'Filtros lubrificantes', 0, 0),
    ('Psh 619', 'Filtros lubrificantes', 0, 0),
    ('Psh 612', 'Filtros lubrificantes', 0, 0),
    ('Psh 145', 'Filtros lubrificantes', 0, 0),
    ('Psh 134', 'Filtros lubrificantes', 0, 0),
    ('Psh 77', 'Filtros lubrificantes', 0, 0),
    ('PE 103', 'Filtros lubrificantes', 0, 0),
    ('Psh 565', 'Filtros lubrificantes', 0, 0),
    ('Psh 615', 'Filtros lubrificantes', 0, 0),
    ('Psh 818', 'Filtros lubrificantes', 0, 0),
    ('G10811', 'Filtros de combustível', 0, 0),
    ('G10711', 'Filtros de combustível', 0, 0),
    ('G10617', 'Filtros de combustível', 0, 0),
    ('G12217', 'Filtros de combustível', 0, 0),
    ('G15017', 'Filtros de combustível', 0, 0),
    ('G10417', 'Filtros de combustível', 0, 0),
    ('G14017', 'Filtros de combustível', 0, 0),
    ('G16017', 'Filtros de combustível', 0, 0),
    ('AG 68', 'Filtros de combustível', 0, 0),
    ('GU 86', 'Filtros de combustível', 0, 0),
    ('G141', 'Filtros de combustível', 0, 0),
    ('ARL 4150', 'Filtros de ar', 0, 0),
    ('ARL 8840', 'Filtros de ar', 0, 0),
    ('ARL 8839', 'Filtros de ar', 0, 0),
    ('ARL 6093', 'Filtros de ar', 0, 0),
    ('ARL 8825', 'Filtros de ar', 0, 0),
    ('ARL 6076', 'Filtros de ar', 0, 0),
    ('ARL 4154', 'Filtros de ar', 0, 0),
    ('ARL 6071', 'Filtros de ar', 0, 0),
    ('ARL 6095', 'Filtros de ar', 0, 0),
    ('ARL 4152', 'Filtros de ar', 0, 0),
    ('ARL 4161', 'Filtros de ar', 0, 0),
    ('ARL 6091', 'Filtros de ar', 0, 0),
    ('ARL 6080', 'Filtros de ar', 0, 0),
    ('ARL 8834', 'Filtros de ar', 0, 0),
    ('ARL 4247', 'Filtros de ar', 0, 0),
    ('ARL 8820', 'Filtros de ar', 0, 0),
    ('ART 6090', 'Filtros de ar', 0, 0),
    ('AR 9621', 'Filtros de ar', 0, 0),
    ('ARL 6096', 'Filtros de ar', 0, 0),
    ('ARL 9608', 'Filtros de ar', 0, 0),
    ('FAP 9288', 'Filtros de ar', 0, 0),
    ('ARL 8832', 'Filtros de ar', 0, 0),
    ('ARL 8825', 'Filtros de ar', 0, 0),
    ('ARL 1034', 'Filtros de ar', 0, 0),
    ('ARL 4155', 'Filtros de ar', 0, 0),
    ('ARL 2203', 'Filtros de ar', 0, 0),
    ('ARL 6074', 'Filtros de ar', 0, 0),
    ('ARL 1035', 'Filtros de ar', 0, 0),
    ('ARL 8829', 'Filtros de ar', 0, 0),
    ('ART 8860', 'Filtros de ar', 0, 0),
    ('ARL 4161', 'Filtros de ar', 0, 0),
    ('ARS 1029', 'Filtros de ar', 0, 0),
    ('ARL 1658', 'Filtros de ar', 0, 0),
    ('AR 7705', 'Filtros de ar', 0, 0),
    ('ARL 6090', 'Filtros de ar', 0, 0),
    ('ARL 4160', 'Filtros de ar', 0, 0),
    ('ARL 2207', 'Filtros de ar', 0, 0),
    ('ARL 2340', 'Filtros de ar', 0, 0),
    ('ARL 2204', 'Filtros de ar', 0, 0),
    ('ART 9613', 'Filtros de ar', 0, 0),
    ('ARL 1043', 'Filtros de ar', 0, 0),
    ('ART 9614', 'Filtros de ar', 0, 0),
    ('AR 2952', 'Filtros de ar', 0, 0),
    ('AR 6046', 'Filtros de ar', 0, 0),
    ('AR 6093', 'Filtros de ar', 0, 0),
    ('ARL 2238', 'Filtros de ar', 0, 0),
    ('ART 9615', 'Filtros de ar', 0, 0),
    ('ACP 105', 'Filtros de ar condicionado', 0, 0),
    ('ACP 300', 'Filtros de ar condicionado', 0, 0),
    ('ACP 303', 'Filtros de ar condicionado', 0, 0),
    ('ACP 103', 'Filtros de ar condicionado', 0, 0),
    ('ACP 311', 'Filtros de ar condicionado', 0, 0),
    ('ACP 126', 'Filtros de ar condicionado', 0, 0),
    ('ACP 887', 'Filtros de ar condicionado', 0, 0),
    ('ACP 312', 'Filtros de ar condicionado', 0, 0),
    ('ACP 003', 'Filtros de ar condicionado', 0, 0),
    ('ACP 906', 'Filtros de ar condicionado', 0, 0),
    ('ACP 008', 'Filtros de ar condicionado', 0, 0),
    ('ACP 305', 'Filtros de ar condicionado', 0, 0),
    ('ACP 972', 'Filtros de ar condicionado', 0, 0),
    ('ACP 709', 'Filtros de ar condicionado', 0, 0),
    ('ACP 001', 'Filtros de ar condicionado', 0, 0),
    ('ACP 888', 'Filtros de ar condicionado', 0, 0),
    ('ACP 205', 'Filtros de ar condicionado', 0, 0),
    ('ACP 721', 'Filtros de ar condicionado', 0, 0),
    ('ACP 727', 'Filtros de ar condicionado', 0, 0),
    ('JFA 0192', 'Filtros de ar condicionado', 0, 0),
    ('Jogo velas Gol H — BKR6ESB-D', 'Velas e cabos de vela', 0, 0),
    ('Jogo velas Fire — BKR6E-D', 'Velas e cabos de vela', 0, 0),
    ('Jogo velas — BR6ES-D', 'Velas e cabos de vela', 0, 0),
    ('Jogo velas — B7ES-D', 'Velas e cabos de vela', 0, 0),
    ('Jogo velas — BPR6E-D', 'Velas e cabos de vela', 0, 0),
    ('Jogo velas — BKR6E-09', 'Velas e cabos de vela', 0, 0),
    ('Jogo velas — BPR5EY-D', 'Velas e cabos de vela', 0, 0),
    ('Jogo velas — BPR6EY-D', 'Velas e cabos de vela', 0, 0),
    ('Jogo velas Magnet — BR6ES-D', 'Velas e cabos de vela', 0, 0),
    ('Jogo de velas Evo — ZKR8B10', 'Velas e cabos de vela', 0, 0),
    ('Cabo velas VW Bosch — F00099C125', 'Velas e cabos de vela', 0, 0),
    ('Cabo velas Fiat Bosch Fire — F00099C320', 'Velas e cabos de vela', 0, 0),
    ('Cabo velas VW Magnet — CVMP8502', 'Velas e cabos de vela', 0, 0),
    ('Cabo velas Magnet — CVMG7302', 'Velas e cabos de vela', 0, 0),
    ('Cabo velas Fiat Magnet — CVMT9902', 'Velas e cabos de vela', 0, 0),
    ('Cabo velas Fiat Evo — F00099C146', 'Velas e cabos de vela', 0, 0),
    ('Cabo velas — F00099C012', 'Velas e cabos de vela', 0, 0),
    ('Cabo velas — F00099C612', 'Velas e cabos de vela', 0, 0),
    ('Cabo velas — F00099C110', 'Velas e cabos de vela', 0, 0),
    ('Cabo velas — F00099C117', 'Velas e cabos de vela', 0, 0),
    ('Cabo velas — F00099C143', 'Velas e cabos de vela', 0, 0),
    ('Jogo velas Gol 1.0 — BKR5EY', 'Velas e cabos de vela', 0, 0),
    ('Cabo velas Gol 1.0 — 9295080044', 'Velas e cabos de vela', 0, 0),
    ('Jogo velas Etorq — KR8B-10D', 'Velas e cabos de vela', 0, 0),
    ('Jogo cabo velas — F00099C142', 'Velas e cabos de vela', 0, 0),
    ('Jogo cabo velas (Celta) — NGR', 'Velas e cabos de vela', 0, 0),
    ('Correia dentada Gol (Dayco 76,50)', 'Correias e esticadores', 0, 0),
    ('Correia 129P85220H', 'Correias e esticadores', 0, 0),
    ('Correia 124P85220H', 'Correias e esticadores', 0, 0),
    ('Correia 111SP170H', 'Correias e esticadores', 0, 0),
    ('Correia 1295x180H', 'Correias e esticadores', 0, 0),
    ('Correia 3495TP8M254H', 'Correias e esticadores', 0, 0),
    ('Correia 3PK796EE (ar condicionado)', 'Correias e esticadores', 0, 0),
    ('Correia 6PK1200EE (alternador)', 'Correias e esticadores', 0, 0),
    ('Correia 5PK1795', 'Correias e esticadores', 0, 0),
    ('Correia 5PK1170', 'Correias e esticadores', 0, 0),
    ('Correia 1175T0', 'Correias e esticadores', 0, 0),
    ('Correia 1315HP170H', 'Correias e esticadores', 0, 0),
    ('Correia 1175150', 'Correias e esticadores', 0, 0),
    ('Correia 4PK9673 (alternador)', 'Correias e esticadores', 0, 0),
    ('Correia 5PK1190 (alternador)', 'Correias e esticadores', 0, 0),
    ('Correia 3PK905 (direção)', 'Correias e esticadores', 0, 0),
    ('Correia 6PK1795', 'Correias e esticadores', 0, 0),
    ('Correia 5PK1030', 'Correias e esticadores', 0, 0),
    ('Correia 5PK1185', 'Correias e esticadores', 0, 0),
    ('Correia 5PK1175 (alternador)', 'Correias e esticadores', 0, 0),
    ('Correia 5PK1180', 'Correias e esticadores', 0, 0),
    ('Correia 5PK1460', 'Correias e esticadores', 0, 0),
    ('Correia 10A0925C', 'Correias e esticadores', 0, 0),
    ('Correia 3PK890EE', 'Correias e esticadores', 0, 0),
    ('Correia 1465TP8M200H', 'Correias e esticadores', 0, 0),
    ('Correia 6PK2270', 'Correias e esticadores', 0, 0),
    ('Correia 6PK870', 'Correias e esticadores', 0, 0),
    ('Correia 6PK1700', 'Correias e esticadores', 0, 0),
    ('Polia do alternador 1143', 'Correias e esticadores', 0, 0),
    ('Polia do alternador 1152', 'Correias e esticadores', 0, 0),
    ('Tensor 7796 GM', 'Correias e esticadores', 0, 0),
    ('Tensor 7704 Fiat', 'Correias e esticadores', 0, 0),
    ('Tensor 7736 Gol', 'Correias e esticadores', 0, 0),
    ('Tensor 7741 Fiat', 'Correias e esticadores', 0, 0),
    ('Tensor 7792 GM', 'Correias e esticadores', 0, 0),
    ('Tensor 7782 Gol', 'Correias e esticadores', 0, 0),
    ('Tensor 7732 Fiat', 'Correias e esticadores', 0, 0),
    ('Tensor RT6367 Fiat', 'Correias e esticadores', 0, 0),
    ('Tensor RT6009L17', 'Correias e esticadores', 0, 0),
    ('Tensor RT6526 Fiat', 'Correias e esticadores', 0, 0),
    ('Tensor RT0816 Gol', 'Correias e esticadores', 0, 0),
    ('Tensor RT0817 Gol', 'Correias e esticadores', 0, 0),
    ('Tensor RT6180 Gol', 'Correias e esticadores', 0, 0),
    ('Tensor RT6027 Gol', 'Correias e esticadores', 0, 0),
    ('Polia esticador GM 1139', 'Correias e esticadores', 0, 0),
    ('Polia esticador GM 1129', 'Correias e esticadores', 0, 0),
    ('Polia esticador Gol 1114', 'Correias e esticadores', 0, 0),
    ('Rolamento esticador GM RT6026', 'Correias e esticadores', 0, 0),
    ('Polia do alternador Cobalt', 'Correias e esticadores', 0, 0),
    ('Polia do alternador 1180', 'Correias e esticadores', 0, 0),
    ('Correia 3PK895EE', 'Correias e esticadores', 0, 0),
    ('Pastilha de freio — P.85', 'Pastilhas/Sapatas', 0, 0),
    ('Pastilha de freio — P.1346', 'Pastilhas/Sapatas', 0, 0),
    ('Pastilha de freio — P.92', 'Pastilhas/Sapatas', 0, 0),
    ('Pastilha de freio — P.73', 'Pastilhas/Sapatas', 0, 0),
    ('Pastilha de freio — P.58', 'Pastilhas/Sapatas', 0, 0),
    ('Pastilha de freio — P.88', 'Pastilhas/Sapatas', 0, 0),
    ('Pastilha de freio — P.362', 'Pastilhas/Sapatas', 0, 0),
    ('Pastilha de freio — P.1482', 'Pastilhas/Sapatas', 0, 0),
    ('Pastilha de freio — P.368', 'Pastilhas/Sapatas', 0, 0),
    ('Pastilha de freio — P.60', 'Pastilhas/Sapatas', 0, 0),
    ('Pastilha de freio — P.94', 'Pastilhas/Sapatas', 0, 0),
    ('Pastilha de freio — P.82', 'Pastilhas/Sapatas', 0, 0),
    ('Pastilha de freio — P.65', 'Pastilhas/Sapatas', 0, 0),
    ('Pastilha de freio — P.90', 'Pastilhas/Sapatas', 0, 0),
    ('Pastilha de freio — P.54', 'Pastilhas/Sapatas', 0, 0),
    ('Pastilha de freio — P.25', 'Pastilhas/Sapatas', 0, 0),
    ('Pastilha de freio — P.68', 'Pastilhas/Sapatas', 0, 0),
    ('Pastilha de freio — P.55', 'Pastilhas/Sapatas', 0, 0),
    ('Pastilha de freio — P.46', 'Pastilhas/Sapatas', 0, 0),
    ('Pastilha de freio — P.367', 'Pastilhas/Sapatas', 0, 0),
    ('Pastilha de freio — PD/1100', 'Pastilhas/Sapatas', 0, 0),
    ('Pastilha de freio — P.51', 'Pastilhas/Sapatas', 0, 0),
    ('Pastilha de freio — P.23', 'Pastilhas/Sapatas', 0, 0),
    ('Pastilha de freio — PD/588B', 'Pastilhas/Sapatas', 0, 0),
    ('Pastilha de freio — PD/1584', 'Pastilhas/Sapatas', 0, 0),
    ('Pastilha de freio — P.42', 'Pastilhas/Sapatas', 0, 0),
    ('Pastilha de freio — P.66', 'Pastilhas/Sapatas', 0, 0),
    ('Pastilha de freio — PD.28', 'Pastilhas/Sapatas', 0, 0),
    ('Pastilha de freio — SYL', 'Pastilhas/Sapatas', 0, 0),
    ('Pastilha de freio — P.81', 'Pastilhas/Sapatas', 0, 0),
    ('Pastilha de freio — P.42', 'Pastilhas/Sapatas', 0, 0),
    ('Pastilha de freio — PD/1669', 'Pastilhas/Sapatas', 0, 0),
    ('Pastilha de freio — PD/1689', 'Pastilhas/Sapatas', 0, 0),
    ('Pastilha de freio — PD/1696', 'Pastilhas/Sapatas', 0, 0),
    ('Pastilha de freio — 3115', 'Pastilhas/Sapatas', 0, 0),
    ('Pastilha de freio — 4381', 'Pastilhas/Sapatas', 0, 0),
    ('Pastilha de freio — P.1432', 'Pastilhas/Sapatas', 0, 0),
    ('Pastilha de freio — P.4082', 'Pastilhas/Sapatas', 0, 0),
    ('Pastilha de freio — PD/1795', 'Pastilhas/Sapatas', 0, 0),
    ('Pastilha de freio — P.89', 'Pastilhas/Sapatas', 0, 0),
    ('Pastilha de freio — P.17', 'Pastilhas/Sapatas', 0, 0),
    ('Pastilha de freio — PD/1480', 'Pastilhas/Sapatas', 0, 0),
    ('Pastilha de freio — P.87', 'Pastilhas/Sapatas', 0, 0),
    ('Sapata de freio — F193CP', 'Pastilhas/Sapatas', 0, 0),
    ('Sapata de freio — CB149-CP', 'Pastilhas/Sapatas', 0, 0),
    ('Sapata de freio — F191-CP', 'Pastilhas/Sapatas', 0, 0),
    ('Sapata de freio — FD/61CPA', 'Pastilhas/Sapatas', 0, 0),
    ('Sapata de freio — F1219-CPA', 'Pastilhas/Sapatas', 0, 0),
    ('Pastilha de freio — P.47', 'Pastilhas/Sapatas', 0, 0),
    ('Sapata de freio — F1330', 'Pastilhas/Sapatas', 0, 0),
    ('Strada 1.4 dianteiro', 'Amortecedores', 0, 0),
    ('Strada 1.4 traseiro', 'Amortecedores', 0, 0),
    ('Palio Powershock dianteiro', 'Amortecedores', 0, 0),
    ('Celta dianteiro', 'Amortecedores', 0, 0),
    ('Celta traseiro', 'Amortecedores', 0, 0),
    ('Gol G3 dianteiro', 'Amortecedores', 0, 0),
    ('Palio traseiro', 'Amortecedores', 0, 0),
    ('Gol G3 traseiro', 'Amortecedores', 0, 0),
    ('Óleo 10W30 200ml', 'Diversos', 0, 0),
    ('Óleo 10W40 200ml', 'Diversos', 0, 0),
    ('Óleo 10W30 500ml', 'Diversos', 0, 0),
    ('Óleo 10W40 500ml', 'Diversos', 0, 0),
    ('Óleo caixa 90', 'Diversos', 0, 0),
    ('Óleo direção hidráulica ATF10', 'Diversos', 0, 0),
    ('Óleo direção SAE 440', 'Diversos', 0, 0),
    ('Aditivo Teccool', 'Diversos', 0, 0),
    ('Aditivo Petronas', 'Diversos', 0, 0),
    ('Limpa radiador Paraflu', 'Diversos', 0, 0),
    ('Graxa 1kg', 'Diversos', 0, 0),
    ('Querosene', 'Diversos', 0, 0),
    ('Silenciador de freio', 'Diversos', 0, 0),
    ('Desengripante', 'Diversos', 0, 0),
    ('Água desmineralizada', 'Diversos', 0, 0),
    ('Limpa ar condicionado', 'Diversos', 0, 0),
]# --- Seed adicional de estoque: itens de Motor ---
ESTOQUE_BASICO += [
    ('Vela de ignição', 'Motor', 16, 29.90),
    ('Jogo de velas', 'Motor', 4, 119.90),
    ('Cabo de vela', 'Motor', 4, 89.90),
    ('Bobina de ignição', 'Motor', 4, 249.90),
    ('Junta da tampa de válvulas', 'Motor', 4, 49.90),
    ('Junta do cárter', 'Motor', 2, 79.90),
    ('Jogo de juntas (motor)', 'Motor', 2, 399.90),
    ('Retentor do virabrequim (dianteiro)', 'Motor', 4, 39.90),
    ('Retentor do virabrequim (traseiro)', 'Motor', 4, 59.90),
    ('Retentor do comando de válvulas', 'Motor', 4, 39.90),
    ('Bomba de óleo', 'Motor', 2, 349.90),
    ('Bico injetor', 'Motor', 8, 199.90),
    ('Sensor MAP', 'Motor', 4, 129.90),
    ('Sensor MAF', 'Motor', 2, 299.90),
    ('Sensor TPS', 'Motor', 4, 89.90),
    ('Sonda lambda (pré)', 'Motor', 2, 349.90),
    ('Sonda lambda (pós)', 'Motor', 2, 349.90),
    ('Válvula PCV', 'Motor', 4, 79.90),
    ('Coxim do motor', 'Motor', 2, 199.90),
    ('Junta do coletor de admissão', 'Motor', 4, 49.90),
    ('Junta do coletor de escape', 'Motor', 4, 54.90),
]

# ----------------------------- DB LAYER ----------------------------- #
class Database:
    
    def _norm_item_name(self, s: str) -> str:
        try:
            import unicodedata, re as _re
            s = (s or '').strip().lower()
            s = ''.join(ch for ch in unicodedata.normalize('NFKD', s) if not unicodedata.combining(ch))
            s = _re.sub(r'[^a-z0-9]+', ' ', s)
            s = ' '.join(s.split())
            return s
        except Exception:
            return (s or '').strip().lower()

    def __init__(self, db_path: str):
        self.db_path = db_path
        self._ensure_db()

    def _connect(self):
        # Garante que a pasta do banco exista (pode ter sido limpada)
        try:
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        except Exception:
            pass
        con = sqlite3.connect(self.db_path)
        try:
            con.execute("PRAGMA foreign_keys = ON;")
            con.execute("PRAGMA journal_mode = WAL;")
            con.execute("PRAGMA synchronous = NORMAL;")
        except Exception:
            pass
        return con

    def _ensure_db(self):
        with self._connect() as con:
            cur = con.cursor()
            cur.execute("""CREATE TABLE IF NOT EXISTS clientes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL,
                    telefone TEXT
                );
            """)
            cur.execute("""CREATE TABLE IF NOT EXISTS veiculos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cliente_id INTEGER NOT NULL,
                    marca TEXT,
                    modelo TEXT,
                    placa TEXT UNIQUE,
                    ano TEXT,
                    km_atual INTEGER DEFAULT 0,
                    FOREIGN KEY (cliente_id) REFERENCES clientes(id)
                );
            """)
            # --- MIGRATION: correia dentada campos ---
            try:
                cur.execute("PRAGMA table_info(veiculos)")
                cols = [r[1] for r in cur.fetchall()]
                if "km_troca_corr" not in cols:
                    cur.execute("ALTER TABLE veiculos ADD COLUMN km_troca_corr INTEGER DEFAULT 0")
                if "km_corr_trocada" not in cols:
                    cur.execute("ALTER TABLE veiculos ADD COLUMN km_corr_trocada INTEGER DEFAULT 0")
                if "km_corr_proxima" not in cols:
                    cur.execute("ALTER TABLE veiculos ADD COLUMN km_corr_proxima INTEGER DEFAULT 0")
            except Exception as _e:
                print("[DB] migração correia:", _e)

            cur.execute("""CREATE TABLE IF NOT EXISTS servicos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    veiculo_id INTEGER NOT NULL,
                    descricao TEXT,
                    km_atual INTEGER DEFAULT 0,
                    intervalo_km INTEGER DEFAULT 10000,
                    proxima_manut_km INTEGER DEFAULT 0,
                    data TEXT,
                    FOREIGN KEY (veiculo_id) REFERENCES veiculos(id)
                );
            """)
            cur.execute("""CREATE TABLE IF NOT EXISTS itens_servico (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    servico_id INTEGER NOT NULL,
                    categoria TEXT,
                    item TEXT NOT NULL,
                    qtde INTEGER DEFAULT 1,
                    valor_unit REAL DEFAULT 0,
                    FOREIGN KEY (servico_id) REFERENCES servicos(id)
                );
            """)
            cur.execute("""CREATE TABLE IF NOT EXISTS estoque (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    item TEXT NOT NULL,
                    categoria TEXT,
                    qtde INTEGER DEFAULT 0,
                    preco REAL DEFAULT 0
                );
            """)
            con.commit()

    # ---------- CRUD helpers ---------- #
    def upsert_cliente(self, nome: str, telefone: Optional[str]) -> int:
        with self._connect() as con:
            cur = con.cursor()
            cur.execute("SELECT id FROM clientes WHERE nome = ? AND ifnull(telefone,'') = ifnull(?, '')", (nome.strip(), telefone or ""))
            row = cur.fetchone()
            if row:
                return row[0]
            cur.execute("INSERT INTO clientes (nome, telefone) VALUES (?, ?)", (nome.strip(), telefone))
            con.commit()
            return cur.lastrowid

    def upsert_veiculo(self, cliente_id: int, marca: str, modelo: str, placa: str, ano: str,
                   km_atual: int, km_troca_corr: int, km_corr_trocada: int, km_corr_proxima: int) -> int:
        placa = placa.strip().upper()
        with self._connect() as con:
            cur = con.cursor()
            cur.execute("SELECT id FROM veiculos WHERE placa = ?", (placa,))
            row = cur.fetchone()
            if row:
                vid = row[0]
                cur.execute("UPDATE veiculos SET cliente_id=?, marca=?, modelo=?, ano=?, km_atual=?, km_troca_corr=?, km_corr_trocada=?, km_corr_proxima=? WHERE id=?",
                    (cliente_id, marca, modelo, ano, km_atual, km_troca_corr, km_corr_trocada, km_corr_proxima, vid)
                )
                con.commit()
                return vid
            cur.execute("INSERT INTO veiculos (cliente_id, marca, modelo, placa, ano, km_atual, km_troca_corr, km_corr_trocada, km_corr_proxima) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (cliente_id, marca, modelo, placa, ano, km_atual, km_troca_corr, km_corr_trocada, km_corr_proxima)
            )
            con.commit()
            return cur.lastrowid

    def add_servico(self, veiculo_id: int, descricao: str, km_atual: int, intervalo_km: int, proxima_km: int, data: str) -> int:
        with self._connect() as con:
            cur = con.cursor()
            cur.execute("""INSERT INTO servicos (veiculo_id, descricao, km_atual, intervalo_km, proxima_manut_km, data)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (veiculo_id, descricao, km_atual, intervalo_km, proxima_km, data))
            con.commit()
            return cur.lastrowid

    def add_itens_servico(self, servico_id: int, itens: List[Dict[str, Any]]):
        if not itens:
            return
        with self._connect() as con:
            cur = con.cursor()
            cur.executemany("INSERT INTO itens_servico (servico_id, categoria, item, qtde, valor_unit) VALUES (?, ?, ?, ?, ?)",
                            [(servico_id, i['categoria'], i['item'], int(i['qtde']), float(i['valor_unit'])) for i in itens])
            con.commit()
    def get_servico_full(self, servico_id: int):
        with self._connect() as con:
            cur = con.cursor()
            cur.execute("""                SELECT s.id, s.veiculo_id, s.descricao, s.km_atual, s.intervalo_km, s.proxima_manut_km, s.data,
                       v.cliente_id, v.marca, v.modelo, v.placa, v.ano, v.km_atual,
                       c.nome, c.telefone,
                       ifnull(v.km_troca_corr,0), ifnull(v.km_corr_trocada,0), ifnull(v.km_corr_proxima,0)
                FROM servicos s
                JOIN veiculos v ON v.id = s.veiculo_id
                JOIN clientes c ON c.id = v.cliente_id
                WHERE s.id = ?
            """, (int(servico_id),))
            return cur.fetchone()

    def update_servico_fields(self, servico_id: int, descricao: str, km_atual: int, intervalo_km: int, proxima_km: int):
        with self._connect() as con:
            cur = con.cursor()
            cur.execute("""UPDATE servicos
                           SET descricao=?, km_atual=?, intervalo_km=?, proxima_manut_km=?
                           WHERE id=?""", (descricao, int(km_atual), int(intervalo_km), int(proxima_km), int(servico_id)))
            con.commit()

    def replace_itens_servico(self, servico_id: int, itens):
        # itens: list of (categoria, item, qtde, valor_unit)
        with self._connect() as con:
            cur = con.cursor()
            cur.execute("DELETE FROM itens_servico WHERE servico_id=?", (int(servico_id),))
            cur.executemany(
                "INSERT INTO itens_servico (servico_id, categoria, item, qtde, valor_unit) VALUES (?, ?, ?, ?, ?)",
                [(int(servico_id), cat or '', it or '', int(q or 0), float(v or 0.0)) for (cat, it, q, v) in itens]
            )
            con.commit()


    def get_itens_servico(self, servico_id: int) -> List[tuple]:
        with self._connect() as con:
            cur = con.cursor()
            cur.execute("SELECT id, categoria, item, qtde, valor_unit FROM itens_servico WHERE servico_id=? ORDER BY id", (servico_id,))
            return cur.fetchall()

    def buscar(self, termo: str):
        termo = f"%{termo.strip()}%"
        with self._connect() as con:
            cur = con.cursor()
            cur.execute("""SELECT s.id, c.nome, v.marca, v.modelo, v.placa, v.km_atual, s.proxima_manut_km, s.data
                FROM servicos s
                JOIN veiculos v ON v.id = s.veiculo_id
                JOIN clientes c ON c.id = v.cliente_id
                WHERE c.nome LIKE ? OR v.placa LIKE ?
                ORDER BY s.data DESC
            """, (termo, termo))
            return cur.fetchall()

    def estoque_get_preco(self, nome_item: str) -> Optional[float]:
        with self._connect() as con:
            cur = con.cursor()
            cur.execute("SELECT preco FROM estoque WHERE item = ? LIMIT 1", (nome_item,))
            row = cur.fetchone()
            return float(row[0]) if row else None


    def estoque_upsert_preco(self, nome_item: str, categoria: str, novo_preco: float) -> None:
        """Atualiza o preço do item no estoque (ou insere, se não existir).
        Não altera quantidade."""
        nome_item = (nome_item or '').strip()
        categoria = (categoria or 'Outros').strip()
        if not nome_item:
            return
        try: novo_preco = float(novo_preco)
        except Exception: return
        with self._connect() as con:
            cur = con.cursor()
            cur.execute("SELECT id FROM estoque WHERE item = ? LIMIT 1", (nome_item,))
            row = cur.fetchone()
            if row:
                cur.execute("UPDATE estoque SET preco = ? WHERE id = ?", (novo_preco, row[0]))
            else:
                cur.execute("INSERT INTO estoque (item, categoria, qtde, preco) VALUES (?, ?, 0, ?)", (nome_item, categoria, novo_preco))
            con.commit()
    def delete_by_placa(self, placa: str) -> int:
        placa = placa.strip().upper()
        with self._connect() as con:
            cur = con.cursor()
            cur.execute("SELECT id FROM veiculos WHERE placa = ?", (placa,))
            row = cur.fetchone()
            if not row:
                return 0
            vid = row[0]
            cur.execute("SELECT id FROM servicos WHERE veiculo_id=?", (vid,))
            serv_ids = [r[0] for r in cur.fetchall()]
            if serv_ids:
                cur.executemany("DELETE FROM itens_servico WHERE servico_id=?", [(sid,) for sid in serv_ids])
            cur.execute("DELETE FROM servicos WHERE veiculo_id=?", (vid,))
            cur.execute("DELETE FROM veiculos WHERE id=?", (vid,))
            con.commit()
            return len(serv_ids)

    def delete_servico(self, servico_id: int) -> int:
        with self._connect() as con:
            cur = con.cursor()
            cur.execute("DELETE FROM itens_servico WHERE servico_id=?", (servico_id,))
            cur.execute("DELETE FROM servicos WHERE id=?", (servico_id,))
            con.commit()
            return cur.rowcount

    def update_servico_km(self, servico_id: int, km_atual: int, intervalo_km: int, proxima_km: int) -> None:
        """Atualiza campos de KM da OS existente."""
        with self._connect() as con:
            cur = con.cursor()
            cur.execute("""UPDATE servicos
                           SET km_atual=?, intervalo_km=?, proxima_manut_km=?
                           WHERE id=?""", (int(km_atual), int(intervalo_km), int(proxima_km), int(servico_id)))
            con.commit()


# ----------------------------- ScrollFrame util ----------------------------- #


    def buscar_clientes_placas(self, termo: str, limit: int = 100):

        """

        Busca por clientes e seus veículos usando termo em nome, telefone ou placa.

        Retorna: lista de tuplas (cli_id, nome, telefone, marca, modelo, placa, ano, km_atual, vei_id)

        """

        termo = (termo or '').strip()

        pat = f"%{termo}%"

        pat_upper = f"%{(termo or '').strip().upper()}%"

    

        with self._connect() as con:

            cur = con.cursor()

            # LEFT JOIN para também listar clientes sem veículo (placa = NULL)

            cur.execute("""
                SELECT c.id   AS cli_id,

                       c.nome AS nome,

                       c.telefone AS telefone,

                       v.marca, v.modelo, v.placa, v.ano, v.km_atual,

                       v.id    AS vei_id

                FROM clientes c

                LEFT JOIN veiculos v ON v.cliente_id = c.id

                WHERE (? = '' )

                   OR (c.nome     LIKE ?)

                   OR (c.telefone LIKE ?)

                   OR (UPPER(IFNULL(v.placa,'')) LIKE ?)

                ORDER BY c.nome COLLATE NOCASE ASC, v.id DESC

                LIMIT ?

            """, (termo, pat, pat, pat_upper, int(limit)))

            return cur.fetchall()

    

    def get_veiculos_do_cliente(self, cliente_id: int):

        """Opcional: obter todos os veículos de um cliente (ordem: mais recentes primeiro)."""

        with self._connect() as con:

            cur = con.cursor()

            cur.execute("""
                SELECT id, marca, modelo, placa, ano, km_atual

                FROM veiculos

                WHERE cliente_id = ?

                ORDER BY id DESC

            """, (int(cliente_id),))

            return cur.fetchall()


    def estoque_baixa(self, nome_item: str, qtde: int, categoria: str | None = None):
        """Dá baixa de `qtde` unidades no estoque; retorna (ok, disponivel_antes).
        Matching robusto:
          1) match exato normalizado
          2) prefixo/contains
          3) *token match* (todas as palavras do pedido existem no item do estoque,
             considerando singular/plural simples)
          4) fallback global se categoria falhar
        """
        try:
            qtde = int(qtde)
        except Exception:
            qtde = 0
        nome_item = (nome_item or '').strip()
        categoria = (categoria or '').strip() or None
        if not nome_item or qtde <= 0:
            return False, 0

        def _norm(s: str) -> str:
            try:
                import unicodedata, re as _re
                s = (s or '').strip().lower()
                s = ''.join(ch for ch in unicodedata.normalize('NFKD', s) if not unicodedata.combining(ch))
                s = _re.sub(r'[^a-z0-9]+', ' ', s)
                return ' '.join(s.split())
            except Exception:
                return (s or '').strip().lower()

        def _tokens(s: str):
            toks = [t for t in _norm(s).split() if t]
            sg = [t[:-1] if len(t) > 3 and t.endswith('s') else t for t in toks]
            stop = {'de','do','da','dos','das','para','e','ou'}
            return [t for t in sg if t not in stop]

        key = _norm(nome_item)
        key_tokens = _tokens(nome_item)

        import sqlite3
        with self._connect() as con:
            cur = con.cursor()

            def _pick_row(rows):
                # 1) exact normalized match
                for r in rows:
                    if _norm(r[1]) == key:
                        return r
                # 2) startswith/contains
                for r in rows:
                    norm = _norm(r[1])
                    if norm.startswith(key) or key in norm:
                        return r
                # 3) token subset (todas palavras do pedido existem no item do estoque)
                for r in rows:
                    cand_tokens = set(_tokens(r[1]))
                    if key_tokens and set(key_tokens).issubset(cand_tokens):
                        return r
                # 3b) inverso: todas as palavras do estoque existem no pedido
                for r in rows:
                    cand_tokens = set(_tokens(r[1]))
                    if cand_tokens and cand_tokens.issubset(set(key_tokens)):
                        return r
                return None

            # Busca por categoria (se houver)
            if categoria:
                cur.execute("SELECT id, item, qtde FROM estoque WHERE categoria = ?", (categoria,))
            else:
                cur.execute("SELECT id, item, qtde FROM estoque")
            rows = cur.fetchall() or []

            cand = _pick_row(rows)

            # Fallback global caso não encontre na categoria
            if not cand and categoria:
                cur.execute("SELECT id, item, qtde FROM estoque")
                rows = cur.fetchall() or []
                cand = _pick_row(rows)

            if not cand:
                return False, 0

            rid, _item, atual = int(cand[0]), cand[1], int(cand[2] or 0)
            if atual < qtde:
                return False, atual

            novo = atual - qtde
            cur.execute("UPDATE estoque SET qtde = ? WHERE id = ?", (novo, rid))
            con.commit()
            try:
                print(f"[Estoque] BAIXA: '{_item}' -{qtde} (antes={atual} -> depois={novo}) cat={categoria}")
            except Exception:
                pass
            return True, atual

    def estoque_repor(self, nome_item: str, qtde: int, categoria: str | None = None):
        """Repõe `qtde` unidades ao item no estoque (se existir). Usa a mesma lógica de matching da baixa."""
        try:
            qtde = int(qtde)
        except Exception:
            qtde = 0
        nome_item = (nome_item or '').strip()
        categoria = (categoria or '').strip() or None
        if not nome_item or qtde <= 0:
            return False

        def _norm(s: str) -> str:
            try:
                import unicodedata, re as _re
                s = (s or '').strip().lower()
                s = ''.join(ch for ch in unicodedata.normalize('NFKD', s) if not unicodedata.combining(ch))
                s = _re.sub(r'[^a-z0-9]+', ' ', s)
                return ' '.join(s.split())
            except Exception:
                return (s or '').strip().lower()

        def _tokens(s: str):
            toks = [t for t in _norm(s).split() if t]
            sg = [t[:-1] if len(t) > 3 and t.endswith('s') else t for t in toks]
            stop = {'de','do','da','dos','das','para','e','ou'}
            return [t for t in sg if t not in stop]

        key = _norm(nome_item)
        key_tokens = _tokens(nome_item)

        with self._connect() as con:
            cur = con.cursor()

            def _pick_row(rows):
                for r in rows:
                    if _norm(r[1]) == key:
                        return r
                for r in rows:
                    norm = _norm(r[1])
                    if norm.startswith(key) or key in norm:
                        return r
                for r in rows:
                    cand_tokens = set(_tokens(r[1]))
                    if key_tokens and set(key_tokens).issubset(cand_tokens):
                        return r
                for r in rows:
                    cand_tokens = set(_tokens(r[1]))
                    if cand_tokens and cand_tokens.issubset(set(key_tokens)):
                        return r
                return None

            if categoria:
                cur.execute("SELECT id, item, qtde FROM estoque WHERE categoria = ?", (categoria,))
            else:
                cur.execute("SELECT id, item, qtde FROM estoque")
            rows = cur.fetchall() or []
            cand = _pick_row(rows)
            if not cand and categoria:
                cur.execute("SELECT id, item, qtde FROM estoque")
                rows = cur.fetchall() or []
                cand = _pick_row(rows)
            if not cand:
                return False

            rid, _item, atual = int(cand[0]), cand[1], int(cand[2] or 0)
            novo = max(0, atual + qtde)
            cur.execute("UPDATE estoque SET qtde = ? WHERE id = ?", (novo, rid))
            con.commit()
            try:
                print(f"[Estoque] REPOR: '{_item}' +{qtde} (antes={atual} -> depois={novo}) cat={categoria}")
            except Exception:
                pass
            return True
class ScrollFrame(ttk.Frame):
    """
    Frame rolável universal (Canvas + Scrollbar).
    Uso:
        sf = ScrollFrame(parent, bg='#f6f7fb', xscroll=False)
        sf.pack(fill='both', expand=True)
        inner = sf.body   # use 'inner' como container do seu layout
    """
    def __init__(self, parent, bg='#ffffff', xscroll=False, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self._bg = bg
        self._xscroll = bool(xscroll)

        self.canvas = tk.Canvas(self, borderwidth=0, highlightthickness=0, background=bg)
        self.canvas.configure(yscrollcommand=None)

        if self._xscroll:
            self.canvas.configure(xscrollcommand=None)
        else:
            self.hsb = None

        self.canvas.pack(side="left", fill="both", expand=True)

        # corpo interno
        self.body = ttk.Frame(self.canvas)
        self.body_id = self.canvas.create_window((0, 0), window=self.body, anchor="nw")

        # Atualiza scrollregion conforme conteúdo cresce
        def _on_configure(_e=None):
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
            # manter largura do body igual à largura visível do canvas (sem interferir no xscroll)
            # apenas se não houver xscroll, expandimos a largura automaticamente
            if not self._xscroll:
                try:
                    cw = self.canvas.winfo_width()
                    self.canvas.itemconfigure(self.body_id, width=cw)
                except Exception:
                    pass

        self.body.bind("<Configure>", _on_configure)

        # Ajusta altura/largura quando o canvas for redimensionado
        def _on_canvas_configure(e):
            if not self._xscroll:
                self.canvas.itemconfigure(self.body_id, width=e.width)

        self.canvas.bind("<Configure>", _on_canvas_configure)

        # Mouse wheel (vertical) e Shift+wheel (horizontal)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)      # Windows/Mac
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)        # Linux
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)        # Linux
        self.canvas.bind_all("<Shift-MouseWheel>", self._on_mousewheel_h)

        # bg do body
        try:
            self.body.configure(style='TFrame')
        except Exception:
            pass
        try:
            self.body.configure(background=bg)
        except Exception:
            pass

    def _on_mousewheel(self, event):
        # Windows/Mac: event.delta (+120/-120)
        if getattr(event, "delta", 0):
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        else:
            # Linux: Button-4/5
            if getattr(event, "num", None) == 4:
                self.canvas.yview_scroll(-3, "units")
            elif getattr(event, "num", None) == 5:
                self.canvas.yview_scroll(3, "units")

    def _on_mousewheel_h(self, event):
        if not self._xscroll:
            return
        # Shift + rodinha -> horizontal
        if getattr(event, "delta", 0):
            step = -1 if event.delta > 0 else 1
            self.canvas.xview_scroll(step, "units")
        else:
            # fallback linux não usual
            self.canvas.xview_scroll(1 if getattr(event, "num", 0)==5 else -1, "units")

    def _bind_mousewheel(self, event):
        # mantido por compatibilidade com versões anteriores
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)

    def _unbind_mousewheel(self, event):
        self.canvas.unbind_all("<MouseWheel>")
        self.canvas.unbind_all("<Button-4>")
        self.canvas.unbind_all("<Button-5>")
        self.canvas.unbind_all("<Shift-MouseWheel>")

# ----------------------------- APP UI ----------------------------- #
    def estoque_get_qtde(self, nome_item: str, categoria: str | None = None) -> int:
        """Retorna a quantidade disponível do item no estoque (0 se não existir)."""
        nome_item = (nome_item or '').strip()
        categoria = (categoria or '').strip() or None
        if not nome_item:
            return 0
        with self._connect() as con:
            cur = con.cursor()
            cur.execute(
                "SELECT qtde FROM estoque WHERE (item = ? OR LOWER(item) = LOWER(?)) AND (? IS NULL OR categoria = ?) LIMIT 1",
                (nome_item, nome_item, categoria, categoria),
            )
            row = cur.fetchone()
            try:
                return int(row[0]) if row else 0
            except Exception:
                return 0

    def estoque_baixa(self, nome_item: str, qtde: int, categoria: str | None = None):
        """Dá baixa de `qtde` unidades no estoque; retorna (ok, disponivel_antes).
        Matching robusto:
          1) match exato normalizado
          2) prefixo/contains
          3) *token match* (todas as palavras do pedido existem no item do estoque,
             considerando singular/plural simples)
          4) fallback global se categoria falhar
        """
        try:
            qtde = int(qtde)
        except Exception:
            qtde = 0
        nome_item = (nome_item or '').strip()
        categoria = (categoria or '').strip() or None
        if not nome_item or qtde <= 0:
            return False, 0

        def _norm(s: str) -> str:
            try:
                import unicodedata, re as _re
                s = (s or '').strip().lower()
                s = ''.join(ch for ch in unicodedata.normalize('NFKD', s) if not unicodedata.combining(ch))
                s = _re.sub(r'[^a-z0-9]+', ' ', s)
                return ' '.join(s.split())
            except Exception:
                return (s or '').strip().lower()

        def _tokens(s: str):
            toks = [t for t in _norm(s).split() if t]
            # singularização simples: remove 's' final de palavras > 3 letras
            sg = [t[:-1] if len(t) > 3 and t.endswith('s') else t for t in toks]
            # remove stopwords comuns
            stop = {'de','do','da','dos','das','para','e','ou'}
            return [t for t in sg if t not in stop]

        key = _norm(nome_item)
        key_tokens = _tokens(nome_item)

        import sqlite3
        with self._connect() as con:
            cur = con.cursor()

            def _pick_row(rows):
                # 1) exact normalized match
                for r in rows:
                    if _norm(r[1]) == key:
                        return r
                # 2) startswith/contains
                for r in rows:
                    norm = _norm(r[1])
                    if norm.startswith(key) or key in norm:
                        return r
                # 3) token subset (todas palavras do pedido existem no item do estoque)
                for r in rows:
                    cand_tokens = set(_tokens(r[1]))
                    if key_tokens and set(key_tokens).issubset(cand_tokens):
                        return r
                # 3b) inverso: todas as palavras do estoque existem no pedido (útil para nomes longos)
                for r in rows:
                    cand_tokens = set(_tokens(r[1]))
                    if cand_tokens and cand_tokens.issubset(set(key_tokens)):
                        return r
                return None

            # Busca por categoria (se houver)
            if categoria:
                cur.execute("SELECT id, item, qtde FROM estoque WHERE categoria = ?", (categoria,))
            else:
                cur.execute("SELECT id, item, qtde FROM estoque")
            rows = cur.fetchall() or []

            cand = _pick_row(rows)

            # Fallback global caso não encontre na categoria
            if not cand and categoria:
                cur.execute("SELECT id, item, qtde FROM estoque")
                rows = cur.fetchall() or []
                cand = _pick_row(rows)

            if not cand:
                return False, 0

            rid, _item, atual = int(cand[0]), cand[1], int(cand[2] or 0)
            if atual < qtde:
                return False, atual

            novo = atual - qtde
            cur.execute("UPDATE estoque SET qtde = ? WHERE id = ?", (novo, rid))
            con.commit()
            try:
                print(f"[Estoque] BAIXA: '{_item}' -{qtde} (antes={atual} -> depois={novo}) cat={categoria}")
            except Exception:
                pass
            return True, atual

    def estoque_repor(self, nome_item: str, qtde: int, categoria: str | None = None):
        """Repõe `qtde` unidades ao item no estoque (se existir). Usa a mesma lógica de matching da baixa."""
        try:
            qtde = int(qtde)
        except Exception:
            qtde = 0
        nome_item = (nome_item or '').strip()
        categoria = (categoria or '').strip() or None
        if not nome_item or qtde <= 0:
            return False

        def _norm(s: str) -> str:
            try:
                import unicodedata, re as _re
                s = (s or '').strip().lower()
                s = ''.join(ch for ch in unicodedata.normalize('NFKD', s) if not unicodedata.combining(ch))
                s = _re.sub(r'[^a-z0-9]+', ' ', s)
                return ' '.join(s.split())
            except Exception:
                return (s or '').strip().lower()

        def _tokens(s: str):
            toks = [t for t in _norm(s).split() if t]
            sg = [t[:-1] if len(t) > 3 and t.endswith('s') else t for t in toks]
            stop = {'de','do','da','dos','das','para','e','ou'}
            return [t for t in sg if t not in stop]

        key = _norm(nome_item)
        key_tokens = _tokens(nome_item)

        with self._connect() as con:
            cur = con.cursor()

            def _pick_row(rows):
                for r in rows:
                    if _norm(r[1]) == key:
                        return r
                for r in rows:
                    norm = _norm(r[1])
                    if norm.startswith(key) or key in norm:
                        return r
                for r in rows:
                    cand_tokens = set(_tokens(r[1]))
                    if key_tokens and set(key_tokens).issubset(cand_tokens):
                        return r
                for r in rows:
                    cand_tokens = set(_tokens(r[1]))
                    if cand_tokens and cand_tokens.issubset(set(key_tokens)):
                        return r
                return None

            if categoria:
                cur.execute("SELECT id, item, qtde FROM estoque WHERE categoria = ?", (categoria,))
            else:
                cur.execute("SELECT id, item, qtde FROM estoque")
            rows = cur.fetchall() or []
            cand = _pick_row(rows)
            if not cand and categoria:
                cur.execute("SELECT id, item, qtde FROM estoque")
                rows = cur.fetchall() or []
                cand = _pick_row(rows)
            if not cand:
                return False

            rid, _item, atual = int(cand[0]), cand[1], int(cand[2] or 0)
            novo = max(0, atual + qtde)
            cur.execute("UPDATE estoque SET qtde = ? WHERE id = ?", (novo, rid))
            con.commit()
            try:
                print(f"[Estoque] REPOR: '{_item}' +{qtde} (antes={atual} -> depois={novo}) cat={categoria}")
            except Exception:
                pass
            return True



class App(tk.Tk):
    def __init__(self):
        super().__init__()
        init_ttkbootstrap_min(self)
        apply_modern_styles(self)
        self.title(APP_TITLE)
        self.geometry("1280x800")
        self.minsize(1120, 700)
        self.fullscreen = False
        # Modo edição de OS
        self.editando_servico_id = None
        try:
            self.var_edit_badge = tk.StringVar(value="")
        except Exception:
            self.var_edit_badge = None

        # Paleta — Pro Light 2025
        self.palette = {
            'bg': '#f6f7fb',
            'card': '#ffffff',
            'border': '#e5e7eb',
            'muted': '#64748b',
            'fg': '#0f172a',
            'accent': '#2563eb',        # blue-600
            'accent_hover': '#1d4ed8',  # blue-700
            'danger': '#ef4444',
            'danger_hover': '#dc2626',
            'entry_bg': '#ffffff',
            'table_bg': '#ffffff',
            'table_even': '#ffffff',
            'table_odd': '#f8fafc',
            'table_sel': '#dbeafe',     # blue-100
            'heading_bg': '#f1f5f9',
        }
        self.configure(bg=self.palette['bg'])

        # Tipografia base dinâmica por plataforma
        self._setup_fonts()

        
        # Preferências (geometria/estado)
        try:
            self._load_prefs()
            self.protocol("WM_DELETE_WINDOW", self._on_close)
        except Exception:
            pass
        self.db = Database(DB_PATH)
        self.itens_pendentes: List[Dict[str, Any]] = []
        self.puxar_preco_var = tk.BooleanVar(value=True)
        self._build_style()
        self._bind_shortcuts()
        self._build_ui()

    def _setup_fonts(self):
        families = set(tkfont.families())
        prefer = [
            'Segoe UI Variable', 'Segoe UI',  # Windows
            'SF Pro Text', 'SF Pro Display',  # macOS
            'Inter', 'Roboto', 'Helvetica Neue', 'Arial'  # cross-platform
        ]
        chosen = None
        for f in prefer:
            if f in families:
                chosen = f; break
        if not chosen:
            chosen = tkfont.nametofont('TkDefaultFont').actual('family')

        # Tamanhos
        base_size = 12
        if sys.platform.startswith('darwin'):
            base_size = 13

        # Aplica nos tk named fonts
        tkfont.nametofont('TkDefaultFont').configure(family=chosen, size=base_size)
        tkfont.nametofont('TkTextFont').configure(family=chosen, size=base_size)
        tkfont.nametofont('TkHeadingFont').configure(family=chosen, size=base_size+4, weight='bold')
        tkfont.nametofont('TkMenuFont').configure(family=chosen, size=base_size)

        self.font_family = chosen
        self.font_base = base_size

    # ---- Style ---- #
    def _build_style(self):
        style = ttk.Style(self)
        try:
            style.theme_use('clam')
        except Exception:
            pass
        P = self.palette

        # Frames e cartões
        style.configure('TFrame', background=P['bg'])
        style.configure('Card.TFrame', background=P['card'])
        style.configure('TLabelframe', background=P['card'], borderwidth=1, relief='solid')
        style.configure('TLabelframe.Label', background=P['card'], foreground=P['fg'], font=(self.font_family, self.font_base, 'bold'))

        # Títulos
        style.configure('Title.TLabel', font=(self.font_family, self.font_base+8, 'bold'), foreground=P['fg'], background=P['bg'])
        style.configure('H1.TLabel', font=(self.font_family, self.font_base+6, 'bold'), foreground=P['fg'], background=P['bg'])
        style.configure('H2.TLabel', font=(self.font_family, self.font_base+2, 'bold'), foreground=P['fg'], background=P['bg'])
        style.configure('TLabel', foreground=P['fg'], background=P['bg'])

        # Inputs
        style.configure('TEntry', fieldbackground=P['entry_bg'])
        style.map('TEntry',
                  fieldbackground=[('disabled', '#f3f4f6'), ('!disabled', P['entry_bg'])])
        style.configure('TCombobox', fieldbackground=P['entry_bg'])
        style.map('TCombobox',
                  fieldbackground=[('readonly', P['entry_bg'])])
        # Badges para status de manutenção
        style.configure('Badge.Ok.TLabel', background='#16a34a', foreground='#ffffff', padding=(10, 4))
        style.configure('Badge.Warn.TLabel', background='#dc2626', foreground='#ffffff', padding=(10, 4))

        # Botões
        btn_padding = (16, 10)
        style.configure('TButton', padding=btn_padding, relief='flat', borderwidth=0, focusthickness=0)
        style.configure('Primary.TButton', font=(self.font_family, self.font_base, 'bold'), foreground='#ffffff', background=P['accent'])
        style.map('Primary.TButton',
            background=[('active', P['accent_hover']), ('pressed', P['accent_hover']), ('!disabled', P['accent'])],
            foreground=[('!disabled', '#ffffff')])
        style.configure('Ghost.TButton', font=(self.font_family, self.font_base), foreground=P['accent'], background=P['bg'], bordercolor=P['border'])
        style.map('Ghost.TButton',
            foreground=[('active', P['accent_hover']), ('!disabled', P['accent'])],
            background=[('active', P['card']), ('!disabled', P['bg'])])
        style.configure('Danger.TButton', font=(self.font_family, self.font_base, 'bold'), foreground='#ffffff', background=P['danger'])
        style.map('Danger.TButton',
            background=[('active', P['danger_hover']), ('pressed', P['danger_hover']), ('!disabled', P['danger'])],
            foreground=[('!disabled', '#ffffff')])

        # Notebook (abas)
        style.configure('TNotebook', background=P['bg'], borderwidth=0)
        style.configure('TNotebook.Tab', padding=(20, 12), font=(self.font_family, self.font_base, 'bold'), background=P['bg'], foreground=P['muted'])
        style.map('TNotebook.Tab',
                  background=[('selected', P['card'])],
                  foreground=[('selected', P['fg']), ('!selected', P['muted'])])

        # Treeview (tabelas)
        style.configure('Treeview',
                        background=P['table_bg'],
                        fieldbackground=P['table_bg'],
                        foreground=P['fg'],
                        rowheight=30, borderwidth=0, relief='flat', font=(self.font_family, self.font_base))
        style.configure('Treeview.Heading',
                        font=(self.font_family, self.font_base-1, 'bold'),
                        background=P['heading_bg'], foreground=P['fg'],
                        relief='flat')
        style.map('Treeview', background=[('selected', P['table_sel'])])

    # ---- Atalhos ---- #
        # ===== Modern touches =====
        # Buttons
        style.configure('Primary.TButton', padding=(14, 8), relief='flat',
                        background=self.palette['accent'], foreground='#ffffff')
        style.map('Primary.TButton',
                  background=[('active', self.palette['accent_hover'])],
                  relief=[('pressed', 'sunken')])

        style.configure('Ghost.TButton', padding=(12, 6), relief='flat',
                        background=self.palette['card'], foreground=self.palette['fg'])
        style.map('Ghost.TButton', background=[('active', '#eef2ff')])

        # Entry focus styling
        try:
            style.map('TEntry',
                      fieldbackground=[('focus', '#ffffff'), ('!focus', '#f8fafc')],
                      bordercolor=[('focus', self.palette['accent']), ('!focus', self.palette['border'])])
        except Exception:
            pass

        # Treeview modern look
        style.configure('Treeview',
                        background=self.palette['table_bg'],
                        fieldbackground=self.palette['table_bg'],
                        bordercolor=self.palette['border'],
                        rowheight=28)
        style.configure('Treeview.Heading',
                        background=self.palette['heading_bg'],
                        font=(self.font_family, self.font_base, 'bold'))

    def _bind_shortcuts(self):
        self.bind('<F11>', lambda e: self.toggle_fullscreen())
        self.bind('<Escape>', lambda e: self.exit_fullscreen())
        self.bind('<Control-s>', lambda e: self._salvar())
        self.bind('<Control-f>', lambda e: (self.nb.select(self.tab_busca), self.ent_busca.focus_set()))

    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        self.attributes('-fullscreen', self.fullscreen)

    def exit_fullscreen(self):
        self.fullscreen = False
        self.attributes('-fullscreen', False)

    # ---- UI ---- #
        # Modern k
    def toast(self, msg, ms=1800):
        top = tk.Toplevel(self)
        top.overrideredirect(True)
        top.configure(bg='#111827')
        lbl = tk.Label(top, text=msg, fg='#ffffff', bg='#111827',
                       font=(self.font_family, self.font_base))
        lbl.pack(ipadx=14, ipady=10)
        top.update_idletasks()
        w = top.winfo_width(); h = top.winfo_height()
        x = self.winfo_rootx() + self.winfo_width() - w - 24
        y = self.winfo_rooty() + self.winfo_height() - h - 24
        top.geometry(f'{w}x{h}+{x}+{y}')
        top.attributes('-alpha', 0.0)
        def _fade_in(a=0.0):
            if a >= 0.96: return
            top.attributes('-alpha', a); top.after(16, lambda: _fade_in(a+0.08))
        _fade_in()
        def _fade_out(a=0.96):
            if a <= 0.0: top.destroy(); return
            top.attributes('-alpha', a); top.after(16, lambda: _fade_out(a-0.08))
        top.after(ms, _fade_out)

    def _show_help(self):
        try:
            from tkinter import messagebox
            msg = (
                "Atalhos:\n"
                "Ctrl+S  Salvar cadastro\n"
                "Ctrl+F  Ir para busca\n"
                "F1      Ajuda rápida\n"
            )
            messagebox.showinfo("Ajuda", msg, parent=self)
        except Exception:
            pass

    def _focus_busca(self):
        # tenta focar um campo de busca conhecido
        for name in ['ent_busca', 'ent_busca_nome', 'ent_busca_placa']:
            w = getattr(self, name, None)
            if w:
                try:
                    w.focus_set()
                    return
                except Exception:
                    pass
        # fallback: seleciona a aba de busca se existir
        try:
            self.nb.select(self.tab_busca)
        except Exception:
            pass

    def _load_prefs(self):
        import json, os
        self._prefs_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'prefs.json')
        try:
            with open(self._prefs_file, 'r', encoding='utf-8') as f:
                p = json.load(f)
            if 'geometry' in p: 
                try: self.geometry(p['geometry'])
                except Exception: pass
            if p.get('fullscreen'):
                try: self.attributes('-fullscreen', True)
                except Exception: pass
        except Exception:
            pass

    def _on_close(self):
        import json
        prefs = {'geometry': self.geometry()}
        try:
            prefs['fullscreen'] = bool(self.attributes('-fullscreen'))
        except Exception:
            prefs['fullscreen'] = False
        try:
            with open(self._prefs_file, 'w', encoding='utf-8') as f:
                json.dump(prefs, f)
        except Exception:
            pass
        self.destroy()
        # Modern keyboard shortcuts
        try:
            self.bind_all('<Control-s>', lambda e: getattr(self, '_salvar', lambda: None)())
        except Exception:
            pass
        try:
            self.bind_all('<Control-f>', lambda e: self._focus_busca())
        except Exception:
            pass
        try:
            self.bind_all('<F1>', lambda e: self._show_help())
        except Exception:
            pass

    def _build_ui(self):
        topbar = tk.Frame(self, bg=self.palette['card'], height=64)
        topbar.pack(fill='x', side='top')
        right = tk.Frame(topbar, bg=self.palette['card'])
        right.pack(side='right', padx=12)
        ttk.Button(right, text='Nova OS', style='Primary.TButton', command=getattr(self, '_abrir_os_rapida', lambda: None)).pack(side='left', padx=(0,8), pady=8)
        ttk.Button(right, text='Relatórios', style='Ghost.TButton', command=lambda: self.nb.select(self.tab_rel) if hasattr(self,'tab_rel') else None).pack(side='left', pady=8)
        left = tk.Frame(topbar, bg=self.palette['card'])
        left.pack(side='left', padx=12)
        right = tk.Frame(topbar, bg=self.palette['card'])
        right.pack(side='right', padx=12)
        # Logo no cabeçalho
        self.logo_header_img = None
        try:
            from PIL import Image, ImageTk
            import os
            _logo_path = os.path.join(ASSETS_DIR, 'logo_watermark_nobg.png')
            if os.path.exists(_logo_path):
                _img = Image.open(_logo_path).convert('RGBA')
                target_h = 36
                scale = target_h / max(1, _img.height)
                _img = _img.resize((max(1, int(_img.width*scale)), target_h), Image.LANCZOS)
                self.logo_header_img = ImageTk.PhotoImage(_img)
        except Exception as _e:
            print('[header-logo] aviso:', _e)
        if self.logo_header_img:
            tk.Label(left, image=self.logo_header_img, bg=self.palette['card']).pack(side='left', padx=(6,10), pady=6)
        title_lbl = tk.Label(left, text='MECÂNICA DO JAIRO', bg=self.palette['card'], fg=self.palette['fg'],
                 font=(self.font_family, self.font_base+6, 'bold'))
        title_lbl.pack(anchor='w')
        tk.Label(left, text='Sistema de ordens, cadastro e estoque', bg=self.palette['card'], fg=self.palette['muted'], font=(self.font_family, self.font_base)).pack(anchor='w')
        tk.Label(topbar, text='Pro Light 2025 — FIX',  bg=self.palette['card'], fg=self.palette['muted'],
                 font=(self.font_family, self.font_base)).pack(side='left')
        tk.Frame(self, bg=self.palette['border'], height=1).pack(fill='x', side='top')

        self.nb = ttk.Notebook(self)
        self.nb.pack(fill='both', expand=True, padx=8, pady=8)

        self.tab_home = ttk.Frame(self.nb, style='TFrame')
        self.tab_cadastro = ttk.Frame(self.nb, style='TFrame')
        self.tab_busca = ttk.Frame(self.nb, style='TFrame')
        self.tab_estoque = ttk.Frame(self.nb, style='TFrame')
        self.tab_rel = ttk.Frame(self.nb, style='TFrame')

        self.nb.add(self.tab_home, text='🏠 Início')
        self.nb.add(self.tab_cadastro, text='✍️ Cadastro')
        # Ajusta largura quando a aba Cadastro estiver ativa
        self.nb.bind("<<NotebookTabChanged>>", self._on_tab_changed)
        # Força ajuste já na abertura
        try:
            self.after(50, self._on_tab_changed)
        except Exception:
            pass
        self.nb.add(self.tab_busca, text='🔎 Busca')
        self.nb.add(self.tab_estoque, text='📦 Estoque')
        self.nb.add(self.tab_rel, text='📈 Relatórios')

        self._build_home(self.tab_home)
        self._build_cadastro(self.tab_cadastro)   # <-- agora com ScrollFrame
        self._build_busca(self.tab_busca)
        self._build_estoque(self.tab_estoque)
        self._build_rel(self.tab_rel)
        # --- Botão flutuante para Editar OS (fica no topo à direita)
        try:
            btn_editar_os = ttk.Button(topbar, text='Editar OS', command=lambda: BuscarEditarOS(self, self.db))
            btn_editar_os.pack(side='right', padx=8, pady=6)
        except Exception as _e:
            print('[ui] aviso ao criar botão Editar OS:', _e)


    def _card(self, parent, emoji: str, title: str, subtitle: str, on_click, bg_color=None, hover_bg=None, border_color=None):
        # Wrapper visível do card (usa o estilo Card.TFrame do seu tema)
        wrap = ttk.Frame(parent, style='Card.TFrame')
        # Garante que o card ocupe o espaço
        wrap.pack(expand=True, fill='both')
    
        # Sombra leve
        shadow = tk.Frame(wrap, bg="#e2e8f0", bd=0, highlightthickness=0)
        shadow.place(relx=0, rely=0, relwidth=1, relheight=1, x=3, y=4)
    
        # Cores
        _base = bg_color if bg_color else self.palette['card']
        _hov  = hover_bg if hover_bg else '#f8fafc'
        _bdr  = border_color if border_color else self.palette['border']
    
        # Card principal
        card = tk.Frame(wrap, bg=_base, bd=0, highlightthickness=1, highlightbackground=_bdr)
        card.place(relx=0, rely=0, relwidth=1, relheight=1)
    
        # Conteúdo
        icon_lbl = tk.Label(card, text=emoji, font=("Segoe UI Emoji", self.font_base+18),
                            bg=_base, fg=self.palette['fg'])
        icon_lbl.pack(padx=18, pady=(20, 6), anchor='w')
    
        title_lbl = tk.Label(card, text=title, font=(self.font_family, self.font_base+3, 'bold'),
                             bg=_base, fg=self.palette['fg'])
        title_lbl.pack(padx=18, anchor='w')
    
        sub_lbl = tk.Label(card, text=subtitle, font=(self.font_family, self.font_base),
                           bg=_base, fg=self.palette['muted'])
        sub_lbl.pack(padx=18, pady=(4,20), anchor='w')
    
        # Hover effect
        def _hover(_e=None):
            for w in (card, icon_lbl, title_lbl, sub_lbl):
                w.configure(bg=_hov)
        def _leave(_e=None):
            for w in (card, icon_lbl, title_lbl, sub_lbl):
                w.configure(bg=_base)
    
        def _press(_e=None):
            try:
                on_click()
            except Exception as e:
                print("[home] click error:", e)
    
        for w in (card, icon_lbl, title_lbl, sub_lbl):
            w.bind("<Enter>", _hover)
            w.bind("<Leave>", _leave)
            w.bind("<Button-1>", _press)
            w.configure(cursor="hand2")
    
        return wrap

    # ---- Tabs ---- #


    def _build_home(self, parent):
        import tkinter as tk, tkinter.ttk as ttk

        # Limpa
        for ch in list(parent.winfo_children()):
            ch.destroy()

        root = ttk.Frame(parent, style='TFrame')
        root.pack(fill='both', expand=True)

        # Canvas de fundo ocupa toda a Home
        try:
            from PIL import Image, ImageTk, ImageDraw
        except Exception:
            Image = ImageTk = ImageDraw = None

        c = tk.Canvas(root, bd=0, highlightthickness=0, relief='flat')
        c.pack(fill='both', expand=True)

        # Carrega imagem (se houver)
        import os, tkinter.font as tkfont
        candidates = [
            os.path.join(ASSETS_DIR, "bg", "oficina.jpg"),
            os.path.join(ASSETS_DIR, "bg", "oficina.png"),
            os.path.join(ASSETS_DIR, "oficina.jpg"),
            os.path.join(ASSETS_DIR, "oficina.png"),
            os.path.join(_app_base_dir(), "oficina.jpg"),
            os.path.join(_app_base_dir(), "oficina.png"),
        ]
        self._home_bg_full_pil = None
        if Image is not None:
            for pth in candidates:
                if os.path.exists(pth):
                    try:
                        self._home_bg_full_pil = Image.open(pth).convert("RGBA")
                        break
                    except Exception as _e:
                        print("[home] erro lendo imagem:", _e)

        # Fontes (Leoscar -> Calibri -> Arial)
        fams = set(f.lower() for f in tkfont.families())
        def pick(*cands):
            for f in cands:
                if f.lower() in fams:
                    return f
            return cands[-1]
        HEAD = pick('Leoscar', 'Calibri', 'Arial')
        BODY = pick('Leoscar', 'Calibri', 'Arial')

        # Definição dos cards (callbacks mantidos)
        cards = [
            ('✍️', 'Cadastro', 'Cadastro de clientes/veículos', lambda: self.nb.select(self.tab_cadastro)),
            ('🔎', 'Buscar', 'Encontre por nome ou placa', lambda: self.nb.select(self.tab_busca)),
            ('📦', 'Estoque', 'Itens, quantidades e preços', lambda: self.nb.select(self.tab_estoque)),
            ('📈', 'Relatórios', 'Visão geral e desempenho', lambda: self.nb.select(self.tab_rel)),
        ]

        # Layout responsivo dos cards
        def layout(w, h):
            margin = 16
            gap = 14
            cols = 2
            hero_pad = 120     # espaço do topo para os textos
            card_h = 200
            cw = max(320, min(500, (w - margin*2 - gap*(cols-1))//cols))
            y0 = 28 + hero_pad
            pos, r, cix = [], 0, 0
            for _ in cards:
                x = margin + cix * (cw + gap)
                y = y0 + r * (card_h + gap)
                pos.append((x, y, cw, card_h))
                cix += 1
                if cix >= cols:
                    cix = 0
                    r += 1
            return pos

        # Contorno arredondado (somente borda, sem fill → não cobre a foto)
        def round_outline(x, y, w, h, r, outline="#e5e7eb", width=1, tags=None):
            items = []
            items.append(c.create_line(x+r, y, x+w-r, y, fill=outline, width=width, tags=tags))
            items.append(c.create_line(x+r, y+h, x+w-r, y+h, fill=outline, width=width, tags=tags))
            items.append(c.create_line(x, y+r, x, y+h-r, fill=outline, width=width, tags=tags))
            items.append(c.create_line(x+w, y+r, x+w, y+h-r, fill=outline, width=width, tags=tags))
            items.append(c.create_arc(x, y, x+2*r, y+2*r, start=90, extent=90, style='arc', outline=outline, width=width, tags=tags))
            items.append(c.create_arc(x+w-2*r, y, x+w, y+2*r, start=0, extent=90, style='arc', outline=outline, width=width, tags=tags))
            items.append(c.create_arc(x, y+h-2*r, x+2*r, y+h, start=180, extent=90, style='arc', outline=outline, width=width, tags=tags))
            items.append(c.create_arc(x+w-2*r, y+h-2*r, x+w, y+h, start=270, extent=90, style='arc', outline=outline, width=width, tags=tags))
            return items

        def draw(_=None):
            c.delete("all")
            w = max(1, c.winfo_width())
            h = max(1, c.winfo_height())

            # Fundo
            if self._home_bg_full_pil is not None and Image is not None and ImageTk is not None:
                img = self._home_bg_full_pil.copy().resize((w, h), Image.LANCZOS)
                try:
                    overlay = Image.new('RGBA', img.size, (0, 0, 0, 160))  # mais escuro
                    img = Image.alpha_composite(img, overlay)
                except Exception:
                    pass
                self._home_bg_full_tk = ImageTk.PhotoImage(img)
                c.create_image(0, 0, anchor='nw', image=self._home_bg_full_tk, tags="bg")
            else:
                c.create_rectangle(0, 0, w, h, outline="", fill="#1f2937", tags="bg")

            # Títulos no topo
            c.create_text(24, 28, anchor='nw', text='🚗 Mecânica do Jairo', fill='#FFFFFF',
                          font=(HEAD, 22, 'bold'), tags="hero")
            c.create_text(24, 70, anchor='nw', text='Início — escolha uma ação para começar', fill='#E5E7EB',
                          font=(BODY, 12), tags="hero")

            # Cards (glass + contorno + textos)
            positions = layout(w, h)
            self._home_glass_imgs = []  # segurar referências
            for idx, (x, y, cw, ch) in enumerate(positions):
                emoji, title, sub, cb = cards[idx]
                tag = f"card{idx}"
                btag = f"{tag}_bdr"
                ttag = f"{tag}_txt"
                gtag = f"{tag}_glass"

                # Glass (se PIL disponível)
                if Image is not None and ImageDraw is not None and ImageTk is not None:
                    glass = Image.new('RGBA', (cw, ch), (255, 255, 255, 0))
                    draw = ImageDraw.Draw(glass, 'RGBA')
                    # preenchimento translúcido + leve contorno
                    draw.rounded_rectangle([0, 0, cw-1, ch-1], radius=18,
                                           fill=(255, 255, 255, 96),  # ~38% opacidade
                                           outline=(255, 255, 255, 160), width=1)
                    glass_tk = ImageTk.PhotoImage(glass)
                    self._home_glass_imgs.append(glass_tk)
                    c.create_image(x, y, anchor='nw', image=glass_tk, tags=(tag, gtag))

                # contorno destacado (somente borda; tag específica de borda)
                round_outline(x, y, cw, ch, r=18, outline="#e5e7eb", width=1, tags=(tag, btag))

                # textos (tag específica de texto)
                c.create_text(x+18, y+26, anchor='nw', text=f"{emoji} {title}", fill='#FFFFFF',
                              font=(HEAD, 16, 'bold'), tags=(tag, ttag))
                c.create_text(x+18, y+58, anchor='nw', text=sub, fill='#E5E7EB',
                              font=(BODY, 12), tags=(tag, ttag))

                # Hover/click: ajusta SOMENTE a borda (nada de width nas strings!)
                c.tag_bind(tag, "<Enter>", lambda e, t=btag: c.itemconfigure(t, width=2))
                c.tag_bind(tag, "<Leave>", lambda e, t=btag: c.itemconfigure(t, width=1))
                c.tag_bind(tag, "<Button-1>", lambda e, fn=cb: fn())
                c.tag_bind(tag, "<Motion>", lambda e: c.configure(cursor="hand2"))

            # Fora dos cards: cursor normal
            c.tag_bind("bg", "<Motion>", lambda e: c.configure(cursor=""))

        c.bind("<Configure>", draw)
        draw()
    def _set_edit_badge(self, sid: int):
        try:
            if hasattr(self, 'var_edit_badge') and self.var_edit_badge is not None:
                self.var_edit_badge.set(f"Editando OS #{sid}")
        except Exception:
            pass

    def _clear_edit_badge(self):
        try:
            if hasattr(self, 'var_edit_badge') and self.var_edit_badge is not None:
                self.var_edit_badge.set("")
        except Exception:
            pass

    def abrir_os_na_cadastro(self, servico_id: int):
        try:
            try:
                self.nb.select(self.tab_cadastro)
            except Exception:
                pass
            row = self.db.get_servico_full(servico_id)
            if not row:
                from tkinter import messagebox
                messagebox.showerror('Erro', 'OS não encontrada.'); return
            (sid, veic_id, descricao, km_atual_s, intervalo, proxima, data,
             cliente_id, marca, modelo, placa, ano, v_km_atual,
             nome, telefone, km_troca_corr, km_corr_trocada, km_corr_proxima) = row
            self.editando_servico_id = servico_id
            self._set_edit_badge(servico_id)
            try:
                self.ent_cli_nome.delete(0,'end'); self.ent_cli_nome.insert(0, nome or '')
                self.ent_cli_tel.delete(0,'end');  self.ent_cli_tel.insert(0, telefone or '')
            except Exception:
                pass
            try:
                self.cmb_marca.set(marca or 'Outros')
                try:
                    self._load_modelos()
                except Exception:
                    pass
                self.cmb_modelo.set(modelo or '')
                self.ent_placa.delete(0,'end'); self.ent_placa.insert(0, (placa or '').upper())
                self.ent_ano.delete(0,'end');   self.ent_ano.insert(0, ano or '')
            except Exception:
                pass
            try:
                km_base = km_atual_s if (km_atual_s is not None) else (v_km_atual or 0)
                self.ent_km_atual.delete(0,'end'); self.ent_km_atual.insert(0, str(km_base))
                try:
                    self.ent_km_troca_corr.delete(0,'end');  self.ent_km_troca_corr.insert(0, str(km_troca_corr or 0))
                    self.ent_km_corr_trocada.delete(0,'end'); self.ent_km_corr_trocada.insert(0, str(km_corr_trocada or 0))
                    self.ent_km_corr_proxima.delete(0,'end'); self.ent_km_corr_proxima.insert(0, str(km_corr_proxima or 0))
                except Exception:
                    pass
                try:
                    self.cmb_intervalo.set(str(intervalo or 10000))
                except Exception:
                    pass
                try:
                    self._atualiza_proxima()
                except Exception:
                    pass
            except Exception:
                pass
            try:
                self.txt_descricao.delete('1.0','end'); self.txt_descricao.insert('1.0', descricao or '')
            except Exception:
                pass
            try:
                itens = self.db.get_itens_servico(servico_id)
                self.itens_pendentes.clear()
                for it in itens:
                    if len(it) >= 5 and isinstance(it[0], int):
                        _, cat, item, qt, vu = it[:5]
                    else:
                        cat, item, qt, vu = it[:4]
                    self.itens_pendentes.append({'categoria': cat or '', 'item': item or '', 'qtde': int(qt or 0), 'valor_unit': float(vu or 0.0)})
                self._refresh_tree_itens()
            except Exception as e:
                print('[itens] aviso:', e)
        except Exception as e:
            from tkinter import messagebox
            messagebox.showerror('Erro', f'Falha ao abrir OS para edição:\n{e}')

    def _build_cadastro(self, parent):
        # ---- ENVOLVE O CONTEÚDO EM UM SCROLLFRAME ---- #
        sframe = ScrollFrame(parent, bg=self.palette['bg'], xscroll=False)
        sframe.pack(fill='both', expand=True)
        container = ttk.Frame(sframe.body, style='TFrame')
        container.pack(fill='both', expand=True)

        pad = dict(padx=2, pady=1)

        # --- Cliente ---
        sec_cli = ttk.LabelFrame(container, text='Cliente', style='TLabelframe')
        sec_cli.pack(fill='x', **pad)
        ttk.Label(sec_cli, text='Nome:').grid(row=0, column=0, sticky='w', **pad)
        self.ent_cli_nome = ttk.Entry(sec_cli, width=25)
        self.ent_cli_nome.grid(row=0, column=1, sticky='w', **pad)
        ttk.Label(sec_cli, text='Telefone:').grid(row=0, column=2, sticky='w', **pad)
        self.ent_cli_tel = ttk.Entry(sec_cli, width=20)
        self.ent_cli_tel.grid(row=0, column=3, sticky='w', **pad)

        # [NOVO] Botão para puxar cadastro existente + atalho F2
        ttk.Button(sec_cli, text='Puxar cadastro (F2)', style='Ghost.TButton',
                   command=self._abrir_picker_cliente)           .grid(row=0, column=4, sticky='w', **pad)
        try:
            self.bind_all('<F2>', lambda e: self._abrir_picker_cliente())
        except Exception:
            pass


        # --- Veículo ---
        sec_vei = ttk.LabelFrame(container, text='Veículo', style='TLabelframe')
        sec_vei.pack(fill='x', **pad)
        marcas = list(BRANDS.keys())
        ttk.Label(sec_vei, text='Marca:').grid(row=0, column=0, sticky='w', **pad)
        self.cmb_marca = ttk.Combobox(sec_vei, values=marcas, state='normal', width=22)
        self.cmb_marca.grid(row=0, column=1, sticky='w', **pad)
        self.cmb_marca.bind('<<ComboboxSelected>>', lambda e: self._load_modelos())
        self.cmb_marca.bind('<FocusOut>', lambda e: self._load_modelos())
        ttk.Label(sec_vei, text='Veículo/Modelo:').grid(row=0, column=2, sticky='w', **pad)
        # [PATCH] Permitir digitação livre do modelo se não estiver na lista
        self.cmb_modelo = ttk.Combobox(sec_vei, values=[], state='normal', width=28)
        self.cmb_modelo.grid(row=0, column=3, sticky='w', **pad)
        ttk.Label(sec_vei, text='Placa:').grid(row=1, column=0, sticky='w', **pad)
        self.ent_placa = ttk.Entry(sec_vei, width=18)
        self.ent_placa.grid(row=1, column=1, sticky='w', **pad)
        ttk.Label(sec_vei, text='Ano:').grid(row=1, column=2, sticky='w', **pad)
        self.ent_ano = ttk.Entry(sec_vei, width=10)
        self.ent_ano.grid(row=1, column=3, sticky='w', **pad)
        ttk.Label(sec_vei, text='KM atual (troca de óleo):').grid(row=2, column=0, sticky='w', **pad)
        self.ent_km_atual = ttk.Entry(sec_vei, width=12)
        self.ent_km_atual.grid(row=2, column=1, sticky='w', **pad)

        
        # [QUICK BLOCK] KM atual — apenas registro, sem afetar cálculos
        try:
            import tkinter as _tk
            if not hasattr(self, 'var_km_visita'):
                self.var_km_visita = _tk.StringVar(value="")
            sec_km_visita = ttk.LabelFrame(container, text='KM atual — apenas registro', style='TLabelframe')
            sec_km_visita.pack(fill='x', **pad)
            ttk.Label(sec_km_visita, text='KM atual:').grid(row=0, column=0, sticky='w', **pad)
            self.ent_km_visita = ttk.Entry(sec_km_visita, width=12, textvariable=self.var_km_visita)
            self.ent_km_visita.grid(row=0, column=1, sticky='w', **pad)
            # Observação para o usuário
            try:
                ttk.Label(sec_km_visita, text='*Somente registro. Não altera próxima troca.', style='Muted.TLabel').grid(row=0, column=2, sticky='w', **pad)
            except Exception:
                pass
        except Exception:
            pass

            sec_km_quick = ttk.LabelFrame(container, text='KM do veículo (atalho)', style='TLabelframe')
            sec_km_quick.pack(fill='x', **pad)
            ttk.Label(sec_km_quick, text='KM atual (troca de óleo):').grid(row=0, column=0, sticky='w', **pad)
            self.ent_km_atual_quick = ttk.Entry(sec_km_quick, width=12, textvariable=self.var_km_atual)
            self.ent_km_atual_quick.grid(row=0, column=1, sticky='w', **pad)

            # Atualiza cálculos quando o valor mudar por aqui também
            try:
                self.ent_km_atual_quick.bind('<KeyRelease>', lambda e: self._atualiza_proxima())
            except Exception:
                pass
            try:
                # Fallback via trace se KeyRelease não disparar por algum motivo
                self.var_km_atual.trace_add('write', lambda *args: self._atualiza_proxima())
            except Exception:
                pass
        except Exception:
            pass

        self.ent_km_atual.bind('<KeyRelease>', lambda e: self._atualiza_proxima())
        ttk.Label(sec_vei, text='Intervalo (km):').grid(row=2, column=2, sticky='w', **pad)
        self.cmb_intervalo = ttk.Combobox(sec_vei, values=['0','1000','5000','7000','10000','15000'], state='readonly', width=12)
        self.cmb_intervalo.set('10000')
        self.cmb_intervalo.grid(row=2, column=3, sticky='w', **pad)
        self.cmb_intervalo.bind('<<ComboboxSelected>>', lambda e: self._atualiza_proxima())
        
        # --- Correia dentada ---
        ttk.Label(sec_vei, text='Intervalo (km) — Correia:').grid(row=3, column=0, sticky='w', **pad)
        self.ent_km_troca_corr = ttk.Entry(sec_vei, width=12)
        self.ent_km_troca_corr.grid(row=3, column=1, sticky='w', **pad)
        self.ent_km_troca_corr.bind('<KeyRelease>', lambda e: self._sync_correia_para_txt_descricao())
        self.ent_km_troca_corr.bind('<FocusOut>', lambda e: self._sync_correia_para_txt_descricao())
        self.ent_km_troca_corr.bind('<KeyRelease>', lambda e: self._atualiza_proxima_correia())
        ttk.Label(sec_vei, text='(ex.: 60000 ou 80000 km)').grid(row=3, column=2, columnspan=2, sticky='w', **pad)

        # --- Correia dentada (histórico e próximas) ---
        ttk.Label(sec_vei, text='KM que foi feita a troca (Correia):').grid(row=4, column=0, sticky='w', **pad)
        self.ent_km_corr_trocada = ttk.Entry(sec_vei, width=12)
        self.ent_km_corr_trocada.grid(row=4, column=1, sticky='w', **pad)
        self.ent_km_corr_trocada.bind('<KeyRelease>', lambda e: self._sync_correia_para_txt_descricao())
        self.ent_km_corr_trocada.bind('<FocusOut>', lambda e: self._sync_correia_para_txt_descricao())
        self.ent_km_corr_trocada.bind('<KeyRelease>', lambda e: self._atualiza_proxima_correia())

        ttk.Label(sec_vei, text='KM da próxima troca (Correia):').grid(row=4, column=2, sticky='w', **pad)
        self.ent_km_corr_proxima = ttk.Entry(sec_vei, width=12)
        self.ent_km_corr_proxima.grid(row=4, column=3, sticky='w', **pad)
        self.ent_km_corr_proxima.bind('<KeyRelease>', lambda e: self._sync_correia_para_txt_descricao())
        self.ent_km_corr_proxima.bind('<FocusOut>', lambda e: self._sync_correia_para_txt_descricao())
        self._atualiza_proxima_correia()
        self.lbl_proxima = ttk.Label(sec_vei, text='Próxima manutenção: — km', style='H2.TLabel')
        self.lbl_proxima.grid(row=5, column=0, columnspan=4, sticky='w', **pad)

        # --- Serviço: Descrição + Itens ---
        sec_srv = ttk.LabelFrame(container, text='Serviço', style='Compact.TLabelframe')
        # ===== Compactação da área de Itens do serviço (V3 ultra) =====
        try:
            import tkinter.ttk as _ttk
            _st = _ttk.Style()
            # Frame mais enxuto
            _st.configure('Compact.TLabelframe', padding=(4, 2))
            # Linhas do grid bem baixinhas e fonte menor
            _fam = getattr(self, 'font_family', 'Segoe UI')
            _base = getattr(self, 'font_base', 10)
            _mini = max(8, _base-2)
            _st.configure('Treeview', rowheight=14, font=(_fam, _mini))
            _st.configure('Treeview.Heading', padding=(1, 0), font=(_fam, _mini, 'bold'))
            # Botões mais compactos (afetando só estilos usados aqui)
            _st.configure('Primary.TButton', padding=(6, 2), font=(_fam, max(8, _base-1)))
            _st.configure('Danger.TButton', padding=(6, 2), font=(_fam, max(8, _base-1)))
            _st.configure('Ghost.TButton', padding=(6, 2), font=(_fam, max(8, _base-1)))
        except Exception as _e:
            pass

        sec_srv.pack(fill='both', expand=True, **pad)
        inner_nb = ttk.Notebook(sec_srv)
        inner_nb.pack(fill='both', expand=True, padx=2, pady=1)

        # Tab: Descrição
        tab_desc = ttk.Frame(inner_nb)
        inner_nb.add(tab_desc, text='Descrição')
        self.txt_descricao = tk.Text(tab_desc, height=4, wrap='word', font=(self.font_family, self.font_base), bg=self.palette['card'], fg=self.palette['fg'])
        self.txt_descricao.pack(fill='both', expand=True, padx=2, pady=1)

        # Tab: Itens do serviço
        tab_itens = ttk.Frame(inner_nb)
        inner_nb.add(tab_itens, text='Itens do serviço')
        linha_sel = ttk.Frame(tab_itens)
        linha_sel.pack(fill='x', padx=2, pady=1)
        ttk.Button(linha_sel, text='Buscar no estoque', command=self._abrir_picker_estoque).pack(side='left', padx=2)
        ttk.Button(linha_sel, text='Adicionar item', style='Primary.TButton', command=self._adicionar_item_card).pack(side='left', padx=8)
        self.lbl_sel = ttk.Label(linha_sel, text='Nenhum item selecionado')
        self.lbl_sel.pack(side='left', padx=8)

        cols = ('categoria', 'item', 'qtde', 'unit', 'total')
        self.tree_itens = ttk.Treeview(tab_itens, columns=cols, show='headings', height=3)
        self.tree_itens.pack(fill='both', expand=True, padx=2, pady=1)
        # --- Mão de obra (inserção rápida) ---
        frm_mo = ttk.Frame(tab_itens)
        frm_mo.pack(fill='x', padx=2, pady=(2,4))
        ttk.Label(frm_mo, text='Mão de obra:').pack(side='left', padx=(0,6))
        self.ent_mo_desc = ttk.Entry(frm_mo, width=32)
        self.ent_mo_desc.pack(side='left')
        ttk.Label(frm_mo, text='Preço (R$):').pack(side='left', padx=(8,6))
        self.ent_mo_preco = ttk.Entry(frm_mo, width=10)
        self.ent_mo_preco.pack(side='left')
        ttk.Button(frm_mo, text='Adicionar', style='Primary.TButton', command=self._add_mao_de_obra).pack(side='left', padx=(10,0))
        for c, label in zip(cols, ['Categoria', 'Item', 'Qtde', 'Unitário (R$)', 'Total (R$)']):
            self.tree_itens.heading(c, text=label)
        self.tree_itens.column('categoria', width=110)
        self.tree_itens.column('item', width=180)
        self.tree_itens.column('qtde', width=60, anchor='center')
        self.tree_itens.column('unit', width=90, anchor='e')
        self.tree_itens.column('total', width=90, anchor='e')
        self._zebra(self.tree_itens)

        botoes_itens = ttk.Frame(tab_itens)
        botoes_itens.pack(fill='x', padx=2, pady=1)
        ttk.Button(botoes_itens, text='Remover selecionado', style='Ghost.TButton', command=self._remover_item_temp).pack(side='left')
        self.lbl_total = ttk.Label(botoes_itens, text='Total: R$ 0,00', style='H2.TLabel')
        self.lbl_total.pack(side='right')

        # ---- AÇÕES (fica no final do conteúdo rolável) ---- #
        actions = ttk.Frame(container, style='TFrame')
        actions.pack(fill='x', pady=2)
        ttk.Button(actions, text='Salvar cadastro + serviço', style='Primary.TButton', command=self._salvar).pack(side='left', padx=6)
        ttk.Button(actions, text='Excluir por placa', style='Danger.TButton', command=self._excluir).pack(side='left', padx=6)
        ttk.Button(actions, text='Limpar', style='Ghost.TButton', command=self._limpar_form).pack(side='left', padx=6)

    def _on_tab_changed(self, event=None):
        """Mantém a aba Cadastro mais larga para caber melhor o formulário."""
        try:
            sel = self.nb.select()
            curr = self.nb.nametowidget(sel)
        except Exception:
            return
        try:
            h = self.winfo_height() if self.winfo_height() > 0 else 800
        except Exception:
            h = 800
        # Larguras padrão e para cadastro
        W_CAD = 1500
        try:
            # Detecta se é a aba cadastro
            if curr is self.tab_cadastro:
                # Só aumenta se estiver menor que o desejado (não força se usuário já maximizou)
                try:
                    w = self.winfo_width()
                except Exception:
                    w = 0
                if w < W_CAD:
                    self.geometry(f"{W_CAD}x{max(700, h)}")
            else:
                # Restaura uma largura padrão confortável (mantém altura)
                try:
                    w = self.winfo_width()
                except Exception:
                    w = 0
                if w > 1280:
                    self.geometry(f"1280x{max(700, h)}")
        except Exception as e:
            print("[UI] on_tab_changed falhou:", e)

    def _load_modelos(self):
        marca = (self.cmb_marca.get() or 'Outros').strip()
        modelos = BRANDS.get(marca, BRANDS.get('Outros', []))
        self.cmb_modelo['values'] = modelos
        # Se o modelo estiver vazio, já sugere a primeira opção.
        # Se o cliente já digitou/selecionou um modelo, não apaga.
        try:
            if modelos and not (self.cmb_modelo.get() or '').strip():
                self.cmb_modelo.set(modelos[0])
        except Exception:
            pass

    def _atualiza_proxima(self):
        km_atual = safe_int(self.ent_km_atual.get())
        intervalo = safe_int(self.cmb_intervalo.get(), default=10000)
        proxima = km_atual + intervalo if km_atual >= 0 and intervalo > 0 else km_atual
        
        if intervalo == 0:
            self.lbl_proxima.config(text=f'Próxima manutenção: (KM atual(troca de óleo)) {km_atual} km')
        else:
            self.lbl_proxima.config(text=f'Próxima manutenção: {proxima if proxima else "—"} km')
        self._injetar_proxima_na_descricao(proxima)

    def _atualiza_proxima_correia(self):
        """Atualiza o campo 'KM da próxima correia' = (KM que foi feita a troca) + (Intervalo km da correia)."""
        try:
            trocada = safe_int(getattr(self, 'ent_km_corr_trocada', None).get() if hasattr(self, 'ent_km_corr_trocada') else 0)
            intervalo_corr = safe_int(getattr(self, 'ent_km_troca_corr', None).get() if hasattr(self, 'ent_km_troca_corr') else 0)
            proxima = trocada + intervalo_corr if trocada >= 0 and intervalo_corr > 0 else 0
            if hasattr(self, 'ent_km_corr_proxima') and self.ent_km_corr_proxima:
                self.ent_km_corr_proxima.delete(0, 'end')
                if proxima > 0:
                    self.ent_km_corr_proxima.insert(0, str(proxima))
                else:
                    self.ent_km_corr_proxima.insert(0, '0')
        except Exception as e:
            # Não interromper a UI por erro de digitação
            pass

    def _injetar_proxima_na_descricao(self, proxima_km: int):
        txt = self.txt_descricao.get('1.0', 'end').strip()
        linhas = [l for l in txt.splitlines() if not l.strip().lower().startswith(('próxima manutenção:', 'próx. manutenção:', 'próxima troca de óleo:', 'proxima troca de oleo:'))]
        if proxima_km > 0:
            linhas.append(f'Próxima troca de óleo: {proxima_km} km')
        novo = "\n".join(linhas).strip()+"\n"
        self.txt_descricao.delete('1.0', 'end'); self.txt_descricao.insert('1.0', novo)

    # ---- Itens temporários ---- #
    def _sync_correia_para_txt_descricao(self):
        """Lê os campos da correia e mantém a linha na aba 'Descrição' (cadastro)."""
        try:
            def _si(x):
                try: return int(str(x).strip())
                except Exception: return 0
            i = _si(getattr(getattr(self,'ent_km_troca_corr',None),'get',lambda:'0')()) if hasattr(self,'ent_km_troca_corr') else 0
            t = _si(getattr(getattr(self,'ent_km_corr_trocada',None),'get',lambda:'0')()) if hasattr(self,'ent_km_corr_trocada') else 0
            p = _si(getattr(getattr(self,'ent_km_corr_proxima',None),'get',lambda:'0')()) if hasattr(self,'ent_km_corr_proxima') else 0
            if not p and i and t:
                p = t + i
                try:
                    self.ent_km_corr_proxima.delete(0, 'end'); self.ent_km_corr_proxima.insert(0, str(p))
                except Exception: pass
            box = getattr(self, 'txt_descricao', None)
            if not box: return
            txt = box.get('1.0', 'end').strip()
            import re as _re
            txt = _re.sub(r'(?im)^\s*Correia dentada\s+—.*$', '', txt).strip()
            nota = f"Correia dentada — Intervalo: {i} km, Trocada em: {t} km, Próxima: {p} km" if (i or t or p) else ''
            if nota:
                txt = (txt + "\n\n" + nota).strip()
            box.delete('1.0', 'end'); box.insert('1.0', (txt+"\n").strip()+"\n")
        except Exception:
            pass

    def _load_catalogo_itens(self, event=None):
        cat = self.cmb_categoria.get()
        self.cmb_item['values'] = CATALOGO.get(cat, [])
        if self.cmb_item['values']:
            self.cmb_item.current(0)
            self._puxar_preco_do_estoque()

    def _abrir_picker_estoque(self):
        import tkinter as tk
        from tkinter import ttk, messagebox

        top = tk.Toplevel(self)
        top.title('Buscar item no estoque — (ESC para sair do fullscreen)')
        try:
            # Abre em fullscreen; ESC fecha
            top.attributes('-fullscreen', True)
            top.bind('<Escape>', lambda e: top.destroy())
        except Exception:
            # Fallback para um tamanho grande
            sw = self.winfo_screenwidth(); sh = self.winfo_screenheight()
            top.geometry(f"{max(1024, int(sw*0.85))}x{max(640, int(sh*0.75))}")
        try:
            top.transient(self); top.grab_set()
        except Exception:
            pass

        pad = dict(padx=8, pady=6)
        try:
            top.transient(self); top.grab_set()
        except Exception:
            pass

        pad = dict(padx=8, pady=6)

        # Barra de busca
        barra = ttk.Frame(top); barra.pack(fill='x', **pad)
        ttk.Label(barra, text='Buscar:').pack(side='left')

        ent = ttk.Entry(barra, width=32); ent.pack(side='left', padx=(8,8))
        ttk.Label(barra, text='em:').pack(side='left', padx=(0,4))
        cmb = ttk.Combobox(barra, values=['Item', 'Categoria'], state='readonly', width=12)
        cmb.current(0); cmb.pack(side='left')

        btn_buscar = ttk.Button(barra, text='Buscar'); btn_buscar.pack(side='left', padx=(8,0))

        # Tabela de resultados
        cols = ('id','item','categoria','qtde','preco')
        tree = ttk.Treeview(top, columns=cols, show='headings', height=12)
        for c, lbl in [('id','ID'),('item','Item'),('categoria','Categoria'),('qtde','Qtde'),('preco','Preço (R$)')]:
            tree.heading(c, text=lbl)
        tree.column('id', width=50, anchor='center')
        tree.column('item', width=240)
        tree.column('categoria', width=140)
        tree.column('qtde', width=60, anchor='e')
        tree.column('preco', width=90, anchor='e')
        tree.pack(fill='both', expand=True, padx=8, pady=4)
        # Quantidade desejada
        frm_qt = ttk.Frame(top); frm_qt.pack(fill='x', padx=8, pady=4)
        ttk.Label(frm_qt, text='Quantidade:').pack(side='left')
        sp_qtde = ttk.Spinbox(frm_qt, from_=1, to=999, width=8)
        sp_qtde.set('1'); sp_qtde.pack(side='left', padx=(6,0))

        def fazer_busca(*_):
            try:
                termo = ent.get().strip()
                col = 'item' if cmb.get().lower().startswith('item') else 'categoria'
                # Limpa
                for iid in tree.get_children():
                    tree.delete(iid)
                if not termo or not hasattr(self, 'db'):
                    return
                # Usa acesso direto ao banco já existente
                with self.db._connect() as con:
                    cur = con.cursor()
                    cur.execute(
                        f"SELECT id, item, categoria, qtde, preco FROM estoque "
                        f"WHERE {col} LIKE ? ORDER BY item ASC LIMIT 200",
                        (f"%{termo}%",)
                    )
                    for rid, item, categoria, qt, preco in cur.fetchall():
                        try:
                            preco_txt = f"{float(preco):.2f}"
                        except Exception:
                            preco_txt = "0.00"
                        tree.insert('', 'end', values=(rid, item, categoria, qt, preco_txt))
            except Exception as e:
                try:
                    messagebox.showerror('Erro', f'Falha ao buscar no estoque:\n{e}', parent=top)
                except Exception:
                    pass

        def usar_sel(*_):
            iid = tree.focus()
            if not iid:
                try:
                    messagebox.showwarning('Atenção', 'Selecione um item.', parent=top)
                except Exception:
                    pass
                return
            rid, item, categoria, qt, preco = tree.item(iid, 'values')
            # Quantidade escolhida no picker
            try:
                qtd = int(sp_qtde.get())
            except Exception:
                qtd = 1
            if qtd < 1:
                qtd = 1
            # Não dá baixa no estoque apenas por selecionar.
            # A baixa acontece somente ao salvar a OS, evitando desconto duplo
            # e evitando perder estoque quando a pessoa seleciona e cancela.
            # Guarda seleção para o botão "Adicionar item"
            try:
                self._sel_item_nome = str(item)
                self._sel_item_categoria = str(categoria)
                self._sel_item_qtde = int(qtd)
                self._sel_item_preco = float(preco) if str(preco).strip() else 0.0
            except Exception:
                pass
            # Atualiza label de seleção no toolbar
            try:
                if getattr(self, 'lbl_sel', None):
                    self.lbl_sel.config(text=f'Selecionado: {item}  x{qtd}  (R$ {float(preco):.2f})')
            except Exception:
                pass
            # Tenta atualizar grade de estoque (se houver)
            try:
                self._refresh_estoque()
            except Exception:
                pass
            try:
                top.destroy()
            except Exception:
                pass

        # Ligações/binds
        btn_buscar.configure(command=fazer_busca)
        ent.bind('<Return>', lambda e: fazer_busca())
        tree.bind('<Double-1>', usar_sel)

        # Barra de ações
        acoes = ttk.Frame(top); acoes.pack(fill='x', padx=8, pady=(0,8))
        ttk.Button(acoes, text='Usar selecionado', command=usar_sel).pack(side='right')
        ttk.Button(acoes, text='Fechar', command=top.destroy).pack(side='right', padx=6)

    def _puxar_preco_do_estoque(self, event=None):
        if not self.puxar_preco_var.get():
            return
        nome = self.ent_item_custom.get().strip() or self.cmb_item.get().strip()
        if not nome:
            return
        preco = self.db.estoque_get_preco(nome)
        if preco is not None:
            self.ent_vl.delete(0, 'end'); self.ent_vl.insert(0, f'{preco:.2f}')


    def _adicionar_item_card(self):
        import tkinter as tk
        from tkinter import ttk, messagebox
        nome_sel = str(getattr(self, '_sel_item_nome', '') or '').strip()
        if not nome_sel:
            try:
                messagebox.showwarning('Atenção', 'Selecione um item no estoque antes de adicionar.')
            except Exception:
                pass
            return
        qtd_sel = int(getattr(self, '_sel_item_qtde', 1) or 1)
        preco_sel = float(getattr(self, '_sel_item_preco', 0.0) or 0.0)
        cat_sel = str(getattr(self, '_sel_item_categoria', 'Outros') or 'Outros')
        top = tk.Toplevel(self)
        top.title('Adicionar item')
        try:
            top.transient(self); top.grab_set()
        except Exception:
            pass
        frm = ttk.Frame(top, padding=12); frm.pack(fill='both', expand=True)
        ttk.Label(frm, text='Editar nome do produto (opcional):').pack(anchor='w')
        ent_nome = ttk.Entry(frm, width=46)
        ent_nome.insert(0, nome_sel)
        ent_nome.pack(fill='x', pady=(6,8))
        ttk.Label(frm, text=f'Quantidade: {qtd_sel}    Valor unit.: R$ {preco_sel:.2f}').pack(anchor='w')
        btns = ttk.Frame(frm); btns.pack(fill='x', pady=(12,0))
        def confirmar():
            nome_final = ent_nome.get().strip() or nome_sel
            try:
                self.itens_pendentes.append({'categoria': cat_sel, 'item': nome_final, 'qtde': int(qtd_sel), 'valor_unit': float(preco_sel), 'baixado': False})
                self._refresh_tree_itens()
            except Exception as e:
                print('[Adicionar item] falhou:', e)
            try:
                top.destroy()
            except Exception:
                pass
        ttk.Button(btns, text='Cancelar', command=top.destroy).pack(side='right')
        ttk.Button(btns, text='Adicionar', style='Primary.TButton', command=confirmar).pack(side='right', padx=(0,8))
    def _add_item_temp(self):
        cat = (self.cmb_categoria.get() or 'Outros').strip()
        item = (self.ent_item_custom.get().strip() or self.cmb_item.get().strip())
        qtde = max(1, safe_int(self.ent_qtde.get(), 1))
        valor = safe_float(self.ent_vl.get(), 0.0)
        if not item:
            try:
                messagebox.showwarning('Atenção', 'Escolha ou digite um item.')
            except Exception:
                pass
            return
        try:
            self.itens_pendentes.append({'categoria': cat, 'item': item, 'qtde': qtde, 'valor_unit': valor})
            self._refresh_tree_itens()
        except Exception as e:
            print('[Adicionar item] falhou:', e)
        try:
            self.ent_item_custom.delete(0, 'end')
        except Exception:
            pass
    def _add_mao_de_obra(self):
        """Adiciona um item de mão de obra (sem baixa de estoque)."""
        desc = ''
        try:
            desc = (self.ent_mo_desc.get() or '').strip()
        except Exception:
            desc = ''
        try:
            preco_txt = (self.ent_mo_preco.get() or '0').strip()
        except Exception:
            preco_txt = '0'
        valor = safe_float(preco_txt, 0.0)
        if not desc:
            try:
                from tkinter import messagebox
                messagebox.showwarning('Atenção', 'Digite a descrição da mão de obra.')
            except Exception:
                pass
            return
        try:
            self.itens_pendentes.append({'categoria': 'Mão de obra', 'item': desc, 'qtde': 1, 'valor_unit': float(valor), 'baixado': True})
            self._refresh_tree_itens()
            try:
                self.ent_mo_desc.delete(0,'end')
                self.ent_mo_preco.delete(0,'end')
            except Exception:
                pass
        except Exception as e:
            print('[Mão de obra] falhou:', e)

    def _remover_item_temp(self):
        sel = self.tree_itens.selection()
        if not sel:
            return
        idx = self.tree_itens.index(sel[0])
        if 0 <= idx < len(self.itens_pendentes):
            try:
                it = self.itens_pendentes[idx]
                cat0 = str(it.get('categoria','')).lower()
                if it.get('baixado') and cat0 not in ('mão de obra','mao de obra','serviço','servico'):
                    self.db.estoque_repor(it.get('item',''), int(it.get('qtde', 0)), it.get('categoria',''))
            except Exception as e:
                print('[Estoque] reposição falhou:', e)
            self.itens_pendentes.pop(idx)
            self._refresh_tree_itens()
    def _refresh_tree_itens(self):
        for i in self.tree_itens.get_children():
            self.tree_itens.delete(i)
        total = 0.0
        for it in self.itens_pendentes:
            t = float(it['qtde']) * float(it['valor_unit']); total += t
            self.tree_itens.insert('', 'end', values=(it['categoria'], it['item'], it['qtde'], f"{it['valor_unit']:.2f}", f"{t:.2f}"))
        self._zebra(self.tree_itens)
        self.lbl_total.config(text=f"Total: R$ {total:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))

    def _zebra(self, tree: ttk.Treeview):
        tree.tag_configure('odd', background=self.palette['table_odd'])
        tree.tag_configure('even', background=self.palette['table_even'])
        for i, iid in enumerate(tree.get_children()):
            self.item = self.tree  # no-op to avoid linter warning
            tree.item(iid, tags=('odd' if i % 2 else 'even',))

    def _categoria_sem_baixa_estoque(self, categoria: str) -> bool:
        """Categorias que não devem mexer no estoque."""
        cat0 = str(categoria or '').strip().lower()
        return cat0 in ('mão de obra', 'mao de obra', 'serviço', 'servico')

    def _ajustar_estoque_ao_editar_os(self, servico_id: int, novos_itens) -> list:
        """
        Ao editar uma OS pronta, devolve ao estoque os itens antigos e baixa
        os novos itens. Assim dá para corrigir item/quantidade/preço sem refazer a nota.
        Retorna avisos de itens que não conseguiram baixar.
        """
        avisos = []
        try:
            antigos = self.db.get_itens_servico(int(servico_id)) or []
        except Exception:
            antigos = []

        # 1) Devolve o que estava salvo anteriormente na OS
        for row in antigos:
            try:
                if len(row) >= 5:
                    _id, cat, item, qtde, _unit = row[:5]
                else:
                    cat, item, qtde, _unit = row[:4]
                if self._categoria_sem_baixa_estoque(cat):
                    continue
                self.db.estoque_repor(item, int(qtde or 0), cat)
            except Exception as e:
                try:
                    avisos.append(f'Não consegui devolver ao estoque: {item} x{qtde} ({e})')
                except Exception:
                    pass

        # 2) Baixa novamente conforme a OS ficou depois da edição
        for row in (novos_itens or []):
            try:
                cat, item, qtde, _unit = row[:4]
                if self._categoria_sem_baixa_estoque(cat):
                    continue
                ok, disp = self.db.estoque_baixa(item, int(qtde or 0), cat)
                if not ok:
                    ok2, disp2 = self.db.estoque_baixa(item, int(qtde or 0), None)
                    if not ok2:
                        avisos.append(f'Estoque insuficiente ou item não encontrado: {item} x{qtde}. Disponível: {disp}.')
            except Exception as e:
                try:
                    avisos.append(f'Falha ao baixar estoque do item: {item} x{qtde} ({e})')
                except Exception:
                    pass
        return avisos

    # ---- Persistência serviço ---- #
    def _salvar(self):
        # Se estiver em modo edição, atualizar OS existente e sair
        try:
            if getattr(self, 'editando_servico_id', None):
                edit_id = int(self.editando_servico_id)
                descricao_atual = self.txt_descricao.get('1.0','end').strip()
                km_atual_val = safe_int(self.ent_km_atual.get())
                try:
                    intervalo_val = int(self.cmb_intervalo.get() or 0)
                except Exception:
                    intervalo_val = 0
                proxima_val = (km_atual_val + intervalo_val) if intervalo_val > 0 else km_atual_val
                self.db.update_servico_fields(edit_id, descricao_atual, km_atual_val, intervalo_val, proxima_val)
                # Normaliza itens para (categoria, item, qtde, valor_unit) antes de salvar (edição)
                itens_norm = []
                for _it in (self.itens_pendentes or []):
                    if isinstance(_it, dict):
                        itens_norm.append((
                            _it.get('categoria', '') or '',
                            _it.get('item', '') or '',
                            int(_it.get('qtde', 0) or 0),
                            float(_it.get('valor_unit', 0) or 0.0),
                        ))
                    else:
                        try:
                            _cat, _item, _q, _v = _it
                        except Exception:
                            # fallback defensivo
                            _cat = getattr(_it, 'categoria', '') or ''
                            _item = getattr(_it, 'item', '') or ''
                            _q = int(getattr(_it, 'qtde', 0) or 0)
                            _v = float(getattr(_it, 'valor_unit', 0) or 0.0)
                        itens_norm.append((_cat or '', _item or '', int(_q or 0), float(_v or 0.0)))
                avisos_estoque = self._ajustar_estoque_ao_editar_os(edit_id, itens_norm)
                self.db.replace_itens_servico(edit_id, itens_norm)

                from tkinter import messagebox

                try:

                    self.lift(); self.focus_force()

                except Exception:

                    pass

                if avisos_estoque:
                    messagebox.showwarning('OS atualizada com aviso', 'OS atualizada com sucesso, mas alguns itens não deram baixa no estoque:\n\n' + '\n'.join(avisos_estoque[:8]), parent=self)
                else:
                    messagebox.showinfo('Sucesso', 'OS atualizada com sucesso!', parent=self)

                try:

                    self.toast('OS atualizada com sucesso!')

                except Exception:

                    pass

                self.editando_servico_id = None

                self._clear_edit_badge()

                self._limpar_form()

                return
        except Exception as _e:
            from tkinter import messagebox
            messagebox.showerror('Erro', f'Falha ao atualizar OS em modo edição:\n{_e}')
            return

        try:
            nome = self.ent_cli_nome.get().strip()
            if not nome:
                messagebox.showwarning('Atenção', 'Informe o nome do cliente.'); return
            tel = self.ent_cli_tel.get().strip()
            marca = self.cmb_marca.get().strip() or 'Outros'
            modelo = self.cmb_modelo.get().strip() or 'Modelo não listado'
            placa = self.ent_placa.get().strip().upper()
            if not placa:
                messagebox.showwarning('Atenção', 'Informe a placa do veículo.'); return
            ano = self.ent_ano.get().strip()
            km_atual = safe_int(self.ent_km_atual.get())
            km_troca_corr = safe_int(getattr(self, 'ent_km_troca_corr', None).get() if hasattr(self, 'ent_km_troca_corr') else 0)
            km_corr_trocada = safe_int(getattr(self, 'ent_km_corr_trocada', None).get() if hasattr(self, 'ent_km_corr_trocada') else 0)
            km_corr_proxima = safe_int(getattr(self, 'ent_km_corr_proxima', None).get() if hasattr(self, 'ent_km_corr_proxima') else 0)
            intervalo = safe_int(self.cmb_intervalo.get(), default=10000)
            proxima = km_atual + intervalo if km_atual >= 0 and intervalo > 0 else km_atual

            descricao = self.txt_descricao.get('1.0', 'end').strip()
            descricao = "\n".join([l for l in descricao.splitlines() if not l.strip().lower().startswith(('próxima manutenção:', 'próx. manutenção:', 'próxima troca de óleo:', 'proxima troca de oleo:'))]).strip()
            if proxima > 0:
                descricao = (descricao + ("\n" if descricao else "") + f"Próxima troca de óleo: {proxima} km").strip()

            

# === BLOCO DESATIVADO (pedido do usuário) ===
# ITENS NÃO VÃO PARA A DESCRIÇÃO para evitar duplicidade.
# Os itens continuam sendo salvos em itens_servico e aparecem no HTML/Relatório via lista própria.
# Data: 2025-08-26
# if self.itens_pendentes:
#                 resumo = ['Itens do serviço:']
#                 total = 0.0
#                 for it in self.itens_pendentes:
#                     t = float(it['qtde']) * float(it['valor_unit']); total += t
#                     resumo.append(f"- {it['item']} ×{it['qtde']} — R$ {it['valor_unit']:.2f} (R$ {t:.2f})")
#                 resumo.append(f"Total dos itens: R$ {total:.2f}")
#                 descricao = (descricao + "\n\n" + "\n".join(resumo)).strip()

                        # Segurança: baixa no estoque itens ainda não baixados (ex.: adicionados por outro fluxo)
            try:
                for it in list(self.itens_pendentes):
                    if not it.get('baixado'):
                        cat0 = str(it.get('categoria','')).lower()
                        if cat0 in ('mão de obra','mao de obra','serviço','servico'):
                            it['baixado'] = True
                            continue
                        ok, disp = self.db.estoque_baixa(it.get('item',''), int(it.get('qtde',0)), it.get('categoria',''))
                        if not ok:
                            it['baixado'] = False
                            continue
                        it['baixado'] = True
            except Exception as _e:
                print('[Estoque] baixa (salvar) falhou:', _e)
            cli_id = self.db.upsert_cliente(nome, tel)
            vei_id = self.db.upsert_veiculo(cli_id, marca, modelo, placa, ano, km_atual, km_troca_corr, km_corr_trocada, km_corr_proxima)
            hoje = datetime.now().strftime('%Y-%m-%d %H:%M')
            serv_id = self.db.add_servico(vei_id, descricao, km_atual, intervalo, proxima, hoje)
            self.db.add_itens_servico(serv_id, self.itens_pendentes)

            from tkinter import messagebox


            try:


                self.lift(); self.focus_force()


            except Exception:


                pass


            messagebox.showinfo('Sucesso', 'Cadastro e serviço salvos com sucesso!', parent=self)


            try:


                self.toast('Cadastro salvo!')


            except Exception:


                pass
            self._limpar_form()
        except sqlite3.IntegrityError as e:
            messagebox.showerror('Erro', f'Erro de integridade (placa duplicada?):\n{e}')
        except Exception as e:
            messagebox.showerror('Erro', f'Falha ao salvar:\n{e}')

    def _excluir(self):
        placa = (self.ent_placa.get() or '').strip().upper()
        if not placa:
            messagebox.showwarning('Atenção', 'Informe a PLACA para excluir.'); return
        if not messagebox.askyesno('Confirmar', f'Deletar veículo e serviços da placa {placa}?'):
            return
        try:
            apagados = self.db.delete_by_placa(placa)
            if apagados:
                messagebox.showinfo('OK', f'{apagados} serviço(s) apagado(s) para placa {placa}.'); self._limpar_form()
            else:
                messagebox.showinfo('OK', f'Nenhum registro encontrado para placa {placa}.')
        except Exception as e:
            messagebox.showerror('Erro', f'Falha ao excluir:\n{e}')

    def _limpar_form(self):
        self.ent_cli_nome.delete(0, 'end')
        self.ent_cli_tel.delete(0, 'end')
        self.cmb_marca.set('')
        self.cmb_modelo.set('')
        self.ent_placa.delete(0, 'end')
        self.ent_ano.delete(0, 'end')
        self.ent_km_atual.delete(0, 'end')
        try:
            self.ent_km_troca_corr.delete(0, 'end')
        except Exception:
            pass
        try:
            self.ent_km_corr_trocada.delete(0, 'end')
        except Exception:
            pass
        try:
            self.ent_km_corr_proxima.delete(0, 'end')
        except Exception:
            pass
        self.cmb_intervalo.set('10000')
        self.lbl_proxima.config(text='Próxima manutenção: — km')
        self.txt_descricao.delete('1.0', 'end')
        self.itens_pendentes.clear(); self._refresh_tree_itens()

    
        # Sair do modo edição, esconder badge
        try:
            self.editando_servico_id = None
            self._clear_edit_badge()
        except Exception:
            pass
# ---- Busca ---- #
    def _build_busca(self, parent):
        pad = dict(padx=6, pady=6)
        frm = ttk.Frame(parent, style='Card.TFrame')
        frm.pack(fill='both', expand=True, padx=12, pady=12)

        top = ttk.Frame(frm, style='Card.TFrame')
        top.pack(fill='x', **pad)
        ttk.Label(top, text='Buscar por nome ou placa:').pack(side='left')
        self.ent_busca = ttk.Entry(top, width=40)
        self.ent_busca.pack(side='left', padx=8)
        ttk.Button(top, text='Buscar', style='Primary.TButton', command=self._do_busca).pack(side='left')

        cols = ('id', 'cliente', 'carro', 'placa', 'km', 'prox_km', 'data')
        self.tree = ttk.Treeview(frm, columns=cols, show='headings', height=15)
        self.tree.pack(fill='both', expand=True, pady=8)
        self.tree.heading('id', text='ID'); self.tree.column('id', width=60, anchor='center')
        self.tree.heading('cliente', text='Cliente'); self.tree.column('cliente', width=220)
        self.tree.heading('carro', text='Carro'); self.tree.column('carro', width=230)
        self.tree.heading('placa', text='Placa'); self.tree.column('placa', width=100, anchor='center')
        self.tree.heading('km', text='KM atual(troca de óleo)'); self.tree.column('km', width=110, anchor='e')
        self.tree.heading('prox_km', text='Próx. manut. (km)'); self.tree.column('prox_km', width=160, anchor='e')
        self.tree.heading('data', text='Data serviço'); self.tree.column('data', width=170, anchor='center')
        self._zebra(self.tree)

        self.tree.bind('<Double-1>', self._abrir_descricao)

        actions = ttk.Frame(frm, style='Card.TFrame')
        actions.pack(fill='x', pady=(4,0))
        ttk.Button(actions, text='Excluir OS selecionada', style='Danger.TButton', command=self._excluir_os_selecionada).pack(side='left')

        self.lbl_count = ttk.Label(frm, text='0 resultados'); self.lbl_count.pack(anchor='w')

    def _do_busca(self):
        termo = self.ent_busca.get().strip()
        dados = self.db.buscar(termo)
        for i in self.tree.get_children():
            self.tree.delete(i)
        for row in dados:
            sid, nome, marca, modelo, placa, km_atual, prox, data = row
            carro = f"{marca} {modelo}".strip()
            self.tree.insert('', 'end', values=(sid, nome, carro, placa, km_atual, prox, data))
        self._zebra(self.tree)
        self.lbl_count.config(text=f"{len(dados)} resultado(s)")

    def _abrir_descricao(self, event):
        sel = self.tree.selection()
        if not sel:
            return
        item = self.tree.item(sel[0])
        servico_id = item['values'][0]
        with self.db._connect() as con:
            cur = con.cursor()
            cur.execute("SELECT id, veiculo_id, descricao, km_atual, intervalo_km, proxima_manut_km, data FROM servicos WHERE id=?", (servico_id,))
            srow = cur.fetchone()
        if not srow:
            messagebox.showerror('Erro', 'Serviço não encontrado.'); return
        sid, veiculo_id, descricao, km_atual, intervalo, proxima_km, data_str = srow
        JanelaDescricao(self, self.db, sid, descricao, km_atual, intervalo, proxima_km, data_str)

    def _excluir_os_selecionada(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning('Atenção', 'Selecione uma OS na lista.'); return
        item = self.tree.item(sel[0])
        servico_id = int(item['values'][0])
        if not messagebox.askyesno('Confirmar', f'Excluir a OS (ID {servico_id})? Essa ação não pode ser desfeita.'):
            return
        try:
            self.db.delete_servico(servico_id)
            messagebox.showinfo('OK', f'OS {servico_id} excluída.')
            self._do_busca()
        except Exception as e:
            messagebox.showerror('Erro', f'Falha ao excluir OS:\n{e}')

    # ---- Estoque ---- #
    def _build_estoque(self, parent):
        pad = dict(padx=6, pady=6)
        frm = ttk.Frame(parent, style='Card.TFrame')
        frm.pack(fill='both', expand=True, padx=12, pady=12)
        ttk.Label(frm, text='Estoque (MVP)', style='Title.TLabel').pack(anchor='w')
        top = ttk.Frame(frm, style='Card.TFrame')
        top.pack(fill='x', pady=6)
        self.ent_item = ttk.Entry(top, width=30); self.ent_item.insert(0, 'Ex.: Óleo 5W30'); self.ent_item.pack(side='left', padx=4)
        self.ent_cat = ttk.Entry(top, width=18); self.ent_cat.insert(0, 'Lubrificantes'); self.ent_cat.pack(side='left', padx=4)
        self.ent_qt = ttk.Entry(top, width=8); self.ent_qt.insert(0, '0'); self.ent_qt.pack(side='left', padx=4)
        self.ent_preco = ttk.Entry(top, width=10); self.ent_preco.insert(0, '0'); self.ent_preco.pack(side='left', padx=4)
        ttk.Button(top, text='Adicionar', style='Primary.TButton', command=self._add_estoque).pack(side='left', padx=6)
        ttk.Button(top, text='Salvar estoque', command=self._salvar_estoque).pack(side='left', padx=6)
        ttk.Button(top, text='Editar item', command=self._editar_item_estoque).pack(side='left', padx=6)
        ttk.Button(top, text='Imprimir estoque', command=self._imprimir_estoque).pack(side='left', padx=6)
                # Botão para editar preço do item selecionado
        try:
            ttk.Button(
                top,
                text="Editar preço (selecionado)",
                style="Ghost.TButton" if "Ghost.TButton" in str(ttk.Style().theme_use()) else "TButton",
                command=self._editar_preco_estoque
            ).pack(side="left", padx=6)
        except Exception:
            pass
        # Botão para editar quantidade do item selecionado
        try:
            ttk.Button(
                top,
                text="Editar quantidade (selecionado)",
                style="Ghost.TButton" if "Ghost.TButton" in str(ttk.Style().theme_use()) else "TButton",
                command=self._editar_qtde_estoque
            ).pack(side="left", padx=6)
        except Exception:
            pass


        cols = ('id', 'item', 'categoria', 'qtde', 'preco')
        # === Busca no Estoque (UI) ===
        try:
            from tkinter import ttk as _ttk
            _ttk.Label(top, text="Buscar:").pack(side="left", padx=(12, 2))
            self.ent_busca_estoque = _ttk.Entry(top, width=24)
            self.ent_busca_estoque.pack(side="left", padx=4)
            self.cmb_busca_campo_estoque = _ttk.Combobox(top, values=("Item", "Categoria"), state="readonly", width=12)
            self.cmb_busca_campo_estoque.set("Item")
            self.cmb_busca_campo_estoque.pack(side="left", padx=4)
            _ttk.Button(top, text="Buscar", command=self._aplicar_busca_estoque).pack(side="left", padx=4)
            _ttk.Button(top, text="Limpar", command=self._limpar_busca_estoque).pack(side="left", padx=4)
            try:
                self.ent_busca_estoque.bind("<Return>", self._aplicar_busca_estoque)
                try:
                    self.ent_busca_estoque.bind("<KeyRelease>", self._on_busca_keyrelease)
                    self.ent_busca_estoque.bind("<Down>", lambda e: (self._update_suggestions_busca(), "break"))
                    self.ent_busca_estoque.bind("<Escape>", lambda e: (self._hide_suggestions_busca(), "break"))
                except Exception:
                    pass
            except Exception:
                pass
        except Exception:
            pass
        self.tree_estoque = ttk.Treeview(frm, columns=cols, show='headings', height=12)
        try:
            self.tree_estoque.bind("<FocusIn>", lambda e: self._hide_suggestions_busca())
        except Exception:
            pass
        self.tree_estoque.pack(fill='both', expand=True, pady=6)
        for c, label in zip(cols, ['ID', 'Item', 'Categoria', 'Qtde', 'Preço']):
            self.tree_estoque.heading(c, text=label)
        self._zebra(self.tree_estoque)
        self._refresh_estoque()


        # === Edição rápida de preço (duplo clique e menu direito) ===
        try:
            import tkinter as tk
            if not hasattr(self, "_menu_estoque"):
                self._menu_estoque = tk.Menu(self, tearoff=0)
                self._menu_estoque.add_command(label="Editar item completo…", command=self._editar_item_estoque)
                self._menu_estoque.add_command(label="Editar preço…", command=self._editar_preco_estoque)
                self._menu_estoque.add_command(label="Editar quantidade…", command=self._editar_qtde_estoque)
                self._menu_estoque.add_command(label="Imprimir estoque…", command=self._imprimir_estoque)

                self._menu_estoque.add_separator()
                self._menu_estoque.add_command(label="Excluir produto…", command=self._excluir_produto_estoque)

            def _on_right_click_estoque(event):
                iid = self.tree_estoque.identify_row(event.y)
                if iid:
                    self.tree_estoque.selection_set(iid)
                    self._menu_estoque.tk_popup(event.x_root, event.y_root)

            self.tree_estoque.bind("<Double-1>", lambda e: self._editar_item_estoque())
            self.tree_estoque.bind("<Button-3>", _on_right_click_estoque)

            self.tree_estoque.bind("<Delete>", lambda e: self._excluir_produto_estoque())
        except Exception:
            pass
    def _add_estoque(self):
        item = self.ent_item.get().strip(); cat = self.ent_cat.get().strip()
        qt = safe_int(self.ent_qt.get()); preco = safe_float(self.ent_preco.get())
        if not item:
            messagebox.showwarning('Atenção', 'Informe o item.'); return
        try:
            with self.db._connect() as con:
                cur = con.cursor(); cur.execute("INSERT INTO estoque (item, categoria, qtde, preco) VALUES (?, ?, ?, ?)", (item, cat, qt, preco)); con.commit()
            self._refresh_estoque()
            self.ent_item.delete(0, 'end'); self.ent_cat.delete(0, 'end'); self.ent_qt.delete(0, 'end'); self.ent_preco.delete(0, 'end')
        except Exception as e:
            messagebox.showerror('Erro', f'Falha ao inserir no estoque:\n{e}')

    def _popular_estoque_basico(self):
        try:
            with self.db._connect() as con:
                cur = con.cursor()
                cur.execute("""CREATE TABLE IF NOT EXISTS estoque (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        item TEXT NOT NULL,
                        categoria TEXT,
                        qtde INTEGER DEFAULT 0,
                        preco REAL DEFAULT 0
                    );
                """)
                cur.execute("DELETE FROM estoque")
                for (item, categoria, qtde, preco) in ESTOQUE_BASICO:
                    cur.execute("INSERT INTO estoque (item, categoria, qtde, preco) VALUES (?, ?, ?, ?)",
                                (item, categoria, int(qtde), float(preco)))
                con.commit()
            self._refresh_estoque()
            messagebox.showinfo('OK', f'Estoque básico inserido/atualizado com {len(ESTOQUE_BASICO)} itens.')
        except Exception as e:
            messagebox.showerror('Erro', f'Falha ao popular estoque:\n{e}')


    def _salvar_estoque(self):
        """Salva no banco os valores atualmente exibidos na grade do estoque (ID, Item, Categoria, Qtde, Preço).
        Não zera nada e mantém as edições feitas. """
        try:
            tree = getattr(self, "tree_estoque", None)
            if tree is None:
                from tkinter import messagebox
                messagebox.showerror("Erro", "A lista do estoque não foi encontrada.")
                return

            def _parse_preco(val):
                try:
                    if isinstance(val, (int, float)):
                        return float(val)
                    s = str(val).strip().replace("R$", "").replace(" ", "")
                    if "," in s and "." in s:
                        s = s.replace(".", "").replace(",", ".")
                    else:
                        s = s.replace(",", ".")
                    return float(s) if s else 0.0
                except Exception:
                    return 0.0

            rows = []
            for iid in tree.get_children():
                vals = tree.item(iid, "values")
                if not vals or len(vals) < 5:
                    continue
                try:
                    rid = int(vals[0])
                    item = str(vals[1]).strip()
                    categoria = str(vals[2]).strip()
                    qtde = int(str(vals[3]).strip() or "0")
                    preco = _parse_preco(vals[4])
                except Exception:
                    continue
                rows.append((rid, item, categoria, qtde, preco))

            if not rows:
                from tkinter import messagebox
                messagebox.showwarning("Atenção", "Nada para salvar no estoque.")
                return

            with self.db._connect() as con:
                cur = con.cursor()
                for rid, item, categoria, qtde, preco in rows:
                    cur.execute(
                        "UPDATE estoque SET item = ?, categoria = ?, qtde = ?, preco = ? WHERE id = ?",
                        (item, categoria, max(0, int(qtde)), float(preco), int(rid))
                    )
                con.commit()

            try:
                from tkinter import messagebox
                messagebox.showinfo("Estoque", "Estoque salvo com sucesso!")
            except Exception:
                pass

            if hasattr(self, "_refresh_estoque"):
                self._refresh_estoque()

        except Exception as e:
            try:
                from tkinter import messagebox
                messagebox.showerror("Erro", f"Falha ao salvar estoque:\n{e}")
            except Exception:
                pass
    def _refresh_estoque(self):
        if not hasattr(self, 'tree_estoque'):
            return
        for i in self.tree_estoque.get_children():
            self.tree_estoque.delete(i)
        try:
            with self.db._connect() as con:
                cur = con.cursor(); cur.execute("SELECT id, item, categoria, qtde, preco FROM estoque ORDER BY item")
                for (i, it, cat, qt, pr) in cur.fetchall():
                    self.tree_estoque.insert('', 'end', values=(i, it, cat, qt, f"R$ {pr:,.2f}"))
        except Exception:
            pass
        self._zebra(self.tree_estoque)

    # ---- Relatórios ---- #
    def _build_rel(self, parent):
        frm = ttk.Frame(parent, style='Card.TFrame')
        frm.pack(fill='both', expand=True, padx=12, pady=12)
        ttk.Label(frm, text='Relatórios rápidos', style='Title.TLabel').pack(anchor='w')
        ttk.Button(frm, text='Contagem de clientes / veículos / serviços', style='Ghost.TButton', command=self._rel_counts).pack(anchor='w', pady=6)
        self.lbl_rel = ttk.Label(frm, text='—'); self.lbl_rel.pack(anchor='w')

    def _rel_counts(self):
        with self.db._connect() as con:
            cur = con.cursor(); cur.execute("SELECT COUNT(*) FROM clientes"); c = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM veiculos"); v = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM servicos"); s = cur.fetchone()[0]
        self.lbl_rel.config(text=f"Clientes: {c} · Veículos: {v} · Serviços: {s}")

# ----------------------------- JANELA DE DESCRIÇÃO ----------------------------- #


    def _abrir_picker_cliente(self):

        import tkinter as tk

        from tkinter import ttk, messagebox

    

        top = tk.Toplevel(self)

        top.title('Puxar cadastro do cliente')

        top.geometry('760x460')

        try:

            top.transient(self)

            top.grab_set()

        except Exception:

            pass

    

        pad = dict(padx=8, pady=6)

    

        # Barra de busca

        barra = ttk.Frame(top)

        barra.pack(fill='x', **pad)

        ttk.Label(barra, text='Buscar (nome, telefone ou placa):').pack(side='left')

        ent_busca = ttk.Entry(barra, width=36)

        ent_busca.pack(side='left', padx=(8,8))

        btn_buscar = ttk.Button(barra, text='Buscar')

        btn_buscar.pack(side='left')

    

        # Tabela

        cols = ('cli_id','nome','telefone','marca','modelo','placa','ano','km_atual','vei_id')

        tree = ttk.Treeview(top, columns=cols, show='headings', height=12)

        tree.pack(fill='both', expand=True, padx=8, pady=4)
        # Quantidade desejada
        frm_qt = ttk.Frame(top); frm_qt.pack(fill='x', padx=8, pady=4)
        ttk.Label(frm_qt, text='Quantidade:').pack(side='left')
        sp_qtde = ttk.Spinbox(frm_qt, from_=1, to=999, width=8)
        sp_qtde.set('1'); sp_qtde.pack(side='left', padx=(6,0))

    

        headers = {

            'nome':'Nome', 'telefone':'Telefone', 'marca':'Marca', 'modelo':'Modelo',

            'placa':'Placa', 'ano':'Ano', 'km_atual':'KM atual(troca de óleo)'

        }

        for c in cols:

            if c in ('cli_id','vei_id'):

                tree.column(c, width=0, stretch=False)  # oculto (ids)

            else:

                w = 160 if c in ('nome','modelo') else 90

                tree.heading(c, text=headers.get(c, c))

                tree.column(c, width=w, anchor='w')

    

        # Scroll vertical

        vsb = ttk.Scrollbar(top, orient='vertical', command=tree.yview)

        tree.configure(yscroll=vsb.set)

        try:

            vsb.place(in_=tree, relx=1.0, rely=0, relheight=1.0, x=0, y=0, anchor='ne')

        except Exception:

            vsb.pack(side='right', fill='y')

    

        def preencher_form_do_row(values):

            # values: (cli_id, nome, telefone, marca, modelo, placa, ano, km_atual, vei_id)

            _cli_id, nome, tel, marca, modelo, placa, ano, km_atual, _vei_id = values

    

            try:

                # Cliente

                self.ent_cli_nome.delete(0, 'end'); self.ent_cli_nome.insert(0, nome or '')

                self.ent_cli_tel.delete(0, 'end');  self.ent_cli_tel.insert(0,  tel or '')

    

                # Veículo (se houver)

                placa = (placa or '').strip().upper()

                try:

                    self.cmb_marca.set(marca or '')

                except Exception:

                    pass

                try:

                    self._load_modelos()  # garante lista de modelos p/ a marca atual

                except Exception:

                    pass

                try:

                    self.cmb_modelo.set(modelo or '')

                except Exception:

                    pass

    

                try:

                    self.ent_placa.delete(0, 'end'); self.ent_placa.insert(0, placa)

                except Exception:

                    pass

                try:

                    self.ent_ano.delete(0, 'end');   self.ent_ano.insert(0,  ano or '')

                except Exception:

                    pass

    

                try:

                    self.ent_km_atual.delete(0, 'end')

                    if km_atual is not None and str(km_atual).strip() != '':

                        self.ent_km_atual.insert(0, str(km_atual))

                except Exception:

                    pass

    

                # Atualiza label "Próxima manutenção"

                try:

                    self._atualiza_proxima()

                except Exception:

                    pass

    

            except Exception as e:

                try:

                    messagebox.showerror('Erro', f'Falha ao preencher formulário:\n{e}', parent=self)

                except Exception:

                    print('[picker_cliente] erro preenchendo:', e)

    

        def on_select(*_):

            sel = tree.selection()

            if not sel:

                return

            values = tree.item(sel[0], 'values')

            preencher_form_do_row(values)

            try:

                top.destroy()

            except Exception:

                pass

    

        def executar_busca(*_):

            termo = ent_busca.get().strip()

            try:

                rows = self.db.buscar_clientes_placas(termo, limit=150)

            except Exception as e:

                try:

                    messagebox.showerror('Erro', f'Falha na busca:\n{e}', parent=top)

                except Exception:

                    print('[buscar_clientes_placas] erro:', e)

                return

    

            for i in tree.get_children():

                tree.delete(i)

            for r in rows:

                # r: (cli_id, nome, telefone, marca, modelo, placa, ano, km_atual, vei_id)

                tree.insert('', 'end', values=r)

    

        tree.bind('<Double-1>', on_select)

        tree.bind('<Return>',    on_select)

        btn_buscar.configure(command=executar_busca)

        ent_busca.bind('<Return>', executar_busca)

    

        # Busca inicial (opcional: lista tudo se termo vazio)

        executar_busca()

        try:

            ent_busca.focus_set()

        except Exception:

            pass

    def _editar_preco_estoque(self):
        """
        Edita rapidamente o preço do item selecionado no estoque.
        - Abre um diálogo para digitar o novo preço.
        - Atualiza o banco (tabela 'estoque', coluna 'preco').
        - Atualiza a lista do estoque (se existir um método de refresh).
        """
        try:
            tree = getattr(self, "tree_estoque", None)
            if tree is None:
                from tkinter import messagebox
                messagebox.showerror("Erro", "A lista do estoque (tree_estoque) não foi encontrada.")
                return
    
            sel = tree.selection()
            if not sel:
                from tkinter import messagebox
                messagebox.showwarning("Atenção", "Selecione um item do estoque.")
                return
    
            iid = sel[0]
            vals = tree.item(iid, "values")
            if not vals:
                from tkinter import messagebox
                messagebox.showwarning("Atenção", "Não consegui ler os dados do item selecionado.")
                return
    
            # Esperado: (id, item, categoria, qtde, preco) — pelo projeto atual
            try:
                _id = int(vals[0])
            except Exception:
                from tkinter import messagebox
                messagebox.showwarning("Atenção", "Não encontrei o ID na primeira coluna.")
                return
    
            nome = vals[1] if len(vals) > 1 else "item"
    
            # Pergunta novo preço
            from tkinter import simpledialog
            novo = simpledialog.askfloat("Preço", f'Novo preço para "{nome}":', minvalue=0.0)
            if novo is None:
                return
    
            # Atualiza o banco
            try:
                db = getattr(self, "db", None)
                if db is None or not hasattr(db, "_connect"):
                    from tkinter import messagebox
                    messagebox.showerror("Erro", "Conexão com o banco não disponível (self.db._connect ausente).")
                    return
    
                with self.db._connect() as con:
                    cur = con.cursor()
                    cur.execute("UPDATE estoque SET preco = ? WHERE id = ?", (float(novo), _id))
                    con.commit()
            except Exception as e:
                from tkinter import messagebox
                messagebox.showerror("Erro", f"Não consegui atualizar o preço no banco:\n{e}")
                return
    
            # Atualiza a UI do estoque
            try:
                if hasattr(self, "_refresh_estoque"):
                    self._refresh_estoque()
                elif hasattr(self, "_carregar_estoque"):
                    self._carregar_estoque()
                elif hasattr(self, "_load_estoque"):
                    self._load_estoque()
                else:
                    # Atualiza só a linha atual, se possível
                    vals = list(vals)
                    if len(vals) >= 5:
                        vals[4] = f"{float(novo):.2f}"
                        tree.item(iid, values=tuple(vals))
            except Exception:
                pass
        except Exception as e:
            # Evita quebrar a aplicação
            import traceback
            traceback.print_exc()
    # ===== Busca no Estoque =====

    def _editar_qtde_estoque(self):
        '''
        Edita rapidamente a quantidade (qtde) do item selecionado no estoque.
        - Abre um diálogo para digitar a nova quantidade (inteiro).
        - Atualiza o banco (tabela 'estoque', coluna 'qtde').
        - Atualiza a lista do estoque logo em seguida.
        '''
        try:
            tree = getattr(self, "tree_estoque", None)
            if tree is None:
                from tkinter import messagebox
                messagebox.showerror("Erro", "A lista do estoque (tree_estoque) não foi encontrada.")
                return

            sel = tree.selection()
            if not sel:
                from tkinter import messagebox
                messagebox.showwarning("Atenção", "Selecione um item do estoque.")
                return

            iid = sel[0]
            vals = tree.item(iid, "values")
            if not vals or len(vals) < 1:
                from tkinter import messagebox
                messagebox.showerror("Erro", "Não foi possível obter os dados do item.")
                return

            try:
                item_id = int(vals[0])
            except Exception:
                from tkinter import messagebox
                messagebox.showerror("Erro", "ID do item inválido.")
                return

            nome = vals[1] if len(vals) > 1 else "item"

            # Pergunta nova quantidade
            from tkinter import simpledialog
            novo = simpledialog.askinteger("Quantidade", f'Nova quantidade para "{nome}":', minvalue=0)
            if novo is None:
                return

            # Atualiza o banco
            try:
                db = getattr(self, "db", None)
                if db is None or not hasattr(db, "_connect"):
                    from tkinter import messagebox
                    messagebox.showerror("Erro", "Conexão com o banco não disponível (self.db._connect).")
                    return

                with self.db._connect() as con:
                    cur = con.cursor()
                    cur.execute("UPDATE estoque SET qtde = ? WHERE id = ?", (int(novo), item_id))
                    con.commit()
            except Exception as e:
                from tkinter import messagebox
                messagebox.showerror("Erro", f"Falha ao atualizar a quantidade:\n{e}")
                return

            # Atualiza a UI do estoque
            try:
                if hasattr(self, "_refresh_estoque"):
                    self._refresh_estoque()
                elif hasattr(self, "_carregar_estoque"):
                    self._carregar_estoque()
                elif hasattr(self, "_load_estoque"):
                    self._load_estoque()
            except Exception:
                pass

        except Exception as e:
            try:
                from tkinter import messagebox
                messagebox.showerror("Erro", f"Operação falhou:\n{e}")
            except Exception:
                pass


    def _estoque_replace_rows(self, rows):
        "Substitui as linhas do Treeview do estoque pelos `rows` fornecidos."
        try:
            tree = getattr(self, "tree_estoque", None)
            if tree is None:
                return
            for iid in tree.get_children():
                tree.delete(iid)
            for row in rows:
                # Esperado: (id, item, categoria, qtde, preco)
                rid, item, categoria, qtde, preco = row
                try:
                    preco_txt = f"{float(preco):.2f}"
                except Exception:
                    preco_txt = str(preco) if preco is not None else "0.00"
                tree.insert("", "end", values=(rid, item, categoria, qtde, preco_txt))
        except Exception:
            pass
    
    def _aplicar_busca_estoque(self, *_):
        "Aplica o filtro de busca no estoque pelo campo e termo informados."
        try:
            tree = getattr(self, "tree_estoque", None)
            if tree is None:
                return
            termo = ""
            campo = "item"
            try:
                termo = self.ent_busca_estoque.get().strip()
            except Exception:
                pass
            try:
                campo_sel = self.cmb_busca_campo_estoque.get().strip().lower()
                if campo_sel.startswith("cat"):
                    campo = "categoria"
                else:
                    campo = "item"
            except Exception:
                campo = "item"
    
            if not termo:
                # Sem termo -> recarrega estoque padrão
                if hasattr(self, "_refresh_estoque"):
                    self._refresh_estoque()
                elif hasattr(self, "_carregar_estoque"):
                    self._carregar_estoque()
                elif hasattr(self, "_load_estoque"):
                    self._load_estoque()
                return
    
            # Consulta filtrada no banco
            if not hasattr(self, "db") or not hasattr(self.db, "_connect"):
                return
            with self.db._connect() as con:
                cur = con.cursor()
                if campo == "categoria":
                    cur.execute("SELECT id, item, categoria, qtde, preco FROM estoque WHERE categoria LIKE ? ORDER BY item ASC", (f"%{termo}%",))
                else:
                    cur.execute("SELECT id, item, categoria, qtde, preco FROM estoque WHERE item LIKE ? ORDER BY item ASC", (f"%{termo}%",))
                rows = cur.fetchall()
            self._estoque_replace_rows(rows)
        except Exception:
            pass
    
    def _limpar_busca_estoque(self, *_):
        "Limpa os campos de busca e recarrega o estoque."
        try:
            if hasattr(self, "ent_busca_estoque"):
                self.ent_busca_estoque.delete(0, "end")
            if hasattr(self, "cmb_busca_campo_estoque"):
                try:
                    self.cmb_busca_campo_estoque.set("Item")
                except Exception:
                    pass
            if hasattr(self, "_refresh_estoque"):
                self._refresh_estoque()
            elif hasattr(self, "_carregar_estoque"):
                self._carregar_estoque()
            elif hasattr(self, "_load_estoque"):
                self._load_estoque()
        except Exception:
            pass
    # ===== Busca instantânea e Autocomplete (Estoque) =====
    def _busca_schedule(self):
        "Dispara a busca com um pequeno atraso (debounce)."
        try:
            if getattr(self, "_busca_after_id", None):
                try:
                    self.after_cancel(self._busca_after_id)
                except Exception:
                    pass
            self._busca_after_id = self.after(250, self._aplicar_busca_estoque)
        except Exception:
            pass
    
    def _on_busca_keyrelease(self, event=None):
        "Teclou no campo de busca: agenda busca e atualiza sugestões."
        try:
            keys_ignore = {"Return","Escape","Up","Down","Left","Right","Prior","Next","Home","End"}
            if event is not None and getattr(event, "keysym", "") in keys_ignore:
                # não dispara ao navegar
                return
            self._busca_schedule()
            self._update_suggestions_busca()
        except Exception:
            pass
    
    def _update_suggestions_busca(self):
        "Atualiza a lista de sugestões sob o campo de busca."
        try:
            if not hasattr(self, "ent_busca_estoque"):
                return
            termo = self.ent_busca_estoque.get().strip()
            campo_sel = "Item"
            try:
                campo_sel = self.cmb_busca_campo_estoque.get().strip()
            except Exception:
                pass
            col = "item" if not campo_sel.lower().startswith("cat") else "categoria"
    
            if not termo:
                self._hide_suggestions_busca()
                return
    
            if not hasattr(self, "db") or not hasattr(self.db, "_connect"):
                return
    
            with self.db._connect() as con:
                cur = con.cursor()
                cur.execute(f"SELECT DISTINCT {col} FROM estoque WHERE {col} LIKE ? ORDER BY {col} ASC LIMIT 8", (termo + "%",))
                results = [r[0] for r in cur.fetchall() if r and r[0]]
    
            if not results:
                self._hide_suggestions_busca()
                return
    
            import tkinter as tk
            if not hasattr(self, "_sug_win") or self._sug_win is None or not self._sug_win.winfo_exists():
                self._sug_win = tk.Toplevel(self)
                self._sug_win.overrideredirect(True)
                self._sug_win.attributes("-topmost", True)
                self._sug_lb = tk.Listbox(self._sug_win, height=min(8, len(results)))
                self._sug_lb.pack(fill="both", expand=True)
                # binds
                self._sug_lb.bind("<Return>", self._suggestions_select)
                self._sug_lb.bind("<Double-1>", self._suggestions_select)
                self._sug_lb.bind("<Escape>", lambda e: self._hide_suggestions_busca())
                self._sug_lb.bind("<Up>", self._suggestions_nav)
                self._sug_lb.bind("<Down>", self._suggestions_nav)
    
            # preencher
            self._sug_lb.delete(0, "end")
            for r in results:
                self._sug_lb.insert("end", r)
    
            # posicionar abaixo do entry
            try:
                x = self.ent_busca_estoque.winfo_rootx()
                y = self.ent_busca_estoque.winfo_rooty() + self.ent_busca_estoque.winfo_height()
                w = self.ent_busca_estoque.winfo_width()
                self._sug_win.geometry(f"{w}x{min(8, len(results))*20}+{x}+{y}")
                self._sug_win.deiconify()
                self._sug_win.lift()
            except Exception:
                pass
        except Exception:
            pass
    
    def _hide_suggestions_busca(self):
        try:
            if hasattr(self, "_sug_win") and self._sug_win is not None and self._sug_win.winfo_exists():
                self._sug_win.withdraw()
        except Exception:
            pass
    
    def _suggestions_select(self, event=None):
        try:
            if not hasattr(self, "_sug_lb"):
                return
            cur = self._sug_lb.curselection()
            if not cur:
                return
            val = self._sug_lb.get(cur[0])
            self.ent_busca_estoque.delete(0, "end")
            self.ent_busca_estoque.insert(0, val)
            self._hide_suggestions_busca()
            # executa busca
            self._aplicar_busca_estoque()
            # retorna foco ao entry
            self.ent_busca_estoque.focus_set()
            return "break"
        except Exception:
            pass
    
    def _suggestions_nav(self, event=None):
        try:
            if not hasattr(self, "_sug_lb"):
                return
            sz = self._sug_lb.size()
            if sz <= 0:
                return
            cur = self._sug_lb.curselection()
            idx = cur[0] if cur else -1
            if event.keysym == "Down":
                idx = min(sz-1, idx+1)
            elif event.keysym == "Up":
                idx = max(0, idx-1)
            if idx >= 0:
                self._sug_lb.selection_clear(0, "end")
                self._sug_lb.selection_set(idx)
                self._sug_lb.activate(idx)
            return "break"
        except Exception:
            pass
    def _parse_preco_estoque(self, valor) -> float:
        try:
            if isinstance(valor, (int, float)):
                return float(valor)
            s = str(valor or '').strip().replace('R$', '').replace(' ', '')
            if ',' in s and '.' in s:
                s = s.replace('.', '').replace(',', '.')
            else:
                s = s.replace(',', '.')
            return float(s or 0)
        except Exception:
            return 0.0

    def _editar_item_estoque(self):
        """Edita nome, categoria, quantidade e preço do item selecionado."""
        try:
            import tkinter as tk
            from tkinter import ttk, messagebox
            tree = getattr(self, 'tree_estoque', None)
            if tree is None:
                messagebox.showerror('Erro', 'A lista do estoque não foi encontrada.')
                return
            sel = tree.selection()
            if not sel:
                messagebox.showwarning('Atenção', 'Selecione um item do estoque para editar.')
                return
            vals = tree.item(sel[0], 'values')
            if not vals or len(vals) < 5:
                messagebox.showwarning('Atenção', 'Não consegui ler os dados do item selecionado.')
                return
            item_id = int(vals[0])
            top = tk.Toplevel(self)
            top.title(f'Editar item do estoque — ID {item_id}')
            top.geometry('520x300')
            try:
                top.transient(self); top.grab_set()
            except Exception:
                pass

            frm = ttk.Frame(top, padding=14)
            frm.pack(fill='both', expand=True)
            frm.columnconfigure(1, weight=1)
            var_nome = tk.StringVar(value=str(vals[1] or ''))
            var_cat = tk.StringVar(value=str(vals[2] or ''))
            var_qtde = tk.StringVar(value=str(vals[3] or '0'))
            var_preco = tk.StringVar(value=str(vals[4] or '0').replace('R$', '').strip())

            campos = [
                ('Nome do item:', var_nome),
                ('Categoria:', var_cat),
                ('Quantidade:', var_qtde),
                ('Preço:', var_preco),
            ]
            entries = []
            for row, (label, var) in enumerate(campos):
                ttk.Label(frm, text=label).grid(row=row, column=0, sticky='w', padx=(0, 8), pady=7)
                ent = ttk.Entry(frm, textvariable=var)
                ent.grid(row=row, column=1, sticky='ew', pady=7)
                entries.append(ent)
            try:
                entries[0].focus_set()
            except Exception:
                pass

            def salvar_edicao():
                nome = var_nome.get().strip()
                cat = var_cat.get().strip() or 'Outros'
                if not nome:
                    messagebox.showwarning('Atenção', 'Digite o nome do item.', parent=top)
                    return
                try:
                    qtde = int(str(var_qtde.get()).strip().replace('.', '').replace(',', '') or '0')
                except Exception:
                    qtde = 0
                if qtde < 0:
                    qtde = 0
                preco = self._parse_preco_estoque(var_preco.get())
                try:
                    with self.db._connect() as con:
                        cur = con.cursor()
                        cur.execute('UPDATE estoque SET item=?, categoria=?, qtde=?, preco=? WHERE id=?',
                                    (nome, cat, int(qtde), float(preco), int(item_id)))
                        con.commit()
                    try:
                        self._refresh_estoque()
                    except Exception:
                        pass
                    top.destroy()
                    messagebox.showinfo('Estoque', 'Item atualizado com sucesso!')
                except Exception as e:
                    messagebox.showerror('Erro', f'Falha ao atualizar item:\n{e}', parent=top)

            btns = ttk.Frame(frm)
            btns.grid(row=5, column=0, columnspan=2, sticky='e', pady=(16, 0))
            ttk.Button(btns, text='Cancelar', command=top.destroy).pack(side='right')
            ttk.Button(btns, text='Salvar alteração', style='Primary.TButton', command=salvar_edicao).pack(side='right', padx=(0, 8))
            top.bind('<Return>', lambda e: salvar_edicao())
            top.bind('<Escape>', lambda e: top.destroy())
        except Exception as e:
            try:
                from tkinter import messagebox
                messagebox.showerror('Erro', f'Falha ao editar item do estoque:\n{e}')
            except Exception:
                pass

    def _imprimir_estoque(self):
        """Gera um HTML para imprimir todos os itens do estoque com preço."""
        try:
            import os, webbrowser, html
            from tkinter import filedialog, messagebox
            with self.db._connect() as con:
                cur = con.cursor()
                cur.execute('SELECT item, categoria, qtde, preco FROM estoque ORDER BY categoria, item')
                rows = cur.fetchall()
            if not rows:
                messagebox.showwarning('Estoque', 'Não há itens cadastrados no estoque.')
                return
            total_custo = 0.0
            linhas = []
            for item, cat, qtde, preco in rows:
                try:
                    qt = int(qtde or 0)
                except Exception:
                    qt = 0
                try:
                    pr = float(preco or 0)
                except Exception:
                    pr = 0.0
                subtotal = qt * pr
                total_custo += subtotal
                linhas.append(
                    '<tr>'
                    f'<td>{html.escape(str(cat or ""))}</td>'
                    f'<td>{html.escape(str(item or ""))}</td>'
                    f'<td class="num">{qt}</td>'
                    f'<td class="num">R$ {pr:,.2f}</td>'
                    f'<td class="num">R$ {subtotal:,.2f}</td>'
                    '</tr>'
                )
            hoje = datetime.now().strftime('%d/%m/%Y %H:%M')
            html_doc = f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<title>Estoque - Mecânica do Jairo</title>
<style>
@page {{ margin: 12mm; }}
body {{ font-family: Arial, Helvetica, sans-serif; color:#111827; margin:0; padding:16px; }}
h1 {{ margin:0 0 4px; font-size:22px; }}
.sub {{ color:#6b7280; margin-bottom:14px; }}
table {{ width:100%; border-collapse:collapse; font-size:12px; }}
th, td {{ border:1px solid #d1d5db; padding:6px 7px; }}
th {{ background:#f3f4f6; text-align:left; }}
.num {{ text-align:right; white-space:nowrap; }}
tfoot td {{ font-weight:bold; background:#f9fafb; }}
.print {{ margin:0 0 12px; }}
@media print {{ .print {{ display:none; }} body {{ padding:0; }} }}
</style>
</head>
<body>
<button class="print" onclick="window.print()">Imprimir estoque</button>
<h1>Estoque - Mecânica do Jairo</h1>
<div class="sub">Gerado em {hoje} • {len(rows)} itens</div>
<table>
<thead><tr><th>Categoria</th><th>Item</th><th class="num">Qtde</th><th class="num">Preço</th><th class="num">Total</th></tr></thead>
<tbody>{''.join(linhas)}</tbody>
<tfoot><tr><td colspan="4" class="num">Total estimado do estoque</td><td class="num">R$ {total_custo:,.2f}</td></tr></tfoot>
</table>
<script>setTimeout(function(){{ window.print(); }}, 500);</script>
</body>
</html>"""
            fname = filedialog.asksaveasfilename(
                title='Salvar lista de estoque',
                defaultextension='.html',
                filetypes=[('HTML', '*.html')],
                initialfile=f'ESTOQUE_{datetime.now().strftime("%Y%m%d_%H%M")}.html'
            )
            if not fname:
                return
            with open(fname, 'w', encoding='utf-8') as f:
                f.write(html_doc)
            webbrowser.open_new_tab('file:///' + os.path.abspath(fname).replace('\\', '/'))
            messagebox.showinfo('Estoque', 'Lista do estoque aberta no navegador. Se não imprimir sozinho, aperte Ctrl+P.')
        except Exception as e:
            try:
                from tkinter import messagebox
                messagebox.showerror('Erro', f'Falha ao imprimir estoque:\n{e}')
            except Exception:
                pass

    def _excluir_produto_estoque(self):
        """
        Exclui o item selecionado do estoque com confirmação e atualização da lista.
        """
        try:
            tree = getattr(self, "tree_estoque", None)
            if tree is None:
                from tkinter import messagebox
                messagebox.showerror("Erro", "A lista do estoque (tree_estoque) não foi encontrada.")
                return

            sel = tree.selection()
            if not sel:
                from tkinter import messagebox
                messagebox.showwarning("Atenção", "Selecione um item do estoque.")
                return

            iid = sel[0]
            vals = tree.item(iid, "values")
            if not vals or len(vals) < 1:
                from tkinter import messagebox
                messagebox.showwarning("Atenção", "Não consegui ler o ID do item selecionado.")
                return

            try:
                _id = int(vals[0])
                _nome = vals[1] if len(vals) > 1 else "item"
            except Exception:
                from tkinter import messagebox
                messagebox.showwarning("Atenção", "ID inválido na primeira coluna.")
                return

            from tkinter import messagebox
            if not messagebox.askyesno("Confirmar exclusão",
                                       f"Excluir definitivamente o produto:\n\nID {_id} • {_nome}\n\nEssa ação não pode ser desfeita."):
                return

            db = getattr(self, "db", None)
            if db is None or not hasattr(db, "_connect"):
                messagebox.showerror("Erro", "Conexão com o banco não disponível (self.db._connect ausente).")
                return

            try:
                import sqlite3
                with self.db._connect() as con:
                    cur = con.cursor()
                    cur.execute("DELETE FROM estoque WHERE id = ?", (_id,))
                    con.commit()
            except sqlite3.IntegrityError as e:
                messagebox.showerror("Não foi possível excluir",
                                     f"O item pode estar vinculado a outra tabela.\n\nDetalhes: {e}")
                return
            except Exception as e:
                messagebox.showerror("Erro", f"Falha ao excluir no banco:\n{e}")
                return

            try:
                if hasattr(self, "_refresh_estoque"):
                    self._refresh_estoque()
                elif hasattr(self, "_carregar_estoque"):
                    self._carregar_estoque()
                elif hasattr(self, "_load_estoque"):
                    self._load_estoque()
                else:
                    try:
                        tree.delete(iid)
                    except Exception:
                        pass
            except Exception:
                pass

        except Exception:
            import traceback; traceback.print_exc()

class BuscarEditarOS(tk.Toplevel):
    def __init__(self, master, db):
        super().__init__(master)
        self.title('Buscar / Editar OS')
        self.geometry('900x520')
        self.db = db
        self._baixas_sessao = []  # [(item, qtde)] baixados nesta sessão
        pad = dict(padx=6, pady=6)

        top = ttk.Frame(self, padding=10)
        top.pack(fill='x')
        ttk.Label(top, text='Buscar por Nome ou Placa:').pack(side='left')
        self.ent_busca = ttk.Entry(top, width=30)
        self.ent_busca.pack(side='left', padx=6)
        ttk.Button(top, text='Buscar', command=self._buscar).pack(side='left')
        ttk.Button(top, text='Abrir descrição', command=self._abrir_descricao).pack(side='right')
        ttk.Button(top, text='Selecionar banco…', command=self._trocar_banco).pack(side='right', padx=6)
        ttk.Button(top, text='Editar na aba Cadastro', command=self._editar_na_cadastro).pack(side='right', padx=6)
        ttk.Button(top, text='Atualizar KM/Intervalo', command=self._editar_km).pack(side='right', padx=6)

        cols = ('id','nome','marca','modelo','placa','km_atual','proxima','data')
        self.tree = ttk.Treeview(self, columns=cols, show='headings', height=18)
        self.tree.pack(fill='both', expand=True, padx=10, pady=8)
        try:
            self.tree.bind('<Double-1>', lambda e: self._editar_na_cadastro())
        except Exception:
            pass
        headers = ['ID','Cliente','Marca','Modelo','Placa','KM atual(troca de óleo)','Próxima','Data']
        for c,h in zip(cols, headers):
            self.tree.heading(c, text=h)
        self.tree.column('id', width=60, anchor='center')
        self.tree.column('nome', width=180)
        self.tree.column('marca', width=100)
        self.tree.column('modelo', width=160)
        self.tree.column('placa', width=90, anchor='center')
        self.tree.column('km_atual', width=90, anchor='e')
        self.tree.column('proxima', width=90, anchor='e')
        self.tree.column('data', width=100, anchor='center')

        self._buscar()
    def _editar_completo(self):
        sid = self._get_sel_id()
        if sid is None: return
        EditorCompletoOS(self, self.db, sid)


    def _editar_na_cadastro(self):
        sid = self._get_sel_id()
        if sid is None:
            return
        try:
            self.master.abrir_os_na_cadastro(sid)
            try:
                self.destroy()
            except Exception:
                pass
        except Exception as e:
            from tkinter import messagebox
            messagebox.showerror('Erro', f'Falha ao abrir na aba Cadastro:\n{e}')

    def _trocar_banco(self):
        try:
            from tkinter import filedialog, messagebox
            path = filedialog.askopenfilename(title='Selecione o banco de dados (oficina.db)', filetypes=[('SQLite DB','*.db'),('Todos','*.*')])
            if path:
                self.master.db.db_path = path
                self._buscar()
        except Exception as e:
            messagebox.showerror('Erro', f'Não foi possível trocar o banco:\n{e}')

    def _buscar(self):

        termo = self.ent_busca.get().strip()
        rows = self.db.buscar(termo or '')
        # limpar
        for i in self.tree.get_children():
            self.tree.delete(i)
        for r in rows:
            self.tree.insert('', 'end', values=r)

    def _get_sel_id(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning('Atenção','Selecione uma OS na lista.')
            return None
        vals = self.tree.item(sel[0], 'values')
        return int(vals[0])  # id

    def _abrir_descricao(self):
        sid = self._get_sel_id()
        if sid is None: return
        # Carrega dados mínimos para a JanelaDescricao
        with self.db._connect() as con:
            cur = con.cursor()
            cur.execute("""SELECT s.descricao, s.km_atual, s.intervalo_km, s.proxima_manut_km, s.data
                           FROM servicos s WHERE s.id=?""", (sid,))
            row = cur.fetchone()
        if not row:
            messagebox.showerror('Erro', 'OS não encontrada.'); return
        descricao, km_atual, intervalo, proxima_km, data_str = row
        # Reaproveita a janela já existente (se houver) ou cria básica
        try:
            JanelaDescricao(self.master, self.db, sid, descricao or '', km_atual or 0, intervalo or 0, proxima_km or 0, data_str or '')
        except Exception:
            win = tk.Toplevel(self); win.title(f'Descrição — OS {sid}')
            txt = tk.Text(win, width=80, height=20); txt.pack(fill='both', expand=True)
            txt.insert('1.0', descricao or '')

    def _editar_km(self):
        sid = self._get_sel_id()
        if sid is None: return
        # Buscar dados atuais
        with self.db._connect() as con:
            cur = con.cursor()
            cur.execute("SELECT km_atual, intervalo_km, proxima_manut_km FROM servicos WHERE id=?", (sid,))
            row = cur.fetchone()
        if not row:
            messagebox.showerror('Erro', 'OS não encontrada.'); return
        km_atual, intervalo_km, proxima = [int(x or 0) for x in row]

        win = tk.Toplevel(self); win.title(f'Editar KM — OS {sid}'); win.geometry('360x180')
        pad = dict(padx=6, pady=6)
        ttk.Label(win, text='KM atual(troca de óleo):').grid(row=0, column=0, sticky='w', **pad)
        ent_km = ttk.Entry(win, width=12); ent_km.grid(row=0, column=1, **pad); ent_km.insert(0, str(km_atual))

        ttk.Label(win, text='Intervalo (km):').grid(row=1, column=0, sticky='w', **pad)
        cmb_int = ttk.Combobox(win, values=['0','5000','7500','10000','15000'], state='readonly', width=12)
        cmb_int.grid(row=1, column=1, **pad); cmb_int.set(str(intervalo_km))

        lbl_prev = ttk.Label(win, text=f'Próxima manutenção: {proxima} km'); lbl_prev.grid(row=2, column=0, columnspan=2, **pad)

        def recalc(*_):
            try:
                k = int(ent_km.get() or 0)
                i = int(cmb_int.get() or 0)
                p = k + i if k >= 0 and i > 0 else k
                lbl_prev.config(text=f'Próxima manutenção: {p} km')
            except Exception:
                pass
        ent_km.bind('<KeyRelease>', recalc); cmb_int.bind('<<ComboboxSelected>>', recalc)

        def salvar():
            try:
                k = int(ent_km.get() or 0); i = int(cmb_int.get() or 0)
                p = k + i if k >= 0 and i > 0 else k
                self.db.update_servico_km(sid, k, i, p)
                messagebox.showinfo('OK', 'KM/intervalo atualizados!')
                self._buscar(); win.destroy()
            except Exception as e:
                messagebox.showerror('Erro', f'Falha ao atualizar:\\n{e}')
        ttk.Button(win, text='Salvar', command=salvar).grid(row=3, column=0, columnspan=2, pady=10)
class EditorCompletoOS(tk.Toplevel):
    def __init__(self, master, db: Database, servico_id: int):
        super().__init__(master)
        self.title(f'Editar OS #{servico_id} (completo)')
        self.geometry('980x640')
        self.db = db
        self.servico_id = servico_id

        self._baixas_sessao = []  # [(categoria,item,qt)] baixados nesta sessão
        try:
            self.protocol('WM_DELETE_WINDOW', self._on_close_edit)
        except Exception:
            pass
        from tkinter import simpledialog

        top = ttk.Frame(self, padding=10); top.pack(fill='x')
        self.vars = {k: tk.StringVar() for k in ['nome','telefone','marca','modelo','placa','ano','km_atual','intervalo']}

        form = ttk.Frame(self, padding=6); form.pack(fill='x')
        def add_row(r, label, key, w=24):
            ttk.Label(form, text=label).grid(row=r, column=0, sticky='w', padx=6, pady=4)
            ttk.Entry(form, textvariable=self.vars[key], width=w).grid(row=r, column=1, sticky='w', padx=6, pady=4)

        add_row(0, 'Nome', 'nome', 36)
        ttk.Label(form, text='Telefone').grid(row=0, column=3, sticky='w', padx=6, pady=4)
        ttk.Entry(form, textvariable=self.vars['telefone'], width=18).grid(row=0, column=4, sticky='w', padx=6, pady=4)

        ttk.Label(form, text='Marca').grid(row=1, column=0, sticky='w', padx=6, pady=4)
        self.cmb_edit_marca = ttk.Combobox(form, textvariable=self.vars['marca'], values=list(BRANDS.keys()), state='normal', width=18)
        self.cmb_edit_marca.grid(row=1, column=1, sticky='w', padx=6, pady=4)
        self.cmb_edit_marca.bind('<<ComboboxSelected>>', lambda e: self._load_modelos_edit())
        self.cmb_edit_marca.bind('<FocusOut>', lambda e: self._load_modelos_edit(escolher_primeiro=False))
        ttk.Label(form, text='Veículo/Modelo').grid(row=1, column=3, sticky='w', padx=6, pady=4)
        self.cmb_edit_modelo = ttk.Combobox(form, textvariable=self.vars['modelo'], values=[], state='normal', width=24)
        self.cmb_edit_modelo.grid(row=1, column=4, sticky='w', padx=6, pady=4)
        ttk.Label(form, text='Placa').grid(row=2, column=0, sticky='w', padx=6, pady=4)
        ttk.Entry(form, textvariable=self.vars['placa'], width=12).grid(row=2, column=1, sticky='w', padx=6, pady=4)
        ttk.Label(form, text='Ano').grid(row=2, column=3, sticky='w', padx=6, pady=4)
        ttk.Entry(form, textvariable=self.vars['ano'], width=10).grid(row=2, column=4, sticky='w', padx=6, pady=4)

        kmfrm = ttk.Frame(self, padding=6); kmfrm.pack(fill='x')
        ttk.Label(kmfrm, text='KM atual(troca de óleo)').pack(side='left'); ttk.Entry(kmfrm, textvariable=self.vars['km_atual'], width=10).pack(side='left', padx=6)
        ttk.Label(kmfrm, text='Intervalo (km)').pack(side='left')
        self.cmb_intervalo = ttk.Combobox(kmfrm, values=['0','5000','7500','10000','15000'], width=10, state='readonly')
        self.cmb_intervalo.pack(side='left', padx=6)
        self.cmb_intervalo.bind('<<ComboboxSelected>>', lambda e: self._recalc_proxima())
        self.lbl_prev = ttk.Label(kmfrm, text='Próxima: —'); self.lbl_prev.pack(side='left', padx=12)

        ttk.Label(self, text='Descrição do serviço').pack(anchor='w', padx=10)
        self.txt_desc = tk.Text(self, height=6); self.txt_desc.pack(fill='x', padx=10, pady=6)

        cols = ('categoria','item','qtde','valor_unit')
        frame_items = ttk.Frame(self, padding=4); frame_items.pack(fill='both', expand=True)
        self.tree = ttk.Treeview(frame_items, columns=cols, show='headings', height=10)
        for c,h,w,a in [('categoria','Categoria',150,'w'),('item','Item',380,'w'),('qtde','Qtde',60,'e'),('valor_unit','R$ Unit',90,'e')]:
            self.tree.heading(c, text=h); self.tree.column(c, width=w, anchor=a)
        self.tree.pack(side='left', fill='both', expand=True, padx=(10,0), pady=6)
        sb = ttk.Scrollbar(frame_items, orient='vertical', command=self.tree.yview); sb.pack(side='left', fill='y'); self.tree.configure(yscrollcommand=sb.set)

        btns = ttk.Frame(frame_items); btns.pack(side='left', fill='y', padx=8)
        ttk.Button(btns, text='Adicionar', command=self._add_item).pack(fill='x', pady=4)
        ttk.Button(btns, text='Editar', command=self._edit_item).pack(fill='x', pady=4)
        ttk.Button(btns, text='Remover', command=self._del_item).pack(fill='x', pady=4)

        rod = ttk.Frame(self, padding=10); rod.pack(fill='x')
        ttk.Button(rod, text='Salvar', command=self._salvar).pack(side='right')
        ttk.Button(rod, text='Fechar', command=self.destroy).pack(side='right', padx=6)

        self._carregar()


    def _load_modelos_edit(self, escolher_primeiro=True):
        try:
            marca = (self.vars['marca'].get() or 'Outros').strip()
            modelos = BRANDS.get(marca, BRANDS.get('Outros', []))
            self.cmb_edit_modelo['values'] = modelos
            if escolher_primeiro and modelos and not (self.vars['modelo'].get() or '').strip():
                self.vars['modelo'].set(modelos[0])
        except Exception:
            pass

    def _carregar(self):
        row = self.db.get_servico_full(self.servico_id)
        if not row:
            messagebox.showerror('Erro', 'OS não encontrada.'); self.destroy(); return
        (sid, veic_id, descricao, km_atual, intervalo, proxima, data,
         cliente_id, marca, modelo, placa, ano, v_km_atual,
         nome, telefone, km_troca_corr, km_corr_trocada, km_corr_proxima) = row
        self.vars['nome'].set(nome or ''); self.vars['telefone'].set(telefone or '')
        self.vars['marca'].set(marca or ''); self.vars['modelo'].set(modelo or '')
        try:
            self._load_modelos_edit(escolher_primeiro=False)
        except Exception:
            pass
        self.vars['placa'].set(placa or ''); self.vars['ano'].set(ano or '')
        self.vars['km_atual'].set(str(km_atual or v_km_atual or 0))
        self.vars['intervalo'].set(str(intervalo or 0)); self.cmb_intervalo.set(str(intervalo or 0))
        self.txt_desc.delete('1.0','end'); self.txt_desc.insert('1.0', descricao or '')
        itens = self.db.get_itens_servico(self.servico_id)
        for it in itens:
            if len(it) >= 5 and isinstance(it[0], int):
                _, cat, item, qt, vu = it[:5]
            else:
                cat, item, qt, vu = it[:4]
            self.tree.insert('', 'end', values=(cat or '', item or '', int(qt or 0), float(vu or 0.0)))
        self._recalc_proxima()

    def _recalc_proxima(self):
        try:
            k = int(self.vars['km_atual'].get() or 0)
            i = int(self.cmb_intervalo.get() or self.vars['intervalo'].get() or 0)
            p = k + i if k >= 0 and i > 0 else k
            self.lbl_prev.config(text=f'Próxima: {p} km')
        except Exception:
            pass

    def _add_item(self):
        from tkinter import simpledialog, messagebox
        cat = simpledialog.askstring('Categoria', 'Categoria:', initialvalue='') or ''
        item = simpledialog.askstring('Item', 'Item:', initialvalue='') or ''
        qt = simpledialog.askinteger('Quantidade', 'Qtde:', initialvalue=1, minvalue=1) or 1
        vu = simpledialog.askfloat('Valor unitário', 'R$ unit:', initialvalue=0.0, minvalue=0.0) or 0.0
        if not item:
            messagebox.showwarning('Atenção', 'Informe o item.'); return
        
        # NÃO baixa no estoque aqui (apenas quando o item for selecionado via Busca)
        self.tree.insert('', 'end', values=(cat, item, qt, vu))
    def _edit_item(self):
        from tkinter import simpledialog
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning('Atenção', 'Selecione um item.'); return
        vals = list(self.tree.item(sel[0], 'values'))
        cat = simpledialog.askstring('Categoria', 'Categoria:', initialvalue=vals[0]) or vals[0]
        item = simpledialog.askstring('Item', 'Item:', initialvalue=vals[1]) or vals[1]
        qt = simpledialog.askinteger('Quantidade', 'Qtde:', initialvalue=int(vals[2])) or int(vals[2])
        vu = simpledialog.askfloat('Valor unitário', 'R$ unit:', initialvalue=float(vals[3])) or float(vals[3])
        self.tree.item(sel[0], values=(cat, item, qt, vu))

    def _del_item(self):
        sel = self.tree.selection()
        if not sel:
            return
        iid = sel[0]
        vals = list(self.tree.item(iid, 'values'))
        try:
            cat, item, qt = vals[0], vals[1], int(vals[2])
        except Exception:
            cat, item, qt = '', '', 0

        try:
            total_baixado = 0
            for c,i,q in list(self._baixas_sessao):
                if (c or '') == (cat or '') and (i or '') == (item or ''):
                    total_baixado += int(q)
            if total_baixado > 0 and qt > 0:
                repor_qt = min(qt, total_baixado)
                try:
                    self.db.estoque_repor(item, repor_qt, cat)
                except Exception:
                    pass
                resto = []
                a_repor = repor_qt
                for c,i,q in self._baixas_sessao:
                    if a_repor > 0 and (c or '') == (cat or '') and (i or '') == (item or ''):
                        if q <= a_repor:
                            a_repor -= q
                            continue
                        else:
                            resto.append((c,i,q - a_repor))
                            a_repor = 0
                    else:
                        resto.append((c,i,q))
                self._baixas_sessao = resto
        except Exception:
            pass

        self.tree.delete(iid)

    def _salvar(self):
        try:
            nome = self.vars['nome'].get().strip()
            tel = self.vars['telefone'].get().strip() or None
            marca = self.vars['marca'].get().strip()
            modelo = self.vars['modelo'].get().strip()
            placa = self.vars['placa'].get().strip().upper()
            ano = self.vars['ano'].get().strip()
            km = int(self.vars['km_atual'].get() or 0)
            intervalo = int(self.cmb_intervalo.get() or self.vars['intervalo'].get() or 0)
            proxima = km + intervalo if km >= 0 and intervalo > 0 else km
            desc = self.txt_desc.get('1.0','end').strip()

            row = self.db.get_servico_full(self.servico_id)
            _, veic_id, _, _, _, _, _, _, _, _, _, _, _, _, _, km_troca_corr, km_corr_trocada, km_corr_proxima = row
            cliente_id = self.db.upsert_cliente(nome, tel)
            veic_id_new = self.db.upsert_veiculo(cliente_id, marca, modelo, placa, ano, km, km_troca_corr, km_corr_trocada, km_corr_proxima)

            with self.db._connect() as con:
                cur = con.cursor()
                cur.execute("UPDATE servicos SET veiculo_id=? WHERE id=?", (veic_id_new, int(self.servico_id)))
                con.commit()

            self.db.update_servico_fields(self.servico_id, desc, km, intervalo, proxima)

            itens = [self.tree.item(i, 'values') for i in self.tree.get_children()]
            itens = [(v[0], v[1], int(v[2]), float(v[3])) for v in itens]
            self.db.replace_itens_servico(self.servico_id, itens)

            try:
                self._baixas_sessao.clear()
            except Exception:
                pass
            messagebox.showinfo('OK', 'OS atualizada com sucesso!')
            self.destroy()
        except Exception as e:
            messagebox.showerror('Erro', f'Falha ao salvar: {e}')


    def _on_close_edit(self):
        # Fecha a janela e desfaz baixas pendentes desta sessão (caso não tenha salvado)
        try:
            if getattr(self, '_baixas_sessao', None):
                for cat, item, qt in self._baixas_sessao:
                    try:
                        self.db.estoque_repor(item, int(qt), cat)
                    except Exception:
                        pass
                try:
                    self._baixas_sessao.clear()
                except Exception:
                    pass
        except Exception:
            pass
        try:
            self.destroy()
        except Exception:
            pass
class JanelaDescricao(tk.Toplevel):
    def __init__(self, master: App, db: Database, servico_id: int, descricao: str, km_atual: int, intervalo: int, proxima_km: int, data_str: str):
        super().__init__(master)
        self.title(f'Descrição do serviço — ID {servico_id}')
        self.geometry('1060x680')
        self.db = db; self.servico_id = servico_id
        self.master_app = master

        pad = dict(padx=6, pady=6)
        top = ttk.Frame(self, padding=10)
        top.pack(fill='x')
        # KM atual (apenas para mostrar na OS)
        try:
            km_visita = safe_int(getattr(self.master_app, 'var_km_visita', None).get() if hasattr(self.master_app, 'var_km_visita') else '0')
        except Exception:
            km_visita = 0
        ttk.Label(top, text=f'Data: {data_str}  ·  KM atual: {km_visita}  ·  Intervalo (km): {intervalo}  ·  Próxima: {proxima_km} km', style='H2.TLabel').pack(anchor='w')

        
        # Barra de ferramentas da descrição (Busca)
        toolbar = ttk.Frame(self, style='Card.TFrame')
        toolbar.pack(fill='x', padx=10, pady=(0, 6))
        self.badge_status = ttk.Label(toolbar, text='—', style='Badge.Ok.TLabel')
        self.badge_status.pack(side='left', padx=(0,8))
        ttk.Button(toolbar, text='Imprimir', style='Primary.TButton', command=self._export_html).pack(side='right', padx=4)

        # Define o badge conforme KM atual(troca de óleo) e próxima manutenção
        try:
            ok = (not proxima_km) or (km_atual < proxima_km)
            if ok:
                restantes = max(0, (proxima_km or 0) - (km_atual or 0))
                self.badge_status.configure(text=f'🟢 Manutenção OK — faltam {restantes} km', style='Badge.Ok.TLabel')
            else:
                excedido = max(0, (km_atual or 0) - (proxima_km or 0))
                self.badge_status.configure(text=f'🔴 Manutenção vencida — excedido {excedido} km', style='Badge.Warn.TLabel')
        except Exception:
            pass

        body = ttk.Frame(self)
        body.pack(fill='both', expand=True)
        left = ttk.Frame(body)
        left.pack(side='left', fill='both', expand=True, padx=4, pady=8)
        ttk.Label(left, text='Descrição do serviço').pack(anchor='w')
        self.txt = tk.Text(left, wrap='word', font=(self.master_app.font_family, self.master_app.font_base))
        self.txt.pack(fill='both', expand=True, pady=(4,8))
        self.txt.insert('1.0', descricao or '')

        right = ttk.Frame(body)
        right.pack(side='left', fill='y', padx=4, pady=8)
        ttk.Label(right, text='Itens do serviço').pack(anchor='w')
        cols = ('categoria', 'item', 'qtde', 'unit', 'total')
        self.tree_itens = ttk.Treeview(right, columns=cols, show='headings', height=3)
        self.tree_itens.pack(fill='y', expand=False)
        for c, label in zip(cols, ['Categoria', 'Item', 'Qtde', 'Unitário (R$)', 'Total (R$)']):
            self.tree_itens.heading(c, text=label)
        self.tree_itens.column('categoria', width=110)
        self.tree_itens.column('item', width=180)
        self.tree_itens.column('qtde', width=60, anchor='center')
        self.tree_itens.column('unit', width=90, anchor='e')
        self.tree_itens.column('total', width=90, anchor='e')
        self.lbl_total = ttk.Label(right, text='Total: R$ 0,00', style='H2.TLabel'); self.lbl_total.pack(anchor='e', pady=6)
        self._load_itens()

        btns = ttk.Frame(self)
        btns.pack(fill='x', pady=2)
        ttk.Button(btns, text='Salvar descrição', style='Primary.TButton', command=self._salvar).pack(side='left', padx=6)
        ttk.Button(btns, text='Exportar OS (HTML)', style='Ghost.TButton', command=self._export_html).pack(side='left', padx=6)
        ttk.Button(btns, text='Imprimir (Premium PDF)', style='Primary.TButton', command=self._export_html_premium_pdf).pack(side='left', padx=6)

        ttk.Button(btns, text='Excluir OS', style='Danger.TButton', command=self._excluir_os).pack(side='left', padx=6)
        ttk.Button(btns, text='Fechar', style='Ghost.TButton', command=self.destroy).pack(side='right', padx=6)

    def _load_itens(self):
        for i in self.tree_itens.get_children():
            self.tree_itens.delete(i)
        total = 0.0
        for (_id, cat, item, qt, unit) in self.db.get_itens_servico(self.servico_id):
            t = float(qt) * float(unit); total += t
            self.tree_itens.insert('', 'end', values=(cat, item, qt, f"{unit:.2f}", f"{t:.2f}"))
        self.lbl_total.config(text=f"Total: R$ {total:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))

    def _salvar(self):
        texto = self.txt.get('1.0', 'end').strip()
        try:
            with self.db._connect() as con:
                cur = con.cursor(); cur.execute("UPDATE servicos SET descricao=? WHERE id=?", (texto, self.servico_id)); con.commit()
            messagebox.showinfo('OK', 'Descrição atualizada!')
        except Exception as e:
            messagebox.showerror('Erro', f'Falha ao salvar descrição:\n{e}')

    def _export_html(self):
        with self.db._connect() as con:
            cur = con.cursor()
            cur.execute("SELECT id, veiculo_id, descricao, km_atual, intervalo_km, proxima_manut_km, data FROM servicos WHERE id=?", (self.servico_id,))
            sid, veiculo_id, descricao, km_atual, intervalo, proxima_km, data_str = cur.fetchone()
            cur.execute("""SELECT c.nome, c.telefone, v.marca, v.modelo, v.placa, v.ano, v.km_corr_proxima
                FROM veiculos v JOIN clientes c ON c.id = v.cliente_id
                WHERE v.id = ?
            """, (veiculo_id,))
            row = cur.fetchone()
            if row: nome, tel, marca, modelo, placa, ano, km_corr_prox = row
            else: nome = tel = marca = modelo = placa = ano = '—'
        itens = self.db.get_itens_servico(self.servico_id)
        itens_fmt = [dict(categoria=cat, item=item, qtde=qt, valor_unit=unit) for (_id, cat, item, qt, unit) in itens]
        # KM atual do formulário (se existir)
        try:
            km_visita = safe_int(getattr(self.master_app, 'var_km_visita', None).get() if hasattr(self.master_app, 'var_km_visita') else '0')
        except Exception:
            km_visita = 0

        html = gerar_html_os('Ordem de Serviço', LOGO_PATH if os.path.exists(LOGO_PATH) else None,
                             nome, tel, marca, modelo, placa, ano, data_str,
                             km_atual, intervalo, proxima_km, km_corr_prox, self.txt.get('1.0', 'end').strip(), itens_fmt, km_visita=km_visita)
        fname = filedialog.asksaveasfilename(title='Salvar OS em HTML', defaultextension='.html', filetypes=[('HTML', '*.html')], initialfile=f'OS_{placa}_{sid}.html')
        if not fname: return
        try:
            with open(fname, 'w', encoding='utf-8') as f: f.write(html)
            webbrowser.open_new_tab(f'file://{fname}')
        except Exception as e:
            messagebox.showerror('Erro', f'Falha ao salvar/abrir HTML:\n{e}')
        def _export_html_premium(self):
            """Exporta a OS em HTML com tema premium (cores e layout diferenciados)."""
            from tkinter import filedialog, messagebox
            import os, webbrowser
            try:
                with self.db._connect() as con:
                    cur = con.cursor()
                    cur.execute("SELECT id, veiculo_id, descricao, km_atual, intervalo, proxima_manut_km, data FROM servicos WHERE id=?", (self.servico_id,))
                    sid, veiculo_id, descricao, km_atual, intervalo, proxima_km, data_str = cur.fetchone()
                    cur.execute("""SELECT c.nome, c.telefone, v.marca, v.modelo, v.placa, v.ano, v.km_corr_proxima
                        FROM veiculos v JOIN clientes c ON c.id = v.cliente_id
                        WHERE v.id = ?
                    """, (veiculo_id,))
                    row = cur.fetchone()
                    if row: nome, tel, marca, modelo, placa, ano, km_corr_prox = row
                    else: nome = tel = marca = modelo = placa = ano = '—'
                itens = self.db.get_itens_servico(self.servico_id)
                itens_fmt = [dict(categoria=cat, item=item, qtde=qt, valor_unit=unit) for (_id, cat, item, qt, unit) in itens]
                # KM atual do formulário (se existir)
                try:
                    km_visita = safe_int(getattr(self.master_app, 'var_km_visita', None).get() if hasattr(self.master_app, 'var_km_visita') else '0')
                except Exception:
                    km_visita = 0

                html = gerar_html_os_premium('Ordem de Serviço', _resolve_logo_path(),
                                             nome, tel, marca, modelo, placa, ano, data_str,
                                             km_atual, intervalo, proxima_km, km_corr_prox, self.txt.get('1.0', 'end').strip(), itens_fmt, km_visita=km_visita)
                fname = filedialog.asksaveasfilename(title='Salvar OS premium (HTML)', defaultextension='.html', filetypes=[('HTML','*.html')], initialfile=f'OS_{placa}_{sid}_premium.html')
                if not fname:
                    return
                with open(fname, 'w', encoding='utf-8') as f:
                    f.write(html)
                webbrowser.open_new_tab('file://' + fname)
            except Exception as e:
                try:
                    messagebox.showerror('Erro', f'Falha ao gerar premium:\n{e}')
                except Exception:
                    print('[export_html_premium] erro:', e)
        

        def _export_html_premium_pdf(self):
            """Gera o HTML premium e tenta salvar direto em PDF. Se não for possível, abre o HTML no navegador."""
            from tkinter import filedialog, messagebox
            import os, tempfile, webbrowser
            try:
                with self.db._connect() as con:
                    cur = con.cursor()
                    cur.execute("SELECT id, veiculo_id, descricao, km_atual, intervalo_km, proxima_manut_km, data FROM servicos WHERE id=?", (self.servico_id,))
                    sid, veiculo_id, descricao, km_atual, intervalo, proxima_km, data_str = cur.fetchone()
                    cur.execute("""SELECT c.nome, c.telefone, v.marca, v.modelo, v.placa, v.ano, v.km_corr_proxima
                        FROM veiculos v JOIN clientes c ON c.id = v.cliente_id
                        WHERE v.id = ?
                    """, (veiculo_id,))
                    row = cur.fetchone()
                    if row: nome, tel, marca, modelo, placa, ano, km_corr_prox = row
                    else: nome = tel = marca = modelo = placa = ano = '—'
                itens = self.db.get_itens_servico(self.servico_id)
                itens_fmt = [dict(categoria=cat, item=item, qtde=qt, valor_unit=unit) for (_id, cat, item, qt, unit) in itens]
                html = gerar_html_os_premium('Ordem de Serviço', _resolve_logo_path(),
                                             nome, tel, marca, modelo, placa, ano, data_str,
                                             km_atual, int(intervalo or 0), proxima_km, km_corr_prox, self.txt.get('1.0', 'end').strip(), itens_fmt)
                # Salva HTML temporário
                temp_dir = tempfile.gettempdir()
                html_path = os.path.join(temp_dir, f"OS_{placa}_{sid}_premium.html")
                with open(html_path, "w", encoding="utf-8") as f:
                    f.write(html)
                # Pergunta onde salvar o PDF
                pdf_sug = f"OS_{placa}_{sid}_premium.pdf"
                pdf_path = filedialog.asksaveasfilename(
                    title='Salvar como PDF',
                    defaultextension='.pdf',
                    filetypes=[('PDF', '*.pdf')],
                    initialfile=pdf_sug
                )
                if not pdf_path:
                    return
                ok = _salvar_pdf_via_navegador(html_path, pdf_path)
                if ok:
                    messagebox.showinfo('Impressão', f'PDF gerado com sucesso:\n{pdf_path}')
                    try:
                        os.startfile(pdf_path)
                    except Exception:
                        pass
                else:
                    webbrowser.open_new_tab('file://' + html_path.replace("\\", "/"))
                    messagebox.showinfo('Impressão', 'Não consegui gerar PDF automático.\nO HTML foi aberto no navegador.\nUse Ctrl+P → Salvar como PDF.')
            except Exception as e:
                try:
                    messagebox.showerror('Erro', f'Falha ao gerar premium PDF:\n{e}')
                except Exception:
                    print('[export_html_premium_pdf] erro:', e)

    def _excluir_os(self):
        if not messagebox.askyesno('Confirmar', f'Excluir a OS (ID {self.servico_id})? Essa ação não pode ser desfeita.'):
            return
        try:
            self.db.delete_servico(self.servico_id)
            messagebox.showinfo('OK', f'OS {self.servico_id} excluída.')
            try:
                self.master_app._do_busca()
            except Exception:
                pass
            self.destroy()
        except Exception as e:
            messagebox.showerror('Erro', f'Falha ao excluir OS:\n{e}')

# ----------------------------- HELPERS ----------------------------- #
def safe_int(s: str, default: int = 0) -> int:
    try: return int(str(s).strip().replace('.', '').replace(',', ''))
    except Exception: return default

def safe_float(s: str, default: float = 0.0) -> float:
    try: return float(str(s).replace(',', '.'))
    except Exception: return default


def gerar_html_os(titulo: str, logo_path: Optional[str], cliente_nome: str, cliente_tel: str,
                  marca: str, modelo: str, placa: str, ano: str, data: str,
                  km_atual: int, intervalo: int, proxima_km: int, proxima_corr_km: Optional[int], descricao: str,
                  itens: Optional[List[Dict[str, Any]]] = None, km_visita: int = 0) -> str:
    """HTML básico com cabeçalho MECÂNICA DO JAIRO e LOGO embutida (base64)."""
    import base64, mimetypes
    from pathlib import Path

    if not logo_path:
        logo_path = _resolve_logo_path()

    # Embute logo
    logo_tag = "<div style='width:180px;height:80px;border:2px dashed #999;color:#666;display:flex;align-items:center;justify-content:center;font-size:12px;'>SEM LOGO</div>"
    try:
        if logo_path:
            lp = Path(logo_path)
            if not lp.is_absolute():
                base_dir = Path(__file__).resolve().parent
                lp = (base_dir / lp).resolve()
            if lp.exists():
                mime, _ = mimetypes.guess_type(str(lp))
                if not mime:
                    mime = "image/png"
                raw = lp.read_bytes()
                b64 = base64.b64encode(raw).decode("ascii")
                logo_tag = f"<img src='data:{mime};base64,{b64}' alt='Logo' style='height:200px;display:block;margin:0;padding:0;display:block;margin:0;padding:0;display:block;margin:0;padding:0; display:block; object-fit:contain; margin:0'>"
    except Exception:
        pass

    safe_desc = (descricao or '').replace('\n', '<br>')

    corr_col = f"<div class='col'><strong>Próxima troca da correia:</strong><br>{proxima_corr_km}</div>" if proxima_corr_km else ""

    itens_rows = ''; total = 0.0
    if itens:
        for it in itens:
            try:
                qt = int(it.get('qtde', 0)); unit = float(it.get('valor_unit', 0.0))
                t = qt * unit; total += t
                itens_rows += f"<tr><td>{it.get('categoria','')}</td><td>{it.get('item','')}</td><td style='text-align:right'>{qt}</td><td style='text-align:right'>{unit:,.2f}</td><td style='text-align:right'>{t:,.2f}</td></tr>"
            except Exception:
                pass

    qr_tag = f"<img src='data:{QR_PIX_MIME};base64,{QR_PIX_B64}' alt='PIX QR' style='height:200px;display:block;'>"

    # --- Data no formato DD/MM/AAAA ---

    _val_data = (locals().get('data_str') or locals().get('data') or '')

    try:

        data_br = datetime.strptime(str(_val_data)[:10], '%Y-%m-%d').strftime('%d/%m/%Y')

    except Exception:

        try:

            data_br = datetime.strptime(str(_val_data).split()[0], '%d/%m/%Y').strftime('%d/%m/%Y')

        except Exception:

            data_br = str(_val_data)

    html = f"""
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            @page {{ margin: 16mm; }}
            body {{ font-family: Arial, Helvetica, sans-serif; margin:0; padding:16mm; color:#111827; }}
            .header {{ display:flex; align-items:flex-start; justify-content:space-between; margin-bottom:0px; }}
            .empresa {{ font-size:13px; line-height:1.45; }}
            .empresa b {{ font-size:16px; }}
            h1,h2,h3 {{ margin:0; }}
            .title {{ margin:12px 0 8px; }}
            .muted {{ color:#555; }}
            table.grid {{ width:100%; border-collapse:collapse; font-size:11px; margin-top:0px; }}
            table.grid th, table.grid td {{ border:1px solid #e5e7eb; padding:4px; }}
            table.grid th {{ background:#f3f4f6; text-align:left;  font-size:10px}}
            .row {{ display:flex; gap:12px; flex-wrap:wrap; }}
            .col {{ flex:1; min-width:180px; }}
        </style>
    </head>
    <body>
        <!-- {__PATCH_VERSION__} -->
        <div class="header" style="display:block; position:relative; padding-right:150px; min-height:0px; margin-bottom:0px;">
    <div class="brandwrap" style="display:flex; flex-direction:column; align-items:flex-start; gap:8px; max-width: calc(100% - 260px);">
        <div class="logo" style="display:block; margin-bottom:0px;">{logo_tag}</div>
    </div>
    <div class="qr" style="position:absolute; right:0; top:0;">{qr_tag}</div>
</div>

        <hr>

        <div class="title">
            <h2>{titulo}</h2>
            <div class="muted">{data_br}</div>
        </div>

        <h2>Cliente</h2>
        <div class="row">
          <div class="col"><strong>Nome:</strong><br>{cliente_nome}</div>
          <div class="col"><strong>Telefone:</strong><br>{cliente_tel}</div>
        </div>

        <h2>Veículo</h2>
        <div class="row">
          <div class="col"><strong>Marca/Modelo:</strong><br>{marca} {modelo}</div>
          <div class="col"><strong>Placa:</strong><br>{placa}</div>
          <div class="col"><strong>Ano:</strong><br>{ano}</div>
        </div>

      <h2>Serviço</h2>
<div class="row">
  <div class="col"><strong>KM atual(troca de óleo):</strong><br>{km_atual}</div>
  <div class="col"><strong>KM atual:</strong><br>{km_visita}</div>
  <div class="col"><strong>Intervalo (km):</strong><br>{intervalo}</div>
  <div class="col"><strong>Próxima manutenção:</strong><br>{proxima_km}</div>
  {corr_col}
</div>


        </div>

        <p style="white-space: pre-wrap; margin-top: 6px;">{safe_desc}</p>

        {f"<h2>Itens</h2><table class='grid'><thead><tr><th>Categoria</th><th>Item</th><th style='text-align:right'>Qtde</th><th style='text-align:right'>Valor unit.</th><th style='text-align:right'>Subtotal</th></tr></thead><tbody>"+itens_rows+f"<tr><td colspan='4' style='text-align:right'><strong>Total</strong></td><td style='text-align:right'><strong>{total:,.2f}</strong></td></tr></tbody></table>" if itens_rows else ""}
    
            <div style="margin-top:40px; text-align:center;">
                <div style="width:60%; margin:0 auto; border-top:1px solid #e5e7eb; padding-top:6px;">
                    Assinatura do cliente
                </div>
                <div class="muted" style="font-size:12px; margin-top:6px;">Data: {data_br}</div>
            </div>
            
    </body>
    </html>
    """
    return html

def main():
    import os
    video_path = os.path.join(ASSETS_DIR, "intro.mp4")
    if os.path.exists(video_path):
        try:
            play_intro_video(video_path, fullscreen=True, duration_limit=13)
        except Exception as e:
            print("[Intro] Falhou (embutida):", e)
    else:
        print("[Intro] NÃO encontrado:", video_path)

    app = App()
    # Tema moderno
    init_modern_theme(app, mode="light")
    try:
        app.attributes('-fullscreen', True)
    except Exception:
        pass
    # Marca d'água — inicializa recursos
    wm_init_feature(app)
    app.mainloop()

if __name__ == '__main__':
    main()


def gerar_html_os_premium(titulo, logo_path, nome, tel, marca, modelo, placa, ano, data_str,
                               km_atual, intervalo, proxima_km, proxima_corr_km, descricao, itens_fmt, km_visita: int = 0):
    """HTML Premium com cabeçalho MECÂNICA DO JAIRO e LOGO embutida (base64)."""
    import base64, mimetypes
    from pathlib import Path

    if not logo_path:
        logo_path = _resolve_logo_path()

    # Embute logo
    logo_tag = "<div style='width:180px;height:80px;border:2px dashed #999;color:#666;display:flex;align-items:center;justify-content:center;font-size:12px;'>SEM LOGO</div>"
    try:
        if logo_path:
            lp = Path(logo_path)
            if not lp.is_absolute():
                base_dir = Path(__file__).resolve().parent
                lp = (base_dir / lp).resolve()
            if lp.exists():
                mime, _ = mimetypes.guess_type(str(lp))
                if not mime:
                    mime = "image/png"
                raw = lp.read_bytes()
                b64 = base64.b64encode(raw).decode("ascii")
                logo_tag = f"<img src='data:{mime};base64,{b64}' alt='Logo' style='height:200px;display:block;margin:0;padding:0;display:block;margin:0;padding:0;display:block;margin:0;padding:0; display:block; object-fit:contain; margin:0'>"
    except Exception:
        pass

    safe_desc = (descricao or '').replace('\n', '<br>')
    corr_row = f"<tr><td colspan='2'><b>Próx. troca da correia:</b> {proxima_corr_km} km</td></tr>" if proxima_corr_km else ""

    qr_tag = f"<img src='data:{QR_PIX_MIME};base64,{QR_PIX_B64}' alt='PIX QR' style='height:200px;display:block;'>"

    # --- Data no formato DD/MM/AAAA ---

    _val_data = (locals().get('data_str') or locals().get('data') or '')

    try:

        data_br = datetime.strptime(str(_val_data)[:10], '%Y-%m-%d').strftime('%d/%m/%Y')

    except Exception:

        try:

            data_br = datetime.strptime(str(_val_data).split()[0], '%d/%m/%Y').strftime('%d/%m/%Y')

        except Exception:

            data_br = str(_val_data)

    html = f"""
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            @page {{ margin: 16mm; }}
            body {{ font-family: Arial, Helvetica, sans-serif; margin:0; padding:16mm; color:#111827; }}
            .header {{ display:flex; align-items:flex-start; justify-content:space-between; margin-bottom:0px; }}
            .empresa {{ font-size:13px; line-height:1.45; }}
            .empresa b {{ font-size:16px; }}
            h1,h2,h3 {{ margin:0; }}
            .title {{ margin:12px 0 8px; }}
            .muted {{ color:#555; }}
            table.grid {{ width:100%; border-collapse:collapse; font-size:11px; margin-top:0px; }}
            table.grid th, table.grid td {{ border:1px solid #e5e7eb; padding:4px; }}
            table.grid th {{ background:#f3f4f6; text-align:left;  font-size:10px}}
            table.cap {{ width:100%; border-collapse:collapse; font-size:13px; margin:0; }}
            table.cap td {{ padding:4px 0; }}
        </style>
    </head>
    <body>
        <!-- {__PATCH_VERSION__} -->
        <div class="header" style="display:block; position:relative; padding-right:260px; min-height:0px;display:block;margin:0;padding:0;display:block;margin:0;padding:0; margin-bottom:0px;">
    <div class="brandwrap" style="display:flex; flex-direction:column; align-items:flex-start; gap:8px; max-width: calc(100% - 260px);">
        <div class="logo" style="display:block; margin-bottom:0px;">{logo_tag}</div>
        <div class="empresa">
                <b>MECÂNICA DO JAIRO</b><br>
                CNPJ: 21.226.070/0001-32<br>
                Avenida Professora Eunice Gonçalves de Souza<br>
                Número 55
            </div>
    </div>
    <div class="qr" style="position:absolute; right:0; top:0;">{qr_tag}</div>
</div>

        <hr>

        <div class="title">
            <h2>Ordem de Serviço</h2>
            <div class="muted">{data_br}</div>
        </div>

        <table class="cap">
            <tr>
                <td><b>Cliente:</b> {nome} &nbsp; <span class="muted">{tel}</span></td>
                <td><b>Veículo:</b> {marca} {modelo} • {ano} • Placa {placa}</td>
            </tr>
            <tr>
                <td><b>KM atual(troca de óleo):</b> {km_atual}</td>
                <td><b>Próx. manutenção:</b> {proxima_km} <span class="muted">(intervalo {intervalo} km)</span></td>
            </tr>
    {corr_row}
        </table>

        <h3>Serviço executado</h3>
        <p style="white-space: pre-wrap; margin-top: 6px;">{safe_desc}</p>

        {f"<h3>Itens</h3><table class='grid'><thead><tr><th>Descrição</th><th style='text-align:right'>Qtde</th><th style='text-align:right'>Valor unit.</th><th style='text-align:right'>Subtotal</th></tr></thead><tbody>"+(itens_fmt or "")+"</tbody></table>" if (itens_fmt or '').strip() else ""}
    
            <div style="margin-top:40px; text-align:center;">
                <div style="width:60%; margin:0 auto; border-top:1px solid #e5e7eb; padding-top:6px;">
                    Assinatura do cliente
                </div>
                <div class="muted" style="font-size:12px; margin-top:6px;">Data: {data_br}</div>
            </div>
            
    </body>
    </html>
    """
    return html

def _salvar_pdf_via_navegador(html_path: str, pdf_path: str) -> bool:
    import subprocess, os, shutil
    candidatos = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    ]
    navegador = next((p for p in candidatos if os.path.exists(p)), None)
    if not navegador:
        return False
    try:
        cmd = [
            navegador, "--headless", "--disable-gpu",
            f"--print-to-pdf={pdf_path}",
            "file:///" + html_path.replace("\\\\", "/")
        ]
        subprocess.run(cmd, check=True, timeout=40)
        return os.path.exists(pdf_path) and os.path.getsize(pdf_path) > 0
    except Exception:
        return False


# Ajuste: Permitir digitar modelo quando não estiver na lista (Combobox state='normal').