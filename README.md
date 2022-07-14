# Yaml mult db

**Preview :**
Le Yaml permet la représentation de données par sérialisation.

Dans un monde où chacun veille au grain sur ses propres données, c'est très bien.

L'idée de ce projet est de développer une solution pour tous les autres mondes.

L'idée est que l'on puisse développer une base de données ouverte qui soit non seulement humainement lisible mais également que l'on puisse patcher sans pour autant l'écraser.

L'idée est que chacun puisse avoir sa propre version de la base de données en créant ou utilisant les patchs créés par soi ou par d'autres utilisateurs.
Tout en conservant la possibilité d'annuler un patch ou même de patcher un patch.

L'idée est de partir d'une multitude de fichiers yaml, de les assembler de façon ordonnée afin de générer un fichier unique fichier yaml (ou json) qui sera exploité par l'outil.

## En construction


```
from inc.base import YamlManager

cls = YamlManager()
cls.load("_base/")
cls.dump_yaml("default.yaml")
# cls.dump_json("default.json", ensure_ascii=False, indent=1)
```

### Exemples :

## Lien :
```
t0: test0
t1: << t0 >>1
```
Devient
```
t0: test0
t1: test01
```

## Héritage :
```
human:
    level: 1
    hp: 12

villager:
    <: human
    name: Villageois
```

Devient
```
human:
  hp: 12
  level: 1

villager:
  hp: 12
  level: 1
  name: Villageois
```

## Fix :
```
human:
    level: 1
    hp: 12

villager:
    <: human
    name: Villageois

human.fix.£.level: 2
```

Devient
```
human:
  hp: 12
  level: 2

villager:
  hp: 12
  level: 2
  name: Villageois

```

### Fix++
L'ajout d'un opérateur est possible (pas encore stable) :
```
human:
    level: 1
    hp: 12

human.fix.£:
    level|+: 2
    hp|*: 3
```

Devient
```
human:
  level: 3
  hp: 36
```
