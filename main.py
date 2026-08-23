from __future__ import annotations

import json
from contextlib import nullcontext
from functools import partial
from pathlib import Path
from typing import Any

import pandas as pd
from psychopy import core
from psyflow import (
    BlockUnit,
    StimBank,
    StimUnit,
    SubInfo,
    TaskRunOptions,
    TaskSettings,
    context_from_config,
    initialize_exp,
    initialize_triggers,
    load_config,
    parse_task_run_options,
    runtime_context,
)

from src import run_trial, summarize_trials


MODES = ("human", "qa", "sim")
DEFAULT_CONFIG_BY_MODE = {
    "human": "config/config.yaml",
    "qa": "config/config_qa.yaml",
    "sim": "config/config_scripted_sim.yaml",
}


def run(options: TaskRunOptions) -> None:
    task_root = Path(__file__).resolve().parent
    cfg = load_config(str(options.config_path))
    output_dir: Path | None = None
    runtime_scope = nullcontext()
    runtime_ctx = None
    if options.mode in ("qa", "sim"):
        runtime_ctx = context_from_config(task_dir=task_root, config=cfg, mode=options.mode)
        output_dir = runtime_ctx.output_dir
        runtime_scope = runtime_context(runtime_ctx)

    with runtime_scope:
        if options.mode == "qa":
            subject_data = {"subject_id": "qa098"}
        elif options.mode == "sim":
            subject_data = {
                "subject_id": str(runtime_ctx.session.participant_id or "sim098")
            }
        else:
            subject_data = SubInfo(cfg["subform_config"]).collect()

        settings = TaskSettings.from_dict(cfg["task_config"])
        settings.add_subinfo(subject_data)
        if output_dir is not None:
            output_dir.mkdir(parents=True, exist_ok=True)
            settings.save_path = str(output_dir)
            prefix = "qa" if options.mode == "qa" else "sim"
            settings.res_file = str(output_dir / f"{prefix}_trace.csv")
            settings.log_file = str(output_dir / f"{prefix}_psychopy.log")
            settings.json_file = str(output_dir / f"{prefix}_settings.json")

        settings.triggers = cfg["trigger_config"]
        trigger_runtime = (
            initialize_triggers(mock=True)
            if options.mode in ("qa", "sim")
            else initialize_triggers(cfg)
        )
        win, kb = initialize_exp(settings)
        stim_bank = StimBank(win, cfg["stim_config"]).preload_all()
        settings.save_to_json()

        trigger_runtime.send(settings.triggers.get("experiment_start"))
        StimUnit("instruction", win, kb, runtime=trigger_runtime).add_stim(
            stim_bank.get("instruction")
        ).wait_and_continue(keys=[str(settings.continue_key)])

        block_seed = int(settings.block_seed[0])
        block = BlockUnit(
            block_id="wason_block",
            block_idx=0,
            settings=settings,
            window=win,
            keyboard=kb,
            n_trials=int(settings.trials_per_block),
            seed=block_seed,
        )
        block.generate_conditions(
            condition_labels=list(settings.conditions),
            weights=settings.resolve_condition_weights(),
            seed=block_seed,
        )
        block.on_start(lambda _: trigger_runtime.send(settings.triggers.get("block_start")))
        block.on_end(lambda _: trigger_runtime.send(settings.triggers.get("block_end")))
        block.run_trial(
            partial(
                run_trial,
                stim_bank=stim_bank,
                trigger_runtime=trigger_runtime,
                block_id="wason_block",
                block_idx=0,
            )
        )
        all_rows: list[dict[str, Any]] = []
        block.to_dict(all_rows)

        result_path = Path(settings.res_file)
        result_path.parent.mkdir(parents=True, exist_ok=True)
        pd.DataFrame(all_rows).to_csv(result_path, index=False)
        result_path.with_name(f"{result_path.stem}_wason_summary.json").write_text(
            json.dumps(summarize_trials(all_rows), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        trigger_runtime.send(settings.triggers.get("goodbye_onset"))
        StimUnit("goodbye", win, kb, runtime=trigger_runtime).add_stim(
            stim_bank.get("goodbye")
        ).wait_and_continue(keys=[str(settings.continue_key)])
        trigger_runtime.send(settings.triggers.get("experiment_end"))
        trigger_runtime.close()
        win.close()
        core.quit()


def main() -> None:
    run(
        parse_task_run_options(
            task_root=Path(__file__).resolve().parent,
            description="Run the Wason four-card selection task.",
            default_config_by_mode=DEFAULT_CONFIG_BY_MODE,
            modes=MODES,
        )
    )


if __name__ == "__main__":
    main()

