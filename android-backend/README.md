# AI Notification Sorter — Android backend

A local-only Android notification sorter with a native Jetpack Compose
dashboard. It uses `NotificationListenerService`, Room, coroutines/Flow, and a
manual application container. It does not replace or modify Android's
notification shade and makes no network calls.

## Open and run

1. Open the `android-backend` folder in Android Studio (Hedgehog or newer).
2. Use Android Studio's suggested Gradle JDK 17 and allow Gradle sync to finish.
   The project uses AGP 8.7.3, Kotlin 2.0.21, and compile/target SDK 35.
3. Select the `app` run configuration and launch it on an Android 8.0+ device or
   emulator.
4. On the dashboard, tap **Open notification settings**, find **AI
   Notification Sorter**, and enable notification access. Confirm Android's
   warning dialog. Android requires the user to grant this access explicitly.
5. The dashboard shows notification access, priority counts, notifications,
   and rules. Add high-priority keywords, enable or disable rules, mark
   notifications as read, or override their priority.
6. Post a notification from another app. Notifications from this app, group
   summaries, and ongoing notifications are ignored.

`gradle/wrapper/gradle-wrapper.properties` pins Gradle 8.9. The wrapper JAR and
launcher scripts are not included, so the wrapper cannot run yet. Android
Studio can sync using a configured local Gradle 8.9 installation; otherwise
generate wrapper files from Android Studio or a locally installed Gradle 8.9.

## Package map

- `model`: Android-free notification input, priorities, and classifier result.
- `domain`: rule evaluation, classifier interface, and the processing pipeline.
- `data`: Room entities, DAOs, converters, database, and repositories.
- `notification`: Android notification listener and safe extraction.
- `ui`: native Compose dashboard and frontend-facing `MainViewModel`.
- `App` (in `SorterApplication.kt`): database/repository wiring and manual
  `AppContainer`.

## Teammate hand-off

- **SLM:** Implement `NotificationClassifier` and replace the
  `HeuristicClassifier()` binding in `SorterApplication.kt`. Keep inference
  on-device; `NotificationProcessor` enforces a 3-second timeout and falls
  back to MEDIUM on timeout or exception.
- **Android frontend:** The Compose dashboard uses `MainViewModel` as its UI
  API. It exposes `StateFlow`s for `notifications`, `rules`, and
  `countsByPriority`, plus rule, read, override, and clear-history actions.
- **Web frontend:** The React app in `../frontend` remains a separate demo
  connected to the Python SLM. It is not embedded in or connected to this app.
- **Integration:** The listener converts platform notifications to
  `NotificationData`; the processor evaluates user rules first, invokes the
  classifier only when no enabled rule matches, and persists the result.
  User-granted notification access is required. The `<queries>` launcher
  intent permits package-label lookup where Android's package visibility rules
  allow it; the listener falls back to the package name otherwise.

Default keyword rules are seeded once when the rules table is empty:
HIGH (`otp`, `verification code`, `password`, `urgent`, `debited`, `credited`)
and LOW (`offer`, `sale`, `discount`).

Run unit tests from Android Studio's Gradle tool window (`app > Tasks > verification
> test`) or with `gradle :app:testDebugUnitTest` when Gradle is installed.
