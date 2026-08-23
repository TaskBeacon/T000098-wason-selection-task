# Parameter Mapping

## Mapping Table

| Parameter ID | Config Path | Implemented Value | Source Paper ID | Evidence (quote/figure/table) | Decision Type | Notes |
|---|---|---|---|---|---|---|
| logical_form | `task.item_specs.*` | If P, then Q | APA_DICTIONARY_WASON; W2101286810 | APA entry and Oaksford & Chater (1994, p. 608) describe the four-card conditional rule. | direct | All four items preserve the same form. |
| card_roles | `task.item_specs.*.cards` | P, not-P, Q, not-Q | W2101286810 | Oaksford & Chater (1994, p. 608 and Fig. 1) define the four visible roles. | direct | Positions remain fixed so response roles are auditable. |
| normative_set | `task.item_specs.*.correct_cards` | cards 1 and 4 (P and not-Q) | W2101286810 | Oaksford & Chater (1994, pp. 608–609) identify P and not-Q as the potentially falsifying cards. | direct | Exact-set scoring ignores selection order. |
| abstract_material | `task.item_specs.abstract_vowel_even` | A, D, 4, 7; vowel implies even | APA_DICTIONARY_WASON; W2101286810 | The APA entry gives the vowel/even four-card example; Oaksford & Chater give the same role structure. | adapted | Chinese rule wording; visible symbols remain conventional. |
| social_contract_form | `task.item_specs.social_*` | benefit/activity implies requirement | W2151097560 | Stone et al. (2002, Fig. 1 and Task section) distinguish social contracts with the same If-P-then-Q structure. | direct | Car/fuel follows the paper’s example; drink/age is a familiar permission variant. |
| condition_balance | `task.conditions`, `task.total_trials` | four items, two presentations each | W2151097560 | Stone et al. compare content domains across multiple matched problems. | adapted | Eight human trials yield balanced abstract/social observations without feedback. |
| selection_input | `task.card_keys`, `task.submit_key`, `task.max_selection_steps` | 1–4 add; Return submits; up to five decisions | APA_DICTIONARY_WASON | Source task requires selecting any subset of four cards. | inferred | Iterative public StimUnit response stages preserve the final unordered subset. |
| response_deadline | `timing.response_window_s` | 30 s per decision stage | APA_DICTIONARY_WASON | Classic description does not specify a computerized deadline. | inferred | Generous deadline preserves deliberation; timeout submits current set. |
| fixation | `timing.fixation_s` | 0.5 s | implementation inference | Not specified in classic paper-and-pencil reports. | inferred | Neutral computer-display lead-in. |
| iti | `timing.iti_s` | 0.5 s | implementation inference | Not specified in classic paper-and-pencil reports. | inferred | Blank interval; no correctness feedback. |
| scoring_categories | derived trial fields | normative, P+Q matching, P-only, no-card, other | W2101286810 | Oaksford & Chater (1994, p. 608) report P+Q and P-only as common response patterns. | direct | Also records every selected role separately. |
| trigger_codes | `triggers.map.*` | 1–60 | implementation inference | Classic behavioral sources specify no hardware codes. | inferred | Unique phase and key-specific codes support audit/replay. |

