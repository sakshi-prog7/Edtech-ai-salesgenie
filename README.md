# EdTech AI — SalesGenie

### Intelligent Admissions Optimization & Student Lifecycle Intelligence Platform

EdTech AI — SalesGenie is an AI-powered educational technology platform designed to help institutions manage the **student acquisition, admissions, enrollment, engagement, and retention lifecycle**.

The system applies the core concepts of a SalesGenie/CRM platform to the EdTech domain by treating prospective students as **leads** and using their interactions, engagement, preferences, and historical activity to support lead prioritization, personalized recommendations, counselor decision-making, and institutional analytics.

---

## 1. Project Overview

Educational institutions receive large numbers of student inquiries through different channels. However, manually identifying high-intent students, following up with them, recommending suitable courses, and monitoring students after enrollment can be difficult.

**EdTech AI — SalesGenie** addresses this problem by combining:

* CRM-based student and lead management
* AI-powered lead scoring
* Student profiling
* Course recommendations
* Enrollment prediction
* Dropout risk detection
* Admissions and revenue forecasting
* Marketing analytics
* Counselor decision support
* Role-based dashboards

The platform connects the complete student lifecycle:

```text
Student Inquiry
      │
      ▼
Lead Generation
      │
      ▼
Lead Qualification
      │
      ▼
AI Lead Scoring
      │
      ▼
Counselor Prioritization
      │
      ▼
Counseling / Follow-up
      │
      ▼
Course Recommendation
      │
      ▼
Enrollment
      │
      ▼
Learning Engagement
      │
      ▼
Dropout Risk Detection
      │
      ▼
Student Intervention
```

The project therefore extends the SalesGenie approach from conventional sales into the **EdTech and admissions domain**.

---

# 2. Key Objectives

The major objectives of the platform are:

1. Identify and prioritize high-intent prospective students.
2. Provide AI-assisted lead scoring and qualification.
3. Maintain student and lead information through CRM functionality.
4. Recommend suitable courses based on student interests and skills.
5. Predict potential enrollment outcomes.
6. Detect students at risk of disengagement or dropout.
7. Provide admissions and marketing analytics.
8. Forecast future admissions and revenue.
9. Support counselors and administrators through role-specific dashboards.
10. Provide an integrated AI-driven decision-support system.

---

# 3. Core SalesGenie Mapping

The project retains the core SalesGenie concepts while adapting them to the EdTech domain.

| SalesGenie Concept | EdTech AI — SalesGenie              |
| ------------------ | ----------------------------------- |
| Lead               | Prospective student                 |
| Lead Profile       | Student profile                     |
| Lead Activity      | Student interactions and engagement |
| Lead Score         | Admission / conversion intent score |
| Lead Qualification | Hot / Warm / Cold prioritization    |
| Outreach           | Counselor follow-up                 |
| Conversion         | Student enrollment                  |
| CRM                | Student and admissions CRM          |
| Sales Analytics    | Admissions and marketing analytics  |
| Sales Forecast     | Admissions and revenue forecast     |

This allows the project to remain conceptually close to the original SalesGenie implementation while applying it to a different business domain.

---

# 4. System Architecture

```text
                    ┌─────────────────────────┐
                    │      React Frontend     │
                    │   React 18 + TypeScript  │
                    │       Vite + Tailwind    │
                    └────────────┬────────────┘
                                 │
                            HTTP / JSON
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │     FastAPI Backend     │
                    │   REST API + Security   │
                    └────────────┬────────────┘
                                 │
              ┌──────────────────┼──────────────────┐
              │                  │                  │
              ▼                  ▼                  ▼
       ┌─────────────┐   ┌──────────────┐   ┌──────────────┐
       │   SQLite    │   │  ML Inference │   │   Analytics  │
       │ SQLAlchemy  │   │   Pipelines   │   │   Services   │
       └─────────────┘   └──────────────┘   └──────────────┘
                              │
          ┌───────────────────┼────────────────────┐
          │                   │                    │
          ▼                   ▼                    ▼
   Lead Scoring       Dropout Prediction     Recommendations
          │                   │                    │
          └───────────────────┼────────────────────┘
                              ▼
                    Counselor / Admin
                       Decision Support
```

