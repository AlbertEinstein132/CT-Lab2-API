from fastapi import FastAPI, HTTPException, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator, model_validator
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch
import time

app = FastAPI(
    title="Text Summarization API",
    description="English Text Summarization Web API powered by Falconsai/text_summarization",
    version="1.0.0"
)

MODEL_NAME = "Falconsai/text_summarization"
tokenizer = None
model = None

@app.on_event("startup")
def load_model():
    global tokenizer, model
    try:
        print(f"Loading model '{MODEL_NAME}'...")
        tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)
        print("Model loaded successfully!")
    except Exception as e:
        print(f"Error loading model: {e}")

class SummarizeRequest(BaseModel):
    text: str = Field(
        ..., 
        description="English text to summarize (minimum 10 words).",
        example="Artificial intelligence (AI) is intelligence demonstrated by machines, as opposed to the natural intelligence displayed by animals including humans. Leading AI textbooks define the field as the study of intelligent agents: any system that perceives its environment and takes actions that maximize its chance of achieving its goals."
    )
    min_length: int = Field(default=15, ge=5, le=200, description="Minimum token length of the summary")
    max_length: int = Field(default=60, ge=15, le=512, description="Maximum token length of the summary")

    @field_validator("text")
    @classmethod
    def validate_text_content(cls, v: str) -> str:
        cleaned_text = v.strip()
        if not cleaned_text:
            raise ValueError("Input text cannot be empty or contain only whitespace.")
        word_count = len(cleaned_text.split())
        if word_count < 10:
            raise ValueError(f"Text is too short ({word_count} words). Please provide at least 10 words for summarization.")
        return cleaned_text

    @model_validator(mode="after")
    def validate_length_constraints(self):
        if self.min_length >= self.max_length:
            raise ValueError(f"min_length ({self.min_length}) must be strictly less than max_length ({self.max_length}).")
        return self

class SummarizeResponse(BaseModel):
    status: str
    model: str
    original_word_count: int
    summary_word_count: int
    processing_time_seconds: float
    summary: str

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    errors = []
    for err in exc.errors():
        field = " -> ".join(str(loc) for loc in err["loc"])
        errors.append({"field": field, "message": err["msg"]})
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "status": "error",
            "error_type": "Input Validation Error",
            "details": errors
        }
    )

@app.get("/", tags=["General"])
def read_root():
    return {
        "message": "Welcome to the Text Summarization API!",
        "description": "Automated text summarization API system powered by Hugging Face.",
        "model_used": MODEL_NAME,
        "endpoints": {
            "GET /": "API introduction and overview",
            "GET /health": "Check system and model operational status",
            "POST /predict": "Submit text to generate a summary (JSON)",
            "POST /generate": "Alias of /predict"
        }
    }

@app.get("/health", tags=["General"])
def health_check():
    model_loaded = (model is not None) and (tokenizer is not None)
    if not model_loaded:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="System is starting up or model failed to load."
        )
    return {
        "status": "healthy",
        "model_loaded": True,
        "model_name": MODEL_NAME
    }

@app.post("/predict", response_model=SummarizeResponse, tags=["Inference"])
@app.post("/generate", response_model=SummarizeResponse, tags=["Inference"])
def summarize_text(request: SummarizeRequest):
    if model is None or tokenizer is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model is not loaded. Please try again later."
        )
    
    try:
        start_time = time.time()

        input_text = "summarize: " + request.text
        inputs = tokenizer.encode(
            input_text, 
            return_tensors="pt", 
            max_length=1024, 
            truncation=True
        )

        with torch.no_grad():
            summary_ids = model.generate(
                inputs,
                max_length=request.max_length,
                min_length=request.min_length,
                length_penalty=2.0,
                num_beams=4,
                early_stopping=True
            )
            
        summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
        process_time = round(time.time() - start_time, 4)
        
        return SummarizeResponse(
            status="success",
            model=MODEL_NAME,
            original_word_count=len(request.text.split()),
            summary_word_count=len(summary.split()),
            processing_time_seconds=process_time,
            summary=summary
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Model inference failure: {str(e)}"
        )