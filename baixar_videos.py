import os
import tkinter as tk
from tkinter import ttk, filedialog
from yt_dlp import YoutubeDL
import whisper

# Função para baixar vídeos
def baixar_video(video_url, pasta_destino):
    try:
        ydl_opts = {
            'outtmpl': os.path.join(pasta_destino, '%(title)s.%(ext)s'),
            'format': 'mp4/best',
        }
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
        return "Download concluído!"
    except Exception as e:
        return f"Erro ao baixar vídeo: {str(e)}"

# Função para transcrever vídeo
def transcrever_video(video_url, pasta_destino):
    try:
        # Baixar o vídeo primeiro
        ydl_opts = {
            'outtmpl': os.path.join(pasta_destino, '%(title)s.%(ext)s'),
            'format': 'mp4/best',
        }
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            video_path = ydl.prepare_filename(info)

        # Carregar modelo Whisper
        model = whisper.load_model("base")
        result = model.transcribe(video_path, fp16=False)
        return result['text']

    except Exception as e:
        return f"Erro ao transcrever vídeo: {str(e)}"

# Função para selecionar pasta de destino
def selecionar_pasta():
    pasta = filedialog.askdirectory()
    pasta_destino_var.set(pasta)

# Interface gráfica
app = tk.Tk()
app.title("YouDownload - Baixar e Transcrever Vídeos")
app.geometry("600x400")

notebook = ttk.Notebook(app)
notebook.pack(fill='both', expand=True)

# Aba para baixar vídeos
aba_download = ttk.Frame(notebook)
notebook.add(aba_download, text="Baixar Vídeos")

# Componentes da aba de download
tk.Label(aba_download, text="URL do Vídeo:").pack(pady=5)
baixar_url_entry = tk.Entry(aba_download, width=50)
baixar_url_entry.pack(pady=5)

pasta_destino_var = tk.StringVar()
tk.Label(aba_download, text="Pasta de Destino:").pack(pady=5)
tk.Entry(aba_download, textvariable=pasta_destino_var, width=50).pack(pady=5)
tk.Button(aba_download, text="Selecionar Pasta", command=selecionar_pasta).pack(pady=5)

mensagem_download = tk.Text(aba_download, height=5, width=50)
mensagem_download.pack(pady=5)

def acionar_download():
    url = baixar_url_entry.get()
    pasta = pasta_destino_var.get()
    mensagem = baixar_video(url, pasta)
    mensagem_download.delete(1.0, tk.END)
    mensagem_download.insert(tk.END, mensagem)

tk.Button(aba_download, text="Baixar Vídeo", command=acionar_download).pack(pady=5)

# Aba para transcrever vídeos
aba_transcricao = ttk.Frame(notebook)
notebook.add(aba_transcricao, text="Transcrever Vídeos")

# Componentes da aba de transcrição
tk.Label(aba_transcricao, text="URL do Vídeo:").pack(pady=5)
transcricao_url_entry = tk.Entry(aba_transcricao, width=50)
transcricao_url_entry.pack(pady=5)

def acionar_transcricao():
    url = transcricao_url_entry.get()
    pasta = pasta_destino_var.get()
    texto_transcricao = transcrever_video(url, pasta)
    mensagem_transcricao.delete(1.0, tk.END)
    mensagem_transcricao.insert(tk.END, texto_transcricao)

mensagem_transcricao = tk.Text(aba_transcricao, height=10, width=50)
mensagem_transcricao.pack(pady=5)

tk.Button(aba_transcricao, text="Transcrever Vídeo", command=acionar_transcricao).pack(pady=5)

app.mainloop()
