# Force Streamlit to recognize this is a new file version (4.0)
import streamlit as st
import assemblyai as aai
import os

# --- IMPORTANT CONFIGURATION ---
# This line securely fetches the key from the website's Secrets manager
API_KEY = st.secrets["general"]["assembly_api_key"]
aai.settings.api_key = API_KEY


# --- STREAMLIT APP UI & DESIGN ---
st.set_page_config(page_title="Pro Subtitle Generator", layout="wide")

st.title("🎬 Professional Subtitle Generator (AssemblyAI)")
st.markdown("---")

# --- INPUT AND SETTINGS ---

# Sidebar for professional settings
with st.sidebar:
    st.header("Subtitle Formatting")
    
    # 1. Character Limit (Fixed to allow min 14)
    max_chars = st.number_input(
        "Max Characters Per Line",
        min_value=14, # <--- FIX: Changed min value to 14
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
    
    # 3. Subtitle Gap/Spacing (Required by editors for clean cuts)
    subtitle_gap_ms = st.number_input(
        "Min Subtitle Gap (milliseconds)",
        min_value=0,
        max_value=1000,
        value=200, # 200ms is a standard gap (0.2 seconds)
        step=50,
        help="The minimum time (in milliseconds) required between one subtitle ending and the next one starting."
    )

    st.header("Language & Diarization")
    diarization_enabled = st.checkbox("Enable Speaker Diarization (Speaker 1, Speaker 2)", value=True)
    
    st.info("AssemblyAI automatically handles multiple languages and code-switching.")
    
    # --- Design Update (From config.toml theme) ---
    st.markdown("""
        <style>
            .stButton>button {
                background-color: #007bff;
                color: white;
            }
        </style>
    """, unsafe_allow_html=True)


# Main Uploader
uploaded_file = st.file_uploader("Upload Video/Audio File (.mp4, .mov, .wav)", type=["mp4", "mov", "wav", "mp3"])

if uploaded_file is not None:
    
    st.subheader("1. Start Transcription")
    
    # Button to start the process
    if st.button("Generate Timed Captions"):
        
        # --- Transcription Process ---
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
            
            st.subheader("2. Download Files")
            
            # --- Subtitle Generation ---
            
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

            st.success("Captions generated successfully. Download and import into Premiere Pro or web players.")
            
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
                label="Download VTT File (Web Players/YouTube)",
                data=vtt_content,
                file_name="transcript.vtt",
                mime="text/vtt",
                key="vtt_download"
            )

        # Clean up the temporary file
        os.remove(temp_file_path)
