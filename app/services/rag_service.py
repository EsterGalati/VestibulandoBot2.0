import os
import numpy as np
import fitz
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

DOCUMENTS_DIR = "/app/documents"


class RAGMemoria:
    def __init__(self):
        print("📄 Inicializando RAG...")
        self.model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

        self.documentos = []
        self.embeddings = []
        self.origens = []

        self.carregar_documentos()
        print(f"📘 Total carregado: {len(self.documentos)} documentos.")

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
            texto = ""
            for pagina in doc:
                texto += pagina.get_text()
            return texto.strip()
        except Exception as e:
            print(f"❌ Erro ao ler PDF {caminho}: {e}")
            return ""
        
    def carregar_documentos(self):
        if not os.path.exists(DOCUMENTS_DIR):
            print(f"⚠️ Pasta {DOCUMENTS_DIR} não encontrada.")
            return

        arquivos = os.listdir(DOCUMENTS_DIR)

        if not arquivos:
            print(f"⚠️ Nenhum arquivo encontrado no diretório")
            return

        print("📚 Lendo documentos e gerando embeddings...")

        for nome in arquivos:
            caminho = os.path.join(DOCUMENTS_DIR, nome)
            ext = nome.lower().split(".")[-1]

            if ext == "txt":
                print(f"📄 Lendo TXT: {nome}")
                texto = self.ler_txt(caminho)
            elif ext == "pdf":
                print(f"📄 Lendo PDF: {nome}")
                texto = self.ler_pdf(caminho)
            else:
                print(f"⚠️ Ignorando extensão não suportada: {nome}")
                continue

            if not texto:
                print(f"⚠️ Documento vazio ou com erro: {nome}")
                continue

            try:
                emb = self.model.encode(texto)

                self.documentos.append(texto)
                self.embeddings.append(emb)
                self.origens.append(nome)

                print(f"✔ Documento carregado: {nome}")

            except Exception as e:
                print(f"❌ Erro no embedding de {nome}: {e}")

        self.embeddings = np.array(self.embeddings)

    def buscar(self, query, top_k=1):
        if not self.documentos:
            print("⚠️ Nenhum documento carregado.")
            return None

        print("🔎 Rodando busca local...")

        query_emb = self.model.encode(query)
        sims = cosine_similarity([query_emb], self.embeddings)[0]

        idxs = sims.argsort()[::-1][:top_k]

        melhor_idx = idxs[0]
        melhor_score = sims[melhor_idx]
        origem = self.origens[melhor_idx]

        print(f"📌 Melhor similaridade: {melhor_score} (arquivo: {origem})")

        if melhor_score < 0.40:
            print("⚠️ Similaridade muito baixa, ignorando.")
            return None
        
        return self.documentos[melhor_idx]

rag = RAGMemoria()
