import json
import sqlite3
import numpy as np
import streamlit as st
from openai import OpenAI
from pypdf import PdfReader

# Sayfa Yapılandırması
st.set_page_config(
    page_title="Yerel RAG Asistanı",
    page_icon="🔬",
    layout="wide"
)

# Yan Panel - Sunucu Ayarları & Doküman Yükleme
with st.sidebar:
    st.title("⚙️ Sunucu Ayarları")
    server_port = st.text_input("Foundry Portu", value="50000")
    base_url = f"http://127.0.0.1:{server_port}/v1"
    
    client = OpenAI(
        base_url=base_url,
        api_key="foundry"
    )

    st.markdown("---")
    st.title("📂 Doküman Yükleme")
    uploaded_file = st.file_uploader("PDF veya Föy Yükle", type=["pdf"])

# Veritabanı Fonksiyonları
def init_db():
    conn = sqlite3.connect("knowledge_base.db", timeout=30, check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("PRAGMA journal_mode=WAL;")  # Eşzamanlı erişim kilidini çözer
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT,
        page_num INTEGER,
        text TEXT,
        embedding TEXT
    )
    """)
    conn.commit()
    return conn

db_conn = init_db()

def get_embedding(text: str):
    response = client.embeddings.create(
        model="qwen3-embedding-0.6b-generic-cpu:1",
        input=text
    )
    return response.data[0].embedding

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 100):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()
        if len(chunk) > 40:
            chunks.append(chunk)
        start += (chunk_size - overlap)
    return chunks

def ingest_pdf_file(conn, uploaded_file):
    reader = PdfReader(uploaded_file)
    cursor = conn.cursor()
    filename = uploaded_file.name
    total_chunks = 0

    for idx, page in enumerate(reader.pages):
        text = page.extract_text()
        if text and text.strip():
            page_chunks = chunk_text(text.strip(), chunk_size=500, overlap=100)
            for p in page_chunks:
                emb = get_embedding(p)
                cursor.execute(
                    "INSERT INTO documents (filename, page_num, text, embedding) VALUES (?, ?, ?, ?)",
                    (filename, idx + 1, p, json.dumps(emb))
                )
                total_chunks += 1
    conn.commit()
    return total_chunks

def search_similar_docs(conn, query: str, top_k: int = 3):
    query_emb = np.array(get_embedding(query))
    cursor = conn.cursor()
    cursor.execute("SELECT filename, page_num, text, embedding FROM documents")
    rows = cursor.fetchall()

    if not rows:
        return []

    scored_chunks = []
    for fname, page_num, text, emb_str in rows:
        doc_emb = np.array(json.loads(emb_str))
        score = np.dot(query_emb, doc_emb) / (np.linalg.norm(query_emb) * np.linalg.norm(doc_emb))
        scored_chunks.append((score, fname, page_num, text))

    scored_chunks.sort(key=lambda x: x[0], reverse=True)
    return scored_chunks[:top_k]

def ask_rag_stream(conn, question: str):
    results = search_similar_docs(conn, question, top_k=3)
    if not results or results[0][0] < 0.25:
        def not_found():
            yield "Bu bilgi dokümanda bulunmamaktadır."
        return not_found(), []

    # Bağlamı ve kaynakları derle
    context_text = "\n\n".join([text for _, _, _, text in results])
    sources = [(fname, page_num) for _, fname, page_num, _ in results]

    system_prompt = (
        "Sen teknik dokümanları analiz eden uzman bir asistansın. "
        "Aşağıdaki bağlamı oku ve soruya sadece verilen metne sadık kalarak, doğrudan ve net yanıt ver. "
        "Metinde yer almayan hiçbir bilgiyi uydurma."
    )
    user_prompt = f"Bağlam Metni:\n{context_text}\n\nSoru: {question}\nCevap:"

    response = client.chat.completions.create(
        model="phi-3.5-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.1,
        max_tokens=250,
        stream=True
    )
    
    def stream_generator():
        for chunk in response:
            if chunk.choices and len(chunk.choices) > 0:
                delta = chunk.choices[0].delta
                if hasattr(delta, "content") and delta.content:
                    yield delta.content

    return stream_generator(), sources
    return stream_generator(), sources

# İndeksleme ve Veritabanı Sıfırlama Butonları
with st.sidebar:
    if uploaded_file is not None:
        if st.button("Belgeyi İndeksle", type="primary"):
            with st.spinner("Metin parçalanıyor ve vektörleştiriliyor..."):
                try:
                    count = ingest_pdf_file(db_conn, uploaded_file)
                    st.success(f"{uploaded_file.name} başarıyla indekslendi ({count} parça)!")
                except Exception as e:
                    st.error(f"Hata oluştu: {e}")

    if st.button("🗑️ Veritabanını Sıfırla"):
        cursor = db_conn.cursor()
        cursor.execute("DELETE FROM documents")
        db_conn.commit()
        st.warning("Veritabanı temizlendi.")

# Ana Sohbet Ekranı
st.title("🔬 Teknik Doküman RAG Asistanı")
st.caption(f"Phi-3.5-mini + Qwen3-Embedding | Endpoint: `{base_url}`")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Föyle ilgili bir soru sorun..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            stream_gen, sources = ask_rag_stream(db_conn, prompt)
            full_response = st.write_stream(stream_gen)

            # Kaynakları göster
            if sources:
                unique_sources = list(set([f"📌 `{fname}` (Sayfa {pnum})" for fname, pnum in sources]))
                source_box = "\n\n**Referanslar:**\n" + "\n".join(unique_sources)
                st.markdown(source_box)
                full_response += source_box

            st.session_state.messages.append({"role": "assistant", "content": full_response})
        except Exception as e:
            err_msg = f"Model yanıt verirken hata oluştu: {e}"
            st.error(err_msg)
            st.session_state.messages.append({"role": "assistant", "content": err_msg})