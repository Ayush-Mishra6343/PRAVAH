import os
from pathlib import Path
from sarvamai import SarvamAI

# Load .env if present
env_file = Path(__file__).resolve().parent / ".env"
if env_file.is_file():
    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, val = line.split("=", 1)
            key, val = key.strip(), val.strip().strip("'\"")
            if val and key not in os.environ:
                os.environ[key] = val

api_key = os.getenv("SARVAM_API_KEY")
if not api_key:
    raise ValueError("SARVAM_API_KEY is not set. Please set it in your .env file or environment.")

client = SarvamAI(api_subscription_key=api_key)

response = client.chat.completions(
    model="sarvam-105b-conversations",
    messages=[
        {"role": "user", "content": "Hello! Introduce yourself in one short sentence."}
    ],
)

print(response.choices[0].message.content)
