# Latest SwiftUI APIs Reference

> Based on a comparison of Apple's documentation using the Sosumi MCP, we found the latest recommended APIs to use.

> This file lists *what* the modern replacements are. For *how to behave* when you find a soft-deprecated API — when to migrate, when to leave it alone, and the scoping rule for unrelated edits — see `references/soft-deprecation.md`. To refresh this list after a new SDK release, run the maintenance skill at `.agents/skills/update-swiftui-apis/SKILL.md`.

## Table of Contents
- [Always Use (iOS 15+)](#always-use-ios-15)
- [When Targeting iOS 16+](#when-targeting-ios-16)
- [When Targeting iOS 17+](#when-targeting-ios-17)
- [When Targeting iOS 18+](#when-targeting-ios-18)
- [When Targeting iOS 26+](#when-targeting-ios-26)
- [When Targeting iOS 27+](#when-targeting-ios-27)

---

## Always Use (iOS 15+)

These APIs have been deprecated long enough that there is no reason to use the old variants.

### Compact Replacements

These replacements have minimal API shape changes. Most are near-direct swaps; a few require an additional parameter or structural adjustment:

- **`navigationTitle(_:)`** instead of `navigationBarTitle(_:)`
- **`toolbar { ToolbarItem(...) }`** instead of `navigationBarItems(...)` (structural change)
- **`ignoresSafeArea(_:edges:)`** instead of `edgesIgnoringSafeArea(_:)`
- **`preferredColorScheme(_:)`** instead of `colorScheme(_:)`
- **`foregroundStyle(_:)`** instead of `foregroundColor(_:)` (e.g., `.foregroundStyle(.primary)`)
- **`clipShape(.rect(cornerRadius:))`** instead of `cornerRadius()`
- **`textInputAutocapitalization(_:)`** instead of `autocapitalization(_:)` (note: `.never` replaces `.none`)
- **`animation(_:value:)`** instead of `animation(_:)` (adds required `value:` parameter; back-deploys to iOS 13+)
- **`dismiss` or `isPresented` environment values** instead of `PresentationMode` / `presentationMode`
- **`DynamicTypeSize` / `dynamicTypeSize`** instead of `ContentSizeCategory` / `sizeCategory`
- **Closure-based `NavigationLink` destinations** instead of eager `destination:` values
- **Direct `Animatable` conformance** instead of `AnimatableModifier` (use `@Animatable` only when its newer availability fits)

### Lists and Forms

**Use trailing-closure `Section` initializers instead of the positional header/footer View initializers.**

The single-title form is still current and should not be treated as deprecated:

```swift
// Current - single-title LocalizedStringKey initializer
Section("Settings") {
    Toggle("Notifications", isOn: .constant(true))
}

// Replacement - content/header/footer trailing-closure initializer
Section {
    Toggle("Notifications", isOn: .constant(true))
} header: {
    Text("Settings")
} footer: {
    Text("Changes apply immediately.")
}

// Deprecated/renamed - positional header/footer View arguments
Section(header: Text("Settings"), footer: Text("Changes apply immediately.")) {
    Toggle("Notifications", isOn: .constant(true))
}

Section(header: Text("Settings")) {
    Toggle("Notifications", isOn: .constant(true))
}

Section(footer: Text("Changes apply immediately.")) {
    Toggle("Notifications", isOn: .constant(true))
}
```

### Presentation

- **Always use `.confirmationDialog(_:isPresented:actions:message:)`** instead of `actionSheet(...)`.
- **Always use `.alert(_:isPresented:actions:message:)`** instead of `alert(isPresented:content:)`.

Both take a title `String`, `isPresented: Binding<Bool>`, an `actions` builder with `Button` items (supporting `role: .destructive` / `.cancel`), and an optional `message` builder:

```swift
.alert("Delete Item?", isPresented: $showAlert) {
    Button("Delete", role: .destructive) { deleteItem() }
    Button("Cancel", role: .cancel) { }
} message: {
    Text("This action cannot be undone.")
}
```

### Text Input

**Always use `onSubmit(of:_:)` and `focused(_:equals:)` instead of `TextField` `onEditingChanged`/`onCommit` callbacks.**

```swift
@FocusState private var isFocused: Bool

TextField("Search", text: $query)
    .focused($isFocused)
    .onSubmit { performSearch() }
```

### Accessibility

**Always use dedicated accessibility modifiers instead of the generic `accessibility(...)` variants.** Use `.accessibilityLabel()`, `.accessibilityValue()`, `.accessibilityHint()`, `.accessibilityAddTraits()`, `.accessibilityHidden()` instead of `.accessibility(label:)`, `.accessibility(value:)`, etc.

### Custom Environment / Container Values

**Always use the `@Entry` macro instead of manual `EnvironmentKey` conformance.** The `@Entry` macro was introduced in Xcode 16 and back-deploys to all OS versions.

```swift
// Modern — one line replaces ~10 lines of EnvironmentKey boilerplate
extension EnvironmentValues {
    @Entry var myCustomValue: String = "Default value"
}
```

### Styling

**Always use `Button` instead of `onTapGesture()` unless you need tap location or count.**

```swift
Button("Tap me") { performAction() }

// Use onTapGesture only when you need location or count
Image("photo")
    .onTapGesture(count: 2) { handleDoubleTap() }
```

---

## When Targeting iOS 16+

### Navigation

**Use `NavigationStack` (or `NavigationSplitView`) instead of `NavigationView`.** Value-based `NavigationLink(value:)` with `.navigationDestination(for:)` replaces destination-based links.

```swift
NavigationStack {
    List(items) { item in
        NavigationLink(value: item) { Text(item.name) }
    }
    .navigationDestination(for: Item.self) { DetailView(item: $0) }
}
```

### Simple Renames

- **`tint(_:)`** instead of `accentColor(_:)`
- **`autocorrectionDisabled(_:)`** instead of `disableAutocorrection(_:)`

### Scroll Indicators and Search Suggestions

- Replace `ScrollView(..., showsIndicators:)` with `ScrollView(...)` plus `scrollIndicators(_:axes:)`.
- Replace `searchable` overloads with an inline suggestions builder by composing `searchable(...)` with `searchSuggestions { ... }`.

### Clipboard

**Prefer `PasteButton` for user-initiated paste UI** to avoid paste prompts. It handles permissions automatically. Use `UIPasteboard` only when you need programmatic or non-`Transferable` clipboard access (triggers the paste permission prompt).

```swift
PasteButton(payloadType: String.self) { strings in
    pastedText = strings.first ?? ""
}
```

---

## When Targeting iOS 17+

### State Management

- **Prefer `@Observable` over `ObservableObject` for new code.** Use `@State` instead of `@StateObject`; use `@Bindable` instead of `@ObservedObject`. See `state-management.md` for full `@Observable` migration patterns.

### Events

**Use `onChange(of:initial:_:)` or `onChange(of:) { }` instead of `onChange(of:perform:)`.**

The deprecated variant passes only the new value. The modern variants provide either both old and new values, or a no-parameter closure.

- **No-parameter** (most common): `.onChange(of: value) { doSomething() }`
- **Old and new values**: `.onChange(of: value) { old, new in ... }`
- **With initial trigger**: `.onChange(of: value, initial: true) { ... }`
- **Deprecated**: `.onChange(of: value) { newValue in ... }` — single-parameter closure

### Sensory Feedback

**Prefer `sensoryFeedback(_:trigger:)` and related overloads instead of `UIImpactFeedbackGenerator`, `UISelectionFeedbackGenerator`, and `UINotificationFeedbackGenerator` in SwiftUI views.**

Attach haptics declaratively to the view that owns the state change, rather than imperatively firing UIKit generators inside button actions.

```swift
@State private var isFavorite = false

Button("Favorite", systemImage: isFavorite ? "heart.fill" : "heart") {
    isFavorite.toggle()
}
.sensoryFeedback(.selection, trigger: isFavorite)
```

Use the conditional overload when feedback should fire only for specific transitions:

```swift
.sensoryFeedback(.selection, trigger: phase) { old, new in
    old == .inactive || new == .expanded
}
```

### Gestures

- **`MagnifyGesture`** instead of `MagnificationGesture` (access magnitude via `value.magnification`)
- **`RotateGesture`** instead of `RotationGesture` (access angle via `value.rotation`)

### Layout

**Consider `containerRelativeFrame()` or `visualEffect()` as alternatives to `GeometryReader` for sizing and position-based effects.** `GeometryReader` is not deprecated and remains necessary for many measurement-based layouts.

```swift
Image("hero")
    .resizable()
    .containerRelativeFrame(.horizontal) { length, axis in length * 0.8 }
```

- **`visualEffect { content, geometry in ... }`** — position-based effects (parallax, offsets) without a `GeometryReader` wrapper.
- **`onGeometryChange(for:of:action:)`** — react to geometry changes of a specific view; useful for driving state/effects. `GeometryReader` is still better when layout itself depends on geometry. Note the two-closure shape:
  ```swift
  .onGeometryChange(for: CGFloat.self) { proxy in proxy.size.height } action: { newHeight in height = newHeight }
  ```
- **`.coordinateSpace(.named("scroll"))`** instead of `.coordinateSpace(name: "scroll")`.

Prefer overloads accepting `CoordinateSpaceProtocol` for `SpatialTapGesture`, location-aware `onTapGesture`, `onContinuousHover`, and `GeometryProxy.frame(in:)`.

Resolve a color in the current environment before accessing Core Graphics:

```swift
let cgColor = color.resolve(in: environment).cgColor
```

---

## When Targeting iOS 18+

### Toolbar Visibility

Use `toolbarVisibility(_:for:)` instead of `navigationBarHidden(_:)` or the older `toolbar(_:for:)` visibility overload. For deployment targets below iOS 18, retain the older modifier in the fallback branch.

Use `toolbarBackgroundVisibility(_:for:)` instead of the `toolbarBackground(_:for:)` overload whose first argument is `Visibility`.

On iOS, prefer `.topBarLeading` / `.topBarTrailing` over `.navigationBarLeading` / `.navigationBarTrailing`.

### Tabs

**Use the `Tab` API instead of `tabItem(_:)`.**

```swift
TabView {
    Tab("Home", systemImage: "house") { HomeView() }
    Tab("Search", systemImage: "magnifyingglass") { SearchView() }
    Tab("Profile", systemImage: "person") { ProfileView() }
}
```

When using `Tab(role:)`, all tabs must use the `Tab` syntax. Mixing `Tab(role:)` with `.tabItem()` causes compilation errors.

On iOS 18.4+ / macOS 15.4+, use the typed customization accessors:

- `customization[section: id].tabOrder`
- `customization[tab: id].sidebarVisibility`
- `customization[section: id].resetTabOrder()`

### Previews

**Use `@Previewable` for dynamic properties in previews.**

```swift
// Modern (iOS 18+)
#Preview {
    @Previewable @State var isOn = false
    Toggle("Setting", isOn: $isOn)
}
```

---

## When Targeting iOS 26+

For Liquid Glass APIs (`glassEffect`, `GlassEffectContainer`, glass button styles), see [liquid-glass.md](liquid-glass.md).

### Scroll Edge Effects

**Use `scrollEdgeEffectStyle(_:for:)` to configure scroll edge behavior.**

```swift
ScrollView {
    // content
}
.scrollEdgeEffectStyle(.soft, for: .top)
```

### Background Extension

**Use `backgroundExtensionEffect()` for edge-extending blurred backgrounds.**

Views behind a Liquid Glass sidebar can appear clipped. This modifier mirrors and blurs content outside the safe area so artwork remains visible.

```swift
Image("hero")
    .backgroundExtensionEffect()
```

> Source: "Build a SwiftUI app with the new design" (WWDC25, session 323)

### Tab Bar

**Use `tabBarMinimizeBehavior(_:)` to control tab bar minimization on scroll.**

```swift
TabView {
    // tabs
}
.tabBarMinimizeBehavior(.onScrollDown)
```

**Use `tabViewBottomAccessory` for persistent controls above the tab bar.** Read `tabViewBottomAccessoryPlacement` from the environment to adapt content when the accessory collapses into the tab bar area.

```swift
TabView {
    // tabs
}
.tabViewBottomAccessory {
    NowPlayingBar()
}
```

**Use `Tab(role: .search)` for a dedicated search tab.** The tab separates from the rest and morphs into a search field when selected.

```swift
TabView {
    Tab("Home", systemImage: "house") { HomeView() }
    Tab("Profile", systemImage: "person") { ProfileView() }
    Tab(role: .search) { SearchResultsView() }
}
```

> Source: "What's new in SwiftUI" (WWDC25, session 256) and "Build a SwiftUI app with the new design" (WWDC25, session 323)

### Toolbars

For `ToolbarSpacer`, shared-background visibility, badges, customization, transitions, overflow, and minimization, consult [`toolbar-patterns.md`](toolbar-patterns.md).

### Search

Use `searchToolbarBehavior(.minimize)` on iOS or visionOS 26+ to opt into a minimized search button. See [`toolbar-patterns.md`](toolbar-patterns.md) for platform availability.

### Animations

**Use `@Animatable` macro instead of manual `animatableData` declarations.** The macro auto-synthesizes `animatableData` from all animatable properties. Use `@AnimatableIgnored` to exclude specific properties.

```swift
@Animatable
struct Wedge: Shape {
    var startAngle: Angle
    var endAngle: Angle
    @AnimatableIgnored var drawClockwise: Bool

    func path(in rect: CGRect) -> Path { /* ... */ }
}
```

> Source: "What's new in SwiftUI" (WWDC25, session 256)

### Presentations

**Use `navigationZoomTransition` to morph sheets out of their source view.** Toolbar items and buttons can serve as the transition source.

```swift
.toolbar {
    ToolbarItem {
        Button("Add", systemImage: "plus") { showSheet = true }
            .navigationTransitionSource(id: "addSheet", namespace: namespace)
    }
}
.sheet(isPresented: $showSheet) {
    AddItemView()
        .navigationTransitionDestination(id: "addSheet", namespace: namespace)
}
```

> Source: "Build a SwiftUI app with the new design" (WWDC25, session 323)

### Controls

**Use `controlSize(.extraLarge)` for extra-large prominent action buttons.**

```swift
Button("Get Started") { }
    .buttonStyle(.borderedProminent)
    .controlSize(.extraLarge)
```

**Use `concentric` corner style for buttons that match their container's corners.**

```swift
Button("Confirm") { }
    .clipShape(.rect(cornerRadius: 12, style: .concentric))
```

**Sliders now support tick marks and a neutral value.**

```swift
Slider(value: $speed, in: 0.5...2.0, step: 0.25) {
    Text("Speed")
} ticks: {
    SliderTick(value: 0.6)
    SliderTick(value: 0.9)
}
.sliderNeutralValue(1.0)
```

> Source: "Build a SwiftUI app with the new design" (WWDC25, session 323)

### Rich Text

**Use `TextEditor` with an `AttributedString` binding for rich text editing.** Supports bold, italic, underline, strikethrough, custom fonts, foreground/background colors, paragraph styles, and Genmoji.

```swift
@State private var text: AttributedString = "Hello, world!"

var body: some View {
    TextEditor(text: $text)
}
```

> Source: "Cook up a rich text experience in SwiftUI with AttributedString" (WWDC25, session 280)

### Web Content

**Use `WebView` to display web content.** For richer interaction, create a `WebPage` observable model.

```swift
// Simple URL display
WebView(url: URL(string: "https://example.com")!)

// With observable model
@State private var page = WebPage()

WebView(page)
    .onAppear { page.load(URLRequest(url: myURL)) }
    .navigationTitle(page.title ?? "")
```

> Source: "Meet WebKit for SwiftUI" (WWDC25, session 231)

### Drag and Drop

**Use `dragContainer` for multi-item drag operations.** Combine with `DragConfiguration` for custom drag behavior and `onDragSessionUpdated` to observe events.

```swift
PhotoGrid(photos: photos)
    .dragContainer(for: Photo.self) { selection in
        return selection.map { $0.transferable }
    }
    .onDragSessionUpdated { session in
        if session.phase == .endedWithDelete {
            deleteSelectedPhotos()
        }
    }
```

Migrate the older location/`isTargeted` `dropDestination` overload to `dropDestination(for:isEnabled:action:)` when targeting iOS, macOS, or visionOS 26+. Its action receives a `DropSession` and returns `Void`, so this is a behavioral migration rather than a label-only rename.

> Source: "What's new in SwiftUI" (WWDC25, session 256)

### Scene Bridging

**UIKit and AppKit lifecycle apps can now request SwiftUI scenes.** This enables using SwiftUI-only scene types like `MenuBarExtra` and `ImmersiveSpace` from imperative lifecycle apps via `UIApplication.shared.activateSceneSession(for:errorHandler:)`.

> Source: "What's new in SwiftUI" (WWDC25, session 256)

---

## When Targeting iOS 27+

Use the focused topic references for detailed guidance:

- [`state-management.md`](state-management.md)
- [`view-structure.md`](view-structure.md)
- [`list-patterns.md`](list-patterns.md)
- [`image-optimization.md`](image-optimization.md)
- [`sheet-navigation-patterns.md`](sheet-navigation-patterns.md)
- [`toolbar-patterns.md`](toolbar-patterns.md)

On iOS 27+, use `toolbarVisibility(_:for: .statusBar)` instead of `statusBarHidden(_:)`. `ToolbarPlacement.statusBar` is iOS-only; on visionOS, remove `statusBarHidden` because it has no effect. The newer `dropDestination(for:isEnabled:action:)` overload is also available on visionOS 26+ (as well as iOS/macOS 26+).

### Additional SDK 27 soft-deprecated families

Use `Menu` / `MenuStyle` instead of `MenuButton`, `MenuButtonStyle`, and the legacy menu-button styles (`PullDownMenuButtonStyle`, `BorderlessPullDownMenuButtonStyle`, `BorderlessButtonMenuButtonStyle`, `DefaultMenuButtonStyle`, `BorderedButtonMenuStyle`, and `BorderlessButtonMenuStyle`). Use `.menuStyle(.menu)` or `.menuStyle(.button)` with a button style instead of `PopUpButtonPickerStyle`.

Other lookup entries from the SDK include:

- `ContextMenu` and `contextMenu(_:)` → `contextMenu(menuItems:)`
- `Section(header:...)/Section(footer:...)/Section(header:footer:...)` → trailing-closure `Section(content:header:footer:)` forms
- `GroupBox(label:content:)` → `GroupBox(content:label:)`
- `Picker(selection:label:content:)` → `Picker(selection:content:label:)`
- `Color(_:)` platform and `CGColor` initializers → `Color(uiColor:)`, `Color(nsColor:)`, and `Color(cgColor:)`; `Color.cgColor` → `resolve(in:).cgColor`
- `onLongPressGesture` overloads with `pressing:` → `onLongPressGesture(minimumDuration:maximumDuration:perform:onPressingChanged:)` or its shorter counterpart
- `Font.system(_:design:)` and legacy `Font.system(size:weight:design:)` forms → `system(_:weight:design:)` and the current size/weight/design overloads
- `Section.collapsible(_:)` → a standard `Section` initializer (collapsibility is no longer enabled by that modifier)
- string-type paste/drop APIs (`PasteButton`, `onPasteCommand`, `onInsert`, and `DropInfo.hasItemsConforming`) → UTType-based APIs

Platform-specific entries include `CarouselTabViewStyle` → `VerticalTabViewStyle` and `listRowPlatterColor(_:)` → `listItemTint(_:)` on watchOS, `ControlActiveState` → `appearsActive` on macOS, and `SurroundingsEffect.systemDark` → `.dark` on visionOS.

Search this file's lookup table when migrating an API that the 27 SDK marks soft-deprecated. Do not introduce unrelated migrations during feature work; follow [`soft-deprecation.md`](soft-deprecation.md).

---

## Quick Lookup Table

| Deprecated | Recommended | Since |
|-----------|-------------|-------|
| `navigationBarTitle(_:)` | `navigationTitle(_:)` | iOS 15+ |
| `navigationBarItems(...)` | `toolbar { ToolbarItem(...) }` | iOS 15+ |
| `navigationBarHidden(_:)` | `toolbarVisibility(.hidden, for: .navigationBar)` | iOS 18+; retain old API in earlier fallback |
| `statusBar(hidden:)` / `statusBarHidden(_:)` | `toolbarVisibility(_:for: .statusBar)` | iOS 27+; retain old API in earlier fallback |
| `edgesIgnoringSafeArea(_:)` | `ignoresSafeArea(_:edges:)` | iOS 15+ |
| `colorScheme(_:)` | `preferredColorScheme(_:)` | iOS 15+ |
| `foregroundColor(_:)` | `foregroundStyle(_:)` | iOS 15+ |
| `cornerRadius(_:)` | `clipShape(.rect(cornerRadius:))` | iOS 15+ |
| `actionSheet(...)` | `confirmationDialog(...)` | iOS 15+ |
| `alert(isPresented:content:)` | `alert(_:isPresented:actions:message:)` | iOS 15+ |
| `autocapitalization(_:)` | `textInputAutocapitalization(_:)` | iOS 15+ |
| `accessibility(label:)` etc. | `accessibilityLabel()` etc. | iOS 15+ |
| `TextField` `onCommit`/`onEditingChanged` | `onSubmit` + `focused` | iOS 15+ |
| `animation(_:)` (no value) | `animation(_:value:)` | Back-deploys (iOS 13+) |
| `Section(header:content:)` | `Section(content:header:)` | Future-deprecated |
| `Section(footer:content:)` | `Section(content:footer:)` | Future-deprecated |
| `Section(header:footer:content:)` | `Section(content:header:footer:)` | Future-deprecated |
| Manual `EnvironmentKey` | `@Entry` macro | Back-deploys (Xcode 16+) |
| `NavigationView` | `NavigationStack` / `NavigationSplitView` | iOS 16+ |
| `accentColor(_:)` | `tint(_:)` | iOS 16+ |
| `disableAutocorrection(_:)` | `autocorrectionDisabled(_:)` | iOS 16+ |
| `UIPasteboard.general` | `PasteButton` | iOS 16+ |
| `onChange(of:perform:)` | `onChange(of:) { }` or `onChange(of:) { old, new in }` | iOS 17+ |
| `UIImpactFeedbackGenerator` / `UISelectionFeedbackGenerator` / `UINotificationFeedbackGenerator` | `sensoryFeedback(_:trigger:)` | iOS 17+ |
| `MagnificationGesture` | `MagnifyGesture` | iOS 17+ |
| `RotationGesture` | `RotateGesture` | iOS 17+ |
| `coordinateSpace(name:)` | `coordinateSpace(.named(...))` | iOS 17+ |
| `ObservableObject` | `@Observable` | iOS 17+ |
| `tabItem(_:)` | `Tab` API | iOS 18+ |
| Manual 1:1 `animatableData` synthesis | `@Animatable` macro; keep manual logic for clamping/normalization | iOS 26+ |
| `presentationBackground(_:)` on sheets | Default Liquid Glass sheet material | iOS 26+ |
| Custom toolbar background hacks | `scrollEdgeEffectStyle(_:for:)` | iOS 26+ |
| `CarouselTabViewStyle` (watchOS) | `VerticalTabViewStyle` | SDK 27 soft-deprecated |
| `ControlActiveState` / `controlActiveState` (macOS) | `appearsActive` | SDK 27 soft-deprecated |
| `AnimatableModifier` | Conform the modifier to `Animatable` directly | SDK 27 soft-deprecated |
| `FileDocument`, `ReferenceFileDocument`, and legacy `DocumentGroup` initializers | `Document` (`ReadableDocument` / `WritableDocument`) and closure-based `DocumentGroup` | SDK 27 soft-deprecated; replacement requires aligned 27 releases |
| `TabView(selection:content:)` legacy builder | `TabContentBuilder`-based `TabView` initializers | SDK 27 soft-deprecated |
| `listRowPlatterColor(_:)` (watchOS) | `listItemTint(_:)` | SDK 27 soft-deprecated |
| `toolbarBackground(_:for:)` visibility overload | `toolbarBackgroundVisibility(_:for:)` | iOS 18+ / macOS 15+ |
| `toolbar(_:for:)` visibility overload | `toolbarVisibility(_:for:)` | iOS 18+ / macOS 15+ |
| `searchable(..., suggestions:)` builder overloads | `searchable(...)` plus `searchSuggestions { ... }` | iOS 16+ / macOS 13+ |
| `ScrollView(..., showsIndicators:)` | `ScrollView(...)` plus `scrollIndicators(_:axes:)` | iOS 16+ / macOS 13+ |
| Eager `NavigationLink(destination:)` initializers | Closure destination or value-based navigation | SDK 27 soft-deprecated |
| String type identifiers in paste/drop APIs | `UTType`-based overloads | SDK 27 soft-deprecated |
| Coordinate-space overloads taking `CoordinateSpace` | `CoordinateSpaceProtocol` overloads | iOS 17+ / macOS 14+ |
| Style initializers with `tint:` | Apply `View.tint(_:)` | SDK 27 soft-deprecated |
| Inset/bordered list or table styles with `alternatesRowBackgrounds:` | Base style plus `alternatingRowBackgrounds()` | SDK 27 soft-deprecated |
| `ToolbarItem(..., showsByDefault:)` | `defaultCustomization(_:options:)` with `.hidden` | SDK 27 soft-deprecated |
| `TabViewCustomization` legacy section/sidebar subscripts | Typed `section`/`tab` subscript properties | iOS 18.4+ / macOS 15.4+ |
| Location/`isTargeted` `dropDestination` overload | `dropDestination(for:isEnabled:action:)` with `DropSession` | iOS/macOS/visionOS 26+ |
