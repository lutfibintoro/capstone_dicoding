import streamlit as st
import pertanyaan1
import pertanyaan2
import pertanyaan3
import pertanyaan4


st.title("📈 Dashboard")
st.sidebar.markdown("# Filter Parameter")

q1 = 'Q1: Apa saja skill yang paling banyak diminta per industri, level pengalaman, dan tipe pekerjaan, serta bagaimana korelasinya dengan rentang gaji ?'
q2 = 'Q2: Bagaimana pola rasio aplikasi terhadap views (apply-through-rate) berdasarkan kompleksitas skill, lokasi, dan kebijakan remote ?'
q3 = 'Q3: Skill apa yang sering muncul bersamaan (co-occurrence) dalam satu lowongan, dan kombinasi mana yang paling prediktif terhadap gaji tinggi atau penutupan lowongan yang cepat ?'
q4 = 'Q4: Bagaimana variasi kompensasi (gaji) dipengaruhi oleh kombinasi: industri, skill teknis vs. non-teknis, ukuran perusahaan, dan lokasi ?'

genre = st.radio(
    "Pilih dasboard interaktif untuk pertanyaan",
    (q1, q2, q3, q4)
)

st.divider()

# 3. Menampilkan Pilihan
if genre == q1:
    pertanyaan1.visualisasi_pertanyaan()

elif genre == q2:
    pertanyaan2.visualisasi_pertanyaan()

elif genre == q3:
    pertanyaan3.visualisasi_pertanyaan()

elif genre == q4:
    pertanyaan4.visualisasi_pertanyaan()
