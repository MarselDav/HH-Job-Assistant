# HH Job Assistant

An AI-assisted job search backend that analyzes vacancies from **hh.ru** and evaluates their relevance to a candidate using a multi-stage matching pipeline.

The project combines traditional vacancy filtering, semantic search, BM25 ranking and LLM-based evaluation. PostgreSQL is used to cache vacancy data and previously computed results, reducing redundant network requests and LLM token consumption.

The current implementation is a **fully functional Python backend**. A FastAPI service and a Qt desktop application are planned as the next development stages.

## Overview

The system is designed to help a candidate find the most relevant vacancies on hh.ru based on their resume, skills and experience.

Instead of sending every vacancy directly to an LLM, the project uses several filtering and ranking stages:

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
                  Candidate profile
                            │
                            ▼
┌──────────────┐    ┌─────────────────┐
│ HH.ru Filters│───▶│ Vacancy Search  │
└──────────────┘    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ PostgreSQL      │
                    │ Cache / Storage  │
                    └────────┬────────┘
                             │
                             ▼
                 ┌──────────────────────┐
                 │ Intermediate Matching │
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

This architecture allows expensive LLM processing to be applied only to the most promising vacancies.

## Current Features

### HH.ru Vacancy Search

The backend can search vacancies on hh.ru using the site's own filtering parameters.

The available filter definitions are obtained from hh.ru and stored in a unified JSON file:

```text
hh_filters.json
```

This avoids hardcoding the available filter values and allows the search layer to work with the current hh.ru filter dictionaries.

The search layer supports parameters such as:

* search text;
* geographic areas;
* experience;
* professional roles;
* industries;
* employment form;
* work format;
* working hours;
* work schedule;
* salary;

### Vacancy Description Parsing

After the initial vacancy search, detailed vacancy information is retrieved when necessary.

Before making an additional request, the backend checks whether the vacancy is already stored in PostgreSQL.

If the vacancy is already available in the database, the stored data is reused.

This provides a caching layer that reduces unnecessary requests to hh.ru.

## Resume Analysis

The candidate's resume is analyzed using an LLM before the matching stage.

The analysis extracts relevant information from the resume, including the candidate's main skills and other information required for vacancy matching.

The resulting structured candidate information can then be reused across multiple vacancy evaluations instead of repeatedly sending the complete resume to the LLM.

This reduces both processing time and token consumption.

## Multi-Stage Vacancy Matching

The project uses several complementary approaches to estimate how well a vacancy matches the candidate.

### Embedding-Based Matching

Embeddings are used to estimate semantic similarity between the candidate profile and vacancy information.

This allows the system to identify conceptually similar skills and requirements even when the wording differs.

### Custom BM25

The project also contains a custom implementation of the **BM25** ranking algorithm.

BM25 provides lexical matching between the candidate's information and vacancy text.

Using BM25 together with embeddings combines two different types of similarity:

```text
Embeddings → semantic similarity
BM25       → lexical similarity
```

The resulting scores are used during the intermediate filtering and ranking stage.

### Candidate Ranking

Vacancies passing the intermediate filtering stage are assigned matching scores and sorted.

Only the most promising `N` vacancies continue to the more expensive LLM evaluation stage.

This significantly reduces the number of LLM requests compared with evaluating every retrieved vacancy.

## LLM-Based Vacancy Evaluation

The highest-ranked vacancies are evaluated by an LLM.

At this stage the model performs a more detailed assessment of the candidate-vacancy match using the information extracted from the resume and the vacancy description.

The LLM-based stage acts as a final ranking/refinement layer after the cheaper retrieval methods.

Conceptually:

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
Final suitable vacancies
```

## PostgreSQL Storage and Caching

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
   └─────┬──────┘
         ▼
    Matching stage
```

This approach is particularly useful for LLM-related processing because previously calculated information does not need to be generated again.

It helps reduce:

* redundant requests;
* network traffic;
* processing time;
* LLM token consumption.

## LLM Client

LLM interaction is isolated in a dedicated client class.

The client handles API-level concerns independently from the application logic.

Implemented reliability mechanisms include:

* automatic delays between requests;
* retrying failed requests;
* exponential backoff;
* handling temporary `503 Service Unavailable` responses.

