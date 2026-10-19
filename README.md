# Applix Showcase

Community apps built with [Applix](https://github.com/Konprostart/Applix). Everyone can browse
them in the app and build them as real, installable Android apps - no code, no build tools.

**Browse in the app:** Applix -> Create -> Showcase

## Layout

```
showcase.json              <- the index the app downloads
<slug>/app.html            <- the app (single self-contained HTML file)
<slug>/showcase.json       <- metadata: name, description, author, bridges, added, resources
<slug>/README.md           <- short description of the app
<slug>/resources/<name>    <- optional bundled files (JSON, images, databases, ...)
tools/build_index.py       <- regenerates showcase.json from the app folders
```

`showcase.json` in the root is generated - never edit it by hand. Run
`python3 tools/build_index.py` after adding or removing an app folder. CI checks that the index
matches the folders and regenerates it automatically on every merge to `main`.

## Submit an app

**Option 1 - from the app (recommended).** Open the app you built in Applix, go to My Apps ->
Submit to Showcase, enter a GitHub token, and Applix opens a pull request for you. The app
forks this repository, creates a branch, and commits your `app.html` plus any bundled files.

**Option 2 - with a pull request.** Create a folder named after your app (lowercase, letters,
digits and dashes) containing `app.html`, `showcase.json` and `README.md`, then open a pull
request. Keep the metadata in `showcase.json` in this shape:

```json
{
  "name": "My App",
  "description": "One or two sentences about what it does.",
  "author": "your-github-username",
  "bridges": ["storage", "device"],
  "added": "2026-10-19"
}
```

## Rules

- One self-contained `app.html` per app. External CDNs are fine, but the app must work offline.
- Only use bridge calls that exist in the [Applix SPEC](https://github.com/Konprostart/Applix/blob/main/SPEC.md).
  Applix runs a bridge linter before every build and will tell you about unknown calls.
- No secrets, no API keys, no tracking, no ads.
- Bundled resources are limited to 25 MB per file.
- Your app must be your own work, and you keep the rights to it. By opening a pull request you
  agree that it is published under the [MIT license](LICENSE) of this repository.
- Be nice. No malware, no crypto miners, no apps that only exist to open ads.

## License

MIT - see [LICENSE](LICENSE). The example apps are derived from
[Applix](https://github.com/Konprostart/Applix), which is itself derived from
[iappyxOS](https://github.com/iappyx/iappyxOS). See [NOTICE.md](NOTICE.md).
