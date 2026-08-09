# SepsisAlert — Regional Language Symptom Triage Chatbot
# Rule-based scoring. No ML training needed. Deploy on Lambda.

SYMPTOM_QUESTIONS = {
    "fever": {
        "en": "Does the patient have fever (temp above 38°C)?",
        "bn": "রোগীর কি জ্বর আছে (৩৮°C এর উপরে)?",
        "hi": "क्या मरीज़ को बुखार है (38°C से ऊपर)?",
        "ta": "நோயாளிக்கு காய்ச்சல் இருக்கிறதா (38°C க்கு மேல்)?",
        "te": "రోగికి జ్వరం ఉందా (38°C పైన)?",
        "kn": "ರೋಗಿಗೆ ಜ್ವರ ಇದೆಯೇ (38°C ಮೇಲೆ)?",
        "mr": "रुग्णाला ताप आहे का (38°C पेक्षा जास्त)?",
    },
    "breathing": {
        "en": "Is the patient breathing fast or struggling to breathe?",
        "bn": "রোগী কি দ্রুত শ্বাস নিচ্ছেন বা শ্বাস নিতে কষ্ট হচ্ছে?",
        "hi": "क्या मरीज़ तेज़ सांस ले रहा है या सांस लेने में तकलीफ है?",
        "ta": "நோயாளி வேகமாக சுவாசிக்கிறாரா அல்லது சுவாசிக்க சிரமப்படுகிறாரா?",
        "te": "రోగి వేగంగా శ్వాస తీసుకుంటున్నారా లేదా శ్వాస తీసుకోవడం కష్టంగా ఉందా?",
        "kn": "ರೋಗಿ ವೇಗವಾಗಿ ಉಸಿರಾಡುತ್ತಿದ್ದಾರೆಯೇ ಅಥವಾ ಉಸಿರಾಡಲು ಕಷ್ಟಪಡುತ್ತಿದ್ದಾರೆಯೇ?",
        "mr": "रुग्ण जलद श्वास घेत आहे का किंवा श्वास घेण्यास त्रास होत आहे का?",
    },
    "confusion": {
        "en": "Is the patient confused, disoriented, or unconscious?",
        "bn": "রোগী কি বিভ্রান্ত, অজ্ঞান বা অস্থির?",
        "hi": "क्या मरीज़ भ्रमित, बेहोश या असामान्य व्यवहार कर रहा है?",
        "ta": "நோயாளி குழப்பமாக இருக்கிறாரா, திசைதிரும்பியிருக்கிறாரா அல்லது மயக்கமாக இருக்கிறாரா?",
        "te": "రోగి గందరగోళంగా, దిశాభ్రమతో లేదా స్పృహలేకుండా ఉన్నారా?",
        "kn": "ರೋಗಿ ಗೊಂದಲದಲ್ಲಿದ್ದಾರೆಯೇ, ದಿಕ್ಕುತಪ್ಪಿದ್ದಾರೆಯೇ ಅಥವಾ ಪ್ರಜ್ಞೆ ಕಳೆದುಕೊಂಡಿದ್ದಾರೆಯೇ?",
        "mr": "रुग्ण गोंधळलेला, दिशाभूल झालेला किंवा बेशुद्ध आहे का?",
    },
    "cold_skin": {
        "en": "Is the patient's skin cold, pale, or clammy?",
        "bn": "রোগীর ত্বক কি ঠান্ডা, ফ্যাকাশে বা ঘামে ভেজা?",
        "hi": "क्या मरीज़ की त्वचा ठंडी, पीली या पसीने से भीगी है?",
        "ta": "நோயாளியின் தோல் குளிர்ச்சியாக, வெளிறியதாக அல்லது வியர்வையாக இருக்கிறதா?",
        "te": "రోగి చర్మం చల్లగా, పాలిపోయి లేదా చెమటతో తడిగా ఉందా?",
        "kn": "ರೋಗಿಯ ಚರ್ಮ ತಣ್ಣಗೆ, ಬಿಳಿಚಿಕೊಂಡಿದೆ ಅಥವಾ ಬೆವರಿದೆಯೇ?",
        "mr": "रुग्णाची त्वचा थंड, फिकट किंवा घामाने ओली आहे का?",
    },
    "no_urination": {
        "en": "Has the patient not urinated in the last 8 hours?",
        "bn": "রোগী কি গত ৮ ঘণ্টায় প্রস্রাব করেননি?",
        "hi": "क्या मरीज़ ने पिछले 8 घंटों में पेशाब नहीं किया?",
        "ta": "கடந்த 8 மணி நேரத்தில் நோயாளி சிறுநீர் கழிக்கவில்லையா?",
        "te": "రోగి గత 8 గంటలలో మూత్రం పోయలేదా?",
        "kn": "ಕಳೆದ 8 ಗಂಟೆಗಳಲ್ಲಿ ರೋಗಿ ಮೂತ್ರ ವಿಸರ್ಜಿಸಿಲ್ಲವೇ?",
        "mr": "रुग्णाने गेल्या 8 तासांत लघवी केली नाही का?",
    },
}

LANG_CODES = {
    "Bengali": "bn",
    "Hindi": "hi",
    "Tamil": "ta",
    "Telugu": "te",
    "Kannada": "kn",
    "Marathi": "mr",
    "English": "en",
}

