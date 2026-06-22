import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, font as tkfont, filedialog
import json
import math
import sys
import os

# ============================================================================
# VERSION
# ============================================================================

VERSION = "0.61.a"

print("Program starting...")
# ============================================================================
# CONSTANTS
# ============================================================================

initial_points = 200
MAX_SKILLS = 5  # Maximum number of skills a character may select (Skills section)

# Skill slots: each of the MAX_SKILLS slots shows a chapter label (when it
# unlocks) and grants a gate tier. A skill with gate G may only be slotted where
# the slot's gate >= G. Both lists must stay length MAX_SKILLS. (The "9/10"
# chapter is still being decided.)
SKILL_SLOT_CHAPTERS = ["6", "9/10", "14", "18", "23"]
SKILL_SLOT_GATES = [0, 1, 2, 3, 4]

skill_data = {}

# Stats that use increments of 5
WEAPON_STAT_INCREMENT_5 = {"Hit", "Crit", "Avoid", "Dodge", "Base Staff Exp"}
STAFF_HIT_SCALE = 4 / 5        # Hit cost multiplier for Staff/Rod weapons
NEGATIVE_CREDIT_SCALE = 0.5    # Scale factor for credits from negative weapon stats/effects
DODGE_COST_SCALE = 2.0   # Scale factor for Dodge cost in both weapon stats and secondary stats

# Cumulative growth cost per attribute, indexed by growth // 5 (0% .. 110%).
# Indices 0-20 cover 0-100% (manual range); 21-22 are 105%/110%, reachable only
# by Aptitude (+10%). The 105/110 entries continue the table's geometric
# marginal (ratio ~1.116) and were extrapolated from the 0-100% values.
ATTRIBUTE_COSTS = {
    "HP": [0, 1.05, 2.21, 3.52, 4.97, 6.6, 8.41, 10.44, 12.7, 15.22, 18.04, 21.18, 24.69, 28.61, 32.98, 37.86, 43.31, 49.39, 56.18, 63.76, 72.23, 81.68, 92.24],
    "Strength": [0, 1.13, 2.4, 3.81, 5.39, 7.15, 9.11, 11.31, 13.76, 16.49, 19.54, 22.95, 26.75, 30.99, 35.73, 41.02, 46.92, 53.51, 60.87, 69.08, 78.24, 88.47, 99.88],
    "Magic": [0, 1.25, 2.65, 4.2, 5.94, 7.88, 10.05, 12.47, 15.17, 18.18, 21.54, 25.3, 29.49, 34.17, 39.39, 45.23, 51.73, 59, 67.11, 76.16, 86.27, 97.56, 110.15],
    "Skill": [0, 1.1, 2.34, 3.71, 5.25, 6.97, 8.88, 11.02, 13.4, 16.07, 19.04, 22.36, 26.06, 30.2, 34.81, 39.97, 45.72, 52.14, 59.31, 67.31, 76.24, 86.21, 97.34],
    "Speed": [0, 1.19, 2.52, 4.01, 5.67, 7.52, 9.58, 11.89, 14.46, 17.34, 20.54, 24.12, 28.12, 32.58, 37.56, 43.12, 49.33, 56.26, 63.99, 72.62, 82.26, 93.02, 105.04],
    "Luck": [0, 1.08, 2.28, 3.62, 5.11, 6.78, 8.65, 10.73, 13.05, 15.64, 18.54, 21.77, 25.38, 29.4, 33.9, 38.91, 44.52, 50.77, 57.75, 65.54, 74.23, 83.93, 94.75],
    "Defense": [0, 1.22, 2.58, 4.11, 5.8, 7.7, 9.82, 12.18, 14.81, 17.76, 21.04, 24.71, 28.81, 33.38, 38.48, 44.17, 50.53, 57.63, 65.55, 74.39, 84.26, 95.28, 107.58],
    "Resistance": [0, 1.16, 2.46, 3.91, 5.53, 7.33, 9.35, 11.6, 14.11, 16.91, 20.04, 23.53, 27.43, 31.79, 36.65, 42.07, 48.12, 54.88, 62.43, 70.85, 80.25, 90.74, 102.46]
}

PERSONAL_SKILLS = {
    "Shove": 0,
    "Swap": 0,
    "Shelter": 0,
    "Lunge": 0,
    "Locktouch": 0,
    "Pass": 0,
    "Nobility / Dragon Blood": 1,
}

# Personal-skill labels whose name differs from the matching skill_data.json
# entry. Used for description lookups and personal/normal overlap checks.
PERSONAL_SKILL_ALIASES = {"Nobility / Dragon Blood": "Nobility"}

MOVEMENT_COSTS = {
    "Infantry": 0,
    "Armor": -10,
    "Cavalry": 5,
    "Flyer": 10
}

SECONDARY_STAT_BASE_COSTS = {
    "Hit": 0.86,
    "Crit": 0.49,
    "Avoid": 0.92,
    "Dodge": 0.24 * DODGE_COST_SCALE
}

EXTRA_WEAPON_COST = 2
NOSFERATU_FORCES_BRONZE_AND_BOLD = True

# ============================================================================
# WEAPON CREATOR BALANCING CONSTANTS
# ============================================================================

WEAPON_TOTAL_POINTS = 100
MAX_SKILL_COST = 24  # Highest point cost any skill can have after scaling

WEAPON_STAT_COSTS = {
    "Might": 2.2,
    "Hit": 0.43,
    "Crit": 0.49,
    "Avoid": 0.92,
    "Dodge": 0.24 * DODGE_COST_SCALE,
    "Mov": 10.52,
    "Effective Speed Offensive": 1.17,
    "Effective Speed Defensive": 1.29,
    "Base Staff Exp": 0.25,
    "Uses": 0.0
}

# Each character has two weapons: a full "Promoted Weapon" (100 pts) and a
# weaker "Base Weapon" (50 pts, Hit costs half). field = key in the saved file.
BASE_WEAPON_TOTAL_POINTS = 50
WEAPON_KINDS = {
    "promoted": {"label": "Promoted Weapon", "points": WEAPON_TOTAL_POINTS,
                 "stat_costs": WEAPON_STAT_COSTS, "field": "custom_weapon"},
    "base": {"label": "Base Weapon", "points": BASE_WEAPON_TOTAL_POINTS,
             "stat_costs": {**WEAPON_STAT_COSTS, "Hit": WEAPON_STAT_COSTS["Hit"] / 2},
             "field": "custom_weapon_base"},
}

WEAPON_STAT_BASE = {
    "Might": 0,
    "Hit": 0,
    "Crit": 0,
    "Avoid": 0,
    "Dodge": 0,
    "Mov": 0,
    "Effective Speed Offensive": 0,
    "Effective Speed Defensive": 0,
    "Base Staff Exp": 0,
    "Uses": 1
}

WEAPON_STAT_MIN = {
    "Might": 0,
    "Hit": 0,
    "Crit": 0,
    "Avoid": -20,
    "Dodge": -20,
    "Mov": -2,
    "Effective Speed Offensive": -5,
    "Effective Speed Defensive": -5,
    "Base Staff Exp": 0,
    "Uses": 1
}

WEAPON_STAT_MAX = {
    "Might": 70,
    "Hit": 200,
    "Crit": 100,
    "Avoid": 50,
    "Dodge": 50,
    "Mov": 2,
    "Effective Speed Offensive": 5,
    "Effective Speed Defensive": 5,
    "Base Staff Exp": 100,
    "Uses": 50
}

MAGIC_MIGHT_COST = 2.43
HP_REGEN_COST_SCALE = 1 / 3  # HP Regeneration cost as fraction of HP growth table cost

# Precomputed HP Regeneration cumulative cost table.
# Built at startup — each step costs at least 1 more than the previous.
def _build_hp_regen_table():
    table = [0]  # index 0 = value 0 costs nothing
    hp = ATTRIBUTE_COSTS["HP"]
    for i in range(1, len(hp)):
        raw_marginal = hp[i] - hp[i - 1]
        step_cost = max(1, round(raw_marginal * HP_REGEN_COST_SCALE))
        table.append(table[-1] + step_cost)
    return table

HP_REGEN_COST_TABLE = _build_hp_regen_table()


MIGHT_COST_MULTIPLIERS = {
    "One Tap": 1.5,
    "Venge": 1.5,
    "Skillful": 1.8,
    "Flier Slayer": 1.5,
    "Dragon Slayer": 1.5,
    "Beast Slayer": 1.5,
    "Armor Slayer": 1.5
}

WEAPON_RANGE_COSTS = {
    "1": 0,
    "1-2": 10,
    "2": 0,
    "2-3": 25,
    "3": 10,
    "1-3": 45
}

SILVER_WEAPON_COST_PHYSICAL = -8.69
SILVER_WEAPON_COST_MAGICAL = -9.14

S_RANK_DEBUFF_COST_PHYSICAL = -22.01
S_RANK_DEBUFF_COST_MAGICAL = -24.27

DEBUFF_COSTS = {
    "Strength": 1.1,
    "Magic": 1.21,
    "Skill": 1.07,
    "Speed": 1.16,
    "Luck": 1.04,
    "Defense": 1.19,
    "Resistance": 1.13
}

DEBUFF_MAX = {
    "Strength": 7,
    "Magic": 7,
    "Skill": 7,
    "Speed": 7,
    "Luck": 7,
    "Defense": 7,
    "Resistance": 7
}

TEN_HEALTH_PERCENT_MOD = 12.53
TEN_DAMAGE_PERCENT_MOD = TEN_HEALTH_PERCENT_MOD / 2

def _staff_might_cost_per_point(cost):
    """Staff/Rod Might cost per point, before the strictly-increasing table."""
    return cost * (1 / 3)

# Precomputed Staff Might cumulative cost table.
# Built at startup — each step costs at least 1 more than the previous.
def _build_staff_might_table():
    import math as _math
    cpp = _staff_might_cost_per_point(WEAPON_STAT_COSTS["Might"])
    table = [0]  # index 0 = 0 points above base costs nothing
    for i in range(1, WEAPON_STAT_MAX["Might"] + 1):
        step_cost = max(1, _math.ceil(i * cpp) - _math.ceil((i - 1) * cpp))
        # Guarantee strictly increasing: at least 1 more than previous marginal
        prev_marginal = table[-1] - table[-2] if len(table) >= 2 else 0
        step_cost = max(step_cost, prev_marginal)
        table.append(table[-1] + step_cost)
    return table

STAFF_MIGHT_COST_TABLE = _build_staff_might_table()
STAFF_SELF_HEAL_SCALE = MAGIC_MIGHT_COST / 2
STAFF_RANGE_COST_PER_POINT = 5
UNLIMITED_USES_SCALING = 2.0
HEAL_SCALING_TOTAL_COST = 5
INTERFERENCE_STAFF_USES_SCALE = 0.25

BUFF_USER_SCALING = 2.0
BUFF_ALLY_SCALING = 4.0
RALLY_COST_SCALING = 1.0
RALLY_COST_NEG_SCALING = 0.5

VALUE_EFFECTS_CONFIG = {
    "HP Regeneration": {
        "cost_type": "table",
        "table_attribute": "HP",
        "min": 0,
        "max": 20,
        "weapon_types": ["all"],  # Can be used with any weapon type except Staff/Rod
        "desc": "Heals X HP at start of each turn when equipped",
        "scaling_note": "Cost follows HP growth table (increases non-linearly)"
    },
    "Rally after battle": {
        "cost_type": "rally",
        "min": -7,
        "max": 7,
        "weapon_types": ["all"],
        "desc": "Value 1 to 7 Rallies Allies, Value -1 to -7 Rallies Enemies",
        "stats_map": {1: "Str", 2: "Mag", 3: "Skl", 4: "Spd", 5: "Luk", 6: "Def", 7: "Res"}
    },
    "Change User HP after battle": {
        "cost_type": "asymmetric",
        "positive_cost_per_point": TEN_HEALTH_PERCENT_MOD,  # per 1%
        "negative_cost_per_point": TEN_DAMAGE_PERCENT_MOD,   # per 1%
        "min": -30,
        "max": 20,
        "weapon_types": ["all"],
        "desc": "Positive = %heal user (cost), Negative = %damage user (credit)"
    },
    "Change Target HP after battle": {
        "cost_type": "asymmetric",
        "positive_cost_per_point": TEN_DAMAGE_PERCENT_MOD,   # per 1%
        "negative_cost_per_point": TEN_HEALTH_PERCENT_MOD,  # per 1%
        "positive_is_credit": True,  # Healing target = credit
        "min": -20,
        "max": 30,
        "weapon_types": ["all"],
        "desc": "Positive = %heal target (credit), Negative = %damage target (cost)"
    },
    "Staff Self Heal": {
        "cost_type": "fixed",
        "cost_per_point": STAFF_SELF_HEAL_SCALE,
        "min": 0,
        "max": 30,
        "weapon_types": ["Staff", "Rod"],  # Only Staff/Rod weapons
        "desc": "Heals self when using staff"
    }
}

# ============================================================================
# FIXED EFFECTS CONFIG
# ============================================================================

FIXED_EFFECTS_CONFIG = {
    "Magic Weapon": {"cost": 0, "desc": "Changes damage to magic / Test on tomes"},
    "No Counter": {"cost": 50, "desc": "Neither user nor target can counter ☄️"},
    "Locktouch": {"cost": 1, "desc": "Untested / Opens doors and chests"},
    "Silver Weapon": {"cost": SILVER_WEAPON_COST_PHYSICAL, "desc": "Drops stats after battle / test in combination with Magic Weapon"},
    "S Rank Debuff": {"cost": S_RANK_DEBUFF_COST_PHYSICAL, "desc": "Halves Str or Mag after battle"},
    "Dual Weapon": {"cost": 12.05, "desc": "Reverses Weapon triangle"},
    "Brave Weapon": {"cost": 17.69, "desc": "Strike twice when attacking"},
    "Bold Weapon": {"cost": 0, "desc": "Cannot double"},
    "Bronze Weapon": {"cost": 0, "desc": "Cannot crit or activate skills"},
    "Crit Weapon": {"cost": 24.5, "desc": "Changes crit mod to x4"},
    "One Tap": {"cost": 0, "desc": "Doubles Might when initiating"},
    "Venge": {"cost": 0, "desc": "Doubles Might when attacked"},
    "Skillful": {"cost": 0, "desc": "Doubles Might when Skill is higher than targets"},
    "Sword Slayer": {"cost": 30.75, "desc": "Effective Damage against Swords"},
    "Lance Slayer": {"cost": 30.75, "desc": "Effective Damage against Lances"},
    "Axe Slayer": {"cost": 30.75, "desc": "Effective Damage against Axes"},
    "Tome Slayer": {"cost": 30.75, "desc": "Effective Damage against Tomes"},
    "Flier Slayer": {"cost": 1.71, "desc": "Effective Damage against Flier"},
    "Dragon Slayer": {"cost": 1.71, "desc": "Effective Damage against Dragons"},
    "Beast Slayer": {"cost": 1.71, "desc": "Effective Damage against Beast"},
    "Armor Slayer": {"cost": 1.71, "desc": "Effective Damage against Armor"},
    "Monster Slayer": {"cost": 14.14, "desc": "Effective Damage against Monster"},
    "Automaton Slayer": {"cost": 14.14, "desc": "Effective Damage against Automaton / unused & untested"},
    "Dragonstone Slayer": {"cost": 14.14, "desc": "Effective Damage against Dragonstone / unused & untested"},
    "Beaststone Slayer": {"cost": 14.14, "desc": "Effective Damage against Beaststone / unused & untested"},
    "Mounted Slayer": {"cost": 14.14, "desc": "Effective Damage against Mounted / unused & untested"},
    "Nosferatu": {"cost": 22.6, "desc": "Heals for half of the damage / activates no crit, no skills and no doubling"},
    "Acrobat": {"cost": round(16.43 * 0.75, 2), "desc": "All terrain costs 1 move / might be enough to have in inventory"},
    "No Terrain Bonus": {"cost": round((2.2 * 3 + 30 * 0.86 + 9.4 * 2 / 3) * 12 / 28, 2), "desc": "Negates terrain effects on both sides in battle"},
    "Debuff on Hit": {"cost": 0, "desc": "Debuffs like Daggers, Values are defined further below"},
    # "Mercy": {"cost": 0, "desc": "Enemy survives with 1 HP"},
    "Disable effective Damage": {"cost": 0, "desc": "Untested / Unknown effect"},
    "Medicine": {"cost": 0, "desc": "Used for Tonics / Might be pointless"},
    "Raider Effect": {"cost": 0.69, "desc": "Strips Clothes with WTA"},
    "Ineffective MT": {"cost": -6.6, "desc": "Reduces Might when used ineffectively"},
    "Ineffective Hit": {"cost": -6.45, "desc": "Reduces Hit when used ineffectively"},
    "Penetrate Dragonskin": {"cost": 1.78, "desc": "Reduces the targets Dragonskin effect"},
}

# ============================================================================
# STAFF EFFECTS CONFIG
# ============================================================================

STAFF_EFFECTS_CONFIG = {
    "Heal Scaling": {"cost": 5, "desc": "Only for Healing Staves, adds a Mag/3 scaling (Requires Recovery Staff)"},
    "Recovery Staff": {"cost": 0, "desc": "Healing Staves of all sorts"},
    "Interference Staff": {"cost": 0, "desc": "Offensive Staves"},
    "Special Staff": {"cost": 0, "desc": "AoE Staves and Bifröst. Also select Recovery Staff if healing"},
    "Buff User": {"cost": 0, "desc": "Only Healing Staves. Buffs user when used for the rest of the map / works like a tonic"},
    "Buff Ally": {"cost": 0, "desc": "Only Healing Staves. Buffs target when used for the rest of the map / works like a tonic"},
    "Unlimited Uses": {"cost": 0, "desc": f"Infinite item uses. Multiplies total staff cost by {UNLIMITED_USES_SCALING}x (after all other calculations)"},
    "Rescue": {"cost": 8.2, "desc": "Teleports an ally to an adjacent tile (Can't combine with Interference or Special, Test with Recovery)"},
    "Freeze": {"cost": 4.36, "desc": "Prevents enemy movement"},
    "Enfeeble": {"cost": 6.4, "desc": "Reduces enemy stats"},
    "Silence": {"cost": 3.73, "desc": "Prevents enemy from using magic"},
    "Hex": {"cost": 8.43, "desc": "Curses the enemy"},
    "Entrap": {"cost": 15.85, "desc": "Pulls enemy closer"},
    "AoE Healing": {"cost": 16.38, "desc": "Area of Effect healing (Requires Recovery and Special Staff)"},
    "Bifröst": {"cost": 67.50, "desc": "Revives fallen ally (Requires Special Staff)"},
}

# ============================================================================
# SKILL DATA LOADING
# ============================================================================

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

skill_data_load_error = False
try:
    with open(resource_path("skill_data.json"), "r", encoding="utf-8") as f:
        skill_data = json.load(f)
except FileNotFoundError:
    skill_data_load_error = True
    print("Error: 'skill_data.json' file not found.")
except json.JSONDecodeError:
    skill_data_load_error = True
    print("Error: Failed to parse 'skill_data.json'.")

# Pre-compute the scaling divisor from the raw costs in skill_data
_max_raw_skill_cost = max((v["cost"] for v in skill_data.values()), default=1)
_max_skill_name = max(skill_data, key=lambda k: skill_data[k]["cost"]) if skill_data else "N/A"
print(f"DEBUG: Highest raw skill cost = {_max_raw_skill_cost} ({_max_skill_name}), scales to MAX_SKILL_COST={MAX_SKILL_COST}")

def scaled_skill_cost(raw_cost):
    """Scale a raw skill cost to the 1–MAX_SKILL_COST range. Zero-cost skills stay at 0."""
    import math
    if raw_cost <= 0:
        return 0
    return max(1, math.ceil(raw_cost / _max_raw_skill_cost * MAX_SKILL_COST))

def skill_gate(name):
    """Gate tier (0-4) a skill requires; missing/unknown skills default to 0."""
    return skill_data.get(name, {}).get("gate", 0)

def eligible_slots(gate):
    """0-based slot indices that can hold a skill of the given gate tier."""
    return [i for i, g in enumerate(SKILL_SLOT_GATES) if g >= gate]

if skill_data_load_error:
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror("Missing Data", 
        "skill_data.json not found or invalid.\n\n"
        "This file is required and must be placed in the same folder as the program.\n"
        "The application will now exit.")
    sys.exit(1)

# ============================================================================
# IMPORT VERIFICATION HELPERS
# ============================================================================

def _verify_weapon_raw(weapon_data, budget=WEAPON_TOTAL_POINTS):
    """Data-only legality checks for a weapon dict (no UI/engine required).

    Inspects the raw file values, so forged out-of-range stats are caught even
    though loading would silently clamp them. Returns a list of issue strings."""
    issues = []
    stat_keys = [
        ("might", "Might"), ("hit", "Hit"), ("crit", "Crit"), ("avoid", "Avoid"),
        ("dodge", "Dodge"), ("mov", "Mov"),
        ("effective_speed_offensive", "Effective Speed Offensive"),
        ("effective_speed_defensive", "Effective Speed Defensive"),
        ("base_staff_exp", "Base Staff Exp"), ("uses", "Uses"),
    ]
    for key, name in stat_keys:
        if key not in weapon_data:
            continue
        val = weapon_data[key]
        if not isinstance(val, (int, float)):
            issues.append(f"{name} = {val!r} is not a number")
            continue
        lo, hi = WEAPON_STAT_MIN[name], WEAPON_STAT_MAX[name]
        if val < lo or val > hi:
            issues.append(f"{name} = {val} is outside the allowed range [{lo}, {hi}]")
    # Range validity
    wtype = weapon_data.get("type")
    rng = weapon_data.get("range")
    if wtype in ("Staff", "Rod"):
        try:
            n = int(rng)
            if n < 1 or n > 15:
                issues.append(f"Staff range {rng} is outside 1-15")
        except (TypeError, ValueError):
            issues.append(f"Staff range {rng!r} is not a valid number")
    elif rng is not None and rng not in WEAPON_RANGE_COSTS:
        issues.append(f"Range {rng!r} is not one of {list(WEAPON_RANGE_COSTS)}")
    # Claimed cost bounds
    tc = weapon_data.get("total_cost")
    if isinstance(tc, (int, float)) and tc > budget + 0.5:
        issues.append(f"Claimed cost {round(tc)} exceeds the {budget}-point budget")
    return issues


def _show_import_verification(parent, kind, name, file_version, issues, show_success=True):
    """Post-import review dialog. Always informational — never blocks the load.

    When show_success is False, stays silent on a clean result — used by the
    weapon-creator load paths so opening your own weapon doesn't nag you."""
    if not issues:
        if show_success:
            messagebox.showinfo(
                "Import Successful",
                f"{kind.capitalize()} '{name}' loaded successfully!", parent=parent)
        return
    header = ""
    if file_version and file_version != VERSION:
        header = (f"Note: this file was made in version {file_version} (current is "
                  f"{VERSION}); some differences may be version changes, not tampering.\n\n")
    body = "\n".join(f"  • {i}" for i in issues)
    messagebox.showwarning(
        "⚠ Verification — please review",
        f"The {kind} '{name}' was loaded, but the following values do not add up "
        f"and should be looked at / changed:\n\n{header}{body}",
        parent=parent)


def _safe_get(var, default=0):
    """tk var .get() that returns a default instead of raising on empty input."""
    try:
        return var.get()
    except (tk.TclError, ValueError):
        var.set(default)
        return default


def _make_int_vcmd(widget, allow_negative=True):
    """Return a (command, '%P') validatecommand pair that restricts typed input
    to integers. allow_negative=False also blocks the minus sign."""
    def _validate(new_val):
        if new_val == "":
            return True
        if allow_negative and new_val == "-":
            return True
        try:
            value = int(new_val)
        except ValueError:
            return False
        return allow_negative or value >= 0
    return (widget.register(_validate), "%P")


# ============================================================================
# SKILL SELECTION WINDOW
# ============================================================================

class Tooltip:
    """Shows a delayed tooltip near the widget it is bound to."""
    DELAY_MS = 100  # hover time before tooltip appears

    def __init__(self, widget, text, delay_ms=None):
        self.widget = widget
        self.text = text
        self._delay = delay_ms if delay_ms is not None else self.DELAY_MS
        self._after_id = None
        self._tip_win = None
        widget.bind("<Enter>", self._on_enter, add="+")
        widget.bind("<Leave>", self._on_leave, add="+")
        widget.bind("<ButtonPress>", self._on_leave, add="+")

    def _on_enter(self, event=None):
        self._cancel()
        self._after_id = self.widget.after(self._delay, self._show)

    def _on_leave(self, event=None):
        self._cancel()
        self._hide()

    def _cancel(self):
        if self._after_id:
            self.widget.after_cancel(self._after_id)
            self._after_id = None

    def _show(self):
        if self._tip_win or not self.text:
            return
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 4
        self._tip_win = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        # Keep tooltip inside screen horizontally
        tw.update_idletasks()
        sw = tw.winfo_screenwidth()
        tw_w = tw.winfo_reqwidth()
        if x + tw_w > sw - 10:
            x = sw - tw_w - 10
            tw.wm_geometry(f"+{x}+{y}")
        lbl = tk.Label(tw, text=self.text, justify="left",
                       background="#fffbe6", foreground="#1a1a1a",
                       relief="solid", borderwidth=1,
                       font=("TkDefaultFont", 9),
                       wraplength=340, padx=6, pady=4)
        lbl.pack()

    def _hide(self):
        if self._tip_win:
            self._tip_win.destroy()
            self._tip_win = None

    def update_text(self, text):
        self.text = text


