# """
# Healthcare Chatbot Backend - Main FastAPI Application
# """
# from fastapi import FastAPI, WebSocket, WebSocketDisconnect
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.responses import JSONResponse
# import json
# import asyncio
# import httpx
# from datetime import datetime
# from typing import Dict, List
# import logging

# # Configure logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# # Create FastAPI app
# app = FastAPI(
#     title="Healthcare Chatbot API",
#     description="Healthcare chatbot with Rasa integration",
#     version="1.0.0"
# )

# # Add CORS middleware
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # Configure appropriately for production
#     allow_credentials=True,
#     allow_methods=["GET", "POST", "PUT", "DELETE"],
#     allow_headers=["*"],
# )

# # WebSocket connection manager
# class ConnectionManager:
#     def __init__(self):
#         self.active_connections: List[WebSocket] = []

#     async def connect(self, websocket: WebSocket):
#         await websocket.accept()
#         self.active_connections.append(websocket)
#         logger.info(f"Client connected. Total connections: {len(self.active_connections)}")

#     def disconnect(self, websocket: WebSocket):
#         if websocket in self.active_connections:
#             self.active_connections.remove(websocket)
#         logger.info(f"Client disconnected. Total connections: {len(self.active_connections)}")

#     async def send_personal_message(self, message: str, websocket: WebSocket):
#         try:
#             await websocket.send_text(message)
#         except Exception as e:
#             logger.error(f"Error sending message: {e}")
#             self.disconnect(websocket)

# manager = ConnectionManager()

# # Rasa client
# class RasaClient:
#     def __init__(self):
#         self.rasa_url = "http://rasa-core:5005"

#     async def send_message(self, message: str, sender: str) -> dict:
#         try:
#             async with httpx.AsyncClient() as client:
#                 payload = {
#                     "sender": sender,
#                     "message": message
#                 }
#                 response = await client.post(
#                     f"{self.rasa_url}/webhooks/rest/webhook",
#                     json=payload,
#                     timeout=30.0
#                 )
#                 if response.status_code == 200:
#                     rasa_responses = response.json()
#                     if rasa_responses:
#                         return rasa_responses[0]

#         except Exception as e:
#             logger.error(f"Rasa connection error: {e}")

#         # Fallback response
#         return {
#             "text": "I'm having trouble processing your message right now. How can I help you with your health concerns?",
#             "buttons": [
#                 {"title": "Report Symptoms", "payload": "/report_symptom"},
#                 {"title": "Book Appointment", "payload": "/book_appointment"},
#                 {"title": "Get Advice", "payload": "/get_advice"}
#             ]
#         }

# rasa_client = RasaClient()

# @app.get("/")
# async def root():
#     return {
#         "message": "Healthcare Chatbot API",
#         "status": "running",
#         "version": "1.0.0",
#         "docs": "/docs"
#     }

# @app.get("/health")
# async def health_check():
#     return {
#         "status": "healthy",
#         "timestamp": datetime.utcnow().isoformat(),
#         "services": {
#             "api": "healthy",
#             "websocket": "healthy"
#         }
#     }

# @app.post("/api/v1/chat")
# async def chat_endpoint(request: dict):
#     """REST API endpoint for chat"""
#     try:
#         message = request.get("message", "")
#         session_id = request.get("session_id", "default_session")

#         # Send to Rasa
#         rasa_response = await rasa_client.send_message(message, session_id)

#         return {
#             "text": rasa_response.get("text", ""),
#             "buttons": rasa_response.get("buttons", []),
#             "session_id": session_id,
#             "timestamp": datetime.utcnow().isoformat()
#         }

#     except Exception as e:
#         logger.error(f"Chat endpoint error: {e}")
#         return JSONResponse(
#             status_code=500,
#             content={"error": "Internal server error"}
#         )

# @app.websocket("/ws/chat/{session_id}")
# async def websocket_chat_endpoint(websocket: WebSocket, session_id: str):
#     """WebSocket endpoint for real-time chat"""
#     await manager.connect(websocket)

#     # Send welcome message
#     welcome_message = {
#         "type": "system",
#         "message": "Connected to healthcare chatbot. How can I help you today?",
#         "timestamp": datetime.utcnow().isoformat()
#     }
#     await manager.send_personal_message(json.dumps(welcome_message), websocket)

#     try:
#         while True:
#             # Receive message from client
#             data = await websocket.receive_text()
#             message_data = json.loads(data)

