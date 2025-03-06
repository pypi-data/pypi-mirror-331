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
import json
from browserstack_sdk.sdk_cli.bstack1111ll1l11_opy_ import (
    bstack1111ll111l_opy_,
    bstack1111l1l1l1_opy_,
    bstack1111l11l1l_opy_,
    bstack111l11111l_opy_,
)
from browserstack_sdk.sdk_cli.bstack1111111lll_opy_ import bstack1llllllll1l_opy_
from browserstack_sdk.sdk_cli.test_framework import TestFramework, bstack1llll11llll_opy_, bstack1lll1llll11_opy_, bstack11111l1l11_opy_
from browserstack_sdk.sdk_cli.bstack1ll1ll1l1l1_opy_ import bstack1ll1ll111ll_opy_
from bstack_utils.measure import measure
from bstack_utils.constants import *
from typing import Tuple, List, Any
class bstack1llll111l11_opy_(bstack1ll1ll111ll_opy_):
    bstack1l1lllll1l1_opy_ = bstack11l1ll1_opy_ (u"ࠣࡶࡨࡷࡹࡥࡤࡳ࡫ࡹࡩࡷࡹࠢሷ")
    bstack1lll1l11ll1_opy_ = bstack11l1ll1_opy_ (u"ࠤࡤࡹࡹࡵ࡭ࡢࡶ࡬ࡳࡳࡥࡳࡦࡵࡶ࡭ࡴࡴࡳࠣሸ")
    bstack1ll11lll1ll_opy_ = bstack11l1ll1_opy_ (u"ࠥࡲࡴࡴ࡟ࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡥࡡࡶࡶࡲࡱࡦࡺࡩࡰࡰࡢࡷࡪࡹࡳࡪࡱࡱࡷࠧሹ")
    bstack1l1llll1lll_opy_ = bstack11l1ll1_opy_ (u"ࠦࡹ࡫ࡳࡵࡡࡶࡩࡸࡹࡩࡰࡰࡶࠦሺ")
    bstack1l1lll1llll_opy_ = bstack11l1ll1_opy_ (u"ࠧࡧࡵࡵࡱࡰࡥࡹ࡯࡯࡯ࡡ࡬ࡲࡸࡺࡡ࡯ࡥࡨࡣࡷ࡫ࡦࡴࠤሻ")
    bstack1ll1l1ll1ll_opy_ = bstack11l1ll1_opy_ (u"ࠨࡣࡣࡶࡢࡷࡪࡹࡳࡪࡱࡱࡣࡨࡸࡥࡢࡶࡨࡨࠧሼ")
    bstack1l1llll1ll1_opy_ = bstack11l1ll1_opy_ (u"ࠢࡤࡤࡷࡣࡸ࡫ࡳࡴ࡫ࡲࡲࡤࡴࡡ࡮ࡧࠥሽ")
    bstack1l1lllll1ll_opy_ = bstack11l1ll1_opy_ (u"ࠣࡥࡥࡸࡤࡹࡥࡴࡵ࡬ࡳࡳࡥࡳࡵࡣࡷࡹࡸࠨሾ")
    def __init__(self):
        super().__init__(bstack1ll1ll11lll_opy_=self.bstack1l1lllll1l1_opy_, frameworks=[bstack1llllllll1l_opy_.NAME])
        if not self.is_enabled():
            return
        TestFramework.bstack1lll11llll1_opy_((bstack1llll11llll_opy_.BEFORE_EACH, bstack1lll1llll11_opy_.POST), self.bstack1l1llll1111_opy_)
        TestFramework.bstack1lll11llll1_opy_((bstack1llll11llll_opy_.TEST, bstack1lll1llll11_opy_.PRE), self.bstack1lll11l1lll_opy_)
        TestFramework.bstack1lll11llll1_opy_((bstack1llll11llll_opy_.TEST, bstack1lll1llll11_opy_.POST), self.bstack1ll1llll11l_opy_)
    def is_enabled(self) -> bool:
        return True
    def bstack1l1llll1111_opy_(
        self,
        f: TestFramework,
        instance: bstack11111l1l11_opy_,
        bstack111l111l1l_opy_: Tuple[bstack1llll11llll_opy_, bstack1lll1llll11_opy_],
        *args,
        **kwargs,
    ):
        bstack1lll1111l11_opy_ = self.bstack1l1lll1l1l1_opy_(instance.context)
        if not bstack1lll1111l11_opy_:
            self.logger.debug(bstack11l1ll1_opy_ (u"ࠤࡶࡩࡹࡥࡡࡤࡶ࡬ࡺࡪࡥࡤࡳ࡫ࡹࡩࡷࡹ࠺ࠡࡰࡲࠤࡩࡸࡩࡷࡧࡵࠤ࡫ࡵࡲࠡࡪࡲࡳࡰࡥࡩ࡯ࡨࡲࡁࠧሿ") + str(bstack111l111l1l_opy_) + bstack11l1ll1_opy_ (u"ࠥࠦቀ"))
        f.bstack1111l11l11_opy_(instance, bstack1llll111l11_opy_.bstack1lll1l11ll1_opy_, bstack1lll1111l11_opy_)
        bstack1l1llll111l_opy_ = self.bstack1l1lll1l1l1_opy_(instance.context, bstack1l1llll11l1_opy_=False)
        f.bstack1111l11l11_opy_(instance, bstack1llll111l11_opy_.bstack1ll11lll1ll_opy_, bstack1l1llll111l_opy_)
    def bstack1lll11l1lll_opy_(
        self,
        f: TestFramework,
        instance: bstack11111l1l11_opy_,
        bstack111l111l1l_opy_: Tuple[bstack1llll11llll_opy_, bstack1lll1llll11_opy_],
        *args,
        **kwargs,
    ):
        self.bstack1l1llll1111_opy_(f, instance, bstack111l111l1l_opy_, *args, **kwargs)
        if not f.bstack111l111111_opy_(instance, bstack1llll111l11_opy_.bstack1l1llll1ll1_opy_, False):
            self.__1l1lll1ll1l_opy_(f,instance,bstack111l111l1l_opy_)
    def bstack1ll1llll11l_opy_(
        self,
        f: TestFramework,
        instance: bstack11111l1l11_opy_,
        bstack111l111l1l_opy_: Tuple[bstack1llll11llll_opy_, bstack1lll1llll11_opy_],
        *args,
        **kwargs,
    ):
        self.bstack1l1llll1111_opy_(f, instance, bstack111l111l1l_opy_, *args, **kwargs)
        if not f.bstack111l111111_opy_(instance, bstack1llll111l11_opy_.bstack1l1llll1ll1_opy_, False):
            self.__1l1lll1ll1l_opy_(f, instance, bstack111l111l1l_opy_)
        if not f.bstack111l111111_opy_(instance, bstack1llll111l11_opy_.bstack1l1lllll1ll_opy_, False):
            self.__1l1lll1lll1_opy_(f, instance, bstack111l111l1l_opy_)
    def bstack1l1lll1l1ll_opy_(
        self,
        f: bstack1llllllll1l_opy_,
        driver: object,
        exec: Tuple[bstack1111l11l1l_opy_, str],
        bstack111l111l1l_opy_: Tuple[bstack1111ll111l_opy_, bstack1111l1l1l1_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
        instance = exec[0]
        if not f.bstack1lll111ll1l_opy_(instance):
            return
        if f.bstack111l111111_opy_(instance, bstack1llll111l11_opy_.bstack1l1lllll1ll_opy_, False):
            return
        driver.execute_script(
            bstack11l1ll1_opy_ (u"ࠦࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡢࡩࡽ࡫ࡣࡶࡶࡲࡶ࠿ࠦࡻࡾࠤቁ").format(
                json.dumps(
                    {
                        bstack11l1ll1_opy_ (u"ࠧࡧࡣࡵ࡫ࡲࡲࠧቂ"): bstack11l1ll1_opy_ (u"ࠨࡳࡦࡶࡖࡩࡸࡹࡩࡰࡰࡖࡸࡦࡺࡵࡴࠤቃ"),
                        bstack11l1ll1_opy_ (u"ࠢࡢࡴࡪࡹࡲ࡫࡮ࡵࡵࠥቄ"): {bstack11l1ll1_opy_ (u"ࠣࡵࡷࡥࡹࡻࡳࠣቅ"): result},
                    }
                )
            )
        )
        f.bstack1111l11l11_opy_(instance, bstack1llll111l11_opy_.bstack1l1lllll1ll_opy_, True)
    def bstack1l1lll1l1l1_opy_(self, context: bstack111l11111l_opy_, bstack1l1llll11l1_opy_= True):
        if bstack1l1llll11l1_opy_:
            bstack1lll1111l11_opy_ = self.bstack1ll1ll1l11l_opy_(context, reverse=True)
        else:
            bstack1lll1111l11_opy_ = self.bstack1ll1ll111l1_opy_(context, reverse=True)
        return [f for f in bstack1lll1111l11_opy_ if f[1].state != bstack1111ll111l_opy_.QUIT]
    @measure(event_name=EVENTS.bstack1llll11lll_opy_, stage=STAGE.bstack1l1ll1llll_opy_)
    def __1l1lll1lll1_opy_(
        self,
        f: TestFramework,
        instance: bstack11111l1l11_opy_,
        bstack111l111l1l_opy_: Tuple[bstack1llll11llll_opy_, bstack1lll1llll11_opy_],
    ):
        bstack1lll1111l11_opy_ = f.bstack111l111111_opy_(instance, bstack1llll111l11_opy_.bstack1lll1l11ll1_opy_, [])
        if not bstack1lll1111l11_opy_:
            self.logger.debug(bstack11l1ll1_opy_ (u"ࠤࡶࡩࡹࡥࡡࡤࡶ࡬ࡺࡪࡥࡤࡳ࡫ࡹࡩࡷࡹ࠺ࠡࡰࡲࠤࡩࡸࡩࡷࡧࡵࠤ࡫ࡵࡲࠡࡪࡲࡳࡰࡥࡩ࡯ࡨࡲࡁࠧቆ") + str(bstack111l111l1l_opy_) + bstack11l1ll1_opy_ (u"ࠥࠦቇ"))
            return
        driver = bstack1lll1111l11_opy_[0][0]()
        status = f.bstack111l111111_opy_(instance, TestFramework.bstack1l1lll1ll11_opy_, None)
        if not status:
            self.logger.debug(bstack11l1ll1_opy_ (u"ࠦࡸ࡫ࡴࡠࡣࡦࡸ࡮ࡼࡥࡠࡦࡵ࡭ࡻ࡫ࡲࡴ࠼ࠣࡲࡴࠦࡳࡵࡣࡷࡹࡸࠦࡦࡰࡴࠣࡸࡪࡹࡴ࠭ࠢ࡫ࡳࡴࡱ࡟ࡪࡰࡩࡳࡂࠨቈ") + str(bstack111l111l1l_opy_) + bstack11l1ll1_opy_ (u"ࠧࠨ቉"))
            return
        bstack1l1lllll11l_opy_ = {bstack11l1ll1_opy_ (u"ࠨࡳࡵࡣࡷࡹࡸࠨቊ"): status.lower()}
        bstack1l1llll1l1l_opy_ = f.bstack111l111111_opy_(instance, TestFramework.bstack1l1llll11ll_opy_, None)
        if status.lower() == bstack11l1ll1_opy_ (u"ࠧࡧࡣ࡬ࡰࡪࡪࠧቋ") and bstack1l1llll1l1l_opy_ is not None:
            bstack1l1lllll11l_opy_[bstack11l1ll1_opy_ (u"ࠨࡴࡨࡥࡸࡵ࡮ࠨቌ")] = bstack1l1llll1l1l_opy_[0][bstack11l1ll1_opy_ (u"ࠩࡥࡥࡨࡱࡴࡳࡣࡦࡩࠬቍ")][0] if isinstance(bstack1l1llll1l1l_opy_, list) else str(bstack1l1llll1l1l_opy_)
        driver.execute_script(
            bstack11l1ll1_opy_ (u"ࠥࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡡࡨࡼࡪࡩࡵࡵࡱࡵ࠾ࠥࢁࡽࠣ቎").format(
                json.dumps(
                    {
                        bstack11l1ll1_opy_ (u"ࠦࡦࡩࡴࡪࡱࡱࠦ቏"): bstack11l1ll1_opy_ (u"ࠧࡹࡥࡵࡕࡨࡷࡸ࡯࡯࡯ࡕࡷࡥࡹࡻࡳࠣቐ"),
                        bstack11l1ll1_opy_ (u"ࠨࡡࡳࡩࡸࡱࡪࡴࡴࡴࠤቑ"): bstack1l1lllll11l_opy_,
                    }
                )
            )
        )
        f.bstack1111l11l11_opy_(instance, bstack1llll111l11_opy_.bstack1l1lllll1ll_opy_, True)
    @measure(event_name=EVENTS.bstack11l11111l_opy_, stage=STAGE.bstack1l1ll1llll_opy_)
    def __1l1lll1ll1l_opy_(
        self,
        f: TestFramework,
        instance: bstack11111l1l11_opy_,
        bstack111l111l1l_opy_: Tuple[bstack1llll11llll_opy_, bstack1lll1llll11_opy_]
    ):
        test_name = f.bstack111l111111_opy_(instance, TestFramework.bstack1l1llll1l11_opy_, None)
        if not test_name:
            self.logger.debug(bstack11l1ll1_opy_ (u"ࠢࡰࡰࡢࡦࡪ࡬࡯ࡳࡧࡢࡸࡪࡹࡴ࠻ࠢࡰ࡭ࡸࡹࡩ࡯ࡩࠣࡸࡪࡹࡴࠡࡰࡤࡱࡪࠨቒ"))
            return
        bstack1lll1111l11_opy_ = f.bstack111l111111_opy_(instance, bstack1llll111l11_opy_.bstack1lll1l11ll1_opy_, [])
        if not bstack1lll1111l11_opy_:
            self.logger.debug(bstack11l1ll1_opy_ (u"ࠣࡵࡨࡸࡤࡧࡣࡵ࡫ࡹࡩࡤࡪࡲࡪࡸࡨࡶࡸࡀࠠ࡯ࡱࠣࡷࡹࡧࡴࡶࡵࠣࡪࡴࡸࠠࡵࡧࡶࡸ࠱ࠦࡨࡰࡱ࡮ࡣ࡮ࡴࡦࡰ࠿ࠥቓ") + str(bstack111l111l1l_opy_) + bstack11l1ll1_opy_ (u"ࠤࠥቔ"))
            return
        for bstack1lll11lll1l_opy_, bstack1l1lllll111_opy_ in bstack1lll1111l11_opy_:
            if not bstack1llllllll1l_opy_.bstack1lll111ll1l_opy_(bstack1l1lllll111_opy_):
                continue
            driver = bstack1lll11lll1l_opy_()
            if not driver:
                continue
            driver.execute_script(
                bstack11l1ll1_opy_ (u"ࠥࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡡࡨࡼࡪࡩࡵࡵࡱࡵ࠾ࠥࢁࡽࠣቕ").format(
                    json.dumps(
                        {
                            bstack11l1ll1_opy_ (u"ࠦࡦࡩࡴࡪࡱࡱࠦቖ"): bstack11l1ll1_opy_ (u"ࠧࡹࡥࡵࡕࡨࡷࡸ࡯࡯࡯ࡐࡤࡱࡪࠨ቗"),
                            bstack11l1ll1_opy_ (u"ࠨࡡࡳࡩࡸࡱࡪࡴࡴࡴࠤቘ"): {bstack11l1ll1_opy_ (u"ࠢ࡯ࡣࡰࡩࠧ቙"): test_name},
                        }
                    )
                )
            )
        f.bstack1111l11l11_opy_(instance, bstack1llll111l11_opy_.bstack1l1llll1ll1_opy_, True)