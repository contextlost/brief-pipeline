"""Render an edition as clean, semantic HTML (reader-mode friendly)."""
import html

CSS = """
body{font-family:-apple-system,system-ui,sans-serif;line-height:1.6;margin:0;
color:#1d1d1f;background:#fff}
@media(prefers-color-scheme:dark){body{color:#f5f5f7;background:#000}}
article{max-width:42rem;margin:0 auto;padding:1.5rem}
h1{font-size:1.4rem}h2{font-size:1.1rem;margin-top:2rem}
li{margin-bottom:.4rem}a{color:inherit}
.meta{color:#86868b;font-size:.85rem}
"""


def render_html(edition):
    paras = "\n".join(f"<p>{html.escape(p)}</p>" for p in edition["paragraphs"])
    refs = "\n".join(
        '<li><a href="{link}">{title}</a> &mdash; {outlet}</li>'.format(
            link=html.escape(r["link"] or "#", quote=True),
            title=html.escape(r["title"]), outlet=html.escape(r["outlet"]))
        for r in edition["references"]
    )
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Brief &mdash; {html.escape(edition['date'])}</title>
<style>{CSS}</style>
</head>
<body>
<article>
<h1>Brief &mdash; {html.escape(edition['date'])}</h1>
<p class="meta">Written by the {html.escape(edition['narrator'])} narrator.
{edition['counts']['stories']} stories from {edition['counts']['items']} items.</p>
{paras}
<h2>References</h2>
<ol>
{refs}
</ol>
</article>
</body>
</html>
"""
