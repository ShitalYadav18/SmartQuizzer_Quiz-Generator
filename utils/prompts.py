QUESTION_GEN_PROMPT = """
You are an expert exam question generator.

Given the following study material, generate {num_questions} questions in JSON list.
Each item must have:
- question (string)
- answer (string)
- distractors (list of 3 strings)
- difficulty (one of: "easy", "medium", "hard")
- topic (short topic name)
- type (one of: "mcq", "true_false", "short_answer", "fill_blank")

Very important rules:
- For 'Who' questions, answer and all distractors must be PERSON names.
- For 'When' questions, answer and all distractors must be years or dates.
- For 'Where' questions, answer and all distractors must be places/locations.
- For 'What' or 'Which' questions, answer and distractors must be the same type of thing.
- Never mix different kinds of answers in the same question.

Return ONLY valid JSON array, no extra text.

Study material:
\"\"\"{context}\"\"\"
"""
