# from flask import Flask, request, jsonify
# from flask_cors import CORS
# import google.generativeai as genai
# import os
# from dotenv import load_dotenv
# from werkzeug.utils import secure_filename
# import threading
# import time
# from paddleocr import PaddleOCR
# import uuid

# # Import your existing functions
# from scripts.extract_label import extract_ingredients_hybrid, extract_label
# from scripts.databasemethods import (
#     setup_database,
#     add_ingredient,
#     view_all_ingredients,
#     find_similar_ingredients,
#     preload_database,
#     clear_all_ingredients
# )
# from scripts.filter_ingredients_new import filter_ingredients, batch_analyze_ingredients


# # Load environment variables
# load_dotenv()

# app = Flask(__name__)
# # CORS(app, resources={r"/api/*": {"origins": "*"}})

# CORS(app,
#      resources={r"/api/*": {
#          "origins": ["http://localhost:3000", "http://127.0.0.1:3000"],
#          "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
#          "supports_credentials": True,
#          "expose_headers": ["Content-Type", "Authorization"]
#      }})

# # Configuration
# UPLOAD_FOLDER = 'uploads'
# ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# # Global variables
# model = None
# ocr = None
# analysis_cache = {}  # Store analysis results by job_id

# def allowed_file(filename):
#     return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# def initialize_model_and_database():
#     """Initialize Gemini model and database on startup"""
#     global model, ocr
    
#     print("🚀 Initializing Gemini model...")
#     API_KEY = os.getenv('API_KEY')
#     genai.configure(api_key=API_KEY)
#     model = genai.GenerativeModel('gemini-2.5-flash')
#     print("✅ Gemini model initialized")
    
#     print("🗄️ Setting up database...")
#     setup_database()
#     print("✅ Database setup complete")

# def seed_database_background():
#     """Seed database with common ingredients in background"""
#     print("🌱 Starting database seeding...")
    
#     common_ingredients = {
#     # Dairy & Dairy Derivatives
#     "milk": {"vegan": 0, "vegetarian": 1, "halal": 1, "gluten-free": 1, 
#              "lactose-intolerant": 0, "nut-allergy": 1, "anti-inflammatory": 0, "low-sugar": 1},
#     "milk fat": {"vegan": 0, "vegetarian": 1, "halal": 1, "gluten-free": 1,
#                  "lactose-intolerant": 0, "nut-allergy": 1, "anti-inflammatory": 0, "low-sugar": 1},
#     "butterfat": {"vegan": 0, "vegetarian": 1, "halal": 1, "gluten-free": 1,
#                   "lactose-intolerant": 0, "nut-allergy": 1, "anti-inflammatory": 0, "low-sugar": 1},
#     "butter": {"vegan": 0, "vegetarian": 1, "halal": 1, "gluten-free": 1,
#                "lactose-intolerant": 0, "nut-allergy": 1, "anti-inflammatory": 0, "low-sugar": 1},
#     "cheese": {"vegan": 0, "vegetarian": 1, "halal": 1, "gluten-free": 1,
#                "lactose-intolerant": 0, "nut-allergy": 1, "anti-inflammatory": 0, "low-sugar": 1},
#     "whey": {"vegan": 0, "vegetarian": 1, "halal": 1, "gluten-free": 1,
#              "lactose-intolerant": 0, "nut-allergy": 1, "anti-inflammatory": 0, "low-sugar": 1},
#     "whey protein": {"vegan": 0, "vegetarian": 1, "halal": 1, "gluten-free": 1,
#                      "lactose-intolerant": 0, "nut-allergy": 1, "anti-inflammatory": 0, "low-sugar": 1},
#     "cream": {"vegan": 0, "vegetarian": 1, "halal": 1, "gluten-free": 1,
#               "lactose-intolerant": 0, "nut-allergy": 1, "anti-inflammatory": 0, "low-sugar": 1},
#     "yogurt": {"vegan": 0, "vegetarian": 1, "halal": 1, "gluten-free": 1,
#                "lactose-intolerant": 0, "nut-allergy": 1, "anti-inflammatory": 0, "low-sugar": 1},
#     "casein": {"vegan": 0, "vegetarian": 1, "halal": 1, "gluten-free": 1,
#                "lactose-intolerant": 0, "nut-allergy": 1, "anti-inflammatory": 0, "low-sugar": 1},
#     "lactose": {"vegan": 0, "vegetarian": 1, "halal": 1, "gluten-free": 1,
#                 "lactose-intolerant": 0, "nut-allergy": 1, "anti-inflammatory": 0, "low-sugar": 1},
    
#     # Grains & Flour
#     "wheat flour": {"vegan": 1, "vegetarian": 1, "halal": 1, "gluten-free": 0,
#                    "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 0, "low-sugar": 1},
#     "wheat": {"vegan": 1, "vegetarian": 1, "halal": 1, "gluten-free": 0,
#               "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 0, "low-sugar": 1},
#     "enriched flour": {"vegan": 1, "vegetarian": 1, "halal": 1, "gluten-free": 0,
#                        "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 0, "low-sugar": 1},
#     "barley": {"vegan": 1, "vegetarian": 1, "halal": 1, "gluten-free": 0,
#               "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 1, "low-sugar": 1},
#     "barley malt": {"vegan": 1, "vegetarian": 1, "halal": 1, "gluten-free": 0,
#                     "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 0, "low-sugar": 0},
#     "oats": {"vegan": 1, "vegetarian": 1, "halal": 1, "gluten-free": 1,
#             "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 1, "low-sugar": 1},
#     "rice": {"vegan": 1, "vegetarian": 1, "halal": 1, "gluten-free": 1,
#             "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 1, "low-sugar": 1},
#     "rice flour": {"vegan": 1, "vegetarian": 1, "halal": 1, "gluten-free": 1,
#                    "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 1, "low-sugar": 1},
#     "corn": {"vegan": 1, "vegetarian": 1, "halal": 1, "gluten-free": 1,
#             "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 0, "low-sugar": 1},
#     "cornstarch": {"vegan": 1, "vegetarian": 1, "halal": 1, "gluten-free": 1,
#                    "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 0, "low-sugar": 1},
    
