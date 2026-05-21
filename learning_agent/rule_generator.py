from typing import Any


def generate_rule(family: str, pattern: str, policy: dict[str, Any]) -> str:
    templates = policy.get("rule_templates", {})
    template = templates.get(family, templates.get("default", "Block future requests matching {pattern}."))
    return template.format(family=family, pattern=pattern)
