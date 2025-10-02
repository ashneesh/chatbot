
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

# Import database client
try:
    from .database import db_client
except ImportError:
    # Fallback if database module not available
    db_client = None

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
        self.rasa_url = "http://localhost:5005"
        self.max_retries = 5
        self.retry_delay = 2
        # Add fallback URLs for deployment
        self.fallback_urls = [
            "http://localhost:5005",
            "http://127.0.0.1:5005",
            "http://rasa:5005"
        ]

    async def wait_for_rasa(self):
        """Wait for Rasa to be ready"""
        for attempt in range(self.max_retries):
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        f"{self.rasa_url}/status",
                        timeout=5.0
                    )
                    if response.status_code == 200:
                        logger.info("✅ Rasa server is ready")
                        return True
            except Exception as e:
                logger.info(f"⏳ Waiting for Rasa... (attempt {attempt + 1}/{self.max_retries})")
                await asyncio.sleep(self.retry_delay)
        
        logger.warning("⚠️ Rasa server not ready - using fallback mode")
        return False

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
    """Initialize services on startup"""
    logger.info("🚀 Starting up healthcare chatbot API...")
    
    # Initialize database connection (if available)
    if db_client:
        try:
            await db_client.connect()
            logger.info("✅ Database connected")
        except Exception as e:
            logger.warning(f"⚠️ Database connection failed: {e}")
    else:
        logger.info("ℹ️ Database client not available - running without database")
    
    # Wait for Rasa to be ready
    await rasa_client.wait_for_rasa()
    
    logger.info("✅ Application startup complete")

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up on shutdown"""
    if db_client:
        await db_client.close()
        logger.info("✅ Database connection closed")
    logger.info("✅ Application shutdown complete")

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

@app.post("/api/v1/appointments")
async def create_appointment(appointment_data: dict):
    """Create a new appointment"""
    try:
        if not db_client or not db_client.pool:
            return JSONResponse(
                status_code=503,
                content={"error": "Database not available"}
            )
        
        # Insert patient first if not exists
        patient_query = """
            INSERT INTO patients (name, email, phone, date_of_birth)
            VALUES ($1, $2, $3, $4)
            ON CONFLICT (email) DO UPDATE SET
                name = EXCLUDED.name,
                phone = EXCLUDED.phone,
                updated_at = NOW()
            RETURNING id
        """
        
        patient_result = await db_client.execute_query(
            patient_query,
            appointment_data.get("name"),
            appointment_data.get("email"),
            appointment_data.get("phone"),
            appointment_data.get("date_of_birth")
        )
        
        patient_id = patient_result[0]["id"]
        
        # Insert appointment
        appointment_query = """
            INSERT INTO appointments (patient_id, session_id, appointment_date, 
                                    appointment_time, appointment_type, reason, symptoms, urgency_level)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            RETURNING id, appointment_date, appointment_time
        """
        
        appointment_result = await db_client.execute_query(
            appointment_query,
            patient_id,
            appointment_data.get("session_id"),
            appointment_data.get("appointment_date"),
            appointment_data.get("appointment_time"),
            appointment_data.get("appointment_type", "consultation"),
            appointment_data.get("reason"),
            json.dumps(appointment_data.get("symptoms", {})),
            appointment_data.get("urgency_level", "low")
        )
        
        return {
            "success": True,
            "appointment_id": appointment_result[0]["id"],
            "appointment_date": appointment_result[0]["appointment_date"],
            "appointment_time": appointment_result[0]["appointment_time"]
        }
        
    except Exception as e:
        logger.error(f"Error creating appointment: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "Failed to create appointment", "detail": str(e)}
        )

@app.delete("/api/v1/appointments/{appointment_id}")
async def cancel_appointment(appointment_id: str):
    """Cancel an appointment"""
    try:
        if not db_client or not db_client.pool:
            return JSONResponse(
                status_code=503,
                content={"error": "Database not available"}
            )
        
        # Update appointment status to cancelled
        query = """
            UPDATE appointments 
            SET status = 'cancelled', updated_at = NOW()
            WHERE id = $1 AND status != 'cancelled'
            RETURNING id, appointment_date, appointment_time
        """
        
        result = await db_client.execute_query(query, appointment_id)
        
        if result:
            return {
                "success": True,
                "message": "Appointment cancelled successfully",
                "appointment_id": result[0]["id"]
            }
        else:
            return JSONResponse(
                status_code=404,
                content={"error": "Appointment not found or already cancelled"}
            )
            
    except Exception as e:
        logger.error(f"Error cancelling appointment: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "Failed to cancel appointment", "detail": str(e)}
        )

@app.post("/api/v1/symptoms")
async def save_symptom_report(symptom_data: dict):
    """Save symptom report to database"""
    try:
        if not db_client or not db_client.pool:
            return JSONResponse(
                status_code=503,
                content={"error": "Database not available"}
            )
        
        query = """
            INSERT INTO symptom_reports (session_id, symptoms, severity, urgency_level, assessment)
            VALUES ($1, $2, $3, $4, $5)
            RETURNING id
        """
        
        result = await db_client.execute_query(
            query,
            symptom_data.get("session_id"),
            json.dumps(symptom_data.get("symptoms", {})),
            symptom_data.get("severity", 5),
            symptom_data.get("urgency_level", "low"),
            symptom_data.get("assessment", "")
        )
        
        return {
            "success": True,
            "report_id": result[0]["id"]
        }
        
    except Exception as e:
        logger.error(f"Error saving symptom report: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "Failed to save symptom report", "detail": str(e)}
        )

@app.get("/api/v1/appointments")
async def get_appointments(session_id: str = None, email: str = None):
    """Get appointments by session_id or email"""
    try:
        if not db_client or not db_client.pool:
            return JSONResponse(
                status_code=503,
                content={"error": "Database not available"}
            )
        
        if session_id:
            query = """
                SELECT a.id, a.appointment_date, a.appointment_time, 
                       a.appointment_type, a.status, a.reason, a.symptoms, a.urgency_level,
                       p.name, p.email
                FROM appointments a
                LEFT JOIN patients p ON a.patient_id = p.id
                WHERE a.session_id = $1
                ORDER BY a.appointment_date DESC
            """
            result = await db_client.execute_query(query, session_id)
        elif email:
            query = """
                SELECT a.id, a.appointment_date, a.appointment_time, 
                       a.appointment_type, a.status, a.reason, a.symptoms, a.urgency_level,
                       p.name, p.email
                FROM appointments a
                JOIN patients p ON a.patient_id = p.id
                WHERE p.email = $1
                ORDER BY a.appointment_date DESC
            """
            result = await db_client.execute_query(query, email)
        else:
            return JSONResponse(
                status_code=400,
                content={"error": "session_id or email parameter required"}
            )
        
        appointments = []
        for row in result:
            appointments.append({
                "id": str(row["id"]),
                "appointment_date": row["appointment_date"].isoformat(),
                "appointment_time": row["appointment_time"].isoformat(),
                "appointment_type": row["appointment_type"],
                "status": row["status"],
                "reason": row["reason"],
                "symptoms": row["symptoms"],
                "urgency_level": row["urgency_level"],
                "patient_name": row["name"],
                "patient_email": row["email"]
            })
        
        return {"appointments": appointments}
        
    except Exception as e:
        logger.error(f"Error getting appointments: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "Failed to get appointments", "detail": str(e)}
        )

@app.post("/api/v1/sessions")
async def create_chat_session(session_data: dict):
    """Create or update a chat session"""
    try:
        if not db_client or not db_client.pool:
            return JSONResponse(
                status_code=503,
                content={"error": "Database not available"}
            )
        
        query = """
            INSERT INTO chat_sessions (session_id, user_id, context)
            VALUES ($1, $2, $3)
            ON CONFLICT (session_id) DO UPDATE SET
                updated_at = NOW(),
                context = EXCLUDED.context,
                is_active = TRUE
            RETURNING id, session_id, created_at
        """
        
        result = await db_client.execute_query(
            query,
            session_data.get("session_id"),
            session_data.get("user_id"),
            json.dumps(session_data.get("context", {}))
        )
        
        return {
            "success": True,
            "session_id": result[0]["session_id"],
            "created_at": result[0]["created_at"].isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error creating chat session: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "Failed to create chat session", "detail": str(e)}
        )

@app.post("/api/v1/messages")
async def save_chat_message(message_data: dict):
    """Save a chat message to database"""
    try:
        if not db_client or not db_client.pool:
            return JSONResponse(
                status_code=503,
                content={"error": "Database not available"}
            )
        
        query = """
            INSERT INTO chat_messages (session_id, content, message_type, sender, metadata)
            VALUES ($1, $2, $3, $4, $5)
            RETURNING id, timestamp
        """
        
        result = await db_client.execute_query(
            query,
            message_data.get("session_id"),
            message_data.get("content"),
            message_data.get("message_type", "text"),
            message_data.get("sender"),
            json.dumps(message_data.get("metadata", {}))
        )
        
        return {
            "success": True,
            "message_id": result[0]["id"],
            "timestamp": result[0]["timestamp"].isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error saving chat message: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "Failed to save chat message", "detail": str(e)}
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