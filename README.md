# Local Technical Document RAG Assistant 
 
Tamamen yerel donanimda calisan, veri gizliligini koruyan teknik dokuman asistanidir. 
 
## Mimari ve Teknolojiler 
- **Yerel LLM:** Phi-3.5-mini (Microsoft Foundry Local / CPU / OpenVINO) 
- **Embedding Modeli:** Qwen3-Embedding-0.6B 
- **Vektor Depolama:** SQLite yerel indeksleme 
- **Arayuz:** Streamlit 
- **Sayfa Referansi:** Yanitlarin hangi dokuman ve sayfadan alindigini dogrulayan kaynak destegi 
 
## Calistirma 
1. pip install -r requirements.txt 
2. foundry server start --port 50000 
3. foundry model load 
4. streamlit run app.py
