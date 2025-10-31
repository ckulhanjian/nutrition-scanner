from PIL import Image, ImageEnhance, ImageFilter
import cv2
import numpy as np
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

# def extract_tesseract(img_path):
#     """
#     Extract text from image using Tesseract OCR
#     """
#     try:
#         # Open image
#         image = Image.open(img_path)
        
#         # Use Tesseract to extract text
#         text = pytesseract.image_to_string(image)
#         text = text.lower().replace("\n", " ").strip()

#         ingredients_text = ""

#         contains_match = re.search(r'contains\s(.*?)(?:\.)', text)
#         if contains_match:
#             ingredients_text = contains_match.group(1)
#         else:
#             # Otherwise, try to find 'ingredients:' or first line
#             ingredients_match = re.search(r'ingredients\s*:?(.+)', text)
#             if ingredients_match:
#                 ingredients_text = ingredients_match.group(1)
#             else:
#                 ingredients_text = text  # fallback: take all OCR text

#         items = []
#         for part in ingredients_text.split(","):
#             part = part.strip()
#             # Check for parentheses
#             paren_match = re.match(r'(.+?)\s*\((.+)\)', part)
#             if paren_match:
#                 items.append(paren_match.group(1).strip())
#                 # Split contents of parentheses by comma
#                 inner_items = [i.strip() for i in paren_match.group(2).split(",")]
#                 items.extend(inner_items)
#             else:
#                 items.append(part)

#         ingredients = [i for i in set(items) if i]

#         print("Text extracted from image using Tesseract.")
#         return ingredients
#     except Exception as e:
#         print(f"Error extracting text with Tesseract: {e}")
#         raise

# def extract_ingredients(model, img_path):
#     # Step 1: Try OCR locally
#     text = extract_tesseract(img_path)
    
#     # Step 2: If OCR failed or text is empty
#     if not text or len(text) < 10:
#         text = extract_label(model, img_path)  # call Gemini

#     return text

# def preprocess_image(image_path, target_size=(1920, 1080)):
#     """
#     Preprocess image for better OCR performance on food labels.
#     Returns a cleaned-up PIL image.
#     """
#     # Open image
#     img = Image.open(image_path)

#     # Convert to RGB if not already
#     if img.mode != "RGB":
#         img = img.convert("RGB")

#     # Resize (keep aspect ratio)
#     img.thumbnail(target_size, Image.Resampling.LANCZOS)

#     # Convert to OpenCV format
#     cv_img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

#     # Grayscale
#     gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)

#     # Slight blur to remove noise (not too strong!)
#     blur = cv2.GaussianBlur(gray, (3, 3), 0)

#     # Light contrast enhancement
#     alpha, beta = 1.3, 8  # softer than before
#     enhanced = cv2.convertScaleAbs(blur, alpha=alpha, beta=beta)

#     # Very light threshold (ONLY if text is dark on light)
#     # Otsu automatically picks level
#     _, thresh = cv2.threshold(enhanced, 0, 255, cv2.THRESH_OTSU)

#     # Mild sharpening before thresholding is better
#     kernel = np.array([[-1, -1, -1],
#                        [-1,  9, -1],
#                        [-1, -1, -1]])
#     sharpened = cv2.filter2D(enhanced, -1, kernel)

#     # Choose sharpened if threshold destroys text
#     processed = cv2.bitwise_and(sharpened, thresh)
#     processed_bgr = cv2.cvtColor(processed, cv2.COLOR_GRAY2BGR)
#     processed_img = Image.fromarray(processed_bgr) # This PIL image will be 3-channel (RGB)
#     return processed_img

# def extract_ingredients_hybrid(ocr, model, image_path):
#     """
#     Extract ingredients using PaddleOCR + Gemini (synchronous)
    
#     Args:
#         ocr: PaddleOCR instance
#         model: Gemini model instance
#         image_path: Path to the image file
    
#     Returns:
#         list: List of ingredient strings (lowercase)
#     """
#     # Step 1: Preprocess image
#     print("1. preprocess image")
#     processed_img = preprocess_image(image_path)
    
#     # Convert PIL image to numpy array for PaddleOCR
#     print("2. convert to number array")
#     img_array = np.array(processed_img)
    
#     # Step 2: Fast OCR with PaddleOCR
#     print("3 paddlecor")
#     try:
#         img_array = np.array(processed_img).astype(np.uint8)
#         result = ocr.ocr(img_array)
        
