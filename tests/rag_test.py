import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rag_functionality.retriever import RAGSystem

rag = RAGSystem("wiedza.txt")

query = "W którym roku powstała adaptacja filmowa ksiązki?"
result = rag.rag_query(query)

print(f"Query: {query}")
print(f"Result: {result}")

query = "Jacy są główni bohaterowie?"
result = rag.rag_query(query)

print(f"Query: {query}")
print(f"Result: {result}")
