from fastapi import APIRouter, HTTPException, Header
from typing import Optional
from models.schemas import ChatRequest, ChatResponse
from utils.groq_client import get_groq_response
from utils.wp_data import get_user_context
from utils.web_search import get_web_context  # DDG + GCS fallback

router = APIRouter()

@router.get("/admin/quota")
async def quota_tracker():
    from utils.web_search import get_ddg_count, get_gcs_count
    return {
        "ddg_used": get_ddg_count(),
        "gcs_used": get_gcs_count()
    }

# ✅ Health check route to prevent 405 errors
@router.get("/chat")
async def chat_health_check():
    return {"status": "Chat endpoint is live"}

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(
    payload: ChatRequest,
    x_user_id: Optional[int] = Header(None, alias="X-User-ID")
):
    """
    Chat endpoint that:
    - Accepts either 'message' or 'question' in the body.
    - Optionally takes X-User-ID header for personalised BuddyPress answers.
    - Uses DuckDuckGo first for web answers, falls back to Google Custom Search if needed.
    - Passes URLs into AI prompt so it can include clickable links.
    """
    try:
        # 1️⃣ Normalise input
        user_message = payload.message or payload.question
        if not user_message:
            raise HTTPException(
                status_code=422,
                detail="Either 'message' or 'question' must be provided."
            )

        # 2️⃣ Get BuddyPress context if user ID provided
        user_context = {}
        if x_user_id:
            try:
                user_context = get_user_context(x_user_id)
            except Exception as db_err:
                print("DB error in get_user_context:", db_err)
                user_context = {}

        # 3️⃣ Decide if we need web search
        needs_web = any(keyword in user_message.lower() for keyword in [
            "today", "latest", "current", "price", "score", "news", "update", "who won", "when is"
        ])

        web_context = ""
        if needs_web:
            web_context = await get_web_context(user_message)

        # 4️⃣ Build system prompt
        system_prompt = f"""
        You are a helpful assistant for a BuddyPress social site.
        The current user is {user_context.get('name', 'Unknown')}.
        They have {user_context.get('unread_messages', 0)} unread messages.
        They are in groups: {', '.join(user_context.get('groups', [])) or 'None'}.
        Use this information to answer questions about the user.
        If the question is unrelated to this data, answer normally.
        If web search results are provided, use them for up-to-date info.
        If you mention a source, include its clickable link in the answer.

        Web search results:
        {web_context}
        """

        # 5️⃣ Get AI reply
        ai_reply = await get_groq_response(user_message, system_prompt)

        return ChatResponse(reply=ai_reply, success=True)

    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print("ERROR in /chat:", e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
