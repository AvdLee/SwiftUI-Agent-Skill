# Agent Guidelines for SwiftUI Expert Skill

This document provides guidance for AI agents working with this skill to ensure consistency and avoid common pitfalls.

## Core Principles

### 1. SwiftUI Focus Only
**This is a SwiftUI skill.** Do not include:
- Swift concurrency patterns (use `.task` for SwiftUI-specific needs only)
- General Swift language features unrelated to SwiftUI
- Backend or server-side Swift patterns
- UIKit patterns (except when bridging is necessary)

### 2. No Code Formatting or Linting
**Do not include formatting/linting rules.** Avoid:
- Property ordering requirements (environment, state, body, etc.)
- Code organization mandates
- Whitespace or indentation rules
- Naming convention enforcement
- File structure requirements

**Exception**: Mention organization patterns as *optional suggestions* for readability, never as requirements.

### 3. No Architectural Opinions
**Stick to facts, not architectures.** Avoid:
- Enforcing MVVM, MVC, VIPER, or any specific architecture
- Mandating view model patterns
- Requiring specific folder structures
- Dictating dependency injection patterns
- Prescribing router/coordinator patterns

**Exception**: Suggest separating business logic for testability without enforcing how.

### 4. No Tool-Specific Instructions
**Agents cannot use external tools.** Do not include:
- Xcode Instruments profiling instructions
- Debugging tool usage
- IDE-specific features
- Command-line tool usage beyond basic git

**Exception**: Mention that users can profile with Instruments if performance issues arise, but don't provide detailed instructions.

## Content Guidelines

### Suggestions vs Requirements

**Use "suggest" or "consider" for optional optimizations:**
- ✅ "Consider downsampling images when using `UIImage(data:)`"
- ❌ "Always downsample images"

**Use "always" or "never" only for correctness issues:**
- ✅ "Never use `.indices` for dynamic ForEach content"
- ✅ "Always mark `@State` as `private`"

### Performance Optimizations

**Present performance optimizations as optional improvements:**
- Image downsampling: Suggest when `UIImage(data:)` is encountered
- POD view wrappers: Mention as advanced optimization technique
- Equatable conformance: Suggest for expensive views

**Do not automatically apply optimizations.** Let developers decide based on their performance needs.

## What to Include

### ✅ Include These Topics:
- Property wrapper selection (`@State`, `@Binding`, `@Observable`, etc.)
- View composition and extraction patterns
- Performance patterns (stable identity, lazy loading, etc.)
- Common pitfalls and how to avoid them
- Sheet, navigation, and list patterns
- Liquid Glass API usage (iOS 26+)
- Accessibility best practices

### ❌ Exclude These Topics:
- Swift concurrency deep dives (actors, sendable, etc.)
- Code formatting and style rules
- Architectural patterns and mandates
- Tool usage instructions (Instruments, debuggers)
- File organization requirements
- Testing frameworks and patterns
- Build system configuration
- Project structure mandates

## Language and Tone

### Use Clear, Direct Language:
- "Consider X when Y" (for optimizations)
- "Avoid X because Y" (for anti-patterns)
- "X is preferred over Y" (for best practices)

### Avoid Prescriptive Language:
- ❌ "You must organize properties in this order"
- ❌ "Always use MVVM architecture"
- ❌ "Profile with Instruments following these steps"
- ❌ "Structure your project like this"

## Examples

### Good Example:
```markdown
## ForEach Identity

**Always provide stable identity for `ForEach`.** Never use `.indices` for dynamic content.

When you encounter `UIImage(data:)`, consider suggesting image downsampling as a performance optimization.
```

### Bad Example:
```markdown
## View Organization

**Always organize view properties in this order:**
1. Environment
2. State
3. Body
4. Helpers

**Use Instruments to profile:**
1. Open Instruments
2. Select SwiftUI template
3. Record and analyze...
```

## Updating the Skill

When adding new content:
1. Ask: "Is this SwiftUI-specific?"
2. Ask: "Is this a fact or an opinion?"
3. Ask: "Can agents actually use this?"
4. Ask: "Is this about correctness or style?"

If unsure, err on the side of excluding content. It's better to have a focused, factual skill than a comprehensive but opinionated one.

## Maintenance Skills

This repository includes a maintenance skill for keeping API guidance up to date:

- **`.agents/skills/update-swiftui-apis/SKILL.md`** — Scan Apple's SwiftUI documentation via the Sosumi MCP, identify deprecated APIs and their modern replacements, and update `swiftui-expert-skill/references/latest-apis.md`. Use after new iOS/Xcode releases or when you want to refresh the deprecated API reference.

## Summary

**Focus**: SwiftUI APIs, patterns, and correctness
**Avoid**: Formatting, architecture, tools, Swift language features
**Tone**: Factual, helpful, non-prescriptive
**Goal**: Make agents SwiftUI experts without enforcing opinions
