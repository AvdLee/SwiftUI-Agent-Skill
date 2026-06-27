# SwiftUI ScrollView Patterns Reference

## Table of Contents

- [ScrollViewReader for Programmatic Scrolling](#scrollviewreader-for-programmatic-scrolling)
- [Scroll Position Tracking](#scroll-position-tracking)
- [Scroll Transitions and Effects](#scroll-transitions-and-effects)
- [Scroll Target Behavior](#scroll-target-behavior)
- [iOS 18+ Scroll APIs](#ios-18-scroll-apis)
- [Summary Checklist](#summary-checklist)

## ScrollViewReader for Programmatic Scrolling

**Use `ScrollViewReader` for scroll-to-top, scroll-to-bottom, and anchor-based jumps.**

```swift
struct ChatView: View {
    @State private var messages: [Message] = []
    private let bottomID = "bottom"
    
    var body: some View {
        ScrollViewReader { proxy in
            ScrollView {
                LazyVStack {
                    ForEach(messages) { message in
                        MessageRow(message: message)
                            .id(message.id)
                    }
                    Color.clear
                        .frame(height: 1)
                        .id(bottomID)
                }
            }
            .onChange(of: messages.count) { _, _ in
                withAnimation {
                    proxy.scrollTo(bottomID, anchor: .bottom)
                }
            }
            .onAppear {
                proxy.scrollTo(bottomID, anchor: .bottom)
            }
        }
    }
}
```

### Scroll-to-Top Pattern

```swift
struct FeedView: View {
    @State private var items: [Item] = []
    @State private var scrollToTop = false
    private let topID = "top"
    
    var body: some View {
        ScrollViewReader { proxy in
            ScrollView {
                LazyVStack {
                    Color.clear
                        .frame(height: 1)
                        .id(topID)
                    
                    ForEach(items) { item in
                        ItemRow(item: item)
                    }
                }
            }
            .onChange(of: scrollToTop) { _, shouldScroll in
                if shouldScroll {
                    withAnimation {
                        proxy.scrollTo(topID, anchor: .top)
                    }
                    scrollToTop = false
                }
            }
        }
    }
}
```

**Why**: `ScrollViewReader` provides programmatic scroll control with stable anchors. Always use stable IDs and explicit animations.

## Scroll Position Tracking

> **iOS 18+**: `onScrollGeometryChange` and `scrollPosition()` (without `id:`) are the recommended APIs. The `GeometryReader` + `PreferenceKey` approach is retained as a legacy fallback for iOS 17 targets.

### Track Scroll Offset (iOS 18+)

**Use `onScrollGeometryChange`** — the modern replacement for `GeometryReader` + `PreferenceKey`. It only fires when the extracted value actually changes, avoiding unnecessary view updates:

```swift
// ✅ iOS 18+ — efficient, only fires when extracted value changes
struct ContentView: View {
    @State private var scrollOffset: CGFloat = 0

    var body: some View {
        ScrollView {
            content
        }
        .onScrollGeometryChange(for: CGFloat.self) { geometry in
            geometry.contentOffset.y
        } action: { _, newValue in
            scrollOffset = newValue
        }
    }
}
```

### Programmatic Scroll Position (iOS 18+)

**Use `scrollPosition()`** — bind scroll position to state directly, without `ScrollViewReader`:

```swift
// ✅ iOS 18+ — no ScrollViewReader or stable IDs needed
struct ContentView: View {
    @State private var scrolledID: Item.ID?

    var body: some View {
        ScrollView {
            LazyVStack {
                ForEach(items) { item in
                    ItemRow(item: item)
                        .id(item.id)
                }
            }
        }
        .scrollPosition($scrolledID)
    }
}
```

### Threshold-Based Updates (iOS 18+)

```swift
// ✅ iOS 18+ — threshold-based state updates
struct ContentView: View {
    @State private var startAnimation: Bool = false

    var body: some View {
        ScrollView {
            content
        }
        .onScrollGeometryChange(for: Bool.self) { geometry in
            geometry.contentOffset.y < -100
        } action: { _, isPastThreshold in
            startAnimation = isPastThreshold
        }
    }
}
```

### Scroll-Based Header Visibility

**iOS 18+ recommended:**

```swift
struct ContentView: View {
    @State private var showHeader = true

    var body: some View {
        VStack(spacing: 0) {
            if showHeader {
                HeaderView()
                    .transition(.move(edge: .top))
            }

            ScrollView {
                content
            }
            .onScrollGeometryChange(for: CGFloat.self) { geometry in
                geometry.contentOffset.y
            } action: { _, offset in
                if offset < -50 {
                    withAnimation { showHeader = false }
                } else if offset > 50 {
                    withAnimation { showHeader = true }
                }
            }
        }
    }
}
```

<details>
<summary>Legacy approach (iOS 17) — GeometryReader + PreferenceKey</summary>

Use this when targeting iOS 17 or earlier. Requires a named coordinate space and a custom `PreferenceKey`.

```swift
struct ContentView: View {
    @State private var showHeader = true

    var body: some View {
        VStack(spacing: 0) {
            if showHeader {
                HeaderView()
                    .transition(.move(edge: .top))
            }

            ScrollView {
                content
                    .background(
                        GeometryReader { geometry in
                            Color.clear
                                .preference(
                                    key: ScrollOffsetPreferenceKey.self,
                                    value: geometry.frame(in: .named("scroll")).minY
                                )
                        }
                    )
            }
            .coordinateSpace(name: "scroll")
            .onPreferenceChange(ScrollOffsetPreferenceKey.self) { offset in
                if offset < -50 {
                    withAnimation { showHeader = false }
                } else if offset > 50 {
                    withAnimation { showHeader = true }
                }
            }
        }
    }
}

struct ScrollOffsetPreferenceKey: PreferenceKey {
    static var defaultValue: CGFloat = 0
    static func reduce(value: inout CGFloat, nextValue: () -> CGFloat) {
        value = nextValue()
    }
}
```

</details>

## Scroll Transitions and Effects

> **iOS 17+**: All APIs in this section require iOS 17 or later.

### Scroll-Based Opacity

```swift
struct ParallaxView: View {
    var body: some View {
        ScrollView {
            LazyVStack(spacing: 20) {
                ForEach(items) { item in
                    ItemCard(item: item)
                        .visualEffect { content, geometry in
                            let frame = geometry.frame(in: .scrollView)
                            let distance = min(0, frame.minY)
                            return content
                                .opacity(1 + distance / 200)
                        }
                }
            }
        }
    }
}
```

### Parallax Effect

```swift
struct ParallaxHeader: View {
    var body: some View {
        ScrollView {
            VStack(spacing: 0) {
                Image("hero")
                    .resizable()
                    .aspectRatio(contentMode: .fill)
                    .frame(height: 300)
                    .visualEffect { content, geometry in
                        let offset = geometry.frame(in: .scrollView).minY
                        return content
                            .offset(y: offset > 0 ? -offset * 0.5 : 0)
                    }
                    .clipped()
                
                ContentView()
            }
        }
    }
}
```

## Scroll Target Behavior

> **iOS 17+**: All APIs in this section require iOS 17 or later.

### Paging ScrollView

```swift
struct PagingView: View {
    var body: some View {
        ScrollView(.horizontal) {
            LazyHStack(spacing: 0) {
                ForEach(pages) { page in
                    PageView(page: page)
                        .containerRelativeFrame(.horizontal)
                }
            }
            .scrollTargetLayout()
        }
        .scrollTargetBehavior(.paging)
    }
}
```

### Snap to Items

```swift
struct SnapScrollView: View {
    var body: some View {
        ScrollView(.horizontal) {
            LazyHStack(spacing: 16) {
                ForEach(items) { item in
                    ItemCard(item: item)
                        .frame(width: 280)
                }
            }
            .scrollTargetLayout()
        }
        .scrollTargetBehavior(.viewAligned)
        .contentMargins(.horizontal, 20)
    }
}
```

## iOS 18+ Scroll APIs

> **iOS 18+**: APIs in this section require iOS 18 or later.

### scrollPosition() without ID

**Use `scrollPosition()` to programmatically scroll to an item by binding its ID to state — no `ScrollViewReader` needed:**

```swift
struct ProgrammaticScrollView: View {
    @State private var scrolledID: Item.ID?

    var body: some View {
        ScrollView {
            LazyVStack {
                ForEach(items) { item in
                    ItemRow(item: item)
                        .id(item.id)
                }
            }
        }
        .scrollPosition($scrolledID)
    }

    func scrollToFirst() {
        withAnimation {
            scrolledID = items.first?.id
        }
    }
}
```

### onScrollGeometryChange

**Use `onScrollGeometryChange(for:of:action:)` to observe scroll geometry — a more efficient replacement for `GeometryReader` + `PreferenceKey`. It only invokes the action when the extracted value actually changes:**

```swift
struct OffsetTrackingView: View {
    @State private var contentOffset: CGFloat = 0

    var body: some View {
        ScrollView {
            content
        }
        .onScrollGeometryChange(for: CGFloat.self) { geometry in
            geometry.contentOffset.y
        } action: { oldValue, newValue in
            contentOffset = newValue
        }
    }
}
```

`geometry` provides access to: `contentOffset`, `contentSize`, `containerSize`, and `visibleRect`. Use `for:` to extract only the value you need — the action closure is only called when that value changes.

## Summary Checklist

- [ ] Use `ScrollViewReader` with stable IDs for programmatic scrolling
- [ ] Use `.visualEffect` for scroll-based visual changes
- [ ] Use `.scrollTargetBehavior(.paging)` for paging behavior
- [ ] Use `.scrollTargetBehavior(.viewAligned)` for snap-to-item behavior
- [ ] Use `onScrollGeometryChange` (iOS 18+) for efficient scroll geometry observation
- [ ] Use `scrollPosition()` (iOS 18+) for programmatic scroll position binding
- [ ] Gate frequent scroll position updates by thresholds
- [ ] Use `GeometryReader` + preference keys only when targeting iOS 17 or earlier
