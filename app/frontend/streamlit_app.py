import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import json
import os
from datetime import datetime
import time

# API base URL - change this to match your FastAPI server
API_BASE_URL = "http://localhost:8000/api"

# Page configuration
st.set_page_config(
    page_title="Sales Call Analyzer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #0D47A1;
        margin-bottom: 0.5rem;
    }
    .metric-card {
        background-color: #f5f5f5;
        border-radius: 0.5rem;
        padding: 1rem;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    }
    .insight-item {
        background-color: #e3f2fd;
        border-left: 4px solid #1E88E5;
        padding: 0.5rem 1rem;
        margin-bottom: 0.5rem;
        border-radius: 0 0.25rem 0.25rem 0;
    }
    .positive {
        color: #2E7D32;
    }
    .negative {
        color: #C62828;
    }
    .neutral {
        color: #616161;
    }
    .high {
        color: #2E7D32;
    }
    .medium {
        color: #F9A825;
    }
    .low {
        color: #C62828;
    }
</style>
""", unsafe_allow_html=True)

# Helper functions
def fetch_calls():
    """Fetch all call records from the API"""
    try:
        response = requests.get(f"{API_BASE_URL}/calls")
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error fetching calls: {response.status_code}")
            return []
    except Exception as e:
        st.error(f"Error connecting to API: {e}")
        return []

def fetch_call_analysis(call_id):
    """Fetch analysis for a specific call"""
    try:
        response = requests.get(f"{API_BASE_URL}/calls/{call_id}")
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error fetching call analysis: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Error connecting to API: {e}")
        return None

def upload_file(file, auto_process=True):
    """Upload an audio file to the API"""
    try:
        files = {"file": file}
        params = {"auto_process": auto_process}
        response = requests.post(f"{API_BASE_URL}/upload", files=files, params=params)
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Upload failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"Error uploading file: {e}")
        return None

def start_processing(call_id):
    """Start processing a call"""
    try:
        response = requests.post(f"{API_BASE_URL}/process/{call_id}")
        if response.status_code == 200:
            return True
        else:
            st.error(f"Processing failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        st.error(f"Error starting processing: {e}")
        return False

def format_timestamp(timestamp):
    """Format timestamp for display"""
    try:
        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return timestamp

def display_call_list(calls):
    """Display a list of calls with key information"""
    if not calls:
        st.info("No calls found. Upload a call recording to get started.")
        return
    
    # Create a dataframe for display
    call_data = []
    for call in calls:
        call_data.append({
            "Call ID": call["call_id"],
            "Filename": call["filename"],
            "Uploaded": format_timestamp(call["upload_date"]),
            "Duration": f"{call['duration']:.1f}s" if call["duration"] else "Unknown",
            "Status": "Processed" if call["processed"] else "Pending",
        })
    
    df = pd.DataFrame(call_data)
    st.dataframe(df, use_container_width=True)

def display_sentiment_gauge(score):
    """Display a gauge chart for sentiment"""
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = score,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Sentiment Score"},
        gauge = {
            'axis': {'range': [-1, 1]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [-1, -0.5], 'color': "firebrick"},
                {'range': [-0.5, 0.5], 'color': "gold"},
                {'range': [0.5, 1], 'color': "forestgreen"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': score
            }
        }
    ))
    
    fig.update_layout(height=250)
    return fig

def display_satisfaction_gauge(score):
    """Display a gauge chart for customer satisfaction"""
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = score,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Customer Satisfaction"},
        gauge = {
            'axis': {'range': [1, 10]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [1, 4], 'color': "firebrick"},
                {'range': [4, 7], 'color': "gold"},
                {'range': [7, 10], 'color': "forestgreen"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': score
            }
        }
    ))
    
    fig.update_layout(height=250)
    return fig

def display_engagement_gauge(score):
    """Display a gauge chart for engagement"""
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = score,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Engagement Score"},
        number = {'suffix': "%"},
        gauge = {
            'axis': {'range': [0, 1]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 0.3], 'color': "firebrick"},
                {'range': [0.3, 0.7], 'color': "gold"},
                {'range': [0.7, 1], 'color': "forestgreen"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': score
            }
        }
    ))
    
    fig.update_layout(height=250)
    return fig

def display_conversion_gauge(score):
    """Display a gauge chart for conversion probability"""
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = score * 100,  # Convert to percentage
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Conversion Probability"},
        number = {'suffix': "%"},
        gauge = {
            'axis': {'range': [0, 100]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 40], 'color': "firebrick"},
                {'range': [40, 70], 'color': "gold"},
                {'range': [70, 100], 'color': "forestgreen"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': score * 100
            }
        }
    ))
    
    fig.update_layout(height=250)
    return fig

def display_objections_chart(objections):
    """Display a bar chart of objections by category"""
    if not objections:
        return None
    
    # Group objections by category
    categories = {}
    for obj in objections:
        cat = obj["category"]
        if cat in categories:
            categories[cat] += 1
        else:
            categories[cat] = 1
    
    # Create dataframe
    df = pd.DataFrame({
        "Category": list(categories.keys()),
        "Count": list(categories.values())
    })
    
    # Create bar chart
    fig = px.bar(
        df, 
        x="Category", 
        y="Count", 
        title="Objections by Category",
        color="Category"
    )
    
    fig.update_layout(height=300)
    return fig

def display_call_analysis(analysis):
    """Display the complete analysis for a call"""
    if not analysis:
        st.warning("No analysis data available for this call.")
        return
    
    call = analysis["call"]
    transcription = analysis["transcription"]
    analysis_data = analysis["analysis"]
    
    # Header with call information
    st.markdown(f"<h1 class='main-header'>Call Analysis: {call['filename']}</h1>", unsafe_allow_html=True)
    
    # Call metadata in cards
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.markdown(f"**Upload Date:** {format_timestamp(call['upload_date'])}")
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.markdown(f"**Duration:** {call['duration']:.1f} seconds")
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col3:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.markdown(f"**Processing Time:** {transcription['processing_time']:.1f} seconds")
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Check if the transcription is valid
    if "is_valid" in transcription and not transcription["is_valid"]:
        st.error(f"⚠️ {transcription['validation_message']}")
        st.warning("Analysis was not performed because the audio does not contain valid speech content. Please upload a different audio file with speech content.")
        
        # Show the transcript anyway
        with st.expander("View Transcript"):
            st.text_area("Raw Transcript", transcription["transcript"], height=100)
        
        return
    
    # Key metrics visualization
    st.markdown("<h2 class='sub-header'>Key Metrics</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        # Sentiment and satisfaction
        st.plotly_chart(display_sentiment_gauge(analysis_data["sentiment_score"]), use_container_width=True)
        st.markdown(f"**Sentiment Level:** <span class='{analysis_data['sentiment_level'].lower()}'>{analysis_data['sentiment_level'].upper()}</span>", unsafe_allow_html=True)
    
    with col2:
        # Customer satisfaction
        st.plotly_chart(display_satisfaction_gauge(analysis_data["customer_satisfaction_score"]), use_container_width=True)
    
    col1, col2 = st.columns(2)
    with col1:
        # Engagement
        st.plotly_chart(display_engagement_gauge(analysis_data["engagement_score"]), use_container_width=True)
        st.markdown(f"**Engagement Level:** <span class='{analysis_data['engagement_level'].lower()}'>{analysis_data['engagement_level'].upper()}</span>", unsafe_allow_html=True)
    
    with col2:
        # Conversion probability
        st.plotly_chart(display_conversion_gauge(analysis_data["conversion_probability_score"]), use_container_width=True)
        st.markdown(f"**Conversion Probability:** <span class='{analysis_data['conversion_probability_level'].lower()}'>{analysis_data['conversion_probability_level'].upper()}</span>", unsafe_allow_html=True)
    
    # Objections section
    st.markdown("<h2 class='sub-header'>Objections</h2>", unsafe_allow_html=True)
    
    if analysis_data["objections"]:
        # Display objections chart
        objections_chart = display_objections_chart(analysis_data["objections"])
        if objections_chart:
            st.plotly_chart(objections_chart, use_container_width=True)
        
        # Display objection details
        for obj in analysis_data["objections"]:
            st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
            st.markdown(f"**Category:** {obj['category'].upper()}")
            st.markdown(f"**Confidence:** {obj['confidence']:.2f}")
            st.markdown(f"**Text:** {obj['text']}")
            st.markdown("</div>", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
    else:
        st.info("No objections detected in this call.")
    
    # Key insights
    st.markdown("<h2 class='sub-header'>Key Insights</h2>", unsafe_allow_html=True)
    
    if analysis_data["key_insights"]:
        for insight in analysis_data["key_insights"]:
            st.markdown(f"<div class='insight-item'>{insight}</div>", unsafe_allow_html=True)
    else:
        st.info("No key insights available for this call.")
    
    # Transcript section
    with st.expander("View Transcript"):
        st.text_area("Full Transcript", transcription["transcript"], height=300)
    
        if transcription["processed_transcript"]:
            st.markdown("### Processed Transcript (Fillers Removed)")
            st.text_area("Processed Transcript", transcription["processed_transcript"], height=300)

# Main app structure
def main():
    # Sidebar
    st.sidebar.image("https://img.icons8.com/color/96/000000/microphone--v1.png", width=100)
    st.sidebar.title("Sales Call Analyzer")
    
    # Upload section in sidebar
    st.sidebar.header("Upload New Call")
    uploaded_file = st.sidebar.file_uploader("Choose an audio file", type=["mp3", "wav", "flac", "m4a"])
    
    auto_process = st.sidebar.checkbox("Auto-process after upload", value=True)
    
    if uploaded_file and st.sidebar.button("Upload"):
        with st.sidebar:
            with st.spinner("Uploading file..."):
                result = upload_file(uploaded_file, auto_process)
                if result:
                    st.success(f"File uploaded successfully: {result['filename']}")
                    if auto_process:
                        st.info("Processing started. This may take a few minutes.")
    
    # Navigation in sidebar
    st.sidebar.header("Navigation")
    page = st.sidebar.radio("Go to", ["Dashboard", "Call List", "About"])
    
    # Fetch all calls for any page
    calls = fetch_calls()
    
    # Main content based on selected page
    if page == "Dashboard":
        st.markdown("<h1 class='main-header'>Sales Call Analysis Dashboard</h1>", unsafe_allow_html=True)
        
        # Call selection
        if calls:
            call_options = {f"{call['filename']} ({format_timestamp(call['upload_date'])})": call["call_id"] for call in calls if call["processed"]}
            
            if call_options:
                selected_call = st.selectbox("Select a call to analyze:", list(call_options.keys()))
                selected_call_id = call_options[selected_call]
                
                # Fetch and display analysis for selected call
                with st.spinner("Loading analysis..."):
                    analysis = fetch_call_analysis(selected_call_id)
                    display_call_analysis(analysis)
            else:
                st.info("No processed calls available. Please upload and process a call recording.")
        else:
            st.info("No calls found. Upload a call recording to get started.")
    
    elif page == "Call List":
        st.markdown("<h1 class='main-header'>Call Recordings</h1>", unsafe_allow_html=True)
        
        # Display list of calls
        display_call_list(calls)
        
        # Allow processing of pending calls
        if calls:
            pending_calls = [call for call in calls if not call["processed"]]
            if pending_calls:
                st.markdown("<h2 class='sub-header'>Process Pending Calls</h2>", unsafe_allow_html=True)
        
                call_options = {f"{call['filename']} ({format_timestamp(call['upload_date'])})": call["call_id"] for call in pending_calls}
                selected_call = st.selectbox("Select a call to process:", list(call_options.keys()))
                selected_call_id = call_options[selected_call]
                
                if st.button("Start Processing"):
                    with st.spinner("Starting processing..."):
                        if start_processing(selected_call_id):
                            st.success("Processing started. This may take a few minutes.")
    
    elif page == "About":
        st.markdown("<h1 class='main-header'>About Sales Call Analyzer</h1>", unsafe_allow_html=True)
        
        st.markdown("""
        The **Sales Call Analysis System** is designed to help sales teams improve their performance by providing 
        insights from sales call recordings. The system uses advanced AI techniques to analyze:
        
        - **Sentiment**: Detect the emotional tone of the conversation
        - **Engagement**: Measure customer's level of interest
        - **Objections**: Identify customer concerns or hesitations
        - **Conversion Probability**: Estimate likelihood of closing the sale
        
        ### How It Works
        
        1. **Upload** your sales call recording
        2. The system **transcribes** the audio to text
        3. AI algorithms **analyze** the transcript
        4. View **insights** and recommendations
        
        ### Benefits
        
        - Identify strengths and weaknesses in sales conversations
        - Track common objections and concerns
        - Focus on high-value leads
        - Measure performance metrics objectively
        
        ### Supported File Formats
        
        Currently supports MP3, WAV, FLAC, and M4A audio files.
        """)

if __name__ == "__main__":
    main() 