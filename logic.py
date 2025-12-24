from tkinter import messagebox


def handle_simpan(v_dasar, entri, entri_kec, entri_ass, list_logistik):
    # Mengambil data alamat gabungan atau terpisah
    kec = entri["alamat_kec"].get()
    kel = entri["alamat_kel"].get()
    dukuh = entri["alamat_dukuh"].get()
    alamat_lengkap = f"Dukuh {dukuh}, Desa {kel}, Kec. {kec}"

    data = {
        "dasar_surat": v_dasar.get(),
        "tanggal": entri["tanggal"].get(),
        "bencana": entri["bencana"].get(),
        "alamat_detail": {"kecamatan": kec, "ds_kel": kel, "dukuh": dukuh},
        "alamat_string": alamat_lengkap,
        "keterangan_dasar": entri["keterangan"].get(),
        "logistik": [],
    }

    # Ambil data dari tabel logistik yang dinamis
    for item in list_logistik:
        u = item["uraian"].get()
        v = item["volume"].get()
        s = item["satuan"].get()
        k = item["keterangan"].get()

        # Hanya simpan jika uraian tidak kosong
        if u.strip():
            data["logistik"].append(
                {"uraian": u, "volume": v, "satuan": s, "keterangan": k}
            )

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
        "Berhasil", f"Data Disimpan! {len(data['logistik'])} item logistik tercatat."
    )


def handle_toggle(v_dasar, frame_kec, frame_ass):
    frame_kec.grid_remove()
    frame_ass.grid_remove()
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
            desa_list = [f"{d['nama']} ({d['status']})" for d in item["daftar_wilayah"]]
            break

    # Masukkan list baru ke combobox desa
    cb_desa["values"] = desa_list
    if desa_list:
        cb_desa.set(desa_list[0])  # Set ke item pertama
    else:
        cb_desa.set("")
