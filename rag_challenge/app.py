import asyncio
import sys
import os
import streamlit as st

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from rag import RAGSystem

# Initialize the RAG system
rag_system = RAGSystem()

st.title("RAG Architecture Challenge")
st.markdown("""
This is a simple RAG (Retrieval-Augmented Generation) system that demonstrates:
- Data retrieval from multiple sources
- Asynchronous operations with simulated delays
- Error handling and logging
- User interface for displaying results
""")

# User input
query = st.text_input("Enter your query:", placeholder="e.g., What is machine learning?")

if st.button("Submit Query"):
    if query.strip():
        with st.spinner("Processing your query... This may take a few seconds due to simulated delays."):
            # Run the async RAG process
            result = asyncio.run(rag_system.process_query(query))

        # Display results
        st.subheader("Response:")
        st.write(result["response"])

        # Display retrieved documents
        if result["retrieved_documents"]:
            st.subheader("Retrieved Documents:")
            for doc in result["retrieved_documents"]:
                with st.expander(f"{doc.get('title', 'Untitled')} (ID: {doc.get('id', 'N/A')})"):
                    st.write(doc.get('content', 'No content available'))
                    if 'source' in doc:
                        st.caption(f"Source: {doc['source']}")

        # Display errors if any
        if result["errors"]:
            st.error("Errors encountered during retrieval:")
            for error in result["errors"]:
                st.write(f"- {error}")

        # Show processing info
        st.info(f"Query processed. Retrieved {len(result['retrieved_documents'])} documents from {len(result['results']) if 'results' in result else 0} sources.")

    else:
        st.warning("Please enter a query.")

# Footer
st.markdown("---")
st.caption("This is a challenge implementation. In a production RAG system, you would use actual LLMs, vector databases, and real data sources.")