# -*- coding: utf-8 -*-
"""
origin_plot.py — Reliable Origin COM plotting for Codex.

Usage (from Codex Python runtime):
    python origin_plot.py

Or inline:
    from origin_plot import OriginPlotter
    op = OriginPlotter()
    op.create_force_figure(data, export_path)

Key lessons from battle-testing:
- expGraph often returns True but creates NO file. Use page.export as fallback.
- save -i crashes COM. Skip project saving or save manually.
- merge_graph may return False. Export individual graphs as fallback.
- Always kill existing Origin before starting: taskkill /f /im Origin64.exe
"""

import os
import sys
import time
import subprocess
from pathlib import Path

ORIGIN_EXE = r"D:\Program Files\OriginLab\Origin2022\Origin64.exe"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def find_origin():
    """Find Origin installation path."""
    paths = [
        ORIGIN_EXE,
        r"C:\Program Files\OriginLab\Origin2022\Origin64.exe",
        r"C:\Program Files\OriginLab\Origin2021\Origin64.exe",
    ]
    for p in paths:
        if os.path.exists(p):
            return p
    # Search
    for root in [r"C:\Program Files", r"D:\Program Files"]:
        try:
            result = subprocess.run(
                ["where", "/r", root, "Origin64.exe"],
                capture_output=True, text=True, timeout=30
            )
            if result.stdout.strip():
                return result.stdout.strip().split("\n")[0]
        except Exception:
            pass
    return None


def kill_origin():
    """Kill all Origin processes."""
    subprocess.run(["taskkill", "/f", "/im", "Origin64.exe"],
                   capture_output=True)
    time.sleep(2)


# ---------------------------------------------------------------------------
# OriginPlotter class
# ---------------------------------------------------------------------------

class OriginPlotter:
    """Reliable COM interface to Origin for Codex-driven plotting."""

    def __init__(self, visible=True):
        self.origin = None
        self.origin_exe = find_origin()
        if not self.origin_exe:
            raise FileNotFoundError(
                "Origin64.exe not found. Check registry or install path."
            )
        self.visible = visible

    def __enter__(self):
        import pythoncom
        pythoncom.CoInitialize()
        kill_origin()
        # Launch Origin via COM
        import win32com.client
        self.origin = win32com.client.Dispatch("Origin.Application")
        self.origin.Visible = self.visible
        time.sleep(3)  # Let Origin finish loading splash
        return self

    def __exit__(self, *args):
        import pythoncom
        pythoncom.CoUninitialize()

    def ex(self, cmd):
        """Execute a LabTalk command. Returns bool."""
        return self.origin.Execute(cmd)

    def new_project(self):
        self.ex("newproject")
        time.sleep(1)

    def create_workbook(self, name="Data", ncols=6, nrows=4):
        """Create a workbook with given dimensions."""
        self.ex("win -t wks")
        time.sleep(0.5)
        self.ex(f"wks.ncols = {ncols}")
        self.ex(f"wks.nrows = {nrows}")
        self.ex(f'page.label$ = "{name}"')
        time.sleep(0.5)

    def set_col_name(self, col, name):
        """Set column long name."""
        self.ex(f'wks.col{col}.name$ = "{name}"')

    def set_x_col(self, col=1):
        """Set column as X."""
        self.ex(f"wks.col{col}.type = 4")

    def fill_cell(self, col, row, value):
        """Fill a single cell."""
        if isinstance(value, str):
            self.ex(f'col({col})[{row}]$ = "{value}"')
        else:
            self.ex(f"col({col})[{row}] = {value}")

    def fill_data(self, data_dict, x_col=1, x_values=None):
        """
        Fill workbook from a dict: {col_idx: [values], ...}
        col_idx is 1-based (A=1, B=2, ...)
        """
        if x_values:
            for i, v in enumerate(x_values):
                self.fill_cell(x_col, i + 1, v)
        for col_idx, values in data_dict.items():
            for i, v in enumerate(values):
                self.fill_cell(col_idx, i + 1, v)

    def activate_page(self, name="Data"):
        """Activate a page by its label."""
        self.ex(f'win -a {name}')

    def create_graph(self, iy, plot_type=202, template="Column"):
        """
        Create a graph.
        iy: tuple like (1,2) for cols 1(x) and 2(y)
        plot_type: 202=Column, 201=Line+Symbol
        """
        self.activate_page()
        self.ex(
            f'plotxy iy:=({iy[0]},{iy[1]}) plot:={plot_type} '
            f'ogl:=[<new template:={template}>]'
        )
        time.sleep(2)

    def set_axis_labels(self, xlabel, ylabel):
        self.ex(f'xb.text$ = "{xlabel}"')
        self.ex(f'yl.text$ = "{ylabel}"')

    def set_axis_range(self, x_from, x_to, y_from, y_to):
        self.ex(f"layer.x.from = {x_from}")
        self.ex(f"layer.x.to = {x_to}")
        self.ex(f"layer.y.from = {y_from}")
        self.ex(f"layer.y.to = {y_to}")

    def set_title(self, title):
        self.ex(f'label -s -sa -n title "{title}"')

    def export_png(self, filepath, width=2400, height=3600):
        """
        Export current graph as PNG.
        Tries expGraph, falls back to page.export.
        """
        fpath = str(Path(filepath)).replace("\\", "/")
        os.makedirs(os.path.dirname(fpath) or ".", exist_ok=True)

        # Method 1: expGraph
        r = self.ex(
            f'expGraph type:=png filename:="{fpath}" '
            f'width:={width} height:={height} tr1.unit:=2'
        )
        time.sleep(3)
        if os.path.exists(filepath):
            return filepath

        # Method 2: page.export
        r = self.ex(
            f'page.export(type:=png, filename:={fpath})'
        )
        time.sleep(3)
        if os.path.exists(filepath):
            return filepath

        # Method 3: expGraph with forward slashes, no quotes
        r = self.ex(
            f'expGraph type:=png filename:={fpath} '
            f'width:={width} height:={height} tr1.unit:=2'
        )
        time.sleep(3)
        if os.path.exists(filepath):
            return filepath

        print(f"WARNING: Could not export to {filepath}")
        return None


