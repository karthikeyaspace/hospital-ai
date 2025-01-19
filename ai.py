from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
from langchain_core.prompts import PromptTemplate
from config import env
from datetime import datetime, time
from typing import Dict, List, Optional

llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    api_key=env["GOOGLE_API_KEY"],
)


class AI:
    def __init__(self):
        self.llm_with_tools = llm.bind_tools(
            [self.book_appointment, self.get_report, self.report_emergency]
        )

        # Store appointments in format {patient_id: {time: str, status: str}}
        self.appointments: Dict[str, Dict[str, str]] = {}

        # Store conversation history in format {chat_id: [{"user": str, "bot": str}, ...]}
        self.conversations: Dict[str, List[Dict[str, str]]] = {}

        # Store emergencies in format {patient_id: details}
        self.emergencies: Dict[str, str] = {}

    def chain(self):
        prompt = PromptTemplate(
            template="""
                You are a Hospital AI Assistant. Your role is to assist patients with booking appointments, retrieving medical reports, and reporting emergencies. 
                Always respond in a professional and empathetic manner. If the request is unclear, ask for clarification.

                Context: {context}
                Question: {question}
                Answer:""",
            input_variables=["context", "question"]
        )
        return prompt

    async def respond(self, chat_id: str, prompt: str) -> str:
        try:
            print(f"User ({chat_id}): {prompt}")

            self._add_to_conversation(chat_id, "user", prompt)

            context = self._get_context(chat_id)
            if context and "awaiting_input" in context:
                response = self._handle_partial_input(chat_id, prompt, context)
            else:
                response = await self._handle_new_request(chat_id, prompt)

            self._add_to_conversation(chat_id, "bot", response)
            return response
        except Exception as e:
            return f"An error occurred: {e}"

    def _add_to_conversation(self, chat_id: str, role: str, message: str):
        if chat_id not in self.conversations:
            self.conversations[chat_id] = []
        self.conversations[chat_id].append({role: message})

    def _get_context(self, chat_id: str) -> Optional[Dict]:
        if chat_id in self.conversations:
            return self.conversations[chat_id][-1].get("context", {})
        return None

    @tool
    def book_appointment(self, patient_id: str, time: str) -> str:
        """
        Books an appointment for a patient at the specified time.

        Args:
            patient_id (str): Unique ID of the patient.
            time (str): Time of the appointment in 'HH:MM' format (24-hour clock).

        Returns:
            str: Confirmation message or error.
        """
        if not self._validate_time(time):
            return "Invalid time format. Please use 'HH:MM' (24-hour clock)."

        if patient_id in self.appointments:
            return f"Patient {patient_id} already has an appointment at {self.appointments[patient_id]['time']}."

        self.appointments[patient_id] = {"time": time, "status": "scheduled"}
        return f"Appointment booked successfully for {patient_id} at {time}."

    @tool
    def get_report(self, patient_id: str) -> str:
        """
        Retrieves the medical report for a patient.

        Args:
            patient_id (str): Unique ID of the patient.

        Returns:
            str: Medical report or error message.
        """
        if patient_id not in self.appointments:
            return f"No records found for patient {patient_id}."

        return f"Medical report for {patient_id}: Blood pressure - 120/80, Cholesterol - 190 mg/dL."

    @tool
    def report_emergency(self, patient_id: str, details: str) -> str:
        """
        Reports an emergency for a patient.

        Args:
            patient_id (str): Unique ID of the patient.
            details (str): Description of the emergency.

        Returns:
            str: Confirmation message or error.
        """
        if not details:
            return "Please provide details of the emergency."

        self.emergencies[patient_id] = details
        return f"Emergency reported for {patient_id}. Details: {details}. Help is on the way!"

