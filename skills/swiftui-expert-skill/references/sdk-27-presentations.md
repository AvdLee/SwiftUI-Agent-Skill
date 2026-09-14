# SDK 27 Item-Driven Presentations

SDK 27 adds `alert(_:item:actions:message:)` and `confirmationDialog(_:item:titleVisibility:actions:message:)`.

The optional binding alone drives presentation, the unwrapped value is passed to the action and message closures, and dismissal resets the binding to `nil`. The item does not need to conform to `Identifiable`.

```swift
@State private var photoToDelete: Photo?

var body: some View {
    PhotoList { photoToDelete = $0 }
        .confirmationDialog(
            "Delete photo?",
            item: $photoToDelete
        ) { photo in
            Button("Delete \(photo.name)", role: .destructive) {
                delete(photo)
            }
        } message: { photo in
            Text("\(photo.name) will be removed.")
        }
}
```

Prefer the item overload for an action tied to an optional value instead of synchronizing a separate Boolean. For deployment targets below 27, provide an `isPresented`/`presenting` fallback.
