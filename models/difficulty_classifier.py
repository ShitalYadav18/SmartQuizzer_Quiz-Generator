import os
from typing import Dict

from huggingface_hub import InferenceClient

from utils.prompts import DIFFICULTY_CLASS_PROMPT

# Read token from environment: first HUGGINGFACEHUB_API_TOKEN, otherwise HF_TOKEN
HF_TOKEN = os.environ.get("HUGGINGFACEHUB_API_TOKEN") or os.environ.get("HF_TOKEN")

MODEL_NAME = "meta-llama/Meta-Llama-3-8B-Instruct"  # conversational model

client = InferenceClient(model=MODEL_NAME, token=HF_TOKEN)


def classify_question_difficulty(question_item: Dict) -> str:
    """
    Assign a difficulty label (easy/medium/hard) based on the question text.
    """
    prompt = DIFFICULTY_CLASS_PROMPT.format(question=question_item["question"])

    completion = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": "Return only one word: easy, medium, or hard."},
            {"role": "user", "content": prompt},
        ],
        max_tokens=5,
        temperature=0.0,
    )
    text = completion.choices[0].message.content
    label = text.strip().lower()

    if "easy" in label:
        label = "easy"
    elif "hard" in label:
        label = "hard"
    else:
        label = "medium"

    question_item["difficulty"] = label
    return label
