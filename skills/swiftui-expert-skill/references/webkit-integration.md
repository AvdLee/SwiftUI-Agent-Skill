# WebKit Integration in SwiftUI

> `WebView` and `WebPage` require iOS 26, macOS 26, or visionOS 26 and are **unavailable on watchOS and tvOS**. A few members require the aligned 27 releases; those are called out inline. Both types are `@MainActor`.

## Table of Contents

- [WebView](#webview)
- [WebPage](#webpage)
- [Configuration and Data Stores](#configuration-and-data-stores)
- [Loading Content](#loading-content)
- [Observing Navigation](#observing-navigation)
- [Deciding Navigation Policy](#deciding-navigation-policy)
- [Calling JavaScript](#calling-javascript)
- [Find Navigator](#find-navigator)
- [View Modifiers](#view-modifiers)
- [Exporting PDF and Images](#exporting-pdf-and-images)
- [Custom URL Schemes](#custom-url-schemes)

---

## WebView

`WebView` has two initializers: one for a bare URL, one backed by a `WebPage`.

```swift
import SwiftUI
import WebKit

WebView(url: URL(string: "https://www.swift.org"))
```

`WebView(url:)` is enough for read-only display; the view reloads when the URL changes. Use the `WebPage` initializer when you need the page's title, loading state, back-forward list, JavaScript, or navigation policy.

## WebPage

`WebPage` is an observable `@MainActor` class that owns the web content. Because it is observable, reading its properties in a `body` re-renders automatically.

```swift
struct BrowserView: View {
    @State private var page = WebPage()

    var body: some View {
        NavigationStack {
            WebView(page)
                .navigationTitle(page.title)
        }
        .onAppear {
            _ = page.load(URL(string: "https://www.apple.com"))
        }
    }
}
```

Observable properties include `url`, `title` (a non-optional `String`), `isLoading`, `estimatedProgress`, `backForwardList`, `serverTrust`, and `customUserAgent`. Note that `title` is not optional — don't write `if let title = page.title`.

```swift
ProgressView(value: page.estimatedProgress)
    .opacity(page.isLoading ? 1 : 0)
```

## Configuration and Data Stores

`WebPage.Configuration` is a value type applied at initialization; changing it afterwards has no effect on an existing page.

```swift
var configuration = WebPage.Configuration()
configuration.loadsSubresources = true
configuration.defaultNavigationPreferences.allowsContentJavaScript = true
configuration.websiteDataStore = .nonPersistent()

let page = WebPage(configuration: configuration)
```

`websiteDataStore` is a `WKWebsiteDataStore`. Use `.default()` to share cookies and caches with other pages in the app, or `.nonPersistent()` for private browsing where nothing survives the session. `defaultNavigationPreferences` supplies the baseline `NavigationPreferences` (JavaScript, `ContentMode`) for every navigation; a `NavigationDeciding` can override it per navigation.

Set `page.customUserAgent` on the page itself, not the configuration.

## Loading Content

Every `load` overload returns an `AsyncSequence` of `WebPage.NavigationEvent` values, so you can iterate it to follow that specific navigation — or bind it to `_` when you don't care.

```swift
_ = page.load(URLRequest(url: url))
_ = page.load(html: "<h1>Hello</h1>", baseURL: URL(string: "https://example.com")!)
_ = page.load(data, mimeType: "text/html", characterEncoding: .utf8, baseURL: baseURL)
_ = page.load(simulatedRequest: request, responseHTML: html)
_ = page.reload(fromOrigin: false)
page.stopLoading()
```

`baseURL` resolves relative links and determines the origin for HTML and `Data` loads. Back-forward navigation loads an item from the list:

```swift
if let backItem = page.backForwardList.backItem {
    _ = page.load(backItem)
}
```

## Observing Navigation

`page.navigations` is an `AsyncSequence` of `NavigationEvent` covering all navigations; the per-call sequence returned by `load` covers just that one. Cases are `.startedProvisionalNavigation`, `.receivedServerRedirect`, `.committed`, and `.finished`. Failures surface as thrown `WebPage.NavigationError` values (`.failedProvisionalNavigation`, `.pageClosed`, `.webContentProcessTerminated`, `.invalidURL`).

```swift
.task {
    do {
        for try await event in page.navigations {
            if event == .finished { await indexPage() }
        }
    } catch {
        // handle NavigationError
    }
}
```

For simple loading indicators, prefer the observable `page.isLoading` and `page.estimatedProgress` over consuming the event stream.

## Deciding Navigation Policy

Conform a type to `WebPage.NavigationDeciding` and pass it to the initializer. Every requirement has a default implementation, so implement only what you need.

```swift
struct LinkPolicy: WebPage.NavigationDeciding {
    func decidePolicy(
        for action: WebPage.NavigationAction,
        preferences: inout WebPage.NavigationPreferences
    ) async -> WKNavigationActionPolicy {
        guard action.request.url?.host() != "blocked.example.com" else { return .cancel }
        preferences.allowsContentJavaScript = true
        return .allow
    }

    func decidePolicy(
        for response: WebPage.NavigationResponse
    ) async -> WKNavigationResponsePolicy {
        (response.response as? HTTPURLResponse)?.statusCode == 200 ? .allow : .cancel
    }
}

let page = WebPage(navigationDecider: LinkPolicy())
```

`decideAuthenticationChallengeDisposition(for:)` handles `URLAuthenticationChallenge`, and `willSubmit(formInfo:)` (iOS/macOS/visionOS 27+) observes form submissions. A separate `dialogPresenter:` parameter takes a `WebPage.DialogPresenting` type for JavaScript alerts, confirms, and prompts.

## Calling JavaScript

```swift
let result = try await page.callJavaScript(
    """
    const meta = document.querySelector('meta[name="description"]');
    return meta ? meta.getAttribute('content') : '';
    """
)
let description = result as? String
```

`callJavaScript(_:arguments:in:contentWorld:)` takes a **function body**, so use `return` to produce a value. `arguments` is a `[String: Any]` dictionary whose keys become in-scope variables — pass values that way instead of interpolating strings. `in:` targets a `WebPage.FrameInfo`; `contentWorld:` takes a `WKContentWorld` (`.page`, `.defaultClient`, or a custom world) to isolate your script's globals from the page's own.

## Find Navigator

`WebView` participates in the standard SwiftUI find navigator:

```swift
WebView(page)
    .findNavigator(isPresented: $isSearching)
```

## View Modifiers

Applied to the `WebView`:

| Modifier | Purpose |
|---|---|
| `webViewBackForwardNavigationGestures(_:)` | `.automatic` / `.enabled` / `.disabled` swipe navigation |
| `webViewMagnificationGestures(_:)` | Pinch-to-zoom behavior |
| `webViewLinkPreviews(_:)` | Long-press / force-touch link previews |
| `webViewTextSelection(_:)` | Takes a `TextSelectability`, e.g. `.enabled` |
| `webViewElementFullscreenBehavior(_:)` | Allows HTML element fullscreen |
| `webViewContentBackground(_:)` | Takes a `Visibility` — hide it to show your own background behind the page |
| `webViewContextMenu(menu:)` | macOS only. Builds a menu from a `WebView.ActivatedElementInfo` (its `linkURL`). |
| `webViewScrollPosition(_:)` | Binds a `ScrollPosition` |
| `webViewOnScrollGeometryChange(for:of:action:)` | Observes `ScrollGeometry` changes |
| `webViewScrollInputBehavior(_:for:)` | Enables or disables a `ScrollInputKind` |

On macOS:

```swift
WebView(page)
    .webViewContentBackground(.hidden)
    .background(.regularMaterial)
    .webViewContextMenu { element in
        if let url = element.linkURL {
            ShareLink(item: url)
        }
    }
```

## Exporting PDF and Images

`WebPage` conforms to `Transferable`, so it can be dragged or shared directly. For explicit exports, call `exported(as:)` with a `WebPage.ExportedContentConfiguration`:

```swift
let pdf = try await page.exported(as: .pdf(region: .contents))
let png = try await page.exported(as: .image(region: .rect(bounds), snapshotWidth: 1024))
```

`Region` is either `.contents` or `.rect(_:)`, and both factories accept `allowTransparentBackground`. Both calls return `Data`.

`WebPage` has no web-archive API. Web archives remain a `WKWebView` API (`createWebArchiveData(completionHandler:)`), so reach for `WKWebView` in a representable only when you specifically need `.webarchive` output.

## Custom URL Schemes

`URLSchemeHandler` replies with an `AsyncSequence` of `URLSchemeTaskResult` values — first a `.response`, then one or more `.data` elements. Register handlers in the configuration's `urlSchemeHandlers` dictionary keyed by `URLScheme`.

```swift
struct AssetSchemeHandler: URLSchemeHandler {
    func reply(for request: URLRequest) -> AsyncThrowingStream<URLSchemeTaskResult, any Error> {
        AsyncThrowingStream { continuation in
            guard let url = request.url else {
                continuation.finish(throwing: URLError(.badURL))
                return
            }
            let html = "<h1>\(url.path())</h1>"
            continuation.yield(.response(URLResponse(
                url: url,
                mimeType: "text/html",
                expectedContentLength: -1,
                textEncodingName: "utf-8"
            )))
            continuation.yield(.data(Data(html.utf8)))
            continuation.finish()
        }
    }
}

var configuration = WebPage.Configuration()
if let scheme = URLScheme("myapp") {
    configuration.urlSchemeHandlers[scheme] = AssetSchemeHandler()
}
let page = WebPage(configuration: configuration)
```

`URLScheme(_:)` is failable — the system rejects reserved schemes such as `http` and `https`. Cancellation is expressed by terminating the returned sequence, so honor `Task` cancellation inside it rather than implementing a separate stop callback.
