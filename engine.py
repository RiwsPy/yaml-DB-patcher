from inc.base import YamlReader

if __name__ == '__main__':
    cls = YamlReader("_base/cre.yaml")
    cls.read_sub_save()
    cls.dump(force=True)
