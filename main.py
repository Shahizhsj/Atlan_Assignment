import streamlit as st
import os
from dotenv import load_dotenv
import time
from ticket_classifer import TicketClassifier, load_tickets
from ai_agent import SupportAgent, create_ticket_from_input

class StreamlitUI:
    @staticmethod
    def load_css():
        st.markdown("""
            <style> 
            .main { background-color: #f5f5f5; }
            .stButton>button {
                background-color: #4CAF50;
                color: white;
                padding: 0.5rem 1rem;
                border-radius: 5px;
                border: none;
            }
            .stProgress .st-bo { background-color: #4CAF50; }
            .ticket-box {
                background-color: white;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                margin: 10px 0;
            }
            .classification-box {
                display: flex;
                justify-content: space-between;
                margin-top: 10px;
            }
            .classification-item {
                background-color: #f8f9fa;
                padding: 10px 15px;
                border-radius: 5px;
                border-left: 4px solid;
                flex: 1;
                margin: 0 5px;
                text-align: center;
            }
            .chat-message {
                padding: 1.5rem;
                border-radius: 0.5rem;
                margin-bottom: 1rem;
                display: flex;
                flex-direction: column;
            }
            .chat-message.user {
                background-color: #e3f2fd;
            }
            .chat-message.bot {
                background-color: #f5f5f5;
            }
            .topic { border-left-color: #2196F3; }
            .sentiment { border-left-color: #FF9800; }
            .priority { border-left-color: #F44336; }
                    
            .response-box {
                background-color: #e8f5e9;
                padding: 15px;
                border-radius: 5px;
                margin: 10px 0;
            }
            .sources-box {
                background-color: #fff3e0;
                padding: 15px;
                border-radius: 5px;
                margin: 10px 0;
            }
            .sources-box ul {
                margin: 5px 0;
                padding-left: 20px;
            }
            .sources-box li {
                margin: 5px 0;
            }
            # Add to existing CSS in StreamlitUI class
            .source-links {
                display: flex;
                flex-direction: column;
                gap: 8px;
                margin-top: 10px;
            }
            .source-link {
                color: #1976D2;
                text-decoration: none;
                padding: 5px 10px;
                border-radius: 4px;
                background-color: #fff;
                transition: background-color 0.2s;
            }
            .source-link:hover {
                background-color: #e3f2fd;
            }
            </style>
            """, unsafe_allow_html=True)

    def display_ticket_result(self, ticket, result):
        topic = result.split('Topic: ')[1].split('\n')[0].strip()
        sentiment = result.split('Sentiment: ')[1].split('\n')[0].strip()
        priority = result.split('Priority: ')[1].strip()

        st.markdown(f"""
        <div class="ticket-box">
            <h4 style="color: #1976D2;">📄 Ticket {ticket['id']}</h4>
            <p><strong>Subject:</strong> {ticket['subject']}</p>
            <p><strong>Body:</strong> {ticket['body']}</p>
            <hr>
            <div class="classification-box">
                <div class="classification-item topic">
                    <div style="font-size: 0.8em; color: #666;">Topic</div>
                    <div style="font-weight: bold; color: #2196F3;">{topic}</div>
                </div>
                <div class="classification-item sentiment">
                    <div style="font-size: 0.8em; color: #666;">Sentiment</div>
                    <div style="font-weight: bold; color: #FF9800;">{sentiment}</div>
                </div>
                <div class="classification-item priority">
                    <div style="font-size: 0.8em; color: #666;">Priority</div>
                    <div style="font-weight: bold; color: #F44336;">{priority}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

def classification_tab(ui: StreamlitUI, api_key: str):
    try:
        tickets = load_tickets('tickets_data.json')
        st.sidebar.success(f"✅ Loaded {len(tickets)} tickets from JSON file")
    except FileNotFoundError:
        st.error("❌ tickets.json file not found in the current directory")
        return
    except Exception as e:
        st.error(f"❌ Error loading tickets: {str(e)}")
        return

    classifier = TicketClassifier(api_key)
    
    st.markdown("### 📝 Ticket Classification")
    start_time = time.time()
    
    with st.spinner('Processing tickets...'):
        progress_bar = st.progress(0)
        results = classifier.process_tickets(
            tickets, 
            progress_callback=lambda p: progress_bar.progress(p)
        )

    # Store results in session state
    st.session_state.classification_results = list(zip(tickets, results))

    st.markdown("### 🔍 Classification Results")
    for ticket, result in st.session_state.classification_results:
        ui.display_ticket_result(ticket, result)

    processing_time = f"{time.time() - start_time:.1f}s"
    
    st.markdown("---")
    st.markdown("### 📊 Overall Statistics")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Total Tickets", value=len(tickets))
    with col2:
        st.metric(label="Processed", value=len(results))
    with col3:
        st.metric(label="Processing Time", value=processing_time)

# Update the chatbot_tab function:

def chatbot_tab(api_key: str):
    if "agent" not in st.session_state:
        st.session_state.agent = SupportAgent(api_key)
    
    with st.form(key="chat_form"):
        message = st.text_area("Your Ticket...", key="message")
        submit = st.form_submit_button("Send")
        
        if submit and message:
            st.markdown(f"""
                <div class="chat-message user">
                    <p>{message}</p>
                </div>
                """, unsafe_allow_html=True)
            
            with st.spinner("Processing..."):
                ticket = create_ticket_from_input(message)
                classification, response, sources = st.session_state.agent.process_ticket(ticket)
                
                # Format the classification result nicely
                topic = classification.split('Topic: ')[1].split('\n')[0].strip()
                sentiment = classification.split('Sentiment: ')[1].split('\n')[0].strip()
                priority = classification.split('Priority: ')[1].strip()

                st.markdown("""
                    <div class="chat-message bot">
                        <div class="classification-box">
                            <div class="classification-item topic">
                                <div style="font-size: 0.8em; color: #666;">Topic</div>
                                <div style="font-weight: bold; color: #2196F3;">{}</div>
                            </div>
                            <div class="classification-item sentiment">
                                <div style="font-size: 0.8em; color: #666;">Sentiment</div>
                                <div style="font-weight: bold; color: #FF9800;">{}</div>
                            </div>
                            <div class="classification-item priority">
                                <div style="font-size: 0.8em; color: #666;">Priority</div>
                                <div style="font-weight: bold; color: #F44336;">{}</div>
                            </div>
                        </div>
                        <div class="response-box">
                            <strong>Response:</strong><br>
                            {}
                        </div>
                    """.format(topic, sentiment, priority, response), 
                    unsafe_allow_html=True
                )

                # Add sources if available
                                # Add sources if available
                if sources:
                    st.markdown("""
                        <div class='sources-box'>
                            <strong>Reference Links:</strong>
                            <div class="source-links">
                    """, unsafe_allow_html=True)
                    
                    for source in sources:
                        st.markdown(f"""
                            <a href="{source}" target="_blank" class="source-link">
                                📄 {source}
                            </a>
                        """, unsafe_allow_html=True)
                    
                    st.markdown("</div></div></div>", unsafe_allow_html=True)
def main():
    load_dotenv()
    
    st.set_page_config(
        page_title="Support Ticket System",
        page_icon="🎫",
        layout="wide"
    )

    # Initialize session state for first load
    if 'first_load' not in st.session_state:
        st.session_state.first_load = True
        st.session_state.classification_results = None

    ui = StreamlitUI()
    ui.load_css()

    st.markdown("<h1 style='text-align: center; color: #2E7D32;'>🎫 Support Ticket System</h1>", 
                unsafe_allow_html=True)

    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        st.error("❌ API Key not found in environment variables. Please check your .env file.")
        return

    # Create tabs
    tab1, tab2 = st.tabs(["📊 Bulk Classification", "🤖 Support Chatbot"])
    
    with tab1:
        if st.session_state.first_load:
            # Run classification on first load
            classification_tab(ui, api_key)
            st.session_state.first_load = False
        else:
            # Display cached results on subsequent runs
            if st.session_state.classification_results:
                for ticket, result in st.session_state.classification_results:
                    ui.display_ticket_result(ticket, result)
    
    with tab2:
        chatbot_tab(api_key)
if __name__ == "__main__":
    main()