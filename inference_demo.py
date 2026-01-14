"""Demo script showing the full two-stage classification pipeline."""

from __future__ import annotations

import shutil

import dspy

from src.common.config import configure_lm
from src.serving.service import (
    AECategoryRequest,
    AEPCRequest,
    PCCategoryRequest,
    get_ae_category_classifier,
    get_ae_pc_classifier,
    get_pc_category_classifier,
)

SHOW_PROMPTS = False  # Set to False to hide DSPy prompt/response details

SAMPLE_COMPLAINTS = [
    "After my first Ozempic injection, I developed severe hives and my throat started swelling.",
    "The Ozempic pen I received has a crack in the barrel and is leaking medication.",
]


class Display:
    """Collapsible display helpers for terminal output."""

    _MAGENTA = "\033[95m"
    _CYAN = "\033[96m"
    _YELLOW = "\033[93m"
    _WHITE = "\033[97m"
    _DIM = "\033[2m"
    _RESET = "\033[0m"
    _TREE_WIDTH = 70
    _current_branch: str | None = None
    _depth: int = 0
    _INDENT = "  "

    @classmethod
    def _terminal_width(cls) -> int:
        return shutil.get_terminal_size().columns

    @classmethod
    def _color_for(cls, classification: str | None = None) -> str:
        branch = classification or cls._current_branch
        return cls._YELLOW if branch == "Adverse Event" else cls._CYAN

    @classmethod
    def _is_ae(cls) -> bool:
        return cls._current_branch == "Adverse Event"

    @classmethod
    def _tree_width(cls) -> int:
        return min(cls._terminal_width(), cls._TREE_WIDTH)

    @classmethod
    def header(cls):
        line = "═" * cls._tree_width()
        print(f"\n{cls._MAGENTA}{line}")
        print("  TWO-STAGE CLASSIFICATION PIPELINE")
        print(f"{line}{cls._RESET}\n")

    @classmethod
    def footer(cls):
        print(f"{cls._WHITE}{'═' * cls._tree_width()}{cls._RESET}\n")

    @classmethod
    def complaint(cls, num: int, text: str):
        cls._depth = 0
        cls._current_branch = None
        line = "─" * cls._tree_width()
        print(f"{cls._WHITE}{line}{cls._RESET}")
        print(f"{cls._MAGENTA}COMPLAINT {num}{cls._RESET}")
        print(f"{cls._WHITE}{text}{cls._RESET}")
        print(f"{cls._WHITE}{line}{cls._RESET}")
        print(f"{cls._WHITE}│{cls._RESET}")

    @classmethod
    def stage(cls, label: str):
        is_router = "Router" in label
        is_category = "Category" in label
        if is_router:
            color = cls._WHITE
        elif is_category:
            color = cls._color_for()
        else:
            color = cls._MAGENTA
        prefix = cls._INDENT * cls._depth
        print(f"{cls._WHITE}{prefix}└─ {color}[{label}]{cls._RESET}")
        cls._depth += 1

    @classmethod
    def prompt_response(cls):
        if SHOW_PROMPTS:
            print(cls._DIM)
            dspy.inspect_history(n=1)
            print(cls._RESET)

    @classmethod
    def result(cls, classification: str, justification: str | None = None):
        if classification in ("Adverse Event", "Product Complaint"):
            cls._current_branch = classification
        color = cls._color_for()
        prefix = cls._INDENT * cls._depth
        print(f"{cls._WHITE}{prefix}└─ {color}➜ {classification}{cls._RESET}")
        if justification:
            detail_prefix = cls._INDENT * (cls._depth + 1)
            print(f"{cls._WHITE}{detail_prefix}{cls._DIM}{justification}{cls._RESET}")
        cls._depth += 1

    @classmethod
    def separator(cls):
        print(f"{cls._WHITE}{'─' * cls._tree_width()}{cls._RESET}\n")


# =============================================================================
# Main classification logic
# =============================================================================


def main() -> None:
    configure_lm()

    classify_ae_pc = get_ae_pc_classifier()
    classify_ae_category = get_ae_category_classifier()
    classify_pc_category = get_pc_category_classifier()

    Display.header()

    for i, complaint_text in enumerate(SAMPLE_COMPLAINTS, 1):
        Display.complaint(i, complaint_text)

        # Stage 1: Route to AE or PC
        Display.stage("STAGE 1: AE vs PC Router")
        stage1 = classify_ae_pc(AEPCRequest(complaint=complaint_text))
        Display.prompt_response()
        Display.result(stage1.classification)

        # Stage 2: Category classification based on Stage 1
        is_ae = stage1.classification == "Adverse Event"
        Display.stage(f"STAGE 2: {'AE' if is_ae else 'PC'} Category")
        if is_ae:
            stage2 = classify_ae_category(AECategoryRequest(complaint=complaint_text))
        else:
            stage2 = classify_pc_category(PCCategoryRequest(complaint=complaint_text))
        Display.prompt_response()
        Display.result(stage2.classification, stage2.justification)

        Display.separator()

    Display.footer()


if __name__ == "__main__":
    main()
