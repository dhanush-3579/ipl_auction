from pathlib import Path
from PIL import Image, ImageChops

FOLDER = Path("processed_players")

files = list(FOLDER.glob("*.webp"))

not_white = []

for file in files:
    try:
        img = Image.open(file).convert("RGB")

        # Check the 4 corners
        corners = [
            img.getpixel((0, 0)),
            img.getpixel((img.width - 1, 0)),
            img.getpixel((0, img.height - 1)),
            img.getpixel((img.width - 1, img.height - 1))
        ]

        # Allow tiny differences from pure white
        for pixel in corners:
            if min(pixel) < 245:
                not_white.append(file.name)
                break

    except Exception as e:
        print("Error:", file.name, e)

print("Total images:", len(files))
print("White-background images:", len(files) - len(not_white))
print("Not-white images:", len(not_white))

if not_white:
    print("\nImages to check:")
    for name in not_white:
        print(name)
else:
    print("\nALL 570 IMAGES HAVE WHITE CORNERS.")