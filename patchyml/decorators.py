import os


def dump_file(func):
    def _(self, filename, *args, force=True, **kwargs):
        if force is False and os.path.exists(self.output_basename(filename)):
            raise FileExistsError(f"Échec. '{self.output_filename}' pré-existant.")

        func(self, filename, *args, **kwargs)
        print(f"Écriture dans {self.output_basename(filename)} terminée.")

    return _


def key_is_str(func):
    def _(self, key, *args, **kwargs):
        return func(self, str(key), *args, **kwargs)

    return _
