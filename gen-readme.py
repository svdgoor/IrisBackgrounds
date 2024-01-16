import os
import datetime

class ReadmeGenerator:
    def __init__(self, readme_path, images_path):
        """
        Initialize the GenReadme object.

        Args:
            readme_path (str): The path to the README file.
            images_path (str): The path to the directory containing the images.

        Attributes:
            readme_path (str): The path to the README file.
            images_path (str): The path to the directory containing the images.
            trigger_images_enter (str): The trigger for the beginning of the images section in the README file.
            trigger_images_exit (str): The trigger for the end of the images section in the README file.
            trigger_count_enter (str): The trigger for the beginning of the count section in the README file.
            trigger_count_exit (str): The trigger for the end of the count section in the README file.
            table_columns (int): The number of columns in the images table.
        """
        self.readme_path = readme_path
        self.images_path = images_path
        self.trigger_images_enter = "<!-- BEGIN IMAGES -->\n"
        self.trigger_images_exit = "<!-- END IMAGES -->\n"
        self.trigger_count_enter = "<!-- BEGIN COUNT -->`"
        self.trigger_count_exit = "`<!-- END COUNT -->"
        self.table_columns = 3

    def generate_readme(self):
        """
        Generate the README file by reading the existing README, filtering and grouping images, and updating the file.

        Raises:
            FileNotFoundError: If the README file is not found.
            ValueError: If the trigger or count section is not found in the README file.
        """
        if not os.path.exists(self.readme_path):
            raise FileNotFoundError("README.md not found")

        readme_lines = self.read_readme()

        if not self.is_trigger_present(readme_lines):
            raise ValueError("Trigger not found")

        trigger_enter_index, trigger_exit_index = self.get_trigger_indices(readme_lines)
        count_index = self.get_count_trigger_index(readme_lines)

        images = self.get_filtered_images()

        images_by_year = self.group_images_by_year(images)

        self.generate_output(readme_lines, trigger_enter_index, trigger_exit_index, count_index, images_by_year, images)

    def read_readme(self) -> 'list[str]':
        """
        Read the existing README file and return its content as a list of lines.

        Returns:
            list: The content of the README file as a list of lines.
        """
        with open(self.readme_path, "r") as f:
            return f.readlines()

    def is_trigger_present(self, readme_lines) -> bool:
        """
        Check if the trigger section is present in the README file.

        Args:
            readme_lines (list): The content of the README file as a list of lines.

        Returns:
            bool: True if the trigger section is present, False otherwise.
        """
        return self.trigger_images_enter in readme_lines and self.trigger_images_exit in readme_lines

    def get_trigger_indices(self, readme_lines) -> 'tuple[int, int]':
        """
        Get the indices of the trigger section in the README file.

        Args:
            readme_lines (list): The content of the README file as a list of lines.

        Returns:
            tuple: A tuple containing the indices of the trigger section in the README file.
        """
        trigger_enter_index = readme_lines.index(self.trigger_images_enter)
        trigger_exit_index = readme_lines.index(self.trigger_images_exit)
        return trigger_enter_index, trigger_exit_index

    def get_count_trigger_index(self, readme_lines) -> int:
        """
        Get the index of the count trigger in the README file.

        Args:
            readme_lines (list): The content of the README file as a list of lines.

        Returns:
            int: The index of the count trigger in the README file.

        Raises:
            ValueError: If the count trigger is not found.
        """
        count_index = -1
        for i, line in enumerate(readme_lines):
            if self.trigger_count_enter in line and self.trigger_count_exit in line:
                count_index = i
        if count_index == -1:
            raise ValueError("Count trigger not found")
        return count_index

    def get_filtered_images(self) -> 'list[str]':
        """
        Get a list of filtered images from the images directory.

        Returns:
            list: A list of filtered images.

        Note:
            The filtering criteria are images with extensions .png or .jpg and not starting with "_ignore".
        """
        images = [image for image in os.listdir(self.images_path) if
                  (image.endswith(".png") or image.endswith(".jpg")) and not image.startswith("_ignore")]
        return images

    def group_images_by_year(self, images) -> 'dict[str, list[str]]':
        """
        Group the images by year.

        Args:
            images (list): A list of images.

        Returns:
            dict: A dictionary where the keys are years and the values are lists of images.

        Note:
            The year is determined by the first part of the image name before the "-" character.
            If the image name does not contain a "-", the creation date of the image file is used.
        """
        images_by_year = {}
        for image in images:
            split = image.split("-")
            if len(split) < 2:
                creation_time = os.path.getctime(f"{self.images_path}/{image}")
                creation_date = datetime.datetime.fromtimestamp(creation_time)
                new_name = self.generate_new_name(image, creation_date)
                os.rename(f"{self.images_path}/{image}", f"{self.images_path}/{new_name}{os.path.splitext(image)[1]}")
                split = new_name.split("-")
            year = split[0]
            if year not in images_by_year:
                images_by_year[year] = []
            images_by_year[year].append(image)
        return images_by_year

    def generate_new_name(self, image, creation_date) -> str:
        """
        Generate a new name for the image based on its creation date.

        Args:
            image (str): The name of the image.
            creation_date (datetime.datetime): The creation date of the image.

        Returns:
            str: The new name for the image.

        Note:
            If a file with the same name already exists, a suffix "_0" is added to the new name.
            If multiple files with the same name exist, the suffix is incremented until a unique name is found.
        """
        new_name = f"{creation_date.year}-{creation_date.month:02}"
        if os.path.exists(f"{self.images_path}/{new_name}.png") or os.path.exists(f"{self.images_path}/{new_name}.jpg"):
            new_name = new_name + "_0"
            while os.path.exists(f"{self.images_path}/{new_name}.png") or os.path.exists(f"{self.images_path}/{new_name}.jpg"):
                new_name = new_name[:-1] + str(int(new_name[-1]) + 1)
        print(f"Renaming {image} to {new_name}{os.path.splitext(image)[1]}")
        return new_name

    def generate_output(self, readme_lines, trigger_enter_index, trigger_exit_index, count_index, images_by_year, images) -> None:
        """
        Generate the output for the README file.

        Args:
            readme_lines (list): The content of the README file as a list of lines.
            trigger_enter_index (int): The index of the trigger enter in the README file.
            trigger_exit_index (int): The index of the trigger exit in the README file.
            count_index (int): The index of the count trigger in the README file.
            images_by_year (dict): A dictionary where the keys are years and the values are lists of images.
            images (list): A list of images.
        """
        with open(self.readme_path, "w") as f:
            for line in readme_lines[:trigger_enter_index + 1]:
                f.write(line)

            f.write("| Preview | Year | Images |\n")
            f.write("|---|:---:|:---:|\n")

            for year in reversed(images_by_year):
                ims = images_by_year[year]
                file_name = f"images_{year}.md"
                with open(file_name, "w") as f_year:
                    f_year.write(f"# {year}\n\n")
                    f_year.write("| ")
                    for j in range(self.table_columns):
                        if j < len(images_by_year[year]):
                            f_year.write(f"![{images_by_year[year][j]}]({self.images_path}/{images_by_year[year][j]}) | ")
                    f_year.write("\n")
                    f_year.write("|---|---|---|\n")
                    for i in range(self.table_columns, len(images_by_year[year]), self.table_columns):
                        f_year.write("| ")
                        for j in range(self.table_columns):
                            if i + j < len(images_by_year[year]):
                                f_year.write(f"![{images_by_year[year][i + j]}]({self.images_path}/{images_by_year[year][i + j]}) | ")
                        f_year.write("\n")

                first_image = images_by_year[year][0]
                f.write(f"| [![{first_image}]({self.images_path}/{first_image})](./{file_name}) | ")
                f.write(f"<a href='./{file_name}'>{year}</a> | {len(images_by_year[year])} |\n")

            for line in readme_lines[trigger_exit_index:count_index]:
                f.write(line)

            count_line = readme_lines[count_index]
            splitup_s = count_line.split(self.trigger_count_enter)
            splitup_e = splitup_s[1].split(self.trigger_count_exit)
            f.write(splitup_s[0] + self.trigger_count_enter + str(len(images)) + self.trigger_count_exit + splitup_e[1])

            for line in readme_lines[count_index + 1:]:
                f.write(line)

# Usage
generator = ReadmeGenerator("README.md", "images")
generator.generate_readme()
