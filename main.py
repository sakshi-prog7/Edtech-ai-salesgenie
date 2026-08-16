



import joblib
import numpy as np
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel
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

#Loading the  trained models 
dropout_model = joblib.load("dropout_warning_model.pkl")

# Load course recommendation assets
course_tfidf, courses_df = joblib.load("course_recommendation_model_light.pkl")
course_tfidf_matrix = course_tfidf.transform(courses_df["combined_features"])

student_profiling_vectorizer = joblib.load("student_profiling_vectorizer.pkl")
forecasting_model = joblib.load("sales_forecasting_model.pkl")


# Define Pydantic Request Schemas for Validation
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
  probability = dropout_model.predict_proba(features)[0][
      int(prediction)
  ] * 100
  return {
      "at_risk_of_dropping_out": bool(prediction),
      "confidence_score": round(float(probability), 2),
  }


@app.post("/predict-lead-score")
def predict_lead_score(data: LeadRequest):
  # Rule-based calculation 
  watch_score = min(1.0, data.time_watched / 45.0) * 0.45
  rating_score = (data.ratings / 5.0) * 0.35
  skip_penalty = min(1.0, data.skip_count / 15.0) * 0.20

  base_score = watch_score + rating_score - skip_penalty

  interests_lower = data.interests.lower()
  keyword_boost = 0.0
  if any(
      kw in interests_lower
      for kw in [
          "advanced",
          "machine learning",
          "neural",
          "python",
          "data science",
          "deep learning",
      ]
  ):
    keyword_boost = 0.15

  total_score = max(0.0, min(1.0, base_score + keyword_boost))
  conversion_prob = round(float(total_score * 100), 2)

  return {
      "high_intent_lead": bool(conversion_prob >= 50.0),
      "conversion_probability": conversion_prob,
  }

@app.post("/recommend-course")
def recommend_course(data: RecommendationRequest):
  student_vec = course_tfidf.transform([data.student_interests])
  sim_scores = cosine_similarity(student_vec, course_tfidf_matrix).flatten()

  # Get indices sorted by score descending 
  sorted_indices = sim_scores.argsort()[::-1]

  recommendations = []
  seen_courses = set()

  for idx in sorted_indices:
    course_name = courses_df.loc[idx, "course_name"]

    # Only add if we haven't already included this course name
    if course_name not in seen_courses:
      seen_courses.add(course_name)
      recommendations.append({
          "recommended_course": course_name,
          "category": courses_df.loc[idx, "category"],
          "similarity_score": round(float(sim_scores[idx] * 100), 2),
      })

    # To have 3 recommendations
    if len(recommendations) == 3:
      break

  return {"recommendations": recommendations}

@app.post("/student-profile")
def student_profile(data: ProfilingRequest):
  interests = data.interests.lower()
  if any(
      kw in interests
      for kw in ["react", "html", "css", "javascript", "web"]
  ):
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