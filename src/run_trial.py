from __future__ import annotations

from typing import Any

from psyflow import StimUnit, next_trial_id, set_trial_context

from .utils import classify_selection, validate_item_spec


def run_trial(
    win,
    kb,
    settings,
    condition,
    stim_bank,
    trigger_runtime,
    block_id=None,
    block_idx=None,
):
    """Present one four-card conditional rule and collect an unordered card set."""

    condition_id = str(condition).strip()
    item_specs = dict(settings.item_specs)
    if condition_id not in item_specs:
        raise ValueError(f"Unsupported Wason condition: {condition_id}")
    item = validate_item_spec(condition_id, item_specs[condition_id])

    trial_id = int(next_trial_id())
    block_id_value = str(block_id or "wason_block")
    block_idx_value = int(block_idx or 0)
    condition_family = str(item["condition_family"])
    correct_cards = list(item["correct_cards"])
    card_keys = [str(key) for key in settings.card_keys]
    submit_key = str(settings.submit_key)
    valid_keys = [*card_keys, submit_key]
    response_window_s = float(settings.response_window_s)
    card_positions = [tuple(pos) for pos in settings.card_positions]
    if len(card_positions) != 4:
        raise ValueError("task.card_positions must define four positions")

    task_factors = {
        "condition_family": condition_family,
        "rule_form": "if_P_then_Q",
        "correct_cards": correct_cards,
        "card_roles": [str(card["role"]) for card in item["cards"]],
        "block_idx": block_idx_value,
    }
    trial_data: dict[str, Any] = {
        "trial_id": trial_id,
        "block_id": block_id_value,
        "block_idx": block_idx_value,
        "condition": condition_id,
        "condition_id": condition_id,
        "condition_family": condition_family,
        "rule_text": str(item["rule_text"]),
        "correct_cards": correct_cards,
    }

    fixation = StimUnit("fixation", win, kb, runtime=trigger_runtime).add_stim(
        stim_bank.get("fixation")
    )
    set_trial_context(
        fixation,
        trial_id=trial_id,
        phase="fixation",
        deadline_s=float(settings.fixation_s),
        valid_keys=[],
        block_id=block_id_value,
        condition_id=condition_id,
        task_factors=task_factors,
        stim_id="fixation",
        stim_features={"symbol": "+"},
    )
    fixation.show(
        duration=float(settings.fixation_s),
        onset_trigger=settings.triggers.get("fixation_onset"),
    ).to_dict(trial_data)

    selected_cards: list[int] = []
    decision_history: list[str] = []
    decision_rts: list[float] = []
    submitted = False
    timed_out = False
    duplicate_attempts = 0

    for step_idx in range(int(settings.max_selection_steps)):
        phase = f"selection_step_{step_idx + 1}"
        selected_text = (
            str(settings.none_selected_label)
            if not selected_cards
            else str(settings.selected_separator).join(str(card) for card in selected_cards)
        )
        selection = StimUnit(phase, win, kb, runtime=trigger_runtime)
        selection.add_stim(
            stim_bank.get_and_format("rule_template", rule_text=str(item["rule_text"]))
        )
        for card_idx, (card, pos) in enumerate(zip(item["cards"], card_positions), start=1):
            marker = str(settings.selected_marker) if card_idx in selected_cards else ""
            card_stim = stim_bank.get_and_format(
                "card_template",
                marker=marker,
                number=card_idx,
                face=str(card["face"]),
            )
            card_stim.pos = pos
            selection.add_stim(card_stim)
        selection.add_stim(
            stim_bank.get_and_format("selection_status_template", selected_text=selected_text)
        )
        selection.add_stim(stim_bank.get("selection_hint"))

        step_factors = {
            **task_factors,
            "selection_step": step_idx,
            "selected_cards_before": list(selected_cards),
        }
        set_trial_context(
            selection,
            trial_id=trial_id,
            phase=phase,
            deadline_s=response_window_s,
            valid_keys=valid_keys,
            block_id=block_id_value,
            condition_id=condition_id,
            task_factors=step_factors,
            stim_id=f"{condition_id}_four_cards",
            stim_features={
                "rule_text": str(item["rule_text"]),
                "card_faces": [str(card["face"]) for card in item["cards"]],
                "selected_cards": list(selected_cards),
            },
        )
        onset_name = (
            "abstract_selection_onset"
            if step_idx == 0 and condition_family == "abstract"
            else "social_selection_onset"
            if step_idx == 0
            else "selection_update_onset"
        )
        selection.capture_response(
            keys=valid_keys,
            duration=response_window_s,
            onset_trigger=settings.triggers.get(onset_name),
            response_trigger={
                "1": settings.triggers.get("card_1_selected"),
                "2": settings.triggers.get("card_2_selected"),
                "3": settings.triggers.get("card_3_selected"),
                "4": settings.triggers.get("card_4_selected"),
                submit_key: settings.triggers.get("selection_submitted"),
            },
            timeout_trigger=settings.triggers.get("selection_timeout"),
        ).to_dict(trial_data)

        response = str(selection.get_state("response", "") or "")
        rt = selection.get_state("rt", None)
        if isinstance(rt, (int, float)):
            decision_rts.append(float(rt))
        decision_history.append(response or "timeout")
        if not response:
            timed_out = True
            submitted = True
            break
        if response == submit_key:
            submitted = True
            break
        card_number = int(response)
        if card_number in selected_cards:
            duplicate_attempts += 1
        else:
            selected_cards.append(card_number)
        if len(selected_cards) == 4:
            submitted = True
            break

    iti = StimUnit("iti", win, kb, runtime=trigger_runtime)
    set_trial_context(
        iti,
        trial_id=trial_id,
        phase="iti",
        deadline_s=float(settings.iti_s),
        valid_keys=[],
        block_id=block_id_value,
        condition_id=condition_id,
        task_factors=task_factors,
        stim_id="blank_iti",
        stim_features={"display": "blank"},
    )
    iti.show(
        duration=float(settings.iti_s),
        onset_trigger=settings.triggers.get("iti_onset"),
    ).to_dict(trial_data)

    selection_outcome = classify_selection(selected_cards, correct_cards)
    selected_roles = [str(item["cards"][card - 1]["role"]) for card in selection_outcome["selected_cards"]]
    trial_data.update(
        {
            **selection_outcome,
            "selected_roles": selected_roles,
            "decision_history": decision_history,
            "decision_count": len(decision_history),
            "duplicate_attempts": duplicate_attempts,
            "submitted": submitted,
            "timed_out": timed_out,
            "response_rt": sum(decision_rts) if decision_rts else None,
        }
    )
    return trial_data

