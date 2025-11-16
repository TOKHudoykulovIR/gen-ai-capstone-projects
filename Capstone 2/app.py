import streamlit as st
import tempfile
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()  # reads variables from a .env file and sets them in os.environ

api_key = os.getenv("OPENAI_API_KEY")  # get the key from .env

client = OpenAI(api_key=api_key)   # define an openai object

# streamlit ui setup
st.set_page_config(page_title="Voice → Image Generator", page_icon="🎨")
st.title("🎤 Voice → 🖼️ Image Generator")

st.write("Upload a short audio message and I will convert it into an image.")
st.write("---")

if "logs" not in st.session_state:
    st.session_state.logs = []  # create log history

log_box = st.empty()

def log(msg):
    st.session_state.logs.append(msg)  # add new log to the list
    # join all logs into one big string and show them inside a code block
    log_box.write("```\n" + "\n".join(st.session_state.logs) + "\n```")


# upload audio section
audio_file = st.file_uploader("Upload audio (mp3, wav, m4a)", type=["mp3", "wav", "m4a"])

if audio_file:
    st.audio(audio_file)  # play uploaded audio in ui

    transcript_response = client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file
    )
    # transcription
    st.write("### 1️⃣ Transcribing your voice...")
    log("Transcribing audio...")

    transcript = transcript_response.text  # extract transcript text

    st.success("Transcript:")
    st.code(transcript)  # display transcript in code block
    log(f"Transcript: {transcript}")

    st.write("### 2️⃣ Creating image prompt...")
    log("Generating image prompt...")

    # create image prompt
    prompt_response = client.responses.create(
        model="gpt-4.1-nano",
        input=f"Convert this into a descriptive image prompt: {transcript}"
    )

    image_prompt = prompt_response.output_text
    st.code(image_prompt)
    log(f"Image prompt: {image_prompt}")

    st.write("### 3️⃣ Generating image...")
    log("Sending prompt to image generation model...")

    # image generation
    image_result = client.images.generate(
        model="dall-e-2",
        prompt=image_prompt,
        size="1024x1024"
    )

    image_url = image_result.data[0].url
    st.image(image_url, caption="Generated Image")
    log(f"Image generated: {image_url}")
else:
    st.info("Upload a short voice message to begin 🎤")
