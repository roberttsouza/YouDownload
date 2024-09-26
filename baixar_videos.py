import babel
import yt_dlp
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkcalendar import DateEntry
from datetime import datetime
import pytz
import os
import zipfile
import shutil
import json


# Caminho do arquivo de configuração
config_file = "config.json"

# Função para carregar o caminho da última pasta
def carregar_config():
    if os.path.exists(config_file):
        with open(config_file, "r") as f:
            return json.load(f).get("last_directory", "")
    return ""

# Função para salvar o caminho da última pasta
def salvar_config(pasta):
    with open(config_file, "w") as f:
        json.dump({"last_directory": pasta}, f)

def baixar_videos_do_canal(channel_url, data_inicio, data_fim, pasta_destino, qualidade):
    # Converter as datas para o formato necessário (YYYYMMDD)
    data_inicio_str = data_inicio.strftime('%Y%m%d')
    data_fim_str = data_fim.strftime('%Y%m%d')

    # Cria uma pasta temporária para baixar os vídeos
    temp_pasta = os.path.join(pasta_destino, 'videos_temp')
    if not os.path.exists(temp_pasta):
        os.makedirs(temp_pasta)

    # Opções para baixar os vídeos e as thumbnails
    ydl_opts = {
        'format': qualidade,
        'outtmpl': os.path.join(temp_pasta, '%(title)s.%(ext)s'),  # Nome do arquivo de vídeo
        'dateafter': data_inicio_str,
        'datebefore': data_fim_str,
        'ignoreerrors': True,
        'writethumbnail': True,  # Baixar a thumbnail junto com o vídeo
        'postprocessors': [{
            'key': 'EmbedThumbnail',  # Vincular a thumbnail ao vídeo
        }],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([channel_url])

    # Compactar vídeos e thumbnails baixados em um arquivo ZIP
    zip_filename = os.path.join(pasta_destino, 'videos.zip')
    with zipfile.ZipFile(zip_filename, 'w') as zipf:
        for root, _, files in os.walk(temp_pasta):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path, os.path.basename(file_path))

    # Limpar a pasta temporária
    shutil.rmtree(temp_pasta)

    return zip_filename

def baixar_video_especifico(video_url, pasta_destino, audio_only, qualidade):
    # Cria a pasta de destino se não existir
    if not os.path.exists(pasta_destino):
        os.makedirs(pasta_destino)

    # Opções para baixar o vídeo ou só o áudio
    if audio_only:
        ydl_opts = {
            'format': 'bestaudio',
            'outtmpl': os.path.join(pasta_destino, '%(title)s.%(ext)s'),  # Nome do arquivo de áudio
            'writethumbnail': True,  # Baixar a thumbnail junto com o áudio
        }
    else:
        ydl_opts = {
            'format': qualidade,
            'outtmpl': os.path.join(pasta_destino, '%(title)s.%(ext)s'),  # Nome do arquivo de vídeo
            'writethumbnail': True,  # Baixar a thumbnail junto com o vídeo
            'postprocessors': [{
                'key': 'EmbedThumbnail',  # Vincular a thumbnail ao vídeo
            }],
        }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])

def escolher_pasta_canal():
    pasta = filedialog.askdirectory()
    if pasta:
        pasta_destino_entry.delete(0, tk.END)
        pasta_destino_entry.insert(0, pasta)
        salvar_config(pasta)  # Salva o caminho da pasta selecionada

def escolher_pasta_video():
    pasta = filedialog.askdirectory()
    if pasta:
        pasta_destino_video_entry.delete(0, tk.END)
        pasta_destino_video_entry.insert(0, pasta)
        salvar_config(pasta)  # Salva o caminho da pasta selecionada

def iniciar_download_canal():
    channel_url = url_entry.get()
    data_inicio = data_inicio_entry.get_date()
    data_fim = data_fim_entry.get_date()
    pasta_destino = pasta_destino_entry.get()
    qualidade = qualidade_canal_combobox.get()

    if not channel_url or not data_inicio or not data_fim or not pasta_destino:
        messagebox.showwarning("Campos vazios", "Por favor, preencha todos os campos.")
        return

    try:
        # Converter as datas para timezone UTC corretamente
        data_inicio = datetime.combine(data_inicio, datetime.min.time()).astimezone(pytz.UTC)
        data_fim = datetime.combine(data_fim, datetime.max.time()).astimezone(pytz.UTC)
    except ValueError:
        messagebox.showerror("Erro", "Formato de data inválido.")
        return

    try:
        zip_file = baixar_videos_do_canal(channel_url, data_inicio, data_fim, pasta_destino, qualidade)
        messagebox.showinfo("Download Completo", f"Vídeos e thumbnails baixados e compactados em: {zip_file}")
    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um erro: {str(e)}")

