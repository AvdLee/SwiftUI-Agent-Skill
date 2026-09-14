# SwiftUI Modifier and Identity Patterns

Use this reference when a modifier is conditional or when modifier composition changes a view's structural identity.

## Avoid Conditional `.if` Modifiers

Do not create an `@ViewBuilder` extension that switches between `transform(self)` and `self`. Its branches produce different view types, so toggling the condition can replace the subtree, reset state, and break animations.

```swift
// AVOID
extension View {
    @ViewBuilder
    func `if`<Content: View>(
        _ condition: Bool,
        transform: (Self) -> Content
    ) -> some View {
        if condition { transform(self) } else { self }
    }
}
```

When two states describe the same view, keep one structural identity and vary the modifier's value:

```swift
Text("Hello")
    .foregroundStyle(isHighlighted ? .red : .primary)
    .opacity(isEnabled ? 1 : 0.5)
```

Use `if` when the branches genuinely represent different views or when content is truly optional. Do not silently refactor an existing `.if` modifier during unrelated work; call out the identity risk and keep the behavioral change focused.

## Use `AnyShapeStyle` When Style Types Differ

Some `ShapeStyle` branches do not unify in a ternary. Preserve the view's identity by erasing the styles, not the view:

```swift
Text("Status")
    .foregroundStyle(
        isActive
            ? AnyShapeStyle(.primary)
            : AnyShapeStyle(.tint)
    )
```

`AnyShapeStyle` is an appropriate value-type eraser and does not have the structural-identity cost of `AnyView`. Add it only when the original ternary does not compile; many combinations involving `Color`, such as `.yellow` and `.primary`, already unify.

## Prefer No-Effect Values for Visual State

For visibility or styling changes where the same view should retain state, prefer an always-present modifier with a no-effect value:

```swift
DetailsView()
    .opacity(isVisible ? 1 : 0)
```

Opacity keeps the view in layout and accessibility by default. Use conditional inclusion when hidden content should be removed from layout, interaction, or accessibility.

## Checklist

- [ ] Conditional styling changes modifier values instead of branching the whole view
- [ ] Existing `.if` helpers are reported as focused identity risks, not rewritten incidentally
- [ ] `AnyShapeStyle` is used only when different style types fail to unify
- [ ] `AnyView` is not introduced to solve a modifier type mismatch
- [ ] Visibility behavior intentionally accounts for layout, hit testing, and accessibility
