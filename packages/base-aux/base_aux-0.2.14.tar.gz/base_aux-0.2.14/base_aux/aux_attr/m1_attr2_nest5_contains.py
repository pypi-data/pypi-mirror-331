from typing import *

from base_aux.aux_attr.m2_annot1_aux import *


# =====================================================================================================================
class NestContains_AttrIC:
    """
    GOAL
    ----
    apply str/repr for show attrs names+values

    CAREFUL
    -------
    dont use in Nest* classes - it can used only in FINALs!!! cause it can have same or meaning is not appropriate!
    """
    def __contains__(self, item):
        return AttrAux(self).anycase__check_exists(item)


# =====================================================================================================================
