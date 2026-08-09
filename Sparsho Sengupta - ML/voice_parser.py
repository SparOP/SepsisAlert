import re
import json


def parse_voice_vitals(transcript: str) -> dict:
    """
    Takes a speech transcript string and extracts HR, SpO2, temp.

    Handles phrases like:
    - "heart rate 95 oxygen 93 temperature 38.2"
    - "HR 95 SpO2 93 temp 38"
    - "95 93 38.2" (just numbers in order)
    - "pulse 95 oxygen saturation 93 body temperature 38"
    """
    transcript = transcript.lower().strip()
    result = {"hr": None, "spo2": None, "temp": None, "raw": transcript}

    # Pattern: keyword followed by a number
    hr_patterns = r"(?:heart\s*rate|pulse|hr|bpm)\s*[:\-]?\s*(\d{2,3})"
    spo2_patterns = r"(?:spo2|oxygen|o2|saturation|spo)\s*[:\-]?\s*(\d{2,3})"
    temp_patterns = r"(?:temp(?:erature)?|fever)\s*[:\-]?\s*(\d{2}(?:\.\d)?)"

    hr_match = re.search(hr_patterns, transcript)
    spo2_match = re.search(spo2_patterns, transcript)
    temp_match = re.search(temp_patterns, transcript)

    if hr_match:
        result["hr"] = float(hr_match.group(1))
    if spo2_match:
        result["spo2"] = float(spo2_match.group(1))
    if temp_match:
        result["temp"] = float(temp_match.group(1))

    # Fallback: if no keywords found, try extracting 3 numbers in order
    # Assumes ASHA worker says: "95 93 38.2" (HR SpO2 Temp)
    if not all([result["hr"], result["spo2"], result["temp"]]):
        numbers = re.findall(r"\d+(?:\.\d+)?", transcript)
        if len(numbers) >= 3:
            result["hr"] = float(numbers[0])
            result["spo2"] = float(numbers[1])
            result["temp"] = float(numbers[2])

    return result


def validate_parsed_vitals(parsed: dict) -> list:
    errors = []
    if parsed["hr"] is None:
        errors.append(
            "Could not detect heart rate. Please say 'heart rate' followed by the number."
        )
    elif not (20 <= parsed["hr"] <= 250):
        errors.append(f"Heart rate {parsed['hr']} seems wrong. Normal range is 20-250.")

    if parsed["spo2"] is None:
        errors.append(
            "Could not detect oxygen level. Please say 'oxygen' followed by the number."
        )
    elif not (50 <= parsed["spo2"] <= 100):
        errors.append(f"Oxygen {parsed['spo2']} seems wrong. Normal range is 50-100.")

    if parsed["temp"] is None:
        errors.append(
            "Could not detect temperature. Please say 'temperature' followed by the number."
        )
    elif not (30 <= parsed["temp"] <= 45):
        errors.append(
            f"Temperature {parsed['temp']} seems wrong. Normal range is 30-45."
        )

    return errors


def lambda_handler(event, context):
    body = json.loads(event["body"])
    transcript = body.get("transcript", "")

    parsed = parse_voice_vitals(transcript)
    errors = validate_parsed_vitals(parsed)

    if errors:
        return {
            "statusCode": 400,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps(
                {
                    "error": "Could not understand vitals from voice",
                    "details": errors,
                    "raw_transcript": transcript,
                    "partial_result": parsed,
                }
            ),
        }

    return {
        "statusCode": 200,
        "headers": {"Access-Control-Allow-Origin": "*"},
        "body": json.dumps(
            {
                "hr": parsed["hr"],
                "spo2": parsed["spo2"],
                "temp": parsed["temp"],
                "raw_transcript": transcript,
            }
        ),
    }


# Local test
if __name__ == "__main__":
    tests = [
        "heart rate 95 oxygen 93 temperature 38.2",
        "HR 110 SpO2 91 temp 39",
        "pulse 85 saturation 97 fever 37.5",
        "95 93 38",  # just numbers
        "heart rate 95",  # missing spo2 and temp
    ]
    for t in tests:
        parsed = parse_voice_vitals(t)
        errors = validate_parsed_vitals(parsed)
        print(f"\nInput:  '{t}'")
        print(f"Output: HR={parsed['hr']} SpO2={parsed['spo2']} Temp={parsed['temp']}")
        if errors:
            print(f"Errors: {errors}")
        else:
            print("Status: VALID")
