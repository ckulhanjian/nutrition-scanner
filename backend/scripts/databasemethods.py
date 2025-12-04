# import sqlite3
# import json
# import numpy as np
# from sentence_transformers import SentenceTransformer

# # Initialize embedding model globally (loaded once)
# _embedding_model = None

# def get_embedding_model():
#     """Lazy load the embedding model"""
#     global _embedding_model
#     if _embedding_model is None:
#         print("Loading embedding model (one-time setup)...")
#         _embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
#     return _embedding_model

# def connect_db():
#     conn = sqlite3.connect("./database/ingredients.db")
#     conn.row_factory = sqlite3.Row
#     return conn

# def setup_database():
#     """Create tables with embedding support"""
#     conn = connect_db()
#     c = conn.cursor()
    
#     # Enhanced ingredients table with dietary flags and embeddings
#     c.execute('''
#         CREATE TABLE IF NOT EXISTS ingredients (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             name TEXT UNIQUE NOT NULL,
#             embedding BLOB,
            
#             -- Dietary restriction flags (1 = passes, 0 = fails)
#             is_vegan INTEGER DEFAULT NULL,
#             is_vegetarian INTEGER DEFAULT NULL,
#             is_halal INTEGER DEFAULT NULL,
#             is_gluten_free INTEGER DEFAULT NULL,
#             is_lactose_free INTEGER DEFAULT NULL,
#             is_nut_free INTEGER DEFAULT NULL,
#             is_anti_inflammatory INTEGER DEFAULT NULL,
#             is_low_sugar INTEGER DEFAULT NULL
#             )
#     ''')
    
#     conn.commit()
#     conn.close()
#     print("Database setup complete with embedding support")

# def serialize_embedding(embedding_array):
#     """Convert numpy array to bytes for storage - NUMBER ARRAY to BYTES"""
#     return embedding_array.tobytes()

# def deserialize_embedding(embedding_bytes):
#     """Convert bytes back to numpy array - BYTES to NUMBERS"""
#     if embedding_bytes is None:
#         return None
#     return np.frombuffer(embedding_bytes, dtype=np.float32)

# def generate_embedding(ingredient_name):
#     """Generate embedding vector for an ingredient - TEXT to NUMBERS"""
#     model = get_embedding_model()
#     embedding = model.encode(ingredient_name, convert_to_numpy=True)
#     return embedding.astype(np.float32)

# def cosine_similarity(vec1, vec2):
#     """Calculate similarity between two vectors (0-1, higher = more similar)"""
#     dot_product = np.dot(vec1, vec2)
#     norm1 = np.linalg.norm(vec1)
#     norm2 = np.linalg.norm(vec2)
#     return dot_product / (norm1 * norm2)

# def add_ingredient(ingredient_name, dietary_flags, confidence=1.0):
#     """
#     Add ingredient with dietary flags and auto-generated embedding
    
#     Args:
#         ingredient_name: Name of ingredient (e.g., "butter")
#         dietary_flags: Dict with keys matching filter names
#                       Example: {
#                           "vegan": 0,  # fails vegan
#                           "vegetarian": 1,  # passes vegetarian
#                           "halal": 1,
#                           "gluten-free": 1,
#                           "lactose-intolerant": 0,  # fails lactose-free
#                           "nut-allergy": 1,
#                           "anti-inflammatory": 0,
#                           "low-sugar": 1
#                       }
#         confidence: How confident we are (0-1)
#     """
#     conn = connect_db()
#     c = conn.cursor()
    
#     # Generate embedding
#     embedding = generate_embedding(ingredient_name)
#     embedding_blob = serialize_embedding(embedding)
    
#     # Map filter names to database columns
#     filter_to_column = {
#         "vegan": "is_vegan",
#         "vegetarian": "is_vegetarian",
#         "halal": "is_halal",
#         "gluten-free": "is_gluten_free",
#         "lactose-intolerant": "is_lactose_free",
#         "nut-allergy": "is_nut_free",
#         "anti-inflammatory": "is_anti_inflammatory",
#         "low-sugar": "is_low_sugar"
#     }
    
