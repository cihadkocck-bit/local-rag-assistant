# 🔬 Local Technical Document RAG Assistant

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" />
  <img src="https://img.shields.io/badge/Model-Phi--3.5--mini-0078D4?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Privacy-100%25_Local-success?style=for-the-badge" />
</p>

<p align="center">
  <img width="1916" height="937" alt="Arayüz Önizleme" src="https://github.com/user-attachments/assets/ef8d5433-4b76-4dfe-87b5-9890e9778688" />
</p>

> **Tamamen yerel donanımda çalışan, veri gizliliğini koruyan teknik doküman asistanıdır.**

---

### 📺 Demo Videosu

<p align="center">
  <a href="https://www.youtube.com/watch?v=RnslqVKXL8U">
    <img src="https://img.youtube.com/vi/RnslqVKXL8U/hqdefault.jpg" alt="Demo Videosu" width="600" />
  </a>
  <br>
  <em>👉 Arayüz ve çalışma videosunu izlemek için görsele tıklayın.</em>
</p>

---

### 🛠️ Mimari ve Teknolojiler

| Bileşen | Teknoloji | Açıklama |
| :--- | :--- | :--- |
| **Yerel LLM** | `Phi-3.5-mini` | Microsoft Foundry Local / CPU / OpenVINO |
| **Embedding Modeli** | `Qwen3-Embedding-0.6B` | Hızlı ve yerel vektörleştirme |
| **Vektör Depolama** | `SQLite` | Sıfır harici bağımlılık, yerel indeksleme |
| **Arayüz** | `Streamlit` | Kullanıcı dostu web paneli |
| **Sayfa Referansı** | Kaynak Doğrulama | Yanıtların hangi doküman ve sayfadan alındığı desteği |

---

### ⚡ Nasıl Çalıştırılır?

**Tek Tıkla Başlatma (Önerilen):**
1. Yeşil **Code** butonuna basıp **Download ZIP** seçeneğiyle projeyi indirin ve zipten çıkarın.
2. Klasörün içindeki `RAG_Baslat.bat` dosyasına çift tıklayın.

<details>
<summary><b>Terminalden Manuel Çalıştırma</b></summary>

```bash
# 1. Kütüphaneleri kurun
pip install -r requirements.txt

# 2. Foundry sunucusunu başlatın
foundry server start --port 50000

# 3. Modelleri yükleyin
foundry model load

# 4. Arayüzü çalıştırın
python -m streamlit run app.py
