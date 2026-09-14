# SDK 27 Collection Interactions

## Reordering Any Container

`reorderable()` and `reorderContainer(for:)` bring drag reordering to lists, stacks, grids, and custom layouts:

```swift
LazyVGrid(columns: columns) {
    ForEach(items) { item in
        ItemView(item)
    }
    .reorderable()
}
.reorderContainer(for: Item.self) { difference in
    apply(difference, to: &items)
}
```

`ReorderDifference` provides source IDs and a destination of `.before(id)` or `.end`; update the model-owned collection accordingly. For multiple sections, add `collectionID:` to each reorderable collection and use `reorderContainer(for:in:)`.

Availability: iOS, macOS, watchOS, and visionOS 27; unavailable on tvOS. Drag/drop customization availability differs by platform, so verify before combining `dragContainer`, `dropDestination`, or `DropSession.reorderDestination(for:)`.

## Swipe Actions Outside `List`

Rows in a scrollable stack or grid can use existing `swipeActions` when the enclosing scroll container has `swipeActionsContainer()`:

```swift
ScrollView {
    LazyVStack {
        ForEach(items) { item in
            ItemRow(item: item).swipeActions { /* buttons */ }
        }
    }
}
.swipeActionsContainer()
```

Without the container modifier, row swipe actions outside `List` have no effect. The new `swipeActions(..., onPresentationChanged:)` overload reports whether actions are revealed.

Availability: iOS, macOS, watchOS, and visionOS 27; unavailable on tvOS.
