"""
This files contains your custom actions which can be used to run
custom Python code.

See this guide on how to implement these action:
https://rasa.com/docs/rasa/custom-actions
"""

from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormValidationAction
from rasa_sdk.events import SlotSet
import logging
import httpx
import json
import re
from datetime import datetime
import asyncio

logger = logging.getLogger(__name__)

class ActionAssessSymptoms(Action):
    """Assess symptoms and provide triage guidance"""

    def name(self) -> Text:
        return "action_assess_symptoms"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        symptoms = tracker.get_slot("symptoms") or []
        logger.debug(symptoms,"symptoms")
        logger.debug(isinstance(symptoms,str),'instance of symptoms')
        if isinstance(symptoms, str):
            symptoms = [symptoms]
        elif symptoms is None:
            symptoms = []
        # Simple symptom assessment
        emergency_symptoms = ["chest pain", "difficulty breathing", "severe bleeding", "heart attack"]
        high_priority = ["severe pain", "high fever", "vomiting blood"]

        symptom_text = " ".join(symptoms).lower() if symptoms else ""
        latest_message = tracker.latest_message.get('text', '').lower()
        combined_text = f"{symptom_text} {latest_message}"

        urgency_level = "low"

        # Check for emergency symptoms
        if any(emergency in combined_text for emergency in emergency_symptoms):
            urgency_level = "emergency"
            dispatcher.utter_message(text="🚨 This sounds like a medical emergency. Please call 911 immediately or go to the nearest emergency room!")
        elif any(high_symptom in combined_text for high_symptom in high_priority):
            urgency_level = "high"
            dispatcher.utter_message(text="⚠️ Your symptoms suggest you should seek immediate medical attention. Please contact your healthcare provider right away.")
        elif symptoms and len(symptoms) > 1:
            urgency_level = "medium"
            dispatcher.utter_message(text="📞 Based on your symptoms, I recommend contacting your healthcare provider within 24 hours.")
        else:
            dispatcher.utter_message(text="📋 Your symptoms appear to be minor. Consider monitoring them and schedule a routine appointment if they persist.")

        dispatcher.utter_message(text="Would you like me to help you book an appointment?")

        return [SlotSet("urgency_level", urgency_level)]

class ActionBookAppointment(Action):
    """Book an appointment and save to database"""
    def name(self) -> Text:
        return "action_book_appointment"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Extract form data
        name = tracker.get_slot("patient_name")
        email = tracker.get_slot("patient_email")
        symptoms = tracker.get_slot("symptoms")
        
        if not all([name, email, symptoms]):
            dispatcher.utter_message(
                text="I need your name, email, and symptoms to book an appointment."
            )
            return []
        
        # Create appointment data
        appointment_data = {
            "name": name,
            "email": email,
            "session_id": tracker.sender_id,
            "appointment_date": "2024-01-15",  # Default date - you can make this dynamic
            "appointment_time": "10:00:00",    # Default time - you can make this dynamic
            "appointment_type": "consultation",
            "reason": f"Symptoms: {', '.join(symptoms) if isinstance(symptoms, list) else symptoms}",
            "symptoms": symptoms if isinstance(symptoms, list) else [symptoms],
            "urgency_level": "medium"  # You can make this dynamic based on symptoms
        }
        
        try:
            # Send to FastAPI backend
            response = httpx.post(
                "http://localhost:8000/api/v1/appointments",
                json=appointment_data,
                timeout=10.0
            )
            
            if response.status_code == 200:
                result = response.json()
                dispatcher.utter_message(
                    text=f"Great! I've booked your appointment for {result['appointment_date']} at {result['appointment_time']}. "
                         f"Your appointment ID is {result['appointment_id']}. You'll receive a confirmation email shortly."
                )
            else:
                dispatcher.utter_message(
                    text="I had trouble booking your appointment. Please try again or contact our office directly."
                )
                
        except Exception as e:
            logger.error(f"Error booking appointment: {e}")
            dispatcher.utter_message(
                text="I had trouble booking your appointment. Please try again or contact our office directly."
            )
        
        return []

