from pathlib import Path
from PIL import Image

FOLDER = Path("processed_players")

files = list(FOLDER.glob("*.webp"))

print("=" * 60)
print("RESIZING PROCESSED IPL IMAGES")
print("=" * 60)
print(f"WebP files found: {len(files)}")

success = 0
failed = 0

for i, file in enumerate(files, 1):
    try:
        with Image.open(file) as img:

            # Already correct
            if img.size == (320, 320):
                print(f"[{i}/{len(files)}] SKIP: {file.name}")
                continue

            # Resize existing processed image
            img = img.convert("RGB")
            img = img.resize(
                (320, 320),
                Image.Resampling.LANCZOS
            )

            img.save(
                file,
                "WEBP",
                quality=95,
                method=6
            )

            print(f"[{i}/{len(files)}] ✓ {file.name}")
            success += 1

    except Exception as e:
        print(f"[{i}/{len(files)}] ✗ {file.name}")
        print(f"    {e}")
        failed += 1

print("\n" + "=" * 60)
print("RESIZE FINISHED")
print("=" * 60)
print(f"Resized : {success}")
print(f"Skipped : {len(files) - success - failed}")
print(f"Failed  : {failed}")
print("=" * 60)