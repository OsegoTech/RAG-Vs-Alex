import asyncio
import json
import logging
import os
import random
from typing import List, Dict, Any

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def retrieve_from_local_source(query: str) -> List[Dict[str, Any]]:
    """
    Simulate retrieving data from a local data source.
    In a real scenario, this could be a database or file system.
    """
    try:
        # Simulate some processing delay
        await asyncio.sleep(random.uniform(0.5, 1.5))

        with open(os.path.join(os.path.dirname(__file__), '..', 'data', 'documents.json'), 'r') as f:
            documents = json.load(f)

        # Simple keyword matching for retrieval
        relevant_docs = []
        query_lower = query.lower()
        for doc in documents:
            if any(word in doc['content'].lower() or word in doc['title'].lower()
                   for word in query_lower.split()):
                relevant_docs.append(doc)

        logger.info(f"Retrieved {len(relevant_docs)} documents from local source for query: {query}")
        return relevant_docs

    except Exception as e:
        logger.error(f"Error retrieving from local source: {str(e)}")
        raise

async def retrieve_from_remote_api(query: str) -> List[Dict[str, Any]]:
    """
    Simulate retrieving data from a remote API.
    In a real scenario, this would make an HTTP request.
    """
    try:
        # Simulate network delay
        await asyncio.sleep(random.uniform(1.0, 3.0))

        # Simulate occasional failures
        if random.random() < 0.2:  # 20% chance of failure
            raise ConnectionError("Simulated API connection failure")

        # Mock API response
        mock_data = [
            {
                "id": "api_1",
                "title": "Latest AI Research",
                "content": f"Recent advancements in AI include improved {query} techniques and novel applications in various domains.",
                "source": "remote_api"
            },
            {
                "id": "api_2",
                "title": "AI Ethics and Safety",
                "content": "As AI systems become more powerful, ensuring ethical use and safety measures is crucial for responsible development.",
                "source": "remote_api"
            }
        ]

        # Filter based on query
        relevant_docs = [doc for doc in mock_data if query.lower() in doc['content'].lower() or query.lower() in doc['title'].lower()]

        logger.info(f"Retrieved {len(relevant_docs)} documents from remote API for query: {query}")
        return relevant_docs

    except Exception as e:
        logger.error(f"Error retrieving from remote API: {str(e)}")
        raise

async def retrieve_all_sources(query: str) -> Dict[str, Any]:
    """
    Retrieve data from all sources concurrently.
    """
    results = {}
    errors = []

    # Run both retrievals concurrently
    tasks = [
        retrieve_from_local_source(query),
        retrieve_from_remote_api(query)
    ]

    task_results = await asyncio.gather(*tasks, return_exceptions=True)

    for i, result in enumerate(task_results):
        source_name = "local_source" if i == 0 else "remote_api"
        if isinstance(result, Exception):
            errors.append(f"{source_name}: {str(result)}")
            results[source_name] = []
        else:
            results[source_name] = result

    return {
        "results": results,
        "errors": errors
    }