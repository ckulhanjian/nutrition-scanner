import re
import json

from scripts.database import get_tags, add_ingredient


FILTERS = {
  "anti-inflammatory": ["saturated fat", "added sugar", "hydrogenated oils","refined flour","corn oil","soybean oil", "bleaced flour","inflammatory"],
  "low-sugar":["sucrose", "high-fructose corn syrup", "corn syrup solids", "maltodextrin"],
  "nut-allergy":["peanuts", "tree nuts", "almonds", "walnuts", "cashews", "pecans", "pistachios", "Brazil nuts", "nut"],
  "halal":["pork", "alcohol", "animal shortening", "gelatin"],
  "gluten-free":["wheat", "barley", "rye", "triticale", "spelt", "kamut", "malt"],
  "lactose-intolerant":["lactose", "milk", "whey", "casein", "butter", "cream", "yogurt", "cheese", "sour cream", "buttermilk","lactalbumin", "lactoferrin"],
  "vegan":["animal products", "meat", "poultry", "fish", "eggs", "dairy", "honey", "beeswax", "gelatin", "casein", "whey", "carmine", "shellac"],
  "vegetarian":["meat","poultry", "fish", "shellfish", "animal flesh"]
}

# COMBINED_PROMPT = """
# **TASK:** Extract nutritional data AND analyze dietary compatibility in a single response.

# **LABEL TEXT:**
# {user_text}
# """

# def clean_json_response(text):
#     text = text.strip()
#     text = re.sub(r'^```(?:json)?\s*\n?', '', text)
#     text = re.sub(r'\n?```\s*$', '', text)
#     return text.strip()

# def filter_ingredients(text_from_img, model, filename):
#     print("Analyzing data from image...")
    
#     # Single API call with combined prompt
#     prompt_formatted = COMBINED_PROMPT.format(user_text=text_from_img)
#     response = model.generate_content(prompt_formatted)
    
#     # Clean and parse response
#     cleaned_response = clean_json_response(response.text)
    
#     try:
#         json_data = json.loads(cleaned_response)
#     except json.JSONDecodeError as e:
#         print(f"Error: Could not parse JSON response: {e}")
#         print(f"Response text: {cleaned_response[:200]}...")
#         with open(f"{filename}.error.txt", 'w') as f:
#             f.write(cleaned_response)
#         raise
    
#     # Write to file
#     try:
#         with open(filename, 'w') as file:
#             json.dump(json_data, file, indent=2)
#         print(f"Successfully wrote data to '{filename}'")
#     except IOError as e:
#         print(f"An error occurred while writing to the file: {e}")
#         raise
    

# text from image
# model to pass in to evaluate ingredients
# user filters


'''
1. compare ingredients list to user filters
2. for each ingredient, get tags 
  - either from database
  - or from model
3. compare tags with each filter

'''

def analyze_ingredient(ingredient, model):
  prompt = f"""Analyze the ingredient "{ingredient}".
  The filters are anti-inflammatory, low-sugar, nut allergy, halal, gluten-free, lactose intolerant, vegan and vegetarian.
  Identify what **allergens** are PRESENT in the product (ex. egg, soy).
  Identify **nutritional tags** (sweetener, processed, high-glycemic).
  Consider both obvious and hidden sources of allergens/restrictions.

  **RESPONSE MUST BE ONLY a comma-separated list of 2 to 5 lowercase tags, with no other text, numbers, or characters.**
  Example: almond, nut-allergy, high-glycemic
      """
  
  response = model.generate_content(prompt)
  tags = response.text.strip()

  tags = [
        tag.strip().lower() # Strip again for internal whitespace and ensure lowercase
        for tag in tags.split(',')
    ]
  
  tags = [tag for tag in tags if tag]  # Remove any empty strings from split
  tags = tags[:5] # Ensure a maximum of 5 tags

  # update database
  add_ingredient(ingredient, tags)

  return tags

def compare_ingredients(filters, ingredient, tags, results, failing_ingredients):
    for filter_name in filters:
        filter_tags = FILTERS[filter_name]
        # print(f"{filter_tags} and {tags}")
        forbidden_tags = set(filter_tags) & set(tags)
        if forbidden_tags:
            results[filter_name] = "fail"
            failing_ingredients[filter_name].append(ingredient)

    return
    

def filter_ingredients(ingredients, model, user_filters):
  results = {}
  failing_ingredients = {}

  for filter in user_filters:
      results[filter] = "pass"
      failing_ingredients[filter] = []
  # get tags
  for ingredient in ingredients:
    tags = get_tags(ingredient.lower())

    if tags is None:
        # call model
        tags = analyze_ingredient(ingredient.lower(), model)

    # print(f"{ingredient}:{tags}")
    # compare tags with filter
    compare_ingredients(user_filters, ingredient, tags, results, failing_ingredients)

  return results, failing_ingredients