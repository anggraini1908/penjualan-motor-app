import streamlit as st
import pandas as pd
import hashlib
import os
import json
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib import colors
from io import BytesIO

# ===============================
# Konfigurasi Halaman
# ===============================
st.set_page_config(
    page_title="HONDA MOTOR - Sistem Pembelian Premium",
    page_icon="🏍️",
    layout="wide"
)

# ===============================
# Daftar Bank di Indonesia
# ===============================
BANKS = [
    "BCA", "Mandiri", "BNI", "BRI", "CIMB Niaga", "Danamon",
    "Permata", "Maybank", "Panin", "OCBC NISP", "Lainnya"
]

# ===============================
# Styling CSS
# ===============================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap');
    @import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css');

    body {
        font-family: 'Roboto', sans-serif;
    }
    .stApp {
        background: none;
    }
    h1, h2, h3 {
        color: #FF5722;
        font-weight: 700;
        text-shadow: 0 0 5px rgba(255, 87, 34, 0.5);
    }
    .stButton > button {
        background: linear-gradient(45deg, #D32F2F, #FF5722);
        color: #FFFFFF;
        border: none;
        border-radius: 25px;
        padding: 12px 24px;
        font-weight: 700;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(211, 47, 47, 0.3);
    }
    .stButton > button:hover {
        background: linear-gradient(45deg, #FF5722, #D32F2F);
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(211, 47, 47, 0.5);
    }
    .stTextInput > div > div > input, .stTextArea > div > div > textarea, .stSelectbox > div > div > select {
        background-color: #2C2C2C;
        color: #FFFFFF;
        border: 2px solid #D32F2F;
        border-radius: 10px;
        padding: 12px;
        font-size: 16px;
    }
    .stSidebar {
        background: linear-gradient(180deg, #2C2C2C, #1A1A1A);
        border-right: 2px solid #D32F2F;
        padding: 20px;
        border-radius: 0 20px 20px 0;
    }
    .stSidebar .stButton > button {
        width: 100%;
        margin-bottom: 15px;
        font-size: 16px;
    }
    .card {
        background: #2C2C2C;
        border: 2px solid #D32F2F;
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
        transition: transform 0.3s ease;
    }
    .card:hover {
        transform: translateY(-5px);
    }
    .stMetric {
        background: #2C2C2C;
        border: 2px solid #D32F2F;
        border-radius: 10px;
        padding: 15px;
        color: #FFFFFF;
    }
    .stAlert {
        background: #2C2C2C;
        border: 2px solid #D32F2F;
        border-radius: 10px;
        color: #FFFFFF;
    }
    .table-container {
        background: #2C2C2C;
        border: 2px solid #D32F2F;
        border-radius: 15px;
        padding: 20px;
    }
    .table-header {
        background: #D32F2F;
        color: #FFFFFF;
        font-weight: 700;
        padding: 10px;
        border-radius: 10px 10px 0 0;
    }
    .table-row:hover {
        background: #3A3A3A;
    }
    .motor-image {
        border-radius: 10px;
        border: 2px solid #D32F2F;
        margin-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# ===============================
# Fungsi Login dan Manajemen Pengguna
# ===============================
def hash_password(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def load_users():
    if os.path.exists("users.json"):
        with open("users.json", "r") as f:
            return json.load(f)
    else:
        default = {
            "admin": {
                "password": hash_password("admin123"),
                "name": "Admin Honda",
                "role": "admin",
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        }
        save_users(default)
        return default

def save_users(users):
    with open("users.json", "w") as f:
        json.dump(users, f, indent=4)

def authenticate(username, password):
    users = load_users()
    if username in users and users[username]["password"] == hash_password(password):
        st.session_state.logged_in = True
        st.session_state.username = username
        st.session_state.user_role = users[username]["role"]
        st.session_state.user_name = users[username]["name"]
        return True
    return False

# ===============================
# Kelas Motor
# ===============================
class Motor:
    def __init__(self):
        self.load_motors()

    def load_motors(self):
        if os.path.exists("motors.json"):
            with open("motors.json", "r") as f:
                self.motor_dict = json.load(f)
        else:
            self.motor_dict = {
                "Honda Vario 125": {
                    "price": 19000000,
                    "image_url": "https://ik.imagekit.io/zlt25mb52fx/ahmcdn/tr:w-550,f-auto,pr-true/uploads/product-draft/colors/v125-variant-web-matte-red-cbs-515x504px-1-01042024-031801-02042024-061006.png",
                    "year": 2024,
                    "type": "Skuter"
                },
                "Honda Beat": {
                    "price": 17500000,
                    "image_url": "https://ik.imagekit.io/zlt25mb52fx/ahmcdn/tr:w-550,f-auto,pr-true/uploads/product-draft/colors/matte-blue-2-03062024-045618.png",
                    "year": 2024,
                    "type": "Skuter"
                },
                "Honda CBR250RR": {
                    "price": 75000000,
                    "image_url": "https://ik.imagekit.io/zlt25mb52fx/ahmcdn/tr:w-550,f-auto,pr-true/uploads/product-draft/colors/variant-mystique-blue-515x504-ys-2-19092022-075428.jpg",
                    "year": 2023,
                    "type": "Sport"
                },
                "Honda PCX 160": {
                    "price": 32000000,
                    "image_url": "https://ik.imagekit.io/zlt25mb52fx/ahmcdn/tr:w-550,f-auto,pr-true/uploads/product-draft/colors/variant-web-roadsync-red-515x504px-r5-06122024-030945.png",
                    "year": 2024,
                    "type": "Skuter"
                },
                "Honda CRF150L": {
                    "price": 35000000,
                    "image_url": "https://ik.imagekit.io/zlt25mb52fx/ahmcdn/tr:w-550,f-auto,pr-true/uploads/product/colors/new-extreme-red-25102021-084922.jpg",
                    "year": 2023,
                    "type": "Trail"
                }
            }
            self.save_motors()

    def save_motors(self):
        with open("motors.json", "w") as f:
            json.dump(self.motor_dict, f, indent=4)

    def get_daftar(self):
        return list(self.motor_dict.keys())

    def get_harga(self, nama):
        return self.motor_dict.get(nama, {}).get("price", 0)

    def get_image_url(self, nama):
        return self.motor_dict.get(nama, {}).get("image_url", "")

    def get_year(self, nama):
        return self.motor_dict.get(nama, {}).get("year", "")

    def get_type(self, nama):
        return self.motor_dict.get(nama, {}).get("type", "")

    def add_motor(self, nama, price, image_url, year, tipe):
        self.motor_dict[nama] = {
            "price": price,
            "image_url": image_url,
            "year": year,
            "type": tipe
        }
        self.save_motors()

    def update_motor(self, nama, price, image_url, year, tipe):
        if nama in self.motor_dict:
            self.motor_dict[nama] = {
                "price": price,
                "image_url": image_url,
                "year": year,
                "type": tipe
            }
            self.save_motors()

    def delete_motor(self, nama):
        if nama in self.motor_dict:
            del self.motor_dict[nama]
            self.save_motors()

# ===============================
# Kelas Pembeli
# ===============================
class Pembeli:
    def __init__(self, ID, NIK, Nama, Alamat, Telepon, **kwargs):
        self.id_pembeli = ID
        self.nik = NIK
        self.nama = Nama
        self.alamat = Alamat
        self.telepon = Telepon
        self.email = kwargs.get("Email", "")
        self.jenis_kelamin = kwargs.get("Jenis Kelamin")
        self.merek_kendaraan = kwargs.get("Merek Kendaraan")
        self.nomor_rangka = kwargs.get("Nomor Rangka")
        self.harga = kwargs.get("Harga", 0)
        self.status_pembelian = kwargs.get("Status Pembelian", "Cash")
        self.metode_pembayaran = kwargs.get("Metode Pembayaran", "")
        self.status = kwargs.get("Status", "Belum Lunas")
        self.dibuat_oleh = kwargs.get("Dibuat Oleh", "")
        self.tanggal_dibuat = kwargs.get("Tanggal Dibuat", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        self.status_pesanan = kwargs.get("Status Pesanan", "Menunggu Konfirmasi") # NEW: Status Pesanan
        cicilan = kwargs.get("Cicilan", [])
        if isinstance(cicilan, str):
            try:
                cicilan = json.loads(cicilan)
            except json.JSONDecodeError:
                cicilan = []
        self.cicilan = cicilan if isinstance(cicilan, list) else []

    def to_dict(self):
        return {
            "ID": self.id_pembeli,
            "NIK": self.nik,
            "Nama": self.nama,
            "Alamat": self.alamat,
            "Telepon": self.telepon,
            "Email": self.email,
            "Jenis Kelamin": self.jenis_kelamin,
            "Merek Kendaraan": self.merek_kendaraan,
            "Nomor Rangka": self.nomor_rangka,
            "Harga": self.harga,
            "Status Pembelian": self.status_pembelian,
            "Metode Pembayaran": self.metode_pembayaran,
            "Status": self.status,
            "Dibuat Oleh": self.dibuat_oleh,
            "Tanggal Dibuat": self.tanggal_dibuat,
            "Status Pesanan": self.status_pesanan, # NEW: Status Pesanan
            "Cicilan": self.cicilan
        }

# ===============================
# Fungsi Cetak Kartu
# ===============================
def generate_card(pembeli):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    
    c.setFillColor(colors.red)
    c.rect(0, A4[1] - 4*cm, A4[0], 4*cm, fill=1)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(A4[0]/2, A4[1] - 2.5*cm, "KARTU PEMBELI HONDA MOTOR")
    
    c.setFillColor(colors.black)
    c.setFont("Helvetica", 12)
    c.drawCentredString(A4[0]/2, A4[1] - 3.5*cm, "[Logo Honda]")
    
    card_width = 16*cm
    card_height = 10*cm
    x_offset = (A4[0] - card_width) / 2
    y_offset = (A4[1] - card_height) / 2 - 2*cm
    
    c.setFillColor(colors.white)
    c.rect(x_offset, y_offset, card_width, card_height, fill=1)
    c.setStrokeColor(colors.black)
    c.rect(x_offset, y_offset, card_width, card_height)
    
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(x_offset + 1*cm, y_offset + card_height - 1.5*cm, "Informasi Pembeli")
    
    c.setFont("Helvetica", 10)
    data = [
        f"NIK: {pembeli.nik}",
        f"Nama: {pembeli.nama}",
        f"Email: {pembeli.email if pembeli.email else '-'}",
        f"Jenis Kelamin: {pembeli.jenis_kelamin}",
        f"Alamat: {pembeli.alamat}",
        f"No Telepon: {pembeli.telepon}",
        f"Merek Kendaraan: {pembeli.merek_kendaraan}",
        f"Nomor Rangka: {pembeli.nomor_rangka}",
        f"Harga: Rp {pembeli.harga:,}",
        f"Status Pembelian: {pembeli.status_pembelian}",
        f"Metode Pembayaran: {pembeli.metode_pembayaran}",
        f"Status Pembayaran: {pembeli.status}",
        f"Status Pesanan: {pembeli.status_pesanan}", # NEW: Status Pesanan
        f"Tanggal Pembelian: {pembeli.tanggal_dibuat}"
    ]
    
    for i, line in enumerate(data):
        c.drawString(x_offset + 1*cm, y_offset + card_height - (2.5*cm + i*0.6*cm), line)
    
    c.setFont("Helvetica-Oblique", 8)
    c.drawCentredString(A4[0]/2, y_offset - 1*cm, "Diterbitkan oleh Honda Motor - Sistem Pembelian")
    
    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

# ===============================
# Fungsi Cetak Struk Cicilan
# ===============================
def generate_struk(pembeli, cicilan_data):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    
    users = load_users()
    user_info = users.get(cicilan_data['Dibuat Oleh'], {})
    user_display = f"{user_info.get('name', cicilan_data['Dibuat Oleh'])} ({user_info.get('role', '').capitalize()})"
    
    total_paid = sum(c['Jumlah'] for c in pembeli.cicilan) if pembeli.cicilan else 0
    remaining = pembeli.harga - total_paid
    
    c.setFillColor(colors.red)
    c.rect(0, A4[1] - 4*cm, A4[0], 4*cm, fill=1)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(A4[0]/2, A4[1] - 2.5*cm, "STRUK PEMBAYARAN CICILAN")
    
    c.setFillColor(colors.black)
    c.setFont("Helvetica", 12)
    c.drawCentredString(A4[0]/2, A4[1] - 3.5*cm, "[Logo Honda]")
    
    struk_width = 12*cm
    struk_height = 16*cm
    x_offset = (A4[0] - struk_width) / 2
    y_offset = (A4[1] - struk_height) / 2 - 2*cm
    
    c.setFillColor(colors.white)
    c.rect(x_offset, y_offset, struk_width, struk_height, fill=1)
    c.setStrokeColor(colors.black)
    c.rect(x_offset, y_offset, struk_width, struk_height)
    
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(x_offset + 1*cm, y_offset + struk_height - 1.5*cm, "Informasi Pembeli")
    
    c.setFont("Helvetica", 10)
    pembeli_data = [
        f"Nama: {pembeli.nama}",
        f"NIK: {pembeli.nik}",
        f"Email: {pembeli.email if pembeli.email else '-'}",
        f"Merek Kendaraan: {pembeli.merek_kendaraan}",
        f"Nomor Rangka: {pembeli.nomor_rangka}",
        f"Metode Pembayaran: {pembeli.metode_pembayaran}"
    ]
    
    for i, line in enumerate(pembeli_data):
        c.drawString(x_offset + 1*cm, y_offset + struk_height - (2.5*cm + i*0.6*cm), line)
    
    c.setFont("Helvetica-Bold", 12)
    c.drawString(x_offset + 1*cm, y_offset + struk_height - 5.5*cm, "Detail Cicilan")
    
    c.setFont("Helvetica", 10)
    cicilan_info = [
        f"Bulan: {cicilan_data['Bulan']}",
        f"Jumlah: Rp {cicilan_data['Jumlah']:,}",
        f"Tanggal: {cicilan_data['Tanggal']}",
        f"Dibuat Oleh: {user_display}",
        f"Total Dibayar: Rp {total_paid:,}",
        f"Sisa Pembayaran: Rp {remaining:,}"
    ]
    
    for i, line in enumerate(cicilan_info):
        c.drawString(x_offset + 1*cm, y_offset + struk_height - (6.5*cm + i*0.6*cm), line)
    
    c.setFont("Helvetica-Oblique", 8)
    c.drawCentredString(A4[0]/2, y_offset - 1*cm, "Diterbitkan oleh Honda Motor - Sistem Pembelian")
    
    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

# ===============================
# Fungsi Cetak Laporan Pembelian
# ===============================
def generate_sales_report(data, period, period_value):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    
    c.setFillColor(colors.red)
    c.rect(0, A4[1] - 4*cm, A4[0], 4*cm, fill=1)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(A4[0]/2, A4[1] - 2.5*cm, f"LAPORAN PEMBELIAN {period.upper()}")
    
    c.setFillColor(colors.black)
    c.setFont("Helvetica", 12)
    c.drawCentredString(A4[0]/2, A4[1] - 3.5*cm, "[Logo Honda]")
    
    report_width = 18*cm
    report_height = 22*cm
    x_offset = (A4[0] - report_width) / 2
    y_offset = (A4[1] - report_height) / 2 - 2*cm
    
    c.setFillColor(colors.white)
    c.rect(x_offset, y_offset, report_width, report_height, fill=1)
    c.setStrokeColor(colors.black)
    c.rect(x_offset, y_offset, report_width, report_height)
    
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(x_offset + 1*cm, y_offset + report_height - 1.5*cm, f"Periode: {period_value}")
    
    c.setFont("Helvetica", 10)
    headers = ["No", "Tanggal", "Nama", "Merek", "Harga", "Status", "Status Pesanan", "Input Oleh"] # NEW: Status Pesanan
    col_widths = [1*cm, 3*cm, 3*cm, 2*cm, 2*cm, 1.5*cm, 2.5*cm, 2*cm] # Adjusted widths
    
    y = y_offset + report_height - 2.5*cm
    c.setFillColor(colors.lightgrey)
    c.rect(x_offset + 1*cm, y, sum(col_widths), 0.7*cm, fill=1)
    
    c.setFillColor(colors.black)
    for i, header in enumerate(headers):
        c.drawString(x_offset + 1*cm + sum(col_widths[:i]), y + 0.2*cm, header)
    
    y -= 0.7*cm
    total = 0
    for idx, pembeli in enumerate(data, 1):
        if y < y_offset + 2*cm:
            c.showPage()
            y = y_offset + report_height - 2.5*cm
            c.setFillColor(colors.lightgrey)
            c.rect(x_offset + 1*cm, y, sum(col_widths), 0.7*cm, fill=1)
            c.setFillColor(colors.black)
            for i, header in enumerate(headers):
                c.drawString(x_offset + 1*cm + sum(col_widths[:i]), y + 0.2*cm, header)
            y -= 0.7*cm
        
        row = [
            str(idx),
            pembeli.tanggal_dibuat.split()[0],
            pembeli.nama,
            pembeli.merek_kendaraan,
            f"Rp {pembeli.harga:,}",
            pembeli.status,
            pembeli.status_pesanan, # NEW: Status Pesanan
            pembeli.dibuat_oleh
        ]
        for i, item in enumerate(row):
            c.drawString(x_offset + 1*cm + sum(col_widths[:i]), y + 0.2*cm, item)
        total += pembeli.harga
        y -= 0.6*cm
    
    c.setFont("Helvetica-Bold", 10)
    c.drawString(x_offset + 1*cm, y - 0.5*cm, f"Total Pembelian: Rp {total:,}")
    
    c.setFont("Helvetica-Oblique", 8)
    c.drawCentredString(A4[0]/2, y_offset - 1*cm, "Diterbitkan oleh Honda Motor - Sistem Pembelian")
    
    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

# ===============================
# Inisialisasi Data
# ===============================
CSV_FILE = "data_pembelian.csv"
motor = Motor()

def init_session_state():
    defaults = {
        "logged_in": False,
        "username": None,
        "user_role": None,
        "user_name": None,
        "data_pembeli": [],
        "search_query": "",
        "current_page": "Home"
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
    if not st.session_state.data_pembeli:
        if os.path.exists(CSV_FILE):
            df = pd.read_csv(CSV_FILE)
            # Ensure 'Status Pesanan' column exists, default to 'Menunggu Konfirmasi' if not
            if 'Status Pesanan' not in df.columns:
                df['Status Pesanan'] = "Menunggu Konfirmasi"
            
            def parse_cicilan(x):
                if isinstance(x, str) and x:
                    try:
                        return json.loads(x)
                    except json.JSONDecodeError as e:
                        print(f"Error parsing Cicilan: {x}, Error: {e}")
                        return []
                return []
            df['Cicilan'] = df['Cicilan'].apply(parse_cicilan)
            st.session_state.data_pembeli = [Pembeli(**row) for _, row in df.iterrows()]

def simpan_data():
    try:
        data = [p.to_dict() for p in st.session_state.data_pembeli]
        for item in data:
            if not isinstance(item['Cicilan'], list):
                print(f"Invalid Cicilan data for ID {item['ID']}: {item['Cicilan']}")
                item['Cicilan'] = []
        df = pd.DataFrame(data)
        df.to_csv(CSV_FILE, index=False)
    except PermissionError:
        st.error("❌ Gagal menyimpan file CSV. Pastikan file tidak sedang dibuka.")

# ===============================
# Halaman Home
# ===============================
def show_home():
    st.markdown("<h1><i class='fas fa-motorcycle'></i> HONDA MOTOR</h1>", unsafe_allow_html=True)
    st.markdown("<h3>Daftar Harga Motor Honda</h3>", unsafe_allow_html=True)
    
    with st.container():
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<h3><i class='fas fa-search'></i> Cari Motor</h3>", unsafe_allow_html=True)
        st.session_state.search_query = st.text_input("Cari Nama Motor", value=st.session_state.search_query, placeholder="Masukkan nama motor...")
        filtered_motors = {k: v for k, v in motor.motor_dict.items() if st.session_state.search_query.lower() in k.lower()}
        
        if st.session_state.user_role == "admin":
            st.markdown("<h4><i class='fas fa-plus-circle'></i> Kelola Motor</h4>", unsafe_allow_html=True)
            with st.form("form_add_motor"):
                col1, col2 = st.columns(2)
                with col1:
                    nama_motor = st.text_input("Nama Motor", placeholder="Masukkan nama motor")
                    price = st.number_input("Harga (Rp)", min_value=0)
                with col2:
                    image_url = st.text_input("URL Gambar", placeholder="Masukkan URL gambar")
                    year = st.number_input("Tahun", min_value=2000, max_value=2025, step=1)
                    tipe = st.selectbox("Tipe", ["Skuter", "Sport", "Trail", "Cub"])
                if st.form_submit_button("➕ Tambah Motor"):
                    if nama_motor and image_url:
                        if nama_motor not in motor.motor_dict:
                            motor.add_motor(nama_motor, price, image_url, year, tipe)
                            st.success("✅ Motor berhasil ditambahkan!")
                        else:
                            st.error("❌ Nama motor sudah ada!")
                    else:
                        st.error("❗ Lengkapi semua field!")
            
            st.markdown("<h4><i class='fas fa-edit'></i> Edit/Hapus Motor</h4>", unsafe_allow_html=True)
            motor_to_edit = st.selectbox("Pilih Motor", motor.get_daftar())
            if motor_to_edit:
                with st.form("form_edit_motor"):
                    col1, col2 = st.columns(2)
                    with col1:
                        new_nama = st.text_input("Nama Motor", value=motor_to_edit)
                        new_price = st.number_input("Harga (Rp)", value=motor.get_harga(motor_to_edit), min_value=0)
                    with col2:
                        new_image_url = st.text_input("URL Gambar", value=motor.get_image_url(motor_to_edit))
                        new_year = st.number_input("Tahun", value=motor.get_year(motor_to_edit), min_value=2000, max_value=2025, step=1)
                        new_tipe = st.selectbox("Tipe", ["Skuter", "Sport", "Trail", "Cub"], index=["Skuter", "Sport", "Trail", "Cub"].index(motor.get_type(motor_to_edit)))
                    col_submit, col_delete = st.columns(2)
                    with col_submit:
                        if st.form_submit_button("💾 Update Motor"):
                            if new_nama and new_image_url:
                                motor.update_motor(new_nama, new_price, new_image_url, new_year, new_tipe)
                                st.success("✅ Motor berhasil diperbarui!")
                            else:
                                st.error("❗ Lengkapi semua field!")
                    with col_delete:
                        if st.form_submit_button("🗑️ Hapus Motor"):
                            motor.delete_motor(motor_to_edit)
                            st.success("✅ Motor berhasil dihapus!")
                            st.rerun()
        
        st.markdown("<h4>Daftar Motor</h4>", unsafe_allow_html=True)
        cols = st.columns(2)
        for idx, (nama, info) in enumerate(filtered_motors.items()):
            with cols[idx % 2]:
                st.image(info["image_url"], caption=nama, use_container_width=True, output_format="auto", clamp=True, channels="RGB")
                st.markdown(f"<h4>{nama}</h4><p><i class='fas fa-money-bill-wave'></i> Rp {info['price']:,}</p>", unsafe_allow_html=True)
                if st.session_state.user_role != "admin":
                    st.markdown(f"<p><i class='fas fa-calendar'></i> Tahun: {info['year']}</p><p><i class='fas fa-tag'></i> Tipe: {info['type']}</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

# ===============================
# Halaman Pembelian
# ===============================
def show_pembelian():
    st.markdown("<h1><i class='fas fa-clipboard-list'></i> Formulir Pembelian Motor</h1>", unsafe_allow_html=True)
    
    with st.container():
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<h3><i class='fas fa-plus-circle'></i> Ajukan Permintaan Pembelian</h3>", unsafe_allow_html=True)
        with st.form("form_pembelian"):
            col1, col2 = st.columns(2)
            with col1:
                nik = st.text_input("No. NIK", placeholder="Masukkan 16 digit NIK")
                nama = st.text_input("Nama Lengkap", placeholder="Masukkan nama lengkap")
                alamat = st.text_area("Alamat", placeholder="Masukkan alamat lengkap")
                telepon = st.text_input("No. Telepon", placeholder="Masukkan nomor telepon")
                email = st.text_input("Email (opsional)", placeholder="Masukkan email")
            with col2:
                jenis_kelamin = st.radio("Jenis Kelamin", ["Laki-laki", "Perempuan"])
                merek_kendaraan = st.selectbox("Merek Kendaraan", motor.get_daftar())
                
                # Nomor Rangka Mesin dan Status Pembayaran awal tidak diisi oleh user
                nomor_rangka_input = "" 
                status_pembayaran_awal = "Belum Lunas" # Default untuk permintaan baru
                
                metode_pembayaran = st.selectbox("Metode Pembayaran", BANKS)
                harga = motor.get_harga(merek_kendaraan)
                st.markdown(f"<p style='color: #FFD700;'><i class='fas fa-money-bill-wave'></i> Harga Motor: <strong>Rp {harga:,}</strong></p>", unsafe_allow_html=True)
                status_pembelian_type = st.selectbox("Jenis Pembelian", ["Cash", "Kredit"])
                
                # Status pesanan awal selalu 'Menunggu Konfirmasi' untuk user
                initial_status_pesanan = "Menunggu Konfirmasi"
            
            if st.form_submit_button("💾 Ajukan Permintaan"):
                if nik and nama and alamat and telepon:
                    if len(nik) != 16:
                        st.error("❌ No. NIK harus 16 digit.")
                    else:
                        id_pembeli = datetime.now().strftime("%Y%m%d%H%M%S")
                        pembeli = Pembeli(
                            id_pembeli,
                            nik,
                            nama,
                            alamat,
                            telepon,
                            **{
                                "Email": email,
                                "Jenis Kelamin": jenis_kelamin,
                                "Merek Kendaraan": merek_kendaraan,
                                "Nomor Rangka": nomor_rangka_input, # Kosong dari user
                                "Harga": harga,
                                "Status Pembelian": status_pembelian_type,
                                "Metode Pembayaran": metode_pembayaran,
                                "Status": status_pembayaran_awal, # Belum Lunas dari user
                                "Dibuat Oleh": st.session_state.username,
                                "Status Pesanan": initial_status_pesanan # Status baru
                            }
                        )
                        st.session_state.data_pembeli.append(pembeli)
                        simpan_data()
                        st.success("✅ Permintaan pembelian Anda berhasil diajukan! Silakan tunggu konfirmasi dari admin.")
                else:
                    st.error("❗ Lengkapi semua field wajib!")
        st.markdown("</div>", unsafe_allow_html=True)
        
# ===============================
# Halaman Riwayat Pembelian
# ===============================
def show_riwayat_pembelian():
    st.markdown("<h1><i class='fas fa-history'></i> Riwayat Pembelian</h1>", unsafe_allow_html=True)
    
    user_pembelian = [p for p in st.session_state.data_pembeli if p.dibuat_oleh == st.session_state.username]
    
    if user_pembelian:
        with st.container():
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("<h3><i class='fas fa-list'></i> Daftar Pembelian Anda</h3>", unsafe_allow_html=True)
            df = pd.DataFrame([{
                "ID": p.id_pembeli,
                "NIK": p.nik,
                "Nama": p.nama,
                "Email": p.email,
                "Merek Kendaraan": p.merek_kendaraan,
                "Nomor Rangka": p.nomor_rangka if p.nomor_rangka else "-", # Display '-' if empty
                "Harga": f"Rp {p.harga:,}",
                "Status Pembelian": p.status_pembelian,
                "Metode Pembayaran": p.metode_pembayaran,
                "Status Pembayaran": p.status,
                "Status Pesanan": p.status_pesanan, # NEW: Status Pesanan
                "Tanggal": p.tanggal_dibuat
            } for p in user_pembelian])
            
            st.table(df.style.set_properties(**{
                'background-color': '#2C2C2C',
                'color': '#FFD700',
                'border': '1px solid #FFD700',
                'padding': '10px'
            }).set_table_styles([
                {'selector': 'th', 'props': [('background-color', '#FFD700'), ('color', '#1a1a1a'), ('font-weight', 'bold'), ('text-align', 'center')]},
                {'selector': 'td', 'props': [('border-right', '1px solid #FFD700')]}
            ]).hide(axis="index"))

            st.markdown("<h4>Informasi Status Pesanan:</h4>", unsafe_allow_html=True)
            for p in user_pembelian:
                if p.status_pesanan == "Menunggu Konfirmasi":
                    st.info(f"Permintaan pembelian motor **{p.merek_kendaraan}** Anda (ID: **{p.id_pembeli}**) sedang ditinjau oleh admin.")
                elif p.status_pesanan == "Dikonfirmasi":
                    st.success(f"Permintaan pembelian motor **{p.merek_kendaraan}** Anda (ID: **{p.id_pembeli}**) telah **dikonfirmasi**! Nomor Rangka: **{p.nomor_rangka if p.nomor_rangka else 'Belum Tersedia'}**. Silakan lanjutkan pembayaran.")
                elif p.status_pesanan == "Ditolak":
                    st.error(f"Maaf, permintaan pembelian motor **{p.merek_kendaraan}** Anda (ID: **{p.id_pembeli}**) **ditolak**. Silakan hubungi admin untuk informasi lebih lanjut.")
                elif p.status_pesanan == "Diproses":
                    st.warning(f"Pesanan motor **{p.merek_kendaraan}** Anda (ID: **{p.id_pembeli}**) sedang **diproses**.")
                elif p.status_pesanan == "Selesai":
                    st.success(f"Pesanan motor **{p.merek_kendaraan}** Anda (ID: **{p.id_pembeli}**) telah **selesai**. Terima kasih!")

        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("Belum ada riwayat pembelian.")

# ===============================
# Halaman Data Pembelian
# ===============================
def show_data():
    if st.session_state.user_role not in ["admin", "staff"]:
        st.warning("⚠️ Akses ditolak.")
        return
    
    st.markdown("<h1><i class='fas fa-table'></i> Data Pembelian</h1>", unsafe_allow_html=True)
    
    if st.session_state.data_pembeli:
        with st.container():
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("<h3><i class='fas fa-list'></i> Daftar Pembelian</h3>", unsafe_allow_html=True)
            col_filter, col_search = st.columns(2)
            with col_filter:
                filter_status_pembayaran = st.selectbox("Filter Status Pembayaran", ["Semua", "Belum Lunas", "Lunas"])
                filter_status_pesanan = st.selectbox("Filter Status Pesanan", ["Semua", "Menunggu Konfirmasi", "Dikonfirmasi", "Ditolak", "Diproses", "Selesai"]) # NEW: Filter Status Pesanan
            with col_search:
                st.session_state.search_query = st.text_input("Cari Nama", value=st.session_state.search_query, placeholder="Masukkan nama pembeli...")
            
            filtered_data = st.session_state.data_pembeli
            if filter_status_pembayaran != "Semua":
                filtered_data = [p for p in filtered_data if p.status == filter_status_pembayaran]
            if filter_status_pesanan != "Semua": # NEW: Filter Status Pesanan
                filtered_data = [p for p in filtered_data if p.status_pesanan == filter_status_pesanan]
            if st.session_state.search_query:
                filtered_data = [p for p in filtered_data if st.session_state.search_query.lower() in p.nama.lower()]
            
            if filtered_data:
                df = pd.DataFrame([{
                    "ID": p.id_pembeli,
                    "NIK": p.nik,
                    "Nama": p.nama,
                    "Email": p.email,
                    "Jenis Kelamin": p.jenis_kelamin,
                    "Alamat": p.alamat,
                    "Telepon": p.telepon,
                    "Merek Kendaraan": p.merek_kendaraan,
                    "Nomor Rangka": p.nomor_rangka if p.nomor_rangka else "-", # Display '-' if empty
                    "Harga": f"Rp {p.harga:,}",
                    "Status Pembelian": p.status_pembelian,
                    "Metode Pembayaran": p.metode_pembayaran,
                    "Status Pembayaran": p.status,
                    "Status Pesanan": p.status_pesanan, # NEW: Status Pesanan
                    "Input Oleh": p.dibuat_oleh,
                    "Tanggal": p.tanggal_dibuat
                } for p in filtered_data])
                
                st.table(df.style.set_properties(**{
                    'background-color': '#2C2C2C',
                    'color': '#FFD700',
                    'border': '1px solid #FFD700',
                    'padding': '10px'
                }).set_table_styles([
                    {'selector': 'th', 'props': [('background-color', '#FFD700'), ('color', '#1a1a1a'), ('font-weight', 'bold'), ('text-align', 'center')]},
                    {'selector': 'td', 'props': [('border-right', '1px solid #FFD700')]}
                ]).hide(axis="index"))
                
                st.markdown("<h4>Cetak Laporan Pembelian</h4>", unsafe_allow_html=True)
                col1, col2 = st.columns(2)
                with col1:
                    month = st.selectbox("Pilih Bulan", range(1, 13), format_func=lambda x: datetime(2025, x, 1).strftime("%B"))
                    year_month = st.selectbox("Tahun (Bulan)", range(2020, 2026))
                    if st.button("🖨️ Cetak Laporan Bulanan"):
                        monthly_data = [p for p in filtered_data if datetime.strptime(p.tanggal_dibuat, "%Y-%m-%d %H:%M:%S").month == month and datetime.strptime(p.tanggal_dibuat, "%Y-%m-%d %H:%M:%S").year == year_month]
                        if monthly_data:
                            period_value = f"{datetime(2025, month, 1).strftime('%B')} {year_month}"
                            report_buffer = generate_sales_report(monthly_data, "Bulanan", period_value)
                            st.download_button(
                                label="Download Laporan Bulanan",
                                data=report_buffer,
                                file_name=f"Laporan_Pembelian_Bulan_{month}_{year_month}.pdf",
                                mime="application/pdf"
                            )
                        else:
                            st.warning("Tidak ada data untuk periode ini.")
                with col2:
                    year = st.selectbox("Pilih Tahun", range(2020, 2026))
                    if st.button("🖨️ Cetak Laporan Tahunan"):
                        yearly_data = [p for p in filtered_data if datetime.strptime(p.tanggal_dibuat, "%Y-%m-%d %H:%M:%S").year == year]
                        if yearly_data:
                            report_buffer = generate_sales_report(yearly_data, "Tahunan", str(year))
                            st.download_button(
                                label="Download Laporan Tahunan",
                                data=report_buffer,
                                file_name=f"Laporan_Pembelian_Tahun_{year}.pdf",
                                mime="application/pdf"
                            )
                        else:
                            st.warning("Tidak ada data untuk tahun ini.")
            else:
                st.info("Tidak ada data yang sesuai dengan filter atau pencarian.")
            st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("Belum ada data pembelian yang tercatat.")

# ===============================
# Halaman Kelola Data
# ===============================
def show_kelola_data():
    if st.session_state.user_role not in ["admin", "staff"]:
        st.warning("⚠️ Akses ditolak.")
        return
    
    st.markdown("<h1><i class='fas fa-edit'></i> Kelola Data Pembelian</h1>", unsafe_allow_html=True)
    
    if st.session_state.data_pembeli:
        with st.container():
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("<h3><i class='fas fa-search'></i> Cari Data</h3>", unsafe_allow_html=True)
            search_rangka = st.text_input("Cari Nomor Rangka", placeholder="Masukkan nomor rangka...")
            filtered_pembeli = [p for p in st.session_state.data_pembeli if search_rangka.lower() in p.nomor_rangka.lower()] if search_rangka else st.session_state.data_pembeli
            
            if filtered_pembeli:
                pembeli_options = {p.id_pembeli: p.nama for p in filtered_pembeli}
                id_to_edit = st.selectbox("Pilih Pembelian", list(pembeli_options.keys()), format_func=lambda x: f"ID: {x} - {pembeli_options[x]}")
                selected_pembeli = next((p for p in st.session_state.data_pembeli if p.id_pembeli == id_to_edit), None)
                
                if selected_pembeli:
                    buffer = generate_card(selected_pembeli)
                    st.download_button(
                        label="🖨️ Cetak Kartu",
                        data=buffer,
                        file_name=f"Kartu_Pembeli_{selected_pembeli.nama}.pdf",
                        mime="application/pdf"
                    )
                    
                    st.markdown(f"<h4>Edit Data: {selected_pembeli.nama}</h4>", unsafe_allow_html=True)
                    with st.form("form_edit"):
                        col1, col2 = st.columns(2)
                        with col1:
                            nik = st.text_input("No. NIK", value=selected_pembeli.nik, placeholder="Masukkan 16 digit NIK")
                            nama = st.text_input("Nama Lengkap", value=selected_pembeli.nama, placeholder="Masukkan nama lengkap")
                            alamat = st.text_area("Alamat", value=selected_pembeli.alamat, placeholder="Masukkan alamat lengkap")
                            telepon = st.text_input("No. Telepon", value=selected_pembeli.telepon, placeholder="Masukkan nomor telepon")
                            email = st.text_input("Email (opsional)", value=selected_pembeli.email, placeholder="Masukkan email")
                        with col2:
                            jenis_kelamin = st.radio("Jenis Kelamin", ["Laki-laki", "Perempuan"], index=0 if selected_pembeli.jenis_kelamin == "Laki-laki" else 1)
                            merek_kendaraan = st.selectbox("Merek Kendaraan", motor.get_daftar(), index=motor.get_daftar().index(selected_pembeli.merek_kendaraan))
                            
                            # Nomor Rangka Mesin hanya diisi oleh admin/staff
                            nomor_rangka = st.text_input("Nomor Rangka Mesin", value=selected_pembeli.nomor_rangka, placeholder="Masukkan nomor rangka")
                            
                            metode_pembayaran = st.selectbox("Metode Pembayaran", BANKS, index=BANKS.index(selected_pembeli.metode_pembayaran) if selected_pembeli.metode_pembayaran in BANKS else 0)
                            status_pembelian = st.selectbox("Status Pembelian", ["Cash", "Kredit"], index=0 if selected_pembeli.status_pembelian == "Cash" else 1)
                            status_pembayaran = st.selectbox("Status Pembayaran", ["Belum Lunas", "Lunas"], index=0 if selected_pembeli.status == "Belum Lunas" else 1)
                            
                            # NEW: Status Pesanan
                            status_pesanan_options = ["Menunggu Konfirmasi", "Dikonfirmasi", "Ditolak", "Diproses", "Selesai"]
                            current_status_pesanan_idx = status_pesanan_options.index(selected_pembeli.status_pesanan)
                            new_status_pesanan = st.selectbox("Status Pesanan", status_pesanan_options, index=current_status_pesanan_idx)
                        
                        col_submit, col_delete = st.columns(2)
                        with col_submit:
                            if st.form_submit_button("💾 Update"):
                                if nik and nama and alamat and telepon:
                                    if len(nik) != 16:
                                        st.error("❌ No. NIK harus 16 digit.")
                                    elif new_status_pesanan == "Dikonfirmasi" and not nomor_rangka:
                                        st.error("❌ Nomor Rangka Mesin wajib diisi saat mengkonfirmasi pesanan.")
                                    else:
                                        selected_pembeli.nik = nik
                                        selected_pembeli.nama = nama
                                        selected_pembeli.alamat = alamat
                                        selected_pembeli.telepon = telepon
                                        selected_pembeli.email = email
                                        selected_pembeli.jenis_kelamin = jenis_kelamin
                                        selected_pembeli.merek_kendaraan = merek_kendaraan
                                        selected_pembeli.nomor_rangka = nomor_rangka
                                        selected_pembeli.harga = motor.get_harga(merek_kendaraan)
                                        selected_pembeli.metode_pembayaran = metode_pembayaran
                                        selected_pembeli.status_pembelian = status_pembelian
                                        selected_pembeli.status = status_pembayaran
                                        selected_pembeli.status_pesanan = new_status_pesanan # NEW: Update Status Pesanan
                                        simpan_data()
                                        st.success("✅ Data berhasil diperbarui!")
                                else:
                                    st.error("❗ Lengkapi semua field wajib!")
                        with col_delete:
                            if st.form_submit_button("🗑️ Hapus"):
                                st.session_state.data_pembeli = [p for p in st.session_state.data_pembeli if p.id_pembeli != id_to_edit]
                                simpan_data()
                                st.success("✅ Data berhasil dihapus!")
                                st.rerun()
            else:
                st.warning("Tidak ada data ditemukan dengan nomor rangka tersebut.")
            st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("Belum ada data pembelian yang tercatat.")

# ===============================
# Halaman Absensi Cicilan
# ===============================
def show_cicilan():
    if st.session_state.user_role not in ["admin", "staff"]:
        st.warning("⚠️ Akses ditolak.")
        return
    
    st.markdown("<h1><i class='fas fa-calendar-check'></i> Absensi Cicilan</h1>", unsafe_allow_html=True)
    
    if st.session_state.data_pembeli:
        kredit_pembeli = [p for p in st.session_state.data_pembeli if p.status_pembelian == "Kredit"]
        if kredit_pembeli:
            with st.container():
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                st.markdown("<h3><i class='fas fa-search'></i> Cari Pembeli Kredit</h3>", unsafe_allow_html=True)
                search_rangka = st.text_input("Cari Nomor Rangka", placeholder="Masukkan nomor rangka...")
                filtered_pembeli = [p for p in kredit_pembeli if search_rangka.lower() in p.nomor_rangka.lower()] if search_rangka else kredit_pembeli
                
                if filtered_pembeli:
                    pembeli_options = {p.id_pembeli: p.nama for p in filtered_pembeli}
                    id_pembeli = st.selectbox("Pilih Pembeli Kredit", list(pembeli_options.keys()), format_func=lambda x: f"ID: {x} - {pembeli_options[x]}")
                    selected_pembeli = next((p for p in st.session_state.data_pembeli if p.id_pembeli == id_pembeli), None)
                    
                    if selected_pembeli:
                        st.markdown(f"<h4>Data Pembeli: {selected_pembeli.nama}</h4>", unsafe_allow_html=True)
                        with st.form("form_cicilan"):
                            bulan = st.selectbox("Bulan Cicilan", [f"Bulan {i+1}" for i in range(12)])
                            jumlah_bayar = st.number_input("Jumlah Pembayaran (Rp)", min_value=0)
                            tanggal_bayar = st.date_input("Tanggal Pembayaran")
                            if st.form_submit_button("💾 Tambah Cicilan"):
                                cicilan_data = {
                                    "Bulan": bulan,
                                    "Jumlah": jumlah_bayar,
                                    "Tanggal": str(tanggal_bayar),
                                    "Dibuat Oleh": st.session_state.username
                                }
                                selected_pembeli.cicilan.append(cicilan_data)
                                simpan_data()
                                st.session_state.last_cicilan = cicilan_data
                                st.session_state.last_pembeli = selected_pembeli
                                st.success("✅ Data cicilan berhasil ditambahkan!")
                        
                        if 'last_cicilan' in st.session_state and 'last_pembeli' in st.session_state and st.session_state.last_pembeli.id_pembeli == selected_pembeli.id_pembeli:
                            struk_buffer = generate_struk(st.session_state.last_pembeli, st.session_state.last_cicilan)
                            st.download_button(
                                label="🖨️ Cetak Struk",
                                data=struk_buffer,
                                file_name=f"Struk_Cicilan_{selected_pembeli.nama}_{st.session_state.last_cicilan['Bulan']}.pdf",
                                mime="application/pdf"
                            )
                        
                        if selected_pembeli.cicilan and isinstance(selected_pembeli.cicilan, list) and all(isinstance(c, dict) for c in selected_pembeli.cicilan):
                            st.markdown("<h4>Riwayat Cicilan</h4>", unsafe_allow_html=True)
                            try:
                                df_cicilan = pd.DataFrame(selected_pembeli.cicilan)
                                st.table(df_cicilan.style.set_properties(**{
                                    'background-color': '#2C2C2C',
                                    'color': '#FFD700',
                                    'border': '1px solid #FFD700',
                                    'text-align': 'center',
                                    'padding': '10px'
                                }).set_table_styles([
                                    {'selector': 'th', 'props': [('background-color', '#FFD700'), ('color', '#1a1a1a'), ('font-weight', 'bold'), ('text-align', 'center')]},
                                    {'selector': 'td', 'props': [('border-right', '1px solid #FFD700')]}
                                ]).hide(axis="index"))
                                
                                total_cicilan = sum(cicilan['Jumlah'] for cicilan in selected_pembeli.cicilan)
                                sisa_pembayaran = selected_pembeli.harga - total_cicilan
                                
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    st.metric("Total Cicilan Dibayar", f"Rp {total_cicilan:,}")
                                with col2:
                                    st.metric("Sisa Pembayaran", f"Rp {sisa_pembayaran:,}")
                                with col3:
                                    if sisa_pembayaran > 0:
                                        st.metric("Status", "Belum Lunas")
                                    else:
                                        st.metric("Status", "Lunas")
                                        if selected_pembeli.status != "Lunas":
                                            selected_pembeli.status = "Lunas"
                                            simpan_data()
                            except ValueError:
                                st.warning("Data cicilan tidak valid. Tidak dapat ditampilkan.")
                        else:
                            st.info("Belum ada data cicilan untuk pembeli ini.")
                else:
                    st.warning("Tidak ada pembeli kredit dengan nomor rangka tersebut.")
                st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("Belum ada pembeli dengan status kredit.")
    else:
        st.info("Belum ada data pembelian yang tercatat.")

# ===============================
# Halaman Manajemen Pengguna
# ===============================
def show_manajemen_pengguna():
    st.markdown("<h1><i class='fas fa-users'></i> Manajemen Pengguna</h1>", unsafe_allow_html=True)
    if st.session_state.user_role != "admin":
        st.warning("⚠️ Akses ditolak. Hanya admin yang dapat mengelola pengguna.")
        return
    
    users = load_users()
    
    with st.container():
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<h3><i class='fas fa-user-plus'></i> Tambah Pengguna</h3>", unsafe_allow_html=True)
        with st.form("form_tambah_pengguna"):
            col1, col2 = st.columns(2)
            with col1:
                username = st.text_input("Username", placeholder="Masukkan username")
                password = st.text_input("Password", type="password", placeholder="Masukkan password")
            with col2:
                name = st.text_input("Nama Lengkap", placeholder="Masukkan nama lengkap")
                role = st.selectbox("Role", ["admin", "staff", "user"], help="Pilih peran pengguna")
            if st.form_submit_button("➕ Tambah Pengguna"):
                if username and password and name:
                    if username not in users:
                        users[username] = {
                            "password": hash_password(password),
                            "name": name,
                            "role": role,
                            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        }
                        save_users(users)
                        st.success("✅ Pengguna berhasil ditambahkan!")
                    else:
                        st.error("❌ Username sudah ada!")
                else:
                    st.error("❗ Lengkapi semua field!")
        st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<h3><i class='fas fa-list'></i> Daftar Pengguna</h3>", unsafe_allow_html=True)
    df_users = pd.DataFrame([
        {"Username": k, "Nama": v["name"], "Role": v["role"], "Dibuat": v["created_at"]}
        for k, v in users.items()
    ])
    st.table(df_users.style.set_properties(**{
        'background-color': '#2C2C2C',
        'color': '#FFD700',
        'border': '1px solid #FFD700',
        'text-align': 'center',
        'padding': '10px'
    }).set_table_styles([
        {'selector': 'th', 'props': [('background-color', '#FFD700'), ('color', '#1a1a1a'), ('font-weight', 'bold'), ('text-align', 'center')]},
        {'selector': 'td', 'props': [('border-right', '1px solid #FFD700')]}
    ]).hide(axis="index"))
    
    with st.container():
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<h3><i class='fas fa-user-minus'></i> Edit/Hapus Pengguna</h3>", unsafe_allow_html=True)
        username_to_edit = st.selectbox("Pilih Username", list(users.keys()))
        with st.form("form_edit_pengguna"):
            col1, col2 = st.columns(2)
            with col1:
                new_password = st.text_input("Password Baru", type="password", placeholder="Kosongkan jika tidak diubah")
                new_name = st.text_input("Nama Lengkap", value=users[username_to_edit]["name"])
            with col2:
                new_role = st.selectbox("Role", ["admin", "staff", "user"], index=["admin", "staff", "user"].index(users[username_to_edit]["role"]))
            col_submit, col_delete = st.columns(2)
            with col_submit:
                if st.form_submit_button("💾 Update Pengguna"):
                    if new_name:
                        users[username_to_edit]["name"] = new_name
                        users[username_to_edit]["role"] = new_role
                        if new_password:
                            users[username_to_edit]["password"] = hash_password(new_password)
                        save_users(users)
                        st.success("✅ Pengguna berhasil diperbarui!")
                    else:
                        st.error("❗ Nama lengkap tidak boleh kosong!")
            with col_delete:
                if st.form_submit_button("🗑️ Hapus Pengguna"):
                    if username_to_edit != st.session_state.username:
                        del users[username_to_edit]
                        save_users(users)
                        st.success("✅ Pengguna berhasil dihapus!")
                        st.rerun()
                    else:
                        st.error("❌ Tidak dapat menghapus pengguna yang sedang login!")
        st.markdown("</div>", unsafe_allow_html=True)

# ===============================
# Halaman Login
# ===============================
def show_login_page():
    st.markdown("<h1><i class='fas fa-motorcycle'></i> HONDA MOTOR</h1>", unsafe_allow_html=True)
    st.markdown("<h3>Sistem Pembelian Motor Premium</h3>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 2])
    with col1:
        with st.container():
            st.markdown("<div class='card'><h3><i class='fas fa-lock'></i> Login</h3>", unsafe_allow_html=True)
            with st.form("login_form"):
                username = st.text_input("Username", placeholder="Masukkan username")
                password = st.text_input("Password", type="password", placeholder="Masukkan password")
                if st.form_submit_button("🔐 Login"):
                    if authenticate(username, password):
                        st.success(f"✅ Selamat datang, {st.session_state.user_name}!")
                        st.rerun()
                    else:
                        st.error("❌ Username atau password salah!")
            
            st.markdown("<h3><i class='fas fa-user-plus'></i> Registrasi</h3>", unsafe_allow_html=True)
            with st.form("register_form"):
                new_username = st.text_input("Username Baru", placeholder="Masukkan username")
                new_password = st.text_input("Password Baru", type="password", placeholder="Masukkan password")
                new_name = st.text_input("Nama Lengkap", placeholder="Masukkan nama lengkap")
                if st.form_submit_button("📝 Daftar"):
                    users = load_users()
                    if new_username and new_password and new_name:
                        if new_username not in users:
                            users[new_username] = {
                                "password": hash_password(new_password),
                                "name": new_name,
                                "role": "user",
                                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            }
                            save_users(users)
                            st.success("✅ Registrasi berhasil! Silakan login.")
                        else:
                            st.error("❌ Username sudah ada!")
                    else:
                        st.error("❗ Lengkapi semua field!")
                with st.expander("Informasi"):
                    st.info("Silakan login atau daftar untuk melanjutkan. Hubungi admin jika ada masalah.")
            st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.image("https://ik.imagekit.io/zlt25mb52fx/ahmcdn/assets/images/logo/honda.svg", use_container_width=True)
        st.markdown("<p style='text-align: center; color: #FFD700;'>HONDA MOTOR - Kualitas dan Kepercayaan</p>", unsafe_allow_html=True)

# ===============================
# Main
# ===============================
def main():
    init_session_state()
    
    if not st.session_state.logged_in:
        show_login_page()
        return
    
    with st.sidebar:
        st.markdown("<h2><i class='fas fa-motorcycle'></i> HONDA MOTOR</h2>", unsafe_allow_html=True)
        st.markdown(f"<p><i class='fas fa-user'></i> {st.session_state.user_name}</p><p>Role: {st.session_state.user_role.capitalize()}</p>", unsafe_allow_html=True)
        st.markdown("<hr style='border-color: #FFD700'>", unsafe_allow_html=True)
        
        menu = [
            ("🏠 Home", "Home"),
            ("📝 Pembelian", "Form Pembelian"), # Changed label
            ("📜 Riwayat Pembelian", "Riwayat Pembelian")
        ]
        if st.session_state.user_role in ["admin", "staff"]:
            menu.extend([
                ("📊 Data Pembelian", "Data Pembelian"), # Changed label
                ("🛠️ Kelola Data", "Kelola Data"),
                ("📅 Absensi Cicilan", "Absensi Cicilan")
            ])
        if st.session_state.user_role == "admin":
            menu.append(("👥 Manajemen Pengguna", "Manajemen Pengguna"))
        
        for label, page in menu:
            if st.button(label, use_container_width=True):
                st.session_state.current_page = page
                st.rerun()
        
        st.markdown("<hr style='border-color: #FFD700'>", unsafe_allow_html=True)
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.username = None
            st.session_state.user_role = None
            st.session_state.user_name = None
            st.rerun()
    
    if st.session_state.current_page == "Home":
        show_home()
    elif st.session_state.current_page == "Form Pembelian": # Changed page name
        show_pembelian()
    elif st.session_state.current_page == "Riwayat Pembelian":
        show_riwayat_pembelian()
    elif st.session_state.current_page == "Data Pembelian": # Changed page name
        show_data()
    elif st.session_state.current_page == "Kelola Data":
        show_kelola_data()
    elif st.session_state.current_page == "Absensi Cicilan":
        show_cicilan()
    elif st.session_state.current_page == "Manajemen Pengguna":
        show_manajemen_pengguna()

if __name__ == "__main__":
    main()
