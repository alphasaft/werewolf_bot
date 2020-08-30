from datetime import timezone, timedelta
from enum import Enum

# Bot settings

PREFIX = '$'
DESCRIPTION = """Je suis le conteur du village, toujours prêt pour de nouvelles aventures au coeur de la nuit..."""
TOKEN = """No token here. See token.py, and replace it by your own token."""

GUILD = 724226339443572770
WELCOME_CHANNEL = 726114430093623308
EVENTS_CHANNEL = 744228828867723476
EXPEDITIONS_CATEGORY = "EXPEDITIONS"
BASE_ROLE = "Manant"


TIMEZONE = timezone(timedelta(hours=2), "France")  # Your time zone here

# Game constants

DIALOGS_PATH = "data/story.json"
EVENTS_PATH = "data/events.xml"
MINIMUM_PLAYERS = 4
ALLTIMES_CMDS = (
    'admin', 'players', 'private', 'public', 'quit', 'commands', 'role', 'help', 'votes', 'again', 'kick', 'skip',
    'destroy',
)
WHITE_VOTE = "Vote blanc"


# Roles

SEEKER = "voyante"
HUNTER = "chasseur"
LOVEMAKER = "cupidon"
WITCH = "sorcière"
VILLAGER = "villageois"
WEREWOLF = "loup-garou"
LITTLE_GIRL = "petite fille"  # eheh

