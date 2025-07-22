 # main.py

from agents import Agent, Runner, OpenAIChatCompletionsModel, set_tracing_disabled, function_tool
from dotenv import load_dotenv
import os
from openai import AsyncOpenAI
from whatsapp import send_whatsapp_message
import chainlit as cl

load_dotenv()
set_tracing_disabled(True)

API_KEY = os.getenv("GEMINI_API_KEY")

external_client = AsyncOpenAI(
    api_key=API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/"
)

model = OpenAIChatCompletionsModel(
    model="gemini-1.5-flash",  # Or 2.5-flash if you're using that endpoint
    openai_client=external_client
)

# 🔧 TOOL: Girls Data
@function_tool
def get_girls_data(min_age: int) -> list[dict]:
    """
    Retrieve fake rishta data for girls based on a minimum age.
    """
    girls = [
        {"name": "Ayesha", "age": 18, "education": "BSCS", "city": "karachi"},
        {"name": "Fatima", "age": 24, "education": "MBBS", "city": "Karachi"},
        {"name": "Zainab", "age": 23, "education": "BBA", "city": "Islamabad"},
        {"name": "Hania", "age": 20, "education": "BS English", "city": "Multan"},
        {"name": "Mariam", "age": 21, "education": "B.Ed", "city": "Rawalpindi"},
        {"name": "Iqra", "age": 22, "education": "MSc Math", "city": "Faisalabad"},
        {"name": "Areeba", "age": 25, "education": "BS Physics", "city": "Sialkot"},
        {"name": "Sana", "age": 23, "education": "BS Psychology", "city": "Quetta"},
        {"name": "Mehwish", "age": 26, "education": "M.Com", "city": "Hyderabad"},
        {"name": "Bushra", "age": 22, "education": "BSc", "city": "Bahawalpur"},
        {"name": "Noor", "age": 24, "education": "BS Zoology", "city": "Peshawar"},
        {"name": "Eman", "age": 21, "education": "BS IT", "city": "Sargodha"},
        {"name": "Laiba", "age": 20, "education": "FSc", "city": "Mardan"},
        {"name": "Komal", "age": 25, "education": "LLB", "city": "Sukkur"},
        {"name": "Hafsa", "age": 23, "education": "BDS", "city": "Abbottabad"},
    ]

    return [girl for girl in girls if girl["age"] >= min_age]

# 👵 Rishta Wali Agent
rishty_agent = Agent(
    name="Rishtay Wali Aunty",
    instructions="""
    You are Rishtay Wali Aunty. Help users find suitable girls' rishtas based on age.
    Use the provided tool to fetch rishta details.
    If the user provides a WhatsApp number, send the matches using WhatsApp.
    """,
    model=model,
    tools=[get_girls_data, send_whatsapp_message]
)

# 💬 Start Chat
@cl.on_chat_start
async def start():
    cl.user_session.set("history", [])
    await cl.Message("🌸 Salam beta! Main Rishtay Wali Auntie hoon. Agar apko achi larki ka rishta chahiye tou apni **age** aur **WhatsApp number** batayein.").send()

# 📥 Handle Messages
@cl.on_message
async def main(message: cl.Message):
    await cl.Message("Soch rahi hoon beta... 🤔").send()

    history = cl.user_session.get("history") or []
    history.append({"role": "user", "content": message.content})

    result = Runner.run_sync(
        starting_agent=rishty_agent,
        input=history
    )

    history.append({"role": "assistant", "content": result.final_output})
    cl.user_session.set("history", history)

    await cl.Message(content=result.final_output).send()
