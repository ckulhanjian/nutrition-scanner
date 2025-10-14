from PIL import Image
import pytesseract
import re

def extract_label(model, img_path):
    img = Image.open(img_path)
    
    prompt = """
    Extract only the ingredient list from this label.
    If an ingredient starts with 'contains', only add the ingredients from that statement.
    If an ingredient is followed by parenthesis (), add all items (seperated by commas) to the ingredients list.
    Return a comma seperated list with no other text
    """
    
    response = model.generate_content([prompt, img])
    
    return response.text

def extract_tesseract(img_path):
    """
    Extract text from image using Tesseract OCR
    """
    try:
        # Open image
        image = Image.open(img_path)
        
        # Use Tesseract to extract text
        text = pytesseract.image_to_string(image)
        text = text.lower().replace("\n", " ").strip()

        ingredients_text = ""

        contains_match = re.search(r'contains\s(.*?)(?:\.)', text)
        if contains_match:
            ingredients_text = contains_match.group(1)
        else:
            # Otherwise, try to find 'ingredients:' or first line
            ingredients_match = re.search(r'ingredients\s*:?(.+)', text)
            if ingredients_match:
                ingredients_text = ingredients_match.group(1)
            else:
                ingredients_text = text  # fallback: take all OCR text

        items = []
        for part in ingredients_text.split(","):
            part = part.strip()
            # Check for parentheses
            paren_match = re.match(r'(.+?)\s*\((.+)\)', part)
            if paren_match:
                items.append(paren_match.group(1).strip())
                # Split contents of parentheses by comma
                inner_items = [i.strip() for i in paren_match.group(2).split(",")]
                items.extend(inner_items)
            else:
                items.append(part)

        ingredients = [i for i in set(items) if i]

        print("Text extracted from image using Tesseract.")
        return ingredients
    except Exception as e:
        print(f"Error extracting text with Tesseract: {e}")
        raise

def extract_ingredients(model, img_path):
    # Step 1: Try OCR locally
    text = extract_tesseract(img_path)
    
    # Step 2: If OCR failed or text is empty
    if not text or len(text) < 10:
        text = extract_label(model, img_path)  # call Gemini

    return text