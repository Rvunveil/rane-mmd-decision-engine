"""
Tests for Project Handbook (docs/HANDBOOK.md)
Team 11:59 · Xovate'26 · Rane (Madras) MMD Decision Engine

Verifies Section 0 Rule 6 requirements:
1. File exists and every TOC link resolves to a valid markdown heading.
2. Every file in the repository (except .git, _refs, .venv, caches, qa/ images) appears in the file inventory.
3. Every engine function and every page is mentioned in the document.
4. The deny-list of invented entity names is completely absent.
5. Every number quoted for the baseline and the 10% shock matches run_all().
"""

import os
import re
import ast
import pytest
from engine.scenario import Scenario
from engine.chain import run_all

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HANDBOOK_PATH = os.path.join(BASE_DIR, "docs", "HANDBOOK.md")


@pytest.fixture(scope="module")
def handbook_text():
    assert os.path.exists(HANDBOOK_PATH), f"HANDBOOK.md does not exist at {HANDBOOK_PATH}"
    with open(HANDBOOK_PATH, "r", encoding="utf-8") as f:
        return f.read()


def test_handbook_exists_and_toc_resolves(handbook_text):
    """Verifies that the handbook exists and every link in the TOC resolves to a real heading."""
    # Extract TOC section
    assert "## Table of Contents" in handbook_text or "# Table of Contents" in handbook_text
    
    # Extract all headings and build GitHub anchor slugs
    heading_slugs = set()
    for line in handbook_text.splitlines():
        if line.startswith("#"):
            # strip markdown heading markers
            title = re.sub(r"^#+\s*", "", line).strip()
            # GitHub slugify: lowercase, remove characters except alphanumeric, space, hyphen
            slug = title.lower()
            slug = re.sub(r"[^\w\s-]", "", slug)
            slug = re.sub(r"[\s_]+", "-", slug).strip("-")
            heading_slugs.add(slug)
    
    # Extract TOC block using robust string offsets
    start_idx = handbook_text.find("## Table of Contents")
    end_idx = handbook_text.find("\n# Part A — Understand It", start_idx)
    assert start_idx != -1 and end_idx != -1, "Could not locate Table of Contents block"
    toc_block = handbook_text[start_idx:end_idx]
    
    toc_links = re.findall(r"\[([^\]]+)\]\(#([^\)]+)\)", toc_block)
    assert len(toc_links) >= 26, f"Expected at least 26 section TOC links, found {len(toc_links)}"
    
    missing_targets = []
    for title, anchor in toc_links:
        if anchor not in heading_slugs:
            missing_targets.append((title, anchor))
            
    assert not missing_targets, f"TOC anchors failed to resolve to headings: {missing_targets}"


def test_all_repo_files_in_inventory(handbook_text):
    """Verifies that every file in the repository (excluding caches/venv/qa images) is listed in the inventory."""
    repo_files = []
    ignored_dirs = {".git", "_refs", ".venv", ".pytest_cache", "__pycache__", "build", ".dart_tool", ".gradle", ".kotlin", ".idea"}
    for root, dirs, files in os.walk(BASE_DIR):
        dirs[:] = [d for d in dirs if d not in ignored_dirs]
        for f in files:
            if f.endswith((".pyc", ".log", ".apk", ".aab", ".dill", ".stamp", ".iml")) or f == ".DS_Store":
                continue
            rel = os.path.relpath(os.path.join(root, f), BASE_DIR).replace(os.sep, "/")
            if rel.startswith("qa/") and rel.endswith((".png", ".jpg", ".webm")):
                continue
            if rel.startswith("demo_out/") and rel.endswith(".webm"):
                continue
            if rel.startswith("Dataset xovate (!)"):  # redundant root copy
                continue
            if rel == "docs/HANDBOOK.md":  # The generated file itself
                continue
            repo_files.append(rel)
            
    assert len(repo_files) >= 90, f"Expected at least 90 repo files, found {len(repo_files)}"
    
    missing_files = []
    for rf in repo_files:
        # Check either full path or basename if distinctive
        if rf not in handbook_text and os.path.basename(rf) not in handbook_text:
            missing_files.append(rf)
            
    assert not missing_files, f"Files missing from handbook inventory ({len(missing_files)}): {missing_files[:15]}"


