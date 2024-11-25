import streamlit as st
import pandas as pd
from PIL import Image
from github import Github

# Authenticate with GitHub using Streamlit Secrets
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
g = Github(GITHUB_TOKEN)

# Define repository and file paths
REPO_NAME = "Abdullahshade/Misapplication"  # Replace with your GitHub repository name
FILE_PATH = "Filtered_Table.csv"  # Path to updated metadata CSV in your GitHub repo
repo = g.get_repo(REPO_NAME)

# Local paths
metadata_file = FILE_PATH
images_folder = "IImages"  # Updated folder where images are stored

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

# Debugging: Display column names to identify any discrepancies
st.write("### Columns in the CSV:", metadata.columns.tolist())

# App title
st.title("Pneumothorax Grading")

# Initialize session state for the current index
if "current_index" not in st.session_state:
    st.session_state.current_index = 0

# Get the current row
current_index = st.session_state.current_index
row = metadata.iloc[current_index]

# Display the image
image_path = f"{images_folder}/{row['Image_File']}"
try:
    st.image(Image.open(image_path), caption=f"Image: {row['Image_File']}", use_column_width=True)
except FileNotFoundError:
    st.error(f"Image {row['Image_File']} not found in {images_folder}.")

# Show Ground Truth as Pneumothorax status
status = "Yes" if row.get("Pneumothorax_Status", 0) == 1 else "No"
st.write(f"### Ground Truth: Pneumothorax - {status}")

# Show the existing Pneumothorax Grading
grading = row.get("Pneumothorax_Grading", "Column Missing")
if grading == "Column Missing":
    st.warning("The column 'Pneumothorax_Grading' is missing from the CSV.")
st.write(f"### Current Grading: {grading}")

# Editable fields for percentage grading
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
    try:
        # Update the metadata locally
        metadata.at[current_index, "Percentage of Grade"] = f"{percentage_grade}%"
        metadata.to_csv(metadata_file, index=False)

        # Push changes to GitHub
        updated_content = metadata.to_csv(index=False)
        repo.update_file(
            path=contents.path,
            message="Update metadata with percentage grade",
            content=updated_content,
            sha=contents.sha
        )
        st.success("Changes saved locally and successfully pushed to GitHub!")
    except Exception as e:
        st.error(f"Failed to save changes: {e}")

# Navigation between images
col1, col2 = st.columns(2)
if col1.button("Previous") and current_index > 0:
    st.session_state.current_index -= 1
if col2.button("Next") and current_index < len(metadata) - 1:
    st.session_state.current_index += 1
