import streamlit as st
import tempfile
import re

# -----------------------------
# RAG + Granite
# -----------------------------

from rag.query import search_docs
from llm.granite_client import ask_granite

# -----------------------------
# Vision
# -----------------------------

from vision.food_detector import describe_food

# -----------------------------
# Nutrition systems
# -----------------------------

from utils.calorie_math import (
    calculate_bmi,
    calculate_bmr,
    calculate_tdee,
    adjust_for_goal,
)

from data.nutrition_loader import filter_by_profile

# --------------------------------------------------
# Page Config
# --------------------------------------------------

st.set_page_config(
    page_title="Smart AI Nutrition Assistant",
    layout="wide"
)

# --------------------------------------------------
# Session Memory
# --------------------------------------------------

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "last_plan" not in st.session_state:
    st.session_state.last_plan = ""

# --------------------------------------------------
# Header
# --------------------------------------------------

st.title("🥗 Smart AI Nutrition Assistant")
st.subheader("AI-powered meal planning + calorie science")

# --------------------------------------------------
# Sidebar — Profile
# --------------------------------------------------

st.sidebar.title("🧍 Personal Profile")

with st.sidebar.expander("📌 Basic Details", expanded=True):
    age = st.number_input("Age", 18, 90, 25)
    gender = st.selectbox("Gender", ["Male", "Female"])
    height = st.number_input("Height (cm)", 140, 210, 170)
    weight = st.number_input("Weight (kg)", 40, 200, 70)

with st.sidebar.expander("🍽 Preferences", expanded=True):
    religion = st.selectbox(
        "Religion",
        ["None", "Jain", "Halal", "Kosher", "Vegetarian"]
    )

    allergies = st.multiselect(
        "Allergies",
        ["Gluten", "Lactose", "Nuts", "Soy", "Seafood"]
    )

with st.sidebar.expander("🩺 Health", expanded=True):
    conditions = st.multiselect(
        "Medical Conditions",
        ["Diabetes", "Hypertension", "PCOS", "Thyroid", "Heart Disease"]
    )

with st.sidebar.expander("🎯 Goals", expanded=True):
    goal = st.selectbox(
        "Fitness Goal",
        ["Weight Loss", "Muscle Gain", "Maintenance"]
    )

    activity = st.selectbox(
        "Activity Level",
        ["Sedentary", "Moderate", "Active"]
    )

# --------------------------------------------------
# FOOD IMAGE + MACROS
# --------------------------------------------------

st.markdown("## 📷 Upload Food Photo")
st.caption("Upload a meal photo to estimate calories, protein & carbs.")

food_image = st.file_uploader(
    "Upload meal image",
    type=["jpg", "jpeg", "png"]
)

food_desc = ""
image_macros = {"calories": 0, "protein": 0, "carbs": 0}

if food_image:

    st.image(food_image, caption="Uploaded Food", use_column_width=True)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
        tmp.write(food_image.read())
        image_path = tmp.name

    with st.spinner("🔍 Detecting food..."):
        food_desc = describe_food(image_path)

    macro_prompt = f"""
Estimate nutrition for this meal.

Detected:
{food_desc}

Return exactly:

Calories: <number>
Protein: <number>
Carbs: <number>
"""

    with st.spinner("📊 Estimating macros..."):
        macro_text = ask_granite(macro_prompt)

    cal = re.search(r"Calories:\s*(\d+)", macro_text)
    prot = re.search(r"Protein:\s*(\d+)", macro_text)
    carb = re.search(r"Carbs:\s*(\d+)", macro_text)

    if cal:
        image_macros["calories"] = int(cal.group(1))
    if prot:
        image_macros["protein"] = int(prot.group(1))
    if carb:
        image_macros["carbs"] = int(carb.group(1))

    st.markdown("### 📊 Estimated Nutrition From Image")

    c1, c2, c3 = st.columns(3)
    c1.metric("Calories", f"{image_macros['calories']} kcal")
    c2.metric("Protein", f"{image_macros['protein']} g")
    c3.metric("Carbs", f"{image_macros['carbs']} g")

# --------------------------------------------------
# User Inputs
# --------------------------------------------------

query = st.text_input(
    "💬 What would you like help with?",
    placeholder="e.g. Create a weekly vegetarian plan"
)

feedback = st.text_input(
    "🔁 Feedback / change request",
    placeholder="e.g. Increase protein on Day 3"
)

# --------------------------------------------------

if st.button("🚀 Generate Plan"):

    if not query:
        st.warning("Enter a question.")
        st.stop()

    bmi = calculate_bmi(weight, height)
    bmr = calculate_bmr(weight, height, age, gender)
    tdee = calculate_tdee(bmr, activity)
    calories = adjust_for_goal(tdee, goal)

    foods_backend = filter_by_profile(age, conditions, goal)

    with st.spinner("🔍 Searching research..."):
        docs = search_docs(query, k=4)

    context = "\n\n".join(d.page_content for d in docs)

    history_text = ""
    for msg in st.session_state.chat_history[-4:]:
        history_text += f"""
User: {msg['user']}
Assistant: {msg['assistant']}
"""

    final_prompt = f"""
You are a certified clinical nutritionist.

FIRST produce:

=== WEEKLY STRATEGY SUMMARY ===
Explain:
• calorie target
• protein plan
• carb strategy
• fat control
• condition handling
• religion fit
• sustainability

THEN:

=== 7 DAY MEAL PLAN ===

FOOD IMAGE:
{food_desc}

IMAGE MACROS:
{image_macros}

USER DATA:
BMI:{bmi}
Target:{calories}

PROFILE:
Age:{age}
Goal:{goal}

DATASET:
{foods_backend.to_dict()}

RESEARCH:
{context}

FEEDBACK:
{feedback if feedback else "None"}

RULES:
- EXACTLY 7 days
- Breakfast / Lunch / Dinner / Snacks
- Calories + Why
"""

    with st.spinner("🤖 Generating plan..."):
        answer = ask_granite(final_prompt)

    # retry if cut
    if answer.count("Day") < 7:
        answer = ask_granite(final_prompt + "\nContinue until Day 7.")

    st.session_state.chat_history.append(
        {"user": query, "assistant": answer}
    )

    st.session_state.last_plan = answer

    # -------------------------------
    # UI SPLIT
    # -------------------------------

    if "=== 7 DAY MEAL PLAN ===" in answer:

        summary, plan = answer.split("=== 7 DAY MEAL PLAN ===")

        st.markdown("## 📘 Weekly Strategy Summary")
        st.info(summary.replace("=== WEEKLY STRATEGY SUMMARY ===", ""))

        st.markdown("## 📅 7-Day Meal Plan")
        st.markdown(plan)

    else:
        st.markdown(answer)

# --------------------------------------------------
# History
# --------------------------------------------------

if st.session_state.chat_history:

    st.markdown("---")
    st.markdown("## 🗂 Conversation History")

    for i, msg in enumerate(reversed(st.session_state.chat_history)):
        with st.expander(f"Conversation {len(st.session_state.chat_history)-i}"):
            st.markdown("**User:**")
            st.write(msg["user"])
            st.markdown("**Assistant:**")
            st.write(msg["assistant"])