The retry strategy can be represented as:

```text
LLM request
    │
    ├── success ───────────────▶ result
    │
    └── 503/error
            │
            ▼
       wait
            │
            ▼
       retry request
            │
            └── exponential backoff
```

This prevents the rest of the application from having to implement request throttling and retry logic independently.

## Cover Letter Generation

The backend also includes LLM-based cover letter generation for suitable vacancies.

The generated cover letter can use the candidate's information together with the specific vacancy context.

The generation stage is deliberately placed after vacancy matching so that LLM resources are not spent generating cover letters for irrelevant vacancies.

## Architecture

The current backend is organized around separate components with different responsibilities.

Conceptually:

```text
                    JobAssistant
                         │
       ┌─────────────────┼─────────────────┐
       │                 │                 │
       ▼                 ▼                 ▼
HHVacancyClient    ResumeAnalyzer    VacancyRetriever
       │                 │                 │
       │                 ▼                 │
       │              LLMClient            │
       │                                   │
       └──────────────┬────────────────────┘
                      │
                      ▼
              PostgreSQL Repositories
                      │
                      ▼
             Matching / Search Results

                         │
                         ▼
                CoverLetterGenerator
                         │
                         ▼
                     LLMClient
```

The `JobAssistant` acts as an orchestration layer connecting the individual components.

The individual classes are responsible for specific parts of the system rather than containing the entire workflow in a single module.

## Main Components

### `HHVacancyClient`

Responsible for:

* building hh.ru search parameters;
* applying the generated filter definitions;
* performing vacancy searches;
* retrieving vacancy data.

## Technologies

### Backend

* Python
* PostgreSQL

### Vacancy Search

* hh.ru
* HTTP requests
* hh.ru filter dictionaries
* HTML vacancy parsing

### Matching

* Text embeddings
* BM25
* ranking

### LLM

* LLM API
* Structured resume analysis
* Vacancy evaluation
* Cover letter generation
* Retry and exponential backoff

## Current Project Status

The current backend is fully functional for its implemented workflow.

Implemented:

* [x] HH.ru vacancy search
* [x] HH.ru filter extraction and unified JSON storage
* [x] Vacancy description parsing
* [x] PostgreSQL storage
* [x] Vacancy caching
* [x] Resume analysis using LLM
* [x] Embedding-based matching
* [x] Custom BM25 matching
* [x] Intermediate vacancy ranking
* [x] LLM-based evaluation of top-ranked vacancies
* [x] Cover letter generation
* [x] LLM request throttling
* [x] Retry handling with exponential backoff
* [x] Handling of temporary `503` API errors

## Roadmap

The current version is focused on the backend. The next stages are planned around exposing the backend through an API and building a user-facing desktop application.

### FastAPI Backend

The next planned step is to add a **FastAPI** layer on top of the existing backend.

The expected architecture is:

```text
┌──────────────────────┐
│      Qt GUI          │
│      C++ / Qt        │
└──────────┬───────────┘
           │ HTTP
           ▼
┌──────────────────────┐
│       FastAPI        │
│       REST API       │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│   Existing Backend   │
│                      │
│   JobAssistant       │
│   HH.ru              │
│   PostgreSQL         │
│   Embeddings         │
│   BM25               │
│   LLM                │
└──────────────────────┘
```

FastAPI will provide an API boundary between the user interface and the existing Python application logic.

### Qt Desktop Application

A desktop GUI based on **C++/Qt** is planned as the client application.

The GUI is intended to provide functionality for:

* configuring vacancy search parameters;
* managing the candidate profile/resume;
* starting vacancy searches;
* displaying ranked vacancies;
* viewing matching results;
* viewing generated cover letters;
* displaying application/search statistics.

The planned separation keeps the Qt application independent from the internal Python implementation.

## Future Development

Potential future improvements include:

* FastAPI REST API;
* Qt desktop client;
* persistent candidate profiles;
* search and matching statistics;
* improved ranking algorithms;
* more detailed matching explanations;
* vacancy/application history;
* automated interaction with hh.ru where technically and legally appropriate.

## License

This project is intended primarily as a personal portfolio and experimental software project.
