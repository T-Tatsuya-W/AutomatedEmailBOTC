"""Phase handlers for different game phases."""
from typing import List

from models import Player, GameStateManager
from email_service import IMAPService, EmailComposer, ResponseCollector
from role_manager import RoleManager
from config import (
    REGISTRATION_SUBJECT_TEMPLATE,
    PHASE_SUBJECT_TEMPLATE
)


class PhaseHandler:
    """Base class for phase handlers."""

    def __init__(self, state_manager: GameStateManager):
        self.state_manager = state_manager
        self.imap_service = IMAPService()
        self.email_composer = EmailComposer()
        self.response_collector = ResponseCollector(self.imap_service)

    def send_phase_emails(
        self,
        players: List[Player],
        phase_name: str,
        subject_template: str
    ) -> None:
        """Send phase emails to all players."""
        players_list = self.email_composer.build_player_list(players)
        announcements = self.state_manager.get_announcements(phase_name)

        for player in players:
            subject = subject_template.format(num=player.number, phase=phase_name)
            body = self._build_email_body(
                player, phase_name, players_list, announcements
            )

            try:
                self.email_composer.send_email(player.email, subject, body)
                print(f"  Sent phase email to {player.number}: {player.name} <{player.email}>")
            except Exception as exc:
                print(f"  Failed to send phase email to {player.number}: {exc}")

    def _build_email_body(
        self,
        player: Player,
        phase_name: str,
        players_list: str,
        announcements: str
    ) -> str:
        """Build email body for a player. Override in subclasses for custom behavior."""
        parts = []

        if not player.alive:
            parts.append("YOU ARE DEAD")

        if announcements:
            parts.append(announcements)

        parts.append("")
        parts.append(f"Current phase: {phase_name}")
        parts.append("")
        parts.append("Players:")
        parts.append(players_list)
        parts.append("")
        parts.append(self._get_action_prompt(player))

        return "\n".join(parts).strip() + "\n"

    def _get_action_prompt(self, player: Player) -> str:
        """Get the action prompt for a player. Override in subclasses."""
        return "Please reply with one line to continue to the next phase."


class RegistrationHandler(PhaseHandler):
    """Handler for player registration phase."""

    def run(self, players: List[Player]) -> None:
        """Send registration confirmation and wait for all players to respond."""
        print("\nSending registration emails...")
        self._send_registration_emails(players)
        self._wait_for_all_responses(players)

    def _send_registration_emails(self, players: List[Player]) -> None:
        """Send registration confirmation email to each player."""
        players_list = self.email_composer.build_player_list(players)

        for player in players:
            subject = REGISTRATION_SUBJECT_TEMPLATE.format(num=player.number)
            body = self._build_registration_body(player, players_list)

            try:
                self.email_composer.send_email(player.email, subject, body)
                print(f"Sent registration to {player.number}: {player.name} <{player.email}>")
            except Exception as exc:
                print(f"Failed to send registration to {player.number}: {exc}")

    def _build_registration_body(self, player: Player, players_list: str) -> str:
        """Build registration email body."""
        parts = []
        if not player.alive:
            parts.append("YOU ARE DEAD")

        parts.extend([
            "",
            "Registration confirmation",
            "",
            "Players:",
            players_list,
            "",
            "Please reply with one line when you are ready to begin the game."
        ])

        return "\n".join(parts).strip() + "\n"

    def _wait_for_all_responses(self, players: List[Player]) -> None:
        """Wait for reply from every alive player."""
        imap = self.imap_service.connect()
        expected_subjects = {
            str(p.number): REGISTRATION_SUBJECT_TEMPLATE.format(num=p.number)
            for p in players
        }
        waiting = {str(p.number) for p in players if p.alive}

        def handle_response(player_key, from_addr, body, subj, uid):
            player = next((p for p in players if str(p.number) == player_key), None)
            if not player or player.email.lower() != from_addr.lower():
                return False

            first_line = self.email_composer.get_first_non_empty_line(body)
            self.state_manager.record_response(
                "REGISTRATION", player.number, first_line, from_addr
            )

            stored_count = len(
                self.state_manager._state
                .get("phase_updates", {})
                .get("REGISTRATION", {})
                .get("responses", {}) or {}
            )
            print(f"Recorded registration reply from {player_key} ({player.name}). "
                  f"Keeping {stored_count} responses.")
            return True

        try:
            self.response_collector.wait_for_responses(
                imap, expected_subjects, waiting, handle_response
            )
        except KeyboardInterrupt:
            print("Registration wait interrupted by user.")
        finally:
            self.imap_service.close(imap)