#     # Convert dietary_flags to column values
#     column_values = {}
#     for filter_name, column_name in filter_to_column.items():
#         if filter_name in dietary_flags:
#             # If ingredient fails filter, store 0; if passes, store 1
#             column_values[column_name] = dietary_flags[filter_name]
    
#     c.execute('''
#         INSERT OR REPLACE INTO ingredients 
#         (name, embedding, is_vegan, is_vegetarian, is_halal, is_gluten_free,
#          is_lactose_free, is_nut_free, is_anti_inflammatory, is_low_sugar)
#         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
#     ''', (
#         ingredient_name.lower(),
#         embedding_blob,
#         column_values.get("is_vegan"),
#         column_values.get("is_vegetarian"),
#         column_values.get("is_halal"),
#         column_values.get("is_gluten_free"),
#         column_values.get("is_lactose_free"),
#         column_values.get("is_nut_free"),
#         column_values.get("is_anti_inflammatory"),
#         column_values.get("is_low_sugar")
#     ))
    
#     conn.commit()
#     conn.close()

# def get_ingredient_properties(ingredient_name):
#     """Get dietary flags for an exact match"""
#     conn = connect_db()
#     c = conn.cursor()
#     c.execute("""
#         SELECT is_vegan, is_vegetarian, is_halal, is_gluten_free,
#                is_lactose_free, is_nut_free, is_anti_inflammatory, 
#                is_low_sugar
#         FROM ingredients 
#         WHERE name = ?
#     """, (ingredient_name.lower(),))
#     row = c.fetchone()
#     conn.close()
    
#     if row:
#         return {
#             "vegan": row["is_vegan"],
#             "vegetarian": row["is_vegetarian"],
#             "halal": row["is_halal"],
#             "gluten-free": row["is_gluten_free"],
#             "lactose-intolerant": row["is_lactose_free"],
#             "nut-allergy": row["is_nut_free"],
#             "anti-inflammatory": row["is_anti_inflammatory"],
#             "low-sugar": row["is_low_sugar"]
#         }
#     return None

# def find_similar_ingredients(ingredient_name, top_k=5, min_similarity=0.80):
#     """
#     Find similar ingredients using embedding similarity
    
#     Returns: List of (ingredient_name, similarity_score, properties) tuples
#     """
#     conn = connect_db()
#     c = conn.cursor()
    
#     # Generate embedding for query ingredient
#     query_embedding = generate_embedding(ingredient_name)
    
#     # Get all ingredients with embeddings
#     c.execute("""
#         SELECT name, embedding, is_vegan, is_vegetarian, is_halal, 
#                is_gluten_free, is_lactose_free, is_nut_free, 
#                is_anti_inflammatory, is_low_sugar
#         FROM ingredients 
#         WHERE embedding IS NOT NULL
#     """)
    
#     similarities = []
#     for row in c.fetchall():
#         stored_embedding = deserialize_embedding(row["embedding"])
#         similarity = cosine_similarity(query_embedding, stored_embedding)
        
#         if similarity >= min_similarity:
#             properties = {
#                 "vegan": row["is_vegan"],
#                 "vegetarian": row["is_vegetarian"],
#                 "halal": row["is_halal"],
#                 "gluten-free": row["is_gluten_free"],
#                 "lactose-intolerant": row["is_lactose_free"],
#                 "nut-allergy": row["is_nut_free"],
#                 "anti-inflammatory": row["is_anti_inflammatory"],
#                 "low-sugar": row["is_low_sugar"]
#             }
#             similarities.append((row["name"], similarity, properties))
    
#     conn.close()
    
#     # Sort by similarity and return top_k
#     similarities.sort(key=lambda x: x[1], reverse=True)
#     return similarities[:top_k]

# def get_or_infer_properties(ingredient_name, similarity_threshold=0.85):
#     """
#     Get ingredient properties with fallback to similarity search
    
