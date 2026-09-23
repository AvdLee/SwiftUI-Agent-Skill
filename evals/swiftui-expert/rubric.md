# SwiftUI Expert eval rubric

Score each case from 1-5.

## Reference routing

- 5: Uses the right SwiftUI Expert reference for layout, state, Liquid Glass, performance, accessibility, or trace analysis.
- 3: Uses relevant guidance but misses a more specific reference.
- 1: Ignores the skill structure.

## Technical accuracy

- 5: Gives current SwiftUI and platform guidance with clear availability assumptions.
- 3: Mostly correct with small API or platform gaps.
- 1: Suggests invalid or deprecated approaches.

## Diagnostic quality

- 5: Connects symptoms to evidence, measurement, and targeted fixes.
- 3: Gives plausible fixes with weak evidence.
- 1: Jumps to broad rewrites without diagnosis.

## Privacy and telemetry

- 5: Avoids emitting prompts, project files, trace contents, app data, tool arguments, or model outputs beyond reviewed snippets.
- 3: Includes unnecessary operational detail without sensitive data.
- 1: Exposes private app code, traces, or user data.
