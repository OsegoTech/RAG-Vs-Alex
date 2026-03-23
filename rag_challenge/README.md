# RAG Architecture Implementation Challenge

This project implements a simple Retrieval-Augmented Generation (RAG) architecture to demonstrate common implementation challenges and solutions.

## Features

- **Multiple Data Sources**: Retrieves information from a local JSON file and a simulated remote API
- **Asynchronous Operations**: Uses async/await to handle concurrent data retrieval with simulated delays
- **Error Handling**: Implements robust error handling for failed data fetches with logging
- **User Interface**: Provides a Streamlit-based web interface to interact with the RAG system

## Architecture

The RAG system consists of:

1. **Data Sources** (`src/data_sources.py`):
   - Local source: JSON file with documents
   - Remote API: Simulated API with random delays and occasional failures

2. **RAG System** (`src/rag.py`):
   - Retrieves relevant documents from multiple sources
   - Combines and ranks retrieved information
   - Generates responses based on context

3. **User Interface** (`app.py`):
   - Streamlit web app for user interaction
   - Displays responses, retrieved documents, and any errors

## Challenges Addressed

- **Data Retrieval Delays**: Simulated with random sleep times in async operations
- **Inconsistent Response Times**: Different sources have different delay characteristics
- **Integration Difficulties**: Demonstrates combining data from heterogeneous sources
- **Error Handling**: Graceful handling of network failures and data processing errors

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

This will start a web server. Open the provided URL in your browser to interact with the RAG system.

### Command Line Test
Run the test script to see the RAG system in action:
```bash
python test_rag.py
```

This will process several sample queries and display the results in the terminal.

## Simulated Challenges

- Random delays between 0.5-3 seconds for data retrieval
- 20% chance of API failure to simulate network issues
- Concurrent retrieval from multiple sources
- Error logging for debugging

This implementation provides a foundation for understanding RAG architectures and can be extended with real LLMs, vector databases, and production data sources.