def test_all_engine_functions_and_pages_mentioned(handbook_text):
    """Verifies that every engine function and page is explicitly mentioned in the handbook."""
    # 1. Check pages
    expected_pages = [
        "pages/0_Command_Centre.py",
        "pages/1_Forecast.py",
        "pages/2_Scenario_Simulator.py",
        "pages/3_Profit_Chain.py",
        "pages/4_Containers_Inventory.py",
        "pages/5_Action_Matrix.py",
        "pages/6_Assumptions_Data_Trace_About.py"
    ]
    for page in expected_pages:
        assert page in handbook_text or os.path.basename(page) in handbook_text, f"Page {page} not mentioned in handbook"
        
    # 2. Extract engine functions via AST
    engine_dir = os.path.join(BASE_DIR, "engine")
    engine_funcs = []
    for fname in os.listdir(engine_dir):
        if fname.endswith(".py") and fname != "__init__.py":
            with open(os.path.join(engine_dir, fname), "r", encoding="utf-8") as f:
                tree = ast.parse(f.read())
            for node in tree.body:
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if not node.name.startswith("_"):  # Public functions
                        engine_funcs.append(node.name)
                        
    assert len(engine_funcs) >= 20, f"Expected >= 20 engine functions, extracted {len(engine_funcs)}"
    
    missing_funcs = []
    for func in engine_funcs:
        if func not in handbook_text:
            missing_funcs.append(func)
            
    assert not missing_funcs, f"Engine functions missing from handbook: {missing_funcs}"


def test_deny_list_absent(handbook_text):
    """Verifies that no ungrounded or invented entity names appear anywhere in the handbook."""
    deny_list = [
        "Maruti", "Tata Motors", "Hyundai", "Renault", "Nissan", "Cummins", "Brembo",
        "Maersk", "MSC", "CMA CGM", "Hapag", "Hindalco", "Vedanta", "Supreme Petrochem",
        "SBI", "HDFC", "Clause 4.2", "Puducherry", "Pantnagar", "Sanand", "Queretaro", "Tumkur", "Viralimalai",
        "ICIS Phenolic", "European Valve"
    ]
    pattern = re.compile(r'\b(' + '|'.join(re.escape(w) for w in deny_list) + r')\b', re.IGNORECASE)
    matches = list(set(pattern.findall(handbook_text)))
    assert not matches, f"Forbidden invented entities found in docs/HANDBOOK.md: {matches}"


def test_baseline_and_shock_numbers_match_engine(handbook_text):
    """Verifies that all numerical values quoted for baseline and 10% shock match run_all() results."""
    # Baseline
    base_res = run_all(Scenario())
    assert f"{base_res.revenue_cr:,.2f}" in handbook_text or f"{base_res.revenue_cr:.1f}" in handbook_text
    assert f"{base_res.ebitda_cr:.2f}" in handbook_text or f"{base_res.ebitda_cr:.1f}" in handbook_text
    assert f"{base_res.material_spend_cr:,.2f}" in handbook_text or f"{base_res.material_spend_cr:.0f}" in handbook_text
    assert f"{base_res.ocean_freight_spend_cr:.2f}" in handbook_text or f"{base_res.ocean_freight_spend_cr:.0f}" in handbook_text
    assert f"{base_res.pat_cr:.2f}" in handbook_text or f"{base_res.pat_cr:.1f}" in handbook_text

    # 10% shock
    shock_scn = Scenario(
        price_shock_pct={
            "copper": 10.0, "nickel": 10.0, "aluminium": 10.0, "resin": 10.0,
            "rubber": 10.0, "steel_hr": 10.0, "steel_cr": 10.0
        }
    )
    shock_res = run_all(shock_scn)
    assert f"{shock_res.delta_material_cr:.2f}" in handbook_text
    assert f"{shock_res.oem_recovery_cr:.2f}" in handbook_text
    assert f"{shock_res.ebitda_cr:.2f}" in handbook_text
    assert f"{shock_res.pat_cr:.2f}" in handbook_text
    assert f"{shock_res.working_capital_gap_cr:.2f}" in handbook_text
