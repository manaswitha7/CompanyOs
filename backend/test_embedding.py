from app.services.embeddings.embedder import embedding_service


text = "NeuroBiomeX is a multimodal platform."

embedding = embedding_service.embed_text(text)

print("Embedding dimension:", len(embedding))
print("First 5 values:", embedding[:5])
