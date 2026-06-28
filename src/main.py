import os
import json
import logging
from fastapi import FastAPI, Request, HTTPException
import openai
import requests

app = FastAPI(title="AI Lead Qualification System")
logging.basicConfig(level=logging.INFO)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your-openai-key")
HUBSPOT_API_KEY = os.getenv("HUBSPOT_API_KEY", "your-hubspot-key")
MAKE_WEBHOOK_URL = os.getenv("MAKE_WEBHOOK_URL", "https://hook.make.com/your-webhook")

openai.api_key = OPENAI_API_KEY

async def analyze_lead_intent(message: str) -> dict:
    """
    Calls OpenAI GPT-4o to analyze the lead's intent and score them.
    """
    prompt = f"""
    Analyze the following lead inquiry for a B2B SaaS product.
    
    Lead Message: "{message}"
    
    Extract the following information and return ONLY valid JSON:
    - "intent": (e.g., "Ready to Buy", "Exploring", "Support Issue", "Spam")
    - "budget_mentioned": true/false
    - "score": (1-10, where 10 is immediate high-value buyer)
    - "summary": A one-sentence summary for the sales rep.
    - "routing": ("Senior Sales", "SDR", "Support", "Ignore")
    """
    try:
        response = await openai.ChatCompletion.acreate(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an expert sales qualifier."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        logging.error(f"OpenAI API Error: {e}")
        return {"error": str(e), "score": 0, "routing": "SDR"}

def push_to_hubspot(email: str, name: str, analysis: dict):
    """
    Pushes the qualified lead into HubSpot CRM.
    """
    url = "https://api.hubapi.com/crm/v3/objects/contacts"
    headers = {
        "Authorization": f"Bearer {HUBSPOT_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "properties": {
            "email": email,
            "firstname": name,
            "lead_score": analysis.get("score"),
            "lead_intent": analysis.get("intent"),
            "hs_lead_status": "NEW" if analysis.get("score", 0) > 5 else "UNQUALIFIED"
        }
    }
    response = requests.post(url, headers=headers, json=data)
    return response.status_code == 201

def trigger_make_automation(email: str, analysis: dict):
    """
    Triggers Make.com for email/SMS follow-up sequences.
    """
    payload = {"email": email, "analysis": analysis}
    requests.post(MAKE_WEBHOOK_URL, json=payload)

@app.post("/webhook/new-lead")
async def receive_lead(request: Request):
    """
    Endpoint for incoming leads from Typeform, Facebook Lead Ads, or Custom Forms.
    """
    try:
        payload = await request.json()
        email = payload.get("email")
        name = payload.get("name")
        message = payload.get("message", "")

        if not email or not message:
            raise HTTPException(status_code=400, detail="Email and message required.")

        logging.info(f"Processing lead: {email}")

        analysis = await analyze_lead_intent(message)
        logging.info(f"Analysis result: {analysis}")

        crm_success = push_to_hubspot(email, name, analysis)
        if not crm_success:
            logging.warning("Failed to push to HubSpot.")

        if analysis.get("score", 0) >= 7:
            trigger_make_automation(email, analysis)

        return {"status": "success", "analysis": analysis}

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Webhook error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

# To run:
# uvicorn lead_qualification:app --reload
