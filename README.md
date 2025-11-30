# Doc Extractor Agent

A system designed to extract and synthesize structured information from multiple documents (PDFs, Images) using **LangGraph** and **Google Gemini**.

## Project Overview

The system allows users to upload multiple documents (e.g., Invoices, Contracts), which are then processed in parallel by a backend agent. The agent identifies document types, extracts relevant fields, and aggregates the data to fill a target form or identify missing information.

### Key Features
*   **Multi-File Upload**: Upload multiple documents simultaneously to Google Cloud Storage (GCS).
*   **Real-Time Status**: Track the extraction process (Uploading -> Processing -> Complete).
*   **Orchestrator-Worker Pattern**: The backend uses a Map-Reduce approach to process documents concurrently.
*   **Human-in-the-Loop**: If information is missing, the agent requests additional documents.

## Tech Stack

*   **Frontend**: [Next.js 14](https://nextjs.org/) (App Router)
*   **Backend**: [FastAPI](https://fastapi.tiangolo.com/)
*   **Graph Orchestration**: [LangGraph](https://langchain.com/docs/integrations/langgraph)
*   **Language**: TypeScript
*   **Styling**: Tailwind CSS
*   **UI Components**: [shadcn/ui](https://ui.shadcn.com/) (Radix UI + Tailwind)
*   **Icons**: Lucide React

## Getting Started

### Prerequisites
*   Node.js 18+
*   Python 3.12+
*   Backend API running (usually on port 8000)

### Installation

1.  Install dependencies:
    ```bash
    npm install
    ```

2.  Configure Environment:
    Create a `.env.local` file:
    ```env
    NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
    ```

3.  Run Development Server:
    ```bash
    npm run dev
    ```

    Open [http://localhost:3000](http://localhost:3000) with your browser.

    ### Running the Backend (Local)

To run the backend locally with Docker:

1.  Navigate to the backend directory:
    ```bash
    cd ../backend
    ```

2.  Install Python dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3.  Set Environment Variables:
    Create a `.env` file in `backend/` or export them:
    ```bash
    export GOOGLE_API_KEY="your-gemini-api-key"
    export GOOGLE_APPLICATION_CREDENTIALS="path/to/gcp-creds.json"
    ```

4.  Start the FastAPI server:
    ```bash
    uvicorn app.api.main:app --reload --port 8000
    ```

## Docker Support

The application is containerized using a multi-stage Dockerfile optimized for production (standalone output).

```bash
# Build and Run with Docker Compose (Full Stack)
docker-compose up --build
```
