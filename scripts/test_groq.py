from groq import Groq
from config.settings import settings


print("API KEY LOADED:", bool(settings.GROQ_API_KEY))
print("MODEL:", settings.GROQ_MODEL)

client = Groq(
    api_key=settings.GROQ_API_KEY
)

response = client.chat.completions.create(
    model=settings.GROQ_MODEL,
    messages=[
        {
            "role": "user",
            "content": "Say hello in one sentence."
        }
    ],
)

print(response.choices[0].message.content)