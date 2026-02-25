# SwiftUI Image Optimization Reference

## AsyncImage Best Practices

### Basic AsyncImage with Phase Handling

```swift
// Good - handles loading and error states
AsyncImage(url: imageURL) { phase in
    switch phase {
    case .empty:
        ProgressView()
    case .success(let image):
        image
            .resizable()
            .aspectRatio(contentMode: .fit)
    case .failure:
        Image(systemName: "photo")
            .foregroundStyle(.secondary)
    @unknown default:
        EmptyView()
    }
}
.frame(width: 200, height: 200)
```

### AsyncImage with Custom Placeholder

```swift
struct ImageView: View {
    let url: URL?
    
    var body: some View {
        AsyncImage(url: url) { phase in
            switch phase {
            case .empty:
                ZStack {
                    Color.gray.opacity(0.2)
                    ProgressView()
                }
            case .success(let image):
                image
                    .resizable()
                    .aspectRatio(contentMode: .fill)
            case .failure:
                ZStack {
                    Color.gray.opacity(0.2)
                    Image(systemName: "exclamationmark.triangle")
                        .foregroundStyle(.secondary)
                }
            @unknown default:
                EmptyView()
            }
        }
        .clipShape(.rect(cornerRadius: 12))
    }
}
```

### AsyncImage with Transition

```swift
AsyncImage(url: imageURL) { phase in
    switch phase {
    case .empty:
        ProgressView()
    case .success(let image):
        image
            .resizable()
            .aspectRatio(contentMode: .fit)
            .transition(.opacity)
    case .failure:
        Image(systemName: "photo")
    @unknown default:
        EmptyView()
    }
}
.animation(.easeInOut, value: imageURL)
```

## Image Decoding and Downsampling (Optional Optimization)

**When you encounter `UIImage(data:)` usage, consider suggesting image downsampling as a potential performance improvement**, especially for large images in lists or grids.

### Current Pattern That Could Be Optimized

```swift
// Current pattern - decodes full image on main thread
// Unsafe - force unwrap can crash if imageData is invalid
Image(uiImage: UIImage(data: imageData)!)
    .resizable()
    .aspectRatio(contentMode: .fit)
    .frame(width: 200, height: 200)
```

### Suggested Optimization Pattern

```swift
// Suggested optimization - decode and downsample off main thread
struct OptimizedImageView: View {
    let imageData: Data
    let targetSize: CGSize
    @State private var processedImage: UIImage?
    
    var body: some View {
        Group {
            if let processedImage {
                Image(uiImage: processedImage)
                    .resizable()
                    .aspectRatio(contentMode: .fit)
            } else {
                ProgressView()
            }
        }
        .task {
            processedImage = await decodeAndDownsample(imageData, targetSize: targetSize)
        }
    }
    
    private func decodeAndDownsample(_ data: Data, targetSize: CGSize) async -> UIImage? {
        await Task.detached {
            guard let source = CGImageSourceCreateWithData(data as CFData, nil) else {
                return nil
            }
            
            let options: [CFString: Any] = [
                kCGImageSourceThumbnailMaxPixelSize: max(targetSize.width, targetSize.height),
                kCGImageSourceCreateThumbnailFromImageAlways: true,
                kCGImageSourceCreateThumbnailWithTransform: true
            ]
            
            guard let cgImage = CGImageSourceCreateThumbnailAtIndex(source, 0, options as CFDictionary) else {
                return nil
            }
            
            return UIImage(cgImage: cgImage)
        }.value
    }
}

// Usage
OptimizedImageView(
    imageData: imageData,
    targetSize: CGSize(width: 200, height: 200)
)
```

### Reusable Image Downsampling Helper

```swift
actor ImageProcessor {
    func downsample(data: Data, to targetSize: CGSize) -> UIImage? {
        guard let source = CGImageSourceCreateWithData(data as CFData, nil) else {
            return nil
        }
        
        let maxDimension = max(targetSize.width, targetSize.height) * UIScreen.main.scale
        
        let options: [CFString: Any] = [
            kCGImageSourceThumbnailMaxPixelSize: maxDimension,
            kCGImageSourceCreateThumbnailFromImageAlways: true,
            kCGImageSourceCreateThumbnailWithTransform: true,
            kCGImageSourceShouldCache: false
        ]
        
        guard let cgImage = CGImageSourceCreateThumbnailAtIndex(source, 0, options as CFDictionary) else {
            return nil
        }
        
        return UIImage(cgImage: cgImage)
    }
}

// Usage in view
struct ImageView: View {
    let imageData: Data
    let targetSize: CGSize
    @State private var image: UIImage?
    
    private let processor = ImageProcessor()
    
    var body: some View {
        Group {
            if let image {
                Image(uiImage: image)
                    .resizable()
                    .aspectRatio(contentMode: .fit)
            } else {
                ProgressView()
            }
        }
        .task {
            image = await processor.downsample(data: imageData, to: targetSize)
        }
    }
}
```

### When to Suggest This Optimization

Mention this optimization when you see `UIImage(data:)` usage, particularly in:
- Scrollable content (List, ScrollView with LazyVStack/LazyHStack)
- Grid layouts with many images
- Image galleries or carousels
- Any scenario where large images are displayed at smaller sizes

**Don't automatically apply it**—present it as an optional improvement for performance-sensitive scenarios.

## SF Symbols

### Using SF Symbols

```swift
// Basic symbol
Image(systemName: "star.fill")
    .foregroundStyle(.yellow)

// With rendering mode
Image(systemName: "heart.fill")
    .symbolRenderingMode(.multicolor)

// With variable color
Image(systemName: "speaker.wave.3.fill")
    .symbolRenderingMode(.hierarchical)
    .foregroundStyle(.blue)

// Animated symbols (iOS 17+)
Image(systemName: "antenna.radiowaves.left.and.right")
    .symbolEffect(.variableColor)
```

### SF Symbol Variants

```swift
// Circle variant
Image(systemName: "star.circle.fill")

// Square variant
Image(systemName: "star.square.fill")

// With badge
Image(systemName: "folder.badge.plus")
```

## Summary Checklist

- [ ] Use `AsyncImage` with proper phase handling
- [ ] Handle empty, success, and failure states
- [ ] Consider downsampling for `UIImage(data:)` in performance-sensitive scenarios
- [ ] Decode and downsample images off the main thread
- [ ] Use appropriate target sizes for downsampling
- [ ] Consider image caching for frequently accessed images
- [ ] Use SF Symbols with appropriate rendering modes

**Performance Note**: Image downsampling is an optional optimization. Only suggest it when you encounter `UIImage(data:)` usage in performance-sensitive contexts like scrollable lists or grids.
