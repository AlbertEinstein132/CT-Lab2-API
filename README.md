# Student Information:
*   **Full Name:** CAP MINH HIEU
*   **Student ID:** 25127328
*   **Class:** 25C09

# Selected model: 
* **Name of model:** `Falconsai/text_summarize`
* **Task:** Text Summarization
* **Hugging Face Page:** [https://huggingface.co/Falconsai/text_summarization]

# Description of system's functionality
This system exposes a FastAPI-based Web API that allows users to submit long English paragraphs and receive well-structured JSON responses containing the summarized text along with metadata.
**Key Features:**
* **System & Health Monitoring:** Provides system introduction (`GET /`) and operational readiness checks (`GET /health`).
* **Summarization Inference:** Supports both `POST /predict` and `POST /generate` endpoints with customizable summary length parameters (`min_length` and `max_length`).
* **Input Validation:** Ensures input text is non-empty, contains at least 10 words, and enforces logical length constraints (`min_length < max_length`).
* **Error Handling:** Gracefully handles missing fields, invalid data formats, and model inference exceptions with structured JSON error responses.

# Installation Instructions
### Step 1: Clone the repository
```bash
git clone [https://github.com/](https://github.com/)<your-username>/<your-repo-name>.git
cd <your-repo-name>
```

### Step 2: Create and activate a virtual environment (Recommended)
```bash
python -m venv venv

# On Windows:
venv\Scripts\activate

# On macOS / Linux:
source venv/bin/activate
```

### Step 3: Install required dependencies
```bash
pip install -r requirements.txt
```
# Running the application
Start the FastAPI server using Uvicorn:
```bash
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```
* **Note:** On the first run, the system will automatically download the `Falconsai/text_summarization` model (~242 MB) from Hugging Face.
* Once running, access the interactive Swagger UI documentation at: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

# Calling the API (Examples & Testing)
## 1.Automated Testing with Python `requests`
With the FastAPI server running in one terminal, open a second terminal and run:
```bash
python test_api.py
```
## 2. Endpoint Overview
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/` | Returns a brief introduction and available API endpoints. |
| `GET` | `/health` | Checks the operational status of the server and model readiness. |
| `POST` | `/predict` | Summarizes input English text and returns structured JSON. |
| `POST` | `/generate` | Alias for `/predict` (provides identical functionality). |
## 3. Example 1: System Introduction (`GET /`)
**Request:**
```bash
curl -X GET "[http://127.0.0.1:8000/](http://127.0.0.1:8000/)"
```

**Response (`200 OK`):**
```json
{
  "message": "Welcome to the Text Summarization API!",
  "description": "Automated text summarization API system powered by Hugging Face.",
  "model_used": "Falconsai/text_summarization",
  "endpoints": {
    "GET /": "API introduction and overview",
    "GET /health": "Check system and model operational status",
    "POST /predict": "Submit text to generate a summary (JSON)",
    "POST /generate": "Alias of /predict"
  }
}
```
## 4. Example 2: Health Check (`GET /health`)
**Request:**
```bash
curl -X GET "[http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)"
```

**Response (`200 OK`):**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "model_name": "Falconsai/text_summarization"
}
```
## 5. Example 3: Valid Summarization Request (`POST /predict`)
**Request (`application/json`):**
```json
{
  "text": "Artificial intelligence (AI) is intelligence demonstrated by machines, as opposed to the natural intelligence displayed by animals including humans. Leading AI textbooks define the field as the study of intelligent agents: any system that perceives its environment and takes actions that maximize its chance of achieving its goals. Some popular accounts use the term artificial intelligence to describe machines that mimic cognitive functions that humans associate with the human mind, such as learning and problem solving.",
  "min_length": 15,
  "max_length": 50
}
```

**Response (`200 OK`):**
```json
{
  "status": "success",
  "model": "Falconsai/text_summarization",
  "original_word_count": 75,
  "summary_word_count": 26,
  "processing_time_seconds": 0.7842,
  "summary": "Artificial intelligence (AI) is intelligence demonstrated by machines . Leading AI textbooks define the field as the study of intelligent agents ."
}
```
## 6. Example 4: Invalid Input / Validation Error (`POST /predict`)
**Request (Input text too short - less than 10 words):**
```json
{
  "text": "This text is too short.",
  "min_length": 10,
  "max_length": 30
}
```

**Response (`422 Unprocessable Entity`):**
```json
{
  "status": "error",
  "error_type": "Input Validation Error",
  "details": [
    {
      "field": "body -> text",
      "message": "Value error, Text is too short (5 words). Please provide at least 10 words for summarization."
    }
  ]
}
```

# Demonstration Video