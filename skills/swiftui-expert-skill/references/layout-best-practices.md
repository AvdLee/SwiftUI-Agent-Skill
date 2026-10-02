# SwiftUI Layout Best Practices Reference

## Table of Contents

- [Relative Layout Over Constants](#relative-layout-over-constants)
- [Context-Agnostic Views](#context-agnostic-views)
- [Adaptive and Resizable Interfaces](#adaptive-and-resizable-interfaces)
- [Adaptive Safe Areas](#adaptive-safe-areas)
- [Two-Column Reflow for Card Screens](#two-column-reflow-for-card-screens)
- [Two-Region Arrangements (iOS 27.1+)](#two-region-arrangements-ios-271)
- [Reserved Regions (iOS 27.1+)](#reserved-regions-ios-271)
- [Own Your Container](#own-your-container)
- [Layout Performance](#layout-performance)
- [View Logic and Testability](#view-logic-and-testability)
- [Full-Width Views](#full-width-views)
- [Action Handlers](#action-handlers)
- [Summary Checklist](#summary-checklist)

## Relative Layout Over Constants

**Use dynamic layout calculations instead of hard-coded values.**

```swift
// Good - relative to actual layout
GeometryReader { geometry in
    VStack {
        HeaderView()
            .frame(height: geometry.size.height * 0.2)
        ContentView()
    }
}

// Avoid - magic numbers that don't adapt
VStack {
    HeaderView()
        .frame(height: 150)  // Doesn't adapt to different screens
    ContentView()
}
```

**Why**: Hard-coded values don't account for different screen sizes, orientations, or dynamic content (like status bars during phone calls).

Avoid fixed frames that match one device (for example `.frame(width: 390, height: 844)`) and hard-coded safe-area insets; both break when the window resizes.

## Context-Agnostic Views

**Views should work in any context.** Never assume presentation style or screen size.

```swift
// Good - adapts to given space
struct ProfileCard: View {
    let user: User
    
    var body: some View {
        VStack {
            Image(user.avatar)
                .resizable()
                .aspectRatio(contentMode: .fit)
            Text(user.name)
            Spacer()
        }
        .padding()
    }
}

// Avoid - assumes full screen
struct ProfileCard: View {
    let user: User
    
    var body: some View {
        VStack {
            Image(user.avatar)
                .frame(width: UIScreen.main.bounds.width)  // Wrong!
            Text(user.name)
        }
    }
}
```

**Why**: Views should work as full screens, modals, sheets, popovers, or embedded content.

## Adaptive and Resizable Interfaces

Size views from the **proposed size**, not from a fixed screen or orientation. Prefer `@Environment(\.horizontalSizeClass)` / `verticalSizeClass`, `ViewThatFits`, and `AnyLayout` when choosing a layout variant. Avoid `UIScreen.main`, `UIScreen.main.bounds`, and portrait/landscape assumptions — those do not track the space actually offered to the view (split view, Stage Manager, windows, sheets).

```swift
struct AdaptiveStack<Content: View>: View {
    @Environment(\.horizontalSizeClass) private var horizontalSizeClass
    @ViewBuilder let content: Content

    var body: some View {
        let layout = horizontalSizeClass == .compact
            ? AnyLayout(VStackLayout())
            : AnyLayout(HStackLayout())
        layout { content }
    }
}
```

Use `ViewThatFits` when a compact alternative should replace a layout that overflows the proposal. Do not branch layout on device orientation or a cached screen size.

Use size classes for *what* to show (for example, fewer or more columns) and the proposed size, `containerRelativeFrame`, or `GeometryReader` for *how big* to draw something. When a layout decision only changes at a breakpoint, prefer `onChange(of: horizontalSizeClass)` over `onChange(of: geometry.size)`, which fires on every resize step.

Avoid branching on a size class between two containers that already adapt on their own, such as `TabView` and `NavigationSplitView`. Swapping the container changes view identity mid-resize and discards navigation state and collapse animations. Branch only when the two layouts are genuinely different, and let `NavigationSplitView` and toolbar overflow handle compact-to-regular transitions. For `TabView`, see [Tab Bar and Sidebar](sheet-navigation-patterns.md#tab-bar-and-sidebar-ios-27).

At wide sizes, consider capping the width of long-form text with `.frame(maxWidth:)` so line lengths stay readable.

Read `@Environment(\.horizontalSizeClass)` or `@Environment(\.verticalSizeClass)` in the `View` or `ViewModifier` nearest the layout decision. Do not cache a size class in an `App`, `Scene`, model, or view model: those objects do not own the view's current proposal and can go stale during resizing. Move the decision into the view, or pass the current value into non-view code at the point of use when that code genuinely needs it.

At a representable boundary, use `context.environment.horizontalSizeClass` or `context.environment.verticalSizeClass` in `makeUIView` / `updateUIView` and the corresponding view-controller methods. This carries the SwiftUI layout context into the bridge without process-global state.

Classify an idiom check before replacing it. Use a size class only when the underlying question is available width or height. A genuine platform, device-idiom, or product-capability decision is not equivalent to a size-class decision, and SwiftUI exposes no user-interface-idiom environment value. Preserve that distinction rather than inventing a size-class mapping or encouraging a global idiom read for ordinary layout.

## Adaptive Safe Areas

Make layout decisions from the size SwiftUI proposes to the view. Flag code that subtracts a `GeometryProxy`'s safe-area insets from its size, or reapplies those same insets as padding inside the reporting view: `GeometryProxy.size` already describes the offered content region, so that double-counts space SwiftUI reserved. Reading insets for diagnostics or passing geometry to a container that has a different proposal is not itself a bug; the problem is applying the same inset twice.

Choose the safe-area modifier by content:

- Use `safeAreaBar(edge:)` for bar content on iOS 26 and aligned releases. It reserves space and supplies bar appearance and scroll-edge behavior. Use `safeAreaInset(edge:)` as the fallback for older targets.
- Use `safeAreaInset(edge:)` for other controls or content that should occupy an inset region.
- When interactive bar content in a `ZStack` or overlay covers scrolling or other content, move the bar out to `safeAreaBar(edge:)` so SwiftUI reserves its space. Do not apply this replacement to a full-bleed background, gradient, artwork layer, or scrim.
- Use `safeAreaPadding` only for an intentional fixed design margin measured inward from the safe area. It does not read or track the current inset, so do not replace a hardcoded stand-in for a bar or device inset with `safeAreaPadding`; remove the stand-in and let safe-area layout reserve the space.
- Scope `ignoresSafeArea(_:edges:)` to only the intended edges. Ignoring all edges is appropriate for a truly full-bleed visual layer such as a background or scrim, not for readable or interactive content.

Avoid `GeometryReader` whose only purpose is to read and reapply safe-area insets. Prefer `safeAreaBar`, `safeAreaInset`, or an intentional fixed `safeAreaPadding`, which express placement without manually carrying inset values.

Vertical toolbar behavior, including `toolbarVerticalEdge`, belongs in [toolbar-patterns.md](toolbar-patterns.md).

## Two-Column Reflow for Card Screens

Apple's iPhone Duo guidance says not to just stretch the compact layout: reflow stacked content into two columns when width allows ([HIG](https://developer.apple.com/design/human-interface-guidelines/designing-for-iphone-duo)). For a scrolling card screen, write a custom `Layout` that reads each child's column from a `LayoutValueKey` (set through a small `.column(_:)` modifier). Children without a column span the full width.

- Choose between the custom layout and `VStackLayout` through `AnyLayout` (see [Adaptive and Resizable Interfaces](#adaptive-and-resizable-interfaces)) when the cards own `@State`, so it survives resizing. A plain branch recreates the cards but is fine when state lives above them, and keeps a compact `LazyVStack`.
- For differently sized cards, assign columns explicitly (masonry). For uniform cards, use a row-major grid that proposes the row's tallest height to both cells; the card surface must accept it (`frame(maxHeight: .infinity)` before the background), opt-in.
- Keep reading and VoiceOver order equal to the single-column order, and keep accessibility Dynamic Type sizes in one column.
- Each column is narrower than the compact screen; grids nested inside may need fewer columns.
- With default `MainActor` isolation, `LayoutValueKey` types and helpers called from `Layout` methods need `nonisolated` if the compiler reports isolated-conformance errors.

## Two-Region Arrangements (iOS 27.1+)

`ArrangementView` is a layout container for a primary and secondary view. Prefer the system's adaptive navigation and presentation containers when they already express the interface. Use an arrangement for an existing custom two-region layout that would otherwise be an `HStack`/`VStack` or `ZStack`:

- `.split` fits a main/detail or peer relationship where neither region should obscure the other.
- `.overlay` fits a foreground/background relationship where temporary overlap is acceptable.

```swift
struct AdaptivePlayer: View {
    var body: some View {
        if #available(iOS 27.1, *) {
            ArrangementView {
                PlayerView()
            } secondary: {
                UpNextView()
            }
            .arrangementViewStyle(.split.axes(.horizontal))
        } else {
            ViewThatFits {
                HStack {
                    PlayerView()
                    UpNextView()
                }
                VStack {
                    PlayerView()
                    UpNextView()
                }
            }
        }
    }
}
```

Both split and overlay styles accept `axes(_:)`. Leave the axes unconstrained when either orientation is valid. Restrict the set only when the content relationship requires it; if a split cannot use the permitted axis in the current proposal, the arrangement may show a single region instead of forcing an unsuitable split. Keep the earlier-OS fallback equivalent in hierarchy and functionality.

Treat these nesting combinations conservatively in the Xcode 27.1 beta:

- Do not put `NavigationSplitView` inside `ArrangementView`, or `ArrangementView` inside `NavigationSplitView`.
- Do not put `ArrangementView` inside `List` or `ScrollView`.

An arrangement supplies layout, not navigation infrastructure. Keep it inside a `NavigationStack` when the arranged content needs stack navigation. Each region handles its own scrolling.

Apple favors small adjustments over rearrangement. Switching between an arrangement and a different layout rebuilds the regions and drops state such as playback or slider position, so consider keeping one arranged branch on the flat inner display (chosen by size classes) and varying only the split axis, with state that must survive owned above the branch. Use accessibility sort priorities when the arranged visual order differs from the logical order.

Tuning modifiers (iOS 27.1+): `splitArrangementLayoutRatio`, `splitArrangementLayoutSize`, `splitArrangementFixedLayoutSize`, and `overlayArrangementEdge`; read `@Environment(\.splitArrangementAxis)` and `@Environment(\.overlayArrangementZIndex)` for the current axis and z-index.

## Reserved Regions (iOS 27.1+)

Start with system containers and presentations: they already adapt around relevant system UI and hardware regions. Query `GeometryProxy.reservedRegions(kind:options:layoutDirectionBehavior:)` only for custom edge-to-edge UI or manually laid-out controls that cannot be expressed with those containers.

```swift
GeometryReader { proxy in
    let divisions = proxy.reservedRegions(kind: .division)
    let occlusions = proxy.reservedRegions(kind: .occlusion)

    CustomCanvas(
        divisionFrames: divisions.map(\.frame),
        occlusionFrames: occlusions.map(\.frame)
    )
}
```

A `.division` region separates the view's bounds into usable areas; use it to move or resize a coherent element into one area rather than spanning the divider. An `.occlusion` region covers a smaller frame within the bounds; keep important visible or interactive content out of that frame. Each `ReservedRegion` also exposes `margins` and `isActive`.

Apple's documentation disagrees on whether a default query includes inactive regions, so do not rely on it: filter on `isActive` before displacing content, and pass `options: .includeInactive` when a decision needs to know a region exists while inactive:

```swift
let possibleDivisions = proxy.reservedRegions(
    kind: .division,
    options: .includeInactive
)
```

Do not treat an inactive region as a current obstruction; inspect `isActive` before displacement. Inactive division regions can have a zero-sized frame.

### Sizing a custom layout around a fold

To put a gutter over a fold (for example in the [two-column reflow](#two-column-reflow-for-card-screens)), call `onGeometryChange` on the laid-out view, so the region frame shares its coordinate space, and store the result in `@State`. The transform closure is `@Sendable` and must return `Equatable & Sendable` values (`nonisolated` under default `MainActor` isolation).

- Keep only vertical divisions (`height > width`) for column layouts; a horizontal fold through scrolling content needs no displacement.
- Query with `.includeInactive` so columns don't jump while folding, fall back to an even split for a zero-sized frame, and widen the gutter only while `isActive`.
- Grids: Apple prefers an even column count whenever a division exists, even an inactive one. While the fold is active, size each side separately (margins can be asymmetric) and let the last leading column's spacing cover the fold.

The query's `layoutDirectionBehavior` defaults to `.mirrors`, so directional geometry follows right-to-left layout. Preserve that default for interface content. Override it only when coordinates intentionally represent physical hardware placement rather than leading/trailing UI, and keep the reason explicit.

These APIs require the Xcode 27.1 SDK and iOS 27.1 at runtime. Put declarations that name the new types in an `@available(iOS 27.1, *)` scope, select them with `#available`, and keep a safe-area or ordinary adaptive-layout fallback for earlier systems.

## Own Your Container

**Custom views should own static containers but not lazy/repeatable ones.**

```swift
// Good - owns static container
struct HeaderView: View {
    var body: some View {
        HStack {
            Image(systemName: "star")
            Text("Title")
            Spacer()
        }
    }
}

// Avoid - missing container
struct HeaderView: View {
    var body: some View {
        Image(systemName: "star")
        Text("Title")
        // Caller must wrap in HStack
    }
}

// Good - caller owns lazy container
struct FeedView: View {
    let items: [Item]
    
    var body: some View {
        LazyVStack {
            ForEach(items) { item in
                ItemRow(item: item)
            }
        }
    }
}
```

## Layout Performance

### Avoid Layout Thrash

**Minimize deep view hierarchies and excessive layout dependencies.**

```swift
// Bad - deep nesting, excessive layout passes
VStack {
    HStack {
        VStack {
            HStack {
                VStack {
                    Text("Deep")
                }
            }
        }
    }
}

// Good - flatter hierarchy
VStack {
    Text("Shallow")
    Text("Structure")
}
```

**Avoid excessive `GeometryReader` and preference chains:**

```swift
// Bad - multiple geometry readers cause layout thrash
GeometryReader { outerGeometry in
    VStack {
        GeometryReader { innerGeometry in
            // Layout recalculates multiple times
        }
    }
}

// Good - single geometry reader or use alternatives (iOS 17+)
containerRelativeFrame(.horizontal) { width, _ in
    width * 0.8
}
```

**Gate frequent geometry updates:**

```swift
// Bad - updates on every pixel change
.onPreferenceChange(ViewSizeKey.self) { size in
    currentSize = size
}

// Good - gate by threshold
.onPreferenceChange(ViewSizeKey.self) { size in
    let difference = abs(size.width - currentSize.width)
    if difference > 10 {  // Only update if significant change
        currentSize = size
    }
}
```

## View Logic and Testability

### Keep Business Logic in Services and Models

**Business logic belongs in services and models, not in views.** Views should stay simple and declarative — orchestrating UI state, not implementing business rules. This makes logic independently testable without requiring view instantiation.

> **iOS 17+**: Use `@Observable` with `@State`.

```swift
@Observable
final class AuthService {
    var email = ""
    var password = ""
    var isValid: Bool {
        !email.isEmpty && password.count >= 8
    }

    func login() async throws {
        // Business logic here — testable without the view
    }
}

struct LoginView: View {
    @State private var authService = AuthService()

    var body: some View {
        Form {
            TextField("Email", text: $authService.email)
            SecureField("Password", text: $authService.password)
            Button("Login") {
                Task {
                    try? await authService.login()
                }
            }
            .disabled(!authService.isValid)
        }
    }
}
```

For iOS 16 and earlier, use `ObservableObject` with `@StateObject` -- see `state-management.md` for the legacy pattern.

Avoid embedding business logic directly in view closures (e.g., validation checks inside a `Button` action). This makes logic untestable without view instantiation.

**Note**: This is about making business logic testable, not about enforcing a specific architecture. The key is that logic lives outside views where it can be tested independently.

## Full-Width Views

**When a single view needs to fill the available width, use `.frame(maxWidth: .infinity, alignment:)` instead of wrapping it in a stack with a `Spacer`.**

```swift
// Good - frame modifier
Text("Hello")
    .frame(maxWidth: .infinity, alignment: .leading)

// Avoid - unnecessary stack and spacer
HStack {
    Text("Hello")
    Spacer()
}
```

**Why**: `.frame(maxWidth:alignment:)` is a single modifier that clearly communicates intent. Wrapping in an `HStack` with a `Spacer` adds an extra container to the view hierarchy for no benefit.

## Action Handlers

**Separate layout from logic.** View body should reference action methods, not contain inline logic.

```swift
// Good - action references method
Button("Publish Project", action: publishService.handlePublish)

// Avoid - multi-line logic in closure
Button("Publish Project") {
    isLoading = true
    apiService.publish(project) { result in /* ... */ }
}
```

## Summary Checklist

- [ ] Use relative layout over hard-coded constants
- [ ] Views work in any context (don't assume screen size)
- [ ] Adapt with proposed size, size classes, `ViewThatFits`, or `AnyLayout` — not `UIScreen.main` or orientation
- [ ] Size classes are read nearest the consuming view (or from representable context), not cached in app/model state
- [ ] Size classes replace available-space decisions, not genuine idiom or product-capability decisions
- [ ] No device-sized fixed frames or hard-coded safe-area insets
- [ ] Breakpoint decisions observe the size class, not every `geometry.size` change; self-adapting containers are not swapped by branch
- [ ] Bar content uses `safeAreaBar` (with an availability fallback); other inset content uses `safeAreaInset`
- [ ] Overlay bars that cover content move to `safeAreaBar`; full-bleed visual layers remain overlays/backgrounds
- [ ] `safeAreaPadding` represents a fixed design margin, not a stand-in for a dynamic inset
- [ ] `ignoresSafeArea` names only intended edges unless the layer is truly full-bleed
- [ ] `GeometryReader` is not used solely to read and reapply safe-area insets
- [ ] `ArrangementView` expresses a two-region layout, has an earlier-OS fallback, and avoids unsupported container nesting
- [ ] System containers are preferred before custom `reservedRegions` handling
- [ ] Reserved-region queries distinguish `.division` from `.occlusion`; `.includeInactive` is intentional
- [ ] Directional reserved-region geometry preserves RTL mirroring unless physical coordinates are explicitly required
- [ ] Custom views own static containers
- [ ] Avoid deep view hierarchies (layout thrash)
- [ ] Gate frequent geometry updates by thresholds
- [ ] Business logic kept in services and models (not in views)
- [ ] Action handlers reference methods, not inline logic
- [ ] Use `.frame(maxWidth: .infinity, alignment:)` for full-width views (not `HStack` + `Spacer`)
- [ ] Avoid excessive `GeometryReader` usage
- [ ] Use `containerRelativeFrame()` when appropriate
