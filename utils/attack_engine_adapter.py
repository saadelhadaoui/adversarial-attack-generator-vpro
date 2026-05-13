from orchestration.graph import DefenseGraph


def run_attack_round(mode: str = "PROTECTION", attack_family: str = "Balanced") -> dict:
    graph = DefenseGraph(mode=mode)
    return graph.run_attack_round(attack_family=attack_family)