#     Returns: (properties_dict, source)
#         - properties_dict: Dietary flags
#         - source: "exact" | "similar:<ingredient>" | "unknown"
#     """
#     # Try exact match first
#     properties = get_ingredient_properties(ingredient_name)
#     if properties:
#         print(properties)
#         return properties, "exact"
    
#     # Try similarity search
#     similar = find_similar_ingredients(ingredient_name, top_k=1, 
#                                       min_similarity=similarity_threshold)
    
#     if similar:
#         similar_name, similarity, similar_properties = similar[0]
#         print(f"  → Inferred from '{similar_name}' (similarity: {similarity:.2f})")
#         return similar_properties, f"similar:{similar_name}"
    
#     # Unknown ingredient
#     return None, "unknown"

# def view_all_ingredients():
#     """Display all ingredients and their dietary properties"""
#     conn = connect_db()
#     c = conn.cursor()
#     c.execute("""
#         SELECT name, is_vegan, is_vegetarian, is_halal, is_gluten_free,
#                is_lactose_free, is_nut_free, is_anti_inflammatory, 
#                is_low_sugar
#         FROM ingredients 
#         ORDER BY name
#     """)
#     rows = c.fetchall()
#     conn.close()
    
#     if not rows:
#         print("Database is empty - no ingredients found.")
#         return []
    
#     print(f"\n{'Ingredient':<25} {'Veg':<4} {'Vgn':<4} {'Hal':<4} {'GF':<4} " +
#           f"{'LF':<4} {'NF':<4} {'AI':<4} {'LS':<4} {'Conf':<5}")
#     print("-" * 85)
    
#     ingredients_list = []
#     for row in rows:
#         # Convert 1/0 to Y/N, None to ?
#         def flag(val):
#             return 'Y' if val == 1 else ('N' if val == 0 else '?')
        
#         print(f"{row['name']:<25} {flag(row['is_vegetarian']):<4} " +
#               f"{flag(row['is_vegan']):<4} {flag(row['is_halal']):<4} " +
#               f"{flag(row['is_gluten_free']):<4} {flag(row['is_lactose_free']):<4} " +
#               f"{flag(row['is_nut_free']):<4} {flag(row['is_anti_inflammatory']):<4} " +
#               f"{flag(row['is_low_sugar']):<4}")
        
#         ingredients_list.append(dict(row))
    
#     print(f"\nTotal ingredients: {len(rows)}\n")
#     return ingredients_list

# def clear_all_ingredients():
#     """Delete all ingredients from the database"""
#     conn = connect_db()
#     c = conn.cursor()
#     c.execute("DELETE FROM ingredients")
#     conn.commit()
#     rows_deleted = c.rowcount
#     conn.close()
#     print(f"Cleared {rows_deleted} ingredient(s) from the database.")
#     return rows_deleted

# def preload_database(json_path="data/preload.json"):
#     """
#     Load ingredients from JSON file
#     Expected format:
#     {
#         "butter": {
#             "vegan": 0, "vegetarian": 1, "halal": 1,
#             "gluten-free": 1, "lactose-intolerant": 0, ...
#         },
#         ...
#     }
#     """
#     conn = connect_db()
    
#     with open(json_path, "r") as f:
#         data = json.load(f)
    
#     print(f"Preloading {len(data)} ingredients...")
#     for ingredient_name, dietary_flags in data.items():
#         add_ingredient(ingredient_name, dietary_flags)
    
#     conn.close()
#     print(f"Preloaded {len(data)} ingredients with embeddings")

# # Legacy function for backward compatibility
# def get_tags(ingredient_name):
#     """DEPRECATED: Use get_ingredient_properties() instead"""
#     properties = get_ingredient_properties(ingredient_name)
#     if properties:
#         # Convert to old tag format if needed
#         tags = []
#         if properties.get("vegan") == 0:
#             tags.append("not-vegan")
#         if properties.get("lactose-intolerant") == 0:
#             tags.append("contains-lactose")
#         return tags
#     return None

# def main():
#     clear_all_ingredients()

import psycopg2
from psycopg2.extras import RealDictCursor
import json
import numpy as np
from sentence_transformers import SentenceTransformer
import os

