import logging
import os
import urllib.parse
from datetime import datetime
from typing import Any, Dict, Optional

from dotenv import load_dotenv

load_dotenv()

# Import FastAPI and Twilio libraries
from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import Response
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse

# Import ChromaDB function
from chromadb_utils.utils import add_document, retrieve_document

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Twilio Voice Call Transcription Service")

# Configuration
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
BASE_URL = os.getenv(
    "BASE_URL"
)  # Your server's public URL (e.g., https://yourdomain.com)

if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN:
    raise ValueError(
        "TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN must be set in environment variables"
    )

if not BASE_URL:
    logger.warning("BASE_URL not set - transcription webhooks may not work properly")

# Initialize Twilio client
twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)


@app.post("/webhooks/voice", response_class=Response)
async def handle_incoming_call(request: Request):
    """
    Webhook endpoint for incoming Twilio voice calls

    This endpoint handles incoming calls and responds with TwiML
    to record the call with transcription enabled
    """
    try:
        # Get form data from Twilio webhook
        form_data = await request.form()
        call_sid = form_data.get("CallSid")
        from_number = form_data.get("From")
        to_number = form_data.get("To")

        logger.info(
            f"Incoming call from {from_number} to {to_number}, Call SID: {call_sid}"
        )

        # Create TwiML response
        response = VoiceResponse()

        # Greet the caller
        response.say("Hello! Welcome to CallMind!")

        # Record the call with transcription enabled
        # The recording will continue until the caller hangs up or presses #
        transcription_callback = (
            f"{BASE_URL}/webhooks/transcription" if BASE_URL else None
        )

        response.record(
            action=f"{BASE_URL}/webhooks/recording-complete" if BASE_URL else None,
            transcribe=True,
            transcribe_callback=transcription_callback,
            finish_on_key="#",
            max_length=3600,  # Maximum 1 hour
            play_beep=True,
        )

        # Say goodbye after recording
        response.say("Thank you for your call. Goodbye!")

        # Return TwiML response
        return Response(content=str(response), media_type="application/xml")

    except Exception as e:
        logger.error(f"Error handling incoming call: {e}")

        # Return a simple TwiML response for errors
        response = VoiceResponse()
        response.say(
            "Sorry, there was an error processing your call. Please try again later."
        )
        return Response(content=str(response), media_type="application/xml")


@app.post("/webhooks/transcription")
async def handle_transcription(
    request: Request,
    CallSid: str = Form(...),
    TranscriptionText: str = Form(...),
    TranscriptionStatus: str = Form(...),
    RecordingSid: str = Form(...),
    RecordingUrl: str = Form(...),
    From: str = Form(None),
    To: str = Form(None),
):
    """
    Webhook endpoint for Twilio transcription results

    This endpoint receives the transcription when recording is complete
    """
    try:
        logger.info(f"Received transcription for call {CallSid}")

        # Print transcription results
        print(f"\n{'='*80}")
        print(f"TRANSCRIPTION COMPLETE - Call SID: {CallSid}")
        print(f"From: {From}")
        print(f"To: {To}")
        print(f"Status: {TranscriptionStatus}")
        print(f"Recording SID: {RecordingSid}")
        print(f"Recording URL: {RecordingUrl}")
        print(f"Transcription: {TranscriptionText}")
        print(f"{'='*80}\n")

        # Log the transcription
        logger.info(f"Transcription for call {CallSid}: {TranscriptionText}")

        # Store in ChromaDB if transcription was successful
        if TranscriptionStatus.lower() == "completed" and TranscriptionText.strip():
            try:
                # Create metadata for the call
                call_metadata = {
                    "call_sid": CallSid,
                    "recording_sid": RecordingSid,
                    "from_number": From,
                    "to_number": To,
                    "transcription_status": TranscriptionStatus,
                    "recording_url": RecordingUrl,
                    "timestamp": datetime.utcnow().isoformat(),
                    "source": "twilio_transcription",
                }

                # Add the transcription to ChromaDB
                add_document(
                    document=TranscriptionText,
                    metadata=call_metadata,  # Pass metadata as a single dict
                )

                logger.info(
                    f"Successfully stored transcription for call {CallSid} in ChromaDB"
                )
                print(f"✓ Transcription stored in ChromaDB for call {CallSid}")

            except Exception as db_error:
                logger.error(f"Failed to store transcription in ChromaDB: {db_error}")
                print(f"✗ Failed to store transcription in ChromaDB: {db_error}")
        else:
            logger.info(
                f"Skipping ChromaDB storage - Status: {TranscriptionStatus}, Text length: {len(TranscriptionText.strip())}"
            )

        return {"status": "success"}

    except Exception as e:
        logger.error(f"Error processing transcription webhook: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/webhooks/recording-complete")
