# Latest SwiftUI APIs Reference

> Based on a comparison of Apple's documentation using the Sosumi MCP, we found the latest recommended APIs to use.

## Table of Contents
- [Always Use (iOS 15+)](#always-use-ios-15)
- [When Targeting iOS 16+](#when-targeting-ios-16)
- [When Targeting iOS 17+](#when-targeting-ios-17)
- [When Targeting iOS 18+](#when-targeting-ios-18)
- [When Targeting iOS 26+](#when-targeting-ios-26)

---

## Always Use (iOS 15+)

These APIs have been deprecated long enough that there is no reason to use the old variants.

### Navigation

**Always use `navigationTitle(_:)` instead of `navigationBarTitle(_:)`.**

```swift
// Modern
NavigationStack {
    List { /* ... */ }
        .navigationTitle("Flavors")
}

// Deprecated
NavigationView {
    List { /* ... */ }
        .navigationBarTitle("Flavors")
}
```

**Always use `toolbar { }` instead of `navigationBarItems(...)`.**

```swift
// Modern
.toolbar {
    ToolbarItem(placement: .topBarTrailing) {
        Button("Add", systemImage: "plus") { addItem() }
    }
}

// Deprecated
.navigationBarItems(trailing:
    Button("Add", systemImage: "plus") { addItem() }
)
```

**Always use `toolbarVisibility(.hidden, for: .navigationBar)` instead of `navigationBarHidden(_:)`.**

```swift
// Modern
.toolbarVisibility(.hidden, for: .navigationBar)

// Deprecated
.navigationBarHidden(true)
```

**Always use `statusBarHidden(_:)` instead of `statusBar(hidden:)`.**

```swift
// Modern
.statusBarHidden(true)

// Deprecated
.statusBar(hidden: true)
```

### Layout

**Always use `ignoresSafeArea(_:edges:)` instead of `edgesIgnoringSafeArea(_:)`.**

```swift
// Modern
Color.blue
    .ignoresSafeArea(.all, edges: .top)

// Deprecated
Color.blue
    .edgesIgnoringSafeArea(.top)
```

### Appearance

**Always use `preferredColorScheme(_:)` instead of `colorScheme(_:)`.**

```swift
// Modern
.preferredColorScheme(.dark)

// Deprecated
.colorScheme(.dark)
```

**Always use `foregroundStyle()` instead of `foregroundColor()`.**

```swift
// Modern
Text("Hello")
    .foregroundStyle(.primary)

// Deprecated
Text("Hello")
    .foregroundColor(.primary)
```

### Presentation

**Always use `confirmationDialog(...)` instead of `actionSheet(...)`.**

```swift
// Modern
.confirmationDialog("Choose Option", isPresented: $showOptions) {
    Button("Option A") { selectA() }
    Button("Option B") { selectB() }
    Button("Cancel", role: .cancel) { }
} message: {
    Text("Select your preferred option.")
}

// Deprecated
.actionSheet(isPresented: $showOptions) {
    ActionSheet(title: Text("Choose Option"), buttons: [
        .default(Text("Option A")) { selectA() },
        .default(Text("Option B")) { selectB() },
        .cancel()
    ])
}
```

**Always use the modern `alert(_:isPresented:actions:message:)` instead of `alert(isPresented:content:)`.**

```swift
// Modern
.alert("Delete Item", isPresented: $showAlert) {
    Button("Delete", role: .destructive) { deleteItem() }
    Button("Cancel", role: .cancel) { }
} message: {
    Text("This action cannot be undone.")
}

// Deprecated
.alert(isPresented: $showAlert) {
    Alert(
        title: Text("Delete Item"),
        message: Text("This action cannot be undone."),
        destructiveButton: .destructive(Text("Delete")) { deleteItem() },
        dismissButton: .cancel()
    )
}
```

### Text Input

**Always use `textInputAutocapitalization(_:)` instead of `autocapitalization(_:)`.**

```swift
// Modern
TextField("Username", text: $username)
    .textInputAutocapitalization(.never)

// Deprecated
TextField("Username", text: $username)
    .autocapitalization(.none)
```

**Always use `onSubmit(of:_:)` and `focused(_:equals:)` instead of `TextField` `onEditingChanged`/`onCommit` callbacks.**

```swift
// Modern
@FocusState private var isFocused: Bool

TextField("Search", text: $query)
    .focused($isFocused)
    .onSubmit { performSearch() }

// Deprecated
TextField("Search", text: $query,
    onEditingChanged: { editing in /* ... */ },
    onCommit: { performSearch() }
)
```

### Accessibility

**Always use dedicated accessibility modifiers instead of the generic `accessibility(...)` variants.**

```swift
// Modern
Text("Score")
    .accessibilityLabel("Current score")
    .accessibilityValue("\(score) points")
    .accessibilityHint("Double-tap to reset")
    .accessibilityAddTraits(.isButton)
    .accessibilityHidden(false)

// Deprecated
Text("Score")
    .accessibility(label: Text("Current score"))
    .accessibility(value: Text("\(score) points"))
    .accessibility(hint: Text("Double-tap to reset"))
    .accessibility(addTraits: .isButton)
    .accessibility(hidden: false)
```

### Custom Environment / Container Values

**Always use the `@Entry` macro instead of manual `EnvironmentKey` conformance.** The `@Entry` macro was introduced in Xcode 16 and back-deploys to all OS versions.

```swift
// Modern
extension EnvironmentValues {
    @Entry var myCustomValue: String = "Default value"
}

// Legacy (unnecessary boilerplate)
struct MyCustomValueKey: EnvironmentKey {
    static let defaultValue: String = "Default value"
}

extension EnvironmentValues {
    var myCustomValue: String {
        get { self[MyCustomValueKey.self] }
        set { self[MyCustomValueKey.self] = newValue }
    }
}
```

### Styling

**Always use `clipShape(.rect(cornerRadius:))` instead of `cornerRadius()`.**

```swift
// Modern
Image("photo")
    .clipShape(.rect(cornerRadius: 12))

// Deprecated
Image("photo")
    .cornerRadius(12)
```

**Always use `Button` instead of `onTapGesture()` unless you need tap location or count.**

```swift
// Modern
Button("Tap me") { performAction() }

// Use onTapGesture only when you need location or count
Image("photo")
    .onTapGesture(count: 2) { handleDoubleTap() }
```

---

## When Targeting iOS 16+

### Navigation

**Use `NavigationStack` (or `NavigationSplitView`) instead of `NavigationView`.**

```swift
// Modern
NavigationStack {
    List(items) { item in
        NavigationLink(value: item) {
            Text(item.name)
        }
    }
    .navigationDestination(for: Item.self) { item in
        DetailView(item: item)
    }
}

// Deprecated
NavigationView {
    List(items) { item in
        NavigationLink(destination: DetailView(item: item)) {
            Text(item.name)
        }
    }
}
```

### Appearance

**Use `tint(_:)` instead of `accentColor(_:)`.**

```swift
// Modern
VStack {
    Button("Accented") { }
    Slider(value: $value)
}
.tint(.purple)

// Deprecated
VStack {
    Button("Accented") { }
    Slider(value: $value)
}
.accentColor(.purple)
```

### Text Input

**Use `autocorrectionDisabled(_:)` instead of `disableAutocorrection(_:)`.**

```swift
// Modern
TextField("Code", text: $code)
    .autocorrectionDisabled()

// Deprecated
TextField("Code", text: $code)
    .disableAutocorrection(true)
```

---

## When Targeting iOS 17+

### State Management

**Prefer `@Observable` over `ObservableObject` for new code.**

```swift
// Modern (iOS 17+)
@Observable
class UserProfile {
    var name: String = ""
    var email: String = ""
}

struct ProfileView: View {
    @State private var profile = UserProfile()
    var body: some View {
        TextField("Name", text: $profile.name)
    }
}

// Legacy
class UserProfile: ObservableObject {
    @Published var name: String = ""
    @Published var email: String = ""
}

struct ProfileView: View {
    @StateObject private var profile = UserProfile()
    var body: some View {
        TextField("Name", text: $profile.name)
    }
}
```

### Events

**Use `onChange(of:initial:_:)` or `onChange(of:) { }` instead of `onChange(of:perform:)`.**

The deprecated variant passes only the new value. The modern variants provide either both old and new values, or a no-parameter closure.

```swift
// Modern — no-parameter closure (most common)
.onChange(of: playState) {
    model.playStateDidChange(state: playState)
}

// Modern — old and new values
.onChange(of: selectedTab) { oldTab, newTab in
    analytics.trackTabChange(from: oldTab, to: newTab)
}

// Modern — with initial trigger
.onChange(of: searchText, initial: true) {
    performSearch()
}

// Deprecated
.onChange(of: playState) { newValue in
    model.playStateDidChange(state: newValue)
}
```

### Animation

**Use `animation(_:value:)` instead of `animation(_:)` without a value parameter.**

```swift
// Modern
Circle()
    .scaleEffect(isExpanded ? 1.5 : 1.0)
    .animation(.spring, value: isExpanded)

// Deprecated — applies to all animatable values (too broad)
Circle()
    .scaleEffect(isExpanded ? 1.5 : 1.0)
    .animation(.spring)
```

### Gestures

**Use `MagnifyGesture` instead of `MagnificationGesture`.**

```swift
// Modern
Image("photo")
    .gesture(
        MagnifyGesture()
            .onChanged { value in
                scale = value.magnification
            }
    )

// Deprecated
Image("photo")
    .gesture(
        MagnificationGesture()
            .onChanged { value in
                scale = value
            }
    )
```

**Use `RotateGesture` instead of `RotationGesture`.**

```swift
// Modern
Image("photo")
    .gesture(
        RotateGesture()
            .onChanged { value in
                angle = value.rotation
            }
    )

// Deprecated
Image("photo")
    .gesture(
        RotationGesture()
            .onChanged { value in
                angle = value
            }
    )
```

### Layout

**Consider `containerRelativeFrame()` or `visualEffect()` as alternatives to `GeometryReader` for sizing and position-based effects.** `GeometryReader` is not deprecated and remains necessary for many measurement-based layouts.

```swift
// Modern — containerRelativeFrame
Image("hero")
    .resizable()
    .containerRelativeFrame(.horizontal) { length, axis in
        length * 0.8
    }

// Modern — visualEffect for position-based effects
Text("Parallax")
    .visualEffect { content, geometry in
        content.offset(y: geometry.frame(in: .global).minY * 0.5)
    }

// Legacy — only use if necessary
GeometryReader { geometry in
    Image("hero")
        .frame(width: geometry.size.width * 0.8)
}
```

**Use `coordinateSpace(_:)` with `NamedCoordinateSpace` instead of `coordinateSpace(name:)`.**

```swift
// Modern
VStack { /* ... */ }
    .coordinateSpace(.named("stack"))

// Deprecated
VStack { /* ... */ }
    .coordinateSpace(name: "stack")
```

---

## When Targeting iOS 18+

### Tabs

**Use the `Tab` API instead of `tabItem(_:)`.**

```swift
// Modern (iOS 18+)
TabView {
    Tab("Home", systemImage: "house") {
        HomeView()
    }

    Tab("Search", systemImage: "magnifyingglass") {
        SearchView()
    }

    Tab("Profile", systemImage: "person") {
        ProfileView()
    }
}

// Legacy
TabView {
    HomeView()
        .tabItem {
            Label("Home", systemImage: "house")
        }

    SearchView()
        .tabItem {
            Label("Search", systemImage: "magnifyingglass")
        }
}
```

When using `Tab(role:)`, all tabs must use the `Tab` syntax. Mixing `Tab(role:)` with `.tabItem()` causes compilation errors.

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

### Liquid Glass

**Use `glassEffect(_:in:)` for glass material effects.**

```swift
if #available(iOS 26, *) {
    content
        .padding()
        .glassEffect(.regular.interactive(), in: .rect(cornerRadius: 16))
} else {
    content
        .padding()
        .background(.ultraThinMaterial, in: RoundedRectangle(cornerRadius: 16))
}
```

**Use `GlassEffectContainer` to group multiple glass elements.**

```swift
GlassEffectContainer(spacing: 24) {
    HStack(spacing: 24) {
        GlassButton1()
        GlassButton2()
    }
}
```

**Use glass button styles for buttons.**

```swift
Button("Confirm") { }
    .buttonStyle(.glassProminent)
```

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

```swift
Image("hero")
    .backgroundExtensionEffect()
```

### Tab Bar

**Use `tabBarMinimizeBehavior(_:)` to control tab bar minimization.**

```swift
TabView {
    // tabs
}
.tabBarMinimizeBehavior(.onScrollDown)
```

---

## Quick Lookup Table

| Deprecated | Recommended | Since |
|-----------|-------------|-------|
| `navigationBarTitle(_:)` | `navigationTitle(_:)` | iOS 15+ |
| `navigationBarItems(...)` | `toolbar { ToolbarItem(...) }` | iOS 15+ |
| `navigationBarHidden(_:)` | `toolbarVisibility(.hidden, for: .navigationBar)` | iOS 15+ |
| `statusBar(hidden:)` | `statusBarHidden(_:)` | iOS 15+ |
| `edgesIgnoringSafeArea(_:)` | `ignoresSafeArea(_:edges:)` | iOS 15+ |
| `colorScheme(_:)` | `preferredColorScheme(_:)` | iOS 15+ |
| `foregroundColor(_:)` | `foregroundStyle()` | iOS 15+ |
| `cornerRadius(_:)` | `clipShape(.rect(cornerRadius:))` | iOS 15+ |
| `actionSheet(...)` | `confirmationDialog(...)` | iOS 15+ |
| `alert(isPresented:content:)` | `alert(_:isPresented:actions:message:)` | iOS 15+ |
| `autocapitalization(_:)` | `textInputAutocapitalization(_:)` | iOS 15+ |
| `accessibility(label:)` etc. | `accessibilityLabel()` etc. | iOS 15+ |
| `TextField` `onCommit`/`onEditingChanged` | `onSubmit` + `focused` | iOS 15+ |
| Manual `EnvironmentKey` | `@Entry` macro | Back-deploys (Xcode 16+) |
| `NavigationView` | `NavigationStack` / `NavigationSplitView` | iOS 16+ |
| `accentColor(_:)` | `tint(_:)` | iOS 16+ |
| `disableAutocorrection(_:)` | `autocorrectionDisabled(_:)` | iOS 16+ |
| `onChange(of:perform:)` | `onChange(of:) { }` or `onChange(of:) { old, new in }` | iOS 17+ |
| `animation(_:)` (no value) | `animation(_:value:)` | iOS 17+ |
| `MagnificationGesture` | `MagnifyGesture` | iOS 17+ |
| `RotationGesture` | `RotateGesture` | iOS 17+ |
| `coordinateSpace(name:)` | `coordinateSpace(.named(...))` | iOS 17+ |
| `ObservableObject` | `@Observable` | iOS 17+ |
| `tabItem(_:)` | `Tab` API | iOS 18+ |
