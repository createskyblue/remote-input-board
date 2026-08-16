# Clipboard Latency and History Insert Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Reduce remote paste latency while changing mobile history selection from whole-input replacement to insertion at the saved cursor/selection, with append behavior as the safe fallback.

**Architecture:** Keep the existing clipboard snapshot/restore flow, but use shorter condition-based polling windows and only wait for history ordering when the first history capture succeeded. Add a pure browser helper for text insertion so the selection behavior can be tested independently from the single-file HTML page.

**Tech Stack:** Python, Win32/WinRT clipboard APIs, inline browser JavaScript, unittest, Node.js.

---

### Task 1: Establish regression tests

**Files:**
- Create: `tests/test_frontend.py`
- Modify: `tests/test_typer.py`

**Steps:**
1. Add a Node-backed test for insertion at a caret, replacement of a selection, and append fallback when selection is unavailable.
2. Add a typer test that verifies the order wait is skipped when Windows history capture is unavailable.
3. Run the focused tests and confirm they fail for the current implementation.

### Task 2: Implement history insertion in the browser

**Files:**
- Modify: `py_remote_input/templates/index.html`

**Steps:**
1. Add a pure `insertTextAtSelection` helper returning the new value and caret position.
2. Add selection-aware composer focus support while preserving the empty-input backspace sentinel.
3. Change history selection to insert at the current selection/caret; use the end of the input when selection data is unavailable.
4. Remove the overwrite confirmation path and update the status text.
5. Run the frontend regression tests.

### Task 3: Reduce paste latency without losing remote-desktop compatibility

**Files:**
- Modify: `py_remote_input/typer.py`
- Modify: `tests/test_typer.py`

**Steps:**
1. Reduce polling interval and restore delay based on the measured Windows history update timing.
2. Skip the post-restore ordering wait when history capture failed or clipboard history is disabled.
3. Keep the ordering confirmation when capture succeeds, so the second-history-item guarantee remains intact.
4. Run the typer tests and the real Windows clipboard-history probe.

### Task 4: Verify end to end

**Steps:**
1. Run the complete unittest suite and `git diff --check`.
2. Rebuild the PyInstaller package.
3. Restart the local service and verify the HTTP endpoint.
4. Manually verify history insertion at the middle of text and append behavior with no active caret.
