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

Apple's main advice for a large display is not to stretch the compact layout: reflow stacked cards into two columns when width allows. A custom `Layout` with a `LayoutValueKey` for column assignment fits a scrolling dashboard of differently sized cards. Swap it with `VStackLayout` through `AnyLayout` so children keep identity and `@State` across size changes.

```swift
nonisolated struct ColumnKey: LayoutValueKey {
    static let defaultValue: Int? = nil
}

extension View {
    func column(_ index: Int) -> some View { layoutValue(key: ColumnKey.self, value: index) }
}

/// `.column(0)` / `.column(1)` children stack in two columns; unassigned children span the full width below.
struct TwoColumnLayout: Layout {
    var spacing: CGFloat = 20

    func sizeThatFits(proposal: ProposedViewSize, subviews: Subviews, cache: inout ()) -> CGSize {
        let width = proposal.width ?? 0
        return CGSize(width: width, height: arrange(width: width, subviews: subviews).height)
    }

    func placeSubviews(in bounds: CGRect, proposal: ProposedViewSize, subviews: Subviews, cache: inout ()) {
        let frames = arrange(width: bounds.width, subviews: subviews).frames
        for (subview, frame) in zip(subviews, frames) {
            subview.place(at: CGPoint(x: bounds.minX + frame.minX, y: bounds.minY + frame.minY),
                          proposal: ProposedViewSize(frame.size))
        }
    }

    nonisolated private func arrange(width: CGFloat, subviews: Subviews) -> (frames: [CGRect], height: CGFloat) {
        let columnWidth = max((width - spacing) / 2, 0)
        var columnY = [CGFloat](repeating: 0, count: 2)
        var frames = [CGRect](repeating: .zero, count: subviews.count)
        for (index, subview) in subviews.enumerated() {
            guard let column = subview[ColumnKey.self], (0..<2).contains(column) else { continue }
            let height = subview.sizeThatFits(ProposedViewSize(width: columnWidth, height: nil)).height
            frames[index] = CGRect(x: CGFloat(column) * (columnWidth + spacing), y: columnY[column],
                                   width: columnWidth, height: height)
            columnY[column] += height + spacing
        }
        var y = columnY.max() ?? 0
        for (index, subview) in subviews.enumerated() where subview[ColumnKey.self] == nil {
            let height = subview.sizeThatFits(ProposedViewSize(width: width, height: nil)).height
            frames[index] = CGRect(x: 0, y: y, width: width, height: height)
            y += height + spacing
        }
        return (frames, max(y - spacing, 0))
    }
}

struct Dashboard: View {
    @Environment(\.horizontalSizeClass) private var horizontalSizeClass
    @Environment(\.dynamicTypeSize) private var dynamicTypeSize

    var body: some View {
        let usesColumns = horizontalSizeClass == .regular && !dynamicTypeSize.isAccessibilitySize
        let layout = usesColumns ? AnyLayout(TwoColumnLayout()) : AnyLayout(VStackLayout(spacing: 20))

        ScrollView {
            layout {
                StorageCard().column(0)
                CleanupCard().column(1)
                RecentCard().column(0)
                FooterNote()
            }
        }
    }
}
```

- The `AnyLayout` swap is only needed when the children own state. An `if`/`else` between `HStack` and `VStack` recreates them and drops that state on every resize; when state lives above the cards, a plain branch is fine and keeps a compact `LazyVStack`.
- For uniform cards, a row-major grid that proposes the row's tallest height to both cells avoids ragged card bottoms. The card surface must accept the taller proposal (`frame(maxHeight: .infinity)` before the background); make that opt-in so other uses keep their size.
- Keep reading and VoiceOver order equal to the single-column order, and keep accessibility Dynamic Type sizes in a single column.
- Each column is narrower than the compact screen, so grids nested inside a column may need fewer columns to avoid truncating titles.
- To keep a fold out of the gutter, size the gutter from a `.division` region as described in [Reserved Regions](#reserved-regions-ios-271).

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

Favor small adjustments over rearrangement as the space changes. If a screen uses an arrangement on the flat inner display, keep it in one branch selected by size classes (regular width and height) and vary only the split axis, for example from aspect ratio. Resizing then keeps the regions and their state, such as playback or slider position, instead of rebuilding them. Own interaction state above the branch between the regular and arranged layouts, and use accessibility sort priorities when the arranged visual order differs from the logical order.

Tuning APIs (iOS 27.1+), applied to a region's content:

- `splitArrangementLayoutRatio(_:)` and `splitArrangementLayoutRatio(minHorizontal:idealHorizontal:maxHorizontal:minVertical:idealVertical:maxVertical:)` set the region's share of the split.
- `splitArrangementLayoutSize(minWidth:idealWidth:maxWidth:minHeight:idealHeight:maxHeight:)` and `splitArrangementFixedLayoutSize(horizontal:vertical:)` size a region explicitly.
- `@Environment(\.splitArrangementAxis)` (`Axis?`) reads the axis the split is using.
- For `.overlay`, `overlayArrangementEdge(_:)` chooses the edge, and `@Environment(\.overlayArrangementZIndex)` reads the overlay's z-index.

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

Apple's documentation disagrees on whether a default query includes inactive regions: the method discussion says it returns regions regardless of activity, while `.includeInactive` implies active-only. Do not rely on the default; always filter on `isActive`. Pass `options: .includeInactive` when a decision needs to know a region exists while inactive:

```swift
let possibleDivisions = proxy.reservedRegions(
    kind: .division,
    options: .includeInactive
)
```

Do not treat an inactive region as a current obstruction; inspect `isActive` before displacement. Inactive division regions can have a zero-sized frame.

### Sizing a custom layout around a fold

To place a gutter over a fold in a custom layout such as the [two-column reflow](#two-column-reflow-for-card-screens), read the region with `onGeometryChange` on the laid-out view so the frame shares that view's coordinate space:

```swift
@available(iOS 27.1, *)
struct FoldReader: View {
    @State private var fold = Fold.none

    var body: some View {
        Color.clear
            .onGeometryChange(for: Fold.self) { proxy in
                let regions = proxy.reservedRegions(kind: .division, options: .includeInactive)
                guard let region = regions.first(where: { $0.frame.height > $0.frame.width }) else { return .none }
                return Fold(frame: region.frame, isActive: region.isActive)
            } action: { fold = $0 }
    }
}

nonisolated struct Fold: Equatable, Sendable {
    var frame: CGRect
    var isActive: Bool
    static let none = Fold(frame: .zero, isActive: false)
}
```

- Keep only vertical divisions (`height > width`) for column layouts; a horizontal fold running through scrolling content needs no displacement.
- Include inactive regions so columns don't jump while folding, and fall back to an even split when the inactive frame is zero-sized. Widen the gutter only while `isActive`.
- Grids: use an even column count whenever a division exists, even an inactive one, so folding doesn't change the count. While the fold is active, size each side separately because the vertical toolbar makes margins asymmetric, and let the last leading column's spacing cover the fold.
- With default `MainActor` isolation, `LayoutValueKey` types, helpers called from `Layout` methods, and values returned from `onGeometryChange` transforms (which must be `Equatable` and `Sendable`) need `nonisolated` when the compiler reports isolated-conformance errors.

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
