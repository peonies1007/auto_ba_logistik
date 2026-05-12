import tkinter as tk
from tkinter import ttk
from date_picker import buat_date_picker
from data_wilayah import DATA_KECAMATAN
import components as comp
from logic.handle_simpan import handle_simpan
import logic.logic as logic
from data_logistik import data_logistik


def main():
    root = tk.Tk()
    root.title("Input Data Logistik & Dashboard Stok")

    # 1. MEMBUAT APLIKASI LANGSUNG FULLSCREEN (MAXIMIZED)
    root.state("zoomed")
    # Catatan: Jika ingin fullscreen total tanpa tombol X (close) di atas layar,
    # gunakan: root.attributes('-fullscreen', True)

    # --- PENGATURAN TEMA UNTUK TABEL ---
    style = ttk.Style()
    # Menggunakan tema 'clam' yang mendukung modifikasi border/garis
    style.theme_use("clam")

    # Konfigurasi bentuk tabel
    style.configure(
        "Treeview",
        background="white",
        foreground="black",
        rowheight=25,
        fieldbackground="white",
        borderwidth=1,
    )

    # Konfigurasi Header (Judul Kolom Tabel) agar ada garis pembatasnya
    style.configure(
        "Treeview.Heading",
        background="#d3d3d3",
        font=("Arial", 9, "bold"),
        relief="solid",
        borderwidth=1,
    )

    # Mengubah warna highlight saat baris diklik
    style.map("Treeview", background=[("selected", "#2196F3")])

    # --- CONTAINER UTAMA ---
    root.columnconfigure(0, weight=0)
    root.columnconfigure(1, weight=0)
    root.columnconfigure(2, weight=1)
    root.rowconfigure(0, weight=1)

    # --- FRAME KIRI (DATA DASAR & UMUM) ---
    left_container = tk.Frame(root, padx=10, pady=10)
    left_container.grid(row=0, column=0, sticky="nsw")

    # Dasar Surat
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
    }

    tk.Label(frame_kecamatan, text="Tanggal Surat").grid(
        row=2, column=0, sticky="w", pady=2
    )
    entri_kec["tgl_surat"] = buat_date_picker(frame_kecamatan)
    entri_kec["tgl_surat"].grid(row=2, column=1, padx=10, pady=2, sticky="w")
    entri_kec["perihal"] = comp.create_label_entry(frame_kecamatan, "Perihal", 3)

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

    # Field Umum
    frame_umum = tk.Frame(left_container)
    frame_umum.grid(row=2, column=0, columnspan=2, pady=10, sticky="w")
    entri = {}

    tk.Label(frame_umum, text="Tanggal Distribusi").grid(
        row=0, column=0, sticky="w", padx=10, pady=2
    )
    entri["tanggal"] = buat_date_picker(frame_umum)
    entri["tanggal"].grid(row=0, column=1, padx=10, pady=2)

    entri["bencana"] = comp.create_label_combobox(
        frame_umum,
        "Bencana",
        1,
        [
            "Angin Kencang",
            "Tanah Longsor",
            "Banjir",
            "Kebakaran Rumah",
            "Rumah Roboh",
            "Backup Dapur Umum",
            "Kerja Bakti",
        ],
    )
    entri["bencana"].configure(state="normal")

    tk.Label(frame_umum, text="Alamat:", font=("Arial", 9, "bold")).grid(
        row=2, column=0, sticky="w", padx=10, pady=5
    )
    entri["alamat_kec"] = comp.create_label_combobox(
        frame_umum, "Kecamatan", 3, [d["kecamatan"] for d in DATA_KECAMATAN]
    )
    entri["alamat_kel"] = comp.create_label_combobox(
        frame_umum, "Kelurahan/Desa", 4, []
    )
    entri["alamat_kel"].configure(state="normal")

    entri["alamat_kec"].bind(
        "<<ComboboxSelected>>",
        lambda e: logic.handle_kecamatan_change(
            e, entri["alamat_kec"], entri["alamat_kel"], DATA_KECAMATAN
        ),
    )

    entri["alamat_dukuh"] = comp.create_label_entry(frame_umum, "Dukuh/Kampung", 5)

    # --- FRAME TENGAH (INPUT LOGISTIK) ---
    right_container = tk.Frame(root, padx=20, pady=10, relief="groove", borderwidth=1)
    right_container.grid(row=0, column=1, sticky="nsew")

    tk.Label(right_container, text="Input Logistik:", font=("Arial", 11, "bold")).grid(
        row=0, column=0, sticky="w", pady=(0, 10)
    )

    frame_tabel = tk.Frame(right_container)
    frame_tabel.grid(row=1, column=0, sticky="nw")

    headers = ["No.", "Keterangan", "Uraian Barang", "Vol", "Satuan", "Aksi"]
    for i, h in enumerate(headers):
        # Menambahkan garis (relief=solid) pada judul kolom tabel input
        tk.Label(
            frame_tabel,
            text=h,
            font=("Arial", 9, "bold"),
            relief="solid",
            borderwidth=1,
            padx=3,
            pady=2,
        ).grid(row=0, column=i, sticky="nsew")

    rows_logistik = []

    def hapus_baris_spesifik(row_dict):
        for widget in row_dict.values():
            if widget.winfo_exists():
                widget.destroy()
        if row_dict in rows_logistik:
            rows_logistik.remove(row_dict)
        for index, row_data in enumerate(rows_logistik):
            row_data["lbl_nomor"].config(text=f"{index + 1}.")

    def tambah_baris():
        idx = len(rows_logistik) + 1
        new_row = comp.create_logistik_row(
            frame_tabel, idx, hapus_baris_spesifik, data_logistik
        )
        rows_logistik.append(new_row)

    tk.Button(
        right_container,
        text="+ Tambah Item",
        command=tambah_baris,
        bg="#4CAF50",
        fg="white",
    ).grid(row=2, column=0, sticky="w", pady=10)

    # --- FRAME PALING KANAN (DASHBOARD STOK) ---
    dashboard_container = tk.Frame(root, padx=15, pady=10, bg="#f8f9fa")
    dashboard_container.grid(row=0, column=2, sticky="nsew")
    dashboard_container.columnconfigure(0, weight=1)

    tk.Label(
        dashboard_container,
        text="STATUS STOK LOGISTIK",
        font=("Arial", 11, "bold"),
        bg="#f8f9fa",
        fg="#333",
    ).grid(row=0, column=0, pady=(0, 20))

    tree_frame = tk.Frame(dashboard_container)
    tree_frame.grid(row=1, column=0, sticky="nsew")
    dashboard_container.rowconfigure(1, weight=1)

    kolom_dash = ("no", "sumber", "nama", "satuan", "stok")

    # 2. MENGECILKAN UKURAN TABEL (Dari height=25 menjadi height=15)
    tabel_stok = ttk.Treeview(
        tree_frame, columns=kolom_dash, show="headings", height=15
    )

    tabel_stok.heading("no", text="No")
    tabel_stok.heading("sumber", text="Sumber")
    tabel_stok.heading("nama", text="Nama Barang")
    tabel_stok.heading("satuan", text="Sat")
    tabel_stok.heading("stok", text="Stok")

    tabel_stok.column("no", width=20, anchor="center")
    tabel_stok.column("sumber", width=80)
    tabel_stok.column("nama", width=180)
    tabel_stok.column("satuan", width=60, anchor="center")
    tabel_stok.column("stok", width=40, anchor="center")

    # 3. WARNA BELANG/GARIS PEMBATAS BARIS
    # Mendefinisikan warna untuk tag 'genap' dan 'ganjil'
    tabel_stok.tag_configure("ganjil", background="white")
    tabel_stok.tag_configure("genap", background="#e9ecef")  # Abu-abu terang

    vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=tabel_stok.yview)
    tabel_stok.configure(yscrollcommand=vsb.set)
    tabel_stok.pack(side="left", fill="both", expand=True)
    vsb.pack(side="right", fill="y")

    def isi_tabel_stok(data_list):
        tabel_stok.delete(*tabel_stok.get_children())
        for index, item in enumerate(data_list, start=1):
            # Tentukan baris ini ganjil atau genap untuk selang-seling warna
            tag_baris = "genap" if index % 2 == 0 else "ganjil"

            tabel_stok.insert(
                "",
                "end",
                values=(index, item[0], item[1], item[2], item[3]),
                tags=(tag_baris,),
            )

    def muat_data_otomatis():
        def tugas_ambil_data():
            status, hasil = logic.ambil_data_spreadsheet()
            if status:
                root.after(0, lambda: isi_tabel_stok(hasil))
            return status, "Stok diperbarui" if status else hasil

        comp.backup_dengan_loading(tugas_ambil_data)

    tk.Button(
        dashboard_container,
        text="Refresh Data Stok",
        command=muat_data_otomatis,
        bg="#6c757d",
        fg="white",
    ).grid(row=2, column=0, pady=10)

    # --- TOMBOL SIMPAN ---
    tk.Button(
        left_container,
        text="SIMPAN DATA",
        bg="#2196F3",
        fg="white",
        font=("Arial", 10, "bold"),
        height=2,
        command=lambda: handle_simpan(
            v_dasar, entri, entri_kec, entri_ass, rows_logistik
        ),
    ).grid(row=10, column=0, columnspan=2, pady=30, sticky="ew")

    # Initial Triggers
    tambah_baris()
    trigger_toggle()
    logic.handle_kecamatan_change(
        None, entri["alamat_kec"], entri["alamat_kel"], DATA_KECAMATAN
    )

    root.after(500, muat_data_otomatis)

    root.mainloop()


if __name__ == "__main__":
    main()
