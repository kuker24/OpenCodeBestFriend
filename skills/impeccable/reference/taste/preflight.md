# Taste: Pre-Flight Visual & Mechanical Checklist

Deep reference module for Impeccable.
Adapted from [taste-skill](https://github.com/Leonxlnx/taste-skill) (MIT, Leonxlnx).

Run this mechanical audit before declaring any UI task complete:

## 1. Typography & Contrast
- [ ] **WCAG AA Contrast**: Body text ≥4.5:1, large text ≥3:1 against actual computed background.
- [ ] **Descender Clearance**: Check italic display headings containing `y`, `g`, `j`, `p`, `q` for clipped descenders; ensure sufficient line-height (`leading-[1.1]`) and bottom padding.
- [ ] **Button Contrast**: Verify button text contrast against button backgrounds across both default and hover states.

## 2. Layout & Viewport Checks
- [ ] **Single-Line CTAs**: Desktop button labels fit cleanly on a single line without wrapping.
- [ ] **No Duplicate CTA Intent**: Confirm that the page does not show multiple competing buttons for the same action (e.g. "Get Started", "Sign Up Free", and "Try Free" in the same view).
- [ ] **Hero Viewport Fit**: Primary headline and initial call-to-action are visible in the first 900px of desktop height.
- [ ] **No Horizontal Overflow**: Verify that mobile viewports (375px–430px) do not suffer unintended horizontal scrolling.

## 3. States & Media
- [ ] **Interactive Feedback**: Verify visible `:focus-visible` styling for keyboard navigation and `:active` tactile response.
- [ ] **Asset Authenticity**: Confirm all images are real or clearly labeled synthetic demo assets; no broken image URLs or `<div>`-drawn fake screenshots.
- [ ] **Reduced Motion**: Verify that animations collapse gracefully when `prefers-reduced-motion: reduce` is active.
