import streamlit as st
from utils import check_staff_login, get_jam_ai_response_admin, post_chat_table, embed_files_into_table, JAMAI_PROJECT_ID

# --- Security Check ---
check_staff_login()

st.title("🧑‍⚕️ Staff Main Portal")
st.info("Welcome, Staff! Your access is confirmed. Use the specialized chatbot below.")

st.subheader("🤖 Staff Management Chatbot")
st.write("This chatbot assists with internal staff management queries (e.g., HR, scheduling, policy).")

# --- Initialize session state ---
if "staff_messages" not in st.session_state:
    st.session_state["staff_messages"] = []

if "uploaded_files" not in st.session_state:
    st.session_state["uploaded_files"] = []

if "show_file_uploader" not in st.session_state:
    st.session_state["show_file_uploader"] = False


# --- Toggle uploader ---
def toggle_uploader():
    st.session_state["show_file_uploader"] = not st.session_state["show_file_uploader"]


# --- Display chat history ---
for message in st.session_state["staff_messages"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- User input ---
if user_input := st.chat_input("Ask a question about staff handling..."):
    # Add user message to history
    st.session_state["staff_messages"].append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Get AI response
    with st.chat_message("ai"):
        with st.spinner('Contacting JAM AI...'):
            action_ai_response = get_jam_ai_response_admin(JAMAI_PROJECT_ID, user_input, "Staff Management")
            ai_response = post_chat_table(JAMAI_PROJECT_ID, action_ai_response, "FAQ Chatbot", "admin")
            st.markdown(ai_response)

        # Add AI response to history
        st.session_state["staff_messages"].append({"role": "ai", "content": ai_response})
        st.rerun()

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

# --- File uploader (hidden until button clicked) ---
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
    if uploaded_files is not None:
        for file in uploaded_files:
            print(file.type)
            st.session_state["uploaded_files"].append(file)
            st.success(f"File '{file.name}' uploaded successfully!")
            embed_files_into_table(table_id, file)
        # TODO: send file to backend for embedding in Knowledge Table
        # backend_embed_file(uploaded_file, table_id="clinic_knowledge")


