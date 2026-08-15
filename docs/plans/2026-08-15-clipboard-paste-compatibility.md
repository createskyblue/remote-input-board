# Clipboard Paste History Preservation Plan

**Goal:** Paste through remote desktop software, then restore the previous clipboard content while keeping the newly pasted text as the second Windows clipboard-history item.

**Architecture:** Snapshot the existing Win32 clipboard formats, write and paste the new text, wait until Windows Clipboard History has indexed that text, then restore the snapshot through Win32 clipboard APIs. The delayed restore gives remote desktop software time to consume the text. After restoring, the code also waits for Windows Clipboard History to finish indexing the restore, then confirms the remote-paste text is the second item instead of erasing it before history capture.

**Tech Stack:** Python, `ctypes` Win32 clipboard APIs, Python/WinRT `Clipboard` history APIs, `unittest`, PyInstaller.

## Steps

1. Add failing tests for restoring the previous clipboard after history capture and after history polling timeout.
2. Add WinRT clipboard-history dependencies and implement clipboard snapshot/restore plus history polling.
3. Run the typer tests and complete unittest suite.
4. Run a real Windows clipboard-history probe and verify the restored item is first and the remote-paste text is second.
5. Rebuild and restart the packaged service.
