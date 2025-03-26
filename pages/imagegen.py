import streamlit as st
import requests
import json
import time, os
from PIL import Image
from io import BytesIO

st.set_page_config(page_title="AI Image Generator", layout="wide", page_icon="🎨")

# Custom CSS for dark mode and modern UI
st.markdown("""
<style>
    .main {
        background-color: #121212;
        color: #f0f0f0;
    }
    .stButton>button {
        background-color: #9333ea;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 10px 24px;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #7e22ce;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(147, 51, 234, 0.3);
    }
    .css-1d391kg {
        background-color: #1e1e1e;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
    }
    h1, h2, h3 {
        color: #f0f0f0;
    }
    .stTextInput>div>div>input, .stSelectbox>div>div>input {
        background-color: #2d2d2d;
        color: #f0f0f0;
        border-radius: 6px;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #2d2d2d;
        border-radius: 6px 6px 0px 0px;
        padding: 10px 20px;
        margin-right: 5px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #9333ea;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# App title
st.title("🎨 Advanced AI Image Generator")
st.markdown("### Create stunning images with AI - built with Ideogram API")

# Initialize session state
if 'generated_images' not in st.session_state:
    st.session_state.generated_images = []
if 'api_key' not in st.session_state:
    st.session_state.api_key = ""

# Sidebar for API key
with st.sidebar:
    st.header("Settings")
    api_key = st.secrets["IDEOGRAM_API_KEY"]
   # api_key = st.text_input("Ideogram API Key", type="password", value=st.session_state.api_key)

    if api_key:
        st.session_state.api_key = api_key

    st.markdown("---")
    st.markdown("### Upcoming Features")
    st.markdown("- Chat interface")
    st.markdown("- Video generation")
    st.markdown("- AI avatars")
    st.markdown("- Style customization")
    st.markdown("- Batch processing")

# Main app interface
tabs = st.tabs(["Generate Images", "My Gallery", "About"])

with tabs[0]:
    col1, col2 = st.columns([3, 2])

    with col1:
        # Image generation form
        st.subheader("Create your image")

        # Initialize session state
        if "show_image" not in st.session_state:
            st.session_state.show_image = False


        # Toggle function
        def toggle_image():
            st.session_state.show_image = not st.session_state.show_image


        # Button to toggle
        st.button("🔄 Toggle Model Price", on_click=toggle_image)

        # Show or hide image
        if st.session_state.show_image:
            st.image("./modelfees.png", caption="Here's your image!", use_container_width=True)

        prompt = st.text_area("Describe your image",
                              placeholder="A serene tropical beach scene. Dominating the foreground are tall palm trees...",
                              height=100)

        # Advanced options with expander
        with st.expander("Advanced Options"):
            col_a, col_b = st.columns(2)
            with col_a:
                aspect_ratio = st.selectbox("Aspect Ratio",
                                            ["ASPECT_1_1", "ASPECT_16_10", "ASPECT_10_16", "ASPECT_16_9", "ASPECT_9_16",
                                             'ASPECT_3_2', 'ASPECT_2_3', 'ASPECT_4_3', 'ASPECT_3_4', 'ASPECT_1_1', 'ASPECT_1_3', 'ASPECT_3_1'],
                                            index=0)
                style_type = st.selectbox("Style Type",
                                         ['AUTO', 'GENERAL', 'REALISTIC', 'DESIGN', 'RENDER_3D', 'ANIME'],
                                          index=0)
            with col_b:
                model = st.selectbox("Model",
                                     ["V_2A_TURBO", "V_3","V_1_TURBO","V_2_TURBO","V_2A", "V_2", "V_3"],
                                     index=0)
                magic_prompt = st.selectbox("Magic Prompt",
                                            ["AUTO", "OFF"],
                                            index=0)

        # Generate button
        if st.button("🔮 Generate Image", use_container_width=True):
            if not st.session_state.api_key:
                st.error("Please enter your Ideogram API key in the sidebar first!")
            elif not prompt:
                st.error("Please enter a prompt to generate an image!")
            else:
                with st.spinner("Creating your masterpiece..."):
                    try:
                        # API request
                        headers = {
                            "Api-Key": st.session_state.api_key,
                            "Content-Type": "application/json"
                        }

                        data = {
                            "image_request": {
                                "prompt": prompt,
                                "aspect_ratio": aspect_ratio,
                                "model": model,
                                "magic_prompt_option": magic_prompt,
                                "style_type": style_type
                            }
                        }

                        response = requests.post(
                            "https://api.ideogram.ai/generate",
                            headers=headers,
                            data=json.dumps(data)
                        )

                        # Handle API response
                        if response.status_code == 200:
                            result = response.json()
                            image_url = result["data"][0]["url"]

                            # Download image
                            img_response = requests.get(image_url)
                            img = Image.open(BytesIO(img_response.content))

                            # Save image to 'streamlit_app/generated_images' folder (Streamlit Cloud friendly)
                            save_dir = os.path.join("streamlit_app", "generated_images")
                            os.makedirs(save_dir, exist_ok=True)
                            timestamp = time.strftime("%Y%m%d-%H%M%S")
                            save_path = os.path.join(save_dir, f"{timestamp}.png")
                            img.save(save_path)

                            # Save to session state
                            image_data = {
                                "id": timestamp,
                                "prompt": prompt,
                                "image": img,
                                "url": image_url,
                                "file_path": save_path,  # Store file path for download
                                "settings": {
                                    "aspect_ratio": aspect_ratio,
                                    "model": model,
                                    "style_type": style_type
                                }
                            }
                            st.session_state.generated_images.insert(0, image_data)

                            st.success("Image generated successfully!")
                        else:
                            st.error(f"Error: {response.status_code} - {response.text}")

                    except Exception as e:
                        st.error(f"An error occurred: {str(e)}")

    with col2:
        # Preview area
        st.subheader("Preview")
        preview_container = st.container(height=400)

        with preview_container:
            if st.session_state.generated_images:
                latest_image = st.session_state.generated_images[0]
                st.image(latest_image["image"], use_container_width=True)
                st.markdown(f"**Prompt:** {latest_image['prompt']}")

                # ⬇️ Download button here
                if "file_path" in latest_image:
                    with open(latest_image["file_path"], "rb") as file:
                        st.download_button(
                            label="⬇️ Download Image",
                            data=file,
                            file_name=f"{latest_image['id']}.png",
                            mime="image/png"
                        )
            else:
                st.info("Your generated image will appear here")

with tabs[1]:
    # Gallery view
    st.subheader("Your Generated Images")

    if not st.session_state.generated_images:
        st.info("You haven't generated any images yet. Start creating!")
    else:
        # Create rows of 3 images each
        for i in range(0, len(st.session_state.generated_images), 3):
            cols = st.columns(3)
            for j in range(3):
                idx = i + j
                if idx < len(st.session_state.generated_images):
                    img_data = st.session_state.generated_images[idx]
                    with cols[j]:
                        st.image(img_data["image"], use_container_width=True)
                        st.markdown(f"**ID:** {img_data['id']}")

                        # Expander for details
                        with st.expander("Details"):
                            st.markdown(f"**Prompt:** {img_data['prompt']}")
                            st.markdown(f"**Style:** {img_data['settings']['style_type']}")
                            st.markdown(f"**Model:** {img_data['settings']['model']}")

                            # Download button
                            st.markdown(f"[Download Image]({img_data['url']})")

                            # Delete button
                            if st.button(f"Delete", key=f"del_{img_data['id']}"):
                                st.session_state.generated_images.pop(idx)
                                st.rerun()

with tabs[2]:
    # About section
    st.subheader("About This App")

    st.markdown("""
    This is a prototype image generator powered by the Ideogram API. The application allows you to:

    * Generate high-quality AI images from text prompts
    * Customize aspect ratio, style, and other parameters
    * Save and manage your generated images
    * Download images for use in your projects

    The interface is designed to be modern, intuitive, and user-friendly, with a focus on showcasing the AI-generated artwork.

    **Upcoming Features:**

    As development continues, we'll be adding more exciting capabilities:
    * Chat interface for more natural image generation
    * Video generation from prompts
    * AI avatars creation
    * More customization options
    * Batch processing for multiple images

    **How to Use:**

    1. Enter your Ideogram API key in the sidebar
    2. Type a descriptive prompt in the text area
    3. Adjust any desired settings in the Advanced Options
    4. Click "Generate Image" and watch the magic happen!

    **Note:** You must have a valid Ideogram API key to use this application.
    """)

# Footer
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: #999999; font-size: 0.8em;">
        Built with Streamlit and Ideogram API • Not affiliated with Ideogram
    </div>
    """,
    unsafe_allow_html=True
)