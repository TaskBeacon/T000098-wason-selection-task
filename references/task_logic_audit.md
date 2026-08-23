# Wason Selection Task Logic Audit

This audit was derived from the cited literature and the user-provided APA paradigm description before task code was written.

## 1. Paradigm Intent

- Task: Wason Selection Task / four-card problem.
- Primary construct: conditional reasoning and falsification-oriented information selection.
- Manipulated factors: abstract descriptive rules versus familiar social-contract rules, each preserving the logical form “If P, then Q.”
- Dependent measures: exact-set accuracy, selected card roles, P/Q matching response, number of cards selected, submission latency, and condition-wise accuracy.
- Key citations: APA Dictionary of Psychology paradigm entry; Oaksford and Chater (1994); Thompson (1994); Stone et al. (2002); Johnson-Laird (2010).

## 2. Block/Trial Workflow

### Block Structure

- Total blocks: 1.
- Trials per block: 8 in the human profile (each of two abstract and two social-contract items occurs twice); QA and simulation profiles use 4 trials so every item and both rule types remain covered.
- Randomization/counterbalancing: the four item labels are scheduled with equal frequency in random order from a block seed; card-role positions are fixed as P, not-P, Q, not-Q so the participant’s numbered response remains interpretable across iterative selection screens.
- Condition weight policy:
  - `task.condition_weights` is omitted/null because every item should occur once.
  - Runtime resolution delegates to `TaskSettings.resolve_condition_weights()` and therefore uses even/default generation.
- Condition generation method:
  - Built-in `BlockUnit.generate_conditions(...)` produces the item-label sequence.
  - Each generated condition is a scalar item ID passed directly to `run_trial.py`.
- Runtime-generated trial values:
  - No experimental factor is randomly generated inside `run_trial.py`.
  - The condition label deterministically selects rule text, four visible card faces, semantic type, and normative answer from config.

### Trial State Machine

1. State name: fixation
   - Onset trigger: `fixation_onset`.
   - Stimuli shown: centered “+”.
   - Valid keys: none.
   - Timeout behavior: ends after 500 ms.
   - Next state: card selection.
2. State name: card selection step (repeated up to five decisions)
   - Onset trigger: `abstract_selection_onset` or `social_selection_onset` on the first step, then `selection_update_onset`.
   - Stimuli shown: the conditional rule, four numbered cards in one horizontal row, currently selected card numbers, and a short action instruction.
   - Valid keys: `1`, `2`, `3`, `4` to add a card; `return` to submit the current set.
   - Timeout behavior: submit the currently selected set when the 30 s decision window expires.
   - Next state: redraw with the selected card marked, or submit when Return is pressed, four unique cards have been selected, or the fifth decision completes.
3. State name: inter-trial interval
   - Onset trigger: `iti_onset`.
   - Stimuli shown: blank screen.
   - Valid keys: none.
   - Timeout behavior: ends after 500 ms.
   - Next state: next trial or task completion.

No correctness feedback is shown, preventing trial-to-trial tutoring.

## 3. Condition Semantics

- Condition ID: `abstract_vowel_even`
  - Participant-facing meaning: test “If a card has a vowel on one side, then it has an even number on the other side” with A, D, 4, 7.
  - Concrete stimulus realization: four gray text cards showing A / D / 4 / 7.
  - Outcome rules: P and not-Q (cards 1 and 4) is the only exact normative set.
- Condition ID: `abstract_shape_color`
  - Participant-facing meaning: test “If one side is a triangle, then the other side is blue” with triangle, circle, blue, orange.
  - Concrete stimulus realization: four gray text cards using the corresponding Chinese labels.
  - Outcome rules: P and not-Q (cards 1 and 4) is the only exact normative set.
- Condition ID: `social_car_fuel`
  - Participant-facing meaning: test the contract “If someone borrows my car, then that person must refill the fuel tank.”
  - Concrete stimulus realization: four person-status cards: borrowed car / did not borrow car / refilled tank / did not refill tank.
  - Outcome rules: benefit-taker and requirement-violator (P and not-Q; cards 1 and 4) is the exact set.
