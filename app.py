
import time
import random

import pandas as pd
import plotly.express as px
import streamlit as st


from utils.text_extraction import extract_text_from_pdf, clean_text
from models.question_generator import generate_questions_from_text
from services.storage import save_questions_json, load_questions_json
from services.analytics import (
    compute_accuracy,
    average_response_time,
    total_score,
    difficulty_progression,
    topic_wise_performance,
    hardest_topics,
    generate_recommendation,
)

# -------------------- PAGE CONFIG --------------------

st.set_page_config(page_title="SmartQuizzer", layout="wide")

# -------------------- GLOBAL THEME & CSS --------------------

base_css = """
<style>

/* ---------------- STREAMLIT DEFAULT BARS REMOVE ---------------- */
header[data-testid="stHeader"],
div[data-testid="stToolbar"] {
    display: none !important;
}

/* ---------------- MAIN CONTAINER ---------------- */
.block-container {
    padding-top: 0rem !important;
    padding-bottom: 1.0rem;
    max-width: 1100px;
}

/* ---------------- HEADINGS ---------------- */
h1 {
    font-weight: 800 !important;
    letter-spacing: 0.03em;
}

h3 {
    margin-top: 0.1rem !important;
    margin-bottom: 0.15rem !important;
}

/* ---------------- TABS ---------------- */
.stTabs [data-baseweb="tab-list"] {
    gap: 0.6rem;
}

.stTabs [data-baseweb="tab"] {
    border-radius: 999px;
    padding: 0.35rem 1.1rem;
    background-color: #020617;
    border: 1px solid #1f2937;
    color: #9ca3af;
    font-size: 0.95rem;
    font-weight: 600;
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #4f46e5, #7c3aed);
    color: #f9fafb;
    border-color: transparent;
}

div[data-baseweb="tab-highlight"],
div[data-baseweb="tab-border"] {
    display: none !important;
}

/* Hide top strip */
.top-bar, .header, .quiz-header {
    display: none !important;
}

/* Hide right panel / sidebar */
.session-overview, .sidebar {
    display: none !important;
}
/* Hide top strip */
.top-bar, .header, .quiz-header {
    display: none !important;
}

/* Hide right panel / sidebar */
.session-overview, .sidebar {
    display: none !important;
}

/* Quiz heading ke neeche aane wali pahli full-width strip hide */
h2:has(span:contains("Quiz session")) + div {
    display: none !important;
}


/* Tab 2 ki body ko thoda upar lao */
div[data-baseweb="tab-panel"]:nth-of-type(2) .block-container {
    margin-top: -2rem;
}


.quiz-container {
    width: 100% !important;
    margin: 0 auto;
}

/* ---------------- QUESTION CARD ---------------- */
.question-card {
    padding: 1.8rem 1.8rem;
    border-radius: 1.4rem;
    background: #020617;
    border: 1px solid #111827;
    margin-top: 0rem;
    margin-bottom: 0.5rem;
}
/* ---------------- ANSWER SPACING (KEY FIX) ---------------- */
.answer-label {
    font-size: 1.05rem;
    font-weight: 600;
    margin-top: 0rem;
    margin-bottom: 0rem;
}

.stRadio {
    margin-top: -0.35rem !important;
}

.stRadio div[role="radiogroup"] label {
    font-size: 1.02rem;
    padding: 0.2rem 0.1rem;
}

/* ---------------- INFO CARD ---------------- */
.info-card {
    padding: 0.6rem 0.8rem; /* reduce padding */
    margin-top: 0 !important; /* remove extra space above */
    border-radius: 1rem;
    background-color: #020617;
    border: 1px solid #111827;
}

/* ---------------- BUTTONS ---------------- */
.stButton > button {
    border-radius: 999px;
    font-weight: 600;
}


/* Pure page ka top gap almost zero */
.block-container {
    padding-top: 0rem !important;
}

/* Block-container ke andar sabse pehla wrapper collapse karo */
.block-container > div:nth-of-type(1) {
    margin-top: 0 !important;
    padding-top: 0 !important;
    height: auto !important;
}

/* Tabs ke baad aane wala extra wrapper bhi collapse */
.block-container > div:nth-of-type(2) {
    margin-top: 0 !important;
    padding-top: 0 !important;
}


/* Quiz tab me tabs ke neeche aane wala pehla empty wrapper hatao */
div[data-baseweb="tab-panel"]:nth-of-type(2) > div > div:nth-of-type(1) {
    margin-top: 0 !important;
    padding-top: 0 !important;
    height: 0 !important;
    overflow: hidden !important;
}


</style>
"""

