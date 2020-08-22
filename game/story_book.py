import json
from random import choice
from assets.utils import block


class StoryBook(dict):
    """
    Store all the dialogs, based on a json file.
    The book is out of several chapters (see _StoryChapter). Use myBook.aChapter to access it.
    """
    def __init__(self, file):
        dict.__init__(self)
        self._get_dialogs(file)

    def __getattr__(self, item):
        """Return self[item]"""
        return self[item]

    def __str__(self):
        return str(self.as_json())

    def _get_dialogs(self, file):
        """Internal function to read the json file."""
        with open(file, 'r') as json_file:
            all_dialogs = json.loads(json_file.read())

        for chapter, chapter_content in all_dialogs.items():
            self[chapter] = _StoryChapter()
            for page, dialogs in chapter_content.items():
                self[chapter][page] = _StoryPage(dialogs)

    def as_json(self):
        """Return a dict, useful for json.dump"""
        json_dict = {}
        for name, chapter in self.items():
            if not json_dict.get(name):
                json_dict[name] = {}
            for page_name, page in chapter.items():
                json_dict[name][page_name] = page.to_list()

        return json_dict

    def save(self, file):
        """
        Saves the storybook into FILE. Then, if you want to put this data into an other StoryBook, you can just do :
        myOtherStorybook = StoryBook(FILE)
        """
        with open(file, 'w') as json_file:
            json.dump(self.as_json(), json_file, indent=4)


class _StoryChapter(dict):
    """
    Represents a chapter of a StoryBook. Each chapter refer to a villager, or a villager group (werewolf, witch...), and
    is out of several pages (see _StoryPage).
    You can access them with myStoryChapter.aPage
    """
    def __init__(self, pages=None):
        if pages:
            dict.__init__(self, pages)
        else:
            dict.__init__(self)

    def __getattr__(self, item):
        """Returns self[item]"""
        return self[item]


class _StoryPage(list):
    def __init__(self, dialogs):
        list.__init__(self, dialogs)

    def to_list(self):
        """Returns list(self)"""
        return list(self)

    def tell(self, **info):
        """
        Select a random dialog in self using random.choice(self), and format it with **infos, e.g. if the selected
        dialog is "Hello {player} !", tell(player="Someone") returns "Hello Someone !".
        Then formats the dialog as a discord block and returns it.
        """
        dialog = choice(self)
        dialog = dialog.format(**info)
        return block(dialog)

    def write(self, *dialogs):
        self.extend(dialogs)