#             if message_data.get("type") == "message":
#                 user_message = message_data.get("message", "")

#                 # Send user message confirmation
#                 user_msg_response = {
#                     "type": "message",
#                     "message": user_message,
#                     "sender": "user",
#                     "timestamp": datetime.utcnow().isoformat()
#                 }
#                 await manager.send_personal_message(json.dumps(user_msg_response), websocket)

#                 # Get response from Rasa
#                 rasa_response = await rasa_client.send_message(user_message, session_id)

#                 # Send bot response
#                 bot_response = {
#                     "type": "message",
#                     "message": rasa_response.get("text", ""),
#                     "sender": "bot",
#                     "buttons": rasa_response.get("buttons", []),
#                     "timestamp": datetime.utcnow().isoformat()
#                 }
#                 await manager.send_personal_message(json.dumps(bot_response), websocket)

#             elif message_data.get("type") == "typing":
#                 # Handle typing indicators
#                 typing_response = {
#                     "type": "typing",
#                     "isTyping": message_data.get("isTyping", False),
#                     "timestamp": datetime.utcnow().isoformat()
#                 }
#                 await manager.send_personal_message(json.dumps(typing_response), websocket)

#     except WebSocketDisconnect:
#         manager.disconnect(websocket)
#     except Exception as e:
#         logger.error(f"WebSocket error: {e}")
#         manager.disconnect(websocket)

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
"""
Healthcare Chatbot Backend - Main FastAPI Application with Enhanced Debugging
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import json
import os
import asyncio
import httpx
from datetime import datetime
from typing import Dict, List, Optional
import logging

# Configure logging with more detail
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Healthcare Chatbot API",
    description="Healthcare chatbot with Rasa integration",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"Client connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"Client disconnected. Total connections: {len(self.active_connections)}")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            self.disconnect(websocket)

manager = ConnectionManager()

# Rasa client with enhanced debugging
class RasaClient:
    def __init__(self):
        self.rasa_url = os.getenv("RASA_SERVER_URL","http://localhost:5005")
        # Alternative URLs to try if running locally
        self.fallback_urls = [
            "http://localhost:5005",
            "http://127.0.0.1:5005",
            "http://rasa:5005"
        ]

    async def check_rasa_health(self) -> bool:
        """Check if Rasa server is healthy"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.rasa_url}/", timeout=5.0)
                logger.info(f"Rasa health check: {response.status_code}")
                return response.status_code == 200
        except Exception as e:
            logger.error(f"Rasa health check failed: {e}")
            return False

    async def send_message(self, message: str, sender: str) -> dict:
        """Send message to Rasa and get response"""
        logger.info(f"Sending to Rasa - Sender: {sender}, Message: {message}")
        
        urls_to_try = [self.rasa_url] + self.fallback_urls
        
        for url in urls_to_try:
            try:
                async with httpx.AsyncClient() as client:
                    payload = {
                        "sender": sender,
                        "message": message
                    }
                    
                    logger.debug(f"Trying Rasa URL: {url}")
                    logger.debug(f"Payload: {payload}")
                    
                    response = await client.post(
                        f"{url}/webhooks/rest/webhook",
                        json=payload,
                        timeout=30.0
                    )
                    
                    logger.info(f"Rasa response status: {response.status_code}")
                    logger.debug(f"Rasa response body: {response.text}")
                    
                    if response.status_code == 200:
                        rasa_responses = response.json()
                        logger.info(f"Rasa returned {len(rasa_responses)} responses")
                        
                        if rasa_responses:
                            # Log the response details
                            for idx, resp in enumerate(rasa_responses):
                                logger.debug(f"Response {idx}: {resp}")
                            
                            # Return the first response
                            return rasa_responses[0]
                        else:
                            logger.warning("Rasa returned empty response list")
                            return self._create_fallback_response(
                                "Rasa returned no responses"
                            )
                    else:
                        logger.error(f"Rasa returned status {response.status_code}")
                        
            except httpx.ConnectError as e:
                logger.error(f"Failed to connect to Rasa at {url}: {e}")
                continue
            except httpx.TimeoutException as e:
                logger.error(f"Rasa request timeout at {url}: {e}")
                continue
            except Exception as e:
                logger.error(f"Unexpected error with Rasa at {url}: {e}", exc_info=True)
                continue
        
        # If all URLs failed
        logger.error("All Rasa connection attempts failed")
        return self._create_fallback_response("Connection failed")

    def _create_fallback_response(self, reason: str) -> dict:
        """Create a fallback response when Rasa is unavailable"""
        logger.warning(f"Creating fallback response. Reason: {reason}")
        return {
            "text": "I'm having trouble processing your message right now. How can I help you with your health concerns?",
            "buttons": [
                {"title": "Report Symptoms", "payload": "/report_symptoms"},
                {"title": "Book Appointment", "payload": "/book_appointment"},
                {"title": "Get Advice", "payload": "/get_health_advice"}
            ]
        }

