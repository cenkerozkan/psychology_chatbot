import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from routes.chat_service_route import router as chat_router

# Initialize FastAPI app
app = FastAPI(
    title="Psychology Chatbot API",
    description="API for Arabic psychological support chatbot",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat_router)

# Error handling
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"message": f"Internal Server Error: {str(exc)}"},
    )

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "Psychology Chatbot API"}

# Root endpoint with API documentation link
@app.get("/")
async def root():
    return {
        "message": "Psychology Chatbot API is running",
        "documentation": "/docs",
    }