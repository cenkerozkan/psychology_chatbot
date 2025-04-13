# Psychology Chatbot

A supportive Arabic psychological assistance chatbot built with Python and Gemini AI.

## Overview

This project implements a conversational AI system designed to provide psychological support in Arabic. The chatbot uses Google's Gemini 2.0 Flash model to generate empathetic, supportive responses while maintaining appropriate boundaries for mental health assistance.

## Features
- **Conversation History**: Maintains chat history for context-aware responses
- **Database Integration**: MongoDB storage for persistent conversations
- **Professional Boundaries**: Clear disclaimers about the limitations of AI assistance
- **Interactive CLI**: Simple command-line interface for testing and interaction

## Architecture

The system follows a modular architecture:

- **Models**: Pydantic models for chat threads and messages
- **Repository**: MongoDB integration for data persistence
- **Service**: Core chat service using Gemini AI
- **Utilities**: Text cleaning, logging, and prompt generation

## Setup

### Prerequisites

- Python 3.10+
- MongoDB
- Google Gemini API key

### Installation

1. Clone the repository
```bash
git clone [repository-url]
cd psychologyChatbot
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Set up environment variables
```bash
export MONGODB_URI="your_mongodb_uri"
export GEMINI_API_KEY="your_gemini_api_key"
```
