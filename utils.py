import streamlit as st
import requests
from jamaibase import JamAI, protocol

# --- Configuration & Mock JAM AI Integration ---

# WARNING: In a production environment, NEVER expose API keys directly in client-side code.
# Use environment variables (st.secrets) and a secure backend for actual API calls.
JAMAI_API_KEY = "jamai_pat_68b1c83ebdb2469ecc6552427a803fb0ff9e96b85b91a25c"
JAMAI_PROJECT_ID = "proj_56f49eb1a5c292ee70c39a58"
JAMAI_TABLE_ID = "Multilingual_Frontline_Agent" # The ID of your JamAI Table

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
        
        # Prepare row data with metadata for logging
        row_data = {
            "User": user_message,
            "Session ID": session_id,
            "User Role": user_role
        }
        
        # Debugging: Print data being sent
        print(f"DEBUG: Sending row data to JamAI: {row_data}")

        completion = jamai_client.table.add_table_rows(
            table_type="chat",
            request=protocol.MultiRowAddRequest(
                table_id=JAMAI_TABLE_ID,
                data=[row_data], 
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
            if "AI" in row_columns:
                return row_columns["AI"].text
            else:
                # Fallback: return the text of the last column
                return list(row_columns.values())[-1].text
        else:
            return "Error: No response received from JamAI Table."

    except Exception as e:
        return f"Error connecting to JamAI: {str(e)}"

def check_staff_login():
    """Checks if the user is logged in as staff and redirects if not."""
    if 'is_staff' not in st.session_state or not st.session_state['is_staff']:
        st.warning("Please log in as a staff member on the main page to access this portal.")
        # Streamlit multi-page structure handles the "redirection" by just showing the warning 
        # and stopping the rest of the page from executing.
        st.stop()