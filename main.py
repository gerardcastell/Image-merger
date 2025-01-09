# group_images_service.py

import io
from enum import Enum
from PIL import Image


class MergeOrientation(Enum):
    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"


class GroupImagesInputDTO:
    """
    Class containing the data necessary to generate merge two images.
    """

    def __init__(self, first_image_in_bytes: bytes, second_image_in_bytes: bytes, orientation: MergeOrientation):
        self.first_image_in_bytes = first_image_in_bytes
        self.second_image_in_bytes = second_image_in_bytes
        self.orientation = orientation


class GroupImagesService:
    """
    Service in charge of grouping two images into a single image.
    """

    def __call__(self, input_data: GroupImagesInputDTO) -> bytes:
        """
        Merge two images based on the specified merge type and return the resulting image.
        """
        # Retrieve images from bytes
        image1 = Image.open(io.BytesIO(input_data.first_image_in_bytes))
        image2 = Image.open(io.BytesIO(input_data.second_image_in_bytes))

        # Merge the images depending on the orientation
        if input_data.orientation == MergeOrientation.VERTICAL:
            merged_image = self._merge_images_vertically(image1, image2)
        elif input_data.orientation == MergeOrientation.HORIZONTAL:
            merged_image = self._merge_images_horizontally(image1, image2)
        else:
            raise ValueError("Unsupported merge orientation")

        # Return the bytes of the resulting image
        return self._image_to_bytes(merged_image)

    def _merge_images_vertically(self, image1, image2):
        """
        Merge two images vertically (one below the other) and return the resulting image.
        """
        max_width = max(image1.width, image2.width)
        image1 = image1.resize(
            (max_width, int(image1.height * max_width / image1.width)), Image.Resampling.LANCZOS
        )
        image2 = image2.resize(
            (max_width, int(image2.height * max_width / image2.width)), Image.Resampling.LANCZOS
        )

        combined_height = image1.height + image2.height
        result = Image.new("RGB", (max_width, combined_height))

        result.paste(image1, (0, 0))
        result.paste(image2, (0, image1.height))

        return result

    def _merge_images_horizontally(self, image1, image2):
        """
        Merge two images side by side horizontally and return the resulting image.
        """
        max_height = max(image1.height, image2.height)
        image1 = image1.resize(
            (int(image1.width * max_height / image1.height), max_height), Image.Resampling.LANCZOS
        )
        image2 = image2.resize(
            (int(image2.width * max_height / image2.height), max_height), Image.Resampling.LANCZOS
        )

        combined_width = image1.width + image2.width
        result = Image.new("RGB", (combined_width, max_height))

        result.paste(image1, (0, 0))
        result.paste(image2, (image1.width, 0))

        return result

    def _image_to_bytes(self, image) -> bytes:
        """
        Convert a Pillow Image object to bytes.
        """
        buffer = io.BytesIO()
        image.save(buffer, format="JPEG", quality=85)
        buffer.seek(0)
        return buffer.getvalue()


# Example usage (uncomment to test):
if __name__ == "__main__":
    with open("image_1.jpg", "rb") as img1, open("image_2.jpg", "rb") as img2:
        first_image_bytes = img1.read()
        second_image_bytes = img2.read()
        orientation = MergeOrientation.VERTICAL
        input_data = GroupImagesInputDTO(first_image_bytes, second_image_bytes, orientation)
        service = GroupImagesService()
        merged_image_bytes = service(input_data)
        with open("merged_image.jpeg", "wb") as merged_img_file:
            merged_img_file.write(merged_image_bytes)