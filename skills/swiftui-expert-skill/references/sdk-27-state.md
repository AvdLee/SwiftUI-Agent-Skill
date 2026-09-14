# SDK 27 `@State` Macro Migration

SDK 27 migrates `@State` from a property wrapper to a macro. Consult this reference before changing code for a new `@State` compilation failure.

## Initialization Errors

When an initializer intentionally seeds view-owned state, remove the declaration's initial value and initialize it once:

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

## Other Source-Compatibility Failures

- “Invalid redeclaration of synthesized property”: another property wrapper composed with `@State` is colliding with macro-generated storage. Remove the redundant wrapper or restructure the composition.
- Missing private memberwise initializer: SDK 27 may not synthesize it for a view containing `@State`. Define the initializer explicitly instead of delegating to the missing memberwise initializer.

Keep `@State` private. Use an initializer seed only for intentional one-time ownership; use a plain value or `@Binding` when later parent updates must propagate.