# Initialize embedding model globally (loaded once)
_embedding_model = None

def get_embedding_model():
    """Lazy load the embedding model"""
    global _embedding_model
    if _embedding_model is None:
        print("Loading embedding model (one-time setup)...")
        _embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
    return _embedding_model

def connect_db():
    """Connect to PostgreSQL database"""
    # Get connection parameters from environment variables or use defaults
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        database=os.getenv("DB_NAME", "ingredients_db"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "postgres")
    )
    return conn

def setup_database():
    """Create tables with embedding support"""
    conn = connect_db()
    c = conn.cursor()
    
    # Enhanced ingredients table with dietary flags and embeddings
    c.execute('''
        CREATE TABLE IF NOT EXISTS ingredients (
            id SERIAL PRIMARY KEY,
            name TEXT UNIQUE NOT NULL,
            embedding BYTEA,
            
            -- Dietary restriction flags (1 = passes, 0 = fails)
            is_vegan INTEGER DEFAULT NULL,
            is_vegetarian INTEGER DEFAULT NULL,
            is_halal INTEGER DEFAULT NULL,
            is_gluten_free INTEGER DEFAULT NULL,
            is_lactose_free INTEGER DEFAULT NULL,
            is_nut_free INTEGER DEFAULT NULL,
            is_anti_inflammatory INTEGER DEFAULT NULL,
            is_low_sugar INTEGER DEFAULT NULL
        )
    ''')
    
    # Create index on name for faster lookups
    c.execute('''
        CREATE INDEX IF NOT EXISTS idx_ingredients_name 
        ON ingredients(name)
    ''')
    
    conn.commit()
    conn.close()
    print("Database setup complete with embedding support")

def serialize_embedding(embedding_array):
    """Convert numpy array to bytes for storage - NUMBER ARRAY to BYTES"""
    return psycopg2.Binary(embedding_array.tobytes())

def deserialize_embedding(embedding_bytes):
    """Convert bytes back to numpy array - BYTES to NUMBERS"""
    if embedding_bytes is None:
        return None
    # PostgreSQL returns memoryview or bytes
    if isinstance(embedding_bytes, memoryview):
        embedding_bytes = embedding_bytes.tobytes()
    return np.frombuffer(embedding_bytes, dtype=np.float32)

def generate_embedding(ingredient_name):
    """Generate embedding vector for an ingredient - TEXT to NUMBERS"""
    model = get_embedding_model()
    embedding = model.encode(ingredient_name, convert_to_numpy=True)
    return embedding.astype(np.float32)

def cosine_similarity(vec1, vec2):
    """Calculate similarity between two vectors (0-1, higher = more similar)"""
    dot_product = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    return dot_product / (norm1 * norm2)

