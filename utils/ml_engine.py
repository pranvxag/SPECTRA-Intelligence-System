"""
utils/ml_engine.py — Machine Learning Core

Models:
1. CareerClassifier     — Multi-class RandomForest to predict best-fit career
2. RiskDetector         — KMeans clustering to identify at-risk student groups
3. StudentClusterer     — KMeans to segment students by learning profile
4. GrowthPredictor      — Linear regression for CGPA trajectory forecast

All models are trained on synthetic data generated from domain knowledge,
then serialised to models/ directory. Re-training is triggered on new data upload.
"""
from __future__ import annotations
import os
import numpy as np
import pandas as pd
import joblib
from typing import Dict, List, Tuple

from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.cluster import KMeans
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.pipeline import Pipeline
from sklearn.model_selection import cross_val_score
from sklearn.metrics import classification_report

from utils.data_engine import get_feature_vector, FEATURE_NAMES

# ── Paths ─────────────────────────────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(BASE_DIR, "models")
os.makedirs(MODELS_DIR, exist_ok=True)

CAREER_MODEL_PATH    = os.path.join(MODELS_DIR, "career_classifier.pkl")
RISK_MODEL_PATH      = os.path.join(MODELS_DIR, "risk_detector.pkl")
CLUSTER_MODEL_PATH   = os.path.join(MODELS_DIR, "student_clusterer.pkl")
SCALER_PATH          = os.path.join(MODELS_DIR, "feature_scaler.pkl")
LABEL_ENCODER_PATH   = os.path.join(MODELS_DIR, "career_label_encoder.pkl")

# ── Career definitions (mirrors career_engine.py) ────────────────────────
CAREER_LABELS = [
    "AI / ML Engineer", "Data Scientist", "Software Engineer",
    "Product Manager", "Research Scientist", "UX / Product Designer",
    "Core Engineer", "Finance/Quant"
]

# ── Synthetic data generation ─────────────────────────────────────────────