#     # Nuts & Seeds
#     "almonds": {"vegan": 1, "vegetarian": 1, "halal": 1, "gluten-free": 1,
#                "lactose-intolerant": 1, "nut-allergy": 0, "anti-inflammatory": 1, "low-sugar": 1},
#     "peanuts": {"vegan": 1, "vegetarian": 1, "halal": 1, "gluten-free": 1,
#                "lactose-intolerant": 1, "nut-allergy": 0, "anti-inflammatory": 1, "low-sugar": 1},
#     "peanut butter": {"vegan": 1, "vegetarian": 1, "halal": 1, "gluten-free": 1,
#                       "lactose-intolerant": 1, "nut-allergy": 0, "anti-inflammatory": 1, "low-sugar": 1},
#     "walnuts": {"vegan": 1, "vegetarian": 1, "halal": 1, "gluten-free": 1,
#                "lactose-intolerant": 1, "nut-allergy": 0, "anti-inflammatory": 1, "low-sugar": 1},
#     "cashews": {"vegan": 1, "vegetarian": 1, "halal": 1, "gluten-free": 1,
#                 "lactose-intolerant": 1, "nut-allergy": 0, "anti-inflammatory": 1, "low-sugar": 1},
#     "pecans": {"vegan": 1, "vegetarian": 1, "halal": 1, "gluten-free": 1,
#                "lactose-intolerant": 1, "nut-allergy": 0, "anti-inflammatory": 1, "low-sugar": 1},
    
#     # Meat & Poultry
#     "chicken": {"vegan": 0, "vegetarian": 0, "halal": 1, "gluten-free": 1,
#                "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 0, "low-sugar": 1},
#     "chicken fat": {"vegan": 0, "vegetarian": 0, "halal": 1, "gluten-free": 1,
#                     "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 0, "low-sugar": 1},
#     "turkey": {"vegan": 0, "vegetarian": 0, "halal": 1, "gluten-free": 1,
#                "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 0, "low-sugar": 1},
#     "beef": {"vegan": 0, "vegetarian": 0, "halal": 1, "gluten-free": 1,
#             "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 0, "low-sugar": 1},
#     "beef fat": {"vegan": 0, "vegetarian": 0, "halal": 1, "gluten-free": 1,
#                  "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 0, "low-sugar": 1},
#     "lamb": {"vegan": 0, "vegetarian": 0, "halal": 1, "gluten-free": 1,
#             "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 0, "low-sugar": 1},
#     "pork": {"vegan": 0, "vegetarian": 0, "halal": 0, "gluten-free": 1,
#             "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 0, "low-sugar": 1},
#     "pork fat": {"vegan": 0, "vegetarian": 0, "halal": 0, "gluten-free": 1,
#                  "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 0, "low-sugar": 1},
#     "bacon": {"vegan": 0, "vegetarian": 0, "halal": 0, "gluten-free": 1,
#              "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 0, "low-sugar": 1},
#     "ham": {"vegan": 0, "vegetarian": 0, "halal": 0, "gluten-free": 1,
#            "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 0, "low-sugar": 1},
#     "sausage": {"vegan": 0, "vegetarian": 0, "halal": 0, "gluten-free": 1,  # Often contains pork
#                "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 0, "low-sugar": 1},
#     "pepperoni": {"vegan": 0, "vegetarian": 0, "halal": 0, "gluten-free": 1,  # Usually pork
#                  "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 0, "low-sugar": 1},
#     "gelatin": {"vegan": 0, "vegetarian": 0, "halal": 0, "gluten-free": 1,  # Often pork-derived
#                "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 0, "low-sugar": 1},
#     "lard": {"vegan": 0, "vegetarian": 0, "halal": 0, "gluten-free": 1,
#             "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 0, "low-sugar": 1},
    
#     # Seafood
#     "fish": {"vegan": 0, "vegetarian": 0, "halal": 1, "gluten-free": 1,
#             "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 1, "low-sugar": 1},
#     "salmon": {"vegan": 0, "vegetarian": 0, "halal": 1, "gluten-free": 1,
#               "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 1, "low-sugar": 1},
#     "tuna": {"vegan": 0, "vegetarian": 0, "halal": 1, "gluten-free": 1,
#             "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 1, "low-sugar": 1},
#     "shrimp": {"vegan": 0, "vegetarian": 0, "halal": 1, "gluten-free": 1,
#               "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 0, "low-sugar": 1},
    
#     # Eggs
#     "eggs": {"vegan": 0, "vegetarian": 1, "halal": 1, "gluten-free": 1,
#             "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 0, "low-sugar": 1},
#     "egg whites": {"vegan": 0, "vegetarian": 1, "halal": 1, "gluten-free": 1,
#                   "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 0, "low-sugar": 1},
#     "egg yolks": {"vegan": 0, "vegetarian": 1, "halal": 1, "gluten-free": 1,
#                  "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 0, "low-sugar": 1},
    
