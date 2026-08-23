from __future__ import annotations

from collections import Counter
from typing import Any, Iterable


CARD_ROLES = ("P", "not_P", "Q", "not_Q")


def validate_item_spec(condition_id: str, raw: Any) -> dict[str, Any]:
    """Validate one config-owned four-card problem without inventing fallbacks."""

    if not isinstance(raw, dict):
        raise TypeError(f"Item {condition_id!r} must be a mapping")
    item = dict(raw)
    cards = item.get("cards")
    if not isinstance(cards, list) or len(cards) != 4:
        raise ValueError(f"Item {condition_id!r} must define exactly four cards")
    roles = [str(card.get("role", "")) for card in cards if isinstance(card, dict)]
    if tuple(roles) != CARD_ROLES:
        raise ValueError(
            f"Item {condition_id!r} card roles must be {CARD_ROLES}, got {tuple(roles)}"
        )
    if any(not str(card.get("face", "")).strip() for card in cards):
        raise ValueError(f"Item {condition_id!r} has an empty participant-facing card")
    if not str(item.get("rule_text", "")).strip():
        raise ValueError(f"Item {condition_id!r} has an empty rule")
    correct_cards = sorted(int(value) for value in item.get("correct_cards", []))
    if correct_cards != [1, 4]:
        raise ValueError(
            f"Item {condition_id!r} must preserve the P/not-Q solution [1, 4]"
        )
    item["correct_cards"] = correct_cards
    return item


def classify_selection(selected_cards: Iterable[int], correct_cards: Iterable[int]) -> dict[str, Any]:
    """Classify a Wason response set, including the canonical matching errors."""

    selected = sorted(set(int(value) for value in selected_cards))
    correct = sorted(set(int(value) for value in correct_cards))
    if selected == correct:
        category = "normative_P_not_Q"
    elif selected == [1, 3]:
        category = "matching_P_Q"
    elif selected == [1]:
        category = "P_only"
    elif not selected:
        category = "no_cards"
    else:
        category = "other"
    return {
        "selected_cards": selected,
        "selected_count": len(selected),
        "response_category": category,
        "response_correct": selected == correct,
        "selected_P": 1 in selected,
        "selected_not_P": 2 in selected,
        "selected_Q": 3 in selected,
        "selected_not_Q": 4 in selected,
        "matching_P_Q": selected == [1, 3],
        "P_only": selected == [1],
    }


def summarize_trials(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Create compact condition-wise accuracy and response-category summaries."""

    trials = [row for row in rows if isinstance(row, dict) and row.get("condition_family")]
    by_family: dict[str, dict[str, Any]] = {}
    for family in sorted({str(row["condition_family"]) for row in trials}):
        family_rows = [row for row in trials if str(row["condition_family"]) == family]
        correct = sum(bool(row.get("response_correct")) for row in family_rows)
        by_family[family] = {
            "n_trials": len(family_rows),
            "n_correct": correct,
            "accuracy": correct / len(family_rows) if family_rows else None,
        }
    return {
        "n_trials": len(trials),
        "n_correct": sum(bool(row.get("response_correct")) for row in trials),
        "overall_accuracy": (
            sum(bool(row.get("response_correct")) for row in trials) / len(trials)
            if trials
            else None
        ),
        "response_categories": dict(Counter(str(row.get("response_category")) for row in trials)),
        "by_condition_family": by_family,
    }

