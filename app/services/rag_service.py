import os
import math
import numpy as np
import fitz
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

DOCUMENTS_DIR = "/app/documents"

# configurações ajustáveis
CHUNK_WORD_SIZE = 200
CHUNK_OVERLAP = 50
TOP_K = 5
SIMILARITY_THRESHOLD = 0.35
MAX_CONTEXT_CHARS = 2000

class RAGMemoria:
    def __init__(self):
        print("📄 Inicializando RAG...")

        self.model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")


        self.chunks = []
        self.embeddings = None  # numpy array (n_chunks, dim)
        self.carregar_documentos()
        total = len(self.chunks)
        print(f"📘 Total de chunks carregados: {total}")

    def ler_txt(self, caminho):
        try:
            with open(caminho, "r", encoding="utf-8") as f:
                return f.read().strip()
        except Exception as e:
            print(f"❌ Erro ao ler TXT {caminho}: {e}")
            return ""

    def ler_pdf(self, caminho):
        try:
            doc = fitz.open(caminho)
            partes = []
            for pagina in doc:
                partes.append(pagina.get_text())
            return "\n".join(partes).strip()
        except Exception as e:
            print(f"❌ Erro ao ler PDF {caminho}: {e}")
            return ""

    def _chunk_text(self, texto, chunk_size=CHUNK_WORD_SIZE, overlap=CHUNK_OVERLAP):
        palavras = texto.split()
        if not palavras:
            return []

        chunks = []
        start = 0
        total = len(palavras)
        chunk_id = 0

        while start < total:
            end = start + chunk_size
            slice_words = palavras[start:end]
            chunk_text = " ".join(slice_words).strip()
            if chunk_text:
                chunks.append({
                    "chunk_id": chunk_id,
                    "start_word": start,
                    "end_word": min(end, total),
                    "text": chunk_text
                })
                chunk_id += 1
            if end >= total:
                break
            start = end - overlap  # overlap
        return chunks

    def carregar_documentos(self):
        if not os.path.exists(DOCUMENTS_DIR):
            print(f"⚠️ Pasta {DOCUMENTS_DIR} não encontrada.")
            return

        arquivos = sorted([f for f in os.listdir(DOCUMENTS_DIR) if not f.startswith(".")])
        if not arquivos:
            print(f"⚠️ Nenhum arquivo encontrado no diretório {DOCUMENTS_DIR}")
            return

        print("📚 Lendo documentos e gerando chunks + embeddings...")

        temp_chunks = []
        for nome in arquivos:
            caminho = os.path.join(DOCUMENTS_DIR, nome)
            ext = nome.lower().split(".")[-1]

            if ext == "txt":
                texto = self.ler_txt(caminho)
            elif ext == "pdf":
                texto = self.ler_pdf(caminho)
            else:
                print(f"⚠️ Ignorando extensão não suportada: {nome}")
                continue

            if not texto:
                print(f"⚠️ Documento vazio ou com erro: {nome}")
                continue

            local_chunks = self._chunk_text(texto)
            if not local_chunks:
                continue

            for c in local_chunks:
                temp_chunks.append({
                    "arquivo": nome,
                    "chunk_id": c["chunk_id"],
                    "start_word": c["start_word"],
                    "end_word": c["end_word"],
                    "text": c["text"]
                })

            print(f"✔ Documento processado: {nome} -> {len(local_chunks)} chunks")

        if not temp_chunks:
            print("⚠️ Nenhum chunk gerado (arquivos vazios?).")
            return

        textos_para_emb = [c["text"] for c in temp_chunks]
        try:
            embs = self.model.encode(textos_para_emb, show_progress_bar=True)
        except Exception as e:
            print(f"❌ Erro ao gerar embeddings dos chunks: {e}")
            return

        self.chunks = temp_chunks
        self.embeddings = np.array(embs)

    def buscar(self, query, top_k=TOP_K, threshold=SIMILARITY_THRESHOLD, max_context_chars=MAX_CONTEXT_CHARS):
        print("\n🔎 Iniciando busca RAG...")
        print(f"📝 Query: {query}")

        if not self.chunks or self.embeddings is None or len(self.embeddings) == 0:
            print("⚠️ Nenhum chunk carregado no RAG.")
            return None

        query_emb = self.model.encode(query)

        sims = cosine_similarity([query_emb], self.embeddings)[0]
        
        top_idxs = sims.argsort()[::-1][:max(top_k * 2, top_k)]

        print("\n📊 Top chunks:")
        for idx in top_idxs:
            chunk = self.chunks[idx]
            print(f" - [{chunk['arquivo']} | chunk {chunk['chunk_id']}] score={sims[idx]:.4f}")

        selected = [(i, float(sims[i])) for i in top_idxs if sims[i] >= threshold]

        if not selected:
            print(f"⚠️ Nenhum chunk atingiu o threshold de {threshold}")
            return None

        selected = sorted(selected, key=lambda t: t[1], reverse=True)[:top_k]

        print("\n🏆 Chunks selecionados:")
        for idx, score in selected:
            chunk = self.chunks[idx]
            print(f" ✔ [{chunk['arquivo']} | chunk {chunk['chunk_id']}] score={score:.4f}")

        contexto_pieces = []
        fontes = []
        raw_chunks = []
        context_len = 0

        print("\n📚 Montando contexto final...")
        for idx, score in selected:
            chunk = self.chunks[idx]
            text = chunk["text"].strip()

            if context_len + len(text) > max_context_chars:
                remaining = max_context_chars - context_len
                if remaining <= 0:
                    break
                text = text[:remaining]

            contexto_pieces.append(text)
            context_len += len(text)

            fontes.append({
                "arquivo": chunk["arquivo"],
                "chunk_id": int(chunk["chunk_id"]),
                "score": float(score)
            })

            raw_chunks.append({
                "arquivo": chunk["arquivo"],
                "chunk_id": int(chunk["chunk_id"]),
                "text": text,
                "score": float(score)
            })

        print(f"📏 Tamanho final do contexto: {context_len} caracteres")

        contexto_final = "\n\n".join(contexto_pieces).strip()

        print("\n✅ Busca concluída!\n")

        return {
            "contexto": contexto_final,
            "fontes": fontes,
            "chunks": raw_chunks
        }


rag = RAGMemoria()
