# Yaml DB patcher

**Preview :**
Le Yaml permet la représentation de données par sérialisation.

Dans un monde où chacun veille au grain sur ses propres données, c'est très bien.

L'idée de ce projet est de développer une solution pour tous les autres mondes.

L'idée est que l'on puisse développer une base de données ouverte qui soit non seulement humainement lisible mais également que l'on puisse patcher sans pour autant l'écraser.

L'idée est que chacun puisse avoir sa propre version de la base de données en créant ou utilisant les patchs créés par soi ou par d'autres utilisateurs.
Tout en conservant la possibilité d'annuler un patch ou même de patcher un patch.

L'idée est de partir d'une multitude de fichiers yaml, de les assembler de façon ordonnée afin de générer un fichier unique fichier yaml (ou json) qui sera exploité par l'outil.

L'idée c'est qu'un utilisateur sans connaissances avancées puisse modifier sa base comme il l'entend, la partager et y appliquer les patchs des autres utilisateurs.

## En construction


```
from patchyml import YamlManager

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

F£.human.level: 2
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

### Fix|+
L'ajout d'un opérateur est possible (pas encore stable) :
```
human:
    level: 1
    hp: 12

F£.human:
    level|+: 2
    hp|*: 3
    atk|+: 1
```

Devient
```
human:
  atk: 1
  hp: 36
  level: 3
```

## Namespace $

Afin de réduire facilement les conflits lors du chargements des différents patchs, il est préférable de namespacer les différentes entrées dans les fichiers yaml.\
Sinon deux entrées au même nom s'écraseront occasionnant des effets parfois indésirables.\
Pour éviter de créer des noms à rallonge, il est conseillé d'utiliser le caractère **$**.
```
# monpatch/d.yaml
$0: entrée0
$1: entrée1
$fake0: <<$0>>
```
Devient
```
monpatch:
    d:
        0: entrée0
        1: entrée1
        fake0: entrée0
```

Cela n'est cependant pas sans conséquence. Comme **$** peut se trouver aussi bien dans les clés que dans les valeurs, tous les caractères **$** sont remplacés.\
Il est donc **fortement déconseillé d'utiliser le caractère $ en dehors de cet usage.**

```
# monpatch/d.yaml
$0: Seulement 10$ ? Une aubaine !
```
Devient
```
monpatch:
    d:
        0: Seulement 10monpatch.d ? Une aubaine !
```
