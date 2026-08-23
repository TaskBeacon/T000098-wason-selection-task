# Stimulus Mapping

## Mapping Table

| Condition | Stage/Phase | Stimulus IDs | Participant-Facing Content | Source Paper ID | Evidence (quote/figure/table) | Implementation Mode | Asset References | Notes |
|---|---|---|---|---|---|---|---|---|
| `abstract_vowel_even` | fixation; selection; ITI | `fixation`, `rule_template`, `card_template`, `selection_status_template`, `selection_hint` | Chinese vowel/even rule; cards A, D, 4, 7 in one row | APA_DICTIONARY_WASON; W2101286810 | APA four-card example and Oaksford & Chater (1994, Fig. 1) | `psychopy_builtin` | none | P/not-P/Q/not-Q are cards 1/2/3/4. |
| `abstract_shape_color` | fixation; selection; ITI | `fixation`, `rule_template`, `card_template`, `selection_status_template`, `selection_hint` | Chinese triangle/blue rule; triangle, circle, blue, orange cards | W1981753740; W2101286810 | Thompson (1994) discusses interpretation of abstract conditionals; logical roles follow Oaksford & Chater. | `psychopy_builtin` | none | Content substitution preserves If-P-then-Q roles. |
| `social_car_fuel` | fixation; selection; ITI | `fixation`, `rule_template`, `card_template`, `selection_status_template`, `selection_hint` | Borrowing a car requires refilling the tank; four person-status cards | W2151097560 | Stone et al. (2002, Fig. 1) use car borrowing and refilling as a social-contract example. | `psychopy_builtin` | none | P/not-Q detect a potential cheater. |
| `social_drink_age` | fixation; selection; ITI | `fixation`, `rule_template`, `card_template`, `selection_status_template`, `selection_hint` | Drinking alcohol requires age 18; drink/activity and age cards | W2151097560 | Stone et al. (2002, Task section) define social-contract rules as benefit/activity contingent on a requirement. | `psychopy_builtin` | none | Familiar permission content is adapted to Chinese participants. |

All participant-facing text and positions are defined in `config/*.yaml`; no external assets are used.

