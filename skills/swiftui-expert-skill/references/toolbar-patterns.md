# SwiftUI Toolbar Patterns

## Customizable toolbars (iOS 26+, macOS 26+, tvOS 26+, watchOS 26+, visionOS 26+)

Use `.toolbar(id:)` when people should be able to add, remove, or rearrange toolbar content. Every customizable `ToolbarItem` needs a stable, unique string ID. Keep IDs tied to the meaning of the action rather than to a changing array position.

```swift
.toolbar(id: "main-toolbar") {
    ToolbarItem(id: "tag") {
        TagButton()
    }
    ToolbarItem(id: "share") {
        ShareButton()
    }
    ToolbarSpacer(.fixed)
    ToolbarItem(id: "more") {
        MoreButton()
    }
}
```

`ToolbarItem(id:placement:content:)` is available on iOS 14+, macOS 11+, tvOS 14+, and watchOS 7+ (visionOS 1+). The `showsByDefault:` overload is soft-deprecated in the SDK 27 toolchain; use `defaultCustomization(_:options:)` instead.

`ToolbarSpacer` separates groups of toolbar content. `ToolbarSpacer(.fixed)` creates a fixed-width gap; `ToolbarSpacer(.flexible)` expands to push content apart. The initializer also accepts a placement. `ToolbarSpacer` is available on iOS 26+ and macOS 26+; it is unavailable on tvOS, watchOS, and visionOS.

## System-defined toolbar content

`DefaultToolbarItem` places a system-defined item, such as search or the sidebar toggle, at a chosen placement. It is available on iOS 26+, macOS 26+, tvOS 26+, watchOS 26+, and visionOS 26+.

```swift
.toolbar {
    DefaultToolbarItem(kind: .search, placement: .bottomBar)
    DefaultToolbarItem(kind: .sidebarToggle, placement: .navigationBarLeading)
}
```

The `.search` kind is available on iOS, macOS, and visionOS 26+; it is unavailable on tvOS and watchOS. The `.sidebarToggle` kind is available on every platform supported by `DefaultToolbarItem`.

The `.largeSubtitle` placement supplies content in the large navigation-title subtitle area. It takes precedence over the value supplied by `navigationSubtitle(_:)`. It is available on iOS 26+ only.

On iOS 26+ and macOS 26+, use `sharedBackgroundVisibility(.hidden)` on the `ToolbarItem` when one item should not participate in the shared Liquid Glass background. It is unavailable on tvOS, watchOS, and visionOS. Apply `badge(_:)` to the item's view to show an indicator:

```swift
.toolbar {
    ToolbarItem(placement: .topBarTrailing) {
        Button("Notifications", systemImage: "bell") { }
            .badge(unreadCount)
    }
    ToolbarItem(placement: .topBarTrailing) {
        ProfileButton()
    }
    .sharedBackgroundVisibility(.hidden)
}
```

## Search

Use `.searchToolbarBehavior(.minimize)` to opt into a compact, button-like search control that expands when selected. The modifier is available on all aligned 26 releases, but `.minimize` is available only on iOS and visionOS; use `.automatic` elsewhere.

## Transitioning from toolbar controls

Attach `matchedTransitionSource(id:in:)` to toolbar content that presents another view, then use a zoom navigation transition with the same ID and namespace in the destination.

```swift
@Namespace private var namespace

.toolbar {
    ToolbarItem(placement: .topBarTrailing) {
        Button("Show details", systemImage: "info") {
            isPresented = true
        }
    }
    .matchedTransitionSource(id: "details", in: namespace)
}
.sheet(isPresented: $isPresented) {
    DetailsView()
        .navigationTransition(.zoom(sourceID: "details", in: namespace))
}
```

The view `matchedTransitionSource(id:in:)` is available on iOS 18+, macOS 15+, tvOS 18+, watchOS 11+, and visionOS 2+. Its toolbar-content form is available on iOS 26+ and is unavailable on macOS, tvOS, watchOS, and visionOS. The zoom navigation transition is available on iOS 18+, macOS 15+, tvOS 18+, watchOS 11+, and visionOS 2+.

