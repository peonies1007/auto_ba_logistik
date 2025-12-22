import tkinter as tk
from date_picker import buat_date_picker
import components as comp
import logic


def main():
    root = tk.Tk()
    root.title("Input Data Logistik")
    root.geometry("450x550")

    # --- BAGIAN 1: DASAR SURAT ---
    tk.Label(root, text="Dasar Surat:", font=("Arial", 10, "bold")).grid(
        row=0, column=0, padx=10, pady=10, sticky="w"
    )
    v_dasar = tk.StringVar(value="kecamatan")
    rb_frame = tk.Frame(root)
    rb_frame.grid(row=0, column=1, sticky="w")

    # Fungsi pembantu untuk toggle
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

    # --- BAGIAN 2: FIELD DINAMIS ---
    # Frame Kecamatan
    frame_kecamatan = tk.Frame(root)
    entri_kec = {
        "surat_dari": comp.create_label_entry(
            frame_kecamatan, "Surat dari Kec/Desa", 0
        ),
        "nomor_surat": comp.create_label_entry(frame_kecamatan, "Nomor Surat", 1),
        "perihal": comp.create_label_entry(frame_kecamatan, "Perihal", 2),
    }

    # Frame Assessment
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
    tk.Label(frame_umum, text="Tanggal").grid(
        row=0, column=0, sticky="w", padx=10, pady=5
    )
    entri["tanggal"] = buat_date_picker(frame_umum)
    entri["tanggal"].grid(row=0, column=1, padx=10, pady=5)

    entri["bencana"] = comp.create_label_combobox(
        frame_umum,
        "Bencana",
        1,
        ["Angin Kencang", "Tanah Longsor", "Banjir", "Kebakaran Rumah"],
    )

    entri["alamat"] = comp.create_label_entry(frame_umum, "Alamat", 2)

    entri["keterangan"] = comp.create_label_combobox(
        frame_umum,
        "Keterangan",
        3,
        ["APBN", "APBD I", "APBD II", "Hibah APBN", "Hibah APBD"],
    )

    # Tombol Simpan
    btn_simpan = tk.Button(
        root,
        text="Simpan Data",
        command=lambda: logic.handle_simpan(v_dasar, entri, entri_kec, entri_ass),
        bg="#2196F3",
        fg="white",
        width=20,
    )
    btn_simpan.grid(row=3, column=0, columnspan=2, pady=20)

    trigger_toggle()
    root.mainloop()


if __name__ == "__main__":
    main()
