from patchyml import YamlManager


if __name__ == "__main__":
    cls = YamlManager()
    cls.load("_base/")
    cls.dump_yaml("default.yaml")
    cls.dump_json("default.json", ensure_ascii=True, indent=1)
