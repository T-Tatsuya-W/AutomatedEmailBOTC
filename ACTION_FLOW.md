# Action Application Flow

## Overview
This document explains how actions (kills, poisons, etc.) are recorded during one phase and applied before the next phase, with announcements made to players.

## The Flow

### Phase N: Actions are Recorded

```
NIGHT1 Phase
├── Emails sent to all players
├── Players respond
├── Demon responds with kill target: "3"
└── Action recorded in gamestate:
    {
      "type": "kill",
      "details": {"by": 5, "target": 3},
      "applied": false  ← Not yet applied!
    }
```

### Between Phases: Actions are Applied

```
DAY2 Phase Starting
├── _apply_previous_phase_actions("DAY2") called
│   ├── Finds previous phase: "NIGHT1"
│   ├── Gets actions from NIGHT1
│   ├── Finds unapplied actions
│   └── Calls apply_actions("NIGHT1", players)
│
├── apply_actions() processes each action:
│   ├── For "kill" action:
│   │   ├── Finds target player (number 3)
│   │   ├── Sets target.alive = False
│   │   ├── Marks action as applied: true
│   │   └── Returns: "Alice was killed"
│   │
│   └── Updates game state with modified players
│
└── Announcements set for DAY2: "Alice was killed"
```

### Phase N+1: Announcements Delivered

```
DAY2 Phase Running
├── Phase emails built with announcements
├── Email body includes:
│   ├── "Alice was killed"  ← From NIGHT1 actions
│   ├── Current phase: DAY2
│   ├── Player list (Alice now dead)
│   └── Action prompts
│
└── Emails sent to all players
```

## Code Trace

### 1. Recording Actions (Night Phase)

**File**: `phase_handlers.py` → `NightPhaseHandler._handle_demon_action()`

```python
# Demon responds with "3"
self.state_manager.record_action(
    phase_name="NIGHT1", 
    "kill",
    {"by": 5, "target": 3}
)
# Action saved with applied: false
```

### 2. Applying Actions (Between Phases)

**File**: `game_flow.py` → `GameOrchestrator.run_game_phases()`

```python
for idx in range(1, max_phases + 1):
    # ... determine phase_name ...
    
    if idx > 1:  # Not the first phase
        self._apply_previous_phase_actions(phase_name)
        # ↑ This applies NIGHT1 actions before DAY2 starts
```

**File**: `game_flow.py` → `GameOrchestrator._apply_previous_phase_actions()`

```python
def _apply_previous_phase_actions(self, current_phase):
    # Get previous phase (e.g., "NIGHT1" when current is "DAY2")
    prev_phase = all_phases[-1]
    
    # Apply all unapplied actions
    announcement_lines = self.state_manager.apply_actions(prev_phase, players)
    
    # Set announcements for current phase
    self.state_manager.set_announcements(current_phase, announcements)
```

**File**: `models.py` → `GameStateManager.apply_actions()`

```python
def apply_actions(self, phase, players):
    results = []
    for action in actions:
        if action.get("applied"):
            continue  # Skip already applied
        
        if action.get("type") == "kill":
            result = self._apply_kill_action(action, players)
            # result = "Alice was killed"
            results.append(result)
    
    return results  # ["Alice was killed"]
```

**File**: `models.py` → `GameStateManager._apply_kill_action()`

```python
def _apply_kill_action(self, action, players):
    target = next(p for p in players if p.number == target_num)
    
    if target and target.alive:
        target.alive = False  # Player is now dead!
        action["applied"] = True
        return f"{target.name} was killed"
```

### 3. Announcing Results (Next Phase)

**File**: `phase_handlers.py` → `PhaseHandler._build_email_body()`

```python
def _build_email_body(self, player, phase_name, players_list, announcements):
    parts = []
    
    if announcements:  # "Alice was killed"
        parts.append(announcements)
    
    # ... rest of email ...
```

## Action Types

### Kill Action
- **Recorded during**: Night phases (by Demon)
- **Applied before**: Next day phase
- **Announcement**: YES - "PlayerName was killed"
- **Effect**: Sets `player.alive = False`

### Poison Action
- **Recorded during**: Night phases (by Poisoner)
- **Applied before**: Next phase
- **Announcement**: NO - Silent/secret
- **Effect**: Sets `player.poisoned = True`

### Butler Choice
- **Recorded during**: First night (by Butler)
- **Applied before**: Next phase
- **Announcement**: NO - Not publicly announced
- **Effect**: Records master choice for voting rules

## Example Game Timeline

```
REGISTRATION
  ↓
NIGHT0 (First Night)
  ├── Actions recorded:
  │   ├── poison(by=4, target=1)
  │   └── butler_choice(by=2, master=3)
  └── [Actions NOT yet applied - no announcements for first night]
  ↓
  ↓ [Apply NIGHT0 actions]
  ↓ └── Player 1 now poisoned (silent)
  ↓ └── Butler's master recorded (silent)
  ↓
DAY1
  ├── Announcements: "" (none - first night actions are silent)
  ├── Player 1 poisoned but doesn't know
  └── [No kill actions recorded during day]
  ↓
  ↓ [No actions to apply from DAY1]
  ↓
NIGHT1
  ├── Actions recorded:
  │   ├── kill(by=5, target=3)
  │   └── poison(by=4, target=2)
  └── [Actions NOT yet applied]
  ↓
  ↓ [Apply NIGHT1 actions]
  ↓ ├── Player 3 killed
  ↓ └── Player 2 poisoned (silent)
  ↓
DAY2
  ├── Announcements: "Charlie was killed" ← From NIGHT1 kill
  ├── Player list shows Charlie as dead
  └── Players can see the result of the night
```

## Debugging Tips

The enhanced logging now shows:

```
Starting DAY2
==================================================

Applying actions from NIGHT1 to DAY2:
  Found 2 unapplied action(s) to process...
    Processing action: kill
      → Charlie was killed
    Processing action: poison
      → Poison applied (no announcement)

Announcements for DAY2:
  ✓ Charlie was killed

Game state snapshot saved for DAY2 (starting)
  Sent phase email to 1: Alice <alice@example.com>
  Sent phase email to 2: Bob <bob@example.com>
  ...
```

## Key Points

1. **Actions recorded** during a phase are marked `applied: false`
2. **Actions applied** at the START of the NEXT phase
3. **Announcements generated** from applied actions
4. **Announcements included** in next phase's emails
5. **Game state updated** immediately when actions applied
6. **All persisted** to gamestate.json with timestamps

This ensures a clear timeline: 
- Players take actions → Actions recorded → Phase ends
- Next phase starts → Actions applied → Results announced
- Players see consequences → New actions taken

The separation ensures actions are atomic and can be traced through the game state!
