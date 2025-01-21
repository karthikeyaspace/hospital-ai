import asyncio
from langchain_google_genai import ChatGoogleGenerativeAI
from config import env
from storage import Storage
import json


template = """
        You are a Swiggles Hospital AI Assistant. Your role is to assist patients with booking appointments, 
        retrieving medical reports, and reporting emergencies. Always respond in a professional and empathetic manner. 
        If the request is unclear, ask for clarification.

        If the user asks a general question about the hospital, respond appropriately without invoking any tools.

        If the user requests to book an appointment, retrieve a medical report, or report an emergency, 
        ensure that all necessary information is provided. If any required information is missing, ask the user for it.

        Your response should be in JSON format with the following fields:
        - "tool": The tool to be invoked (e.g., "book_appointment", "get_report", "report_emergency", or "general" if no tool is needed).
        - "output": The response to the user.
        - "missing_info": Any missing information required to complete the request (if applicable).

        Example JSON response:
        {
            "tool": "book_appointment",
            "output": "Please provide the time for the appointment.",
            "missing_info": "time"
        }
        
        Ensure the response is valid JSON and can be parsed by Python's `json.loads()` function
        Do not generate any note or explanation at the end of the JSON response.
        

        History: {history}
        Question: {question}
        Answer:"""


class AI:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            api_key=env["GOOGLE_API_KEY"],
        )
        self.storage = Storage()

    async def interact(self, patient_id: str, message: str) -> str:
        try:
            history = self.storage.get_past_messages(
                patient_id) or "No past messages found for this patient"
            self.storage.add_to_conversation(patient_id, "user", message)
            prompt = template.format(history=history, question=message)

            response = await self.llm.ainvoke(prompt)

            print("AI response interact - ", response)

            format_res = response['text'].strip()
            if format_res.startswith("```json") and format_res.endswith("```"):
                format_res = format_res[7:-3].strip()

            print("Formatted res - ", format_res)

            try:
                response_json = json.loads(format_res)
                tool = response_json.get("tool")
                output = response_json.get("output")
                missing_info = response_json.get("missing_info", "")

                if tool == "book_appointment":
                    if missing_info == "time":
                        self.storage.add_to_conversation(
                            patient_id, "bot", output)
                        return output
                    else:
                        time = response_json.get("time")
                        result = self.book_appointment(patient_id, time)
                        self.storage.add_to_conversation(
                            patient_id, "bot", result)
                        return result

                elif tool == "get_report":
                    result = self.get_report(patient_id)
                    self.storage.add_to_conversation(patient_id, "bot", result)
                    return result

                elif tool == "report_emergency":
                    if missing_info == "details":
                        self.storage.add_to_conversation(
                            patient_id, "bot", output)
                        return output
                    else:
                        details = response_json.get("details")
                        result = self.report_emergency(patient_id, details)
                        self.storage.add_to_conversation(
                            patient_id, "bot", result)
                        return result

                else:
                    self.storage.add_to_conversation(patient_id, "bot", output)
                    return output

                return response_json.get("output")

            except json.JSONDecodeError:
                self.storage.add_to_conversation(
                    patient_id, "bot", "An error occurred while processing your request.")
                return "An error occurred while processing your request."

        except Exception as e:
            return f"An error occurred @ai.py.interact: {e}"

    def book_appointment(self, patient_id: str, time: str) -> str:
        return self.storage.add_to_appointments(patient_id, time)

    def get_report(self, patient_id: str) -> str:
        return f"Medical report for {patient_id}: Blood pressure - 120/80, Cholesterol - 190 mg/dL."

    def report_emergency(self, patient_id: str, details: str) -> str:
        return self.storage.add_to_emergencies(patient_id, details)


async def test():
    ai = AI()
    res = await ai.interact("6969", "Who are you")
    print(res)
    res = await ai.interact("6969", "I am getting stomach pain, can you book an appointment for 10am tomorrow")
    print(res)
    res = await ai.interact("6969", "I have an emergency, help me!")
    print(res)
    res = await ai.interact("6969", "Can I get my medical reports")
    print(res)

if __name__ == "__main__":
    asyncio.run(test())
