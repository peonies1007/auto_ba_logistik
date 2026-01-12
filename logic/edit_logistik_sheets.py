import gspread
from google.oauth2.service_account import Credentials
import sys
import os

# 1. Get the absolute path of the current script's directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# 2. Construct the path to the parent directory by joining the current directory with '..'
parent_dir = os.path.normpath(os.path.join(current_dir, ".."))

# 3. Construct the full file path
file_path = os.path.join(parent_dir, "credentials_sheets.json")


def update_logistik(data_umum, logistik_data):
    # 1. KONFIGURASI KREDENSIAL
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = Credentials.from_service_account_file(file_path, scopes=scopes)
    client = gspread.authorize(creds)

    # 2. BUKA SPREADSHEET
    url_spreadsheet = "https://docs.google.com/spreadsheets/d/17yyv8Am-WWnWxHysy3ViibSLP7fStJrmJZkseEdTmq8/edit#gid=1275974115"
    spreadsheet = client.open_by_url(url_spreadsheet)
    nama_sheet_target = data_umum["bulan"]

    try:
        worksheet = spreadsheet.worksheet(nama_sheet_target)
    except gspread.exceptions.WorksheetNotFound:
        print(f"❌ Error: Sheet '{nama_sheet_target}' tidak ditemukan!")
        sys.exit()

    list_logistik = []
    for item in logistik_data:
        list_logistik.append(
            {
                "sumber": item["keterangan"],
                "nama": item["uraian"],
                "qty": int(item["volume"]),
            },
        )
    # print(list_logistik)
    # --- DATA INPUT (Pastikan Nama Barang sama persis dengan di Sheet) ---
    # logistik_data = [
    #     {"sumber": "APBN", "nama": "Paket Sembako", "qty": 6},
    #     {"sumber": "APBD II", "nama": "Mie Instan", "qty": 2},
    #     {"sumber": "HIBAH APBN", "nama": "Baju Hazmat", "qty": 1},
    #     {"sumber": "HIBAH APBD II", "nama": "Sepatu Boot", "qty": 0}
    # ]

    # 3. AMBIL DATA & IDENTIFIKASI KOLOM
    all_data = worksheet.get_all_values()
    header_row = all_data[2]  # Header di Baris 6 (Index 5)

    def get_col_idx(name):
        for i, label in enumerate(header_row):
            if name.strip().lower() in label.strip().lower():
                return i + 1
        return None

    idx_nama = get_col_idx("NAMA BARANG")
    idx_total = get_col_idx("JUMLAH TOTAL")
    idx_distribusi = get_col_idx("JML PENDISTRIBUSIAN")
    idx_stok_akhir = get_col_idx("STOK Januari 2026")

    # --- LOGIKA KATEGORI (SCAN SELURUH BARIS UNTUK KEAMANAN) ---
    daftar_kategori = ["HIBAH APBD II", "HIBAH APBN", "APBN", "APBD II", "APBD I"]
    row_to_source = {}
    current_cat = None
    categories_found_in_sheet = set()

    for i, row in enumerate(all_data):
        if not row:
            continue

        # Ambil 3 kolom pertama untuk dicek (A, B, C)
        # Ini jaga-jaga jika teks kategori ada di kolom B atau hasil Merged Cells
        teks_baris = " ".join(row[:3]).strip().upper()

        for kat in daftar_kategori:
            if kat in teks_baris:
                current_cat = kat
                categories_found_in_sheet.add(kat)
                break

        row_to_source[i] = current_cat

    # print("--- Laporan Deteksi Spreadsheet ---")
    # print(
    #     f"Kategori yang ditemukan di Sheet: {', '.join(categories_found_in_sheet) if categories_found_in_sheet else 'TIDAK ADA'}"
    # )
    # print("-----------------------------------")

    def to_num(val):
        try:
            return float(str(val).replace(",", ".").strip()) if val else 0
        except:
            return 0

    # 4. VALIDASI STOK
    errors = []
    start_data_idx = 7

    for item in list_logistik:
        nama_cari = item["nama"].strip().lower()
        sumber_cari = item["sumber"].strip().upper()
        qty_minta = item["qty"]
        found = False

        if sumber_cari not in categories_found_in_sheet:
            errors.append(
                f"❌ Kategori '{sumber_cari}' tidak terbaca di spreadsheet. Pastikan sudah tertulis di Kolom A/B."
            )
            continue

        for i in range(start_data_idx, len(all_data)):
            row_curr = all_data[i]
            if len(row_curr) < idx_nama:
                continue

            nama_sheet = str(row_curr[idx_nama - 1]).strip().lower()
            sumber_sheet = row_to_source.get(i)

            if nama_sheet == nama_cari and sumber_sheet == sumber_cari:
                found = True

                val_total = (
                    to_num(row_curr[idx_total - 1]) if len(row_curr) >= idx_total else 0
                )

                dist_lama = 0
                for j in range(idx_total, idx_distribusi - 1):
                    if j < len(row_curr):
                        dist_lama += to_num(row_curr[j])

                stok_skrg = val_total - dist_lama
                if qty_minta > stok_skrg:
                    errors.append(
                        f"❌ Stok {item['nama']} [{sumber_cari}] kurang! (Sisa stok: {stok_skrg}, Permintaan: {qty_minta})"
                    )
                break

        if not found:
            errors.append(
                f"⚠️ Barang '{item['nama']}' tidak ada di bawah baris '{sumber_cari}'."
            )

    if errors:
        print("\nPROSES BATAL (VALIDASI GAGAL):")
        err = ""
        for e in errors:
            print(e)
            err += f"\n{e}"
        return False, f"\nPROSES BATAL (VALIDASI GAGAL):{err}"
        sys.exit()

    # 5. TENTUKAN KOLOM TARGET
    target_col = None
    for i in range(idx_total, idx_distribusi - 1):
        if i >= len(header_row) or header_row[i].strip() == "":
            target_col = i + 1
            break

    if not target_col:
        worksheet.insert_cols([[]], col=idx_distribusi)
        target_col = idx_distribusi
        idx_distribusi += 1
        idx_stok_akhir += 1

    # 6. SUSUN DATA
    def col_letter(n):
        res = ""
        while n > 0:
            n, r = divmod(n - 1, 26)
            res = chr(65 + r) + res
        return res

    col_ba = col_letter(target_col)
    col_total = col_letter(idx_total)
    col_dist = col_letter(idx_distribusi)
    col_stok = col_letter(idx_stok_akhir)

    # --- CARI BARIS TERAKHIR DATA (SEBELUM TANDA TANGAN) ---
    last_data_idx = start_data_idx
    for i in range(start_data_idx, len(all_data)):
        row = all_data[i]
        # Ambil nilai Nama Barang dan No (Kolom A)
        nama_val = row[idx_nama - 1].strip() if len(row) >= idx_nama else ""
        no_val = row[0].strip() if len(row) > 0 else ""

        # Jika menemukan kata kunci tanda tangan, kita berhenti
        if "Kasi" in nama_val or "Mengetahui" in nama_val or "NIP." in nama_val:
            break

        # Update last_data_idx jika baris tidak kosong (ada Nama Barang atau No)
        if nama_val != "" or no_val != "":
            last_data_idx = i + 1

    vals_ba, f_dist, f_akhir = [], [], []

    for i in range(start_data_idx, last_data_idx):
        r = i + 1
        row_curr = all_data[i]
        nama_sheet = (
            str(row_curr[idx_nama - 1]).strip().lower()
            if len(row_curr) >= idx_nama
            else ""
        )
        sumber_sheet = row_to_source.get(i)

        qty_tulis = ""
        for item in list_logistik:
            if item["nama"].strip().lower() == nama_sheet and item[
                "sumber"
            ].strip().upper() == (sumber_sheet or ""):
                qty_tulis = item["qty"]
                break

        vals_ba.append([qty_tulis])

        start_ba_let = col_letter(idx_total + 1)
        end_ba_let = col_letter(idx_distribusi - 1)
        f_dist.append([f"=SUM({start_ba_let}{r}:{end_ba_let}{r})"])
        f_akhir.append([f"={col_total}{r}-{col_dist}{r}"])

    # 7. UPDATE
    worksheet.update_cell(3, target_col, "BA. ")
    worksheet.update_cell(4, target_col, data_umum["tanggal_lengkap"])
    worksheet.update_cell(5, target_col, f"Santunan Korban {data_umum['bencana']}")
    worksheet.update_cell(6, target_col, f"{data_umum['alamat_string']}")

    worksheet.update(range_name=f"{col_ba}8:{col_ba}{len(all_data)}", values=vals_ba)
    worksheet.update(
        range_name=f"{col_dist}8:{col_dist}{len(all_data)}", values=f_dist, raw=False
    )
    worksheet.update(
        range_name=f"{col_stok}8:{col_stok}{len(all_data)}", values=f_akhir, raw=False
    )

    output_func = (
        f"✅ Berhasil! Data dimasukkan ke dalam Google Sheets pada kolom {col_ba}"
    )
    print(output_func)

    return True, output_func
