import json
from typing import Dict, List

def calculate_cooking_times(pressure_hpa: float) -> Dict:
    # Reference sea level pressure
    SEA_LEVEL_HPA = 1013.25
    
    # Base cooking times at sea level (in minutes)
    base_times = {
        "Hard-boiled Eggs": 8,
        "Dried Pinto Beans": 120,
        "White Rice": 20,
        "Angel Food Cake": 35,
        "Pasta (spaghetti)": 10,
        "Boiled Potatoes": 20,
        "Basic Bread": 40,
        "Chocolate Chip Cookies": 12
    }
    
    # Calculate pressure factor (how much longer cooking will take)
    pressure_factor = SEA_LEVEL_HPA / pressure_hpa
    
    # Additional adjustments needed at different pressures
    adjustments = {
        "Hard-boiled Eggs": {
            "liquid": "Add extra water to prevent rapid evaporation",
            "temperature": "Keep water at rolling boil"
        },
        "Dried Pinto Beans": {
            "liquid": "Add 1-2 cups extra water",
            "temperature": "Maintain steady simmer"
        },
        "White Rice": {
            "liquid": f"Add {round((pressure_factor - 1) * 3, 1)} tbsp water per cup",
            "temperature": "Keep covered"
        },
        "Angel Food Cake": {
            "temperature": f"Increase temperature by {int((1 - pressure_factor) * -25)}°F",
            "ingredients": "Reduce sugar by 1-2 tbsp, increase flour by 1-2 tbsp"
        },
        "Pasta (spaghetti)": {
            "liquid": "Use extra water",
            "temperature": "Maintain rolling boil"
        },
        "Boiled Potatoes": {
            "liquid": "Add extra water",
            "temperature": "Keep covered"
        },
        "Basic Bread": {
            "ingredients": "Decrease yeast by ¼ tsp, may need extra liquid",
            "temperature": "Keep same temperature"
        },
        "Chocolate Chip Cookies": {
            "ingredients": "Increase flour by 2 tbsp per cup, decrease sugar slightly",
            "temperature": f"Increase temperature by {int((1 - pressure_factor) * -15)}°F"
        }
    }
    
    # Calculate new cooking times and create result structure
    result = {
        "metadata": {
            "pressure_hpa": pressure_hpa,
            "sea_level_hpa": SEA_LEVEL_HPA,
            "pressure_factor": round(pressure_factor, 3)
        },
        "cooking_times": []
    }
    
    for food, base_time in base_times.items():
        # Calculate new cooking time with pressure factor
        new_time = round(base_time * pressure_factor, 1)
        time_diff = round(new_time - base_time, 1)
        
        item = {
            "food": food,
            "sea_level_time": base_time,
            "adjusted_time": new_time,
            "time_difference": time_diff,
            "adjustments": adjustments[food]
        }
        result["cooking_times"].append(item)
    
    return result

# Example usage:
if __name__ == "__main__":
    # Example for Denver (approximately 850 hPa)
    denver_times = calculate_cooking_times(850)
    print(json.dumps(denver_times, indent=2))