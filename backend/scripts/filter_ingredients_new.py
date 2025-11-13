import json
from scripts.databasemethods import (
    get_or_infer_properties, 
    add_ingredient
)

def analyze_ingredient_with_llm(ingredient, model):
    """
    Use LLM to determine dietary properties for unknown ingredient
    Returns dietary_flags dict
    """
    prompt = f"""Analyze the ingredient "{ingredient}" for dietary restrictions.

For each restriction, respond with 1 if the ingredient PASSES (is safe), or 0 if it FAILS (violates the restriction):

- vegan: Does NOT contain any animal products (meat, dairy, eggs, honey, etc.)
- vegetarian: Does NOT contain meat or fish
- halal: Does NOT contain pork, alcohol, or non-halal animal products
- gluten-free: Does NOT contain wheat, barley, rye, or gluten
- lactose-intolerant: Does NOT contain lactose or dairy
- nut-allergy: Does NOT contain any tree nuts or peanuts
- anti-inflammatory: Does NOT contain inflammatory ingredients (saturated fats, refined sugars, processed oils)
- low-sugar: Does NOT contain added sugars or high-glycemic sweeteners

Respond ONLY with valid JSON in this exact format:
{{
  "vegan": 0,
  "vegetarian": 1,
  "halal": 1,
  "gluten-free": 1,
  "lactose-intolerant": 0,
  "nut-allergy": 1,
  "anti-inflammatory": 0,
  "low-sugar": 1
}}

No explanations, just the JSON object."""
    
    response = model.generate_content(prompt)
    
    # Clean and parse response
    text = response.text.strip()
    # Remove markdown code blocks if present
    text = text.replace('```json', '').replace('```', '').strip()
    
    try:
        dietary_flags = json.loads(text)
        return dietary_flags
    except json.JSONDecodeError as e:
        print(f"Error parsing LLM response: {e}")
        print(f"Response: {text}")
        # Return conservative defaults (fail everything)
        return {
            "vegan": 0,
            "vegetarian": 0,
            "halal": 0,
            "gluten-free": 0,
            "lactose-intolerant": 0,
            "nut-allergy": 0,
            "anti-inflammatory": 0,
            "low-sugar": 0
        }

def filter_ingredients(ingredients, model, user_filters, similarity_threshold=0.85):
    """
    Analyze ingredients against user's dietary filters using embeddings
    
    Args:
        ingredients: List of ingredient names from OCR
        model: Gemini model for LLM fallback
        user_filters: List of filter names (e.g., ["vegan", "halal"])
        similarity_threshold: Minimum similarity for inference (0.80-0.95)
    
    Returns:
        results: Dict of {filter_name: "pass" or "fail"}
        failing_ingredients: Dict of {filter_name: [list of ingredients]}
        stats: Dict with performance metrics
    """
    results = {}
    failing_ingredients = {}
    
    # Initialize results
    for filter_name in user_filters:
        results[filter_name] = "pass"
        failing_ingredients[filter_name] = []
    
    # Statistics
    # stats = {
    #     "total_ingredients": len(ingredients),
    #     "exact_matches": 0,
    #     "inferred_from_similarity": 0,
    #     "llm_calls": 0
    # }
    
    print(f"\nAnalyzing {len(ingredients)} ingredients...")
    print("-" * 60)
    
    # Process each ingredient
    for ingredient in ingredients:
        ingredient_lower = ingredient.lower().strip()
        
        # Get properties (exact match or similarity inference)
        properties, source = get_or_infer_properties(
            ingredient_lower, 
            similarity_threshold=similarity_threshold
        )
        
        # Track statistics
        if source == "exact":
            # stats["exact_matches"] += 1
            print(f"✓ {ingredient:<30} [exact match]")
        # elif source.startswith("similar:"):
            # stats["inferred_from_similarity"] += 1
            # Already printed in get_or_infer_properties
        elif source == "unknown":
            # Fallback to LLM
            print(f"⚠ {ingredient:<30} [calling LLM...]")
            # stats["llm_calls"] += 1
            
            dietary_flags = analyze_ingredient_with_llm(ingredient_lower, model)
            
            # Store in database for future use
            add_ingredient(ingredient_lower, dietary_flags, confidence=0.9)
            properties = dietary_flags
            print(f"  → Added to database")
        
        # Check against user's filters
        if properties:
            for filter_name in user_filters:
                # Properties use same keys as user_filters
                # 0 = fails filter, 1 = passes filter, None = unknown
                passes = properties.get(filter_name)

                print(passes)
                
                if passes == 0:  # Ingredient fails this filter
                    results[filter_name] = "fail"
                    failing_ingredients[filter_name].append(ingredient)
    
    # print("-" * 60)
    # print(f"Stats: {stats['exact_matches']} exact | " +
    #       f"{stats['inferred_from_similarity']} inferred | " +
    #       f"{stats['llm_calls']} LLM calls")
    # print()
    
    return results, failing_ingredients

def batch_analyze_ingredients(ingredients, model):
    """
    Alternative: Analyze ALL ingredients in a single LLM call
    Use this for the first scan to seed your database quickly
    
    Returns: Dict of {ingredient: dietary_flags}
    """
    ingredients_str = ", ".join(ingredients)
    
    prompt = f"""Analyze these ingredients for dietary restrictions: {ingredients_str}

For EACH ingredient, determine if it passes (1) or fails (0) these restrictions:
- vegan, vegetarian, halal, gluten-free, lactose-intolerant, nut-allergy, anti-inflammatory, low-sugar

Respond ONLY with valid JSON in this format:
{{
  "butter": {{"vegan": 0, "vegetarian": 1, "halal": 1, "gluten-free": 1, "lactose-intolerant": 0, "nut-allergy": 1, "anti-inflammatory": 0, "low-sugar": 1}},
  "flour": {{"vegan": 1, "vegetarian": 1, ...}},
  ...
}}"""
    
    response = model.generate_content(prompt)
    text = response.text.strip().replace('```json', '').replace('```', '').strip()
    
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        print(f"Batch analysis failed: {e}")
        return {}