import asyncio
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from rag import RAGSystem

async def test_rag():
    rag = RAGSystem()

    queries = [
        "What is machine learning?",
        "Tell me about AI",
        "Deep learning explanation"
    ]

    for query in queries:
        print(f"\n--- Query: {query} ---")
        result = await rag.process_query(query)

        print(f"Response: {result['response'][:200]}...")
        print(f"Retrieved {len(result['retrieved_documents'])} documents")
        if result['errors']:
            print(f"Errors: {result['errors']}")

if __name__ == "__main__":
    asyncio.run(test_rag())