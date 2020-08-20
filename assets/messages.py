import discord
from discord import Embed

import assets.constants as consts

class _EmbedSkeleton:
    """
    Represents an incomplete discord Embed. This allows you to record a template into it and
    to format this template to get a ready Embed using self.build()
    """
    def __init__(self, *, title, content, footer=None, color=None):
        self.title = title
        self.content = content
        self.footer = footer
        self.color = color

    def build(self, **info):
        """
        Format self.content with *info, the title with title_info if provided and the footer with footer_info if
        provided.

        Parameters

        **info -- the info that will format the content

        Returns

        The corresponding discord Embed
        """
        embed = Embed(
            title=self.title.format(**info),
            description=self.content.format(**info),
            color=getattr(discord.Color, self.color)() if self.color else Embed.Empty
        )
        if self.footer:
            embed.set_footer(text=self.footer.format(**info))
        return embed

    def as_str(self, **info):
        """Same as build, by returns a string instead of an Embed"""
        template = """%s
        
        %s
        
        %s"""

        header = self.title.format(**info)
        content = self.content.format(**info)
        footer = self.footer.format(**info)

        return template % (header, content, footer)


# --- Global ---

MISSING_PARAMETER = """
Syntaxe attendue : %s, paramêtre %s manquant
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


# --- Others ---

WELCOME = """
Bienvenue à %s dans notre charmant village ! Combien de temps vas-tu tenir ?
N'oublie pas de lire les règles à la Mairie !
"""


# --- game new ---

SUCCESSFULLY_CREATED = """
--- Partie %s créée avec succès ! :thumbsup: ---
Utilisez `$game join %s` pour la rejoindre !
"""

FAILED_GAME_CREATION = """
Erreur lors de la création de la partie %s : %s
"""

# --- game join ---

SUCCESSFULLY_JOINED = """
Vous avez rejoint la partie %s avec succès ! :partying_face:
"""

FAILED_JOIN = """
Vous ne pouvez pas rejoindre cette partie : vous appartenez déjà à celle %s :weary:
"""

NOT_JOIGNABLE = """
La partie %s ne peut pas être jointe, car elle est en cours :cry:
"""


# --- game admin ---

FAILED_ADMIN_CHANGE = """
Le joueur %s n'a pas pu être mis administrateur de la partie %s, car il ne l'a pas jointe. :x:
"""

ADMIN_SUCCESSFULLY_CHANGED = """
L'administrateur de la partie %s est maintenant %s :innocent:
"""

# --- game quit ---

CANNOT_QUIT_IN_GAME = """
:x: Vous appartenez à une partie en cours et ne pouvez pas la quitter de cette façon !
Retournez dans votre partie (fil de discussion privé avec Clyde the Storyteller), puis tapez `$quit` ! 
"""

CONFIRM_FOR_GAME_DESTRUCTION = """
:exclamation: Attention :exclamation:
Etant l'adminstrateur de la partie %s, la quitter la détruira ! Êtes vous sûr ?
"""

SUCCESSFULLY_DELETED = """
La partie %s a bien été détruite.
"""

SUCCESSFULLY_QUITED = """
Vous avez quitté la partie %s avec succès
"""


# --- game kick ---

SUCCESSFULLY_KICKED = """
Le joueur %s a bien été kické de la partie %s
"""

CANNOT_KICK_YOURSELF = """
Vous ne pouvez pas vous banir vous-même de la partie ; Utilisez $game quit pour la quiter.
"""


# --- game list ---

OPENED_GAMES_LIST = _EmbedSkeleton(
    title="Voici la liste des parties joignables sur ce serveur :",
    content="- {games}",
    footer="Utilisez $game join UnePartie pour en rejoindre une"
)

NO_OPENED_GAME = _EmbedSkeleton(
    title="Mince...",
    content="Il n'y a aucune partie ouverte sur ce serveur...",
    footer="Et si vous en créiez une ?"
)


# --- game members ---

GAME_MEMBERS_LIST = _EmbedSkeleton(
    title="Membres de la partie {name}",
    content="- {members}",
    footer="{how_much}/" + str(consts.MINIMUM_PLAYERS) + '+'
)


# --- game start ---

MISSING_PLAYERS = """
:x: Il manque encore des joueurs pour pouvoir démarrer la partie %s ! (%i/{})
""".format(consts.MINIMUM_PLAYERS)

GAME_START = _EmbedSkeleton(
    title="Nouvelle expédition !",
    content="- {members}",
    footer="Souhaitez-leur bonne chance !"
)


# --- kick ---

MISSING_USER = """
:x: L'utilisateur %s n'a pas joint ce serveur.
"""


# --- NICKNAMES ---

BAD_NAME = """
Votre nom (%s) ne peut pas être utilisé tel quel pour jouer, merci de choisir un pseudonyme pour cette partie avec \
$nickname unPseudo, puis de confirmer avec $confirm. Le pseudonyme choisi doit ne pas comporter d'espaces, \
n'être composé que de chiffres et/ou lettres et ne pas dépasser 15 caractères.
"""

CHOOSE_NICKNAME = """
Vous pouvez choisir un pseudonyme pour cette partie avec $nickname unPseudo et confirmer avec $confirm, ou simplement \
conserver le votre (%s) directement en tapant $confirm. La partie commencera lorsque tous auront confirmé.
"""

PLEASE_FIRST_CHOOSE_NICKNAME = """
Merci de d'abord choisir votre pseudonyme. La partie ne commencera qu'après.
"""

INVALID_NICKNAME = """
Pseudonyme invalide '%s' (le pseudonyme doit avoir une longueur de 15 caractères maximum, être uniquement \
alphanumérique, et ne pas comporter d'espaces).
"""

NICKNAME_ALREADY_CONFIRMED = """
Votre pseudo est déjà bloqué pour %s
"""

NICKNAME_ALREADY_TAKEN = """
Le pseudo %s est déjà pris par %s
"""

CHANGED_NICKNAME = """
Votre pseudonyme a été changé pour %s
"""

CONFIRMED_NICKNAME = """
%s a bloqué son pseudo pour %s
"""

GET_NICKNAMES = _EmbedSkeleton(
    title="Liste des joueurs",
    content="- {nicknames}",
    footer="Tapez $players si vous ne vous en souvenez plus"
)

GET_COMMANDS = _EmbedSkeleton(
    title="Liste des commandes disponibles",
    content="- {commands}",
    footer="Tapez $commands si vous ne vous en souvenez plus"
)

GET_VOTES = _EmbedSkeleton(
    title="Liste des votes",
    content="- {votes}",
    footer="Tapez $votes si vous voulez les reconsulter."
)

GET_WEREWOLFS = _EmbedSkeleton(
    title="Liste des loup-garous",
    content="- {werewolfs}",
    footer="La cible actuelle est {target}. {agree} est/sont d'accord pour l'instant."
)

GET_ROLE = """Vous êtes %s"""


# --- GAME ---

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

GAME_RESTARTED = """
Vous retournez dans la forêt pour une nouvelle expédition, afin de terminer ce que vous avez commencé...
"""

GAME_HAS_ENDED = """
> Les membres de l'expédition %s sont de retour !
"""


# --- Game beginner's guide ---

# Game principe
GAME_PRINCIPE = _EmbedSkeleton(
    title="__Principe du jeu__",
    content="""

Ce jeu est une version online du jeu original, utilisant un bot en tant que maître du jeu. 
Les règles ne changent donc pas (vous pouvez les lire ici : \
https://ludos.brussels/ludo-luAPE/opac_css/doc_num.php?explnum_id=307 ; attention, certains personnages sont dans une \
version mais pas d'en l'autre, il s'agit juste pour vous d'apréhender l'unviers et/ou l'histoire !)

Attaquons le vif du sujet : le jeu en lui-même. Il y a plusieurs choses importantes à savoir :

- Tous vos amis jouent en parallèle, sur leurs propres fils de discussion avec Clyde. Cela permet en effet d'envoyer \
les bons messages aux bonnes personnes pour conserver l'anonymat la nuit.

- Le jeu est à base de commandes, par exemple pour tuer le joueur "Alphasaft" avec la sorcière, vous devez taper \
"$kill Alphasaft". Les commandes à utiliser sont décrites à chaque étape du jeu, et vous pouvez toujours \
demander de l'aide au jeu en utilisant la commande $help, ou celle $commands (essayez et vous verrez :laughing:)

- Un message commençant par '$' est considéré comme une commande. Il ne sera envoyé à aucun de vos amis. Chaque \
commande déclenchera une action ou vous affichera une information correspondante.

- Un message ne commençant pas par '$' sera lui relayé à tous les joueurs, à moins que vous soyez un loup-garou pendant\
 la phase des loup-garous , auquel cas seuls les loup-garous le recevront.

- Attention, certaines commandes vous demandent d'indiquer un joueur. Utilisez son pseudo, choisi en début de partie au\
 lieu de son nom discord réel ! 
  
Votre but du jeu vous sera (ou vous a déjà été) indiqué en début de partie, ainsi que votre rôle. De plus, pour \
faciliter la communication, un salon vocal portant le nom de votre partie est crée automatiquement. Il vous suffit \
de vous y connecter ! Vous pouvez également demander de l'aide aux joueurs plus expérimentés, à vos amis et/ou dans le \
salon faq, cela pourra peut être vous permettre d'avoir des réponses plus détaillées.

""".strip(),
    footer=Embed.Empty,
    color="green"
)

# Commands list
BASE_COMMANDS = _EmbedSkeleton(
    title="Commandes de base",
    content="""

Il existe un certain nombre de commandes dans le jeu : certaines déclenchent des actions, font avancer le jeu ou encore\
 vous aident. Voici une liste des quelques commandes disponibles quel que soit votre rôle et le moment:

- `$public monMessage` force l'envoi de votre message à tout le monde (même si vous êtes un loup-garou)

- `$private unJoueur monMessage` n'enverra votre message qu'à ce joueur

- `$players` vous affiche la liste des joueurs, leur pseudo ainsi que leur état (mort ou vivant)

- `$commands` affiche une liste des commandes que vous pouvez actuellement utiliser, ainsi qu'une courte description.

- `$help (full)` vous offre une courte description de ce que vous devez actuellement faire, ou affiche ce tutoriel si \
vous tapez `$help full`

- `$role` vous indique votre role, qui vous sera de toute manière donné au début

- `$quit` vous permet de quitter à tout moment la partie. Attention, car vous ne pourrez plus y revenir ! 

- `$kick unJoueur` vous permet de kicker un membre de la partie, uniquement si vous êtes son admin

- `$admin unJoueur` change l'admin de votre partie pour unJoueur, uniquement si vous étiez le précédant admin.

D'autres commandes existent, mais leur usage sera clairement explicité lors du jeu, uniquement à des moments précis.
Si vous avez un doute, vous pouvez toujours taper $commands et/ou $ĥelp.
Dans tous les cas, bon jeu, en espérant que vous ayez compris !

""".strip(),
    footer="Tapez $help full, $help ou $commands pour obtenir de l'aide à tout moment",
    color="blue"
)

