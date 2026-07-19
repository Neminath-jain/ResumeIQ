# AI Chatbot — Setup Instructions

## 1. Get a free Groq API key
Sign up at https://console.groq.com/keys — it's free, no credit card, and gives
you a generous daily rate limit on fast open models (Llama 3.3 70B here).

## 2. Add the key to your environment

    GROQ_API_KEY = "gsk_your_key_here"


## 3. Drop in the view
Copy `chatbot.py` into whichever Django app holds your other views
(the same app as `index`, `history`, `result`). If you'd rather not add a new
file, just paste the `chat_api` function (and its imports/constants) into your
existing `views.py`.

## 4. Wire up the URL
In your app's `urls.py`:

    from . import chatbot   # or: from .views import chat_api

    urlpatterns = [
        # ...your existing urls...
        path('api/chat/', chatbot.chat_api, name='chat_api'),
    ]

The widget's JS posts to `/api/chat/` exactly — if your project uses a URL
prefix (e.g. everything under `/app/`), update the fetch URL in base.html's
widget script to match.

## 5. Templates — already done
- `base.html` — floating chat widget (button + panel + JS) added right before
  `</body>`. It appears on every page that extends base.html.
- `result.html` — added `json_script` blocks + a small script that exposes
  `window.RESUME_CONTEXT` (ats score, detected role, skill gaps, etc.) so the
  assistant gives personalized answers when a person is viewing their report.
  On every other page `window.RESUME_CONTEXT` is simply undefined, and the
  assistant falls back to general Q&A.

## 6. requirements.txt
Only dependency is `requests`, which almost every Django project already has.
If not:

    pip install requests

## Notes
- Groq's free tier is rate-limited per day/minute — fine for personal/small
  projects. If you outgrow it, swapping to OpenAI or Anthropic later just
  means changing the URL/headers/model in `chat_api` — the frontend widget
  doesn't need to change at all.
- The widget keeps conversation history in memory (JS variable) only — it
  resets on page reload. If you want persistent chat history per user, you'd
  add a Django model and save/load messages keyed by `request.user`.
