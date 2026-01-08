from tkinter import messagebox
from .logic import upload_to_drive
from .logic_formatter import get_indonesia_date
from .constant import bulan_nama
from .handle_generate_word import generate_word_output
from components import backup_dengan_loading

def handle_simpan(v_dasar, entri, entri_kec, entri_ass, list_logistik):
    data = {}

    # FIX: Gunakan get_date() untuk DateEntry
    try:
        obj_tanggal = entri["tanggal"].get_date()
        # Konversi ke string dd/mm/yyyy untuk fungsi get_indonesia_date
        str_tanggal = obj_tanggal.strftime("%d/%m/%Y")
    except AttributeError:
        # Jika ternyata bukan DateEntry (fallback)
        str_tanggal = entri["tanggal"].get()

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
        "alamat_kel": entri["alamat_kel"].get(),
        "dasar_surat_text": txt_dasar,
    }

    # Ambil list logistik dari widget tabel [cite: 16, 33, 50, 66, 86, 103]
    logistik_data = []
    teks_logistik = ""
    for i, row in enumerate(list_logistik, 1):
        uraian_val = row["uraian"].get()
        if uraian_val:
            vol = row["volume"].get()
            sat = row["satuan"].get()
            ket_raw = row["keterangan"].get()
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
            teks_logistik += f"{i}. {uraian_val} ({vol} {sat}) - {ket_clean}\n"

    pesan_konfirmasi = (
        f"PERIKSA KEMBALI DATA ANDA:\n\n"
        f"--- DATA UMUM ---\n"
        f"Tanggal BA: {waktu['tanggal_lengkap']}\n"
        f"Jenis Bencana: {data_umum['bencana']}\n"
        f"Lokasi: {data_umum['alamat_string']}\n\n"
        f"--- DASAR SURAT ---\n"
        f"{txt_dasar}\n\n"
        f"--- DAFTAR LOGISTIK ---\n"
        f"{teks_logistik if teks_logistik else '(Belum ada item)'}\n"
        f"---------------------------\n"
        f"Apakah data di atas sudah benar?"
    )

    if not logistik_data:
        messagebox.showwarning("Peringatan", "Daftar logistik masih kosong!")
        return

    # Tampilkan Message Box Konfirmasi dengan tambahan info backup
    konfirmasi_lokal = messagebox.askyesno("Konfirmasi Simpan", pesan_konfirmasi)

    if konfirmasi_lokal:  # Jika user menekan 'Yes'
        # Jalankan Export ke Word
        try:
            output_file = generate_word_output(data_umum, logistik_data)

            messagebox.showinfo(
                "Berhasil", f"Data Berhasil Disimpan!\nFile: {output_file}"
            )

        except Exception as e:
            messagebox.showerror("Error", f"Gagal menyimpan file: {str(e)}")
        # Tampilkan Message Box Konfirmasi dengan tambahan info backup
        konfirmasi_backup = messagebox.askyesno(
            "Konfirmasi Backup Drive",
            "Apakah ingin Backup ke Google Drive juga?",
        )

        if konfirmasi_backup:  # Jika user menekan 'Yes'
            try:
                backup_dengan_loading(output_file)
            except Exception as e:
                messagebox.showerror("Error", f"Gagal backup file: {str(e)}")
        else:
            # Jika user menekan 'No', proses dibatalkan
            pass
    else:
        # Jika user menekan 'No', proses dibatalkan
        pass