st.markdown(base_css, unsafe_allow_html=True)


# -------------------- HELPERS --------------------

def clean_questions(questions):
    """Remove invalid questions (empty text/answer or missing distractors)."""
    if not questions:
        return []

    cleaned = []
    for q in questions:
        text = str(q.get("question", "")).strip()
        ans = str(q.get("answer", "")).strip()
        distractors = [str(d).strip() for d in q.get("distractors", [])]

        if not text or not ans:
            continue
        if not distractors:
            continue

        q["distractors"] = distractors
        cleaned.append(q)

    return cleaned


# -------------------- HEADER --------------------

st.markdown(
    """
    <div style="text-align:center; margin-bottom: 1rem;">
        <h1>SmartQuizzer</h1>
        <p style="color:#9ca3af; margin-top:0.2rem;">
            Adaptive AI-based quiz generator 
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

tab1, tab2, tab3 = st.tabs(["⚙️ Upload & Generate", "📝 Quiz", "📊 Analytics"])

# =========================================================
# TAB 1: UPLOAD & GENERATE
# =========================================================
with tab1:
    # Hero section
    st.markdown(
        """
        <div style="
            padding: 1.8rem 1.5rem;
            border-radius: 1.5rem;
            background: radial-gradient(circle at top left, #4f46e533, #020617 55%);
            border: 1px solid #1f2937;
            display: flex;
            gap: 1.5rem;
            align-items: center;
            justify-content: space-between;
        ">
            <div style="max-width: 60%;">
                <div style="font-size:0.9rem;color:#a5b4fc;margin-bottom:0.25rem;">
                    AI‑Powered Quiz Workspace
                </div>
                <div style="font-size:1.8rem;font-weight:800;line-height:1.2;margin-bottom:0.4rem;">
                    Turn your PDFs into smart, adaptive quizzes.
                </div>
                <div style="color:#9ca3af;font-size:0.95rem;margin-bottom:0.7rem;">
                    Upload notes, auto‑generate MCQs, practice with live feedback, and track your progress with rich analytics.
                </div>
                <div style="display:flex;gap:0.6rem;flex-wrap:wrap;">
                    <span style="
                        padding:0.25rem 0.75rem;
                        border-radius:999px;
                        background-color:#111827;
                        font-size:0.8rem;
                        color:#e5e7eb;
                    ">⚡ Groq‑powered LLM questions</span>
                    <span style="
                        padding:0.25rem 0.75rem;
                        border-radius:999px;
                        background-color:#111827;
                        font-size:0.8rem;
                        color:#e5e7eb;
                    ">📊 Difficulty & topic analytics</span>
                    <span style="
                        padding:0.25rem 0.75rem;
                        border-radius:999px;
                        background-color:#111827;
                        font-size:0.8rem;
                        color:#e5e7eb;
                    ">🧠 Adaptive engine ready</span>
                </div>
            </div>
            <div style="text-align:right; min-width: 180px;">
                <div style="font-size:0.8rem;color:#9ca3af;">Session overview</div>
                <div style="font-size:1.4rem;font-weight:700;">Quiz Hub</div>
                <div style="font-size:0.9rem;color:#9ca3af;margin-top:0.35rem;">
                    Start by uploading a PDF and choosing how many questions you want.
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


    st.markdown("")


    col_left, col_right = st.columns([2, 1])


    # ---- Left: upload + controls ----
    with col_left:
        upload_card = st.container(border=True)
        with upload_card:
            st.markdown("#### Create a new quiz")
            uploaded_file = st.file_uploader("Upload PDF file", type=["pdf"])


            num_questions = st.slider(
                "Number of questions",
                min_value=3,
                max_value=20,
                value=8,
                step=1,
            )


            difficulty_mode = st.radio(
                "Target difficulty",
                ["Mixed", "Mostly easy", "Mostly medium", "Mostly hard"],
                horizontal=True,
            )


            st.caption("Pro tip: Use focused chapter notes for sharper questions.")


            generate_clicked = st.button(
                "🚀 Extract & Generate Questions",
                use_container_width=True,
            )


    # ---- Right: quick info ----
    with col_right:
        st.markdown(
            """
            <div style="
                padding:1rem;
                border-radius:1rem;
                background-color:#020617;
                border:1px solid #111827;
                font-size:0.9rem;
            ">
                <b>Why SmartQuizzer?</b>
                <ul style="padding-left:1.1rem;margin-top:0.4rem;">
                    <li>No manual question writing.</li>
                    <li>MCQs with real explanations.</li>
                    <li>Tracks accuracy & speed over time.</li>
                    <li>Spot weak topics instantly.</li>
                </ul>
                <hr style="border-color:#1f2937;margin:0.6rem 0;">
                <span style="color:#9ca3af;">Next:</span>
                <span>Generate a quiz and jump to the <b>Quiz</b> tab.</span>
            </div>
            """,
            unsafe_allow_html=True,
        )


    # ---- Generation logic ----
    if uploaded_file is not None and generate_clicked:
        with open("temp_upload.pdf", "wb") as f:
            f.write(uploaded_file.read())


        raw_text = extract_text_from_pdf("temp_upload.pdf")
        clean = clean_text(raw_text)


        with st.spinner("Generating questions using the LLM..."):
            questions = generate_questions_from_text(
                clean, num_questions=num_questions
            ) or []


        questions = clean_questions(questions)


        if questions:
            save_questions_json(questions)
            st.success(
                f"Generated {len(questions)} questions and saved to data/questions.json"
            )


            # clear old quiz state
            for key in list(st.session_state.keys()):
                if key.startswith("options_") or key.startswith("quiz_"):
                    del st.session_state[key]


            # Non-clickable but interactive-looking info card
            st.markdown(
                f"""
                <div style="
                    margin-top:0.2rem;
                    margin-bottom:1.5rem; 
                    padding:1.0rem 1.0rem;
                    border-radius:1.1rem;
                    background-color:#020617;
                    border:1px solid #1f2937;
                    display:flex;
                    align-items:center;
                    justify-content:space-between;
                    gap:0.8rem;
                ">
                    <div>
                        <div style="font-size:1rem;font-weight:700;margin-bottom:0.2rem;">
                            Ready to practice?
                        </div>
                        <div style="color:#9ca3af;font-size:0.9rem;">
                            {len(questions)} questions are ready. Open the <b>Quiz</b> tab above and start your session.
                        </div>
                    </div>
                    <div style="
                        min-width:190px;
                        text-align:right;
                        font-size:0.85rem;
                        color:#e5e7eb;
                    ">
                        <span style="
                            display:inline-flex;
                            align-items:center;
                            gap:0.35rem;
                            padding:0.35rem 0.9rem;
                            border-radius:999px;
                            background-color:#4f46e5;
                        ">
                            <span style="font-size:1rem;">👉</span>
                            <span>Next step: click the <b>Quiz</b> tab</span>
                        </span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )


# =========================================================
# TAB 2: QUIZ – FULLSCREEN CUSTOM LAYOUT (NO STRIP)
# =========================================================
with tab2:
    # -------- LOAD QUESTIONS --------
    questions = load_questions_json() or []
    total_questions = len(questions)

    if total_questions == 0:
        st.info("First generate questions in the Upload & Generate tab.")
        st.stop()

    # -------- SESSION STATE --------
    if "quiz_index" not in st.session_state:
        st.session_state.quiz_index = 0
    if "quiz_attempts" not in st.session_state:
        st.session_state.quiz_attempts = 0
    if "quiz_start_time" not in st.session_state:
        st.session_state.quiz_start_time = time.time()
    if "show_result_view" not in st.session_state:
        st.session_state.show_result_view = False
    if "quiz_score" not in st.session_state:
        st.session_state.quiz_score = 0
    if "quiz_history" not in st.session_state:
        st.session_state.quiz_history = []

    # -------- END OF QUIZ (TOP LEVEL) --------
    if (
        st.session_state.quiz_index >= total_questions
        and not st.session_state.show_result_view
    ):
        st.success("You have attempted all questions.")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("📊 See Result", use_container_width=True):
                st.session_state.show_result_view = True
                st.rerun()
        with c2:
            if st.button("🔁 Restart Quiz", use_container_width=True):
                st.session_state.quiz_index = 0
                st.session_state.quiz_attempts = 0
                st.session_state.quiz_start_time = time.time()
                st.session_state.quiz_score = 0
                st.session_state.quiz_history = []
                st.session_state.show_result_view = False
                st.rerun()
        st.stop()

    # -------- POLISHED RESULT VIEW --------
    if st.session_state.show_result_view:
        hist = st.session_state.quiz_history
        if not hist:
            st.info("No attempts recorded yet.")
            st.stop()

        acc = compute_accuracy(hist)
        avg_time = average_response_time(hist)
        score = total_score(hist)

        if acc >= 0.8:
            mood_emoji = "🎉"
            mood_title = "Outstanding!"
            mood_color = "#22c55e"
        elif acc >= 0.5:
            mood_emoji = "💪"
            mood_title = "Nice effort!"
            mood_color = "#eab308"
        else:
            mood_emoji = "🚀"
            mood_title = "You just warmed up!"
            mood_color = "#f97316"

        st.markdown(
            "<h2 style='margin-top:0.2rem;margin-bottom:0.5rem;'>Result</h2>",
            unsafe_allow_html=True,
        )

        # Top banner
        st.markdown(
            f"""
            <div style="
                margin-top:0.4rem;
                margin-bottom:1.0rem;
                padding:1.2rem 1.4rem;
                border-radius:1.4rem;
                background: radial-gradient(circle at top left, #111827, #020617 55%);
                border:1px solid #1f2937;
            ">
                <div style="display:flex;align-items:center;gap:0.6rem;margin-bottom:0.25rem;">
                    <div style="font-size:1.6rem;">{mood_emoji}</div>
                    <div style="font-size:1.25rem;font-weight:700;color:{mood_color};">
                        {mood_title}
                    </div>
                </div>
                <div style="color:#9ca3af;font-size:0.95rem;">
                    Here is a quick snapshot of how this quiz went for you.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Score circle + stats
        col_a, col_b = st.columns([1, 2])
        with col_a:
            st.markdown(
                f"""
                <div style="display:flex;justify-content:center;margin-bottom:0.6rem;">
                    <div style="
                        position:relative;
                        width:170px;
                        height:170px;
                        border-radius:999px;
                        background:conic-gradient({mood_color} {acc*360:.0f}deg, #111827 {acc*360:.0f}deg);
                        display:flex;
                        align-items:center;
                        justify-content:center;
                    ">
                        <div style="
                            width:130px;
                            height:130px;
                            border-radius:999px;
                            background-color:#020617;
                            display:flex;
                            flex-direction:column;
                            align-items:center;
                            justify-content:center;
                            text-align:center;
                        ">
                            <div style="font-size:0.8rem;color:#9ca3af;">Final score</div>
                            <div style="font-size:1.8rem;font-weight:800;margin-top:0.1rem;">
                                {score}/{st.session_state.quiz_attempts}
                            </div>
                            <div style="font-size:0.85rem;color:#e5e7eb;margin-top:0.15rem;">
                                {acc*100:.1f}% correct
                            </div>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col_b:
            st.markdown(
                f"""
                <div style="display:flex;gap:1rem;flex-wrap:wrap;margin-top:0.2rem;">
                    <div style="
                        flex:1;
                        min-width:150px;
                        padding:0.85rem 0.9rem;
                        border-radius:1rem;
                        background-color:#020617;
                        border:1px solid #1f2937;
                        font-size:0.9rem;
                    ">
                        <div style="color:#9ca3af;font-size:0.8rem;margin-bottom:0.2rem;">
                            Questions attempted
                        </div>
                        <div style="font-size:1.25rem;font-weight:700;">{st.session_state.quiz_attempts}</div>
                    </div>
                    <div style="
                        flex:1;
                        min-width:150px;
                        padding:0.85rem 0.9rem;
                        border-radius:1rem;
                        background-color:#020617;
                        border:1px solid #1f2937;
                        font-size:0.9rem;
                    ">
                        <div style="color:#9ca3af;font-size:0.8rem;margin-bottom:0.2rem;">
                            Avg. time / question
                        </div>
                        <div style="font-size:1.25rem;font-weight:700;">{avg_time:.1f}s</div>
                    </div>
                    <div style="
                        flex:1;
                        min-width:150px;
                        padding:0.85rem 0.9rem;
                        border-radius:1rem;
                        background-color:#020617;
                        border:1px solid #1f2937;
                        font-size:0.9rem;
                    ">
                        <div style="color:#9ca3af;font-size:0.8rem;margin-bottom:0.2rem;">
                            Total questions
                        </div>
                        <div style="font-size:1.25rem;font-weight:700;">{total_questions}</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown(
            """
            <div style="height:1.0rem;"></div>
            <div style="
                padding:1.0rem 1.0rem;
                border-radius:1.1rem;
                background-color:#020617;
                border:1px solid #1f2937;
                font-size:0.9rem;
            ">
                <div style="font-weight:600;margin-bottom:0.4rem;">Suggested next steps</div>
                <ul style="margin:0;padding-left:1.1rem;color:#9ca3af;">
                    <li>Generate a focused quiz on the topics you struggled with.</li>
                    <li>Re‑attempt this quiz after a quick revision to see improvement.</li>
                    <li>Open the Analytics tab to dive into topic‑wise performance.</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("<div style='height:0.8rem;'></div>", unsafe_allow_html=True)
        col_back, col_restart = st.columns(2)
        with col_back:
            if st.button("⬅ Back to questions", use_container_width=True):
                st.session_state.show_result_view = False
                st.rerun()
        with col_restart:
            if st.button("🔁 Restart this quiz", use_container_width=True):
                st.session_state.quiz_index = 0
                st.session_state.quiz_attempts = 0
                st.session_state.quiz_score = 0
                st.session_state.quiz_history = []
                st.session_state.quiz_start_time = time.time()
                st.session_state.show_result_view = False
                st.rerun()

    # -------- QUESTION DATA + LAYOUT
    if not st.session_state.show_result_view:
        idx = st.session_state.quiz_index
        q = questions[idx]
        q_num = idx + 1

        # 2) PURE HTML CANVAS
        st.markdown(
            """
            <div id="quiz-root" style="
                position:relative;
                width:100%;
                display:flex;
                justify-content:center;
                align-items:flex-start;
            ">
              <div style="
                  width:100%;
                  max-width:1100px;
                  display:block;
              ">
            """,
            unsafe_allow_html=True,
        )

        # 3) LEFT COLUMN (QUESTION)
        left_col, right_col = st.columns([2.1, 0.9], gap="large")

        with left_col:
            st.markdown(
                """
                <div style="
                    padding:1.6rem 1.7rem;
                    border-radius:1.3rem;
                    background:#020617;
                    border:1px solid #111827;
                    box-shadow:0 20px 50px rgba(15,23,42,0.9);
                ">
                  <div style="font-size:1.6rem;font-weight:700;margin-bottom:1.0rem;">
                    Quiz session
                  </div>
                """,
                unsafe_allow_html=True,
            )

            st.markdown(
                f"""
                <h3 style="
                    margin-top:0.2rem;
                    margin-bottom:1.0rem;
                    line-height:1.4;
                    font-size:1.35rem;
                ">{q['question']}</h3>
                """,
                unsafe_allow_html=True,
            )

            opt_key = f"options_{idx}"
            if opt_key not in st.session_state:
                opts = [q["answer"]] + q.get("distractors", [])
                opts = list(dict.fromkeys(opts))
                random.shuffle(opts)
                st.session_state[opt_key] = opts
            options = st.session_state[opt_key]

            st.markdown(
                "<div style='font-size:0.95rem;font-weight:600;margin-bottom:0.3rem;'>"
                "Select an answer:</div>",
                unsafe_allow_html=True,
            )
            selected = st.radio(
                "",
                options,
                key=f"quiz_q_{idx}",
                label_visibility="hidden",
            )

            submit_clicked = st.button(
                "✅ Submit", key=f"submit_{idx}", use_container_width=False
            )

            st.markdown("</div>", unsafe_allow_html=True)

        # 4) RIGHT COLUMN (SESSION OVERVIEW + PROGRESS)
        with right_col:
            st.markdown(
                """
                <div style="
                    margin-top:0.3rem;
                    padding:1.1rem 1.1rem;
                    border-radius:1.2rem;
                    background:#020617;
                    border:1px solid #111827;
                    font-size:0.85rem;
                ">
                  <div style="font-size:1rem;color:#9ca3af;margin-bottom:0.2rem;">
                      Session overview
                  </div>
                """,
                unsafe_allow_html=True,
            )

            st.markdown(
                f"<div style='font-size:1.05rem;font-weight:700;margin-bottom:0.6rem;'>Question {q_num}/{total_questions}</div>",
                unsafe_allow_html=True,
            )

            diff = q.get("difficulty", "unknown").title()
            topic = q.get("topic", "Unknown")

            st.markdown(
                f"""
                <div style="display:flex;flex-direction:column;gap:0.3rem;margin-bottom:0.6rem;">
                    <span style="font-size:0.85rem;color:#9ca3af;">Difficulty</span>
                    <span style="
                        padding:0.2rem 0.7rem;
                        border-radius:999px;
                        background-color:#111827;
                        font-size:0.85rem;
                    ">{diff}</span>
                    <span style="font-size:0.85rem;color:#9ca3af;">Topic</span>
                    <span style="
                        padding:0.2rem 0.7rem;
                        border-radius:999px;
                        background-color:#111827;
                        font-size:0.85rem;
                    ">{topic}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

            attempted = len(st.session_state.quiz_history)
            remaining = max(total_questions - attempted, 0)

            if total_questions > 0:
                progress_val = attempted / total_questions
            else:
                progress_val = 0.0

            progress_val = max(0.0, min(1.0, progress_val))

            st.progress(progress_val, text=f"Progress: {int(progress_val*100)}%")
            st.caption(f"✅ Attempted: {attempted} • ❓ Remaining: {remaining}")

            elapsed_now = time.time() - st.session_state.quiz_start_time
            st.caption(f"⏱ Time running: {elapsed_now:.1f} seconds")

            is_last = q_num == total_questions
            col_n1, col_n2 = st.columns(2)
            with col_n1:
                next_clicked = st.button(
                    "➡ Next Question",
                    disabled=is_last,
                    use_container_width=True,
                    key=f"next_{idx}",
                )
            with col_n2:
                result_clicked = st.button(
                    "📊 See Result",
                    disabled=not is_last,
                    use_container_width=True,
                )

            st.markdown("</div>", unsafe_allow_html=True)

        # 5) Close root wrappers
        st.markdown(
            """
              </div>  <!-- grid -->
            </div>    <!-- quiz-root -->
            """,
            unsafe_allow_html=True,
        )

        # -------- LOGIC --------
        if submit_clicked:
            elapsed = time.time() - st.session_state.quiz_start_time
            is_correct = selected.strip().lower() == q["answer"].strip().lower()

            st.session_state.quiz_history.append(
                {
                    "is_correct": is_correct,
                    "difficulty": q.get("difficulty"),
                    "topic": q.get("topic"),
                    "response_time": elapsed,
                }
            )
            if is_correct:
                st.session_state.quiz_score += 1
                st.success("✅ Correct!")
            else:
                st.error(f"❌ Incorrect. Correct answer: {q['answer']}")
            st.session_state.quiz_attempts += 1

        if next_clicked and st.session_state.quiz_attempts >= q_num:
            st.session_state.quiz_index += 1
            st.session_state.quiz_start_time = time.time()
            st.rerun()

        if result_clicked:
            st.session_state.show_result_view = True
            st.rerun()



# =========================================================
# TAB 3: ANALYTICS
# =========================================================

with tab3:
    st.subheader("📈 Performance analytics")

    hist = st.session_state.get("quiz_history", [])

    if not hist:
        st.info("Attempt the quiz first to view analytics.")
        st.stop()

    acc = compute_accuracy(hist)
    avg_time = average_response_time(hist)
    score = total_score(hist)

    # ----- Difficulty progression -----
    st.subheader("Difficulty progression")
    diff_list = difficulty_progression(hist)
    diff_map = {"easy": 1, "medium": 2, "hard": 3}
    diff_values = [diff_map.get(d, 2) for d in diff_list]
    x = list(range(1, len(diff_values) + 1))

    fig_diff = px.line(
        x=x,
        y=diff_values,
        markers=True,
        labels={
            "x": "Question #",
            "y": "Difficulty level (1 = Easy, 2 = Medium, 3 = Hard)",
        },
    )
    st.plotly_chart(fig_diff, use_container_width=True)

    # ----- Topic-wise performance + insight cards -----
    st.subheader("Topic-wise performance")
    df_topics = topic_wise_performance(hist)
    if not df_topics.empty:
        fig_topic = px.bar(
            df_topics,
            x="topic",
            y="accuracy",
            text="accuracy",
            labels={"accuracy": "Accuracy"},
            range_y=[0, 1],
        )
        fig_topic.update_traces(texttemplate="%{text:.0%}", textposition="outside")
        st.plotly_chart(fig_topic, use_container_width=True)

        weak = hardest_topics(df_topics)

        col_insight1, col_insight2 = st.columns(2)
        with col_insight1:
            st.markdown(
                """
                <div style="
                    padding:1rem 1rem;
                    border-radius:1rem;
                    background:radial-gradient(circle at top left,#111827,#020617 55%);
                    border:1px solid #1f2937;
                    font-size:0.9rem;
                ">
                    <div style="font-size:0.95rem;font-weight:700;margin-bottom:0.3rem;">
                        📌 Strength snapshot
                    </div>
                """,
                unsafe_allow_html=True,
            )
            best_row = df_topics.sort_values("accuracy", ascending=False).iloc[0]
            st.markdown(
                f"""
                    <p style="margin:0 0 0.4rem 0;">
                        You perform best in <b>{best_row['topic']}</b>
                        with <b>{best_row['accuracy']*100:.0f}%</b> accuracy.
                    </p>
                    <p style="margin:0;color:#9ca3af;">
                        Keep revising a few key questions here to lock in your advantage.
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col_insight2:
            st.markdown(
                """
                <div style="
                    padding:1rem 1rem;
                    border-radius:1rem;
                    background-color:#020617;
                    border:1px solid #1f2937;
                    font-size:0.9rem;
                ">
                    <div style="font-size:0.95rem;font-weight:700;margin-bottom:0.3rem;">
                        ⚠️ Weak spots
                    </div>
                """,
                unsafe_allow_html=True,
            )
            if weak:
                weak_topics = ", ".join(weak)
                st.markdown(
                    f"""
                        <p style="margin:0 0 0.4rem 0;">
                            Topics needing attention:
                            <b>{weak_topics}</b>.
                        </p>
                        <p style="margin:0;color:#9ca3af;">
                            Create focused quizzes just on these topics for the next 2–3 sessions.
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    """
                        <p style="margin:0;">
                            No clear weak topics yet – great balance!
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
    else:
        st.write("Topic-wise data is not available yet.")

    # ----- Final recommendation + CTA -----
    st.subheader("Smart study plan")

    recommendation_text = generate_recommendation(hist)

    col_plan, col_actions = st.columns([2, 1])
    with col_plan:
        st.markdown(
            """
            <div style="
                padding:1.2rem 1.1rem;
                border-radius:1.2rem;
                background:radial-gradient(circle at top left,#111827,#020617 55%);
                border:1px solid #1f2937;
                font-size:0.9rem;
            ">
                <div style="font-size:0.95rem;font-weight:700;margin-bottom:0.4rem;">
                    🧠 Personalized insight
                </div>
            """,
            unsafe_allow_html=True,
        )
        st.write(recommendation_text)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_actions:
        st.markdown(
            """
            <div style="
                padding:1rem 1rem;
                border-radius:1.2rem;
                background-color:#020617;
                border:1px solid #1f2937;
                font-size:0.9rem;
                margin-bottom :2rem;
            ">
                <div style="font-size:0.95rem;font-weight:700;margin-bottom:0.4rem;">
                    Next steps
                </div>
                <ul style="padding-left:1.1rem;margin:0;">
                    <li>Generate a new quiz focusing on weak topics.</li>
                    <li>Try a higher difficulty mix.</li>
                    <li>Re‑attempt after revision and compare analytics.</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

