# rss-story-cluster

A tiny, readable pipeline: **fetch RSS feeds → group items into stories → rank by outlet breadth**.

This is a learning template, not a product. It mirrors the first stage of a news-brief
pipeline (fetch headlines, narrate each duplicated event once, rank by how many outlets
cover it). Each module is short enough to read in one sitting.

## Run it

```bash
cp feeds.example.yaml feeds.yaml   # then put your own feeds in
pip install -r requirements.txt
python main.py
```

## The pipeline

| Module | Job |
|---|---|
| `rss_fetcher.py` | Fetch + parse feeds with `feedparser`; a bad feed is skipped, never fatal |
| `cluster.py` | Title tokens → Jaccard similarity → union-find grouping (no ML deps) |
| `rank.py` | Sort stories by distinct-outlet count — breadth as a proxy for importance |
| `config.py` | Loads `feeds.yaml`; settings overridable via env vars |

## Secrets rule

Secrets live in **environment variables**, never in the repo:

- `.env` and `feeds.yaml` are gitignored — your feeds and keys stay yours.
- `.env.example` and `feeds.example.yaml` show the shape without values.
- `config.py` is the only place that reads `os.getenv(...)`.

If a friend clones this, they copy the `.example` files, add their own feeds/keys,
and run it — nothing of yours leaks.

## Ideas to grow it

- Replace Jaccard clustering with embeddings for better grouping.
- Add full-article fetching for the top stories.
- Add a writer step that narrates each story once (this is where an LLM slots in).
