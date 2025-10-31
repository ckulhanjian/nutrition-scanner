# Install: pip install paddleocr paddlepaddle

from paddleocr import PaddleOCR
import re

# Initialize PaddleOCR (do this once at startup)
ocr = PaddleOCR(use_angle_cls=True, lang='en', show_log=False)

def extract_ingredients_with_paddle(image_path):
    """
    Fast ingredient extraction using PaddleOCR + Gemini for parsing
    
    Strategy:
    1. Use PaddleOCR for fast text extraction (0.5-2s)
    2. Use Gemini only for intelligent parsing of the extracted text
    
    This is 5-10x faster than using Gemini for OCR
    """
    # Step 1: Fast OCR with PaddleOCR
    result = ocr.ocr(image_path, cls=True)
    
    # Extract all text
    extracted_text = []
    for line in result[0]:
        text = line[1][0]  # Get the text content
        confidence = line[1][1]  # Get confidence score
        
        # Only include high-confidence results
        if confidence > 0.7:
            extracted_text.append(text)
    
    full_text = "\n".join(extracted_text)
    
    # Step 2: Use Gemini to intelligently parse ingredients
    # This is much faster since Gemini only processes text, not image
    prompt = f"""From this product label text, extract ONLY the ingredients list.

Label text:
{full_text}

Return the ingredients as a comma-separated list in lowercase.
Remove quantities, percentages, and allergen warnings.
Do not include headers.

Ingredients:"""
    
    response = model.generate_content(prompt)
    ingredients = response.text.strip()
    
    # Clean up
    ingredients = re.sub(r'^(ingredients:|ingredients list:|ingredients are:)\s*', '', 
                        ingredients, flags=re.IGNORECASE)
    
    return ingredients


def extract_ingredients_paddle_only(image_path):
    """
    Ultra-fast extraction using ONLY PaddleOCR (no Gemini)
    
    Uses regex to find ingredient lists. Fastest but less accurate.
    Good for simple, well-formatted labels.
    """
    result = ocr.ocr(image_path, cls=True)
    
    # Extract all text
    all_text = []
    for line in result[0]:
        text = line[1][0]
        confidence = line[1][1]
        if confidence > 0.7:
            all_text.append(text.lower())
    
    full_text = " ".join(all_text)
    
    # Find ingredients section using common patterns
    patterns = [
        r'ingredients?[:\s]+([^.]+)',
        r'contains?[:\s]+([^.]+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, full_text, re.IGNORECASE)
        if match:
            ingredients_text = match.group(1)
            # Clean and format
            ingredients_text = re.sub(r'\([^)]*\)', '', ingredients_text)  # Remove parentheses
            ingredients_text = re.sub(r'\d+%?', '', ingredients_text)  # Remove percentages
            return ingredients_text.strip()
    
    # Fallback: return all text if no pattern found
    return full_text