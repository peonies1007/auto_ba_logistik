import tkinter as tk
from tkinter import ttk


def create_label_entry(parent, label_text, row):
    """Membuat Label dan Entry standar"""
    tk.Label(parent, text=label_text).grid(row=row, column=0, sticky="w", pady=2)
    entry = tk.Entry(parent, width=30)
    entry.grid(row=row, column=1, padx=10, pady=2)
    return entry


def create_label_combobox(parent, label_text, row, values):
    """Membuat Label dan Combobox Readonly"""
    tk.Label(parent, text=label_text).grid(row=row, column=0, sticky="w", pady=5)
    cb = ttk.Combobox(parent, values=values, width=27, state="readonly")
    cb.grid(row=row, column=1, padx=10, pady=5)
    cb.set(values[0])
    return cb
