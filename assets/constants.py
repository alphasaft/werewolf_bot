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
TOP_PLAYER_ROLE = "Chasseur pro"


TIMEZONE = timezone(timedelta(hours=2), "France")  # Your time zone here

# Game constants

DIALOGS_PATH = "data/story.json"
EVENTS_PATH = "data/events.xml"
XP_COUNTS_PATH = "data/xp_counts.xml"
MINIMUM_PLAYERS = 1
WHITE_VOTE = "Vote blanc"
ALLTIMES_CMDS = (
    'admin',
    'players',
    'private',
    'public',
    'quit',
    'commands',
    'role',
    'help',
    'votes',
    'again',
    'kick',
    'skip',
    'destroy',
)
LEVELS = (
    "Nouvel arrivant",
    "Paysan",
    "Villageois",
    "Citoyen",
    "Marchand",
    "Forgeron",
    "Novice en chasse",
    "Apprenti chasseur"
    "Chasseur confirmé",
    "Spécialiste en chasse",
    "Expert en chasse",
    "Virtuose en chasse"
)

# Roles

SEEKER = "voyante"
HUNTER = "chasseur"
LOVEMAKER = "cupidon"
WITCH = "sorcière"
VILLAGER = "villageois"
WEREWOLF = "loup-garou"
LITTLE_GIRL = "petite fille"
GUARD = "garde"
IDIOT = "idiot du village"

