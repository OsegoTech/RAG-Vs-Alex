import logging
import time
from typing import List, Dict, Any
from data_sources import retrieve_all_sources
from metrics import MetricsCollector

logger = logging.getLogger(__name__)

class RAGSystem:
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.metrics_collector = MetricsCollector()

    async def process_query(self, query: str) -> Dict[str, Any]:
        """
        Process a user query using RAG architecture.
        """
        start_time = time.time()

        try:
            # Step 1: Retrieve relevant information from multiple sources
            retrieval_result = await retrieve_all_sources(query)

            # Step 2: Combine and rank the retrieved information
            combined_context = self._combine_context(retrieval_result["results"])

            # Step 3: Generate response based on retrieved context
            response = self._generate_response(query, combined_context)

            # Calculate metrics
            response_time = time.time() - start_time
            num_sources = len(retrieval_result["results"])
            num_documents = len(combined_context)
            num_errors = len(retrieval_result["errors"])
            success = len(retrieval_result["errors"]) == 0

            # Record metrics
            self.metrics_collector.record_query(
                query=query,
                response_time=response_time,
                num_sources=num_sources,
                num_documents=num_documents,
                num_errors=num_errors,
                success=success
            )

            return {
                "query": query,
                "response": response,
                "retrieved_documents": combined_context,
                "errors": retrieval_result["errors"]
            }

        except Exception as e:
            response_time = time.time() - start_time
            self.logger.error(f"Error processing query '{query}': {str(e)}")

            # Record failed query metrics
            self.metrics_collector.record_query(
                query=query,
                response_time=response_time,
                num_sources=0,
                num_documents=0,
                num_errors=1,
                success=False
            )

            return {
                "query": query,
                "response": "Sorry, I encountered an error while processing your query.",
                "retrieved_documents": [],
                "errors": [f"System error: {str(e)}"]
            }

    def _combine_context(self, results: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """
        Combine and deduplicate retrieved documents from different sources.
        """
        combined = []
        seen_ids = set()

        for source_docs in results.values():
            for doc in source_docs:
                doc_id = doc.get('id', doc.get('title', str(doc)))
                if doc_id not in seen_ids:
                    combined.append(doc)
                    seen_ids.add(doc_id)

        # Sort by relevance (simple: prefer longer content as proxy for relevance)
        combined.sort(key=lambda x: len(x.get('content', '')), reverse=True)

        return combined[:5]  # Limit to top 5 documents

    def _generate_response(self, query: str, context: List[Dict[str, Any]]) -> str:
        """
        Simulate response generation based on retrieved context.
        In a real RAG system, this would use an LLM.
        """
        if not context:
            return f"I couldn't find relevant information for your query: '{query}'. Please try rephrasing or check for typos."

        # Simple response generation: summarize the top documents
        response_parts = [f"Based on the information I retrieved about '{query}':"]

        for i, doc in enumerate(context[:3], 1):  # Use top 3 documents
            title = doc.get('title', 'Untitled')
            content = doc.get('content', '')[:200] + '...' if len(doc.get('content', '')) > 200 else doc.get('content', '')
            response_parts.append(f"{i}. {title}: {content}")

        response_parts.append("\nThis is a simulated response. In a real RAG system, an LLM would generate a more natural and comprehensive answer.")

        return '\n'.join(response_parts)