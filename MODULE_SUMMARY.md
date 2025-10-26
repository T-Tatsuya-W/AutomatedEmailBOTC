# Module Summary

## Quick Reference Guide

### Module Dependencies

```
main.py
├── config.py (no dependencies)
├── models.py
│   └── config.py
├── player_setup.py
│   ├── models.py
│   └── config.py
├── role_manager.py
│   ├── models.py
│   └── config.py
├── email_service.py
│   ├── config.py
│   └── email_sender.py (external)
├── phase_handlers.py
│   ├── models.py
│   ├── email_service.py
│   ├── role_manager.py
│   └── config.py
└── game_flow.py
    ├── models.py
    ├── phase_handlers.py
    └── config.py
```

## Module Responsibilities

| Module | Lines | Primary Responsibility | Key Classes |
|--------|-------|------------------------|-------------|
| `config.py` | ~60 | Configuration & constants | None (just constants) |
| `models.py` | ~200 | Data models & state management | `Player`, `GameStateManager` |
| `email_service.py` | ~200 | Email I/O operations | `IMAPService`, `EmailComposer`, `ResponseCollector` |
| `role_manager.py` | ~70 | Role assignment logic | `RoleManager` |
| `phase_handlers.py` | ~300 | Phase-specific game logic | `PhaseHandler`, `RegistrationHandler`, `DayPhaseHandler`, `NightPhaseHandler` |
| `game_flow.py` | ~50 | Game orchestration | `GameOrchestrator` |
| `player_setup.py` | ~50 | Player creation | `PlayerSetup` |
| `main.py` | ~35 | Entry point | None (orchestration only) |

## Key Design Patterns Used

### 1. **Single Responsibility Principle**
Each module has one clear purpose.

### 2. **Dependency Injection**
Services receive dependencies rather than creating them:
```python
response_collector = ResponseCollector(imap_service)
```

### 3. **Template Method Pattern**
`PhaseHandler` base class with overridable methods:
```python
class PhaseHandler:
    def _get_action_prompt(self, player: Player) -> str:
        # Override in subclasses
```

### 4. **Strategy Pattern**
Different phase handlers for different game phases:
- `RegistrationHandler`
- `DayPhaseHandler`
- `NightPhaseHandler`

### 5. **Callback Pattern**
`ResponseCollector.wait_for_responses()` uses callbacks for flexible response handling.

### 6. **Static Utility Classes**
`RoleManager` and `PlayerSetup` provide static methods for stateless operations.

## Code Flow

### Startup Sequence
1. `main.py::main()` - Entry point
2. Initialize `GameStateManager`
3. Reset game state
4. `PlayerSetup.prompt_player_count()` - Get player count
5. `PlayerSetup.build_players()` - Create player objects
6. `RoleManager.assign_roles()` - Assign roles randomly
7. Save players to game state
8. `RegistrationHandler.run()` - Wait for player confirmation
9. `GameOrchestrator.run_game_phases()` - Run game loop

### Game Phase Loop
1. Apply actions from previous phase
2. Set announcements for current phase
3. Select appropriate handler (Day/Night)
4. Send phase emails to all players
5. Collect responses via email
6. Validate demon actions (if night phase)
7. Record responses and actions
8. Repeat until max phases reached

## Testing Strategy

### Unit Tests (Future)
- `test_models.py` - Test Player and GameStateManager
- `test_role_manager.py` - Test role distribution
- `test_email_service.py` - Mock IMAP/SMTP
- `test_phase_handlers.py` - Mock email service
- `test_game_flow.py` - Integration tests

### Mock Objects
Use mocks for:
- IMAP connections (`IMAPService`)
- Email sending (`EmailComposer`)
- File I/O (`GameStateManager`)

## Migration Notes

### Breaking Changes
None - the refactored code maintains backward compatibility.

### File System
All files remain in the same directory. No changes to:
- `gamestate.json`
- `.env` configuration
- `requirements.txt`

### Runtime Behavior
The game runs identically to the original implementation.
