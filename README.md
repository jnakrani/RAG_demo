# FastAPI RAG Service with RBAC

A sophisticated FastAPI microservice that combines AI-powered document processing with secure user management and role-based access control (RBAC). This service provides a robust Question-Answering system over documents with fine-grained access control.

## Features

- 🔐 JWT-based Authentication & Authorization
- 👥 User Profile Management (CRUD operations)
- 🔑 Dynamic Role-Based Access Control (RBAC) using Oso
- 🧪 Comprehensive Test Coverage
- 📚 API Documentation (Swagger UI)

- 👥 **User Management**
  - User registration and authentication
  - Profile management (CRUD operations)
  - Role assignment and management
  - Admin and regular user roles

- 📄 **Document Management & RAG Pipeline**
  - PDF document upload and processing
  - Document chunking and vectorization
  - ChromaDB vector storage integration
  - Secure document access control
  - Document deletion and collection management

- 🤖 **Question Answering System**
  - Context-aware question answering
  - Document-based response generation
  - Answer processing and formatting
  - QA history tracking

- 📝 **Logging and Monitoring**
  - Comprehensive application logging
  - Error tracking and debugging
  - Performance monitoring
  - Audit trail for security events

## Project Structure

```
RAG_demo/
├── authorization/           # Authorization and RBAC
│   ├── auth.py            # Authentication logic
│   └── policy.polar       # Oso policy definitions
├── chroma_db/             # Vector database storage
│   └── chroma.sqlite3     # ChromaDB database
├── controler/             # Business logic controllers
│   └── chromadb_controler.py  # ChromaDB operations
├── logs/                  # Application logs
│   └── app.log           # Log file
├── routes/               # API endpoints
│   ├── chroma_routes.py  # Document management routes
│   ├── role_routes.py    # Role management routes
│   ├── user_routes.py    # User management routes
│   ├── qa_routes.py      # Question answering routes
│   └── general.py        # General utility routes
├── tests/                # Test suite
│   └── test_user_routes.py  # User route tests
├── utils/                # Utility functions
│   ├── logging_utils.py  # Logging configuration
│   ├── auth_utils.py     # Authentication utilities
│   ├── utils.py         # General utilities
│   ├── request_payload.py # Request models
│   ├── user_curd.py     # User CRUD operations
│   └── llm_setup.py     # LLM configuration
├── main.py              # Application entry point
└── user_model.py        # Database models
```

## API Endpoints

### Authentication
- `POST /users/register` - Register new user
- `POST /users/token` - Login and get JWT token

### User Management
- `GET /users/me` - Get current user profile
- `PUT /users/me` - Update current user profile
- `DELETE /users/me` - Delete current user
- `GET /users/` - List all users (Admin only)
- `GET /users/{user_id}` - Get user by ID (Admin or self only)

### Role Management
- `GET /roles/` - List all roles (Admin only)
- `POST /roles/` - Create new role (Admin only)
- `DELETE /roles/{role_id}` - Delete role (Admin only)
- `POST /roles/assign/{user_id}/{role_id}` - Assign role to user (Admin only)
- `DELETE /roles/remove/{user_id}/{role_id}` - Remove role from user (Admin only)

### Document Management
- `GET /documents/` - List all documents
- `POST /documents/upload` - Upload PDF document
- `DELETE /documents/{document_id}` - Delete document
- `DELETE /documents/clear` - Clear all documents

### Question Answering
- `POST /qa/ask` - Ask question about documents
- `GET /qa/history` - Get QA history

## Role-Based Access Control

### Default Roles
1. **Admin Role**
   - Full access to all endpoints
   - Can manage roles and users
   - Can read, write, and delete documents
   - Can manage system configuration

2. **User Role**
   - Can read and write documents
   - Can access QA functionality
   - Can manage own profile
   - Limited to own resource access