def _generate_synthetic_data(n_samples: int = 3000) -> Tuple[np.ndarray, np.ndarray]:
    """
    Generate realistic synthetic training data based on domain knowledge.
    Each career archetype has a realistic feature profile with Gaussian noise.
    """
    np.random.seed(42)
    rng = np.random.default_rng(42)

    # Career archetype feature profiles
    # [cgpa, effort, tech, analytical, creative, comm, leadership, consistency,
    #  projects, internships, hackathons, certs, extras,
    #  int_aiml, int_prog, int_math, int_research, int_design, int_mgmt, int_core, int_finance]
    archetypes = {
        "AI/ML Engineer": {
            "means": [0.82, 0.78, 0.85, 0.88, 0.55, 0.60, 0.45, 0.78,
                      0.50, 0.30, 0.55, 0.50, 0.30,
                      0.90, 0.80, 0.85, 0.60, 0.20, 0.20, 0.10, 0.15],
            "std":   [0.08, 0.10, 0.10, 0.08, 0.12, 0.12, 0.12, 0.10,
                      0.20, 0.20, 0.25, 0.20, 0.20,
                      0.12, 0.15, 0.12, 0.20, 0.10, 0.10, 0.05, 0.10],
        },
        "Data Scientist": {
            "means": [0.80, 0.74, 0.78, 0.90, 0.58, 0.65, 0.48, 0.75,
                      0.45, 0.35, 0.40, 0.55, 0.30,
                      0.70, 0.72, 0.90, 0.65, 0.25, 0.25, 0.10, 0.30],
            "std":   [0.09, 0.10, 0.10, 0.07, 0.12, 0.12, 0.12, 0.10,
                      0.20, 0.20, 0.20, 0.20, 0.20,
                      0.15, 0.15, 0.10, 0.20, 0.10, 0.10, 0.05, 0.15],
        },
        "Software Engineer": {
            "means": [0.75, 0.72, 0.88, 0.78, 0.55, 0.60, 0.50, 0.80,
                      0.60, 0.40, 0.60, 0.50, 0.40,
                      0.50, 0.90, 0.65, 0.40, 0.30, 0.30, 0.15, 0.10],
            "std":   [0.10, 0.10, 0.08, 0.10, 0.12, 0.12, 0.12, 0.08,
                      0.20, 0.20, 0.25, 0.20, 0.20,
                      0.20, 0.10, 0.15, 0.15, 0.10, 0.10, 0.08, 0.05],
        },
        "Product Manager": {
            "means": [0.78, 0.80, 0.65, 0.75, 0.72, 0.85, 0.82, 0.75,
                      0.55, 0.50, 0.45, 0.40, 0.60,
                      0.35, 0.55, 0.50, 0.40, 0.70, 0.85, 0.10, 0.25],
            "std":   [0.08, 0.08, 0.12, 0.10, 0.10, 0.08, 0.08, 0.10,
                      0.20, 0.20, 0.20, 0.20, 0.20,
                      0.15, 0.15, 0.15, 0.15, 0.12, 0.10, 0.05, 0.12],
        },
        "Research Scientist": {
            "means": [0.88, 0.76, 0.80, 0.92, 0.65, 0.60, 0.50, 0.82,
                      0.40, 0.20, 0.30, 0.55, 0.30,
                      0.65, 0.60, 0.90, 0.92, 0.25, 0.25, 0.10, 0.15],
            "std":   [0.06, 0.09, 0.10, 0.06, 0.12, 0.12, 0.12, 0.08,
                      0.15, 0.15, 0.15, 0.20, 0.15,
                      0.15, 0.15, 0.08, 0.08, 0.10, 0.10, 0.05, 0.10],
        },
        "UX Designer": {
            "means": [0.72, 0.70, 0.58, 0.68, 0.88, 0.80, 0.58, 0.70,
                      0.55, 0.45, 0.40, 0.45, 0.55,
                      0.25, 0.50, 0.40, 0.30, 0.90, 0.55, 0.10, 0.10],
            "std":   [0.10, 0.10, 0.12, 0.10, 0.08, 0.08, 0.12, 0.10,
                      0.20, 0.20, 0.20, 0.20, 0.20,
                      0.10, 0.15, 0.15, 0.15, 0.08, 0.15, 0.05, 0.05],
        },
        "Core Engineer": {
            "means": [0.74, 0.70, 0.78, 0.72, 0.55, 0.62, 0.52, 0.75,
                      0.45, 0.35, 0.30, 0.40, 0.45,
                      0.15, 0.40, 0.60, 0.35, 0.25, 0.30, 0.88, 0.15],
            "std":   [0.10, 0.10, 0.10, 0.10, 0.12, 0.12, 0.12, 0.10,
                      0.20, 0.20, 0.15, 0.20, 0.20,
                      0.08, 0.15, 0.15, 0.15, 0.10, 0.10, 0.10, 0.08],
        },
        "Finance/Quant": {
            "means": [0.80, 0.75, 0.70, 0.88, 0.60, 0.72, 0.68, 0.78,
                      0.35, 0.40, 0.25, 0.50, 0.40,
                      0.30, 0.50, 0.82, 0.55, 0.30, 0.60, 0.15, 0.90],
            "std":   [0.08, 0.09, 0.10, 0.07, 0.12, 0.10, 0.10, 0.08,
                      0.15, 0.20, 0.15, 0.20, 0.18,
                      0.12, 0.15, 0.10, 0.15, 0.10, 0.12, 0.08, 0.08],
        },
    }

    n_per_class = n_samples // len(archetypes)
    X_list, y_list = [], []

    for career, params in archetypes.items():
        means = np.array(params["means"])
        stds  = np.array(params["std"])
        samples = rng.normal(means, stds, size=(n_per_class, len(means)))
        # Clip to valid ranges
        samples = np.clip(samples, 0.0, 1.0)
        # Binary interest features should be 0 or 1
        for i in range(13, 21):
            samples[:, i] = (samples[:, i] > 0.5).astype(float)
        X_list.append(samples)
        y_list.extend([career] * n_per_class)

    X = np.vstack(X_list)
    y = np.array(y_list)
    return X, y


# ── Model Training ────────────────────────────────────────────────────────

