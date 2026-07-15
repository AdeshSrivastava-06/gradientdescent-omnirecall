# Privacy and Safety — OmniRecall

## Data Handling

- All captured data (screenshots, extracted text, embeddings) is stored exclusively in a local SQLite database (`omnirecall.db`) and a local `screenshots/` folder, both on the user's own machine.
- No data is transmitted over a network at any point during normal operation.
- No user account, login, or cloud sync exists in this build — the tool is single-user, single-device by design.

## Permissions Required

- Screen capture permission (implicit via `mss`, standard OS screenshot access)
- Ability to read the currently focused window title (`pygetwindow`) — used only to tag captures with an app name and to check against the user's privacy blocklist; window titles are stored, but window *content* is only captured via the standard screenshot path already covered above.

## Storage and Retention

- Screenshots are retained in full for approximately 3 hours after capture, primarily to support "proof" display in search results and live demoing.
- After 3 hours, the screenshot image file is deleted from disk. A compact JSON text record (timestamp, app name, extracted text) is retained in its place, so search continues to function on older data without unbounded image storage growth.
- There is currently no automatic expiry of the text/embedding records themselves — the user's full text history persists until manually deleted (by removing `omnirecall.db`).

## User-Controlled Privacy Blocklist

- A settings interface lets the user toggle which applications are excluded from capture entirely (pre-populated with common sensitive categories: password managers, banking apps, incognito browser windows — fully editable).
- Blocked applications are checked **before** any screenshot is taken; if blocked, no screenshot, OCR, or storage occurs for that moment — the skip happens at the earliest possible point in the pipeline, not as a post-hoc filter.
- The user can add custom application names to the blocklist at any time via the Settings tab.

## Limitations and Potential Risks

- **Incomplete blocklist coverage:** the blocklist matches on window title text. An application whose title doesn't clearly indicate its sensitive nature (e.g. a banking site open in a generically-titled browser tab) may not be automatically excluded. Users should be aware the blocklist is a best-effort control, not a guarantee.
- **Local storage is not encrypted at rest** in the current build. Anyone with direct access to the user's file system could read the SQLite database or screenshot files. This is a known limitation, not a claim of full security — encryption at rest is a natural next step beyond the current hackathon scope.
- **No secondary confirmation before capture** — the tool captures continuously in the background by design; a user who forgets it's running could inadvertently capture something they'd have preferred to exclude, beyond what the blocklist catches.
- **Multi-user machines are not accounted for** — the tool assumes a single user of the device; no separation exists between different OS user accounts sharing the same machine.

## What This Tool Does Not Do

- Does not send any captured data to a cloud service or third party
- Does not require or create a user account
- Does not track or profile the user for any purpose beyond enabling their own local search
