# PDF Question-Answering System

A FastAPI-based application that provides PDF document management and question-answering capabilities using ChromaDB and LangChain.

## Features

- PDF document upload and processing
- Document chunking and vector storage
- Natural language question answering
- Document management (list, delete, clear)
- Token usage tracking
- Comprehensive logging

## Prerequisites

- Python 3.8+
- OpenAI API key

## Installation

1. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory:
```env
OPENAI_API_KEY=your_openai_api_key_here
DATABASE_URL=postgresql://user:password@localhost:5432/your_database_name
```

4. Initialize and run Alembic migrations:
```bash
alembic init alembic

alembic revision --autogenerate -m "initial tables"

alembic upgrade head
```

## Running the Application

1. Start the FastAPI server:
```bash
uvicorn main:app --reload
```

2. Access the API documentation:
- Swagger UI: `http://localhost:8000/docs`

## API Endpoints

### Document Management

- `GET /` - Root endpoint, API status
- `GET /list_documents` - List all stored documents
- `POST /upload_pdf` - Upload and process PDF file
- `DELETE /delete_documents` - Delete specific document
- `DELETE /clear_collection` - Clear all documents

### Question Answering

- `POST /question_answer` - Ask questions about stored documents

## Usage Examples

#### Upload a PDF

```bash
curl -X POST -F "file=@example.pdf" http://localhost:8000/upload_pdf
```

#### Ask a Question

```bash
curl -X POST "http://localhost:8000/question_answer?query=your question here"
```

#### List Documents

```bash
curl http://localhost:8000/list_documents
```

## Logging

The application logs are stored in `qa_system.log` file with the following details:
- All API requests and responses
- Error messages and stack traces
- Document processing status
- System operations

Example log entries:
```log
2024-02-14 10:00:00 - main - INFO - PDF processed successfully, 5 chunks stored
2024-02-14 10:01:15 - main - INFO - Successfully retrieved 3 documents
2024-02-14 10:02:30 - main - ERROR - Error processing PDF: File not found
```

## Role-Based Access Control (RBAC)

The application implements RBAC using the Oso framework. There are two main roles:

- **User**: Can read documents, upload PDFs, and query the system
- **Admin**: Has full access to all features including document deletion and role management

### Authentication

To access protected endpoints, you need to:

1. Obtain a JWT token:
```bash
curl -X POST "http://localhost:8000/token" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=your_email&password=your_password"
```

2. Use the token in subsequent requests:
```bash
curl -X GET "http://localhost:8000/list_documents" \
     -H "Authorization: Bearer your_token_here"
```

### Permissions

- Document Reading: All authenticated users
- Document Upload: All authenticated users
- Question Answering: All authenticated users
- Document Deletion: Admin only
- Collection Management: Admin only

## Acknowledgments

- OpenAI for GPT and embedding models
- LangChain for document processing
- ChromaDB for vector storage
- FastAPI for the web framework