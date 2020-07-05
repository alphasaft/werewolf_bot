import assets.constants as consts

# global

MISSING_PARAMETER = """
Syntaxe attendue : %s, paramêtre <%s> manquant
"""

TOO_MUCH_PARAMETERS = """
Syntaxe attendue : %s, le(s) paramêtre(s) '%s' sont en trop 
"""

MISSING_PERMISSIONS = """
Erreur : Il vous manque la/les permission(s) %s pour la partie %s pour faire cela. 
"""

WRONG_GAME_NAME = """
Erreur : la partie %s n'existe pas
"""

NO_GAME_JOINED = """
Erreur : L'utilisateur %s n'a pas rejoint %s.
"""

ALREADY_WAITING = """
Erreur :  Déjà en attente d'une confirmation pour la commande %s
"""


# Others

WELCOME = """
Bienvenue à %s dans notre charmant village ! Combien de temps vas-tu tenir ?
N'oublie pas de lire les règles à la Mairie !
"""


# game new

SUCCESSFULLY_CREATED = """
--- Partie %s créée avec succès ! ---
Utilisez !game join %s pour la rejoindre !
"""

FAILED_GAME_CREATION = """
Erreur lors de la création de la partie %s : %s
"""

# game join

SUCCESSFULLY_JOINED = """
Vous avez rejoint la partie %s avec succès !
"""

FAILED_JOIN = """
Vous ne pouvez pas rejoindre cette partie : vous appartenez déjà à celle %s 
"""

NOT_JOIGNABLE = """
La partie %s ne peut pas être jointe, car elle est en cours
"""


# game admin

FAILED_ADMIN_CHANGE = """
Le joueur %s n'a pas pu être mis administrateur de la partie %s, car il ne l'a pas jointe.
"""

ADMIN_SUCCESSFULLY_CHANGED = """
L'administrateur de la partie %s est maintenant %s 
"""

# game quit

CONFIRM_FOR_GAME_DESTRUCTION = """
/!\ Attention /!\\
Etant l'adminstrateur de la partie %s, la quitter la détruira ! Êtes vous sûr ?
"""

SUCCESSFULLY_DELETED = """
La partie %s a bien été détruite.
"""

SUCCESSFULLY_QUITED = """
Vous avez quitté la partie %s avec succès
"""


# game kick

SUCCESSFULLY_KICKED = """
Le joueur %s a bien été kické de la partie %s
"""

CANNOT_KICK_YOURSELF = """
Vous ne pouvez pas vous banir vous-même de la partie ; Utilisez !game quit pour la quiter.
"""


# game list

NO_OPENED_GAME = """
Il n'y a aucune partie ouverte sur ce serveur
"""

OPENED_GAMES_LIST = """
Voici la liste des parties joignables sur ce serveur :

- %s

Utilisez !game join <NOM DE LA PARTIE> pour en rejoindre une
"""


# game members

GAME_MEMBERS_LIST = f"""
Voici la liste des membres de la partie %s :

- %s

%i/{consts.MINIMUM_PLAYERS}+
"""


# game start

MISSING_PLAYERS = f"""
Il manque encore des joueurs pour pouvoir démarrer la partie %s ! (%i/{consts.MINIMUM_PLAYERS}) 
"""

GAME_START = """
Les joueurs 

- %s

semblent déterminés à éliminer la menace des loup-garous. Souhaitez-leur bonne chance...
"""


# kick

MISSING_USER = """
L'utilisateur %s n'a pas joint ce serveur.
"""


# NICKNAMES

BAD_NAME = """
Votre nom (%s) ne peut pas être utilisé tel quel pour jouer, merci de choisir un pseudonyme pour cette partie avec \ 
!nickname <votre pseudonyme>, puis de confirmer avec confirm. Le pseudonyme choisi doit ne pas comporter d'espaces, \
n'être composé que de chiffres et/ou lettres et ne pas dépasser 10 caractères.
"""

CHOOSE_NICKNAME = """
Vous pouvez choisir un pseudonyme pour cette partie avec !nickname <pseudo> et confirmer avec !confirm, ou simplement \
conserver le votre (%s) directement en tapant !confirm. La partie commencera lorque tous auront confirmé.
"""

PLEASE_FIRST_CHOOSE_NICKNAME = """
Merci de d'abord choisir votre pseudonyme. La partie ne commencera qu'après.
"""

INVALID_NICKNAME = """
Pseudonyme invalide '%s' (le pseudonyme doit avoir une longueur de 10 caractères maximum, être uniquement \
alphanumérique, et je te vois, le mec du fond qui va choisir un pseudo pas adapté ; évite, merci pour les autres).
"""

CHANGED_NICKNAME = """
Votre pseudonyme a été changé pour %s
"""

CONFIRMED_NICKNAME = """
Vous avez bloqué votre pseudo pour %s
"""

NICKNAME_ALREADY_CONFIRMED = """
Votre pseudo est déjà bloqué pour %s
"""

GET_NICKNAMES = """
Les pseudos des joueurs sont les suivants :

- %s

Tapez !players si vous ne vous en souvenez plus.
"""



# GAME

NO_SUCH_PLAYER = """
Le joueur %s n'existe pas, ou il n'habite pas dans ce village
"""

DEAD_PLAYER = """
Le joueur %s appartient bien à cette partie, mais il est déjà definitivement mort !
"""

WOUNDED_PLAYER = """
Le joueur %s appartient bien à cette partie, mais il est déjà mort !
"""

ALIVE_PLAYER = """
Le joueur %s appartient bien à cette partie, mais il est en parfaite santé !
"""

WRONG_COMMAND = """
La commande %s ne doit pas être utilisée maintenant ; elle peut aussi ne simplement pas exister.
"""

WRONG_ROLE = """
Ce n'est pas votre tour, vous ne pouvez donc pas utiliser de commandes !
"""

DEAD_USER_INVOKES_CMD = """
Vous ne pouvez plus utiliser de commandes impliquant des actions puisque vous êtes mort(e) !
"""
