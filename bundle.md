---
bundle:
  name: deepwiki
  version: 1.4.0
  description: AI-powered open-source project understanding via DeepWiki

includes:
  - bundle: git+https://github.com/microsoft/amplifier-foundation@main
  - bundle: deepwiki:behaviors/deepwiki
---

# DeepWiki Integration

Understand open-source projects with AI-powered documentation analysis.

<!-- Awareness context is injected by behaviors/deepwiki.yaml -->

---

@foundation:context/shared/common-system-base.md
