# Android app

The Android app is a Java application in `android/`. It mirrors the main
dashboard views: messages, Marsami room occupation, sound, and temperature.

## Requirements

- Android Studio (or the Android SDK + Gradle)
- JDK 11+
- Android SDK 35 (`compileSdk = 35`, `targetSdk = 35`, `minSdk = 24`)

## Open and run

1. Open the `android/` directory in Android Studio.
2. Let Gradle sync.
3. Run on an emulator or a physical device.

From the command line:

```bash
cd android
./gradlew assembleDebug
```

On Windows use `gradlew.bat`.

## Login

The login screen (`MazeLoginActivity`) asks for:

| Field | Example | Notes |
| --- | --- | --- |
| Email | `user@example.com` | Matches `user.email` |
| Password | `secret` | bcrypt-verified by `login.php` |
| Host | `10.0.2.2:8000` | Emulator alias for the host machine |
| Database | `mazerun` | Sent to the API and stored in the JWT |

The app normalizes the host with `ApiClient.formatUrl()`:

- Adds `http://` if no scheme is present.
- Removes the legacy `/maze_app_php` path.
- Appends `/android/` to the base URL.

So `10.0.2.2:8000` becomes `http://10.0.2.2:8000/android/`.

For a physical device, use the LAN IP of the machine running the PHP container,
for example `192.168.1.50:8000`. The device and the host must be on the same
network, and port `8000` must be reachable.

## Screens

| Screen | Fragment | Data source |
| --- | --- | --- |
| Messages | `MazeMessagesFragment` | `get_messages.php` |
| Marsami room | `MarsamiRoomFragment` | `get_room_data.php` |
| Sound | `MazeSoundFragment` | `get_sound_data.php`, `get_max_sound_value.php` |
| Temperature | `MazeTemperatureFragment` | `get_temperature_data.php`, `get_min_max_temp_values.php` |

The room screen uses a bar chart; sound and temperature use line charts
(MPAndroidChart).

## Session handling

`SessionManager` keeps the host, database, email, password, and JWT in memory.
There is no `SharedPreferences` persistence, so the session is lost when the
process is killed. Log in again after swiping the app away.

## Networking

- `ApiClient` uses OkHttp with 15-second connect/read/write timeouts.
- Requests to protected endpoints include `Authorization: Bearer <token>`.
- Cleartext HTTP is allowed (`android:usesCleartextTraffic="true"`) for local
  development. Use HTTPS behind a reverse proxy for anything else.

## Build configuration

- `android/app/build.gradle.kts` declares the SDK levels and dependencies.
- `android/gradle/libs.versions.toml` holds the version catalog.
- `gradle/wrapper/gradle-wrapper.jar` is tracked so the wrapper works from a
  fresh clone.

## Troubleshooting

- **Connection refused:** use `10.0.2.2` in the emulator, not `localhost`.
- **401 Unauthorized:** the token expired (8 hours) or `JWT_SECRET` changed;
  log in again.
- **Login fails:** the `user` table must have a bcrypt hash. See
  [SECURITY.md](../SECURITY.md).
- **Cleartext blocked:** the manifest allows cleartext, but a network security
  policy or a release build may override it.
- **Gradle sync fails:** check the JDK and SDK 35 installation.

## Related docs

- [HTTP API](api.md)
- [Configuration](configuration.md)
- [Getting started](getting-started.md)
