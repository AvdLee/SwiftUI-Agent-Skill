# Document-Based Apps (SDK 27+)

> The `Document` protocol family replaces `FileDocument` / `ReferenceFileDocument` for new code on iOS 27, macOS 27, and visionOS 27. **Unavailable on watchOS and tvOS.** For older deployment targets, see the `FileDocument` section in `references/macos-scenes.md`.

## Table of Contents

- [Protocol Map](#protocol-map)
- [Read and Write Flow](#read-and-write-flow)
- [Flat-File Document](#flat-file-document)
- [Undo Registration Is Required for Autosave](#undo-registration-is-required-for-autosave)
- [DocumentGroup and Launch Scenes](#documentgroup-and-launch-scenes)
- [Custom Readers and Writers](#custom-readers-and-writers-direct-url-access)
- [Package Documents](#package-documents)
- [Progress Reporting](#progress-reporting-with-subprogress)
- [Coordinated Access Outside Read/Write](#coordinated-access-outside-readwrite)
- [Export](#export)
- [Migrating from FileDocument](#migrating-from-filedocument)
- [Content Types](#content-types)
- [Troubleshooting Checklist](#troubleshooting-checklist)

---

## Protocol Map

| Symbol | Role |
|---|---|
| `ReadableDocument` | Read-only. Requires `readableContentTypes`, `reader(configuration:)`, `apply(snapshot:previous:)`. |
| `WritableDocument` | Saving. Requires `writer(configuration:)` and `snapshot(contentType:)`; `writableContentTypes` defaults to `readableContentTypes` when both protocols are adopted. |
| `Document` | `ReadableDocument & WritableDocument`, no requirements of its own. |
| `DocumentReader` | `@concurrent func read(from:progress:) async throws -> sending Snapshot` |
| `DocumentWriter` | `@concurrent func write(snapshot:to:previous:progress:) async throws` |
| `FileWrapperDocumentReader<Snapshot>` | Convenience reader; closure `(FileWrapper) async throws -> sending Snapshot`. |
| `FileWrapperDocumentWriter<Snapshot>` | Convenience writer; closure `(Snapshot, FileWrapper?) async throws -> FileWrapper`. |
| `URLDocumentConfiguration` | `@MainActor @Observable`. `fileURL`, `lastContentModificationDate`, `makeFileCoordinator()`. |
| `DocumentCreationContext` | `creationSource: DocumentCreationSource?`. |

Documents are `AnyObject`-constrained, so a document is a class. Mark it `@Observable` so SwiftUI tracks individual property changes instead of recreating the model.

A **snapshot** is the document's state at one moment. It can be any type — `String`, a struct, or the document itself — and reading and writing may use different snapshot types. Keep snapshot, reader, and writer types at `internal` access; protocol requirements expose them in signatures, so `private` or `fileprivate` fails to compile.

## Read and Write Flow

**Open:** `reader(configuration:)` → `read(from:progress:)` in the background → `apply(snapshot:previous:)` on the main actor.

**Save:** `snapshot(contentType:)` on the main actor → `writer(configuration:)` → `write(snapshot:to:previous:progress:)` in the background with coordinated file access.

`snapshot(contentType:)` and `apply(snapshot:previous:)` are `@MainActor async throws` — keep them cheap and serialize inside `read(…)` / `write(…)`. Inside those methods, use the `source` / `destination` parameter rather than `configuration.fileURL`; the framework hands you the URL for *this* operation, which is not necessarily the document's URL.

## Flat-File Document

`FileWrapperDocumentReader` and `FileWrapperDocumentWriter` handle file coordination for you. `readableContentTypes` drives the document browser; `writableContentTypes` drives the save panel.

```swift
@Observable
final class TextDocument: Document {
    static let readableContentTypes = [UTType.plainText]

    var text: String = ""

    func reader(configuration: sending ReadConfiguration) -> sending FileWrapperDocumentReader<String> {
        FileWrapperDocumentReader(configuration) { fileWrapper in
            guard let data = fileWrapper.regularFileContents else {
                throw CocoaError(.fileReadCorruptFile)
            }
            return String(decoding: data, as: UTF8.self)
        }
    }

    func writer(configuration: sending WriteConfiguration) -> sending FileWrapperDocumentWriter<String> {
        FileWrapperDocumentWriter(configuration) { snapshot, previous in
            FileWrapper(regularFileWithContents: Data(snapshot.utf8))
        }
    }

    @MainActor
    func snapshot(contentType: UTType) async throws -> sending String { text }

    @MainActor
    func apply(snapshot: sending String, previous: sending String?) async throws {
        text = snapshot
    }
}
```

## Undo Registration Is Required for Autosave

SwiftUI detects unsaved changes through the undo stack. **Without registered undo actions, autosave never runs.** Read `\.undoManager` from the environment and register an undo action for every change:

```swift
struct TextDocumentView: View {
    @Bindable var document: TextDocument
    @Environment(\.undoManager) private var undoManager

    var body: some View {
        TextEditor(text: $document.text)
            .onChange(of: document.text) { oldValue, _ in
                undoManager?.registerUndo(withTarget: document) { document in
                    document.text = oldValue
                }
            }
    }
}
```

Registering with `withTarget: document` gives redo for free — SwiftUI replays the same closure with the restored value.

When autosave fails, route the investigation here first: confirm the app uses `DocumentGroup` as its first scene, verify every user-visible mutation registers undo through the environment manager, and test that undo and redo actually restore model values. Do not start by adding manual save calls; they bypass the change-tracking contract instead of repairing it.

## DocumentGroup and Launch Scenes

`DocumentGroup` (or `DocumentGroupLaunchScene`) must be the app's first scene to opt into autosave, file coordination, file dialogs, undo management, and conflict resolution. On iOS, set `UISupportsDocumentBrowser` to `YES` to present a document browser.

```swift
DocumentGroup { document in
    TextDocumentView(document: document)
} makeDocument: { configuration, context in
    TextDocument()
}
```

Read-only apps conform only to `ReadableDocument` and use `viewer:` / `makeReadableDocument:`, with `CFBundleTypeRole` set to `Viewer` instead of `Editor`.

`makeDocument` is `async` and runs on the main actor, so you can suspend it to show a template picker or import preview before the document appears; throw `CancellationError` to cancel. On macOS and visionOS, drive that from a separate `Window` scene via a stored `CheckedContinuation`; on iOS, present a `.sheet` from a `NewDocumentButton`.

`DocumentGroupLaunchScene` (iOS/visionOS) hosts `NewDocumentButton`s, each carrying a `DocumentCreationSource`. Read `context.creationSource` in `makeDocument` to configure the new document:

```swift
DocumentGroupLaunchScene("My Notes") {
    NewDocumentButton("New Note", source: .note)
    NewDocumentButton("New List", source: .list)
} background: {
    Color.accentColor.gradient
}

extension DocumentCreationSource {
    static let note = DocumentCreationSource(id: "note")
}
```

## Custom Readers and Writers (Direct URL Access)

Implement `DocumentReader` / `DocumentWriter` directly when you need streaming, custom write logic, or a file URL for frameworks such as Core Graphics, AVFoundation, or PDFKit. Their `Source` and `Destination` associated types default to `URL`; specialize them only when the backing store requires another type.

Those associated-type defaults do not make every source or destination compatible with SwiftUI scenes. Public `DocumentGroup` initializers constrain a reader's `Source` and a writer's `Destination` to `URL`, and `fileExporter` constrains the writer destination to `URL`. A custom non-URL reader or writer can still be useful in another pipeline, but it cannot be passed directly to these APIs. Do not respond to the resulting generic-constraint error by force-casting; keep a URL-facing adapter or choose a URL-based implementation.

```swift
struct Reader: DocumentReader {
    @concurrent
    func read(from source: URL, progress: consuming Subprogress) async throws -> sending ImageSnapshot {
        guard let imageSource = CGImageSourceCreateWithURL(source as CFURL, nil),
              let image = CGImageSourceCreateImageAtIndex(imageSource, 0, nil) else {
            throw CocoaError(.fileReadCorruptFile)
        }
        return ImageSnapshot(image: image)
    }
}
```

The writer's `previous` parameter holds the last successfully written snapshot; ignoring it and rewriting everything is the simplest correct behavior.

## Package Documents

A package is a directory the system presents as one item. `FileWrapperDocumentReader` / `FileWrapperDocumentWriter` work here too: read children from `directory.fileWrappers`, and build a fresh `FileWrapper(directoryWithFileWrappers:)` with `preferredFilename` set on each child when writing.

Rewriting the whole package on every save is the default recommendation. `FileWrapper` loads contents **on demand**, so a child can be gone by the time you call `regularFileContents` — always handle errors when reading children.

Incremental writes are worth it only against a measured problem. The pattern: carry a per-child `isChanged` flag, reuse the previous `FileWrapper` from the writer closure's second parameter, replace only changed children, remove children no longer listed in your metadata, and clear the flags in `snapshot(contentType:)`.

## Progress Reporting with `Subprogress`

Custom readers and writers receive a `Subprogress` (Foundation). The `FileWrapper` convenience closures do **not**. `Subprogress` is `~Copyable`, so the compiler enforces single use; unconsumed units auto-complete.

```swift
let progressManager = progress.start(totalCount: 2)
let data = try Data(contentsOf: source)
progressManager.complete(count: 1)
let image = try decodeImage(from: data)
progressManager.complete(count: 1)
```

Pick a coarse `totalCount` — chunks or files, not bytes. SwiftUI decides case by case whether to show an indicator.

## Coordinated Access Outside Read/Write

SwiftUI coordinates `read` and `write` for you. For any other disk access — loading one file from a package on tap, for instance — retain the `URLDocumentConfiguration` passed to `makeDocument`, call `makeFileCoordinator()` on it for each operation, then use `coordinate(readingItemAt:options:error:)` (or the writing variant) and check the `NSError` out-parameter. Skipping coordination risks corruption when another process edits the same document.

## Export

Export to another location or format with `fileExporter(isPresented:document:contentType:defaultFilename:onCompletion:)`, passing the `WritableDocument` itself. Its writer destination is constrained to `URL`, even though `DocumentWriter.Destination` has a general associated-type default.

## Migrating from FileDocument

| Before | After |
|---|---|
| `FileDocument` struct / `ReferenceFileDocument` class | `@Observable final class` conforming to `Document` |
| `init(configuration:)` | `DocumentReader` + `apply(snapshot:previous:)` |
| `fileWrapper(configuration:)` | `DocumentWriter` + `snapshot(contentType:)` |
| `DocumentGroup(newDocument:editor:)` | `DocumentGroup { editor } makeDocument: { configuration, context in }` |
| Single `Snapshot` type | Separate read and write snapshot types |
| Change tracked by value comparison | Undo registration required |

`FileDocument`, `ReferenceFileDocument`, and their `DocumentGroup(newDocument:)` APIs are soft-deprecated in the SDK 27 toolchain. They remain the compatible option for deployment targets below the aligned 27 releases; follow `references/soft-deprecation.md` when deciding whether migration belongs in the current task. When migrating a `ReferenceFileDocument`, drop `ObservableObject` and `@Published` rather than layering `@Observable` on top.

## Content Types

Built-in formats need no custom type (`UTType.plainText`, `.jpeg`, `.pdf`). Mirror a custom document type in code:

```swift
extension UTType {
    static let notebook = UTType(exportedAs: "com.mycompany.notebook")
}
```

Use `static let` for exported types and `static var` for `UTType(importedAs:)` types. Custom identifiers use lowercase reverse-DNS syntax. Flat files conform to `public.data`; packages conform to `com.apple.package`.

For a custom-type migration, keep these declarations aligned:

- `UTExportedTypeDeclarations` for a format the app owns, or `UTImportedTypeDeclarations` for another owner's format, including `UTTypeConformsTo` and a `public.filename-extension` tag.
- `CFBundleDocumentTypes` with the same identifier in `LSItemContentTypes`, plus `CFBundleTypeRole` (`Editor` or `Viewer`) and an appropriate `LSHandlerRank`.
- The code-level `UTType` identifier and `readableContentTypes` / `writableContentTypes`.

If files are unavailable, grayed out, treated as folders, or open read-only after a migration, compare those identifiers character-for-character and verify the conformance chain. Use `uttype --verbose <identifier>` and `uttype --conformsto public.data <identifier>` for flat files, or `com.apple.package` for packages. Do not change document model code until registration and conformance are known to be correct.

## Troubleshooting Checklist

- [ ] Autosave failures are checked for a first-scene `DocumentGroup`, undo registration for every mutation, and working undo/redo
- [ ] `snapshot(contentType:)` and `apply(snapshot:previous:)` stay cheap on the main actor; serialization remains in async reader/writer work
- [ ] `DocumentGroup` reader sources and writer destinations are `URL`
- [ ] `fileExporter` uses a writer whose destination is `URL`
- [ ] Custom UTType identifiers match across code, type declarations, `LSItemContentTypes`, and document content-type arrays
- [ ] Flat-file types conform to `public.data`; package types conform to `com.apple.package`
- [ ] `FileDocument` and `ReferenceFileDocument` migrations preserve the soft-deprecation and deployment-target fallback guidance
