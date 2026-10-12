"""Start ohne Installation:  python run.py run config.yaml"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))
from cfdpost.cli import main  # noqa: E402

main()