#         if not result or not result[0]:
#             print("⚠️ No text detected, trying original image")
#             img_array_orig = np.array(Image.open(image_path)).astype(np.uint8)
#             result = ocr.ocr(img_array_orig)
#     except Exception as e:
#         print(f"❌ OCR failed: {e}")
#         return []


#     print("extracted text?")
#     extracted_text = []

#     if not result or not result[0]:
#         print("⚠️ No OCR results returned")
#     else:
#         print("we got a result...")
#         # for line in result[0]:
#         #     # 1. Basic check for list structure
#         #     if not line or len(line) < 2:
#         #         continue
#         #     # 2. Assign the potential (text, confidence) tuple
#         #     ocr_data = line[1]
#         #     # 3. CRITICAL FIX: Check if the data is a tuple and has exactly 2 elements
#         #     if not isinstance(ocr_data, tuple) or len(ocr_data) != 2:
#         #         # print(f"⚠️ Skipping malformed OCR result: {ocr_data}") # Optional debug print
#         #         continue
#         #     # 4. Safe unpacking
#         #     text, confidence = ocr_data  # Now safe to unpack
#         #     # Only include high-confidence results
#         #     if confidence > 0.7:
#         #         extracted_text.append(text)

#     print("full text?")
#     full_text = "\n".join(extracted_text)
#     print(full_text)
    
#     # # Step 3: Use Gemini to intelligently parse ingredients
#     # print("4. gemini")
#     # prompt = f"""From this product label text, extract ONLY the ingredients list.

#     # Label text:
#     # {full_text}

#     # Return the ingredients as a comma-separated list in lowercase.
#     # Remove quantities, percentages, and allergen warnings.
#     # Do not include headers like "Ingredients:" or "Contains:".

#     # Ingredients:"""
    
#     # response = model.generate_content(prompt)
#     # ingredients_text = response.text.strip()
    
#     # Clean up response
#     ingredients_text = re.sub(
#         r'^(ingredients:|ingredients list:|ingredients are:)\s*', 
#         '', 
#         ingredients_text, 
#         flags=re.IGNORECASE
#     )
    
#     # Convert to list
#     ingredients_list = [item.strip().lower() for item in ingredients_text.split(",")]
    
#     # Filter out empty strings
#     ingredients_list = [ing for ing in ingredients_list if ing]
#     print("ingredients list: ", ingredients_list)
    
#     return ingredients_list



def extract_ingredients_hybrid(ocr, model, image_path):
    """
    Extract ingredients using PaddleOCR + Gemini (synchronous), 
    skipping local preprocessing for speed.
    """
    
    # Step 1: Skip preprocessing and load the original image
    print("1. loading original image")
    try:
        # Load and convert to NumPy array (ensuring 3 channels for robustness)
        img_array_orig = np.array(Image.open(image_path).convert("RGB")).astype(np.uint8)
    except Exception as e:
        print(f"❌ Image loading failed: {e}")
        return []
    
    # Step 2: Fast OCR with PaddleOCR
    print("2. paddleocr on original image")
    try:
        # Perform OCR directly on the original image array
        result = ocr.ocr(img_array_orig)
        
        # Check if the result is completely empty
        if not result or (isinstance(result[0], list) and not result[0]):
            print("⚠️ No text detected on original image.")
    except Exception as e:
        print(f"❌ OCR failed: {e}")
        return []

    print("3. processing extracted text")
    extracted_text = []

    if not result or not result[0]:
        print("⚠️ No OCR results returned")
    else:
        print("we got a result...")
        for line in result[0]:
            # 1. Basic check for list structure
            if not line or len(line) < 2:
                continue
            
            # 2. Assign the potential (text, confidence) tuple
            ocr_data = line[1]
            
            # 3. CRITICAL FIX: Check if the data is a tuple and has exactly 2 elements
            if not isinstance(ocr_data, tuple) or len(ocr_data) != 2:
                continue
            
            # 4. Safe unpacking
            text, confidence = ocr_data
            
            # Only include high-confidence results
            if confidence > 0.7:
                extracted_text.append(text)

    print("4. combining full text")
    full_text = "\n".join(extracted_text)
    print(full_text)
    
    # Step 5: Local Parsing or Gemini Fallback (Not shown, but should follow here)
    # ... Your Gemini code to process full_text ...
    
    # Note: If this still takes 10 seconds, the delay is definitely within the 
    # ocr.ocr(img_array_orig) call itself, even with global initialization.
    # This might indicate an issue with your PaddleOCR version/setup or CPU/GPU configuration.
    
    # Returning empty list here as the rest of the Gemini code is omitted
    return []