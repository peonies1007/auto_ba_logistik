import tkinter as tk
from tkinter import ttk


def create_label_entry(parent, label_text, row):
    tk.Label(parent, text=label_text).grid(row=row, column=0, sticky="w", pady=2)
    entry = tk.Entry(parent, width=30)
    entry.grid(row=row, column=1, padx=10, pady=2)
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


def create_logistik_row(parent, row_index, on_delete):
    """
    Membuat satu baris logistik dengan tombol hapus spesifik.
    on_delete: fungsi yang dipanggil saat tombol hapus diklik.
    """
    # Container untuk menyimpan widget agar mudah dikelola
    row_widgets = {}

    uraian = tk.Entry(parent, width=20)
    uraian.grid(row=row_index, column=0, padx=2, pady=2)

    volume = tk.Entry(parent, width=8)
    volume.grid(row=row_index, column=1, padx=2, pady=2)

    satuan = tk.Entry(parent, width=10)
    satuan.grid(row=row_index, column=2, padx=2, pady=2)

    keterangan = tk.Entry(parent, width=15)
    keterangan.grid(row=row_index, column=3, padx=2, pady=2)

    # Tombol Hapus Baris Ini
    btn_hapus = tk.Button(
        parent,
        text="X",
        fg="white",
        bg="#f44336",
        command=lambda: on_delete(row_widgets),
    )
    btn_hapus.grid(row=row_index, column=4, padx=5, pady=2)

    row_widgets = {
        "uraian": uraian,
        "volume": volume,
        "satuan": satuan,
        "keterangan": keterangan,
        "btn_hapus": btn_hapus,
    }

    return row_widgets
