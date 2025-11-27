import uuid
import streamlit as st
from utils import create_new_chat_table, delete_table, check_staff_login, get_jam_ai_response_admin, post_chat_table, embed_files_into_table, JAMAI_PROJECT_ID

# --- Security Check ---
check_staff_login()

st.title("🧑‍⚕️ Staff Main Portal")
st.info("Welcome, Staff! Your access is confirmed. Use the specialized chatbot below.")

st.subheader("🤖 Staff Management Chatbot")
st.write("This chatbot assists with internal staff management queries (e.g., HR, scheduling, policy).")

# --- Initialize session state ---
if "staff_chat_sessions" not in st.session_state:
    st.session_state["staff_chat_sessions"] = []

if "active_staff_chat_id" not in st.session_state:
    st.session_state["active_staff_chat_id"] = None

if "uploaded_files" not in st.session_state:
    st.session_state["uploaded_files"] = []

if "show_file_uploader" not in st.session_state:
    st.session_state["show_file_uploader"] = False


# --- Functions ---
def toggle_uploader():
    st.session_state["show_file_uploader"] = not st.session_state["show_file_uploader"]

def create_new_chat(title=None):
    chat_id = str(uuid.uuid4())
    if title is None:
        title = f"New Staff Chat"
    new_chat = {
        "id": chat_id,
        "table_id": create_new_chat_table("adminguy"),
        "title": title,
        "messages": [{"role": "ai", "content": "Hello Staff! How can I help you with your management queries today?"}]
    }
    st.session_state['staff_chat_sessions'].append(new_chat)
    st.session_state['active_staff_chat_id'] = chat_id

def delete_chat(chat_id):
    chat_to_delete = next((c for c in st.session_state['staff_chat_sessions'] if c['id'] == chat_id), None)
    if chat_to_delete:
        # Delete backend table
        delete_table("chat", chat_to_delete['table_id'])

        # Remove from frontend
        st.session_state['staff_chat_sessions'] = [c for c in st.session_state['staff_chat_sessions'] if c['id'] != chat_id]

        # Update active chat
        if st.session_state.get('active_staff_chat_id') == chat_id:
            st.session_state['active_staff_chat_id'] = st.session_state['staff_chat_sessions'][0]['id'] if st.session_state[
                'staff_chat_sessions'] else None


# --- Sidebar: Chat Sessions ---
st.sidebar.title("📋 Staff Chat Sessions")
if st.sidebar.button("➕ New Conversation"):
    create_new_chat()

for chat in st.session_state['staff_chat_sessions']:
    col1, col2 = st.sidebar.columns([3, 1])
    with col1:
        if st.button(chat['title'], key=f"select_{chat['id']}"):
            st.session_state['active_staff_chat_id'] = chat['id']
    with col2:
        if st.button("🗑️", key=f"delete_{chat['id']}"):
            delete_chat(chat['id'])
            st.rerun()  # Refresh sidebar

# --- Active Chat Selection ---
active_chat = next(
    (c for c in st.session_state['staff_chat_sessions'] if c['id'] == st.session_state.get('active_staff_chat_id')),
    None
)

if not active_chat and st.session_state['staff_chat_sessions']:
    active_chat = st.session_state['staff_chat_sessions'][0]
    st.session_state['active_staff_chat_id'] = active_chat['id']

# --- Display Active Chat ---
if active_chat:
    st.title(active_chat['title'])

    # Display chat messages
    for message in active_chat['messages']:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # User input
    if user_input := st.chat_input("Ask a question about staff handling..."):
        active_chat['messages'].append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        # Get AI response
        with st.chat_message("ai"):
            with st.spinner('Contacting JAM AI...'):
                action_ai_response = get_jam_ai_response_admin(JAMAI_PROJECT_ID, user_input, "Staff Management")
                ai_response = post_chat_table(JAMAI_PROJECT_ID, action_ai_response, "FAQ Chatbot",
                                              active_chat["table_id"])
                st.markdown(ai_response)

            active_chat['messages'].append({"role": "ai", "content": ai_response})
            st.rerun()


# --- File Upload Section ---
st.markdown("---")
col1, col2 = st.columns([1, 1])

with col1:
    st.button("📎 Attach File", on_click=toggle_uploader)

with col2:
    st.page_link("app.py", label="🏠 Back to Main Page (Logout)", icon="🚪")


KNOWLEDGE_TABLES = {
    "Disease": "Disease",
    "Clinic Info": "Clinic Info",
    "Covid-19": "staff_guidelines",
    "WHO Data": "medical_refs",
    "Vaccination": "Vaccination",
}

if st.session_state["show_file_uploader"]:
    selected_table = st.selectbox(
        "Select the knowledge table to upload into:",
        list(KNOWLEDGE_TABLES.keys())
    )

    table_id = KNOWLEDGE_TABLES[selected_table]

    uploaded_files = st.file_uploader(
        "Upload files (PDF, DOCX, TXT, CSV, Markdown, HTML)",
        type=["pdf", "docx", "txt", "csv", "md", "html"],
        accept_multiple_files=True
    )
    if uploaded_files:
        for file in uploaded_files:
            st.session_state["uploaded_files"].append(file)
            st.success(f"File '{file.name}' uploaded successfully!")
            embed_files_into_table(table_id, file)
