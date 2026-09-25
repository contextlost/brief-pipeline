"""Group feed items that describe the same story.

Technique: tokenize titles -> Jaccard similarity -> union-find grouping.
Simple, dependency-free, easy to read. A real system might use embeddings;
this is the learning version.
"""
import re

STOPWORDS = frozenset("""
a an the and or of to in on for with by at from as is are was were be been
el la los las de del en y o un una unos unas que se por con para como mas
""".split())

_TOKEN_RE = re.compile(r"[a-z0-9]+")  # ascii fold keeps it dependency-free


def _tokens(text):
    return {t for t in _TOKEN_RE.findall(text.lower()) if t not in STOPWORDS and len(t) > 2}


def _jaccard(a, b):
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def cluster_items(items, threshold=0.35):
    """Return a list of clusters; each cluster is a list of items."""
    n = len(items)
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    tokenized = [_tokens(it["title"]) for it in items]
    for i in range(n):
        for j in range(i + 1, n):
            if _jaccard(tokenized[i], tokenized[j]) >= threshold:
                union(i, j)

    groups = {}
    for i, it in enumerate(items):
        groups.setdefault(find(i), []).append(it)
    return list(groups.values())
