<<<<<<< HEAD
import os
import sys
import hashlib
from datetime import datetime
from typing import List, Optional
=======
>>>>>>> origin/Adithyan

import joblib
import numpy as np
import pandas as pd
<<<<<<< HEAD
from fastapi import FastAPI, Depends, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
=======
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
>>>>>>> origin/Adithyan
from sklearn.metrics.pairwise import cosine_similarity
from sqlalchemy import func
from sqlalchemy.orm import Session

# ==========================================
# 0. SCIKIT-LEARN PICKLE COMPATIBILITY PATCH
# ==========================================
try:
    import sklearn._loss as _loss
    for base_name in [
        "HalfBinomialLoss", "HalfMultinomialLoss", "HalfSquaredError",
        "HalfPoissonLoss", "HalfGammaLoss", "HalfTweedieLoss", "PinballLoss", "ExponentialLoss"
    ]:
        cy_name = f"Cy{base_name}"
        if hasattr(_loss, base_name):
            setattr(_loss, cy_name, getattr(_loss, base_name))
        else:
            setattr(_loss, cy_name, type(cy_name, (), {}))
    sys.modules["_loss"] = _loss
except Exception:
    pass

# ==========================================
# 1. DATABASE IMPORTS & INITIALIZATION
# ==========================================
from db.database import engine, Base, get_db
from db.models import (
    User, LoginHistory, OnlineLearningEngagement, 
    MarketingCampaignPerformance, StudentDropout, StudentPerformance
)
from db.schemas import (
    UserRegister, UserLogin, UserResponse,
    StudentLeadResponse, DashboardOverviewResponse,
    MarketingAnalyticsResponse
)
from services.routing_engine import route_lead_workflow

# Auto-generate DB tables
Base.metadata.create_all(bind=engine)

# ==========================================
# 2. FASTAPI APP & CORS CONFIGURATION
# ==========================================
app = FastAPI(
    title="EdTech AI SalesGenie Enterprise Platform",
    description="Unified API for Database CRM, Predictive AI Models, Authentication, and Marketing Analytics",
    version="2.0.0"
)

<<<<<<< HEAD
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
=======
# Load Trained Models (All in .pkl format)

dropout_model = joblib.load("dropout_warning_model.pkl")
>>>>>>> origin/Adithyan

# ==========================================
# 3. LOAD TRAINED ML MODELS
# ==========================================
def safe_load_model(filename):
    if os.path.exists(filename):
        try:
            return joblib.load(filename)
        except Exception as e:
            print(f"[WARNING] Could not load {filename}: {e}")
    return None

dropout_model = safe_load_model("dropout_warning_model.pkl")
course_rec_asset = safe_load_model("course_recommendation_model_light.pkl")
if course_rec_asset:
    course_tfidf, courses_df = course_rec_asset
    course_tfidf_matrix = course_tfidf.transform(courses_df["combined_features"])
else:
    course_tfidf, courses_df, course_tfidf_matrix = None, None, None

<<<<<<< HEAD
student_profiling_vectorizer = safe_load_model("student_profiling_vectorizer.pkl")
forecasting_model = safe_load_model("sales_forecasting_model.pkl")

# ==========================================
# 4. REQUEST SCHEMAS (MEMBER 2 + CRM)
# ==========================================
class DropoutRequest(BaseModel):
    age: float
    time_spent_on_course: float
    time_watched: float
    skip_count: float
    pause_count: float
    disengagement_score: float
    experience_level_encoded: int
    learning_style_encoded: int
    difficulty_level_encoded: int

class LeadRequest(BaseModel):
    age: float
    time_spent_on_course: float
    time_watched: float
    skip_count: float
    pause_count: float
    ratings: float
    num_reviews: float
    video_duration: float = 0.0
    experience_level: str
    difficulty_level: str
    learning_style: str
    category: str
    interests: str

class RecommendationRequest(BaseModel):
    student_interests: str

class ProfilingRequest(BaseModel):
    interests: str
    experience_level: str
    learning_style: str
=======
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
>>>>>>> origin/Adithyan

class LeadScoreRequest(BaseModel):
    student_id: int
    country: Optional[str] = "Global"
    engagement_score: float
    attendance_rate: float
    avg_quiz_score: float
    login_frequency_weekly: int

