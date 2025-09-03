import streamlit as st
from supabase import create_client
import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo  # Python 3.9+

# === CUSTOM BACKGROUND & SIDEBAR ===
st.markdown(
    """
    <style>
    /* Background halaman utama: pink gradient */
    .stApp {
        background-color: #252525;
    }

    /* Sidebar warna hijau */
    [data-testid="stSidebar"] {
        background-color: #f784c5;
    }
    /* Teks di sidebar jadi putih dan bold */
    [data-testid="stSidebar"] label, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3 {
        color: white;
        font-weight: bold;
        font-size: 18px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# === KONFIGURASI SUPABASE ===
supabase_url = st.secrets["SUPABASE_URL"]
supabase_key = st.secrets["SUPABASE_KEY"]
supabase = create_client(supabase_url, supabase_key)

# === KONFIGURASI STREAMLIT ===
st.set_page_config(page_title="Peminjaman iPhone 13", page_icon="📱")
st.title("📱 Peminjaman iPhone 13")

# === FUNGSI BANTUAN ===
def get_data():
    response = supabase.table("peminjaman").select("*").execute()
    return pd.DataFrame(response.data)

def pinjam(nama):
    supabase.table("peminjaman").insert({
        "nama": nama,
        "barang": "iPhone 13",
        "tanggal_pinjam": datetime.now(ZoneInfo("Asia/Jakarta")).strftime("%Y-%m-%d %H:%M"),
        "tanggal_kembali": "-",
        "status": "Dipinjam",
        "dipindahkan_ke": "-"
    }).execute()

def update_status(nama_asal, status, dipindahkan_ke="-"):
    supabase.table("peminjaman").update({
        "status": status,
        "tanggal_kembali": datetime.now(ZoneInfo("Asia/Jakarta")).strftime("%Y-%m-%d %H:%M"),
        "dipindahkan_ke": dipindahkan_ke
    }).eq("nama", nama_asal).eq("status", "Dipinjam").execute()

# === CEK DATA AKTIF ===
df = get_data()
peminjam_aktif = None
if not df.empty:
    aktif = df[df["status"] == "Dipinjam"]
    if not aktif.empty:
        peminjam_aktif = aktif.iloc[0]["nama"]

# === MENU ===
menu = st.sidebar.radio("Pilih Menu:", ["Pinjam", "Kembalikan / Transfer", "Lihat Status", "Riwayat"])

# === FITUR PINJAM ===
if menu == "Pinjam":
    st.header("📑 Pinjam iPhone 13")
    if peminjam_aktif:
        st.warning(f"❌ iPhone 13 sedang dipinjam oleh **{peminjam_aktif}**")
    else:
        nama = st.text_input("Nama Peminjam")
        if st.button("Pinjam"):
            if nama.strip() == "":
                st.error("Nama peminjam harus diisi!")
            else:
                pinjam(nama)
                st.success(f"✅ iPhone 13 berhasil dipinjam oleh {nama}")

# === FITUR KEMBALIKAN / TRANSFER ===
elif menu == "Kembalikan / Transfer":
    st.header("🔄 Kembalikan / Transfer iPhone 13")
    if peminjam_aktif:
        st.info(f"Saat ini iPhone 13 sedang dipinjam oleh **{peminjam_aktif}**")
        aksi = st.radio("Aksi:", ["Kembalikan ke Stok", "Pindahkan ke Peminjam Lain"])

        if aksi == "Pindahkan ke Peminjam Lain":
            penerima = st.text_input("Nama Peminjam Baru")

        if st.button("Proses"):
            if aksi == "Kembalikan ke Stok":
                update_status(peminjam_aktif, "Dikembalikan")
                st.success(f"🔄 iPhone 13 dikembalikan oleh {peminjam_aktif}")
            elif aksi == "Pindahkan ke Peminjam Lain" and penerima.strip() != "":
                update_status(peminjam_aktif, "Dipindahkan", dipindahkan_ke=penerima)
                pinjam(penerima)
                st.success(f"🔁 iPhone 13 dipindahkan dari {peminjam_aktif} ke {penerima}")
    else:
        st.info("✅ iPhone 13 sedang tersedia.")

# === LIHAT STATUS ===
elif menu == "Lihat Status":
    st.header("📋 Status iPhone 13 Saat Ini")
    if peminjam_aktif:
        st.warning(f"❌ iPhone 13 sedang dipinjam oleh **{peminjam_aktif}**")
    else:
        st.success("✅ iPhone 13 tersedia")

# === RIWAYAT ===
elif menu == "Riwayat":
    st.header("📜 Riwayat Peminjaman iPhone 13")
    df = get_data()
    if not df.empty:
        st.dataframe(df)
    else:
        st.info("Belum ada transaksi.")
