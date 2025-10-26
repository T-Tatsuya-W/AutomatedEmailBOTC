# Game State Structure Documentation

## Overview
The `gamestate.json` file is the central persistence mechanism for the Blood on the Clocktower game. It's updated at every phase and contains complete information about the game state, enabling games to be paused and resumed.

## Phase Naming Convention

The game uses descriptive phase names that clearly indicate the game progression:

- **REGISTRATION**: Initial player registration phase
- **NIGHT0**: First night (special first night with role reveals)
- **DAY1**: First day phase
- **NIGHT1**: Second night phase
- **DAY2**: Second day phase
- **NIGHT2**: Third night phase
- And so on...

### Pattern
- Registration happens before the game starts
- Night phases: NIGHT0, NIGHT1, NIGHT2, ...
- Day phases: DAY1, DAY2, DAY3, ...
- Phases alternate: NIGHT0 → DAY1 → NIGHT1 → DAY2 → NIGHT2 → ...

## JSON Structure

```json
{
  "phase": "CURRENT_PHASE_NAME",
  "players": [
    {
      "number": 1,
      "name": "Alice",
      "email": "alice@example.com",
      "alive": true,
      "hasGhostVote": true,
      "drunk": false,
      "poisoned": false,
      "roleClass": "townsfolk",
      "roleName": "Washerwoman"
    }
  ],
  "phase_updates": {
    "REGISTRATION": {
      "sent": "Registration email body...",
      "responses": {
        "1": {
          "from": "alice@example.com",
          "text": "ready"
        }
      },
      "actions": [],
      "announcements": "",
      "phase_type": "registration",
      "completed": true,
      "player_snapshot": {
        "alive_count": 5,
        "dead_count": 0,
        "players": [...]
      }
    },
    "NIGHT0": {
      "sent": "BOTC First Night: NIGHT0...",
      "responses": {
        "1": {
          "from": "alice@example.com",
          "text": "ready"
        },
        "2": {
          "from": "bob@example.com",
          "text": "3"
        }
      },
      "actions": [
        {
          "type": "butler_choice",
          "details": {
            "by": 2,
            "master": 3
          },
          "applied": false
        },
        {
          "type": "poison",
          "details": {
            "by": 4,
            "target": 1
          },
          "applied": false
        }
      ],
      "announcements": "",
      "phase_type": "first_night",
      "completed": true,
      "player_snapshot": {
        "alive_count": 5,
        "dead_count": 0,
        "players": [...]
      }
    },
    "DAY1": {
      "sent": "BOTC Day Phase: DAY1...",
      "responses": {...},
      "actions": [],
      "announcements": "Alice was killed",
      "phase_type": "day",
      "completed": true,
      "player_snapshot": {
        "alive_count": 4,
        "dead_count": 1,
        "players": [...]
      }
    },
    "NIGHT1": {
      "sent": "BOTC Night Phase: NIGHT1...",
      "responses": {...},
      "actions": [
        {
          "type": "kill",
          "details": {
            "by": 5,
            "target": 2
          },
          "applied": true,
          "result": {
            "target": 2,
            "target_name": "Bob"
          }
        }
      ],
      "announcements": "",
      "phase_type": "night",
      "completed": false,
      "player_snapshot": {...}
    }
  },
  "metadata": {
    "created_at": "2025-10-26T14:30:00.123456",
    "last_updated": "2025-10-26T15:45:30.789012",
    "version": "1.0"
  }
}
```

## Field Descriptions

### Top Level

| Field | Type | Description |
|-------|------|-------------|
| `phase` | string | Current active phase name (e.g., "NIGHT1", "DAY2") |
| `players` | array | Array of all player objects with current state |
| `phase_updates` | object | Map of phase names to phase data |
| `metadata` | object | Game metadata (timestamps, version) |

### Player Object