class ActionProvideHealthAdvice(Action):
    """Provide general health advice"""

    def name(self) -> Text:
        return "action_provide_health_advice"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        latest_message = tracker.latest_message.get('text', '').lower()

        # Simple health advice based on keywords
        advice_responses = {
            "cold": "For a common cold: Rest, stay hydrated, and consider over-the-counter medications. If symptoms persist beyond a week or worsen, consult a healthcare provider.",
            "fever": "For fever: Rest, stay hydrated, and monitor your temperature. Seek medical attention if fever is above 103°F (39.4°C) or persists.",
            "headache": "For headaches: Try resting in a quiet, dark room and staying hydrated. If headaches are severe or frequent, consult a healthcare provider.",
            "cough": "For cough: Stay hydrated and avoid irritants. A persistent cough should be evaluated by a healthcare provider.",
        }

        advice_given = False
        for condition, advice in advice_responses.items():
            if condition in latest_message:
                dispatcher.utter_message(text=advice)
                advice_given = True
                break

        if not advice_given:
            dispatcher.utter_message(
                text="For specific health concerns, I recommend consulting with a qualified healthcare provider. "
                     "They can provide personalized advice based on your medical history."
            )

        dispatcher.utter_message(text="⚠️ Disclaimer: This is general information only and not medical advice. Always consult healthcare professionals for medical concerns.")

        return []

class ActionHandoverToHuman(Action):
    """Handover conversation to human agent"""

    def name(self) -> Text:
        return "action_handover_to_human"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(
            text="I'm connecting you with a healthcare professional. "
                 "Please hold on while I transfer you to our nursing staff. "
                 "In the meantime, if this is an emergency, please call 911."
        )

        # In a real implementation, this would trigger a handover to live chat
        return []

class ActionDefaultFallback(Action):
    """Default fallback action"""

    def name(self) -> Text:
        return "action_default_fallback"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(
            text="""I'm sorry, I didn't understand that. I can help you with:
"
                 "• Reporting symptoms
"
                 "• Booking appointments
" 
                 "• Health advice
"
                 "• Connecting you with a healthcare professional

"
                 "How can I assist you?"""
        )

        return []

