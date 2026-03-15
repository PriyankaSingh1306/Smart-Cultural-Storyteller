import streamlit as st
import math
from utils import generate_story, extract_image_prompts, generate_image, generate_audio

# ----------------------------
# STREAMLIT APP
# ----------------------------
st.set_page_config(page_title="Smart Cultural Storyteller", page_icon="📖", layout="wide")
st.title("📖 Smart Cultural Storyteller")
st.write("Generate stories in English or Hindi with audio narration and comic-style images.")

# ----------------------------
# SESSION STATE INIT
# ----------------------------
if "story" not in st.session_state: 
    st.session_state.story = ""
if "image_prompts" not in st.session_state: 
    st.session_state.image_prompts = []
if "images" not in st.session_state: 
    st.session_state.images = []
if "story_id" not in st.session_state: 
    st.session_state.story_id = 0
if "language" not in st.session_state: 
    st.session_state.language = "English" # default

# ----------------------------
# USER INPUT
# ----------------------------
prompt = st.text_area("Enter your story idea:", "A lion meets a rabbit in the jungle")
language = st.selectbox("Choose story language:", ["English", "Hindi"])
st.session_state.language = language # Save language persistently

# ----------------------------
# GENERATE STORY
# ----------------------------
if st.button("Generate Story"):
    st.session_state.story_id += 1
    st.session_state.story = generate_story(prompt, st.session_state.language)
    st.session_state.image_prompts = []
    st.session_state.images = []

if st.session_state.story:
    st.subheader("📝 Generated Story")
    st.write(st.session_state.story)

# ----------------------------
# GENERATE AUDIO
# ----------------------------
if st.session_state.story and st.button("Generate Audio"):
    with st.spinner("Generating audio..."):
        audio_file = generate_audio(
            st.session_state.story,
            st.session_state.language,
            st.session_state.story_id
        )
        st.success("✅ Audio generated!")
        st.audio(audio_file, format="audio/mp3")

# ----------------------------
# GENERATE IMAGES
# ----------------------------
if st.session_state.story and st.button("Generate Images"):
    if not st.session_state.image_prompts:
        with st.spinner("Extracting image prompts..."):
            st.session_state.image_prompts = extract_image_prompts(st.session_state.story)

    st.subheader("🎨 Comic Panels")
    cols_per_row = 3
    total_panels = len(st.session_state.image_prompts)
    rows = math.ceil(total_panels / cols_per_row)
    st.session_state.images = []

    for r in range(rows):
        cols = st.columns(cols_per_row)
        for c in range(cols_per_row):
            idx = r*cols_per_row + c
            if idx < total_panels:
                prompt_text = st.session_state.image_prompts[idx]
                with st.spinner(f"Generating panel {idx+1}..."):
                    img = generate_image(prompt_text)
                    st.session_state.images.append((img, prompt_text))
                    with cols[c]:
                        st.image(img, caption=prompt_text, use_container_width=True)