import streamlit as st
import pandas as pd
from PIL import Image
from github import Github
import os

# Authenticate with GitHub using Streamlit Secrets
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
g = Github(GITHUB_TOKEN)

# Define repository and file paths
REPO_NAME = "Abdullahshade/Misapplication"  # Replace with your GitHub repository name
FILE_PATH = "Filtered_Table.csv"  # Path to metadata CSV in your GitHub repo
repo = g.get_repo(REPO_NAME)

# Local paths
metadata_file = FILE_PATH
images_folder = "IImages"  # Folder where images are stored

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
st.title("Pneumothorax *******Grading and Image Viewer with GitHub Integration")

# Initialize session state for the current index
if "current_index" not in st.session_state:
    st.session_state.current_index = 0

# Get the current row
current_index = st.session_state.current_index
row = metadata.iloc[current_index]

# Check if image ID is valid (check if file exists in the images folder)
image_path_base = f"{images_folder}/{row['Image_ID']}"
image_extensions = ['.jpeg', '.jpg', '.png']

image_found = False
for ext in image_extensions:
    image_path = f"{image_path_base}{ext}"
    if os.path.exists(image_path):
        try:
            st.image(Image.open(image_path), caption=f"Image ID: {row['Image_ID']}", use_column_width=True)
            image_found = True
            break
        except Exception as e:
            st.error(f"Error opening image {image_path}: {e}")
            break

if not image_found:
    st.error(f"Image {row['Image_ID']} not found in {images_folder} with expected extensions.")

# Handling cases where Pneumothorax_Type or Percentage are missing
if pd.isna(row['Pneumothorax_Type']) or pd.isna(row['Percentage']):
    st.warning(f"Missing Pneumothorax Type or Percentage for Image {row['Image_ID']}. Please update.")
    pneumothorax_type = st.selectbox("Pneumothorax Type", ["Simple", "Tension"], index=0)
    A = st.number_input("Enter value for A:", min_value=0, max_value=100, value=0, step=1)
    B = st.number_input("Enter value for B:", min_value=0, max_value=100, value=0, step=1)
    C = st.number_input("Enter value for C:", min_value=0, max_value=100, value=0, step=1)
    percentage = 4.2 + (4.7 * A + B + C)
    st.write(f"### Calculated Pneumothorax Volume Percentage: {percentage:.2f}%")

else:
    pneumothorax_type = row["Pneumothorax_Type"]
    A = row["A"]
    B = row["B"]
    C = row["C"]
    percentage = row["Percentage"]
    st.write(f"### Pneumothorax Volume Percentage: {percentage}")

# Save changes
if st.button("Save Changes"):
    # Update the metadata locally
    metadata.at[current_index, "Pneumothorax_Type"] = pneumothorax_type
    metadata.at[current_index, "A"] = A
    metadata.at[current_index, "B"] = B
    metadata.at[current_index, "C"] = C
    metadata.at[current_index, "Percentage"] = percentage
    metadata.at[current_index, "Label_Flag"] = 1
    metadata.to_csv(metadata_file, index=False)

    # Push changes to GitHub
    try:
        updated_content = metadata.to_csv(index=False)
        repo.update_file(
            path=contents.path,
            message="Update metadata with pneumothorax grading",
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
