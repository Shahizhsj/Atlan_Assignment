import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any
from langchain_openai import OpenAI
class TicketClassifier:
    def __init__(self, api_key: str):
         self.llm = OpenAI(
            model="gpt-3.5-turbo",
            temperature=0.3,
            openai_api_key=api_key
        )
        self.classification_chain = self._create_chain()

    def _create_chain(self) -> LLMChain:
        prompt = PromptTemplate(
            input_variables=["ticket_text"],
            template=(
                "You are a ticket classification assistant.\n"
                "Given the user support ticket below, label it with:\n"
                "  - Topic: one of [How-to, Product, Connector, Feedback, Bug]\n"
                "  - Sentiment: one of [Frustrated, Curious, Angry, Neutral]\n"
                "  - Priority: one of [P0/High, P1/Medium, P2/Low]\n"
                
                "Ticket:\n---\n{ticket_text}\n---\n"
                "Return format:\n"
                "Topic: <topic>\nSentiment: <sentiment>\nPriority: <priority>\n"
            )
        )
        return LLMChain(llm=self.llm, prompt=prompt)

    def classify_ticket(self, ticket_input: Dict[str, str]) -> str:
        return self.classification_chain.apply([ticket_input])[0]["text"]

    def process_tickets(self, tickets: List[Dict[str, Any]], progress_callback=None) -> List[str]:
        inputs = [
            {"ticket_text": ticket["body"]}
            for ticket in tickets
        ]
        
        results = []
        with ThreadPoolExecutor(max_workers=1) as executor:
            futures = [executor.submit(self.classify_ticket, inp) for inp in inputs]
            for idx, future in enumerate(as_completed(futures)):
                results.append(future.result())
                if progress_callback:
                    progress_callback((idx + 1) / len(futures))
        
        return results

def load_tickets(file_path: str) -> List[Dict[str, Any]]:
    import json
    with open(file_path, 'r') as file:
        return json.load(file)
