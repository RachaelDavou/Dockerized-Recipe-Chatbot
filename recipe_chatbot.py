import json
import requests
import streamlit as st
from openai import OpenAI

# Replace with your OpenAI API key
OPENAI_API_KEY = "your-openai-api-key-here"

# TheMealDB base URL 
MEALDB_BASE = "https://www.themealdb.com/api/json/v1/1"


# Function to search for a recipe by name
def search_recipe(name):
    url = f"{MEALDB_BASE}/search.php?s={name}" 
    response = requests.get(url)
    data = response.json()
    
    if not data["meals"]:
        return f"No recipes found for '{name}'."
    
    results = []
    for meal in data["meals"][:3]:
        results.append(f"- {meal['strMeal']} ({meal['strCategory']}, {meal['strArea']})")
    
    return f"Found these recipes:\n" + "\n".join(results)


# Function to search for recipes by ingredient
def search_by_ingredient(ingredient):
    url = f"{MEALDB_BASE}/filter.php?i={ingredient}"
    response = requests.get(url)
    data = response.json()
    
    if not data["meals"]:
        return f"No recipes found with '{ingredient}'."
    
    results = []
    for meal in data["meals"][:5]:
        results.append(f"- {meal['strMeal']}")
    
    return f"Recipes with {ingredient}:\n" + "\n".join(results)


# Function to get a random recipe suggestion
def get_random_recipe():
    url = f"{MEALDB_BASE}/random.php"
    response = requests.get(url)
    data = response.json()
    
    meal = data["meals"][0]
    
    ingredients = []
    for i in range(1, 6):
        ing = meal.get(f"strIngredient{i}")
        if ing and ing.strip():
            ingredients.append(ing)
    
    return (
        f"How about: {meal['strMeal']}\n"
        f"Category: {meal['strCategory']}\n"
        f"Cuisine: {meal['strArea']}\n"
        f"Key ingredients: {', '.join(ingredients)}"
    )


# Get list of categories
def get_categories():
    url = f"{MEALDB_BASE}/categories.php"
    response = requests.get(url)
    data = response.json()
    
    categories = [cat["strCategory"] for cat in data["categories"]]
    return "Available categories: " + ", ".join(categories)


# Get list of cuisines
def get_cuisines():
    url = f"{MEALDB_BASE}/list.php?a=list"
    response = requests.get(url)
    data = response.json()
    
    areas = [item["strArea"] for item in data["meals"]]
    return "Available cuisines: " + ", ".join(areas)


# Filter recipes by category
def filter_by_category(category):
    url = f"{MEALDB_BASE}/filter.php?c={category}"
    response = requests.get(url)
    data = response.json()
    
    if not data["meals"]:
        return f"No recipes found in category '{category}'."
    
    results = []
    for meal in data["meals"][:5]:
        results.append(f"- {meal['strMeal']}")
    
    return f"{category} recipes:\n" + "\n".join(results)


# Filter recipes by cuisine
def filter_by_cuisine(cuisine):
    url = f"{MEALDB_BASE}/filter.php?a={cuisine}"
    response = requests.get(url)
    data = response.json()
    
    if not data["meals"]:
        return f"No recipes found for '{cuisine}' cuisine."
    
    results = []
    for meal in data["meals"][:5]:
        results.append(f"- {meal['strMeal']}")
    
    return f"{cuisine} recipes:\n" + "\n".join(results)


# Tool Definitions for OpenAI
tools = [
    {
        "type": "function",
        "function": {
            "name": "search_recipe",
            "description": "Search for a recipe by name. Use when user asks for a specific dish.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Recipe name to search for"}
                },
                "required": ["name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_by_ingredient",
            "description": "Find recipes using a specific ingredient.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ingredient": {"type": "string", "description": "Ingredient to search for"}
                },
                "required": ["ingredient"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_random_recipe",
            "description": "Get a random recipe suggestion.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_categories",
            "description": "List all recipe categories.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_cuisines",
            "description": "List all available cuisines.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "filter_by_category",
            "description": "Get recipes from a category like Seafood, Dessert.",
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {"type": "string", "description": "Category name"}
                },
                "required": ["category"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "filter_by_cuisine",
            "description": "Get recipes from a specific cuisine like Italian, Japanese.",
            "parameters": {
                "type": "object",
                "properties": {
                    "cuisine": {"type": "string", "description": "Cuisine name"}
                },
                "required": ["cuisine"]
            }
        }
    }
]

# Map names to functions
available_functions = {
    "search_recipe": search_recipe,
    "search_by_ingredient": search_by_ingredient,
    "get_random_recipe": get_random_recipe,
    "get_categories": get_categories,
    "get_cuisines": get_cuisines,
    "filter_by_category": filter_by_category,
    "filter_by_cuisine": filter_by_cuisine
}


# Function to handle chat interactions 
def chat(user_message, client, messages):  
    messages.append({"role": "user", "content": user_message})
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )
    
    reply = response.choices[0].message
    
    if reply.tool_calls:
        messages.append(reply)
        
        for tool_call in reply.tool_calls:
            func_name = tool_call.function.name
            func_args = json.loads(tool_call.function.arguments)
            
            if func_name in available_functions:
                if func_args:
                    result = available_functions[func_name](**func_args)
                else:
                    result = available_functions[func_name]()
            else:
                result = "Function not found."
            
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result
            })
        
        final = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )
        
        answer = final.choices[0].message.content
        messages.append({"role": "assistant", "content": answer})
        return answer
    
    else:
        content = reply.content
        messages.append({"role": "assistant", "content": content})
        return content


# Streamlit UI
st.title("Recipe Chatbot")

st.write("Hello! I'm your Recipe Assistant")
st.write("\nI can help you with:")
st.write("  - Find specific recipes by name")
st.write("  - Suggest recipes using ingredients you have")
st.write("  - Show recipes from different cuisines")
st.write("  - Browse recipe categories")
st.write("  - Give you random recipe ideas!")

if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "system",
        "content": "You are a helpful recipe assistant. Use the available tools to help users find recipes."
    }]

if "history" not in st.session_state:
    st.session_state.history = []

client = OpenAI(api_key=OPENAI_API_KEY)

user_input = st.text_input("Enter your question:")

if user_input:
    try:
        response = chat(user_input, client, st.session_state.messages)
        
        st.session_state.history.append(f"You: {user_input}")
        st.session_state.history.append(f"Assistant: {response}")
        
        st.subheader("Answer")
        st.write(response)
    except Exception as e:
        st.error(f"Error: {e}")

with st.expander("Conversation History"):
    if st.session_state.history:
        for entry in st.session_state.history:
            st.write(entry)
    else:
        st.info("No conversation yet.")

if st.button("Clear History"):
    st.session_state.messages = [{
        "role": "system",
        "content": "You are a helpful recipe assistant. Use the available tools to help users find recipes."
    }]
    st.session_state.history = []
    st.rerun()
