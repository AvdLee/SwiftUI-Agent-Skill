# SwiftUI State Management Reference

## Table of Contents

- [Property Wrapper Selection Guide](#property-wrapper-selection-guide)
- [@State](#state)
- [SDK 27 `@State` Macro](#sdk-27-state-macro)
- [Property Wrappers Inside @Observable Classes](#property-wrappers-inside-observable-classes)
- [Make @Observable Property Types Equatable](#make-observable-property-types-equatable)
- [@Observable Dependency Granularity](#observable-dependency-granularity)
- [@Binding](#binding)
- [@FocusState](#focusstate)
- [@StateObject vs @ObservedObject (Legacy - Pre-iOS 17)](#stateobject-vs-observedobject-legacy---pre-ios-17)
- [Don't Store Parent-Owned Inputs as @State](#dont-store-parent-owned-inputs-as-state)
- [@Bindable (iOS 17+)](#bindable-ios-17)
- [Passed Value Inputs](#passed-value-inputs)
- [Isolate Side-Effect-Only Dependencies](#isolate-side-effect-only-dependencies)
- [Decision Flowchart](#decision-flowchart)
- [State Privacy Rules](#state-privacy-rules)
- [Avoid Nested ObservableObject](#avoid-nested-observableobject)
- [Key Principles](#key-principles)

## Property Wrapper Selection Guide

| Wrapper | Use When | Notes |
|---------|----------|-------|
| `@State` | Internal view state that triggers updates | Must be `private` |
| `@Binding` | Child view needs to modify parent's state | Don't use for read-only |
| `@Bindable` | iOS 17+: View receives `@Observable` object and needs bindings | For injected observables |
| `let` | Read-only value passed from parent | Simplest option |

**Legacy (Pre-iOS 17):**
| Wrapper | Use When | Notes |
|---------|----------|-------|
| `@StateObject` | View owns an `ObservableObject` instance | Use `@State` with `@Observable` instead |
| `@ObservedObject` | View receives an `ObservableObject` from outside | Never create inline |

## @State

Always mark `@State` properties as `private`. Use for internal view state that triggers UI updates.

```swift
// Correct
@State private var isAnimating = false
@State private var selectedTab = 0
```

**Why Private?** Marking state as `private` makes it clear what's created by the view versus what's passed in. It also prevents accidentally passing initial values that will be ignored (see "Don't Pass Values as @State" below).

### iOS 17+ with @Observable (Preferred)

**Always prefer `@Observable` over `ObservableObject`.** With iOS 17's `@Observable` macro, use `@State` instead of `@StateObject`:

```swift
@Observable
@MainActor  // Always mark @Observable classes with @MainActor
final class DataModel {
    var name = "Some Name"
    var count = 0
}

struct MyView: View {
    @State private var model = DataModel()  // Use @State, not @StateObject

    var body: some View {
        VStack {
            TextField("Name", text: $model.name)
            Stepper("Count: \(model.count)", value: $model.count)
        }
    }
}
```

**Critical**: When a view *owns* an `@Observable` object, always use `@State` -- not `let`. Without `@State`, SwiftUI may recreate the instance when a parent view redraws, losing accumulated state. `@State` tells SwiftUI to preserve the instance across view redraws. Using `@State` also provides bindings directly (no need for `@Bindable`).

**Note**: You may want to mark `@Observable` classes with `@MainActor` to ensure thread safety with SwiftUI, unless your project or package uses Default Actor Isolation set to `MainActor`—in which case, the explicit attribute is redundant and can be omitted.

## SDK 27 `@State` Macro

SDK 27 migrates `@State` from a property wrapper to a macro. When an initializer intentionally seeds view-owned state, drop the declaration's initial value and assign it once in `init`:

```swift
struct CounterView: View {
    let name: String
    @State private var count: Int

    init(name: String, count: Int) {
        self.name = name
        self.count = count
    }
}
```

Do not fix “used before being initialized” by reordering assignments. Assigning in `init` to state that already has a declaration default remains incorrect: SwiftUI preserves the declaration's state storage, and later parent arguments do not replace child-owned state.

Other source-compatibility failures:

- “Invalid redeclaration of synthesized property”: another property wrapper composed with `@State` is colliding with macro-generated storage. Remove the redundant wrapper or restructure the composition.
- Missing private memberwise initializer: SDK 27 may not synthesize it for a view containing `@State`. Define the initializer explicitly instead of delegating to the missing memberwise initializer.

Keep `@State` private. Use an initializer seed only for intentional one-time ownership; use a plain value or `@Binding` when later parent updates must propagate.

## Property Wrappers Inside @Observable Classes

**Critical**: The `@Observable` macro transforms stored properties to add observation tracking. Property wrappers (like `@AppStorage`, `@SceneStorage`, `@Query`) also transform properties with their own storage. These two transformations conflict, causing a compiler error.

**Always annotate property-wrapper properties with `@ObservationIgnored` inside `@Observable` classes.**

```swift
@Observable
@MainActor
final class SettingsModel {
    // WRONG - compiler error: property wrappers conflict with @Observable
    // @AppStorage("username") var username = ""

    // CORRECT - @ObservationIgnored prevents the conflict
    @ObservationIgnored @AppStorage("username") var username = ""
    @ObservationIgnored @AppStorage("isDarkMode") var isDarkMode = false

    // Regular stored properties work fine with @Observable
    var isLoading = false
}
```

This applies to **any** property wrapper used inside an `@Observable` class, including but not limited to:
- `@AppStorage`
- `@SceneStorage`
- `@Query` (SwiftData)

**Note**: Since `@ObservationIgnored` disables observation tracking for that property, SwiftUI won't detect changes through the Observation framework. However, property wrappers like `@AppStorage` already notify SwiftUI of changes through their own mechanisms (e.g., UserDefaults KVO), so views still update correctly.

**Never remove `@ObservationIgnored`** from property-wrapper properties in `@Observable` classes — doing so causes a compiler error.

## Make @Observable Property Types Equatable

The `@Observable` macro generates a setter that **skips invalidation when the new value equals the current one** — but only when it can compare them, which means only when the property's type is `Equatable`. Without that conformance, every assignment notifies observing views, even when the value is identical. This is an easy win for properties written frequently with the same value (polling, streaming updates, timers).

```swift
// AVOID: not Equatable — every assignment invalidates, even no-op writes
enum DeliveryStatus { case placed, preparing, shipped, delivered }

// PREFER: Equatable lets the generated setter short-circuit redundant writes
enum DeliveryStatus: Equatable { case placed, preparing, shipped, delivered }
```

This applies to collection properties too: an `Array`/`Set`/`Dictionary` is only `Equatable` when its element type is, so a non-`Equatable` element defeats the short-circuit for the whole collection. (The check is emitted into the generated setter as user code, so it applies on every OS that supports `@Observable` when built with current Xcode.)

This is distinct from `Equatable` *views* (see `references/performance-patterns.md`): that conformance lets SwiftUI skip a view's body; this one lets the model skip notifying observers in the first place.

## @Observable Dependency Granularity

Observation tracks reads at the **property** level, not the field level — so reading any part of a compound property establishes a dependency on the whole thing. Three common traps and their fixes:

- **A computed property establishes dependencies transitively.** `var currentUser: User? { users.first { $0.id == currentID } }` reads `users` in its body, so any view reading `currentUser` depends on the entire `users` array. Renaming the access doesn't change what observation tracks.
- **A struct-typed stored property drags the whole struct.** A view reading `session.user.name` depends on `session.user`; editing any other field of `user` invalidates it.
- **An array/collection read drags the whole collection.** Reading one element establishes a dependency on the entire stored collection.
- **A row that receives the parent model plus an index subscribes too broadly.** The list that owns the `ForEach` legitimately depends on the collection. A row that looks up `state.users[index]` also depends on the entire collection, so editing one element invalidates every row. Pass the element (or the fields the row reads) directly.

```swift
// PREFER: cache derived values as stored properties, kept in sync in didSet
@MainActor @Observable
final class AppState {
    var users: [User] = [] { didSet { recomputeCurrentUser() } }
    var currentID: User.ID? { didSet { recomputeCurrentUser() } }

    private(set) var currentUser: User?
    private func recomputeCurrentUser() { currentUser = users.first { $0.id == currentID } }
}
```

For struct-typed properties, expose the fields the views actually read as individual properties on the model (each is then tracked separately). If the struct must remain round-trippable (re-encoded to a payload), keep both: a stored `var user: User` for the original shape and the flattened properties for view consumption, kept in sync in `didSet` on `user`. When many rows each observe several fields of their element, model each element as its own `@Observable` and have the parent **persist** the instances — see the per-item view model pattern in `references/performance-patterns.md`. Reading several already-narrow properties from one model is fine and does not need splitting.

## @Binding

Use only when child view needs to **modify** parent's state. If child only reads the value, use `let` instead.

```swift
// Parent
struct ParentView: View {
    @State private var isSelected = false

    var body: some View {
        ChildView(isSelected: $isSelected)
    }
}

// Child - will modify the value
struct ChildView: View {
    @Binding var isSelected: Bool

    var body: some View {
        Button("Toggle") {
            isSelected.toggle()
        }
    }
}
```

### When NOT to use @Binding

- **Don't use `@Binding` for read-only values.** If the child only displays the value and never modifies it, use `let` instead. `@Binding` adds unnecessary overhead and implies a write contract that doesn't exist.

### Declare a Binding with @Binding, Not a Plain Property

A binding you react to must be `@Binding var x: T`. SwiftUI subscribes only to `DynamicProperty` properties (`@State`, `@Binding`, `@Environment`, …); a binding held in an undecorated property (`let x: Binding<T>`) is just a value it never looks inside, so external changes to the bound value don't re-evaluate the view.

```swift
struct SelectionBadge: View {
    // let selection: Binding<Item?>   // WRONG - untracked; external changes missed
    @Binding var selection: Item?      // CORRECT - DynamicProperty, tracked

    var body: some View { Text(selection?.name ?? "None") }
}
```

Debug builds can mask this with extra graph passes, so it often fails only in Release. It bites hardest in `UIViewRepresentable`/`NSViewRepresentable`, where the missing re-evaluation means `updateUIView(_:context:)` never runs (e.g. a presented controller that won't dismiss when its bound item is reset).

### Prefer KeyPath Bindings Over Closure Bindings

When you need a binding into a model, prefer a KeyPath/subscript-based binding over a hand-written `Binding(get:set:)` closure. A closure binding allocates a new closure each time `body` runs and can't be compared, which can trigger unnecessary invalidations.

```swift
// BAD - closure binding: heap allocation each body pass, defeats comparison
let binding = Binding(
    get: { model[scoreFor: player] },
    set: { model[scoreFor: player] = $0 }
)
PlayerScoreRow(player: player, score: binding)

// GOOD - project through a subscript with @Bindable
@Bindable var model = model
PlayerScoreRow(player: player, score: $model[scoreFor: player])
```

If no suitable subscript exists, add one (a labeled subscript reads as a clean projection into the model). Reserve closure bindings for cases where no key path or subscript can express the transform.

For an argumentless projection, use a computed property. A marker-enum subscript (`$model[playback: .isPlaying]`) is ceremony around a property that takes no arguments:

```swift
// AVOID: marker enum dresses up an argumentless projection
fileprivate subscript(playback _: PlaybackProjection) -> Bool {
    get { rate > 0 }
    set { rate = newValue ? 1 : 0 }
}
Toggle("Play", isOn: $model[playback: .isPlaying])

// PREFER: computed property
var isPlaying: Bool {
    get { rate > 0 }
    set { rate = newValue ? 1 : 0 }
}
Toggle("Play", isOn: $model.isPlaying)
```

## @FocusState

See `references/focus-patterns.md` for comprehensive focus management guidance including `@FocusState`, `@FocusedValue`, `.focusable()`, default focus, and common pitfalls.

Always mark `@FocusState` as `private`.

## @StateObject vs @ObservedObject (Legacy - Pre-iOS 17)

**Note**: Always prefer `@Observable` with `@State` for iOS 17+.

The key distinction is **ownership**: `@StateObject` when the view **creates and owns** the object; `@ObservedObject` when the view **receives** it from outside.

```swift
// View creates it → @StateObject
@StateObject private var viewModel = MyViewModel()

// View receives it → @ObservedObject
@ObservedObject var viewModel: MyViewModel
```

**Never** create an `ObservableObject` inline with `@ObservedObject` -- it recreates the instance on every view update.

### @StateObject instantiation in View's initializer

Prefer storing the `@StateObject` in the parent view and passing it down. If you must create one in a custom initializer, pass the expression directly to `StateObject(wrappedValue:)` so the `@autoclosure` prevents redundant allocations:

```swift
// Inside a View's init(movie:):
// WRONG — assigning to a local first defeats @autoclosure
let vm = MovieDetailsViewModel(movie: movie)
_viewModel = StateObject(wrappedValue: vm)

// CORRECT — inline expression defers creation
_viewModel = StateObject(wrappedValue: MovieDetailsViewModel(movie: movie))
```

**Modern Alternative**: Use `@Observable` with `@State` instead.

## Don't Store Parent-Owned Inputs as @State

Do not declare a changing parent-owned input as `@State` or `@StateObject`. State accepts an initial value and then remains owned by the child, so subsequent parent updates are ignored.

```swift
// WRONG - child ignores parent updates
struct ChildView: View {
    @State var item: Item  // Shows initial value forever!
    var body: some View { Text(item.name) }
}

// CORRECT - child receives updates
struct ChildView: View {
    let item: Item  // Or @Binding if child needs to modify
    var body: some View { Text(item.name) }
}
```

Mark `@State` and `@StateObject` as `private` so they do not appear in a generated initializer. A custom initializer may intentionally seed private, view-owned state once; make that ownership explicit and do not expect later argument changes to replace the state. See [SDK 27 `@State` Macro](#sdk-27-state-macro) for initialization diagnostics.

## @Bindable (iOS 17+)

Use when receiving an `@Observable` object from outside and needing bindings:

```swift
@Observable
final class UserModel {
    var name = ""
    var email = ""
}

struct ParentView: View {
    @State private var user = UserModel()

    var body: some View {
        EditUserView(user: user)
    }
}

struct EditUserView: View {
    @Bindable var user: UserModel  // Received from parent, needs bindings

    var body: some View {
        Form {
            TextField("Name", text: $user.name)
            TextField("Email", text: $user.email)
        }
    }
}
```

## Passed Value Inputs

Use `let` for read-only values passed from a parent. A view can still observe replacement values with `.onChange`; the property does not need to be `var`.

```swift
struct ProfileHeader: View {
    let username: String
    let avatarURL: URL

    var body: some View {
        HStack {
            AsyncImage(url: avatarURL)
            Text(username)
        }
    }
}
```

### Pass only the fields a view reads

SwiftUI compares value-type inputs field by field. A child that accepts an entire struct can re-evaluate when any field changes, even if its body displays only one field. Passing a large value can also make comparison walk nested fields and collections.

```swift
// AVOID: unrelated User changes can invalidate AvatarBadge.
struct AvatarBadge: View {
    let user: User

    var body: some View {
        AsyncImage(url: user.avatarURL)
    }
}

// PREFER: the input matches what the view reads.
struct AvatarBadge: View {
    let avatarURL: URL

    var body: some View {
        AsyncImage(url: avatarURL)
    }
}
```

This rule primarily applies to value types. Class references compare by identity; an `@Observable` class additionally tracks the individual properties read during `body`. Compound properties still have broad granularity: reading one element of an observed array or one field of an observed struct establishes a dependency on that whole stored property.

## Isolate Side-Effect-Only Dependencies

An `.onChange(of:)` expression reads its value in the enclosing view's body scope. If a dependency exists only to trigger a side effect, every change still re-evaluates that view's body.

For a non-trivial parent, consider moving the dependency and `.onChange` into a focused `ViewModifier`. This gives the side effect its own invalidation boundary:

```swift
private struct CounterSyncModifier: ViewModifier {
    @Environment(\.counter) private var counter
    let model: Model

    func body(content: Content) -> some View {
        content.onChange(of: counter) {
            model.counter = counter
        }
    }
}
```

Do not add this indirection when the dependency also affects rendering or the parent body is already trivial; it would not reduce meaningful work.

## Environment

For custom environment values, `@Entry`, focused values, stable defaults, and invalidation costs, consult `references/environment-patterns.md`.

## Decision Flowchart

```
Is this value owned by this view?
├─ YES: Is it a simple value type?
│       ├─ YES → @State private var
│       └─ NO (class):
│           ├─ Use @Observable → @State private var (mark class @MainActor)
│           └─ Legacy ObservableObject → @StateObject private var
│
└─ NO (passed from parent):
    ├─ Does child need to MODIFY it?
    │   ├─ YES → @Binding var
    │   └─ NO: Does child need BINDINGS to its properties?
    │       ├─ YES (@Observable) → @Bindable var
    │       └─ NO: Does child react to changes?
    │           ├─ YES → let + .onChange()
    │           └─ NO → let
    │
    └─ Is it a legacy ObservableObject from parent?
        └─ YES → @ObservedObject var (consider migrating to @Observable)
```

## State Privacy Rules

**All view-owned state should be `private`:**

```swift
// Correct - clear what's created vs passed
struct MyView: View {
    // Created by view - private
    @State private var isExpanded = false
    @State private var viewModel = ViewModel()
    @AppStorage("theme") private var theme = "light"
    @Environment(\.colorScheme) private var colorScheme
    
    // Passed from parent - not private
    let title: String
    @Binding var isSelected: Bool
    @Bindable var user: User
    
    var body: some View {
        // ...
    }
}
```

**Why**: This makes dependencies explicit and improves code completion for the generated initializer.

## Avoid Nested ObservableObject

**Note**: This limitation only applies to `ObservableObject`. `@Observable` fully supports nested observed objects.

SwiftUI can't track changes through nested `ObservableObject` properties. Workaround: pass the nested object directly to child views as `@ObservedObject`. With `@Observable`, nesting works automatically.

## Key Principles

1. **Always prefer `@Observable` over `ObservableObject`** for new code
2. **Mark `@Observable` classes with `@MainActor` for thread safety (unless using default actor isolation)`**
3. Use `@State` with `@Observable` classes (not `@StateObject`)
4. Use `@Bindable` for injected `@Observable` objects that need bindings
5. **Always mark `@State` and `@StateObject` as `private`**
6. Do not store changing parent-owned inputs as `@State` or `@StateObject`; use private state only for intentional child ownership
7. With `@Observable`, nested objects work fine; with `ObservableObject`, pass nested objects directly to child views
8. **Always add `@ObservationIgnored` to property wrappers** (e.g., `@AppStorage`, `@SceneStorage`, `@Query`) inside `@Observable` classes — they conflict with the macro's property transformation
9. **Prefer `Equatable` types for frequently-written `@Observable` properties** so the generated setter skips redundant invalidations
10. Pass value-type views only the fields they read
11. Isolate side-effect-only dependencies when they would invalidate an expensive parent
12. Follow `references/environment-patterns.md` for custom environment and focused values
13. **Prefer KeyPath/subscript bindings over closure bindings**; use a computed property, not a marker-enum subscript, for argumentless projections
14. **Declare a binding you react to as `@Binding`, not a plain `Binding`-typed property** — a plain property isn't tracked, so external changes won't re-evaluate the view (often a Release-only failure)
15. Do not pass a parent `@Observable` plus an index into a row; pass the element or the fields the row reads
