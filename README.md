# Key Overlay

A lightweight, customizable keyboard input overlay for rhythm games on Windows.  
Displays key presses in real time with animated blocks, particles, and glow effects.

---

## Features

- **Animated key display** — rising blocks, particles, and glow pulses on each press
- **Per-key colors** — assign a different color to each key
- **Stats** — KPS (keys per second) and per-key press counters displayed on the overlay
- **Click-through** — fully transparent to mouse input during normal mode
- **Multi-language** — Korean, English, Russian, Japanese, Chinese (switches instantly, no restart)
- **Presets** — one-click 2K / 4K / 5K / 6K / 7K key layouts
- **Always on top** — stays visible over fullscreen and borderless-window games
- **Portable exe** — no installer needed, just run `KeyOverlay.exe`

---

## Download

Go to the [Releases](../../releases) page and download `KeyOverlay.exe`.  
No installation required — just run it.

---

## Requirements

- Windows 10 / 11

---

## Usage

Run `KeyOverlay.exe`. A tray icon appears in the system tray — right-click it for the menu.

| Hotkey | Action |
|--------|--------|
| `Ctrl+Alt+S` | Open settings |
| `Ctrl+Alt+M` | Toggle move mode (drag to reposition) |
| `ESC` (in move mode) | Exit move mode |

> The hotkey modifier (`Ctrl+Alt` or `Ctrl+Shift`) can be changed in **Settings → General**.

---

## Settings

Open with `Ctrl+Alt+S` or via the tray icon.

### Keys tab
- Add / remove / reorder tracked keys
- Assign a unique color to each key
- Quick presets: 2K, 4K, 5K, 6K, 7K

### Style tab
- Key size, spacing, font size
- Border / block color, text color, fill opacity
- Window opacity

### Animation tab
- Rising block effect (height, scroll speed, fade zone)
- Key press depth (push-down animation)
- Particles (burst count, continuous rate, color)
- Glow / light effect (size, intensity, color)

### Stats tab
- KPS display (keys per second)
- Per-key press count (shown inside each key box)
- Total press count

### General tab
- Language selector — applies immediately without restarting
- Hotkey modifier

---

## Special Key Names

When adding keys, use these names for non-letter keys:

| Key | Name |
|-----|------|
| Space | `space` |
| Shift | `shift` |
| Ctrl | `ctrl` |
| Alt | `alt` |
| Enter | `enter` |
| Backspace | `backspace` |
| Tab | `tab` |
| Caps Lock | `caps_lock` |
| Delete | `delete` |

---

## Config File Location

Settings are saved automatically at:

```
C:\Users\<YourName>\AppData\Roaming\KeyOverlay\config.json
```

The file is created on first launch. Delete it to reset all settings to default.  
The exe can be placed anywhere — the config is always stored in the same location regardless.

---

## Building from Source

```
pip install PyQt5 pynput pyinstaller
pyinstaller --onefile --windowed --name "KeyOverlay" overlay.py
```

The exe will be output to `dist\KeyOverlay.exe`.

---

## License

MIT
