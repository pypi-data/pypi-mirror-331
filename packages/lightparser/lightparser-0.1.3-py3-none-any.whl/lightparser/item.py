class Item(dict):
    def __setitem__(self, key, value):
        if value is not None:
            super().__setitem__(key, value)
