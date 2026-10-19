#!/usr/bin/env python3
"""Rasterize a diagram page to PNG: the diagram-design skill's export procedure, verbatim in behaviour.
usage: python3 assets/src/export-png.py <src.html> <out.png> [scale]
"""
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError, sync_playwright
import sys, pathlib, math

src, out = sys.argv[1], sys.argv[2]
scale = float(sys.argv[3]) if len(sys.argv) > 3 else 2
if not math.isfinite(scale) or not 1 <= scale <= 4:
    raise ValueError("PNG scale must be a finite number between 1 and 4")

with sync_playwright() as p:
    try:
        browser = p.chromium.launch()
    except Exception:
        # no bundled browser: use the machine's own Chrome through Playwright's channel (nothing gets installed)
        browser = p.chromium.launch(channel="chrome")
    page = browser.new_page(device_scale_factor=scale)
    page.goto(pathlib.Path(src).resolve().as_uri() + "?motion=static", wait_until="domcontentloaded")
    try:
        page.wait_for_load_state("networkidle", timeout=15000)
    except PlaywrightTimeoutError:
        page.evaluate("window.stop()")
        page.wait_for_timeout(4000)
        print("warning: webfont request stalled - captured with fallback typography; the PNG may not match the intended fonts", file=sys.stderr)
    page.evaluate("document.fonts.ready")
    if not page.locator("[data-motion-root]").evaluate_all(
        "roots => roots.every(root => root.dataset.frame === 'static')"
    ):
        raise RuntimeError("motion export requires a complete static frame")
    svg = page.locator("svg").first
    svg.evaluate("""el => {
        const box = el.viewBox.baseVal;
        if (![box.width, box.height].every(n => Number.isFinite(n) && n > 0))
            throw new Error('PNG export requires a nonzero finite viewBox');
        for (const [axis, size] of [['width', box.width], ['height', box.height]])
            for (const prefix of ['', 'min-', 'max-'])
                el.style.setProperty(prefix + axis, size + 'px', 'important');
    }""")
    svg.evaluate("el => { for (let a = el.parentElement; a; a = a.parentElement) a.style.setProperty('overflow', 'visible', 'important'); }")
    svg.screenshot(path=out, omit_background=True)
    browser.close()
