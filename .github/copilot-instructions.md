# Copilot Instructions for news-flash-website

## Project Architecture
- **Static site generator** for a blog
- **All HTML is generated locally** using Python scripts and Jinja2 templates; no server-side logic
- **Output is fully static** and deployed via GitHub Pages from the `/docs/` folder

## Tech Stack & Conventions

- **Python 3.11+** (automation/scripts), **Jinja2** (templating), **Markdown** (content), **Pillow/piexif/BeautifulSoup4** (image/content processing)
- **Plain CSS** only; no preprocessors, frameworks, or build tools
- **Vanilla JS** only; all scripts in `/js/`, no bundlers or frameworks
- **No PHP, React, Vue, Svelte, or server-side code**
- **Never edit `/docs/` directly**; always regenerate via scripts

## Folder Structure

- `/posts/` – Markdown blog posts (`YYYY-MM-DD-slug.md`), with required frontmatter (`title`, `date`, `tags`, `excerpt`)
- `/assets/images` – Local image assets; images referenced in posts must be present here
- `/templates/` – Jinja2 HTML templates (`blog-index.html`, `blog-post.html`, etc.)
- `/assets/css/` – Main stylesheet(s)
- `/assets/js/` – All JavaScript files (e.g., `modal.js`, `search.js`)
- `/docs/` – Build output for GitHub Pages (never hand-edit)

## Key Workflows

- **Create a new post:**  
  `python new_post.py` (prompts for metadata, copies image if provided)
- **Build the site:**  
  `python generate_blog.py` (generates all HTML, tag pages, pagination, search index)
- **Preview locally:**  
  Open `/docs/index.html` in Live Server or browser
- **Deploy:**  
  `git add . && git commit -m "…" && git push` (GitHub Pages auto-publishes from `/docs/`)

## Blog & Content Rules

- **Post filenames:** `YYYY-MM-DD-slug.md` (slug: lowercase, hyphens, ASCII)
- **Images:**  
  - Must be in `/images/`  
  - JPEGs resized ≤1600px, quality ~82, EXIF stripped  
  - `alt` text required
- **Output is deterministic:**  
  - Posts sorted by date (desc), then slug (asc)
  - Tag and index pages paginated as `/page-2.html`, `/tag-{tag}-2.html`, etc.

## HTML/CSS/JS Patterns

- **Semantic, minimal HTML**; mobile-first CSS (breakpoints: 768px, 1440px)
- **Fonts:** Space Grotesk, Inter, Courier New (code), Georgia (quotes)
- **Dark theme:** `# 202124`, AA contrast
- **No inline JS**; all scripts loaded from `/js/`
- **Modal:** Must support focus trap, ESC to close, ARIA attributes

## Integration Points

- **No external APIs or dynamic data sources**
- **All dependencies managed via `requirements.txt`**; install with `pip install -r requirements.txt`

## Agent Guidance

- **Never add new tech outside the allowed stack**
- **Ask for missing context before major changes**
- **Reference `/templates/` for HTML structure and `/css/` for styling conventions**
- **Scripts (`new_post.py`, `generate_blog.py`) are the only way to update content/output**