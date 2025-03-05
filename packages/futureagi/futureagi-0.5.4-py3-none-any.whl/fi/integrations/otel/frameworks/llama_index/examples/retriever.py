from llama_index import SimpleDirectoryReader, VectorStoreIndex
from llama_index.postprocessor import SimilarityPostprocessor
from llama_index.query_engine import RetrieverQueryEngine
from llama_index.retrievers import VectorIndexRetriever


def create_index(documents_path):
    # Load documents from the specified directory
    documents = SimpleDirectoryReader(documents_path).load_data()

    # Create a vector store index
    index = VectorStoreIndex.from_documents(documents)
    return index


def setup_retriever_engine(index, similarity_cutoff=0.7, top_k=10):
    # Configure the retriever
    retriever = VectorIndexRetriever(index=index, similarity_top_k=top_k)

    # Create a similarity postprocessor for reranking
    postprocessor = SimilarityPostprocessor(similarity_cutoff=similarity_cutoff)

    # Create the query engine with the retriever and postprocessor
    query_engine = RetrieverQueryEngine(
        retriever=retriever, node_postprocessors=[postprocessor]
    )

    return query_engine


def search_and_rerank(query_engine, query_text):
    # Perform the search and reranking
    response = query_engine.query(query_text)

    # Get source nodes (retrieved documents)
    source_nodes = response.source_nodes

    # Print results
    print(f"\nQuery: {query_text}")
    print("\nRanked Results:")
    for idx, node in enumerate(source_nodes, 1):
        print(f"\n{idx}. Score: {node.score:.4f}")
        print(f"Text: {node.node.text[:200]}...")  # Show first 200 chars


def main():
    # Initialize the system
    documents_path = "path/to/your/documents"
    index = create_index(documents_path)
    query_engine = setup_retriever_engine(index, similarity_cutoff=0.7, top_k=5)

    # Example queries
    queries = [
        "What is machine learning?",
        "How does natural language processing work?",
    ]

    # Process each query
    for query in queries:
        search_and_rerank(query_engine, query)


if __name__ == "__main__":
    main()
