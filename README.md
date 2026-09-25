# brief-pipeline

One repo, one pipeline: **RSS feeds → story clusters → ranked stories → narrated edition**.

```
feeds.yaml ──> rss_fetcher ──> cluster ──> rank ──> edition (diff vs prior)
                                                        │
                              .env (keys, gitignored) ──┤
                                                        ▼
                                        writer (extractive | LLM)
                                                        │
                                                        ▼
                                        format ──> editions/YYYY-MM-DD.{json,html}
```

A learning template distilled from a real news-brief pipeline. Each module is short
enough to read in one sitting, and the data flows straight through `main.py`.

## Run it

```bash
cp feeds.example.yaml feeds.yaml   # then put your own feeds in
pip install -r requirements.txt
python main.py
```

Without any API key you get the **extractive** narrator: mechanical but transparent.
Set `LLM_API_KEY` (see `.env.example`) to upgrade to full LLM-written narratives
via any OpenAI-compatible chat API.

## Modules

| Module | Stage | Job |
|---|---|---|
| `rss_fetcher.py` | fetch | Fetch + parse feeds; a bad feed is skipped, never fatal |
| `cluster.py` | cluster | Title tokens → Jaccard similarity → union-find grouping (no ML deps) |
| `rank.py` | rank | Sort by distinct-outlet breadth — breadth as a proxy for importance |
| `edition.py` | diff | Persist editions as JSON; split stories into new vs continuing |
| `writer.py` | write | Narrate each event once, inline citations, References section |
| `format.py` | format | Clean semantic HTML, reader-mode friendly, light/dark aware |
| `config.py` | config | Loads `feeds.yaml` + `.env`; the only place that reads secrets |

## Editorial rules (encoded in `writer.py`)

- Narrate each duplicated event **once**, however many outlets cover it.
- Inline numbered citations on factual claims; literal `References:` section.
- Diff against the prior edition — genuinely new developments lead.

## Secrets rule

Secrets live in **environment variables**, never in the repo:

- `.env` and `feeds.yaml` are gitignored — your feeds and keys stay yours.
- `.env.example` and `feeds.example.yaml` show the shape without values.
- `config.py` is the only module that reads `os.getenv(...)`.

If a friend clones this, they copy the `.example` files, add their own feeds/keys,
and run it — nothing of yours leaks.

## Ideas to grow it

- Swap Jaccard clustering for embeddings.
- Add full-article fetching for the top stories before writing.
- Link the `[n]` citations to the reference list in the HTML.
- Keep a 14-edition archive and prune old ones.
