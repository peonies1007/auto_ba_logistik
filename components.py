import tkinter as tk
from tkinter import ttk


def create_label_entry(parent, label_text, row):
    tk.Label(parent, text=label_text).grid(
        row=row, column=0, sticky="w", pady=5, padx=5
    )
    entry = tk.Entry(parent, width=30)
    entry.grid(row=row, column=1, padx=10, pady=5)
    return entry


def create_label_combobox(parent, label_text, row, values):
    """Membuat Label dan Combobox Readonly"""
    tk.Label(parent, text=label_text).grid(
        row=row, column=0, sticky="w", pady=5, padx=10
    )
    cb = ttk.Combobox(parent, values=values, width=27, state="readonly")
    cb.grid(row=row, column=1, padx=10, pady=5)

    # Hanya set nilai default jika list 'values' tidak kosong
    if values:
        cb.set(values[0])
    else:
        cb.set("")  # Kosongkan jika tidak ada data

    return cb


def create_logistik_row(parent, row_index, on_delete, data_logistik):
    row_widgets = {}

    # 1. Dropdown Keterangan (Sumber Dana)
    keys_keterangan = list(data_logistik.keys())
    keterangan = ttk.Combobox(
        parent, values=keys_keterangan, width=15, state="readonly"
    )
    keterangan.grid(row=row_index, column=0, padx=2, pady=2)

    # 2. Dropdown Uraian (Nama Barang)
    uraian = ttk.Combobox(parent, width=25, state="readonly")
    uraian.grid(row=row_index, column=1, padx=2, pady=2)

    # 3. Spinbox Volume
    volume = tk.Spinbox(parent, from_=0, to=9999, width=7)
    volume.grid(row=row_index, column=2, padx=2, pady=2)

    # 4. Entry Satuan (Readonly karena otomatis)
    satuan = tk.Entry(parent, width=10, state="readonly")
    satuan.grid(row=row_index, column=3, padx=2, pady=2)

    # --- LOGIKA INTERNAL BARIS ---

    def on_keterangan_change(event):
        """Update daftar barang berdasarkan sumber dana"""
        sumber = keterangan.get()
        if sumber in data_logistik:
            daftar_barang = [item["nama_barang"] for item in data_logistik[sumber]]
            uraian["values"] = daftar_barang
            uraian.set("")
            satuan.config(state="normal")
            satuan.delete(0, tk.END)
            satuan.config(state="readonly")

    def on_uraian_change(event):
        """Update satuan berdasarkan barang yang dipilih"""
        sumber = keterangan.get()
        barang_nama = uraian.get()
        if sumber in data_logistik:
            for item in data_logistik[sumber]:
                if item["nama_barang"] == barang_nama:
                    satuan.config(state="normal")
                    satuan.delete(0, tk.END)
                    satuan.insert(0, item["satuan"])
                    satuan.config(state="readonly")
                    break

    keterangan.bind("<<ComboboxSelected>>", on_keterangan_change)
    uraian.bind("<<ComboboxSelected>>", on_uraian_change)

    # Tombol Hapus
    btn_hapus = tk.Button(
        parent,
        text="X",
        fg="white",
        bg="#f44336",
        command=lambda: on_delete(row_widgets),
    )
    btn_hapus.grid(row=row_index, column=4, padx=5, pady=2)

    row_widgets = {
        "keterangan": keterangan,
        "uraian": uraian,
        "volume": volume,
        "satuan": satuan,
        "btn_hapus": btn_hapus,
    }
    return row_widgets
