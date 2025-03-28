import streamlit as st
import os
from pathlib import Path
import requests
import json
import time
import pandas as pd
import shutil

# Page configuration
st.set_page_config(page_title="Batch Image Renamer", layout="wide")

# App title and description
st.title("📸 Smart Screenshot Batch Renamer")

# Collapsible instructions
with st.expander("ℹ️ About this app", expanded=False):
    st.markdown("""
    ### What this app does
    This app uses AI to analyze your screenshots and generate descriptive filenames based on their content. 
    It can process multiple images in batches and optionally move them to a dedicated folder.

    ### How to use
    1. Enter your Ideogram API key in the sidebar
    2. Specify the folder containing your screenshots
    3. Configure the renaming options in the sidebar
    4. Use preview mode first to verify results
    5. Process your images when ready

    ### Tips
    - The **Preview Mode** lets you see changes without modifying files
    - Customize the prompt to get more relevant descriptions
    - Adjust the naming template to control filename format
    - Use file name filtering to target specific groups of files
    """)

# Main content area
col1, col2 = st.columns([3, 1])
with col1:
    folder = st.text_input("Enter path to your screenshot folder:")
with col2:
    file_prefix = st.text_input("File name starts with:",
                                placeholder="e.g., Screenshot, Leonard")

# Sidebar for settings
with st.sidebar:
    st.header("Settings")

    # API Key input with collapsible info
    with st.expander("🔑 API Key", expanded=True):
        st.markdown("""
        You need an Ideogram API key to use this app. Get one at [ideogram.ai](https://ideogram.ai).
        """)
        api_key = st.secrets["IDEOGRAM_API_KEY"]

    # Advanced settings with collapsible info
    with st.expander("⚙️ Advanced Options", expanded=False):
        st.markdown("""
        Configure how images are processed and renamed.

        - **Batch Size**: Number of images to process together
        - **Delay**: Time between API calls to avoid rate limits
        - **Naming Template**: Format for the new filenames
        - **File Types**: Image formats to process
        """)

        batch_size = st.slider("Batch Size", 1, 50, 10)
        delay = st.slider("Delay Between API Calls (seconds)", 0.0, 5.0, 1.0, 0.1)

        st.markdown("**Naming Template**")
        st.markdown("Available variables: `{base}`, `{description}`")
        naming_template = st.text_input("Template", "{base}_{description}")

        file_types = st.multiselect("File Types",
                                    [".png", ".jpg", ".jpeg", ".webp"],
                                    [".png", ".jpg", ".jpeg", ".webp"])

    # Prompt customization with collapsible info
    with st.expander("💬 Prompt Customization", expanded=False):
        st.markdown("""
        Customize the instructions sent to the AI when analyzing images.

        - Be specific about what aspects of the image are important
        - Focus on elements like URLs, site names, or UI elements
        - Limit the word count to keep filenames manageable
        """)

        prompt_template = st.text_area(
            "Custom Prompt Instructions",
            "Pay close attention to the site name, URL, and all visible text in the image."
        )

        max_description_length = st.slider(
            "Max Description Length (words)",
            3, 15, 7
        )

    # File handling options with collapsible info
    with st.expander("📁 File Handling", expanded=False):
        st.markdown("""
        Configure what happens to files after processing.

        - Move files to a separate folder to keep originals intact
        - Organize by content type (Premium feature)
        """)

        move_to_renamed = st.checkbox("Move files to 'renamed' folder", value=True)

    # Premium features with collapsible info
    with st.expander("💎 Premium Features", expanded=False):
        st.markdown("""
        Unlock additional capabilities with a premium subscription.

        - **Metadata**: Add descriptions to image metadata
        - **Tags**: Generate content tags for better organization
        - **Smart Folders**: Automatically organize by content type
        """)

        add_metadata = st.checkbox("Add descriptions to metadata")
        create_tags = st.checkbox("Generate tags from images")
        smart_folders = st.checkbox("Organize into smart folders")

