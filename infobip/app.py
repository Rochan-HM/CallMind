import logging
import os
from typing import Any, Dict, Optional

import requests
from dotenv import load_dotenv
from fastapi import BackgroundTasks, FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Infobip Voice Call Transcription Service")

# Configuration
INFOBIP_API_KEY = os.getenv("INFOBIP_API_KEY")
INFOBIP_BASE_URL = os.getenv("INFOBIP_BASE_URL")

if not INFOBIP_API_KEY or not INFOBIP_BASE_URL:
    raise ValueError(
        "INFOBIP_API_KEY and INFOBIP_BASE_URL must be set in environment variables"
    )

# Base URL for API calls
API_BASE = f"https://{INFOBIP_BASE_URL}"

# Headers for Infobip API requests
API_HEADERS = {
    "Authorization": f"App {INFOBIP_API_KEY}",
    "Content-Type": "application/json",
    "Accept": "application/json",
}


class CallEventData(BaseModel):
    """Model for incoming call event data"""

    pass


class TranscriptionData(BaseModel):
    """Model for transcription event data"""

    pass


def make_infobip_api_call(
    endpoint: str, method: str = "POST", data: Optional[Dict] = None
) -> Optional[Dict]:
    """
    Make an API call to Infobip

    Args:
        endpoint: API endpoint path
        method: HTTP method
        data: Request payload

    Returns:
        Response data or None if failed
    """
    url = f"{API_BASE}{endpoint}"

    try:
        if method.upper() == "POST":
            response = requests.post(url, headers=API_HEADERS, json=data)
        elif method.upper() == "GET":
            response = requests.get(url, headers=API_HEADERS)
        else:
            logger.error(f"Unsupported HTTP method: {method}")
            return None

        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as e:
        logger.error(f"API call failed: {e}")
        if hasattr(e, "response") and e.response is not None:
            logger.error(f"Response status: {e.response.status_code}")
            logger.error(f"Response body: {e.response.text}")
        return None


def accept_call(call_id: str) -> bool:
    """
    Accept an incoming call

    Args:
        call_id: The ID of the call to accept

    Returns:
        True if successful, False otherwise
    """
    endpoint = f"/calls/1/calls/{call_id}/accept"

    # Basic accept call payload
    payload = {}

    logger.info(f"Accepting call {call_id}")
    result = make_infobip_api_call(endpoint, "POST", payload)

    if result:
        logger.info(f"Successfully accepted call {call_id}")
        return True
    else:
        logger.error(f"Failed to accept call {call_id}")
        return False


def start_transcription(call_id: str) -> bool:
    """
    Start transcription for a call

    Args:
        call_id: The ID of the call to start transcription for

    Returns:
        True if successful, False otherwise
    """
    endpoint = f"/calls/1/calls/{call_id}/start-transcription"

    # Transcription configuration payload
    payload = {
        "transcription": {
            "language": "en-US",
            "sendInterimResults": True,
            "advancedFormatting": True,
            "customDictionary": [],
        }
    }

    logger.info(f"Starting transcription for call {call_id}")
    result = make_infobip_api_call(endpoint, "POST", payload)

    if result:
        logger.info(f"Successfully started transcription for call {call_id}")
        return True
    else:
        logger.error(f"Failed to start transcription for call {call_id}")
        return False


async def handle_call_received(call_data: Dict[str, Any]):
    """
    Handle incoming call - accept it and start transcription

    Args:
        call_data: Call event data from Infobip
    """
    call_id = call_data.get("callId")

    if not call_id:
        logger.error("No callId found in call data")
        return

    logger.info(f"Processing incoming call {call_id}")

    # Accept the call
    if accept_call(call_id):
        logger.info(f"Call {call_id} accepted, waiting for establishment...")
    else:
        logger.error(f"Failed to accept call {call_id}")


async def handle_call_established(call_data: Dict[str, Any]):
    """
    Handle call established - start transcription

    Args:
        call_data: Call event data from Infobip
    """
    call_id = call_data.get("callId")

    if not call_id:
        logger.error("No callId found in call data")
        return

    logger.info(f"Call {call_id} established, starting transcription...")

    # Start transcription
    if start_transcription(call_id):
        logger.info(f"Transcription started for call {call_id}")
    else:
        logger.error(f"Failed to start transcription for call {call_id}")


@app.post("/webhooks/call-received")
async def call_received_webhook(request: Request, background_tasks: BackgroundTasks):
    """
    Webhook endpoint for CALL_RECEIVED events

    This endpoint handles incoming calls from Infobip
    """
    try:
        # Parse incoming webhook data
        webhook_data = await request.json()
        logger.info(f"Received call webhook: {webhook_data}")

        # Extract event type and call data
        event_type = webhook_data.get("type")
        call_data = webhook_data

        if event_type == "CALL_RECEIVED":
            # Process the incoming call in the background
            background_tasks.add_task(handle_call_received, call_data)
        elif event_type == "CALL_ESTABLISHED":
            # Process the established call in the background
            background_tasks.add_task(handle_call_established, call_data)
        else:
            logger.info(f"Received event type: {event_type}")

        return JSONResponse(content={"status": "accepted"}, status_code=200)

    except Exception as e:
        logger.error(f"Error processing call webhook: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/webhooks/events")
async def events_webhook(request: Request):
    """
    Webhook endpoint for call events including transcription results

    This endpoint handles all call-related events from Infobip
    """
    try:
        # Parse incoming webhook data
        webhook_data = await request.json()
        event_type = webhook_data.get("type")

        logger.info(f"Received event: {event_type}")

        if event_type == "TRANSCRIPTION":
            # Handle transcription results
            await handle_transcription_event(webhook_data)
        elif event_type == "CALL_ESTABLISHED":
            # Handle call established
            await handle_call_established(webhook_data)
        elif event_type == "CALL_FINISHED":
            call_id = webhook_data.get("callId")
            logger.info(f"Call {call_id} finished")
        elif event_type == "CALL_FAILED":
            call_id = webhook_data.get("callId")
            error_code = webhook_data.get("errorCode")
            logger.error(f"Call {call_id} failed with error: {error_code}")
        else:
            logger.info(f"Unhandled event type: {event_type}")
            logger.debug(f"Event data: {webhook_data}")

        return JSONResponse(content={"status": "accepted"}, status_code=200)

    except Exception as e:
        logger.error(f"Error processing event webhook: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


async def handle_transcription_event(transcription_data: Dict[str, Any]):
    """
    Handle transcription events and print the results

    Args:
        transcription_data: Transcription event data from Infobip
    """
    call_id = transcription_data.get("callId")

    # Extract transcription results
    transcription = transcription_data.get("transcription", {})
    text = transcription.get("text", "")
    is_final = transcription.get("isFinal", False)
    confidence = transcription.get("confidence", 0)

    # Print transcription results
    transcript_type = "FINAL" if is_final else "INTERIM"

    print(f"\n{'='*60}")
    print(f"TRANSCRIPTION [{transcript_type}] - Call ID: {call_id}")
    print(f"Confidence: {confidence:.2f}")
    print(f"Text: {text}")
    print(f"{'='*60}\n")

    # Log the transcription
    logger.info(f"Transcription [{transcript_type}] for call {call_id}: {text}")


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Infobip Voice Transcription Service is running"}


@app.get("/health")
async def health_check():
    """Health check endpoint with configuration status"""
    config_status = {
        "api_key_configured": bool(INFOBIP_API_KEY),
        "base_url_configured": bool(INFOBIP_BASE_URL),
        "service_status": "running",
    }
    return config_status


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
