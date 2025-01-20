from typing import Dict, List

# TODO - reconfigure the retunr types to storage class

class Storage:
    def __init__(self):
        # Store appointments in format {patient_id: {time: str, status: str}}
        self.appointments: Dict[str, Dict[str, str]] = {}

        # Store conversation history in format {chat_id: [{"user": str, "bot": str}, ...]}
        self.conversations: Dict[str, List[Dict[str, str]]] = {}

        # Store emergencies in format {patient_id: details}
        self.emergencies: List[str] = []

    
    # store ai and user conversation
    def add_to_conversation(self, patient_id: str, role: str, message: str):
        if patient_id not in self.conversations:
            self.conversations[patient_id] = []
        self.conversations[patient_id].append({role: message})

    
    # return all chats of user
    def get_past_messages(self, patient_id: str) -> Dict:
        if patient_id in self.conversations:
            return self.conversations[patient_id][-1]
        return None


    # add to appointments
    def add_to_appointments(self, patient_id: str, time: str):
        if patient_id in self.appointments:
            return f"Patient {patient_id} already has an appointment at {self.appointments[patient_id]['time']}."
        self.appointments[patient_id] = {"time": time, "status": "scheduled"}
        return f"Appointment booked successfully for {patient_id} at {time}."

    
    # add to emergencies
    def add_to_emergencies(self, patient_id: str):
        self.emergencies.append(patient_id)
        return f"Emergency reported successfully for {patient_id}. Help is on the way"
