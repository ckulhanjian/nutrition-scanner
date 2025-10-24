# step 1 : api
import google.generativeai as genai
import json
from dotenv import load_dotenv
import os


from scripts.extract_label import extract_label

# from scripts.filter_ingredients import filter_ingredients

# from scripts.check_filters import check_filters
# from scripts.database import setup_database, view_all_ingredients, clear_all_ingredients, preload_database

from scripts.databasemethods import (
    setup_database,
    add_ingredient,
    view_all_ingredients,
    find_similar_ingredients,
    preload_database,
    clear_all_ingredients
)
from scripts.filter_ingredients_new import filter_ingredients, batch_analyze_ingredients


def initial_setup():
    """Run this once to set up your database"""
    print("Setting up database...")
    setup_database()
    
    # Seed with common ingredients
    print("\nSeeding common ingredients...")
    common_ingredients = {
        # Dairy
        "milk": {"vegan": 0, "vegetarian": 1, "halal": 1, "gluten-free": 1, 
                 "lactose-intolerant": 0, "nut-allergy": 1, "anti-inflammatory": 0, "low-sugar": 1},
        "butter": {"vegan": 0, "vegetarian": 1, "halal": 1, "gluten-free": 1,
                   "lactose-intolerant": 0, "nut-allergy": 1, "anti-inflammatory": 0, "low-sugar": 1},
        "cheese": {"vegan": 0, "vegetarian": 1, "halal": 1, "gluten-free": 1,
                   "lactose-intolerant": 0, "nut-allergy": 1, "anti-inflammatory": 0, "low-sugar": 1},
        "whey": {"vegan": 0, "vegetarian": 1, "halal": 1, "gluten-free": 1,
                 "lactose-intolerant": 0, "nut-allergy": 1, "anti-inflammatory": 0, "low-sugar": 1},
        "cream": {"vegan": 0, "vegetarian": 1, "halal": 1, "gluten-free": 1,
                  "lactose-intolerant": 0, "nut-allergy": 1, "anti-inflammatory": 0, "low-sugar": 1},
        
        # Grains
        "wheat flour": {"vegan": 1, "vegetarian": 1, "halal": 1, "gluten-free": 0,
                       "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 0, "low-sugar": 1},
        "barley": {"vegan": 1, "vegetarian": 1, "halal": 1, "gluten-free": 0,
                  "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 1, "low-sugar": 1},
        "oats": {"vegan": 1, "vegetarian": 1, "halal": 1, "gluten-free": 1,
                "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 1, "low-sugar": 1},
        "rice": {"vegan": 1, "vegetarian": 1, "halal": 1, "gluten-free": 1,
                "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 1, "low-sugar": 1},
        
        # Nuts
        "almonds": {"vegan": 1, "vegetarian": 1, "halal": 1, "gluten-free": 1,
                   "lactose-intolerant": 1, "nut-allergy": 0, "anti-inflammatory": 1, "low-sugar": 1},
        "peanuts": {"vegan": 1, "vegetarian": 1, "halal": 1, "gluten-free": 1,
                   "lactose-intolerant": 1, "nut-allergy": 0, "anti-inflammatory": 1, "low-sugar": 1},
        "walnuts": {"vegan": 1, "vegetarian": 1, "halal": 1, "gluten-free": 1,
                   "lactose-intolerant": 1, "nut-allergy": 0, "anti-inflammatory": 1, "low-sugar": 1},
        
        # Meat/Animal
        "chicken": {"vegan": 0, "vegetarian": 0, "halal": 1, "gluten-free": 1,
                   "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 0, "low-sugar": 1},
        "beef": {"vegan": 0, "vegetarian": 0, "halal": 1, "gluten-free": 1,
                "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 0, "low-sugar": 1},
        "pork": {"vegan": 0, "vegetarian": 0, "halal": 0, "gluten-free": 1,
                "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 0, "low-sugar": 1},
        "gelatin": {"vegan": 0, "vegetarian": 0, "halal": 0, "gluten-free": 1,
                   "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 0, "low-sugar": 1},
        "eggs": {"vegan": 0, "vegetarian": 1, "halal": 1, "gluten-free": 1,
                "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 0, "low-sugar": 1},
        
        # Sugars
        "sugar": {"vegan": 1, "vegetarian": 1, "halal": 1, "gluten-free": 1,
                 "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 0, "low-sugar": 0},
        "high fructose corn syrup": {"vegan": 1, "vegetarian": 1, "halal": 1, "gluten-free": 1,
                                     "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 0, "low-sugar": 0},
        "honey": {"vegan": 0, "vegetarian": 1, "halal": 1, "gluten-free": 1,
                 "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 0, "low-sugar": 0},
        
        # Oils
        "soybean oil": {"vegan": 1, "vegetarian": 1, "halal": 1, "gluten-free": 1,
                       "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 0, "low-sugar": 1},
        "palm oil": {"vegan": 1, "vegetarian": 1, "halal": 1, "gluten-free": 1,
                    "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 0, "low-sugar": 1},
        "olive oil": {"vegan": 1, "vegetarian": 1, "halal": 1, "gluten-free": 1,
                     "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 1, "low-sugar": 1},
        
        # Other common
        "salt": {"vegan": 1, "vegetarian": 1, "halal": 1, "gluten-free": 1,
                "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 1, "low-sugar": 1},
        "water": {"vegan": 1, "vegetarian": 1, "halal": 1, "gluten-free": 1,
                 "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 1, "low-sugar": 1},
    }
    
    for ingredient, flags in common_ingredients.items():
        add_ingredient(ingredient, flags)
    
    print(f"Added {len(common_ingredients)} common ingredients")
    print("\nSetup complete! Your database is ready.")



def main():
    # API key, image path, output filename
    # Load environment variables from .env file
    load_dotenv()
    # Get the API key
    API_KEY = os.getenv('API_KEY')
    # step 1 - configure your API key
    genai.configure(api_key=API_KEY)
    # create a model
    model = genai.GenerativeModel('gemini-2.5-flash')
    # setup database
    # preload_database()
    initial_setup()

    # user input
    # image
    # user_input = input("Choose an image: \n1. Granola Bar\n2. Poptart\nInput: ")
    # images_dict = {"1":"images/granola.jpg", "2": "images/poptart.jpg"}
    # img_path = images_dict[user_input]

    img_path = "images/pediasure.jpg"

    # filters
    # filters_dict = {1: "anti-inflammatory",2:"low-sugar", 3:"vegan", 4:"vegetarian", 5:"lactose-intolerant", 6:"nut-allergy"}
    # print("\nFilters...")
    # for key, value in filters_dict.items():
    #     print(f"{key}: {value}")
    # user_input = input("Enter the numbers of the filters you want to check, separated by commas: ")
    # selected_numbers = [int(x.strip()) for x in user_input.split(",")]
    # user_filters = [filters_dict[num] for num in selected_numbers if num in filters_dict]
    # print()

    user_filters = ["anti-inflammatory","low-sugar","lactose-intolerant"]

    # Step 1 - image to text
    text_from_img = ""
    try:
        text_from_img = extract_label(model,img_path)
    except Exception as e:
        print(f"Error: {e}")

    # format text as a list of ingredients
    ingredients_list = [item.strip().lower() for item in text_from_img.split(",")]

    # Step 2 - analyze ingredients and compare against filters
    # results, failing_ingredients = filter_ingredients(ingredients_list, model, user_filters)
    # Analyze
    results, failing = filter_ingredients(
        ingredients_list,
        model,
        user_filters,
        similarity_threshold=0.85
    )

    # print(f"\nProduct Ingredients: \n{ingredients_list}\n")
    # print(f"User Filters: \n{user_filters}\n")
    
    # for filter_name in results:
    #     status = results[filter_name]
    #     failed_items = failing_ingredients.get(filter_name, [])
        
    #     if status == "pass":
    #         print(f"{filter_name}: ✅ {status}")
    #     else:
    #         failing_list = ", ".join(failed_items) if failed_items else "Unknown ingredient"
    #         print(f"{filter_name}: ❌ {status} (caused by: {failing_list})")

    for filter_name in user_filters:
        status = results[filter_name]
        print(f"\n{filter_name.upper()}: {status.upper()}")
        
        if status == "fail":
            print(f"  ❌ Failed due to: {', '.join(failing[filter_name])}")

main()

    
    
    
