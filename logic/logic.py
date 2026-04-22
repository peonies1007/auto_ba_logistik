import pickle
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import MediaFileUpload
import os
import sys
import webbrowser
import socket
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from .constant import bulan_nama

# Tentukan scope akses: 'file' artinya aplikasi bisa melihat/mengedit file yang diunggahnya sendiri
SCOPES = ["https://www.googleapis.com/auth/drive.file"]


def resource_path(relative_path):
    """Dapatkan path absolut ke resource, bekerja untuk dev dan PyInstaller"""
    try:
        # PyInstaller membuat folder sementara dan menyimpan path di _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def handle_toggle(v_dasar, frame_kec, frame_ass):
    frame_kec.grid_remove()
    frame_ass.grid_remove()
    # Sekarang kita gunakan row=1 di dalam kontainer kirinya
    if v_dasar.get() == "kecamatan":
        frame_kec.grid(row=1, column=0, columnspan=2, sticky="w", padx=10, pady=5)
    else:
        frame_ass.grid(row=1, column=0, columnspan=2, sticky="w", padx=10, pady=5)


def handle_kecamatan_change(event, cb_kecamatan, cb_desa, data_wilayah):
    """Update pilihan di dropdown desa berdasarkan kecamatan yang dipilih"""
    kecamatan_terpilih = cb_kecamatan.get()

    # Cari daftar wilayah untuk kecamatan tersebut
    desa_list = []
    for item in data_wilayah:
        if item["kecamatan"] == kecamatan_terpilih:
            # Gabungkan Nama + Status (Contoh: "Sine (Kelurahan)")
            desa_list = [f"{d['status']} {d['nama']}" for d in item["daftar_wilayah"]]
            break

    # Masukkan list baru ke combobox desa
    cb_desa["values"] = desa_list
    if desa_list:
        cb_desa.set(desa_list[0])  # Set ke item pertama
    else:
        cb_desa.set("")


def get_drive_service():
    creds = None
    # File token.pickle menyimpan token akses user
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)

    # Jika tidak ada token valid, minta user login
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                resource_path("credentials.json"), SCOPES
            )

            # --- MODIFIKASI DI SINI ---
            # Kita mendapatkan URL otorisasi terlebih dahulu
            auth_url, _ = flow.authorization_url(prompt="consent")

            print("Membuka browser untuk otorisasi...")
            # Paksa buka di browser default (Chrome)
            webbrowser.open(auth_url)

            # Baru jalankan server untuk menerima kode kembalian
            creds = flow.run_local_server(port=0)
            # --------------------------
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)

    return build("drive", "v3", credentials=creds)


def upload_to_drive(file_path):
    try:
        # MASUKKAN FOLDER ID ANDA DI SINI
        FOLDER_ID = "1CvDN3tnuoeCvJ5ik94bI-Ff_lSHGFReH"
        service = get_drive_service()
        file_metadata = {"name": os.path.basename(file_path), "parents": [FOLDER_ID]}
        media = MediaFileUpload(
            file_path,
            mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )

        file = (
            service.files()
            .create(body=file_metadata, media_body=media, fields="id")
            .execute()
        )
        return True, f"Data berhasil dibackup di Google Drive pada id {file.get('id')}"
    except Exception as e:
        print(f"Error Drive: {e}")
        return False, e


def cek_internet(host="8.8.8.8", port=53, timeout=3):
    """
    Mengecek koneksi internet dengan cara yang lebih aman.
    """
    try:
        # socket.create_connection adalah cara yang lebih modern
        # 'with' memastikan socket ditutup otomatis setelah pengecekan
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except (socket.timeout, socket.error):
        return False


def get_worksheet(bulan):
    # 1. Get the absolute path of the current script's directory
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # 2. Construct the path to the parent directory by joining the current directory with '..'
    parent_dir = os.path.normpath(os.path.join(current_dir, ".."))

    # 3. Construct the full file path
    file_path = os.path.join(parent_dir, "credentials_sheets.json")

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = Credentials.from_service_account_file(file_path, scopes=scopes)
    client = gspread.authorize(creds)

    # 2. BUKA SPREADSHEET
    url_spreadsheet = "https://docs.google.com/spreadsheets/d/17yyv8Am-WWnWxHysy3ViibSLP7fStJrmJZkseEdTmq8/edit#gid=1275974115"
    spreadsheet = client.open_by_url(url_spreadsheet)

    try:
        worksheet = spreadsheet.worksheet(bulan)
    except gspread.exceptions.WorksheetNotFound:
        print(f"❌ Error: Sheet '{bulan}' tidak ditemukan!")
        sys.exit()

    return worksheet


def ambil_data_spreadsheet():
    month_now = bulan_nama[datetime.now().month - 1]

    try:
        values = get_worksheet(
            month_now
        ).get_all_values()  # Ganti "April" dengan nama sheet yang sesuai
        header_row = values[2]

        def get_col_idx(name):
            for i, label in enumerate(header_row):
                if name.strip().lower() in label.strip().lower():
                    return i + 1
            return None

        if not values:
            return False, "Data tidak ditemukan di spreadsheet."

        data_bersih = []
        sumber_diizinkan = ["APBN", "APBD I", "APBD II", "HIBAH APBN", "HIBAH APBD II"]
        sumber_dana_aktif = None

        for row in values:
            if not row:
                continue

            # Cek Kategori Sumber Dana (Kolom A)
            if len(row) > 0 and (len(row) == 1 or str(row[1]).strip() == ""):
                kategori = str(row[0]).strip().upper()
                if kategori in sumber_diizinkan:
                    sumber_dana_aktif = kategori
                else:
                    sumber_dana_aktif = None
                continue

            if sumber_dana_aktif is None:
                continue

            # Pastikan minimal ada Kolom B dan C
            if len(row) >= 3:
                nama_barang = str(row[1]).strip()
                satuan = str(row[2]).strip()

                # Lewati header tabel
                if nama_barang == "" or nama_barang.upper() == "NAMA BARANG":
                    continue

                # --- TRIK JITU: PADDING ARRAY ---
                # Memaksa array 'row' agar selalu punya minimal 15 kolom.
                # Ini mencegah error jika Google Sheets memotong kolom kanan yang kosong.
                row_stok_akhir = get_col_idx(f"STOK {month_now} 2026")
                row_lengkap = row + [""] * (row_stok_akhir - len(row))

                # Sekarang kita bisa dengan aman mengambil Indeks ke-13
                # (A=0, B=1, ... M=12, N=13)
                stok_april = str(row_lengkap[row_stok_akhir - 1]).strip()

                # Jika stok di Kolom N benar-benar kosong, jadikan "0"
                if stok_april == "":
                    stok_april = "0"

                data_bersih.append([sumber_dana_aktif, nama_barang, satuan, stok_april])

        return True, data_bersih

    except Exception as e:
        return False, f"Gagal mengambil data API: {str(e)}"