## SDK 27 overflow and visibility

When toolbar content does not fit, the system can move lower-priority items into an overflow menu. `visibilityPriority(_:)` is available on iOS 27+, macOS 26.1+, watchOS 27+, tvOS 27+, and visionOS 27+. `.automatic` is available on every supported platform. `.low` and `.high` are available only on iOS and macOS. `ToolbarItemVisibilityPriority(higherThan:)` and `(lowerThan:)` are available on iOS 27+ and macOS 27+.

```swift
.toolbar {
    ToolbarItemGroup {
        UndoButton()
        RedoButton()
    }
    .visibilityPriority(.high)
}
```

`ToolbarOverflowMenu` is toolbar content whose children always appear in the overflow menu. The `View.toolbarOverflowMenu { ... }` modifier provides the same behavior outside a toolbar builder. Both are available on iOS 27+ and visionOS 27+ only. The type and modifier have different syntaxes:

```swift
.toolbar {
    ToolbarOverflowMenu {
        ExportButton()
        ClearButton()
    }
}

content
    .toolbarOverflowMenu {
        ExportButton()
        ClearButton()
    }
```

`.topBarPinnedTrailing` keeps a `ToolbarItem` at the trailing edge and prevents it from moving into overflow. It is available on iOS 27+ and visionOS 27+ only.

For deployment targets below SDK 27, prefer one availability check around the toolbar content when using these APIs:

```swift
.toolbar {
    if #available(iOS 27, *) {
        ToolbarItem(placement: .topBarPinnedTrailing) {
            ShareButton()
        }
        ToolbarOverflowMenu {
            ExportButton()
        }
    } else {
        ToolbarItem {
            ShareButton()
        }
    }
}
```

## Minimization, margins, and status bar

`toolbarMinimizationBehavior(_:for:)`, `toolbarMinimizationSafeAreaAdjustment(_:for:)`, and `toolbarMinimizationRestoration(_:for:)` are available on all Apple platforms in SDK 27. The behavior cases `.automatic`, `.onScrollDown`, `.onScrollUp`, and `.never` and the safe-area cases `.automatic`, `.enabled`, and `.disabled` have platform-specific availability; use `.automatic` for cross-platform code and gate iOS-only cases as needed.

```swift
ScrollView {
    Content()
}
.toolbarMinimizationBehavior(.onScrollDown, for: .navigationBar)
.toolbarMinimizationSafeAreaAdjustment(.automatic, for: .navigationBar)
```

`contentMarginsRemoved(_:)` removes the system margins around toolbar content. It is available on iOS 27+, macOS 27+, tvOS 27+, watchOS 27+, and visionOS 27+.

On iOS 27+, `ToolbarPlacement.statusBar` can be passed to `toolbarVisibility(_:for:)` to control status-bar visibility. It is iOS-only; keep `statusBarHidden(_:)` in an earlier deployment fallback and do not suggest a replacement on visionOS, where there is no status bar.

```swift
.toolbarVisibility(.hidden, for: .statusBar)
```

## Dynamic toolbar content

`ForEach` conforms to `ToolbarContent` when built with the SDK 27 toolchain and back-deploys to iOS 16+, macOS 13+, watchOS 9+, tvOS 16+, and visionOS 1+. Give the collection elements stable identity. `EmptyView` as toolbar content requires iOS 27+, macOS 27+, tvOS 27+, watchOS 27+, and visionOS 27+.

```swift
.toolbar {
    ForEach(actions) { action in
        ToolbarItem {
            Button(action.title) {
                action.perform()
            }
        }
    }
}
```

For broader Liquid Glass styling, see [liquid-glass.md](liquid-glass.md). For macOS window and toolbar concerns, keep platform-specific guidance in the macOS references.