- Condition ID: `social_drink_age`
  - Participant-facing meaning: test the permission rule “If someone is drinking alcohol, then that person must be at least 18 years old.”
  - Concrete stimulus realization: four person-status cards: drinking alcohol / drinking soda / age 22 / age 16.
  - Outcome rules: regulated activity and under-age case (P and not-Q; cards 1 and 4) is the exact set.

Participant-facing wording and item material are defined in `config/*.yaml` under `task.item_specs` and reusable stimulus templates. The Chinese profiles use SimHei; localization can replace config wording without editing Python.

## 4. Response and Scoring Rules

- Response mapping: number keys 1–4 add the correspondingly numbered card; Return submits. Already-selected cards cannot be added twice.
- Response key source: `task.card_keys` and `task.submit_key` in config.
- Missing-response policy: a timeout submits the selections already made; zero selected cards remains a valid analyzable response but is incorrect.
- Correctness logic: compare the unordered selected-card set with the config-defined normative set `[1, 4]`.
- Reward/penalty updates: none.
- Running metrics: selected roles, selected count, exact-set accuracy, P-only response, P+Q matching response, inclusion of P, inclusion of not-Q, and submission RT from first selection-screen onset.

## 5. Stimulus Layout Plan

- Screen name: card selection.
- Stimulus IDs shown together: `rule_template`, `card_template` rebuilt at four x-positions, `selection_status_template`, and `selection_hint`.
- Layout anchors (`pos`): rule `[0, 235]`; cards `[-450, -150, 150, 450]` at y `20`; selection status `[0, -155]`; hint `[0, -245]`.
- Size/spacing: 1280×720 px window, rule height 30 px with 1120 px wrap; each card is a 230×150 px TextBox2 with 26 px lettering; gaps are 70 px; status/hint stay below the card row.
- Readability/overlap checks: QA screenshots and `task_flow.png` must show all four cards without overlap or clipping at the specified window size.
- Rationale: a single horizontal row matches the classic four-card display and makes number-to-card mapping unambiguous.

## 6. Trigger Plan

- `experiment_start` / `experiment_end`: task lifecycle.
- `block_start` / `block_end`: single block lifecycle.
- `fixation_onset`: pre-trial fixation.
- `abstract_selection_onset`: first abstract item selection screen.
- `social_selection_onset`: first social-contract item selection screen.
- `selection_update_onset`: redraw after a card choice.
- `card_1_selected` through `card_4_selected`: key-specific card choices.
- `selection_submitted`: Return submission.
- `selection_timeout`: decision window timeout.
- `iti_onset`: inter-trial interval.
- `goodbye_onset`: completion screen.

## 7. Architecture Decisions (Auditability)

- `main.py` runtime flow style: one simple mode-aware flow with built-in block scheduling.
- `utils.py` used: yes.
- Exact purpose: pure item validation, response-set classification, and summary computation only; it owns no timing, display, triggers, trial IDs, or condition randomization.
- Custom controller used: no.
- Legacy/backward-compatibility fallback logic required: no.

The iterative response is implemented as a short sequence of public `StimUnit.capture_response(...)` stages. This preserves PsyFlow ownership of response timing, response/timeout triggers, context, and phase data while allowing a set-valued answer without a manual event loop.

## 8. Inference Log

- Decision: use a balanced eight-trial human profile rather than a single paper-and-pencil problem.
  - Why inference was required: the classic task defines one four-card problem, but a reusable behavioral implementation needs both abstract and social-contract observations.
  - Citation-supported rationale: Stone et al. (2002) explicitly compare problem types with the same conditional structure; the item pool keeps that contrast while avoiding feedback.
- Decision: use a 500 ms fixation and 500 ms blank ITI.
  - Why inference was required: classic self-paced reports do not specify these computer-display intervals.
  - Citation-supported rationale: these neutral intervals do not alter the conditional problem and are marked inferred.
- Decision: allow 30 s per iterative decision step and submit on timeout.
  - Why inference was required: the classic task is self-paced and does not define a deadline.
  - Citation-supported rationale: the generous window preserves deliberative reasoning; QA/sim timings are shortened only by mode scaling.
- Decision: represent multi-card selection through numbered selection steps.
  - Why inference was required: the canonical task allows any subset, while PsyFlow’s standard response primitive records one key per response stage.
  - Citation-supported rationale: the displayed four-card problem and final unordered selected set remain unchanged; exact-set and matching-bias outcomes are preserved.
