"""Validate and deduplicate the book summaries before splitting."""

import csv
import re
from collections import Counter, defaultdict


def normalize_text(value):
    return re.sub(r"\s+", " ", (value or "").strip())


def prepare_records(path):
    groups = defaultdict(list)
    counts = Counter()
    with open(path, encoding="utf-8-sig", newline="") as source:
        reader = csv.DictReader(source)
        if not {"summary", "genre"}.issubset(reader.fieldnames or []):
            raise ValueError("Dataset must contain summary and genre columns")
        for row in reader:
            counts["source_rows"] += 1
            text = normalize_text(row.get("summary"))
            label = normalize_text(row.get("genre")).lower()
            if not text or not label:
                counts["missing_rows"] += 1
                continue
            groups[text.casefold()].append((text, label))
    records = []
    for items in groups.values():
        labels = {label for _, label in items}
        if len(labels) != 1:
            counts["conflicting_rows_removed"] += len(items)
            continue
        records.append(items[0])
        counts["duplicate_rows_removed"] += len(items) - 1
    counts["usable_rows"] = len(records)
    counts["class_distribution"] = dict(
        sorted(Counter(label for _, label in records).items())
    )
    if (
        len(counts["class_distribution"]) < 2
        or min(counts["class_distribution"].values()) < 2
    ):
        raise ValueError("At least two classes with two examples each are required")
    return records, dict(counts)