class DayPhaseHandler(PhaseHandler):
    """Handler for day phases."""

    def run(self, players: List[Player], phase_name: str) -> None:
        """Execute a day phase - collect simple one-line replies."""
        print(f"Running day phase: {phase_name}")
        self._update_phase(players, phase_name)
        self.send_phase_emails(players, phase_name, PHASE_SUBJECT_TEMPLATE)
        self._wait_for_responses(players, phase_name)
        # Ensure final state is written after all responses collected
        self.state_manager.set_players(players)
        print(f"Day phase {phase_name} complete. State saved.")

    def _update_phase(self, players: List[Player], phase_name: str) -> None:
        """Update phase with generic sent body."""
        players_list = self.email_composer.build_player_list(players)
        generic_sent = (
            f"BOTC Day Phase: {phase_name}\n\n"
            f"Players:\n{players_list}\n\n"
            f"Reply instructions: Respond with one line."
        )
        self.state_manager.update_phase(phase_name, sent_body=generic_sent)

    def _wait_for_responses(self, players: List[Player], phase_name: str) -> None:
        """Wait for one-line reply from all alive players."""
        imap = self.imap_service.connect()
        expected_subjects = {
            str(p.number): PHASE_SUBJECT_TEMPLATE.format(num=p.number, phase=phase_name)
            for p in players
        }
        waiting = {str(p.number) for p in players if p.alive}

        def handle_response(player_key, from_addr, body, subj, uid):
            player = next((p for p in players if str(p.number) == player_key), None)
            if not player or player.email.lower() != from_addr.lower():
                return False

            # Skip if already recorded
            if self.state_manager.has_response(phase_name, player.number):
                return True

            first_line = self.email_composer.get_first_non_empty_line(body)
            self.state_manager.record_response(
                phase_name, player.number, first_line, from_addr
            )

            stored_count = len(
                self.state_manager._state
                .get("phase_updates", {})
                .get(phase_name, {})
                .get("responses", {}) or {}
            )
            print(f"Recorded response from player {player_key} ({player.name}): {first_line!r}")
            print(f"Keeping {stored_count} responses.")
            return True

        try:
            self.response_collector.wait_for_responses(
                imap, expected_subjects, waiting, handle_response
            )
        finally:
            self.imap_service.close(imap)


