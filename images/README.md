# Images

Source images for the site live in this folder. `python3 -B scripts/site/sync.py --write` copies them into `docs/assets/images/`, which the sync tool owns. Never edit that folder by hand. The tools need Python 3.10 or newer. The full rules are in the [authoring conventions](../docs/contributing/authoring-conventions.md).

## Naming

- Use lowercase letters, digits, hyphens, underscores, and dots, then the file extension, as in `pipeline-overview.svg`. A name with a space or a capital letter stops the sync tool with `sync: <path>: image names may use only a-z, 0-9, '.', '_', '-' and '/'` and exit status 2.
- Name what the image shows. Do not use a bare number, or the name of the page that uses it.
- The sync tool copies files that end in `.svg`, `.png`, `.jpg`, `.jpeg`, `.gif`, or `.webp`. It ignores other files, such as this README. A subfolder is copied with its path.

## Format

- Use SVG first. It stays sharp at any size, and it is plain text, so changes are easy to review in a pull request.
- Use another format, such as PNG, only when SVG cannot do the job. A screenshot is one example.
- Give each SVG a `<title>` and a `<desc>` element, so the file makes sense on its own. The page still needs alt text, as described next.

## Alt text

Write the alt text where the image is used, in the page's Markdown. Do not store it in this folder. The alt text says what the image tells the reader. The checker reports a missing image file and empty alt text.

```markdown
![Alt text that says what the image shows](../assets/images/pipeline-overview.svg)
```

The path is relative to the page. A page in `docs/contributing/` reaches the copy at `../assets/images/`. A page directly in `docs/` uses `assets/images/`. Never start the path with a slash.

For a diagram, also give a visible text version of the same information next to it, such as a list or a table. Do not rely on the image alone.

## No decorative images

Add an image only when it carries information the reader needs. If the page reads the same without it, leave it out. The checker cannot tell whether an image is decorative, because it only reports missing files and empty alt text. Checking this is up to you and your reviewer.

## Licensing and privacy

- Use only images you made yourself, or images that are already in the public domain or under CC0. Everything in this repository is released under CC0. See [Contributing](../docs/contributing/index.md).
- Do not put personal data, file paths from your own computer, or keys in an image, in its text, or in a screenshot. The checker scans SVG files for forbidden strings.

## How an image reaches the site

1. Save the source file in this folder.
2. Run `python3 -B scripts/site/sync.py` to preview the copy. It writes nothing.
3. Run `python3 -B scripts/site/sync.py --write` to copy the file into `docs/assets/images/`.
4. Reference the copy from a page with Markdown, as shown above.
5. Run `python3 -B scripts/site/check.py`.
