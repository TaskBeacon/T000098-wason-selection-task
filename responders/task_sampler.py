from __future__ import annotations

import random as _py_random
from dataclasses import dataclass
from typing import Any

from psyflow.sim.contracts import Action, Feedback, Observation, SessionInfo


@dataclass
class TaskSamplerResponder:
    correct_rate: float = 0.65
    response_rate: float = 0.95
    rt_mean_s: float = 0.08
    rt_sd_s: float = 0.01

    def __post_init__(self) -> None:
        self._rng: Any = None
        self._paths: dict[Any, list[str]] = {}
        self.correct_rate = min(1.0, max(0.0, float(self.correct_rate)))
        self.response_rate = min(1.0, max(0.0, float(self.response_rate)))

    def start_session(self, session: SessionInfo, rng: Any) -> None:
        self._rng = rng
        self._paths.clear()

    def on_feedback(self, fb: Feedback) -> None:
        return None

    def end_session(self) -> None:
        self._rng = None
        self._paths.clear()

    def _random(self) -> float:
        return float(self._rng.random()) if self._rng is not None else float(_py_random.random())

    def _normal(self) -> float:
        if self._rng is not None and hasattr(self._rng, "normal"):
            return float(self._rng.normal(self.rt_mean_s, self.rt_sd_s))
        if self._rng is not None and hasattr(self._rng, "gauss"):
            return float(self._rng.gauss(self.rt_mean_s, self.rt_sd_s))
        return float(_py_random.gauss(self.rt_mean_s, self.rt_sd_s))

    def act(self, obs: Observation) -> Action:
        valid_keys = [str(key) for key in list(obs.valid_keys or [])]
        if not valid_keys:
            return Action(key=None, rt_s=None, meta={"source": "wason_sampler", "reason": "no_valid_keys"})
        if not str(obs.phase).startswith("selection_step_"):
            return Action(key=valid_keys[0], rt_s=max(0.02, self._normal()), meta={"source": "wason_sampler"})

        trial_key = obs.trial_id
        if trial_key not in self._paths:
            if self._random() > self.response_rate:
                self._paths[trial_key] = []
            elif self._random() < self.correct_rate:
                self._paths[trial_key] = ["1", "4", "return"]
            else:
                self._paths[trial_key] = ["1", "3", "return"]
        path = self._paths[trial_key]
        step = int((obs.task_factors or {}).get("selection_step", 0))
        key = path[step] if step < len(path) else None
        if key not in valid_keys:
            key = None
        return Action(
            key=key,
            rt_s=max(0.02, self._normal()) if key is not None else None,
            meta={"source": "wason_sampler", "planned_path": list(path), "step": step},
        )

