# EdTech AI Backend Microservice (SalesGenie)

A  production-ready FastAPI microservice powering AI-driven student analytics, risk prediction, and course recommendations for the EdTech SalesGenie platform.

---

##  Features & Endpoints

The API provides the following core endpoints:
* **Student Dropout Warning (`/predict-dropout`):** Evaluates student engagement metrics and predicts at-risk students with confidence scores.

* **Lead Scoring (`/predict-lead-score`):** I tried to train an ML model using the dataset to provide the lead scores but its not working well as expected.For most leads its giving like above 95 percent and for avg leads its giving very poor lead scores.So thought of Utilizing a calibrated heuristic/rule-based engine to evaluate sales leads and calculate conversion probabilities.

* **Course Recommendation (`/recommend-course`):** Leverages TF-IDF vectorization and cosine similarity with built-in deduplication to recommend 3 unique, highly relevant courses.

* **Student Profiling & Sales Forecasting:** Processes student behavior features and forecasts future trends.
git commit -m "Update README with detailed context on lead scoring heuristic"
---

##  Tech Stack
* **Framework:** FastAPI, Uvicorn
* **Machine Learning & Data:** Scikit-Learn, Pandas, NumPy, Joblib
* **Version Control:** Git & GitHub

---

## Installation & Setup

Follow these steps to set up and run the backend locally on your machine:

### **1. Clone the Repository & Switch to your Branch**
```bash
git clone [https://github.com/sakshi-prog7/Edtech-ai-salesgenie.git](https://github.com/sakshi-prog7/Edtech-ai-salesgenie.git)
cd Edtech-ai-salesgenie
git checkout Adithyan


python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

Install Dependencies
pip install -r requirements.txt

Run the FastAPI Server
python -m uvicorn main:app --reload

API Documentation & Testing
Once the server is running, you can interact with and test all endpoints live using the interactive Swagger UI documentation:

URL: http://127.0.0.1:8000/docs