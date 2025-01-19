from langchain_google_genai import GoogleGenerativeAI
from config import env

ai = GoogleGenerativeAI(
    model="gemini-1.5-flash",
    api_key=env["GOOGLE_API_KEY"],
)


async def respond(prompt: str) -> str:
    try:
        print(f"User: {prompt}")
        response = await ai.agenerate([prompt])
        generated_text = response.generations[0][0].text
        print(f"Bot: {generated_text}")
        return generated_text
    except Exception as e:
        return f"An error occurred: {e}"
