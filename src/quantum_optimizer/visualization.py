"""Visualization routines for QAOA optimization, distributions, and benchmarks."""

from typing import List, Optional, Tuple
import matplotlib.pyplot as plt
import numpy as np

from .problem import ProblemInstance
from .qaoa_solver import QAOAResult


def plot_convergence(
    history: List[float],
    output_path: Optional[str] = None,
    title: str = "QAOA Energy Convergence Trajectory",
) -> plt.Figure:
    """Plots expected Hamiltonian energy <H_C> across classical optimizer iterations."""
    fig, ax = plt.subplots(figsize=(8, 4.5), dpi=150)
    ax.plot(history, color="#1f77b4", linewidth=2.0, label=r"Expected Cost $\langle H_C \rangle$")
    ax.axhline(y=min(history), color="#d62728", linestyle="--", alpha=0.7, label=f"Min Energy: {min(history):.4f}")

    ax.set_xlabel("Optimizer Iteration (COBYLA)", fontsize=11, fontweight="bold")
    ax.set_ylabel(r"Expected Cost $\langle H_C \rangle$", fontsize=11, fontweight="bold")
    ax.set_title(title, fontsize=12, fontweight="bold", pad=12)
    ax.grid(True, linestyle=":", alpha=0.6)
    ax.legend(frameon=True, loc="upper right")
    fig.tight_layout()

    if output_path:
        fig.savefig(output_path, dpi=300)
    return fig


def plot_sampled_distribution(
    result: QAOAResult,
    output_path: Optional[str] = None,
    top_k: int = 10,
) -> plt.Figure:
    """Plots histogram of sampled bitstrings, color-coding feasible vs infeasible states."""
    top_samples = result.sampled_bitstrings[:top_k]
    labels = ["".join(str(b) for b in s[0]) for s in top_samples]
    counts = [s[1] for s in top_samples]
    feasibility = [s[4] for s in top_samples]

    colors = ["#2ca02c" if f else "#d62728" for f in feasibility]

    fig, ax = plt.subplots(figsize=(10, 5), dpi=150)
    bars = ax.bar(labels, counts, color=colors, edgecolor="black", linewidth=0.8, alpha=0.85)

    # Highlight optimal solution with a gold star or badge
    optimal_str = "".join(str(b) for b in result.known_optimal_assignment) if result.known_optimal_assignment else None
    for i, bar in enumerate(bars):
        if labels[i] == optimal_str:
            bar.set_edgecolor("#ffd700")
            bar.set_linewidth(2.5)
            ax.text(
                bar.get_x() + bar.get_width() / 2.0,
                bar.get_height() + 5,
                "★ OPTIMAL",
                ha="center",
                va="bottom",
                fontweight="bold",
                color="#b8860b",
                fontsize=9,
            )

    ax.set_xlabel("Portfolio Bitstring (Asset 0 to N-1)", fontsize=11, fontweight="bold")
    ax.set_ylabel(f"Sample Count (out of {result.shots} shots)", fontsize=11, fontweight="bold")
    ax.set_title(
        f"QAOA Sampled Solution Distribution (p={result.reps}, Yield={result.feasibility_yield:.1f}%)",
        fontsize=12,
        fontweight="bold",
        pad=12,
    )
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=9)
    ax.grid(axis="y", linestyle=":", alpha=0.6)

    # Custom legend
    import matplotlib.patches as mpatches
    green_patch = mpatches.Patch(color="#2ca02c", label=f"Feasible (sum(x) == {result.best_sampled_assignment.count(1)})")
    red_patch = mpatches.Patch(color="#d62728", label="Infeasible (Budget Violated)")
    ax.legend(handles=[green_patch, red_patch], loc="upper right")
    fig.tight_layout()

    if output_path:
        fig.savefig(output_path, dpi=300)
    return fig


def plot_depth_comparison(
    depths: List[int],
    approx_ratios: List[float],
    feasibility_yields: List[float],
    output_path: Optional[str] = None,
) -> plt.Figure:
    """Plots Approximation Ratio and Feasibility Yield as a function of QAOA circuit depth p."""
    fig, ax1 = plt.subplots(figsize=(8, 4.5), dpi=150)

    color_ar = "#1f77b4"
    ax1.set_xlabel("QAOA Circuit Depth (p)", fontsize=11, fontweight="bold")
    ax1.set_ylabel("Approximation Ratio (C_quantum / C_opt)", color=color_ar, fontsize=11, fontweight="bold")
    line1 = ax1.plot(depths, approx_ratios, color=color_ar, marker="o", linewidth=2.2, markersize=8, label="Approximation Ratio")
    ax1.tick_params(axis="y", labelcolor=color_ar)
    ax1.set_ylim([min(0.5, min(approx_ratios) - 0.05), 1.05])
    ax1.set_xticks(depths)
    ax1.grid(True, linestyle=":", alpha=0.6)

    ax2 = ax1.twinx()
    color_fy = "#2ca02c"
    ax2.set_ylabel("Feasibility Yield (%)", color=color_fy, fontsize=11, fontweight="bold")
    line2 = ax2.plot(depths, feasibility_yields, color=color_fy, marker="s", linestyle="--", linewidth=2.0, markersize=8, label="Feasibility Yield")
    ax2.tick_params(axis="y", labelcolor=color_fy)
    ax2.set_ylim([0, 100])

    lines = line1 + line2
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc="lower right", frameon=True)

    fig.suptitle("QAOA Performance Scaling with Circuit Depth (p)", fontsize=12, fontweight="bold", y=0.98)
    fig.tight_layout()

    if output_path:
        fig.savefig(output_path, dpi=300)
    return fig


def plot_penalty_sweep(
    lambdas: List[float],
    feasibility_yields: List[float],
    approx_ratios: List[float],
    output_path: Optional[str] = None,
) -> plt.Figure:
    """Plots Feasibility Yield and Approximation Ratio as a function of penalty multiplier lambda."""
    fig, ax1 = plt.subplots(figsize=(8, 4.5), dpi=150)

    color_fy = "#2ca02c"
    ax1.set_xlabel(r"Constraint Penalty Multiplier ($\lambda$)", fontsize=11, fontweight="bold")
    ax1.set_ylabel("Feasibility Yield (%)", color=color_fy, fontsize=11, fontweight="bold")
    line1 = ax1.plot(lambdas, feasibility_yields, color=color_fy, marker="o", linewidth=2.2, markersize=7, label="Feasibility Yield")
    ax1.tick_params(axis="y", labelcolor=color_fy)
    ax1.set_ylim([0, 105])
    ax1.grid(True, linestyle=":", alpha=0.6)

    ax2 = ax1.twinx()
    color_ar = "#ff7f0e"
    ax2.set_ylabel("Approximation Ratio", color=color_ar, fontsize=11, fontweight="bold")
    line2 = ax2.plot(lambdas, approx_ratios, color=color_ar, marker="^", linestyle="--", linewidth=2.0, markersize=7, label="Approximation Ratio")
    ax2.tick_params(axis="y", labelcolor=color_ar)
    ax2.set_ylim([0.4, 1.05])

    lines = line1 + line2
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc="center right", frameon=True)

    fig.suptitle(r"Penalty Multiplier ($\lambda$) vs Solution Feasibility & Quality", fontsize=12, fontweight="bold", y=0.98)
    fig.tight_layout()

    if output_path:
        fig.savefig(output_path, dpi=300)
    return fig
