import streamlit as st
from dotenv import load_dotenv
import os
from google.cloud import language_v1
from youtube_transcript_api import YouTubeTranscriptApi
import re
import random
import google.generativeai as genai
import base64

def analyze_text(text):
    client = language_v1.LanguageServiceClient()
    document = language_v1.Document(content=text, type_=language_v1.Document.Type.PLAIN_TEXT)
    response = client.analyze_sentiment(document=document)
    return response
    
st.set_page_config(page_title="YouTube Note Cards", page_icon="hi7.png", layout="wide")

# Load environment variables
load_dotenv()
api_key = os.getenv("YOUR_API_KEY")
if not api_key:
    st.error("API key not found. Please set up your environment variable correctly.")
    st.stop()

# Ensure the google.generativeai module is configured correctly
try:
    genai.configure(api_key=api_key)  # Use the actual API key
except Exception as e:
    st.error(f"Error configuring Google Generative AI: {e}")
    st.stop()

# --- Functions ---

def extract_video_id(youtube_url):
    """Extracts video ID from a YouTube URL."""
    pattern = r'(?:v=|\/)([0-9A-Za-z_-]{11}).*'
    match = re.search(pattern, youtube_url)
    if match:
        return match.group(1)
    else:
        st.error("Invalid YouTube URL.")
        return None

def extract_transcript_details(video_id):
    """Extracts and returns the transcript text from a YouTube video ID."""
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        full_transcript = " ".join([segment['text'] for segment in transcript_list])
        return full_transcript
    except Exception as e:
        st.error(f"Error extracting transcript: {e}")
        return None

def generate_note_cards_from_transcript(full_transcript, keywords):
    """Generates note cards focused on keywords using Google Gemini Pro."""
    prompt = f"""
    You are an advanced educational assistant with a deep understanding of content analysis and summarization. 
    Your task is to create detailed, engaging, and informative note cards from a YouTube video transcript, focusing specifically on the given keywords.

    Here is the full transcript of the video:
    "{full_transcript}"

    Keywords: {keywords}

    Your goal is to produce a set of comprehensive and concise note cards based on this transcript. Each note card should:
    1. Highlight the most important concepts, facts, or ideas mentioned in the video.
    2. Provide clear and brief explanations for each highlighted concept or fact.
    3. Include bullet points, sub-points, and examples where relevant to enhance understanding.
    4. Be written in simple, easy-to-understand language that is also engaging and catchy.
    5. Focus specifically on the provided keywords to ensure relevance.

    Ensure that you generate a minimum of 8 and a maximum of 12 note cards. Each note card should cover unique content from the transcript, ensuring that the entire video is comprehensively summarized. The note cards should be highly informative, engaging, and directly related to the content of the video.

    Please start by creating the note cards based on the above guidelines.
    """
    try:
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"Error generating note card content: {e}")
        return None


def format_note_cards(note_cards_content):
    """Formats the note cards content into HTML for display."""
    note_cards = note_cards_content.split("Note Card ")
    formatted_note_cards = []
    colors = ['#FFCDD2', '#F8BBD0', '#E1BEE7', '#D1C4E9', '#C5CAE9', '#BBDEFB', '#B3E5FC', '#B2EBF2', '#B2DFDB', '#C8E6C9']
    for i, note_card in enumerate(note_cards[1:], start=1):  # Skip the first empty element
        note_card = note_card.strip()
        if note_card:
            color = random.choice(colors)
            formatted_note_cards.append(f"""
                <div class="note-card" style="background-color: {color};">
                    <h3>Note Card {i}</h3>
                    <ul>
                        {note_card.replace('. ', '.<br>')}
                    </ul>
                </div>
            """)
    return formatted_note_cards

def add_bg_from_local(image_file):
    with open(image_file, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    st.markdown(
        f"""
    <style>
    .stApp {{
        background-image: url(data:image/{"png"};base64,{encoded_string.decode()});
        background-size: cover
    }}

    .main {{  /* Added to target the main content area */
        background-color: rgba(255, 255, 255, 0);  /* Semi-transparent white background */
        padding: 20px;
        border-radius: 10px; /* Optional rounded corners */
        margin: 80px auto; /* Center the container horizontally */
        margin-bottom: 20px; /* Add some space at the bottom */
        max-width: 900px;  /* Set a maximum width */
        
    }}

    /* Additional styling for other elements (optional) */
    .stVideo {{ /* Style the video embed */
        margin-top: 2px;
        margin-bottom: 20px;
    }}

    </style>
    """,
        unsafe_allow_html=True
    )

# Custom CSS for input box design
st.markdown(
    """
    <style>
    .stTextInput > div > div > input {
        background-color: rgba(3, 3, 3, 0.22) !important;
        color: white !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Add background image (replace 'your_background_image.png' with your actual image path)
add_bg_from_local('hi5.jpg')

# --- Streamlit App ---
st.title("📚YouTube Video to Note Cards🎓")

# Custom CSS for note card design
st.markdown("""
    <style>
    .note-card {
        border: 2px solid #000;
        padding: 20px;
        margin: 10px 0;
        border-radius: 10px;
        font-size: 1.1em;
        line-height: 1.5em;
        color: #000;
    }
    .note-card h3 {
        margin-top: 0;
    }
    .note-card p {
        margin: 0;
    }
    .note-card ul {
        padding-left: 20px;
    }
    .note-card li {
        margin-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# Set background image
st.markdown(
    """
    <style>
    .reportview-container {
        background: url("https://imgur.com/a/Cab4ZMk") center center;
        background-size: cover;
    }
    </style>
    """,
    unsafe_allow_html=True
)

youtube_link = st.text_input("Enter YouTube Video Link:")

if youtube_link:
    video_id = extract_video_id(youtube_link)
    if video_id:
        st.video(f"https://www.youtube.com/watch?v={video_id}")

        # Keyword input
        keywords = st.text_input("Enter keywords (comma-separated):") 

        if st.button("Generate Note Cards"):
            with st.spinner("Extracting transcript..."):
                full_transcript = extract_transcript_details(video_id)

            if full_transcript:
                with st.spinner("Generating note cards..."):
                    # Pass keywords to the note generation function
                    note_cards_content = generate_note_cards_from_transcript(
                        full_transcript, keywords
                    )
                    if note_cards_content:
                        formatted_note_cards = format_note_cards(note_cards_content)
                        st.markdown("## Note Cards:")
                        # Adjust the number of note cards based on video length
                        min_cards = 8
                        max_cards = 12
                        video_length = len(full_transcript.split())
                        num_cards = min(max(min_cards, int(video_length / 200)), max_cards)
                        for card in formatted_note_cards[:num_cards]:
                            st.markdown(card, unsafe_allow_html=True)
                    else:
                        st.error("Failed to generate note cards.")
    else:
        st.error("Failed to extract video ID from the URL.")
