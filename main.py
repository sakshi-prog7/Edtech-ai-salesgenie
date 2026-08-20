import os
import sys
import hashlib
from datetime import datetime, timedelta, timezone
from typing import List, Optional

import joblib
import numpy as np
import pandas as pd
from fastapi import FastAPI, Depends, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel
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
# 1. DATABASE & MODEL IMPORTS
# ==========================================
from db.database import engine, Base, get_db
import db.models
from db.models import (
    User, LoginHistory, OnlineLearningEngagement, 
    MarketingCampaignPerformance, StudentDropout, StudentPerformance
)
from db.schemas import (
    Token, TokenData, UserRegister, UserLogin, UserResponse,
    StudentLeadResponse, DashboardOverviewResponse,
    MarketingAnalyticsResponse, LeadScoreRequest
)
from services.routing_engine import route_lead_workflow

Base.metadata.create_all(bind=engine)

# ==========================================
# 2. JWT SECURITY CONFIGURATION
# ==========================================
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "edtech-ai-salesgenie-super-secret-jwt-key-2026")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 120

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

def hash_pw(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.email == email).first()
    if user is None or not user.is_active:
        raise credentials_exception
    return user

# ==========================================
# 3. FASTAPI APP INITIALIZATION
# ==========================================
app = FastAPI(
    title="EdTech AI SalesGenie Enterprise Platform",
    description="Unified API with JWT Authentication, Database CRM, Member 2 Retrained ML Models, and Marketing Analytics",
    version="2.2.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# 4. LOAD TRAINED ML MODELS (MEMBER 2 ASSETS)
# ==========================================
def safe_load_model(filename):
    if os.path.exists(filename):
        try:
            return joblib.load(filename)
        except Exception as e:
            print(f"[WARNING] Could not load {filename}: {e}")
    return None

dropout_model = safe_load_model("dropout_warning_model.pkl")
lead_scoring_model = safe_load_model("lead_scoring_model.pkl")

course_rec_asset = safe_load_model("course_recommendation_model_light.pkl")
if course_rec_asset:
    course_tfidf, courses_df = course_rec_asset
    course_tfidf_matrix = course_tfidf.transform(courses_df["combined_features"])
else:
    course_tfidf, courses_df, course_tfidf_matrix = None, None, None

student_profiling_vectorizer = safe_load_model("student_profiling_vectorizer.pkl")
forecasting_model = safe_load_model("sales_forecasting_model.pkl")

# ==========================================
# 5. REQUEST SCHEMAS (MEMBER 2 PREDICTIVE)
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
    experience_level: Optional[str] = "Intermediate"
    difficulty_level: Optional[str] = "Medium"
    learning_style: Optional[str] = "Visual"
    category: Optional[str] = "Data Science"
    interests: Optional[str] = "Machine Learning"

class RecommendationRequest(BaseModel):
    student_interests: str

class ProfilingRequest(BaseModel):
    interests: str
    experience_level: str
    learning_style: str

# ==========================================
# 6. SYSTEM HEALTH ENDPOINT
# ==========================================
@app.get("/")
def home():
    return {
        "status": "online",
        "service": "EdTech AI SalesGenie Enterprise Backend",
        "security": "JWT Bearer Token Enabled",
        "database": "connected",
        "ml_models": {
            "dropout_model_loaded": dropout_model is not None,
            "lead_scoring_model_loaded": lead_scoring_model is not None,
            "recommender_loaded": course_tfidf is not None,
            "forecasting_loaded": forecasting_model is not None
        }
    }

# ==========================================
# 7. JWT AUTHENTICATION ENDPOINTS
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

@app.post("/api/auth/login", response_model=Token)
def login(creds: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == creds.email).first()
    if not user or user.password_hash != hash_pw(creds.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user.last_login = datetime.now(timezone.utc)
    history = LoginHistory(user_id=user.id, ip_address="127.0.0.1", status="SUCCESS")
    db.add(history)
    db.commit()

    access_token = create_access_token(
        data={"sub": user.email, "role": user.role, "name": user.full_name}
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/auth/me", response_model=UserResponse)
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    return current_user

# ==========================================
# 8. SECURE CRM LEADS & ROUTING WORKFLOWS
# ==========================================
@app.get("/api/leads", response_model=List[StudentLeadResponse])
def get_leads(
    priority: Optional[str] = Query(None, description="Filter by HOT, WARM, or COLD"),
    limit: int = Query(50, description="Max rows to return"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(OnlineLearningEngagement)
    if priority:
        query = query.filter(OnlineLearningEngagement.priority_level == priority.upper())
    return query.limit(limit).all()

@app.post("/api/leads/score-and-route")
def score_and_route_lead(
    lead_input: LeadScoreRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
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
# 9. DASHBOARD & MARKETING ANALYTICS
# ==========================================
@app.get("/api/dashboard/overview", response_model=DashboardOverviewResponse)
def get_dashboard_overview(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
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
def get_marketing_breakdown(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
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
# 10. PREDICTIVE AI MODEL ENDPOINTS
# ==========================================
@app.post("/predict-dropout")
def predict_dropout(data: DropoutRequest):
    if not dropout_model:
        raise HTTPException(status_code=503, detail="Dropout warning model is not loaded")
    
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

@app.post("/predict-lead-score")
def predict_lead_score(data: LeadRequest):
    if lead_scoring_model:
        try:
            features = np.array([[
                data.age,
                data.time_spent_on_course,
                data.time_watched,
                data.skip_count,
                data.pause_count,
                data.ratings,
                data.num_reviews
            ]])
            if hasattr(lead_scoring_model, "predict_proba"):
                prob = float(lead_scoring_model.predict_proba(features)[0][1] * 100)
            else:
                prob = float(lead_scoring_model.predict(features)[0] * 100)
            return {
                "high_intent_lead": bool(prob >= 50.0),
                "conversion_probability": round(prob, 2),
                "engine": "retrained_ml_model"
            }
        except Exception:
            pass

    watch_score = min(1.0, data.time_watched / 45.0) * 0.45
    rating_score = (data.ratings / 5.0) * 0.35
    skip_penalty = min(1.0, data.skip_count / 15.0) * 0.20
    base_score = watch_score + rating_score - skip_penalty

    interests_lower = (data.interests or "").lower()
    keyword_boost = 0.15 if any(kw in interests_lower for kw in ["advanced", "ml", "python", "data"]) else 0.0
    total_score = max(0.0, min(1.0, base_score + keyword_boost))
    conversion_prob = round(float(total_score * 100), 2)

    return {
        "high_intent_lead": bool(conversion_prob >= 50.0),
        "conversion_probability": conversion_prob,
        "engine": "heuristic_routing"
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
    elif any(kw in interests for kw in ["ai", "machine learning", "neural", "python", "data"]):
        track = "AI & Machine Learning Engineering"
    elif any(kw in interests for kw in ["cybersecurity", "hacking", "penetration"]):
        track = "Cybersecurity & Ethical Hacking"
    else:
        track = "Cloud & Big Data Architecture"

    return {
        "experience_level": data.experience_level,
        "learning_style": data.learning_style,
        "assigned_career_profile": track,
    }

@app.get("/forecast-sales")
def forecast_sales():
    if not forecasting_model:
        raise HTTPException(status_code=503, detail="Sales forecasting model is not loaded")

    forecast = forecasting_model.forecast(steps=3)
    forecast_dict = {
        str(date.strftime("%Y-%m")): round(float(val), 2)
        for date, val in forecast.items()
    }
    return {"next_3_months_revenue_forecast": forecast_dict}