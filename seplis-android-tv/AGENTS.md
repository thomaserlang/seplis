# Android TV Port

- Treat `../seplis-apple-tv/seplis-apple-tv` as the reference for layout, labels,
  component ownership, and navigation. Read the corresponding Swift files first.
- Keep shared filenames, feature directories, and ownership aligned with Apple TV,
  including models, networking, and tests. Do not add Android-only repository layers.
- Keep native platform adapters where needed. Prefer native Compose behavior over
  elaborate code to reproduce platform-specific effects.
- Test only with the `fixture` variant and mock accounts. Never authenticate a
  live account or exercise live account data for development verification.
- Target an explicitly selected emulator with `ANDROID_SERIAL` or `adb -s`.
  Do not deploy to a connected physical TV unless the user requests it.
- See `README.md` for fixture build/test commands.
