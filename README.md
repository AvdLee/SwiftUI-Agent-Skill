# SwiftUI Expert Skill
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://github.com/AvdLee/SwiftUI-Agent-Skill/blob/main/LICENSE)
[![Weekly Installs](https://img.shields.io/badge/weekly%20installs-14.3k-brightgreen)](https://skills.sh/avdlee/swiftui-agent-skill/swiftui-expert-skill)
[![GitHub Release](https://img.shields.io/github/v/release/AvdLee/SwiftUI-Agent-Skill)](https://github.com/AvdLee/SwiftUI-Agent-Skill/releases)
[![GitHub Stars](https://img.shields.io/github/stars/AvdLee/SwiftUI-Agent-Skill?style=flat)](https://github.com/AvdLee/SwiftUI-Agent-Skill/stargazers)

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

### Option A: Using skills.sh
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

### Option C: Cursor plugin (coming soon)
This repository is now packaged for Cursor plugin submission, but the marketplace listing is not live yet.

Once approved, you'll be able to install it from the Cursor Marketplace.

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

### Option D: Codex / OpenAI-compatible tools
This repository includes an `agents/openai.yaml` manifest. Copy or symlink the `swiftui-expert-skill/` folder into your Codex skills directory:

```bash
cp -R swiftui-expert-skill/ "$CODEX_HOME/skills/swiftui-expert-skill"
```

See [Codex skills documentation](https://developers.openai.com/codex/skills/) for details on where to save skills.

### Option E: Using pi package manager

Install via [pi](https://github.com/badlogic/pi-mono):
```bash
pi install https://github.com/AvdLee/SwiftUI-Agent-Skill
```

The skill will be available automatically in pi sessions.

### Option F: Manual install
1) **Clone** this repository.
2) **Install or symlink** the `swiftui-expert-skill/` folder following your tool’s official skills installation docs (see links below).
3) **Use your AI tool** as usual and ask it to use the “swiftui-expert” skill for SwiftUI tasks.

#### Where to Save Skills
Follow your tool’s official documentation, here are a few popular ones:
- **Codex:** [Where to save skills](https://developers.openai.com/codex/skills/#where-to-save-skills)
- **Claude:** [Using Skills](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview)
- **Cursor:** [Plugins documentation](https://cursor.com/docs/plugins) or [Enabling Skills](https://cursor.com/docs/context/skills#enabling-skills)

**How to verify**:

Your agent should reference the workflow/checklists in `swiftui-expert-skill/SKILL.md` and jump into the relevant reference file for your task.

## What's Inside

This skill covers the full surface of SwiftUI development -- from state management and view composition to Swift Charts, macOS multi-window scenes, animations, and iOS 26+ Liquid Glass -- without bloating your agent's task context. Reference files load on demand, so your agent gets deep guidance only for the topic at hand.

- **State management** -- property wrapper selection, `@Observable`, data flow patterns
- **View composition** -- extraction patterns, container views, identity stability
- **Performance** -- hot-path optimization, lazy loading, `@Observable` granularity
- **Lists & ForEach** -- stable identity, Table, inline filtering pitfalls
- **Navigation & sheets** -- NavigationStack, NavigationSplitView, Inspector, enum-based sheets
- **Swift Charts** -- marks, axes, selection, styling, accessibility, Chart3D
- **Animations** -- implicit/explicit, transitions, phase/keyframe, `@Animatable` macro
- **macOS** -- scenes, window styling, Table, HSplitView, AppKit interop
- **Liquid Glass** -- iOS 26+ glass effects, containers, fallback patterns
- **Accessibility** -- VoiceOver, Dynamic Type, grouping, traits
- **Image optimization** -- AsyncImage, downsampling, caching
- **Latest APIs** -- deprecated-to-modern migration guide (iOS 15+ through iOS 26+)

Non-opinionated: focuses on correctness and performance, not architecture or code style.

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
    charts-accessibility.md - Charts accessibility, fallback strategies, and WWDC sessions
    charts.md - Swift Charts marks, axes, selection, styling, composition, and Chart3D
    focus-patterns.md
    image-optimization.md - AsyncImage usage, downsampling, caching
    latest-apis.md
    layout-best-practices.md - Layout patterns and GeometryReader alternatives
    liquid-glass.md - iOS 26+ glass effects and fallback patterns
    list-patterns.md - ForEach identity and list performance
    macos-scenes.md - Scene lifecycle, multi-window setups, and menu bar scenes on macOS
    macos-views.md - macOS-specific SwiftUI views and platform differences from iOS
    macos-window-styling.md - Window chrome, toolbar, and title bar styling in SwiftUI
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

Note: only `swiftui-expert-skill` is intended to be published in the Cursor plugin. The maintenance skill remains a repository workflow utility.

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
- [Swift Charts Examples](https://github.com/jordibruin/Swift-Charts-Examples) by [Jordi Bruin](https://x.com/jordibruin) — a comprehensive collection of Swift Charts examples covering line, bar, area, range, heat map, and point charts with accessibility and customization patterns. Used with permission.

## About the authors

Created by [Antoine van der Lee](https://www.avanderlee.com) and [Omar Elsayed](https://www.swiftdifferently.com). With years of experience in Swift & SwiftUI, this skill distills practical knowledge into actionable guidance for AI assistants. Antoine [published tens of articles on SwiftUI](https://www.avanderlee.com/category/swiftui/) on his blog called SwiftLee.

## Resources
- [Story behind this skill](https://www.swiftdifferently.com/blog/swiftui/How%20I%20stopped-resisting-ai-and-atarted-teaching-it)

## License

This skill is open-source and available under the MIT License. See [LICENSE](LICENSE) for details.
