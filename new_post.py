import os
from datetime import date
import re

# Prompt user for inputs
title = input("Post title: ").strip()
category = input("Category [News]: ").strip() or "News"
tags = input("Tags (comma separated): ").strip()
image_input = input("Image path [https://ik.imagekit.io/1wh3oo1zp/larrie-knighs-default_lhSm1y4Pb]: ").strip()
image = image_input if image_input else "https://ik.imagekit.io/1wh3oo1zp/larrie-knighs-default_lhSm1y4Pb"
image_alt = input("Image alt text: ").strip()

# Validate image URL
if not image.startswith("http"):
    print("⚠️  Warning: This image path is not a URL. Consider uploading your image to ImageKit or another host.")

# Generate date and slug
today = date.today().isoformat()
slug = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')
filename = f"{today}-{slug}"
filepath = f"posts/{filename}.md"

# Format frontmatter
frontmatter = f"""---
title: {title}
date: {today}
slug: {filename}
category: {category}
tags: [{', '.join(t.strip() for t in tags.split(','))}]
image: {image}
image_alt: {image_alt}
---

Start writing your post here..."""

# Write to file
os.makedirs("posts", exist_ok=True)
with open(filepath, "w") as f:
    f.write(frontmatter)

print(f"✓ Created new post: {filepath}")
