import tkinter as tk
from tkinter import messagebox


def toggle_fields():
    # Sembunyikan semua field dinamis terlebih dahulu
    frame_kecamatan.grid_remove()
    frame_assessment.grid_remove()

    # Tampilkan berdasarkan pilihan Radio Button
    if v_dasar.get() == "kecamatan":
        frame_kecamatan.grid(row=1, column=0, columnspan=2, sticky="w", padx=10, pady=5)
    else:
        frame_assessment.grid(
            row=1, column=0, columnspan=2, sticky="w", padx=10, pady=5
        )


def simpan_data():
    # Mengambil data dari field umum
    data = {
        "dasar_surat": v_dasar.get(),
        "tanggal_lengkap": entri["tanggal_lengkap"].get(),
        "bencana": entri["bencana"].get(),
        "alamat": entri["alamat"].get(),
        "keterangan": entri["keterangan"].get(),
    }

    # Menambahkan data spesifik berdasarkan pilihan
    if v_dasar.get() == "kecamatan":
        data.update(
            {
                "surat_dari": entri_kec["surat_dari"].get(),
                "nomor_surat": entri_kec["nomor_surat"].get(),
                "perihal": entri_kec["perihal"].get(),
            }
        )
    else:
        data.update({"tanggal_assessment": entri_ass["tgl_ass"].get()})

    print("Data Terinput:", data)
    messagebox.showinfo("Berhasil", "Data berhasil diproses!")


root = tk.Tk()
root.title("Input Data Logistik")
root.geometry("450x500")

# --- BAGIAN 1: DASAR SURAT (RADIO BUTTON) ---
tk.Label(root, text="Dasar Surat:", font=("Arial", 10, "bold")).grid(
    row=0, column=0, padx=10, pady=10, sticky="w"
)
v_dasar = tk.StringVar(value="kecamatan")

rb_frame = tk.Frame(root)
rb_frame.grid(row=0, column=1, sticky="w")
tk.Radiobutton(
    rb_frame,
    text="Kecamatan",
    variable=v_dasar,
    value="kecamatan",
    command=toggle_fields,
).pack(side="left")
tk.Radiobutton(
    rb_frame,
    text="Assessment",
    variable=v_dasar,
    value="assessment",
    command=toggle_fields,
).pack(side="left")

# --- BAGIAN 2: FIELD DINAMIS (KONDISIONAL) ---
# Frame untuk pilihan Kecamatan
frame_kecamatan = tk.Frame(root)
entri_kec = {}
labels_kec = [
    ("Surat dari Kec/Desa/Kel", "surat_dari"),
    ("Nomor Surat", "nomor_surat"),
    ("Perihal", "perihal"),
]

for i, (teks, key) in enumerate(labels_kec):
    tk.Label(frame_kecamatan, text=teks).grid(row=i, column=0, sticky="w", pady=2)
    e = tk.Entry(frame_kecamatan, width=30)
    e.grid(row=i, column=1, padx=10, pady=2)
    entri_kec[key] = e

# Frame untuk pilihan Assessment
frame_assessment = tk.Frame(root)
tk.Label(frame_assessment, text="Tanggal Assessment").grid(
    row=0, column=0, sticky="w", pady=2
)
entri_ass = {"tgl_ass": tk.Entry(frame_assessment, width=30)}
entri_ass["tgl_ass"].grid(row=0, column=1, padx=10, pady=2)

# --- BAGIAN 3: FIELD UMUM (SETELAH PENGHAPUSAN) ---
frame_umum = tk.Frame(root)
frame_umum.grid(row=2, column=0, columnspan=2, pady=10)

# Field yang tersisa: tanggal_lengkap, bencana, alamat, keterangan
fields_umum = ["tanggal_lengkap", "bencana", "alamat", "keterangan"]
entri = {}

for i, field in enumerate(fields_umum):
    tk.Label(frame_umum, text=field.replace("_", " ").title()).grid(
        row=i, column=0, sticky="w", padx=10, pady=5
    )
    e = tk.Entry(frame_umum, width=40)
    e.grid(row=i, column=1, padx=10, pady=5)
    entri[field] = e

# Tombol Simpan
tk.Button(
    root, text="Simpan Data", command=simpan_data, bg="#2196F3", fg="white", width=20
).grid(row=3, column=0, columnspan=2, pady=20)

# Inisialisasi tampilan pertama kali
toggle_fields()

root.mainloop()