if folder:
    folder_path = Path(folder)
    if not folder_path.exists():
        st.error(f"Folder not found: {folder}")
    else:
        # Get all supported image types
        all_images = []
        for ext in file_types:
            all_images.extend(list(folder_path.glob(f"*{ext}")))

        # Filter images by prefix if specified
        if file_prefix:
            images = [img for img in all_images if img.name.startswith(file_prefix)]
            if len(images) < len(all_images):
                st.info(f"Filtered {len(images)} out of {len(all_images)} images that start with '{file_prefix}'")
        else:
            images = all_images

        if not images:
            if file_prefix:
                st.warning(
                    f"No images found in {folder} with prefix '{file_prefix}' and types: {', '.join(file_types)}")
            else:
                st.warning(f"No images found in {folder} with types: {', '.join(file_types)}")
        else:
            st.success(f"Found {len(images)} images{' matching your filter' if file_prefix else ''}")

            # Show preview of images
            with st.expander("🖼️ Image Preview", expanded=True):
                # Create a dataframe for display
                image_df = pd.DataFrame({
                    "Filename": [img.name for img in images],
                    "Size (KB)": [round(os.path.getsize(img) / 1024, 2) for img in images],
                    "Type": [img.suffix for img in images],
                    "Path": [str(img) for img in images]
                })

                # Display the dataframe
                st.dataframe(image_df, use_container_width=True)

            # Batch processing options
            st.subheader("Batch Processing")

            col1, col2 = st.columns(2)
            with col1:
                preview_mode = st.checkbox("Preview Mode (no changes)", value=True)
            with col2:
                if preview_mode:
                    process_button = st.button("Preview Renaming")
                else:
                    process_button = st.button("Process All Images")


            # Define the processing function
            def describe_image(image_path, api_key, prompt_instructions, max_words):
                url = "https://api.ideogram.ai/describe"
                headers = {"Api-Key": api_key}

                # Construct the specific prompt for the API
                full_prompt = f"Describe this image in {max_words} words or less. {prompt_instructions}"

                with open(image_path, "rb") as f:
                    files = {
                        "image_file": (image_path.name, f,
                                       "image/png" if image_path.suffix.lower() == ".png" else
                                       "image/jpeg" if image_path.suffix.lower() in [".jpg", ".jpeg"] else
                                       "image/webp")
                    }

                    # Additional parameters for the API call
                    data = {
                        "prompt": full_prompt
                    }

                    try:
                        response = requests.post(url, headers=headers, files=files, data=data)

                        if response.status_code == 200:
                            result = response.json()
                            descriptions = result.get("descriptions", [])
                            if descriptions and len(descriptions) > 0 and "text" in descriptions[0]:
                                # Limit the description to the specified number of words
                                description = descriptions[0]["text"].strip()
                                words = description.split()
                                if len(words) > max_words:
                                    description = " ".join(words[:max_words])
                                return description

                        # If we get here, something went wrong
                        return f"Error: {response.status_code}"
                    except Exception as e:
                        return f"Error: {str(e)}"


            def rename_and_move_image(image_path, description, template, move_to_renamed_dir):
                if not description or description.startswith("Error:"):
                    return image_path.name, False, ""

                # Remove any unsafe characters from description
                safe_desc = ''.join(c if c.isalnum() or c.isspace() else '-' for c in description)
                short_desc = safe_desc  # We're already limiting the word count
                safe_desc_hyphenated = short_desc.replace(' ', '-').lower()[:50]

                # Apply naming template
                try:
                    new_name = template.format(
                        base=image_path.stem,
                        description=safe_desc_hyphenated
                    ) + image_path.suffix

                    # Determine target location
                    if move_to_renamed_dir and not preview_mode:
                        # Create 'renamed' directory if it doesn't exist
                        renamed_dir = image_path.parent / "renamed"
                        renamed_dir.mkdir(exist_ok=True)
                        new_path = renamed_dir / new_name
                        location = "renamed folder"
                    else:
                        new_path = image_path.parent / new_name
                        location = "same folder"

                    if not preview_mode:
                        # Move the file (rename + move if needed)
                        shutil.move(str(image_path), str(new_path))

                    return new_name, True, location
                except Exception as e:
                    return f"{image_path.name} (error: {str(e)})", False, ""


            # Process images when button is clicked
            if process_button:
                if not api_key:
                    st.error("Please enter your Ideogram API key in the sidebar")
                else:
                    results = []

                    progress_bar = st.progress(0)
                    status_text = st.empty()

                    # Show prompt information
                    st.info(
                        f"Using prompt: 'Describe this image in {max_description_length} words or less. {prompt_template}'")

                    # Create 'renamed' directory for preview purposes
                    if move_to_renamed:
                        renamed_dir = folder_path / "renamed"
                        if not preview_mode:
                            renamed_dir.mkdir(exist_ok=True)
                        if preview_mode:
                            st.info(f"A 'renamed' directory will be created at: {renamed_dir}")

                    # Process in batches
                    for i in range(0, len(images), batch_size):
                        batch = images[i:i + batch_size]
                        status_text.text(
                            f"Processing batch {i // batch_size + 1}/{(len(images) + batch_size - 1) // batch_size}")

                        for j, img_path in enumerate(batch):
                            # Update progress
                            progress = (i + j) / len(images)
                            progress_bar.progress(progress)

                            # Get description or use mock in preview mode
                            if preview_mode:
                                description = f"Sample description for {img_path.name}"
                            else:
                                description = describe_image(
                                    img_path,
                                    api_key,
                                    prompt_template,
                                    max_description_length
                                )

                            # Rename and move image
                            new_name, success, location = rename_and_move_image(
                                img_path, description, naming_template, move_to_renamed
                            )

                            # Save result
                            results.append({
                                "Original": img_path.name,
                                "Description": description,
                                "New Name": new_name,
                                "Location": location if success else "N/A",
                                "Status": "Success" if success else "Failed"
                            })

                            # Add delay to avoid rate limiting
                            if delay > 0 and not preview_mode:
                                time.sleep(delay)

                    # Complete progress bar
                    progress_bar.progress(1.0)
                    status_text.text("Processing complete!")

                    # Show results
                    with st.expander("📋 Results", expanded=True):
                        results_df = pd.DataFrame(results)
                        st.dataframe(results_df, use_container_width=True)

                    # Summary
                    st.subheader("Summary")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Images Processed", len(results))
                    with col2:
                        success_count = sum(1 for r in results if r["Status"] == "Success")
                        st.metric("Successfully Renamed", success_count)
                    with col3:
                        failed_count = sum(1 for r in results if r["Status"] == "Failed")
                        st.metric("Failed", failed_count)

                    # Show final location info
                    if move_to_renamed and success_count > 0 and not preview_mode:
                        st.success(f"✅ {success_count} files moved to: {renamed_dir}")

                    # Show premium features callout
                    if any([add_metadata, create_tags, smart_folders]):
                        st.info("💎 Premium features selected! Upgrade to unlock these capabilities.")