def train_all_models(df: pd.DataFrame | None = None) -> Dict[str, float]:
    """
    Train all ML models. If df is provided, augment synthetic data with real data.
    Returns dict of model -> CV accuracy.
    """
    print("🔧 Generating synthetic training data...")
    X_syn, y_syn = _generate_synthetic_data(3000)

    # If real data provided, extract features + labels
    if df is not None and "career_goal" in df.columns and len(df) >= 10:
        print(f"📊 Augmenting with {len(df)} real student records...")
        real_X, real_y = [], []
        for _, row in df.iterrows():
            from utils.data_engine import df_to_profile
            profile = df_to_profile(row)
            fv = get_feature_vector(profile)
            goal = str(row.get("career_goal", "")).strip()
            if goal and goal in CAREER_LABELS:
                real_X.append(fv)
                real_y.append(goal)
        if real_X:
            X_syn = np.vstack([X_syn, np.array(real_X)])
            y_syn = np.concatenate([y_syn, np.array(real_y)])

    # ── 1. Career Classifier ──────────────────────────────────────────
    print("🤖 Training Career Classifier (RandomForest)...")
    le = LabelEncoder()
    y_enc = le.fit_transform(y_syn)

    career_model = Pipeline([
        ("scaler", StandardScaler()),
        ("clf", RandomForestClassifier(
            n_estimators=200,
            max_depth=12,
            min_samples_leaf=3,
            class_weight="balanced",
            random_state=42,
            n_jobs=-1,
        ))
    ])
    cv_scores = cross_val_score(career_model, X_syn, y_enc, cv=5, scoring="accuracy")
    career_model.fit(X_syn, y_enc)

    joblib.dump(career_model, CAREER_MODEL_PATH)
    joblib.dump(le, LABEL_ENCODER_PATH)
    results = {"career_classifier_cv_acc": float(cv_scores.mean())}
    print(f"  ✅ Career Classifier CV Accuracy: {cv_scores.mean():.3f} ± {cv_scores.std():.3f}")

    # ── 2. Student Clusterer (learning profiles) ──────────────────────
    print("🧩 Training Student Clusterer (KMeans, k=5)...")
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_syn)

    clusterer = KMeans(n_clusters=5, random_state=42, n_init=20, max_iter=500)
    clusterer.fit(X_scaled)

    joblib.dump(clusterer, CLUSTER_MODEL_PATH)
    joblib.dump(scaler, SCALER_PATH)
    results["student_clusterer_inertia"] = float(clusterer.inertia_)
    print(f"  ✅ Clusterer inertia: {clusterer.inertia_:.1f}")

    print("✅ All models trained and saved.")
    return results


def _ensure_models_exist():
    """Train models on first run if not already saved."""
    if not os.path.exists(CAREER_MODEL_PATH):
        print("⚡ First run — training models on synthetic data...")
        train_all_models()


# ── Prediction API ────────────────────────────────────────────────────────

def predict_career_fit(profile: dict) -> List[Dict]:
    """
    Return ranked list of careers with ML-predicted probabilities
    combined with the formula-based score.
    """
    _ensure_models_exist()

    career_model = joblib.load(CAREER_MODEL_PATH)
    le           = joblib.load(LABEL_ENCODER_PATH)

    fv = get_feature_vector(profile).reshape(1, -1)
    proba = career_model.predict_proba(fv)[0]  # probability per class

    results = []
    for idx, career_label in enumerate(le.classes_):
        ml_score   = float(proba[idx]) * 100
        # Blend with formula score from career_engine
        from utils.career_engine import CAREERS, calculate_career_fit
        # Fuzzy title match: strip spaces/slashes for comparison
        def _norm(s): return s.lower().replace(" ","").replace("/","").replace("-","")
        formula_career = next((c for c in CAREERS if _norm(c["title"]) == _norm(career_label)), None)
        # Also try partial match
        if not formula_career:
            formula_career = next((c for c in CAREERS if _norm(career_label)[:8] in _norm(c["title"])), None)
        formula_score  = calculate_career_fit(profile, formula_career) if formula_career else ml_score * 0.8

        # Blend: 35% ML probability signal + 65% domain formula
        # (ML weight increases as real training data grows)
        blended = round(ml_score * 0.35 + formula_score * 0.65, 1)

        career_info = formula_career or {"title": career_label, "salary": "—",
                                          "demand": "—", "skills_needed": [],
                                          "path": "—", "id": career_label.lower().replace(" ", "_")}
        results.append({**career_info, "fit": blended,
                        "ml_score": round(ml_score, 1),
                        "formula_score": round(formula_score, 1)})

    return sorted(results, key=lambda x: x["fit"], reverse=True)


