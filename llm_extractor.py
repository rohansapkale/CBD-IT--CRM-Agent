import requests
import json

def extract_with_llm(text):
    try:
        prompt = f"""
Extract data in STRICT JSON ONLY.

No explanation.
No extra text.
No array.

Format:
{{
"name": "",
"email": "",
"company": "",
"phone": "",
"gender": "",
"job_title": ""
}}

Text: {text}
"""

        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "tinyllama",
                "prompt": prompt,
                "stream": False
            }
        )

        result = response.json()

        raw_output = result.get("response", "")
        print("LLM RAW:", raw_output)

        # 🔥 Extract only JSON part
        start = raw_output.find("{")
        end = raw_output.rfind("}") + 1

        json_str = raw_output[start:end]

        parsed = json.loads(json_str)

        return parsed

    except Exception as e:
        print("LLM ERROR:", e)
        return {}
