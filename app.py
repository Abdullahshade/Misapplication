import streamlit as st
import pandas as pd
from PIL import Image
from github import Github

# Authenticate with GitHub using Streamlit Secrets
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
g = Github(GITHUB_TOKEN)

# Define repository and file paths
REPO_NAME = "Abdullahshade/Misapplication"  # Replace with your GitHub repository name
FILE_PATH = "Updated_GTruth_with_Grading.csv"  # Path to metadata CSV in your GitHub repo
repo = g.get_repo(REPO_NAME)

# Local paths
metadata_file = FILE_PATH
images_folder = "Images"  # Folder where images are stored

# Load metadata
try:
    # Fetch the latest file from the GitHub repository
    contents = repo.get_contents(FILE_PATH)
    with open(metadata_file, "wb") as f:
        f.write(contents.decoded_content)
    metadata = pd.read_csv(metadata_file)
except Exception as e:
    st.error(f"Failed to fetch metadata from GitHub: {e}")
    st.stop()

# App title
st.title("Pneumonia Grading and Image Viewer with GitHub Integration")

# Initialize session state for the current index
if "current_index" not in st.session_state:
    st.session_state.current_index = 0

# Get the current row
current_index = st.session_state.current_index
row = metadata.iloc[current_index]

# Display the image
image_path = f"{images_folder}/{row['Id']}.jpeg"
try:
    st.image(Image.open(image_path), caption=f"Image ID: {row['Id']}", use_column_width=True)
except FileNotFoundError:
    st.error(f"Image {row['Id']}.jpeg not found in {images_folder}.")

# Show Ground Truth as pneumonia status
ground_truth = row['Ground_Truth']
if ground_truth == 1:
    st.write("### Ground Truth: Pneumonia - Yes")
else:
    st.write("### Ground Truth: Pneumonia - No")

# Editable fields for metadata
st.write("### Update Pneumonia Grading:")
grading = st.selectbox(
    "Pneumonia Grading",
    options=["No Pneumonia", "Mild", "Moderate", "Severe", "Critical"],
    index=["No Pneumonia", "Mild", "Moderate", "Severe", "Critical"].index(
        row["Pneumonia_Grading"] if pd.notna(row["Pneumonia_Grading"]) else "No Pneumonia"
    )
)

# Slider for percentage grading
percentage_grade = row.get("Percentage of Grade", 0)
if not isinstance(percentage_grade, (int, float)) or pd.isna(percentage_grade):
    percentage_grade = 0  # Default to 0 if invalid data

percentage_grade = st.slider(
    "Percentage of Grade",
    min_value=0,
    max_value=100,
    value=int(percentage_grade),
    step=1
)

# Save changes
if st.button("Save Changes"):
    # Update the metadata locally
    metadata.at[current_index, "Pneumonia_Grading"] = grading
    metadata.at[current_index, "Percentage of Grade"] = f"{percentage_grade}%"
    metadata.to_csv(metadata_file, index=False)

    # Push changes to GitHub
    try:
        updated_content = metadata.to_csv(index=False)
        repo.update_file(
            path=contents.path,
            message="Update metadata with pneumonia grading",
            content=updated_content,
            sha=contents.sha
        )
        st.success("Changes saved locally and successfully pushed to GitHub!")
    except Exception as e:
        st.error(f"Failed to push changes to GitHub: {e}")

# Navigation between images
col1, col2 = st.columns(2)
if col1.button("Previous") and current_index > 0:
    st.session_state.current_index -= 1
if col2.button("Next") and current_index < len(metadata) - 1:
    st.session_state.current_index += 1
