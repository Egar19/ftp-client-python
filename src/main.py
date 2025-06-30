from ftplib import FTP
import os

def login_ftp():
    """Login dengan validasi input dari pengguna (support anonymous)"""
    print("=== LOGIN FTP ===")

    while True:
        host = input("Alamat IP FTP: ").strip()
        if host:
            break
        print("❌ Alamat tidak boleh kosong")

    while True:
        port_input = input("Port [default 21]: ").strip()
        if not port_input:
            port = 21
            break
        if port_input.isdigit():
            port = int(port_input)
            break
        print("❌ Port harus berupa angka")

    while True:
        mode = input("Login sebagai (1) User biasa / (2) Anonymous [1/2]: ").strip()
        if mode in ['1', '2']:
            break
        print("❌ Pilih 1 atau 2")

    try:
        ftp = FTP()
        ftp.connect(host=host, port=port)

        if mode == '2':
            ftp.login()
            print(f"\n✅ Login anonymous berhasil ke {host}")
        else:
            while True:
                user = input("Username: ").strip()
                if user:
                    break
                print("❌ Username tidak boleh kosong")

            while True:
                passwd = input("Password: ").strip()
                if passwd:
                    break
                print("❌ Password tidak boleh kosong")

            ftp.login(user=user, passwd=passwd)
            print(f"\n✅ Login berhasil ke {host} sebagai {user}")

        return ftp

    except Exception as e:
        print(f"❌ Gagal login: {e}")
        return None

def menu():
    print("""
=== MENU FTP ===
1. Lihat isi direktori
2. Pindah direktori
3. Buat file
4. Edit file
5. Hapus file
6. Upload file
7. Download file
8. Download direktori
0. Keluar
""")

def list_dir(ftp):
    try:
        print("\n📂 Isi direktori saat ini:")
        files = ftp.nlst()
        if not files:
            print(" (Kosong)")
        else:
            for f in files:
                print(" -", f)
    except Exception as e:
        print(f"❌ Gagal menampilkan isi: {e}")

def change_dir(ftp):
    new_dir = input("Masukkan nama direktori tujuan: ").strip()
    if not new_dir:
        print("❌ Nama direktori tidak boleh kosong")
        return
    try:
        ftp.cwd(new_dir)
        print(f"✅ Berhasil pindah ke: {ftp.pwd()}")
    except Exception as e:
        print(f"❌ Gagal pindah direktori: {e}")

def create_file(ftp):
    filename = input("Nama file baru: ").strip()
    if not filename:
        print("❌ Nama file tidak boleh kosong")
        return
    content = input("Isi file (biarkan kosong jika ingin kosong): ")
    try:
        with open(filename, 'w') as f:
            f.write(content)
        with open(filename, 'rb') as f:
            ftp.storbinary('STOR ' + filename, f)
        os.remove(filename)
        print(f"✅ File {filename} berhasil dibuat")
    except Exception as e:
        print(f"❌ Gagal membuat file: {e}")

def edit_file(ftp):
    filename = input("Nama file yang ingin diedit: ").strip()
    if not filename:
        print("❌ Nama file tidak boleh kosong")
        return
    try:
        # Unduh file
        with open(filename, 'wb') as f:
            ftp.retrbinary('RETR ' + filename, f.write)
        print("✅ File berhasil diunduh sementara untuk diedit")
        os.system(f"notepad {filename}" if os.name == 'nt' else f"nano {filename}")
        with open(filename, 'rb') as f:
            ftp.storbinary('STOR ' + filename, f)
        os.remove(filename)
        print("✅ File berhasil diedit dan diupload ulang")
    except Exception as e:
        print(f"❌ Gagal edit file: {e}")

def delete_file(ftp):
    filename = input("Nama file yang ingin dihapus: ").strip()
    if not filename:
        print("❌ Nama file tidak boleh kosong")
        return
    try:
        ftp.delete(filename)
        print(f"✅ File {filename} dihapus")
    except Exception as e:
        print(f"❌ Gagal hapus file: {e}")

def upload_file(ftp):
    filepath = input("Path file lokal: ").strip()
    if not filepath or not os.path.isfile(filepath):
        print("❌ File tidak ditemukan atau path kosong")
        return
    remote_name = input("Nama file di server (kosong = sama): ").strip() or os.path.basename(filepath)
    try:
        with open(filepath, 'rb') as f:
            ftp.storbinary('STOR ' + remote_name, f)
        print(f"✅ File {remote_name} berhasil diupload")
    except Exception as e:
        print(f"❌ Gagal upload: {e}")

def download_file(ftp):
    filename = input("Nama file di server: ").strip()
    if not filename:
        print("❌ Nama file tidak boleh kosong")
        return
    save_as = input("Simpan sebagai (lokal): ").strip()
    if not save_as:
        print("❌ Nama file lokal tidak boleh kosong")
        return
    try:
        with open(save_as, 'wb') as f:
            ftp.retrbinary('RETR ' + filename, f.write)
        print(f"✅ File {filename} berhasil diunduh sebagai {save_as}")
    except Exception as e:
        print(f"❌ Gagal download: {e}")

def download_directory(ftp):
    remote_dir = input("Nama direktori di server: ").strip()
    local_dir = input("Folder tujuan lokal: ").strip()

    if not remote_dir or not local_dir:
        print("❌ Nama direktori tidak boleh kosong")
        return

    def recursive_download(ftp_conn, remote_path, local_path):
        os.makedirs(local_path, exist_ok=True)
        try:
            ftp_conn.cwd(remote_path)
            items = ftp_conn.nlst()
        except Exception as e:
            print(f"❌ Gagal membuka direktori: {e}")
            return

        for item in items:
            try:
                ftp_conn.cwd(item)
                ftp_conn.cwd("..")
                recursive_download(ftp_conn, f"{remote_path}/{item}", os.path.join(local_path, item))
            except:
                try:
                    with open(os.path.join(local_path, item), 'wb') as f:
                        ftp_conn.retrbinary(f"RETR {item}", f.write)
                    print(f"⬇️ File '{item}' berhasil diunduh.")
                except Exception as e:
                    print(f"❌ Gagal unduh '{item}': {e}")

    recursive_download(ftp, remote_dir, local_dir)


def main():
    ftp = login_ftp()
    if not ftp:
        return

    while True:
        menu()
        choice = input("Pilih menu (0-8): ").strip()

        if choice == '1':
            list_dir(ftp)
        elif choice == '2':
            change_dir(ftp)
        elif choice == '3':
            create_file(ftp)
        elif choice == '4':
            edit_file(ftp)
        elif choice == '5':
            delete_file(ftp)
        elif choice == '6':
            upload_file(ftp)
        elif choice == '7':
            download_file(ftp)
        elif choice == '8':
            download_directory(ftp)
        elif choice == '0':
            print("📤 Keluar...")
            ftp.quit()
            break
        else:
            print("❌ Pilihan tidak valid, coba lagi.")  
main()