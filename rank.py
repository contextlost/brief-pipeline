"""Rank story clusters by outlet breadth.

Breadth -- the number of distinct outlets covering a story -- is a cheap
proxy for importance. A story in five outlets outranks one in a single
outlet. Ties keep cluster order (stable sort).
"""


def rank_clusters(clusters):
    def breadth(cluster):
        return len({item["outlet"] for item in cluster})

    return sorted(clusters, key=breadth, reverse=True)
