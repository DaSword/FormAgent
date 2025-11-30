from typing import TypedDict, List, Dict, Any, Annotated
import operator

class Document(TypedDict):
    content: str
    source: str
    metadata: Dict[str, Any]

class AgentState(TypedDict):
    # GCS URIs of uploaded files (input)
    file_uris: List[str]
    
    # Processed documents (text extracted)
    documents: List[Document]
    
    # Aggregated extracted data (reducer output)
    # operator.add allows parallel branches to append to this list
    extracted_data: Annotated[List[dict], operator.add]
    
    # Missing info list
    missing_info: List[str]
    
    # Final decision: 'FILL_PDF' or 'REQUEST_MORE'
    decision: str
