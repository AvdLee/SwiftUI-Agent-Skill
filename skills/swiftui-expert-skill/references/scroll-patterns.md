# SwiftUI ScrollView Patterns Reference

## Table of Contents

- [Choose the Appropriate Scroll API](#choose-the-appropriate-scroll-api)
- [ScrollViewReader for Programmatic Scrolling](#scrollviewreader-for-programmatic-scrolling)
- [Scroll Position Tracking](#scroll-position-tracking)
- [Scroll Transitions and Effects](#scroll-transitions-and-effects)
- [Scroll Target Behavior](#scroll-target-behavior)
- [Summary Checklist](#summary-checklist)

## Choose the Appropriate Scroll API

- On iOS 18+, use `onScrollGeometryChange(for:of:action:)` to observe scroll geometry.
- On iOS 18+, use `scrollPosition(_:)` with `ScrollPosition` to scroll by identity, offset, or edge.
- On iOS 17+, use `scrollPosition(id:)` when an optional ID binding is sufficient.
- Use `ScrollViewReader` when proxy-based scrolling or support for earlier versions is needed.

## ScrollViewReader for Programmatic Scrolling

**Use `ScrollViewReader` for proxy-based scroll-to-top, scroll-to-bottom, and anchor-based jumps.**

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

**Why**: `ScrollViewReader` provides proxy-based programmatic scroll control. Use stable IDs for scroll targets, and add animation when an animated transition is appropriate.

## Scroll Position Tracking

> **iOS 18+**: Use `onScrollGeometryChange(for:of:action:)` to observe scroll geometry and `scrollPosition(_:)` with a `ScrollPosition` binding for flexible programmatic scrolling. For iOS 17, use `scrollPosition(id:)` with an optional ID binding.

### Observe Scroll Geometry (iOS 18+)

`onScrollGeometryChange` transforms frequently changing `ScrollGeometry` into an `Equatable` value and runs its action when that transformed value changes. Extract the smallest value needed by the feature.

When exact offset tracking is required, extract `contentOffset`. This value normally changes on every scrolling frame, so avoid using it to update large or expensive view hierarchies:

```swift
struct OffsetTrackingView: View {
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

When only a threshold matters, transform the geometry into a `Bool` so the action runs only when the scroll view crosses that threshold. The header visibility example below demonstrates this pattern.

### Programmatic Scroll Position (iOS 18+)

The unlabeled `scrollPosition(_:)` overload requires a `Binding<ScrollPosition>`. Add `scrollTargetLayout()` to the layout containing the identified views:

```swift
struct ProgrammaticScrollView: View {
    @State private var position = ScrollPosition(idType: Item.ID.self)

    var body: some View {
        ScrollView {
            LazyVStack {
                ForEach(items) { item in
                    ItemRow(item: item)
                }
            }
            .scrollTargetLayout()
        }
        .scrollPosition($position)
        .toolbar {
            Button("Scroll to First") {
                if let firstID = items.first?.id {
                    withAnimation {
                        position.scrollTo(id: firstID)
                    }
                }
            }
        }
    }
}
```

For iOS 17, bind the ID using the labeled overload instead:

```swift
@State private var scrolledID: Item.ID?

ScrollView {
    LazyVStack {
        ForEach(items) { item in
            ItemRow(item: item)
        }
    }
    .scrollTargetLayout()
}
.scrollPosition(id: $scrolledID)
```

### Scroll-Based Header Visibility

Extracting the threshold as a `Bool` avoids running the action for every offset change:

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
            .onScrollGeometryChange(for: Bool.self) { geometry in
                geometry.contentOffset.y + geometry.contentInsets.top > 50
            } action: { _, isPastThreshold in
                withAnimation {
                    showHeader = !isPastThreshold
                }
            }
        }
    }
}
```

<details>
<summary>Pre-iOS 18 compatibility — GeometryReader + PreferenceKey</summary>

Use this approach when supporting iOS 17 or earlier. `GeometryReader` and preferences remain available, but require a named coordinate space and a custom `PreferenceKey`.

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
                let shouldShowHeader = offset >= -50
                if shouldShowHeader != showHeader {
                    withAnimation {
                        showHeader = shouldShowHeader
                    }
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

## Summary Checklist

- [ ] Use `ScrollViewReader` with stable IDs when proxy-based scrolling is needed
- [ ] Use `.visualEffect` for scroll-based visual changes
- [ ] Use `.scrollTargetBehavior(.paging)` for paging behavior
- [ ] Use `.scrollTargetBehavior(.viewAligned)` for snap-to-item behavior
- [ ] Use `onScrollGeometryChange` (iOS 18+) and extract only the value needed
- [ ] Use `scrollPosition(_:)` with `ScrollPosition` for flexible scrolling on iOS 18+
- [ ] Use `scrollPosition(id:)` with an optional ID binding on iOS 17+
- [ ] Add `.scrollTargetLayout()` when scrolling to identified views
- [ ] Derive threshold values instead of propagating every offset change when possible
- [ ] Use the `GeometryReader` + preference approach when supporting pre-iOS 18 versions
