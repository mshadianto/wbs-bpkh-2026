# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

WBS BPKH is an AI-powered whistleblowing system for Badan Pengelola Keuangan Haji (Indonesian Hajj Financial Management Agency). It uses a multi-agent AI architecture to process whistleblowing reports, classify violations, route to appropriate units, and ensure regulatory compliance.

## Commands

### Run the Application
```bash
# Windows
python -m streamlit run app.py

# Or use the batch script
run.bat

# Linux/Mac
streamlit run app.py
# Or
./run.sh
```

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Environment Setup
Copy `.env.example` to `.env` and add your Groq API key:
```
GROQ_API_KEY=gsk_your_groq_api_key_here
```

## Architecture

### Multi-Agent System (`agents.py`)

The system uses 6 specialized AI agents coordinated by an orchestrator:

1. **IntakeAgent** - Validates report completeness (4W+1H: What, Who, When, Where, How), generates report IDs, calculates completeness scores
2. **ClassificationAgent** - Classifies violations into 9 types (V001-V009), determines severity (Critical/High/Medium/Low), extracts entities
3. **RoutingAgent** - Routes to appropriate unit (SPI, Unit Kepatuhan, Biro Hukum, Unit SDM, Komite Audit), manages escalation and SLA deadlines
4. **InvestigationAgent** - Creates investigation plans, identifies evidence requirements and witnesses
5. **ComplianceAgent** - Checks regulatory compliance, calculates compliance scores, generates recommendations
6. **OrchestratorAgent** - Coordinates all agents in sequence: Intake → Classification → Routing → Investigation → Compliance

All agents inherit from `AgentBase` which provides:
- Groq LLM integration via `_call_llm()`
- JSON extraction from LLM responses via `_extract_json()`
- Fallback responses when API unavailable

### Knowledge Base (`knowledge_base.py`)

RAG knowledge base with 29 knowledge chunks organized into categories:
- Definisi (1 chunk)
- Jenis Pelanggaran (9 chunks - violation types)
- Severity Assessment (4 chunks)
- Unit Routing (5 chunks)
- Investigation (4 chunks)
- Compliance (3 chunks)
- Reporting/Analytics (3 chunks)

Search uses keyword matching with relevance scoring, filterable by category.

### Configuration (`config.py`)

Contains:
- `VIOLATION_TYPES` - 9 violation types with codes (V001-V009), legal basis, severity, and keywords
- `SEVERITY_LEVELS` - Priority (P1-P4), SLA hours (4/24/48/72), escalation paths
- `ROUTING_UNITS` - Mapping of violation types to responsible units
- `AGENT_PROMPTS` - System prompts for each AI agent
- `PERFORMANCE_METRICS` - Target thresholds

### Database (`database.py`)

SQLite database (`wbs_database.db`) with tables:
- `reports` - Main report data including classification, routing, scores
- `investigations` - Investigation plans linked to reports
- `compliance_history` - Compliance check records
- `analytics` - Aggregated metrics

Key methods: `insert_report()`, `get_statistics()`, `search_reports()`, `export_to_csv()`

### Frontend (`app.py`)

Streamlit application with pages:
- Home & Submit Report - Report submission form with 4W+1H fields
- Dashboard & Analytics - Statistics, charts, KPIs
- Report Database - Search, filter, view reports
- Knowledge Base - Browse and search KB chunks
- Settings & About - API configuration, documentation

## Key Implementation Details

- AI processing uses Groq API with `llama-3.3-70b-versatile` model (configurable)
- Without API key, system falls back to rule-based processing using keyword matching
- Report IDs format: `WBS-YYYY-HHMMSS`
- Compliance score calculated from: completeness (25%), classification accuracy (25%), routing correctness (25%), documentation (25%)
- SLA tracking: Critical=4hrs, High=24hrs, Medium=48hrs, Low=72hrs

## Indonesian Language Context

Reports and UI are primarily in Indonesian (Bahasa Indonesia). Key terms:
- "Pelanggaran" = Violation
- "Korupsi" = Corruption
- "Gratifikasi" = Gratuity/Bribery
- "Penggelapan" = Embezzlement
- "Pelapor" = Reporter/Whistleblower
- "Terlapor" = Reported person
