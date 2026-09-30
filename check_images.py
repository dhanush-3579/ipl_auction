from pathlib import Path
from PIL import Image

INPUT_DIR = Path(".")
SUPPORTED = {".jpg", ".jpeg", ".png", ".webp"}

total = 0
webp_ok = 0
square_ok = 0
white_bg_ok = 0
failed = []

for file in INPUT_DIR.iterdir():

    if not file.is_file() or file.suffix.lower() not in SUPPORTED:
        continue

    total += 1

    try:
        with Image.open(file) as img:
            width, height = img.size

            # 1. Check WEBP
            is_webp = file.suffix.lower() == ".webp"
            if is_webp:
                webp_ok += 1

            # 2. Check 1:1
            is_square = width == height
            if is_square:
                square_ok += 1

            # 3. Check white background
            rgb = img.convert("RGB")

            corners = [
                rgb.getpixel((0, 0)),
                rgb.getpixel((width - 1, 0)),
                rgb.getpixel((0, height - 1)),
                rgb.getpixel((width - 1, height - 1))
            ]

            # Allow tiny compression differences
            is_white_bg = all(
                r >= 245 and g >= 245 and b >= 245
                for r, g, b in corners
            )

            if is_white_bg:
                white_bg_ok += 1

            if not (is_webp and is_square and is_white_bg):
                failed.append({
                    "file": file.name,
                    "size": f"{width}x{height}",
                    "webp": is_webp,
                    "white_corners": is_white_bg
                })

    except Exception as e:
        failed.append({
            "file": file.name,
            "error": str(e)
        })


print("\n" + "=" * 60)
print("IMAGE CHECK COMPLETE")
print("=" * 60)

print(f"Total images       : {total}")
print(f"WEBP format        : {webp_ok}/{total}")
print(f"1:1 ratio          : {square_ok}/{total}")
print(f"White background   : {white_bg_ok}/{total}")

print("\n" + "=" * 60)

if not failed:
    print("✅ ALL IMAGES PASSED ALL 3 CHECKS!")
else:
    print(f"❌ {len(failed)} image(s) need checking.")
    print("\nProblematic files:")

    for item in failed:
        print("-" * 50)
        print(item)

print("=" * 60)