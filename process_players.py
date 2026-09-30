from pathlib import Path
from rembg import remove, new_session
from PIL import Image
from concurrent.futures import ThreadPoolExecutor, as_completed
import io
import os

# ============================================================
# SETTINGS
# ============================================================

INPUT_DIR = Path(".")
OUTPUT_DIR = Path("processed_players")

OUTPUT_DIR.mkdir(exist_ok=True)

SUPPORTED = {".jpg", ".jpeg", ".png", ".webp"}

# Number of images processed simultaneously.
# Start with 4. If your laptop handles it well, try 6.
WORKERS = 4

# Final image size
FINAL_SIZE = 320

# WebP quality
WEBP_QUALITY = 95


# ============================================================
# LOAD REMBG MODEL ONCE
# ============================================================

print("=" * 65)
print("FAST IPL PLAYER IMAGE PROCESSOR")
print("=" * 65)

print("\nLoading background-removal model...")
session = new_session("u2net")
print("Model loaded successfully.")


# ============================================================
# FIND IMAGES
# ============================================================

images = [
    file for file in INPUT_DIR.iterdir()
    if file.is_file()
    and file.suffix.lower() in SUPPORTED
]

print(f"\nImages found: {len(images)}")
print(f"Workers: {WORKERS}")
print(f"Final size: {FINAL_SIZE}x{FINAL_SIZE}")
print("Format: WebP")
print("Background: White")

print("=" * 65)


# ============================================================
# PROCESS ONE IMAGE
# ============================================================

def process_image(image_path):

    output_path = OUTPUT_DIR / f"{image_path.stem}.webp"

    # Skip if already processed
    if output_path.exists():
        return (
            image_path.name,
            "SKIPPED",
            "Already exists"
        )

    try:

        # ----------------------------------------------------
        # READ IMAGE
        # ----------------------------------------------------

        with open(image_path, "rb") as f:
            input_data = f.read()

        # ----------------------------------------------------
        # REMOVE BACKGROUND
        # ----------------------------------------------------

        output_data = remove(
            input_data,
            session=session
        )

        image = Image.open(
            io.BytesIO(output_data)
        ).convert("RGBA")

        # ----------------------------------------------------
        # WHITE BACKGROUND
        # ----------------------------------------------------

        white = Image.new(
            "RGB",
            image.size,
            (255, 255, 255)
        )

        white.paste(
            image,
            mask=image.getchannel("A")
        )

        # ----------------------------------------------------
        # MAKE 1:1 SQUARE
        # ----------------------------------------------------

        width, height = white.size

        square_size = max(width, height)

        square = Image.new(
            "RGB",
            (square_size, square_size),
            (255, 255, 255)
        )

        x = (square_size - width) // 2
        y = (square_size - height) // 2

        square.paste(
            white,
            (x, y)
        )

        # ----------------------------------------------------
        # RESIZE
        # ----------------------------------------------------

        square = square.resize(
            (FINAL_SIZE, FINAL_SIZE),
            Image.Resampling.LANCZOS
        )

        # ----------------------------------------------------
        # SAVE WEBP
        # ----------------------------------------------------

        square.save(
            output_path,
            "WEBP",
            quality=WEBP_QUALITY,
            method=6
        )

        return (
            image_path.name,
            "SUCCESS",
            output_path.name
        )

    except Exception as e:

        return (
            image_path.name,
            "FAILED",
            str(e)
        )


# ============================================================
# PROCESS IN PARALLEL
# ============================================================

successful = 0
failed = 0
skipped = 0

print("\nStarting processing...\n")

with ThreadPoolExecutor(max_workers=WORKERS) as executor:

    futures = {
        executor.submit(process_image, image): image
        for image in images
    }

    completed = 0

    for future in as_completed(futures):

        completed += 1

        filename, status, message = future.result()

        if status == "SUCCESS":

            successful += 1

            print(
                f"[{completed}/{len(images)}] "
                f"✓ {filename} → {message}"
            )

        elif status == "SKIPPED":

            skipped += 1

            print(
                f"[{completed}/{len(images)}] "
                f"↷ {filename} → already processed"
            )

        else:

            failed += 1

            print(
                f"[{completed}/{len(images)}] "
                f"✗ {filename}"
            )

            print(
                f"    Error: {message}"
            )


# ============================================================
# FINAL SUMMARY
# ============================================================

print("\n")
print("=" * 65)
print("PROCESSING FINISHED")
print("=" * 65)

print(f"Images found : {len(images)}")
print(f"Successful   : {successful}")
print(f"Skipped      : {skipped}")
print(f"Failed       : {failed}")

print(f"\nOutput folder:")
print(OUTPUT_DIR.resolve())

print("=" * 65)