class FirstNightHandler(PhaseHandler):
    """Handler for the first night with role-specific information and actions."""

    def run(self, players: List[Player], phase_name: str) -> None:
        """Execute the first night - send role info and collect initial responses."""
        print(f"Running first night phase: {phase_name}")
        self._update_phase(players, phase_name)
        self.send_phase_emails(players, phase_name, PHASE_SUBJECT_TEMPLATE)
        self._wait_for_responses(players, phase_name)
        # Ensure final state is written after all responses collected
        self.state_manager.set_players(players)
        print(f"First night phase {phase_name} complete. State saved.")

    def _update_phase(self, players: List[Player], phase_name: str) -> None:
        """Update phase with first night sent body."""
        players_list = self.email_composer.build_player_list(players)
        generic_sent = (
            f"BOTC First Night: {phase_name}\n\n"
            f"Players:\n{players_list}\n\n"
            f"Reply instructions: Respond based on your role."
        )
        self.state_manager.update_phase(phase_name, sent_body=generic_sent)

    def _build_email_body(
        self,
        player: Player,
        phase_name: str,
        players_list: str,
        announcements: str
    ) -> str:
        """Build first night email body with role information."""
        parts = []

        if not player.alive:
            parts.append("YOU ARE DEAD")

        if announcements:
            parts.append(announcements)

        parts.append("")
        parts.append("=" * 50)
        parts.append("FIRST NIGHT - ROLE INFORMATION")
        parts.append("=" * 50)
        parts.append("")
        parts.append(f"Your Role: {player.roleName}")
        parts.append(f"Role Type: {player.roleClass.upper()}")
        parts.append("")
        parts.append(self._get_role_description(player))
        parts.append("")
        parts.append(f"Current phase: {phase_name}")
        parts.append("")
        parts.append("Players:")
        parts.append(players_list)
        parts.append("")
        parts.append(self._get_action_prompt(player))

        return "\n".join(parts).strip() + "\n"

    def _get_role_description(self, player: Player) -> str:
        """Get role-specific description for first night."""
        role_descriptions = {
            # Townsfolk
            "Washerwoman": "You learn that one of two players is a particular Townsfolk.",
            "Librarian": "You learn that one of two players is a particular Outsider.",
            "Investigator": "You learn that one of two players is a particular Minion.",
            "Chef": "You learn how many pairs of evil players are sitting next to each other.",
            "Empath": "You learn how many of your living neighbors are evil.",
            "Fortune Teller": "You may choose two players each night. You learn if either is the Demon.",
            "Undertaker": "Each night (except the first), you learn which role died during the day.",
            "Monk": "Each night (except the first), you may protect another player from the Demon.",
            "Ravenkeeper": "If you die at night, you may choose a player and learn their role.",
            "Virgin": "The first time you are nominated, if the nominator is a Townsfolk, they die.",
            "Slayer": "Once per game, you may choose a player to die. If they are the Demon, they die.",
            "Soldier": "You are safe from the Demon.",
            "Mayor": "If only 3 players live and no execution occurs, your team wins.",
            
            # Outsiders
            "Butler": "Each night, choose a player (not yourself): tomorrow, you may only vote if they are voting too.",
            "Drunk": "You do not know you are the Drunk. You think you are a Townsfolk but have no ability.",
            "Recluse": "You might register as evil & as a Minion or Demon, even if dead.",
            "Saint": "If you die by execution, your team loses.",
            
            # Minions
            "Poisoner": "Each night, choose a player: they are poisoned tonight and tomorrow day.",
            "Spy": "Each night, you see the Grimoire. You might register as good & as a Townsfolk or Outsider.",
            "Scarlet Woman": "If there are 5 or more players alive and the Demon dies, you become the Demon.",
            "Baron": "There are extra Outsiders in play. [+2 Outsiders]",
            
            # Demons
            "Imp": "Each night (except the first), choose a player to kill. If you kill yourself, a Minion becomes the Imp."
        }
        
        description = role_descriptions.get(player.roleName, "No description available.")
        return f"ROLE DESCRIPTION:\n{description}"

    def _get_action_prompt(self, player: Player) -> str:
        """Get action prompt specific to first night."""
        if not player.alive:
            return "You are dead. Reply with 'acknowledged' to continue."

        role = player.roleName
        
        # Roles that need specific first night information
        first_night_info_roles = [
            "Washerwoman", "Librarian", "Investigator", 
            "Chef", "Empath", "Fortune Teller"
        ]
        
        # Roles that need to make a choice
        first_night_action_roles = ["Butler", "Poisoner"]
        
        if role in first_night_info_roles:
            return (
                f"FIRST NIGHT ACTION ({role}):\n"
                f"As the Storyteller will provide your information separately, "
                f"please reply 'ready' when you have received and understood your role information."
            )
        elif role == "Butler":
            return (
                "FIRST NIGHT ACTION (Butler):\n"
                "Reply with the NUMBER of the player you choose as your master for tomorrow. "
                "You may only vote tomorrow if they are voting too."
            )
        elif role == "Poisoner":
            return (
                "FIRST NIGHT ACTION (Poisoner):\n"
                "Reply with the NUMBER of the player you wish to poison tonight and tomorrow day. "
                "Their ability will not function."
            )
        elif role == "Spy":
            return (
                "FIRST NIGHT (Spy):\n"
                "You can see all player roles. This information will be provided by the Storyteller. "
                "Reply 'ready' when acknowledged."
            )
        elif RoleManager.is_demon(player):
            return (
                "FIRST NIGHT (Demon):\n"
                "You do not kill on the first night. "
                "You will be informed of your Minions. "
                "Reply 'ready' when acknowledged."
            )
        else:
            return (
                "FIRST NIGHT:\n"
                "You have received your role information. "
                "Reply 'ready' to continue to the first day."
            )

    def _wait_for_responses(self, players: List[Player], phase_name: str) -> None:
        """Wait for first night responses and handle role-specific actions."""
        imap = self.imap_service.connect()
        expected_subjects = {
            str(p.number): PHASE_SUBJECT_TEMPLATE.format(num=p.number, phase=phase_name)
            for p in players
        }
        waiting = {str(p.number) for p in players if p.alive}

        def handle_response(player_key, from_addr, body, subj, uid):
            player = next((p for p in players if str(p.number) == player_key), None)
            if not player or player.email.lower() != from_addr.lower():
                return False

            # Skip if already recorded
            if self.state_manager.has_response(phase_name, player.number):
                return True

            first_line = self.email_composer.get_first_non_empty_line(body)
            self.state_manager.record_response(
                phase_name, player.number, first_line, from_addr
            )

            # Handle role-specific first night actions
            if player.roleName == "Butler":
                return self._handle_butler_action(player, first_line, players, phase_name, expected_subjects)
            elif player.roleName == "Poisoner":
                return self._handle_poisoner_action(player, first_line, players, phase_name, expected_subjects)
            else:
                # Just acknowledge for most roles
                stored_count = len(
                    self.state_manager._state
                    .get("phase_updates", {})
                    .get(phase_name, {})
                    .get("responses", {}) or {}
                )
                print(f"Recorded first night response from player {player_key} ({player.name}): {first_line!r}")
                print(f"Keeping {stored_count} responses.")
                return True

        try:
            self.response_collector.wait_for_responses(
                imap, expected_subjects, waiting, handle_response
            )
        finally:
            self.imap_service.close(imap)

    def _handle_butler_action(
        self,
        player: Player,
        response: str,
        players: List[Player],
        phase_name: str,
        expected_subjects: dict
    ) -> bool:
        """Handle and validate Butler's master choice."""
        valid = False
        try:
            master_num = int(response.split()[0])
            master = next((p for p in players if p.number == master_num), None)
            if master and master.alive and master.number != player.number:
                self.state_manager.record_action(
                    phase_name, "butler_choice",
                    {"by": player.number, "master": master_num}
                )
                valid = True
                print(f"Recorded Butler choice by player {player.number} -> master {master_num}.")
        except Exception:
            valid = False

        if not valid:
            expected_subject = expected_subjects.get(str(player.number), "")
            prompt_body = (
                "Your Butler choice could not be interpreted. "
                "Please reply with the NUMBER of another living player to be your master."
            )
            try:
                self.email_composer.send_email(player.email, expected_subject, prompt_body)
                print(f"Requested valid Butler choice from player {player.number}.")
            except Exception as exc:
                print(f"Failed to send validation request to {player.email}: {exc}")
            return False

        return True

    def _handle_poisoner_action(
        self,
        player: Player,
        response: str,
        players: List[Player],
        phase_name: str,
        expected_subjects: dict
    ) -> bool:
        """Handle and validate Poisoner's target choice."""
        valid = False
        try:
            target_num = int(response.split()[0])
            target = next((p for p in players if p.number == target_num), None)
            if target and target.alive:
                self.state_manager.record_action(
                    phase_name, "poison",
                    {"by": player.number, "target": target_num}
                )
                valid = True
                print(f"Recorded Poisoner action by player {player.number} -> target {target_num}.")
        except Exception:
            valid = False

        if not valid:
            expected_subject = expected_subjects.get(str(player.number), "")
            prompt_body = (
                "Your Poisoner target could not be interpreted. "
                "Please reply with the NUMBER of a living player to poison."
            )
            try:
                self.email_composer.send_email(player.email, expected_subject, prompt_body)
                print(f"Requested valid Poisoner target from player {player.number}.")
            except Exception as exc:
                print(f"Failed to send validation request to {player.email}: {exc}")
            return False

        return True


