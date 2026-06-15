# Chatquest 2 Character Creator

A desktop tool for designing custom characters and personal (prf) weapons for
**Chatquest 2**, a Fire Emblem Fates-based project. Every character is built
against a fixed point budget, so each stat, skill, and weapon effect has a cost —
the tool keeps the running total and stops you from going over budget.

Built with Python and tkinter. Distributed as a standalone Windows `.exe` on
itch.io; this repository holds the source.

## Features

- **Character builder** — name, class, appearance, birthday (validated MM/DD),
  movement type, and personal skill.
- **Skills** — pick up to 4 from a searchable, group-filterable list. Costs are
  scaled automatically and skills are sorted by the order they're learned.
- **Attribute growths** — 0–100% in steps of 5, with a Strength/Magic "hybrid
  discount" and a live total-growth readout that drives your base stats.
- **Secondary stats** — Hit, Crit, Avoid, and Dodge with scaled costs.
- **Attack Stance & Pair-Up bonuses** — per support level, with enforced limits.
- **Custom Weapon Creator** — build a prf weapon within its own point budget:
  stats, fixed effects, value effects, staff/rod effects, on-hit debuffs, and
  buffs, with all the interlocking rules handled for you.
- **Import / Export** — save and load characters and weapons as JSON, with
  validation on export and graceful handling of skills that no longer exist.

## Requirements

- Python 3.13 (earlier 3.x versions with tkinter should also work)
- tkinter (included with standard Python installs on Windows)

No third-party packages are required to run the tool.

## Running from source

`skill_data.json` must sit next to `character_creator.py` (it's required — the
program exits with an error if it's missing).

```sh
python character_creator.py
```

## Building a standalone executable

Building requires [PyInstaller](https://pyinstaller.org/) (`pip install pyinstaller`).

The simplest path is the bundled build script, which reads the version from the
source and names the output accordingly:

```sh
python build_exe.py
```

The resulting `.exe` lands in the `dist/` folder. The `.spec` files are
alternative PyInstaller recipes; note that `FE_Fates_Character_Creator.spec`
references an `icon.ico` that is not included here.

## Repository layout

| Path                     | Description                                  |
| ------------------------ | -------------------------------------------- |
| `character_creator.py`   | The application (single-file tkinter app).   |
| `skill_data.json`        | Skill catalog: costs, groups, descriptions.  |
| `build_exe.py`           | Convenience PyInstaller build script.        |
| `*.spec`                 | PyInstaller build recipes.                   |
| `Skill_Description.txt`  | Reference text for skill descriptions.       |

## License

Copyright (C) 2026 kronfarore

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE. See the GNU General Public License for more details.

The full license text is in [LICENSE](LICENSE).
