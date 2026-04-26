"""AI service for recipe generation using Google Gemini."""
import os
import json
from google import genai
from flask import current_app

def configure_gemini():
    """Configure Gemini API with the API key."""
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set")
    
    client = genai.Client(api_key=api_key)
    return client

def generate_recipe_from_prompt(prompt):
    """
    Generate a recipe from a user prompt using Gemini.
    
    Returns a dictionary with:
    - title: str
    - description: str
    - base_servings: int
    - prep_time_minutes: int
    - cook_time_minutes: int
    - ingredients: list of dicts with {name, quantity, unit, allergen}
    - instructions: list of strings
    """
    try:
        client = configure_gemini()
        
        system_prompt = """You are a professional recipe assistant. Generate a detailed recipe based on the user's request.

Return ONLY a valid JSON object with this exact structure:
{
  "title": "Recipe Title",
  "description": "Brief description of the dish",
  "base_servings": 4,
  "prep_time_minutes": 15,
  "cook_time_minutes": 30,
  "ingredients": [
    {
      "name": "ingredient name",
      "quantity": 2.0,
      "unit": "cups",
      "allergen": "dairy"
    }
  ],
  "instructions": [
    "Step 1 instruction",
    "Step 2 instruction"
  ]
}

For units, use common cooking measurements: cups, tablespoons, teaspoons, ounces, pounds, grams, milliliters, liters, pieces, cloves, pinch, dash, etc.

For allergens, only include one of these if applicable: dairy, eggs, fish, shellfish, tree_nuts, peanuts, wheat, soy, gluten. If no allergen, omit the field or set to null.

Make the recipe practical, accurate, and detailed. Include all necessary ingredients and clear step-by-step instructions."""

        full_prompt = f"{system_prompt}\n\nUser request: {prompt}"
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=full_prompt
        )
        
        # Extract JSON from response
        response_text = response.text.strip()
        
        # Remove markdown code blocks if present
        if response_text.startswith('```json'):
            response_text = response_text[7:]
        if response_text.startswith('```'):
            response_text = response_text[3:]
        if response_text.endswith('```'):
            response_text = response_text[:-3]
        
        response_text = response_text.strip()
        
        recipe_data = json.loads(response_text)
        
        # Validate required fields
        required_fields = ['title', 'description', 'ingredients', 'instructions']
        for field in required_fields:
            if field not in recipe_data:
                raise ValueError(f"Missing required field: {field}")
        
        # Set defaults for optional fields
        recipe_data.setdefault('base_servings', 4)
        recipe_data.setdefault('prep_time_minutes', 15)
        recipe_data.setdefault('cook_time_minutes', 30)
        
        return recipe_data
        
    except json.JSONDecodeError as e:
        current_app.logger.error(f"Failed to parse JSON from Gemini response: {e}")
        return {"error": "Failed to parse recipe from AI response. Please try again."}
    except Exception as e:
        current_app.logger.error(f"Error generating recipe: {e}")
        return {"error": str(e)}
