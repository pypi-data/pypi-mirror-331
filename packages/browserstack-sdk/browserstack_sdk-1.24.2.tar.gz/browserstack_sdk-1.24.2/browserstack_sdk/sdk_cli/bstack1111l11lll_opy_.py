# coding: UTF-8
import sys
bstack1111_opy_ = sys.version_info [0] == 2
bstack111_opy_ = 2048
bstack1lll11_opy_ = 7
def bstack11l1ll1_opy_ (bstack111lll_opy_):
    global bstack11ll_opy_
    bstack1l11lll_opy_ = ord (bstack111lll_opy_ [-1])
    bstack11111_opy_ = bstack111lll_opy_ [:-1]
    bstack111ll11_opy_ = bstack1l11lll_opy_ % len (bstack11111_opy_)
    bstack1l1l11_opy_ = bstack11111_opy_ [:bstack111ll11_opy_] + bstack11111_opy_ [bstack111ll11_opy_:]
    if bstack1111_opy_:
        bstack1ll11ll_opy_ = unicode () .join ([unichr (ord (char) - bstack111_opy_ - (bstack111l1l1_opy_ + bstack1l11lll_opy_) % bstack1lll11_opy_) for bstack111l1l1_opy_, char in enumerate (bstack1l1l11_opy_)])
    else:
        bstack1ll11ll_opy_ = str () .join ([chr (ord (char) - bstack111_opy_ - (bstack111l1l1_opy_ + bstack1l11lll_opy_) % bstack1lll11_opy_) for bstack111l1l1_opy_, char in enumerate (bstack1l1l11_opy_)])
    return eval (bstack1ll11ll_opy_)
import os
import threading
import os
from typing import Dict, Any
from dataclasses import dataclass
from collections import defaultdict
from datetime import timedelta
@dataclass
class bstack111l11111l_opy_:
    id: str
    hash: str
    thread_id: int
    process_id: int
    type: str
class bstack1111l1lll1_opy_:
    bstack1l1l111ll11_opy_ = bstack11l1ll1_opy_ (u"ࠨࡢࡦࡰࡦ࡬ࡲࡧࡲ࡬ࠤᏒ")
    context: bstack111l11111l_opy_
    data: Dict[str, Any]
    platform_index: int
    def __init__(self, context: bstack111l11111l_opy_):
        self.context = context
        self.data = dict({bstack1111l1lll1_opy_.bstack1l1l111ll11_opy_: defaultdict(lambda: timedelta(microseconds=0))})
        self.platform_index = int(os.environ.get(bstack11l1ll1_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡐࡍࡃࡗࡊࡔࡘࡍࡠࡋࡑࡈࡊ࡞ࠧᏓ"), bstack11l1ll1_opy_ (u"ࠨ࠲ࠪᏔ")))
    def ref(self) -> str:
        return str(self.context.id)
    def bstack1111lll111_opy_(self, target: object):
        return bstack1111l1lll1_opy_.create_context(target) == self.context
    def bstack1ll1ll1l111_opy_(self, context: bstack111l11111l_opy_):
        return context and context.thread_id == self.context.thread_id and context.process_id == self.context.process_id
    def bstack111l11l1_opy_(self, key: str, value: timedelta):
        self.data[bstack1111l1lll1_opy_.bstack1l1l111ll11_opy_][key] += value
    def bstack1lllll1llll_opy_(self) -> dict:
        return self.data[bstack1111l1lll1_opy_.bstack1l1l111ll11_opy_]
    @staticmethod
    def create_context(
        target: object,
        thread_id=threading.get_ident(),
        process_id=os.getpid(),
    ):
        return bstack111l11111l_opy_(
            id=id(target),
            hash=hash(target),
            thread_id=thread_id,
            process_id=process_id,
            type=type(target),
        )