### Permission Structure
```
# Document Permissions
- read: View documents and ask questions
- write: Upload new documents
- delete: Remove documents (admin only)

# Role Permissions
- manage_roles: Create, delete, assign roles
- read: View role information

# User Permissions
- manage_users: Manage user accounts
- read: View user information
```

## Setup and Installation

1. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
# Create .env file with:
SECRET_KEY=your_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DATABASE_URL=sqlite:///./app.db
```

4. Initialize the database:
```bash
# The application will automatically create tables on first run
```

5. Start the server:
```bash
uvicorn main:app --reload
```

## Development

### Testing Strategy

The application includes comprehensive test suites for all major components:

#### 1. User Management Tests (`test_user_routes.py`)
```python
# Authentication Tests
- test_create_user()              # Test user registration
- test_create_user_duplicate_email() # Test duplicate email handling
- test_login_user()              # Test user login and token generation
- test_read_users_me()           # Test profile retrieval
- test_update_user()             # Test profile updates
- test_delete_user()             # Test account deletion
```

#### 2. Role Management Tests (`test_role_routes.py`)
```python
# Role Management Tests
- test_create_role_admin()       # Test role creation by admin
- test_create_role_unauthorized() # Test unauthorized role creation
- test_list_roles_admin()        # Test role listing
- test_list_roles_unauthorized() # Test unauthorized access
- test_delete_role_admin()       # Test role deletion
- test_assign_role_admin()       # Test role assignment
- test_remove_role_admin()       # Test role removal
- test_cannot_delete_admin_role() # Test admin role protection
```

#### 3. Document Management Tests (`test_chroma_routes.py`)
```python
# Document Management Tests
- test_list_documents_user()     # Test document listing
- test_list_documents_admin()    # Test admin document access
- test_upload_document_user()    # Test document upload
- test_upload_invalid_file()     # Test file validation
- test_delete_document_admin()   # Test document deletion
- test_clear_collection_admin()  # Test collection clearing
```

#### 4. Question Answering Tests (`test_qa_routes.py`)
```python
# QA System Tests
- test_ask_question_user()       # Test QA functionality
- test_ask_question_admin()      # Test admin QA access
- test_ask_question_unauthorized() # Test unauthorized access
- test_ask_question_no_documents() # Test empty collection
- test_get_qa_history_user()     # Test history retrieval
```

### Test Coverage

The test suite covers:
- ✅ Authentication & Authorization
- ✅ CRUD Operations
- ✅ Permission Validation
- ✅ Error Handling
- ✅ File Operations
- ✅ QA Functionality
- ✅ Edge Cases

### Running Tests

1. Run all tests:
```bash
pytest tests/
```

2. Run specific test files:
```bash
pytest tests/test_user_routes.py
pytest tests/test_role_routes.py
pytest tests/test_chroma_routes.py
pytest tests/test_qa_routes.py
```

3. Run with verbose output:
```bash
pytest -v tests/
```

4. Run with coverage report:
```bash
pytest --cov=. tests/
```

### Test Database

Tests use a separate SQLite database:
```python
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
```

### Test Fixtures

Common fixtures include:
```python
@pytest.fixture
def client():
    # Setup test client with fresh database

@pytest.fixture
def admin_token(client):
    # Create and authenticate admin user

@pytest.fixture
def user_token(client):
    # Create and authenticate regular user

@pytest.fixture
def sample_pdf():
    # Create test PDF document

@pytest.fixture
def uploaded_document(client, admin_token, sample_pdf):
    # Upload test document
```

### Logging
- Logs are stored in `logs/app.log`
- Log level can be configured in `utils/logging_utils.py`

### Security Considerations
- JWT tokens for authentication
- Bcrypt password hashing
- Role-based access control
- Input validation
- SQL injection protection
- CORS middleware

## Dependencies

- FastAPI: Web framework
- SQLAlchemy: Database ORM
- ChromaDB: Vector database
- LangChain: LLM integration
- Oso: RBAC implementation
- PyJWT: JWT token handling
- Bcrypt: Password hashing
- Pytest: Testing framework

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License.