def iniciar_download_video():
    video_url = video_url_entry.get()
    pasta_destino = pasta_destino_video_entry.get()
    audio_only = audio_var.get()
    qualidade = qualidade_video_combobox.get()

    if not video_url or not pasta_destino:
        messagebox.showwarning("Campos vazios", "Por favor, preencha todos os campos.")
        return

    try:
        baixar_video_especifico(video_url, pasta_destino, audio_only, qualidade)
        messagebox.showinfo("Download Completo", "Vídeo/Áudio e thumbnail baixados com sucesso.")
    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um erro: {str(e)}")

# Criação da interface gráfica
app = tk.Tk()
app.title("Downloader de Vídeos do YouTube")
app.geometry("600x600")

# Carregar a última pasta selecionada
ultima_pasta = carregar_config()

# Criação das abas
tab_control = ttk.Notebook(app)

# Aba para baixar vídeos de canal
canal_tab = ttk.Frame(tab_control)
tab_control.add(canal_tab, text='Baixar Vídeos do Canal')

# URL do Canal
tk.Label(canal_tab, text="URL do Canal YouTube:").pack(pady=5)
url_entry = tk.Entry(canal_tab, width=50)
url_entry.pack(pady=5)

# Data de Início com Calendário
tk.Label(canal_tab, text="Data de Início:").pack(pady=5)
data_inicio_entry = DateEntry(canal_tab, width=20, date_pattern='dd/mm/yyyy')
data_inicio_entry.pack(pady=5)

# Data de Fim com Calendário
tk.Label(canal_tab, text="Data de Fim:").pack(pady=5)
data_fim_entry = DateEntry(canal_tab, width=20, date_pattern='dd/mm/yyyy')
data_fim_entry.pack(pady=5)

# Escolher Pasta de Destino
tk.Label(canal_tab, text="Escolher Pasta de Destino:").pack(pady=5)
pasta_destino_entry = tk.Entry(canal_tab, width=40)
pasta_destino_entry.insert(0, ultima_pasta)  # Preencher com a última pasta
pasta_destino_entry.pack(pady=5)

escolher_pasta_button = tk.Button(canal_tab, text="Escolher Pasta", command=escolher_pasta_canal)
escolher_pasta_button.pack(pady=5)

# Qualidade do Vídeo
tk.Label(canal_tab, text="Qualidade do Vídeo:").pack(pady=5)
qualidade_canal_combobox = ttk.Combobox(canal_tab, values=["best", "worst", "bestaudio"])
qualidade_canal_combobox.set("best")  # Opção padrão
qualidade_canal_combobox.pack(pady=5)

# Botão de Iniciar Download do Canal
baixar_canal_button = tk.Button(canal_tab, text="Iniciar Download", command=iniciar_download_canal)
baixar_canal_button.pack(pady=20)

# Aba para baixar vídeo específico
video_tab = ttk.Frame(tab_control)
tab_control.add(video_tab, text='Baixar Vídeo Específico')

# URL do Vídeo
tk.Label(video_tab, text="URL do Vídeo YouTube:").pack(pady=5)
video_url_entry = tk.Entry(video_tab, width=50)
video_url_entry.pack(pady=5)

# Opção para Baixar Apenas o Áudio
audio_var = tk.BooleanVar()
audio_checkbox = tk.Checkbutton(video_tab, text="Baixar Apenas Áudio", variable=audio_var)
audio_checkbox.pack(pady=5)

# Qualidade do Vídeo
tk.Label(video_tab, text="Qualidade do Vídeo:").pack(pady=5)
qualidade_video_combobox = ttk.Combobox(video_tab, values=["best", "worst", "bestaudio"])
qualidade_video_combobox.set("best")  # Opção padrão
qualidade_video_combobox.pack(pady=5)

# Escolher Pasta de Destino para Vídeo Específico
tk.Label(video_tab, text="Escolher Pasta de Destino:").pack(pady=5)
pasta_destino_video_entry = tk.Entry(video_tab, width=40)
pasta_destino_video_entry.insert(0, ultima_pasta)  # Preencher com a última pasta
pasta_destino_video_entry.pack(pady=5)

escolher_pasta_video_button = tk.Button(video_tab, text="Escolher Pasta", command=escolher_pasta_video)
escolher_pasta_video_button.pack(pady=5)

# Botão de Iniciar Download do Vídeo Específico
baixar_video_button = tk.Button(video_tab, text="Iniciar Download", command=iniciar_download_video)
baixar_video_button.pack(pady=20)

# Exibir as abas
tab_control.pack(expand=1, fill='both')

# Iniciar a interface
app.mainloop()