class ActionCancelAppointment(Action):
    """Cancel an appointment using database"""
    def name(self) -> Text:
        return "action_cancel_appointment"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Try to get appointment ID from user message
        latest_message = tracker.latest_message.get('text', '')
        
        # Look for appointment ID in the message (UUID format)
        appointment_id_match = re.search(r'[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}', latest_message)
        
        if appointment_id_match:
            appointment_id = appointment_id_match.group(0)
            
            try:
                # Cancel appointment via API
                response = httpx.delete(
                    f"http://localhost:8000/api/v1/appointments/{appointment_id}",
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    dispatcher.utter_message(
                        text="Your appointment has been successfully cancelled. You will receive a confirmation email shortly."
                    )
                else:
                    dispatcher.utter_message(
                        text="I couldn't find an appointment with that ID. Please check your appointment ID and try again."
                    )
                    
            except Exception as e:
                logger.error(f"Error cancelling appointment: {e}")
                dispatcher.utter_message(
                    text="I had trouble cancelling your appointment. Please try again or contact our office directly."
                )
        else:
            # Try to find appointments by email or session
            email = tracker.get_slot("patient_email")
            session_id = tracker.sender_id
            
            try:
                # Get appointments for this user
                if email:
                    response = httpx.get(
                        f"http://localhost:8000/api/v1/appointments?email={email}",
                        timeout=10.0
                    )
                else:
                    response = httpx.get(
                        f"http://localhost:8000/api/v1/appointments?session_id={session_id}",
                        timeout=10.0
                    )
                
                if response.status_code == 200:
                    appointments = response.json().get("appointments", [])
                    active_appointments = [apt for apt in appointments if apt["status"] != "cancelled"]
                    
                    if active_appointments:
                        # Show available appointments to cancel
                        appointment_list = "\n".join([
                            f"- ID: {apt['id']}, Date: {apt['appointment_date']}, Time: {apt['appointment_time']}"
                            for apt in active_appointments
                        ])
                        dispatcher.utter_message(
                            text=f"I found these active appointments:\n{appointment_list}\n\nPlease provide the appointment ID you'd like to cancel."
                        )
                    else:
                        dispatcher.utter_message(
                            text="I couldn't find any active appointments to cancel. Please check your appointment ID or email address."
                        )
                else:
                    dispatcher.utter_message(
                        text="I couldn't find any appointments. Please provide your appointment ID or the email address you used for booking."
                    )
                    
            except Exception as e:
                logger.error(f"Error getting appointments: {e}")
                dispatcher.utter_message(
                    text="I had trouble accessing your appointments. Please provide your appointment ID or contact our office directly."
                )
        
        return []

class ValidatePatientForm(FormValidationAction):
    """Validate patient form inputs"""

    def name(self) -> Text:
        return "validate_patient_form"

    def validate_patient_name(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate patient name"""
        if slot_value and len(slot_value.strip()) > 1:
            return {"patient_name": slot_value.strip()}
        else:
            dispatcher.utter_message(text="Please provide a valid name.")
            return {"patient_name": None}

    def validate_patient_email(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate patient email"""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if slot_value and re.match(email_pattern, slot_value.strip()):
            return {"patient_email": slot_value.strip()}
        else:
            dispatcher.utter_message(text="Please provide a valid email address.")
            return {"patient_email": None}

    def validate_symptoms(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate symptoms input"""
        if slot_value:
            if isinstance(slot_value, str):
                # Convert string to list if needed
                symptoms = [symptom.strip() for symptom in slot_value.split(',') if symptom.strip()]
            elif isinstance(slot_value, list):
                symptoms = [symptom.strip() for symptom in slot_value if symptom.strip()]
            else:
                symptoms = []
            
            if symptoms:
                return {"symptoms": symptoms}
        
        dispatcher.utter_message(text="Please describe your symptoms in detail.")
        return {"symptoms": None}

class ActionSaveSymptomReport(Action):
    """Save symptom report to database"""
    def name(self) -> Text:
        return "action_save_symptom_report"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        symptoms = tracker.get_slot("symptoms")
        session_id = tracker.sender_id
        
        if not symptoms:
            return []
        
        # Determine severity and urgency based on symptoms
        severity = 5  # Default medium severity
        urgency_level = "low"  # Default low urgency
        
        # You can add logic here to determine severity based on symptoms
        if isinstance(symptoms, list):
            symptom_text = " ".join(symptoms).lower()
        else:
            symptom_text = str(symptoms).lower()
        
        # Simple urgency detection
        urgent_keywords = ["emergency", "severe", "pain", "bleeding", "chest pain", "difficulty breathing"]
        if any(keyword in symptom_text for keyword in urgent_keywords):
            urgency_level = "high"
            severity = 8
        
        symptom_data = {
            "session_id": session_id,
            "symptoms": symptoms if isinstance(symptoms, list) else [symptoms],
            "severity": severity,
            "urgency_level": urgency_level,
            "assessment": f"Reported symptoms: {', '.join(symptoms) if isinstance(symptoms, list) else symptoms}"
        }
        
        try:
            # Save to database
            response = httpx.post(
                "http://localhost:8000/api/v1/symptoms",
                json=symptom_data,
                timeout=10.0
            )
            
            if response.status_code == 200:
                logger.info(f"Symptom report saved for session {session_id}")
            else:
                logger.error(f"Failed to save symptom report: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Error saving symptom report: {e}")
        
        return []

class ActionGetPerformanceMetrics(Action):
    """Get performance metrics for monitoring"""
    
    def name(self) -> Text:
        return "action_get_performance_metrics"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Simple performance metrics
        metrics = {
            "total_messages": len(tracker.events),
            "session_duration": "active",
            "intent_confidence": tracker.latest_message.get("intent", {}).get("confidence", 0),
            "timestamp": datetime.now().isoformat()
        }
        
        dispatcher.utter_message(
            text=f"Performance metrics: {json.dumps(metrics, indent=2)}"
        )
        
        return []
