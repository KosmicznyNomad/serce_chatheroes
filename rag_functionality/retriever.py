import os
from dotenv import load_dotenv
from openai import OpenAI
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import glob

class RAGSystem:
    def __init__(self, file_path, chunk_size=1000, chunk_overlap=200):
        load_dotenv(dotenv_path='../.env')
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.client = OpenAI(api_key=self.openai_api_key)
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.file_path = file_path
        self.documents = []
        self.embeddings = []
        self.setup_rag_system()

    def setup_rag_system(self):
        self.load_documents()
        self.create_embeddings()

    def load_documents(self):
        if os.path.isdir(self.file_path):
            for txt_file in glob.glob(os.path.join(self.file_path, "**/*.txt"), recursive=True):
                self.documents.extend(self.read_txt(txt_file))
        else:
            self.documents = self.read_txt(self.file_path)

    def read_txt(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read()
        return self.split_text(text)

    def split_text(self, text):
        chunks = []
        start = 0
        while start < len(text):
            end = start + self.chunk_size
            if end < len(text):
                end = text.rfind(' ', start, end)
            chunks.append(text[start:end])
            start = end - self.chunk_overlap
        return chunks

    def create_embeddings(self):
        for chunk in self.documents:
            response = self.client.embeddings.create(
                input=chunk,
                model="text-embedding-3-small"
            )
            self.embeddings.append(response.data[0].embedding)

    def query(self, question, top_k=3):
        query_embedding = self.client.embeddings.create(
            input=question,
            model="text-embedding-3-small"
        ).data[0].embedding

        similarities = cosine_similarity([query_embedding], self.embeddings)[0]
        top_k_indices = np.argsort(similarities)[-top_k:][::-1]
        contexts = [self.documents[i] for i in top_k_indices]

        combined_context = "\n\n".join(contexts)

        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant. Answer the question based on the given contexts."},
                {"role": "user", "content": f"Contexts:\n{combined_context}\n\nQuestion: {question}"}
            ]
        )

        return response.choices[0].message.content

    def rag_query(self, query):
        return self.query(query)