async def handle_recording_complete(
    request: Request,
    CallSid: str = Form(...),
    RecordingSid: str = Form(...),
    RecordingUrl: str = Form(...),
    RecordingDuration: str = Form(...),
    From: str = Form(None),
    To: str = Form(None),
):
    """
    Webhook endpoint for when recording is complete

    This is called when the recording finishes (before transcription is ready)
    """
    try:
        logger.info(f"Recording complete for call {CallSid}")
        logger.info(f"Recording SID: {RecordingSid}, Duration: {RecordingDuration}s")
        logger.info(f"Recording URL: {RecordingUrl}")

        print(f"\n{'='*60}")
        print(f"RECORDING COMPLETE - Call SID: {CallSid}")
        print(f"From: {From}")
        print(f"To: {To}")
        print(f"Duration: {RecordingDuration} seconds")
        print(f"Recording URL: {RecordingUrl}")
        print(f"Transcription will be available shortly...")
        print(f"{'='*60}\n")

        return {"status": "success"}

    except Exception as e:
        logger.error(f"Error processing recording complete webhook: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/webhooks/call-status")
async def handle_call_status(
    request: Request,
    CallSid: str = Form(...),
    CallStatus: str = Form(...),
    From: str = Form(None),
    To: str = Form(None),
):
    """
    Webhook endpoint for call status updates

    This receives updates about call progress (ringing, answered, completed, etc.)
    """
    try:
        logger.info(f"Call status update: {CallSid} - {CallStatus}")

        if CallStatus == "completed":
            print(f"\nCall {CallSid} from {From} to {To} has ended.")
        elif CallStatus == "answered":
            print(f"\nCall {CallSid} from {From} to {To} was answered.")

        return {"status": "success"}

    except Exception as e:
        logger.error(f"Error processing call status webhook: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Twilio Voice Transcription Service is running"}


@app.get("/health")
async def health_check():
    """Health check endpoint with configuration status"""
    config_status = {
        "account_sid_configured": bool(TWILIO_ACCOUNT_SID),
        "auth_token_configured": bool(TWILIO_AUTH_TOKEN),
        "base_url_configured": bool(BASE_URL),
        "service_status": "running",
    }
    return config_status


@app.get("/transcriptions/search")
async def search_transcriptions(
    query: str,
    n_results: int = 5,
    from_number: Optional[str] = None,
    to_number: Optional[str] = None,
):
    """
    Search stored transcriptions by content or metadata

    Args:
        query: Text to search for in transcriptions
        n_results: Maximum number of results to return
        from_number: Filter by caller phone number
        to_number: Filter by called phone number
    """
    try:
        # Build where clause for filtering
        where_clause = {}
        if from_number:
            where_clause["from_number"] = from_number
        if to_number:
            where_clause["to_number"] = to_number

        # Search transcriptions
        results = retrieve_document(
            query=query,
            n_results=n_results,
            where=where_clause if where_clause else None,
            include=["documents", "metadatas", "distances"],
        )

        # Format results for response
        formatted_results = []
        if results.get("documents") and results["documents"][0]:
            for i, doc in enumerate(results["documents"][0]):
                result = {
                    "transcription": doc,
                    "metadata": (
                        results["metadatas"][0][i] if results.get("metadatas") else None
                    ),
                    "similarity_score": (
                        1 - results["distances"][0][i]
                        if results.get("distances")
                        else None
                    ),
                }
                formatted_results.append(result)

        return {
            "query": query,
            "results_count": len(formatted_results),
            "results": formatted_results,
        }

    except Exception as e:
        logger.error(f"Error searching transcriptions: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@app.get("/transcriptions/recent")
async def get_recent_transcriptions(limit: int = 10):
    """
    Get recent transcriptions (simple search with no query)
    """
    try:
        # Get recent transcriptions by searching with a broad query
        results = retrieve_document(
            query="call transcription",  # Broad query to match most transcriptions
            n_results=limit,
            include=["documents", "metadatas"],
        )

        # Format results
        formatted_results = []
        if results.get("documents") and results["documents"][0]:
            for i, doc in enumerate(results["documents"][0]):
                metadata = (
                    results["metadatas"][0][i] if results.get("metadatas") else None
                )
                result = {
                    "transcription": doc,
                    "call_sid": metadata.get("call_sid") if metadata else None,
                    "from_number": metadata.get("from_number") if metadata else None,
                    "to_number": metadata.get("to_number") if metadata else None,
                    "timestamp": metadata.get("timestamp") if metadata else None,
                }
                formatted_results.append(result)

        return {"results_count": len(formatted_results), "results": formatted_results}

    except Exception as e:
        logger.error(f"Error getting recent transcriptions: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to get transcriptions: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
