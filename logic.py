from tkinter import messagebox
import datetime
from docxtpl import DocxTemplate
from docx import Document
import os
from docxcompose.composer import Composer  # Tambahkan ini

bulan_nama = [
    "Januari",
    "Februari",
    "Maret",
    "April",
    "Mei",
    "Juni",
    "Juli",
    "Agustus",
    "September",
    "Oktober",
    "November",
    "Desember",
]


def handle_simpan(v_dasar, entri, entri_kec, entri_ass, list_logistik):
    # Mengambil data alamat gabungan atau terpisah
    kec = entri["alamat_kec"].get()
    kel = entri["alamat_kel"].get()
    dukuh = entri["alamat_dukuh"].get()
    alamat_lengkap = f"Dukuh {dukuh}, Desa {kel}, Kec. {kec}"

    # FIX: Gunakan get_date() untuk DateEntry
    try:
        obj_tanggal = entri["tanggal"].get_date()
        # Konversi ke string dd/mm/yyyy untuk fungsi get_indonesia_date
        str_tanggal = obj_tanggal.strftime("%d/%m/%Y")
    except AttributeError:
        # Jika ternyata bukan DateEntry (fallback)
        str_tanggal = entri["tanggal"].get()

    data = {
        "dasar_surat": v_dasar.get(),
        "tanggal": entri["tanggal"].get_date(),
        "bencana": entri["bencana"].get(),
        "alamat_detail": {"kecamatan": kec, "ds_kel": kel, "dukuh": dukuh},
        "alamat_string": alamat_lengkap,
        "keterangan_dasar": entri,
        "logistik": [],
    }

    # Ambil data dari tabel logistik yang dinamis
    logistik_final = []
    for item in list_logistik:
        uraian_val = item["uraian"].get()
        if uraian_val:  # Hanya simpan jika barang sudah dipilih
            logistik_final.append(
                {
                    "keterangan": item["keterangan"].get(),
                    "uraian": uraian_val,
                    "volume": item["volume"].get(),
                    "satuan": item["satuan"].get(),
                }
            )

    data["logistik"] = logistik_final

    if v_dasar.get() == "kecamatan":
        data.update(
            {
                "surat_dari": entri_kec["surat_dari"].get(),
                "nomor_surat": entri_kec["nomor_surat"].get(),
                "perihal": entri_kec["perihal"].get(),
            }
        )
    else:
        data.update({"tanggal_assessment": entri_ass["tgl_ass"].get_date()})

    # Siapkan data waktu untuk template (Indonesian Format)
    waktu = get_indonesia_date(str_tanggal)

    # Format dasar surat untuk template core [cite: 55]
    if v_dasar.get() == "kecamatan":
        # Ambil tanggal dari date picker kecamatan
        tgl_obj = entri_kec["tgl_surat"].get_date()
        tgl_surat_fmt = f"{tgl_obj.day} {bulan_nama[tgl_obj.month - 1]} {tgl_obj.year}"

        # Gabungkan teks untuk {{ dasar_surat }}
        txt_dasar = (
            f"surat dari {entri_kec['surat_dari'].get()} "
            f"No. {entri_kec['nomor_surat'].get()} "
            f"tanggal {tgl_surat_fmt} "
            f"perihal {entri_kec['perihal'].get()}"
        )
    else:
        # Ambil tanggal assessment dengan get_date() juga
        tgl_ass_obj = entri_ass["tgl_ass"].get_date()
        hari = tgl_ass_obj.day
        bulan = bulan_nama[tgl_ass_obj.month - 1]
        tahun = tgl_ass_obj.year

        tgl_ass_formatted = f"{hari} {bulan} {tahun}"

        # 4. Masukkan ke teks dasar surat
        txt_dasar = f"hasil assessment tanggal {tgl_ass_formatted} tentang kejadian {entri['bencana'].get()}"

    # Data Umum sesuai template [cite: 13, 30, 47, 64, 83, 100]
    data_umum = {
        **waktu,  # Memasukkan hari, tanggal, bulan, tahun, tanggal_lengkap
        "bencana": entri["bencana"].get(),
        "alamat_string": f"{entri['alamat_dukuh'].get()}, {entri['alamat_kel'].get()}, Kec. {entri['alamat_kec'].get()}",
        "alamat_kec": entri["alamat_kec"].get(),
        "dasar_surat_text": txt_dasar,
    }

    # Ambil list logistik dari widget tabel [cite: 16, 33, 50, 66, 86, 103]
    logistik_data = []
    for row in list_logistik:
        uraian_val = row["uraian"].get()
        if uraian_val:
            # Ambil nilai keterangan asli (misal: "HIBAH_APBN")
            ket_raw = row["keterangan"].get()

            # Hilangkan underscore untuk tampilan di tabel Word (misal: "HIBAH APBN")
            ket_clean = ket_raw.replace("_", " ")

            logistik_data.append(
                {
                    "keterangan": ket_clean,  # Ini yang akan tampil di kolom Keterangan Word
                    "keterangan_raw": ket_raw,  # Simpan versi asli untuk memilih template file"uraian": uraian_val,
                    "uraian": uraian_val,
                    "volume": row["volume"].get(),
                    "satuan": row["satuan"].get(),
                }
            )

    # Jalankan Export ke Word
    generate_word_output(data_umum, logistik_data)
    # print("Data Terinput:", data)
    messagebox.showinfo(
        "Berhasil", f"Data Disimpan! {len(data['logistik'])} item logistik tercatat."
    )


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


