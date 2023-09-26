# This script generates a readme file for the project.
# It adapts the readme without changing the text in there.
# This includes a reference to each image in the repository in the readme.
# This reads the readme and searches for 'TRIGGER'
# Then it writes previews of the images in the repository right after that.

import os

# Path to the readme file
README_PATH = "README.md"

# Images path
IMAGES_PATH = "images"

# Trigger
TRIGGER_IMAGES_ENTER = "<!-- BEGIN IMAGES -->\n"
TRIGGER_IMAGES_EXIT = "<!-- END IMAGES -->\n"
TRIGGER_COUNT_ENTER = "<!-- BEGIN COUNT -->`"
TRIGGER_COUNT_EXIT = "`<!-- END COUNT -->"

# Table dimensions
TABLE_COLUMNS = 3

# Set cwd to the directory of this script
os.chdir(os.path.dirname(os.path.realpath(__file__)))

# Check if the readme exists
if not os.path.exists(README_PATH):
    print("README.md not found")
    exit(1)

# Read the readme
readme_lines = None
with open(README_PATH, "r") as f:
    readme_lines = f.readlines()

# Check if the trigger is in the readme
if TRIGGER_IMAGES_ENTER not in readme_lines:
    print("Trigger enter not found")
    exit(1)
if TRIGGER_IMAGES_EXIT not in readme_lines:
    print("Trigger exit not found")
    exit(1)
count_index = -1
for i, line in enumerate(readme_lines):
    if TRIGGER_COUNT_ENTER in line and TRIGGER_COUNT_EXIT in line:
        count_index = i
if count_index == -1:
    print("Count trigger not found")
    exit(1)

# Get the index of the trigger
trigger_enter_index = readme_lines.index(TRIGGER_IMAGES_ENTER)
trigger_exit_index = readme_lines.index(TRIGGER_IMAGES_EXIT)

# Filter out non-images from the repository
images: 'list[str]' = [image for image in os.listdir(IMAGES_PATH) if image.endswith(".png") or image.endswith(".jpg")]

# Group the images by year
images_by_year: 'dict' = {}
for image in images:
    split = image.split("-")
    if len(split) < 2:
        # Get the creation year and month from the file metadata
        import datetime
        creation_time = os.path.getctime(f"{IMAGES_PATH}/{image}")
        creation_date = datetime.datetime.fromtimestamp(creation_time)

        # Rename the file to the format YYYY-MM_ID.png|jpg where _ID is omitted if it is 0
        # Format month to 2 digits
        new_name = f"{creation_date.year}-{creation_date.month:02}"
        if os.path.exists(f"{IMAGES_PATH}/{new_name}.png") or os.path.exists(f"{IMAGES_PATH}/{new_name}.jpg"):
            new_name = new_name + "_0"
            while os.path.exists(f"{IMAGES_PATH}/{new_name}.png") or os.path.exists(f"{IMAGES_PATH}/{new_name}.jpg"):
                new_name = new_name[:-1] + str(int(new_name[-1]) + 1)
        print(f"Renaming {image} to {new_name}{os.path.splitext(image)[1]}")
        os.rename(f"{IMAGES_PATH}/{image}", f"{IMAGES_PATH}/{new_name}{os.path.splitext(image)[1]}")
        split = new_name.split("-")
    year = split[0]
    if year not in images_by_year:
        images_by_year[year] = []
    images_by_year[year].append(image)

# Write the readme
out = ""
# Write the lines before and including the enter trigger
for line in readme_lines[:trigger_enter_index + 1]:
    out += line

# Write the images with markdown in a table format of 3 columns
for year in images_by_year:

    # Get images for the year
    ims = images_by_year[year]

    # Details block for dropdown
    out += "<details>\n"
    out += f"<summary>{year}</summary>\n\n"
    
    # Number of images
    out += f"Number of images: {len(ims)}\n\n"

    # Write the table header
    out += "| "
    for j in range(TABLE_COLUMNS):
        if j < len(ims):
            out += f"![{ims[j]}]({IMAGES_PATH}/{ims[j]}) | "
    out += "\n"

    # Write the table divider (required to make the table work)
    out += "|---|---|---|\n"

    # Write the table rows
    # The TABLE_COLUMNS as the first argument of range is to skip the first row
    for i in range(TABLE_COLUMNS, len(ims), TABLE_COLUMNS):
        out += "| "
        for j in range(TABLE_COLUMNS):
            if i + j < len(ims):
                out += f"![{ims[i + j]}]({IMAGES_PATH}/{ims[i + j]}) | "
        out += "\n"

    # Close the details block
    out += "</details>\n\n"

# Write the lines after and including the exit trigger
for line in readme_lines[trigger_exit_index:count_index]:
    out += line

# Write the image count
count_line = readme_lines[count_index]
splitup_s = count_line.split(TRIGGER_COUNT_ENTER)
splitup_e = splitup_s[1].split(TRIGGER_COUNT_EXIT)
out += splitup_s[0] + TRIGGER_COUNT_ENTER + str(len(images)) + TRIGGER_COUNT_EXIT + splitup_e[1]

# Write remaining lines
for line in readme_lines[count_index + 1:]:
    out += line

with open(README_PATH, "w") as f:
    f.write(out)