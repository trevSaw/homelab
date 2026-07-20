# Self-Hosting Documentation Guide

This Markdown file contains all recommendations and tools for creating clean, navigable documentation for Docker, self-hosting, and technical setups.

---

## 🛠️ Recommended Tools

### 1. MkDocs (Best for Simplicity)

- Converts Markdown to a full documentation site.
- Supports images, TOC, search, and themes.
- Use with **Material theme** for professional design.

**Install:**

```bash
pip install mkdocs mkdocs-material
```

**Config (mkdocs.yml):**

```yaml
site_name: My Self-Hosted Stack
theme:
  name: material
nav:
  - Home: index.md
  - Setup: setup.md
  - Backup: backup.md
```

---

### 2. Docusaurus (Best for Large Projects)

- Facebook-built static site generator.
- Supports versioning, i18n, and Algolia search.
- Great for team collaboration.

**Website:** [docusaurus.io](https://docusaurus.io)

---

### 3. Docsify (Zero Build, Dynamic Loading)

- No static build — loads `.md` files on demand.
- Ideal for quick, lightweight docs.

**Website:** [docsify.js.org](https://docsify.js.org)

---

### 4. Pandoc (Best for Offline/Portable HTML)

- CLI tool to convert Markdown to HTML, PDF, DOCX.
- Preserves formatting and images.

**Example Command:**

```bash
pandoc -s --toc -o docs.html *.md
```

**Template Suggestion:** [easy-pandoc-templates](https://github.com/ryangrose/easy-pandoc-templates)

---

### 5. StackEdit (Best Browser Editor)

- Free, offline-capable Markdown editor.
- Export to Styled HTML with TOC.
- Supports image embedding.

**Website:** [stackedit.io](https://stackedit.io)

---

## 🖼️ Adding Screenshots

Use standard Markdown syntax:

```markdown
![Portainer Dashboard](img/portainer.png)
```

Keep images in an `img/` folder alongside your `.md` files.

---

## 📁 Project Structure

```
docs/
├── mkdocs.yml
├── docs/
│   ├── index.md
│   ├── setup.md
│   └── backup.md
└── img/
    └── portainer.png
```

---

## 🚀 Quick Start

1. Write docs in Markdown.
2. Choose a tool (e.g., MkDocs).
3. Run `mkdocs serve` to preview.
4. Run `mkdocs build` to deploy.

---

> ✅ **Tip:** Use GitHub Pages or a static host (e.g., Netlify, VPS) to publish your docs online.
 