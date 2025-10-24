import re
import json
import pytesseract
from PIL import Image

COMBINED_PROMPT = """
**TASK:** Extract nutritional data AND analyze dietary compatibility in a single response.

**STEP 1 - Extract from label text:**
- Product info (serving size, servings per container)
- Nutrition facts (nutrient name, value per serving, daily value %)
- Full ingredients list
- Allergens
- Warnings

**STEP 2 - Analyze against these dietary filters:**

**Anti-Inflammatory:** FAIL if Saturated Fat >8g OR Added Sugar >10g OR contains partially hydrogenated oils, refined flour, corn oil, soybean oil. CAUTION if Saturated Fat 5-8g OR Added Sugar 5-10g.

**Low-Sugar:** FAIL if contains sucrose, high-fructose corn syrup, corn syrup solids, maltodextrin. CAUTION if Added Sugar >4g.

**Nut Allergy:** FAIL if contains peanuts, tree nuts (almonds, walnuts, cashews, pecans, pistachios, Brazil nuts). CAUTION if warning mentions nut cross-contamination.

**Halal:** FAIL if contains pork, alcohol, animal shortening (non-halal), gelatin (non-halal), enzymes (non-halal). CAUTION if gelatin/enzymes source unspecified.

**Gluten-Free:** FAIL if contains wheat, barley, rye, triticale, spelt, kamut. CAUTION if cross-contamination warning OR derivatives like modified food starch, malt, dextrin (non-GF source) OR non-certified oats.

**Lactose Intolerant:** FAIL if contains lactose, milk, whey, casein, butter, cream, yogurt, cheese, sour cream, buttermilk, milk solids, milk powder, lactalbumin, lactoferrin.

**Vegan:** FAIL if contains any animal products: meat, poultry, fish, eggs, dairy, honey, beeswax, gelatin, casein, whey, carmine, shellac, Vitamin D3 (from lanolin).

**Vegetarian:** FAIL if contains meat, poultry, fish, shellfish, animal flesh.

**OUTPUT FORMAT (single JSON, no markdown):**
{{
  "product_info": {{
    "serving_size": "string or null",
    "servings_per_container": "string or null"
  }},
  "nutrition_facts": [
    {{
      "nutrient_name": "string",
      "value_per_serving": "string",
      "daily_value_percent": "string or null"
    }}
  ],
  "ingredients": ["string"],
  "allergens": ["string"],
  "warnings": "string or null",
  "dietary_analysis": {{
    "Anti-Inflammatory": {{
      "result": "Pass/Caution/Fail",
      "reason": "specific ingredient/nutrient causing result",
      "cautious_ingredients": "comma-separated list or null"
    }},
    "Low-Sugar": {{"result": "...", "reason": "...", "cautious_ingredients": "..."}},
    "Nut Allergy": {{"result": "...", "reason": "...", "cautious_ingredients": "..."}},
    "Halal": {{"result": "...", "reason": "...", "cautious_ingredients": "..."}},
    "Gluten-Free": {{"result": "...", "reason": "...", "cautious_ingredients": "..."}},
    "Lactose Intolerant": {{"result": "...", "reason": "...", "cautious_ingredients": "..."}},
    "Vegan": {{"result": "...", "reason": "...", "cautious_ingredients": "..."}},
    "Vegetarian": {{"result": "...", "reason": "...", "cautious_ingredients": "..."}}
  }}
}}

**LABEL TEXT:**
{user_text}
"""

def extract_text_with_tesseract(img_path):
    """
    Extract text from image using Tesseract OCR
    """
    try:
        # Open image
        image = Image.open(img_path)
        
        # Use Tesseract to extract text
        # You can customize the config for better results
        custom_config = r'--oem 3 --psm 6'
        text = pytesseract.image_to_string(image, config=custom_config)
        
        print("Text extracted from image using Tesseract.")
        return text
    except Exception as e:
        print(f"Error extracting text with Tesseract: {e}")
        raise

def clean_json_response(text):
    text = text.strip()
    text = re.sub(r'^```(?:json)?\s*\n?', '', text)
    text = re.sub(r'\n?```\s*$', '', text)
    return text.strip()