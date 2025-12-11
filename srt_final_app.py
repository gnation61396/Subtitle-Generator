# Renamed Repo - Final Commit
import streamlit as st
import assemblyai as aai
import os

# --- IMPORTANT CONFIGURATION: API KEY (MUST BE AT THE TOP) ---
# This line securely fetches the key from the website's Secrets manager
API_KEY = st.secrets["general"]["assembly_api_key"] 
aai.settings.api_key = API_KEY

# Set default values for variables used early by the interpreter
diarization_enabled = True
max_chars = 42

# --- STREAMLIT APP UI & DESIGN ---
st.set_page_config(page_title="Pro Subtitle Generator", layout="wide")

# Custom Title/Branding Area
st.markdown(
    """
    <div style='text-align: center; padding: 10px; background-color: #f0f0f5; border-radius: 10px;'>
        <h1 style='color: #0069d9; font-size: 40px;'>🎬 Professional Subtitle & Analysis Tool</h1>
    </div>
    <hr/>
    """,
    unsafe_allow_html=True
)

# Custom CSS for Premium Buttons (Matching config.toml theme)
st.markdown(
    """
    <style>
        /* Main Button Styling */
        div.stButton > button {
            background-color: #007bff; /* Primary Blue */
            color: white; /* White text */
            border-radius: 10px; /* Rounded corners */
            padding: 10px 24px;
            font-size: 16px;
            font-weight: bold;
            border: 2px solid #007bff; 
            transition: background-color 0.3s, border-color 0.3s;
        }
        
        /* Button Hover Effect (Premium) */
        div.stButton > button:hover {
            background-color: #0056b3; /* Darker blue on hover */
            border-color: #0056b3;
        }
        
        /* Sidebar Headers (for consistency with the blue accent) */
        .css-pkz3mm {
            color: #007bff; 
            font-weight: 700;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# --- INPUT AND SETTINGS ---

# Sidebar for professional settings
with st.sidebar:
    st.header("Subtitle Formatting")
    
    # 1. Character Limit (Min 2 characters fixed)
    max_chars = st.number_input(
        "Max Characters Per Line",
        min_value=2, 
        max_value=60,
        value=42, 
        step=1,
        help="Sets the maximum number of characters allowed on one line of text."
    )
    
    # 2. Line Count
    max_lines = st.radio(
        "Max Lines Per Block",
        options=[1, 2],
        index=1,
        help="Select 1 or 2 lines per subtitle block."
    )
    
    # 3. Subtitle Gap/Spacing
    subtitle_gap_ms = st.number_input(
        "Min Subtitle Gap (milliseconds)",
        min_value=0,
        max_value=1000,
        value=200, 
        step=50,
        help="The minimum time (ms) required between one subtitle ending and the next one starting."
    )

    st.header("Language & Analysis")
    diarization_enabled = st.checkbox("Enable Speaker Diarization (Speaker 1, Speaker 2)", value=True)
    
    st.info("Configured for high accuracy with English and Hebrew (Code-Switching).")


# Main Uploader
uploaded_file = st.file_uploader("Upload Video/Audio File (.mp4, .mov, .wav)", type=["mp4", "mov", "wav", "mp3"])

if uploaded_file is not None:
    
    st.subheader("1. Start Transcription")
    
    # Button to start the process
    if st.button("Generate Timed Captions & Transcript"):
        
        # --- Transcription Process ---
        transcriber = aai.Transcriber()
        
        temp_file_path = f"temp_{uploaded_file.name}"
        with open(temp_file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        with st.spinner("Uploading and Transcribing (This may take a few minutes for long videos)..."):
            
            # --- CRITICAL FIX: Configuration is now safely created INSIDE the button block ---
            config = aai.TranscriptionConfig(
                speaker_diarization=diarization_enabled,
                language_code="en", 
                language_codes=["he", "en"] # Enable code-switching for Hebrew and English
            )
            
            # Call the service
            transcript = transcriber.transcribe(temp_file_path, config=config)

        # --- Error Handling ---
        if transcript.status == aai.TranscriptStatus.error:
            st.error(f"Transcription failed: {transcript.error}")
        else:
            
            st.subheader("2. Download Files")
            
            # Subtitle Gap (converted from ms to seconds for the function)
            subtitle_gap_seconds = subtitle_gap_ms / 1000.0

            # 1. Generate SRT File
            srt_content = transcript.export_subtitles_srt(
                chars_per_caption=max_chars,
                max_lines=max_lines,
                subtitle_gap=subtitle_gap_seconds 
            )
            
            # 2. Generate VTT File (For web players/YouTube)
            vtt_content = transcript.export_subtitles_vtt(
                chars_per_caption=max_chars,
                max_lines=max_lines,
                subtitle_gap=subtitle_gap_seconds 
            )
            
            st.success("Analysis complete! Download files below.")

            # Download Button: SRT
            st.download_button(
                label="Download SRT File (Premiere Pro)",
                data=srt_content,
                file_name="transcript.srt",
                mime="application/x-subrip",
                key="srt_download"
            )
            
            # Download Button: VTT
            st.download_button(
                label="Download VTT File (Web/YouTube)",
                data=vtt_content,
                file_name="transcript.vtt",
                mime="text/vtt",
                key="vtt_download"
            )

            # --- CRITICAL FEATURE: Raw Transcript Output (for Proofing) ---
            st.subheader("3. Raw Transcript (Proofread Here)")
            st.text_area(
                "Full Transcript (Edit text below before downloading)", 
                value=transcript.text, 
                height=250
            )

        # Clean up the temporary file
        os.remove(temp_file_path)



