from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import joblib, numpy as np, os, requests, json

app = FastAPI(title="Blood Donation ML Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.environ.get("CORS_ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:8080").split(","),
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

# Load models
BASE = os.path.dirname(os.path.abspath(__file__))
MODELS = os.path.join(BASE, "models")

donor_model    = joblib.load(os.path.join(MODELS, "donor_model.pkl"))
stock_model    = joblib.load(os.path.join(MODELS, "stock_model.pkl"))
location_model = joblib.load(os.path.join(MODELS, "location_model.pkl"))
location_data  = joblib.load(os.path.join(MODELS, "location_data.pkl"))

print("✅ All 4 ML models loaded successfully")

# ─────────────────────────────────────────────────────────────────────────────
# HUGGINGFACE KEY SETUP:
# 1. Go to https://huggingface.co → Sign Up (free)
# 2. Click Profile → Settings → Access Tokens → New Token → Read → Generate
# 3. Copy token (starts with hf_...)
# 4. Set it in the environment: HF_API_KEY=hf_... (see .env.example)
# The chatbot works WITHOUT this key using the smart fallback below
# ─────────────────────────────────────────────────────────────────────────────
HF_KEY = os.environ.get("HF_API_KEY", "")  # never write the key in the code
HF_URL = "https://api-inference.huggingface.co/models/HuggingFaceH4/zephyr-7b-beta:featherless-ai"

BG_MAP = {"A+":0,"A-":1,"B+":2,"B-":3,"AB+":4,"AB-":5,"O+":6,"O-":7}
CITY_MAP = {
    "Chennai":0,"Mumbai":1,"Delhi":2,"Hyderabad":3,"Bangalore":4,"Pune":5,
    "Kochi":6,"Coimbatore":7,"Madurai":8,"Trichy":9,"Salem":10,
    "Vellore":11,"Erode":12,"Tirupur":13,"Tirunelveli":14
}

class DonorIn(BaseModel):
    age: int
    total_donations: int
    days_since_last: int
    blood_group: Optional[str] = "A+"
    city: Optional[str] = "Chennai"

class StockIn(BaseModel):
    current_units: float
    daily_usage: float
    camps_this_month: int
    season: Optional[str] = "Summer"

class LocIn(BaseModel):
    lat: float
    lon: float
    donor_density: Optional[int] = 50

class ChatIn(BaseModel):
    message: str
    context: Optional[str] = ""

@app.get("/")
def root():
    return {"status": "Blood Donation ML Service running OK ✅", "models": "loaded"}

@app.get("/health")
def health():
    return {"status": "healthy", "models_loaded": True}

@app.post("/predict-donor")
def predict_donor(d: DonorIn):
    try:
        f = np.array([[
            d.age, d.total_donations, d.days_since_last,
            BG_MAP.get(d.blood_group, 0), CITY_MAP.get(d.city, 0)
        ]])
        prob = float(donor_model.predict_proba(f)[0][1])
        ret  = bool(donor_model.predict(f)[0])
        if   prob >= 0.75: rec = "🟢 High likelihood. Send a personalized SMS reminder."
        elif prob >= 0.45: rec = "🟡 Moderate chance. Send awareness campaign message."
        else:              rec = "🔴 Low chance. Engage with incentives or drive campaign."
        return {
            "will_return": ret,
            "probability": round(prob, 3),
            "probability_percent": f"{round(prob * 100, 1)}%",
            "label": "Likely to return" if ret else "May not return",
            "recommendation": rec
        }
    except Exception as e:
        return {"error": str(e)}

@app.post("/predict-stock")
def predict_stock(d: StockIn):
    try:
        sm = {"Spring":0,"Summer":1,"Autumn":2,"Winter":3}
        f  = np.array([[d.current_units, d.daily_usage, d.camps_this_month, sm.get(d.season, 1)]])
        pred = max(0.0, float(stock_model.predict(f)[0]))
        if   pred < 5:  level, rec = "CRITICAL", "🚨 EMERGENCY: Organise blood drive immediately!"
        elif pred < 10: level, rec = "WARNING",  "⚠️ Schedule a camp within 5-7 days."
        elif pred < 20: level, rec = "LOW",      "📅 Plan a camp within 2 weeks."
        else:           level, rec = "NORMAL",   "✅ Stock levels are healthy."
        return {
            "predicted_units_7d": round(pred, 2),
            "current_units": d.current_units,
            "is_shortage_alert": pred < 10,
            "alert_level": level,
            "recommendation": rec
        }
    except Exception as e:
        return {"error": str(e)}

@app.post("/recommend-location")
def recommend_location(d: LocIn):
    try:
        pt = np.array([[d.lat, d.lon, d.donor_density]])
        cluster = int(location_model.predict(pt)[0])
        center  = location_model.cluster_centers_[cluster]
        labels  = location_model.labels_
        cluster_df = location_data.iloc[[i for i, l in enumerate(labels) if l == cluster]]
        avg = float(cluster_df["donor_density"].mean())
        return {
            "recommended_cluster": cluster,
            "center_lat": round(float(center[0]), 4),
            "center_lon": round(float(center[1]), 4),
            "expected_turnout": int(avg * 1.3),
            "avg_donor_density": round(avg, 1),
            "recommendation": f"Cluster {cluster} near ({center[0]:.3f}, {center[1]:.3f}) — expected {int(avg*1.3)} donors."
        }
    except Exception as e:
        return {"error": str(e)}

@app.post("/chat")
def chat(d: ChatIn):
    msg = d.message.lower().strip()

    # Try HuggingFace only if a real key is provided
    if HF_KEY and HF_KEY != "hf_PASTE_YOUR_KEY_HERE" and len(HF_KEY) > 20:
        try:
            prompt = f"""<|system|>
You are a helpful blood bank assistant. Answer questions about blood donation, blood groups, eligibility, camps, and stock management. Keep answers under 3 sentences and factual.
Context: {d.context}
</s>
<|user|>
{d.message}
</s>
<|assistant|>"""
            headers = {"Authorization": f"Bearer {HF_KEY}", "Content-Type": "application/json"}
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": 200,
                    "temperature": 0.6,
                    "return_full_text": False,
                    "stop": ["</s>", "<|user|>"]
                }
            }
            resp = requests.post(HF_URL, headers=headers, json=payload, timeout=20)
            result = resp.json()
            if isinstance(result, list) and result and result[0].get("generated_text", "").strip():
                answer = result[0]["generated_text"].strip()
                return {"reply": answer, "source": "huggingface"}
        except Exception as e:
            print(f"HuggingFace error: {e}")

    # ── SMART RULE-BASED FALLBACK (always works, no key needed) ──────────────
    # Blood group questions
    if any(w in msg for w in ["o-","o negative","universal donor"]):
        reply = "O- (O negative) is the universal donor blood group. It can be given to anyone regardless of their blood type. It's critical for emergencies when there's no time to type a patient's blood. O- makes up about 7% of the population."
    elif any(w in msg for w in ["ab+","ab positive","universal recipient"]):
        reply = "AB+ (AB positive) is the universal recipient — people with this blood type can receive blood from ANY donor. AB+ individuals can also donate plasma to anyone. About 3.4% of people have AB+ blood."
    elif any(w in msg for w in ["o+","o positive"]):
        reply = "O+ (O positive) is the most common blood group, found in about 38% of people. O+ can be given to any Rh-positive patient, which covers ~85% of the population. It's in highest demand in hospitals."
    elif any(w in msg for w in ["ab-","ab negative"]):
        reply = "AB- is the rarest blood group, found in only about 1% of people. AB- individuals can donate red cells to other AB patients and platelets/plasma to all blood types."
    elif any(w in msg for w in ["blood group","blood type","which group","a+","a-","b+","b-"]):
        reply = "The 8 blood groups are: A+, A-, B+, B-, AB+, AB-, O+, O-. O- is the universal donor (given to anyone). AB+ is the universal recipient. O+ is the most common (38%). AB- is the rarest (1%). Always verify compatibility before transfusion."

    # Eligibility questions
    elif any(w in msg for w in ["eligible","can i donate","when can i","90 day","how often","donate again","next donation"]):
        reply = "You can donate blood if: ✅ Age 18-65 years, ✅ Weight above 50kg, ✅ At least 90 days since your last donation, ✅ No recent illness, fever, or medication. Whole blood can be donated every 3 months (90 days). Platelets can be donated every 2 weeks."

    # Stock/shortage questions
    elif any(w in msg for w in ["low","shortage","critical","stock","urgent","empty","running out"]):
        reply = "Blood stock levels are monitored in real-time on the dashboard. O- and AB- are most frequently at critical levels due to their rarity. O+ is always in high demand. When any group falls below the critical threshold, automatic alerts are triggered. Check the Hospital Admin dashboard for live stock data."

    # Camp questions
    elif any(w in msg for w in ["camp","location","next camp","organise","organize","where","schedule"]):
        reply = "Blood donation camps are organised at hospitals, colleges, and community centres. The ML Location Recommender uses KMeans clustering on donor density data to suggest optimal camp locations. Upcoming camps are shown on the Dashboard. Contact a Camp Coordinator to register a new camp."

    # Certificate questions
    elif any(w in msg for w in ["certificate","proof","document","receipt"]):
        reply = "Donation certificates are issued after each successful blood donation. You can view and download your certificates from the Donor Dashboard under 'Donation History'. Each certificate includes the date, blood group, camp location, and donation ID."

    # Process/how to donate
    elif any(w in msg for w in ["how to donate","process","steps","procedure","what happens"]):
        reply = "Blood donation process: 1️⃣ Register and check eligibility (90-day gap required). 2️⃣ Fill a health questionnaire. 3️⃣ Brief health check (BP, haemoglobin). 4️⃣ Blood drawn (~10 minutes, 350-450mL). 5️⃣ Rest 10-15 minutes with refreshments. The whole process takes about 30-45 minutes."

    # Benefits
    elif any(w in msg for w in ["benefit","why donate","help","save","impact"]):
        reply = "Benefits of donating blood: ❤️ One donation saves up to 3 lives. 🩺 Free mini health check-up. 💪 Stimulates new blood cell production. 🏥 Reduces iron levels (may lower heart disease risk). 😊 Psychological benefit of helping others. India needs 14.6 million units annually — every donor matters!"

    # Greeting
    elif any(w in msg for w in ["hello","hi","hey","good morning","good evening","help"]):
        reply = "Hello! 👋 I'm your BloodBank AI Assistant. I can help you with:\n🩸 Blood group information & compatibility\n✅ Donation eligibility checks\n🏕️ Camp locations & schedules\n📊 Blood stock levels\n📜 Donation certificates\n\nWhat would you like to know?"

    # Thank you
    elif any(w in msg for w in ["thank","thanks","great","awesome","good"]):
        reply = "You're welcome! 😊 Remember, donating blood is one of the most impactful things you can do. Every unit donated can save up to 3 lives. Is there anything else I can help you with?"

    # Default
    else:
        reply = f"I received your question: '{d.message}'\n\nI can help with: 🩸 Blood group info | ✅ Eligibility | 🏕️ Camp locations | 📊 Stock levels | 📜 Certificates\n\nCould you rephrase your question? For example: 'Which blood group is rarest?' or 'How often can I donate?'"

    return {"reply": reply, "source": "smart-fallback"}
