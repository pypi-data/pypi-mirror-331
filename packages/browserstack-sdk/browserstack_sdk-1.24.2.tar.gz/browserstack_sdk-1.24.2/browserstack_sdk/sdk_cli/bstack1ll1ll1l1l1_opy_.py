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
from browserstack_sdk.sdk_cli.bstack1llll11111l_opy_ import bstack1111111l1l_opy_
from browserstack_sdk.sdk_cli.bstack1111ll1l11_opy_ import (
    bstack1111ll111l_opy_,
    bstack1111l1l1l1_opy_,
    bstack1111llll1l_opy_,
    bstack1111l11l1l_opy_,
)
from browserstack_sdk.sdk_cli.bstack1111111lll_opy_ import bstack1llllllll1l_opy_
from browserstack_sdk.sdk_cli.bstack1111l11lll_opy_ import bstack111l11111l_opy_
from typing import Tuple, Dict, Any, List, Callable
from browserstack_sdk.sdk_cli.bstack1llll11111l_opy_ import bstack1111111l1l_opy_
import weakref
class bstack1ll1ll111ll_opy_(bstack1111111l1l_opy_):
    bstack1ll1ll11lll_opy_: str
    frameworks: List[str]
    drivers: Dict[str, Tuple[Callable, bstack1111l11l1l_opy_]]
    def __init__(self, bstack1ll1ll11lll_opy_: str, frameworks: List[str]):
        super().__init__()
        self.drivers = dict()
        self.bstack1ll1ll11ll1_opy_ = dict()
        self.bstack1ll1ll11lll_opy_ = bstack1ll1ll11lll_opy_
        self.frameworks = frameworks
        if any(bstack1llllllll1l_opy_.NAME in f.lower().strip() for f in frameworks):
            bstack1llllllll1l_opy_.bstack1lll11llll1_opy_(
                (bstack1111ll111l_opy_.bstack1111l1l11l_opy_, bstack1111l1l1l1_opy_.PRE), self.__1ll1ll1l1ll_opy_
            )
            bstack1llllllll1l_opy_.bstack1lll11llll1_opy_(
                (bstack1111ll111l_opy_.QUIT, bstack1111l1l1l1_opy_.POST), self.__1ll1ll11l1l_opy_
            )
    def __1ll1ll1l1ll_opy_(
        self,
        f: bstack1llllllll1l_opy_,
        driver: object,
        exec: Tuple[bstack1111l11l1l_opy_, str],
        bstack111l111l1l_opy_: Tuple[bstack1111ll111l_opy_, bstack1111l1l1l1_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
        instance, _ = exec
        if instance.ref() in self.drivers or bstack1111llll1l_opy_.bstack111l111111_opy_(instance, self.bstack1ll1ll11lll_opy_, False):
            return
        if not f.bstack1ll1lll1lll_opy_(f.hub_url(driver)):
            self.bstack1ll1ll11ll1_opy_[instance.ref()] = weakref.ref(driver), instance
            bstack1111llll1l_opy_.bstack1111l11l11_opy_(instance, self.bstack1ll1ll11lll_opy_, True)
            self.logger.debug(bstack11l1ll1_opy_ (u"ࠢࡠࡡࡲࡲࡤࡹࡥ࡭ࡧࡱ࡭ࡺࡳ࡟ࡪࡰ࡬ࡸ࠿ࠦ࡮ࡰࡰࡢࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡡࡧࡶ࡮ࡼࡥࡳࠢ࡬ࡲࡸࡺࡡ࡯ࡥࡨࡁࠧᅖ") + str(instance.ref()) + bstack11l1ll1_opy_ (u"ࠣࠤᅗ"))
            return
        self.drivers[instance.ref()] = weakref.ref(driver), instance
        bstack1111llll1l_opy_.bstack1111l11l11_opy_(instance, self.bstack1ll1ll11lll_opy_, True)
        self.logger.debug(bstack11l1ll1_opy_ (u"ࠤࡢࡣࡴࡴ࡟ࡴࡧ࡯ࡩࡳ࡯ࡵ࡮ࡡ࡬ࡲ࡮ࡺ࠺ࠡ࡫ࡱࡷࡹࡧ࡮ࡤࡧࡀࠦᅘ") + str(instance.ref()) + bstack11l1ll1_opy_ (u"ࠥࠦᅙ"))
    def __1ll1ll11l1l_opy_(
        self,
        f: bstack1llllllll1l_opy_,
        driver: object,
        exec: Tuple[bstack1111l11l1l_opy_, str],
        bstack111l111l1l_opy_: Tuple[bstack1111ll111l_opy_, bstack1111l1l1l1_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
        instance, _ = exec
        if not instance.ref() in self.drivers:
            return
        self.bstack1ll1ll1ll11_opy_(instance)
        self.logger.debug(bstack11l1ll1_opy_ (u"ࠦࡤࡥ࡯࡯ࡡࡶࡩࡱ࡫࡮ࡪࡷࡰࡣࡶࡻࡩࡵ࠼ࠣ࡭ࡳࡹࡴࡢࡰࡦࡩࡂࠨᅚ") + str(instance.ref()) + bstack11l1ll1_opy_ (u"ࠧࠨᅛ"))
    def bstack1ll1ll1l11l_opy_(self, context: bstack111l11111l_opy_, reverse=True) -> List[Tuple[Callable, bstack1111l11l1l_opy_]]:
        matches = []
        for data in self.drivers.values():
            if (
                bstack1llllllll1l_opy_.bstack1lll111ll1l_opy_(data[1])
                and data[1].bstack1ll1ll1l111_opy_(context)
                and getattr(data[0](), bstack11l1ll1_opy_ (u"ࠨࡳࡦࡵࡶ࡭ࡴࡴ࡟ࡪࡦࠥᅜ"), False)
            ):
                matches.append(data)
        return sorted(matches, key=lambda d: d[1].bstack1111llll11_opy_, reverse=reverse)
    def bstack1ll1ll111l1_opy_(self, context: bstack111l11111l_opy_, reverse=True) -> List[Tuple[Callable, bstack1111l11l1l_opy_]]:
        matches = []
        for data in self.bstack1ll1ll11ll1_opy_.values():
            if (
                data[1].bstack1ll1ll1l111_opy_(context)
                and getattr(data[0](), bstack11l1ll1_opy_ (u"ࠢࡴࡧࡶࡷ࡮ࡵ࡮ࡠ࡫ࡧࠦᅝ"), False)
            ):
                matches.append(data)
        return sorted(matches, key=lambda d: d[1].bstack1111llll11_opy_, reverse=reverse)
    def bstack1ll1ll11l11_opy_(self, instance: bstack1111l11l1l_opy_) -> bool:
        return instance and instance.ref() in self.drivers
    def bstack1ll1ll1ll11_opy_(self, instance: bstack1111l11l1l_opy_) -> bool:
        if self.bstack1ll1ll11l11_opy_(instance):
            self.drivers.pop(instance.ref())
            bstack1111llll1l_opy_.bstack1111l11l11_opy_(instance, self.bstack1ll1ll11lll_opy_, False)
            return True
        return False