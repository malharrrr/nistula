import os
import uuid
import json
from datetime import datetime
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import anthropic

load_dotenv()

app = FastAPI(title="Nistula Webhook Service")

api_key = os.getenv("ANTHROPIC_API_KEY")
client = anthropic.Anthropic(api_key=api_key) if api_key else None

class InboundMessage(BaseModel):
    source: str
    guest_name: str
    message: str
    timestamp: str
    booking_ref: str
    property_id: str

PROPERTY_CONTEXT = """
Property: Villa B1, Assagao, North Goa
Bedrooms: 3 | Max guests: 6 | Private pool: Yes
Check-in: 2pm | Check-out: 11am
Base rate: INR 18,000 per night (up to 4 guests)
Extra guest: INR 2,000 per night per person
WiFi password: Nistula@2024
Caretaker: Available 8am to 10pm
Chef on call: Yes, pre-booking required
Availability April 20-24: Available
Cancellation: Free up to 7 days before check-in
"""

SYSTEM_PROMPT = """
You are an AI assistant for Nistula, managing luxury villas.
Analyze the guest message and return a pure JSON object (no markdown formatting) with exactly three keys:
1. "query_type": Must be one of: [pre_sales_availability, pre_sales_pricing, post_sales_checkin, special_request, complaint, general_enquiry]
2. "drafted_reply": A polite, helpful response using ONLY the provided context. If context is missing, apologize and say you will check.
3. "confidence_score": A float between 0.0 and 1.0 representing how completely the property context answers the query.

Context:
{context}
"""

@app.post("/webhook/message")
async def handle_guest_message(payload: InboundMessage):
    try:
        message_id = str(uuid.uuid4())
        unified_message = {
            "message_id": message_id,
            "source": payload.source,
            "guest_name": payload.guest_name,
            "message_text": payload.message,
            "timestamp": payload.timestamp,
            "booking_ref": payload.booking_ref,
            "property_id": payload.property_id
        }

        if not client:
             raise HTTPException(status_code=500, detail="Anthropic API key not configured.")

        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=500,
            system=SYSTEM_PROMPT.format(context=PROPERTY_CONTEXT),
            messages=[
                {"role": "user", "content": f"Guest Name: {payload.guest_name}\nMessage: {payload.message}"}
            ]
        )

        try:
            ai_output = json.loads(response.content[0].text)
            query_type = ai_output.get("query_type", "general_enquiry")
            drafted_reply = ai_output.get("drafted_reply", "")
            raw_confidence = float(ai_output.get("confidence_score", 0.5))
        except (json.JSONDecodeError, ValueError):
            query_type = "general_enquiry"
            drafted_reply = "I've received your message and an agent will be with you shortly."
            raw_confidence = 0.0

        final_confidence = raw_confidence
        if query_type == "complaint":
            final_confidence = min(final_confidence, 0.5)

        if query_type == "complaint" or final_confidence < 0.60:
            action = "escalate"
        elif final_confidence > 0.85:
            action = "auto_send"
        else:
            action = "agent_review"

        return {
            "message_id": message_id,
            "query_type": query_type,
            "drafted_reply": drafted_reply,
            "confidence_score": final_confidence,
            "action": action
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))