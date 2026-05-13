class VectorMemory:
    def __init__(self):
        self.patterns: list[dict] = []

    def add_pattern(self, pattern_label, metadata=None):
        self.patterns.append({"label": pattern_label, "meta": metadata or {}})

    def search_similar(self, text, top_k=5):
        query = set(str(text).lower().split())
        scored = []
        for item in self.patterns:
            label = item["label"]
            words = set(str(label).lower().replace("_", " ").split())
            score = len(query & words) / max(len(query | words), 1)
            scored.append((score, item))
        return [item for score, item in sorted(scored, reverse=True)[:top_k] if score > 0]

    def calculate_similarity(self, a, b):
        left = set(str(a).lower().split())
        right = set(str(b).lower().split())
        return len(left & right) / max(len(left | right), 1)

    def get_all_patterns(self):
        return self.patterns
