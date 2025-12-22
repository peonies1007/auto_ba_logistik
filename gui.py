import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from date_picker import buat_date_picker


def toggle_fields():
    frame_kecamatan.grid_remove()
    frame_assessment.grid_remove()

    if v_dasar.get() == "kecamatan":
        frame_kecamatan.grid(row=1, column=0, columnspan=2, sticky="w", padx=10, pady=5)
    else:
        frame_assessment.grid(
            row=1, column=0, columnspan=2, sticky="w", padx=10, pady=5
        )


def simpan_data():
    # Mengambil data dengan kunci "tanggal"
    data = {
        "dasar_surat": v_dasar.get(),
        "tanggal": entri["tanggal"].get(),
        "bencana": entri["bencana"].get(),
        "alamat": entri["alamat"].get(),
        "keterangan": entri["keterangan"].get(),
    }

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
    messagebox.showinfo(
        "Berhasil", f"Data Berhasil Disimpan!\nTanggal: {data['tanggal']}"
    )


root = tk.Tk()
root.title("Input Data Logistik")
root.geometry("450x500")

# --- BAGIAN 1: DASAR SURAT ---
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

# --- BAGIAN 2: FIELD DINAMIS ---
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

frame_assessment = tk.Frame(root)
tk.Label(frame_assessment, text="Tanggal Assessment").grid(
    row=0, column=0, sticky="w", pady=2
)
entri_ass = {"tgl_ass": buat_date_picker(frame_assessment)}
entri_ass["tgl_ass"].grid(row=0, column=1, padx=10, pady=2)

# --- BAGIAN 3: FIELD UMUM ---
frame_umum = tk.Frame(root)
frame_umum.grid(row=2, column=0, columnspan=2, pady=10, sticky="w")

entri = {}

# 1. Field Tanggal
tk.Label(frame_umum, text="Tanggal").grid(row=0, column=0, sticky="w", padx=10, pady=5)
entri["tanggal"] = buat_date_picker(frame_umum)
entri["tanggal"].grid(row=0, column=1, padx=10, pady=5)

# 2. Field Bencana (Dropdown)
tk.Label(frame_umum, text="Bencana").grid(row=1, column=0, sticky="w", padx=10, pady=5)
list_bencana = ["Angin Kencang", "Tanah Longsor", "Banjir", "Kebakaran Rumah"]
cb_bencana = ttk.Combobox(frame_umum, values=list_bencana, width=27, state="readonly")
cb_bencana.grid(row=1, column=1, padx=10, pady=5)
cb_bencana.set(list_bencana[0])
entri["bencana"] = cb_bencana

# 3. Field Alamat (Input Manual)
tk.Label(frame_umum, text="Alamat").grid(row=2, column=0, sticky="w", padx=10, pady=5)
entri["alamat"] = tk.Entry(frame_umum, width=30)
entri["alamat"].grid(row=2, column=1, padx=10, pady=5)

# 4. Field Keterangan (Dropdown Baru)
tk.Label(frame_umum, text="Keterangan").grid(
    row=3, column=0, sticky="w", padx=10, pady=5
)
list_keterangan = ["APBN", "APBD I", "APBD II", "Hibah APBN", "Hibah APBD"]
cb_keterangan = ttk.Combobox(
    frame_umum, values=list_keterangan, width=27, state="readonly"
)
cb_keterangan.grid(row=3, column=1, padx=10, pady=5)
cb_keterangan.set(list_keterangan[0])
entri["keterangan"] = cb_keterangan
# Tombol Simpan
tk.Button(
    root, text="Simpan Data", command=simpan_data, bg="#2196F3", fg="white", width=20
).grid(row=3, column=0, columnspan=2, pady=20)

toggle_fields()
root.mainloop()
