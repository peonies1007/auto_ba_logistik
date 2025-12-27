import datetime
from .constant import bilangan, hari_nama, bulan_nama


def angka_ke_kata(n):
    if n < 12:
        return bilangan[n]
    elif n < 20:
        return bilangan[n - 10] + " Belas"
    elif n < 100:
        return bilangan[n // 10] + " Puluh " + bilangan[n % 10]
    elif n < 200:
        return "Seratus " + angka_ke_kata(n - 100)
    # n untuk tanggal maksimal hanya sampai 31, jadi logika di atas sudah cukup
    return str(n)


def get_indonesia_date(date_str):
    """Konversi dd/mm/yyyy ke format tanggal, hari, bulan Indonesia"""

    d, m, y = map(int, date_str.split("/"))
    dt = datetime.date(y, m, d)

    return {
        "hari": hari_nama[dt.weekday()],
        "tanggal": angka_ke_kata(d).strip(),
        "tanggal_int": d,
        "bulan": bulan_nama[m - 1],
        "bulan_int": m,
        "tahun": y,
        "tanggal_lengkap": f"{d} {bulan_nama[m - 1]} {y}",
    }