<<<<<<< HEAD
def hash_pw(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

# ==========================================
# 5. BASE & SYSTEM HEALTH ENDPOINTS
# ==========================================
@app.get("/")
def home():
    return {
        "status": "online",
        "service": "EdTech AI SalesGenie Enterprise Backend",
        "database": "connected",
        "ml_models_loaded": dropout_model is not None
    }
=======
# API Endpoints

@app.get("/")
def home():
    return {"status": "SalesGenie AI Microservice is running successfully!"}
>>>>>>> origin/Adithyan

# ==========================================
# 6. USER AUTHENTICATION & LOGIN LOGS
# ==========================================
@app.post("/api/auth/register", response_model=UserResponse)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user = User(
        full_name=user_data.full_name,
        email=user_data.email,
        password_hash=hash_pw(user_data.password),
        role=user_data.role
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@app.post("/api/auth/login")
def login(creds: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == creds.email).first()
    if not user or user.password_hash != hash_pw(creds.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    
    user.last_login = datetime.utcnow()
    history = LoginHistory(user_id=user.id, ip_address="127.0.0.1", status="SUCCESS")
    db.add(history)
    db.commit()
    return {
        "status": "success",
        "message": f"Welcome back, {user.full_name}",
        "user": {
            "id": user.id,
            "full_name": user.full_name,
            "email": user.email,
            "role": user.role,
            "last_login": user.last_login
        }
    }

# ==========================================
# 7. CRM LEADS & AUTOMATED ROUTING
# ==========================================
@app.get("/api/leads", response_model=List[StudentLeadResponse])
def get_leads(
    priority: Optional[str] = Query(None, description="Filter by HOT, WARM, or COLD"),
    limit: int = Query(50, description="Max rows to return"),
    db: Session = Depends(get_db)
):
    query = db.query(OnlineLearningEngagement)
    if priority:
        query = query.filter(OnlineLearningEngagement.priority_level == priority.upper())
    return query.limit(limit).all()

@app.post("/api/leads/score-and-route")
def score_and_route_lead(lead_input: LeadScoreRequest, db: Session = Depends(get_db)):
    result = route_lead_workflow(lead_input.model_dump())
    
    existing_record = db.query(OnlineLearningEngagement).filter(
        OnlineLearningEngagement.student_id == lead_input.student_id
    ).first()

    if existing_record:
        existing_record.engagement_score = lead_input.engagement_score
        existing_record.attendance_rate = lead_input.attendance_rate
        existing_record.avg_quiz_score = lead_input.avg_quiz_score
        existing_record.login_frequency_weekly = lead_input.login_frequency_weekly
        existing_record.ai_lead_score = result["ai_lead_score"]
        existing_record.priority_level = result["priority_level"]
        existing_record.assigned_counselor = result["routed_to"]
        existing_record.next_action = result["recommended_action"]
    else:
        new_lead = OnlineLearningEngagement(
            student_id=lead_input.student_id,
            country=lead_input.country,
            engagement_score=lead_input.engagement_score,
            attendance_rate=lead_input.attendance_rate,
            avg_quiz_score=lead_input.avg_quiz_score,
            login_frequency_weekly=lead_input.login_frequency_weekly,
            ai_lead_score=result["ai_lead_score"],
            priority_level=result["priority_level"],
            assigned_counselor=result["routed_to"],
            next_action=result["recommended_action"]
        )
        db.add(new_lead)

    db.commit()
    return result

# ==========================================
# 8. WEBSITE DASHBOARD KPI CALCULATIONS
# ==========================================
@app.get("/api/dashboard/overview", response_model=DashboardOverviewResponse)
def get_dashboard_overview(db: Session = Depends(get_db)):
    total_leads = db.query(OnlineLearningEngagement).count()
    hot_leads = db.query(OnlineLearningEngagement).filter(OnlineLearningEngagement.priority_level == "HOT").count()
    warm_leads = db.query(OnlineLearningEngagement).filter(OnlineLearningEngagement.priority_level == "WARM").count()
    cold_leads = db.query(OnlineLearningEngagement).filter(OnlineLearningEngagement.priority_level == "COLD").count()

    totals = db.query(
        func.sum(MarketingCampaignPerformance.cost).label("cost"),
        func.sum(MarketingCampaignPerformance.revenue).label("rev")
    ).first()

    cost = float(totals.cost or 0.0)
    rev = float(totals.rev or 0.0)
    roi = round(((rev - cost) / cost * 100), 2) if cost > 0 else 0.0
    at_risk = db.query(StudentDropout).filter(StudentDropout.target == "Dropout").count()

    return {
        "total_leads": total_leads,
        "hot_leads_count": hot_leads,
        "warm_leads_count": warm_leads,
        "cold_leads_count": cold_leads,
        "total_marketing_spend": round(cost, 2),
        "total_revenue_generated": round(rev, 2),
        "overall_roi_percentage": roi,
        "at_risk_dropout_students": at_risk
    }

@app.get("/api/marketing/analytics", response_model=List[MarketingAnalyticsResponse])
def get_marketing_breakdown(db: Session = Depends(get_db)):
    results = db.query(
        MarketingCampaignPerformance.platform,
        func.sum(MarketingCampaignPerformance.impressions).label("impressions"),
        func.sum(MarketingCampaignPerformance.clicks).label("clicks"),
        func.sum(MarketingCampaignPerformance.leads).label("leads"),
        func.sum(MarketingCampaignPerformance.applications).label("applications"),
        func.sum(MarketingCampaignPerformance.enrollments).label("enrollments"),
        func.sum(MarketingCampaignPerformance.cost).label("cost"),
        func.sum(MarketingCampaignPerformance.revenue).label("revenue")
    ).group_by(MarketingCampaignPerformance.platform).all()

    return [
        {
            "platform": r.platform,
            "impressions": int(r.impressions or 0),
            "clicks": int(r.clicks or 0),
            "leads": int(r.leads or 0),
            "applications": int(r.applications or 0),
            "enrollments": int(r.enrollments or 0),
            "cost": round(float(r.cost or 0.0), 2),
            "revenue": round(float(r.revenue or 0.0), 2)
        }
        for r in results
    ]

# ==========================================
# 9. MEMBER 2 PREDICTIVE AI MODEL ENDPOINTS
# ==========================================
@app.post("/predict-dropout")
def predict_dropout(data: DropoutRequest):
<<<<<<< HEAD
    if not dropout_model:
        raise HTTPException(status_code=503, detail="Dropout warning model is not loaded")
    
=======
>>>>>>> origin/Adithyan
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

<<<<<<< HEAD
@app.post("/predict-lead-score")
def predict_lead_score(data: LeadRequest):
    watch_score = min(1.0, data.time_watched / 45.0) * 0.45
    rating_score = (data.ratings / 5.0) * 0.35
    skip_penalty = min(1.0, data.skip_count / 15.0) * 0.20

    base_score = watch_score + rating_score - skip_penalty

    interests_lower = data.interests.lower()
    keyword_boost = 0.0
    if any(kw in interests_lower for kw in [
        "advanced", "machine learning", "neural", "python", "data science", "deep learning"
    ]):
        keyword_boost = 0.15

    total_score = max(0.0, min(1.0, base_score + keyword_boost))
    conversion_prob = round(float(total_score * 100), 2)

    return {
        "high_intent_lead": bool(conversion_prob >= 50.0),
        "conversion_probability": conversion_prob,
    }

@app.post("/recommend-course")
def recommend_course(data: RecommendationRequest):
    if not course_tfidf or courses_df is None:
        raise HTTPException(status_code=503, detail="Course recommendation model is not loaded")

    student_vec = course_tfidf.transform([data.student_interests])
    sim_scores = cosine_similarity(student_vec, course_tfidf_matrix).flatten()
    sorted_indices = sim_scores.argsort()[::-1]

    recommendations = []
    seen_courses = set()

    for idx in sorted_indices:
        course_name = courses_df.loc[idx, "course_name"]
=======
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

>>>>>>> origin/Adithyan
        if course_name not in seen_courses:
            seen_courses.add(course_name)
            recommendations.append({
                "recommended_course": course_name,
                "category": courses_df.loc[idx, "category"],
                "similarity_score": round(float(sim_scores[idx] * 100), 2),
            })
<<<<<<< HEAD
        if len(recommendations) == 3:
            break

    return {"recommendations": recommendations}
=======

        if len(recommendations) == 3:
            break

    return {"recommendations": recommendations}

>>>>>>> origin/Adithyan

@app.post("/student-profile")
def student_profile(data: ProfilingRequest):
    interests = data.interests.lower()
    if any(kw in interests for kw in ["react", "html", "css", "javascript", "web"]):
        track = "Fullstack Web Development"
<<<<<<< HEAD
    elif any(kw in interests for kw in [
        "ai", "machine learning", "neural", "python", "nlp", "computer vision"
    ]):
        track = "AI & Machine Learning Engineering"
    elif any(kw in interests for kw in ["cybersecurity", "hacking", "penetration"]):
        track = "Cybersecurity & Ethical Hacking"
    else:
        track = "Cloud & Big Data Architecture"
=======
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
>>>>>>> origin/Adithyan

    return {
        "experience_level": data.experience_level,
        "learning_style": data.learning_style,
        "assigned_career_profile": track,
    }

@app.get("/forecast-sales")
def forecast_sales():
<<<<<<< HEAD
    if not forecasting_model:
        raise HTTPException(status_code=503, detail="Sales forecasting model is not loaded")

=======
>>>>>>> origin/Adithyan
    forecast = forecasting_model.forecast(steps=3)
    forecast_dict = {
        str(date.strftime("%Y-%m")): round(float(val), 2)
        for date, val in forecast.items()
    }
    return {"next_3_months_revenue_forecast": forecast_dict}