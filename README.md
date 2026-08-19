# AI-Powered Research & Recommendation Agent

## Demo

**🎥 Video walkthrough:** [Watch the demo](https://drive.google.com/file/d/1cL8nXTfn6mMRC95HiaXUiBEJvo8Y-6TK/view?usp=sharing)


## Overview

AI-Powered Research & Recommendation Agent is a multi-agent AI application that automates company research and business analysis.

The user enters a company name, and the system automatically:

- Collects company information from the internet
- Analyzes the company
- Identifies business challenges
- Recommends AI opportunities
- Generates a personalized CEO pitch

The application reduces manual research effort and provides structured AI-driven insights. :contentReference[oaicite:0]{index=0}

---

## Architecture

The project follows a Multi-Agent Architecture where each agent performs a specific task. :contentReference[oaicite:1]{index=1}

### Agents

### Research Agent
- Collects company information from the internet

### Analysis Agent
- Generates company overview
- Extracts key business information

### Challenge Agent
- Identifies business challenges
- Detects operational and market risks

### Opportunity Agent
- Discovers AI opportunities
- Suggests practical AI implementations

### Pitch Agent
- Generates a personalized CEO pitch

---

## Workflow

1. User enters a company name.
2. Research Agent generates search queries.
3. Tavily API collects company information.
4. Research data is stored in ResearchContext.
5. Analysis Agent generates business insights.
6. Challenge Agent identifies business problems.
7. Opportunity Agent recommends AI solutions.
8. Pitch Agent creates a CEO recommendation.
9. Final report is displayed in Streamlit. :contentReference[oaicite:2]{index=2}

---

## Project Structure

```text
ai_research_agent/
│
├── agents/
│   ├── base_agent.py
│   ├── research_agent.py
│   ├── analysis_agent.py
│   ├── challenge_agent.py
│   ├── opportunity_agent.py
│   └── pitch_agent.py
│
├── core/
│   ├── context.py
│   └── orchestrator.py
│
├── services/
│   ├── tavily_service.py
│   └── groq_service.py
│
├── utils/
│
├── app.py
├── config.py
├── requirements.txt
└── README.md
```

---

## Technologies Used

- Python
- Streamlit
- Groq API
- Tavily Search API
- Llama 3.1 8B Instant

:contentReference[oaicite:3]{index=3}

---

## Installation

Clone the repository:

```bash
git clone <repository-url>
cd ai_research_agent
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate the environment:

### Windows

```bash
venv\Scripts\activate
```

### Linux / Mac

```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Environment Variables

Create a `.env` file and add:

```env
GROQ_API_KEY=your_groq_api_key
TAVILY_API_KEY=your_tavily_api_key
```

---

## Run the Application

```bash
streamlit run app.py
```

---

## Key Components

### ResearchContext

Acts as a shared memory object between agents.

Stores:

- Company Name
- Research Data
- Company Overview
- Key Information
- Challenges
- AI Opportunities
- CEO Pitch

:contentReference[oaicite:4]{index=4}

---

## Challenges Faced

### API Integration
Integrated multiple AI services with different SDKs and response formats.

### Configuration Management
Centralized API keys and model settings into a single configuration file.

### Error Handling
Implemented custom exception handling for improved reliability.

### Data Flow Management
Used a shared ResearchContext object to maintain agent communication.

### Token Optimization
Reduced prompt size and optimized search results to minimize token usage.

:contentReference[oaicite:5]{index=5}