---

# 5. Application Modules

## M1 — Lead Management & Intelligence

The Lead Management module manages prospective students and their associated information.

### Major functions

* Student/lead profile management
* Lead activity tracking
* Engagement information
* Lead prioritization
* CRM activity management
* Counselor assignment
* Conversion-related information

The system transforms student interaction data into useful intelligence for the admissions team.

---

## M2 — AI Lead Scoring & Outreach Intelligence

The Lead Scoring Engine evaluates student engagement and behavioral signals to estimate admission intent.

The project uses a **hybrid scoring approach**, combining machine-learning prediction with behavioral indicators.

### Lead scoring workflow

```text
Student Activity
      │
      ▼
Feature Extraction
      │
      ▼
ML Lead Scoring Model
      │
      ├───────────────┐
      ▼               ▼
ML Probability   Behavioral Score
      │               │
      └───────┬───────┘
              ▼
       Final Lead Score
              │
       ┌──────┼──────┐
       ▼      ▼      ▼
      HOT    WARM   COLD
       │      │      │
       └──────┼──────┘
              ▼
     Counselor Action
```

The resulting score helps counselors identify which students should receive priority attention.

---

# 6. Machine Learning Components

## 6.1 Hybrid AI Lead Scoring

### Objective

Predict the likelihood that a prospective student is a high-value/high-intent lead.

### Model

**Calibrated Gradient Boosting Classifier**

The system combines:

* Machine-learning probability
* Behavioral engagement indicators
* Student interaction information

The final score is used to categorize leads into priority levels.

```text
P1 — HOT
P2 — WARM
P3 — COLD
```

This prioritization allows counselors to focus their effort on the most promising leads.

---

## 6.2 Student Dropout Early Warning

### Objective

Identify students who may be at risk of disengagement or dropout so that counselors or academic teams can intervene early.

### Model

**Random Forest Classifier**

### Important signals

* Course completion milestones
* Forum engagement
* Video interaction
* Video skip ratio
* Learning activity
* Engagement behavior

### Workflow

```text
Student Learning Activity
          │
          ▼
   Feature Extraction
          │
          ▼
   Dropout Risk Model
          │
          ▼
      Risk Score
          │
     ┌────┴────┐
     ▼         ▼
   Lower      Higher
    Risk       Risk
                │
                ▼
       Early Intervention
```

---

## 6.3 Semantic Course Recommendation

### Objective

Recommend courses that match a student's:

* Interests
* Skills
* Learning goals
* Background
* Career direction

### Algorithm

**TF-IDF Vectorization + Cosine Similarity**

### Workflow

```text
Student Profile
      │
      ▼
Text Representation
      │
      ▼
TF-IDF Vectorization
      │
      ▼
Cosine Similarity
      │
      ▼
Ranked Course Recommendations
```

The recommendation engine compares student information with course descriptions, syllabi, and learning outcomes.

---

## 6.4 Automated Student Profiling

The profiling module converts unstructured student information into a structured representation.

### Example

```text
Input:

Python, Machine Learning, Data Analysis,
Interested in Artificial Intelligence

              │
              ▼

Student Profile

Skills:
- Python
- Machine Learning
- Data Analysis

Interest:
- Artificial Intelligence

Suggested Path:
- AI / ML Engineering
```

Text vectorization is used to associate student backgrounds with relevant skills, interests, and learning pathways.

---

## 6.5 Admissions & Revenue Forecasting

### Objective

Provide institutions with future estimates for:

* Admission volume
* Cohort size
* Revenue
* Seasonal enrollment trends

### Model

**ARIMA (1,1,1)**

```text
Historical Admissions / Revenue
              │
              ▼
          ARIMA Model
              │
              ▼
       Future Forecast
              │
              ▼
 Institutional Planning
```

The forecasting component can assist administrators in planning admissions capacity and revenue targets.

---

# 7. Application Portals

