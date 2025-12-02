import os
import shutil
import markdown
import yaml
import datetime
from jinja2 import Environment, FileSystemLoader
from PIL import Image, ImageDraw, ImageFont

# Paths
POSTS_DIR = "posts"
TEMPLATES_DIR = "templates"
OUTPUT_POSTS_DIR = "docs/posts"
TAG_IMAGES_DIR = "assets/images/tags"

# Template filenames in templates/
INDEX_TEMPLATE_FILE = "index.html"
POST_TEMPLATE_FILE = "post.html"
TAG_TEMPLATE_FILE = "tag.html"
ABOUT_TEMPLATE_FILE = "about.html"

OUTPUT_INDEX_FILE = "docs/index.html"

# Color palette for tag images
TAG_COLORS = {
    "travel": "#FF6B6B",
    "food": "#FFD93D",
    "technology": "#6BCB77",
    "tech": "#6BCB77",
    "health": "#FF6B9D",
    "nature": "#4D96FF",
    "fitness": "#FFB4B4",
    "photography": "#A8E6CF",
    "productivity": "#FFD3B6",
    "social": "#FF8B94",
    "updates": "#A8D8EA",
    "launch": "#AA96DA",
    "github": "#2D2D2D",
    "tv": "#FF9F1C",
}

def generate_tag_image(tag_name, output_path, color=None):
    """Generate a tag image with text and gradient background"""
    # Use provided color or default from palette
    color = color or TAG_COLORS.get(tag_name.lower(), "#5F27CD")
    
    # Create image
    width, height = 400, 300
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)
    
    # Parse hex color to RGB
    color_hex = color.lstrip('#')
    r, g, b = tuple(int(color_hex[i:i+2], 16) for i in (0, 2, 4))
    
    # Draw gradient background
    for y in range(height):
        ratio = y / height
        r_grad = int(r * (1 - ratio * 0.3))
        g_grad = int(g * (1 - ratio * 0.3))
        b_grad = int(b * (1 - ratio * 0.3))
        draw.line([(0, y), (width, y)], fill=(r_grad, g_grad, b_grad))
    
    # Add tag name text
    tag_text = tag_name.upper()
    try:
        # Try to use a larger font if available
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 48)
    except:
        font = ImageFont.load_default()
    
    # Get text bbox to center it
    bbox = draw.textbbox((0, 0), tag_text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (width - text_width) // 2
    y = (height - text_height) // 2
    
    # Draw text with white color
    draw.text((x, y), tag_text, fill='white', font=font)
    
    # Save image
    img.save(output_path)
    print(f"✅ Generated tag image: {output_path}")

# Create tag images directory if it doesn't exist
os.makedirs(TAG_IMAGES_DIR, exist_ok=True)

# Setup Jinja2
env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))

# Load templates
post_template = env.get_template(POST_TEMPLATE_FILE)
index_template = env.get_template(INDEX_TEMPLATE_FILE)
tag_template = env.get_template(TAG_TEMPLATE_FILE)
about_template = env.get_template(ABOUT_TEMPLATE_FILE)

# Read all markdown posts
all_posts = []