rasa_client = RasaClient()

@app.on_event("startup")
async def startup_event():
    """Check Rasa connection on startup"""
    logger.info("Starting up healthcare chatbot API...")
    is_healthy = await rasa_client.check_rasa_health()
    if is_healthy:
        logger.info("✅ Rasa server is healthy and reachable")
    else:
        logger.error("❌ Rasa server is not reachable - fallback mode enabled")

@app.get("/")
async def root():
    return {
        "message": "Healthcare Chatbot API",
        "status": "running",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Enhanced health check with Rasa status"""
    rasa_healthy = await rasa_client.check_rasa_health()
    
    return {
        "status": "healthy" if rasa_healthy else "degraded",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "api": "healthy",
            "websocket": "healthy",
            "rasa": "healthy" if rasa_healthy else "unavailable"
        }
    }

@app.get("/debug/rasa-status")
async def debug_rasa_status():
    """Debug endpoint to check Rasa connectivity"""
    rasa_healthy = await rasa_client.check_rasa_health()
    
    return {
        "rasa_url": rasa_client.rasa_url,
        "status": "connected" if rasa_healthy else "disconnected",
        "fallback_urls": rasa_client.fallback_urls,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/api/v1/chat")
async def chat_endpoint(request: dict):
    """REST API endpoint for chat with enhanced logging"""
    try:
        message = request.get("message", "")
        session_id = request.get("session_id", "default_session")
        
        logger.info(f"Chat request - Session: {session_id}, Message: {message}")

        if not message:
            return JSONResponse(
                status_code=400,
                content={"error": "Message is required"}
            )

        # Send to Rasa
        rasa_response = await rasa_client.send_message(message, session_id)
        
        response_data = {
            "text": rasa_response.get("text", ""),
            "buttons": rasa_response.get("buttons", []),
            "session_id": session_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        logger.info(f"Sending response: {response_data['text'][:100]}...")
        
        return response_data

    except Exception as e:
        logger.error(f"Chat endpoint error: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error", "detail": str(e)}
        )

@app.websocket("/ws/chat/{session_id}")
async def websocket_chat_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time chat"""
    await manager.connect(websocket)
    
    logger.info(f"WebSocket connected for session: {session_id}")

    # Send welcome message
    welcome_message = {
        "type": "system",
        "message": "Connected to healthcare chatbot. How can I help you today?",
        "timestamp": datetime.utcnow().isoformat()
    }
    await manager.send_personal_message(json.dumps(welcome_message), websocket)

    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            logger.debug(f"WebSocket received: {message_data}")

            if message_data.get("type") == "message":
                user_message = message_data.get("message", "")
                
                logger.info(f"User message via WebSocket: {user_message}")

                # Send user message confirmation
                user_msg_response = {
                    "type": "message",
                    "message": user_message,
                    "sender": "user",
                    "timestamp": datetime.utcnow().isoformat()
                }
                await manager.send_personal_message(json.dumps(user_msg_response), websocket)

                # Get response from Rasa
                rasa_response = await rasa_client.send_message(user_message, session_id)
                
                logger.info(f"Bot response: {rasa_response.get('text', '')[:100]}...")

                # Send bot response
                bot_response = {
                    "type": "message",
                    "message": rasa_response.get("text", ""),
                    "sender": "bot",
                    "buttons": rasa_response.get("buttons", []),
                    "timestamp": datetime.utcnow().isoformat()
                }
                await manager.send_personal_message(json.dumps(bot_response), websocket)

            elif message_data.get("type") == "typing":
                # Handle typing indicators
                typing_response = {
                    "type": "typing",
                    "isTyping": message_data.get("isTyping", False),
                    "timestamp": datetime.utcnow().isoformat()
                }
                await manager.send_personal_message(json.dumps(typing_response), websocket)

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for session: {session_id}")
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}", exc_info=True)
        manager.disconnect(websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, log_level="debug")