def angka_ke_kata(n):
    bilangan = [
        "",
        "Satu",
        "Dua",
        "Tiga",
        "Empat",
        "Lima",
        "Enam",
        "Tujuh",
        "Delapan",
        "Sembilan",
        "Sepuluh",
        "Sebelas",
    ]
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
    hari_nama = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]

    d, m, y = map(int, date_str.split("/"))
    dt = datetime.date(y, m, d)

    return {
        "hari": hari_nama[dt.weekday()],
        "tanggal": angka_ke_kata(d).strip(),
        "bulan": bulan_nama[m - 1],
        "tahun": y,
        "tanggal_lengkap": f"{d} {bulan_nama[m - 1]} {y}",
    }


def generate_word_output(data_umum, list_logistik):
    # 1. Kelompokkan Logistik berdasarkan Keterangan
    grouped_logistik = {}
    for item in list_logistik:
        ket = item["keterangan_raw"]
        if ket not in grouped_logistik:
            grouped_logistik[ket] = []
        grouped_logistik[ket].append(item)

    # 2. Render Halaman Pertama (CORE)
    context_core = {
        "hari": data_umum["hari"],
        "tanggal": data_umum["tanggal"],
        "bulan": data_umum["bulan"],
        "tanggal_lengkap": data_umum["tanggal_lengkap"],
        "dasar_surat": data_umum["dasar_surat_text"],
        "bencana": data_umum["bencana"],
        "alamat": data_umum["alamat_string"],
        "daftar_logistik": list_logistik,
    }

    doc_main_tpl = DocxTemplate("template_ba_logistik_core.docx")
    doc_main_tpl.render(context_core)
    doc_main_tpl.save("temp_result.docx")

    # Gunakan Composer untuk mempertahankan format saat penggabungan
    master_doc = Document("temp_result.docx")
    composer = Composer(master_doc)

    # 3. Tambahkan Halaman BAST per Sumber Dana
    for keterangan, items in grouped_logistik.items():
        template_path = f"template_ba_logistik_{keterangan}.docx"

        if os.path.exists(template_path):
            # Render sub-template
            sub_tpl = DocxTemplate(template_path)
            context_bast = {
                **data_umum,
                "daftar_logistik": items,
            }
            sub_tpl.render(context_bast)
            sub_tpl.save("temp_sub.docx")

            # Load dokumen sub yang baru dirender
            doc_to_add = Document("temp_sub.docx")

            # Tambahkan Page Break pada dokumen sumber sebelum digabung
            # (Agar setiap BAST mulai di halaman baru)
            master_doc.add_page_break()

            # GABUNGKAN dengan Composer (Ini akan menjaga list Romawi tetap ada)
            composer.append(doc_to_add)

    # 4. Simpan Final
    output_name = f"BA_LOGISTIK_{data_umum['tanggal']}_{data_umum['alamat_kec']}.docx"
    composer.save(output_name)

    # Bersihkan file sementara
    for temp_file in ["temp_result.docx", "temp_sub.docx"]:
        if os.path.exists(temp_file):
            os.remove(temp_file)

    return output_name
