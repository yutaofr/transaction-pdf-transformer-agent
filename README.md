# Transaction PDF Parser Agent

An AI-powered agent designed to extract bank transactions from PDF documents. It uses a multimodal LLM (via Ollama) to parse document images and extract structured transaction data, including bank names, account numbers, and specific transaction details.

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)
![Pydantic](https://img.shields.io/badge/Pydantic-E92063?style=for-the-badge&logo=pydantic&logoColor=white)
![Google](https://img.shields.io/badge/google-4285F4?style=for-the-badge&logo=google&logoColor=white)
![Ollama](https://img.shields.io/badge/Ollama-black?style=for-the-badge&logo=ollama&logoColor=white)
![Qwen](https://img.shields.io/badge/Qwen-FF6701?style=for-the-badge&logoColor=white)

## 🚀 Features

- **Multimodal Extraction**: Uses Vision LLMs (like `qwen3-vl:8b`) to "read" PDF pages converted to images.
- **Structured Output**: Extracted data is saved in a clean JSON format.
- **Smart Deduplication**: Automatically avoids importing duplicate transactions based on unique reference IDs.
- **French Banking Support**: Optimized for French account types like "Compte Titres" and "PEA".
- **Dockerized**: Easy to run in an isolated environment with all dependencies included.

## 🛠 Prerequisites

- **Python 3.11+**
- **Docker & Docker Compose**
- **Ollama**: Must be running with the `qwen3-vl:8b` model pulled.
  ```bash
  ollama pull qwen3-vl:8b
  ```

## 📥 Installation

1. **Clone the repository**:

   ```bash
   git clone <repository-url>
   cd transactions-pdf-parser
   ```

2. **Set up Python environment (optional if using Docker)**:
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

## 🏃 Usage

### Using Docker Compose (Recommended)

1. Place your bank transaction PDFs in the `data/` directory.
2. Run the agent:
   ```bash
   docker-compose up --build
   ```
3. The results will be saved to `results.json`.

### Running Locally

1. Ensure Ollama is reachable at `http://host.docker.internal:11434` or update the host in `agent.py`.
2. Run the main script:
   ```bash
   python main.py --dir ./data --output results.json
   ```

## 📊 Data Format

The agent extracts transactions into the following JSON structure:

```json
{
  "reference": "TX123456",
  "bank_name": "Example Bank",
  "account_number": "FR76...",
  "account_type": "compte titres",
  "date": "2023-10-27",
  "target": {
    "isin": "US0378331005",
    "name": "Apple Inc",
    "exchange": "NASDAQ"
  },
  "price": 175.5,
  "quantity": 10,
  "type": "Buy",
  "fees": 2.5,
  "taxes": 0.0,
  "is_pea": false
}
```

## 🧪 Testing

To verify the setup:

```bash
python verify_setup.py
```

Or run tests using pytest:

```bash
pytest
```
