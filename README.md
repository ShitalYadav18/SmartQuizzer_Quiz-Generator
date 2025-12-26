# 🧠 SmartQuizzer – Adaptive AI-Based Quiz Generator

SmartQuizzer is an **AI-powered quiz generation system** built using **Python and Streamlit**.  
The application analyzes study materials (PDF/Text), automatically generates quiz questions using **Large Language Models (LLMs)**, and provides difficulty-aware quizzes with performance insights. 

This project was developed as part of an **Internship Project**, focusing on practical implementation of **AI, NLP, and learning analytics**. 

---

## 📌 Project Description

Traditional quizzes are static and often fail to adapt to a learner’s understanding.  
**SmartQuizzer** addresses this by creating a more **personalized assessment experience**, where questions are generated from the user’s own study material and tagged with difficulty levels. 

The system combines **AI-based question generation**, **difficulty classification**, and **performance analytics** within an interactive **Streamlit web application**. 

---

## 🎯 Internship Objectives

- Implement AI-driven quiz generation using Python and LLMs  
- Apply NLP concepts (text extraction, cleaning, prompt design) to real study material  
- Design and implement a difficulty-aware quiz experience  
- Build an end-to-end Streamlit-based application with analytics and clean UI [file:43]

---

## ✨ Features

- 📄 Upload **PDF / Text** study materials  
- 🤖 AI-generated quiz questions:  
- Multiple-choice questions (MCQ)  
- True/False and short-answer style questions (depending on LLM output and prompts)  
- 🧠 Difficulty labels for each question (Easy / Medium / Hard)  
- 📝 Quiz interface with timer, question navigation, and inline feedback  
- 📊 Performance analytics: score, accuracy, difficulty progression, topic-wise performance  
- 💾 Local data storage using JSON for generated questions and quiz attempts  
- 🖥 Clean, minimal, and interactive Streamlit UI suitable for internship evaluation 

---

## 🛠 Tech Stack

- **Programming Language:** Python  
- **Web Framework:** Streamlit  
- **AI / NLP:**  
  - Large Language Model: *Meta-Llama-3-8B-Instruct* via Hugging Face Inference API  
  - Prompt Engineering for question generation and difficulty classification  
- **Data Processing:** Python text processing utilities, basic Pandas in analytics  
- **Visualization:** Plotly line and bar charts  
- **Storage:** Local JSON file (`data/questions.json`) for questions and quiz history 

---

## 🧩 Application Workflow

### 1️⃣ Document Upload & Text Extraction
- User uploads a PDF file containing study material  
- Text is extracted and cleaned (removing noise and formatting) to prepare it for the LLM [file:43]

### 2️⃣ AI Content Understanding & Question Generation
- A structured prompt is sent to the LLM asking it to generate questions in **valid JSON format**  
- Each generated item contains fields such as `question`, `answer`, `distractors`, `difficulty`, `topic`, and `type` [file:43]  
- A post-processing step removes clearly invalid or mismatched questions

### 3️⃣ Difficulty Tagging
- Questions are assigned difficulty labels such as **easy**, **medium**, or **hard** based on their content  
- These labels are later used in analytics and can be extended to drive adaptive logic 

### 4️⃣ Quiz Experience
  - The user starts a quiz from the generated question set in the **Quiz** tab  
  - For each question, the app:
  - Displays the question text, topic, and difficulty  
  - Presents shuffled answer options (correct answer + distractors)  
  - Records correctness and response time on submission

### 5️⃣ Analytics & Feedback
  - In the **Analytics** tab, the app computes and visualizes:
  - Total score and accuracy  
  - Difficulty progression over the attempted questions  
  - Topic-wise accuracy and weak topics  
  - A recommendation message is generated based on overall performance (revise basics, focus on medium topics, or attempt more difficult questions) 

---

## 📂 Project Structure

SmartQuizzer/
│
├── app.py
│   └── Main Streamlit application entry point
│
├── models/
│   ├── question_generator.py
│   │   └── AI-based quiz question generation logic
│   │
│   ├── difficulty_classifier.py
│   │   └── Classifies questions into Easy / Medium / Hard
│   │
│   └── adaptive_engine.py
│       └── Adaptive logic to adjust quiz difficulty based on user performance
│
├── services/
│   ├── analytics.py
│   │   └── Score calculation, accuracy, topic-wise & difficulty analysis
│   │
│   └── storage.py
│       └── Handles reading/writing questions and results to JSON storage
│
├── utils/
│   ├── text_extraction.py
│   │   └── PDF/text extraction and preprocessing utilities
│   │
│   └── prompts.py
│       └── Prompt templates for LLM-based question generation and classification
│
├── data/
│   └── questions.json
│       └── Stores generated questions (created at runtime)
│
├── requirements.txt
│   └── List of required Python dependencies
│
└── README.md
    └── Project documentation



---

## 📥 Example Question Object

The LLM is instructed to return questions in JSON objects like the following:
{
"question": "What does AI simulate?",
"answer": "Human intelligence",
"distractors": [
"Machine behavior",
"Animal instincts",
"Natural processes"
],
"difficulty": "easy",
"topic": "Artificial Intelligence",
"type": "mcq"
}

This format allows the app to automatically build MCQ options, tag difficulty, and group analytics by topic. 

---

## 🚀 How to Run the Project

### 1️⃣ Clone the Repository
### 2️⃣ (Optional) Create Virtual Environment
### 3️⃣ Install Dependencies
pip install -r requirements.txt

### 4️⃣ Set Up LLM API Access

- Create a Hugging Face access token and set it as an environment variable:  
  - `HF_TOKEN`  
- The app uses this token to call the **Meta-Llama-3-8B-Instruct** model for question generation and difficulty classification.

### 5️⃣ Run the Streamlit Application
python -m streamlit run app.py


- Open the local URL shown in the terminal .  
- Use the **Upload & Generate** tab to upload a PDF and generate questions.  
- Switch to the **Quiz** tab to attempt the quiz.  
- View performance in the **Analytics** tab.

---

## 📌 Future Enhancements

- Fully adaptive quiz path that changes difficulty based on recent answers in real time  
- Support for additional input formats (multiple PDFs, plain text, URLs)  
- Persistent storage using MongoDB instead of local JSON files  
- Exportable reports for learners or teachers (PDF/CSV dashboards)


