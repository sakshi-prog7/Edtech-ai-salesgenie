
import joblib
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from sklearn.metrics.pairwise import cosine_similarity

# Initialize FastAPI app
app = FastAPI(
    title="SalesGenie AI Microservice",
    description=(
        "API endpoints for Lead Scoring, Dropout Warning, Course"
        " Recommendations, Student Profiling, and Sales Forecasting."
    ),
    version="1.0",
)

# Load Trained Models (All in .pkl format)

dropout_model = joblib.load("dropout_warning_model.pkl")

# Load course recommendation assets
course_tfidf, courses_df = joblib.load("course_recommendation_model_light.pkl")
course_tfidf_matrix = course_tfidf.transform(courses_df["combined_features"])

student_profiling_vectorizer = joblib.load("student_profiling_vectorizer.pkl")
forecasting_model = joblib.load("sales_forecasting_model.pkl")

# Load newly trained Gradient Boosting Lead Scoring Model (.pkl)
try:
    lead_scoring_model = joblib.load("lead_scoring_model.pkl")
except Exception:
    lead_scoring_model = None


EXP_MAP = {"advanced": 0, "beginner": 1, "expert": 2, "intermediate": 3}
STYLE_MAP = {"auditory": 0, "kinesthetic": 1, "reading/writing": 2, "visual": 3}
DIFF_MAP = {"advanced": 0, "beginner": 1, "intermediate": 2}
CAT_MAP = {
    "ai": 0,
    "blockchain": 1,
    "cloud computing": 2,
    "cybersecurity": 3,
    "data science": 4,
    "web development": 5,
}


#  Pydantic Request & Response Schemas

class DropoutRequest(BaseModel):
    age: float = Field(..., example=24.0)
    time_spent_on_course: float = Field(..., example=120.0)
    time_watched: float = Field(..., example=80.0)
    skip_count: float = Field(..., example=4.0)
    pause_count: float = Field(..., example=2.0)
    disengagement_score: float = Field(..., example=0.65)
    experience_level_encoded: int = Field(..., example=1)
    learning_style_encoded: int = Field(..., example=2)
    difficulty_level_encoded: int = Field(..., example=1)


class LeadRequest(BaseModel):
    student_id: str = Field(default="N/A", example="9c19eea1-3955-4b62-90c4-379f6cd2edf7")
    name: str = Field(default="Candidate Lead", example="Rahul Sharma")
    course_name: str = Field(default="General Track", example="Full Stack Web Development")
    age: float = Field(..., example=24.0)
    ratings: float = Field(..., ge=1.0, le=5.0, example=4.8)
    time_spent_on_course: float = Field(..., example=450.0)
    video_duration: float = Field(..., example=300.0)
    time_watched: float = Field(..., example=285.0)
    skip_count: float = Field(..., example=1.0)
    pause_count: float = Field(..., example=3.0)
    disengagement_score: float = Field(default=0.2, ge=0.0, le=1.0, example=0.15)
    num_reviews: float = Field(default=10.0, example=12.0)
    experience_level: str = Field(default="Intermediate", example="Intermediate")
    difficulty_level: str = Field(default="Intermediate", example="Intermediate")
    learning_style: str = Field(default="Visual", example="Visual")
    category: str = Field(default="Web Development", example="Web Development")
    interests: str = Field(default="", example="React, Node.js, Web Development")


class LeadScoreResponse(BaseModel):
    student_id: str
    name: str
    course_name: str
    ai_conversion_probability: float
    behavioral_momentum_index: float
    lead_score: float
    priority_tier: str
    high_intent_lead: bool
    counsellor_directive: str


class RecommendationRequest(BaseModel):
    student_interests: str = Field(..., example="Penetration Testing and React")


class ProfilingRequest(BaseModel):
    interests: str = Field(..., example="React, JavaScript, Node.js, Web")
    experience_level: str = Field(..., example="Beginner")
    learning_style: str = Field(..., example="Kinesthetic")


# API Endpoints

@app.get("/")
def home():
    return {"status": "SalesGenie AI Microservice is running successfully!"}


@app.post("/predict-dropout")
def predict_dropout(data: DropoutRequest):
    features = [[
        data.age,
        data.time_spent_on_course,
        data.time_watched,
        data.skip_count,
        data.pause_count,
        data.disengagement_score,
        data.experience_level_encoded,
        data.learning_style_encoded,
        data.difficulty_level_encoded,
    ]]
    prediction = dropout_model.predict(features)[0]
    probability = dropout_model.predict_proba(features)[0][int(prediction)] * 100
    return {
        "at_risk_of_dropping_out": bool(prediction),
        "confidence_score": round(float(probability), 2),
    }

