"""Drive the running Flask UI in a real headless Chromium and save screenshots.

Usage:
    python3 tools/capture_ui.py <base_url> <prefix> <text> <expect_substring>

Screenshots are written to submission_evidence/<prefix>_input.png and
submission_evidence/<prefix>_blank.png using Playwright against the system
Chromium binary. Nothing is rendered or synthesized.
"""

import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

EVIDENCE = Path(__file__).resolve().parent.parent / "submission_evidence"


def main():
    """Capture a successful emotion analysis and a blank-input error."""
    base_url = sys.argv[1]
    prefix = sys.argv[2]
    text = sys.argv[3]
    expected = sys.argv[4]
    EVIDENCE.mkdir(exist_ok=True)

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            executable_path="/usr/bin/chromium",
            args=["--no-sandbox", "--disable-gpu"],
        )
        page = browser.new_page(viewport={"width": 1280, "height": 900})

        page.goto(base_url, wait_until="networkidle")
        page.fill("#textToAnalyze", text)
        page.click("button")
        page.wait_for_function(
            "expected => document.getElementById('system_response')"
            ".innerText.includes(expected)",
            arg=expected,
            timeout=90000,
        )
        result = page.inner_text("#system_response")
        page.screenshot(path=str(EVIDENCE / f"{prefix}_input.png"), full_page=True)

        page.fill("#textToAnalyze", "")
        page.click("button")
        page.wait_for_function(
            "() => document.getElementById('system_response')"
            ".innerText.includes('Invalid text! Please try again!')",
            timeout=90000,
        )
        blank = page.inner_text("#system_response")
        page.screenshot(path=str(EVIDENCE / f"{prefix}_blank.png"), full_page=True)

        browser.close()

    print(f"URL           : {base_url}")
    print(f"INPUT TEXT    : {text}")
    print(f"APP RESPONSE  : {result}")
    print(f"BLANK RESPONSE: {blank}")
    print(f"SCREENSHOTS   : {EVIDENCE / (prefix + '_input.png')}")
    print(f"                {EVIDENCE / (prefix + '_blank.png')}")


if __name__ == "__main__":
    main()
