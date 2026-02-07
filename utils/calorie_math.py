# utils/calorie_math.py

def calculate_bmi(weight_kg: float, height_cm: float) -> float:
    """
    Calculate Body Mass Index.
    """
    if height_cm <= 0:
        raise ValueError("Height must be greater than 0")

    height_m = height_cm / 100
    bmi = weight_kg / (height_m ** 2)

    return round(bmi, 2)


def calculate_bmr(weight_kg: float, height_cm: float, age: int, gender: str) -> float:
    """
    Mifflin-St Jeor Equation for BMR.
    """

    gender = gender.lower()

    if gender == "male":
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
    else:
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age - 161

    return round(bmr)


def calculate_tdee(bmr: float, activity: str) -> float:
    """
    Total Daily Energy Expenditure.
    """

    factors = {
        "Sedentary": 1.2,
        "Moderate": 1.55,
        "Active": 1.75,
    }

    if activity not in factors:
        raise ValueError(f"Unknown activity level: {activity}")

    return round(bmr * factors[activity])


def adjust_for_goal(tdee: float, goal: str) -> int:
    """
    Adjust calories for fitness goal.
    """

    if goal == "Weight Loss":
        return int(tdee - 400)

    elif goal == "Muscle Gain":
        return int(tdee + 400)

    return int(tdee)
