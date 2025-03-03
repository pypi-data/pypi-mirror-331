"""
Entrypoint for CLI functionality of optilab.
"""

import argparse
from pathlib import Path

import pandas as pd
from tabulate import tabulate

from .data_classes import OptimizationRun
from .plotting import plot_box_plot, plot_convergence_curve, plot_ecdf_curves
from .utils.pickle_utils import load_from_pickle
from .utils.stat_test import display_test_grid, mann_whitney_u_test_grid

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Optilab CLI utility.", prog="python -m optilab"
    )
    parser.add_argument(
        "pickle_path",
        type=Path,
        help="Path to pickle file or directory with optimization runs.",
    )
    parser.add_argument(
        "--hide_plots", action="store_true", help="Hide plots when running the script."
    )
    parser.add_argument(
        "--test_y", action="store_true", help="Perform Mann-Whitney U test on y values."
    )
    parser.add_argument(
        "--test_evals",
        action="store_true",
        help="Perform Mann-Whitney U test on eval values.",
    )
    parser.add_argument(
        "--entries",
        nargs="+",
        type=int,
        help="Space separated list of indexes of entries to include in analysis.",
    )
    parser.add_argument(
        "--raw_values",
        action="store_true",
        help="If specified, y values below tolerance are not substituted by tolerance value.",
    )
    parser.add_argument(
        "--hide_outliers",
        action="store_true",
        help="If specified, outliers will not be shown in the box plot.",
    )
    args = parser.parse_args()

    file_path_list = []

    if args.pickle_path.is_file():
        file_path_list.append(args.pickle_path)
    elif args.pickle_path.is_dir():
        for file_path in sorted(args.pickle_path.iterdir()):
            if file_path.is_file() and file_path.suffix == ".pkl":
                file_path_list.append(file_path)

    for file_path in file_path_list:
        print(f"# File {file_path}")
        filename_stem = file_path.stem

        data = load_from_pickle(file_path)

        if args.entries:
            data = [data[i] for i in args.entries if 0 <= i < len(data)]

        assert isinstance(data, list)
        for run in data:
            assert isinstance(run, OptimizationRun)

        # plots
        plot_convergence_curve(
            data={run.model_metadata.name: run.logs for run in data},
            savepath=f"{filename_stem}.convergence.png",
            show=not args.hide_plots,
            function_name=data[0].function_metadata.name,
        )

        plot_ecdf_curves(
            data={run.model_metadata.name: run.logs for run in data},
            n_dimensions=data[0].function_metadata.dim,
            n_thresholds=100,
            allowed_error=data[0].tolerance,
            savepath=f"{filename_stem}.ecdf.png",
            show=not args.hide_plots,
            function_name=data[0].function_metadata.name,
        )

        plot_box_plot(
            data={
                run.model_metadata.name: run.bests_y(args.raw_values) for run in data
            },
            savepath=f"{filename_stem}.box_plot.png",
            show=not args.hide_plots,
            function_name=data[0].function_metadata.name,
            hide_outliers=args.hide_outliers,
        )

        # stats
        stats = pd.concat(
            [run.stats(args.raw_values) for run in data], ignore_index=True
        )
        stats_evals = stats.filter(like="evals_", axis=1)
        stats_y = stats.filter(like="y_", axis=1)
        stats_df = stats.drop(columns=stats_evals.columns.union(stats_y.columns))

        stats.to_csv(f"{filename_stem}.stats.csv")
        print(tabulate(stats_df, headers="keys", tablefmt="github"), "\n")
        print(tabulate(stats_y, headers="keys", tablefmt="github"), "\n")
        print(tabulate(stats_evals, headers="keys", tablefmt="github"), "\n")

        # stat tests
        if args.test_y:
            print("## Mann Whitney U test on optimization results (y).")
            print("p-values for alternative hypothesis row < column")
            print(
                display_test_grid(
                    mann_whitney_u_test_grid([run.bests_y() for run in data])
                ),
                "\n",
            )

        if args.test_evals:
            print("## Mann Whitney U test on number of objective function evaluations.")
            print("p-values for alternative hypothesis row < column")
            print(
                display_test_grid(
                    mann_whitney_u_test_grid([run.log_lengths() for run in data])
                ),
                "\n",
            )