for filename in os.listdir(POSTS_DIR):
    if filename.endswith(".md"):
        filepath = os.path.join(POSTS_DIR, filename)
        with open(filepath, "r") as f:
            content = f.read()

        # Split YAML frontmatter and markdown body
        parts = content.split("---")
        if len(parts) < 3:
            continue

        metadata = yaml.safe_load(parts[1])
        body_markdown = "---".join(parts[2:]).strip()

        # Format date
        raw_date = metadata.get("date")
        if isinstance(raw_date, datetime.date):
            formatted_date = raw_date.strftime("%-d %B %Y")
        else:
            formatted_date = datetime.datetime.strptime(raw_date, "%Y-%m-%d").strftime("%-d %B %Y")

        # Convert markdown to HTML
        html_body = markdown.markdown(body_markdown)

        # Create excerpt
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(html_body, 'html.parser')

        # Remove all heading tags
        for tag in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
            tag.decompose()

        # Remove all links but keep the text
        for a in soup.find_all('a'):
            a.unwrap()

        # Find the first non-empty paragraph with text
        first_para = None
        for p in soup.find_all('p'):
            # Remove images from paragraph
            for img in p.find_all('img'):
                img.decompose()
            # Check if paragraph has non-whitespace text
            if p.get_text(strip=True):
                first_para = p
                break

        if first_para:
            words = first_para.get_text().strip().split()
            truncated_text = ' '.join(words[:30]) + '...'
            new_para = soup.new_tag("p")
            new_para.string = truncated_text
            excerpt = str(new_para)
        else:
            excerpt = ""

        slug = metadata["slug"]

        # Warn if image path is not a URL
        image_path = metadata.get("image", "")
        if image_path and not (image_path.startswith("http") or image_path.startswith("/")):
            print(f"ℹ️  Note: Post '{metadata.get('title', 'Untitled')}' uses a relative image path: {image_path}")

        # Calculate read time (rough estimate: 200 words per minute)
        word_count = len(html_body.split())
        read_time_minutes = max(1, round(word_count / 200))
        read_time = f"{read_time_minutes} min read"

        # Build post object
        post = {
            "title": metadata["title"],
            "date": formatted_date,
            "slug": slug,
            "category": metadata.get("category", "News"),
            "tags": metadata.get("tags", []),
            "image": image_path,
            "image_alt": metadata.get("image_alt", ""),
            "body": html_body,
            "excerpt": excerpt,
            "read_time": read_time,
            "url": f"posts/{slug}.html",     # used by blog index
            "filename": f"{slug}.html",      # used by post navigation
        }

        all_posts.append(post)

# Sort posts by date (newest first)
all_posts.sort(key=lambda x: datetime.datetime.strptime(x["date"], "%d %B %Y"), reverse=True)

# Pagination setup
POSTS_PER_PAGE = 8

# Split posts into chunks
def chunk_posts(posts, size):
    return [posts[i:i + size] for i in range(0, len(posts), size)]

paginated_posts = chunk_posts(all_posts, POSTS_PER_PAGE)

# Add prev/next post objects
for i, post in enumerate(all_posts):
    post["prev_post"] = all_posts[i - 1] if i > 0 else None
    post["next_post"] = all_posts[i + 1] if i < len(all_posts) - 1 else None
    # Keep URL versions for backward compatibility
    post["prev_url"] = all_posts[i - 1]["filename"] if i > 0 else None
    post["next_url"] = all_posts[i + 1]["filename"] if i < len(all_posts) - 1 else None

# Clear out old blog post HTML files
if os.path.exists(OUTPUT_POSTS_DIR):
    for f in os.listdir(OUTPUT_POSTS_DIR):
        if f.endswith(".html"):
            os.remove(os.path.join(OUTPUT_POSTS_DIR, f))

# Ensure output directory exists
os.makedirs(OUTPUT_POSTS_DIR, exist_ok=True)

# Render blog posts
for post in all_posts:
    output_html = post_template.render(post=post)
    output_path = os.path.join(OUTPUT_POSTS_DIR, post["filename"])
    with open(output_path, "w") as f:
        f.write(output_html)

# Render paginated blog index pages
total_pages = len(paginated_posts)

