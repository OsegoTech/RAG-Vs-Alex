import asyncio
import sys
import os
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from rag import RAGSystem
from metrics import MetricsCollector

# Initialize systems
rag_system = RAGSystem()
metrics_collector = MetricsCollector()

st.title("RAG Architecture Challenge & Performance Dashboard")
st.markdown("""
This application demonstrates a RAG (Retrieval-Augmented Generation) system with performance monitoring.
""")

# Create tabs
tab1, tab2 = st.tabs(["RAG Query Interface", "Performance Dashboard"])

with tab1:
    st.header("RAG Query Interface")
    st.markdown("""
    Enter a query to test the RAG system. The system will retrieve information from multiple sources
    and generate a response.
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
            st.info(f"Query processed. Retrieved {len(result['retrieved_documents'])} documents from {len(result.get('results', {}))} sources.")

        else:
            st.warning("Please enter a query.")

with tab2:
    st.header("Performance Dashboard")
    st.markdown("""
    Monitor the performance metrics of the RAG system including response times, error rates, and query statistics.
    """)

    # Date range filter
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", datetime.now().date() - timedelta(days=7))
    with col2:
        end_date = st.date_input("End Date", datetime.now().date())

    start_datetime = datetime.combine(start_date, datetime.min.time())
    end_datetime = datetime.combine(end_date, datetime.max.time())

    # Get metrics
    metrics_data = metrics_collector.get_metrics(start_datetime, end_datetime)
    summary_stats = metrics_collector.get_summary_stats(start_datetime, end_datetime)

    if not metrics_data:
        st.warning("No metrics data available for the selected date range. Try submitting some queries first.")
    else:
        # Summary section
        st.subheader("Key Performance Indicators")

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Queries", summary_stats["total_queries"])
        with col2:
            st.metric("Success Rate", f"{(1 - summary_stats['error_rate'])*100:.1f}%")
        with col3:
            st.metric("Avg Response Time", f"{summary_stats['avg_response_time']:.2f}s")
        with col4:
            st.metric("Avg Documents Retrieved", f"{summary_stats['avg_documents_retrieved']:.1f}")

        # Charts
        st.subheader("Performance Charts")

        # Convert metrics to DataFrame
        df = pd.DataFrame(metrics_data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp')

        # Response Time Over Time
        fig_response_time = px.line(df, x='timestamp', y='response_time',
                                   title='Response Time Over Time',
                                   labels={'response_time': 'Response Time (seconds)', 'timestamp': 'Time'})
        st.plotly_chart(fig_response_time, use_container_width=True)

        # Success/Error Rate
        col1, col2 = st.columns(2)

        with col1:
            success_counts = df['success'].value_counts()
            fig_success = px.pie(values=success_counts.values, names=['Failed', 'Successful'] if len(success_counts) > 1 else ['Successful'],
                                title='Query Success Rate')
            st.plotly_chart(fig_success, use_container_width=True)

        with col2:
            # Documents Retrieved Distribution
            fig_docs = px.histogram(df, x='num_documents', title='Documents Retrieved Distribution',
                                   labels={'num_documents': 'Number of Documents'})
            st.plotly_chart(fig_docs, use_container_width=True)

        # Response Time vs Documents Retrieved
        fig_scatter = px.scatter(df, x='num_documents', y='response_time',
                                title='Response Time vs Documents Retrieved',
                                labels={'num_documents': 'Documents Retrieved', 'response_time': 'Response Time (s)'},
                                color='success', color_discrete_map={True: 'green', False: 'red'})
        st.plotly_chart(fig_scatter, use_container_width=True)

        # Recent Queries Table
        st.subheader("Recent Queries")
        recent_df = df.tail(10)[['timestamp', 'query', 'response_time', 'num_documents', 'num_errors', 'success']]
        recent_df['query'] = recent_df['query'].str[:50] + '...'  # Truncate long queries
        st.dataframe(recent_df, use_container_width=True)

# Footer
st.markdown("---")
st.caption("RAG Challenge: Built with Streamlit, AsyncIO, and Plotly. Metrics are collected automatically for each query.")