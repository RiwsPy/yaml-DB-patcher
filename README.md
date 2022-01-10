# Yaml mult db

**Preview :**
Le Yaml permet la représentation de données par sérialisation.

Dans un monde où chacun veille au grain sur ses propres données, c'est très bien.

L'idée de ce projet est de développer une solution pour tous les autres mondes.

L'idée est que l'on puisse développer une base de données ouverte qui soit non seulement humainement lisible mais également que l'on puisse patcher sans pour autant l'écraser.

L'idée est que chacun puisse avoir sa propre version de la base de données en créant ou utilisant les patchs créés par soi ou par d'autres utilisateurs.
Tout en conservant la possibilité d'annuler un patch ou même de patcher un patch.

L'idée est de partir d'une multitude de fichiers yaml, de les assembler de façon ordonnée afin de générer un fichier unique fichier json qui sera exploité par l'outil.