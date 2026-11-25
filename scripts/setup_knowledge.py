from src.rag.index import MODEL, Knowledge

if __name__ == "__main__":
    knowledge = Knowledge.load()
    knowledge.enable_embeddings(download=True)
    print(f"Ready: {MODEL}, {len(knowledge.vectors)} reviewed vectors.")
