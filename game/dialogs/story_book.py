import json
from random import choice


class StoryBook(dict):
    """
    Store all the dialogs, based on a json file. Allows you to do storybook.a_dialog instead of storybook['a_dialog']
    """
    def __init__(self, file):
        dict.__init__(self)
        self._get_dialogs(file)

    def __getattr__(self, item):
        """Return dict.__getitem__(self, item)"""
        return self.__getitem__(item)

    def __str__(self):
        return str(self.as_json())

    def _get_dialogs(self, file):
        with open(file, 'r') as json_file:
            all_dialogs = json.load(json_file)

        for name, chapter in all_dialogs.items():
            self[name] = _StoryChapter()
            for page, dialogs in chapter.items():
                self[name].pages[page] = _StoryPage(dialogs)

    def as_json(self):
        """Return a dict, usefull for json.dump"""
        json_dict = {}
        for name, chapter in self.items():
            if not json_dict.get(chapter):
                json_dict[chapter] = {}
            for page_name, page in chapter.pages.items():
                json_dict[chapter][page_name] = page.to_list()

        return json_dict

    def save(self, file):
        """
        Saves the storybook into FILE. Then, if you want to put this data into an other StoryBook, you can just do :
        myOtherStorybook = StoryBook(FILE)
        """
        with open(file, 'w') as json_file:
            json.dump(self.as_json(), json_file, indent=4)


class _StoryChapter:
    def __init__(self, pages=None):
        self.pages = pages or {}

    def __getattr__(self, item):
        return self.pages[item]


class _StoryPage:
    def __init__(self, dialogs):
        self.dialogs = dialogs

    def to_list(self):
        return self.dialogs

    def tell(self, **infos):
        dialog = choice(self.dialogs)
        for name, info in infos.items():
            if "<"+name+">" not in dialog:
                raise ValueError("Cannot find info '<%s>' in dialog '%s'" % (info, dialog))
            dialog = dialog.replace('<'+name+'>', info)
        return dialog

