# Changelog

All notable changes to the Chatquest 2 Character Creator are documented here.

## 0.65.a

### Changed
- **Attribute growth costs are now capped per step** — no single +5% step can
  cost more than **5 points** (new `GROWTH_STEP_COST_CAP` option). Only the
  expensive top of the curve is affected; the early steps are unchanged, so
  nothing got more expensive. Reaching 100% in a stat now costs about **63
  points instead of ~70**.
- Why: the old curve made the last steps cost ~7x the first, so maxing a stat
  was the worst-value purchase available — build analysis showed you were
  always better off shaving a maxed stat to buy skills instead. Capping the top
  step makes a maxed stat a real choice again without making anything else
  cheaper.
- **Build budget lowered 180 → 170**, offsetting the cheaper growth costs above
  so overall character power stays roughly where it was.

## 0.64.c

### Fixed
- **Reload skill_data.json** now also re-checks gate legality of slotted
  skills: a skill whose gate was raised above its slot is moved to an eligible
  free slot (or unslotted if none is free), and the reload dialog reports
  every move/removal. Previously an illegal placement survived silently until
  export validation.

## 0.64.b

Code-review pass: fixes for all confirmed findings.

### Fixed
- **Weapon Creator Reset wiped the weapon on the first click** — the two-click
  confirmation was inverted. It now arms first ("Click Again to Confirm Reset")
  and only wipes on the second click, like the character Reset.
- **Reset Character / Reset Everything** now close an open Skill Selection
  window — previously its stale slots could silently re-populate the skills you
  just cleared when Confirm was clicked later.
- Importing a **pre-0.60 character file** with exactly 5 skills is no longer
  misread as the new ordered-slot format (old flat lists are always re-slotted
  by gate). Slot placement is also two-pass now: an entry that doesn't fit its
  slot can no longer displace a later skill from its own legitimate slot.
- The Base Weapon creator's "Not available for Base Weapon" note is no longer
  wiped when the weapon type changes (or on reset).
- **Reload skill_data.json** now recomputes the skill-cost scaling, refreshes
  the Gate filter options, and pushes pruned slots to the main window
  (previously a removed slotted skill could crash later cost updates).
- Exported `points_summary.attribute_points` now includes the Hybrid Discount,
  so the itemized components add up to `used_points` exactly.

### Internal
- Skill list derived live from the slots (no more manual re-sync), Hybrid
  Discount readout derived from the same helper that charges it, removed a
  doubled next-step-cost recompute per keystroke and a dead parameter.

## 0.64.a

### Changed
- The **Hybrid Discount now applies to Strength/Magic only**. Defense and
  Resistance still share a cost (priced the same as each other via **Use Same
  Cost**) but receive no discount.

### Skill Selection window
- New **Sort** selector: sort skills by **Cost** or **Alphabetical** (within each
  gate section).
- The group filter no longer changes when you type while it isn't focused —
  letter-jump only works while the group button has focus.
- Dev builds get a **Reload skill_data.json** button (reloads the catalog from
  disk without restarting). Hidden in stable releases.

## 0.63.b

### Changed
- **Hybrid Discount raised to 60%** (was 50%) and now applies to **two** stat
  pairs — Strength/Magic *and* Defense/Resistance. Within each pair the cheaper
  of the two costs is discounted; the readout lists both.
- New **Use Same Cost** option (on by default): the cheaper stat of each pair
  uses its pricier partner's cost curve, so Strength/Magic and Defense/Resistance
  cost the same at equal growth% and only differ when set to different growths.
- Repriced a number of skills; corrected the **Seal Defence → Seal Defense**
  spelling (name and description).

### Fixed
- **Reset Everything** now also clears the Total Growth% readout.
- Attribute growth steps are now guaranteed to never get cheaper than the
  previous step (rounding no longer produces an occasional dip).
- Clicking an input field then clicking empty space now deselects the field.

### Skill Selection window
- Slotted skills are highlighted with a blue **button colour** (was a font-colour
  change).

## 0.63.a

### Added
- **Reset Everything** button — resets the character and both weapons at once.
- Click a slotted skill (in the slot header or the list) to move it to another
  eligible slot.

### Changed
- Skill Selection window: skills are now **grouped into gate sections**, sorted
  cheapest-first within each; slotted skills are highlighted, and each slot shows
  its skill's cost.
- **Gate numbering now starts at 1** (was 0) — gates are 1–5.
- Attribute growth costs **raised back up** — steeper curve (~70 to reach 100%,
  ramping up past 60%), from the flatter 0.62.a values.

