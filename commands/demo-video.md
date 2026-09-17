---
description: "Manual specialist: demo-video"
---

Load and follow the OpenCode-adapted manual specialist `demo-video` (alias for `id-demo-video`).

Plan and produce an application walkthrough demo video with Indonesian narration using the `id-demo-video` specialist.

Collect the following parameters from user arguments or context:
1. Application target URL (e.g. `http://localhost:3000`)
2. Start command (how to start if offline, e.g. `npm run dev`)
3. Target duration (default: `10:00` / 600 seconds)
4. Voice: `id-ID-GadisNeural` (default, female) or `id-ID-ArdiNeural` (male)
5. Output directory: `demos/<slug>/`

Then load and follow the canonical `id-demo-video` specialist:
- In repository tree: `skills/id-demo-video/SKILL.md`
- After installation: `~/.config/opencode/skills/id-demo-video/SKILL.md`

User arguments:

$ARGUMENTS

Do not substitute another specialist. Do not load this via the skill tool.
