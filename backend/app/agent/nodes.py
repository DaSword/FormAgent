from typing import Any, Dict, List, Optional
import json
from app.agent.state import AgentState, Document
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from app.core.config import settings
from google.cloud import storage
import pdfplumber
import io

# Initialize LLM
llm = ChatGoogleGenerativeAI(
    model=settings.LLM_MODEL, 
    api_key=settings.LLM_API_KEY,
    temperature=0
)

def download_blob_to_bytes(gcs_uri: str) -> bytes:
    """Downloads a blob from GCS to bytes."""
    try:
        storage_client = storage.Client()
        # Parse URI: gs://bucket-name/path/to/file
        if not gcs_uri.startswith("gs://"):
            raise ValueError(f"Invalid GCS URI: {gcs_uri}")
        
        parts = gcs_uri[5:].split("/", 1)
        bucket_name = parts[0]
        blob_name = parts[1]
        
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        return blob.download_as_bytes()
    except Exception as e:
        print(f"Error downloading {gcs_uri}: {e}")
        # Fallback for local testing/mocking if no creds
        return f"Mock content for {gcs_uri}".encode('utf-8')

def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """Extracts text from PDF bytes using pdfplumber."""
    try:
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text() or ""
            return text
    except Exception as e:
        print(f"Error extracting PDF: {e}")
        return str(pdf_bytes) # Fallback

def loader_node(state: AgentState) -> Dict[str, Any]:
    """Downloads files from GCS and extracts text."""
    file_uris = state.get("file_uris", [])
    documents: List[Document] = []
    
    print(f"--- Loading {len(file_uris)} files ---")
    
    for uri in file_uris:
        # Check if we already processed this URI (deduplication could happen here)
        # For now, we process all input URIs
        
        content_bytes = download_blob_to_bytes(uri)
        
        # Simple check for PDF based on extension or magic bytes could be added
        if uri.lower().endswith(".pdf"):
            text = extract_text_from_pdf(content_bytes)
        else:
            # Assume text for other types or mock
            text = content_bytes.decode('utf-8', errors='ignore')
            
        documents.append({"content": text, "source": uri, "metadata": {}})
        
    return {"documents": documents}

def extractor_node(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extracts structured data from a single document.
    Uses prompt chaining: Classify -> Extract.
    """
    doc = input_data["doc"]
    print(f"--- Extracting from {doc['source']} ---")
    
    # 1. Classify and Identify Fields
    # We ask the LLM to identify the document type and what fields *should* be extracted.
    # This makes it flexible for any doc type.
    
    classification_prompt = ChatPromptTemplate.from_template(
        """
        Analyze the following document text:
        {text}
        
        Identify the document type (e.g., Invoice, Contract, W-2, Bank Statement).
        Then, list the key fields that are typically found in this document type and should be extracted.
        Return JSON in this format:
        {{
            "doc_type": "string",
            "fields_to_extract": ["field1", "field2"]
        }}
        """
    )
    
    chain = classification_prompt | llm | JsonOutputParser()
    try:
        classification = chain.invoke({"text": doc["content"][:2000]}) # Truncate for classification speed
    except Exception as e:
        print(f"Classification failed: {e}")
        classification = {"doc_type": "Unknown", "fields_to_extract": []}
        
    # 2. Extract Specific Fields
    if classification["fields_to_extract"]:
        extraction_prompt = ChatPromptTemplate.from_template(
            """
            You are an expert data extractor.
            Document Type: {doc_type}
            Fields to Extract: {fields}
            
            Document Text:
            {text}
            
            Extract the specified fields from the document.
            Return a JSON object with the extracted key-value pairs.
            If a field is missing, set value to null.
            """
        )
        
        extract_chain = extraction_prompt | llm | JsonOutputParser()
        try:
            extracted_data = extract_chain.invoke({
                "doc_type": classification["doc_type"],
                "fields": classification["fields_to_extract"],
                "text": doc["content"]
            })
        except Exception as e:
            print(f"Extraction failed: {e}")
            extracted_data = {}
    else:
        extracted_data = {}
        
    # Add metadata
    result_record = {
        "source": doc["source"],
        "doc_type": classification["doc_type"],
        "data": extracted_data
    }
    
    return {"extracted_data": [result_record]}

def decision_node(state: AgentState) -> Dict[str, Any]:
    """Aggregates results and decides next step."""
    data = state.get("extracted_data", [])
    print(f"--- Aggregating {len(data)} records ---")
    
    # Define a simple "Master Schema" requirement for demonstration
    # In a real app, this might be dynamic based on the user's goal
    REQUIRED_DOCS = ["Invoice", "Contract"] 
    
    found_types = [item.get("doc_type") for item in data]
    missing_info = []
    
    # Check if we have at least one of each required type
    # This is a heuristic; real logic would be more complex (e.g. matching Invoice to Contract)
    if "Invoice" not in found_types:
        missing_info.append("Missing an Invoice document.")
    if "Contract" not in found_types:
        missing_info.append("Missing a Contract document.")
        
    if missing_info:
        return {"missing_info": missing_info, "decision": "REQUEST_MORE"}
    
    return {"decision": "FILL_PDF", "missing_info": []}

def fill_pdf_node(state: AgentState) -> Dict[str, Any]:
    print("--- Filling PDF ---")
    # TODO: PDF filling logic using pypdf or similar
    # For now, we just print the final data
    data = state.get("extracted_data", [])
    print(f"Final Data for PDF: {json.dumps(data, indent=2)}")
    return {}

def wait_node(state: AgentState) -> Dict[str, Any]:
    print("--- Waiting for User Input ---")
    # This node doesn't do much; it just acts as a pause point
    # The graph execution will stop here if we use an interrupt, 
    # or just return state that the API interprets as "needs input".
    return {}