#     # Sugars & Sweeteners
#     "sugar": {"vegan": 1, "vegetarian": 1, "halal": 1, "gluten-free": 1,
#              "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 0, "low-sugar": 0},
#     "cane sugar": {"vegan": 1, "vegetarian": 1, "halal": 1, "gluten-free": 1,
#                    "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 0, "low-sugar": 0},
#     "brown sugar": {"vegan": 1, "vegetarian": 1, "halal": 1, "gluten-free": 1,
#                     "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 0, "low-sugar": 0},
#     "high fructose corn syrup": {"vegan": 1, "vegetarian": 1, "halal": 1, "gluten-free": 1,
#                                  "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 0, "low-sugar": 0},
#     "corn syrup": {"vegan": 1, "vegetarian": 1, "halal": 1, "gluten-free": 1,
#                    "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 0, "low-sugar": 0},
#     "honey": {"vegan": 0, "vegetarian": 1, "halal": 1, "gluten-free": 1,
#              "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 0, "low-sugar": 0},
#     "maple syrup": {"vegan": 1, "vegetarian": 1, "halal": 1, "gluten-free": 1,
#                     "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 0, "low-sugar": 0},
#     "molasses": {"vegan": 1, "vegetarian": 1, "halal": 1, "gluten-free": 1,
#                 "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 0, "low-sugar": 0},
#     "dextrose": {"vegan": 1, "vegetarian": 1, "halal": 1, "gluten-free": 1,
#                 "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 0, "low-sugar": 0},
#     "fructose": {"vegan": 1, "vegetarian": 1, "halal": 1, "gluten-free": 1,
#                 "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 0, "low-sugar": 0},
    
#     # Oils & Fats
#     "soybean oil": {"vegan": 1, "vegetarian": 1, "halal": 1, "gluten-free": 1,
#                    "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 0, "low-sugar": 1},
#     "palm oil": {"vegan": 1, "vegetarian": 1, "halal": 1, "gluten-free": 1,
#                 "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 0, "low-sugar": 1},
#     "olive oil": {"vegan": 1, "vegetarian": 1, "halal": 1, "gluten-free": 1,
#                  "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 1, "low-sugar": 1},
#     "canola oil": {"vegan": 1, "vegetarian": 1, "halal": 1, "gluten-free": 1,
#                   "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 0, "low-sugar": 1},
#     "coconut oil": {"vegan": 1, "vegetarian": 1, "halal": 1, "gluten-free": 1,
#                    "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 0, "low-sugar": 1},
#     "vegetable oil": {"vegan": 1, "vegetarian": 1, "halal": 1, "gluten-free": 1,
#                      "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 0, "low-sugar": 1},
#     "sunflower oil": {"vegan": 1, "vegetarian": 1, "halal": 1, "gluten-free": 1,
#                      "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 0, "low-sugar": 1},
    
#     # Common Additives & Flavors
#     "natural flavors": {"vegan": 1, "vegetarian": 1, "halal": 1, "gluten-free": 1,  # Usually plant-based but ambiguous
#                        "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 1, "low-sugar": 1},
#     "artificial flavors": {"vegan": 1, "vegetarian": 1, "halal": 1, "gluten-free": 1,
#                           "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 1, "low-sugar": 1},
#     "vanilla extract": {"vegan": 1, "vegetarian": 1, "halal": 1, "gluten-free": 1,
#                        "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 1, "low-sugar": 1},
#     "citric acid": {"vegan": 1, "vegetarian": 1, "halal": 1, "gluten-free": 1,
#                    "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 1, "low-sugar": 1},
#     "baking soda": {"vegan": 1, "vegetarian": 1, "halal": 1, "gluten-free": 1,
#                    "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 1, "low-sugar": 1},
#     "baking powder": {"vegan": 1, "vegetarian": 1, "halal": 1, "gluten-free": 1,
#                      "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 1, "low-sugar": 1},
#     "yeast": {"vegan": 1, "vegetarian": 1, "halal": 1, "gluten-free": 1,
#              "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 1, "low-sugar": 1},
#     "vinegar": {"vegan": 1, "vegetarian": 1, "halal": 1, "gluten-free": 1,
#                "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 1, "low-sugar": 1},
    
#     # Soy Products
#     "soy": {"vegan": 1, "vegetarian": 1, "halal": 1, "gluten-free": 1,
#            "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 0, "low-sugar": 1},
#     "soy lecithin": {"vegan": 1, "vegetarian": 1, "halal": 1, "gluten-free": 1,
#                     "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 0, "low-sugar": 1},
#     "tofu": {"vegan": 1, "vegetarian": 1, "halal": 1, "gluten-free": 1,
#             "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 0, "low-sugar": 1},
    
#     # Basic Ingredients
#     "salt": {"vegan": 1, "vegetarian": 1, "halal": 1, "gluten-free": 1,
#             "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 1, "low-sugar": 1},
#     "water": {"vegan": 1, "vegetarian": 1, "halal": 1, "gluten-free": 1,
#              "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 1, "low-sugar": 1},
#     "pepper": {"vegan": 1, "vegetarian": 1, "halal": 1, "gluten-free": 1,
#               "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 1, "low-sugar": 1},
#     "garlic": {"vegan": 1, "vegetarian": 1, "halal": 1, "gluten-free": 1,
#               "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 1, "low-sugar": 1},
#     "onion": {"vegan": 1, "vegetarian": 1, "halal": 1, "gluten-free": 1,
#              "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 1, "low-sugar": 1},
# }
    
#     for ingredient, flags in common_ingredients.items():
#         add_ingredient(ingredient, flags)
    
#     print(f"✅ Database seeded with {len(common_ingredients)} common ingredients")

# def analyze_ingredients_background(job_id, ingredients_list, filters):
#     """Analyze ingredients in background and store results"""
#     try:
#         print(f"🔬 Starting analysis for job {job_id}...")
#         analysis_cache[job_id]['status'] = 'analyzing'
        
#         # Run the filter_ingredients function
#         results, failing = filter_ingredients(
#             ingredients_list,
#             model,
#             filters,
#             similarity_threshold=0.85
#         )
        
