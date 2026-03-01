# SwiftUI Expert Skill

Expert guidance for any AI coding tool that supports the [Agent Skills open format](https://agentskills.io/home) — SwiftUI state management, view composition, performance, and iOS 26+ Liquid Glass adoption.

This repository distills practical SwiftUI best practices into actionable, concise references for agents and code review workflows.

## Who this is for
- Teams adopting modern SwiftUI APIs who want quick, correct defaults
- Developers reviewing or refactoring SwiftUI views and data flow
- Anyone shipping performant lists, scrolling, sheets, and navigation in SwiftUI

## See also my other skills:
- [Swift Concurrency Expert](https://github.com/AvdLee/Swift-Concurrency-Agent-Skill)
- [Core Data Expert](https://github.com/AvdLee/Core-Data-Agent-Skill)
- [Swift Testing Expert](https://github.com/AvdLee/Swift-Testing-Agent-Skill)

## How to Use This Skill

### Option A: Using skills.sh (recommended)
Install this skill with a single command:

```bash
npx skills add https://github.com/avdlee/swiftui-agent-skill --skill swiftui-expert-skill
```

For more information, [visit the skills.sh platform page](https://skills.sh/avdlee/swiftui-agent-skill/swiftui-expert-skill).

Then use the skill in your AI agent, for example:
> Use the swiftui expert skill and review the current SwiftUI code for state-management and performance improvements

### Option B: Claude Code Plugin

#### Personal Usage
To install this Skill for your personal use in Claude Code:

1. Add the marketplace:

```bash
/plugin marketplace add AvdLee/SwiftUI-Agent-Skill
```

2. Install the Skill:

```bash
/plugin install swiftui-expert@swiftui-expert-skill
```

#### Project Configuration
To automatically provide this Skill to everyone working in a repository, configure the repository's `.claude/settings.json`:

```json
{
  "enabledPlugins": {
    "swiftui-expert@swiftui-expert-skill": true
  },
  "extraKnownMarketplaces": {
    "swiftui-expert-skill": {
      "source": {
        "source": "github",
        "repo": "AvdLee/SwiftUI-Agent-Skill"
      }
    }
  }
}
```

When team members open the project, Claude Code will prompt them to install the Skill.

### Option C: Manual install
1) **Clone** this repository.
2) **Install or symlink** the `swiftui-expert-skill/` folder following your tool’s official skills installation docs (see links below).
3) **Use your AI tool** as usual and ask it to use the “swiftui-expert” skill for SwiftUI tasks.

#### Where to Save Skills
Follow your tool’s official documentation, here are a few popular ones:
- **Codex:** [Where to save skills](https://developers.openai.com/codex/skills/#where-to-save-skills)
- **Claude:** [Using Skills](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview#using-skills)
- **Cursor:** [Enabling Skills](https://cursor.com/docs/context/skills#enabling-skills)

**How to verify**:

Your agent should reference the workflow/checklists in `swiftui-expert-skill/SKILL.md` and jump into the relevant reference file for your task.

## What This Skill Offers

This skill gives your AI coding tool practical SwiftUI guidance. It can:

### Guide Your SwiftUI Decisions
- Choose the right state management tool (`@State`, `@Binding`, `@Observable`, `@Bindable`)
- Provide clear guidance for sheets, navigation, scrolling, and lists
- Advise on iOS 26+ Liquid Glass usage with safe availability fallbacks

### Write Better SwiftUI Views
- Keep view identity stable (e.g. avoid common `ForEach` pitfalls)
- Improve view composition for readability and efficient diffing
- Avoid common update/refresh pitfalls that cause unnecessary re-renders

### Improve Performance
- Reduce redundant state updates in hot paths
- Improve list performance via stable identity and consistent row structure
- Suggest image downsampling when `UIImage(data:)` is encountered (as an optional optimization)

## What Makes This Skill Different

**Non-Opinionated**: Focuses on SwiftUI correctness, not forcing an architecture, project structure, or code style.

**Practical & concise**: Treats the agent as capable; provides the checklists and pitfalls that actually matter in day-to-day SwiftUI work.

## Skill Structure
<!-- BEGIN REFERENCE STRUCTURE -->
```text
swiftui-expert-skill/
  SKILL.md
  references/
    accessibility-patterns.md - Accessibility traits, grouping, Dynamic Type, and VoiceOver
    animation-advanced.md - Performance, interpolation, and complex animation chains
    animation-basics.md - Core animation concepts, implicit/explicit animations, timing
    animation-transitions.md - View transitions, matchedGeometryEffect, and state changes
    image-optimization.md - AsyncImage usage, downsampling, caching
    latest-apis.md
    layout-best-practices.md - Layout patterns and GeometryReader alternatives
    liquid-glass.md - iOS 26+ glass effects and fallback patterns
    list-patterns.md - ForEach identity and list performance
    performance-patterns.md - Hot-path optimizations and update control
    scroll-patterns.md - ScrollViewReader and programmatic scrolling
    sheet-navigation-patterns.md - Sheets and type-safe navigation
    state-management.md - Property wrapper selection and data flow
    view-structure.md - View extraction and composition patterns
```
<!-- END REFERENCE STRUCTURE -->

## Maintenance

The repository includes a maintenance skill for keeping API guidance current:

```text
.agents/skills/update-swiftui-apis/
  SKILL.md               - Workflow for scanning Apple docs and updating latest-apis.md
  references/
    scan-manifest.md     - Categorized API areas, doc paths, and search queries to scan
```

Use this skill after new iOS or Xcode releases to refresh the deprecated API reference. It requires the [Sosumi MCP](https://github.com/kanaa257/sosumi.ai) to be available. See `AGENTS.md` or `CONTRIBUTING.md` for details.

## Contributing

Contributions are welcome! This repository follows the [Agent Skills open format](https://agentskills.io/home), which has specific structural requirements.

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for:
- How to contribute improvements to `SKILL.md` and the reference files
- Format requirements and quality standards
- Pull request process

## Acknowledgments

Several SwiftUI guidelines in this skill were inspired by or derived from the following works:

- [Skills](https://github.com/Dimillian/Skills) by [Thomas Ricouard](https://github.com/Dimillian) — a collection of SwiftUI-focused Codex skills covering UI patterns, performance auditing, and Liquid Glass.
- [SwiftLee SwiftUI articles](https://www.avanderlee.com/category/swiftui/) and [Swift articles](https://www.avanderlee.com/category/swift/) by [Antoine van der Lee](https://www.avanderlee.com) — practical SwiftUI best practices covering state management, accessibility, view composition, performance debugging, image optimization, and more.

## About the authors

Created by [Antoine van der Lee](https://www.avanderlee.com) and [Omar Elsayed](https://www.swiftdifferently.com). With years of experience in Swift & SwiftUI, this skill distills practical knowledge into actionable guidance for AI assistants. Antoine [published tens of articles on SwiftUI](https://www.avanderlee.com/category/swiftui/) on his blog called SwiftLee.

## Resources
- [Story behind this skill](https://www.swiftdifferently.com/blog/swiftui/How%20I%20stopped-resisting-ai-and-atarted-teaching-it)

## License

This skill is open-source and available under the MIT License. See [LICENSE](LICENSE) for details.