REFER_MSG = {
    "en": "Based on symptoms, this patient needs immediate assessment. Please use the SepsisAlert sensor now.",
    "bn": "উপসর্গের ভিত্তিতে, এই রোগীর তাৎক্ষণিক মূল্যায়ন প্রয়োজন। এখনই SepsisAlert সেন্সর ব্যবহার করুন।",
    "hi": "लक्षणों के आधार पर इस मरीज़ को तुरंत जांच की जरूरत है। अभी SepsisAlert सेन्सर इस्तेमाल करें।",
    "ta": "அறிகுறிகளின் அடிப்படையில், இந்த நோயாளிக்கு உடனடி மதிப்பீடு தேவை। இப்போதே SepsisAlert சென்சரைப் பயன்படுத்தவும்.",
    "te": "లక్షణాల ఆధారంగా, ఈ రోగికి తక్షణ అంచనా అవసరం. ఇప్పుడే SepsisAlert సెన్సర్ ఉపయోగించండి.",
    "kn": "ರೋಗಲಕ್ಷಣಗಳ ಆಧಾರದ ಮೇಲೆ, ಈ ರೋಗಿಗೆ ತಕ್ಷಣ ಮೌಲ್ಯಮಾಪನ ಅಗತ್ಯ. ಈಗಲೇ SepsisAlert ಸೆನ್ಸರ್ ಬಳಸಿ.",
    "mr": "लक्षणांच्या आधारे, या रुग्णाला तात्काळ मूल्यमापन आवश्यक आहे. आत्ताच SepsisAlert सेन्सर वापरा.",
}

SAFE_MSG = {
    "en": "Symptoms appear mild. Monitor the patient and check again if condition worsens.",
    "bn": "উপসর্গ হালকা মনে হচ্ছে। রোগীকে পর্যবেক্ষণ করুন এবং অবস্থা খারাপ হলে আবার পরীক্ষা করুন।",
    "hi": "लक्षण हल्के लगते हैं। मरीज़ की निगरानी करें और स्थिति बिगड़ने पर फिर जांचें।",
    "ta": "அறிகுறிகள் லேசாக தெரிகின்றன. நோயாளியை கண்காணிக்கவும், நிலை மோசமடைந்தால் மீண்டும் சரிபார்க்கவும்.",
    "te": "లక్షణాలు తేలికగా కనిపిస్తున్నాయి. రోగిని పర్యవేక్షించండి మరియు పరిస్థితి దిగజారితే మళ్ళీ తనిఖీ చేయండి.",
    "kn": "ರೋಗಲಕ್ಷಣಗಳು ಸೌಮ್ಯವಾಗಿ ಕಾಣುತ್ತವೆ. ರೋಗಿಯನ್ನು ಮೇಲ್ವಿಚಾರಣೆ ಮಾಡಿ ಮತ್ತು ಸ್ಥಿತಿ ಹದಗೆಟ್ಟರೆ ಮತ್ತೆ ಪರಿಶೀಲಿಸಿ.",
    "mr": "लक्षणे सौम्य वाटतात. रुग्णावर लक्ष ठेवा आणि स्थिती बिघडल्यास पुन्हा तपासा.",
}


def score_symptoms(answers: dict) -> int:
    # Each Yes = 1 point. Score >= 2 → refer for sensor assessment
    return sum(1 for v in answers.values() if v is True)


def get_recommendation(score: int, lang_code: str) -> dict:
    if score >= 2:
        return {
            "score": score,
            "action": "REFER_FOR_SENSOR",
            "message": REFER_MSG.get(lang_code, REFER_MSG["en"]),
        }
    return {
        "score": score,
        "action": "MONITOR",
        "message": SAFE_MSG.get(lang_code, SAFE_MSG["en"]),
    }


def get_questions(language: str) -> list:
    lang_code = LANG_CODES.get(language, "en")
    return [
        {"symptom": key, "question": val.get(lang_code, val["en"])}
        for key, val in SYMPTOM_QUESTIONS.items()
    ]


# ── Lambda handler ────────────────────────────────────────────
def lambda_handler(event, context):
    import json

    body = json.loads(event["body"])
    language = body.get("language", "English")
    answers = body.get("answers", {})
    # answers = {"fever": True, "breathing": False, "confusion": True, ...}

    lang_code = LANG_CODES.get(language, "en")
    score = score_symptoms(answers)
    result = get_recommendation(score, lang_code)

    return {
        "statusCode": 200,
        "headers": {"Access-Control-Allow-Origin": "*"},
        "body": json.dumps(result),
    }


# ── Local test ────────────────────────────────────────────────
if __name__ == "__main__":
    print("Questions in Hindi:")
    for q in get_questions("Hindi"):
        print(f"  {q['symptom']}: {q['question']}")

    test_answers = {
        "fever": True,
        "breathing": True,
        "confusion": False,
        "cold_skin": False,
        "no_urination": False,
    }
    result = get_recommendation(score_symptoms(test_answers), "hi")
    print(f"\nScore: {result['score']}")
    print(f"Action: {result['action']}")
    print(f"Message: {result['message']}")
