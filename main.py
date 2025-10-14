# step 1 : api
import google.generativeai as genai
import json
from dotenv import load_dotenv
import os


from scripts.extract_label import extract_ingredients, extract_label

from scripts.filter_ingredients import filter_ingredients

from scripts.check_filters import check_filters

from scripts.database import setup_database, view_all_ingredients, clear_all_ingredients, preload_database


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
    # clear_all_ingredients()

    setup_database()

    # preload_database()


    # view_all_ingredients()

    # variables
    img_path = "images/granola.jpg"
    text_from_img = ""
    user_filters = ["anti-inflammatory","low-sugar", "vegan", "vegetarian", "lactose-intolerant", "nut-allergy"]

    # # # # step 2 - image to text
    try:
        text_from_img = extract_label(model,img_path)
    except Exception as e:
        print(f"Error: {e}")

    ingredients_list = [item.strip().lower() for item in text_from_img.split(",")]
    # ingredients_list = ["wheat","soy","calcium","lactose","bleached wheat flour", "sugar",
    # "wheat starch", "pecans"]

    print(f"Ingredients List: {ingredients_list}")

    # # # # step 3 analyze text and output json
    results, failing_ingredients = filter_ingredients(ingredients_list, model, user_filters)

    print(f"Product Ingredients: {ingredients_list}\n")
    print(f"User Filters: {user_filters}\n")
    print(results, "\n")
    print(failing_ingredients, "\n")

    # # step 4 get filters (returns a dictionary)
    # data = check_filters(filename, user_input)
    # print(results)

main()

    
    
    
