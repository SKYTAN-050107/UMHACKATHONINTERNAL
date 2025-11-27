import os
import tempfile
import uuid

import streamlit as st
from jamaibase import JamAI, protocol

# --- Configuration & Mock JAM AI Integration ---

# WARNING: In a production environment, NEVER expose API keys directly in client-side code.
# Use environment variables (st.secrets) and a secure backend for actual API calls.
JAMAI_API_KEY = "jamai_pat_23748a43d10e3651a516d2c0758aac37473bd392177a4eed"
JAMAI_PROJECT_ID = "proj_db0bde09a1a60ca9f4932bb7"
JAMAI_TABLE_ID = "FAQ"  # The ID of your JamAI Table

# Initialize JamAI client
# Note: The SDK uses 'token' instead of 'api_key' in newer versions, but we'll use what works.
# Based on inspection, it seems 'token' is the correct argument name for the init.
jamai_client = JamAI(token=JAMAI_API_KEY, project_id=JAMAI_PROJECT_ID)

def get_jam_ai_response(project_id, user_message, model_context):
    """
    Function to call the JAM AI API using the Table interface.
    This ensures we use the specific project/table configuration (models, prompts) you built in JamAI.
    """
    
    try:
        # We use the 'add_table_rows' method to send the user message to the table.
        # This triggers the AI column generation based on your table's configuration.
        
        # Retrieve session_id from Streamlit state if available
        session_id = st.session_state.get('session_id', 'unknown_session')
        
        # Determine User Role based on context or state
        user_role = "Public"
        if "staff" in model_context.lower():
            user_role = "Staff"
        
        # # Prepare row data with metadata for logging
        # row_data = {
        #     "User": user_message,
        #     "Session ID": session_id,
        #     "User Role": user_role
        # }
        
        # Debugging: Print data being sent
        print(f"DEBUG: Sending row data to JamAI: {user_message}")

        completion = jamai_client.table.add_table_rows(
            table_type="action",
            request=protocol.MultiRowAddRequest(
                table_id=JAMAI_TABLE_ID,
                data=[{"usr_input": user_message}],
                stream=False # We wait for the full response for simplicity in this Streamlit app
            )
        )
        
        # The response structure for add_table_rows (non-streaming) contains the rows.
        # We need to extract the AI's response from the output column.
        # Assuming the output column is named 'AI' based on standard JamAI chat tables.
        
        if completion.rows and len(completion.rows) > 0:
            # Get the first row's columns
            row_columns = completion.rows[0].columns
            
            # Debugging: Print received columns to console
            print(f"DEBUG: Received columns from JamAI: {list(row_columns.keys())}")
            
            # Find the 'AI' column or the last column which usually contains the response
            if "user_output" in row_columns:
                return f"User: {user_message}\n Action Table: {row_columns["user_output"].text}"
            else:
                # Fallback: return the text of the last column
                return list(row_columns.values())[-1].text
        else:
            return "Error: No response received from JamAI Table."

    except Exception as e:
        return f"Error connecting to JamAI: {str(e)}"


def get_jam_ai_response_admin(project_id, user_message, model_context):
    """
    Function to call the JAM AI API using the Table interface.
    This ensures we use the specific project/table configuration (models, prompts) you built in JamAI.
    """

    try:
        # We use the 'add_table_rows' method to send the user message to the table.
        # This triggers the AI column generation based on your table's configuration.

        # Retrieve session_id from Streamlit state if available
        session_id = st.session_state.get('session_id', 'unknown_session')

        # Determine User Role based on context or state
        user_role = "Public"
        if "staff" in model_context.lower():
            user_role = "Staff"

        # # Prepare row data with metadata for logging
        # row_data = {
        #     "User": user_message,
        #     "Session ID": session_id,
        #     "User Role": user_role
        # }

        # Debugging: Print data being sent
        print(f"DEBUG: Sending row data to JamAI: {user_message}")

        completion = jamai_client.table.add_table_rows(
            table_type="action",
            request=protocol.MultiRowAddRequest(
                table_id="staff FAQ",
                data=[{"usr_input": user_message}],
                stream=False  # We wait for the full response for simplicity in this Streamlit app
            )
        )

        # The response structure for add_table_rows (non-streaming) contains the rows.
        # We need to extract the AI's response from the output column.
        # Assuming the output column is named 'AI' based on standard JamAI chat tables.

        if completion.rows and len(completion.rows) > 0:
            # Get the first row's columns
            row_columns = completion.rows[0].columns

            # Debugging: Print received columns to console
            print(f"DEBUG: Received columns from JamAI: {list(row_columns.keys())}")

            # Find the 'AI' column or the last column which usually contains the response
            if "user_output" in row_columns:
                return f"User: {user_message}\n Action Table: {row_columns["user_output"].text}"
            else:
                # Fallback: return the text of the last column
                return list(row_columns.values())[-1].text
        else:
            return "Error: No response received from JamAI Table."

    except Exception as e:
        return f"Error connecting to JamAI: {str(e)}"