#         # Store results
#         analysis_cache[job_id]['status'] = 'complete'
#         analysis_cache[job_id]['results'] = results
#         analysis_cache[job_id]['failing'] = failing

#         # print(results)
#         # print(failing)
        
#         print(f"✅ Analysis complete for job {job_id}")
        
#     except Exception as e:
#         print(f"❌ Analysis error for job {job_id}: {e}")
#         analysis_cache[job_id]['status'] = 'error'
#         analysis_cache[job_id]['error'] = str(e)

# # ========== ENDPOINTS ==========
# @app.route('/api/health', methods=['GET'])
# def health_check():
#     """Check if server is running and model is initialized"""
#     return jsonify({
#         'status': 'healthy',
#         'model_initialized': model is not None,
#         'database_ready': True
#     }), 200

# @app.route('/api/upload', methods=['POST'])
# def upload_image():
#     print("Image uploading...")
#     """
#     Step 1: Upload image and extract ingredients
#     Returns ingredients list immediately for frontend display
#     """
#     if 'file' not in request.files:
#         return jsonify({'error': 'No file provided'}), 400
    
#     file = request.files['file']
    
#     if file.filename == '':
#         return jsonify({'error': 'No file selected'}), 400
    
#     if not allowed_file(file.filename):
#         return jsonify({'error': 'Invalid file type'}), 400
    
#     ingredients_list = []
#     try:
#         # Save file
#         filename = secure_filename(file.filename)
#         filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
#         file.save(filepath)
        
#         print(f"📁 File uploaded: {filename}")
        
#         # Extract ingredients from image
#         print("🔍 Extracting ingredients from image...")
#         text_from_img = extract_label(model, filepath)
#         # ingredients_list = extract_ingredients_hybrid(ocr, model, filepath)
#         # print(f"✅ Extracted {len(ingredients_list)} ingredients")
        
#         # Format as list
#         ingredients_list = [item.strip().lower() for item in text_from_img.split(",")]
#         print(f"✅ Extracted {len(ingredients_list)} ingredients")
        
#         # # Generate job ID for tracking
#         # job_id = f"{int(time.time())}_{filename}"
#         job_id = f"{uuid.uuid4()}_{secure_filename(file.filename)}"
#         print(job_id)
        
#         # Clean up uploaded file
#         os.remove(filepath)
        
#         return jsonify({
#             'job_id': job_id,
#             'ingredients': ingredients_list,
#             'count': len(ingredients_list)
#         }), 200
        
#     except Exception as e:
#         print(f"❌ Error processing image: {e}")
#         return jsonify({'error': str(e)}), 500

# @app.route('/api/analyze', methods=['POST'])
# def start_analysis():
#     """
#     Step 2: Start analyzing ingredients against filters
#     Runs in background, returns immediately with job_id
#     """
#     data = request.get_json()
    
#     if not data or 'job_id' not in data or 'ingredients' not in data or 'filters' not in data:
#         return jsonify({'error': 'Missing required fields'}), 400
    
#     job_id = data['job_id']
#     ingredients_list = data['ingredients']
#     filters = data['filters']
    
#     if not isinstance(filters, list) or len(filters) == 0:
#         return jsonify({'error': 'Filters must be a non-empty list'}), 400
    
#     # Initialize cache entry
#     analysis_cache[job_id] = {
#         'status': 'pending',
#         'ingredients': ingredients_list,
#         'filters': filters
#     }
    
#     # Start analysis in background
#     thread = threading.Thread(
#         target=analyze_ingredients_background,
#         args=(job_id, ingredients_list, filters)
#     )
#     thread.daemon = True
#     thread.start()
    
#     print(f"🚀 Started analysis for job {job_id}")
    
#     return jsonify({
#         'job_id': job_id,
#         'status': 'pending',
#         'message': 'Analysis started'
#     }), 202

# @app.route('/api/status/<job_id>', methods=['GET'])
# def check_status(job_id):
#     """
#     Step 3: Check analysis status
#     Returns current progress/status without blocking
#     """
#     if job_id not in analysis_cache:
#         return jsonify({'error': 'Job not found'}), 404
    
#     job_data = analysis_cache[job_id]
    
#     response = {
#         'job_id': job_id,
#         'status': job_data['status']
#     }
    
#     if job_data['status'] == 'complete':
#         response['results'] = job_data['results']
#         response['failing'] = job_data['failing']
#     elif job_data['status'] == 'error':
#         response['error'] = job_data.get('error', 'Unknown error')
    
#     return jsonify(response), 200

# @app.route('/api/results/<job_id>', methods=['GET'])
# def get_results(job_id):
#     """
#     Step 4: Get final results (only returns when complete)
#     """
#     if job_id not in analysis_cache:
#         return jsonify({'error': 'Job not found'}), 404
    
#     job_data = analysis_cache[job_id]
    
#     if job_data['status'] == 'pending' or job_data['status'] == 'analyzing':
#         return jsonify({
#             'status': job_data['status'],
#             'message': 'Analysis still in progress'
#         }), 202
    
#     if job_data['status'] == 'error':
#         return jsonify({
#             'status': 'error',
#             'error': job_data.get('error', 'Unknown error')
#         }), 500
    
#     print(job_data['results'])
#     print(job_data['failing'])
#     print(job_data['filters'])
    
#     return jsonify({
#         'status': 'complete',
#         'results': job_data['results'],
#         'failing': job_data['failing'],
#         'ingredients': job_data['ingredients'],
#         'filters': job_data['filters']
#     }), 200

# # Initialize on startup
# initialize_model_and_database()

# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=5002, debug=True)

from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import os
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
import threading
import time
from paddleocr import PaddleOCR
import uuid
import psycopg2
from psycopg2 import pool