for i, posts_on_page in enumerate(paginated_posts):
    page_num = i + 1
    is_first = page_num == 1
    is_last = page_num == total_pages

    pagination = {
        "current": page_num,
        "total": total_pages,
        "prev_page": None if is_first else (f"index.html" if page_num == 2 else f"page-{page_num - 1}.html"),
        "next_page": None if is_last else f"page-{page_num + 1}.html",
        "page_numbers": list(range(1, total_pages + 1)),
    }

    # Prepare category data for index
    featured_posts = all_posts[:3] if is_first else []
    trending_posts = all_posts[:5] if is_first else []
    quick_read_posts = all_posts[:6] if is_first else []
    older_posts = posts_on_page
    
    # Extract popular tags
    tag_counts = {}
    for post in all_posts:
        for tag in post["tags"]:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1
    
    # Sort tags by frequency and get top 6
    popular_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:6]
    
    # Generate tag images for popular tags (if they don't exist)
    for tag, count in popular_tags:
        tag_slug = tag.lower().replace(" ", "-")
        tag_image_path = os.path.join(TAG_IMAGES_DIR, f"{tag_slug}-tag.jpg")
        if not os.path.exists(tag_image_path):
            generate_tag_image(tag, tag_image_path)
    
    # Build popular tags data with generated image paths
    popular_tags_data = [
        {
            "name": tag,
            "image": f"./assets/images/tags/{tag.lower().replace(' ', '-')}-tag.jpg"
        } 
        for tag, count in popular_tags
    ]

    rendered_html = index_template.render(
        posts=posts_on_page,
        pagination=pagination,
        featured_posts=featured_posts,
        trending_posts=trending_posts,
        quick_read_posts=quick_read_posts,
        older_posts=older_posts,
        popular_tags=popular_tags_data,
        featured_headline="Latest news updates..."
    )

    output_filename = "index.html" if is_first else f"page-{page_num}.html"
    output_path = os.path.join("docs", output_filename)

    with open(output_path, "w") as f:
        f.write(rendered_html)

# Group posts by tag
from collections import defaultdict
tag_map = defaultdict(list)
for post in all_posts:
    for tag in post['tags']:
        tag_map[tag].append(post)

# Generate paginated tag pages
for tag, posts in tag_map.items():
    tag_slug = tag.lower().replace(" ", "-")
    tag_paginated = chunk_posts(posts, POSTS_PER_PAGE)
    total_tag_pages = len(tag_paginated)

    for i, posts_on_page in enumerate(tag_paginated):
        page_num = i + 1
        is_first = page_num == 1
        is_last = page_num == total_tag_pages

        # Pagination dict for tag pages
        pagination = {
            "current": page_num,
            "total": total_tag_pages,
            "prev_page": None if is_first else (
                f"tag-{tag_slug}.html" if page_num == 2 else f"tag-{tag_slug}-{page_num-1}.html"
            ),
            "next_page": None if is_last else f"tag-{tag_slug}-{page_num+1}.html",
            "page_numbers": list(range(1, total_tag_pages + 1)),
        }

        output_filename = f"tag-{tag_slug}.html" if is_first else f"tag-{tag_slug}-{page_num}.html"
        tag_output_path = os.path.join("docs", output_filename)
        with open(tag_output_path, "w") as f:
            f.write(tag_template.render(tag=tag, posts=posts_on_page, pagination=pagination))

import shutil

# Render the About page from template (static content)
about_output_path = os.path.join("docs", "about.html")
with open(about_output_path, "w") as f:
    f.write(about_template.render())

# Copy all assets (css, js, images) into docs/assets for the generated site
ASSETS_SRC = "assets"
ASSETS_DEST = os.path.join("docs", "assets")

if os.path.exists(ASSETS_DEST):
    shutil.rmtree(ASSETS_DEST)

shutil.copytree(ASSETS_SRC, ASSETS_DEST)
print("✅ Assets copied to docs/assets/")

# --------------------------------------------
# Generate search.json
# --------------------------------------------

import json

search_data = []
for post in all_posts:
    search_data.append({
        "title": post['title'],
        "excerpt": post['excerpt'],
        "url": f"/{post['url'].lstrip('/')}",  # ✅ Force absolute URL
        "image": post['image'],
        "image_alt": post['image_alt'],
        "tags": post['tags']
    })

search_path = os.path.join("docs", "search.json")
with open(search_path, "w", encoding="utf-8") as f:
    json.dump(search_data, f, ensure_ascii=False, indent=2)

print(f"✅ search.json written to {search_path}")
