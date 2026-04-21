FROM python:3.11-slim

WORKDIR /app

RUN pip install openai requests streamlit

COPY recipe_chatbot.py .

EXPOSE 8501

CMD ["streamlit", "run", "recipe_chatbot.py", "--server.address=0.0.0.0"]