The platform provides different views based on the user's role.

## Counselor Portal

Counselors can:

* View prioritized leads
* View AI-generated lead scores
* Review engagement information
* View conversion probabilities
* Manage prospective students
* Track CRM activities
* Access recommended follow-up actions

---

## Admin Portal

Administrators can:

* Monitor institutional KPIs
* View enrollment analytics
* Monitor AI predictions
* View revenue forecasts
* Analyze admission performance
* Analyze marketing performance
* Monitor model-related metrics

---

## Admissions Portal

Admissions teams can:

* Monitor enrollment velocity
* Analyze marketing channels
* Track admission performance
* Review cohort trends
* Monitor conversion metrics

---

## Student Portal

Students can:

* Discover courses
* Receive personalized recommendations
* View learning pathways
* Track skill development
* Access course information

---

# 8. CRM

The CRM layer maintains information related to prospective and enrolled students.

The system is designed around entities such as:

```text
Students
   │
   ├── Activities
   ├── Enrollments
   ├── Payments
   ├── Communications
   ├── Follow-ups
   └── AI Predictions
```

This allows the platform to combine CRM information with machine-learning predictions.

---

# 9. Database Architecture

The application uses:

* **SQLite**
* **SQLAlchemy ORM**
* Relational database design
* WAL mode for improved concurrent read/write behavior

The primary database contains information required for authentication, CRM operations, student information, activities, analytics, and AI predictions.

The project also includes database generation and seeding scripts.

```text
Application
     │
     ▼
SQLAlchemy ORM
     │
     ▼
SQLite Database
     │
     ├── Users
     ├── Students / Leads
     ├── Activities
     ├── Campaign Data
     ├── Enrollments
     └── AI Predictions
```

---

# 10. Authentication & Security

The backend uses:

* JWT authentication
* OAuth2-based authentication flow
* Role-based access control
* Password hashing
* Protected API endpoints

The API uses bearer tokens to authenticate users and control access to application functionality.

---

# 11. REST API

The React frontend communicates with the FastAPI backend using REST APIs.

Major API areas include:

```text
/auth
/leads
/predict
/analytics
```

The integration flow is:

```text
React
  │
  │ HTTP / JSON
  ▼
FastAPI
  │
  ├── Database
  │
  └── ML Inference
        ├── Lead Scoring
        ├── Dropout Prediction
        ├── Course Recommendation
        ├── Student Profiling
        └── Revenue Forecasting
```

FastAPI also provides interactive API documentation through Swagger/OpenAPI.

---

# 12. ML Model Artifacts

The project contains serialized machine-learning assets using Joblib.

| File                                    | Purpose                         |
| --------------------------------------- | ------------------------------- |
| `lead_scoring_model.pkl`                | Lead scoring                    |
| `dropout_warning_model.pkl`             | Student dropout prediction      |
| `course_recommendation_model_light.pkl` | Course recommendation           |
| `sales_forecasting_model.pkl`           | Admissions/revenue forecasting  |
| `student_profiling_vectorizer.pkl`      | Student profile text processing |

The models are loaded by the backend and used for inference through the REST API.

---

# 13. Machine Learning Pipeline

The general ML development pipeline is:

```text
Raw Dataset
     │
     ▼
Data Cleaning
     │
     ▼
Feature Engineering
     │
     ▼
Train / Validation Split
     │
     ▼
Model Training
     │
     ▼
Model Evaluation
     │
     ▼
Model Serialization
     │
     ▼
FastAPI Inference
     │
     ▼
React Application
```

---

# 14. Technology Stack

## Frontend

* React 18
* TypeScript
* Vite
* Tailwind CSS
* Lucide Icons
* Axios

## Backend

* Python
* FastAPI
* Uvicorn
* Pydantic
* SQLAlchemy
* SQLite

## Machine Learning

* Scikit-learn
* Pandas
* NumPy
* Joblib
* TF-IDF
* Cosine Similarity
* Statsmodels
* ARIMA

## Security

* OAuth2
* JWT
* Password hashing
* Role-based access control

