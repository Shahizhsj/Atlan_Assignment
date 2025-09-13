from ticket_classifer import TicketClassifier
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from dotenv import load_dotenv
from typing import Dict, Any, Tuple, List
import os 

class SupportAgent:
    RAG_TOPICS = {"How-to", "Product", "Best practices", "API/SDK", "SSO"}
    
    def __init__(self, api_key: str):
        self.classifier = TicketClassifier(api_key)
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self.vectorstore = FAISS.load_local("faiss_store", self.embeddings, 
                                          allow_dangerous_deserialization=True)
        self.retriever = self.vectorstore.as_retriever()
        
        self.prompt = PromptTemplate(
            template="""You are a support ticket assistant for Atlan's data catalog platform.
            
Context Information:
{context}

User Question:
{question}

Instructions:
1. Provide a clear, direct answer addressing the user's question
2. Keep the response between 100-250 words
3. Focus on actionable solutions and steps when applicable
4. Use bullet points for steps or lists
5. Include relevant technical details but avoid jargon
6. If information is missing from context, acknowledge it

Response Format:
- Start with a direct answer to the question
- Break into short paragraphs or bullets
- End with a clear next step or conclusion

Answer:""",
            input_variables=["context", "question"]
        )
        
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.classifier.llm,
            chain_type="stuff",
            retriever=self.retriever,
            return_source_documents=True,
            chain_type_kwargs={
                "prompt": self.prompt,
                "verbose": True
            }
        )
    def process_ticket(self, ticket: Dict[str, Any]) -> Tuple[str, str, List[str]]:
        classification_input = {
            "ticket_text": ticket["body"]
        }
        
        classification_result = self.classifier.classify_ticket(classification_input)
        topic = classification_result.split('Topic: ')[1].split('\n')[0].strip()
        
        # Initialize sources as empty list
        sources = []
        
        # Generate response based on topic
        if topic in self.RAG_TOPICS:
            query = f"{ticket['body']}"
            try:
                rag_response = self.qa_chain({"query": query})
                response = rag_response['result']
                # Extract sources from source documents
                sources = [doc.metadata.get("source", None) or doc.metadata.get("url", None) for doc in rag_response['source_documents']]
            except Exception as e:
                response = f"Error generating response: {str(e)}"
        else:
            response = f"This ticket has been classified as a '{topic}' issue and routed to the appropriate team."
            
        return classification_result, response, sources

def create_ticket_from_input(body: str) -> Dict[str, Any]:
    return {
        "body": body
    }
