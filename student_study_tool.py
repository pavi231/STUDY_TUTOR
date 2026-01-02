import streamlit as st
import tempfile
import os
import urllib.parse
import re
import cv2
from youtube_transcript_api import YouTubeTranscriptApi
from google import genai
from google.genai.types import Part 
import requests
from gtts import gTTS
from io import BytesIO

# ============================================================
# 👇 PASTE YOUR GOOGLE GEMINI API KEY HERE 👇
# ============================================================
GEMINI_API_KEY = st.secrets["API_KEY"]
# ============================================================

st.set_page_config(
    page_title="🎓 STABLE Study Tutor",
    layout="wide",
    page_icon="🎓"
)

custom_css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .main {
        background: #1a1a2e !important;
    }
    
    .stApp {
        background: #16213e !important;
    }
    
    h1 {
        color: #fff !important;
        font-weight: 800;
        font-size: 3rem !important;
        margin-bottom: 0.5rem !important;
        letter-spacing: -1px;
    }
    
    .subtitle {
        color: #fff !important;
        font-size: 1.1rem;
        font-weight: 500;
        margin-bottom: 2rem;
        padding: 0.75rem 1.5rem;
        background: rgba(255,255,255,0.1);
        border-radius: 50px;
        display: inline-block;
        box-shadow: 0 2px 10px rgba(0,0,0,0.3);
        border: 1px solid rgba(255,255,255,0.2);
    }
    
    [data-testid="stSidebar"] {
        background: #0f3460 !important;
        border-right: 1px solid #16213e;
    }
    
    [data-testid="stSidebar"] * {
        color: #fff !important;
    }
    
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        color: #fff !important;
        font-weight: 700;
    }
    
    [data-testid="stSidebar"] label, [data-testid="stSidebar"] p, [data-testid="stSidebar"] span {
        color: #fff !important;
    }
    
    [data-testid="stSidebar"] div {
        color: #fff !important;
    }
    
    .sidebar-section {
        background: transparent;
        padding: 0;
        margin-bottom: 1.5rem;
    }
    
    .output-container {
        background: rgba(31, 52, 96, 0.5);
        padding: 2rem;
        margin: 2rem 0;
        border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    .output-header {
        color: #fff !important;
        font-weight: 700;
        font-size: 1.5rem;
        margin-bottom: 1.5rem;
        padding-bottom: 1rem;
        border-bottom: 3px solid #667eea;
    }
    
    .action-buttons {
        display: flex;
        gap: 1rem;
        margin: 1.5rem 0;
        flex-wrap: wrap;
    }
    
    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: 600;
        padding: 0.75rem 2rem;
        border-radius: 12px;
        border: none;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        transition: all 0.3s ease;
        font-size: 1.05rem;
    }
    
    .stButton > button:hover {
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
        transform: translateY(-2px);
    }
    
    .stDownloadButton > button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: 600;
        padding: 0.75rem 2rem;
        border-radius: 12px;
        border: none;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        transition: all 0.3s ease;
        font-size: 1.05rem;
    }
    
    .stDownloadButton > button:hover {
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
        transform: translateY(-2px);
    }
    
    .stTextInput > div > div > input {
        border-radius: 10px;
        border: 2px solid #667eea;
        padding: 0.75rem 1rem;
        font-size: 1rem;
        transition: all 0.3s ease;
        background: rgba(255,255,255,0.1) !important;
        color: #fff !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.3);
        background: rgba(255,255,255,0.15) !important;
    }
    
    .stTextInput > div > div > input::placeholder {
        color: rgba(255,255,255,0.5) !important;
    }
    
    .stRadio > div {
        background: rgba(255,255,255,0.05);
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid rgba(102,126,234,0.3);
    }
    
    .stRadio > div > label {
        font-weight: 600;
        color: #fff !important;
        margin-bottom: 0.5rem;
    }
    
    div[data-testid="stFileUploader"] {
        background: rgba(255,255,255,0.05) !important;
        border: 2px dashed #667eea !important;
        border-radius: 12px;
        padding: 1.5rem;
        transition: all 0.3s ease;
    }
    
    div[data-testid="stFileUploader"]:hover {
        border-color: #667eea;
        background: rgba(255,255,255,0.1) !important;
    }
    
    .info-badge {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: 600;
        display: inline-block;
        margin: 0.5rem 0;
    }
    
    .stAlert {
        border-radius: 12px;
        border: none;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }
    
    .video-preview {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        margin: 1.5rem 0;
    }
    
    .frame-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin: 1.5rem 0;
    }
    
    .frame-item {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        transition: transform 0.3s ease;
    }
    
    .frame-item:hover {
        transform: scale(1.05);
    }
    
    .input-section {
        background: rgba(31, 52, 96, 0.5);
        padding: 2rem;
        border-radius: 16px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        margin: 2rem 0;
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    .section-divider {
        height: 2px;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
        margin: 2rem 0;
    }
    
    .welcome-message {
        text-align: center;
        padding: 3rem 2rem;
        color: #fff !important;
        font-size: 1.1rem;
        line-height: 1.8;
    }
    
    .stSpinner > div {
        border-top-color: #667eea !important;
    }
    
    hr {
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
        margin: 2rem 0;
    }
    
    body, p, div, span {
        color: #fff !important;
    }
    
    .stMarkdown {
        color: #fff !important;
    }
    
    .stMarkdown p {
        color: #fff !important;
    }
    
    [data-testid="stMarkdownContainer"] {
        color: #fff !important;
    }
    
    [data-testid="stMarkdownContainer"] p, [data-testid="stMarkdownContainer"] div {
        color: #fff !important;
    }
</style>
"""

st.markdown(custom_css, unsafe_allow_html=True)

try:
    api_key = os.environ.get("GEMINI_API_KEY") or GEMINI_API_KEY
    
    if not api_key or api_key == "YOUR_API_KEY_HERE":
        st.error("❌ API Key not configured!")
        st.info("📝 **To fix this:** Edit `app.py` at line 17 and replace `YOUR_API_KEY_HERE` with your actual Google Gemini API key")
        st.markdown("**Get your API key here:** https://aistudio.google.com/apikey")
        st.stop()
    
    client = genai.Client(api_key=api_key)
except Exception as e:
    st.error(f"❌ Error initializing Gemini client: {e}")
    st.stop()


def extract_video_id(url):
    patterns = [
        r"v=([0-9A-Za-z_-]{11})",
        r"youtu\.be/([0-9A-Za-z_-]{11})",
        r"shorts/([0-9A-Za-z_-]{11})",
    ]
    for p in patterns:
        m = re.search(p, url)
        if m:
            return m.group(1)
    return None


def get_transcript(url):
    vid = extract_video_id(url)
    if not vid:
        return None
    try:
        data = YouTubeTranscriptApi.get_transcript(vid, languages=['en'])
        return " ".join([x['text'] for x in data])
    except:
        return None


def extract_3_frames(video_file):
    temp_path = tempfile.mktemp(".mp4")

    video_file.seek(0) 
    with open(temp_path, "wb") as f:
        f.write(video_file.read())

    video_file.seek(0) 
    
    cap = cv2.VideoCapture(temp_path)
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    if not cap.isOpened() or total == 0:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        return []

    positions = [int(total * 0.25), int(total * 0.50), int(total * 0.75)]
    frame_paths = []

    for pos in positions:
        cap.set(cv2.CAP_PROP_POS_FRAMES, pos)
        ret, frame = cap.read()
        if ret:
            img_path = tempfile.mktemp(".jpg")
            cv2.imwrite(img_path, frame)
            frame_paths.append(img_path)

    cap.release()
    os.remove(temp_path)
    return frame_paths


def generate_output(contents):
    try:
        # FIX: Using 'gemini-1.5-flash-001' which is fully compatible with the v1beta API version
        resp = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=contents
        )
        return resp.text
    except Exception as e:
        return f"⚠ Gemini Error: {e}"
        


def text_to_speech(text):
    try:
        tts = gTTS(text=text, lang='en', slow=False)
        audio_fp = BytesIO()
        tts.write_to_fp(audio_fp)
        audio_fp.seek(0)
        return audio_fp.getvalue()
    except Exception as e:
        st.error(f"Error generating speech: {e}")
        return None

def render_interactive_quiz(quiz_text):
    # Split the AI output into separate question blocks
    # The regex looks for "**Q1.", "**Q2.", "**Q3.", etc.
    blocks = re.split(r'\*\*Q\d+[:.]', quiz_text)
    
    # Initialize a place to store scores/results if not already there
    if 'quiz_results' not in st.session_state:
        st.session_state.quiz_results = {}

    q_count = 1
    for block in blocks:
        if not block.strip() or len(block) < 10: continue
        
        lines = block.strip().splitlines()
        question_text = lines[0].strip()
        
        # Extract options: Looks for lines starting with "* A)", "* B)", etc.
        options = [l.strip().replace("* ", "") for l in lines if re.match(r'^\*\s*[A-D]\)', l.strip())]
        
        # Extract the correct answer letter
        ans_match = re.search(r"Correct Answer:\s*([A-D])", block, re.IGNORECASE)
        
        st.markdown(f"### Q{q_count}. {question_text}")
        
        if options:
            # The radio button for selecting an answer
            choice = st.radio("Choose your answer:", options, key=f"quiz_q_{q_count}")
            
            # The interactive "Submit" logic
            if st.button("Submit Answer", key=f"quiz_btn_{q_count}"):
                if ans_match:
                    correct_letter = ans_match.group(1).upper()
                    if choice.strip().startswith(correct_letter):
                        st.session_state.quiz_results[q_count] = ("correct", f"🎉 Correct! It is {correct_letter}.")
                    else:
                        # Find the full text of the correct option to show the user
                        correct_text = next((opt for opt in options if opt.startswith(correct_letter)), correct_letter)
                        st.session_state.quiz_results[q_count] = ("error", f"❌ Wrong. The correct answer is: {correct_text}")

            # Persist the feedback so it doesn't disappear on re-run
            if q_count in st.session_state.quiz_results:
                status, msg = st.session_state.quiz_results[q_count]
                if status == "correct":
                    st.success(msg)
                else:
                    st.error(msg)
                    
        st.divider()
        q_count += 1
        
        

if 'output' not in st.session_state:
    st.session_state.output = ""

if 'query' not in st.session_state:
    st.session_state.query = ""

if 'current_mode' not in st.session_state:
    st.session_state.current_mode = "Explanation"


with st.sidebar:
    youtube_link = st.text_input(
        "🔗 YouTube Link",
        placeholder="Paste YouTube URL here...",
        key="youtube_link",
        help="Enter a YouTube video URL for analysis"
    )
    
    st.markdown("**OR**")
    
    uploaded_video = st.file_uploader(
        "📁 Upload Video File",
        type=["mp4", "mov", "avi", "webm"],
        key="uploaded_video",
        help="Upload a local video file (MP4, MOV, AVI, WEBM)"
    )
    
    st.markdown("---")
    
    mode = st.radio(
        "Output Type:",
        ["Explanation", "Notes", "Quiz", "Highlights"],
        key="mode",
        help="Select the type of content to generate"
    )
    
    st.markdown("---")
    
    content_uploaded = bool(youtube_link or uploaded_video)
    
    if content_uploaded:
        query_placeholder = "Refine your request (e.g., 'focus on chapter 3')..."
        query_help = "Add specific instructions to refine the analysis"
    else:
        query_placeholder = "Enter a topic or question (e.g., 'photosynthesis')..."
        query_help = "Enter a topic to learn about using AI knowledge"
    
    st.session_state.query = st.text_input(
        "🧠 Topic / Question:",
        value=st.session_state.query,
        key="query_input_main",
        placeholder=query_placeholder,
        help=query_help
    )
    
    st.markdown("---")
    
    go = st.button("🚀 Generate Content", key="generate_button", help="Click to start analysis", type="primary")


st.markdown('<h1>🎓 STABLE Study Tutor</h1>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">🤖 AI-Powered Learning • 📹 Video Analysis • 📝 Smart Notes • 🎯 Quiz Generation</div>',
    unsafe_allow_html=True
)

if youtube_link:
    st.video(youtube_link)
elif uploaded_video:
    st.video(uploaded_video)

st.markdown('<div class="output-container">', unsafe_allow_html=True)
st.markdown('<div class="output-header">📄 Generated Content</div>', unsafe_allow_html=True)

if st.session_state.output:
    # If the mode is Quiz, render the interactive UI, otherwise show raw text
    if st.session_state.current_mode == "Quiz":
        render_interactive_quiz(st.session_state.output)
    else:
        st.markdown(st.session_state.output)
else:
    st.info("Your generated content will appear here...")

st.markdown('</div>', unsafe_allow_html=True)


if go:
    query_text = st.session_state.query.strip()
    youtube_link_val = youtube_link.strip() if youtube_link else ""
    uploaded_video_val = uploaded_video
    content_uploaded_logic = bool(youtube_link_val or uploaded_video_val)

    if not (youtube_link_val or uploaded_video_val or query_text):
        st.error("❗ Please provide either content (video/link) OR enter a topic/question.")
        st.stop()

    frame_cleanup_paths = []

    base_instruction = (
        "You are an expert tutor. Use Markdown formatting.\n"
        "If transcript or images are provided, strictly use ONLY that content. "
        "The current task is to generate output for: "
    )
    
    # STRICT formatting for the Quiz prompt to ensure the parser works
    quiz_instruction = (
        "CRITICAL: Generate exactly 5 Multiple Choice Questions (MCQs) in this perfect format, ensuring each option is on a new, separate line using list items (*):\n\n"
        "**Q1. Question text?**\n"
        "* A) Option A\n"
        "* B) Option B\n"
        "* C) Option C\n"
        "* D) Option D\n"
        "**Correct Answer: B**\n\n"
    )

    task = f"create {mode.lower()} based on the provided content/topic. "
    if not content_uploaded_logic and query_text:
         task += f"The user query is: {query_text}"
    elif content_uploaded_logic and query_text:
         task += f"The specific request is: {query_text}"
    
    contents = [base_instruction + task]
    
    if mode == "Quiz":
        contents.append(quiz_instruction)

    if youtube_link_val:
        transcript = get_transcript(youtube_link_val)

        if transcript:
            st.success("📝 Transcript found! Analyzing video content...")
            contents.append(f"TRANSCRIPT:\n{transcript}")
        else:
            st.warning("⚠ No transcript available. Using video title for context...")
            try:
                page = requests.get(youtube_link_val).text
                title = re.search(r'<title>(.*?)</title>', page).group(1).replace("- YouTube", "")
            except:
                title = "Unknown Title"

            contents.append(f"VIDEO TITLE: {title}")

    elif uploaded_video_val:
        with st.spinner("📸 Extracting key frames from your video..."):
            frames = extract_3_frames(uploaded_video_val)
            frame_cleanup_paths = frames 

        if frames:
            st.success("✅ Frames extracted! Analyzing visual content...")
            
            st.markdown("### 🖼️ Extracted Frames")
            cols = st.columns(3)
            for i, f in enumerate(frames):
                with cols[i]:
                    st.image(f, caption=f"Frame {i+1}", use_container_width=True)

            contents.append("Below are 3 key frames extracted from the uploaded video. Use ONLY these images:")

            for f in frames:
                with open(f, "rb") as image_file:
                    contents.append(
                        Part.from_bytes(
                            data=image_file.read(),
                            mime_type='image/jpeg'
                        )
                    )

        else:
            st.warning("⚠ Could not extract frames. Using general topic analysis...")

    elif query_text:
        st.info(f"🧠 Generating {mode.lower()} for topic: **{query_text}**")
        contents.append("General knowledge allowed.")

    with st.spinner(f"✨ Generating {mode.lower()}... This may take a moment."):
        output = generate_output(contents)

    st.session_state.output = output
    st.session_state.current_mode = mode
    st.rerun()

    if frame_cleanup_paths:
        for f in frame_cleanup_paths:
            if os.path.exists(f):
                os.remove(f)


if st.session_state.output:
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    st.markdown("### 📥 Download & Listen")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.download_button(
            label="📝 Download as Text",
            data=st.session_state.output,
            file_name=f"{st.session_state.current_mode.lower()}_output.txt",
            mime="text/plain",
            key="download_txt"
        )
    
    with col2:
        if st.button("🔊 Read Out Loud", key="speak_button"):
            with st.spinner("🎤 Generating audio..."):
                audio_bytes = text_to_speech(st.session_state.output)
                if audio_bytes:
                    st.audio(audio_bytes, format="audio/mp3")
                    st.success("✅ Audio ready! Press play above.")
                else:
                    st.error("❌ Failed to generate audio.")
    
    with col3:
        st.markdown("")


if not (youtube_link or uploaded_video) and st.session_state.query.strip():
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    st.markdown("### 📺 Suggested Video Resources")

    search_term = f"{st.session_state.query} tutorial"
    encoded = urllib.parse.quote_plus(search_term)
    search_url = f"https://www.youtube.com/results?search_query={encoded}"

    st.markdown(f"🔍 [Search YouTube for: **{search_term}**]({search_url})")
    st.caption("💡 Find related video tutorials to enhance your learning")
