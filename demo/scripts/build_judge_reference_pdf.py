"""Build the consolidated judge reference appendix PDF.

The module notes in demo/presentation_notes remain the source of truth. This
script combines them into one Pandoc source file and compiles a PDF appendix.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
NOTES_DIR = ROOT / "demo" / "presentation_notes"
DECK_DIR = ROOT / "demo" / "presentation_deck"

OUTPUT_MD = NOTES_DIR / "kshetraai_judge_reference_appendix.md"
OUTPUT_PDF = DECK_DIR / "kshetraai_judge_reference_appendix.pdf"

SOURCE_FILES = [
    "01_data_foundation.md",
    "02_feature_generation.md",
    "03_dynamic_prioritization.md",
    "04_contextual_decision.md",
    "05_anomaly_and_opportunity_detection.md",
    "06_explainability_and_trust.md",
    "07_outcome_learning_and_feedback.md",
    "08_fastapi_backend_integration.md",
    "09_frontend_dashboard_and_workflow.md",
    "10_demo_integration_testing_final_polish.md",
]


def read_source_file(filename: str) -> str:
    path = NOTES_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Missing appendix source file: {path}")
    return path.read_text(encoding="utf-8").strip()


def build_markdown() -> str:
    frontmatter = """---
title: "KshetraAI"
author: ""
date: "May 2026"
documentclass: book
classoption:
  - 11pt
  - oneside
  - openany
toc: true
toc-depth: 2
numbersections: true
top-level-division: chapter
geometry: "a4paper,margin=1in"
fontsize: 11pt
hidelinks: true
header-includes: |
  \\usepackage{xcolor}
  \\definecolor{KshetraGreen}{HTML}{0B6B45}
  \\definecolor{KshetraLeaf}{HTML}{5FA777}
  \\definecolor{KshetraSlate}{HTML}{334155}
  \\pagestyle{plain}
  \\renewcommand{\\maketitle}{%
    \\begin{titlepage}
    \\centering
    \\vspace*{1.2cm}
    {\\color{KshetraGreen}\\rule{0.82\\textwidth}{1.2pt}\\par}
    \\vspace{1.8cm}
    {\\Huge\\bfseries\\color{KshetraGreen} KshetraAI\\par}
    \\vspace{0.85cm}
    {\\LARGE\\bfseries\\color{KshetraSlate} Judge Reference Appendix\\par}
    \\vspace{1.35cm}
    {\\Large\\color{KshetraSlate} Explainable Field-Force Intelligence\\par}
    \\vspace{0.18cm}
    {\\Large\\color{KshetraSlate} for Agricultural Sales Operations\\par}
    \\vfill
    {\\large\\bfseries\\color{KshetraGreen} Stage 1 Submission\\par}
    \\vspace{0.28cm}
    {\\large\\color{KshetraSlate} Syngenta Hackathon\\par}
    \\vspace{0.28cm}
    {\\large\\color{KshetraSlate} May 2026\\par}
    \\vspace{1.4cm}
    {\\color{KshetraLeaf}\\rule{0.42\\textwidth}{0.8pt}\\par}
    \\end{titlepage}
  }
  \\makeatletter
  \\def\\@makechapterhead#1{\\vspace*{18pt}{\\parindent \\z@ \\raggedright \\normalfont \\Huge\\bfseries \\thechapter\\quad #1\\par\\nobreak\\vskip 28pt}}
  \\def\\@makeschapterhead#1{\\vspace*{18pt}{\\parindent \\z@ \\raggedright \\normalfont \\Huge\\bfseries #1\\par\\nobreak\\vskip 28pt}}
  \\makeatother
---

"""

    intro = """\\mainmatter

# Document Scope

This appendix consolidates the judge-reference notes for KshetraAI into one
reviewable document. It is intended to support the presentation deck with
implementation-grounded detail.

The claims in this appendix are limited to the current codebase, generated
artifacts, sample outputs, and verified demo workflow. Where a capability is a
foundation or future scope, it is labeled that way.

## Reference Roadmap

| Section | What It Covers |
|---|---|
| Data Foundation | source boundaries, schemas, public-data readiness |
| Feature Generation | normalized decision signals and generated feature views |
| Dynamic Prioritization | visit ranking, component weights, and demo scenario output |
| Contextual Decision | next best action rules and recommendation evidence |
| Anomaly Detection | alerts, severity, confidence, and current calibration limits |
| Explainability | evidence-backed reasoning for priority, recommendations, and alerts |
| Outcome Learning | outcome capture and human-governed feedback foundation |
| API Integration | FastAPI contracts and processed-output serving boundary |
| Frontend Workflow | React dashboard path and UI behavior |
| Demo Integration | deterministic scenario, sample outputs, and acceptance checks |

\\newpage

"""

    sections: list[str] = []
    for index, filename in enumerate(SOURCE_FILES):
        if index:
            sections.append("\\newpage\n")
        sections.append(read_source_file(filename))
        sections.append("\n")

    closing_page = """\\newpage
\\thispagestyle{empty}
\\begin{center}
\\vspace*{3.2cm}
{\\color{KshetraGreen}\\rule{0.62\\textwidth}{1pt}\\par}
\\vspace{1.7cm}
{\\Huge\\bfseries\\color{KshetraGreen} KshetraAI\\par}
\\vspace{1.0cm}
{\\Large\\color{KshetraSlate} Explainable. Deterministic. Human-governed.\\par}
\\vfill
{\\LARGE\\bfseries\\color{KshetraSlate} Thank you.\\par}
\\vfill
{\\large\\color{KshetraSlate} Stage 1 Submission\\par}
\\vspace{0.22cm}
{\\large\\color{KshetraSlate} Syngenta Hackathon\\par}
\\vspace{0.22cm}
{\\large\\color{KshetraSlate} May 2026\\par}
\\vspace{1.2cm}
{\\color{KshetraLeaf}\\rule{0.36\\textwidth}{0.8pt}\\par}
\\end{center}
"""

    return frontmatter + intro + "\n".join(sections) + closing_page


def run_pandoc() -> None:
    pandoc = shutil.which("pandoc")
    if pandoc is None:
        raise RuntimeError("Pandoc is not installed or not available on PATH.")

    DECK_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_MD.write_text(build_markdown(), encoding="utf-8")

    command = [
        pandoc,
        str(OUTPUT_MD),
        "--from",
        "markdown+raw_tex",
        "--pdf-engine=pdflatex",
        "--top-level-division=chapter",
        "--toc",
        "--toc-depth=2",
        "--number-sections",
        "-o",
        str(OUTPUT_PDF),
    ]
    subprocess.run(command, cwd=ROOT, check=True)


def main() -> None:
    run_pandoc()
    print(f"Wrote {OUTPUT_MD.relative_to(ROOT)}")
    print(f"Wrote {OUTPUT_PDF.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
