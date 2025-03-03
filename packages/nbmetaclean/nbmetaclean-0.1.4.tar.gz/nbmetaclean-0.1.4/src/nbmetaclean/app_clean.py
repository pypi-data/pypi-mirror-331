from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Union

from nbmetaclean.clean import CleanConfig, TupleStr, clean_nb_file
from nbmetaclean.helpers import get_nb_names_from_list
from nbmetaclean.version import __version__


parser = argparse.ArgumentParser(
    prog="nbmetaclean",
    description="Clean metadata and execution_count from Jupyter notebooks.",
)
parser.add_argument(
    "path",
    default=".",
    nargs="*",
    help="Path for nb or folder with notebooks.",
)
parser.add_argument(
    "-s",
    "--silent",
    action="store_true",
    help="Silent mode.",
)
parser.add_argument(
    "--not_ec",
    action="store_false",
    help="Do not clear execution_count.",
)
parser.add_argument(
    "--not-pt",
    action="store_true",
    help="Do not preserve timestamp.",
)
parser.add_argument(
    "--dont_clear_nb_metadata",
    action="store_true",
    help="Do not clear notebook metadata.",
)
parser.add_argument(
    "--clear_cell_metadata",
    action="store_true",
    help="Clear cell metadata.",
)
parser.add_argument(
    "--clear_outputs",
    action="store_true",
    help="Clear outputs.",
)
parser.add_argument(
    "--nb_metadata_preserve_mask",
    nargs="+",
    help="Preserve mask for notebook metadata.",
)
parser.add_argument(
    "--cell_metadata_preserve_mask",
    nargs="+",
    help="Preserve mask for cell metadata.",
)
parser.add_argument(
    "--dont_merge_masks",
    action="store_true",
    help="Do not merge masks.",
)
parser.add_argument(
    "--clean_hidden_nbs",
    action="store_true",
    help="Clean hidden notebooks.",
)
parser.add_argument(
    "-D",
    "--dry_run",
    action="store_true",
    help="perform a trial run, don't write results",
)
parser.add_argument(
    "-V",
    "--verbose",
    action="store_true",
    help="Verbose mode. Print extra information.",
)
parser.add_argument(
    "-v",
    "--version",
    action="store_true",
    help="Print version information.",
)


def process_mask(mask: Union[list[str], None]) -> Union[tuple[TupleStr, ...], None]:
    if mask is None:
        return None
    return tuple(tuple(item.split(".")) for item in mask)


def print_result(
    cleaned: list[Path],
    errors: list[Path],
    clean_config: CleanConfig,
    path: list[str],
    num_nbs: int,
) -> None:
    if clean_config.verbose:
        print(
            f"Path: {', '.join(path)}, preserve timestamp: {clean_config.preserve_timestamp}"
        )
        print(f"checked: {num_nbs} notebooks")
    if cleaned:
        if len(cleaned) == 1:
            print(f"cleaned: {cleaned[0]}")
        else:
            print(f"cleaned: {len(cleaned)} notebooks")
            for nb in cleaned:
                print("- ", nb)
    if errors:
        print(f"with errors: {len(errors)}")
        for nb in errors:
            print("- ", nb)


def app_clean() -> None:
    """Clean metadata and execution_count from Jupyter notebook."""
    cfg = parser.parse_args()

    if cfg.version:
        print(f"nbmetaclean version: {__version__}")
        sys.exit(0)

    clean_config = CleanConfig(
        clear_nb_metadata=not cfg.dont_clear_nb_metadata,
        clear_cell_metadata=cfg.clear_cell_metadata,
        clear_execution_count=cfg.not_ec,
        clear_outputs=cfg.clear_outputs,
        preserve_timestamp=not cfg.not_pt,
        silent=cfg.silent,
        nb_metadata_preserve_mask=process_mask(cfg.nb_metadata_preserve_mask),
        cell_metadata_preserve_mask=process_mask(cfg.cell_metadata_preserve_mask),
        mask_merge=not cfg.dont_merge_masks,
        dry_run=cfg.dry_run,
        verbose=cfg.verbose if not cfg.silent else False,
    )
    path_list: list[str] = cfg.path if isinstance(cfg.path, list) else [cfg.path]
    nb_files = get_nb_names_from_list(path_list, hidden=cfg.clean_hidden_nbs)

    cleaned, errors = clean_nb_file(
        nb_files,
        clean_config,
    )
    # print(cfg)
    if cfg.path == ".":  # if running without arguments add some info.
        if not nb_files:
            print("No notebooks found at current directory.")
            sys.exit(0)
        elif not cfg.silent and not cleaned and not errors:
            print(f"Checked: {len(nb_files)} notebooks. All notebooks are clean.")

    if not cfg.silent:
        print_result(cleaned, errors, clean_config, path_list, len(nb_files))


if __name__ == "__main__":  # pragma: no cover
    app_clean()