# ---------------------------------------------------------------------------
# High-level API
# ---------------------------------------------------------------------------

def create_force_figure(data, export_dir):
    """
    Create a 3-panel Origin figure for combined-tool force analysis.

    data: dict with keys:
        - "penetration": list of penetration values
        - "cutting_force": list of cutting tool forces
        - "leading_force": list of leading tool forces
        - "specific_energy": list of SE values
        - "k_coeff": list of K coefficient values

    export_dir: directory for output PNGs
    """
    x = data["penetration"]
    cfs = {
        2: data["cutting_force"],     # Col B
        3: data["leading_force"],     # Col C
        4: data["specific_energy"],   # Col D
        5: data["k_coeff"],           # Col E
    }

    with OriginPlotter(visible=True) as op:
        op.new_project()

        # Workbook
        op.create_workbook("Data", ncols=6, nrows=len(x))
        op.set_col_name(1, "Penetration(mm)")
        op.set_col_name(2, "CuttingTool(N)")
        op.set_col_name(3, "LeadingTool(N)")
        op.set_col_name(4, "SE(N/mm)")
        op.set_col_name(5, "K_coeff")
        op.set_x_col(1)
        op.fill_data(cfs, x_col=1, x_values=x)

        # Graph 1: Forces (Grouped Column)
        op.create_graph((1, 2), plot_type=202, template="Column")
        op.set_axis_labels("Penetration (mm)", "Cutting Force (N)")
        op.set_axis_range(0, 65, 0, 700)
        op.set_title("(a) Combined Tool Forces")
        p1 = op.export_png(os.path.join(export_dir, "Fig1_Force.png"))

        # Graph 2: Specific Energy (Line+Symbol)
        op.create_graph((1, 3), plot_type=201, template="LineSymb")
        op.set_axis_labels("Penetration (mm)", "Specific Energy (N/mm)")
        op.set_axis_range(0, 65, 0, 55)
        op.set_title("(b) Cutting Specific Energy")
        p2 = op.export_png(os.path.join(export_dir, "Fig2_SE.png"))

        # Graph 3: K coefficient (Line+Symbol)
        op.create_graph((1, 4), plot_type=201, template="LineSymb")
        op.set_axis_labels("Penetration (mm)", "Synergistic Coefficient K")
        op.set_axis_range(0, 65, 0.40, 0.55)
        op.set_title("(c) Synergistic Coefficient")
        p3 = op.export_png(os.path.join(export_dir, "Fig3_K.png"))

    return {"force": p1, "se": p2, "k": p3}


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Default: run the penetration analysis with known data
    data = {
        "penetration": [10, 20, 40, 50],
        "cutting_force": [130.32, 145.10, 177.15, 192.82],
        "leading_force": [292.05, 316.03, 361.17, 391.48],
        "specific_energy": [42.24, 23.06, 13.46, 11.69],
        "k_coeff": [0.4462, 0.4591, 0.4905, 0.4925],
    }
    export_dir = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
    result = create_force_figure(data, export_dir)
    print("Export results:", result)
