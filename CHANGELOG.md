# Changelog

All notable changes to the Chatquest 2 Character Creator are documented here.

## 0.59.a

### Weapon cost rebalance
- **Magic Weapon** no longer changes the **Might** stat cost — Might is priced
  the same whether or not Magic Weapon is active.
- **Magic Weapon** no longer changes **Silver Weapon** or **S-Rank Debuff** costs.
- **Silver Weapon** and **S-Rank Debuff** now use a single flat cost for *every*
  weapon type (the old Tome/Scroll-vs-physical "magical cost" distinction is gone).
- Cleaned up the now-obsolete cost notes/labels tied to the above.

### Skill balance
- **Healing Descant** cost 8.36 → **16.37**.
- **Amaterasu** cost 16.71 → **32.72**.
- **Inspiring Song** description clarified: cannot sing for other characters.

### Added — import verification (anti-tamper)
- Importing a **character** or **weapon** recomputes the true cost and legality;
  if something does not add up, a **"Verification — please review"** window lists
  each issue (forged/mismatched cost, over budget, forged base stats,
  out-of-range values, broken pairup/stance/skill limits). It **never blocks the
  load** — it is purely informational.
- The full weapon recompute also runs when you **open the Weapon Creator** or it
  **auto-reloads** a weapon (silent when everything checks out).
- Version-aware: files made in an older version get a "may be version drift, not
  tampering" note instead of false alarms.

### Skills
- **Skill limit raised from 4 to 6.**
- **Main-window Skills display redesigned** — from a cramped text box to an
  aligned **#/Skill/Cost** table that scales to 6, with a hover tooltip
  (description + groups) on each skill.
- **Skill Selection** hover tooltips now also show each skill's **groups**.

### Personal skills
- **Hover** the picker to see the selected skill's **description**.
- Added a **"?"** help note next to the picker.
- A personal skill is now **required** (None not allowed) — blocked on export,
  flagged on import.
- A personal skill **cannot also be a normal skill** — blocked on export, flagged
  on import (alias-aware: *Nobility / Dragon Blood* is treated as *Nobility*).

## 0.58.d
- Baseline release distributed on itch.io.
