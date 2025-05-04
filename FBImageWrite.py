from PIL import Image
import numpy as np

# Framebuffer device and resolution
fb_path = "/dev/fb0"
screen_width = 240
screen_height = 240

# Load and resize your image
# Center Image
image = Image.open("DirectionGrahic.png").convert("RGB")
imageCenter = image.rotate(0, expand=True)
imageCenter = imageCenter.resize((screen_width, screen_height))

# Convert to RGB565 format
rgb_array = np.array(imageCenter)
r = (rgb_array[:, :, 0] >> 3).astype(np.uint16)
g = (rgb_array[:, :, 1] >> 2).astype(np.uint16)
b = (rgb_array[:, :, 2] >> 3).astype(np.uint16)
rgb565 = (r << 11) | (g << 5) | b
rgb565_bytesCenter = rgb565.flatten().tobytes()

# Right
imageRight = image.rotate(-60, expand=False)
imageRight = imageRight.resize((screen_width, screen_height))

# Convert to RGB565 format
rgb_array = np.array(imageRight)
r = (rgb_array[:, :, 0] >> 3).astype(np.uint16)
g = (rgb_array[:, :, 1] >> 2).astype(np.uint16)
b = (rgb_array[:, :, 2] >> 3).astype(np.uint16)
rgb565 = (r << 11) | (g << 5) | b
rgb565_bytesRight = rgb565.flatten().tobytes()

# Left
imageLeft = image.rotate(60, expand=False)
imageLeft = imageLeft.resize((screen_width, screen_height))

# Convert to RGB565 format
rgb_array = np.array(imageLeft)
r = (rgb_array[:, :, 0] >> 3).astype(np.uint16)
g = (rgb_array[:, :, 1] >> 2).astype(np.uint16)
b = (rgb_array[:, :, 2] >> 3).astype(np.uint16)
rgb565 = (r << 11) | (g << 5) | b
rgb565_bytesLeft = rgb565.flatten().tobytes()



def WriteToDisplay(rotation: str = 'Center'):

    if rotation == 'Center':
        # Write image data to framebuffer
        with open(fb_path, "wb") as f:
            f.write(rgb565_bytesCenter)
    elif rotation == 'Left':
        # Write image data to framebuffer
        with open(fb_path, "wb") as f:
            f.write(rgb565_bytesLeft)
    elif rotation == 'Right':
        # Write image data to framebuffer
        with open(fb_path, "wb") as f:
            f.write(rgb565_bytesRight)

if __name__ == "__main__":
    WriteToDisplay('Center')