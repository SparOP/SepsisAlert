import json


def validate_vitals(hr, spo2, temp):
    errors = []
    if not isinstance(hr, (int, float)):
        errors.append("Heart rate must be a number")
    elif not (20 <= hr <= 250):
        errors.append(f"Heart rate {hr} out of range (20–250 BPM)")

    if not isinstance(spo2, (int, float)):
        errors.append("SpO2 must be a number")
    elif not (50 <= spo2 <= 100):
        errors.append(f"SpO2 {spo2} out of range (50–100%)")

    if not isinstance(temp, (int, float)):
        errors.append("Temperature must be a number")
    elif not (30.0 <= temp <= 45.0):
        errors.append(f"Temperature {temp} out of range (30–45°C)")

    return errors


def lambda_handler(event, context):
    body = json.loads(event["body"])
    hr = body.get("heart_rate")
    spo2 = body.get("spo2")
    temp = body.get("temperature")

    errors = validate_vitals(hr, spo2, temp)
    if errors:
        return {
            "statusCode": 400,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps(
                {
                    "error": "Invalid vitals detected",
                    "details": errors,
                    "note": "Please re-check sensor readings or re-enter manually",
                }
            ),
        }

    # Continue to model inference below
    # imputer.transform → model.predict_proba → return probability
    # (paste rest of existing Lambda code here)
