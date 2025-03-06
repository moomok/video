import asyncio
import time
import os
import uuid
import glob
from dotenv import load_dotenv
from playwright.async_api import async_playwright
import requests

# Load token dari file tokens.txt
TOKENS_FILE = "tokens.txt"
TEXTS_FOLDER = "texts/"  # Folder untuk menyimpan file teks

# Model UID yang digunakan (MINIMAX Video Model)
MODEL_UID = "9137cf0c-4cf0-4b31-8619-de700c5b4f35"

def load_tokens():
    if os.path.exists(TOKENS_FILE):
        with open(TOKENS_FILE, "r", encoding="utf-8") as f:
            tokens = [line.strip() for line in f.readlines() if line.strip()]
        if tokens:
            return tokens
    return []

TOKENS = load_tokens()

# Fungsi untuk membaca teks dari semua file dalam folder TEXTS_FOLDER
def load_texts():
    all_texts = []
    if os.path.exists(TEXTS_FOLDER):
        text_files = glob.glob(os.path.join(TEXTS_FOLDER, "*.txt"))  # Ambil semua file .txt
        for file in text_files:
            with open(file, "r", encoding="utf-8") as f:
                texts = [line.strip() for line in f.readlines() if line.strip()]
                all_texts.extend(texts)  # Gabungkan semua teks dari berbagai file
    return all_texts if all_texts else ["Default text if no files found."]

TEXT_OPTIONS = load_texts()

# Fungsi untuk mengecek akses token
def check_access(token):
    url = "https://app.videofi.ai/create"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.head(url, headers=headers)
    print(f"HEAD Response: {response.status_code}, {response.headers}")
    return response.status_code == 200

# Fungsi untuk mengirim permintaan generate video
def generate_video(token, text):
    url = "https://api.videofi.ai/user-requests"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    payload = {
        "model_id": MODEL_UID,
        "content": text,
        "config": {}
    }
    
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        print(f"[SUCCESS] Video berhasil dibuat dengan teks: {text} (Model: {MODEL_UID})")
    else:
        print(f"[FAILED] Gagal membuat video: {response.status_code}, {response.text}")

# Main program
def main():
    if not TOKENS:
        print("Token tidak ditemukan, harap tambahkan token di tokens.txt!")
        return
    
    valid_tokens = [token for token in TOKENS if check_access(token)]
    
    if not valid_tokens:
        print("Semua token gagal mendapatkan akses. Periksa kembali!")
        return
    
    wait_time = int(input("Masukkan waktu jeda antar request (dalam detik): "))
    
    for text in TEXT_OPTIONS:  # Jalankan satu per satu berdasarkan urutan teks
        for token in valid_tokens:  # Gunakan token satu per satu
            print(f"\n🔹 Menggunakan akun dengan token {token[:10]}... (dipersingkat)")
            print(f"📤 Mengirim permintaan untuk teks: {text}")
            generate_video(token, text)
            print(f"⏳ Menunggu {wait_time} detik sebelum permintaan berikutnya...")
            time.sleep(wait_time)

if __name__ == "__main__":
    main()
