import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def print_response(title, response):
    print("=" * 65)
    print(f"TEST CASE: {title}")
    print(f"Status Code: {response.status_code}")
    try:
        print("Response JSON:")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    except Exception:
        print("Response Text:", response.text)
    print("=" * 65 + "\n")

def run_tests():
    res_root = requests.get(f"{BASE_URL}/")
    print_response("GET / - System Introduction", res_root)

    res_health = requests.get(f"{BASE_URL}/health")
    print_response("GET /health - Operational Status Check", res_health)

    payload_1 = {
        "text": (
            "Artificial intelligence (AI) is intelligence demonstrated by machines, as opposed to "
            "the natural intelligence displayed by animals including humans. Leading AI textbooks "
            "define the field as the study of intelligent agents: any system that perceives its "
            "environment and takes actions that maximize its chance of achieving its goals. "
            "Some popular accounts use the term artificial intelligence to describe machines that "
            "mimic cognitive functions that humans associate with the human mind, such as learning "
            "and problem solving."
        ),
        "min_length": 15,
        "max_length": 50
    }
    res_pred_1 = requests.post(f"{BASE_URL}/predict", json=payload_1)
    print_response("POST /predict - Valid Input #1 (Artificial Intelligence)", res_pred_1)

    payload_2 = {
        "text": (
            "Climate change includes both global warming driven by human-induced emissions of "
            "greenhouse gases and the resulting large-scale shifts in weather patterns. Though "
            "there have been previous periods of climatic change, since the mid-20th century "
            "humans have had an unprecedented impact on Earth's climate system and caused change "
            "on a global scale. The largest driver of warming is the emission of gases that "
            "create a greenhouse effect, of which more than 90% are carbon dioxide and methane."
        ),
        "min_length": 10,
        "max_length": 45
    }
    res_pred_2 = requests.post(f"{BASE_URL}/predict", json=payload_2)
    print_response("POST /predict - Valid Input #2 (Climate Change)", res_pred_2)

    payload_short = {
        "text": "This text is too short.",
        "min_length": 10,
        "max_length": 30
    }
    res_err_short = requests.post(f"{BASE_URL}/predict", json=payload_short)
    print_response("POST /predict - Validation Error (Text Too Short)", res_err_short)

    payload_missing = {
        "min_length": 10,
        "max_length": 30
    }
    res_err_missing = requests.post(f"{BASE_URL}/predict", json=payload_missing)
    print_response("POST /predict - Validation Error (Missing 'text' Field)", res_err_missing)

    payload_invalid_len = {
        "text": (
            "Computer networking refers to interconnected computing devices that can exchange data "
            "and share resources with each other. These networked devices use a system of rules, "
            "called communications protocols, to transmit information over physical or wireless technologies."
        ),
        "min_length": 50,
        "max_length": 20
    }
    res_err_len = requests.post(f"{BASE_URL}/predict", json=payload_invalid_len)
    print_response("POST /predict - Validation Error (min_length >= max_length)", res_err_len)

if __name__ == "__main__":
    print("Starting automated API tests...\n")
    try:
        run_tests()
    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to the FastAPI server.")
        print("Please make sure the server is running via: uvicorn main:app --reload")