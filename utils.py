import os
import io
import math
import requests
from gtts import gTTS
from PIL import Image
import google.generativeai as genai
from dotenv import load_dotenv

# ----------------------------
# CONFIGURATION
# ----------------------------
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") # Gemini API Key
HF_API_KEY = os.getenv("HF_API_KEY") # Hugging Face API Key

# Configure Gemini + Hugging Face
genai.configure(api_key=GEMINI_API_KEY)
HF_HEADERS = {"Authorization": f"Bearer {HF_API_KEY}"}
HF_API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"


# ----------------------------
# STORY GENERATION
# ----------------------------
def generate_story(prompt, language):
    """Generate a ~300 word story in chosen language using Gemini."""
    model = genai.GenerativeModel("gemini-1.5-flash")
    resp = model.generate_content(f"Write a story (~300 words) in {language} about: {prompt}")
    return resp.text


# ----------------------------
# IMAGE PROMPT EXTRACTION
# ----------------------------
def extract_image_prompts(story_text):
    """Break story into 6 short visual prompts for Stable Diffusion."""
    model = genai.GenerativeModel("gemini-1.5-flash")
    prompt_extract = f"""
    Break this story into 6 short, visual prompts for stable diffusion.
    RULES:
    - Max 1 line each
    - Focus on visuals (characters, setting, action)
    - Avoid long narrative sentences
    Story:
    {story_text}
    """
    resp = model.generate_content(prompt_extract)
    return [line.strip("-• ").strip() for line in resp.text.split("\n") if line.strip()][:6]


# ----------------------------
# IMAGE GENERATION
# ----------------------------
def generate_image(prompt):
    """Generate one image from Stable Diffusion via Hugging Face API (with debug)."""
    try:
        response = requests.post(HF_API_URL, headers=HF_HEADERS, json={"inputs": prompt})

        # ✅ Debug info
        print(f"[HF DEBUG] Status: {response.status_code}, Content-Type: {response.headers.get('content-type')}")
        if response.headers.get("content-type", "").startswith("application/json"):
            print("[HF DEBUG] JSON Response:", response.text[:500]) # first 500 chars

        if response.status_code == 200 and response.headers.get("content-type", "").startswith("image"):
            return Image.open(io.BytesIO(response.content))
        else:
            # Show the error message in Streamlit UI
            import streamlit as st
            st.warning(f"Hugging Face API Error ({response.status_code}): {response.text[:300]}")
    except Exception as e:
        import streamlit as st
        st.error(f"Image Generation Failed: {e}")

    # fallback red square
    return Image.new("RGB", (300, 300), color=(200, 0, 0))

# ----------------------------
# AUDIO GENERATION
# ----------------------------
def generate_audio(text, language, story_id):
    """Generate audio narration for the story using gTTS."""
    lang_code = "en" if language == "English" else "hi"
    audio_dir = "audio"
    os.makedirs(audio_dir, exist_ok=True)
    audio_path = os.path.join(audio_dir, f"story_{story_id}.mp3")
    tts = gTTS(text, lang=lang_code)
    tts.save(audio_path)
    return audio_path


# ----------------------------
# SAVE IMAGES
# ----------------------------
def save_images(images, story_id):
    """Save generated images with captions to disk."""
    image_dir = os.path.join("images", str(story_id))
    os.makedirs(image_dir, exist_ok=True)
    paths = []
    for idx, (img, caption) in enumerate(images, 1):
        path = os.path.join(image_dir, f"panel_{idx}.png")
        img.save(path)
        paths.append((path, caption))
    return paths