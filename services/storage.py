import json
from typing import List, Dict
from pathlib import Path

BASE_DIR = Path("data")
QUESTIONS_PATH = BASE_DIR / "questions.json"


def save_questions_json(questions: List[Dict]):
    BASE_DIR.mkdir(parents=True, exist_ok=True)
    with open(QUESTIONS_PATH, "w", encoding="utf-8") as f:
        json.dump(questions, f, ensure_ascii=False, indent=2)


def load_questions_json() -> List[Dict]:
    # Debug line: prints the path and whether it exists
    print("DEBUG QUESTIONS_PATH:", QUESTIONS_PATH, QUESTIONS_PATH.exists())

    if not QUESTIONS_PATH.exists():
        return []  # file does not exist

    with open(QUESTIONS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Safety: always return a list
    if not isinstance(data, list):
        return []

    return data
