from typing import List, Dict, Optional
import random

DIFFICULTY_LEVELS = ["easy", "medium", "hard"]

class AdaptiveEngine:
    def __init__(self, questions: List[Dict]):
        self.questions = questions
        self.history: List[Dict] = []
        self.current_difficulty = "medium"

    def _get_pool(self, difficulty: str) -> List[Dict]:
        return [q for q in self.questions if q.get("difficulty") == difficulty]

    def select_next_question(self) -> Optional[Dict]:
        pool = self._get_pool(self.current_difficulty)
        if not pool:
            pool = self.questions
        if not pool:
            return None
        question = random.choice(pool)
        return question

    def record_answer(self, question: Dict, is_correct: bool, response_time: float):
        entry = {
            "question_id": id(question),
            "difficulty": question.get("difficulty"),
            "is_correct": is_correct,
            "response_time": response_time,
        }
        self.history.append(entry)
        self._update_difficulty(is_correct)

    def _update_difficulty(self, is_correct: bool):
        idx = DIFFICULTY_LEVELS.index(self.current_difficulty)
        if is_correct and idx < len(DIFFICULTY_LEVELS) - 1:
            self.current_difficulty = DIFFICULTY_LEVELS[idx + 1]
        elif not is_correct and idx > 0:
            self.current_difficulty = DIFFICULTY_LEVELS[idx - 1]
