# zk-rag-wikipedia Plugin

A plugin for zk-rag that enables Wikipedia content lookup functionality.

## Description

This plugin provides a tool to search and retrieve content from Wikipedia articles. It can be used to enhance your RAG (Retrieval-Augmented Generation) applications with Wikipedia knowledge.

## Features

- Search Wikipedia articles
- Retrieve article summaries
- Handle disambiguation pages
- Comprehensive error handling

## Installation

```bash
pip install zk-rag-wikipedia
```

## Usage

The plugin will be automatically discovered by zk-rag when installed. It provides the `LookUpTopicOnWikipedia` tool which can be used to retrieve information about specific topics from Wikipedia.

Example usage through zk-rag:

```python
from zk_rag import get_tool

wikipedia_tool = get_tool("wikipedia")
result = wikipedia_tool.run("Python programming language")
print(result.title)  # The article title
print(result.content)  # The article summary
print(result.url)  # The Wikipedia URL
```

## Requirements

- Python >= 3.11
- mojentic
- wikipedia

## Local Development

To set up this project for local development:

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/zk-rag-wikipedia.git
   cd zk-rag-wikipedia
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows, use: .venv\Scripts\activate
   ```

3. Install development dependencies:
   ```bash
   pip install -r requirements.txt
   pip install -r dev-requirements.txt
   ```

4. Install the package in editable mode:
   ```bash
   pip install -e .
   ```

## Building Locally

To build the package locally:

1. Ensure you have the build dependencies:
   ```bash
   pip install build
   ```

2. Build the package:
   ```bash
   python -m build
   ```

This will create both wheel and source distribution in the `dist/` directory.

## Running Tests

To run the tests:
```bash
pytest
```

## License

MIT License

## Author

Stacey Vetzal (stacey@vetzal.com)