def add_ingredient(ingredient_name, dietary_flags, confidence=1.0):
    """
    Add ingredient with dietary flags and auto-generated embedding
    
    Args:
        ingredient_name: Name of ingredient (e.g., "butter")
        dietary_flags: Dict with keys matching filter names
                      Example: {
                          "vegan": 0,  # fails vegan
                          "vegetarian": 1,  # passes vegetarian
                          "halal": 1,
                          "gluten-free": 1,
                          "lactose-intolerant": 0,  # fails lactose-free
                          "nut-allergy": 1,
                          "anti-inflammatory": 0,
                          "low-sugar": 1
                      }
        confidence: How confident we are (0-1)
    """
    conn = connect_db()
    c = conn.cursor()
    
    # Generate embedding
    embedding = generate_embedding(ingredient_name)
    embedding_blob = serialize_embedding(embedding)
    
    # Map filter names to database columns
    filter_to_column = {
        "vegan": "is_vegan",
        "vegetarian": "is_vegetarian",
        "halal": "is_halal",
        "gluten-free": "is_gluten_free",
        "lactose-intolerant": "is_lactose_free",
        "nut-allergy": "is_nut_free",
        "anti-inflammatory": "is_anti_inflammatory",
        "low-sugar": "is_low_sugar"
    }
    
    # Convert dietary_flags to column values
    column_values = {}
    for filter_name, column_name in filter_to_column.items():
        if filter_name in dietary_flags:
            # If ingredient fails filter, store 0; if passes, store 1
            column_values[column_name] = dietary_flags[filter_name]
    
    # PostgreSQL uses ON CONFLICT for upsert
    c.execute('''
        INSERT INTO ingredients 
        (name, embedding, is_vegan, is_vegetarian, is_halal, is_gluten_free,
         is_lactose_free, is_nut_free, is_anti_inflammatory, is_low_sugar)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (name) DO UPDATE SET
            embedding = EXCLUDED.embedding,
            is_vegan = EXCLUDED.is_vegan,
            is_vegetarian = EXCLUDED.is_vegetarian,
            is_halal = EXCLUDED.is_halal,
            is_gluten_free = EXCLUDED.is_gluten_free,
            is_lactose_free = EXCLUDED.is_lactose_free,
            is_nut_free = EXCLUDED.is_nut_free,
            is_anti_inflammatory = EXCLUDED.is_anti_inflammatory,
            is_low_sugar = EXCLUDED.is_low_sugar
    ''', (
        ingredient_name.lower(),
        embedding_blob,
        column_values.get("is_vegan"),
        column_values.get("is_vegetarian"),
        column_values.get("is_halal"),
        column_values.get("is_gluten_free"),
        column_values.get("is_lactose_free"),
        column_values.get("is_nut_free"),
        column_values.get("is_anti_inflammatory"),
        column_values.get("is_low_sugar")
    ))
    
    conn.commit()
    conn.close()

def get_ingredient_properties(ingredient_name):
    """Get dietary flags for an exact match"""
    conn = connect_db()
    c = conn.cursor(cursor_factory=RealDictCursor)
    c.execute("""
        SELECT is_vegan, is_vegetarian, is_halal, is_gluten_free,
               is_lactose_free, is_nut_free, is_anti_inflammatory, 
               is_low_sugar
        FROM ingredients 
        WHERE name = %s
    """, (ingredient_name.lower(),))
    row = c.fetchone()
    conn.close()
    
    if row:
        return {
            "vegan": row["is_vegan"],
            "vegetarian": row["is_vegetarian"],
            "halal": row["is_halal"],
            "gluten-free": row["is_gluten_free"],
            "lactose-intolerant": row["is_lactose_free"],
            "nut-allergy": row["is_nut_free"],
            "anti-inflammatory": row["is_anti_inflammatory"],
            "low-sugar": row["is_low_sugar"]
        }
    return None

def find_similar_ingredients(ingredient_name, top_k=5, min_similarity=0.80):
    """
    Find similar ingredients using embedding similarity
    
    Returns: List of (ingredient_name, similarity_score, properties) tuples
    """
    conn = connect_db()
    c = conn.cursor(cursor_factory=RealDictCursor)
    
    # Generate embedding for query ingredient
    query_embedding = generate_embedding(ingredient_name)
    
    # Get all ingredients with embeddings
    c.execute("""
        SELECT name, embedding, is_vegan, is_vegetarian, is_halal, 
               is_gluten_free, is_lactose_free, is_nut_free, 
               is_anti_inflammatory, is_low_sugar
        FROM ingredients 
        WHERE embedding IS NOT NULL
    """)
    
    similarities = []
    for row in c.fetchall():
        stored_embedding = deserialize_embedding(row["embedding"])
        similarity = cosine_similarity(query_embedding, stored_embedding)
        
        if similarity >= min_similarity:
            properties = {
                "vegan": row["is_vegan"],
                "vegetarian": row["is_vegetarian"],
                "halal": row["is_halal"],
                "gluten-free": row["is_gluten_free"],
                "lactose-intolerant": row["is_lactose_free"],
                "nut-allergy": row["is_nut_free"],
                "anti-inflammatory": row["is_anti_inflammatory"],
                "low-sugar": row["is_low_sugar"]
            }
            similarities.append((row["name"], similarity, properties))
    
    conn.close()
    
    # Sort by similarity and return top_k
    similarities.sort(key=lambda x: x[1], reverse=True)
    return similarities[:top_k]

