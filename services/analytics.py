from typing import List, Dict
import pandas as pd


def compute_accuracy(history: List[Dict]) -> float:
    if not history:
        return 0.0
    correct = sum(1 for h in history if h["is_correct"])
    return correct / len(history)


def difficulty_progression(history: List[Dict]) -> List[str]:
    return [h["difficulty"] for h in history]


def average_response_time(history: List[Dict]) -> float:
    if not history:
        return 0.0
    return sum(h["response_time"] for h in history) / len(history)


def total_score(history: List[Dict], mark_per_question: int = 1) -> int:
    return sum(mark_per_question for h in history if h["is_correct"])


def topic_wise_performance(history: List[Dict]) -> pd.DataFrame:
    """
    Each history entry is expected to contain a 'topic' field copied from the question at quiz time.
    """
    if not history:
        return pd.DataFrame(columns=["topic", "attempts", "correct", "accuracy"])

    rows = []
    for h in history:
        rows.append(
            {
                "topic": h.get("topic", "Unknown"),
                "is_correct": h["is_correct"],
            }
        )

    df = pd.DataFrame(rows)
    grouped = df.groupby("topic").agg(
        attempts=("is_correct", "count"),
        correct=("is_correct", "sum"),
    )
    grouped["accuracy"] = grouped["correct"] / grouped["attempts"]
    grouped = grouped.reset_index()
    return grouped


def hardest_topics(df: pd.DataFrame, top_k: int = 3) -> List[str]:
    """
    Return the topics with the lowest accuracy.
    """
    if df.empty:
        return []
    df_sorted = df.sort_values("accuracy").head(top_k)
    return df_sorted["topic"].tolist()


def generate_recommendation(history: List[Dict]) -> str:
    acc = compute_accuracy(history)
    if acc < 0.5:
        return "Overall accuracy is low. Revise basic topics first and practice more easy questions."
    if acc < 0.8:
        return "Performance is moderate. Revisit medium-level topics and review your incorrect attempts."
    return "You are performing very well. Focus on more hard-level questions to achieve mastery."
