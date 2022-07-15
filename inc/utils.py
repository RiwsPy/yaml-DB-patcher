import functools


class OutputOfMyClass(type):
    """
    Méta classe qui permet de convertir le type des retours de toutes les méthodes de la classe dans le type de la classe.

    Prenons l'exemple d'une classe MyStr vide qui hérite de str :
    le retour de MyStr("test") sera "test", de type MyStr
    MyStr("test").upper() renverra "TEST", de type str

    Sans redéfinir upper() et en utilisant cette Méta classe,
    MyStr("test").upper() renverra "TEST", de type MyStr

    TODO: à tester plus en profondeur, notamment en cas d'héritage multiple
    """

    def __new__(mcs, name, bases, nmspc):
        for attrname, attrval in nmspc.items():
            if callable(attrval):
                nmspc[attrname] = mcs.change_return_type(attrval, bases)

        # overkill? ajout de toutes les méthodes str wrappées dans StrModel
        for base in bases:
            for attrname, attrval in base.__dict__.items():
                if callable(attrval) and attrname not in nmspc:
                    nmspc[attrname] = mcs.change_return_type(attrval, bases)

        return super().__new__(mcs, name, bases, nmspc)

    @classmethod
    def change_return_type(mcs, func, bases):
        @functools.wraps(func)
        def _(self, *args, **kwargs):
            ret = func(self, *args, **kwargs)
            if type(ret) in bases:
                return self.__class__(ret)
            return ret

        return _


def update_values(source: dict, other: dict) -> None:
    """
    Similaire à dict.update(other_dict)
    Excepté : seules les values sont affectées
    """
    if not isinstance(other, dict) or not isinstance(source, dict):
        return

    for k, v in other.items():
        if isinstance(v, dict) and isinstance(source.get(k), dict):
            update_values(source[k], other[k])
        else:
            # v.copy() ??
            source[k] = v


class Breaker(Exception):
    pass
