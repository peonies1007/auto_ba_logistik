def handle_toggle(v_dasar, frame_kec, frame_ass):
    frame_kec.grid_remove()
    frame_ass.grid_remove()
    # Sekarang kita gunakan row=1 di dalam kontainer kirinya
    if v_dasar.get() == "kecamatan":
        frame_kec.grid(row=1, column=0, columnspan=2, sticky="w", padx=10, pady=5)
    else:
        frame_ass.grid(row=1, column=0, columnspan=2, sticky="w", padx=10, pady=5)


def handle_kecamatan_change(event, cb_kecamatan, cb_desa, data_wilayah):
    """Update pilihan di dropdown desa berdasarkan kecamatan yang dipilih"""
    kecamatan_terpilih = cb_kecamatan.get()

    # Cari daftar wilayah untuk kecamatan tersebut
    desa_list = []
    for item in data_wilayah:
        if item["kecamatan"] == kecamatan_terpilih:
            # Gabungkan Nama + Status (Contoh: "Sine (Kelurahan)")
            desa_list = [f"{d['status']} {d['nama']}" for d in item["daftar_wilayah"]]
            break

    # Masukkan list baru ke combobox desa
    cb_desa["values"] = desa_list
    if desa_list:
        cb_desa.set(desa_list[0])  # Set ke item pertama
    else:
        cb_desa.set("")
