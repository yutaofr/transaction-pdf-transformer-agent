import io
import json
import base64
from typing import List, Optional
from pydantic import BaseModel, Field, PrivateAttr
import ollama
from google.adk.agents import Agent
from utils import pdf_to_images

class TransactionTarget(BaseModel):
    isin: Optional[str] = Field(None, description="ISIN code")
    name: Optional[str] = Field(None, description="Name of the security/asset")
    exchange: Optional[str] = Field(None, description="Exchange name")

class Transaction(BaseModel):
    reference: str = Field(..., description="Unique transaction reference ID")
    bank_name: str = Field(..., description="Name of the bank")
    account_number: str = Field(..., description="Bank account number")
    account_type: str = Field(..., description="Type of the account (e.g., 'compte titres')")
    date: str = Field(..., description="Date of the transaction")
    target: TransactionTarget = Field(..., description="Details of the target asset")
    price: float = Field(..., description="Execution price")
    quantity: float = Field(..., description="Quantity traded")
    type: str = Field(..., description="Buy or Sell")
    fees: float = Field(0.0, description="Transaction fees")
    taxes: float = Field(0.0, description="Taxes applied")
    is_pea: bool = Field(False, description="Whether the account is a PEA (Plan Épargne Actions)")

class TransactionParserAgent(Agent):
    """
    An agent that uses the google-adk structure to parse bank transactions from PDFs 
    using a multimodal model via Ollama.
    """
    name: str = "PDFTransactionParser"
    model_name: str = "qwen3-vl:8b"
    host: str = "http://host.docker.internal:11434"
    _client: ollama.Client = PrivateAttr()

    def __init__(self, **data):
        super().__init__(**data)
        self._client = ollama.Client(host=self.host)

    def _img_to_base64(self, img):
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode('utf-8')

    def run(self, pdf_path: str) -> List[dict]:
        """
        Main execution method for the agent to parse a PDF.
        """
        images = pdf_to_images(pdf_path)
        all_transactions = []
        
        prompt = """
        Extract ALL transaction data from this document image. 
        Identify the bank name, account number, and account type first. 
        Note: The account type is likely 'compte titres' or 'compte PEA'.
        If the account type is 'Compte PEA' or mentions 'Plan Epargne Action', set is_pea to true.
        
        For each transaction row, extract:
        - Transaction Reference ID (Unique identifier for the operation)
        - Date
        - Target Asset (Name, ISIN, Exchange if available)
        - Price
        - Quantity
        - Transaction Type (Buy or Sell)
        - Fees and Taxes
        - is_pea (boolean, true if it's a PEA account)

        Output MUST be a JSON object with a 'transactions' key containing a list of objects.
        Fields for each transaction:
        - reference (string)
        - bank_name (string)
        - account_number (string)
        - account_type (string, e.g., 'compte titres' or 'compte PEA')
        - date (string)
        - target: { isin: string, name: string, exchange: string }
        - price (number)
        - quantity (number)
        - type (string: "Buy" or "Sell")
        - fees (number)
        - taxes (number)
        - is_pea (boolean)

        If information is missing, use null or 0.0 for numbers.
        Return ONLY valid JSON.
        """

        for i, img in enumerate(images):
            print(f"Agent: Processing page {i+1} of {pdf_path} using {self.model_name}...")
            img_b64 = self._img_to_base64(img)
            
            try:
                response = self._client.generate(
                    model=self.model_name,
                    prompt=prompt,
                    images=[img_b64],
                    stream=False
                )
                
                content = response.get("response", "").strip()
                if not content:
                    print(f"Agent: Received empty response from Ollama on page {i+1}")
                    continue
                
                # Extract JSON from potential markdown tags or finding the first { and last }
                json_content = content
                if "```json" in content:
                    json_content = content.split("```json")[1].split("```")[0].strip()
                elif "```" in content:
                    json_content = content.split("```")[1].split("```")[0].strip()
                else:
                    # Try to find the first '{' or '[' and the last '}' or ']'
                    start_idx = min(content.find('{') if '{' in content else len(content), 
                                    content.find('[') if '[' in content else len(content))
                    end_idx = max(content.rfind('}') if '}' in content else -1, 
                                  content.rfind(']') if ']' in content else -1)
                    if start_idx < end_idx:
                        json_content = content[start_idx:end_idx+1]

                try:
                    data = json.loads(json_content)
                    print(f"Agent: Raw data extracted: {json.dumps(data, indent=2)[:500]}...")
                    
                    if isinstance(data, list):
                        new_txs = data
                    elif isinstance(data, dict):
                        new_txs = data.get("transactions", [data])
                    else:
                        new_txs = []

                    # Ensure is_pea is explicitly handled if missing
                    for tx in new_txs:
                        if "is_pea" not in tx:
                            # Heuristic if model missed it but account_type says PEA
                            acc_type = str(tx.get("account_type", "")).lower()
                            tx["is_pea"] = "pea" in acc_type or "plan epargne action" in acc_type
                        
                    all_transactions.extend(new_txs)
                    print(f"Agent: Successfully extracted {len(new_txs)} transactions from page {i+1}.")
                except json.JSONDecodeError as je:
                    print(f"Agent: Failed to parse JSON on page {i+1}: {je}")
                    print(f"Agent: Raw content snippet: {content[:100]}...")
            except Exception as e:
                print(f"Agent: Error on page {i+1}: {e}")
                
        return all_transactions
