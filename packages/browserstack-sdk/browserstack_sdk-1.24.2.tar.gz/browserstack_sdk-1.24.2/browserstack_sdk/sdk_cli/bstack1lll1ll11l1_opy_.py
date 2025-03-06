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
from typing import Dict, List, Any, Callable, Tuple, Union
from browserstack_sdk import sdk_pb2 as structs
from browserstack_sdk.sdk_cli.bstack1llll11111l_opy_ import bstack1111111l1l_opy_
from browserstack_sdk.sdk_cli.bstack1111ll1l11_opy_ import (
    bstack1111ll111l_opy_,
    bstack1111l1l1l1_opy_,
    bstack1111l11l1l_opy_,
)
from bstack_utils.helper import  bstack1ll1l1lll_opy_
from browserstack_sdk.sdk_cli.bstack1111111lll_opy_ import bstack1llllllll1l_opy_
from browserstack_sdk.sdk_cli.test_framework import TestFramework, bstack1llll11llll_opy_, bstack11111l1l11_opy_, bstack1lll1llll11_opy_, bstack1llll111ll1_opy_
from typing import Tuple, Any
import threading
from bstack_utils.bstack111l1ll1_opy_ import bstack1ll1l1ll11_opy_
from browserstack_sdk.sdk_cli.bstack1lllll1l1l1_opy_ import bstack1llll111l11_opy_
from bstack_utils.percy import bstack111l1l11l_opy_
from bstack_utils.percy_sdk import PercySDK
from bstack_utils.constants import *
import re
class bstack1lll1lllll1_opy_(bstack1111111l1l_opy_):
    def __init__(self, bstack1ll11l11111_opy_: Dict[str, str]):
        super().__init__()
        self.bstack1ll11l11111_opy_ = bstack1ll11l11111_opy_
        self.percy = bstack111l1l11l_opy_()
        self.bstack111ll11ll_opy_ = bstack1ll1l1ll11_opy_()
        self.bstack1ll111llll1_opy_()
        bstack1llllllll1l_opy_.bstack1lll11llll1_opy_((bstack1111ll111l_opy_.bstack1111l1l11l_opy_, bstack1111l1l1l1_opy_.PRE), self.bstack1ll111lll1l_opy_)
        TestFramework.bstack1lll11llll1_opy_((bstack1llll11llll_opy_.TEST, bstack1lll1llll11_opy_.POST), self.bstack1ll1llll11l_opy_)
    def is_enabled(self) -> bool:
        return True
    def bstack1ll11ll1111_opy_(self, instance: bstack1111l11l1l_opy_, driver: object):
        bstack1ll1l11ll11_opy_ = TestFramework.bstack1111lll1ll_opy_(instance.context)
        for t in bstack1ll1l11ll11_opy_:
            bstack1lll1111l11_opy_ = TestFramework.bstack111l111111_opy_(t, bstack1llll111l11_opy_.bstack1lll1l11ll1_opy_, [])
            if any(instance is d[1] for d in bstack1lll1111l11_opy_) or instance == driver:
                return t
    def bstack1ll111lll1l_opy_(
        self,
        f: bstack1llllllll1l_opy_,
        driver: object,
        exec: Tuple[bstack1111l11l1l_opy_, str],
        bstack111l111l1l_opy_: Tuple[bstack1111ll111l_opy_, bstack1111l1l1l1_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
        try:
            instance, method_name = exec
            if not bstack1llllllll1l_opy_.bstack1lll111lll1_opy_(method_name):
                return
            platform_index = f.bstack111l111111_opy_(instance, bstack1llllllll1l_opy_.bstack1lll11ll1l1_opy_, 0)
            bstack1ll1l1l111l_opy_ = self.bstack1ll11ll1111_opy_(instance, driver)
            bstack1ll11l11ll1_opy_ = TestFramework.bstack111l111111_opy_(bstack1ll1l1l111l_opy_, TestFramework.bstack1ll11l11l1l_opy_, None)
            if not bstack1ll11l11ll1_opy_:
                self.logger.debug(bstack11l1ll1_opy_ (u"ࠦࡴࡴ࡟ࡱࡴࡨࡣࡪࡾࡥࡤࡷࡷࡩ࠿ࠦࡲࡦࡶࡸࡶࡳ࡯࡮ࡨࠢࡤࡷࠥࡹࡥࡴࡵ࡬ࡳࡳࠦࡩࡴࠢࡱࡳࡹࠦࡹࡦࡶࠣࡷࡹࡧࡲࡵࡧࡧࠦᇑ"))
                return
            driver_command = f.bstack1lll11l11ll_opy_(*args)
            for command in bstack1l1l1111l_opy_:
                if command == driver_command:
                    self.bstack1lllllll1_opy_(driver, platform_index)
            bstack1ll1lll1l1_opy_ = self.percy.bstack111llll1l_opy_()
            if driver_command in bstack11lll11111_opy_[bstack1ll1lll1l1_opy_]:
                self.bstack111ll11ll_opy_.bstack11lllll111_opy_(bstack1ll11l11ll1_opy_, driver_command)
        except Exception as e:
            self.logger.error(bstack11l1ll1_opy_ (u"ࠧࡵ࡮ࡠࡲࡵࡩࡤ࡫ࡸࡦࡥࡸࡸࡪࡀࠠࡦࡴࡵࡳࡷࠨᇒ"), e)
    def bstack1ll1llll11l_opy_(
        self,
        f: TestFramework,
        instance: bstack11111l1l11_opy_,
        bstack111l111l1l_opy_: Tuple[bstack1llll11llll_opy_, bstack1lll1llll11_opy_],
        *args,
        **kwargs,
    ):
        from bstack_utils.bstack1ll111ll1l_opy_ import bstack1llll111lll_opy_
        bstack1lll1111l11_opy_ = f.bstack111l111111_opy_(instance, bstack1llll111l11_opy_.bstack1lll1l11ll1_opy_, [])
        if not bstack1lll1111l11_opy_:
            self.logger.debug(bstack11l1ll1_opy_ (u"ࠨ࡯࡯ࡡࡤࡪࡹ࡫ࡲࡠࡶࡨࡷࡹࡀࠠ࡯ࡱࠣࡨࡷ࡯ࡶࡦࡴࡶࠤ࡫ࡵࡲࠡࡪࡲࡳࡰࡥࡩ࡯ࡨࡲࡁࢀ࡮࡯ࡰ࡭ࡢ࡭ࡳ࡬࡯ࡾࠢࡤࡶ࡬ࡹ࠽ࡼࡣࡵ࡫ࡸࢃࠠ࡬ࡹࡤࡶ࡬ࡹ࠽ࠣᇓ") + str(kwargs) + bstack11l1ll1_opy_ (u"ࠢࠣᇔ"))
            return
        if len(bstack1lll1111l11_opy_) > 1:
            self.logger.debug(bstack11l1ll1_opy_ (u"ࠣࡱࡱࡣࡦ࡬ࡴࡦࡴࡢࡸࡪࡹࡴ࠻ࠢࡾࡰࡪࡴࠨࡥࡴ࡬ࡺࡪࡸ࡟ࡪࡰࡶࡸࡦࡴࡣࡦࡵࠬࢁࠥࡪࡲࡪࡸࡨࡶࡸࠦࡦࡰࡴࠣ࡬ࡴࡵ࡫ࡠ࡫ࡱࡪࡴࡃࡻࡩࡱࡲ࡯ࡤ࡯࡮ࡧࡱࢀࠤࡦࡸࡧࡴ࠿ࡾࡥࡷ࡭ࡳࡾࠢ࡮ࡻࡦࡸࡧࡴ࠿ࠥᇕ") + str(kwargs) + bstack11l1ll1_opy_ (u"ࠤࠥᇖ"))
        bstack1lll11lll1l_opy_, bstack1lll111l111_opy_ = bstack1lll1111l11_opy_[0]
        driver = bstack1lll11lll1l_opy_()
        if not driver:
            self.logger.debug(bstack11l1ll1_opy_ (u"ࠥࡳࡳࡥࡡࡧࡶࡨࡶࡤࡺࡥࡴࡶ࠽ࠤࡳࡵࠠࡥࡴ࡬ࡺࡪࡸࠠࡧࡱࡵࠤ࡭ࡵ࡯࡬ࡡ࡬ࡲ࡫ࡵ࠽ࡼࡪࡲࡳࡰࡥࡩ࡯ࡨࡲࢁࠥࡧࡲࡨࡵࡀࡿࡦࡸࡧࡴࡿࠣ࡯ࡼࡧࡲࡨࡵࡀࠦᇗ") + str(kwargs) + bstack11l1ll1_opy_ (u"ࠦࠧᇘ"))
            return
        bstack1ll11l1111l_opy_ = {
            TestFramework.bstack1lll11ll111_opy_: bstack11l1ll1_opy_ (u"ࠧࡺࡥࡴࡶࠣࡲࡦࡳࡥࠣᇙ"),
            TestFramework.bstack1lll111l1l1_opy_: bstack11l1ll1_opy_ (u"ࠨࡴࡦࡵࡷࠤࡺࡻࡩࡥࠤᇚ"),
            TestFramework.bstack1ll11l11l1l_opy_: bstack11l1ll1_opy_ (u"ࠢࡵࡧࡶࡸࠥࡸࡥࡳࡷࡱࠤࡳࡧ࡭ࡦࠤᇛ")
        }
        bstack1ll111lllll_opy_ = { key: f.bstack111l111111_opy_(instance, key) for key in bstack1ll11l1111l_opy_ }
        bstack1ll11l11lll_opy_ = [key for key, value in bstack1ll111lllll_opy_.items() if not value]
        if bstack1ll11l11lll_opy_:
            for key in bstack1ll11l11lll_opy_:
                self.logger.debug(bstack11l1ll1_opy_ (u"ࠣࡱࡱࡣࡦ࡬ࡴࡦࡴࡢࡸࡪࡹࡴ࠻ࠢࡰ࡭ࡸࡹࡩ࡯ࡩࠣࠦᇜ") + str(key) + bstack11l1ll1_opy_ (u"ࠤࠥᇝ"))
            return
        platform_index = f.bstack111l111111_opy_(instance, bstack1llllllll1l_opy_.bstack1lll11ll1l1_opy_, 0)
        if self.bstack1ll11l11111_opy_.percy_capture_mode == bstack11l1ll1_opy_ (u"ࠥࡸࡪࡹࡴࡤࡣࡶࡩࠧᇞ"):
            bstack1llll1llll_opy_ = bstack1ll111lllll_opy_.get(TestFramework.bstack1ll11l11l1l_opy_) + bstack11l1ll1_opy_ (u"ࠦ࠲ࡺࡥࡴࡶࡦࡥࡸ࡫ࠢᇟ")
            bstack1lll11l1l1l_opy_ = bstack1llll111lll_opy_.bstack1lll11l1111_opy_(EVENTS.bstack1ll11l11l11_opy_.value)
            PercySDK.screenshot(
                driver,
                bstack1llll1llll_opy_,
                bstack1llll1l11l_opy_=bstack1ll111lllll_opy_[TestFramework.bstack1lll11ll111_opy_],
                bstack111l1ll11_opy_=bstack1ll111lllll_opy_[TestFramework.bstack1lll111l1l1_opy_],
                bstack1l1lll1ll1_opy_=platform_index
            )
            bstack1llll111lll_opy_.end(EVENTS.bstack1ll11l11l11_opy_.value, bstack1lll11l1l1l_opy_+bstack11l1ll1_opy_ (u"ࠧࡀࡳࡵࡣࡵࡸࠧᇠ"), bstack1lll11l1l1l_opy_+bstack11l1ll1_opy_ (u"ࠨ࠺ࡦࡰࡧࠦᇡ"), True, None, None, None, None, test_name=bstack1llll1llll_opy_)
    def bstack1lllllll1_opy_(self, driver, platform_index):
        if self.bstack111ll11ll_opy_.bstack1ll1l111_opy_() is True or self.bstack111ll11ll_opy_.capturing() is True:
            return
        self.bstack111ll11ll_opy_.bstack11llll111l_opy_()
        while not self.bstack111ll11ll_opy_.bstack1ll1l111_opy_():
            bstack1ll11l11ll1_opy_ = self.bstack111ll11ll_opy_.bstack1ll11llll1_opy_()
            self.bstack1l111l1lll_opy_(driver, bstack1ll11l11ll1_opy_, platform_index)
        self.bstack111ll11ll_opy_.bstack1l1l111111_opy_()
    def bstack1l111l1lll_opy_(self, driver, bstack11l11lll1_opy_, platform_index, test=None):
        from bstack_utils.bstack1ll111ll1l_opy_ import bstack1llll111lll_opy_
        bstack1lll11l1l1l_opy_ = bstack1llll111lll_opy_.bstack1lll11l1111_opy_(EVENTS.bstack1l11l11l11_opy_.value)
        if test != None:
            bstack1llll1l11l_opy_ = getattr(test, bstack11l1ll1_opy_ (u"ࠧ࡯ࡣࡰࡩࠬᇢ"), None)
            bstack111l1ll11_opy_ = getattr(test, bstack11l1ll1_opy_ (u"ࠨࡷࡸ࡭ࡩ࠭ᇣ"), None)
            PercySDK.screenshot(driver, bstack11l11lll1_opy_, bstack1llll1l11l_opy_=bstack1llll1l11l_opy_, bstack111l1ll11_opy_=bstack111l1ll11_opy_, bstack1l1lll1ll1_opy_=platform_index)
        else:
            PercySDK.screenshot(driver, bstack11l11lll1_opy_)
        bstack1llll111lll_opy_.end(EVENTS.bstack1l11l11l11_opy_.value, bstack1lll11l1l1l_opy_+bstack11l1ll1_opy_ (u"ࠤ࠽ࡷࡹࡧࡲࡵࠤᇤ"), bstack1lll11l1l1l_opy_+bstack11l1ll1_opy_ (u"ࠥ࠾ࡪࡴࡤࠣᇥ"), True, None, None, None, None, test_name=bstack11l11lll1_opy_)
    def bstack1ll111llll1_opy_(self):
        os.environ[bstack11l1ll1_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡔࡊࡘࡃ࡚ࠩᇦ")] = str(self.bstack1ll11l11111_opy_.success)
        os.environ[bstack11l1ll1_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡕࡋࡒࡄ࡛ࡢࡇࡆࡖࡔࡖࡔࡈࡣࡒࡕࡄࡆࠩᇧ")] = str(self.bstack1ll11l11111_opy_.percy_capture_mode)
        self.percy.bstack1ll11l111l1_opy_(self.bstack1ll11l11111_opy_.is_percy_auto_enabled)
        self.percy.bstack1ll11l111ll_opy_(self.bstack1ll11l11111_opy_.percy_build_id)