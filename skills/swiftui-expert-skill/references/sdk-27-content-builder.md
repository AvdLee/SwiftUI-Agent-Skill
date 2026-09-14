# SDK 27 Content Builder Migration

SDK 27 unifies many SwiftUI result builders under `@ContentBuilder`. Because block contents are no longer constrained to `View` in the same way, previously compiling source can become ambiguous.

## Common Fixes

- For ambiguous `ShapeStyle.opacity` or `blendMode` passed directly to `overlay` or `background`, select the builder overload:
  ```swift
  Rectangle().overlay {
      Color.blue.opacity(0.3).blendMode(.overlay)
  }
  ```
- Fully qualify a shadowed SwiftUI type, such as `SwiftUI.Color.clear`.
- Avoid spelling concrete `TupleView` or `TupleContent` generic structures; prefer opaque `some View`. If a concrete SDK 27 type is unavoidable, the builder now produces `TupleContent`.
- If an empty nested builder is ambiguous, provide `EmptyContent()` or `EmptyView()`. This can occur with MapKit in the dependency graph or a conditional-compilation branch that becomes empty.
- For deeply branching Charts content that times out only when back-deployed, extract the branches into an `@ChartContentBuilder` helper.

Choose the narrow fix matching the diagnostic. Do not broadly rewrite working builders or rename unrelated types.
