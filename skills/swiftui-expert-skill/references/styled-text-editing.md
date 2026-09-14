# Styled Text Editing

> Attributed `TextEditor`, `AttributedTextSelection`, and `AttributedTextFormattingDefinition` require iOS 26, macOS 26, or visionOS 26. `TextEditor` itself is **unavailable on watchOS and tvOS**. For the verbatim-vs-localized decision on `Text`, see `references/text-patterns.md`.

## Table of Contents

- [Attributed TextEditor](#attributed-texteditor)
- [AttributedTextSelection](#attributedtextselection)
- [Reading Attributes at the Selection](#reading-attributes-at-the-selection)
- [Transforming Attributes](#transforming-attributes)
- [Resolving Fonts](#resolving-fonts)
- [Editing Text While Keeping the Selection Valid](#editing-text-while-keeping-the-selection-valid)
- [Formatting Definitions](#formatting-definitions)
- [Text and Markdown](#text-and-markdown)

---

## Attributed TextEditor

`TextEditor` has three initializers. The attributed one accepts an optional selection binding:

```swift
TextEditor(text: Binding<String>)                                  // iOS 14+
TextEditor(text: Binding<String>, selection: Binding<TextSelection?>)   // iOS 18+
TextEditor(text: Binding<AttributedString>, selection: Binding<AttributedTextSelection>? = nil)  // iOS 26+
```

Binding an `AttributedString` gives you a rich-text editor with no extra work — the system handles bold, italic, and the standard formatting commands.

```swift
struct RichTextEditor: View {
    @State private var text = AttributedString("Editable styled text")
    @State private var selection = AttributedTextSelection()

    var body: some View {
        TextEditor(text: $text, selection: $selection)
    }
}
```

Pass a selection binding whenever you need custom formatting controls; without it you cannot read or transform what the person has selected.

## AttributedTextSelection

`AttributedTextSelection` is an opaque `Equatable, Sendable` value. Resolve it against the text to inspect it:

```swift
switch selection.indices(in: text) {
case .insertionPoint(let index):
    // caret only, no characters selected
case .ranges(let rangeSet):
    // one or more selected ranges
}
```

Initializers: `init()`, `init(range:)`, `init(ranges:)`, and `init(insertionPoint:typingAttributes:)`. `affinity(in:)` returns a `TextSelectionAffinity` for the caret's direction.

Because a selection can hold a `RangeSet` (discontiguous ranges), don't assume a single `Range`. Use the provided helpers rather than reaching for the indices directly.

## Reading Attributes at the Selection

`typingAttributes(in:)` returns the `AttributeContainer` that would apply to newly typed text. This is what you want for driving control state, since it works for a bare insertion point as well as a range:

```swift
private var selectionColor: Color {
    selection.typingAttributes(in: text).foregroundColor ?? .primary
}
```

`attributes(in:)` returns a `Sequence` of `AttributeContainer` values covering the selection, with a subscript for a single key. Use it to detect mixed values across a selection:

```swift
let underlines = selection.attributes(in: text)[\.underlineStyle]
let allUnderlined = underlines.allSatisfy { $0 != nil }
```

## Transforming Attributes

`AttributedString.transformAttributes(in:body:)` is the mutating entry point for formatting commands. It takes the selection `inout` and hands you an `inout AttributeContainer` to modify:

```swift
private func toggleUnderline() {
    text.transformAttributes(in: &selection) { container in
        container.underlineStyle = container.underlineStyle == nil ? .single : nil
    }
}

private func setColor(_ color: Color) {
    text.transformAttributes(in: &selection) { container in
        container.foregroundColor = color
    }
}
```

When the selection is an insertion point, the change applies to the typing attributes instead of any characters, so the next typed character picks up the formatting. That is why the selection is `inout` — the transform updates it.

## Resolving Fonts

`Font` values are declarative and may be relative (`.body`, `.headline`), so you cannot read a weight or an italic flag off them directly. Read `\.fontResolutionContext` from the environment (a `Font.Context`) and call `resolve(in:)` to get a `Font.Resolved` with concrete `isBold`, `isItalic`, and `weight`:

```swift
struct FormattingBar: View {
    @Binding var text: AttributedString
    @Binding var selection: AttributedTextSelection
    @Environment(\.fontResolutionContext) private var fontResolutionContext

    var body: some View {
        HStack {
            Button("Bold", systemImage: "bold") { toggleBold() }
            Button("Italic", systemImage: "italic") { toggleItalic() }
        }
    }

    private func toggleBold() {
        text.transformAttributes(in: &selection) { container in
            let font = container.font ?? .default
            let resolved = font.resolve(in: fontResolutionContext)
            container.font = font.bold(!resolved.isBold)
        }
    }

    private func toggleItalic() {
        text.transformAttributes(in: &selection) { container in
            let font = container.font ?? .default
            let resolved = font.resolve(in: fontResolutionContext)
            container.font = font.italic(!resolved.isItalic)
        }
    }
}
```

Note the `?? .default` fallback: an unstyled run has no `font` attribute at all. Resolving the context (rather than assuming `.body`) keeps the toggle correct under Dynamic Type and inherited font modifiers.

## Editing Text While Keeping the Selection Valid

Mutating an `AttributedString` invalidates indices, which can leave a stored selection pointing at the wrong place. Use the selection-aware replacement APIs so SwiftUI updates the selection with the text:

```swift
text.replaceSelection(&selection, with: AttributedString("replacement"))
text.replaceSelection(&selection, withCharacters: "plain replacement")
```

Foundation's `transform(updating:)` accepts attributed-string index ranges, not `AttributedTextSelection`. Use it only after resolving and managing those ranges yourself.

## Formatting Definitions

An `AttributedTextFormattingDefinition` constrains which attribute values an editor accepts, so pasted or system-applied formatting is normalized instead of rejected ad hoc. The protocol has a `Scope` (an `AttributeScope`) and a `body` built from constraints:

```swift
struct BrandFormatting: AttributedTextFormattingDefinition {
    struct Scope: AttributeScope {
        let foregroundColor: AttributeScopes.SwiftUIAttributes.ForegroundColorAttribute
        let font: AttributeScopes.SwiftUIAttributes.FontAttribute
    }

    var body: some AttributedTextFormattingDefinition<Scope> {
        ValueConstraint(for: \.foregroundColor, values: [.primary, .brandRed], default: .primary)
    }
}
```

`ValueConstraint` takes a key path (or attribute type), a `Set` of allowed values, and a default that replaces anything outside the set. Custom constraints conform to `AttributedTextValueConstraint` and implement `constrain(_:)`, which receives a mutable proxy over the attribute container.

Apply a definition with `attributedTextFormattingDefinition(_:)`. Overloads also accept a bare `AttributeScope` type or a `KeyPath<AttributeScopes, S.Type>` when you only want to limit *which* attributes survive:

```swift
TextEditor(text: $text, selection: $selection)
    .attributedTextFormattingDefinition(BrandFormatting())
```

The modifier is `attributedTextFormattingDefinition(_:)` — not `textFormattingDefinition(_:)`.

Attributes outside the scope are dropped from the editor's text, which is the mechanism that keeps a document's attribute set closed. Restricting the scope also means your persistence layer only ever sees attributes you declared.

## Text and Markdown

`Text` accepts Markdown in a localized string literal, but only an inline subset. Interpolating a `String` variable bypasses both localization and Markdown parsing.

```swift
Text("This is **bold** and *italic*")
Text("Visit [Apple](https://www.apple.com)")
```

Supported: emphasis, strong emphasis, strikethrough, inline code, and links. **Not** supported: headings, lists, block quotes, code blocks, tables, images, and hard or soft line breaks — `Text` parses with `inlineOnlyPreservingWhitespace`, so a `#` or `-` renders literally and a newline in the literal is preserved as whitespace rather than becoming a break.

For block-level Markdown, parse it yourself into `AttributedString` with a full `AttributedString.MarkdownParsingOptions` configuration and lay the blocks out as separate views.

For read-only styled content, build an `AttributedString` and hand it to `Text`:

```swift
var styled = AttributedString("Red and Blue")
if let range = styled.range(of: "Red") {
    styled[range].foregroundColor = .red
}
Text(styled)
```

Prefer `foregroundStyle(_:)` over `foregroundColor(_:)` on `Text`; the former accepts any `ShapeStyle`, including gradients and materials.