@app.post("/predict-lead-score", response_model=LeadScoreResponse)
def predict_lead_score(data: LeadRequest):
    global lead_scoring_model
    if lead_scoring_model is None:
        raise HTTPException(
            status_code=500, detail="lead_scoring_model.pkl not found on server."
        )

    #  Check if the loaded artifact is a dictionary or raw model estimator
    clf = lead_scoring_model
    if isinstance(lead_scoring_model, dict) and "model" in lead_scoring_model:
        clf = lead_scoring_model["model"]

    try:
        #  Defensive numeric casting and clipping
        duration = max(float(data.video_duration or 0.0), 1.0)
        time_watched = float(data.time_watched or 0.0)
        disengagement = float(data.disengagement_score if data.disengagement_score is not None else 0.2)
        ratings = float(data.ratings or 4.0)
        skip_count = float(data.skip_count or 0.0)
        pause_count = float(data.pause_count or 0.0)
        age = float(data.age or 24.0)
        time_spent = float(data.time_spent_on_course or 0.0)

        # Behavioral feature normalization
        watch_ratio = float(np.clip(time_watched / duration, 0.0, 1.0))
        engagement_score = float(1.0 - np.clip(disengagement, 0.0, 1.0))
        normalized_rating = float(np.clip((ratings - 1.0) / 4.0, 0.0, 1.0))
        skip_penalty = float(np.clip(skip_count / 10.0, 0.0, 1.0))

        #  Categorical encodings
        exp_str = str(data.experience_level or "Intermediate").strip().lower()
        style_str = str(data.learning_style or "Visual").strip().lower()
        diff_str = str(data.difficulty_level or "Intermediate").strip().lower()
        cat_str = str(data.category or "Web Development").strip().lower()

        exp_encoded = int(EXP_MAP.get(exp_str, 1))
        style_encoded = int(STYLE_MAP.get(style_str, 3))
        diff_encoded = int(DIFF_MAP.get(diff_str, 1))
        cat_encoded = int(CAT_MAP.get(cat_str, 5))

        #  Build feature row
        feature_order = [
            "age", "ratings", "time_spent_on_course", "watch_ratio",
            "engagement_score", "normalized_rating", "skip_count", "pause_count",
            "experience_level_encoded", "learning_style_encoded",
            "difficulty_level_encoded", "category_encoded"
        ]

        features_df = pd.DataFrame([{
            "age": age,
            "ratings": ratings,
            "time_spent_on_course": time_spent,
            "watch_ratio": watch_ratio,
            "engagement_score": engagement_score,
            "normalized_rating": normalized_rating,
            "skip_count": skip_count,
            "pause_count": pause_count,
            "experience_level_encoded": exp_encoded,
            "learning_style_encoded": style_encoded,
            "difficulty_level_encoded": diff_encoded,
            "category_encoded": cat_encoded
        }])[feature_order]

        try:
            ml_prob = float(clf.predict_proba(features_df)[0, 1])
        except Exception:
            ml_prob = float(clf.predict_proba(features_df.to_numpy())[0, 1])

        heuristic_index = float(
            watch_ratio * 0.35
            + engagement_score * 0.35
            + normalized_rating * 0.20
            + (1.0 - skip_penalty) * 0.10
        )
        lead_score = round(float((0.50 * ml_prob + 0.50 * heuristic_index) * 100), 1)

       
        if lead_score >= 75:
            tier = "🔥 P1_HOT"
            action = "Direct Outbound Call / Priority WhatsApp Offer"
        elif lead_score >= 50:
            tier = "⚡ P2_WARM"
            action = "Automated Email Drip + Demo Class Invite"
        else:
            tier = "❄️ P3_COLD"
            action = "Drip Re-engagement / Free Masterclass"

        return LeadScoreResponse(
            student_id=str(data.student_id or "N/A"),
            name=str(data.name or "Candidate Lead"),
            course_name=str(data.course_name or "General Track"),
            ai_conversion_probability=round(ml_prob * 100, 1),
            behavioral_momentum_index=round(heuristic_index * 100, 1),
            lead_score=lead_score,
            priority_tier=tier,
            high_intent_lead=bool(lead_score >= 50.0),
            counsellor_directive=action,
        )

    except Exception as e:
        print(f"[ERROR in /predict-lead-score]: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Inference Error: {str(e)}")
    

@app.post("/recommend-course")
def recommend_course(data: RecommendationRequest):
    student_vec = course_tfidf.transform([data.student_interests])
    sim_scores = cosine_similarity(student_vec, course_tfidf_matrix).flatten()

    sorted_indices = sim_scores.argsort()[::-1]
    recommendations = []
    seen_courses = set()

    for idx in sorted_indices:
        course_name = courses_df.loc[idx, "course_name"]

        if course_name not in seen_courses:
            seen_courses.add(course_name)
            recommendations.append({
                "recommended_course": course_name,
                "category": courses_df.loc[idx, "category"],
                "similarity_score": round(float(sim_scores[idx] * 100), 2),
            })

        if len(recommendations) == 3:
            break

    return {"recommendations": recommendations}


@app.post("/student-profile")
def student_profile(data: ProfilingRequest):
    interests = data.interests.lower()
    if any(kw in interests for kw in ["react", "html", "css", "javascript", "web"]):
        track = "Fullstack Web Development"
    elif any(
        kw in interests
        for kw in [
            "ai",
            "machine learning",
            "neural",
            "python",
            "nlp",
            "computer vision",
        ]
    ):
        track = "AI & Machine Learning Engineering"
    elif any(kw in interests for kw in ["cybersecurity", "hacking", "penetration"]):
        track = "Cybersecurity & Ethical Hacking"
    elif any(
        kw in interests
        for kw in ["sql", "tableau", "powerbi", "analytics", "dashboard"]
    ):
        track = "Data Analytics & Business Intelligence"
    elif any(
        kw in interests
        for kw in ["docker", "kubernetes", "devops", "aws", "ci/cd"]
    ):
        track = "DevOps & Cloud Engineering"
    elif any(
        kw in interests
        for kw in ["flutter", "react native", "ios", "android", "mobile"]
    ):
        track = "Mobile App Development"
    else:
        track = "Cloud & Big Data Architecture"

    return {
        "experience_level": data.experience_level,
        "learning_style": data.learning_style,
        "assigned_career_profile": track,
    }


@app.get("/forecast-sales")
def forecast_sales():
    forecast = forecasting_model.forecast(steps=3)
    forecast_dict = {
        str(date.strftime("%Y-%m")): round(float(val), 2)
        for date, val in forecast.items()
    }
    return {"next_3_months_revenue_forecast": forecast_dict}