def predict_student_cluster(profile: dict) -> Dict:
    """
    Assign a student to a learning profile cluster.
    Returns cluster label + description.
    """
    _ensure_models_exist()

    scaler    = joblib.load(SCALER_PATH)
    clusterer = joblib.load(CLUSTER_MODEL_PATH)

    fv = get_feature_vector(profile).reshape(1, -1)
    fv_scaled = scaler.transform(fv).astype("float64")
    cluster_id = int(clusterer.predict(fv_scaled)[0])

    cluster_profiles = {
        0: {"name": "🚀 High Achiever",     "desc": "Strong academics + skills + activities. Top placement candidate.", "color": "#00E887"},
        1: {"name": "📐 Technical Specialist","desc": "High STEM scores. Best suited for deep technical/research roles.", "color": "#00D4FF"},
        2: {"name": "🌱 Growing Talent",     "desc": "Moderate profile with clear upward trajectory. High potential.", "color": "#FFB800"},
        3: {"name": "🤝 Soft Skill Leader",  "desc": "Strong communication + leadership. Ideal for PM/consulting roles.", "color": "#A78BFA"},
        4: {"name": "⚠️ Needs Support",      "desc": "Below-average scores across dimensions. Intervention recommended.", "color": "#FF4D6A"},
    }
    profile_info = cluster_profiles.get(cluster_id, cluster_profiles[2])
    return {"cluster_id": cluster_id, **profile_info}


def predict_cgpa_trajectory(profile: dict, semesters: int = 4) -> List[float]:
    """
    Simple polynomial growth model for CGPA trajectory.
    Uses current CGPA + trend + effort to project future values.
    """
    cgpa    = profile.get("cgpa", 7.0)
    effort  = profile.get("effort", 3)
    trend   = {"Improving": 0.15, "Stable": 0.05, "Declining": -0.10}.get(
               profile.get("academic_trend", "Stable"), 0.05)

    effort_bonus = (effort - 3) * 0.03  # bonus/penalty per effort unit above/below 3
    base_growth  = trend + effort_bonus

    projected = []
    for i in range(1, semesters + 1):
        # Diminishing returns as CGPA approaches 10
        headroom = (10 - cgpa) / 10
        growth   = base_growth * headroom * (1 - 0.1 * i)  # growth decelerates
        new_cgpa = min(10.0, round(cgpa + growth, 2))
        projected.append(new_cgpa)

    return projected


def batch_analyse(df: pd.DataFrame) -> pd.DataFrame:
    """
    Run full ML analysis on a batch DataFrame.
    Adds: intelligence_score, career_prediction, cluster, risk_level, fit_score
    """
    from utils.data_engine import df_to_profile
    _ensure_models_exist()

    career_model = joblib.load(CAREER_MODEL_PATH)
    le           = joblib.load(LABEL_ENCODER_PATH)
    scaler       = joblib.load(SCALER_PATH)
    clusterer    = joblib.load(CLUSTER_MODEL_PATH)

    results = []
    for _, row in df.iterrows():
        profile  = df_to_profile(row)
        fv       = get_feature_vector(profile).reshape(1, -1)

        # Career prediction
        proba    = career_model.predict_proba(fv)[0]
        top_idx  = np.argmax(proba)
        career   = le.classes_[top_idx]
        conf     = round(float(proba[top_idx]) * 100, 1)

        # Cluster
        fv_sc    = scaler.transform(fv).astype("float64")
        cluster  = int(clusterer.predict(fv_sc)[0])

        # Intelligence score (already computed in preprocessing)
        intel = float(row.get("intelligence_score", 0))

        results.append({
            "student_id":         row.get("student_id", ""),
            "name":               row.get("name", ""),
            "predicted_career":   career,
            "career_confidence":  conf,
            "cluster_id":         cluster,
            "intelligence_score": round(intel, 1),
            "risk_level":         str(row.get("risk_level", "Low")),
        })

    return pd.DataFrame(results)


def get_feature_importance() -> pd.DataFrame:
    """Return feature importance from the career classifier."""
    _ensure_models_exist()
    career_model = joblib.load(CAREER_MODEL_PATH)
    rf = career_model.named_steps["clf"]
    importances = rf.feature_importances_
    return pd.DataFrame({
        "Feature":    FEATURE_NAMES,
        "Importance": importances,
    }).sort_values("Importance", ascending=False).reset_index(drop=True)
