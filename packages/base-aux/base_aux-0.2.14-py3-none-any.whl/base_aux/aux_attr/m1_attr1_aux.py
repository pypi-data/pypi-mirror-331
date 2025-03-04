import re

from base_aux.base_inits.m1_nest_init_source import *
from base_aux.base_statics.m4_enums import *
from base_aux.base_statics.m1_types import *
from base_aux.aux_callable.m1_callable_aux import CallableAux
from base_aux.aux_attr.m0_dump import AttrsDump


# =====================================================================================================================
@final
class AttrAux(NestInit_Source):
    """
    NOTE
    ----
    if there are several same aux_attr in different cases - you should resolve it by yourself!

    ANNOTS
    ------
    not used/intended here! dont mess they - it means you need to know what exact you will work with (attrs or annots)
    and prepare classes appropriate!
    """
    SOURCE: Any = AttrsDump

    # =================================================================================================================
    def get_name__private_external(self, dirname: str) -> str | None:
        """
        typically BUILTIN - NOT INCLUDED!

        NOTE
        ----
        BEST WAY TO USE EXACTLY iter__not_private

        GOAL
        ----
        using name (from dir(obj)) return user-friendly name! external name!

        REASON
        ------
        here in example - "__hello" will never appear directly!!!
        class Cls:
            ATTR1 = 1
            def __hello(self, *args) -> None:
                kwargs = dict.fromkeys(args)
                self.__init_kwargs(**kwargs)

        name='_Cls__hello' hasattr(self.SOURCE, name)=True
        name='__class__' hasattr(self.SOURCE, name)=True
        name='__delattr__' hasattr(self.SOURCE, name)=True
        name='__dict__' hasattr(self.SOURCE, name)=True
        name='__dir__' hasattr(self.SOURCE, name)=True
        name='__doc__' hasattr(self.SOURCE, name)=True
        ///
        name='ATTR1' hasattr(self.SOURCE, name)=True
        """
        # filter not hidden -------
        if not dirname.startswith("_"):
            return

        # filter private builtin -------
        if dirname.startswith("__"):
            return

        # parse private user -------
        if re.fullmatch(r"_.+__.+", dirname):
            # print(f"{dirname=}")
            # print(f"{self.SOURCE=}")
            try:
                # print(11)
                mro = self.SOURCE.__mro__
            except:
                # print(111)
                mro = self.SOURCE.__class__.__mro__
                # print(f"{mro=}")

            # fixme: cant solve problem for GetattrPrefixInst_RaiseIf! in case of _GETATTR__PREFIXES!!!
            for cls in mro:
                if dirname.startswith(f"_{cls.__name__}__"):
                    name_external = dirname.replace(f"_{cls.__name__}", "")
                    return name_external

    # =================================================================================================================
    # def __contains__(self, item: str):      # IN=DONT USE IT! USE DIRECT METHOD anycase__check_exists
    #     return self.anycase__check_exists(item)

    # ITER ------------------------------------------------------------------------------------------------------------
    def iter__external_not_builtin(self) -> Iterable[str]:
        """
        NOTE
        ----
        BEST WAY TO USE EXACTLY iter__not_private

        GOAL
        ----
        1/ iter only without builtins!!!
        2/ use EXT private names!

        SPECIALLY CREATED FOR
        ---------------------
        this class - all iterations!
        """
        for name in dir(self.SOURCE):
            # filter builtin ----------
            if name.startswith("__"):
                continue

            # filter private external ----------
            name_private_ext = self.get_name__private_external(name)
            if name_private_ext:
                yield name_private_ext
                continue

            # direct user attr ----------
            # print(f"{name=}")
            yield name

    # -----------------------------------------------------------------------------------------------------------------
    def iter__attrs(self, attr_level: AttrLevel = AttrLevel.NOT_PRIVATE) -> Iterable[str]:
        for name in self.iter__external_not_builtin():
            if attr_level == AttrLevel.NOT_PRIVATE:
                if not name.startswith("__"):
                    yield name

            elif attr_level == AttrLevel.NOT_HIDDEN:
                if not name.startswith("_"):
                    yield name

            elif attr_level == AttrLevel.PRIVATE:
                if name.startswith("__"):
                    yield name

            elif attr_level == AttrLevel.ALL:
                yield name

            else:
                raise Exx__Incompatible(f"{attr_level=}")

    def iter__not_hidden(self) -> Iterable[str]:
        """
        NOTE
        ----
        hidden names are more simple to detect then private!
        cause of private methods(!) changes to "_<ClsName><__MethName>"
        """
        return self.iter__attrs(AttrLevel.NOT_HIDDEN)

    def iter__not_private(self) -> Iterable[str]:
        """
        NOTE
        ----
        BEST WAY TO USE EXACTLY iter__not_private
        """
        return self.iter__attrs(AttrLevel.NOT_PRIVATE)

    def iter__private(self) -> Iterable[str]:
        """
        BUILTIN - NOT INCLUDED!

        NOTE
        ----
        BEST WAY TO USE EXACTLY iter__not_private

        GOAL
        ----
        collect all privates in original names! without ClassName-Prefix

        BEST IDEA
        ---------
        keep list of iters
        """
        return self.iter__attrs(AttrLevel.PRIVATE)


    # def __iter__(self):     # DONT USE IT! USE DIRECT METHODS
    #     yield from self.iter__not_hidden()

    # =================================================================================================================
    pass

    # NAME ------------------------------------------------------------------------------------------------------------
    def anycase__name_original(self, name: str) -> str | None:
        """
        get attr name in original register
        """
        if not isinstance(name, str):
            return

        name = str(name).strip()
        if not name:
            return

        for name_original in self.iter__external_not_builtin():
            if name_original.lower() == name.lower():
                return name_original

        return

    def anycase__check_exists(self, name: str) -> bool:
        return self.anycase__name_original(name) is not None

    # ATTR ------------------------------------------------------------------------------------------------------------
    def anycase__getattr(self, name: str) -> Any | Callable | NoReturn:
        """
        GOAL
        ----
        get attr value by name in any register
        no execution/resolving! return pure value as represented in object!
        """
        name_original = self.anycase__name_original(name)
        if name_original is None:
            raise AttributeError(name)

        value = getattr(self.SOURCE, name_original)
        return value

    def anycase__setattr(self, name: str, value: Any) -> None | NoReturn:
        """
        get attr value by name in any register
        no execution! return pure value as represented in object!

        NoReturn - in case of not accepted names when setattr
        """
        if not isinstance(name, str):
            raise TypeError(name)

        name = name.strip()
        if name in ["", ]:
            raise AttributeError(name)

        name_original = self.anycase__name_original(name)
        if name_original is None:
            name_original = name

        # NOTE: you still have no exx with setattr(self.SOURCE, "    HELLO", value) and ""
        setattr(self.SOURCE, name_original, value)

    def anycase__delattr(self, name: str) -> None:
        name_original = self.anycase__name_original(name)
        if name_original is None:
            return      # already not exists

        delattr(self.SOURCE, name_original)

    # ITEM ------------------------------------------------------------------------------------------------------------
    def anycase__getitem(self, name: str) -> Any | Callable | NoReturn:
        return self.anycase__getattr(name)

    def anycase__setitem(self, name: str, value: Any) -> None | NoReturn:
        self.anycase__setattr(name, value)

    def anycase__delitem(self, name: str) -> None:
        self.anycase__delattr(name)

    # =================================================================================================================
    def getattr__callable_resolve(self, name: str, callables_resolve: CallableResolve = CallableResolve.DIRECT) -> Any | Callable | CallableResolve | NoReturn:
        """
        SAME AS
        -------
        CallableAux(*).resolve_*

        WHY NOT-1=CallableAux(*).resolve_*
        ----------------------------------
        it is really the same, BUT
        1. additional try for properties (could be raised without calling)
        2. cant use here cause of Circular import accused
        """
        # resolve property --------------
        # result_property = CallableAux(getattr).resolve(callables_resolve, self.SOURCE, realname)
        # TypeAux

        try:
            value = self.anycase__getattr(name)
        except Exception as exx:
            if callables_resolve == CallableResolve.SKIP_RAISED:
                return ProcessState.SKIPPED
            elif callables_resolve == CallableResolve.EXX:
                return exx
            elif callables_resolve == CallableResolve.RAISE_AS_NONE:
                return None
            elif callables_resolve == CallableResolve.RAISE:
                raise exx
            elif callables_resolve == CallableResolve.BOOL:
                return False
            else:
                raise exx

        # resolve callables ------------------
        result = CallableAux(value).resolve(callables_resolve)
        return result

    # =================================================================================================================
    def load__by_dict(self, other: dict[str, Any], only_existed: bool = None) -> Any | AttrsDump:
        """
        MAIN ITEA
        ----------
        LOAD MEANS basically setup final values for final not callables values!
        but you can use any types for your own!
        expected you know what you do and do exactly ready to use final values/not callables in otherObj!

        NOTE
        ----
        1/ dont use callables_resolve here
        2/ dont add any TEMPLATES!!! its responsibility for DictAux! use it by yourself!!!
        """
        # work ----------
        for key, value in other.items():
            if only_existed and not self.anycase__check_exists(key):
                continue
            self.anycase__setattr(key, value)

        return self.SOURCE

    # DUMP ------------------------------------------------------------------------------------------------------------
    def dump_dict(self, callables_resolve: CallableResolve = CallableResolve.EXX) -> dict[str, Any | Callable | Exception] | NoReturn:
        """
        MAIN IDEA
        ----------
        BUMPS MEANS basically save final values for all (even any dynamic/callables) values! or only not callables!

        NOTE
        ----
        DUMP WITHOUT PRIVATE NAMES

        GOAL
        ----
        make a dict from any object from aux_attr (not hidden)

        SPECIALLY CREATED FOR
        ---------------------
        using any object as rules for Translator
        """
        result = {}
        for name in self.iter__not_private():
            value = self.getattr__callable_resolve(name=name, callables_resolve=callables_resolve)
            if value == ProcessState.SKIPPED:
                continue
            result.update({name: value})

        return result

    def dump_dict__resolve_exx(self) -> dict[str, Any | Exception]:
        """
        MAIN DERIVATIVE!
        """
        return self.dump_dict(CallableResolve.EXX)

    def dump_dict__direct(self) -> TYPING.KWARGS_FINAL:
        return self.dump_dict(CallableResolve.DIRECT)

    def dump_dict__skip_callables(self) -> TYPING.KWARGS_FINAL:
        return self.dump_dict(CallableResolve.SKIP_CALLABLE)

    def dump_dict__skip_raised(self) -> dict[str, Any] | NoReturn:
        return self.dump_dict(CallableResolve.RAISE)

    # -----------------------------------------------------------------------------------------------------------------
    def dump_obj(self, callables_resolve: CallableResolve = CallableResolve.EXX) -> AttrsDump | NoReturn:
        data = self.dump_dict(callables_resolve)
        obj = AttrAux().load__by_dict(data)
        return obj

    # -----------------------------------------------------------------------------------------------------------------
    def dump__pretty_str(self) -> str:
        result = f"{self.SOURCE.__class__.__name__}(Attributes):"
        for key, value in self.dump_dict(CallableResolve.EXX).items():
            result += f"\n\t{key}={value}"
        else:
            result += f"\nEmpty=Empty"

        return result


# =====================================================================================================================
