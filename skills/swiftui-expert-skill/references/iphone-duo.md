# iPhone Duo SwiftUI Guidance

> iPhone Duo support in Xcode 27.1 and the iOS 27.1 SDK is beta. Confirm behavior against the shipping SDK.

## Displays and Continuity

iPhone Duo has an outer display and a larger inner display. The outer display uses the familiar compact-horizontal, regular-vertical iPhone context in portrait; the inner display can provide regular width and height, including sidebar and multi-column presentations. Use the current proposal and size classes, not a device check, orientation, fixed breakpoint, or global screen.

Opening, closing, rotating, partially folding, Split View multitasking, and pinned video all resize the same app experience. Preserve navigation state, content hierarchy, and functionality across those transitions. Do not make a feature available only in one pose or prescribe a bespoke layout for every pose. Generic resizability, safe-area, and display-scale rules remain canonical in [layout-best-practices.md](layout-best-practices.md) and [image-optimization.md](image-optimization.md).

Hardware placement is asymmetric. The outer and inner cameras occupy different positions, and system controls can use a vertical bar on a hardware-aligned side. Never assume opposite safe-area or margin values are equal. Let standard SwiftUI containers and directional safe areas place foreground controls; full-bleed visual backgrounds can extend behind them. See [toolbar-patterns.md](toolbar-patterns.md) for vertical-bar APIs.

## Choose the Technique by Screen Structure

Classify the screen by its structure before choosing any fold technique; reaching for `ArrangementView` or `reservedRegions` first tends to misread the screen. Check in this order:

1. **Rows push further screens** (settings, mailboxes, folders; even a short list): `NavigationSplitView`. It collapses on compact width, splits evenly along a fold, and scales to iPad and resizable windows with no Duo-specific code. A screen whose rows are `NavigationLink`s is this case. Details in [sheet-navigation-patterns.md](sheet-navigation-patterns.md#large-displays).
2. **Cards or a feed in one `ScrollView`** (dashboards, collection grids): reflow into two columns with a custom `Layout`, with the gutter over a vertical fold. Do not split at a horizontal fold. See [two-column reflow](layout-best-practices.md#two-column-reflow-for-card-screens).
3. **Two peer regions without navigation** (media and controls, visual and copy): `ArrangementView` with `.split`, outside any scroll view.
4. **Content plus a supplementary queue or panel**: consider the compact pattern, a persistent bar that pushes the full view (like the Music mini player), instead of a side column. If `.inspector` is used, attach it around the `NavigationStack`, not to a pushed screen; in Xcode 27.1, an inspector on a pushed screen that hosted its own `NavigationStack` broke pushes, and full-bleed content laid out underneath the inspector column.
5. **Custom edge-to-edge chrome only**: read `reservedRegions` directly.

In a portrait-only iPhone app, regular width effectively means the inner display, and the inner display ignores supported orientations, so it can still be landscape.

## Fold and Camera Regions

The outer camera always shapes the outer-display area; standard safe areas and bars account for it. On the inner display, an active fold is represented as a `.division` reserved region because it separates the available area. The active FaceTime camera is an `.occlusion` region because it covers a smaller frame. Inner regions can change activity as the device pose and camera use change.

System components (`NavigationStack`, `NavigationSplitView`, `TabView`, sheets, alerts, menus, `List`, `ScrollView`) already adapt around the fold and system UI. Do not displace continuously scrolling articles, feeds, documents, or lists merely because a fold exists; scrolling already preserves continuity. Pick the technique with the structure list above, then see [`ArrangementView`](layout-best-practices.md#two-region-arrangements-ios-271) and [reserved-region](layout-best-practices.md#reserved-regions-ios-271) details.

## Duo Displacement Heuristics

Displacement means moving or resizing the same element around a reserved region, not creating a pose-specific feature. Keep related elements together, move the smallest coherent group, and avoid large jumps that weaken their visual relationship.

When a partially folded book-like pose requires displacement, a trailing region supports continuity as the device closes toward the outer display. In a table-like pose, the upper region suits content viewed at a distance and the lower stable region suits touch controls. Treat these as heuristics after purpose, reachability, and context, not as pose detection rules. Keep the same controls and general hierarchy everywhere.

## Hinge Effects, Not Layout

`onHingeChange` provides live hinge state and angle for optional interactions or effects. Do not use it to drive layout; use size classes, `ArrangementView`, and reserved regions instead. `DeviceHingeContext.hinge` is optional, so reset effect state when there is no hinge or when the relevant hinge status ends.

```swift
@available(iOS 27.1, *)
struct HingeReactiveArtwork: View {
    @State private var foldEffect = 0.0

    var body: some View {
        Artwork()
            .scaleEffect(1 + foldEffect * 0.04)
            .onHingeChange { _, context in
                if let hinge = context.hinge,
                   hinge.status == .partiallyOpen {
                    foldEffect = min(max(hinge.angle.degrees / 180, 0), 1)
                } else {
                    foldEffect = 0
                }
            }
    }
}
```

Select this view behind `#available(iOS 27.1, *)`; the fallback omits the optional effect.

## Scene Accessories

Scene accessories can pair supplementary content with the main scene on another display, but the system controls their availability and it can change at runtime. Keep enablement state synchronized with `onAvailabilityChange`, disable unavailable controls, and handle failed scene requests rather than inferring availability from pose. For camera accessories, register the accessory with the relevant camera view, but defer capture session, camera selection, preview, and rotation behavior to AVFoundation guidance.

## Verifying Layouts

Simulator command-line tools cannot fold the device, rotate the inner display, or set the hinge angle, and coordinate taps can miss the inner display. Do not spend iterations scripting poses: iterate on layout in Xcode Previews where possible, add a debug entry point that opens the screen under test, and ask the user to confirm folded and landscape poses in a simulator they have already posed.

## Official Sources

- [Get ready for iPhone Duo](https://developer.apple.com/iphone-duo/)
- [Preparing your app for iPhone Duo](https://developer.apple.com/documentation/technologyoverviews/preparing-your-app-for-iphone-duo)
- [Designing for iPhone Duo](https://developer.apple.com/design/human-interface-guidelines/designing-for-iphone-duo)
- Apple Tech Talks 111461–111466, especially [Prepare your app](https://developer.apple.com/videos/play/tech-talks/111461/), [Raise the bar](https://developer.apple.com/videos/play/tech-talks/111462/), [Strike a pose](https://developer.apple.com/videos/play/tech-talks/111463/), and [Leverage multiple displays and scenes](https://developer.apple.com/videos/play/tech-talks/111464/)
