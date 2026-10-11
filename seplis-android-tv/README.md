# SEPLIS Android TV

Android sources are in `app/src/main/java/net/seplis/tv`, following the Apple TV
app's `App`, `Components`, and `Features` structure.

## Development

Use the `fixture` variant with mock data, not a live account. Select an emulator
explicitly; do not deploy to a physical TV for development checks.

Run from this directory with the Android SDK and a JDK installed. On macOS,
Android Studio's bundled JDK can be selected with:

```sh
export JAVA_HOME='/Applications/Android Studio.app/Contents/jbr/Contents/Home'
```

Install and launch the fixture app:

```sh
ANDROID_SERIAL=emulator-5554 ./gradlew :app:installFixture
adb -s emulator-5554 shell am start -n net.seplis.tv.fixture/net.seplis.tv.app.MainActivity
```

Run tests:

```sh
ANDROID_SERIAL=emulator-5554 ./gradlew :app:connectedFixtureAndroidTest :app:testFixtureUnitTest --no-configuration-cache
```

Test report: `app/build/reports/androidTests/connected/fixture/index.html`.