class SkillSelectionWindow:
    def __init__(self, parent, callback, current_points, preselected=None):
        self.parent = parent
        self.callback = callback
        self.initial_points = current_points
        self.remaining_points = current_points
        self.points_var = tk.StringVar(value=str(int(self.remaining_points)))
        self.skill_widgets = {}        # skill name -> its button widget
        self.MAX_SKILLS = MAX_SKILLS
        # slots: the source of truth. Length MAX_SKILLS; each entry is a skill
        # name or None. `preselected` is the incoming slot list from the caller.
        slots = list(preselected) if preselected else []
        self.slots = (slots + [None] * MAX_SKILLS)[:MAX_SKILLS]
        self._original_slots = list(self.slots)   # for Cancel-revert
        self._after_id = None          # debounce handle for resize
        self._last_canvas_width = 0

        self.window = tk.Toplevel(parent)
        self.window.title("Skill Selection")
        self.window.minsize(680, 500)

        self.setup_ui()

    # ------------------------------------------------------------------ UI ---

    def setup_ui(self):
        if not skill_data:
            messagebox.showerror("No Skill Data",
                "Skill data could not be loaded.\nCannot display skills.")
            self.window.destroy()
            return

        # ── Fixed header ──────────────────────────────────────────────────────
        header = ttk.Frame(self.window, relief="groove", padding=(10, 6))
        header.pack(side="top", fill="x")

        # Points + counter row
        info_row = ttk.Frame(header)
        info_row.pack(fill="x", pady=(0, 4))
        ttk.Label(info_row, text="Remaining Points:",
                  font=("TkDefaultFont", 10, "bold")).pack(side="left")
        self.points_label = ttk.Label(info_row, textvariable=self.points_var,
                                      font=("TkDefaultFont", 10, "bold"),
                                      foreground="blue")
        self.points_label.pack(side="left", padx=(5, 20))
        self.skill_counter_var = tk.StringVar(value=f"Skills: 0/{self.MAX_SKILLS}")
        ttk.Label(info_row, textvariable=self.skill_counter_var,
                  font=("TkDefaultFont", 10)).pack(side="left")
        # System buttons on the right of the info row
        ttk.Button(info_row, text="Cancel",
                   command=self._cancel).pack(side="right", padx=5)
        ttk.Button(info_row, text="Reset",
                   command=self.reset_selection).pack(side="right", padx=5)
        ttk.Button(info_row, text="Confirm",
                   command=self.confirm_selection).pack(side="right", padx=5)

        # Search + group filter row
        filter_row = ttk.Frame(header)
        filter_row.pack(fill="x")
        ttk.Label(filter_row, text="Search:").pack(side="left")
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self._refresh_skills())
        self.search_entry = ttk.Entry(filter_row, textvariable=self.search_var, width=22)
        self.search_entry.pack(side="left", padx=(4, 16))

        ttk.Label(filter_row, text="Filter by group:").pack(side="left")
        all_groups = ["All"] + sorted({g for info in skill_data.values() for g in info["groups"]})
        self.group_var = tk.StringVar(value="All")
        self._group_values = all_groups
        self._group_dropdown_open = False
        self.group_btn = ttk.Button(filter_row, textvariable=self.group_var,
                                    width=22, command=self._toggle_group_dropdown)
        self.group_btn.pack(side="left", padx=(4, 0))

        ttk.Label(filter_row, text="Gate:").pack(side="left", padx=(16, 0))
        self.gate_var = tk.StringVar(value="All")
        gate_values = ["All"] + [str(g) for g in sorted({info.get("gate", 0) for info in skill_data.values()})]
        gate_cb = ttk.Combobox(filter_row, textvariable=self.gate_var, values=gate_values,
                               state="readonly", width=5)
        gate_cb.pack(side="left", padx=(4, 0))
        gate_cb.bind("<<ComboboxSelected>>", lambda e: self._refresh_skills())

        # Window-level keypress: jumps group filter, guards search entry focus
        self.window.bind("<KeyPress>",
            lambda e: self._group_filter_keypress_all(e), add="+")

        # ── Slots header (the 6 slots and their current skills) ───────────────
        self.slots_frame = ttk.Frame(header)
        self.slots_frame.pack(fill="x", pady=(6, 0))
        self._render_slot_header()

        # ── Scrollable skills area ────────────────────────────────────────────
        scroll_container = ttk.Frame(self.window)
        scroll_container.pack(side="top", fill="both", expand=True,
                               padx=10, pady=(6, 0))

        self.canvas = tk.Canvas(scroll_container, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(scroll_container, orient="vertical",
                                       command=self.canvas.yview)
        self.scroll_frame = ttk.Frame(self.canvas)

        self.scroll_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")))
        self._canvas_win = self.canvas.create_window(
            (0, 0), window=self.scroll_frame, anchor="nw")

        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Bind canvas resize to reflow columns (debounced)
        self.canvas.bind("<Configure>", self._on_canvas_configure)

        # Mouse-wheel scrolling
        self.canvas.bind("<Enter>",
            lambda e: self.canvas.bind_all("<MouseWheel>", self._on_mousewheel))
        self.canvas.bind("<Leave>",
            lambda e: self.canvas.unbind_all("<MouseWheel>"))

        # Initial render (after window is visible so canvas has a real width)
        self.window.update_idletasks()
        self._refresh_skills()

    # --------------------------------------------------------------- Events ---

    def _on_canvas_configure(self, event):
        """Debounce canvas resize → reflow checkboxes."""
        if abs(event.width - self._last_canvas_width) < 5:
            return
        self._last_canvas_width = event.width
        if self._after_id:
            self.window.after_cancel(self._after_id)
        self._after_id = self.window.after(120, self._refresh_skills)

    def _on_mousewheel(self, event):
        # Don't scroll the canvas if the event came from a spinbox or entry
        if isinstance(event.widget, (tk.Spinbox, ttk.Spinbox, tk.Entry, ttk.Entry)):
            return
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    # --------------------------------------------------- Skill display logic --

    def _toggle_group_dropdown(self):
        """Open or close the custom group filter dropdown."""
        if self._group_dropdown_open:
            self._close_group_dropdown()
        else:
            self._open_group_dropdown()

    def _open_group_dropdown(self):
        self._group_dropdown_open = True
        x = self.group_btn.winfo_rootx()
        y = self.group_btn.winfo_rooty() + self.group_btn.winfo_height()
        self._group_popup = tk.Toplevel(self.window)
        self._group_popup.wm_overrideredirect(True)
        self._group_popup.wm_geometry(f"+{x}+{y}")
        frame = ttk.Frame(self._group_popup, relief="solid", borderwidth=1)
        frame.pack(fill="both", expand=True)
        sb = ttk.Scrollbar(frame, orient="vertical")
        self._group_listbox = tk.Listbox(frame, yscrollcommand=sb.set,
                                         width=24, height=min(15, len(self._group_values)),
                                         font=("TkDefaultFont", 10),
                                         activestyle="dotbox", exportselection=False)
        sb.config(command=self._group_listbox.yview)
        for item in self._group_values:
            self._group_listbox.insert(tk.END, item)
        # Select current
        try:
            idx = self._group_values.index(self.group_var.get())
            self._group_listbox.selection_set(idx)
            self._group_listbox.see(idx)
        except ValueError:
            pass
        self._group_listbox.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        self._group_listbox.bind("<ButtonRelease-1>", self._on_group_select)
        self._group_listbox.bind("<Return>", self._on_group_select)
        self._group_listbox.bind("<Escape>", lambda e: self._close_group_dropdown())
        self._group_listbox.bind("<KeyPress>", self._on_group_listbox_key)
        self._group_popup.bind("<FocusOut>", lambda e: self._close_group_dropdown())
        self._group_listbox.focus_set()

    def _close_group_dropdown(self):
        self._group_dropdown_open = False
        if hasattr(self, "_group_popup") and self._group_popup.winfo_exists():
            self._group_popup.destroy()

    def _on_group_select(self, event=None):
        sel = self._group_listbox.curselection()
        if sel:
            self.group_var.set(self._group_values[sel[0]])
            self._refresh_skills()
        self._close_group_dropdown()

    def _on_group_listbox_key(self, event):
        """Letter-jump inside the open dropdown listbox."""
        key = event.char.lower()
        if not key or not key.isalpha():
            return
        current_sel = self._group_listbox.curselection()
        start = current_sel[0] if current_sel else 0
        n = len(self._group_values)
        for i in range(1, n + 1):
            idx = (start + i) % n
            if self._group_values[idx].lower().startswith(key):
                self._group_listbox.selection_clear(0, tk.END)
                self._group_listbox.selection_set(idx)
                self._group_listbox.see(idx)
                return

    def _group_filter_keypress_all(self, event):
        """Window-level keypress: jump group filter when dropdown is closed."""
        # Ignore if search entry has focus
        if hasattr(self, "search_entry") and self.window.focus_get() == self.search_entry:
            return
        # Ignore if our custom dropdown is open (it handles its own keys)
        if self._group_dropdown_open:
            return
        key = event.char.lower()
        if not key or not key.isalpha():
            return
        current = self.group_var.get()
        try:
            start = self._group_values.index(current)
        except ValueError:
            start = 0
        n = len(self._group_values)
        for i in range(1, n + 1):
            candidate = self._group_values[(start + i) % n]
            if candidate.lower().startswith(key):
                self.group_var.set(candidate)
                self._refresh_skills()
                return

    def _visible_skills(self):
        """Return ordered list of (skill, info) matching current filters."""
        query = self.search_var.get().strip().lower()
        group  = self.group_var.get()
        gate = getattr(self, "gate_var", None)
        gate = gate.get() if gate else "All"
        result = []
        for skill, info in skill_data.items():
            if query and query not in skill.lower():
                continue
            if group != "All" and group not in info["groups"]:
                continue
            if gate != "All" and str(info.get("gate", 0)) != gate:
                continue
            result.append((skill, info))
        return result

    def _min_item_width(self, skills):
        """Return the pixel width needed for the widest visible skill label."""
        if not skills:
            return 200
        # Measure text width using tkinter font metrics
        font = tkfont.nametofont("TkDefaultFont")
        # Checkbutton has indicator (~20px) + padding (~16px) on each side
        CHROME = 52
        widest = max(
            font.measure(f"{skill}  ({scaled_skill_cost(info['cost'])} pts)  [g{info.get('gate', 0)}]  → Slot 6")
            for skill, info in skills
        )
        return widest + CHROME

    def _columns_for_width(self, canvas_width, skills):
        """Fit as many columns as the canvas can hold for the widest label."""
        if not skills:
            return 1
        item_w = self._min_item_width(skills)
        cols = max(1, canvas_width // item_w)
        return int(cols)


    def _refresh_skills(self):
        """Rebuild the clickable skill grid to match current filters and width."""
        for w in self.scroll_frame.winfo_children():
            w.destroy()
        self.skill_widgets.clear()

        skills = self._visible_skills()
        canvas_w = self.canvas.winfo_width() or 600
        cols = self._columns_for_width(canvas_w, skills)
        for c in range(cols):
            self.scroll_frame.grid_columnconfigure(c, weight=1)

        for i, (skill, info) in enumerate(skills):
            col = i % cols
            row = i // cols
            gate = info.get("gate", 0)
            cost = scaled_skill_cost(info["cost"])
            slot = self._slot_of(skill)
            label = f"{skill}  ({cost} pts)  [g{gate}]"
            if slot is not None:
                label += f"  → Slot {slot + 1}"
            btn = ttk.Button(self.scroll_frame, text=label,
                             command=lambda s=skill, g=gate: self._open_slot_menu(s, g))
            btn.grid(row=row, column=col, sticky="ew", padx=8, pady=2)
            tip_parts = []
            if info.get("desc"):
                tip_parts.append(info["desc"])
            if info.get("groups"):
                tip_parts.append("Groups: " + ", ".join(info["groups"]))
            tip_parts.append(f"Gate {gate}")
            Tooltip(btn, "\n\n".join(tip_parts))
            self.skill_widgets[skill] = btn

        self.canvas.itemconfigure(self._canvas_win, width=canvas_w)
        self.update_points()
        self.update_skill_counter()

    # --------------------------------------------------- Slot assignment ------

    def _assigned_skills(self):
        return [s for s in self.slots if s]

    def _slot_of(self, skill):
        return self.slots.index(skill) if skill in self.slots else None

    def _projected_cost(self, skill, slot):
        sim = list(self.slots)
        cur = self._slot_of(skill)
        if cur is not None:
            sim[cur] = None
        sim[slot] = skill
        return sum(scaled_skill_cost(skill_data[s]["cost"]) for s in sim if s)

    def _open_slot_menu(self, skill, gate):
        """Pop a menu of the gate-eligible slots this skill may go into."""
        menu = tk.Menu(self.window, tearoff=0)
        current = self._slot_of(skill)
        if current is not None:
            menu.add_command(label=f"Remove from Slot {current + 1}",
                             command=lambda: self._clear_slot(current))
            menu.add_separator()
        added = 0
        for i in eligible_slots(gate):
            if self.slots[i] == skill:
                continue
            occ = self.slots[i]
            txt = (f"Slot {i + 1} · Chapter {SKILL_SLOT_CHAPTERS[i]}"
                   + ("  (free)" if occ is None else f"  (replace {occ})"))
            menu.add_command(label=txt, command=lambda idx=i: self._assign(skill, idx))
            added += 1
        if added == 0 and current is None:
            menu.add_command(label="No eligible slot for this gate", state="disabled")
        menu.tk_popup(self.window.winfo_pointerx(), self.window.winfo_pointery())

    def _assign(self, skill, slot):
        # No affordability block — over-budget is allowed (verified on export).
        cur = self._slot_of(skill)
        if cur is not None:
            self.slots[cur] = None
        self.slots[slot] = skill        # replaces any current occupant
        self._sync()

    def _clear_slot(self, idx):
        self.slots[idx] = None
        self._sync()

    def _sync(self):
        """Refresh this window and live-apply the slots to the main window."""
        self._refresh_all()
        self.callback(list(self.slots))

    def _refresh_all(self):
        self._render_slot_header()
        self._refresh_skills()

    def _render_slot_header(self):
        for w in self.slots_frame.winfo_children():
            w.destroy()
        for i in range(self.MAX_SKILLS):
            cell = ttk.Frame(self.slots_frame, relief="groove", padding=4)
            cell.grid(row=0, column=i, padx=2, sticky="nsew")
            self.slots_frame.grid_columnconfigure(i, weight=1)
            ttk.Label(cell, text=f"Slot {i + 1}",
                      font=("TkDefaultFont", 8, "bold")).pack(anchor="w")
            ttk.Label(cell, text=f"Chapter {SKILL_SLOT_CHAPTERS[i]}",
                      font=("TkDefaultFont", 7), foreground="gray").pack(anchor="w")
            sk = self.slots[i]
            if sk:
                rowf = ttk.Frame(cell)
                rowf.pack(fill="x")
                ttk.Label(rowf, text=sk, font=("TkDefaultFont", 8), foreground="blue",
                          wraplength=90, justify="left").pack(side="left")
                ttk.Button(rowf, text="✕", width=2,
                           command=lambda idx=i: self._clear_slot(idx)).pack(side="right")
            else:
                ttk.Label(cell, text="— empty —", font=("TkDefaultFont", 8),
                          foreground="gray").pack(anchor="w")

    # -------------------------------------------------- Points / counter ------

    def update_points(self):
        total = sum(scaled_skill_cost(skill_data[s]["cost"]) for s in self._assigned_skills())
        self.remaining_points = self.initial_points - total
        self.points_var.set(str(int(self.remaining_points)))
        self.points_label.configure(foreground="red" if self.remaining_points < 0 else "blue")

    def set_budget(self, budget):
        """Update the skills budget live (main window cost changed while open)."""
        self.initial_points = budget
        self.update_points()

    def update_skill_counter(self):
        self.skill_counter_var.set(f"Skills: {len(self._assigned_skills())}/{self.MAX_SKILLS}")

    def reset_selection(self):
        """Clear all slots, reset filters, and live-apply to the main window."""
        self.slots = [None] * self.MAX_SKILLS
        self.search_var.set("")
        self.group_var.set("All")
        if hasattr(self, "gate_var"):
            self.gate_var.set("All")
        self._sync()

    def confirm_selection(self):
        # Slots are already live-applied; just close.
        self.callback(list(self.slots))
        self.window.destroy()

    def _cancel(self):
        """Revert the main window to the slots from when this window opened."""
        self.callback(list(self._original_slots))
        self.window.destroy()


# ============================================================================
# CUSTOM WEAPON CREATOR
# ============================================================================

class CustomWeaponCreator:
    def __init__(self, parent, callback, initial_weapon_data=None,
                 total_points=WEAPON_TOTAL_POINTS, stat_costs=None, kind_label="Weapon"):
        print("CustomWeaponCreator  init starting...")
        self.parent = parent
        self.callback = callback
        self.weapon_points = total_points
        self.remaining_weapon_points = total_points
        self.stat_costs = dict(stat_costs) if stat_costs else dict(WEAPON_STAT_COSTS)
        self.kind_label = kind_label

        self.window = tk.Toplevel(parent)
        self.window.title(f"{kind_label} Creator - Fire Emblem Fates Tool v{VERSION}")
        self.window.geometry("750x650")
        self.window.minsize(650, 550)

        self.fixed_effects = FIXED_EFFECTS_CONFIG.copy()
        self.staff_effects = STAFF_EFFECTS_CONFIG.copy()
        self.value_effects = VALUE_EFFECTS_CONFIG.copy()

        self.effect_value_var = tk.IntVar(value=0)
        self.effect_value_cost_var = tk.StringVar(value="0")

        self.weapon_data = {
            "name": "", "type": "Sword", "custom_type": "",
            "might": 0, "hit": 0, "crit": 0, "avoid": 0, "dodge": 0, "mov": 0,
            "effective_speed_offensive": 0, "effective_speed_defensive": 0,
            "range": "1", "fixed_effects": [], "value_effects": [],
            "effect_value": 0, "description": ""
        }

        # State tracking
        # TODO(remove pending feedback): magic_weapon_active is currently write-only
        # since Magic Weapon was decoupled from costs. Kept until the design is confirmed.
        self.magic_weapon_active = False
        self.silver_weapon_active = False
        self.silver_weapon_adjusted_cost = SILVER_WEAPON_COST_PHYSICAL
        self.s_rank_debuff_active = False
        self.s_rank_debuff_adjusted_cost = S_RANK_DEBUFF_COST_PHYSICAL

        self.one_tap_active = False
        self.venge_active = False
        self.skillful_active = False
        self.flier_slayer_active = False
        self.dragon_slayer_active = False
        self.beast_slayer_active = False
        self.armor_slayer_active = False

        self.nosferatu_active = False
        self.bronze_was_forced = False
        self.bold_was_forced = False

        # Staff tracking
        self.staff_frame_visible = False
        self.staff_effect_vars = {}
        self.staff_effect_cost_labels = {}
        self.staff_effect_note_labels = {}
        self.staff_effect_note_widgets = {}
        self.recovery_staff_selected = False
        self.interference_staff_selected = False
        self.special_staff_selected = False
        self.staff_warning_label = None
        self.heal_scaling_checkbox = None
        self.rescue_selected = False
        self.aoe_healing_selected = False
        self.bifrost_selected = False
        self.enfeeble_was_active = False
        self.unlimited_uses_active = False

        # Buff tracking
        self.buff_user_active = False
        self.buff_ally_active = False
        
        self.value_effect_desc_vars = {}
        self.value_effect_desc_labels = {}
        
        self.setup_ui()
        self.update_value_effects_availability()
        if initial_weapon_data:
            self.window.after(50, lambda: self._load_weapon_data(initial_weapon_data))

    # ------------------------------------------------------------------------
    # UI Setup Methods
    # ------------------------------------------------------------------------

    def setup_ui(self):
        # Weapon Creation
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Fixed header — always visible, never scrolls
        header_frame = ttk.Frame(main_frame, relief="groove", padding=(10, 6))
        header_frame.pack(side="top", fill="x", pady=(0, 6))
        ttk.Label(header_frame, text="Available Points:",
                  font=("TkDefaultFont", 11, "bold")).pack(side="left")
        self.points_var = tk.StringVar(value=str(round(self.remaining_weapon_points)))
        self.points_label = ttk.Label(header_frame, textvariable=self.points_var,
                                      font=("TkDefaultFont", 11, "bold"), foreground="blue")
        self.points_label.pack(side="left", padx=(5, 4))
        ttk.Label(header_frame, text=f"/ {self.weapon_points}",
                  font=("TkDefaultFont", 11)).pack(side="left", padx=(0, 20))
        # System buttons in header
        self.reset_button = ttk.Button(header_frame, text="Reset", command=self.reset_weapon,
                                       width=28)
        self.reset_button.pack(side="right", padx=5)
        self.reset_confirmation_needed = False
        ttk.Button(header_frame, text="Cancel", command=self.window.destroy).pack(side="right", padx=5)
        ttk.Button(header_frame, text="Import Weapon", command=self.import_weapon).pack(side="right", padx=5)
        ttk.Button(header_frame, text="Export Weapon", command=self.export_weapon).pack(side="right", padx=5)
        ttk.Button(header_frame, text="Create Weapon", command=self.create_weapon).pack(side="right", padx=5)

        # Scrollable content area below the header
        scroll_container = ttk.Frame(main_frame)
        scroll_container.pack(side="top", fill="both", expand=True)

        canvas = tk.Canvas(scroll_container)
        scrollbar = ttk.Scrollbar(scroll_container, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Mousewheel scrolling
        def _weapon_scroll(ev):
            if isinstance(ev.widget, (tk.Spinbox, ttk.Spinbox, tk.Entry, ttk.Entry)):
                return
            canvas.yview_scroll(int(-1 * (ev.delta / 120)), "units")
        canvas.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", _weapon_scroll))
        canvas.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))

        self.scrollable_frame.columnconfigure(0, weight=1)

        self.setup_overview_frame()
        self.setup_staff_effects()
        self.setup_stats_frame()
        self.setup_fixed_effects_frame()
        self.setup_value_effects_frame()
        self.setup_debuff_frame()
        self.setup_buff_frame()
        self.setup_description_frame()

    def setup_overview_frame(self):
        frame = ttk.LabelFrame(self.scrollable_frame, text="Weapon Overview", padding=10)
        frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)

        # Row 0: Weapon Name
        ttk.Label(frame, text="Weapon Name:").grid(row=0, column=0, sticky="w", pady=2)
        self.name_entry = ttk.Entry(frame, width=30)
        self.name_entry.grid(row=0, column=1, sticky="ew", pady=2, padx=5)
        self.name_entry.bind("<KeyRelease>", self.on_name_change)

        # Row 1: Weapon Type
        ttk.Label(frame, text="Weapon Type:").grid(row=1, column=0, sticky="w", pady=2)
        weapon_types = ["Sword", "Katana", "Lance", "Naginata", "Axe", "Club", "Tome", "Scroll",
                        "Dagger", "Shuriken", "Bow", "Yumi", "Staff", "Rod", "Dragonstone", "Beaststone", "Other"]
        self.type_combobox = ttk.Combobox(frame, values=weapon_types, state="readonly", width=27)
        self.type_combobox.set("Sword")
        self.type_combobox.grid(row=1, column=1, sticky="ew", pady=2, padx=5)
        self.type_combobox.bind("<<ComboboxSelected>>", self.on_type_change)

        # Row 2: Custom Type (hidden by default)
        self.custom_type_frame = ttk.Frame(frame)
        self.custom_type_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=2)
        ttk.Label(self.custom_type_frame, text="Custom Type:").pack(side="left", padx=(0, 5))
        self.custom_type_entry = ttk.Entry(self.custom_type_frame, width=20)
        self.custom_type_entry.pack(side="left")
        self.custom_type_entry.bind("<KeyRelease>", self.on_custom_type_change)
        self.custom_type_frame.grid_remove()

        # Row 3: Weapon Hint (for Dagger/Shuriken)
        self.weapon_hint_var = tk.StringVar(value="")
        self.weapon_hint_label = ttk.Label(frame, textvariable=self.weapon_hint_var, foreground="gray")
        self.weapon_hint_label.grid(row=3, column=0, columnspan=2, sticky="w", pady=2)

        # Row 4: INFO NOTE (ADD THIS)
        info_note_frame = ttk.Frame(frame)
        info_note_frame.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(5, 5))
        
        info_note = (
            "ℹ Note: The weapon you are building here is the S rank version of it.\n"
            "  You will receive a scaled down version ingame starting with E rank.\n"
            "  Once you achieve a higher proficiency rank, you receive the next upgrade in My Castle.\n"
            "  Weapons (not Staves/Rods) get replaced. Old versions of Staves and Rods are kept, unless you have Unlimited Uses."
        )
        info_label = ttk.Label(info_note_frame, text=info_note, foreground="blue", 
                               font=('TkDefaultFont', 8), justify="left")
        info_label.pack(anchor="w")



    def _fmt_cost(self, value):
        """Round a cost value to nearest integer for display."""
        return str(round(value))

    def _int_vcmd(self):
        return _make_int_vcmd(self.window)

    def setup_stats_frame(self):
        self.stats_frame = ttk.LabelFrame(self.scrollable_frame, text="Weapon Stats", padding=10)
        self.stats_frame.grid(row=3, column=0, sticky="ew", padx=5, pady=5)

        for widget in self.stats_frame.winfo_children():
            widget.destroy()

        self.weapon_stats = {}
        regular_stats = ["Might", "Hit", "Crit", "Avoid", "Dodge", "Mov",
                         "Effective Speed Offensive", "Effective Speed Defensive"]
        staff_stats = ["Base Staff Exp", "Uses"]

        for stat in regular_stats + staff_stats:
            self.weapon_stats[stat] = {
                "min": WEAPON_STAT_MIN[stat],
                "max": WEAPON_STAT_MAX[stat],
                "cost_per_point": self.stat_costs[stat],
                "base": WEAPON_STAT_BASE[stat]
            }

        headers = ["Stat", "Value", "Cost", "Range", "Notes"]
        for col, header in enumerate(headers):
            ttk.Label(self.stats_frame, text=header, font=('TkDefaultFont', 9, 'bold')).grid(
                row=0, column=col, padx=5, pady=2)

        self.stat_vars = {}
        self.stat_spinboxes = {}

        for i, (stat, info) in enumerate(self.weapon_stats.items()):
            row = i + 1

            stat_label = ttk.Label(self.stats_frame, text=f"{stat}:")
            stat_label.grid(row=row, column=0, sticky="w", padx=5, pady=2)

            var = tk.IntVar(value=info["base"])
            _vcmd = self._int_vcmd()
            _inc = 5 if stat in WEAPON_STAT_INCREMENT_5 else 1
            spin = ttk.Spinbox(self.stats_frame, from_=info["min"], to=info["max"],
                               increment=_inc, textvariable=var, width=8,
                               command=lambda s=stat: self.on_stat_change(s),
                               validate="key", validatecommand=_vcmd)
            spin.grid(row=row, column=1, padx=5, pady=2)
            spin.bind("<FocusOut>", lambda e, s=stat: self.validate_stat(s))

            cost_var = tk.StringVar(value="0")
            ttk.Label(self.stats_frame, textvariable=cost_var, width=8).grid(row=row, column=2, padx=5, pady=2)

            range_info = f"[{info['min']} to {info['max']}]"
            ttk.Label(self.stats_frame, text=range_info, foreground="gray").grid(row=row, column=3, padx=5, pady=2)

            note_var = tk.StringVar(value="")
            ttk.Label(self.stats_frame, textvariable=note_var, foreground="blue", font=('TkDefaultFont', 8)).grid(
                row=row, column=4, sticky="w", padx=5, pady=2)

            self.stat_vars[stat] = {"value": var, "cost": cost_var, "note": note_var, "label": stat_label, "spin": spin}
            self.stat_spinboxes[stat] = spin

        # Range selection
        range_row = len(self.weapon_stats) + 1
        ttk.Label(self.stats_frame, text="Range:").grid(row=range_row, column=0, sticky="w", padx=5, pady=2)
        self.range_var = tk.StringVar(value="1")
        self.range_combobox = ttk.Combobox(self.stats_frame, textvariable=self.range_var, state="readonly", width=8)
        self.range_combobox.grid(row=range_row, column=1, padx=5, pady=2)
        self.range_combobox.bind("<<ComboboxSelected>>", self.on_range_change)

        self.range_cost_var = tk.StringVar(value="0")
        ttk.Label(self.stats_frame, textvariable=self.range_cost_var, width=8).grid(row=range_row, column=2, padx=5, pady=2)

        self.range_info_var = tk.StringVar(value="Select weapon range")
        ttk.Label(self.stats_frame, textvariable=self.range_info_var, foreground="gray").grid(
            row=range_row, column=3, padx=5, pady=2)

        self.range_note_var = tk.StringVar(value="")
        ttk.Label(self.stats_frame, textvariable=self.range_note_var, foreground="blue", font=('TkDefaultFont', 8)).grid(
            row=range_row, column=4, sticky="w", padx=5, pady=2)

        self.update_range_options()
        self.update_staff_stats_state(False)
        self.update_might_cost_for_staff()
        self.update_might_stat_state()
        self.update_hit_stat_state()
        self.update_interference_effects_state()

    def setup_fixed_effects_frame(self):
        self.fixed_effects_frame = ttk.LabelFrame(self.scrollable_frame, text="Fixed Effects", padding=10)
        self.fixed_effects_frame.grid(row=4, column=0, sticky="ew", padx=5, pady=5)

        self.fixed_effects_container = ttk.Frame(self.fixed_effects_frame)
        self.fixed_effects_container.pack(fill="x", expand=True)

        for col, weight, minsize in [(0, 2, 200), (1, 0, 100), (2, 4, 400), (3, 2, 300)]:
            self.fixed_effects_container.columnconfigure(col, weight=weight, minsize=minsize)

        headers = ["Effect", "Cost", "Description", "Notes"]
        for col, header in enumerate(headers):
            ttk.Label(self.fixed_effects_container, text=header, font=('TkDefaultFont', 9, 'bold')).grid(
                row=0, column=col, sticky="w", padx=5, pady=2)

        self.fixed_effect_vars = {}
        self.fixed_effect_cost_labels = {}
        self.fixed_effect_note_labels = {}
        self.fixed_effect_checkbuttons = {}

        for i, (effect, info) in enumerate(FIXED_EFFECTS_CONFIG.items()):
            row = i + 1

            var = tk.BooleanVar()
            chk = ttk.Checkbutton(self.fixed_effects_container, text=effect, variable=var,
                                  command=lambda e=effect, v=var: self.on_fixed_effect_toggle(e, v))
            chk.grid(row=row, column=0, sticky="w", padx=5, pady=2)

            cost_label = ttk.Label(self.fixed_effects_container, text=self._fmt_cost(info['cost']), foreground="blue")
            cost_label.grid(row=row, column=1, sticky="w", padx=5, pady=2)

            desc_label = ttk.Label(self.fixed_effects_container, text=info['desc'], foreground="gray",
                                   font=('TkDefaultFont', 8), wraplength=400)
            desc_label.grid(row=row, column=2, sticky="w", padx=5, pady=2)

            note_var = tk.StringVar(value="")
            ttk.Label(self.fixed_effects_container, textvariable=note_var, foreground="green",
                      font=('TkDefaultFont', 8)).grid(row=row, column=3, sticky="w", padx=5, pady=2)

            self.fixed_effect_vars[effect] = var
            self.fixed_effect_cost_labels[effect] = cost_label
            self.fixed_effect_note_labels[effect] = note_var
            self.fixed_effect_checkbuttons[effect] = chk

        self.update_fixed_effects_visibility()
        self._update_ineffective_state()

    def setup_value_effects_frame(self):
        self.value_effects_frame = ttk.LabelFrame(self.scrollable_frame, text="Value Effects", padding=10)
        self.value_effects_frame.grid(row=5, column=0, sticky="ew", padx=5, pady=5)

        canvas = tk.Canvas(self.value_effects_frame)
        scrollbar = ttk.Scrollbar(self.value_effects_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Shared Value Control at top
        value_control_frame = ttk.Frame(scrollable_frame)
        value_control_frame.grid(row=0, column=0, columnspan=7, sticky="ew", pady=5, padx=5)
        
        ttk.Label(value_control_frame, text="Shared Effect Value:", font=('TkDefaultFont', 9, 'bold')).pack(side="left")
        _vcmd = self._int_vcmd()
        self.effect_value_spin = ttk.Spinbox(value_control_frame, from_=-30, to=30, textvariable=self.effect_value_var,
                                             width=6, command=self.on_effect_value_change,
                                             validate="key", validatecommand=_vcmd)
        self.effect_value_spin.pack(side="left", padx=5)
        self.effect_value_spin.bind("<FocusOut>", lambda e: self.on_effect_value_change())

        # Total cost display
        self.effect_value_total_cost_var = tk.StringVar(value="0")
        ttk.Label(value_control_frame, text="Total Cost:", font=('TkDefaultFont', 9, 'bold')).pack(side="left", padx=(20, 5))
        ttk.Label(value_control_frame, textvariable=self.effect_value_total_cost_var, font=('TkDefaultFont', 9, 'bold'),
                  foreground="green").pack(side="left")
        ttk.Label(value_control_frame, text="pts", foreground="gray").pack(side="left")

        # Add Staff/Rod note (initially hidden)
        self.staff_value_note_var = tk.StringVar(value="")
        staff_note_label = ttk.Label(value_control_frame, textvariable=self.staff_value_note_var, 
                                      foreground="orange", font=('TkDefaultFont', 8))
        staff_note_label.pack(side="left", padx=(10, 0))

        ttk.Separator(scrollable_frame, orient='horizontal').grid(row=1, column=0, columnspan=7, sticky="ew", pady=10, padx=5)

        # Headers - New order: Effect, Min, Next -1 Cost, Current Cost, Next +1 Cost, Max, Description
        headers = ["Effect", "Min", "Next -1 Cost", "Current Cost", "Next +1 Cost", "Max", "Description"]
        for col, header in enumerate(headers):
            ttk.Label(scrollable_frame, text=header, font=('TkDefaultFont', 9, 'bold')).grid(
                row=2, column=col, sticky="w", padx=5, pady=2)

        self.value_effect_vars = {}
        self.value_effect_current_cost_vars = {}
        self.value_effect_next_plus_cost_vars = {}
        self.value_effect_next_minus_cost_vars = {}
        self.value_effect_cost_label_widgets = {}

        row = 3
        for effect, info in VALUE_EFFECTS_CONFIG.items():
            var = tk.BooleanVar()
            chk = ttk.Checkbutton(scrollable_frame, text=effect, variable=var,
                                  command=lambda e=effect, v=var: self.on_value_effect_toggle(e, v))
            chk.grid(row=row, column=0, sticky="w", padx=5, pady=2)
            var.widget = chk  # Store widget reference for enabling/disabling
            
            # Min value label
            min_label = ttk.Label(scrollable_frame, text=str(info.get('min', 0)), foreground="gray", width=5)
            min_label.grid(row=row, column=1, padx=5, pady=2)

            # Next -1 Cost (cost to decrease by 1)
            next_minus_cost_var = tk.StringVar(value="0")
            next_minus_label = ttk.Label(scrollable_frame, textvariable=next_minus_cost_var, foreground="orange", width=10)
            next_minus_label.grid(row=row, column=2, padx=5, pady=2)

            # Current Cost
            current_cost_var = tk.StringVar(value="0")
            current_label = ttk.Label(scrollable_frame, textvariable=current_cost_var, foreground="blue", width=10)
            current_label.grid(row=row, column=3, padx=5, pady=2)

            # Next +1 Cost
            next_plus_cost_var = tk.StringVar(value="0")
            next_plus_label = ttk.Label(scrollable_frame, textvariable=next_plus_cost_var, foreground="green", width=10)
            next_plus_label.grid(row=row, column=4, padx=5, pady=2)

            # Max value label
            max_label = ttk.Label(scrollable_frame, text=str(info.get('max', 100)), foreground="gray", width=5)
            max_label.grid(row=row, column=5, padx=5, pady=2)
            
            # Description - make it wider and store for updates
            desc_var = tk.StringVar(value=info['desc'])
            desc_label = ttk.Label(scrollable_frame, textvariable=desc_var, foreground="gray", 
                                   font=('TkDefaultFont', 8), wraplength=400, justify="left")
            desc_label.grid(row=row, column=6, sticky="w", padx=5, pady=2)

            # Store both the variable AND the label widget for color changes
            self.value_effect_desc_vars[effect] = desc_var
            self.value_effect_desc_labels[effect] = desc_label  # Add this line

            self.value_effect_vars[effect] = var
            self.value_effect_current_cost_vars[effect] = current_cost_var
            self.value_effect_cost_label_widgets[effect] = current_label
            self.value_effect_next_plus_cost_vars[effect] = next_plus_cost_var
            self.value_effect_next_minus_cost_vars[effect] = next_minus_cost_var
            
            # Store info for cost calculation
            self.value_effect_vars[effect].info = info
            
            row += 1

        # Add note for HP Regeneration scaling
        note_frame = ttk.Frame(scrollable_frame)
        note_frame.grid(row=row, column=0, columnspan=7, sticky="w", pady=(10, 0), padx=5)
        ttk.Label(note_frame, text="* HP Regeneration cost follows the HP growth table (increases non-linearly with each point)",
                  foreground="gray", font=('TkDefaultFont', 8)).pack(side="left")

        scrollable_frame.columnconfigure(0, weight=1)
        scrollable_frame.columnconfigure(6, weight=2)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def setup_debuff_frame(self):
        self.debuff_frame = ttk.LabelFrame(self.scrollable_frame, text="Debuff Effects", padding=10)
        self.debuff_frame.grid(row=6, column=0, sticky="ew", padx=5, pady=5)
        self.debuff_frame.grid_remove()

        ttk.Label(self.debuff_frame, text="Debuffs applied on hit:", font=('TkDefaultFont', 10, 'bold')).grid(
            row=0, column=0, columnspan=5, sticky="w", pady=5)
        ttk.Label(self.debuff_frame, text="(Positive values = enemy stat reduction)", foreground="gray",
                  font=('TkDefaultFont', 8)).grid(row=1, column=0, columnspan=5, sticky="w", pady=(0, 5))

        headers = ["Stat", "Value (0-7)", "Next Cost", "Total Cost"]
        for col, header in enumerate(headers):
            ttk.Label(self.debuff_frame, text=header, font=('TkDefaultFont', 9, 'bold')).grid(
                row=2, column=col, sticky="w", padx=5)

        self.debuff_vars = {}
        self.debuff_cost_vars = {}
        self.debuff_next_cost_vars = {}

        for i, (stat, info) in enumerate(DEBUFF_COSTS.items()):
            row = i + 3

            ttk.Label(self.debuff_frame, text=f"{stat}:").grid(row=row, column=0, sticky="w", padx=5)

            var = tk.IntVar(value=0)
            _vcmd = self._int_vcmd()
            spin = ttk.Spinbox(self.debuff_frame, from_=0, to=DEBUFF_MAX[stat], textvariable=var, width=5,
                               command=lambda s=stat: self.update_debuff_cost(s),
                               validate="key", validatecommand=_vcmd)
            spin.grid(row=row, column=1, padx=5)
            spin.bind("<FocusOut>", lambda e, s=stat: self.update_debuff_cost(s))

            # Next Cost: marginal cost of the next step, starts at cost of step 1
            next_cost_var = tk.StringVar(value=str(round(info)))
            ttk.Label(self.debuff_frame, textvariable=next_cost_var, foreground="blue").grid(row=row, column=2, padx=5)

            cost_var = tk.StringVar(value="0")
            ttk.Label(self.debuff_frame, textvariable=cost_var, foreground="green").grid(row=row, column=3, padx=5)

            self.debuff_vars[stat] = {"var": var}
            self.debuff_cost_vars[stat] = cost_var
            self.debuff_next_cost_vars[stat] = next_cost_var

        ttk.Separator(self.debuff_frame, orient='horizontal').grid(row=len(DEBUFF_COSTS) + 3, column=0, columnspan=5, sticky="ew", pady=10)

        ttk.Label(self.debuff_frame, text="Total Debuff Cost:", font=('TkDefaultFont', 9, 'bold')).grid(
            row=len(DEBUFF_COSTS) + 4, column=2, sticky="e", padx=5)

        self.total_debuff_cost_var = tk.StringVar(value="0")
        ttk.Label(self.debuff_frame, textvariable=self.total_debuff_cost_var, font=('TkDefaultFont', 9, 'bold'),
                  foreground="green").grid(row=len(DEBUFF_COSTS) + 4, column=3, sticky="w", padx=5)

        footnote_frame = ttk.Frame(self.debuff_frame)
        footnote_frame.grid(row=len(DEBUFF_COSTS) + 5, column=0, columnspan=5, sticky="w", pady=(10, 0))
        ttk.Label(footnote_frame, text="* For Defense and Resistance, only the higher cost is applied",
                  foreground="gray", font=('TkDefaultFont', 8)).pack(side="left")

    def setup_buff_frame(self):
        self.buff_frame = ttk.LabelFrame(self.scrollable_frame, text="Buff Effects", padding=10)
        self.buff_frame.grid(row=7, column=0, sticky="ew", padx=5, pady=5)
        self.buff_frame.grid_remove()

        buff_stats = ["Strength", "Magic", "Skill", "Speed", "Luck", "Defense", "Resistance"]

        ttk.Label(self.buff_frame, text="Stats buffed on use (fixed values, work like tonics)",
                  font=('TkDefaultFont', 10, 'bold')).grid(row=0, column=0, columnspan=len(buff_stats) + 1, sticky="w", pady=5)

        # Row 1: Stat names
        ttk.Label(self.buff_frame, text="Stat", font=('TkDefaultFont', 9, 'bold')).grid(row=1, column=0, padx=5, pady=2)
        for col, stat in enumerate(buff_stats, 1):
            ttk.Label(self.buff_frame, text=stat, font=('TkDefaultFont', 9, 'bold')).grid(row=1, column=col, padx=5, pady=2)

        # Row 2: Checkboxes
        ttk.Label(self.buff_frame, text="Buff?", font=('TkDefaultFont', 9, 'bold')).grid(row=2, column=0, padx=5, pady=2)
        self.buff_checkboxes = {}
        for col, stat in enumerate(buff_stats, 1):
            var = tk.BooleanVar()
            chk = ttk.Checkbutton(self.buff_frame, variable=var, command=lambda s=stat: self.update_buff_cost(s))
            chk.grid(row=2, column=col, padx=5, pady=2)
            self.buff_checkboxes[stat] = var

        # Row 3: Cost labels
        ttk.Label(self.buff_frame, text="Cost", font=('TkDefaultFont', 9, 'bold')).grid(row=3, column=0, padx=5, pady=2)
        self.buff_cost_labels = {}
        for col, stat in enumerate(buff_stats, 1):
            cost_var = tk.StringVar(value="0")
            ttk.Label(self.buff_frame, textvariable=cost_var, foreground="green").grid(row=3, column=col, padx=5, pady=2)
            self.buff_cost_labels[stat] = cost_var

        # Row 4: Total buff cost display
        ttk.Separator(self.buff_frame, orient='horizontal').grid(row=4, column=0, columnspan=len(buff_stats) + 1, sticky="ew", pady=10)

        ttk.Label(self.buff_frame, text="Total Buff Cost:", font=('TkDefaultFont', 9, 'bold')).grid(
            row=5, column=len(buff_stats) - 1, sticky="e", padx=5)

        self.total_buff_cost_var = tk.StringVar(value="0")
        ttk.Label(self.buff_frame, textvariable=self.total_buff_cost_var, font=('TkDefaultFont', 9, 'bold'),
                  foreground="green").grid(row=5, column=len(buff_stats), sticky="w", padx=5)

    def setup_description_frame(self):
        desc_frame = ttk.LabelFrame(self.scrollable_frame, text="Weapon Description", padding=10)
        desc_frame.grid(row=8, column=0, sticky="ew", padx=5, pady=5)
        self.desc_text = scrolledtext.ScrolledText(desc_frame, height=3, wrap=tk.WORD)
        self.desc_text.pack(fill="x", expand=True)
        self.desc_text.bind("<KeyRelease>", self.on_desc_change)

    def setup_staff_effects(self):
        self.staff_frame = ttk.LabelFrame(self.scrollable_frame, text="Staff/Rod Effects", padding=10)

        self.staff_container = ttk.Frame(self.staff_frame)
        self.staff_container.pack(fill="x", expand=True)

        for col, weight, minsize in [(0, 2, 200), (1, 0, 100), (2, 4, 400), (3, 2, 300)]:
            self.staff_container.columnconfigure(col, weight=weight, minsize=minsize)

        headers = ["Effect", "Cost", "Description", "Notes"]
        for col, header in enumerate(headers):
            ttk.Label(self.staff_container, text=header, font=('TkDefaultFont', 9, 'bold')).grid(
                row=0, column=col, sticky="w", padx=5, pady=2)

        self.interference_dependent_effects = ["Freeze", "Enfeeble", "Silence", "Hex", "Entrap"]
        self.special_dependent_effects = ["Bifröst"]
        self.aoe_healing_effects = ["AoE Healing"]

        effects = list(self.staff_effects.items())
        current_row = 1
        warning_row = None

        for effect, info in effects:
            if effect == "Rescue":
                if warning_row is None:
                    self.staff_warning_label = ttk.Label(self.staff_container,
                        text="⚠ WARNING: You must select a staff type!", foreground="red",
                        font=('TkDefaultFont', 9, 'bold'))
                    self.staff_warning_label.grid(row=current_row, column=0, columnspan=4, sticky="w", padx=5, pady=5)
                    warning_row = current_row
                    current_row += 1

                ttk.Label(self.staff_container, text="").grid(row=current_row, column=0, columnspan=4, pady=2)
                current_row += 1

                separator = ttk.Separator(self.staff_container, orient='horizontal')
                separator.grid(row=current_row, column=0, columnspan=4, sticky="ew", pady=5)
                current_row += 1

            var = tk.BooleanVar()
            chk = ttk.Checkbutton(self.staff_container, text=effect, variable=var,
                                  command=lambda e=effect, v=var: self.on_staff_effect_toggle(e, v))
            chk.grid(row=current_row, column=0, sticky="w", padx=5, pady=2)

            if effect == "Heal Scaling":
                self.heal_scaling_checkbox = chk

            cost_label = ttk.Label(self.staff_container, text=self._fmt_cost(info['cost']), foreground="blue")
            cost_label.grid(row=current_row, column=1, sticky="w", padx=5, pady=2)

            desc_label = ttk.Label(self.staff_container, text=info['desc'], foreground="gray", font=('TkDefaultFont', 8))
            desc_label.grid(row=current_row, column=2, sticky="w", padx=5, pady=2)

            note_var = tk.StringVar(value="")
            note_label = ttk.Label(self.staff_container, textvariable=note_var, foreground="green", font=('TkDefaultFont', 8))
            note_label.grid(row=current_row, column=3, sticky="w", padx=5, pady=2)

            self.staff_effect_vars[effect] = var
            self.staff_effect_cost_labels[effect] = cost_label
            self.staff_effect_note_labels[effect] = note_var
            self.staff_effect_note_widgets[effect] = note_label

            if effect in self.interference_dependent_effects:
                chk.state(['disabled'])
                note_var.set("Requires Interference Staff")
            elif effect in self.special_dependent_effects:
                chk.state(['disabled'])
                note_var.set("Requires Special Staff")
            elif effect in self.aoe_healing_effects:
                chk.state(['disabled'])
                note_var.set("Requires Recovery AND Special Staff")

            current_row += 1

        if warning_row is None:
            self.staff_warning_label = ttk.Label(self.staff_container,
                text="⚠ WARNING: You must select a staff type!", foreground="red",
                font=('TkDefaultFont', 9, 'bold'))
            self.staff_warning_label.grid(row=current_row, column=0, columnspan=4, sticky="w", padx=5, pady=5)

        if self.heal_scaling_checkbox:
            self.heal_scaling_checkbox.state(['disabled'])
            self.staff_effect_note_labels["Heal Scaling"].set("Requires Recovery Staff")

        self.staff_frame.grid_remove()

    # ------------------------------------------------------------------------
    # Event Handlers
    # ------------------------------------------------------------------------

    def on_name_change(self, event=None):
        self.weapon_data["name"] = self.name_entry.get()

    def on_custom_type_change(self, event=None):
        self.weapon_data["custom_type"] = self.custom_type_entry.get()

    def on_stat_change(self, stat):
        self.validate_stat(stat)

    def on_range_change(self, event=None):
        range_value = self.range_var.get()
        self.weapon_data["range"] = range_value

        if self.type_combobox.get() in ["Staff", "Rod"]:
            try:
                range_num = int(range_value)
                cost = (range_num - 1) * STAFF_RANGE_COST_PER_POINT
                self.range_note_var.set(f"Range 1 - {range_num}")
            except ValueError:
                cost = 0
                self.range_note_var.set("Range 1 - ?")
        else:
            cost = WEAPON_RANGE_COSTS.get(range_value, 0)
            self.range_note_var.set("")

        self.range_cost_var.set(self._fmt_cost(cost))
        self.update_total_cost()

    def on_desc_change(self, event=None):
        self.weapon_data["description"] = self.desc_text.get("1.0", tk.END).strip()

    def on_type_change(self, event=None):
        selected_type = self.type_combobox.get()
        old_type = self.weapon_data["type"]
        self.weapon_data["type"] = selected_type

        if selected_type == "Other":
            self.custom_type_frame.grid()
            self.weapon_hint_var.set("")
        else:
            self.custom_type_frame.grid_remove()
            self.custom_type_entry.delete(0, tk.END)
            self.weapon_hint_var.set("Enables Stat Drops on hit" if selected_type in ["Dagger", "Shuriken"] else "")

        if selected_type in ["Staff", "Rod"]:
            self.set_staff_rod_stats_state(False)
        else:
            self.set_staff_rod_stats_state(True)

        self.update_fixed_effects_visibility()
        self.update_might_cost_for_staff()
        self.update_might_stat_state()
        self.update_hit_stat_state()

        if selected_type in ["Staff", "Rod"]:
            if not self.staff_frame_visible:
                # Clear all regular fixed effects when switching to Staff/Rod
                # Call on_fixed_effect_toggle so active flags (magic_weapon_active etc.) are reset
                for effect, var in list(self.fixed_effect_vars.items()):
                    if var.get():
                        var.set(False)
                        self.on_fixed_effect_toggle(effect, var)
                for effect, var in self.staff_effect_vars.items():
                    if var.get():
                        var.set(False)
                        if effect in self.weapon_data["fixed_effects"]:
                            self.weapon_data["fixed_effects"].remove(effect)

                if "Bifröst" in self.weapon_data["fixed_effects"]:
                    self.weapon_data["fixed_effects"].remove("Bifröst")

                if hasattr(self, 'buff_checkboxes'):
                    for stat, var in self.buff_checkboxes.items():
                        var.set(False)
                    if hasattr(self, 'total_buff_cost_var'):
                        self.total_buff_cost_var.set("0")

                if hasattr(self, 'buff_frame') and self.buff_frame.winfo_viewable():
                    self.buff_frame.grid_remove()

                self.update_uses_stat_state()

                self.recovery_staff_selected = False
                self.interference_staff_selected = False
                self.special_staff_selected = False
                self.rescue_selected = False
                self.buff_user_active = False
                self.buff_ally_active = False
                self.unlimited_uses_active = False
                self.bifrost_selected = False

                if self.heal_scaling_checkbox:
                    self.heal_scaling_checkbox.state(['disabled'])
                    self.staff_effect_note_labels["Heal Scaling"].set("Requires Recovery Staff")
                    if self.staff_effect_vars.get("Heal Scaling", tk.BooleanVar()).get():
                        self.staff_effect_vars["Heal Scaling"].set(False)
                        if "Heal Scaling" in self.weapon_data["fixed_effects"]:
                            self.weapon_data["fixed_effects"].remove("Heal Scaling")

                self.staff_frame.grid(row=2, column=0, sticky="ew", padx=5, pady=5)
                self.staff_frame_visible = True
                self.update_staff_warning()
                self.update_total_cost()
                self.clamp_effect_value()  
                self.update_value_effects_availability()
        else:
            if self.staff_frame_visible:
                for effect, var in self.staff_effect_vars.items():
                    if var.get():
                        var.set(False)
                        if effect in self.weapon_data["fixed_effects"]:
                            self.weapon_data["fixed_effects"].remove(effect)

                self.recovery_staff_selected = False
                self.interference_staff_selected = False
                self.special_staff_selected = False
                self.rescue_selected = False
                self.buff_user_active = False
                self.buff_ally_active = False
                self.unlimited_uses_active = False

                if hasattr(self, 'buff_checkboxes'):
                    for stat, var in self.buff_checkboxes.items():
                        var.set(False)
                    if hasattr(self, 'total_buff_cost_var'):
                        self.total_buff_cost_var.set("0")

                if hasattr(self, 'buff_frame') and self.buff_frame.winfo_viewable():
                    self.buff_frame.grid_remove()

                self.update_uses_stat_state()
                self.staff_frame.grid_remove()
                self.staff_frame_visible = False
                self.update_value_effects_availability()

        if old_type in ["Dagger", "Shuriken"] and selected_type not in ["Dagger", "Shuriken"]:
            if "Debuff on Hit" not in self.weapon_data["fixed_effects"]:
                self.reset_debuffs()

        self.update_silver_weapon_cost()
        self.update_s_rank_debuff_cost()

        if self.silver_weapon_active or self.s_rank_debuff_active:
            self.update_total_cost()

        self.update_range_options()
        self.update_debuff_frame_visibility()

    def on_staff_effect_toggle(self, effect, var):
        def disable_enfeeble():
            if self.staff_effect_vars.get("Enfeeble", tk.BooleanVar()).get():
                self.staff_effect_vars["Enfeeble"].set(False)
                if "Enfeeble" in self.weapon_data["fixed_effects"]:
                    self.weapon_data["fixed_effects"].remove("Enfeeble")
                if self.debuff_frame.winfo_viewable():
                    self.debuff_frame.grid_remove()
                    self.reset_debuffs()
                    self.enfeeble_was_active = False
            elif "Enfeeble" in self.weapon_data["fixed_effects"]:
                self.weapon_data["fixed_effects"].remove("Enfeeble")

        def refresh_ui():
            self.update_interference_effects_state()
            self.update_special_effects_state()
            self.update_aoe_healing_state()
            self.update_might_stat_state()
            self.update_hit_stat_state()
            self.update_might_cost_for_staff()
            self.update_staff_warning()
            self.update_buff_ally_state()
            self.update_interference_special_state()
            self.update_total_cost()

        # Rescue
        if effect == "Rescue":
            if var.get():
                if self.interference_staff_selected:
                    self.staff_effect_vars["Interference Staff"].set(False)
                    if "Interference Staff" in self.weapon_data["fixed_effects"]:
                        self.weapon_data["fixed_effects"].remove("Interference Staff")
                    self.interference_staff_selected = False

                if self.special_staff_selected:
                    self.staff_effect_vars["Special Staff"].set(False)
                    if "Special Staff" in self.weapon_data["fixed_effects"]:
                        self.weapon_data["fixed_effects"].remove("Special Staff")
                    self.special_staff_selected = False
                    disable_enfeeble()

                if self.staff_effect_vars.get("AoE Healing", tk.BooleanVar()).get():
                    self.staff_effect_vars["AoE Healing"].set(False)
                    if "AoE Healing" in self.weapon_data["fixed_effects"]:
                        self.weapon_data["fixed_effects"].remove("AoE Healing")

                for child in self.staff_container.winfo_children():
                    if isinstance(child, ttk.Checkbutton) and child.cget("text") == "AoE Healing":
                        child.state(['disabled'])
                        break

                self.rescue_selected = True
            else:
                self.rescue_selected = False
                for child in self.staff_container.winfo_children():
                    if isinstance(child, ttk.Checkbutton) and child.cget("text") == "AoE Healing":
                        child.state(['!disabled'])
                        break

            refresh_ui()

        # AoE Healing
        elif effect == "AoE Healing":
            self.aoe_healing_selected = var.get()

        # Enfeeble
        elif effect == "Enfeeble":
            if var.get():
                self.enfeeble_was_active = True
                if not self.debuff_frame.winfo_viewable():
                    self.debuff_frame.grid()
                if "Enfeeble" in self.staff_effect_note_labels:
                    self.staff_effect_note_labels["Enfeeble"].set("See Debuff Effects below")
            else:
                self.enfeeble_was_active = False
                if "Enfeeble" in self.staff_effect_note_labels:
                    self.staff_effect_note_labels["Enfeeble"].set("")
                debuff_active = ("Debuff on Hit" in self.weapon_data["fixed_effects"] or
                                 self.type_combobox.get() in ["Dagger", "Shuriken"])
                if not debuff_active:
                    self.debuff_frame.grid_remove()
                    self.reset_debuffs()

        # Bifröst
        elif effect == "Bifröst":
            if var.get():
                if not self.special_staff_selected:
                    self.staff_effect_vars["Special Staff"].set(True)
                    self.special_staff_selected = True
                    if "Special Staff" not in self.weapon_data["fixed_effects"]:
                        self.weapon_data["fixed_effects"].append("Special Staff")

                self.bifrost_selected = True
                if "Bifröst" not in self.weapon_data["fixed_effects"]:
                    self.weapon_data["fixed_effects"].append("Bifröst")

                if self.recovery_staff_selected:
                    self.staff_effect_vars["Recovery Staff"].set(False)
                    if "Recovery Staff" in self.weapon_data["fixed_effects"]:
                        self.weapon_data["fixed_effects"].remove("Recovery Staff")
                    self.recovery_staff_selected = False

                if self.staff_effect_vars.get("Heal Scaling", tk.BooleanVar()).get():
                    self.staff_effect_vars["Heal Scaling"].set(False)
                    if "Heal Scaling" in self.weapon_data["fixed_effects"]:
                        self.weapon_data["fixed_effects"].remove("Heal Scaling")

                disable_enfeeble()
            else:
                self.bifrost_selected = False
                if "Bifröst" in self.weapon_data["fixed_effects"]:
                    self.weapon_data["fixed_effects"].remove("Bifröst")

            self.update_bifrost_exclusive_state()
            refresh_ui()

        # Recovery Staff
        elif effect == "Recovery Staff":
            if var.get():
                if self.interference_staff_selected:
                    self.staff_effect_vars["Interference Staff"].set(False)
                    if "Interference Staff" in self.weapon_data["fixed_effects"]:
                        self.weapon_data["fixed_effects"].remove("Interference Staff")
                    self.interference_staff_selected = False

                self.recovery_staff_selected = True
                disable_enfeeble()

                if hasattr(self, 'heal_scaling_checkbox') and self.heal_scaling_checkbox:
                    self.heal_scaling_checkbox.state(['!disabled'])
                    self.staff_effect_note_labels["Heal Scaling"].set("")

                if self.staff_effect_vars.get("Bifröst", tk.BooleanVar()).get():
                    self.staff_effect_vars["Bifröst"].set(False)
                    if "Bifröst" in self.weapon_data["fixed_effects"]:
                        self.weapon_data["fixed_effects"].remove("Bifröst")
                    self.bifrost_selected = False
                    self.update_bifrost_exclusive_state()

                for child in self.staff_container.winfo_children():
                    if isinstance(child, ttk.Checkbutton) and child.cget("text") == "Bifröst":
                        child.state(['disabled'])
                        break
            else:
                self.recovery_staff_selected = False

                if self.staff_effect_vars.get("Heal Scaling", tk.BooleanVar()).get():
                    self.staff_effect_vars["Heal Scaling"].set(False)
                    if "Heal Scaling" in self.weapon_data["fixed_effects"]:
                        self.weapon_data["fixed_effects"].remove("Heal Scaling")

                if hasattr(self, 'heal_scaling_checkbox') and self.heal_scaling_checkbox:
                    self.heal_scaling_checkbox.state(['disabled'])
                    self.staff_effect_note_labels["Heal Scaling"].set("Requires Recovery Staff")

                if self.special_staff_selected:
                    for child in self.staff_container.winfo_children():
                        if isinstance(child, ttk.Checkbutton) and child.cget("text") == "Bifröst":
                            child.state(['!disabled'])
                            break

            refresh_ui()

        # Special Staff
        elif effect == "Special Staff":
            if var.get():
                if self.buff_ally_active:
                    var.set(False)
                    return

                if self.interference_staff_selected:
                    self.staff_effect_vars["Interference Staff"].set(False)
                    if "Interference Staff" in self.weapon_data["fixed_effects"]:
                        self.weapon_data["fixed_effects"].remove("Interference Staff")
                    self.interference_staff_selected = False

                if self.rescue_selected:
                    self.staff_effect_vars["Rescue"].set(False)
                    if "Rescue" in self.weapon_data["fixed_effects"]:
                        self.weapon_data["fixed_effects"].remove("Rescue")
                    self.rescue_selected = False

                self.special_staff_selected = True
                disable_enfeeble()
                self.update_buff_ally_state()
            else:
                self.special_staff_selected = False
                self.update_buff_ally_state()

                if self.bifrost_selected:
                    self.staff_effect_vars["Bifröst"].set(False)
                    if "Bifröst" in self.weapon_data["fixed_effects"]:
                        self.weapon_data["fixed_effects"].remove("Bifröst")
                    self.bifrost_selected = False
                    self.update_bifrost_exclusive_state()

                disable_enfeeble()

                if self.aoe_healing_selected:
                    self.staff_effect_vars["AoE Healing"].set(False)
                    if "AoE Healing" in self.weapon_data["fixed_effects"]:
                        self.weapon_data["fixed_effects"].remove("AoE Healing")
                    self.aoe_healing_selected = False

            refresh_ui()

        # Interference Staff
        elif effect == "Interference Staff":
            if var.get():
                if self.buff_ally_active:
                    var.set(False)
                    return

                if self.recovery_staff_selected:
                    self.staff_effect_vars["Recovery Staff"].set(False)
                    if "Recovery Staff" in self.weapon_data["fixed_effects"]:
                        self.weapon_data["fixed_effects"].remove("Recovery Staff")
                    self.recovery_staff_selected = False

                    if hasattr(self, 'heal_scaling_checkbox') and self.heal_scaling_checkbox:
                        self.heal_scaling_checkbox.state(['disabled'])
                        self.staff_effect_note_labels["Heal Scaling"].set("Requires Recovery Staff")

                    if self.staff_effect_vars.get("Heal Scaling", tk.BooleanVar()).get():
                        self.staff_effect_vars["Heal Scaling"].set(False)
                        if "Heal Scaling" in self.weapon_data["fixed_effects"]:
                            self.weapon_data["fixed_effects"].remove("Heal Scaling")

                if self.special_staff_selected:
                    self.staff_effect_vars["Special Staff"].set(False)
                    if "Special Staff" in self.weapon_data["fixed_effects"]:
                        self.weapon_data["fixed_effects"].remove("Special Staff")
                    self.special_staff_selected = False

                if self.rescue_selected:
                    self.staff_effect_vars["Rescue"].set(False)
                    if "Rescue" in self.weapon_data["fixed_effects"]:
                        self.weapon_data["fixed_effects"].remove("Rescue")
                    self.rescue_selected = False

                self.interference_staff_selected = True
                self.update_buff_ally_state()

                if self.staff_effect_vars.get("Bifröst", tk.BooleanVar()).get():
                    self.staff_effect_vars["Bifröst"].set(False)
                    if "Bifröst" in self.weapon_data["fixed_effects"]:
                        self.weapon_data["fixed_effects"].remove("Bifröst")
                    self.bifrost_selected = False
                    self.update_bifrost_exclusive_state()

                for child in self.staff_container.winfo_children():
                    if isinstance(child, ttk.Checkbutton) and child.cget("text") == "Bifröst":
                        child.state(['disabled'])
                        break
            else:
                self.interference_staff_selected = False
                self.update_buff_ally_state()

            refresh_ui()

        # Unlimited Uses
        elif effect == "Unlimited Uses":
            self.unlimited_uses_active = var.get()
            if var.get():
                self.staff_effect_note_labels["Unlimited Uses"].set(f"⚠ Multiplies total cost by {UNLIMITED_USES_SCALING}x")
                if effect in self.staff_effect_note_widgets:
                    self.staff_effect_note_widgets[effect].configure(foreground="red")
                self.update_uses_stat_state()
            else:
                self.staff_effect_note_labels["Unlimited Uses"].set("")
                if effect in self.staff_effect_note_widgets:
                    self.staff_effect_note_widgets[effect].configure(foreground="green")
                self.update_uses_stat_state()

        # Buff User
        elif effect == "Buff User":
            self.buff_user_active = var.get()
            self.staff_effect_note_labels["Buff User"].set("Adds buff effects (see Buff Effects frame)" if var.get() else "")
            self.update_buff_frame_visibility()
            self.update_total_buff_cost()

        # Buff Ally
        elif effect == "Buff Ally":
            if var.get():
                if self.interference_staff_selected or self.special_staff_selected:
                    var.set(False)
                    return
                self.buff_ally_active = True
                self.staff_effect_note_labels["Buff Ally"].set("Adds buff effects (see Buff Effects frame)")
            else:
                self.buff_ally_active = False
                self.staff_effect_note_labels["Buff Ally"].set("")

            self.update_buff_frame_visibility()
            self.update_total_buff_cost()
            self.update_interference_special_state()
            refresh_ui()

        # Add to weapon data (skip Bifröst - already handled)
        if effect != "Bifröst":
            if var.get():
                if effect not in self.weapon_data["fixed_effects"]:
                    self.weapon_data["fixed_effects"].append(effect)
            else:
                if effect in self.weapon_data["fixed_effects"]:
                    self.weapon_data["fixed_effects"].remove(effect)

        scaling_effects = ["Freeze", "Enfeeble", "Silence", "Hex", "Entrap", "Rescue", "AoE Healing", "Bifröst", "Heal Scaling"]
        if effect in scaling_effects:
            self.validate_stat("Uses")

        self.update_debuff_frame_visibility()
        self.update_total_cost()

    # Slayers that unlock the Ineffective MT / Ineffective Hit checkboxes
    EFFECTIVE_SLAYERS = ['Sword Slayer', 'Lance Slayer', 'Axe Slayer', 'Tome Slayer', 'Flier Slayer', 'Dragon Slayer', 'Beast Slayer', 'Armor Slayer', 'Monster Slayer', 'Automaton Slayer', 'Dragonstone Slayer', 'Beaststone Slayer', 'Mounted Slayer']

    def _has_effective_effect(self):
        """Return True if at least one Slayer effect is currently checked."""
        return any(
            self.fixed_effect_vars[s].get()
            for s in self.EFFECTIVE_SLAYERS
            if s in self.fixed_effect_vars
        )

    def _update_ineffective_state(self):
        """Enable or disable Ineffective MT / Hit based on active Slayers."""
        has_effective = self._has_effective_effect()
        for ineff in ("Ineffective MT", "Ineffective Hit"):
            if ineff not in self.fixed_effect_checkbuttons:
                continue
            chk = self.fixed_effect_checkbuttons[ineff]
            if has_effective:
                chk.state(["!disabled"])
                self.fixed_effect_note_labels[ineff].set("")
            else:
                # Uncheck and zero out if being disabled
                if self.fixed_effect_vars[ineff].get():
                    self.fixed_effect_vars[ineff].set(False)
                    self.on_fixed_effect_toggle(ineff, self.fixed_effect_vars[ineff])
                chk.state(["disabled"])
                self.fixed_effect_note_labels[ineff].set("Requires an Effective effect")

    def on_fixed_effect_toggle(self, effect, var):
        if effect == "Heal Scaling" and var.get() and not self.recovery_staff_selected:
            var.set(False)
            messagebox.showwarning("Requires Recovery Staff", "Heal Scaling can only be used when Recovery Staff is selected.", parent=self.window)
            return

        if effect == "Magic Weapon":
            self.magic_weapon_active = var.get()
            self.fixed_effect_note_labels["Magic Weapon"].set("")

        elif effect == "Silver Weapon":
            self.silver_weapon_active = var.get()
            self.update_silver_weapon_cost()

        elif effect == "S Rank Debuff":
            self.s_rank_debuff_active = var.get()
            self.update_s_rank_debuff_cost()

        elif effect == "One Tap":
            self.one_tap_active = var.get()
            self.update_might_multiplier_notes()
            if "Might" in self.stat_vars:
                self.validate_stat("Might")
            self.fixed_effect_note_labels["One Tap"].set("Might cost increased by 1.5x" if var.get() else "")

        elif effect == "Venge":
            self.venge_active = var.get()
            self.update_might_multiplier_notes()
            if "Might" in self.stat_vars:
                self.validate_stat("Might")
            self.fixed_effect_note_labels["Venge"].set("Might cost increased by 1.5x" if var.get() else "")

        elif effect == "Skillful":
            self.skillful_active = var.get()
            self.update_might_multiplier_notes()
            if "Might" in self.stat_vars:
                self.validate_stat("Might")
            self.fixed_effect_note_labels["Skillful"].set("Might cost increased by 2x" if var.get() else "")

        elif effect == "Flier Slayer":
            self.flier_slayer_active = var.get()
            self.update_might_multiplier_notes()
            if "Might" in self.stat_vars:
                self.validate_stat("Might")
            self.fixed_effect_note_labels["Flier Slayer"].set("Might cost increased by 1.5x" if var.get() else "")
            self._update_ineffective_state()

        elif effect == "Dragon Slayer":
            self.dragon_slayer_active = var.get()
            self.update_might_multiplier_notes()
            if "Might" in self.stat_vars:
                self.validate_stat("Might")
            self.fixed_effect_note_labels["Dragon Slayer"].set("Might cost increased by 1.5x" if var.get() else "")
            self._update_ineffective_state()

        elif effect == "Beast Slayer":
            self.beast_slayer_active = var.get()
            self.update_might_multiplier_notes()
            if "Might" in self.stat_vars:
                self.validate_stat("Might")
            self.fixed_effect_note_labels["Beast Slayer"].set("Might cost increased by 1.5x" if var.get() else "")
            self._update_ineffective_state()

        elif effect == "Armor Slayer":
            self.armor_slayer_active = var.get()
            self.update_might_multiplier_notes()
            if "Might" in self.stat_vars:
                self.validate_stat("Might")
            self.fixed_effect_note_labels["Armor Slayer"].set("Might cost increased by 1.5x" if var.get() else "")
            self._update_ineffective_state()

        elif effect == "Nosferatu":
            self.nosferatu_active = var.get()
            if var.get():
                self.force_bronze_and_bold(True)
                self.fixed_effect_note_labels["Nosferatu"].set("Forces Bronze Weapon & Bold Weapon")
                if "Bronze Weapon" in self.fixed_effect_note_labels:
                    self.fixed_effect_note_labels["Bronze Weapon"].set("Forced by Nosferatu (No crit/skills)")
                if "Bold Weapon" in self.fixed_effect_note_labels:
                    self.fixed_effect_note_labels["Bold Weapon"].set("Forced by Nosferatu (Cannot double)")
            else:
                self.force_bronze_and_bold(False)
                self.fixed_effect_note_labels["Nosferatu"].set("")

        if var.get():
            if effect not in self.weapon_data["fixed_effects"]:
                self.weapon_data["fixed_effects"].append(effect)
        else:
            if effect in self.weapon_data["fixed_effects"]:
                self.weapon_data["fixed_effects"].remove(effect)
                if effect == "Debuff on Hit" and self.type_combobox.get() not in ["Dagger", "Shuriken"]:
                    self.reset_debuffs()
                if effect in self.fixed_effect_note_labels:
                    self.fixed_effect_note_labels[effect].set("")

        # Update Ineffective state whenever any Slayer is toggled via the generic path
        if effect in self.EFFECTIVE_SLAYERS:
            self._update_ineffective_state()

        self.update_debuff_frame_visibility()
        self.update_total_cost()

    def on_value_effect_toggle(self, effect, var):
        # Special check for Rally after battle
        if effect == "Rally after battle" and var.get():
            # Check if all required Rally skills exist in skill_data
            rally_skills = ["Rally Strength", "Rally Magic", "Rally Skill", 
                            "Rally Speed", "Rally Luck", "Rally Defence", "Rally Resistance"]
            missing_skills = [skill for skill in rally_skills if skill not in skill_data]
            
            if missing_skills:
                messagebox.showwarning(
                    "Missing Rally Data",
                    f"Cannot activate 'Rally after battle' because the following skills are missing from skill_data.json:\n\n" +
                    "\n".join(missing_skills)
                , parent=self.window)
                var.set(False)
                return
        
        if var.get():
            if effect not in self.weapon_data["value_effects"]:
                self.weapon_data["value_effects"].append(effect)
        else:
            if effect in self.weapon_data["value_effects"]:
                self.weapon_data["value_effects"].remove(effect)
        
        # Clamp the current value to the new min/max range
        self.clamp_effect_value()
        
        self.update_value_effect_costs()
        self.update_total_cost()
        
    # ------------------------------------------------------------------------
    # Value effect specific methods
    # ------------------------------------------------------------------------
    
    def on_effect_value_change(self):
        value = _safe_get(self.effect_value_var, 0)
        
        # Find min and max allowed based on selected effects
        min_allowed = -100  # Default min
        max_allowed = 100  # Default max
        
        # Check if current weapon is Staff/Rod - prevent negative values
        current_type = self.type_combobox.get()
        is_staff_rod = current_type in ["Staff", "Rod"]
        
        for effect in self.weapon_data["value_effects"]:
            if effect in VALUE_EFFECTS_CONFIG:
                effect_min = VALUE_EFFECTS_CONFIG[effect].get("min", -100)
                effect_max = VALUE_EFFECTS_CONFIG[effect].get("max", 100)
                if effect_min > min_allowed:
                    min_allowed = effect_min
                if effect_max < max_allowed:
                    max_allowed = effect_max
        
        # Override min_allowed for Staff/Rod weapons (prevent negative values)
        if is_staff_rod and min_allowed < 0:
            min_allowed = 0
        
        # Clamp value
        if value > max_allowed:
            value = max_allowed
            self.effect_value_var.set(value)
        elif value < min_allowed:
            value = min_allowed
            self.effect_value_var.set(value)
        
        self.update_value_effect_costs()
        self.update_total_cost()
            
    def calculate_value_effect_cost(self, effect, value):
        """Calculate cost for a specific value effect at given value."""
        info = VALUE_EFFECTS_CONFIG.get(effect, {})
        cost_type = info.get("cost_type", "fixed")
        
        if cost_type == "table":
            # Table-based costs (positive values only)
            if value <= 0:
                return 0.0
            table_attr = info.get("table_attribute")
            if table_attr and table_attr in ATTRIBUTE_COSTS:
                table = ATTRIBUTE_COSTS[table_attr]
                index = min(value, 20)
                raw = table[index]
                if effect == "HP Regeneration":
                    # Use precomputed table — guarantees every step costs at least 1 more
                    return HP_REGEN_COST_TABLE[index]
                return raw
            return 0.0
            
        elif cost_type == "asymmetric":
            # Asymmetric cost: different rates for positive and negative values.
            # Whether a value is a cost or a credit depends on the effect:
            #   Change User HP:   negative = damaging the user    = credit (return negative)
            #                     positive = healing the user      = cost   (return positive)
            #   Change Target HP: positive = healing the target    = credit (return negative)
            #                     negative = damaging the target   = cost   (return positive)
            positive_cost = info.get("positive_cost_per_point", 0.0)
            negative_cost = info.get("negative_cost_per_point", 0.0)
            # A flag in the config marks effects where positive value = credit
            positive_is_credit = info.get("positive_is_credit", False)
            
            if value > 0:
                raw = (value / 10) * positive_cost
                return -raw if positive_is_credit else raw
            elif value < 0:
                raw = (abs(value) / 10) * negative_cost
                return -raw if not positive_is_credit else raw
            return 0.0
            
        elif cost_type == "rally":
            # Rally cost: uses skill_data.json with different scaling for positive/negative
            if value == 0:
                return 0.0
            
            abs_value = abs(value)
            # Map value to Rally skill name
            rally_map = {
                1: "Rally Strength",
                2: "Rally Magic", 
                3: "Rally Skill",
                4: "Rally Speed",
                5: "Rally Luck",
                6: "Rally Defence",
                7: "Rally Resistance"
            }
            rally_skill = rally_map.get(abs_value, None)
            
            if rally_skill and rally_skill in skill_data:
                # Get base cost from skill_data
                base_cost = scaled_skill_cost(skill_data[rally_skill]["cost"])
                
                # Apply different scaling for positive (ally rally) vs negative (enemy rally)
                if value > 0:
                    return base_cost * RALLY_COST_SCALING
                else:
                    # Negative rally (debuffs enemies) gives a credit
                    return -(base_cost * RALLY_COST_NEG_SCALING)
            elif rally_skill:
                # Skill not found in data - print warning
                print(f"Warning: '{rally_skill}' not found in skill_data.json")
            return 0.0
            
        else:
            # Fixed cost per point (can be positive or negative)
            cost_per_point = info.get("cost_per_point", 0.0)
            return abs(value) * cost_per_point
    
    def update_value_effect_costs(self):
        """Update current, next +1, and next -1 costs for all selected value effects."""
        current_value = self.effect_value_var.get()
        total_cost = 0.0
        
        for effect, var in self.value_effect_vars.items():
            if var.get():
                # Current cost
                current_cost = self.calculate_value_effect_cost(effect, current_value)
                self.value_effect_current_cost_vars[effect].set(self._fmt_cost(current_cost))
                total_cost += round(current_cost)
                # Colour the cost label: green = credit, blue = normal cost
                if effect in self.value_effect_cost_label_widgets:
                    color = "green" if current_cost < 0 else "blue"
                    self.value_effect_cost_label_widgets[effect].configure(foreground=color)
                
                # Get min/max for this effect
                info = VALUE_EFFECTS_CONFIG.get(effect, {})
                min_val = info.get("min", -30)
                max_val = info.get("max", 30)
                
                # Next +1 Cost (increase by 1)
                if current_value < max_val:
                    _next_plus_raw = self.calculate_value_effect_cost(effect, current_value + 1)
                    next_plus_cost = round(_next_plus_raw) - round(current_cost)
                    self.value_effect_next_plus_cost_vars[effect].set(self._fmt_cost(next_plus_cost))
                else:
                    self.value_effect_next_plus_cost_vars[effect].set("MAX")
                
                # Next -1 Cost (decrease by 1)
                if current_value > min_val:
                    _next_minus_raw = self.calculate_value_effect_cost(effect, current_value - 1)
                    next_minus_cost = round(_next_minus_raw) - round(current_cost)
                    self.value_effect_next_minus_cost_vars[effect].set(self._fmt_cost(abs(next_minus_cost)))
                else:
                    self.value_effect_next_minus_cost_vars[effect].set("MIN")
                
                # Update dynamic description for Rally (only when selected)
                if effect == "Rally after battle" and current_value != 0:
                    rally_map = {
                        1: "Strength",
                        2: "Magic",
                        3: "Skill", 
                        4: "Speed",
                        5: "Luck",
                        6: "Defence",
                        7: "Resistance"
                    }
                    rally_skill_map = {
                        1: "Rally Strength",
                        2: "Rally Magic",
                        3: "Rally Skill",
                        4: "Rally Speed", 
                        5: "Rally Luck",
                        6: "Rally Defence",
                        7: "Rally Resistance"
                    }
                    if current_value > 0:
                        stat = rally_map.get(current_value, "Unknown")
                        skill_name = rally_skill_map.get(current_value, "")
                        if skill_name in skill_data:
                            skill_cost = scaled_skill_cost(skill_data[skill_name]["cost"])
                            base_desc = f"Rallies Allies: +4 {stat} (Cost: {skill_cost} * {RALLY_COST_SCALING})"
                        else:
                            base_desc = f"Rallies Allies: +4 {stat} (WARNING: {skill_name} missing from skill_data!)"
                        self.value_effect_desc_vars[effect].set(base_desc)
                        self.value_effect_desc_labels[effect].configure(foreground="purple")
                    elif current_value < 0:
                        stat = rally_map.get(abs(current_value), "Unknown")
                        skill_name = rally_skill_map.get(abs(current_value), "")
                        if skill_name in skill_data:
                            skill_cost = scaled_skill_cost(skill_data[skill_name]["cost"])
                            base_desc = f"Rallies Enemies: -4 {stat} debuff (Cost: {skill_cost} * {RALLY_COST_NEG_SCALING})"
                        else:
                            base_desc = f"Rallies Enemies: -4 {stat} debuff (WARNING: {skill_name} missing from skill_data!)"
                        self.value_effect_desc_vars[effect].set(base_desc)
                        self.value_effect_desc_labels[effect].configure(foreground="purple")
                elif effect == "Rally after battle":
                    # Reset Rally description when value is 0, change color back to gray
                    self.value_effect_desc_vars[effect].set(VALUE_EFFECTS_CONFIG[effect]['desc'])
                    self.value_effect_desc_labels[effect].configure(foreground="gray")
                # For non-Rally effects, description stays as default (already set in setup)
            else:
                self.value_effect_current_cost_vars[effect].set("0")
                self.value_effect_next_plus_cost_vars[effect].set("0")
                self.value_effect_next_minus_cost_vars[effect].set("0")
                if effect in self.value_effect_cost_label_widgets:
                    self.value_effect_cost_label_widgets[effect].configure(foreground="blue")
                # Reset description when not selected
                if effect in self.value_effect_desc_vars:
                    self.value_effect_desc_vars[effect].set(VALUE_EFFECTS_CONFIG[effect]['desc'])
                    # Reset color to gray for Rally when deselected
                    if effect == "Rally after battle":
                        self.value_effect_desc_labels[effect].configure(foreground="gray")
        
        self.effect_value_total_cost_var.set(self._fmt_cost(total_cost))
        self.weapon_data["effect_value"] = current_value
        self.weapon_data["value_effects_cost"] = total_cost
        
    def update_value_effects_availability(self):
        """Enable/disable value effects based on current weapon type."""
        current_type = self.type_combobox.get()
        is_staff_rod = current_type in ["Staff", "Rod"]
        
        # Show/hide Staff/Rod note
        if hasattr(self, 'staff_value_note_var'):
            if is_staff_rod:
                self.staff_value_note_var.set("⚠ Staff/Rod cannot use negative values")
            else:
                self.staff_value_note_var.set("")
        
        # If switching to Staff/Rod and current value is negative, reset to 0
        if is_staff_rod and self.effect_value_var.get() < 0:
            self.effect_value_var.set(0)
            self.update_value_effect_costs()
        
        for effect, var in self.value_effect_vars.items():
            info = VALUE_EFFECTS_CONFIG.get(effect, {})
            allowed_types = info.get("weapon_types", ["all"])
            
            # Determine if this effect should be available
            if is_staff_rod:
                # Staff/Rod weapons: HP Regeneration is NOT allowed, Staff Self Heal IS allowed
                if effect == "HP Regeneration":
                    available = False
                elif effect == "Staff Self Heal":
                    available = True
                else:
                    available = "all" in allowed_types
            else:
                # Non-staff weapons: Staff Self Heal is NOT allowed
                if effect == "Staff Self Heal":
                    available = False
                else:
                    available = "all" in allowed_types or current_type in allowed_types
            
            # Apply availability
            if available:
                self.value_effect_vars[effect].widget.config(state="normal")
            else:
                self.value_effect_vars[effect].widget.config(state="disabled")
                # If this effect was selected, deselect it
                if var.get():
                    var.set(False)
                    if effect in self.weapon_data["value_effects"]:
                        self.weapon_data["value_effects"].remove(effect)
                # Add a visual indicator that it's disabled
                if hasattr(self, 'value_effect_current_cost_vars') and effect in self.value_effect_current_cost_vars:
                    self.value_effect_current_cost_vars[effect].set("N/A")
                    self.value_effect_next_plus_cost_vars[effect].set("N/A")
                    self.value_effect_next_minus_cost_vars[effect].set("N/A")
        
        # Recalculate costs after availability changes
        self.update_value_effect_costs()
    
    def clamp_effect_value(self):
        """Clamp the current shared effect value to the allowed range of selected effects."""
        current_value = self.effect_value_var.get()
        
        # Find min and max allowed based on selected effects
        min_allowed = -999
        max_allowed = 999
        
        current_type = self.type_combobox.get()
        is_staff_rod = current_type in ["Staff", "Rod"]
        
        for effect in self.weapon_data["value_effects"]:
            if effect in VALUE_EFFECTS_CONFIG:
                effect_min = VALUE_EFFECTS_CONFIG[effect].get("min", -999)
                effect_max = VALUE_EFFECTS_CONFIG[effect].get("max", 999)
                if effect_min > min_allowed:
                    min_allowed = effect_min
                if effect_max < max_allowed:
                    max_allowed = effect_max
        
        # If no effects selected, use reasonable defaults
        if min_allowed == -999:
            min_allowed = -20
        if max_allowed == 999:
            max_allowed = 100
        
        # Override min_allowed for Staff/Rod weapons (prevent negative values)
        if is_staff_rod and min_allowed < 0:
            min_allowed = 0
        
        # Clamp value
        clamped = False
        if current_value > max_allowed:
            self.effect_value_var.set(max_allowed)
            clamped = True
        elif current_value < min_allowed:
            self.effect_value_var.set(min_allowed)
            clamped = True
        
        if clamped:
            self.update_value_effect_costs()
            
    # ------------------------------------------------------------------------
    # Validation and Calculation Methods
    # ------------------------------------------------------------------------

    def validate_stat(self, stat):
        if stat == "Uses" and self.unlimited_uses_active:
            self.stat_vars["Uses"]["cost"].set("0")
            self.update_total_cost()
            return

        var = self.stat_vars[stat]["value"]
        info = self.weapon_stats[stat]

        value = _safe_get(var, info["base"])
        if value < info["min"]:
            value = info["min"]
            var.set(value)
        elif value > info["max"]:
            value = info["max"]
            var.set(value)
        # Snap Hit/Crit/Avoid/Dodge to nearest multiple of 5
        if stat in WEAPON_STAT_INCREMENT_5:
            snapped = round(value / 5) * 5
            snapped = max(info["min"], min(info["max"], snapped))
            if snapped != value:
                value = snapped
                var.set(value)

        point_diff = value - info["base"]

        if stat == "Uses":
            current_might_cost = self.weapon_stats["Might"]["cost_per_point"]
            might_value = self.stat_vars["Might"]["value"].get()

            might_base = self.weapon_stats["Might"]["base"]
            might_point_diff = might_value - might_base
            total_might_cost = might_point_diff * current_might_cost

            if might_value > might_base:
                multiplier = self.calculate_might_cost_multiplier()
                if multiplier != 1.0:
                    total_might_cost = total_might_cost * multiplier

            cost = 0
            if self.recovery_staff_selected:
                uses_percent = (value * 2) / 100
                cost = total_might_cost * uses_percent

                heal_scaling_active = self.staff_effect_vars.get("Heal Scaling", tk.BooleanVar()).get()
                if heal_scaling_active:
                    heal_scaling_cost_per_use = HEAL_SCALING_TOTAL_COST / WEAPON_STAT_MAX["Uses"]
                    cost += (value - WEAPON_STAT_BASE["Uses"]) * heal_scaling_cost_per_use

            scaling_effects = ["Freeze", "Enfeeble", "Silence", "Hex", "Entrap", "Rescue", "Bifröst"]
            total_effect_cost = 0

            for effect in self.weapon_data["fixed_effects"]:
                if effect in scaling_effects and effect in self.staff_effects:
                    total_effect_cost += self.staff_effects[effect]["cost"]

            if "AoE Healing" in self.weapon_data["fixed_effects"]:
                aoe_healing_cost = self.staff_effects["AoE Healing"]["cost"]
                range_value = self.range_var.get()
                try:
                    if self.type_combobox.get() in ["Staff", "Rod"]:
                        range_num = int(range_value)
                    else:
                        if "-" in range_value:
                            range_num = int(range_value.split("-")[1])
                        else:
                            range_num = int(range_value)
                except (ValueError, TypeError):
                    range_num = 1

                base_cost = cost
                if range_num > 1:
                    cost = base_cost ** range_num
                else:
                    cost = base_cost
                cost += aoe_healing_cost

            if point_diff > 0:
                is_interference = self.interference_staff_selected or total_effect_cost > 0
                if is_interference:
                    cost += (total_effect_cost * point_diff) * INTERFERENCE_STAFF_USES_SCALE
                else:
                    cost += total_effect_cost * point_diff

        else:
            _cpp = info["cost_per_point"]
            if stat in WEAPON_STAT_INCREMENT_5 and point_diff != 0:
                _abs = abs(point_diff)
                _sign = 1 if point_diff > 0 else -1
                _steps = _abs // 5  # each increment of 5 = 1 step
                cost = _sign * math.ceil(_cpp * (100 + _steps) / 100 * _steps * 5)
            else:
                cost = point_diff * _cpp

        # Negative credit stats: scale the credit when value is below base
        _credit_stats = {"Avoid", "Dodge", "Mov", "Effective Speed Offensive", "Effective Speed Defensive"}
        if stat in _credit_stats and point_diff < 0:
            cost = cost * NEGATIVE_CREDIT_SCALE

        # Apply Staff Hit scale for Staff/Rod weapons
        if stat == "Hit" and self.type_combobox.get() in ["Staff", "Rod"]:
            cost = cost * STAFF_HIT_SCALE

        # Staff Might: use precomputed table for strictly increasing steps
        if stat == "Might" and self.type_combobox.get() in ["Staff", "Rod"] and self.recovery_staff_selected:
            idx = min(abs(point_diff), len(STAFF_MIGHT_COST_TABLE) - 1)
            cost = STAFF_MIGHT_COST_TABLE[idx] * (1 if point_diff >= 0 else -1)

        if stat == "Might":
            multiplier = self.calculate_might_cost_multiplier()
            if multiplier != 1.0:
                cost = cost * multiplier

        self.stat_vars[stat]["cost"].set(self._fmt_cost(cost))
        self.weapon_data[stat.lower().replace(" ", "_")] = value

        if stat == "Might":
            self.validate_stat("Uses")

        self.update_total_cost()

    def update_total_cost(self):
        # update_total_cost in Weapon creation
        total_cost = 0

        for stat in self.weapon_stats.keys():
            cost_str = self.stat_vars[stat]["cost"].get()
            if cost_str:
                total_cost += float(cost_str)

        range_cost_str = self.range_cost_var.get()
        if range_cost_str:
            total_cost += float(range_cost_str)

        for effect in self.weapon_data["fixed_effects"]:
            if effect in self.fixed_effects:
                if effect == "Silver Weapon":
                    total_cost += round(self.silver_weapon_adjusted_cost * NEGATIVE_CREDIT_SCALE)
                elif effect == "S Rank Debuff":
                    total_cost += round(self.s_rank_debuff_adjusted_cost * NEGATIVE_CREDIT_SCALE)
                else:
                    total_cost += round(self.fixed_effects[effect]["cost"])
            elif effect in self.staff_effects and effect != "Unlimited Uses":
                total_cost += round(self.staff_effects[effect]["cost"])

        # Value effects cost (already tracked in effect_value_total_cost_var)
        if hasattr(self, 'effect_value_total_cost_var'):
            total_cost += float(self.effect_value_total_cost_var.get())

        if hasattr(self, 'total_debuff_cost_var'):
            total_cost += float(self.total_debuff_cost_var.get())

        if hasattr(self, 'total_buff_cost_var'):
            total_cost += float(self.total_buff_cost_var.get())

        if self.unlimited_uses_active:
            total_cost = total_cost * UNLIMITED_USES_SCALING

        self.remaining_weapon_points = self.weapon_points - total_cost
        if self.remaining_weapon_points != int(self.remaining_weapon_points):
            print(f"WARNING: remaining_weapon_points is not a full integer: {self.remaining_weapon_points}")
        self.points_var.set(str(round(self.remaining_weapon_points)))

        if self.remaining_weapon_points < 0:
            self.points_var.set(f"OVER: {abs(round(self.remaining_weapon_points))}")
            self.points_label.configure(foreground='red')
        else:
            self.points_label.configure(foreground='blue')

    def update_debuff_cost(self, stat):
        var = self.debuff_vars[stat]["var"]
        info = DEBUFF_COSTS[stat]

        value = _safe_get(var, 0)
        if value < 0:
            value = 0
            var.set(value)
        elif value > DEBUFF_MAX[stat]:
            value = DEBUFF_MAX[stat]
            var.set(value)

        cost = value * info
        self.debuff_cost_vars[stat].set(self._fmt_cost(cost))

        # Update next cost: marginal cost of the next step, or MAX if at limit
        if stat in self.debuff_next_cost_vars:
            if value >= DEBUFF_MAX[stat]:
                self.debuff_next_cost_vars[stat].set("MAX")
            else:
                next_total = (value + 1) * info
                next_marginal = round(next_total) - round(cost)
                self.debuff_next_cost_vars[stat].set(str(max(1, next_marginal)))

        self.update_total_debuff_cost()

    def update_total_debuff_cost(self):
        total_cost = 0
        costs = {}

        for stat, cost_var in self.debuff_cost_vars.items():
            costs[stat] = float(cost_var.get())
            total_cost += costs[stat]

        if "Defense" in costs and "Resistance" in costs:
            defense_cost = costs["Defense"]
            resistance_cost = costs["Resistance"]
            if defense_cost > 0 and resistance_cost > 0:
                total_cost -= min(defense_cost, resistance_cost)

        self.total_debuff_cost_var.set(self._fmt_cost(total_cost))

        self.weapon_data["debuffs"] = {}
        for stat, data in self.debuff_vars.items():
            value = data["var"].get()
            if value > 0:
                self.weapon_data["debuffs"][stat.lower()] = value

        self.update_total_cost()

    def update_buff_cost(self, stat):
        if not (self.buff_user_active or self.buff_ally_active):
            return

        scaling_factor = 0
        if self.buff_user_active:
            scaling_factor += BUFF_USER_SCALING
        if self.buff_ally_active:
            scaling_factor += BUFF_ALLY_SCALING

        if stat in DEBUFF_COSTS:
            cost = DEBUFF_COSTS[stat] * scaling_factor

            if self.buff_checkboxes[stat].get():
                self.buff_cost_labels[stat].set(self._fmt_cost(cost))
            else:
                self.buff_cost_labels[stat].set("0")

        self.update_total_buff_cost()

    def update_total_buff_cost(self):
        if not (self.buff_user_active or self.buff_ally_active):
            self.total_buff_cost_var.set("0")
            return

        scaling_factor = 0
        if self.buff_user_active:
            scaling_factor += BUFF_USER_SCALING
        if self.buff_ally_active:
            scaling_factor += BUFF_ALLY_SCALING

        total_cost = 0
        for stat, var in self.buff_checkboxes.items():
            if var.get() and stat in DEBUFF_COSTS:
                total_cost += DEBUFF_COSTS[stat] * scaling_factor

        self.total_buff_cost_var.set(self._fmt_cost(total_cost))
        self.update_total_cost()

    # ------------------------------------------------------------------------
    # State Update Methods
    # ------------------------------------------------------------------------

    def update_range_options(self):
        if self.type_combobox.get() in ["Staff", "Rod"]:
            range_options = [str(i) for i in range(1, 16)]
            self.range_info_var.set("Range (1-15)")
        else:
            range_options = ["1", "1-2", "2", "2-3", "3", "1-3"]
            self.range_info_var.set("Select weapon range")

        self.range_combobox['values'] = range_options
        if self.range_var.get() not in range_options:
            self.range_var.set("1")
        self.on_range_change()  # Always update note when range options change

    def update_might_cost_for_staff(self):
        if "Might" in self.stat_vars:
            use_staff_might = (self.type_combobox.get() in ["Staff", "Rod"] and self.recovery_staff_selected)
            original_cost = self.stat_costs["Might"]

            if use_staff_might:
                # Keep the fractional per-point for the Uses-cost scaling, but the
                # actual Might charge comes from STAFF_MIGHT_COST_TABLE, so show its
                # real per-point cost (the table's first step) in the note.
                self.weapon_stats["Might"]["cost_per_point"] = _staff_might_cost_per_point(original_cost)
                per_point = STAFF_MIGHT_COST_TABLE[1] - STAFF_MIGHT_COST_TABLE[0]
                self.stat_vars["Might"]["note"].set(f"Staff Might: {per_point} per point")
                self.validate_stat("Might")
            else:
                self.weapon_stats["Might"]["cost_per_point"] = original_cost
                current_note = self.stat_vars["Might"]["note"].get()
                if current_note.startswith("Staff Might:"):
                    self.stat_vars["Might"]["note"].set("")

            self.validate_stat("Might")

    def update_might_stat_state(self):
        if "Might" in self.stat_spinboxes:
            enable_might = not (self.type_combobox.get() in ["Staff", "Rod"] and not self.recovery_staff_selected)

            state = "normal" if enable_might else "disabled"
            label_color = "black" if enable_might else "gray"

            self.stat_spinboxes["Might"].config(state=state)

            if "Might" in self.stat_vars:
                self.stat_vars["Might"]["label"].configure(foreground=label_color)

            if not enable_might and self.stat_vars["Might"]["value"].get() != WEAPON_STAT_BASE["Might"]:
                self.stat_vars["Might"]["value"].set(WEAPON_STAT_BASE["Might"])
                self.validate_stat("Might")

            if not enable_might:
                self.stat_vars["Might"]["note"].set("Requires Recovery Staff")
            elif enable_might:
                current_note = self.stat_vars["Might"]["note"].get()
                if current_note == "Requires Recovery Staff":
                    self.stat_vars["Might"]["note"].set("")

    def update_hit_stat_state(self):
        if "Hit" in self.stat_spinboxes:
            enable_hit = not (self.type_combobox.get() in ["Staff", "Rod"] and not self.interference_staff_selected)

            state = "normal" if enable_hit else "disabled"
            label_color = "black" if enable_hit else "gray"

            self.stat_spinboxes["Hit"].config(state=state)

            if "Hit" in self.stat_vars:
                self.stat_vars["Hit"]["label"].configure(foreground=label_color)

            if not enable_hit and self.stat_vars["Hit"]["value"].get() != WEAPON_STAT_BASE["Hit"]:
                self.stat_vars["Hit"]["value"].set(WEAPON_STAT_BASE["Hit"])
                self.validate_stat("Hit")

            if not enable_hit:
                self.stat_vars["Hit"]["note"].set("Requires Interference Staff")
            elif enable_hit:
                current_note = self.stat_vars["Hit"]["note"].get()
                if current_note == "Requires Interference Staff":
                    self.stat_vars["Hit"]["note"].set("")

    def update_uses_stat_state(self):
        if "Uses" in self.stat_spinboxes:
            if self.unlimited_uses_active:
                self.stat_spinboxes["Uses"].config(state="disabled")
                self.stat_vars["Uses"]["label"].configure(foreground="gray")
                self.stat_vars["Uses"]["value"].set(WEAPON_STAT_BASE["Uses"])
                self.stat_vars["Uses"]["cost"].set("0")
                self.stat_vars["Uses"]["note"].set("Unlimited uses - no cost")
                self.weapon_data["uses"] = WEAPON_STAT_BASE["Uses"]
            else:
                if self.type_combobox.get() in ["Staff", "Rod"]:
                    self.stat_spinboxes["Uses"].config(state="normal")
                    self.stat_vars["Uses"]["label"].configure(foreground="black")
                    self.stat_vars["Uses"]["note"].set("")
                    self.validate_stat("Uses")
                else:
                    self.stat_spinboxes["Uses"].config(state="disabled")
                    self.stat_vars["Uses"]["label"].configure(foreground="gray")

    def update_interference_effects_state(self):
        if "Bifröst" in self.weapon_data["fixed_effects"]:
            for effect in self.interference_dependent_effects:
                if effect in self.staff_effect_vars:
                    if self.staff_effect_vars[effect].get():
                        self.staff_effect_vars[effect].set(False)
                        if effect in self.weapon_data["fixed_effects"]:
                            self.weapon_data["fixed_effects"].remove(effect)
                    for child in self.staff_container.winfo_children():
                        if isinstance(child, ttk.Checkbutton) and child.cget("text") == effect:
                            child.state(['disabled'])
                            break
                    self.staff_effect_note_labels[effect].set("Disabled by Bifröst")
            return

        for effect in self.interference_dependent_effects:
            if effect in self.staff_effect_vars:
                if self.interference_staff_selected:
                    for child in self.staff_container.winfo_children():
                        if isinstance(child, ttk.Checkbutton) and child.cget("text") == effect:
                            child.state(['!disabled'])
                            break
                    self.staff_effect_note_labels[effect].set("")
                else:
                    if self.staff_effect_vars[effect].get():
                        self.staff_effect_vars[effect].set(False)
                        if effect in self.weapon_data["fixed_effects"]:
                            self.weapon_data["fixed_effects"].remove(effect)
                    for child in self.staff_container.winfo_children():
                        if isinstance(child, ttk.Checkbutton) and child.cget("text") == effect:
                            child.state(['disabled'])
                            break
                    self.staff_effect_note_labels[effect].set("Requires Interference Staff")

    def update_special_effects_state(self):
        for effect in self.special_dependent_effects:
            if effect in self.staff_effect_vars:
                if self.special_staff_selected:
                    for child in self.staff_container.winfo_children():
                        if isinstance(child, ttk.Checkbutton) and child.cget("text") == effect:
                            child.state(['!disabled'])
                            break
                    self.staff_effect_note_labels[effect].set("")
                else:
                    if self.staff_effect_vars[effect].get():
                        self.staff_effect_vars[effect].set(False)
                        if effect in self.weapon_data["fixed_effects"]:
                            self.weapon_data["fixed_effects"].remove(effect)
                    for child in self.staff_container.winfo_children():
                        if isinstance(child, ttk.Checkbutton) and child.cget("text") == effect:
                            child.state(['disabled'])
                            break
                    self.staff_effect_note_labels[effect].set("Requires Special Staff")

    def update_aoe_healing_state(self):
        if "Bifröst" in self.weapon_data["fixed_effects"]:
            for effect in self.aoe_healing_effects:
                if effect in self.staff_effect_vars:
                    if self.staff_effect_vars[effect].get():
                        self.staff_effect_vars[effect].set(False)
                        if effect in self.weapon_data["fixed_effects"]:
                            self.weapon_data["fixed_effects"].remove(effect)
                    for child in self.staff_container.winfo_children():
                        if isinstance(child, ttk.Checkbutton) and child.cget("text") == effect:
                            child.state(['disabled'])
                            break
                    self.staff_effect_note_labels[effect].set("Disabled by Bifröst")
            return

        for effect in self.aoe_healing_effects:
            if effect in self.staff_effect_vars:
                if self.rescue_selected:
                    if self.staff_effect_vars[effect].get():
                        self.staff_effect_vars[effect].set(False)
                        if effect in self.weapon_data["fixed_effects"]:
                            self.weapon_data["fixed_effects"].remove(effect)
                    for child in self.staff_container.winfo_children():
                        if isinstance(child, ttk.Checkbutton) and child.cget("text") == effect:
                            child.state(['disabled'])
                            break
                    self.staff_effect_note_labels[effect].set("Disabled by Rescue")
                elif self.recovery_staff_selected and self.special_staff_selected:
                    for child in self.staff_container.winfo_children():
                        if isinstance(child, ttk.Checkbutton) and child.cget("text") == effect:
                            child.state(['!disabled'])
                            break
                    self.staff_effect_note_labels[effect].set("")
                else:
                    if self.staff_effect_vars[effect].get():
                        self.staff_effect_vars[effect].set(False)
                        if effect in self.weapon_data["fixed_effects"]:
                            self.weapon_data["fixed_effects"].remove(effect)
                    for child in self.staff_container.winfo_children():
                        if isinstance(child, ttk.Checkbutton) and child.cget("text") == effect:
                            child.state(['disabled'])
                            break
                    self.staff_effect_note_labels[effect].set("Requires Recovery AND Special Staff")

    def update_bifrost_exclusive_state(self):
        bifrost_selected = "Bifröst" in self.weapon_data["fixed_effects"]

        effects_to_disable = [
            "Heal Scaling", "Recovery Staff", "Interference Staff",
            "Rescue", "Freeze", "Enfeeble", "Buff User", "Buff Ally",
            "Silence", "Hex", "Entrap", "AoE Healing"
        ]

        for effect, var in self.staff_effect_vars.items():
            if effect == "Bifröst":
                continue

            if bifrost_selected:
                if effect in effects_to_disable:
                    if var.get():
                        var.set(False)
                        if effect in self.weapon_data["fixed_effects"]:
                            self.weapon_data["fixed_effects"].remove(effect)
                    for child in self.staff_container.winfo_children():
                        if isinstance(child, ttk.Checkbutton) and child.cget("text") == effect:
                            child.state(['disabled'])
                            break
                    if effect in self.staff_effect_note_labels:
                        self.staff_effect_note_labels[effect].set("Disabled by Bifröst")
                elif effect == "Special Staff":
                    for child in self.staff_container.winfo_children():
                        if isinstance(child, ttk.Checkbutton) and child.cget("text") == effect:
                            child.state(['!disabled'])
                            break
                    if not var.get():
                        var.set(True)
                        if effect not in self.weapon_data["fixed_effects"]:
                            self.weapon_data["fixed_effects"].append(effect)
                    self.special_staff_selected = True
                    if effect in self.staff_effect_note_labels:
                        self.staff_effect_note_labels[effect].set("")
            else:
                for effect_to_restore in effects_to_disable:
                    if effect_to_restore == "Heal Scaling":
                        continue
                    for child in self.staff_container.winfo_children():
                        if isinstance(child, ttk.Checkbutton) and child.cget("text") == effect_to_restore:
                            child.state(['!disabled'])
                            break
                    if effect_to_restore in self.staff_effect_note_labels:
                        current_note = self.staff_effect_note_labels[effect_to_restore].get()
                        if current_note == "Disabled by Bifröst":
                            self.staff_effect_note_labels[effect_to_restore].set("")

                if "Interference Staff" in effects_to_disable:
                    self.interference_staff_selected = False
                if "Recovery Staff" in effects_to_disable:
                    self.recovery_staff_selected = False
                if "Buff User" in effects_to_disable:
                    self.buff_user_active = False
                if "Buff Ally" in effects_to_disable:
                    self.buff_ally_active = False

                if "Heal Scaling" in self.staff_effect_vars:
                    if self.recovery_staff_selected:
                        for child in self.staff_container.winfo_children():
                            if isinstance(child, ttk.Checkbutton) and child.cget("text") == "Heal Scaling":
                                child.state(['!disabled'])
                                break
                        if self.staff_effect_note_labels["Heal Scaling"].get() == "Disabled by Bifröst":
                            self.staff_effect_note_labels["Heal Scaling"].set("")
                    else:
                        for child in self.staff_container.winfo_children():
                            if isinstance(child, ttk.Checkbutton) and child.cget("text") == "Heal Scaling":
                                child.state(['disabled'])
                                break

        if bifrost_selected and "Enfeeble" in effects_to_disable:
            if self.debuff_frame.winfo_viewable():
                self.debuff_frame.grid_remove()
                self.reset_debuffs()

        if "Might" in self.stat_spinboxes:
            if bifrost_selected:
                self.stat_spinboxes["Might"].config(state="disabled")
                self.stat_vars["Might"]["label"].configure(foreground="gray")
                self.stat_vars["Might"]["note"].set("Disabled by Bifröst")
                if self.stat_vars["Might"]["value"].get() != WEAPON_STAT_BASE["Might"]:
                    self.stat_vars["Might"]["value"].set(WEAPON_STAT_BASE["Might"])
                    self.validate_stat("Might")
            else:
                self.update_might_stat_state()

        if "Hit" in self.stat_spinboxes:
            if bifrost_selected:
                self.stat_spinboxes["Hit"].config(state="disabled")
                self.stat_vars["Hit"]["label"].configure(foreground="gray")
                self.stat_vars["Hit"]["note"].set("Disabled by Bifröst")
            else:
                self.update_hit_stat_state()

        if bifrost_selected:
            self.range_combobox.config(state="disabled")
            self.range_note_var.set("Disabled by Bifröst")
        else:
            self.range_combobox.config(state="readonly")
            self.range_note_var.set("")
            self.update_range_options()

        if bifrost_selected:
            self.staff_effect_note_labels["Bifröst"].set("Active - Most effects disabled")
            self.update_interference_effects_state()
            self.update_aoe_healing_state()
        else:
            self.staff_effect_note_labels["Bifröst"].set("")
            self.update_interference_effects_state()
            self.update_aoe_healing_state()
            self.update_hit_stat_state()
            self.update_might_stat_state()

    def update_buff_ally_state(self):
        if "Buff Ally" in self.staff_effect_vars:
            disable_buff_ally = self.interference_staff_selected or self.special_staff_selected

            for child in self.staff_container.winfo_children():
                if isinstance(child, ttk.Checkbutton) and child.cget("text") == "Buff Ally":
                    if disable_buff_ally:
                        child.state(['disabled'])
                        self.staff_effect_note_labels["Buff Ally"].set("Not available with Interference/Special Staff")
                    else:
                        child.state(['!disabled'])
                        current_note = self.staff_effect_note_labels["Buff Ally"].get()
                        if current_note == "Not available with Interference/Special Staff":
                            self.staff_effect_note_labels["Buff Ally"].set("")
                    break

    def update_interference_special_state(self):
        effects_to_disable = ["Interference Staff", "Special Staff"]

        for effect in effects_to_disable:
            if effect in self.staff_effect_vars:
                for child in self.staff_container.winfo_children():
                    if isinstance(child, ttk.Checkbutton) and child.cget("text") == effect:
                        if self.buff_ally_active:
                            child.state(['disabled'])
                            self.staff_effect_note_labels[effect].set("Not available with Buff Ally")
                        else:
                            child.state(['!disabled'])
                            current_note = self.staff_effect_note_labels[effect].get()
                            if current_note == "Not available with Buff Ally":
                                self.staff_effect_note_labels[effect].set("")
                        break

    def update_buff_frame_visibility(self):
        show_buff = self.buff_user_active or self.buff_ally_active

        if show_buff:
            if not self.buff_frame.winfo_viewable():
                self.buff_frame.grid()
                self.update_total_buff_cost()
        else:
            if self.buff_frame.winfo_viewable():
                for stat, var in self.buff_checkboxes.items():
                    var.set(False)
                    self.buff_cost_labels[stat].set("0")
                self.total_buff_cost_var.set("0")
                self.buff_frame.grid_remove()

    def update_debuff_frame_visibility(self):
        show_debuff = (self.type_combobox.get() in ["Dagger", "Shuriken"] or
                       "Debuff on Hit" in self.weapon_data["fixed_effects"] or
                       "Enfeeble" in self.weapon_data["fixed_effects"])

        if show_debuff:
            if not self.debuff_frame.winfo_viewable():
                self.debuff_frame.grid()
        else:
            if self.debuff_frame.winfo_viewable():
                self.reset_debuffs()
                self.debuff_frame.grid_remove()

    def update_fixed_effects_visibility(self):
        if self.type_combobox.get() in ["Staff", "Rod"]:
            self.fixed_effects_frame.grid_remove()
        else:
            self.fixed_effects_frame.grid()
        self._update_ineffective_state()

    def update_staff_warning(self):
        weapon_type = self.type_combobox.get()

        if weapon_type in ["Staff", "Rod"]:
            if not (self.recovery_staff_selected or self.interference_staff_selected or
                    self.special_staff_selected or self.rescue_selected):
                if self.staff_warning_label is None:
                    self.staff_warning_label = ttk.Label(self.staff_container,
                        text="⚠ WARNING: You must select 'Recovery Staff', 'Interference Staff', 'Special Staff', or 'Rescue'!",
                        foreground="red", font=('TkDefaultFont', 9, 'bold'))
                    self.staff_warning_label.grid(row=len(self.staff_effects) + 1, column=0, columnspan=4, sticky="w", padx=5, pady=5)
                else:
                    self.staff_warning_label.config(
                        text="⚠ WARNING: You must select 'Recovery Staff', 'Interference Staff', 'Special Staff', or 'Rescue'!",
                        foreground="red")
                    self.staff_warning_label.grid()
            else:
                if self.staff_warning_label is None:
                    self.staff_warning_label = ttk.Label(self.staff_container,
                        text="✓ Staff type selected - Ready to create weapon",
                        foreground="green", font=('TkDefaultFont', 9, 'bold'))
                    self.staff_warning_label.grid(row=len(self.staff_effects) + 1, column=0, columnspan=4, sticky="w", padx=5, pady=5)
                else:
                    self.staff_warning_label.config(text="✓ Staff type selected - Ready to create weapon", foreground="green")
                    self.staff_warning_label.grid()
        else:
            if self.staff_warning_label is not None:
                self.staff_warning_label.grid_remove()

    def update_silver_weapon_cost(self):
        if "Silver Weapon" in self.fixed_effect_cost_labels:
            self.fixed_effect_cost_labels["Silver Weapon"].config(text=self._fmt_cost(SILVER_WEAPON_COST_PHYSICAL), foreground="blue")
            self.fixed_effect_note_labels["Silver Weapon"].set("")
            self.silver_weapon_adjusted_cost = SILVER_WEAPON_COST_PHYSICAL

    def update_s_rank_debuff_cost(self):
        if "S Rank Debuff" in self.fixed_effect_cost_labels:
            self.fixed_effect_cost_labels["S Rank Debuff"].config(text=self._fmt_cost(S_RANK_DEBUFF_COST_PHYSICAL), foreground="blue")
            self.fixed_effect_note_labels["S Rank Debuff"].set("")
            self.s_rank_debuff_adjusted_cost = S_RANK_DEBUFF_COST_PHYSICAL

    def update_might_multiplier_notes(self):
        multiplier_effects = []
        if self.one_tap_active:
            multiplier_effects.append("One Tap: Might cost x1.5")
        if self.venge_active:
            multiplier_effects.append("Venge: Might cost x1.5")
        if self.skillful_active:
            multiplier_effects.append("Skillful: Might cost x2")
        if self.flier_slayer_active:
            multiplier_effects.append("Flier Slayer: Might cost x1.5")
        if self.dragon_slayer_active:
            multiplier_effects.append("Dragon Slayer: Might cost x1.5")
        if self.beast_slayer_active:
            multiplier_effects.append("Beast Slayer: Might cost x1.5")
        if self.armor_slayer_active:
            multiplier_effects.append("Armor Slayer: Might cost x1.5")

        if multiplier_effects:
            self.stat_vars["Might"]["note"].set(" | ".join(multiplier_effects))
        else:
            self.stat_vars["Might"]["note"].set("")

    def set_staff_rod_stats_state(self, enabled):
        disabled_stats = ["Crit", "Avoid", "Dodge", "Mov", "Effective Speed Offensive", "Effective Speed Defensive"]

        state = "normal" if enabled else "disabled"
        label_color = "black" if enabled else "gray"

        for stat in disabled_stats:
            if stat in self.stat_spinboxes:
                self.stat_spinboxes[stat].config(state=state)
                if not enabled:
                    self.stat_vars[stat]["value"].set(0)
                    self.validate_stat(stat)

            if stat in self.stat_vars:
                self.stat_vars[stat]["label"].configure(foreground=label_color)

        self.update_staff_stats_state(not enabled)
        self.update_might_cost_for_staff()

    def update_staff_stats_state(self, enabled):
        staff_stats = ["Base Staff Exp", "Uses"]

        state = "normal" if enabled else "disabled"
        label_color = "black" if enabled else "gray"

        for stat in staff_stats:
            if stat in self.stat_spinboxes:
                self.stat_spinboxes[stat].config(state=state)
                if not enabled:
                    self.stat_vars[stat]["value"].set(WEAPON_STAT_BASE[stat])
                    self.validate_stat(stat)

            if stat in self.stat_vars:
                self.stat_vars[stat]["label"].configure(foreground=label_color)

    # ------------------------------------------------------------------------
    # Helper Methods
    # ------------------------------------------------------------------------

    def calculate_might_cost_multiplier(self):
        multiplier = 1.0
        if self.one_tap_active:
            multiplier *= MIGHT_COST_MULTIPLIERS["One Tap"]
        if self.venge_active:
            multiplier *= MIGHT_COST_MULTIPLIERS["Venge"]
        if self.skillful_active:
            multiplier *= MIGHT_COST_MULTIPLIERS["Skillful"]
        if self.flier_slayer_active:
            multiplier *= MIGHT_COST_MULTIPLIERS["Flier Slayer"]
        if self.dragon_slayer_active:
            multiplier *= MIGHT_COST_MULTIPLIERS["Dragon Slayer"]
        if self.beast_slayer_active:
            multiplier *= MIGHT_COST_MULTIPLIERS["Beast Slayer"]
        if self.armor_slayer_active:
            multiplier *= MIGHT_COST_MULTIPLIERS["Armor Slayer"]
        return multiplier

    def force_bronze_and_bold(self, force=True):
        if not NOSFERATU_FORCES_BRONZE_AND_BOLD:
            return

        if force:
            # Store trace IDs when forcing
            if "Bronze Weapon" in self.fixed_effect_vars:
                if not self.fixed_effect_vars["Bronze Weapon"].get():
                    self.bronze_was_forced = True
                    self.fixed_effect_vars["Bronze Weapon"].set(True)
                    self.on_fixed_effect_toggle("Bronze Weapon", self.fixed_effect_vars["Bronze Weapon"])
                
                # Remove existing trace if any, then add new one
                if hasattr(self, '_bronze_trace_id'):
                    try:
                        self.fixed_effect_vars["Bronze Weapon"].trace_remove('write', self._bronze_trace_id)
                    except (KeyError, ValueError, AttributeError):
                        pass  # Trace didn't exist or was already removed
                    finally:
                        delattr(self, '_bronze_trace_id')

            if "Bold Weapon" in self.fixed_effect_vars:
                if not self.fixed_effect_vars["Bold Weapon"].get():
                    self.bold_was_forced = True
                    self.fixed_effect_vars["Bold Weapon"].set(True)
                    self.on_fixed_effect_toggle("Bold Weapon", self.fixed_effect_vars["Bold Weapon"])
                
                if hasattr(self, '_bold_trace_id'):
                    try:
                        self.fixed_effect_vars["Bold Weapon"].trace_remove('write', self._bold_trace_id)
                    except (KeyError, ValueError, AttributeError):
                        pass  # Trace didn't exist or was already removed
                    finally:
                        delattr(self, '_bold_trace_id')

            if "Bronze Weapon" in self.fixed_effect_note_labels:
                self.fixed_effect_note_labels["Bronze Weapon"].set("Forced by Nosferatu")
            if "Bold Weapon" in self.fixed_effect_note_labels:
                self.fixed_effect_note_labels["Bold Weapon"].set("Forced by Nosferatu")
            # Disable the checkbuttons so the user cannot uncheck them
            for fx in ("Bronze Weapon", "Bold Weapon"):
                if fx in self.fixed_effect_checkbuttons:
                    self.fixed_effect_checkbuttons[fx].state(["disabled"])
        else:
            # Re-enable checkbuttons when Nosferatu is removed
            for fx in ("Bronze Weapon", "Bold Weapon"):
                if fx in self.fixed_effect_checkbuttons:
                    self.fixed_effect_checkbuttons[fx].state(["!disabled"])
            # Remove traces when unforcing
            if self.bronze_was_forced and "Bronze Weapon" in self.fixed_effect_vars:
                if hasattr(self, '_bronze_trace_id'):
                    try:
                        self.fixed_effect_vars["Bronze Weapon"].trace_remove('write', self._bronze_trace_id)
                        delattr(self, '_bronze_trace_id')
                    except (tk.TclError, ValueError, AttributeError):
                        pass
                self.fixed_effect_vars["Bronze Weapon"].set(False)
                self.on_fixed_effect_toggle("Bronze Weapon", self.fixed_effect_vars["Bronze Weapon"])
                self.bronze_was_forced = False

            if self.bold_was_forced and "Bold Weapon" in self.fixed_effect_vars:
                if hasattr(self, '_bold_trace_id'):
                    try:
                        self.fixed_effect_vars["Bold Weapon"].trace_remove('write', self._bold_trace_id)
                        delattr(self, '_bold_trace_id')
                    except (tk.TclError, ValueError, AttributeError):
                        pass
                self.fixed_effect_vars["Bold Weapon"].set(False)
                self.on_fixed_effect_toggle("Bold Weapon", self.fixed_effect_vars["Bold Weapon"])
                self.bold_was_forced = False

            if "Bronze Weapon" in self.fixed_effect_note_labels:
                self.fixed_effect_note_labels["Bronze Weapon"].set("")
            if "Bold Weapon" in self.fixed_effect_note_labels:
                self.fixed_effect_note_labels["Bold Weapon"].set("")

    def reset_debuffs(self):
        if hasattr(self, 'debuff_vars'):
            for stat, data in self.debuff_vars.items():
                data["var"].set(0)
                self.debuff_cost_vars[stat].set("0")
            self.total_debuff_cost_var.set("0")
            self.update_total_debuff_cost()

    def reset_confirmation_cancel(self):
        """Cancel the reset confirmation after timeout."""
        if not self.reset_confirmation_needed:
            self.reset_confirmation_needed = True
            self.reset_button.config(text="Reset")
            
    def reset_weapon(self):
        # Check if confirmation is needed
        if self.reset_confirmation_needed:
            self.reset_confirmation_needed = False
            self.reset_button.config(text="Click Again to Confirm Reset")
            self.window.after(3000, self.reset_confirmation_cancel)
            return
        
        # Reset confirmation flag
        self.reset_confirmation_needed = True
        self.reset_button.config(text="Reset")

        self.name_entry.delete(0, tk.END)
        self.type_combobox.set("Sword")
        self.update_value_effects_availability()
        self.custom_type_frame.grid_remove()
        self.custom_type_entry.delete(0, tk.END)
        self.weapon_hint_var.set("")

        self.magic_weapon_active = False
        self.silver_weapon_active = False
        self.silver_weapon_adjusted_cost = -8.69
        self.s_rank_debuff_active = False
        self.s_rank_debuff_adjusted_cost = -22.01

        self.one_tap_active = False
        self.venge_active = False
        self.skillful_active = False
        self.flier_slayer_active = False
        self.dragon_slayer_active = False
        self.beast_slayer_active = False
        self.armor_slayer_active = False

        self.nosferatu_active = False
        self.bronze_was_forced = False
        self.bold_was_forced = False

        for effect in self.fixed_effect_note_labels:
            self.fixed_effect_note_labels[effect].set("")

        if "Silver Weapon" in self.fixed_effect_cost_labels:
            self.fixed_effect_cost_labels["Silver Weapon"].config(text=self._fmt_cost(SILVER_WEAPON_COST_PHYSICAL), foreground="blue")
        if "S Rank Debuff" in self.fixed_effect_cost_labels:
            self.fixed_effect_cost_labels["S Rank Debuff"].config(text=self._fmt_cost(S_RANK_DEBUFF_COST_PHYSICAL), foreground="blue")

        if "Might" in self.stat_vars:
            self.stat_vars["Might"]["note"].set("")

        for stat, info in self.weapon_stats.items():
            self.stat_vars[stat]["value"].set(info["base"])
            self.stat_vars[stat]["cost"].set("0")
            self.weapon_data[stat.lower().replace(" ", "_")] = info["base"]

        if "Bronze Weapon" in self.fixed_effect_vars:
            if hasattr(self, '_bronze_trace_id'):
                try:
                    self.fixed_effect_vars["Bronze Weapon"].trace_remove('write', self._bronze_trace_id)
                    delattr(self, '_bronze_trace_id')
                except (tk.TclError, ValueError, AttributeError):
                    pass
        if "Bold Weapon" in self.fixed_effect_vars:
            if hasattr(self, '_bold_trace_id'):
                try:
                    self.fixed_effect_vars["Bold Weapon"].trace_remove('write', self._bold_trace_id)
                    delattr(self, '_bold_trace_id')
                except (tk.TclError, ValueError, AttributeError):
                    pass

        # Reset fixed effects checkboxes
        for effect, var in self.fixed_effect_vars.items():
            if var.get():
                var.set(False)
                self.on_fixed_effect_toggle(effect, var)
        self.weapon_data["fixed_effects"] = []

        # Reset staff effects
        if hasattr(self, 'staff_effect_vars'):
            for effect, var in self.staff_effect_vars.items():
                if var.get():
                    var.set(False)
                    self.on_staff_effect_toggle(effect, var)
            self.recovery_staff_selected = False
            self.interference_staff_selected = False
            self.special_staff_selected = False
            self.rescue_selected = False
            self.buff_user_active = False
            self.buff_ally_active = False
            self.unlimited_uses_active = False
            self.bifrost_selected = False
            self.aoe_healing_selected = False
            self.enfeeble_was_active = False
            self.update_interference_effects_state()

        # Reset buff checkboxes
        if hasattr(self, 'buff_checkboxes'):
            for stat, var in self.buff_checkboxes.items():
                if var.get():
                    var.set(False)
            for stat in self.buff_cost_labels:
                self.buff_cost_labels[stat].set("0")
            self.total_buff_cost_var.set("0")

        self.unlimited_uses_active = False
        self.update_uses_stat_state()

        self.set_staff_rod_stats_state(True)
        self.update_might_stat_state()
        self.update_hit_stat_state()

        if self.staff_warning_label is not None:
            self.staff_warning_label.grid_remove()

        if hasattr(self, 'staff_frame') and self.staff_frame_visible:
            self.staff_frame.grid_remove()
            self.staff_frame_visible = False

        self.range_var.set("1")
        self.range_cost_var.set("0")
        self.weapon_data["range"] = "1"
        self.on_range_change()

        # Reset value effects
        for effect, var in self.value_effect_vars.items():
            if var.get():
                var.set(False)
                self.on_value_effect_toggle(effect, var)
        self.weapon_data["value_effects"] = []
        self.effect_value_var.set(0)
        self.effect_value_total_cost_var.set("0")
        self.weapon_data["effect_value"] = 0
        self.weapon_data["value_effects_cost"] = 0.0

        # Reset value effect descriptions to default
        for effect in self.value_effect_desc_vars:
            self.value_effect_desc_vars[effect].set(VALUE_EFFECTS_CONFIG[effect]['desc'])
            if effect in self.value_effect_desc_labels:
                self.value_effect_desc_labels[effect].configure(foreground="gray")

        # Reset current and next cost displays
        for effect in self.value_effect_current_cost_vars:
            self.value_effect_current_cost_vars[effect].set("0")
            self.value_effect_next_plus_cost_vars[effect].set("0")
            self.value_effect_next_minus_cost_vars[effect].set("0")

        # Reset debuffs
        if hasattr(self, 'debuff_vars'):
            for stat, data in self.debuff_vars.items():
                data["var"].set(0)
                self.debuff_cost_vars[stat].set("0")
            self.total_debuff_cost_var.set("0")
            self.weapon_data["debuffs"] = {}
        self.debuff_frame.grid_remove()

        # Reset buff frame visibility
        if hasattr(self, 'buff_frame') and self.buff_frame.winfo_viewable():
            self.buff_frame.grid_remove()

        self.desc_text.delete("1.0", tk.END)
        self.weapon_data["description"] = ""

        self.update_fixed_effects_visibility()

        self.weapon_data["custom_type"] = ""
        self.weapon_data["name"] = ""

        self.remaining_weapon_points = self.weapon_points
        self.points_var.set(str(self.weapon_points))

        # Force a full UI update
        self.update_total_cost()
        self.update_value_effect_costs()

    def _validate_weapon_export(self):
        """Run all pre-export checks for the weapon. Returns (ok, errors) tuple."""
        errors = []
        if not self.weapon_data.get("name", "").strip():
            errors.append("\u2022 Weapon name is required.")
        if not self.type_combobox.get():
            errors.append("\u2022 Weapon type must be selected.")
        self.update_total_cost()
        if self.remaining_weapon_points < 0:
            errors.append(
                f"\u2022 Over budget by {abs(round(self.remaining_weapon_points))} points "
                f"(limit is {self.weapon_points:.0f})."
            )
        active_value_effects = [e for e, var in self.value_effect_vars.items() if var.get()]
        if active_value_effects and _safe_get(self.effect_value_var, 0) == 0:
            errors.append(
                f"\u2022 Value effect(s) selected ({', '.join(active_value_effects)}) "
                f"but the shared effect value is 0 - set a non-zero value."
            )
        for ineff in ("Ineffective MT", "Ineffective Hit"):
            if (ineff in self.fixed_effect_vars
                    and self.fixed_effect_vars[ineff].get()
                    and not self._has_effective_effect()):
                errors.append(f"\u2022 '{ineff}' is checked but no Slayer effect is active.")
        if self.type_combobox.get() in ["Staff", "Rod"]:
            active_staff = [e for e, var in self.staff_effect_vars.items() if var.get()]
            if not active_staff:
                errors.append("\u2022 Staff / Rod weapons must have at least one Staff Effect selected.")
        return len(errors) == 0, errors

    def create_weapon(self):
        if not self.weapon_data["name"]:
            messagebox.showwarning("Missing Name", "Please enter a weapon name.", parent=self.window)
            return

        if self.type_combobox.get() == "Other" and not self.custom_type_entry.get():
            messagebox.showwarning("Missing Custom Type", "Please enter a custom weapon type.", parent=self.window)
            return

        if self.type_combobox.get() in ["Staff", "Rod"]:
            if not (self.recovery_staff_selected or self.interference_staff_selected or self.special_staff_selected):
                messagebox.showwarning(
                    "Missing Staff Type",
                    "Staff/Rod weapons require 'Recovery Staff', 'Interference Staff', or 'Special Staff' to be selected.\n"
                    "Please choose at least one before creating the weapon.",
                    parent=self.window
                )
                return

        self.update_total_cost()

        if self.remaining_weapon_points < 0:
            messagebox.showwarning("Too Many Points",
                                   f"Weapon uses {abs(round(self.remaining_weapon_points))} extra points!\n"
                                   f"Reduce stats or effects to fit within {self.weapon_points} points.",
                                   parent=self.window)
            return

        # Stats
        for stat in self.weapon_stats.keys():
            key = stat.lower().replace(" ", "_")
            self.weapon_data[key] = self.stat_vars[stat]["value"].get()

        # Range
        self.weapon_data["range"] = self.range_var.get()

        # Type and custom type
        if self.type_combobox.get() == "Other":
            self.weapon_data["type"] = self.custom_type_entry.get()
        else:
            self.weapon_data["type"] = self.type_combobox.get()
        
        self.weapon_data["custom_type"] = self.custom_type_entry.get()

        # Fixed effects
        self.weapon_data["fixed_effects"] = [e for e, var in self.fixed_effect_vars.items() if var.get()]
        
        # Value effects
        self.weapon_data["value_effects"] = self.weapon_data["value_effects"]
        
        # Effect value and its cost
        self.weapon_data["effect_value"] = self.effect_value_var.get()
        self.weapon_data["value_effects_cost"] = float(self.effect_value_total_cost_var.get())
        
        # Staff/Rod specific data
        if self.type_combobox.get() in ["Staff", "Rod"]:
            self.weapon_data["staff_effects"] = [e for e, var in self.staff_effect_vars.items() if var.get()]
            self.weapon_data["recovery_staff"] = self.recovery_staff_selected
            self.weapon_data["interference_staff"] = self.interference_staff_selected
            self.weapon_data["special_staff"] = self.special_staff_selected
            self.weapon_data["unlimited_uses"] = self.unlimited_uses_active
            self.weapon_data["buff_user"] = self.buff_user_active
            self.weapon_data["buff_ally"] = self.buff_ally_active
            
            if self.buff_user_active or self.buff_ally_active:
                self.weapon_data["buffs"] = [stat for stat, var in self.buff_checkboxes.items() if var.get()]

        # Debuffs
        if self.debuff_frame.winfo_viewable() and hasattr(self, 'debuff_vars'):
            self.weapon_data["debuffs"] = {}
            for stat, data in self.debuff_vars.items():
                value = data["var"].get()
                if value > 0:
                    self.weapon_data["debuffs"][stat.lower()] = value

        # Description
        self.weapon_data["description"] = self.desc_text.get("1.0", tk.END).strip()

        # Cost summary
        self.weapon_data["total_cost"] = self.weapon_points - self.remaining_weapon_points
        self.weapon_data["remaining_points"] = self.remaining_weapon_points

        # Send to callback (main window)
        self.callback(self.weapon_data)
        
        # Silently export the weapon to file (no success message)
        self.export_weapon(silent=True)
        
        # Brief visual feedback - flash the window or show a quick status
        self.window.configure(bg="#90EE90")  # Light green flash
        self.window.after(200, lambda: self.window.configure(bg=self.window.cget("bg")))
        
        # Don't close - keep the window open
        # self.window.destroy()  # REMOVED

    def export_weapon(self, silent=False):
        """Export the current weapon data to a JSON file."""
        ok, errors = self._validate_weapon_export()
        if not ok:
            if not silent:
                messagebox.showerror(
                    "Export Failed — Validation Errors",
                    "Please fix the following before exporting:\n\n" + "\n".join(errors),
                    parent=self.window
                )
            return

        # Make sure all data is up to date
        self.update_total_cost()
        
        # Prepare export data with all current values
        export_data = {
            "name": self.weapon_data["name"],
            "type": self.weapon_data["type"],
            "custom_type": self.weapon_data["custom_type"],
            "might": self.stat_vars["Might"]["value"].get(),
            "hit": self.stat_vars["Hit"]["value"].get(),
            "crit": self.stat_vars["Crit"]["value"].get(),
            "avoid": self.stat_vars["Avoid"]["value"].get(),
            "dodge": self.stat_vars["Dodge"]["value"].get(),
            "mov": self.stat_vars["Mov"]["value"].get(),
            "effective_speed_offensive": self.stat_vars["Effective Speed Offensive"]["value"].get(),
            "effective_speed_defensive": self.stat_vars["Effective Speed Defensive"]["value"].get(),
            "base_staff_exp": self.stat_vars["Base Staff Exp"]["value"].get(),
            "uses": self.stat_vars["Uses"]["value"].get(),
            "range": self.range_var.get(),
            "fixed_effects": [e for e, var in self.fixed_effect_vars.items() if var.get()],
            "value_effects": self.weapon_data["value_effects"],
            "effect_value": self.effect_value_var.get(),
            "value_effects_cost": float(self.effect_value_total_cost_var.get()),
            "description": self.desc_text.get("1.0", tk.END).strip(),
            "total_cost": self.weapon_points - self.remaining_weapon_points,
            "version": VERSION,  # For verification
        }
        
        # Add staff-specific data if applicable
        if self.type_combobox.get() in ["Staff", "Rod"]:
            export_data["staff_effects"] = [e for e, var in self.staff_effect_vars.items() if var.get()]
            export_data["recovery_staff"] = self.recovery_staff_selected
            export_data["interference_staff"] = self.interference_staff_selected
            export_data["special_staff"] = self.special_staff_selected
            export_data["unlimited_uses"] = self.unlimited_uses_active
            export_data["buff_user"] = self.buff_user_active
            export_data["buff_ally"] = self.buff_ally_active
            
            if self.buff_user_active or self.buff_ally_active:
                export_data["buffs"] = [stat for stat, var in self.buff_checkboxes.items() if var.get()]
        
        # Add debuffs if any
        if hasattr(self, 'debuff_vars') and self.debuff_frame.winfo_viewable():
            export_data["debuffs"] = {}
            for stat, data in self.debuff_vars.items():
                value = data["var"].get()
                if value > 0:
                    export_data["debuffs"][stat.lower()] = value
        
        # Generate filename
        safe_name = self.weapon_data["name"].replace(" ", "_").replace("/", "_").replace("\\", "_")
        filename = f"weapon_{safe_name}.json"

        if os.path.exists(filename):
            if not messagebox.askyesno(
                "File Already Exists",
                f"\"{filename}\" already exists.\n\nOverwrite it?",
                parent=self.window
            ):
                return

        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            if not silent:
                messagebox.showinfo("Export Successful", f"Weapon exported to:\n{filename}", parent=self.window)
        except Exception as e:
            messagebox.showerror("Export Failed", f"Failed to save weapon:\n{str(e)}", parent=self.window)
            
    def _load_weapon_data(self, weapon_data, announce=False):
        """Load a weapon data dict into the UI. Shared by file import, the
        open-creator pre-load, and the character-import auto-reload.

        announce=True shows a success popup when the file verifies clean (used by
        explicit Import); otherwise the post-load verification is silent on success.
        """
        required = ["name", "type", "might", "hit", "crit"]
        if not all(f in weapon_data for f in required):
            return
        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(0, weapon_data.get("name", ""))
        self.weapon_data["name"] = weapon_data.get("name", "")
        if weapon_data["type"] in self.type_combobox['values']:
            self.type_combobox.set(weapon_data["type"])
        else:
            self.type_combobox.set("Other")
            self.custom_type_entry.delete(0, tk.END)
            self.custom_type_entry.insert(0, weapon_data["type"])
            self.custom_type_frame.grid()
        self.on_type_change()
        stat_mapping = {
            "Might": "might", "Hit": "hit", "Crit": "crit",
            "Avoid": "avoid", "Dodge": "dodge", "Mov": "mov",
            "Effective Speed Offensive": "effective_speed_offensive",
            "Effective Speed Defensive": "effective_speed_defensive",
            "Base Staff Exp": "base_staff_exp", "Uses": "uses"
        }
        for stat_name, key in stat_mapping.items():
            if key in weapon_data:
                self.stat_vars[stat_name]["value"].set(weapon_data[key])
                self.validate_stat(stat_name)
        if "range" in weapon_data:
            self.range_var.set(weapon_data["range"])
            self.on_range_change()
        if "fixed_effects" in weapon_data:
            for effect, var in self.fixed_effect_vars.items():
                if effect in weapon_data["fixed_effects"]:
                    var.set(True)
                    self.on_fixed_effect_toggle(effect, var)
        if "value_effects" in weapon_data:
            for effect in weapon_data["value_effects"]:
                if effect in self.value_effect_vars:
                    self.value_effect_vars[effect].set(True)
                    self.on_value_effect_toggle(effect, self.value_effect_vars[effect])
        if "effect_value" in weapon_data:
            self.effect_value_var.set(weapon_data["effect_value"])
            self.on_effect_value_change()
        if "description" in weapon_data:
            self.desc_text.delete("1.0", tk.END)
            self.desc_text.insert("1.0", weapon_data["description"])
        if self.type_combobox.get() in ["Staff", "Rod"]:
            if "staff_effects" in weapon_data:
                for effect in weapon_data["staff_effects"]:
                    if effect in self.staff_effect_vars:
                        self.staff_effect_vars[effect].set(True)
                        self.on_staff_effect_toggle(effect, self.staff_effect_vars[effect])
            if weapon_data.get("unlimited_uses"):
                self.staff_effect_vars["Unlimited Uses"].set(True)
                self.on_staff_effect_toggle("Unlimited Uses", self.staff_effect_vars["Unlimited Uses"])
            # Buff User / Buff Ally
            if weapon_data.get("buff_user"):
                self.staff_effect_vars["Buff User"].set(True)
                self.on_staff_effect_toggle("Buff User", self.staff_effect_vars["Buff User"])
            if weapon_data.get("buff_ally"):
                self.staff_effect_vars["Buff Ally"].set(True)
                self.on_staff_effect_toggle("Buff Ally", self.staff_effect_vars["Buff Ally"])
            if "buffs" in weapon_data and (weapon_data.get("buff_user") or weapon_data.get("buff_ally")):
                for stat in weapon_data["buffs"]:
                    if stat in self.buff_checkboxes:
                        self.buff_checkboxes[stat].set(True)
                        self.update_buff_cost(stat)
        # Debuffs (any weapon type; ensure the debuff frame is visible first)
        if "debuffs" in weapon_data:
            if not self.debuff_frame.winfo_viewable() and "Debuff on Hit" in self.fixed_effect_vars:
                self.fixed_effect_vars["Debuff on Hit"].set(True)
                self.on_fixed_effect_toggle("Debuff on Hit", self.fixed_effect_vars["Debuff on Hit"])
            for stat, value in weapon_data["debuffs"].items():
                stat_cap = stat.capitalize()
                if stat_cap in self.debuff_vars:
                    self.debuff_vars[stat_cap]["var"].set(value)
                    self.update_debuff_cost(stat_cap)

        # Force a full UI refresh
        self.update_total_cost()
        self.update_value_effect_costs()
        self.update_value_effects_availability()

        # Recompute-and-verify the loaded weapon. Silent on clean unless announce.
        issues = self._verify_imported_weapon(weapon_data)
        _show_import_verification(self.window, "weapon",
                                  weapon_data.get("name", ""),
                                  weapon_data.get("version"), issues,
                                  show_success=announce)

    def _verify_imported_weapon(self, weapon_data):
        """Compare a freshly loaded weapon file against the tool's recomputed cost.

        The UI has already loaded and recalculated, so self.remaining_weapon_points
        is the true cost. Returns a list of discrepancy strings (empty = clean)."""
        issues = list(_verify_weapon_raw(weapon_data, self.weapon_points))
        recomputed = self.weapon_points - self.remaining_weapon_points
        claimed = weapon_data.get("total_cost")
        if isinstance(claimed, (int, float)) and abs(round(claimed) - round(recomputed)) >= 1:
            issues.append(
                f"Claimed cost {round(claimed)} does not match the recomputed cost "
                f"{round(recomputed)}")
        if recomputed > self.weapon_points + 0.5:
            issues.append(
                f"Recomputed cost {round(recomputed)} is over the {self.weapon_points}-point "
                f"budget by {round(recomputed - self.weapon_points)}")
        claimed_ve = weapon_data.get("value_effects_cost")
        if isinstance(claimed_ve, (int, float)):
            true_ve = float(self.effect_value_total_cost_var.get())
            if abs(round(claimed_ve) - round(true_ve)) >= 1:
                issues.append(
                    f"Claimed value-effects cost {round(claimed_ve)} does not match the "
                    f"recomputed {round(true_ve)}")
        return issues

    def import_weapon(self):
        """Import a weapon from a JSON file and load all its data."""
        filename = filedialog.askopenfilename(
            title="Select Weapon File",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if not filename:
            return
        try:
            with open(filename, "r", encoding="utf-8") as f:
                weapon_data = json.load(f)

            required_fields = ["name", "type", "might", "hit", "crit", "avoid", "dodge", "mov", "range"]
            for field in required_fields:
                if field not in weapon_data:
                    raise ValueError(f"Missing required field: {field}")

            # Shared loader handles all field loading + recompute-and-verify.
            self._load_weapon_data(weapon_data, announce=True)

        except Exception as e:
            messagebox.showerror("Import Failed", f"Failed to load weapon:\n{str(e)}", parent=self.window)
            import traceback
            traceback.print_exc()

# ============================================================================
# MAIN CHARACTER CREATOR WINDOW
# ============================================================================

class CharacterCreator:
    def __init__(self, root):
        print("CharacterCreator init starting...")
        self.root = root
        self.root.title(f"Character Creator - Fire Emblem Fates Tool v{VERSION}")
        self.selected_skills = []
        self.skill_slots = [None] * MAX_SKILLS   # slot index -> skill name or None
        self.remaining_points = initial_points
        self.points_var = tk.StringVar(value=str(int(self.remaining_points)))

        self.attribute_costs = ATTRIBUTE_COSTS

        self.attributes = list(self.attribute_costs.keys())
        self.growth_vars = {}
        self.cost_vars = {}
        self.spinboxes = {}
        self.base_vars = {}

        self.next_step_cost_vars = {}
        self.next_step_labels = {}
        self.secondary_next_cost_vars = {}
        self.secondary_next_labels = {}

        self.secondary_stats_vars = {}
        self.secondary_cost_vars = {}
        self.secondary_spinboxes = {}

        self.weapon_points = 100
        self.weapon_points_var = tk.StringVar(value="100")
        self.custom_weapon_name_var = tk.StringVar()
        self.weapon_type_var = tk.StringVar(value="Sword")

        self.reset_confirmation_needed = False

        self.setup_ui()

    # ------------------------------------------------------------------------
    # UI Setup
    # ------------------------------------------------------------------------

    def setup_ui(self):
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill="both", expand=True)

        # Fixed header — always visible, never scrolls
        header_frame = ttk.Frame(main_frame, relief="groove", padding=(10, 6))
        header_frame.pack(side="top", fill="x")
        ttk.Label(header_frame, text="Remaining Points:",
                  font=('TkDefaultFont', 11, 'bold')).pack(side="left")
        self.points_header_label = ttk.Label(header_frame, textvariable=self.points_var,
                                             font=('TkDefaultFont', 11, 'bold'), foreground="blue")
        self.points_header_label.pack(side="left", padx=(6, 20))
        # System buttons in header
        self.reset_button = ttk.Button(header_frame, text="Reset Character", command=self.reset_character,
                                       width=28)
        self.reset_button.pack(side="right", padx=5)
        ttk.Button(header_frame, text="Import Character", command=self.import_character).pack(side="right", padx=5)
        ttk.Button(header_frame, text="Export Character", command=self.export_character).pack(side="right", padx=5)

        # Scrollable content area below the header
        scroll_container = ttk.Frame(main_frame)
        scroll_container.pack(side="top", fill="both", expand=True)

        canvas = tk.Canvas(scroll_container)
        scrollbar = ttk.Scrollbar(scroll_container, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Mousewheel scrolling — bind on scrollable_frame so it works
        # everywhere inside the scrollable area, not just over the bare canvas
        def _char_scroll(ev):
            if isinstance(ev.widget, (tk.Spinbox, ttk.Spinbox)):
                return
            canvas.yview_scroll(int(-1 * (ev.delta / 120)), "units")
        def _bind_scroll(e=None):
            scroll_container.bind_all("<MouseWheel>", _char_scroll)
        def _unbind_scroll(e=None):
            scroll_container.unbind_all("<MouseWheel>")
        scroll_container.bind("<Enter>", lambda e: _bind_scroll())
        scroll_container.bind("<Leave>", lambda e: _unbind_scroll())

        self.setup_info_frame(scrollable_frame)
        self.setup_skills_frame(scrollable_frame)
        self.setup_growth_frame(scrollable_frame)
        self.setup_combat_frame(scrollable_frame)
        self.setup_stance_frame(scrollable_frame)
        self.setup_pairup_frame(scrollable_frame)
        self.setup_secondary_frame(scrollable_frame)

    def _int_vcmd(self):
        return _make_int_vcmd(self.root)

    def _uint_vcmd(self):
        return _make_int_vcmd(self.root, allow_negative=False)

    def setup_info_frame(self, parent):
        frame = ttk.LabelFrame(parent, text="Character Info", padding=10)
        frame.pack(fill="x", padx=10, pady=10)
        _info_ci = tk.Label(frame, text=" ? ", relief="groove",
                            background="#4a90d9", foreground="white",
                            font=("TkDefaultFont", 9, "bold"), cursor="hand2")
        _info_ci.grid(row=0, column=2, sticky="w", padx=(10, 0))
        Tooltip(_info_ci,
                "Assume your character is in a special class, no promotion. "
                "Starting with unpromoted movement, promoted movement is going "
                "to be handled in another way.",
                delay_ms=400)

        ttk.Label(frame, text="Character Name:").grid(row=0, column=0, sticky="w")
        self.name_entry = ttk.Entry(frame)
        self.name_entry.grid(row=0, column=1, sticky="ew")

        ttk.Label(frame, text="Class Name:").grid(row=1, column=0, sticky="w")
        self.class_entry = ttk.Entry(frame)
        self.class_entry.grid(row=1, column=1, sticky="ew")

        ttk.Label(frame, text="Character Description (Ingame):").grid(row=2, column=0, sticky="w")
        self.char_desc_entry = scrolledtext.ScrolledText(frame, height=2, width=60)
        self.char_desc_entry.grid(row=3, column=0, columnspan=2, sticky="ew", pady=5)

        ttk.Label(frame, text="Class Description (Ingame):").grid(row=4, column=0, sticky="w")
        self.class_desc_entry = scrolledtext.ScrolledText(frame, height=2, width=60)
        self.class_desc_entry.grid(row=5, column=0, columnspan=2, sticky="ew", pady=5)

        ttk.Label(frame, text="Birthday (MM/DD):").grid(row=6, column=0, sticky="w")
        # Two separate fields with a fixed "/" label between them
        bday_frame = ttk.Frame(frame)
        bday_frame.grid(row=6, column=1, sticky="w")
        vcmd_mm = (self.root.register(self._validate_birthday_digits), '%P')
        self.birthday_month_entry = ttk.Entry(bday_frame, validate="key",
                                              validatecommand=vcmd_mm, width=3)
        self.birthday_month_entry.pack(side="left")
        self.birthday_month_entry.bind("<FocusOut>", self._birthday_on_focus_out)
        self.birthday_month_entry.bind("<KeyRelease>", self._birthday_month_key)
        ttk.Label(bday_frame, text="/").pack(side="left")
        self.birthday_day_entry = ttk.Entry(bday_frame, validate="key",
                                            validatecommand=vcmd_mm, width=3)
        self.birthday_day_entry.pack(side="left")
        self.birthday_day_entry.bind("<FocusOut>", self._birthday_on_focus_out)
        # Inline feedback label
        self.birthday_status_var = tk.StringVar(value="")
        self.birthday_status_label = ttk.Label(bday_frame, textvariable=self.birthday_status_var,
                                               font=('TkDefaultFont', 8))
        self.birthday_status_label.pack(side="left", padx=(6, 0))

        # Appearance field
        ttk.Label(frame, text="Appearance Description (Ingame):").grid(row=7, column=0, sticky="w", pady=(10,0))
        self.appearance_text = scrolledtext.ScrolledText(frame, height=3, width=60)
        self.appearance_text.grid(row=8, column=0, columnspan=2, sticky="ew", pady=5)

        # Personal Skill - FIXED POSITION
        ttk.Label(frame, text="Personal Skill:").grid(row=9, column=0, sticky="w", pady=(10,0))
        self.personal_skill_var = tk.StringVar(value="None (0 pts)")
        self.personal_skill_menu = ttk.Combobox(frame, textvariable=self.personal_skill_var,
                                                values=[f"{skill} ({cost} pts)" for skill, cost in PERSONAL_SKILLS.items()],
                                                state="readonly")
        self.personal_skill_menu.grid(row=9, column=1, sticky="ew", pady=(10,0))
        self.personal_skill_menu.bind("<<ComboboxSelected>>", lambda e: self.update_total_cost())
        # Hover tooltip showing the selected personal skill's description.
        # A trace keeps it current through selection, reset, and import.
        self._personal_skill_tip = Tooltip(self.personal_skill_menu, "")
        self.personal_skill_var.trace_add(
            "write", lambda *_: self._update_personal_skill_tooltip())
        self._update_personal_skill_tooltip()
        _info_ps = tk.Label(frame, text=" ? ", relief="groove",
                            background="#4a90d9", foreground="white",
                            font=("TkDefaultFont", 9, "bold"), cursor="hand2")
        _info_ps.grid(row=9, column=2, sticky="w", padx=(10, 0), pady=(10, 0))
        Tooltip(_info_ps,
                "Hover over the skill after selection for a skill description. "
                "Can't pick the same skill as personal skill and a normal skill.",
                delay_ms=400)

    def _personal_skill_description(self):
        """Description text for the currently selected personal skill."""
        name = self.personal_skill_var.get().split(" (")[0]
        if name not in PERSONAL_SKILLS:
            return "No personal skill selected — one is required to export."
        lookup = PERSONAL_SKILL_ALIASES.get(name, name)
        desc = skill_data.get(lookup, {}).get("desc", "")
        return desc or f"{name}: (no description available)"

    def _update_personal_skill_tooltip(self):
        if hasattr(self, "_personal_skill_tip"):
            self._personal_skill_tip.update_text(self._personal_skill_description())


    # ------------------------------------------------------------------------
    # Birthday Validation
    # ------------------------------------------------------------------------

    def _validate_birthday_digits(self, new_value):
        """Allow only up to 2 digits in each birthday field."""
        if new_value == "":
            return True
        if len(new_value) > 2:
            return False
        return new_value.isdigit()

    def _birthday_month_key(self, event=None):
        """Auto-advance focus to the day field once two digits are entered."""
        if len(self.birthday_month_entry.get()) == 2:
            self.birthday_day_entry.focus_set()
            self.birthday_day_entry.select_range(0, tk.END)

    def _birthday_on_focus_out(self, event=None):
        """Validate both fields when either loses focus."""
        mm = self.birthday_month_entry.get().strip()
        dd = self.birthday_day_entry.get().strip()

        # Both empty — birthday is optional
        if mm == "" and dd == "":
            self.birthday_status_var.set("")
            self._birthday_set_color("black")
            return True

        # One filled, one not
        if mm == "" or dd == "":
            self.birthday_status_var.set("✗ Fill both MM and DD")
            self.birthday_status_label.configure(foreground="red")
            self._birthday_set_color("red")
            return False

        try:
            month, day = int(mm), int(dd)
        except ValueError:
            self.birthday_status_var.set("✗ Invalid date")
            self.birthday_status_label.configure(foreground="red")
            self._birthday_set_color("red")
            return False

        # Days per month — use 29 for Feb to allow leap-year birthdays
        days_in_month = [0, 31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        if month < 1 or month > 12 or day < 1 or day > days_in_month[month]:
            self.birthday_status_var.set("✗ Invalid date")
            self.birthday_status_label.configure(foreground="red")
            self._birthday_set_color("red")
            return False

        self.birthday_status_var.set("✓")
        self.birthday_status_label.configure(foreground="green")
        self._birthday_set_color("black")
        return True

    def _birthday_set_color(self, color):
        """Apply foreground colour to both birthday fields."""
        self.birthday_month_entry.configure(foreground=color)
        self.birthday_day_entry.configure(foreground=color)

    def _birthday_get(self):
        """Return the birthday as a MM/DD string, or empty string if blank."""
        mm = self.birthday_month_entry.get().strip()
        dd = self.birthday_day_entry.get().strip()
        if mm == "" and dd == "":
            return ""
        return f"{mm.zfill(2)}/{dd.zfill(2)}"

    def _birthday_set(self, value):
        """Load a MM/DD string (or empty) into the two fields."""
        self.birthday_month_entry.delete(0, tk.END)
        self.birthday_day_entry.delete(0, tk.END)
        self._birthday_set_color("black")
        self.birthday_status_var.set("")
        if value and "/" in value:
            parts = value.split("/", 1)
            self.birthday_month_entry.insert(0, parts[0])
            self.birthday_day_entry.insert(0, parts[1])

    def _is_birthday_valid(self):
        """Return True if birthday is empty (optional) or a valid MM/DD date."""
        return self._birthday_on_focus_out()

    def setup_skills_frame(self, parent):
        frame = ttk.LabelFrame(parent, text="Skills", padding=10)
        frame.pack(fill="none", expand=False, padx=10, pady=5, anchor="w")

        # Selected skills shown as an aligned table (rebuilt by _render_skills_list)
        self.skills_list_frame = ttk.Frame(frame)
        self.skills_list_frame.pack(fill="x", anchor="w")
        self._render_skills_list()

        skills_row = ttk.Frame(frame)
        skills_row.pack(pady=5)
        ttk.Button(skills_row, text="Select Skills",
                   command=self.open_skill_selection).pack(side="left")
        _info = tk.Label(skills_row, text=" ? ", relief="groove",
                         background="#4a90d9", foreground="white",
                         font=("TkDefaultFont", 9, "bold"), cursor="hand2")
        _info.pack(side="left", padx=(6, 0))
        Tooltip(_info,
                "You have 5 skill slots, unlocked after chapter: 6, 9 or 10, 14, 18, 23. \n\n"
                "Author's note: That translates to:\n"
                "After Branch\n"
                "Before or after Takumi Harbor\n"
                "After increasing groans of discomfort\n"
                "After Ninja Cave\n"
                "After Takumi Wall\n\n"
                "Each skill has a gate (0-4) tied to chapter progress; a skill can "
                "only be placed in a slot whose gate is high enough. In the Skill "
                "Selection window, click a skill to choose an eligible slot for it.",
                delay_ms=400)

    def _render_skills_list(self):
        """Rebuild the skill-slot table in slot order (no auto-sort)."""
        for w in self.skills_list_frame.winfo_children():
            w.destroy()

        slots = getattr(self, "skill_slots", None) or [None] * MAX_SKILLS
        if not any(slots):
            ttk.Label(self.skills_list_frame, text="No skills selected",
                      foreground="gray").grid(row=0, column=0, sticky="w")
            return

        for col, header in enumerate(("Slot", "Chapter", "Gate", "Skill", "Cost")):
            ttk.Label(self.skills_list_frame, text=header,
                      font=("TkDefaultFont", 9, "bold")).grid(
                row=0, column=col, sticky="w", padx=(0, 14), pady=(0, 2))

        for i, skill in enumerate(slots):
            r = i + 1
            ttk.Label(self.skills_list_frame, text=str(i + 1)).grid(
                row=r, column=0, sticky="w", padx=(0, 14))
            ttk.Label(self.skills_list_frame, text=SKILL_SLOT_CHAPTERS[i],
                      foreground="gray").grid(row=r, column=1, sticky="w", padx=(0, 14))
            ttk.Label(self.skills_list_frame, text=str(SKILL_SLOT_GATES[i]),
                      foreground="gray").grid(row=r, column=2, sticky="w", padx=(0, 14))
            if skill and skill in skill_data:
                cost = scaled_skill_cost(skill_data[skill]["cost"])
                name_lbl = ttk.Label(self.skills_list_frame, text=skill)
                name_lbl.grid(row=r, column=3, sticky="w", padx=(0, 14))
                ttk.Label(self.skills_list_frame, text=str(int(cost))).grid(
                    row=r, column=4, sticky="w")
                info = skill_data.get(skill, {})
                tip_parts = []
                if info.get("desc"):
                    tip_parts.append(info["desc"])
                if info.get("groups"):
                    tip_parts.append("Groups: " + ", ".join(info["groups"]))
                if tip_parts:
                    Tooltip(name_lbl, "\n\n".join(tip_parts))
            else:
                ttk.Label(self.skills_list_frame, text="— empty —",
                          foreground="gray").grid(row=r, column=3, sticky="w", padx=(0, 14))

    def setup_growth_frame(self, parent):
        frame = ttk.LabelFrame(parent, text="Attribute Growth", padding=10)
        frame.pack(fill="x", padx=10, pady=10)
        _info_g = tk.Label(frame, text=" ? ", relief="groove",
                           background="#4a90d9", foreground="white",
                           font=("TkDefaultFont", 9, "bold"), cursor="hand2")
        _info_g.grid(row=0, column=len(self.attributes) + 2,
                     sticky="w", padx=(10, 0))
        Tooltip(_info_g,
                "Growth rates directly decide your starting stats. "
                "Strength and Magic share a Hybrid Discount: "
                "the cheaper of the two costs 50% less.",
                delay_ms=400)

        ttk.Label(frame, text="Attribute", font='bold').grid(row=0, column=0, padx=5, pady=2)
        for col, attr in enumerate(self.attributes, 1):
            ttk.Label(frame, text=attr, font='bold').grid(row=0, column=col, padx=5, pady=2)

        ttk.Label(frame, text="Growth Rate %").grid(row=1, column=0, padx=5, pady=2)
        for col, attr in enumerate(self.attributes, 1):
            self.growth_vars[attr] = tk.IntVar(value=0)
            _vcmd = self._int_vcmd()
            spin = ttk.Spinbox(frame, from_=0, to=100, increment=5, textvariable=self.growth_vars[attr],
                               width=5, command=lambda a=attr: self.on_spinbox_change(a),
                               validate="key", validatecommand=_vcmd)
            spin.grid(row=1, column=col, padx=5, pady=2)
            spin.bind("<FocusOut>", lambda e, a=attr: self.validate_growth(a))
            self.spinboxes[attr] = spin

        ttk.Label(frame, text="Current Cost").grid(row=2, column=0, padx=5, pady=2)
        for col, attr in enumerate(self.attributes, 1):
            self.cost_vars[attr] = tk.StringVar(value="0")
            ttk.Label(frame, textvariable=self.cost_vars[attr]).grid(row=2, column=col, padx=5, pady=2)

        ttk.Label(frame, text="Next +5% Cost").grid(row=3, column=0, padx=5, pady=2)
        for col, attr in enumerate(self.attributes, 1):
            self.next_step_cost_vars[attr] = tk.StringVar(value="0")
            label = ttk.Label(frame, textvariable=self.next_step_cost_vars[attr])
            label.grid(row=3, column=col, padx=5, pady=2)
            self.next_step_labels[attr] = label

        ttk.Label(frame, text="Base Stats").grid(row=4, column=0, padx=5, pady=2)
        for col, attr in enumerate(self.attributes, 1):
            self.base_vars[attr] = tk.StringVar(value="0")
            ttk.Label(frame, textvariable=self.base_vars[attr]).grid(row=4, column=col, padx=5, pady=2)

        self.discount_label = ttk.Label(frame, text="", foreground="green")
        self.discount_label.grid(row=5, columnspan=len(self.attributes) + 1, pady=5)

        # Total growth% checksum + Reset button to the right of the grid
        side_frame = ttk.Frame(frame)
        side_frame.grid(row=0, column=len(self.attributes) + 1, rowspan=6,
                        padx=(16, 4), sticky="n")
        ttk.Label(side_frame, text="Total Growth %",
                  font=("TkDefaultFont", 9, "bold")).pack(anchor="w")
        self.total_growth_var = tk.StringVar(value="0%")
        ttk.Label(side_frame, textvariable=self.total_growth_var,
                  font=("TkDefaultFont", 11, "bold"),
                  foreground="blue").pack(anchor="w", pady=(0, 10))
        ttk.Button(side_frame, text="Reset Attributes",
                   command=self.reset_attributes).pack(anchor="w")

        base_stats = self.calculate_base_stats()
        for attr, value in base_stats.items():
            self.base_vars[attr].set(str(value))

        # Show discount label from startup, not only after first spinbox change
        zero_costs = {attr: 0 for attr in self.attributes}
        self.update_discount_display(zero_costs)

    def setup_combat_frame(self, parent):
        frame = ttk.LabelFrame(parent, text="Combat Attributes", padding=10)
        frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(frame, text="Movement Type:").grid(row=0, column=0, sticky="w")
        self.movement_var = tk.StringVar(value="Infantry (Free)")
        movement_options = [f"Infantry (Free)", f"Armor (gain {MOVEMENT_COSTS['Armor']} pts)",
                            f"Cavalry (costs {MOVEMENT_COSTS['Cavalry']} pts)",
                            f"Flyer (costs {MOVEMENT_COSTS['Flyer']} pts)"]
        self.movement_dropdown = ttk.Combobox(frame, textvariable=self.movement_var, values=movement_options, state="readonly")
        self.movement_dropdown.grid(row=0, column=1, sticky="ew", padx=5)
        self.movement_dropdown.bind("<<ComboboxSelected>>", lambda e: self.update_total_cost())

        ttk.Label(frame, text="Primary Weapon Type:").grid(row=1, column=0, sticky="w")

        self.weapon_vars = []
        self.weapon_entries = []

        self.weapon_vars.append(tk.StringVar())
        self.weapon_entries.append(ttk.Entry(frame, textvariable=self.weapon_vars[-1]))
        self.weapon_entries[-1].grid(row=1, column=1, sticky="ew", padx=5)

        self.extra_weapon_vars = []
        for i in range(2):
            self.extra_weapon_vars.append(tk.BooleanVar())
            weapon_ordinal = "Second" if i == 0 else "Third"
            cb = ttk.Checkbutton(frame, text=f"{weapon_ordinal} Weapon Type (costs {EXTRA_WEAPON_COST} pts)",
                                 variable=self.extra_weapon_vars[-1], command=lambda idx=i: self.toggle_weapon(idx))
            cb.grid(row=2 + i, column=0, sticky="w")

            self.weapon_vars.append(tk.StringVar())
            self.weapon_entries.append(ttk.Entry(frame, textvariable=self.weapon_vars[-1], state="disabled"))
            self.weapon_entries[-1].grid(row=2 + i, column=1, sticky="ew", padx=5)

        # Two weapons per character: a full Promoted Weapon and a weaker Base
        # Weapon, built with the same creator but different budget / Hit cost.
        self.custom_weapons = {}      # kind -> weapon_data dict (or None)
        self.weapon_windows = {}      # kind -> open CustomWeaponCreator
        self.weapon_displays = {}     # kind -> Text widget
        self.reset_weapon_btns = {}
        wrow = 4
        for kind, cfg in WEAPON_KINDS.items():
            self.custom_weapons[kind] = None
            btn_frame = ttk.Frame(frame)
            btn_frame.grid(row=wrow, column=0, columnspan=2, pady=(10, 2))
            ttk.Button(btn_frame, text=f"Open {cfg['label']} Creator ({cfg['points']} pts)",
                       command=lambda k=kind: self.open_custom_weapon_creator(k)).pack(side="left", padx=(0, 8))
            rb = ttk.Button(btn_frame, text="Reset",
                            command=lambda k=kind: self.reset_custom_weapon(k))
            rb.pack(side="left")
            self.reset_weapon_btns[kind] = rb
            if kind == "promoted":
                _info_w = tk.Label(btn_frame, text=" ? ", relief="groove",
                                   background="#4a90d9", foreground="white",
                                   font=("TkDefaultFont", 9, "bold"), cursor="hand2")
                _info_w.pack(side="left", padx=(6, 0))
                Tooltip(_info_w,
                        "Two prf weapons: the Promoted Weapon (100 pts) and a weaker "
                        "Base Weapon (50 pts, where Hit costs half as much).",
                        delay_ms=400)
            disp = tk.Text(frame, height=7, width=60, state="disabled", wrap="word",
                           relief="groove", font=("TkDefaultFont", 9), foreground="blue",
                           background=ttk.Style().lookup("TFrame", "background"))
            disp.grid(row=wrow + 1, column=0, columnspan=2, sticky="ew", pady=(2, 6))
            self.weapon_displays[kind] = disp
            self._set_custom_weapon_display(kind, f"No {cfg['label']} created")
            wrow += 2

    def setup_stance_frame(self, parent):
        frame = ttk.LabelFrame(parent, text="Attack Stance Bonus", padding=10)
        frame.pack(fill="x", padx=10, pady=10)

        headers = ["", "Hit", "Crit", "Avoid", "Dodge", "Limit"]
        for col, header in enumerate(headers):
            ttk.Label(frame, text=header, font='bold').grid(row=0, column=col, padx=5, pady=2)

        support_levels = ["C Support", "B Support", "A Support", "S Support"]
        self.stance_vars = {}
        self.limit_labels = {}

        for row, level in enumerate(support_levels, 1):
            ttk.Label(frame, text=level).grid(row=row, column=0, sticky="w", padx=5)

            for col in range(1, 5):
                var = tk.BooleanVar()
                cb = ttk.Checkbutton(frame, variable=var,
                                     command=lambda r=row, c=col: self.validate_stance_checkboxes(r, c))
                cb.grid(row=row, column=col, padx=5, pady=2)

                if level not in self.stance_vars:
                    self.stance_vars[level] = []
                self.stance_vars[level].append(var)

            limit_max = 1 if level != "S Support" else 2
            limit_label = ttk.Label(frame, text=f"Selected: 0/{limit_max}", foreground="blue")
            limit_label.grid(row=row, column=5, padx=5)
            self.limit_labels[level] = limit_label

        footnote_frame = ttk.Frame(frame)
        footnote_frame.grid(row=len(support_levels) + 1, column=0, columnspan=len(headers), sticky="w", pady=(10, 0), padx=5)
        ttk.Label(footnote_frame, text="* Specifically, 5 Hit, 3 Crit, 5 Avoid, 5 Dodge.", foreground="gray").pack(side="left")

    def setup_pairup_frame(self, parent):
        frame = ttk.LabelFrame(parent, text="Pairup Bonus", padding=10)
        frame.pack(fill="x", padx=10, pady=10)

        headers = ["", "Move", "Str", "Mag", "Skl", "Spd", "Luk", "Def", "Res", "Limit"]
        for col, header in enumerate(headers):
            ttk.Label(frame, text=header, font='bold').grid(row=0, column=col, padx=5, pady=2)

        support_levels = ["No Support", "C Support", "B Support", "A Support", "S Support"]
        limits = [2, 3, 2, 3, 3]
        self.pairup_vars = {}
        self.pairup_limits = {}

        footnote_frame = ttk.Frame(frame)
        footnote_frame.grid(row=len(support_levels) + 1, column=0, columnspan=len(headers), sticky="w", pady=(10, 0), padx=5)
        ttk.Label(footnote_frame, text="* Each point in Move counts as 2 points toward the limit", foreground="gray").pack(side="left")

        for row, (level, limit) in enumerate(zip(support_levels, limits), 1):
            ttk.Label(frame, text=level).grid(row=row, column=0, sticky="w", padx=5)

            row_vars = []
            for col in range(1, 9):
                var = tk.IntVar(value=0)
                if col == 1:
                    _vcmd = self._uint_vcmd()
                    spin = ttk.Spinbox(frame, from_=0, to=1, textvariable=var, width=3,
                                       command=lambda r=row, l=limit: self.validate_pairup_spinboxes(r, l),
                                       validate="key", validatecommand=_vcmd)
                else:
                    _vcmd = self._uint_vcmd()
                    spin = ttk.Spinbox(frame, from_=0, to=3, textvariable=var, width=3,
                                       command=lambda r=row, l=limit: self.validate_pairup_spinboxes(r, l),
                                       validate="key", validatecommand=_vcmd)
                spin.grid(row=row, column=col, padx=5, pady=2)
                spin.bind("<FocusOut>", lambda e, r=row, l=limit: self.validate_pairup_spinboxes(r, l))
                row_vars.append(var)

            self.pairup_vars[level] = row_vars

            limit_label = ttk.Label(frame, text=f"Used: 0/{limit}", foreground="blue")
            limit_label.grid(row=row, column=9, padx=5)
            self.pairup_limits[level] = (limit, limit_label)

    def setup_secondary_frame(self, parent):
        frame = ttk.LabelFrame(parent, text="Secondary Stats", padding=10)
        frame.pack(fill="x", padx=10, pady=10)

        headers = ["Stat", "Value (0-100)", "Current Cost", "Next +5 Cost"]
        for col, header in enumerate(headers):
            ttk.Label(frame, text=header, font='bold').grid(row=0, column=col, padx=5, pady=2)

        for row, stat in enumerate(SECONDARY_STAT_BASE_COSTS.keys(), 1):
            ttk.Label(frame, text=stat).grid(row=row, column=0, sticky="w", padx=5)

            self.secondary_stats_vars[stat] = tk.IntVar(value=0)
            _vcmd = self._int_vcmd()
            spin = ttk.Spinbox(frame, from_=0, to=100, increment=5, textvariable=self.secondary_stats_vars[stat],
                               width=5, command=lambda s=stat: self.validate_secondary_stat(s),
                               validate="key", validatecommand=_vcmd)
            spin.grid(row=row, column=1, padx=5, pady=2)
            spin.bind("<FocusOut>", lambda e, s=stat: self.validate_secondary_stat(s))
            self.secondary_spinboxes[stat] = spin

            self.secondary_cost_vars[stat] = tk.StringVar(value="0")
            ttk.Label(frame, textvariable=self.secondary_cost_vars[stat]).grid(row=row, column=2, padx=5, pady=2)

            self.secondary_next_cost_vars[stat] = tk.StringVar(value="0")
            label = ttk.Label(frame, textvariable=self.secondary_next_cost_vars[stat])
            label.grid(row=row, column=3, padx=5, pady=2)
            self.secondary_next_labels[stat] = label

    # ------------------------------------------------------------------------
    # Event Handlers
    # ------------------------------------------------------------------------

    def on_spinbox_change(self, attribute):
        # Free editing: no over-budget block here (the budget is verified on
        # export / import instead). Going negative is allowed.
        try:
            new_value = int(self.spinboxes[attribute].get())
        except ValueError:
            new_value = self.growth_vars[attribute].get()
            self.spinboxes[attribute].delete(0, tk.END)
            self.spinboxes[attribute].insert(0, str(new_value))
            return
        self.growth_vars[attribute].set(new_value)
        self.validate_growth(attribute)

    def update_next_step_costs(self):
        raw_attr_cost_dict = {
            attr: math.ceil(self.attribute_costs[attr][self.growth_vars[attr].get() // 5])
            for attr in self.attributes
        }

        str_cost = raw_attr_cost_dict.get("Strength", 0)
        mag_cost = raw_attr_cost_dict.get("Magic", 0)

        if str_cost <= mag_cost:
            current_discounted_total = math.floor(str_cost * 0.5) + mag_cost
        else:
            current_discounted_total = str_cost + math.floor(mag_cost * 0.5)

        for attr, cost in raw_attr_cost_dict.items():
            if attr not in ["Strength", "Magic"]:
                current_discounted_total += cost

        for attr in self.attributes:
            current_growth = self.growth_vars[attr].get()

            if current_growth < 100:
                current_idx = current_growth // 5
                next_idx = current_idx + 1

                test_costs = raw_attr_cost_dict.copy()
                test_costs[attr] = math.ceil(self.attribute_costs[attr][next_idx])

                str_test = test_costs.get("Strength", 0)
                mag_test = test_costs.get("Magic", 0)

                if str_test <= mag_test:
                    new_discounted_total = math.floor(str_test * 0.5) + mag_test
                else:
                    new_discounted_total = str_test + math.floor(mag_test * 0.5)

                for a, cost in test_costs.items():
                    if a not in ["Strength", "Magic"]:
                        new_discounted_total += cost

                next_step_cost = new_discounted_total - current_discounted_total

                self.next_step_cost_vars[attr].set(str(math.ceil(next_step_cost)))

                if next_step_cost > self.remaining_points:
                    self.next_step_labels[attr].configure(foreground='red')
                else:
                    self.next_step_labels[attr].configure(foreground='black')
            else:
                self.next_step_cost_vars[attr].set("MAX")
                self.next_step_labels[attr].configure(foreground='red')

    def open_skill_selection(self):
        if hasattr(self, 'skill_window') and self.skill_window.window.winfo_exists():
            self.skill_window.window.lift()
            self.skill_window.window.focus_force()  # Bring to fron
        else:
            # Pass remaining_points + current skill cost so the window
            # starts with the full budget and deducts skills fresh
            current_skill_cost = sum(
                scaled_skill_cost(skill_data[s]["cost"])
                for s in self.selected_skills if s in skill_data
            )
            self.skill_window = SkillSelectionWindow(
                self.root, self.update_skills_and_points,
                self.remaining_points + current_skill_cost, self.skill_slots)

    def update_skills_and_points(self, slots):
        self.skill_slots = list(slots)
        self.selected_skills = [s for s in self.skill_slots if s]
        self.update_total_cost()
        self._render_skills_list()

    def _slots_from_imported(self, raw):
        """Build a length-MAX_SKILLS slot list from imported skill data.

        Accepts the new ordered slot list (may contain null) or an old flat list.
        Keeps a skill's original slot when it's gate-eligible, otherwise drops it
        into the earliest eligible free slot; unknown skills and overflow are
        skipped (verification surfaces any problems)."""
        slots = [None] * MAX_SKILLS
        if not isinstance(raw, list):
            return slots
        positional = len(raw) == MAX_SKILLS
        for idx, name in enumerate(raw):
            if not name or name not in skill_data or name in slots:
                continue
            gate = skill_gate(name)
            if (positional and idx < MAX_SKILLS
                    and SKILL_SLOT_GATES[idx] >= gate and slots[idx] is None):
                slots[idx] = name
                continue
            for i in eligible_slots(gate):
                if slots[i] is None:
                    slots[i] = name
                    break
        return slots

    def validate_growth(self, attribute):
        value = _safe_get(self.growth_vars[attribute], 0)
        rounded_value = max(0, min(100, (round(value / 5) * 5)))
        if value != rounded_value:
            self.growth_vars[attribute].set(rounded_value)
            self.spinboxes[attribute].delete(0, tk.END)
            self.spinboxes[attribute].insert(0, str(rounded_value))
        self.update_growth_cost(attribute)
        self.update_next_step_costs()

    def validate_pairup_spinboxes(self, row, limit):
        support_levels = ["No Support", "C Support", "B Support", "A Support", "S Support"]
        current_level = support_levels[row - 1]

        current_values = [_safe_get(var, 0) for var in self.pairup_vars[current_level]]
        weighted_values = [val * 2 if i == 0 else val for i, val in enumerate(current_values)]
        total = sum(weighted_values)

        if total > limit:
            for i in range(len(current_values) - 1, 0, -1):
                if current_values[i] > 0:
                    reduction = total - limit
                    new_value = max(0, current_values[i] - reduction)
                    self.pairup_vars[current_level][i].set(new_value)
                    break

        current_values = [_safe_get(var, 0) for var in self.pairup_vars[current_level]]
        weighted_total = sum(val * 2 if i == 0 else val for i, val in enumerate(current_values))

        if weighted_total > limit:
            color = "red"
        elif weighted_total == limit:
            color = "green"
        else:
            color = "blue"

        self.pairup_limits[current_level][1].config(text=f"Used: {weighted_total}/{limit}", foreground=color)

    def calculate_base_stats(self):
        base_stats = {}
        for attr, growth_var in self.growth_vars.items():
            growth_rate = growth_var.get()
            if attr == "HP":
                base = 1.18 * (10 * math.log10(1 + growth_rate / 1))
            else:
                base = 0.51 * (10 * math.log10(1 + growth_rate / 1))

            if growth_rate >= 100:
                base += 1.0

            base_stats[attr] = round(base)
        return base_stats

    def update_total_growth(self):
        """Update the total growth% checksum label."""
        if not hasattr(self, "total_growth_var"):
            return
        total = sum(_safe_get(v, 0) for v in self.growth_vars.values())
        self.total_growth_var.set(f"{total}%")

    def reset_attributes(self):
        """Reset all attribute growth spinboxes to 0."""
        for attr in self.attributes:
            self.growth_vars[attr].set(0)
            self.cost_vars[attr].set("0")
            self.next_step_cost_vars[attr].set("0")
        self.update_total_growth()
        self.update_total_cost()

    def update_growth_cost(self, attribute):
        growth_rate = self.growth_vars[attribute].get()
        index = growth_rate // 5
        self.cost_vars[attribute].set(str(math.ceil(self.attribute_costs[attribute][index])))

        base_stats = self.calculate_base_stats()
        for attr, value in base_stats.items():
            self.base_vars[attr].set(str(value))

        self.update_total_growth()
        self.update_total_cost()

    def toggle_weapon(self, index):
        # No over-budget block — the extra slot can be taken freely (verified on export).
        if self.extra_weapon_vars[index].get():
            self.weapon_entries[index + 1].config(state="normal")
        else:
            self.weapon_entries[index + 1].config(state="disabled")
            self.weapon_vars[index + 1].set("")

        self.update_total_cost()

    def update_total_cost(self):
        raw_attr_cost_dict = {
            attr: math.ceil(self.attribute_costs[attr][self.growth_vars[attr].get() // 5])
            for attr in self.attributes
        }

        selected_movement = self.movement_var.get().split(" (")[0]
        movement_cost = MOVEMENT_COSTS.get(selected_movement, 0)

        weapon_cost = sum(EXTRA_WEAPON_COST for i, var in enumerate(self.extra_weapon_vars) if var.get())

        attr_cost_dict = raw_attr_cost_dict.copy()
        if "Strength" in self.attributes and "Magic" in self.attributes:
            strength_cost = raw_attr_cost_dict["Strength"]
            magic_cost = raw_attr_cost_dict["Magic"]

            if strength_cost <= magic_cost:
                attr_cost_dict["Strength"] = math.floor(strength_cost * 0.5)
            else:
                attr_cost_dict["Magic"] = math.floor(magic_cost * 0.5)

        selected_personal = self.personal_skill_var.get().split(" (")[0]
        personal_skill_cost = PERSONAL_SKILLS.get(selected_personal, 0)

        secondary_cost = sum(int(self.secondary_cost_vars[stat].get()) for stat in SECONDARY_STAT_BASE_COSTS.keys())

        attr_cost = sum(attr_cost_dict.values())
        skill_cost = sum(scaled_skill_cost(skill_data[skill]["cost"]) for skill in self.selected_skills)

        self.remaining_points = initial_points - (attr_cost + skill_cost + movement_cost + weapon_cost + personal_skill_cost + secondary_cost)
        if self.remaining_points != int(self.remaining_points):
            print(f"WARNING: remaining_points is not a full integer: {self.remaining_points}")
        self.points_var.set(str(int(self.remaining_points)))
        if hasattr(self, "points_header_label"):
            color = "red" if self.remaining_points < 0 else "blue"
            self.points_header_label.configure(foreground=color)

        self.update_spinbox_limits(raw_attr_cost_dict)
        self.update_discount_display(raw_attr_cost_dict)
        self.update_next_step_costs()
        self.update_secondary_spinbox_limits()

        # Keep an open Skill Selection window's budget in sync with the main window.
        if hasattr(self, "skill_window") and self.skill_window.window.winfo_exists():
            self.skill_window.set_budget(self.remaining_points + skill_cost)

    def update_spinbox_limits(self, raw_attr_cost_dict):
        # No affordability cap — growth may exceed the budget (verified on export).
        for attr in self.attributes:
            self.spinboxes[attr].configure(to=100)

    def update_secondary_spinbox_limits(self):
        # No affordability cap — only the hard 0-100 range applies (verified on export).
        for stat in SECONDARY_STAT_BASE_COSTS.keys():
            current_value = self.secondary_stats_vars[stat].get()
            self.secondary_spinboxes[stat].configure(to=100)
            if current_value < 100:
                next_step_cost = (self._secondary_stat_cost(stat, current_value + 5)
                                  - self._secondary_stat_cost(stat, current_value))
                self.secondary_next_cost_vars[stat].set(str(math.ceil(next_step_cost)))
                self.secondary_spinboxes[stat].configure(foreground='black')
                self.secondary_next_labels[stat].configure(foreground='black')
            else:
                self.secondary_next_cost_vars[stat].set("MAX")
                self.secondary_spinboxes[stat].configure(foreground='red')
                self.secondary_next_labels[stat].configure(foreground='red')

    def update_discount_display(self, raw_attr_cost_dict):
        if "Strength" in self.attributes and "Magic" in self.attributes:
            strength_cost = raw_attr_cost_dict["Strength"]
            magic_cost = raw_attr_cost_dict["Magic"]

            if strength_cost <= magic_cost:
                discount = math.floor(strength_cost * 0.5)
                self.discount_label.config(
                    text=f"Hybrid Discount: -{discount} pts (50% off Strength)",
                    foreground="green")
            else:
                discount = math.floor(magic_cost * 0.5)
                self.discount_label.config(
                    text=f"Hybrid Discount: -{discount} pts (50% off Magic)",
                    foreground="green")

    def validate_stance_checkboxes(self, row, col):
        support_levels = ["C Support", "B Support", "A Support", "S Support"]
        current_level = support_levels[row - 1]
        level_vars = self.stance_vars[current_level]

        if current_level in ["C Support", "B Support", "A Support"]:
            current_var = level_vars[col - 1]
            if current_var.get():
                for i, var in enumerate(level_vars):
                    if i != col - 1:
                        var.set(False)
        elif current_level == "S Support":
            checked_count = sum(var.get() for var in level_vars)
            if checked_count > 2:
                for i, var in enumerate(level_vars):
                    if var.get() and i == col - 1:
                        var.set(False)
                        break

        self.update_all_stance_labels()

    def update_all_stance_labels(self):
        for level in self.stance_vars.keys():
            checked_count = sum(var.get() for var in self.stance_vars[level])
            max_allowed = 2 if level == "S Support" else 1

            if checked_count == 0:
                color = "blue"
            elif checked_count == max_allowed:
                color = "green"
            else:
                color = "blue"

            self.limit_labels[level].config(text=f"Selected: {checked_count}/{max_allowed}", foreground=color)

    def _secondary_stat_cost(self, stat, value):
        """Cumulative point cost for a secondary stat at the given value."""
        steps = value // 5
        base = SECONDARY_STAT_BASE_COSTS[stat]
        return math.ceil(base * (100 + steps) / 100 * steps * 5)

    def validate_secondary_stat(self, stat):
        value = _safe_get(self.secondary_stats_vars[stat], 0)
        rounded_value = max(0, min(100, (round(value / 5) * 5)))
        if value != rounded_value:
            self.secondary_stats_vars[stat].set(rounded_value)

        value = _safe_get(self.secondary_stats_vars[stat], 0)
        self.secondary_cost_vars[stat].set(str(self._secondary_stat_cost(stat, value)))
        self.update_total_cost()

    def reset_custom_weapon(self, kind="promoted"):
        """Clear a weapon slot, with confirmation if one exists."""
        cfg = WEAPON_KINDS[kind]
        if not self.custom_weapons.get(kind):
            return
        if not messagebox.askyesno(
            "Reset Weapon",
            f"This will remove the current {cfg['label']}. Are you sure?"
        ):
            return
        self.custom_weapons[kind] = None
        self._set_custom_weapon_display(kind, f"No {cfg['label']} created")
        self.update_total_cost()

    def open_custom_weapon_creator(self, kind="promoted"):
        win = self.weapon_windows.get(kind)
        if win is not None and win.window.winfo_exists():
            win.window.lift()
            return
        cfg = WEAPON_KINDS[kind]
        self.weapon_windows[kind] = CustomWeaponCreator(
            self.root, lambda data, k=kind: self.update_custom_weapon(data, k),
            self.custom_weapons.get(kind),
            total_points=cfg["points"], stat_costs=cfg["stat_costs"],
            kind_label=cfg["label"])

    def _set_custom_weapon_display(self, kind, text):
        disp = self.weapon_displays[kind]
        disp.config(state="normal")
        disp.delete("1.0", tk.END)
        disp.insert("1.0", text)
        disp.config(state="disabled")

    def update_custom_weapon(self, weapon_data, kind="promoted", show_message=True):
        cfg = WEAPON_KINDS[kind]
        self.custom_weapons[kind] = weapon_data
        w = weapon_data
        weapon_name = w.get("name", "")
        weapon_type = w.get("type", "")

        lines = [
            f"[{cfg['label']}]  Name: {weapon_name}  |  Type: {weapon_type}  |  Range: {w.get('range', '1')}",
            f"MT:{w.get('might',0)}  HIT:{w.get('hit',0)}  CRT:{w.get('crit',0)}  "
            f"AVO:{w.get('avoid',0)}  DGE:{w.get('dodge',0)}  "
            f"MOV:{w.get('mov',0)}  SPD-O:{w.get('effective_speed_offensive',0)}  "
            f"SPD-D:{w.get('effective_speed_defensive',0)}",
        ]
        if w.get("fixed_effects"):
            lines.append(f"Effects: {', '.join(w['fixed_effects'])}")
        if w.get("value_effects") and w.get("effect_value", 0) != 0:
            lines.append(f"Value Effects: {', '.join(w['value_effects'])}  Val:{w['effect_value']}")
        if w.get("staff_effects"):
            lines.append(f"Staff Effects: {', '.join(w['staff_effects'])}")
        if w.get("buffs"):
            lines.append(f"Buffs: {', '.join(w['buffs'])}")
        if w.get("description"):
            lines.append(f"Desc: {w['description']}")
        self._set_custom_weapon_display(kind, "\n".join(lines))

        if not show_message:
            return

        # Build detailed message
        message = (f"Custom weapon '{weapon_name}' created successfully!\n"
                   f"Type: {weapon_type}\n"
                   f"Stats: MT {weapon_data['might']} | HIT {weapon_data['hit']} | CRT {weapon_data['crit']}\n"
                   f"      AVO {weapon_data['avoid']} | DGE {weapon_data['dodge']} | MOV {weapon_data['mov']}\n"
                   f"      SPD-O {weapon_data['effective_speed_offensive']} | SPD-D {weapon_data['effective_speed_defensive']}\n"
                   f"Range: {weapon_data.get('range', '1')}")
        
        if weapon_data.get('fixed_effects'):
            message += f"\nFixed Effects: {', '.join(weapon_data['fixed_effects'])}"
        
        if weapon_data.get('value_effects') and weapon_data.get('effect_value', 0) != 0:
            message += f"\nValue Effects: {', '.join(weapon_data['value_effects'])} (Value: {weapon_data['effect_value']}, Cost: {round(weapon_data.get('value_effects_cost', 0))} pts)"
        
        if weapon_type in ["Staff", "Rod"]:
            if weapon_data.get('staff_effects'):
                message += f"\nStaff Effects: {', '.join(weapon_data['staff_effects'])}"
            if weapon_data.get('unlimited_uses'):
                message += "\nUnlimited Uses: Yes (2.0x cost multiplier)"
            if weapon_data.get('buffs'):
                message += f"\nBuffs: {', '.join(weapon_data['buffs'])}"
        
        if weapon_data.get('debuffs'):
            debuff_str = ", ".join([f"{k.upper()}:{v}" for k, v in weapon_data['debuffs'].items()])
            message += f"\nDebuffs: {debuff_str}"
        
        if weapon_data.get('description'):
            message += f"\nDescription: {weapon_data['description'][:100]}..."
        
        message += f"\n\nPoint Cost: {round(weapon_data.get('total_cost', 0))}/{cfg['points']}"

        messagebox.showinfo(f"{cfg['label']} Created", message)
    
    def _validate_character_export(self):
        """Run all pre-export checks for the character. Returns (ok, errors) tuple."""
        errors = []
        if not self.name_entry.get().strip():
            errors.append("\u2022 Character name is required.")
        if self.remaining_points < 0:
            errors.append(
                f"\u2022 Over budget by {abs(round(self.remaining_points))} points (limit is {initial_points})."
            )
        if all(_safe_get(v, 0) == 0 for v in self.growth_vars.values()):
            errors.append("\u2022 All growth rates are 0 - please set at least one.")
        support_levels = ["No Support", "C Support", "B Support", "A Support", "S Support"]
        limits = [2, 3, 2, 3, 3]
        for level, limit in zip(support_levels, limits):
            if level not in self.pairup_vars:
                continue
            values = [_safe_get(v, 0) for v in self.pairup_vars[level]]
            weighted = sum(val * 2 if i == 0 else val for i, val in enumerate(values))
            if weighted > limit:
                errors.append(
                    f"\u2022 Pairup '{level}': weighted total {weighted} exceeds limit of {limit}."
                )
        # Attack Stance: each support level must not exceed its max
        stance_limits = {"No Support": 1, "C Support": 1, "B Support": 1,
                         "A Support": 1, "S Support": 2}
        for level, max_sel in stance_limits.items():
            if level not in self.stance_vars:
                continue
            checked = sum(var.get() for var in self.stance_vars[level])
            if checked > max_sel:
                errors.append(
                    f"\u2022 Attack Stance '{level}': {checked} bonuses selected, max is {max_sel}."
                )
        # Skills: cannot exceed MAX_SKILLS
        if len(self.selected_skills) > MAX_SKILLS:
            errors.append(
                f"\u2022 Too many skills selected ({len(self.selected_skills)}), maximum is {MAX_SKILLS}."
            )
        # Skill slots: each slotted skill must fit its slot's gate.
        for idx, name in enumerate(self.skill_slots):
            if name and name in skill_data and skill_gate(name) > SKILL_SLOT_GATES[idx]:
                errors.append(
                    f"\u2022 '{name}' (gate {skill_gate(name)}) is in Slot {idx + 1}, which "
                    f"only allows gate {SKILL_SLOT_GATES[idx]}."
                )
        # Personal skill: one must be chosen (None is not allowed) and it must
        # not also be selected as a normal skill.
        personal = self.personal_skill_var.get().split(" (")[0]
        if personal not in PERSONAL_SKILLS:
            errors.append("\u2022 A personal skill must be selected (None is not allowed).")
        else:
            eff = PERSONAL_SKILL_ALIASES.get(personal, personal)
            if eff in self.selected_skills or personal in self.selected_skills:
                errors.append(
                    f"\u2022 '{personal}' is chosen as both the personal skill and a normal "
                    f"skill \u2014 pick a different one.")
        return len(errors) == 0, errors

    def export_character(self):
        # Validate birthday before exporting
        if not self._is_birthday_valid():
            messagebox.showerror("Export Failed", "Birthday is not valid.\nPlease use MM/DD format (e.g. 03/14).")
            self.birthday_month_entry.focus_set()
            return
        # Run all pre-export validations first
        ok, errors = self._validate_character_export()
        if not ok:
            messagebox.showerror(
                "Export Failed — Validation Errors",
                "Please fix the following before exporting:\n\n" + "\n".join(errors)
            )
            return

        # Warn if no custom weapon has been created (after validation passes)
        if not any(self.custom_weapons.values()):
            if not messagebox.askyesno(
                "No Custom Weapon",
                "This character has no custom weapon.\n\nExport anyway?"
            ):
                return
        movement_type = self.movement_var.get().split(" (")[0]

        secondary_stats_data = {}
        for stat in SECONDARY_STAT_BASE_COSTS.keys():
            secondary_stats_data[stat] = {
                "value": self.secondary_stats_vars[stat].get(),
                "cost": float(self.secondary_cost_vars[stat].get())
            }

        character_data = {
            "version": VERSION,
            "name": self.name_entry.get(),
            "class": self.class_entry.get(),
            "character_description": self.char_desc_entry.get("1.0", tk.END).strip(),
            "class_description": self.class_desc_entry.get("1.0", tk.END).strip(),
            "birthday": self._birthday_get(),
            "appearance": self.appearance_text.get("1.0", tk.END).strip(),
            "movement_type": movement_type,
            "weapons": [w.get() for w in self.weapon_vars if w.get()],
            "personal_skill": self.personal_skill_var.get().split(" (")[0],
            "skills": list(self.skill_slots),   # ordered 6-slot list (None = empty)
            "growths": {attr: var.get() for attr, var in self.growth_vars.items()},
            "base_stats": {attr: int(self.base_vars[attr].get()) for attr in self.attributes},
            "secondary_stats": secondary_stats_data
        }

        stance_bonuses = {}
        for level, vars in self.stance_vars.items():
            bonus_types = ["Hit", "Crit", "Avoid", "Dodge"]
            active_bonuses = [bonus_types[i] for i, var in enumerate(vars) if var.get()]
            stance_bonuses[level] = active_bonuses
        character_data["stance_bonuses"] = stance_bonuses

        pairup_bonuses = {}
        for level, vars in self.pairup_vars.items():
            stat_names = ["Move", "Str", "Mag", "Skl", "Spd", "Luk", "Def", "Res"]
            bonuses = {stat_names[i]: var.get() for i, var in enumerate(vars)}
            pairup_bonuses[level] = bonuses
        character_data["pairup_bonuses"] = pairup_bonuses

        # Add custom weapons (each under its own field) if present
        for _k, _cfg in WEAPON_KINDS.items():
            if self.custom_weapons.get(_k):
                character_data[_cfg["field"]] = self.custom_weapons[_k]

        character_data["points_summary"] = {
            "total_points": initial_points,
            "remaining_points": int(self.points_var.get()),
            "used_points": initial_points - float(self.points_var.get()),
            "attribute_points": sum(float(self.cost_vars[attr].get()) for attr in self.attributes),
            "secondary_points": sum(float(self.secondary_cost_vars[stat].get()) for stat in SECONDARY_STAT_BASE_COSTS.keys()),
            "skill_points": sum(scaled_skill_cost(skill_data[skill]["cost"]) for skill in self.selected_skills),
            "movement_cost": MOVEMENT_COSTS.get(movement_type, 0),
            "weapon_cost": sum(EXTRA_WEAPON_COST for i, var in enumerate(self.extra_weapon_vars) if var.get()),
            "personal_skill_cost": PERSONAL_SKILLS.get(character_data["personal_skill"], 0)
        }

        safe_name = (self.name_entry.get() or "unnamed").replace(" ", "_").replace("/", "_").replace("\\", "_")
        filename = f"character_{safe_name}.json"

        if os.path.exists(filename):
            if not messagebox.askyesno(
                "File Already Exists",
                f"\"{filename}\" already exists.\n\nOverwrite it?"
            ):
                return

        try:
            with open(filename, "w") as f:
                json.dump(character_data, f, indent=2)

            summary = (f"Character exported to: {filename}\n\n"
                       f"Points Summary:\n"
                       f"  Total used: {round(character_data['points_summary']['used_points'])}/{initial_points}\n"
                       f"  Remaining: {round(character_data['points_summary']['remaining_points'])}\n\n"
                       f"Breakdown:\n"
                       f"  Attributes: {round(character_data['points_summary']['attribute_points'])}\n"
                       f"  Secondary Stats: {round(character_data['points_summary']['secondary_points'])}\n"
                       f"  Skills: {int(character_data['points_summary']['skill_points'])}\n"
                       f"  Movement: {round(character_data['points_summary']['movement_cost'])}\n"
                       f"  Weapons: {round(character_data['points_summary']['weapon_cost'])}\n"
                       f"  Personal Skill: {round(character_data['points_summary']['personal_skill_cost'])}")

            messagebox.showinfo("Export Successful", summary)

        except Exception as e:
            messagebox.showerror("Export Failed", f"Failed to save character:\n{str(e)}")
    
    def _verify_imported_character(self, char_data):
        """Compare a freshly loaded character file against the tool's recomputed truth.

        update_total_cost() has already run, so self.remaining_points and
        calculate_base_stats() reflect the real values. Raw file fields are also
        inspected directly, so forgeries that loading would clamp are still caught.
        Returns a list of discrepancy strings (empty = clean)."""
        issues = []

        # --- Budget: recomputed remaining vs the file's claim ---
        true_remaining = self.remaining_points
        ps = char_data.get("points_summary", {})
        claimed_remaining = ps.get("remaining_points")
        if isinstance(claimed_remaining, (int, float)) and abs(round(claimed_remaining) - round(true_remaining)) >= 1:
            issues.append(
                f"Claimed remaining points {round(claimed_remaining)} does not match the "
                f"recomputed {round(true_remaining)}")
        if true_remaining < 0:
            issues.append(
                f"Over budget: the build costs {round(initial_points - true_remaining)} points, "
                f"limit is {initial_points}")

        # --- Forged base stats (base stats are derived from growths) ---
        growths = char_data.get("growths", {})
        true_bs = self.calculate_base_stats()
        claimed_bs = char_data.get("base_stats", {})
        for attr in self.attributes:
            cv = claimed_bs.get(attr)
            tv = true_bs.get(attr)
            if cv is not None and tv is not None and int(cv) != int(tv):
                issues.append(
                    f"Base {attr} = {cv} but growth {growths.get(attr, 0)}% yields {tv}")

        # --- Growth legality (raw, before loading clamps it) ---
        for attr, g in growths.items():
            if not isinstance(g, int) or g < 0 or g > 100 or g % 5 != 0:
                issues.append(f"Growth {attr} = {g} is not a valid 0-100 value in steps of 5")

        # --- Secondary stats: raw value legality + stored-cost consistency ---
        for stat, data in (char_data.get("secondary_stats") or {}).items():
            if stat not in SECONDARY_STAT_BASE_COSTS or not isinstance(data, dict):
                continue
            val = data.get("value")
            if not isinstance(val, int) or val < 0 or val > 100 or val % 5 != 0:
                issues.append(f"Secondary {stat} = {val} is not a valid 0-100 value in steps of 5")
                continue
            claimed_c = data.get("cost")
            true_c = self._secondary_stat_cost(stat, val)
            if isinstance(claimed_c, (int, float)) and abs(round(claimed_c) - true_c) >= 1:
                issues.append(
                    f"Secondary {stat} cost {round(claimed_c)} does not match the recomputed {true_c}")

        # --- Skills: count, plus gate legality of slotted skills ---
        raw_skills = char_data.get("skills", []) or []
        valid_skills = [s for s in raw_skills if s in skill_data]
        if len(valid_skills) > MAX_SKILLS:
            issues.append(f"{len(valid_skills)} skills selected; the limit is {MAX_SKILLS}")
        # Gate legality applies only to the positional 6-slot format
        if isinstance(raw_skills, list) and len(raw_skills) == MAX_SKILLS:
            for idx, name in enumerate(raw_skills):
                if name and name in skill_data and skill_gate(name) > SKILL_SLOT_GATES[idx]:
                    issues.append(
                        f"'{name}' (gate {skill_gate(name)}) is in Slot {idx + 1}, which "
                        f"only allows gate {SKILL_SLOT_GATES[idx]}")

        # --- Personal skill: must be chosen and not overlap a normal skill ---
        personal = char_data.get("personal_skill", "")
        if personal not in PERSONAL_SKILLS:
            issues.append(f"No valid personal skill selected (personal_skill = {personal!r})")
        else:
            eff = PERSONAL_SKILL_ALIASES.get(personal, personal)
            file_skills = [s for s in (char_data.get("skills") or []) if s]
            if eff in file_skills or personal in file_skills:
                issues.append(f"Personal skill '{personal}' is also selected as a normal skill")

        # --- Pairup limits (raw, before loading reduces over-limit rows) ---
        pairup_limits = {"No Support": 2, "C Support": 3, "B Support": 2,
                         "A Support": 3, "S Support": 3}
        for level, bonuses in char_data.get("pairup_bonuses", {}).items():
            if level not in pairup_limits or not isinstance(bonuses, dict):
                continue
            weighted = 0
            for stat, v in bonuses.items():
                try:
                    v = int(v)
                except (TypeError, ValueError):
                    continue
                weighted += v * 2 if stat == "Move" else v
            if weighted > pairup_limits[level]:
                issues.append(
                    f"Pairup '{level}': weighted total {weighted} exceeds the limit of "
                    f"{pairup_limits[level]}")

        # --- Attack-stance limits (raw) ---
        stance_limits = {"C Support": 1, "B Support": 1, "A Support": 1, "S Support": 2}
        for level, bonuses in char_data.get("stance_bonuses", {}).items():
            if level in stance_limits and isinstance(bonuses, list) and len(bonuses) > stance_limits[level]:
                issues.append(
                    f"Attack Stance '{level}': {len(bonuses)} bonuses selected, max is "
                    f"{stance_limits[level]}")

        # --- Embedded custom weapons (raw legality, each vs its own budget) ---
        for _cfg in WEAPON_KINDS.values():
            cw = char_data.get(_cfg["field"])
            if isinstance(cw, dict):
                for wi in _verify_weapon_raw(cw, _cfg["points"]):
                    issues.append(f"{_cfg['label']}: " + wi)

        return issues

    def import_character(self):
        """Import a character from a JSON file and load all data."""
        
        filename = filedialog.askopenfilename(
            title="Select Character File",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if not filename:
            return
        
        try:
            with open(filename, "r", encoding="utf-8") as f:
                char_data = json.load(f)
            
            # Validate required fields
            required_fields = ["name", "class", "growths", "base_stats", "skills", "personal_skill"]
            for field in required_fields:
                if field not in char_data:
                    raise ValueError(f"Missing required field: {field}")
            
            # Load basic info
            self.name_entry.delete(0, tk.END)
            self.name_entry.insert(0, char_data.get("name", ""))
            
            self.class_entry.delete(0, tk.END)
            self.class_entry.insert(0, char_data.get("class", ""))
            
            self.char_desc_entry.delete("1.0", tk.END)
            self.char_desc_entry.insert("1.0", char_data.get("character_description", ""))
            
            self.class_desc_entry.delete("1.0", tk.END)
            self.class_desc_entry.insert("1.0", char_data.get("class_description", ""))
            
            self._birthday_set(char_data.get("birthday", ""))
            
            self.appearance_text.delete("1.0", tk.END)
            self.appearance_text.insert("1.0", char_data.get("appearance", ""))
            
            # Load personal skill
            personal_skill = char_data.get("personal_skill", "None")
            # Find the matching display string in the combobox
            found = False
            for value in self.personal_skill_menu['values']:
                if value.startswith(personal_skill):
                    self.personal_skill_var.set(value)
                    found = True
                    break
            if not found:
                # Default to None if not found
                self.personal_skill_var.set("None (0 pts)")
            
            # Load movement type
            movement = char_data.get("movement_type", "Infantry")
            for option in self.movement_dropdown['values']:
                if option.startswith(movement):
                    self.movement_var.set(option)
                    break
            else:
                self.movement_var.set("Infantry (Free)")
            
            # Load weapons
            weapons = char_data.get("weapons", [])
            for i, weapon in enumerate(weapons):
                if i < len(self.weapon_vars):
                    self.weapon_vars[i].set(weapon)
            
            # Load extra weapon slots
            extra_weapon_count = len(weapons) - 1 if weapons else 0
            for i in range(2):
                if i < extra_weapon_count:
                    if not self.extra_weapon_vars[i].get():
                        self.extra_weapon_vars[i].set(True)
                        self.toggle_weapon(i)
                    self.weapon_vars[i + 1].set(weapons[i + 1] if i + 1 < len(weapons) else "")
                else:
                    if self.extra_weapon_vars[i].get():
                        self.extra_weapon_vars[i].set(False)
                        self.toggle_weapon(i)
            
            # Load growths
            growths = char_data.get("growths", {})
            for attr, value in growths.items():
                if attr in self.growth_vars:
                    self.growth_vars[attr].set(value)
                    self.validate_growth(attr)
            
            # Load secondary stats
            secondary_stats = char_data.get("secondary_stats", {})
            for stat, data in secondary_stats.items():
                if stat in self.secondary_stats_vars:
                    self.secondary_stats_vars[stat].set(data.get("value", 0))
                    self.validate_secondary_stat(stat)
            
            # Load skills into slots. Accepts the new ordered slot list (may
            # contain null) and old flat lists of any length, re-slotting into
            # gate-eligible positions. Surface anything that had to be dropped.
            raw_skills = char_data.get("skills", []) or []
            named = list(dict.fromkeys(s for s in raw_skills if s))   # unique, ordered
            missing_skills = [s for s in named if s not in skill_data]
            slots = self._slots_from_imported(raw_skills)
            placed = [s for s in slots if s]
            dropped = [s for s in named if s in skill_data and s not in placed]
            notes = []
            if missing_skills:
                notes.append("No longer exist in this version (removed):\n"
                             + "\n".join(f"  • {s}" for s in missing_skills))
            if dropped:
                notes.append(f"Could not be slotted into the {MAX_SKILLS} slots "
                             "(no free slot at their gate — dropped):\n"
                             + "\n".join(f"  • {s}" for s in dropped))
            if notes:
                messagebox.showwarning("Skills adjusted on import", "\n\n".join(notes))
            self.update_skills_and_points(slots)
            
            # Load stance bonuses
            stance_bonuses = char_data.get("stance_bonuses", {})
            for level, bonuses in stance_bonuses.items():
                if level in self.stance_vars:
                    bonus_map = {"Hit": 0, "Crit": 1, "Avoid": 2, "Dodge": 3}
                    for bonus in bonuses:
                        if bonus in bonus_map:
                            col = bonus_map[bonus]
                            self.stance_vars[level][col].set(True)
                    self.update_all_stance_labels()
            
            # Load pairup bonuses
            pairup_bonuses = char_data.get("pairup_bonuses", {})
            for level, bonuses in pairup_bonuses.items():
                if level in self.pairup_vars:
                    stat_names = ["Move", "Str", "Mag", "Skl", "Spd", "Luk", "Def", "Res"]
                    for i, stat in enumerate(stat_names):
                        value = bonuses.get(stat, 0)
                        if value > 0:
                            self.pairup_vars[level][i].set(value)
                    # Update limit display
                    support_levels = ["No Support", "C Support", "B Support", "A Support", "S Support"]
                    limits = [2, 3, 2, 3, 3]
                    for row, (lvl, limit) in enumerate(zip(support_levels, limits), 1):
                        if lvl == level:
                            self.validate_pairup_spinboxes(row, limit)
                            break
            
            # Load both custom weapons (each from its own field), and reload any
            # open creator window for that kind.
            for kind, cfg in WEAPON_KINDS.items():
                new_weapon = char_data.get(cfg["field"])
                if new_weapon:
                    self.update_custom_weapon(new_weapon, kind, show_message=False)
                else:
                    self.custom_weapons[kind] = None
                    self._set_custom_weapon_display(kind, f"No {cfg['label']} created")
                win = self.weapon_windows.get(kind)
                if win is not None and win.window.winfo_exists():
                    if new_weapon:
                        win._load_weapon_data(new_weapon)
                    else:
                        win.reset_weapon()

            # Debug: check imported summary for decimal values
            if "points_summary" in char_data:
                _dec = [f"{k}={v}" for k, v in char_data["points_summary"].items()
                        if isinstance(v, float) and v != int(v)]
                if _dec:
                    print(f"WARNING: Imported summary contains decimals: {_dec}")

            # Force a full UI update
            self.update_total_cost()
            
            issues = self._verify_imported_character(char_data)
            _show_import_verification(self.root, "character",
                                      char_data.get("name", ""),
                                      char_data.get("version"), issues)
            
        except Exception as e:
            messagebox.showerror("Import Failed", f"Failed to load character:\n{str(e)}")
            import traceback
            traceback.print_exc()
            
    def reset_character(self):
        # First click: arm the confirmation and wait for second click
        if not self.reset_confirmation_needed:
            self.reset_confirmation_needed = True
            self.reset_button.config(text="Click Again to Confirm Reset")
            self.root.after(3000, self.reset_confirmation_cancel)
            return

        # Second click: perform the reset
        self.reset_confirmation_needed = False
        self.reset_button.config(text="Reset Character")

        self.name_entry.delete(0, tk.END)
        self.class_entry.delete(0, tk.END)
        self.char_desc_entry.delete(1.0, tk.END)
        self.class_desc_entry.delete(1.0, tk.END)
        self._birthday_set("")
        self.appearance_text.delete(1.0, tk.END)

        # Reset personal skill - FIXED
        self.personal_skill_var.set("None (0 pts)")

        self.selected_skills = []
        self.skill_slots = [None] * MAX_SKILLS
        self._render_skills_list()

        for attr in self.attributes:
            self.growth_vars[attr].set(0)
            self.spinboxes[attr].delete(0, tk.END)
            self.spinboxes[attr].insert(0, "0")
            self.cost_vars[attr].set("0")
            self.next_step_cost_vars[attr].set("0")
            self.next_step_labels[attr].configure(foreground='black')

        base_stats = self.calculate_base_stats()
        for attr, value in base_stats.items():
            self.base_vars[attr].set(str(value))

        self.movement_var.set("Infantry (Free)")

        self.weapon_vars[0].set("")
        for i in range(2):
            self.extra_weapon_vars[i].set(False)
            self.weapon_vars[i + 1].set("")
            self.weapon_entries[i + 1].config(state="disabled")

        for level in self.stance_vars.keys():
            for var in self.stance_vars[level]:
                var.set(False)
        self.update_all_stance_labels()

        for level in self.pairup_vars.keys():
            for var in self.pairup_vars[level]:
                var.set(0)

        for stat in SECONDARY_STAT_BASE_COSTS.keys():
            self.secondary_stats_vars[stat].set(0)
            self.secondary_cost_vars[stat].set("0")
            self.secondary_next_cost_vars[stat].set("0")
            self.secondary_spinboxes[stat].configure(foreground='black')
            self.secondary_next_labels[stat].configure(foreground='black')

        self.remaining_points = initial_points
        self.points_var.set(str(int(initial_points)))

        support_levels = ["No Support", "C Support", "B Support", "A Support", "S Support"]
        limits = [2, 3, 2, 3, 3]
        for row, (level, limit) in enumerate(zip(support_levels, limits), 1):
            self.validate_pairup_spinboxes(row, limit)

        self.update_total_cost()

    def reset_confirmation_cancel(self):
        # Timer fired before the second click — disarm the confirmation
        if self.reset_confirmation_needed:
            self.reset_confirmation_needed = False
            self.reset_button.config(text="Reset Character")

# ============================================================================
# RUN APPLICATION
# ============================================================================

if __name__ == "__main__":
    root = tk.Tk()
    app = CharacterCreator(root)
    root.mainloop()