### Removed
- Skills: Kidnap, Capture, Paragon, Dragonskin, Divine Shield, Immobilize.

## 0.62.b

### Changed
- Build budget lowered 200 → 180.
- Lowered the skill cost scale cap (24 → 20) and repriced several skills,
  notably Aptitude (cheaper, ~its recalculated value), Rally Movement, and
  Rally Spectrum.
- Skill Selection slot headers now show the gate next to the chapter number.

## 0.62.a

### Changed
- Rebalanced **attribute growth costs**: flattened (the last +5% step now costs
  ~3x the first instead of ~8x) and brought down (reaching 100% in a stat now
  averages ~50, was ~80), with the per-stat spread preserved. HP Regeneration,
  which derives from the HP table, is cheaper as a result.
- Reduced **secondary stat** (Hit/Crit/Avoid/Dodge) base costs by ~25%, keeping
  the mild curve.

## 0.61.d

### Changed
- The weapon creator's info note is now specific to the weapon kind: the Base
  Weapon notes it's available from when the character joins; the Promoted Weapon
  notes it's available after chapter 17.

## 0.61.c

### Added
- A weapon file with no kind tag (made in an earlier version) is treated as a
  Promoted Weapon on import.
- Loading a weapon now warns which effects were removed because they are not
  available for that weapon kind.

## 0.61.b

### Added
- Exported weapon files now carry a `weapon_kind` tag (Promoted / Base).
- Importing a weapon of the other kind into a creator is allowed but shows a
  notice; effects unavailable for that kind are dropped on load.

### Changed
- **Silver Weapon** and **S Rank Debuff** fixed effects are unavailable in the
  Base Weapon creator.

## 0.61.a

### Added
- Each character now has **two weapons**: a full **Promoted Weapon** (100 pts)
  and a weaker **Base Weapon** (50 pts, where Hit costs half as much). Both are
  built with the same creator, shown and reset independently, exported/imported
  with the character, and each is verified against its own budget.

### Changed
- The weapon creator is now opened per weapon: "Open Promoted Weapon Creator"
  and "Open Base Weapon Creator". Saved character files gain a `custom_weapon_base`
  field (older files with only `custom_weapon` still load as the Promoted Weapon).

## 0.60.c

### Changed
- The point budget is no longer enforced while editing — growth rates, secondary
  stats, weapon slots, and skills can all go over budget (remaining shows
  negative in red). The budget is verified on export and on import instead, so
  it's easier to make changes mid-build.

### Fixed
- Picking/removing skills in the Skill Selection window now updates the main
  window's points live (mirror of the earlier main → window fix). Cancel reverts.
- Character export now replaces spaces and slashes in the saved filename, matching
  the weapon export.

## 0.60.b

### Added
- Gate filter in the Skill Selection window.

### Changed
- Skill slots are now labelled by chapter (6, 9/10, 14, 18, 23) instead of level.

### Fixed
- The Skill Selection window's remaining-points display now updates live when a
  main-window change alters the budget while the window is open.

## 0.60.a

### Added — skill gate / slot system
- Skills now occupy **5 ordered slots** (levels 1, 10, 15, 20, 25), each with a
  gate tier (0–4) tied to chapter progress. Every skill has a gate and can only
  be placed in a slot whose gate is high enough.
- Skill Selection reworked: a slot header shows all slots, and clicking a skill
  pops a menu of just the slots it's allowed in. Auto-sort by cost is gone.
- Skills export/import as an ordered slot list. Imports from older or different-
  length files are re-slotted into eligible positions; anything that no longer
  exists or can't be slotted is reported.
- Export **and** import verification now check gate legality and skill count.

### Changed
- Character build budget raised **180 → 200**.
- **Aptitude** repriced 29.29 → 49 (per the value analysis).
- Attribute cost tables extended to **110%** so Aptitude can push growth past 100.

### Fixed
- Corrected malformed entries in `skill_data.json`.

## 0.59.b

### Fixed
- Weapon Creator: the "Staff Might" note now shows the real per-point cost (1)
  instead of the underlying 0.73 fraction.
- Loading or opening a non-staff weapon that has on-hit debuffs now restores
  those debuffs correctly (they were skipped on open/auto-reload before).

### Internal
- Import verification now also checks secondary stats (value legality and
  stored-cost consistency).
- Assorted code-review cleanups and refactors (consolidated weapon loading,
  deduplicated helpers, specific exception handling) — no behavior change.

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
