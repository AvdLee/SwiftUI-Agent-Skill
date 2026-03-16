# SwiftUI Canvas and GraphicsContext Reference

## Table of Contents

- [Overview](#overview)
- [Performance Optimization](#performance-optimization)
- [Using Symbols](#using-symbols)
- [GraphicsContext State](#graphicscontext-state)
- [Best Practices](#best-practices)
- [Summary Checklist](#summary-checklist)

## Overview

`Canvas` provides an immediate mode 2D drawing environment in SwiftUI, passing a `GraphicsContext` to its renderer closure. It is ideal for complex, dynamic graphics that don't require individual element interactivity or accessibility.

```swift
Canvas { context, size in
    context.fill(
        Path(ellipseIn: CGRect(origin: .zero, size: size)),
        with: .color(.blue))
}
.frame(width: 200, height: 200)
```

## Performance Optimization

### 1. Opaque Canvas

If your drawing doesn't require transparency, set `opaque` to `true`. This allows the system to optimize rendering by skipping alpha blending.

```swift
// GOOD - optimized for non-transparent backgrounds
Canvas(opaque: true) { context, size in
    context.fill(Path(CGRect(origin: .zero, size: size)), with: .color(.white))
    // ... drawing commands
}
```

### 2. Asynchronous Rendering

For complex drawings that might block the main thread, enable `rendersAsynchronously`. This allows the canvas to present its contents in a non-blocking manner.

```swift
// GOOD - prevents main thread stalls for complex graphics
Canvas(rendersAsynchronously: true) { context, size in
    // Expensive drawing operations
}
```

### 3. Path Caching

Avoid recreating complex paths inside the renderer closure if they don't change. While `Canvas` is immediate mode, pre-calculating paths outside the renderer can save CPU cycles.

```swift
// BAD - recreating path every frame
Canvas { context, size in
    let path = Path { p in /* complex path construction */ }
    context.fill(path, with: .color(.red))
}

// GOOD - pre-calculating or caching path
let cachedPath = Path { p in /* complex path construction */ }
Canvas { context, size in
    context.fill(cachedPath, with: .color(.red))
}
```

## Using Symbols

Symbols allow you to reuse SwiftUI views as drawing elements within a `Canvas`. This is more efficient than drawing complex shapes manually when those shapes can be represented as views.

```swift
Canvas { context, size in
    if let mark = context.resolveSymbol(id: "mark") {
        context.draw(mark, at: CGPoint(x: size.width / 2, y: size.height / 2))
    }
} symbols: {
    Circle()
        .fill(.red)
        .frame(width: 20, height: 20)
        .tag("mark")
}
```

**Note**: Views passed as symbols lose their interactivity and accessibility within the `Canvas`.

## GraphicsContext State

`GraphicsContext` is a value type. To perform independent operations like clipping or transforms without affecting the rest of the drawing, create a copy of the context.

```swift
Canvas { context, size in
    // Create a copy for a specific operation
    var maskedContext = context
    maskedContext.clip(to: Path(CGRect(x: 0, y: 0, width: 50, height: 50)))
    maskedContext.fill(Path(Circle(in: CGRect(origin: .zero, size: size))), with: .color(.green))

    // Original context remains unaffected
    context.fill(Path(CGRect(x: 60, y: 60, width: 40, height: 40)), with: .color(.blue))
}
```

## Best Practices

- **Use Canvas for Performance**: Prefer `Canvas` over many individual `Shape` views when drawing hundreds or thousands of elements (e.g., particle systems, complex charts).
- **Avoid Interactivity**: Do not use `Canvas` if you need users to interact with individual drawn elements. Use standard SwiftUI views instead.
- **Accessibility**: `Canvas` is treated as a single image by accessibility tools. Provide a high-level `accessibilityLabel` for the entire `Canvas` rather than trying to make internal elements accessible.
- **Coordinate System**: `Canvas` uses a standard 2D coordinate system where `(0,0)` is the top-left corner. Use the `size` parameter to make your drawing responsive.

## Summary Checklist

- [ ] Use `opaque: true` if no transparency is needed
- [ ] Enable `rendersAsynchronously: true` for complex, expensive drawings
- [ ] Use `symbols` to reuse SwiftUI views as drawing elements
- [ ] Copy `GraphicsContext` for independent state changes (clipping, transforms)
- [ ] Pre-calculate or cache complex paths outside the renderer when possible
- [ ] Provide a high-level `accessibilityLabel` for the entire `Canvas`
- [ ] Use `Canvas` only when individual element interactivity is not required