# Import your existing functions
from scripts.extract_label import extract_ingredients_hybrid, extract_label
from scripts.databasemethods import (
    setup_database,
    add_ingredient,
    view_all_ingredients,
    find_similar_ingredients,
    clear_all_ingredients,
    connect_db
)
from scripts.filter_ingredients_new import filter_ingredients, batch_analyze_ingredients


# Load environment variables
load_dotenv()

app = Flask(__name__)

CORS(app,
     resources={r"/api/*": {
         "origins": ["http://localhost:3000", "http://127.0.0.1:3000"],
         "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
         "supports_credentials": True,
         "expose_headers": ["Content-Type", "Authorization"]
     }})

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Global variables
model = None
ocr = None
analysis_cache = {}  # Store analysis results by job_id
db_pool = None  # PostgreSQL connection pool

def initialize_db_pool():
    """Initialize PostgreSQL connection pool"""
    global db_pool
    try:
        db_pool = psycopg2.pool.SimpleConnectionPool(
            1,  # minimum connections
            10,  # maximum connections
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", "5432"),
            database=os.getenv("DB_NAME", "ingredients_db"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", "postgres")
        )
        print("✅ PostgreSQL connection pool initialized")
        return True
    except Exception as e:
        print(f"❌ Failed to initialize database pool: {e}")
        return False

def get_db_connection():
    """Get a connection from the pool"""
    if db_pool:
        return db_pool.getconn()
    return None

def return_db_connection(conn):
    """Return a connection to the pool"""
    if db_pool and conn:
        db_pool.putconn(conn)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def initialize_model_and_database():
    """Initialize Gemini model and database on startup"""
    global model, ocr
    
    print("🚀 Initializing Gemini model...")
    API_KEY = os.getenv('API_KEY')
    if not API_KEY:
        print("❌ Warning: API_KEY not found in environment variables")
    else:
        genai.configure(api_key=API_KEY)
        model = genai.GenerativeModel('gemini-2.5-flash')
        print("✅ Gemini model initialized")
    
    print("🗄️ Setting up database connection pool...")
    if initialize_db_pool():
        print("🗄️ Setting up database schema...")
        try:
            setup_database()
            print("✅ Database setup complete")
        except Exception as e:
            print(f"❌ Database setup error: {e}")
    else:
        print("❌ Failed to initialize database - check your PostgreSQL configuration")

def seed_database_background():
    """Seed database with common ingredients in background"""
    print("🌱 Starting database seeding...")
    
    common_ingredients = {
        # Dairy & Dairy Derivatives
        "milk": {"vegan": 0, "vegetarian": 1, "halal": 1, "gluten-free": 1, 
                 "lactose-intolerant": 0, "nut-allergy": 1, "anti-inflammatory": 0, "low-sugar": 1},
        "milk fat": {"vegan": 0, "vegetarian": 1, "halal": 1, "gluten-free": 1,
                     "lactose-intolerant": 0, "nut-allergy": 1, "anti-inflammatory": 0, "low-sugar": 1},
        "butterfat": {"vegan": 0, "vegetarian": 1, "halal": 1, "gluten-free": 1,
                      "lactose-intolerant": 0, "nut-allergy": 1, "anti-inflammatory": 0, "low-sugar": 1},
        "butter": {"vegan": 0, "vegetarian": 1, "halal": 1, "gluten-free": 1,
                   "lactose-intolerant": 0, "nut-allergy": 1, "anti-inflammatory": 0, "low-sugar": 1},
        "cheese": {"vegan": 0, "vegetarian": 1, "halal": 1, "gluten-free": 1,
                   "lactose-intolerant": 0, "nut-allergy": 1, "anti-inflammatory": 0, "low-sugar": 1},
        "whey": {"vegan": 0, "vegetarian": 1, "halal": 1, "gluten-free": 1,
                 "lactose-intolerant": 0, "nut-allergy": 1, "anti-inflammatory": 0, "low-sugar": 1},
        "whey protein": {"vegan": 0, "vegetarian": 1, "halal": 1, "gluten-free": 1,
                         "lactose-intolerant": 0, "nut-allergy": 1, "anti-inflammatory": 0, "low-sugar": 1},
        "cream": {"vegan": 0, "vegetarian": 1, "halal": 1, "gluten-free": 1,
                  "lactose-intolerant": 0, "nut-allergy": 1, "anti-inflammatory": 0, "low-sugar": 1},
        "yogurt": {"vegan": 0, "vegetarian": 1, "halal": 1, "gluten-free": 1,
                   "lactose-intolerant": 0, "nut-allergy": 1, "anti-inflammatory": 0, "low-sugar": 1},
        "casein": {"vegan": 0, "vegetarian": 1, "halal": 1, "gluten-free": 1,
                   "lactose-intolerant": 0, "nut-allergy": 1, "anti-inflammatory": 0, "low-sugar": 1},
        "lactose": {"vegan": 0, "vegetarian": 1, "halal": 1, "gluten-free": 1,
                    "lactose-intolerant": 0, "nut-allergy": 1, "anti-inflammatory": 0, "low-sugar": 1},
        
        # Grains & Flour
        "wheat flour": {"vegan": 1, "vegetarian": 1, "halal": 1, "gluten-free": 0,
                       "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 0, "low-sugar": 1},
        "wheat": {"vegan": 1, "vegetarian": 1, "halal": 1, "gluten-free": 0,
                  "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 0, "low-sugar": 1},
        "enriched flour": {"vegan": 1, "vegetarian": 1, "halal": 1, "gluten-free": 0,
                           "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 0, "low-sugar": 1},
        "barley": {"vegan": 1, "vegetarian": 1, "halal": 1, "gluten-free": 0,
                  "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 1, "low-sugar": 1},
        "barley malt": {"vegan": 1, "vegetarian": 1, "halal": 1, "gluten-free": 0,
                        "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 0, "low-sugar": 0},
        "oats": {"vegan": 1, "vegetarian": 1, "halal": 1, "gluten-free": 1,
                "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 1, "low-sugar": 1},
        "rice": {"vegan": 1, "vegetarian": 1, "halal": 1, "gluten-free": 1,
                "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 1, "low-sugar": 1},
        "rice flour": {"vegan": 1, "vegetarian": 1, "halal": 1, "gluten-free": 1,
                       "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 1, "low-sugar": 1},
        "corn": {"vegan": 1, "vegetarian": 1, "halal": 1, "gluten-free": 1,
                "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 0, "low-sugar": 1},
        "cornstarch": {"vegan": 1, "vegetarian": 1, "halal": 1, "gluten-free": 1,
                       "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 0, "low-sugar": 1},
        
        # Nuts & Seeds
        "almonds": {"vegan": 1, "vegetarian": 1, "halal": 1, "gluten-free": 1,
                   "lactose-intolerant": 1, "nut-allergy": 0, "anti-inflammatory": 1, "low-sugar": 1},
        "peanuts": {"vegan": 1, "vegetarian": 1, "halal": 1, "gluten-free": 1,
                   "lactose-intolerant": 1, "nut-allergy": 0, "anti-inflammatory": 1, "low-sugar": 1},
        "peanut butter": {"vegan": 1, "vegetarian": 1, "halal": 1, "gluten-free": 1,
                          "lactose-intolerant": 1, "nut-allergy": 0, "anti-inflammatory": 1, "low-sugar": 1},
        "walnuts": {"vegan": 1, "vegetarian": 1, "halal": 1, "gluten-free": 1,
                   "lactose-intolerant": 1, "nut-allergy": 0, "anti-inflammatory": 1, "low-sugar": 1},
        "cashews": {"vegan": 1, "vegetarian": 1, "halal": 1, "gluten-free": 1,
                    "lactose-intolerant": 1, "nut-allergy": 0, "anti-inflammatory": 1, "low-sugar": 1},
        "pecans": {"vegan": 1, "vegetarian": 1, "halal": 1, "gluten-free": 1,
                   "lactose-intolerant": 1, "nut-allergy": 0, "anti-inflammatory": 1, "low-sugar": 1},
        
        # Meat & Poultry
        "chicken": {"vegan": 0, "vegetarian": 0, "halal": 1, "gluten-free": 1,
                   "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 0, "low-sugar": 1},
        "chicken fat": {"vegan": 0, "vegetarian": 0, "halal": 1, "gluten-free": 1,
                        "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 0, "low-sugar": 1},
        "turkey": {"vegan": 0, "vegetarian": 0, "halal": 1, "gluten-free": 1,
                   "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 0, "low-sugar": 1},
        "beef": {"vegan": 0, "vegetarian": 0, "halal": 1, "gluten-free": 1,
                "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 0, "low-sugar": 1},
        "beef fat": {"vegan": 0, "vegetarian": 0, "halal": 1, "gluten-free": 1,
                     "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 0, "low-sugar": 1},
        "lamb": {"vegan": 0, "vegetarian": 0, "halal": 1, "gluten-free": 1,
                "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 0, "low-sugar": 1},
        "pork": {"vegan": 0, "vegetarian": 0, "halal": 0, "gluten-free": 1,
                "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 0, "low-sugar": 1},
        "pork fat": {"vegan": 0, "vegetarian": 0, "halal": 0, "gluten-free": 1,
                     "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 0, "low-sugar": 1},
        "bacon": {"vegan": 0, "vegetarian": 0, "halal": 0, "gluten-free": 1,
                 "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 0, "low-sugar": 1},
        "ham": {"vegan": 0, "vegetarian": 0, "halal": 0, "gluten-free": 1,
               "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 0, "low-sugar": 1},
        "sausage": {"vegan": 0, "vegetarian": 0, "halal": 0, "gluten-free": 1,
                   "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 0, "low-sugar": 1},
        "pepperoni": {"vegan": 0, "vegetarian": 0, "halal": 0, "gluten-free": 1,
                     "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 0, "low-sugar": 1},
        "gelatin": {"vegan": 0, "vegetarian": 0, "halal": 0, "gluten-free": 1,
                   "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 0, "low-sugar": 1},
        "lard": {"vegan": 0, "vegetarian": 0, "halal": 0, "gluten-free": 1,
                "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 0, "low-sugar": 1},
        
        # Seafood
        "fish": {"vegan": 0, "vegetarian": 0, "halal": 1, "gluten-free": 1,
                "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 1, "low-sugar": 1},
        "salmon": {"vegan": 0, "vegetarian": 0, "halal": 1, "gluten-free": 1,
                  "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 1, "low-sugar": 1},
        "tuna": {"vegan": 0, "vegetarian": 0, "halal": 1, "gluten-free": 1,
                "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 1, "low-sugar": 1},
        "shrimp": {"vegan": 0, "vegetarian": 0, "halal": 1, "gluten-free": 1,
                  "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 0, "low-sugar": 1},
        
        # Eggs
        "eggs": {"vegan": 0, "vegetarian": 1, "halal": 1, "gluten-free": 1,
                "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 0, "low-sugar": 1},
        "egg whites": {"vegan": 0, "vegetarian": 1, "halal": 1, "gluten-free": 1,
                      "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 0, "low-sugar": 1},
        "egg yolks": {"vegan": 0, "vegetarian": 1, "halal": 1, "gluten-free": 1,
                     "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 0, "low-sugar": 1},
        
        # Sugars & Sweeteners
        "sugar": {"vegan": 1, "vegetarian": 1, "halal": 1, "gluten-free": 1,
                 "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 0, "low-sugar": 0},
        "cane sugar": {"vegan": 1, "vegetarian": 1, "halal": 1, "gluten-free": 1,
                       "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 0, "low-sugar": 0},
        "brown sugar": {"vegan": 1, "vegetarian": 1, "halal": 1, "gluten-free": 1,
                        "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 0, "low-sugar": 0},
        "high fructose corn syrup": {"vegan": 1, "vegetarian": 1, "halal": 1, "gluten-free": 1,
                                     "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 0, "low-sugar": 0},
        "corn syrup": {"vegan": 1, "vegetarian": 1, "halal": 1, "gluten-free": 1,
                       "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 0, "low-sugar": 0},
        "honey": {"vegan": 0, "vegetarian": 1, "halal": 1, "gluten-free": 1,
                 "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 0, "low-sugar": 0},
        "maple syrup": {"vegan": 1, "vegetarian": 1, "halal": 1, "gluten-free": 1,
                        "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 0, "low-sugar": 0},
        "molasses": {"vegan": 1, "vegetarian": 1, "halal": 1, "gluten-free": 1,
                    "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 0, "low-sugar": 0},
        "dextrose": {"vegan": 1, "vegetarian": 1, "halal": 1, "gluten-free": 1,
                    "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 0, "low-sugar": 0},
        "fructose": {"vegan": 1, "vegetarian": 1, "halal": 1, "gluten-free": 1,
                    "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 0, "low-sugar": 0},
        
        # Oils & Fats
        "soybean oil": {"vegan": 1, "vegetarian": 1, "halal": 1, "gluten-free": 1,
                       "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 0, "low-sugar": 1},
        "palm oil": {"vegan": 1, "vegetarian": 1, "halal": 1, "gluten-free": 1,
                    "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 0, "low-sugar": 1},
        "olive oil": {"vegan": 1, "vegetarian": 1, "halal": 1, "gluten-free": 1,
                     "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 1, "low-sugar": 1},
        "canola oil": {"vegan": 1, "vegetarian": 1, "halal": 1, "gluten-free": 1,
                      "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 0, "low-sugar": 1},
        "coconut oil": {"vegan": 1, "vegetarian": 1, "halal": 1, "gluten-free": 1,
                       "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 0, "low-sugar": 1},
        "vegetable oil": {"vegan": 1, "vegetarian": 1, "halal": 1, "gluten-free": 1,
                         "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 0, "low-sugar": 1},
        "sunflower oil": {"vegan": 1, "vegetarian": 1, "halal": 1, "gluten-free": 1,
                         "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 0, "low-sugar": 1},
        
        # Common Additives & Flavors
        "natural flavors": {"vegan": 1, "vegetarian": 1, "halal": 1, "gluten-free": 1,
                           "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 1, "low-sugar": 1},
        "artificial flavors": {"vegan": 1, "vegetarian": 1, "halal": 1, "gluten-free": 1,
                              "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 1, "low-sugar": 1},
        "vanilla extract": {"vegan": 1, "vegetarian": 1, "halal": 1, "gluten-free": 1,
                           "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 1, "low-sugar": 1},
        "citric acid": {"vegan": 1, "vegetarian": 1, "halal": 1, "gluten-free": 1,
                       "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 1, "low-sugar": 1},
        "baking soda": {"vegan": 1, "vegetarian": 1, "halal": 1, "gluten-free": 1,
                       "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 1, "low-sugar": 1},
        "baking powder": {"vegan": 1, "vegetarian": 1, "halal": 1, "gluten-free": 1,
                         "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 1, "low-sugar": 1},
        "yeast": {"vegan": 1, "vegetarian": 1, "halal": 1, "gluten-free": 1,
                 "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 1, "low-sugar": 1},
        "vinegar": {"vegan": 1, "vegetarian": 1, "halal": 1, "gluten-free": 1,
                   "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 1, "low-sugar": 1},
        
        # Soy Products
        "soy": {"vegan": 1, "vegetarian": 1, "halal": 1, "gluten-free": 1,
               "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 0, "low-sugar": 1},
        "soy lecithin": {"vegan": 1, "vegetarian": 1, "halal": 1, "gluten-free": 1,
                        "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 0, "low-sugar": 1},
        "tofu": {"vegan": 1, "vegetarian": 1, "halal": 1, "gluten-free": 1,
                "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 0, "low-sugar": 1},
        
        # Basic Ingredients
        "salt": {"vegan": 1, "vegetarian": 1, "halal": 1, "gluten-free": 1,
                "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 1, "low-sugar": 1},
        "water": {"vegan": 1, "vegetarian": 1, "halal": 1, "gluten-free": 1,
                 "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 1, "low-sugar": 1},
        "pepper": {"vegan": 1, "vegetarian": 1, "halal": 1, "gluten-free": 1,
                  "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 1, "low-sugar": 1},
        "garlic": {"vegan": 1, "vegetarian": 1, "halal": 1, "gluten-free": 1,
                  "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 1, "low-sugar": 1},
        "onion": {"vegan": 1, "vegetarian": 1, "halal": 1, "gluten-free": 1,
                 "lactose-intolerant": 1, "nut-allergy": 1, "anti-inflammatory": 1, "low-sugar": 1},
    }
    
    try:
        for ingredient, flags in common_ingredients.items():
            add_ingredient(ingredient, flags)
        
        print(f"✅ Database seeded with {len(common_ingredients)} common ingredients")
    except Exception as e:
        print(f"❌ Error seeding database: {e}")

def analyze_ingredients_background(job_id, ingredients_list, filters):
    """Analyze ingredients in background and store results"""
    try:
        print(f"🔬 Starting analysis for job {job_id}...")
        analysis_cache[job_id]['status'] = 'analyzing'
        
        # Run the filter_ingredients function
        results, failing = filter_ingredients(
            ingredients_list,
            model,
            filters,
            similarity_threshold=0.85
        )
        
        # Store results
        analysis_cache[job_id]['status'] = 'complete'
        analysis_cache[job_id]['results'] = results
        analysis_cache[job_id]['failing'] = failing
        
        print(f"✅ Analysis complete for job {job_id}")
        
    except Exception as e:
        print(f"❌ Analysis error for job {job_id}: {e}")
        analysis_cache[job_id]['status'] = 'error'
        analysis_cache[job_id]['error'] = str(e)

# ========== ENDPOINTS ==========
@app.route('/api/health', methods=['GET'])
def health_check():
    """Check if server is running and model is initialized"""
    db_healthy = False
    try:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.close()
            return_db_connection(conn)
            db_healthy = True
    except Exception as e:
        print(f"Database health check failed: {e}")
    
    return jsonify({
        'status': 'healthy' if (model is not None and db_healthy) else 'degraded',
        'model_initialized': model is not None,
        'database_ready': db_healthy
    }), 200 if (model is not None and db_healthy) else 503

@app.route('/api/upload', methods=['POST'])
def upload_image():
    """
    Step 1: Upload image and extract ingredients
    Returns ingredients list immediately for frontend display
    """
    print("📤 Image uploading...")
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type'}), 400
    
    ingredients_list = []
    try:
        # Save file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        print(f"📁 File uploaded: {filename}")
        
        # Extract ingredients from image
        print("🔍 Extracting ingredients from image...")
        text_from_img = extract_label(model, filepath)
        
        # Format as list
        ingredients_list = [item.strip().lower() for item in text_from_img.split(",")]
        print(f"✅ Extracted {len(ingredients_list)} ingredients")
        
        # Generate job ID for tracking
        job_id = f"{uuid.uuid4()}_{secure_filename(file.filename)}"
        print(f"🆔 Generated job ID: {job_id}")
        
        # Clean up uploaded file
        os.remove(filepath)
        
        return jsonify({
            'job_id': job_id,
            'ingredients': ingredients_list,
            'count': len(ingredients_list)
        }), 200
        
    except Exception as e:
        print(f"❌ Error processing image: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/analyze', methods=['POST'])
def start_analysis():
    """
    Step 2: Start analyzing ingredients against filters
    Runs in background, returns immediately with job_id
    """
    data = request.get_json()
    
    if not data or 'job_id' not in data or 'ingredients' not in data or 'filters' not in data:
        return jsonify({'error': 'Missing required fields'}), 400
    
    job_id = data['job_id']
    ingredients_list = data['ingredients']
    filters = data['filters']
    
    if not isinstance(filters, list) or len(filters) == 0:
        return jsonify({'error': 'Filters must be a non-empty list'}), 400
    
    # Initialize cache entry
    analysis_cache[job_id] = {
        'status': 'pending',
        'ingredients': ingredients_list,
        'filters': filters
    }
    
    # Start analysis in background
    thread = threading.Thread(
        target=analyze_ingredients_background,
        args=(job_id, ingredients_list, filters)
    )
    thread.daemon = True
    thread.start()
    
    print(f"🚀 Started analysis for job {job_id}")
    
    return jsonify({
        'job_id': job_id,
        'status': 'pending',
        'message': 'Analysis started'
    }), 202

@app.route('/api/status/<job_id>', methods=['GET'])
def check_status(job_id):
    """
    Step 3: Check analysis status
    Returns current progress/status without blocking
    """
    if job_id not in analysis_cache:
        return jsonify({'error': 'Job not found'}), 404
    
    job_data = analysis_cache[job_id]
    
    response = {
        'job_id': job_id,
        'status': job_data['status']
    }
    
    if job_data['status'] == 'complete':
        response['results'] = job_data['results']
        response['failing'] = job_data['failing']
    elif job_data['status'] == 'error':
        response['error'] = job_data.get('error', 'Unknown error')
    
    return jsonify(response), 200

@app.route('/api/results/<job_id>', methods=['GET'])
def get_results(job_id):
    """
    Step 4: Get final results (only returns when complete)
    """
    if job_id not in analysis_cache:
        return jsonify({'error': 'Job not found'}), 404
    
    job_data = analysis_cache[job_id]
    
    if job_data['status'] == 'pending' or job_data['status'] == 'analyzing':
        return jsonify({
            'status': job_data['status'],
            'message': 'Analysis still in progress'
        }), 202
    
    if job_data['status'] == 'error':
        return jsonify({
            'status': 'error',
            'error': job_data.get('error', 'Unknown error')
        }), 500
    
    print(f"📊 Returning results for job {job_id}")
    
    return jsonify({
        'status': 'complete',
        'results': job_data['results'],
        'failing': job_data['failing'],
        'ingredients': job_data['ingredients'],
        'filters': job_data['filters']
    }), 200

@app.route('/api/seed', methods=['POST'])
def seed_database():
    """Manually trigger database seeding"""
    try:
        thread = threading.Thread(target=seed_database_background)
        thread.daemon = True
        thread.start()
        return jsonify({
            'status': 'success',
            'message': 'Database seeding started in background'
        }), 202
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Cleanup function
@app.teardown_appcontext
def cleanup_db_pool(exception=None):
    """Close all database connections when app context ends"""
    global db_pool
    if db_pool:
        db_pool.closeall()
        print("🔒 Database connection pool closed")

# Initialize on startup
initialize_model_and_database()

# Optional: Seed database on startup (comment out if not needed)
# threading.Thread(target=seed_database_background, daemon=True).start()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)