# HH Job Assistant

An AI-assisted job search backend that searches vacancies on hh.ru, evaluates their relevance to a candidate, and generates personalized cover letters.

The project combines traditional vacancy filtering, semantic retrieval, BM25 ranking, LLM-based evaluation, PostgreSQL storage and caching, and a FastAPI REST API.

The main goal is to reduce the amount of expensive LLM processing by applying several inexpensive filtering and ranking stages before sending the most relevant vacancies to an LLM.

## Overview

The system helps a candidate find vacancies that match their resume, skills, and experience.

Instead of sending every vacancy directly to an LLM, the project uses a multi-stage matching pipeline:

```text
                         Resume
                            │
                            ▼
                    ┌───────────────┐
                    │ Resume        │
                    │ Analysis      │
                    │     LLM       │
                    └───────┬───────┘
                            │
                            ▼
                    Candidate Profile
                            │
                            ▼
┌──────────────┐    ┌─────────────────┐
│ HH.ru Filters│───▶│ Vacancy Search  │
└──────────────┘    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ PostgreSQL      │
                    │ Storage / Cache  │
                    └────────┬────────┘
                             │
                             ▼
                 ┌──────────────────────┐
                 │ Intermediate Matching│
                 │                      │
                 │ Embeddings + BM25    │
                 └──────────┬───────────┘
                            │
                            ▼
                       Ranked List
                            │
                          Top-N
                            │
                            ▼
                 ┌──────────────────────┐
                 │ LLM Vacancy          │
                 │ Evaluation           │
                 └──────────┬───────────┘
                            │
                            ▼
                   Suitable Vacancies
                            │
                            ▼
                 ┌──────────────────────┐
                 │ Cover Letter         │
                 │ Generation           │
                 └──────────────────────┘
```

The FastAPI layer exposes the application functionality through an HTTP API while keeping the core vacancy search, matching, database, and LLM logic separated from the API layer.

## Features

### HH.ru Vacancy Search

The backend searches vacancies on hh.ru using the site's filtering parameters.

Available filter definitions are obtained from hh.ru and stored in a unified JSON file:

```text
hh/hh_filters.json
```

This avoids hardcoding filter values and allows the search layer to work with the current hh.ru filter dictionaries.

Supported search parameters include:

* search text;
* geographic areas;
* experience;
* professional roles;
* industries;
* employment form;
* work format;
* working hours;
* work schedule;
* salary.

### Vacancy Description Parsing

Detailed vacancy information is retrieved when necessary.

Before making an additional request, the backend checks whether the vacancy is already stored in PostgreSQL.

If the vacancy exists in the database, the stored information is reused instead of requesting and parsing the vacancy again.

This provides a caching layer that reduces unnecessary requests to hh.ru.

### Resume Analysis

The candidate's resume is analyzed using an LLM before the matching stage.

The analysis extracts structured information such as:

* main technical skills;
* experience;
* relevant technologies;
* other information required for vacancy matching.

The structured candidate profile can then be reused across multiple vacancy evaluations instead of repeatedly sending the complete resume to the LLM.

This reduces processing time and LLM token consumption.

### Multi-Stage Vacancy Matching

The project combines several complementary approaches to rank vacancies.

#### Embedding-Based Matching

Text embeddings are used to estimate semantic similarity between the candidate profile and vacancy information.

This allows the system to identify conceptually similar skills and requirements even when different wording is used.

#### Custom BM25

The project contains a custom implementation of the BM25 ranking algorithm.

BM25 provides lexical matching between candidate information and vacancy text.

The two approaches complement each other:

```text
Embeddings → semantic similarity
BM25       → lexical similarity
```

The resulting scores are used during the intermediate filtering and ranking stage.

#### Candidate Ranking

Vacancies passing the intermediate matching stage are assigned matching scores and sorted.

Only the most promising `N` vacancies are passed to the more expensive LLM evaluation stage.

This reduces the number of LLM requests compared with evaluating every retrieved vacancy.

### LLM-Based Vacancy Evaluation

The highest-ranked vacancies are evaluated by an LLM.

The model performs a more detailed assessment using:

* structured candidate information;
* vacancy description;
* candidate skills;
* vacancy requirements.

The LLM stage acts as the final ranking and refinement layer after the cheaper retrieval methods.

```text
HH.ru filtering
      ↓
Embeddings + BM25
      ↓
Initial ranking
      ↓
Top-N vacancies
      ↓
LLM evaluation
      ↓
Suitable vacancies
```

### Cover Letter Generation

The project can generate a personalized cover letter for a suitable vacancy using the candidate profile and vacancy context.

Cover letter generation is performed after vacancy matching so that LLM resources are not spent on irrelevant vacancies.

### FastAPI REST API

The application exposes its functionality through a FastAPI-based REST API.

The API layer is separated from the underlying application logic and provides an HTTP interface for interacting with the job assistant.

FastAPI also provides automatic OpenAPI-based API documentation.

The API is implemented as a separate application layer:

```text
                  HTTP Client
                       │
                       ▼
              ┌─────────────────┐
              │    FastAPI API   │
              └────────┬────────┘
                       │
                       ▼
              ┌─────────────────┐
              │  JobAssistant    │
              │  Application     │
              └────────┬────────┘
                       │
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
    HH.ru Client   Matching        LLM
        │              │              │
        └──────────────┼──────────────┘
                       ▼
                  PostgreSQL
```

