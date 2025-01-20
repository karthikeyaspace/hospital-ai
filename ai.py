import asyncio
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
from langchain_core.prompts import PromptTemplate
from langchain.chains.question_answering import load_qa_chain
from pydantic import BaseModel, Field
from config import env
from storage import Storage

llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    api_key=env["GOOGLE_API_KEY"],
)

prompt = PromptTemplate(
    template="""
        You are a Swiggles Hospital AI Assistant. Your role is to assist patients with booking appointments, retrieving medical reports, and reporting emergencies.
        Always respond in a professional and empathetic manner. If the request is unclear, ask for clarification
        
        Context: {context}
        Question: {question}
        Answer:""",
    input_variables=["context", "question"],
)


class AI:
    def __init__(self):
        self.llm_with_tools = llm.bind_tools(
            [self.book_appointment, self.get_report, self.report_emergency]
        )

        # Run time storage initialization
        self.storage = Storage()

        self.chain = load_qa_chain(llm=llm, chain_type="stuff", prompt=prompt)

    async def interact(self, patient_id: str, message: str) -> str:
        try:
            self.storage.add_to_conversation(patient_id, "user", message)
            context = self.storage.get_past_messages(patient_id)

            # For tool calling - invoking functions
            response = await self.llm_with_tools.ainvoke(message)

            print("AI response interact: ", response)

            # Check if the response includes tool calls
            if hasattr(response, "tool_calls"):
                for tool_call in response.tool_calls:
                    tool_name = tool_call["name"]
                    tool_args = tool_call["args"]

                    # Call the appropriate tool based on the tool name
                    if tool_name == "book_appointment":
                        tool_output = self.book_appointment(patient_id, tool_args["time"])
                    elif tool_name == "get_report":
                        tool_output = self.get_report(patient_id)
                    elif tool_name == "report_emergency":
                        tool_output = self.report_emergency(patient_id, tool_args["details"])
                    else:
                        tool_output = "Unknown tool call."

                    # Add tool output to conversation history
                    self.storage.add_to_conversation(patient_id, "bot", tool_output)
                    return tool_output

            # If no tool calls, return a generic response
            self.storage.add_to_conversation(patient_id, "bot", "Thanks for messaging")
            return "Thanks for messaging"
        except Exception as e:
            return f"An error occurred @ai.py.interact: {e}"


    class BookAppointmentInput(BaseModel):
        time: str = Field(description="The time of the appointment in 'HH:MM' format (24-hour clock).")

    @tool(args_schema=BookAppointmentInput)
    def book_appointment(self, patient_id: str, time: str) -> str:
        if not self._validate_time(time):
            return "Invalid time format. Please use 'HH:MM' (24-hour clock)."

        return self.storage.add_to_appointments(patient_id, time)

    class GetReportInput(BaseModel):
        pass  # No arguments needed for this tool

    @tool(args_schema=GetReportInput)
    def get_report(self, patient_id: str) -> str:
        if patient_id not in self.storage.appointments:
            return f"No records found for patient {patient_id}."

        return f"Medical report for {patient_id}: Blood pressure - 120/80, Cholesterol - 190 mg/dL."

    class ReportEmergencyInput(BaseModel):
        details: str = Field(description="Description of the emergency.")

    @tool(args_schema=ReportEmergencyInput)
    def report_emergency(self, patient_id: str, details: str) -> str:
        if not details:
            return "Please provide details of the emergency."

        return self.storage.add_to_emergencies(patient_id, details)

    def _validate_time(self, time: str) -> bool:
        try:
            hours, minutes = map(int, time.split(':'))
            return 0 <= hours < 24 and 0 <= minutes < 60
        except ValueError:
            return False


async def test():
    ai = AI()
    res = await ai.interact("6969", "Who are you")
    print(res)
    res = await ai.interact("6969", "I am getting stomach pain, can you book an appointment for 10am tomorrow")
    print(res)
    res = await ai.interact("6969", "I have an emergency, can you book an emergency")
    print(res)
    res = await ai.interact("6969", "Can I get my medical reports")
    print(res)


if __name__ == "__main__":
    asyncio.run(test())