## Development & Deployment

* Git
* GitHub
* GitHub Actions
* Docker
* Docker Compose
* Automated E2E testing

---

# 15. Repository Structure

```text
Edtech-ai-salesgenie/
│
├── backend/
│   └── app/
│       ├── core/
│       ├── models/
│       ├── routers/
│       ├── services/
│       └── main.py
│
├── db/
│   ├── database.py
│   ├── models.py
│   └── schemas.py
│
├── services/
│   └── routing_engine.py
│
├── src/
│   ├── components/
│   ├── pages/
│   ├── hooks/
│   └── services/
│
├── scripts/
│   ├── generate_seed_data.py
│   ├── seed_database.py
│   ├── dev-full.mjs
│   └── e2e-login-check.mjs
│
├── data/
│
├── reports/
│
├── tests/
│
├── lead_scoring_model.pkl
├── dropout_warning_model.pkl
├── course_recommendation_model_light.pkl
├── sales_forecasting_model.pkl
├── student_profiling_vectorizer.pkl
│
├── ed38976-edd_cleaned.csv
├── ranked_counselor_14k_leads.csv
│
├── main.py
├── requirements.txt
├── package.json
├── docker-compose.yml
└── README.md
```

---

# 16. Installation

## Prerequisites

Install:

* Python 3.10+
* Node.js
* npm
* Git
* Docker *(optional)*

---

## Step 1 — Clone the Repository

```bash
git clone https://github.com/AdithyanAnil0011/Edtech-ai-salesgenie.git
cd Edtech-ai-salesgenie
```

---

## Step 2 — Create Python Virtual Environment

### Windows

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### Linux / macOS

```bash
python -m venv .venv
source .venv/bin/activate
```

---

## Step 3 — Install Python Dependencies

```bash
python -m pip install -r requirements.txt
```

If required by the installed project version:

```bash
python -m pip install pydantic-settings PyJWT
```

---

## Step 4 — Install Frontend Dependencies

```bash
npm install
```

---

## Step 5 — Configure Environment Variables

Create a `.env` file in the project root.

Example:

```env
VITE_API_URL=http://127.0.0.1:8001
```

Use the backend port configured for your local environment.

---

# 17. Database Setup

The project uses SQLite with SQLAlchemy.

If the database needs to be regenerated/seeding is required:

```bash
python scripts/generate_seed_data.py
python scripts/seed_database.py
```

The database uses WAL mode to support improved concurrent database operations.

---

# 18. Running the Application

The application consists of two services:

### Terminal 1 — Backend

For the current local setup:

```powershell
python -m uvicorn main:app --host 127.0.0.1 --port 8001
```

Backend:

```text
http://127.0.0.1:8001
```

Swagger API documentation:

```text
http://127.0.0.1:8001/docs
```

### Terminal 2 — Frontend

```bash
npm run dev
```

Frontend:

```text
http://localhost:5173
```

> **Note:** The backend port must match the `VITE_API_URL` value in `.env`.

---

# 19. Demo Accounts

The project includes demonstration accounts for the main application roles.

| Role       | Email                  | Password   | Main Access                          |
| ---------- | ---------------------- | ---------- | ------------------------------------ |
| Admin      | `admin@edtech.ai`      | `demo1234` | KPIs, forecasting, monitoring        |
| Counselor  | `counselor@edtech.ai`  | `demo1234` | Lead scoring, CRM                    |
| Admissions | `admissions@edtech.ai` | `demo1234` | Admissions and marketing analytics   |
| Student    | `student@edtech.ai`    | `demo1234` | Course discovery and recommendations |

These credentials are intended only for local/project demonstration environments.

---

# 20. Example AI Workflow

### Before Enrollment

```text
Student Inquiry
      │
      ▼
Lead Created
      │
      ▼
Student Activity Collected
      │
      ▼
AI Lead Scoring
      │
      ▼
Lead Priority
      │
      ▼
Counselor Routing
      │
      ▼
Follow-up
      │
      ▼
Course Recommendation
      │
      ▼
Enrollment
```

