from PIL import Image, ImageDraw, ImageFont
import numpy as np

# Framebuffer device and resolution
fb_path = "/dev/fb0"
screen_width = 240
screen_height = 240

# Load and resize your image
image = Image.open("DirectionGrahic.png").convert("RGB")

# Center
imageCenter = image.rotate(0, expand=True)
imageCenter = imageCenter.resize((screen_width, screen_height))


# Right
imageRight = image.rotate(-60, expand=False)
imageRight = imageRight.resize((screen_width, screen_height))


# Left
imageLeft = image.rotate(60, expand=False)
imageLeft = imageLeft.resize((screen_width, screen_height))


try:
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
except IOError:
    font = ImageFont.load_default()


def WriteToDisplay(rotation: str = 'Center', classifiedAlert: str = ''):
    global imageCenter, imageLeft, imageRight
    if rotation == 'Center':
        tempImageCenter = imageCenter.copy()
        # Draw text on the image
        draw = ImageDraw.Draw(tempImageCenter)

        # Position (x, y), text content, font, and color
        draw.text((80, 120), classifiedAlert, font=font, fill="red")

        # Convert to RGB565 format
        rgb_array = np.array(tempImageCenter)
        r = (rgb_array[:, :, 0] >> 3).astype(np.uint16)
        g = (rgb_array[:, :, 1] >> 2).astype(np.uint16)
        b = (rgb_array[:, :, 2] >> 3).astype(np.uint16)
        rgb565 = (r << 11) | (g << 5) | b
        rgb565_bytes = rgb565.flatten().tobytes()

        # Write image data to framebuffer
        with open(fb_path, "wb") as f:
            f.write(rgb565_bytes)

    elif rotation == 'Left':
        tempImageLeft = imageLeft.copy()
        # Draw text on the image
        draw = ImageDraw.Draw(tempImageLeft)

        # Position (x, y), text content, font, and color
        draw.text((80, 120), classifiedAlert, font=font, fill="red")

        # Convert to RGB565 format
        rgb_array = np.array(tempImageLeft)
        r = (rgb_array[:, :, 0] >> 3).astype(np.uint16)
        g = (rgb_array[:, :, 1] >> 2).astype(np.uint16)
        b = (rgb_array[:, :, 2] >> 3).astype(np.uint16)
        rgb565 = (r << 11) | (g << 5) | b
        rgb565_bytes = rgb565.flatten().tobytes()

        # Write image data to framebuffer
        with open(fb_path, "wb") as f:
            f.write(rgb565_bytes)

    elif rotation == 'Right':
        tempImageRight = imageRight.copy()
        # Draw text on the image
        draw = ImageDraw.Draw(tempImageRight)

        # Position (x, y), text content, font, and color
        draw.text((80, 120), classifiedAlert, font=font, fill="red")

        # Convert to RGB565 format
        rgb_array = np.array(tempImageRight)
        r = (rgb_array[:, :, 0] >> 3).astype(np.uint16)
        g = (rgb_array[:, :, 1] >> 2).astype(np.uint16)
        b = (rgb_array[:, :, 2] >> 3).astype(np.uint16)
        rgb565 = (r << 11) | (g << 5) | b
        rgb565_bytes = rgb565.flatten().tobytes()

        # Write image data to framebuffer
        with open(fb_path, "wb") as f:
            f.write(rgb565_bytes)


if __name__ == "__main__":
    WriteToDisplay('Center')