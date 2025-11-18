import os
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

DOCUMENTS_DIR = "/app/documents"

class RAGMemoria:
    def __init__(self):
        print("📄 Inicializando RAG local (offline)...")
        self.model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        self.documentos = []      # Lista com textos
        self.embeddings = []      # Embeddings em memória
        self.carregar_documentos()
        print(f"📘 Total carregado: {len(self.documentos)} documentos.")

    def carregar_documentos(self):
        """Carrega arquivos .txt e gera embeddings"""
        if not os.path.exists(DOCUMENTS_DIR):
            print(f"⚠️ Pasta {DOCUMENTS_DIR} não encontrada.")
            return

        arquivos = [f for f in os.listdir(DOCUMENTS_DIR) if f.endswith(".txt")]

        if not arquivos:
            print(f"⚠️ Nenhum .txt encontrado em {DOCUMENTS_DIR}")
            return

        print("📚 Lendo documentos e gerando embeddings...")

        for nome in arquivos:
            caminho = os.path.join(DOCUMENTS_DIR, nome)
            try:
                with open(caminho, "r", encoding="utf-8") as f:
                    texto = f.read().strip()

                emb = self.model.encode(texto)

                self.documentos.append(texto)
                self.embeddings.append(emb)

                print(f"✔ Documento carregado: {nome}")

            except Exception as e:
                print(f"❌ Erro ao carregar {nome}: {e}")

        self.embeddings = np.array(self.embeddings)

    def buscar(self, query, top_k=1):
        """Retorna o documento mais relevante usando similarity local"""
        if not self.documentos:
            print("⚠️ Nenhum documento carregado no RAG.")
            return None

        print("🔎 Rodando busca local...")

        query_emb = self.model.encode(query)
        sims = cosine_similarity([query_emb], self.embeddings)[0]

        idxs = sims.argsort()[::-1][:top_k]
        melhor_idx = idxs[0]
        melhor_score = sims[melhor_idx]

        print(f"📌 Melhor similaridade: {melhor_score}")

        if melhor_score < 0.40:
            print("⚠️ Similaridade muito baixa, ignorando documento.")
            return None

        return self.documentos[melhor_idx]

# Instância global
rag = RAGMemoria()