class NightPhaseHandler(PhaseHandler):
    """Handler for night phases with demon actions."""

    def run(self, players: List[Player], phase_name: str) -> None:
        """Execute a night phase - collect replies and handle demon kills."""
        print(f"Running night phase: {phase_name}")
        self._update_phase(players, phase_name)
        self.send_phase_emails(players, phase_name, PHASE_SUBJECT_TEMPLATE)
        self._wait_for_responses(players, phase_name)
        # Ensure final state is written after all responses collected
        self.state_manager.set_players(players)
        print(f"Night phase {phase_name} complete. State saved.")

    def _update_phase(self, players: List[Player], phase_name: str) -> None:
        """Update phase with generic sent body."""
        players_list = self.email_composer.build_player_list(players)
        generic_sent = (
            f"BOTC Night Phase: {phase_name}\n\n"
            f"Players:\n{players_list}\n\n"
            f"Reply instructions: Respond with one line."
        )
        self.state_manager.update_phase(phase_name, sent_body=generic_sent)

    def _get_action_prompt(self, player: Player) -> str:
        """Get action prompt - demons get kill instructions."""
        if player.alive and RoleManager.is_demon(player):
            return (
                "IMP ACTION: Reply to this email with the NUMBER of the player "
                "you choose to kill (one-line reply)."
            )
        return "Please reply with one line to continue to the next phase."

    def _wait_for_responses(self, players: List[Player], phase_name: str) -> None:
        """Wait for replies from all alive players and validate demon kills."""
        imap = self.imap_service.connect()
        expected_subjects = {
            str(p.number): PHASE_SUBJECT_TEMPLATE.format(num=p.number, phase=phase_name)
            for p in players
        }
        waiting = {str(p.number) for p in players if p.alive}

        def handle_response(player_key, from_addr, body, subj, uid):
            player = next((p for p in players if str(p.number) == player_key), None)
            if not player or player.email.lower() != from_addr.lower():
                return False

            # Skip if already recorded
            if self.state_manager.has_response(phase_name, player.number):
                return True

            first_line = self.email_composer.get_first_non_empty_line(body)
            self.state_manager.record_response(
                phase_name, player.number, first_line, from_addr
            )

            # If demon, validate and record kill action
            if RoleManager.is_demon(player):
                return self._handle_demon_action(
                    player, first_line, players, phase_name, expected_subjects
                )
            else:
                stored_count = len(
                    self.state_manager._state
                    .get("phase_updates", {})
                    .get(phase_name, {})
                    .get("responses", {}) or {}
                )
                print(f"Recorded response from player {player_key} ({player.name}): {first_line!r}")
                print(f"Keeping {stored_count} responses.")
                return True

        try:
            self.response_collector.wait_for_responses(
                imap, expected_subjects, waiting, handle_response
            )
        finally:
            self.imap_service.close(imap)

    def _handle_demon_action(
        self,
        player: Player,
        response: str,
        players: List[Player],
        phase_name: str,
        expected_subjects: dict
    ) -> bool:
        """Handle and validate demon kill action."""
        valid = False
        try:
            target_num = int(response.split()[0])
            target = next((p for p in players if p.number == target_num), None)
            if target and target.alive:
                self.state_manager.record_action(
                    phase_name, "kill",
                    {"by": player.number, "target": target_num}
                )
                valid = True
                print(f"Recorded kill action by player {player.number} -> target {target_num}.")
        except Exception:
            valid = False

        if not valid:
            # Send validation prompt
            expected_subject = expected_subjects.get(str(player.number), "")
            prompt_body = (
                "Your last response could not be interpreted as a valid reply. "
                "Please reply to this same thread with a valid single-line response."
            )
            try:
                self.email_composer.send_email(player.email, expected_subject, prompt_body)
                print(f"Requested valid response from player {player.number}.")
            except Exception as exc:
                print(f"Failed to send validation request to {player.email}: {exc}")
            return False  # Keep waiting

        return True  # Valid response received
