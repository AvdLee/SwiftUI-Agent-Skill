# Contributing to SwiftUI Expert Skill

Thanks for your interest in improving this skill. Contributions that make SwiftUI guidance clearer, more accurate, and more up to date are welcome.

## About Agent Skills
Agent Skills are structured prompt assets with:
- A `SKILL.md` file that defines behavior and checklists
- Reference files that provide focused guidance for specific topics

## Recommended Workflow (Skill Creator)
If you use the `skill-creator` skill, you can:
- Propose changes in plain language
- Have the skill generate or refine `SKILL.md` and reference content
- Review for SwiftUI accuracy and consistency

## Alternative Workflows
### Claude without skill-creator
- Make changes directly in `SKILL.md` or `swiftui-expert-skill/references/`
- Keep content concise and focused on SwiftUI

### Manual edits
- Edit Markdown files directly
- Ensure headings and checklists stay consistent

## Updating Latest API Guidance

To refresh the deprecated-to-modern API reference after a new iOS or Xcode release, use the maintenance skill at `.agents/skills/update-swiftui-apis/SKILL.md`. It walks through scanning Apple's documentation via the Sosumi MCP and updating `swiftui-expert-skill/references/latest-apis.md` with new findings.

## Types of Contributions
- Fix incorrect SwiftUI guidance
- Add new modern APIs or deprecations
- Improve clarity in checklists
- Expand reference files with specific SwiftUI patterns
- Improve documentation in README or this guide

## Quality Standards
- SwiftUI-specific content only
- Avoid architecture mandates or project structure requirements
- Avoid tooling instructions beyond basic git usage
- Use modern APIs and flag deprecated ones
- Prefer clear, direct language over opinionated phrasing

## Pull Request Process
1. Fork the repo (or branch if you have access).
2. Make changes in a focused scope.
3. Ensure `SKILL.md` and references remain consistent.
4. Open a PR with a short summary and test notes.

## Development Setup
- Standard Markdown editing is sufficient.
- If you add or rename reference files, the README structure is auto-synced via GitHub Actions.

## Resources
- Agent Skills documentation: https://docs.anthropic.com/en/docs/claude-code/agent-skills
- SwiftUI documentation: https://developer.apple.com/documentation/swiftui

## Code of Conduct
Be respectful and constructive. Assume positive intent and focus on improving the quality of SwiftUI guidance.
