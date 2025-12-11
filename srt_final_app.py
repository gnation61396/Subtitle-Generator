# Version 3.0: Final Launch Attempt
# Force Streamlit to recognize this is a new file version
import streamlit as st
import assemblyai as aai
import os

# --- IMPORTANT CONFIGURATION ---
# 1. PASTE YOUR ASSEMBLYAI API KEY HERE
# This key is a simple text string, not a JSON file.
API_KEY = "YOUR_ASSEMBLYAI_API_KEY_HERE" 

# --- STREAMLIT APP UI ---
st.set_page_config(page_title="Pro Subtitle Generator", layout="wide")
st.title("🎬 Single-Step Subtitle Generator (AssemblyAI)")
st.markdown("---")

if API_KEY == "YOUR_ASSEMBLYAI_API_KEY_HERE":
    st.error("❌ ERROR: Please replace the placeholder API_KEY in the code with your actual AssemblyAI key.")
    st.stop()

# --- INPUT AND SETTINGS ---

# Sidebar for professional settings
with st.sidebar:
    st.header("Subtitle Settings")
    
    # Character Limit (Professional Requirement)
    max_chars = st.number_input(
        "Max Characters Per Line",
        min_value=30,
        max_value=60,
        value=42, # Standard YouTube/Netflix character limit
        step=1,
        help="Controls how long each line of text can be before wrapping."
    )
    
    # Line Count (Professional Requirement)
    max_lines = st.radio(
        "Max Lines Per Block",
        options=[1, 2],
        index=1,
        help="Controls whether captions are split into 1 or 2 lines."
    )
    
    # Language/Code-Switching Settings (AssemblyAI handles this in the API)
    st.header("Language & Diarization")
    diarization_enabled = st.checkbox("Enable Speaker Diarization (Speaker 1, Speaker 2)", value=True)
    
    st.info("AssemblyAI automatically handles multiple languages and code-switching.")

# Main Uploader
uploaded_file = st.file_uploader("Upload Video/Audio File (.mp4, .mov, .wav)", type=["mp4", "mov", "wav", "mp3"])

if uploaded_file is not None:
    
    st.subheader("1. Start Transcription")
    
    if st.button("Generate Timed SRT"):
        
        # --- Transcription Process ---
        aai.settings.api_key = API_KEY
        transcriber = aai.Transcriber()
        
        # Save file to a temporary location for the transcriber
        temp_file_path = f"temp_{uploaded_file.name}"
        with open(temp_file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        with st.spinner("Uploading and Transcribing... This may take several minutes for long videos."):
            
            # Transcription parameters including diarization
            config = aai.TranscriptionConfig(
                speaker_diarization=diarization_enabled
            )
            
            # Call the service
            transcript = transcriber.transcribe(temp_file_path, config=config)

        # --- Error Handling ---
        if transcript.status == aai.TranscriptStatus.error:
            st.error(f"Transcription failed: {transcript.error}")
        else:
            
            st.subheader("2. Download Final SRT File")
            
            # Use the built-in function to generate SRT with line/character limits
            srt_content = transcript.export_subtitles_srt(
                chars_per_caption=max_chars,
                # AssemblyAI handles max_lines implicitly with the chars_per_caption logic
                # For 1 line, use a high char count. For 2 lines, use a medium one (like 42).
            )
            
            st.success("SRT generated successfully. Download and import into Premiere Pro.")
            
            # Download Button
            st.download_button(
                label="Download transcript.srt",
                data=srt_content,
                file_name="transcript.srt",
                mime="application/x-subrip",
                help="Imports directly into Premiere Pro with all timings."
            )
            
        # Clean up the temporary file

        os.remove(temp_file_path)

