import tkinter as tk
from date_picker import buat_date_picker
import components as comp
import logic
from data_wilayah import DATA_KECAMATAN


def main():
    root = tk.Tk()
    root.title("Input Data Logistik")
    root.geometry("600x850")

    # --- BAGIAN 1 & 2 (Tetap Sama) ---
    tk.Label(root, text="Dasar Surat:", font=("Arial", 10, "bold")).grid(
        row=0, column=0, padx=10, pady=10, sticky="w"
    )
    v_dasar = tk.StringVar(value="kecamatan")
    rb_frame = tk.Frame(root)
    rb_frame.grid(row=0, column=1, sticky="w")

    frame_kecamatan = tk.Frame(root)
    entri_kec = {
        "surat_dari": comp.create_label_entry(
            frame_kecamatan, "Surat dari Kec/Desa", 0
        ),
        "nomor_surat": comp.create_label_entry(frame_kecamatan, "Nomor Surat", 1),
        "perihal": comp.create_label_entry(frame_kecamatan, "Perihal", 2),
    }

    frame_assessment = tk.Frame(root)
    tk.Label(frame_assessment, text="Tanggal Assessment").grid(
        row=0, column=0, sticky="w", pady=2
    )
    entri_ass = {"tgl_ass": buat_date_picker(frame_assessment)}
    entri_ass["tgl_ass"].grid(row=0, column=1, padx=10, pady=2)

    def trigger_toggle():
        logic.handle_toggle(v_dasar, frame_kecamatan, frame_assessment)

    tk.Radiobutton(
        rb_frame,
        text="Kecamatan",
        variable=v_dasar,
        value="kecamatan",
        command=trigger_toggle,
    ).pack(side="left")
    tk.Radiobutton(
        rb_frame,
        text="Assessment",
        variable=v_dasar,
        value="assessment",
        command=trigger_toggle,
    ).pack(side="left")

    # --- BAGIAN 3: FIELD UMUM ---
    frame_umum = tk.Frame(root)
    frame_umum.grid(row=2, column=0, columnspan=2, pady=10, sticky="w")

    entri = {}
    # Label Data Distribusi
    tk.Label(frame_umum, text="Data Distribusi:", font=("Arial", 10, "bold")).grid(
        row=0, column=0, padx=10, pady=5, sticky="w"
    )
    # Tanggal & Bencana
    tk.Label(frame_umum, text="Tanggal").grid(
        row=1, column=0, sticky="w", padx=10, pady=2
    )
    entri["tanggal"] = buat_date_picker(frame_umum)
    entri["tanggal"].grid(row=1, column=1, padx=10, pady=2)

    entri["bencana"] = comp.create_label_combobox(
        frame_umum,
        "Bencana",
        2,
        ["Angin Kencang", "Tanah Longsor", "Banjir", "Kebakaran Rumah"],
    )

    # --- SETUP DROPDOWN WILAYAH ---
    list_nama_kecamatan = [d["kecamatan"] for d in DATA_KECAMATAN]

    # Dropdown Kecamatan
    entri["alamat_kec"] = comp.create_label_combobox(
        frame_umum, "  - Kecamatan", 3, list_nama_kecamatan
    )

    # Dropdown Desa (Awalnya kosong, akan diisi saat Kecamatan dipilih)
    entri["alamat_kel"] = comp.create_label_combobox(
        frame_umum, "  - Kelurahan/Desa", 4, []
    )

    # Event Binding: Saat Kecamatan berubah, update Desa
    entri["alamat_kec"].bind(
        "<<ComboboxSelected>>",
        lambda event: logic.handle_kecamatan_change(
            event, entri["alamat_kec"], entri["alamat_kel"], DATA_KECAMATAN
        ),
    )

    # Input Dukuh (Tetap manual)
    entri["alamat_dukuh"] = comp.create_label_entry(frame_umum, "  - Dukuh/Kampung", 5)

    # Trigger pengisian desa pertama kali agar tidak kosong saat start
    logic.handle_kecamatan_change(
        None, entri["alamat_kec"], entri["alamat_kel"], DATA_KECAMATAN
    )

    # Keterangan (Pindah ke baris 6 karena alamat memakan 3 baris)
    entri["keterangan"] = comp.create_label_combobox(
        frame_umum,
        "Keterangan",
        6,
        ["APBN", "APBD I", "APBD II", "Hibah APBN", "Hibah APBD"],
    )

    # --- BAGIAN 4: TABEL LOGISTIK (DINAMIS) ---
    tk.Label(root, text="Daftar Logistik:", font=("Arial", 10, "bold")).grid(
        row=4, column=0, padx=10, pady=5, sticky="w"
    )

    frame_tabel = tk.Frame(root)
    frame_tabel.grid(row=5, column=0, columnspan=2, padx=10, sticky="w")

    # Header Tabel
    headers = ["Uraian", "Vol", "Satuan", "Keterangan", "Aksi"]
    for i, h in enumerate(headers):
        tk.Label(frame_tabel, text=h, font=("Arial", 9, "italic")).grid(row=0, column=i)

    rows_logistik = []

    def hapus_baris_spesifik(row_dict):
        """Menghapus widget dari layar dan dari daftar data"""
        # Hapus widget dari tampilan GUI
        for widget in row_dict.values():
            widget.destroy()

        # Hapus dictionary dari list rows_logistik
        if row_dict in rows_logistik:
            rows_logistik.remove(row_dict)

    def tambah_baris():
        # Gunakan len + 1 sebagai indeks baris grid agar tidak bertumpuk dengan header
        # Catatan: Grid Tkinter akan otomatis menyesuaikan posisi jika baris di tengah dihapus
        idx = len(rows_logistik) + 1
        new_row = comp.create_logistik_row(frame_tabel, idx, hapus_baris_spesifik)
        rows_logistik.append(new_row)

    # Tombol Tambah Baris (Hanya Tambah, karena hapus sudah ada di tiap baris)
    btn_frame = tk.Frame(root)
    btn_frame.grid(row=6, column=0, columnspan=2, padx=10, sticky="w")
    tk.Button(
        btn_frame,
        text="+ Tambah Item Logistik",
        command=tambah_baris,
        bg="#4CAF50",
        fg="white",
    ).pack(pady=5)

    # Tambah 1 baris pertama secara otomatis
    tambah_baris()

    # Tombol Simpan Akhir
    tk.Button(
        root,
        text="Simpan Data",
        command=lambda: logic.handle_simpan(
            v_dasar, entri, entri_kec, entri_ass, rows_logistik
        ),
        bg="#2196F3",
        fg="white",
        width=20,
    ).grid(row=7, column=0, columnspan=2, pady=20)

    trigger_toggle()
    root.mainloop()


if __name__ == "__main__":
    main()
