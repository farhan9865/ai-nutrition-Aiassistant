import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_PATH = BASE_DIR / "data" / "raw" / "diet_recommendations_dataset.csv.xlsx"


# --------------------------------------------------
# Load dataset
# --------------------------------------------------

def load_nutrition_data():

    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Nutrition dataset not found: {DATA_PATH}")

    return pd.read_excel(DATA_PATH)


# --------------------------------------------------
# Profile-based filtering
# --------------------------------------------------

def filter_by_profile(age, conditions, goal):

    df = load_nutrition_data()

    filtered = df.copy()

    # ----------------------------
    # Age band filter
    # ----------------------------

    if "Age" in filtered.columns:
        filtered = filtered[
            (filtered["Age"] >= age - 10) &
            (filtered["Age"] <= age + 10)
        ]

    # ----------------------------
    # Goal → Diet mapping
    # ----------------------------

    goal_map = {
        "Weight Loss": ["Low", "Low_Carb", "Low_Sodium"],
        "Muscle Gain": ["High_Protein", "Balanced"],
        "Maintenance": ["Balanced"],
    }

    if "Diet_Recommendation" in filtered.columns:

        patterns = goal_map.get(goal, [])

        if patterns:
            regex = "|".join(patterns)

            filtered = filtered[
                filtered["Diet_Recommendation"]
                .astype(str)
                .str.contains(regex, case=False, na=False)
            ]

    # ----------------------------
    # Medical condition matching
    # ----------------------------

    if conditions and "Medical_Condition" in filtered.columns:

        for cond in conditions:

            filtered = filtered[
                filtered["Medical_Condition"]
                .astype(str)
                .str.contains(cond, case=False, na=False)
            ]

    # ----------------------------
    # Final cleanup
    # ----------------------------

    filtered = filtered.drop_duplicates()

    return filtered.head(20)
