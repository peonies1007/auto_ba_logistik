import tkinter as tk
from tkcalendar import DateEntry


def buat_date_picker(parent):
    """
    Membuat DateEntry yang muncul sebagai pop-up.
    Secara default, DateEntry akan menutup (close) jika user
    mengklik di luar area kalender.
    """
    cal = DateEntry(
        parent,
        width=28,
        background="darkblue",
        foreground="white",
        borderwidth=2,
        date_pattern="dd/mm/yyyy",
        # Memastikan user tidak bisa mengetik manual agar tidak error
        state="readonly",
    )
    return cal
