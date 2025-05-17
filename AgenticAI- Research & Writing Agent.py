import os
from dotenv import load_dotenv
import google.generativeai as gemini
import wikipedia
import requests

import streamlit as st # Importing streamlit for web UI.
st.set_page_config(page_title="Dhruv's Research & Writing AI Tool", page_icon="👾") # Assigned the name and the favicon to the webpage.
st.title = ("Welcome to Dhruv's Research & Writing AI.") # Assigned the title to the webpage.

load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")

# Task# 3: Designing streamlit UI:

topic = st.text_input("What would you like to research?")
user_language = st.selectbox("What's your preferred language?", ["Hindi", "Bengali", "Tamil", "Marathi"]) # User selects their preferred language. 
research_depth = st.radio("How deep do you want to dive into this research? ", ["Basic", "Detailed"])
writing_style = st.radio("How you like your writing style? ", ["Informative", "Opinionated"])
search_engine = st.selectbox("Select the search engine you would like to fetch your data from: ",
                             ["Wikipedia", "Serper", "DuckDuckGo"])

# Task# 4: Mapping languages:

language_instructions = { # Created a dictionary of languages.
    "Hindi": "Write in Hindi.",
    "Bengali": "Write in Bengali.",
    "Tamil": "Write in Tamil.",
    "Marathi": "Write in Marathi."
}

# Task #5: Fetching data from search engines:

def fetch_from_wikipedia(topic):
    try:
        summary = wikipedia.summary(topic, sentences=20)
        return summary, wikipedia.page(topic).url
    except wikipedia.exceptions.DisambiguationError as e:
        return str(e), ""
def fetch_from_duckduckgo(query):
    response = requests.get(f"https://api.duckduckgo.com/?q={query}&format=json")
    data = response.json()
    return data['AbstractText'], data['AbstractURL']

# Task# 6: Devloping Planning Agent.
def generate_subtopics(topic, language_instruction):
    prompt = f"{language_instruction} Break down the topic '{topic}' into 3–5 subtopics."
    response = gemini.generate_text(prompt)
    return response.text.split('\n')

# Task# 7: Creating the wrinting agent:
def write_article(subtopics, research_sources, language_instruction, writing_style):
    article = f"Writing an article in {language_instruction} with {writing_style} style.\n"
    for subtopic in subtopics:
        article += f"\n{subtopic}:\n{research_sources[subtopic]}\n"
    return article

# Task# 8: Add Reflection Agent:

def review_article(article):
    if len(article.split()) < 200:
        return "Article too short. Rewriting."
    return article


# Task# 9: Create Summary Agent:

def summarize_article(article, language_instruction):
    prompt = f"{language_instruction} Summarize this article: {article}"
    response = gemini.generate_text(prompt)
    return response.text

# Task 10: Final Integration and Display:

if st.button("Run Agentic AI"):
    subtopics = generate_subtopics(topic, language_instructions[user_language])
    research_sources = {}
    for subtopic in subtopics:
        if search_engine == "Wikipedia":
            research_sources[subtopic] = fetch_from_wikipedia(subtopic)
        elif search_engine == "Serper":
            research_sources[subtopic] = fetch_from_serper(subtopic)
        else:
            research_sources[subtopic] = fetch_from_duckduckgo(subtopic)
    
    article = write_article(subtopics, research_sources, language_instructions[user_language], writing_style)
    article = review_article(article)
    summary = summarize_article(article, language_instructions[user_language])

    st.subheader("Final Article")
    st.write(article)
    st.subheader("Summary")
    st.write(summary)

# Task# 11: Creating a download button:

def save_article(article):
    with open("article.md", "w") as file:
        file.write(article)

if st.button("Download Article"):
    save_article(article)
    st.download_button("Download", "article.md")