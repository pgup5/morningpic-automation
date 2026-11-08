from pathlib import Path
from playwright.sync_api import (
    sync_playwright,
    TimeoutError as PlaywrightTimeoutError,
)

URL = "https://morningpic.streamlit.app/"
WAKE_BUTTON = "Yes, get this app back up!"

Path("results").mkdir(exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    try:
        page.goto(
            URL,
            wait_until="domcontentloaded",
            timeout=90_000,
        )

        wake = page.get_by_role(
            "button",
            name=WAKE_BUTTON,
            exact=True,
        )

        try:
            wake.wait_for(state="visible", timeout=30_000)
        except PlaywrightTimeoutError:
            print("沒有看到休眠按鈕；請查看截圖確認頁面狀態。")
        else:
            wake.click(timeout=15_000)
            print("已點擊喚醒按鈕。")

            wake.wait_for(state="hidden", timeout=120_000)
            print("休眠按鈕已消失；仍需查看截圖確認 App 是否正常。")

        # 留一點時間讓 Streamlit 載入畫面。
        page.wait_for_timeout(15_000)

    finally:
        page.screenshot(
            path="results/page.png",
            full_page=True,
            timeout=30_000,
        )
        Path("results/page.txt").write_text(
            page.locator("body").inner_text(),
            encoding="utf-8",
        )
        browser.close()
