import tkinter as tk
from date_picker import buat_date_picker
from data_wilayah import DATA_KECAMATAN
import components as comp
import logic
from data_logistik import data_logistik  # Pastikan file ini ada


def main():
    root = tk.Tk()
    root.title("Input Data Logistik")
    root.geometry("1100x700")  # Lebar ditambah untuk mengakomodasi sisi kanan

    # --- CONTAINER UTAMA ---
    # Membagi root menjadi dua kolom utama
    root.columnconfigure(0, weight=0)  # Kolom kiri (Form)
    root.columnconfigure(1, weight=1)  # Kolom kanan (Logistik) - bisa meluas
    root.rowconfigure(0, weight=1)

    # --- FRAME KIRI (DATA DASAR & UMUM) ---
    left_container = tk.Frame(root, padx=10, pady=10)
    left_container.grid(row=0, column=0, sticky="nsw")

    # --- BAGIAN 1: DASAR SURAT (di dalam left_container) ---
    tk.Label(left_container, text="Dasar Surat:", font=("Arial", 10, "bold")).grid(
        row=0, column=0, sticky="w", pady=10
    )
    v_dasar = tk.StringVar(value="kecamatan")
    rb_frame = tk.Frame(left_container)
    rb_frame.grid(row=0, column=1, sticky="w")

    frame_kecamatan = tk.Frame(left_container)
    entri_kec = {
        "surat_dari": comp.create_label_entry(
            frame_kecamatan, "Surat dari Kec/Desa", 0
        ),
        "nomor_surat": comp.create_label_entry(frame_kecamatan, "Nomor Surat", 1),
        "perihal": comp.create_label_entry(frame_kecamatan, "Perihal", 2),
    }

    frame_assessment = tk.Frame(left_container)
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

    # --- BAGIAN 3: FIELD UMUM (di dalam left_container) ---
    frame_umum = tk.Frame(left_container)
    frame_umum.grid(row=2, column=0, columnspan=2, pady=10, sticky="w")
    entri = {}

    tk.Label(frame_umum, text="Tanggal").grid(
        row=0, column=0, sticky="w", padx=10, pady=2
    )
    entri["tanggal"] = buat_date_picker(frame_umum)
    entri["tanggal"].grid(row=0, column=1, padx=10, pady=2)

    entri["bencana"] = comp.create_label_combobox(
        frame_umum,
        "Bencana",
        1,
        ["Angin Kencang", "Tanah Longsor", "Banjir", "Kebakaran Rumah"],
    )

    tk.Label(frame_umum, text="Alamat:", font=("Arial", 9, "bold")).grid(
        row=2, column=0, sticky="w", padx=10, pady=5
    )
    entri["alamat_kec"] = comp.create_label_combobox(
        frame_umum, "  - Kecamatan", 3, [d["kecamatan"] for d in DATA_KECAMATAN]
    )
    entri["alamat_kel"] = comp.create_label_combobox(
        frame_umum, "  - Kelurahan/Desa", 4, []
    )

    # Event Binding Alamat
    entri["alamat_kec"].bind(
        "<<ComboboxSelected>>",
        lambda e: logic.handle_kecamatan_change(
            e, entri["alamat_kec"], entri["alamat_kel"], DATA_KECAMATAN
        ),
    )

    entri["alamat_dukuh"] = comp.create_label_entry(frame_umum, "  - Dukuh/Kampung", 5)

    # --- FRAME KANAN (LOGISTIK) ---
    right_container = tk.Frame(root, padx=20, pady=10, relief="groove", borderwidth=1)
    right_container.grid(row=0, column=1, sticky="nsew")
    right_container.grid_columnconfigure(0, weight=1)

    tk.Label(right_container, text="Daftar Logistik:", font=("Arial", 11, "bold")).grid(
        row=0, column=0, sticky="w", pady=(0, 10)
    )

    # Bungkus tabel dalam Canvas untuk Scrollbar (Opsional jika daftar sangat panjang)
    frame_tabel = tk.Frame(right_container)
    frame_tabel.grid(row=1, column=0, sticky="nw")

    headers = ["Keterangan", "Uraian Barang", "Vol", "Satuan", "Aksi"]
    for i, h in enumerate(headers):
        tk.Label(frame_tabel, text=h, font=("Arial", 9, "bold")).grid(
            row=0, column=i, padx=5
        )

    rows_logistik = []

    def hapus_baris_spesifik(row_dict):
        for widget in row_dict.values():
            widget.destroy()
        if row_dict in rows_logistik:
            rows_logistik.remove(row_dict)

    def tambah_baris():
        idx = len(rows_logistik) + 1
        # Tambahkan data_logistik sebagai argumen
        new_row = comp.create_logistik_row(
            frame_tabel, idx, hapus_baris_spesifik, data_logistik
        )
        rows_logistik.append(new_row)

    # Tombol Tambah Baris Logistik
    tk.Button(
        right_container,
        text="+ Tambah Item Logistik",
        command=tambah_baris,
        bg="#4CAF50",
        fg="white",
    ).grid(row=2, column=0, sticky="w", pady=10)

    # --- TOMBOL SIMPAN AKHIR (Di bawah form kiri atau floating) ---
    tk.Button(
        left_container,
        text="SIMPAN DATA",
        command=lambda: logic.handle_simpan(
            v_dasar, entri, entri_kec, entri_ass, rows_logistik
        ),
        bg="#2196F3",
        fg="white",
        font=("Arial", 10, "bold"),
        height=2,
    ).grid(row=10, column=0, columnspan=2, pady=30, sticky="ew")

    # Initial Triggers
    tambah_baris()
    trigger_toggle()
    logic.handle_kecamatan_change(
        None, entri["alamat_kec"], entri["alamat_kel"], DATA_KECAMATAN
    )

    root.mainloop()


if __name__ == "__main__":
    main()
