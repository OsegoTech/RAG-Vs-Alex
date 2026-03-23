# RAG Architecture Implementation Challenge & Performance Dashboard

This project implements a simple Retrieval-Augmented Generation (RAG) architecture with comprehensive performance monitoring and visualization.

## Features

- **Multiple Data Sources**: Retrieves information from a local JSON file and a simulated remote API
- **Asynchronous Operations**: Uses async/await to handle concurrent data retrieval with simulated delays
- **Error Handling**: Implements robust error handling for failed data fetches with logging
- **Performance Metrics**: Automatically collects and stores performance data for each query
- **Interactive Dashboard**: Visualize performance metrics with charts and filters
- **Real-time Monitoring**: Track response times, error rates, and query statistics

## Architecture

The system consists of:

1. **Data Sources** (`src/data_sources.py`):
   - Local source: JSON file with documents
   - Remote API: Simulated API with random delays and occasional failures

2. **RAG System** (`src/rag.py`):
   - Retrieves relevant documents from multiple sources
   - Combines and ranks retrieved information
   - Generates responses based on context
   - Records performance metrics for each query

3. **Metrics Collector** (`src/metrics.py`):
   - Collects performance data (response time, error rate, etc.)
   - Persists metrics to JSON file
   - Provides filtering and summary statistics

4. **Dashboard** (`app.py`):
   - Streamlit web application with two tabs
   - RAG query interface
   - Performance metrics dashboard with charts and filters

## Performance Metrics Collected

- **Response Time**: Total time to process a query
- **Success Rate**: Percentage of successful queries
- **Documents Retrieved**: Number of relevant documents found
- **Error Count**: Number of errors encountered per query
- **Source Utilization**: Which data sources were queried

## Challenges Addressed

- **Data Retrieval Delays**: Simulated with random sleep times in async operations
- **Inconsistent Response Times**: Different sources have different delay characteristics
- **Integration Difficulties**: Demonstrates combining data from heterogeneous sources
- **Performance Monitoring**: Tracks and visualizes system performance over time
- **Error Scenarios**: Handles connection failures and data processing errors

## Installation

1. Create a virtual environment:
   ```bash
   python3 -m venv venv
   ```

2. Activate the virtual environment:
   ```bash
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Web Interface
Run the Streamlit web application:
```bash
streamlit run app.py
```

This will start a web server. Open the provided URL in your browser to:
- **RAG Query Interface**: Test the RAG system by entering queries
- **Performance Dashboard**: Monitor system performance with interactive charts and metrics

*Note: The web dashboard requires additional packages (plotly, pandas). Install them with `pip install plotly pandas` if not already installed.*

### Command Line Test
Run the test script to generate sample metrics data:
```bash
python test_rag.py
```

### Dashboard Demo
Run the command-line dashboard demo to see metrics summary:
```bash
python dashboard_demo.py
```

This displays key performance indicators and recent query statistics.

## Simulated Challenges

- Random delays between 0.5-3 seconds for data retrieval
- 20% chance of API failure to simulate network issues
- Concurrent retrieval from multiple sources
- Error logging for debugging

This implementation provides a foundation for understanding RAG architectures and can be extended with real LLMs, vector databases, and production data sources.