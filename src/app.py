import os
import streamlit as st 
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser
load_dotenv()

if "chat_history" not in st.session_state:
  st.session_state.chat_history = []


st.set_page_config(page_title='Streaming Bot', page_icon="🤖")

st.title("Streaming Bot")
st.markdown("""
<style>
.chat-message {
    display: flex;
    justify-content: flex-start;
    margin-bottom: 10px;
}
.chat-message.user {
    justify-content: flex-end;
}
.chat-message .message-content {
    max-width: 60%;
    padding: 10px;
    border-radius: 10px;
}
.chat-message.user .message-content {
    background-color: #DCF8C6;
}
.chat-message.ai .message-content {
    background-color: #ECECEC;
}
</style>
""", unsafe_allow_html=True)

# Add a button to reset chat history
if st.button("Start New Chat"):
    st.session_state.chat_history = []

# Get response
def get_response(query, chat_history):
  template = """
  You are a helpful assistant. Answer the following questions considering the history of the conversation:

  Chat history : {chat_history}

  User question : {user_question}
  """
  
  chat_history_str = "\n".join(
        [f"Human: {msg.content}" 
         if isinstance(msg, HumanMessage) 
         else f"AI: {msg.content}" for msg in chat_history]
    )
  
  prompt = ChatPromptTemplate.from_template(template)
  llm = ChatGroq(
            api_key=os.getenv("GROQ_API_KEY"),
            model="llama3-70b-8192"
            # model="gemma-7b-it",
            # model="mixtral-8x7b-32768"
  )
  chain = prompt | llm | StrOutputParser()


  return chain.stream({
    "chat_history" : chat_history_str,
    "user_question" : query
  })


# Conversation
for message in st.session_state.chat_history:
    if isinstance(message, HumanMessage):
        with st.chat_message("Human"):
            st.markdown(f'<div class="chat-message user"><div class="message-content">{message.content}</div></div>', unsafe_allow_html=True)
    else:
        with st.chat_message("AI"):
            st.markdown(f'<div class="chat-message ai"><div class="message-content">{message.content}</div></div>', unsafe_allow_html=True)



# user input
user_query = st.chat_input("Your message")
if user_query is not None and user_query != "":
  st.session_state.chat_history.append(HumanMessage(user_query))

  with st.chat_message("Human"):
    st.markdown(f'<div class="chat-message user"><div class="message-content">{user_query}</div></div>', unsafe_allow_html=True)

  with st.chat_message("AI"):
     
    ai_response = st.write_stream(get_response(user_query, st.session_state.chat_history))

  st.session_state.chat_history.append(AIMessage(ai_response))
