# WBS BPKH - System Architecture

## Overview

WBS BPKH uses a modular, layered architecture designed for scalability and maintainability.

## Directory Structure

```
wbs-bpkh-2026/
├── src/                          # Main source code
│   ├── config/                   # Configuration & constants
│   │   ├── settings.py          # Environment-based settings
│   │   └── constants.py         # Enums & constants
│   │
│   ├── models/                   # Data models (dataclasses)
│   │   ├── report.py            # Report model
│   │   ├── user.py              # User model
│   │   └── message.py           # Message/Conversation models
│   │
│   ├── database/                 # Data access layer
│   │   ├── base.py              # Abstract database interface
│   │   ├── sqlite.py            # SQLite implementation
│   │   ├── supabase.py          # Supabase implementation
│   │   ├── factory.py           # Database factory
│   │   └── repositories.py      # Repository pattern classes
│   │
│   ├── services/                 # Business logic layer
│   │   ├── auth.py              # Authentication service
│   │   ├── report_service.py    # Report operations
│   │   └── notification.py      # Email/WhatsApp notifications
│   │
│   ├── agents/                   # AI Agents
│   │   ├── base.py              # Base agent class
│   │   ├── classifier.py        # Classification agent
│   │   ├── validator.py         # Validation agent
│   │   ├── summarizer.py        # Summary generation
│   │   ├── chatbot.py           # Chatbot agent
│   │   └── pipeline.py          # Agent orchestration
│   │
│   ├── integrations/             # External integrations
│   │   └── waha.py              # WhatsApp/WAHA integration
│   │
│   ├── ui/                       # UI components
│   │   ├── styles.py            # CSS styles
│   │   ├── themes.py            # Theme configuration
│   │   └── components.py        # Reusable UI components
│   │
│   └── portals/                  # Streamlit page modules
│       ├── home.py              # Landing page
│       ├── reporter.py          # Reporter portal
│       └── manager.py           # Manager portal
│
├── api/                          # REST API
│   └── server.py                # FastAPI server
│
├── tests/                        # Test suite
│   ├── test_database.py
│   ├── test_agents.py
│   └── test_services.py
│
├── scripts/                      # Utility scripts
│   ├── run_app.py
│   ├── run_api.py
│   └── run_tests.py
│
├── docs/                         # Documentation
│
├── app.py                        # Main Streamlit entry point
├── app_reporter.py               # Legacy reporter (backward compat)
├── app_manager.py                # Legacy manager (backward compat)
└── requirements.txt
```

## Architecture Layers

### 1. Configuration Layer (`src/config/`)

Centralized configuration management:
- Environment-based settings via `Settings` class
- Type-safe constants using Python Enums
- Single source of truth for all config values

### 2. Models Layer (`src/models/`)

Data structures using Python dataclasses:
- Immutable data transfer objects
- Validation logic embedded in models
- Serialization/deserialization methods

### 3. Database Layer (`src/database/`)

Repository pattern with database abstraction:
- `DatabaseInterface`: Abstract contract for all databases
- `SQLiteDatabase`: Local SQLite implementation
- `SupabaseDatabase`: Cloud Supabase implementation
- `DatabaseFactory`: Automatic selection based on config
- `Repository` classes: High-level data access with model conversion

### 4. Services Layer (`src/services/`)

Business logic isolated from UI:
- `AuthService`: Authentication for reporters and managers
- `ReportService`: Report lifecycle management
- `NotificationService`: Multi-channel notifications

### 5. Agents Layer (`src/agents/`)

AI-powered processing:
- `BaseAgent`: Abstract base with common functionality
- `ClassifierAgent`: Categorization and severity detection
- `ValidatorAgent`: Report completeness validation
- `SummarizerAgent`: Executive summary generation
- `ChatbotAgent`: Conversational AI assistant
- `AgentPipeline`: Orchestrates multiple agents

### 6. UI Layer (`src/ui/`)

Presentation components:
- `styles.py`: Complete CSS styling
- `themes.py`: Theme configuration
- `components.py`: Reusable HTML components

### 7. Portals Layer (`src/portals/`)

Streamlit page modules:
- `home.py`: Landing page with portal selection
- `reporter.py`: Reporter interface
- `manager.py`: Manager dashboard

## Design Patterns

### Repository Pattern
Separates data access from business logic. Each entity has a repository class that handles CRUD operations.

### Factory Pattern
`DatabaseFactory` creates the appropriate database instance based on configuration.

### Strategy Pattern
Database implementations (`SQLiteDatabase`, `SupabaseDatabase`) are interchangeable strategies.

### Singleton Pattern
Settings and database connections use cached singletons for efficiency.

### Pipeline Pattern
`AgentPipeline` chains multiple agents for comprehensive report processing.

## Key Features

### Database Flexibility
Switch between SQLite (development) and Supabase (production) by changing `DB_MODE` environment variable.

### AI Processing
Reports are automatically classified, validated, and summarized using keyword-based AI agents.

### Multi-Channel
Supports web portal, WhatsApp (via WAHA), and email notifications.

### Scalability
Modular design allows adding new features without affecting existing code.

## Configuration

All settings are loaded from environment variables:

```env
# Database
DB_MODE=supabase        # sqlite or supabase
SUPABASE_URL=https://...
SUPABASE_ANON_KEY=eyJ...

# WhatsApp
WAHA_ENABLED=true
WAHA_API_URL=http://localhost:3000

# Email
EMAIL_ENABLED=true
SMTP_HOST=smtp.gmail.com
```

## Running the Application

```bash
# Streamlit UI
streamlit run app.py

# API Server
python scripts/run_api.py

# Tests
python scripts/run_tests.py
```