| Field | Type | Description |
|-------|------|-------------|
| `number` | integer | Player number (1-based) |
| `name` | string | Player's display name |
| `email` | string | Player's email address |
| `alive` | boolean | Whether player is alive |
| `hasGhostVote` | boolean | Whether player can use ghost vote |
| `drunk` | boolean | Whether player is drunk (ability doesn't work) |
| `poisoned` | boolean | Whether player is poisoned |
| `roleClass` | string | Role class: "townsfolk", "outsider", "minion", "demon" |
| `roleName` | string | Specific role name (e.g., "Imp", "Washerwoman") |

### Phase Update Object

| Field | Type | Description |
|-------|------|-------------|
| `sent` | string | Generic message body sent for this phase |
| `responses` | object | Map of player numbers to their responses |
| `actions` | array | List of actions taken during this phase |
| `announcements` | string | Announcements from previous phase actions |
| `phase_type` | string | Type: "registration", "first_night", "night", "day" |
| `completed` | boolean | Whether phase has finished |
| `player_snapshot` | object | Snapshot of player states during this phase |

### Action Object

| Field | Type | Description |
|-------|------|-------------|
| `type` | string | Action type: "kill", "poison", "butler_choice", etc. |
| `details` | object | Action-specific details (by, target, etc.) |
| `applied` | boolean | Whether action has been applied to game state |
| `result` | object | Result of applying the action (if applied) |

### Response Object

| Field | Type | Description |
|-------|------|-------------|
| `from` | string | Email address of respondent |
| `text` | string | First non-empty line of response |

### Player Snapshot

| Field | Type | Description |
|-------|------|-------------|
| `alive_count` | integer | Number of living players |
| `dead_count` | integer | Number of dead players |
| `players` | array | Array of player state snapshots |

## Update Frequency

The game state is updated at these key moments:

1. **Game Reset**: When `state_manager.reset()` is called
2. **Player Setup**: When players are created/assigned roles
3. **Phase Start**: When a new phase begins (snapshot saved)
4. **Phase Update**: When `update_phase()` is called with sent body
5. **Response Recording**: When each player response is recorded
6. **Action Recording**: When actions (kill, poison, etc.) are recorded
7. **Action Application**: When previous phase actions are applied
8. **Phase Complete**: When phase ends (final snapshot saved)
9. **Metadata Update**: Every write operation updates `last_updated`

## Using for Pause/Resume

To resume a game, you would:

1. Read `gamestate.json`
2. Check the `phase` field to see current phase
3. Check `phase_updates[current_phase].completed` to see if phase finished
4. Restore player list from `players` array
5. Continue from the current phase or start next phase

Example logic:
```python
state = json.load(open("gamestate.json"))
current_phase = state["phase"]
phase_data = state["phase_updates"].get(current_phase, {})

if phase_data.get("completed"):
    # Phase is complete, start next phase
    start_next_phase()
else:
    # Phase incomplete, resume current phase
    resume_phase(current_phase)
```

## Tracing Game Progress

The gamestate.json provides complete traceability:

1. **Timeline**: Check `metadata.created_at` and `last_updated`
2. **Phase History**: All phases in `phase_updates` keys (sorted chronologically)
3. **Player Evolution**: Compare `player_snapshot` across phases
4. **Action History**: Review `actions` array in each phase
5. **Communication**: Review `sent` and `responses` for each phase
6. **Effects**: Check `announcements` and action `result` fields

## Example Trace

```json
// Game created
"metadata": {"created_at": "2025-10-26T14:00:00"}

// Registration complete
"phase_updates": {
  "REGISTRATION": {
    "completed": true,
    "player_snapshot": {"alive_count": 5, "dead_count": 0}
  }
}

// First night - roles revealed, actions taken
"NIGHT0": {
  "completed": true,
  "actions": [
    {"type": "poison", "details": {"by": 4, "target": 1}}
  ]
}

// First day - poison announced
"DAY1": {
  "announcements": "",
  "player_snapshot": {"alive_count": 5, "dead_count": 0}
}

// Second night - demon kills
"NIGHT1": {
  "actions": [
    {"type": "kill", "details": {"by": 5, "target": 2}, "applied": true}
  ]
}

// Second day - kill announced
"DAY2": {
  "announcements": "Bob was killed",
  "player_snapshot": {"alive_count": 4, "dead_count": 1}
}
```

## Benefits

1. **Complete History**: Every phase transition is recorded
2. **Player State Tracking**: Snapshots show player evolution
3. **Action Audit Trail**: All actions and results tracked
4. **Pause/Resume Ready**: Contains everything needed to resume
5. **Debugging**: Easy to trace what happened when
6. **Analysis**: Post-game analysis of decisions and outcomes
