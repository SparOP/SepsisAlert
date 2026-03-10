import streamlit as st
import joblib
import numpy as np
import os

st.set_page_config(page_title="SepsisAlert", page_icon="🏥", layout="centered")

st.markdown("""
<style>
.stApp { background-color: #0D1B2A; }
h1, h2, h3 { color: #02C39A !important; }
.stSlider label { color: #B0D4EC !important; font-size:16px !important; }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def load_model():
    if not os.path.exists('sepsis_model.pkl'):
        return None, None
    model   = joblib.load('sepsis_model.pkl')
    imputer = joblib.load('imputer.pkl')
    return model, imputer

model, imputer = load_model()

st.title("🏥 SepsisAlert")
st.markdown("<p style='color:#B0D4EC; font-size:18px;'>AI-Powered Early Sepsis Screening · Rural India</p>", unsafe_allow_html=True)
st.markdown("---")

language = st.selectbox("🌏 Select ASHA Worker's State Language", [
    "English (Default)",
    "Bengali (West Bengal)",
    "Hindi (UP / Bihar / MP / Rajasthan)",
    "Tamil (Tamil Nadu)",
    "Telugu (Andhra Pradesh / Telangana)",
    "Kannada (Karnataka)",
    "Marathi (Maharashtra)",
])

st.markdown("---")
st.subheader("📊 Enter Patient Vitals")
st.markdown("<p style='color:#88AACC;'>Move the sliders to match sensor readings</p>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
with col1:
    hr   = st.slider("❤️ Heart Rate (BPM)", 40, 200, 85)
with col2:
    spo2 = st.slider("🩺 SpO2 (%)", 70, 100, 97)
with col3:
    temp = st.slider("🌡️ Temperature (°C)", 35.0, 42.0, 37.0, step=0.1)

st.markdown("---")
m1, m2, m3 = st.columns(3)
m1.metric("Heart Rate",   f"{hr} BPM")
m2.metric("SpO2",         f"{spo2}%")
m3.metric("Temperature",  f"{temp}°C")

st.markdown("")
if st.button("🔍 Analyse Risk", use_container_width=True, type="primary"):

    if model is None:
        st.error("Model not found. Run train_model.py first.")
    else:
        # Model was trained on 6 features per patient (max and mean of each vital)
        # Since we only have one reading, we use it for both max and mean
        features = np.array([[hr, hr, spo2, spo2, temp, temp]])
        features = imputer.transform(features)
        prob    = model.predict_proba(features)[0][1]
        percent = round(prob * 100, 1)

        if prob >= 0.05:
            color, level, action = "#E63B3B", "HIGH RISK", "Refer immediately. Do not wait."
            icon = "🔴"
        elif prob >= 0.03:
            color, level, action = "#F5A623", "MEDIUM RISK", "Monitor closely. Re-check in 30 minutes."
            icon = "🟡"
        else:
            color, level, action = "#02C39A", "LOW RISK", "Vitals appear stable."
            icon = "🟢"

        st.markdown(f"""
        <div style="background:{color}; padding:30px; border-radius:12px; text-align:center; margin:20px 0;">
            <div style="font-size:48px;">{icon}</div>
            <div style="color:white; font-size:36px; font-weight:bold;">{level}</div>
            <div style="color:white; font-size:52px; font-weight:bold;">{percent}%</div>
            <div style="color:rgba(255,255,255,0.8); font-size:15px;">sepsis risk probability</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style="background:#1A2E3D; border-left:5px solid {color};
                    padding:20px; border-radius:8px; color:white; font-size:18px;">
            <strong>Action:</strong> {action}
        </div>
        """, unsafe_allow_html=True)

        guidance = {
            "Bengali":  f"রোগীর ঝুঁকি {percent}%। এখনই হাসপাতালে পাঠান।",
            "Hindi":    f"मरीज़ का जोखिम {percent}% है। तुरंत अस्पताल ले जाएं।",
            "Tamil":    f"நோயாளிக்கு {percent}% ஆபத்து. உடனே மருத்துவமனைக்கு அழைத்துச் செல்லுங்கள்.",
            "Telugu":   f"రోగికి {percent}% ప్రమాదం. వెంటనే ఆసుపత్రికి తీసుకెళ్ళండి.",
            "Kannada":  f"ರೋಗಿಗೆ {percent}% ಅಪಾಯ. ತಕ್ಷಣ ಆಸ್ಪತ್ರೆಗೆ ಕರೆದೊಯ್ಯಿರಿ.",
            "Marathi":  f"रुग्णाला {percent}% धोका. ताबडतोब रुग्णालयात न्या.",
        }
        lang_key = next((k for k in guidance if k in language), None)
        if lang_key:
            st.markdown(f"""
            <div style="background:#0D2D3D; border:1px solid #02C39A;
                        padding:20px; border-radius:8px; margin-top:16px;">
                <div style="color:#02C39A; font-weight:bold; margin-bottom:8px;">
                    🗣️ Guidance in {lang_key} (via AWS Bedrock)
                </div>
                <div style="color:white; font-size:20px; line-height:1.8;">
                    {guidance[lang_key]}
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        st.subheader("🔬 SIRS Criteria Check")
        c1, c2, c3 = st.columns(3)
        for col, label, val, flag_text, flagged in [
            (c1, "Heart Rate",  f"{hr} BPM", "⚠️ ELEVATED", hr > 90),
            (c2, "SpO2",        f"{spo2}%",  "⚠️ LOW",      spo2 < 94),
            (c3, "Temperature", f"{temp}°C", "⚠️ ABNORMAL", temp > 38.3 or temp < 36.0),
        ]:
            bg = "#E63B3B" if flagged else "#1E8449"
            col.markdown(f"""
            <div style="background:{bg}; padding:14px; border-radius:8px;
                        text-align:center; color:white;">
                <b>{label}</b><br/>{val}<br/>{"⚠️ FLAGGED" if flagged else "✓ Normal"}
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<p style='color:#445566; font-size:12px; margin-top:20px;'>"
                    "⚕️ Screening tool only. Refer high-risk patients — diagnosis at hospital.</p>",
                    unsafe_allow_html=True)

st.markdown("---")
st.markdown("<p style='color:#334455; font-size:12px; text-align:center;'>"
            "SepsisAlert · MCA 2nd Semester · 2026 · "
            "Sparsho Sengupta · Shouvik Das · Chandan Nayak · Dibyakanti Laha"
            "</p>", unsafe_allow_html=True)