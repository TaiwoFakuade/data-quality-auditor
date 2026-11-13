"""Inter-annotator agreement: Cohen's kappa for two annotators.

Kappa measures agreement beyond chance. 1.0 is perfect agreement,
0 is chance-level, negative means worse than chance. Use it when two
people labelled the same items, before trusting either set of labels
on its own — it is the check the first roadmap asked for, and it is
exactly the kind of QA a TELUS / Podonos reviewer would run.
"""


def cohens_kappa(labels_a, labels_b):
    """Cohen's kappa for two lists of categorical labels, same order."""
    if len(labels_a) != len(labels_b) or not labels_a:
        raise ValueError("Both label lists must be non-empty and the same length")
    n = len(labels_a)
    observed = sum(1 for a, b in zip(labels_a, labels_b) if a == b) / n
    # Expected agreement if the two annotators labelled at random,
    # keeping each annotator's own label frequencies.
    categories = sorted(set(labels_a) | set(labels_b))
    expected = 0.0
    for cat in categories:
        p_a = sum(1 for x in labels_a if x == cat) / n
        p_b = sum(1 for x in labels_b if x == cat) / n
        expected += p_a * p_b
    if expected == 1.0:
        return 1.0 if observed == 1.0 else 0.0
    return (observed - expected) / (1 - expected)
