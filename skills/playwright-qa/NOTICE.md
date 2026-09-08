# Playwright QA Skill Notice

This skill is an OpenCodeBestFriend adaptation of the Playwright CLI interface
originally developed by Microsoft Corporation.

- Upstream project: https://github.com/microsoft/playwright-cli
- Upstream commit: 655530f6d0dc71a0d6bf46ae165877d3c7311099
- License: Apache License 2.0 (see vendor/licenses/MICROSOFT-PLAYWRIGHT-CLI-APACHE2.txt)
- Copyright (c) Microsoft Corporation

## Modifications for OpenCodeBestFriend
- Adapted as an in-session exploratory QA tool for local UI changes.
- Scoped browser sessions with task/workspace naming to prevent cross-project collisions.
- Explicit runtime discovery without unprompted background downloads or package mutations.
- Strict separation between OCBF tool invocation and target application dependencies.
- Suite preservation: project Playwright Test and other E2E suites remain authoritative for regressions.
