"""Turn ranked story clusters into a brief: narrative + citations + references.

Editorial rules encoded here (distilled from a real news-brief pipeline):
- Narrate each duplicated event ONCE, however many outlets cover it.
- Inline numbered citations on factual claims.
- A literal References section listing every cited link.
- Diff against the prior edition: genuinely new developments lead.

The Narrator protocol is one method:
    narrate(new_stories, continuing_stories) -> {"paragraphs": [...], "references": [...]}
"""
import json
import urllib.request


class ExtractiveNarrator:
    """No LLM, no keys. Mechanical but fully transparent."""

    name = "extractive"

    def narrate(self, new_stories, continuing_stories):
        refs, index = [], {}

        def cite(item):
            key = item["link"] or item["title"]
            if key not in index:
                index[key] = len(refs) + 1
                refs.append({"n": len(refs) + 1, "title": item["title"],
                             "outlet": item["outlet"], "link": item["link"]})
            return f"[{index[key]}]"

        def sentence(story):
            lead = story[0]
            outlets = sorted({i["outlet"] for i in story})
            coverage = (f"covered by {len(outlets)} outlets" if len(outlets) > 1
                        else f"reported by {outlets[0]}")
            cites = "".join(cite(i) for i in story[:4])
            return f"{lead['title']} ({coverage}){cites}."

        paragraphs = []
        if new_stories:
            paragraphs.append("New since the last edition: " +
                              " ".join(sentence(s) for s in new_stories[:4]))
        else:
            paragraphs.append("No major new developments since the last edition.")
        if continuing_stories:
            paragraphs.append("Continuing: " +
                              " ".join(sentence(s) for s in continuing_stories[:4]))
        rest = new_stories[4:] + continuing_stories[4:]
        if rest:
            paragraphs.append("Also: " + " ".join(sentence(s) for s in rest[:6]))
        return {"paragraphs": paragraphs, "references": refs}


class LLMNarrator:
    """Calls an OpenAI-compatible chat API. Bring your own key via env."""

    name = "llm"

    SYSTEM = ("You write a 3-paragraph news brief in English. Rules: narrate each "
              "event once no matter how many outlets cover it; put inline numbered "
              "citations like [1] on factual claims; end with a literal 'References:' "
              "section listing each cited link. New developments first.")

    def __init__(self, llm_config):
        self.cfg = llm_config

    def narrate(self, new_stories, continuing_stories):
        if not self.cfg.get("api_key"):
            raise RuntimeError("LLM_API_KEY is not set")
        payload = {
            "model": self.cfg.get("model") or "gpt-4o-mini",
            "temperature": 0.3,
            "messages": [
                {"role": "system", "content": self.SYSTEM},
                {"role": "user", "content": self._format_stories(new_stories, continuing_stories)},
            ],
        }
        base = (self.cfg.get("base_url") or "https://api.openai.com/v1").rstrip("/")
        req = urllib.request.Request(
            base + "/chat/completions",
            data=json.dumps(payload).encode(), method="POST",
            headers={"Content-Type": "application/json",
                     "Authorization": f"Bearer {self.cfg['api_key']}"},
        )
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.loads(resp.read().decode())
        text = data["choices"][0]["message"]["content"]
        paragraphs, references = self._split(text)
        return {"paragraphs": paragraphs, "references": references}

    @staticmethod
    def _format_stories(new_stories, continuing_stories):
        lines = []
        for tag, stories in (("NEW", new_stories), ("CONTINUING", continuing_stories)):
            for s in stories[:10]:
                outlets = sorted({i["outlet"] for i in s})
                lines.append(f"[{tag}] {s[0]['title']} "
                             f"(outlets: {', '.join(outlets)}; link: {s[0]['link']})")
        return "\n".join(lines)

    @staticmethod
    def _split(text):
        if "References:" in text:
            body, _, tail = text.partition("References:")
            paragraphs = [p.strip() for p in body.strip().split("\n\n") if p.strip()]
            references = [{"n": i + 1, "title": line.strip().lstrip("-*0123456789. "),
                           "outlet": "", "link": ""}
                          for i, line in enumerate(tail.strip().splitlines()) if line.strip()]
            return paragraphs, references
        return [p.strip() for p in text.split("\n\n") if p.strip()], []
