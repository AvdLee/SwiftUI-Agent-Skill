# SDK 27 AsyncImage

For phase handling, placeholders, decoding, and downsampling, consult `references/image-optimization.md`.

On aligned 27 runtimes, `AsyncImage(url:)` uses standard HTTP caching according to response headers without code changes. The runtime behavior also benefits apps built with an older SDK.

Do not add custom caching merely to obtain that default behavior. If images still reload, first check the server's cache headers.

## Request and Session Control

SDK 27 adds:

- `AsyncImage(request:)` overloads for a per-image `URLRequest`, including its cache policy
- `asyncImageURLSession(_:)` to provide a configured `URLSession` and `URLCache` to a subtree

```swift
AsyncImage(
    request: URLRequest(
        url: imageURL,
        cachePolicy: .returnCacheDataElseLoad
    )
)
.asyncImageURLSession(imageSession)
```

The new initializer and modifier require the aligned OS 27 releases. Gate them for older deployment targets and retain `AsyncImage(url:)` as the fallback.
