# Recipe Chatbot - Dockerized AI Service

A Streamlit chatbot that helps users find recipes. It fetches real-time data from TheMealDB API and uses OpenAI function calling to select the right tool based on user queries. Containerized with Docker for easy deployment.


## Requirements



You will also need an OpenAI API key. Get one at https://platform.openai.com/api-keys

For Docker deployment, install Docker: https://www.docker.com/products/docker-desktop/


## How to Run

1. Open `recipe_chatbot.py` and replace the placeholder with your OpenAI API key:

```python
OPENAI_API_KEY = "your-openai-api-key-here"
```

2. Run with Docker:


```
docker-compose up --build
```



3. Open browser: http://localhost:8501


## Tools

| Tool | Description |
|------|-------------|
| `search_recipe` | Search for a recipe by name |
| `search_by_ingredient` | Find recipes using a specific ingredient |
| `get_random_recipe` | Get a random recipe suggestion |
| `get_categories` | List all recipe categories (Beef, Dessert, etc.) |
| `get_cuisines` | List all available cuisines (Italian, Japanese, etc.) |
| `filter_by_category` | Get recipes from a specific category |
| `filter_by_cuisine` | Get recipes from a specific cuisine |


## Sample Queries

The chatbot can handle natural language requests like:

1. "Find me a chicken recipe"
2. "What can I make with salmon?"
3. "Surprise me with a random recipe"
4. "Show me Italian recipes"
5. "What categories are available?"
6. "Give me some dessert ideas"


## How It Works

The chatbot uses OpenAI's function calling feature to select and execute the appropriate tool.

1. **User Input** - The user asks a question in natural language.
2. **Tool Selection** - The LLM reads the tool descriptions and selects the most relevant one.
3. **API Call** - The selected function makes an HTTP request to TheMealDB API.
4. **Response Parsing** - The JSON response is parsed and formatted.
5. **Final Answer** - The LLM generates a natural language response for the user.


## API Used

TheMealDB is free and requires no API key.

Full docs: https://www.themealdb.com/api.php
