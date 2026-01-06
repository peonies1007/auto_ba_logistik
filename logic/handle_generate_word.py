from docxtpl import DocxTemplate
from docx import Document
import os
from docxcompose.composer import Composer  # Tambahkan ini


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
                **context_core,
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
    if data_umum["tanggal_int"] < 10:
        kode_awal_name_tanggal = f"0{data_umum['tanggal_int']}"
    else:
        kode_awal_name_tanggal = data_umum["tanggal_int"]
    if data_umum["bulan_int"] < 10:
        kode_awal_name_bulan = f"0{data_umum['bulan_int']}"
    else:
        kode_awal_name_bulan = data_umum["bulan_int"]

    output_name = f"{kode_awal_name_tanggal}{kode_awal_name_bulan}-BA Logistik-{data_umum['tanggal_lengkap']}-{data_umum['alamat_kel']}-Kec. {data_umum['alamat_kec']}.docx"
    composer.save(output_name)

    # Bersihkan file sementara
    for temp_file in ["temp_result.docx", "temp_sub.docx"]:
        if os.path.exists(temp_file):
            os.remove(temp_file)

    return output_name
