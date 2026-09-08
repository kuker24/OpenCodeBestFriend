# Academic Integrity & Toolchain Policy

Standards governing sources, toolchain availability, and ethical boundaries.

## Attribution & Anti-Plagiarism Standards

- **Source Traceability:** Every factual statement, equation, or parameter value not established by the current author's original experiments must cite its primary provenance.
- **Direct Quotation:** Verbatim excerpts must be set in quotation marks or blockquotes with page-level citations.
- **Paraphrasing Discipline:** Paraphrasing must reflect genuine synthesis, not simple synonym substitution.
- **Zero Detector Evasion:** Do not perform lexical obfuscation to bypass automated similarity checkers or detectors. Focus exclusively on scholarly clarity and genuine attribution.

## Toolchain & Compilation Gates

- **Pandoc / LaTeX / Typst:**
  - If compiling to PDF/TeX/Word is requested and the host system lacks the compiler, return:
    `NOT_CONFIGURED: [pandoc|pdflatex|xelatex|typst] is not installed on this host.`
  - Never fake successful document compilation or return a corrupt binary placeholder.
- **Reference Management:**
  - Standard BibTeX/CSL JSON formats should be generated directly in text.
  - If a Zotero / Mendeley bridge is not available locally, export standard `.bib` files.

## Source Verification Protocol

- Canonical sources: Official publisher DOIs (doi.org), arXiv / bioRxiv / medRxiv pre-prints, OpenReview archives, IEEE Xplore, ACM Digital Library, PubMed.
- When an article title or author is provided by memory/heuristic but cannot be resolved via available web tools:
  - Mark as `[UNVERIFIED CITATION: <details>]`.
  - Prompt the researcher to provide the DOI or local PDF source before integrating into a locked manuscript.