def get_or_infer_properties(ingredient_name, similarity_threshold=0.85):
    """
    Get ingredient properties with fallback to similarity search
    
    Returns: (properties_dict, source)
        - properties_dict: Dietary flags
        - source: "exact" | "similar:<ingredient>" | "unknown"
    """
    # Try exact match first
    properties = get_ingredient_properties(ingredient_name)
    if properties:
        print(properties)
        return properties, "exact"
    
    # Try similarity search
    similar = find_similar_ingredients(ingredient_name, top_k=1, 
                                      min_similarity=similarity_threshold)
    
    if similar:
        similar_name, similarity, similar_properties = similar[0]
        print(f"  → Inferred from '{similar_name}' (similarity: {similarity:.2f})")
        return similar_properties, f"similar:{similar_name}"
    
    # Unknown ingredient
    return None, "unknown"

def view_all_ingredients():
    """Display all ingredients and their dietary properties"""
    conn = connect_db()
    c = conn.cursor(cursor_factory=RealDictCursor)
    c.execute("""
        SELECT name, is_vegan, is_vegetarian, is_halal, is_gluten_free,
               is_lactose_free, is_nut_free, is_anti_inflammatory, 
               is_low_sugar
        FROM ingredients 
        ORDER BY name
    """)
    rows = c.fetchall()
    conn.close()
    
    if not rows:
        print("Database is empty - no ingredients found.")
        return []
    
    print(f"\n{'Ingredient':<25} {'Veg':<4} {'Vgn':<4} {'Hal':<4} {'GF':<4} " +
          f"{'LF':<4} {'NF':<4} {'AI':<4} {'LS':<4} {'Conf':<5}")
    print("-" * 85)
    
    ingredients_list = []
    for row in rows:
        # Convert 1/0 to Y/N, None to ?
        def flag(val):
            return 'Y' if val == 1 else ('N' if val == 0 else '?')
        
        print(f"{row['name']:<25} {flag(row['is_vegetarian']):<4} " +
              f"{flag(row['is_vegan']):<4} {flag(row['is_halal']):<4} " +
              f"{flag(row['is_gluten_free']):<4} {flag(row['is_lactose_free']):<4} " +
              f"{flag(row['is_nut_free']):<4} {flag(row['is_anti_inflammatory']):<4} " +
              f"{flag(row['is_low_sugar']):<4}")
        
        ingredients_list.append(dict(row))
    
    print(f"\nTotal ingredients: {len(rows)}\n")
    return ingredients_list

def clear_all_ingredients():
    """Delete all ingredients from the database"""
    conn = connect_db()
    c = conn.cursor()
    c.execute("DELETE FROM ingredients")
    conn.commit()
    rows_deleted = c.rowcount
    conn.close()
    print(f"Cleared {rows_deleted} ingredient(s) from the database.")
    return rows_deleted

def preload_database(json_path="data/preload.json"):
    """
    Load ingredients from JSON file
    Expected format:
    {
        "butter": {
            "vegan": 0, "vegetarian": 1, "halal": 1,
            "gluten-free": 1, "lactose-intolerant": 0, ...
        },
        ...
    }
    """
    with open(json_path, "r") as f:
        data = json.load(f)
    
    print(f"Preloading {len(data)} ingredients...")
    for ingredient_name, dietary_flags in data.items():
        add_ingredient(ingredient_name, dietary_flags)
    
    print(f"Preloaded {len(data)} ingredients with embeddings")

# Legacy function for backward compatibility
def get_tags(ingredient_name):
    """DEPRECATED: Use get_ingredient_properties() instead"""
    properties = get_ingredient_properties(ingredient_name)
    if properties:
        # Convert to old tag format if needed
        tags = []
        if properties.get("vegan") == 0:
            tags.append("not-vegan")
        if properties.get("lactose-intolerant") == 0:
            tags.append("contains-lactose")
        return tags
    return None

def main():
    clear_all_ingredients()