def post_chat_table(project_id, user_message, model_context, table_id):

    try:

        # Retrieve session_id from Streamlit state if available
        session_id = st.session_state.get('session_id', 'unknown_session')

        # Determine User Role based on context or state
        user_role = "Public"
        if "staff" in model_context.lower():
            user_role = "Staff"

        # # Prepare row data with metadata for logging
        # row_data = {
        #     "User": user_message,
        #     "Session ID": session_id,
        #     "User Role": user_role
        # }

        # Debugging: Print data being sent
        print(f"DEBUG chat: Sending row data to JamAI: {user_message}")

        completion = jamai_client.table.add_table_rows(
            table_type="chat",
            request=protocol.MultiRowAddRequest(
                table_id=table_id,
                data=[{"User": user_message}],
                stream=False  # We wait for the full response for simplicity in this Streamlit app
            )
        )

        # The response structure for add_table_rows (non-streaming) contains the rows.
        # We need to extract the AI's response from the output column.
        # Assuming the output column is named 'AI' based on standard JamAI chat tables.

        if completion.rows and len(completion.rows) > 0:
            # Get the first row's columns
            row_columns = completion.rows[0].columns

            # Debugging: Print received columns to console
            print(f"DEBUG: Received columns from JamAI: {list(row_columns.keys())}")

            # Find the 'AI' column or the last column which usually contains the response
            if "user_output" in row_columns:
                return f"User: {user_message}\n Action Table: {row_columns["user_output"].text}"
            else:
                # Fallback: return the text of the last column
                return list(row_columns.values())[-1].text
        else:
            return "Error: No response received from JamAI Table."

    except Exception as e:
        return f"Error connecting to JamAI: {str(e)}"

def embed_files_into_table(table_id: str, file):
    """
    Embeds a file uploaded from Streamlit into a JamAI table.
    'file' is a Streamlit UploadedFile.
    """

    # Extract the original filename (this includes the extension)
    filename = file.name

    # Create a temporary file with the same extension
    suffix = os.path.splitext(filename)[1]  # e.g. ".pdf", ".txt"

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(file.getbuffer())  # write the file contents
        tmp_path = tmp.name  # get the actual file path

    response = jamai_client.table.embed_file(
        file_path=tmp_path,
        table_id=table_id,
    )

    return response


def create_new_chat_table(table_id_src):
    new_table_id = f"chat_{str(uuid.uuid4())[:8]}"

    try:
        jamai_client.table.duplicate_table(
            table_type="chat",
            table_id_src=table_id_src,  # Your base agent ID
            table_id_dst=new_table_id,
            include_data=True,
            create_as_child=True
        )
        return new_table_id
    except Exception as e:
        print(f"Error creating new chat: {str(e)}")
        return None


def delete_table(table_type, table_id):

    try:
        jamai_client.table.delete_table(table_type=table_type, table_id=table_id)
        return True

    except Exception as e:
        print(f"Error deleting chat: {str(e)}")
        return False


def check_staff_login():
    """Checks if the user is logged in as staff and redirects if not."""
    if 'is_staff' not in st.session_state or not st.session_state['is_staff']:
        st.warning("Please log in as a staff member on the main page to access this portal.")
        # Streamlit multi-page structure handles the "redirection" by just showing the warning 
        # and stopping the rest of the page from executing.
        st.stop()