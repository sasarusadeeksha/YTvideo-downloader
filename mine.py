import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pytube import YouTube
import threading
import os
from pathlib import Path
from PIL import Image, ImageTk  # For icon support

# ================= Dark Mode Colors =================
BG_COLOR = "#121212"
FG_COLOR = "#e0e0e0"
BUTTON_BG = "#1f1f1f"
BUTTON_FG = "#ffffff"
ENTRY_BG = "#222222"
ENTRY_FG = "#e0e0e0"
COMBO_BG = "#222222"
COMBO_FG = "#e0e0e0"

# ================ Global Variables ==================
download_folder = str(Path.home() / "Downloads")

# =============== Functions =========================
def set_icon(window):
    try:
        # You can add your own icon file path here (must be .ico)
        window.iconbitmap('youtube_icon.ico')  # Replace with your icon path
    except Exception:
        pass  # Ignore if icon not found

def choose_folder():
    global download_folder
    folder = filedialog.askdirectory(initialdir=download_folder)
    if folder:
        download_folder_label.config(text=folder)
        download_folder = folder

def fetch_resolutions():
    url = url_entry.get()
    if not url:
        messagebox.showwarning("Warning", "Please enter a YouTube URL first.")
        return

    try:
        yt = YouTube(url)
        streams = yt.streams.filter(progressive=True, file_extension='mp4')
        resolutions = sorted({s.resolution for s in streams if s.resolution}, reverse=True)
        if not resolutions:
            raise Exception("No video resolutions found.")

        resolution_menu['values'] = resolutions
        resolution_menu.current(0)
        messagebox.showinfo("Resolutions Loaded", "Available resolutions loaded successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to fetch resolutions:\n{e}")

def download_video():
    url = url_entry.get()
    if not url:
        messagebox.showwarning("Warning", "Please enter a YouTube URL.")
        return

    try:
        yt = YouTube(url)
        if download_type.get() == 'Video':
            selected_res = resolution_var.get()
            streams = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc()

            stream = None
            for s in streams:
                if s.resolution == selected_res:
                    stream = s
                    break

            if not stream:
                messagebox.showerror("Error", f"No video stream found for resolution {selected_res}")
                return

            download_button.config(text="Downloading...", state="disabled")
            stream.download(output_path=download_folder)
            messagebox.showinfo("Success", f"Video downloaded: {yt.title}")

        else:  # Audio (MP3) download
            audio_stream = yt.streams.filter(only_audio=True).order_by('abr').desc().first()
            if not audio_stream:
                messagebox.showerror("Error", "No audio stream found.")
                return

            download_button.config(text="Downloading...", state="disabled")
            out_file = audio_stream.download(output_path=download_folder)

            # Rename to mp3
            base, ext = os.path.splitext(out_file)
            new_file = base + ".mp3"
            os.rename(out_file, new_file)
            messagebox.showinfo("Success", f"MP3 downloaded: {yt.title}")

    except Exception as e:
        messagebox.showerror("Error", str(e))
    finally:
        download_button.config(text="Download", state="normal")

def threaded_download():
    threading.Thread(target=download_video).start()

def toggle_resolution_menu():
    if download_type.get() == 'Video':
        resolution_menu.configure(state='readonly')
        load_res_button.configure(state='normal')
    else:
        resolution_menu.configure(state='disabled')
        load_res_button.configure(state='disabled')

# ================== GUI Setup =======================
root = tk.Tk()
root.title("YouTube Downloader - Dark Mode")
root.geometry("450x320")
root.configure(bg=BG_COLOR)
root.resizable(False, False)
set_icon(root)

# Title
title_label = tk.Label(root, text="YouTube Downloader", font=("Segoe UI", 18, "bold"), bg=BG_COLOR, fg=FG_COLOR)
title_label.pack(pady=10)

# URL input
url_entry = ttk.Entry(root, width=55)
url_entry.pack(pady=8)
url_entry.insert(0, "Paste YouTube video URL here")

# Download type (Video / Audio)
download_type = tk.StringVar(value="Video")
frame_radio = tk.Frame(root, bg=BG_COLOR)
frame_radio.pack()

video_radio = ttk.Radiobutton(frame_radio, text="Video", variable=download_type, value="Video", command=toggle_resolution_menu)
video_radio.grid(row=0, column=0, padx=10, pady=5)

audio_radio = ttk.Radiobutton(frame_radio, text="MP3 Audio", variable=download_type, value="Audio", command=toggle_resolution_menu)
audio_radio.grid(row=0, column=1, padx=10, pady=5)

# Resolution dropdown
resolution_var = tk.StringVar()
resolution_menu = ttk.Combobox(root, textvariable=resolution_var, state='readonly', width=15)
resolution_menu.pack(pady=5)

load_res_button = ttk.Button(root, text="Load Resolutions", command=fetch_resolutions)
load_res_button.pack()

# Download folder selection
folder_frame = tk.Frame(root, bg=BG_COLOR)
folder_frame.pack(pady=10)

folder_label_text = tk.Label(folder_frame, text="Download Folder:", bg=BG_COLOR, fg=FG_COLOR)
folder_label_text.grid(row=0, column=0, padx=5)

download_folder_label = tk.Label(folder_frame, text=download_folder, bg=BG_COLOR, fg=FG_COLOR, width=35, anchor="w")
download_folder_label.grid(row=0, column=1, padx=5)

folder_button = ttk.Button(folder_frame, text="Choose Folder", command=choose_folder)
folder_button.grid(row=0, column=2, padx=5)

# Download button
download_button = ttk.Button(root, text="Download", command=threaded_download)
download_button.pack(pady=15)

# Apply dark style to ttk widgets
style = ttk.Style(root)
style.theme_use('clam')
style.configure("TEntry", fieldbackground=ENTRY_BG, foreground=ENTRY_FG)
style.configure("TCombobox", fieldbackground=COMBO_BG, foreground=COMBO_FG)
style.configure("TButton", background=BUTTON_BG, foreground=BUTTON_FG)

# Initially disable resolution menu if Audio selected
toggle_resolution_menu()

root.mainloop()

