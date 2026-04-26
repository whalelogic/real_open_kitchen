# Quick Start Guide: AI Recipe Generator

## Setup (One-time)

### 1. Get Your Gemini API Key
1. Visit https://makersuite.google.com/app/apikey
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the key

### 2. Set Environment Variable

**Option A: Export in terminal (temporary)**
```bash
export GEMINI_API_KEY=your_actual_api_key_here
```

**Option B: Create .env file (permanent)**
```bash
echo "GEMINI_API_KEY=your_actual_api_key_here" > .env
```

**Option C: Add to run.sh**
Edit `run.sh` and add before `flask run`:
```bash
export GEMINI_API_KEY=your_actual_api_key_here
```

### 3. Start the Application
```bash
./run.sh
```

## Using the AI Recipe Generator

### Step 1: Navigate to Create Recipe
- Login to your account
- Click "My Kitchen" in the navigation
- Click "Create New Recipe"

### Step 2: Open AI Assistant
- Look for the purple "AI Assistant" button on the right side of the screen
- Click it to open the AI sidebar

### Step 3: Describe Your Recipe
Type what you want to cook in natural language. Be descriptive!

**Good Examples:**
```
"A creamy tomato pasta with fresh basil and garlic, serves 4"
"Quick chocolate chip cookies that are crispy on the outside and chewy inside"
"Spicy Thai chicken curry with coconut milk and vegetables"
"A hearty vegetarian chili with black beans and bell peppers"
"Simple grilled salmon with lemon butter sauce"
```

**Tips for Best Results:**
- Mention serving size if important
- Include key ingredients or flavors
- Specify cooking style (quick, healthy, traditional, etc.)
- Note dietary preferences (vegetarian, gluten-free, etc.)

### Step 4: Generate Recipe
- Click "Generate Recipe" button
- Wait 5-10 seconds (you'll see a loading spinner)
- Review the AI-generated recipe:
  - Title
  - Description  
  - Servings, prep time, cook time
  - Complete ingredient list with quantities
  - Step-by-step instructions

### Step 5: Use the Recipe
- Click "Use This Recipe" button
- The form will auto-fill with recipe details
- Review and adjust as needed
- Click "SAVE AND ADD INGREDIENTS"

### Step 6: Add AI Ingredients
- You'll see a purple banner: "AI Generated Ingredients Ready!"
- Click "Add AI Ingredients"
- All ingredients will be added automatically
- Review the list and delete/edit any if needed
- Click "NEXT: ADD INSTRUCTIONS"

### Step 7: Add AI Instructions
- You'll see a purple banner: "AI Generated Instructions Ready!"
- Click "Add AI Instructions"
- All steps will be added automatically
- Review and reorder/edit as needed
- Click "DONE"

### Step 8: Enjoy!
Your recipe is now complete and saved!

## Troubleshooting

### "GEMINI_API_KEY environment variable not set"
- Make sure you exported the API key
- Restart the Flask server after setting the variable
- Check the key is correct (no spaces or quotes)

### "Failed to generate recipe"
- Check your internet connection
- Verify API key is valid
- Try a simpler prompt
- Check API quota hasn't been exceeded

### AI generates incomplete recipes
- Be more specific in your prompt
- Include serving size and time expectations
- Try rephrasing your request

### Ingredients not matching database units
- The system tries to auto-match common units
- If it defaults to "pieces", manually edit the ingredient
- Common units work best: cups, tablespoons, grams, etc.

## Example Workflow

```
1. Click "AI Assistant" → Opens purple sidebar
2. Type: "Creamy mushroom risotto for 4 people"
3. Click "Generate Recipe" → Wait 5-10 seconds
4. Review generated recipe → Looks good!
5. Click "Use This Recipe" → Form auto-fills
6. Adjust template type to "Standard"
7. Click "SAVE AND ADD INGREDIENTS"
8. Click "Add AI Ingredients" → 8 ingredients added
9. Click "NEXT: ADD INSTRUCTIONS"
10. Click "Add AI Instructions" → 6 steps added
11. Click "DONE" → Recipe complete! 🎉
```

## Pro Tips

1. **Iterate**: If the first result isn't perfect, try rephrasing
2. **Be Specific**: More details = better results
3. **Edit After**: Use AI as a starting point, then customize
4. **Save Favorites**: Note which prompt styles work best for you
5. **Combine Methods**: Use AI for structure, add your personal touches

## Privacy Note

- Your prompts are sent to Google's Gemini API
- Recipe data is stored in your local database
- No personal data is shared beyond the prompt text
- Review Google's privacy policy for Gemini API usage
