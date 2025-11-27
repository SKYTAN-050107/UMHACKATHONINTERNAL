import uuid

import streamlit as st
from utils import delete_table, create_new_chat_table, get_jam_ai_response, post_chat_table, JAMAI_PROJECT_ID

if 'chat_sessions' not in st.session_state:
    # Each session is a dict with id, title, messages
    st.session_state['chat_sessions'] = []

# Function to create a new chat session
def create_new_chat(title=None):
    chat_id = str(uuid.uuid4())
    if title is None:
        title = f"New Chat"

    chat_table_id = create_new_chat_table("niceguy")

    new_chat = {
        "id": chat_id,
        "table_id": chat_table_id,
        "title": title,
        "messages": [{"role": "ai", "content": "Hello! How can I help you today?"}]
    }

    st.session_state['chat_sessions'].append(new_chat)
    st.session_state['active_chat_id'] = chat_id

def delete_chat(chat_id):
    chat_to_delete = next((c for c in st.session_state['chat_sessions'] if c['id'] == chat_id), None)
    if chat_to_delete:
        # Delete backend table
        delete_table("chat", chat_to_delete['table_id'])

        # Remove from frontend
        st.session_state['chat_sessions'] = [c for c in st.session_state['chat_sessions'] if c['id'] != chat_id]

        # Update active chat
        if st.session_state.get('active_chat_id') == chat_id:
            st.session_state['active_chat_id'] = st.session_state['chat_sessions'][0]['id'] if st.session_state[
                'chat_sessions'] else None


st.title("📚 Clinic FAQs Chatbot")
st.write("Ask questions about **clinic hours, appointments, or services**.")
st.caption("This chatbot is specialized to answer only clinic-specific administrative questions.")

st.sidebar.title("📋 Chat Sessions")
if st.sidebar.button("➕ New Conversation"):
    create_new_chat()

for chat in st.session_state['chat_sessions']:
    col1, col2 = st.sidebar.columns([3, 1])
    with col1:
        if st.button(chat['title'], key=f"select_{chat['id']}"):
            st.session_state['active_chat_id'] = chat['id']
    with col2:
        if st.button("🗑️", key=f"delete_{chat['id']}"):
            delete_chat(chat['id'])
            st.rerun()  # Refresh sidebar

active_chat = next((c for c in st.session_state['chat_sessions']
                    if c['id'] == st.session_state.get('active_chat_id')), None)

if active_chat:
    st.title(active_chat['title'])

    # Display messages
    for message in active_chat['messages']:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Input
    if user_input := st.chat_input("Type a message..."):
        active_chat['messages'].append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("ai"):
            with st.spinner("Thinking..."):
                ai_response = get_jam_ai_response(JAMAI_PROJECT_ID, user_input, "FAQ Chatbot")
                ai_response = post_chat_table(JAMAI_PROJECT_ID, ai_response, "FAQ Chatbot", active_chat["table_id"])
                st.markdown(ai_response)

            active_chat['messages'].append({"role": "ai", "content": ai_response})
            st.rerun()

st.markdown("---")
st.page_link("app.py", label=" Back to Main Menu", icon="🏠")

# --- FAQ Chat Interface ---

# Display chat history
# for message in st.session_state["faq_messages"]:
#     with st.chat_message(message["role"]):
#         st.markdown(message["content"])
#
# # User input
# if user_input := st.chat_input("Ask a question about the clinic..."):
#     st.session_state["faq_messages"].append({"role": "user", "content": user_input})
#     with st.chat_message("user"):
#         st.markdown(user_input)
#
#     # Get AI response
#     with st.chat_message("ai"):
#         with st.spinner('Contacting JAM AI...'):
#             # Call shared mock AI function with the 'FAQ Chatbot' context
#             action_ai_response = get_jam_ai_response(JAMAI_PROJECT_ID, user_input, "FAQ Chatbot")
#             ai_response = post_chat_table(JAMAI_PROJECT_ID, action_ai_response, "FAQ Chatbot", "test")
#             st.markdown(ai_response)
#
#         st.session_state["faq_messages"].append({"role": "ai", "content": ai_response})
#         st.rerun() # Rerun to update chat history instantly
#
# st.markdown("---")
# st.page_link("app.py", label="🏠 Back to Main Menu", icon="🏠")