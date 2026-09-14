# SDK 27 Toolbars

Use these APIs to adapt toolbar content when space is constrained:

- `visibilityPriority(_:)` controls which items remain visible
- `ToolbarOverflowMenu` / `toolbarOverflowMenu` keeps content in overflow
- `.topBarPinnedTrailing` pins one trailing item
- `toolbarMinimizeBehavior(_:for:)` controls minimization while scrolling
- `toolbarMinimizationSafeAreaAdjustment(_:for:)` controls the corresponding safe-area change
- `contentMarginsRemoved(_:)` removes margins around toolbar content
- `ToolbarPlacement.statusBar` controls status-bar visibility on iOS

`ForEach` and `EmptyView` can also participate in toolbar builders:

```swift
.toolbar {
    ForEach(quickActions) { action in
        ToolbarItem {
            Button(action.title) { action.perform() }
        }
    }
}
```

Availability varies by API and platform:

- `ToolbarPlacement.statusBar` requires iOS 27 and is unavailable elsewhere.
- `ToolbarOverflowMenu` and `.topBarPinnedTrailing` are iOS/visionOS 27.
- `visibilityPriority(_:)` starts at iOS 27 and macOS 26.1; supported priority values differ by platform.
- `ForEach` toolbar conformance back-deploys when built with SDK 27 (iOS 16, macOS 13, watchOS 9, tvOS 16, visionOS 1).
- `EmptyView` toolbar conformance requires the aligned 27 releases.

Verify the exact target before generating code. For older systems, gate the new toolbar content in `if #available` and provide ordinary `ToolbarItem` fallbacks.
