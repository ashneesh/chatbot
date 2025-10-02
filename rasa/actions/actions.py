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
    """Book an appointment for the patient"""
    def name(self) -> Text:
        return "action_book_appointment"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        logger.info("Entered appointment booking action")

        patient_name = tracker.get_slot("patient_name")
        patient_email = tracker.get_slot("patient_email")
        if patient_name and patient_email:
            # In a real implementation, this would integrate with a booking system
            dispatcher.utter_message(
                text=f"✅ Thank you {patient_name}! I've scheduled an appointment request for you. "
                     f"We'll send confirmation details to {patient_email} within the next hour. "
                     f"Our staff will contact you to confirm the date and time."
            )
        else:
            dispatcher.utter_message(text="I need your name and email to book an appointment. Let me collect that information first.")

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
    """Cancel an existing appointment"""

    def name(self) -> Text:
        return "action_cancel_appointment"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        logger.info("Entered appointment cancellation action")
        
        # In a real implementation, this would query the database
        # For now, we'll simulate the cancellation process
        latest_message = tracker.latest_message.get('text', '').lower()
        
        # Check if user provided appointment details
        if any(keyword in latest_message for keyword in ['appointment', 'booking', 'visit']):
            # Simulate successful cancellation
            dispatcher.utter_message(
                text="✅ Your appointment has been successfully cancelled. "
                     "You will receive a confirmation email shortly. "
                     "If you need to reschedule, please let me know!"
            )
        else:
            dispatcher.utter_message(
                text="I'd be happy to help you cancel your appointment. "
                     "Please provide your appointment ID or the email address "
                     "you used for booking, and I'll cancel it for you."
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
        import re
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
