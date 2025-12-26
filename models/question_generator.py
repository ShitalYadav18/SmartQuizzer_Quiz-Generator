import os
import json
from typing import List, Dict

from huggingface_hub import InferenceClient

from utils.prompts import QUESTION_GEN_PROMPT
from utils.text_extraction import split_into_chunks

# Read token from environment: first HUGGINGFACEHUB_API_TOKEN, otherwise HF_TOKEN
HF_TOKEN = os.environ.get("HUGGINGFACEHUB_API_TOKEN") or os.environ.get("HF_TOKEN")

# Conversational model (Meta-Llama 3 Instruct)
MODEL_NAME = "meta-llama/Meta-Llama-3-8B-Instruct"

client = InferenceClient(model=MODEL_NAME, token=HF_TOKEN)


def call_llm_chat(prompt: str, max_tokens: int = 512, temperature: float = 0.7) -> str:
    """
    Get a chat-style completion from the LLM for a given prompt.
    """
    completion = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a helpful assistant that outputs ONLY valid JSON when asked."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        max_tokens=max_tokens,
        temperature=temperature,
    )
    return completion.choices[0].message.content


def clean_questions(questions: List[Dict]) -> List[Dict]:
    """
    Post-process generated questions and remove obviously mismatched or weak ones.
    Rules:
    - For 'who' questions, the answer should not be a number (e.g., a year).
    - For 'when' questions, the answer should contain at least one digit (e.g., a year/date).
    - The distractors list must be non-empty.
    """
    if not questions:
        return []

    cleaned: List[Dict] = []
    for q in questions:
        text = str(q.get("question", "")).strip().lower()
        ans = str(q.get("answer", "")).strip()
        distractors = [str(d).strip() for d in q.get("distractors", [])]

        if not text or not ans:
            continue
        if not distractors:
            continue

        # Drop who-questions whose answer looks numeric
        if text.startswith("who") and any(ch.isdigit() for ch in ans):
            continue

        # Drop when-questions whose answer does not contain any digit
        if text.startswith("when") and not any(ch.isdigit() for ch in ans):
            continue

        q["distractors"] = distractors
        cleaned.append(q)

    return cleaned


def generate_questions_from_text(
    text: str,
    num_questions: int = 10,
) -> List[Dict]:
    """
    Generate quiz questions from study material text.
    Each returned question should contain:
    question, answer, distractors, difficulty, topic, and type.
    """
    if not text.strip():
        return []

    chunks = split_into_chunks(text, max_tokens=800)
    if not chunks:
        return []

    questions: List[Dict] = []
    per_chunk = max(1, num_questions // max(1, len(chunks)))

    for chunk in chunks:
        prompt = QUESTION_GEN_PROMPT.format(
            context=chunk,
            num_questions=per_chunk,
        )

        try:
            raw = call_llm_chat(prompt)
        except Exception:
            # If the LLM call fails for this chunk, skip it
            continue

        # Safely extract only the JSON array/dict part
        start = raw.find("[")
        end = raw.rfind("]")
        if start == -1 or end == -1:
            # It may be a single JSON object {}
            start = raw.find("{")
            end = raw.rfind("}")
            if start == -1 or end == -1:
                continue

        json_str = raw[start : end + 1]

        try:
            data = json.loads(json_str)
        except Exception:
            # JSON parsing failed
            continue

        # Normalize: dict → list
        if isinstance(data, dict):
            data = [data]

        if not isinstance(data, list):
            continue

        for q in data:
            if not isinstance(q, dict):
                continue

            # Check required keys
            required_keys = [
                "question",
                "answer",
                "distractors",
                "difficulty",
                "topic",
                "type",
            ]
            if not all(k in q for k in required_keys):
                continue

            # Distractors must be a list
            if not isinstance(q.get("distractors"), list):
                continue

            questions.append(q)

    # Limit to the requested count and run cleaning
    questions = questions[:num_questions]
    questions = clean_questions(questions)
    return questions
