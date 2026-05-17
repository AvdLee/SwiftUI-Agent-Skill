# SwiftUI Testing & Previews Reference

## Table of Contents

- [Preview Macro](#preview-macro)
- [Preview with Mock Data](#preview-with-mock-data)
- [@Previewable Property Wrappers](#previewable-property-wrappers)
- [XCTest for SwiftUI Views](#xctest-for-swiftui-views)
- [Snapshot Testing](#snapshot-testing)
- [Testing @Observable Models](#testing-observable-models)
- [Common Diagnostics](#common-diagnostics)
- [Summary Checklist](#summary-checklist)

---

## Preview Macro

The `#Preview` macro (Swift 5.9+, Xcode 15+) replaces the legacy `PreviewProvider` protocol with a lightweight syntax.

### Basic Usage

```swift
// ✅ Modern: #Preview macro
#Preview {
    ContentView()
}

// ✅ Named preview
#Preview("Dark Mode") {
    ContentView()
        .preferredColorScheme(.dark)
}

// ❌ Legacy: PreviewProvider (avoid for new code)
struct ContentView_Previews: PreviewProvider {
    static var previews: some View {
        ContentView()
    }
}
```

### Multiple Previews

```swift
#Preview("Default") {
    SettingsRow(title: "Notifications", isOn: true)
}

#Preview("Off State") {
    SettingsRow(title: "Notifications", isOn: false)
}

#Preview("Long Title") {
    SettingsRow(title: "Enable Push Notifications for All Events", isOn: true)
}
```

### Preview Traits

Use traits to configure the preview environment:

```swift
// Fixed size
#Preview(traits: .fixedLayout(width: 300, height: 100)) {
    CompactBanner(message: "Welcome")
}

// Size that fits content
#Preview(traits: .sizeThatFitsLayout) {
    BadgeView(count: 5)
}

// Landscape orientation
#Preview(traits: .landscapeLeft) {
    DashboardView()
}
```

### Previewing in NavigationStack

```swift
#Preview {
    NavigationStack {
        DetailView(item: .sample)
    }
}
```

### UIKit / AppKit Preview

The `#Preview` macro also supports UIKit view controllers and views:

```swift
// UIViewController
#Preview {
    let vc = ProfileViewController()
    vc.user = .sample
    return vc
}

// UIView
#Preview {
    let label = UILabel()
    label.text = "Hello"
    label.textAlignment = .center
    return label
}
```

---

## Preview with Mock Data

Previews should use self-contained mock data that compiles without external dependencies.

### Static Sample Data

```swift
struct Item: Identifiable {
    let id: UUID
    var name: String
    var price: Double
}

extension Item {
    static let sample = Item(id: UUID(), name: "Widget", price: 9.99)

    static let samples: [Item] = [
        Item(id: UUID(), name: "Widget", price: 9.99),
        Item(id: UUID(), name: "Gadget", price: 19.99),
        Item(id: UUID(), name: "Doohickey", price: 4.99),
    ]
}

#Preview {
    ItemListView(items: Item.samples)
}
```

### Mock Observable Models

```swift
@Observable
@MainActor
final class CartModel {
    var items: [Item] = []
    var isLoading = false

    static var preview: CartModel {
        let model = CartModel()
        model.items = Item.samples
        return model
    }

    static var emptyPreview: CartModel {
        CartModel()
    }

    static var loadingPreview: CartModel {
        let model = CartModel()
        model.isLoading = true
        return model
    }
}

#Preview("With Items") {
    CartView()
        .environment(CartModel.preview)
}

#Preview("Empty") {
    CartView()
        .environment(CartModel.emptyPreview)
}

#Preview("Loading") {
    CartView()
        .environment(CartModel.loadingPreview)
}
```

### Preview with Environment Dependencies

```swift
#Preview {
    OrderDetailView(order: .sample)
        .environment(CartModel.preview)
        .environment(\.locale, Locale(identifier: "ja_JP"))
        .environment(\.dynamicTypeSize, .xxxLarge)
}
```

### Protocol-Based Mock Services

For views that depend on network or data services, use protocols to inject mocks:

```swift
protocol DataFetching: Sendable {
    func fetchItems() async throws -> [Item]
}

struct LiveDataFetcher: DataFetching {
    func fetchItems() async throws -> [Item] {
        // Real network call
        try await URLSession.shared.decode([Item].self, from: endpoint)
    }
}

struct MockDataFetcher: DataFetching {
    var result: Result<[Item], Error> = .success(Item.samples)

    func fetchItems() async throws -> [Item] {
        try result.get()
    }
}

#Preview {
    ItemListView(fetcher: MockDataFetcher())
}

#Preview("Error State") {
    ItemListView(fetcher: MockDataFetcher(result: .failure(URLError(.notConnectedToInternet))))
}
```

---

## @Previewable Property Wrappers

`@Previewable` (iOS 18+, Xcode 16+) allows using `@State` and other property wrappers directly inside `#Preview` blocks, enabling interactive previews without wrapper views.

### Interactive State

```swift
// ✅ @Previewable: interactive toggle in preview
#Preview {
    @Previewable @State var isOn = false
    Toggle("Notifications", isOn: $isOn)
}

// ❌ Without @Previewable: requires a wrapper view
struct TogglePreviewWrapper: View {
    @State private var isOn = false
    var body: some View {
        Toggle("Notifications", isOn: $isOn)
    }
}

#Preview {
    TogglePreviewWrapper()
}
```

### Multiple Interactive Controls

```swift
#Preview {
    @Previewable @State var name = "Alice"
    @Previewable @State var age = 25.0

    VStack {
        TextField("Name", text: $name)
        Slider(value: $age, in: 0...100, step: 1) {
            Text("Age: \(Int(age))")
        }
        Text("Hello, \(name)! Age: \(Int(age))")
    }
    .padding()
}
```

### @Previewable with @FocusState

```swift
#Preview {
    @Previewable @FocusState var isFocused: Bool

    TextField("Search", text: .constant(""))
        .focused($isFocused)
        .onAppear { isFocused = true }
}
```

### Fallback for Pre-iOS 18

If targeting older OS versions, use wrapper views instead:

```swift
private struct SliderPreview: View {
    @State private var value = 0.5
    var body: some View {
        CustomSlider(value: $value)
    }
}

#Preview {
    SliderPreview()
}
```

---

## XCTest for SwiftUI Views

SwiftUI views are value types describing UI — they don't have a DOM you can query directly. Test strategies focus on the model layer and use UI tests for integration.

### Unit Testing @Observable Models

The most effective approach: test the model logic that drives the view.

```swift
import Testing

@MainActor
struct CartModelTests {
    @Test func addItemIncreasesCount() {
        let cart = CartModel()
        cart.addItem(.sample)
        #expect(cart.items.count == 1)
    }

    @Test func removeItemDecreasesTotal() {
        let cart = CartModel()
        cart.addItem(Item(id: UUID(), name: "Widget", price: 10.0))
        cart.removeAll()
        #expect(cart.items.isEmpty)
        #expect(cart.total == 0)
    }

    @Test func totalComputesCorrectly() {
        let cart = CartModel()
        cart.addItem(Item(id: UUID(), name: "A", price: 10.0))
        cart.addItem(Item(id: UUID(), name: "B", price: 20.0))
        #expect(cart.total == 30.0)
    }
}
```

### XCTest with Hosting (UIKit bridge)

For cases where you need to verify the rendered view hierarchy:

```swift
import XCTest
import SwiftUI

final class BadgeViewTests: XCTestCase {
    @MainActor
    func testBadgeRendersInHostingController() throws {
        let view = BadgeView(count: 5)
        let hostingController = UIHostingController(rootView: view)

        // Force layout
        hostingController.view.layoutIfNeeded()

        // Verify the hosting controller loaded without crash
        XCTAssertNotNil(hostingController.view)

        // Check accessibility
        let accessibilityLabel = hostingController.view.accessibilityLabel
        XCTAssertEqual(accessibilityLabel, "5 notifications")
    }
}
```

### UI Tests with XCUITest

For end-to-end integration testing:

```swift
import XCTest

final class SettingsUITests: XCTestCase {
    let app = XCUIApplication()

    override func setUpWithError() throws {
        continueAfterFailure = false
        app.launchArguments = ["--ui-testing"]
        app.launch()
    }

    @MainActor
    func testToggleNotifications() throws {
        let toggle = app.switches["Notifications"]
        XCTAssertTrue(toggle.exists)

        toggle.tap()
        XCTAssertEqual(toggle.value as? String, "1")
    }

    @MainActor
    func testNavigationToDetail() throws {
        app.buttons["Settings"].tap()
        XCTAssertTrue(app.navigationBars["Settings"].exists)

        app.cells.firstMatch.tap()
        XCTAssertTrue(app.navigationBars["Detail"].exists)
    }
}
```

### Accessibility Identifiers for Testing

Add identifiers to make views findable in UI tests:

```swift
struct ItemRow: View {
    let item: Item

    var body: some View {
        HStack {
            Text(item.name)
            Spacer()
            Text(item.price, format: .currency(code: "USD"))
        }
        .accessibilityIdentifier("item-row-\(item.id)")
    }
}
```

---

## Snapshot Testing

Snapshot testing captures rendered images of views and compares them against stored references. Useful for catching unintended visual regressions.

### Using swift-snapshot-testing

[swift-snapshot-testing](https://github.com/pointfreeco/swift-snapshot-testing) is the most widely adopted library.

**Setup** in `Package.swift`:

```swift
.package(url: "https://github.com/pointfreeco/swift-snapshot-testing", from: "1.17.0")
```

### Writing Snapshot Tests

```swift
import XCTest
import SnapshotTesting
import SwiftUI

final class BadgeViewSnapshotTests: XCTestCase {
    @MainActor
    func testDefaultAppearance() {
        let view = BadgeView(count: 3)
            .frame(width: 50, height: 50)

        assertSnapshot(
            of: UIHostingController(rootView: view),
            as: .image(on: .iPhone13)
        )
    }

    @MainActor
    func testDarkMode() {
        let view = BadgeView(count: 3)
            .frame(width: 50, height: 50)
            .preferredColorScheme(.dark)

        assertSnapshot(
            of: UIHostingController(rootView: view),
            as: .image(on: .iPhone13),
            named: "dark"
        )
    }

    @MainActor
    func testLargeContentSize() {
        let view = BadgeView(count: 3)
            .frame(width: 100, height: 50)
            .environment(\.dynamicTypeSize, .accessibility3)

        assertSnapshot(
            of: UIHostingController(rootView: view),
            as: .image(on: .iPhone13),
            named: "a11y-xxxl"
        )
    }
}
```

### Best Practices for Snapshots

- **Record once, then compare**: First run creates the reference image; subsequent runs compare against it.
- **Test multiple configurations**: Light/dark mode, dynamic type sizes, locales, device sizes.
- **Keep snapshots deterministic**: Use fixed dates, mock network images, disable animations.
- **Review diffs in PR**: Store reference images in the repo so reviewers can see visual changes.
- **Don't over-snapshot**: Focus on complex or layout-critical views. Simple `Text` labels don't need snapshots.

### Making Snapshots Deterministic

```swift
@MainActor
func testOrderCard() {
    // Fixed data — no random UUIDs or live dates
    let order = Order(
        id: "test-001",
        date: Date(timeIntervalSince1970: 1_700_000_000),
        items: [Item(id: "A", name: "Widget", price: 9.99)]
    )

    let view = OrderCard(order: order)
        .frame(width: 350)
        .environment(\.locale, Locale(identifier: "en_US"))
        .environment(\.timeZone, TimeZone(identifier: "UTC")!)

    assertSnapshot(of: UIHostingController(rootView: view), as: .image)
}
```

---

## Testing @Observable Models

### Async Method Testing

```swift
import Testing

@MainActor
struct ItemListModelTests {
    @Test func fetchItemsPopulatesList() async throws {
        let model = ItemListModel(fetcher: MockDataFetcher())
        #expect(model.items.isEmpty)

        await model.loadItems()

        #expect(model.items.count == 3)
        #expect(!model.isLoading)
    }

    @Test func fetchItemsHandlesError() async throws {
        let failingFetcher = MockDataFetcher(
            result: .failure(URLError(.notConnectedToInternet))
        )
        let model = ItemListModel(fetcher: failingFetcher)

        await model.loadItems()

        #expect(model.items.isEmpty)
        #expect(model.errorMessage != nil)
    }

    @Test func fetchItemsSetsLoadingState() async throws {
        let model = ItemListModel(fetcher: MockDataFetcher())

        // Before loading
        #expect(!model.isLoading)

        // After loading completes
        await model.loadItems()
        #expect(!model.isLoading)
    }
}
```

### Testing State Transitions

```swift
@Observable
@MainActor
final class FormModel {
    var email = ""
    var password = ""

    var isValid: Bool {
        email.contains("@") && password.count >= 8
    }

    enum SubmitState: Equatable {
        case idle, submitting, success, failed(String)
    }

    var submitState: SubmitState = .idle

    func submit() async {
        guard isValid else {
            submitState = .failed("Invalid input")
            return
        }
        submitState = .submitting
        do {
            try await api.submit(email: email, password: password)
            submitState = .success
        } catch {
            submitState = .failed(error.localizedDescription)
        }
    }
}

@MainActor
struct FormModelTests {
    @Test func validationRequiresAtSymbol() {
        let form = FormModel()
        form.email = "test"
        form.password = "12345678"
        #expect(!form.isValid)

        form.email = "test@example.com"
        #expect(form.isValid)
    }

    @Test func submitFailsWhenInvalid() async {
        let form = FormModel()
        form.email = "bad"
        form.password = "short"

        await form.submit()

        #expect(form.submitState == .failed("Invalid input"))
    }
}
```

---

## Common Diagnostics

| Error / Warning | Cause | Fix |
|---|---|---|
| `#Preview` body type mismatch | Returning a non-`View` type from `#Preview` block | Ensure the block returns a `View` (or `UIViewController` for UIKit) |
| `@Previewable` only available in iOS 18+ | Using `@Previewable` with lower deployment target | Use a wrapper view instead, or gate with `#available` |
| Preview crashes with "missing environment" | `@Environment(SomeType.self)` not injected in preview | Add `.environment(SomeType.preview)` to the preview |
| Snapshot test fails on CI but passes locally | Different OS / simulator version renders differently | Pin CI to a specific Xcode and simulator version |
| `@MainActor`-isolated model in non-isolated test | Calling `@MainActor` model methods from sync test | Mark the test struct/class `@MainActor` or use `await` |
| Preview renders blank | View depends on async data that never loads | Use mock data with pre-populated state for previews |

---

## Summary Checklist

- [ ] Use `#Preview` macro instead of `PreviewProvider` for all new previews
- [ ] Provide named previews for key states (default, empty, error, loading)
- [ ] Use `@Previewable` for interactive previews (iOS 18+); wrapper views for older targets
- [ ] Supply static `.sample` / `.preview` data on models for previews
- [ ] Inject mock services via protocols for previews that depend on network / data
- [ ] Test `@Observable` model logic with Swift Testing (`@Test`) as the primary strategy
- [ ] Add `.accessibilityIdentifier` to views that need to be found in UI tests
- [ ] Use snapshot tests for complex or layout-critical views
- [ ] Keep snapshots deterministic: fixed data, fixed locale, mocked images
- [ ] Mark test structs `@MainActor` when testing `@MainActor`-isolated models
