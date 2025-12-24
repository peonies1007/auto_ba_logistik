import ttkbootstrap as tb
from ttkbootstrap.widgets import DateEntry


def buat_date_picker(parent):
    # Menggunakan DateEntry dari ttkbootstrap
    cal = DateEntry(parent, bootstyle="primary", dateformat="%d/%m/%Y")
    return cal
