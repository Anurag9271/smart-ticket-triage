# Smart Customer Support Ticket Triage & Auto-Responder

## Overview

A local-first AI application that classifies customer support emails, prioritizes tickets, retrieves relevant information from an approved knowledge base, and generates suggested responses for human review.

## Goals

- Classify incoming tickets by category, urgency, and sentiment.
- Evaluate the classifier on labelled examples.
- Retrieve relevant FAQ and support-policy passages using RAG.
- Generate grounded response drafts using a local LLM.
- Store tickets and predictions in SQLite.
- Provide a dashboard for reviewing and managing tickets.
- Add automated tests, logging, and monitoring.

## Planned Technology Stack

- Python
- Laya for classification, subject to local compatibility and evaluation
- FastAPI for the backend
- Sentence Transformers and ChromaDB for retrieval
- Ollama for local LLM inference
- SQLite for persistence
- Streamlit for the dashboard
- Git and GitHub for version control and project tracking

## Development Status

Phase 0: Repository and environment setup  
Phase 1: Verify Laya and build a classification baseline  
Phase 2: Evaluate classification quality and latency  
Phase 3: Implement the RAG pipeline  
Phase 4: Integrate the API, database, and dashboard  
Phase 5: Test reliability and improve production readiness

## Safety

Generated responses are drafts and require human review. Customer data, credentials, local model weights, and private datasets must not be committed to the repository.

## Development

Setup instructions and dependencies will be documented as the implementation progresses.
