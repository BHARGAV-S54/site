import os
import httpx

async def get_groq_response(user_message: str, system_prompt: str = "") -> str:
    """
    Sends a chat completion request to Groq API with optional system prompt.
    Returns the AI-generated reply or raises an HTTPException with details.
    """
    api_key = os.getenv("GROQ_API_KEY")
    model = os.getenv("MODEL", "llama3-70b-8192")

    if not api_key:
        raise ValueError("GROQ_API_KEY is missing from environment variables.")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": model,
        "messages": []
    }

    if system_prompt:
        payload["messages"].append({
            "role": "system",
            "content": system_prompt.strip()
        })

    payload["messages"].append({
        "role": "user",
        "content": user_message.strip()
    })

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            resp.raise_for_status()
            data = resp.json()

            # Defensive parsing
            choices = data.get("choices")
            if not choices or "message" not in choices[0]:
                raise ValueError("Invalid response format from Groq API.")

            return choices[0]["message"]["content"].strip()

    except httpx.HTTPStatusError as http_err:
        print(f"Groq API returned {http_err.response.status_code}: {http_err.response.text}")
        raise

    except Exception as e:
        import traceback
        print("Error in get_groq_response:", e)
        traceback.print_exc()
        raise
