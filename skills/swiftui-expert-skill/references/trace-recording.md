# Recording an Instruments Trace

Use this reference when the user asks to record a new trace — either to
attach to a running app, launch one fresh, or capture a specific session
of actions they'll perform interactively.

The bundled `scripts/record_trace.py` wraps `xctrace record` with:

- The **SwiftUI** template by default (override with `--template`).
- **Manual stop** via Ctrl+C, a stop-file, or `--time-limit`.
- JSON discovery for devices and templates.
- Normal Python exit codes so an agent can orchestrate.
- Redacted command logging for values passed through `--env`.
- An explicit acknowledgement gate for system-wide recordings.

## Privacy and consent

Prefer `--attach` or `--launch`, which limits collection to the app being
diagnosed. A system-wide recording can capture activity and metadata from
unrelated applications. Before using `--all-processes`, explain that scope to
the user and obtain their explicit approval. Then pass
`--allow-system-wide-recording` to record that acknowledgement in the command.

Values passed through `--env KEY=VALUE` are forwarded to `xctrace`, but the
wrapper redacts each value from its displayed command. Avoid placing secrets on
command lines when a safer launch configuration is available, because other
local process-inspection tools may still expose process arguments.

## Typical flows

### A) Attach to a running app on a connected device

```bash
python3 "${SKILL_DIR}/scripts/record_trace.py" \
  --device "Pol's iPhone" \
  --attach "Helm" \
  --output ~/Desktop/helm-session.trace
```

Leave it running while the user exercises the app. Stop with **Ctrl+C**.

### B) Launch an app and record from the first frame

```bash
python3 "${SKILL_DIR}/scripts/record_trace.py" \
  --device "<UDID>" \
  --launch "/path/to/App.app" \
  --output ~/Desktop/launch.trace
```

On a simulator, pass the bundle ID to `--launch` instead. A `.app` path from
DerivedData can run in the background while the simulator stays on the home
screen, so the trace contains no real interaction.

Useful for diagnosing cold-start hitches and view-creation cost.

### C) Agent-driven: start in background, stop via stop-file

When you (the agent) are running non-interactively — e.g. via
`Bash run_in_background` — use a stop-file so you can signal the
recording to end cleanly:

```bash
# Start recording (background)
python3 "${SKILL_DIR}/scripts/record_trace.py" \
  --attach Helm --stop-file /tmp/stop-trace \
  --output ~/Desktop/session.trace

# ...user does their thing...

# Stop cleanly (from another shell or tool call)
touch /tmp/stop-trace
```

The script polls every 0.5s for the stop-file, sends SIGINT to xctrace
when it appears, and waits up to 60s for the trace to finalise.

### D) Time-boxed recording

```bash
python3 "${SKILL_DIR}/scripts/record_trace.py" \
  --attach Helm --time-limit 30s --output ~/Desktop/30s.trace
```

xctrace stops itself at the limit.

## Discovery helpers

```bash
# List every connected device, simulator, and the host — JSON.
python3 "${SKILL_DIR}/scripts/record_trace.py" --list-devices

# List all Instruments templates — JSON with a flat list + by-section map.
python3 "${SKILL_DIR}/scripts/record_trace.py" --list-templates
```

Device entries have `kind` (`devices`, `devices offline`, `simulators`),
`name`, `os`, `udid`. Offline devices are known but unplugged / unpaired —
plug them in before recording.

## Picking a template

> **Hard rule: the `SwiftUI` template only populates the SwiftUI lane on a
> real device — a physical iOS/iPadOS device or the host Mac. On the iOS
> Simulator it records but the SwiftUI lane comes back empty.** If the
> chosen UDID falls under the `simulators` kind from `--list-devices`,
> switch to `Time Profiler`. It gives you Time Profiler + Hangs, which
> `analyze_trace.py` analyses and correlates normally; the `hitches` and
> `swiftui` lanes will report `available: false`.

Decision flow:

| Target                                       | Template to pass     |
|----------------------------------------------|----------------------|
| Physical iOS/iPadOS device (connected)       | `SwiftUI` (default)  |
| Host Mac (macOS app, `--all-processes`, etc.)| `SwiftUI` (default)  |
| iOS / iPadOS / watchOS / tvOS Simulator      | `Time Profiler`      |

Always confirm the target kind with `--list-devices` before starting a
recording: entries under `simulators` mean you must switch to Time
Profiler; entries under `devices` (both connected devices and the host
Mac) support the SwiftUI template. Entries under `devices offline` need
the user to connect/unlock/trust the device before recording.

For ad-hoc hang hunting on any target, `Time Profiler` or
`Animation Hitches` alone may be enough.

The `Time Profiler` template's Hangs threshold defaults to 250 ms, so lower it to
capture the lighter tiers in `references/trace-analysis.md`. `record_trace.py`
doesn't forward recording options, so call `xctrace` directly:

```bash
xcrun xctrace record --template "Time Profiler" --show-recording-options \
  | sed 's/"hangsThreshold" : 250/"hangsThreshold" : 33/' > options.json
xcrun xctrace record --no-prompt --template "Time Profiler" \
  --recording-options options.json --device "<UDID>" --time-limit 60s \
  --output ~/Desktop/hangs.trace --launch -- com.example.MyApp
```

For an explicitly approved system-wide recording:

```bash
python3 "${SKILL_DIR}/scripts/record_trace.py" \
  --all-processes --allow-system-wide-recording \
  --time-limit 30s --output ~/Desktop/system-wide.trace
```

## Chaining into analysis

The recording script prints `trace written: <path>` on exit. Feed that
path straight into `analyze_trace.py`:

```bash
TRACE=$(python3 "${SKILL_DIR}/scripts/record_trace.py" \
    --attach Helm --stop-file /tmp/stop-trace --output ~/Desktop/session.trace \
    2>&1 | awk '/trace written:/ {print $NF}')
python3 "${SKILL_DIR}/scripts/analyze_trace.py" --trace "$TRACE" --json-only
```

If the user wanted a specific scope, combine with `--list-logs` /
`--list-signposts` / `--window` from `references/trace-analysis.md`.

## Failure modes to handle

- **Device offline** — `--list-devices` shows it in `devices offline`.
  Ask the user to connect/unlock the device and retry.
- **Output path exists** — the script refuses to overwrite. Either pick
  a new `--output` or delete the existing bundle.
- **App not running (for `--attach`)** — xctrace exits with an error;
  fall back to `--launch` or tell the user to open the app first.
- **`Cannot find process matching name`** — `--attach` matches the name
  Instruments shows for the process, which can differ from the scheme or
  executable name. An app whose executable is `MyApp` but whose display name
  is `Trails` attaches as `--attach Trails`. If a simulator app's PID reports
  `Cannot find process for provided pid`, try that name instead.
- **Signing / trust on device** — iOS requires a development build
  signed with the user's team. If xctrace returns a signing error, point
  the user to trust the developer profile on the device.
