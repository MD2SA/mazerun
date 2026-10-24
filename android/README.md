# Android app

Android client for the Mazerun project. It shows messages, room occupation,
sound, and temperature.

## Requirements

- Android Studio
- JDK 11+
- Android SDK 35 (`minSdk 24`)

## Run

1. Open `android/` in Android Studio.
2. Sync Gradle.
3. Run the app.

Command line:

```bash
cd android
./gradlew assembleDebug
```

## Login

Enter:

- **Email / password** — a user from the MySQL `user` table
- **Host** — `10.0.2.2:8000` for the emulator, or the PHP host's LAN IP
- **Database** — `mazerun`

The app appends `/android/` to the host automatically.

## Docs

See [../docs/android.md](../docs/android.md) for screens, networking, and
troubleshooting.