### PostgreSQL Storage and Caching

PostgreSQL is used to persist vacancy information and matching results.

The database allows the backend to reuse information that has already been obtained or calculated.

For example:

```text
Vacancy requested
       │
       ▼
Exists in database?
   │           │
  Yes          No
   │           │
   ▼           ▼
Load data    Parse vacancy
from DB         │
   │            ▼
   │         Save to DB
   │            │
   └──────┬─────┘
          ▼
    Matching stage
```

This is particularly useful for LLM-related processing because previously calculated information does not need to be generated again.

It helps reduce:

* redundant requests;
* network traffic;
* processing time;
* LLM token consumption.

### LLM Client

LLM interaction is isolated in a dedicated client.

The client handles API-level concerns independently from the application logic.

Implemented reliability mechanisms include:

* automatic delays between requests;
* retrying failed requests;
* exponential backoff;
* handling temporary `503 Service Unavailable` responses.

```text
LLM request
     │
     ├── success ───────────▶ result
     │
     └── error / 503
             │
             ▼
           wait
             │
             ▼
       retry request
             │
             └── exponential backoff
```

This keeps rate limiting and retry logic out of the higher-level application components.

## Architecture

The project is divided into several components with separate responsibilities:

```text
HH-Job-Assistant
│
├── api/
│   └── FastAPI REST API
│
├── application/
│   └── JobAssistant
│
├── hh/
│   ├── HH vacancy client
│   ├── search filters
│   └── hh.ru models
│
├── matching/
│   └── vacancy retrieval and ranking
│
├── llm/
│   ├── LLM client
│   ├── resume analysis
│   └── cover letter generation
│
└── database/
    ├── PostgreSQL connection
    ├── SQL queries
    └── repositories
```

The `JobAssistant` acts as the orchestration layer connecting the individual components.

The API layer is responsible for HTTP interaction, while the application layer contains the actual job-search workflow.

This separation makes the core functionality independent from the way it is accessed.

## Main Components

### `HHVacancyClient`

Responsible for:

* building hh.ru search parameters;
* applying generated filter definitions;
* performing vacancy searches;
* retrieving vacancy data;
* parsing vacancy information.

### `JobAssistant`

The main application orchestration component.

It coordinates:

* resume processing;
* vacancy search;
* vacancy retrieval;
* matching;
* LLM evaluation;
* cover letter generation;
* database interaction.

### `VacancyRetriever`

Responsible for the intermediate vacancy matching stage.

It combines:

* text embeddings;
* BM25;
* matching scores;
* candidate ranking.

### `ResumeAnalyzer`

Uses an LLM to convert an unstructured resume into structured candidate information that can be reused during vacancy matching.

### `CoverLetterGenerator`

Generates vacancy-specific cover letters using the candidate profile and vacancy information.

### Database Repositories

Repository classes encapsulate PostgreSQL operations and separate database access from application logic.

## Technologies

### Backend

* Python
* FastAPI
* Uvicorn
* Pydantic

### Database

* PostgreSQL
* psycopg
* psycopg_pool

### Vacancy Search

* hh.ru
* HTTP requests
* hh.ru filter dictionaries
* HTML parsing
* BeautifulSoup

### Matching

* Sentence Transformers
* Text embeddings
* BM25
* Custom ranking logic

### LLM

* Google Gemini API
* Structured resume analysis
* Vacancy evaluation
* Cover letter generation
* Request throttling
* Retry and exponential backoff

### Deployment

* Docker
* Docker Compose

## Project Structure

```text
HH-Job-Assistant/
│
├── api/                    # FastAPI application
│
├── application/            # Application / orchestration layer
│
├── database/               # PostgreSQL connection, queries and repositories
│
├── hh/                     # hh.ru client, filters and models
│
├── llm/                    # LLM client and LLM-powered components
│
├── matching/               # Vacancy matching and ranking
│
├── Dockerfile
├── compose.yaml
├── requirements.txt
├── main.py                 # Local application entry point
└── README.md
```

## Current Project Status

The main backend workflow is implemented and exposed through a FastAPI API.

Implemented:

* [x] HH.ru vacancy search
* [x] HH.ru filter extraction and unified JSON storage
* [x] Vacancy description parsing
* [x] PostgreSQL storage
* [x] Vacancy caching
* [x] Resume analysis using an LLM
* [x] Embedding-based matching
* [x] Custom BM25 matching
* [x] Intermediate vacancy ranking
* [x] LLM-based evaluation of top-ranked vacancies
* [x] Cover letter generation
* [x] LLM request throttling
* [x] Retry handling with exponential backoff
* [x] Handling of temporary `503` API errors
* [x] FastAPI REST API
* [x] Docker configuration
* [x] Docker Compose configuration

## Future Development

The core backend and API are currently the main focus of the project.

Potential future improvements include:

* persistent candidate profiles;
* search and matching statistics;
* improved ranking algorithms;
* more detailed matching explanations;
* vacancy and application history;
* automated interaction with hh.ru where technically and legally appropriate;
* a desktop client based on C++/Qt.

The Qt client is intentionally treated as a possible future client application rather than part of the current backend architecture.

## License

This project is intended primarily as a personal portfolio and experimental software project.
