# SwiftUI Environment Patterns

Use this reference for `@Environment`, `EnvironmentValues`, `@Entry`, `@FocusedValue`, and values propagated through the environment.

## Read Framework Values

Use `@Environment` to read framework-provided values and actions from the nearest ancestor:

```swift
struct DetailView: View {
    @Environment(\.dismiss) private var dismiss
    @Environment(\.colorScheme) private var colorScheme

    var body: some View {
        Button("Done") { dismiss() }
    }
}
```

Keep the declaration in the smallest view that uses it so environment changes do not invalidate a broader parent.

## Share Observable Models

On iOS 17+ and aligned platforms, inject an `@Observable` model by type and read it with type-based `@Environment`:

```swift
@MainActor
@Observable
final class AppState {
    var isLoggedIn = false
}

RootView()
    .environment(AppState())

struct AccountView: View {
    @Environment(AppState.self) private var appState

    var body: some View {
        Text(appState.isLoggedIn ? "Signed in" : "Signed out")
    }
}
```

Observation tracks the model properties read during `body`, so unrelated properties do not invalidate the view. Use `@Bindable` locally when a control needs bindings to the injected model.

For older deployment targets, `@EnvironmentObject` with `.environmentObject(...)` remains the corresponding `ObservableObject` pattern. Do not create the shared model inline at multiple reader sites.

## Prefer `@Entry` for Custom Values

Use `@Entry` instead of manual key conformances when defining custom environment, transaction, container, or focused values:

```swift
extension EnvironmentValues {
    @Entry var accentTheme: Theme = .default
}

extension FocusedValues {
    @Entry var selectedDocument: Document?
}
```

Focused-value entries are optional and do not specify a non-`nil` default.

## Never Store Closures in Custom Keys

SwiftUI cannot reliably compare functions. A closure in a custom environment or focused-value key can therefore make every reader invalidate whenever the environment propagates. Wrapping the closure in a struct or storing it on a `View` does not fix comparison; the closure is still present.

Framework action values such as `\.dismiss`, `\.openURL`, and `\.refresh` are designed for this purpose and are not affected by this rule.

Represent custom behavior with a value that stores comparable inputs and exposes a method or `callAsFunction`, or share an `@Observable` model when the behavior belongs with shared state:

```swift
// AVOID
extension EnvironmentValues {
    @Entry var submit: (String) -> Void = { _ in }
}

// PREFER
struct SubmitAction {
    func callAsFunction(_ draft: String) { /* submit */ }
}

extension EnvironmentValues {
    @Entry var submit = SubmitAction()
}
```

## Keep Default Values Stable

An `@Entry` default expression is evaluated when a reader falls back to it. The default is unstable when repeated evaluation produces a different value, such as a fresh class instance, `Date()`, `UUID()`, or a struct containing a newly allocated reference. Any unrelated environment write can then make fallback readers appear changed.

```swift
// AVOID: creates a different instance on each fallback read
extension EnvironmentValues {
    @Entry var model = Model()
}

// PREFER: resolves to the same instance
extension EnvironmentValues {
    @Entry var model = defaultModel
    private static let defaultModel = Model()
}
```

Use an optional with a `nil` default when absence is meaningful. This is preferable when readers currently test a sentinel such as an empty identifier:

```swift
extension EnvironmentValues {
    @Entry var editingSession: EditingSession?
}
```

`Equatable` conformance does not repair an unstable default: the expression still allocates or changes on every read. Conversely, do not rewrite already-stable defaults. Literals, enum cases without associated values, `nil`, and structs built only from deterministic values or stable references are stable even without `Equatable`.

## Avoid High-Frequency Environment Updates

Every environment write propagates through the subtree and makes environment readers check their values. Do not put per-frame or rapidly changing measurements such as scroll offsets, drag positions, geometry, timer ticks, or animation progress in custom environment keys.

For visual scroll effects, prefer `scrollTransition` or `visualEffect(in:)`. When the value drives logic, consider an `@Observable` model that exposes a coarsened property such as `isWide` instead of raw width:

```swift
@MainActor
@Observable
final class ViewportModel {
    var width: CGFloat = 0 {
        didSet { isWide = width > 600 }
    }

    private(set) var isWide = false
}
```

The model alone is not the optimization: readers must observe a value that changes less often than the raw input.

## Remove Unused Reads

An unused key-path declaration such as `@Environment(\.theme)` still subscribes the view to that key. Remove it when neither `body` nor anything called from `body` reads the value.

Type-based `@Environment(Model.self)` uses Observation's property-level tracking. Merely declaring the model without reading one of its properties does not establish the same live dependency, though removing dead declarations still improves clarity.

## Checklist

- [ ] Custom values use `@Entry`
- [ ] Custom environment and focused-value keys do not store closures
- [ ] Default expressions return the same result on every fallback read
- [ ] Optional defaults represent semantic absence instead of sentinel instances
- [ ] High-frequency raw values do not flow through the environment
- [ ] Key-path environment declarations are actually read