### After Enrollment

```text
Learning Activity
      │
      ▼
Engagement Monitoring
      │
      ▼
Dropout Risk Prediction
      │
      ▼
Early Warning
      │
      ▼
Academic Intervention
```

---

# 21. Testing

The project includes automated diagnostic and end-to-end testing.

Example:

```bash
node scripts/e2e-login-check.mjs
```

Testing covers areas such as:

* Authentication API availability
* Database connectivity
* ML inference
* Frontend/backend integration
* End-to-end application flow

---

# 22. Docker

The project includes:

```text
docker-compose.yml
```

Docker can be used to create a reproducible environment for running the application services.

---

# 23. Development Workflow

```text
Developer
    │
    ▼
   Git
    │
    ▼
 GitHub
    │
    ▼
GitHub Actions
    │
    ├── Automated Tests
    ├── Validation
    └── CI/CD
```

---

# 24. Team Contributions

| Team Member            | Responsibility                                                                    |
| ---------------------- | --------------------------------------------------------------------------------- |
| **Adithyan Anilkumar** | AI/ML Pipelines, Hybrid Lead Scoring Engine, Model Calibration & API Integration  |
| **Varun Kandula**      | Backend Engineering, Relational Database Schema Design, REST API Routes           |
| **Sakshi**             | Frontend UX Architecture, React Component Development, Interactive Visualizations |
| **Sanskruti Vankar**   | Data Pipeline Engineering, Model Evaluation, Testing & Verification               |

---

# 25. Key Features

* AI-powered lead prioritization
* Hybrid behavioral + ML lead scoring
* Student enrollment prediction
* Student dropout early warning
* Semantic course recommendations
* Automated student profiling
* Admissions forecasting
* Revenue forecasting
* Counselor CRM
* Role-based portals
* JWT authentication
* REST API architecture
* React-based dashboard
* FastAPI backend
* SQLite persistence
* Pretrained ML inference
* Automated testing
* Docker support

---

# 26. Future Enhancements

Possible future improvements include:

* PostgreSQL production deployment
* Cloud-native deployment
* Real-time event streaming
* Advanced deep-learning recommendation models
* LLM-powered counselor assistant
* Automated WhatsApp/SMS integration
* Explainable AI dashboards
* Multi-institution support
* Real-time model monitoring
* Continuous model retraining

---

# 27. Disclaimer

This project is developed primarily as an **academic and demonstration platform** for intelligent admissions optimization and student lifecycle analytics.

AI predictions should be treated as **decision-support signals**, not definitive judgments about students.

Any real-world deployment should include:

* Data privacy controls
* Security validation
* Fairness evaluation
* Model validation
* Human oversight
* Institutional policies and governance

---

# 28. Project Summary

**EdTech AI — SalesGenie** combines CRM functionality, machine learning, natural-language processing, recommendation systems, and time-series forecasting into a unified platform for educational institutions.

The system connects the complete student lifecycle:

```text
                 ACQUISITION
                     │
                     ▼
                LEAD SCORING
                     │
                     ▼
            COUNSELOR PRIORITY
                     │
                     ▼
          COURSE DISCOVERY
                     │
                     ▼
        PERSONALIZED RECOMMENDATION
                     │
                     ▼
                 ENROLLMENT
                     │
                     ▼
             LEARNING ACTIVITY
                     │
                     ▼
          DROPOUT RISK WARNING
                     │
                     ▼
          STUDENT INTERVENTION
                     │
                     ▼
          INSTITUTIONAL ANALYTICS
```

The overall goal is to transform raw student and institutional data into **actionable intelligence for counselors, admissions teams, administrators, and students**.

---

## Academic Project

**EdTech AI — SalesGenie**
*Intelligent Admissions Optimization & Student Lifecycle Intelligence Platform*

Developed as an academic project demonstrating the integration of:

**CRM + Machine Learning + Recommendation Systems + NLP + Forecasting + Analytics + REST APIs**

## Contributors
* Sakshi Tiwari
* Sanskruthi
* Varun 
* Adithyan Anilkumar
