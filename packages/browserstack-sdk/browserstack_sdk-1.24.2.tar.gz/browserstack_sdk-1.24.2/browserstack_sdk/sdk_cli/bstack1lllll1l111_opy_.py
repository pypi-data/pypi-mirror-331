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
from datetime import datetime, timezone
from uuid import uuid4
from typing import Dict, List, Any, Tuple
from browserstack_sdk.sdk_cli.bstack1111l11lll_opy_ import bstack1111l1lll1_opy_
from browserstack_sdk.sdk_cli.test_framework import (
    TestFramework,
    bstack1llll11llll_opy_,
    bstack11111l1l11_opy_,
    bstack1lll1llll11_opy_,
    bstack1l1l1l11lll_opy_,
    bstack1llll111ll1_opy_,
)
import traceback
from bstack_utils.bstack1ll111ll1l_opy_ import bstack1llll111lll_opy_
from bstack_utils.constants import EVENTS
from bstack_utils.bstack11l11l1lll_opy_ import bstack11ll1ll1_opy_
class bstack1lllllll1ll_opy_(TestFramework):
    bstack1l1ll111lll_opy_ = bstack11l1ll1_opy_ (u"ࠤࡷࡩࡸࡺ࡟ࡧ࡫ࡻࡸࡺࡸࡥࡴࠤዮ")
    bstack1l1l1lll1l1_opy_ = bstack11l1ll1_opy_ (u"ࠥࡸࡪࡹࡴࡠࡪࡲࡳࡰࡹ࡟ࡴࡶࡤࡶࡹ࡫ࡤࠣዯ")
    bstack1l1ll1lll1l_opy_ = bstack11l1ll1_opy_ (u"ࠦࡹ࡫ࡳࡵࡡ࡫ࡳࡴࡱࡳࡠࡨ࡬ࡲ࡮ࡹࡨࡦࡦࠥደ")
    bstack1l1lll11ll1_opy_ = bstack11l1ll1_opy_ (u"ࠧࡺࡥࡴࡶࡢ࡬ࡴࡵ࡫ࡠ࡮ࡤࡷࡹࡥࡳࡵࡣࡵࡸࡪࡪࠢዱ")
    bstack1l1ll1111ll_opy_ = bstack11l1ll1_opy_ (u"ࠨࡴࡦࡵࡷࡣ࡭ࡵ࡯࡬ࡡ࡯ࡥࡸࡺ࡟ࡧ࡫ࡱ࡭ࡸ࡮ࡥࡥࠤዲ")
    bstack1l1l1ll1l1l_opy_: bool
    bstack1l1l1ll1lll_opy_ = [
        bstack1llll11llll_opy_.BEFORE_ALL,
        bstack1llll11llll_opy_.AFTER_ALL,
        bstack1llll11llll_opy_.BEFORE_EACH,
        bstack1llll11llll_opy_.AFTER_EACH,
    ]
    def __init__(
        self,
        bstack1l1lll1l111_opy_: Dict[str, str],
        bstack1lll1l1l111_opy_: List[str]=[bstack11l1ll1_opy_ (u"ࠢࡱࡻࡷࡩࡸࡺࠢዳ")],
    ):
        super().__init__(bstack1lll1l1l111_opy_, bstack1l1lll1l111_opy_)
        self.bstack1l1l1ll1l1l_opy_ = any(bstack11l1ll1_opy_ (u"ࠣࡲࡼࡸࡪࡹࡴࠣዴ") in item.lower() for item in bstack1lll1l1l111_opy_)
    def track_event(
        self,
        context: bstack1l1l1l11lll_opy_,
        test_framework_state: bstack1llll11llll_opy_,
        test_hook_state: bstack1lll1llll11_opy_,
        *args,
        **kwargs,
    ):
        super().track_event(self, context, test_framework_state, test_hook_state, *args, **kwargs)
        if test_framework_state == bstack1llll11llll_opy_.NONE:
            self.logger.warning(bstack11l1ll1_opy_ (u"ࠤ࡬࡫ࡳࡵࡲࡦࡦࠣࡧࡦࡲ࡬ࡣࡣࡦ࡯ࠥࡺࡥࡴࡶࡢࡪࡷࡧ࡭ࡦࡹࡲࡶࡰࡥࡳࡵࡣࡷࡩࡂࢁࡴࡦࡵࡷࡣ࡫ࡸࡡ࡮ࡧࡺࡳࡷࡱ࡟ࡴࡶࡤࡸࡪࢃࠠࡵࡧࡶࡸࡤ࡮࡯ࡰ࡭ࡢࡷࡹࡧࡴࡦ࠿ࠥድ") + str(test_hook_state) + bstack11l1ll1_opy_ (u"ࠥࠦዶ"))
            return
        if not self.bstack1l1l1ll1l1l_opy_:
            self.logger.warning(bstack11l1ll1_opy_ (u"ࠦࡹࡸࡡࡤ࡭ࡢࡩࡻ࡫࡮ࡵ࠼ࠣࡹࡳࡹࡵࡱࡲࡲࡶࡹ࡫ࡤࠡࡨࡵࡥࡲ࡫ࡷࡰࡴ࡮ࡁࠧዷ") + str(str(self.bstack1lll1l1l111_opy_)) + bstack11l1ll1_opy_ (u"ࠧࠨዸ"))
            return
        if not isinstance(args, tuple) or len(args) == 0:
            self.logger.warning(bstack11l1ll1_opy_ (u"ࠨࡴࡳࡣࡦ࡯ࡤ࡫ࡶࡦࡰࡷ࠾ࠥࡻ࡮ࡦࡺࡳࡩࡨࡺࡥࡥࠢࡤࡶ࡬ࡹ࠽ࡼࡣࡵ࡫ࡸࢃࠠ࡬ࡹࡤࡶ࡬ࡹ࠽ࠣዹ") + str(kwargs) + bstack11l1ll1_opy_ (u"ࠢࠣዺ"))
            return
        instance = self.__1l1ll1ll1ll_opy_(context, test_framework_state, test_hook_state, *args, **kwargs)
        if not instance:
            self.logger.debug(bstack11l1ll1_opy_ (u"ࠣࡶࡵࡥࡨࡱ࡟ࡦࡸࡨࡲࡹࡀࠠࡶࡰ࡫ࡥࡳࡪ࡬ࡦࡦࠣࡩࡻ࡫࡮ࡵ࠿ࡾࡸࡪࡹࡴࡠࡨࡵࡥࡲ࡫ࡷࡰࡴ࡮ࡣࡸࡺࡡࡵࡧࢀ࠲ࢀࡺࡥࡴࡶࡢ࡬ࡴࡵ࡫ࡠࡵࡷࡥࡹ࡫ࡽࠡࡣࡵ࡫ࡸࡃࠢዻ") + str(args) + bstack11l1ll1_opy_ (u"ࠤࠥዼ"))
            return
        try:
            if instance!= None and test_framework_state in bstack1lllllll1ll_opy_.bstack1l1l1ll1lll_opy_ and test_hook_state == bstack1lll1llll11_opy_.PRE:
                bstack1lll11l1l1l_opy_ = bstack1llll111lll_opy_.bstack1lll11l1111_opy_(EVENTS.bstack1lll111l11_opy_.value)
                name = str(EVENTS.bstack1lll111l11_opy_.name)+bstack11l1ll1_opy_ (u"ࠥ࠾ࠧዽ")+str(test_framework_state.name)
                TestFramework.bstack1l1ll1l1l11_opy_(instance, name, bstack1lll11l1l1l_opy_)
        except Exception as e:
            self.logger.debug(bstack11l1ll1_opy_ (u"ࠦࡊࡾࡣࡦࡲࡷ࡭ࡴࡴࠠࡪࡰࠣ࡬ࡴࡵ࡫ࠡࡧࡵࡶࡴࡸࠠࡱࡴࡨ࠾ࠥࢁࡽࠣዾ").format(e))
        try:
            if not TestFramework.bstack111l1111ll_opy_(instance, TestFramework.bstack1l1l1llll11_opy_) and test_hook_state == bstack1lll1llll11_opy_.PRE:
                test = bstack1lllllll1ll_opy_.__1l1l1lll1ll_opy_(args[0])
                if test:
                    instance.data.update(test)
                    self.logger.debug(bstack11l1ll1_opy_ (u"ࠧࡲ࡯ࡢࡦࡨࡨࠥ࡯࡮ࡴࡶࡤࡲࡨ࡫࠽ࡼ࡫ࡱࡷࡹࡧ࡮ࡤࡧ࠱ࡶࡪ࡬ࠨࠪࡿࠣࡩࡻ࡫࡮ࡵ࠿ࡾࡸࡪࡹࡴࡠࡨࡵࡥࡲ࡫ࡷࡰࡴ࡮ࡣࡸࡺࡡࡵࡧࢀ࠲ࠧዿ") + str(test_hook_state) + bstack11l1ll1_opy_ (u"ࠨࠢጀ"))
            if test_framework_state == bstack1llll11llll_opy_.TEST:
                if test_hook_state == bstack1lll1llll11_opy_.PRE and not TestFramework.bstack111l1111ll_opy_(instance, TestFramework.bstack1ll11ll1l11_opy_):
                    TestFramework.bstack1111l11l11_opy_(instance, TestFramework.bstack1ll11ll1l11_opy_, datetime.now(tz=timezone.utc))
                    self.logger.debug(bstack11l1ll1_opy_ (u"ࠢࡴࡧࡷࠤࡹ࡫ࡳࡵ࠯ࡶࡸࡦࡸࡴࠡࡨࡲࡶࠥ࡯࡮ࡴࡶࡤࡲࡨ࡫࠽ࡼ࡫ࡱࡷࡹࡧ࡮ࡤࡧ࠱ࡶࡪ࡬ࠨࠪࡿࠣࡩࡻ࡫࡮ࡵ࠿ࡾࡸࡪࡹࡴࡠࡨࡵࡥࡲ࡫ࡷࡰࡴ࡮ࡣࡸࡺࡡࡵࡧࢀ࠲ࠧጁ") + str(test_hook_state) + bstack11l1ll1_opy_ (u"ࠣࠤጂ"))
                elif test_hook_state == bstack1lll1llll11_opy_.POST and not TestFramework.bstack111l1111ll_opy_(instance, TestFramework.bstack1ll1l111l11_opy_):
                    TestFramework.bstack1111l11l11_opy_(instance, TestFramework.bstack1ll1l111l11_opy_, datetime.now(tz=timezone.utc))
                    self.logger.debug(bstack11l1ll1_opy_ (u"ࠤࡶࡩࡹࠦࡴࡦࡵࡷ࠱ࡪࡴࡤࠡࡨࡲࡶࠥ࡯࡮ࡴࡶࡤࡲࡨ࡫࠽ࡼ࡫ࡱࡷࡹࡧ࡮ࡤࡧ࠱ࡶࡪ࡬ࠨࠪࡿࠣࡩࡻ࡫࡮ࡵ࠿ࡾࡸࡪࡹࡴࡠࡨࡵࡥࡲ࡫ࡷࡰࡴ࡮ࡣࡸࡺࡡࡵࡧࢀ࠲ࠧጃ") + str(test_hook_state) + bstack11l1ll1_opy_ (u"ࠥࠦጄ"))
            elif test_framework_state == bstack1llll11llll_opy_.LOG and test_hook_state == bstack1lll1llll11_opy_.POST:
                bstack1lllllll1ll_opy_.__1l1ll1lll11_opy_(instance, *args)
            elif test_framework_state == bstack1llll11llll_opy_.LOG_REPORT and test_hook_state == bstack1lll1llll11_opy_.POST:
                self.__1l1ll1ll11l_opy_(instance, *args)
            elif test_framework_state in bstack1lllllll1ll_opy_.bstack1l1l1ll1lll_opy_:
                self.__1l1ll1l1111_opy_(instance, test_framework_state, test_hook_state, *args)
            self.logger.debug(bstack11l1ll1_opy_ (u"ࠦࡹࡸࡡࡤ࡭ࡢࡩࡻ࡫࡮ࡵ࠼ࠣ࡬ࡦࡴࡤ࡭ࡧࡧࠤࡪࡼࡥ࡯ࡶࡀࡿࡹ࡫ࡳࡵࡡࡩࡶࡦࡳࡥࡸࡱࡵ࡯ࡤࡹࡴࡢࡶࡨࢁ࠳ࢁࡴࡦࡵࡷࡣ࡭ࡵ࡯࡬ࡡࡶࡸࡦࡺࡥࡾࠢ࡬ࡲࡸࡺࡡ࡯ࡥࡨࡁࠧጅ") + str(instance.ref()) + bstack11l1ll1_opy_ (u"ࠧࠨጆ"))
        except Exception as e:
            self.logger.error(e)
            traceback.print_exc()
        self.bstack1l1lll11111_opy_(instance, (test_framework_state, test_hook_state), *args, **kwargs)
        try:
            if instance!= None and test_framework_state in bstack1lllllll1ll_opy_.bstack1l1l1ll1lll_opy_ and test_hook_state == bstack1lll1llll11_opy_.POST:
                name = str(EVENTS.bstack1lll111l11_opy_.name)+bstack11l1ll1_opy_ (u"ࠨ࠺ࠣጇ")+str(test_framework_state.name)
                bstack1lll11l1l1l_opy_ = TestFramework.bstack1l1ll1111l1_opy_(instance, name)
                bstack1llll111lll_opy_.end(EVENTS.bstack1lll111l11_opy_.value, bstack1lll11l1l1l_opy_+bstack11l1ll1_opy_ (u"ࠢ࠻ࡵࡷࡥࡷࡺࠢገ"), bstack1lll11l1l1l_opy_+bstack11l1ll1_opy_ (u"ࠣ࠼ࡨࡲࡩࠨጉ"), True, None, test_framework_state.name)
        except Exception as e:
            self.logger.debug(bstack11l1ll1_opy_ (u"ࠤࡈࡼࡨ࡫ࡰࡵ࡫ࡲࡲࠥ࡯࡮ࠡࡪࡲࡳࡰࠦࡥࡳࡴࡲࡶ࠿ࠦࡻࡾࠤጊ").format(e))
    def bstack1ll11l1ll11_opy_(self):
        return self.bstack1l1l1ll1l1l_opy_
    def __1l1lll11l11_opy_(self, *args):
        if len(args) > 2 and callable(getattr(args[2], bstack11l1ll1_opy_ (u"ࠥ࡫ࡪࡺ࡟ࡳࡧࡶࡹࡱࡺࠢጋ"), None)):
            rep = args[2].get_result()
            if rep:
                return TestFramework.bstack1ll11l1l11l_opy_(rep, [bstack11l1ll1_opy_ (u"ࠦࡼ࡮ࡥ࡯ࠤጌ"), bstack11l1ll1_opy_ (u"ࠧࡵࡵࡵࡥࡲࡱࡪࠨግ"), bstack11l1ll1_opy_ (u"ࠨࡰࡢࡵࡶࡩࡩࠨጎ"), bstack11l1ll1_opy_ (u"ࠢࡧࡣ࡬ࡰࡪࡪࠢጏ"), bstack11l1ll1_opy_ (u"ࠣࡵ࡮࡭ࡵࡶࡥࡥࠤጐ"), bstack11l1ll1_opy_ (u"ࠤ࡯ࡳࡳ࡭ࡲࡦࡲࡵࡸࡪࡾࡴࠣ጑")])
        return None
    def __1l1ll1ll11l_opy_(self, instance: bstack11111l1l11_opy_, *args):
        result = self.__1l1lll11l11_opy_(*args)
        if not result:
            return
        failure = None
        bstack111l1l1111_opy_ = None
        if result.get(bstack11l1ll1_opy_ (u"ࠥࡳࡺࡺࡣࡰ࡯ࡨࠦጒ"), None) == bstack11l1ll1_opy_ (u"ࠦ࡫ࡧࡩ࡭ࡧࡧࠦጓ") and len(args) > 1 and getattr(args[1], bstack11l1ll1_opy_ (u"ࠧ࡫ࡸࡤ࡫ࡱࡪࡴࠨጔ"), None) is not None:
            failure = [{bstack11l1ll1_opy_ (u"࠭ࡢࡢࡥ࡮ࡸࡷࡧࡣࡦࠩጕ"): [args[1].excinfo.exconly(), result.get(bstack11l1ll1_opy_ (u"ࠢ࡭ࡱࡱ࡫ࡷ࡫ࡰࡳࡶࡨࡼࡹࠨ጖"), None)]}]
            bstack111l1l1111_opy_ = bstack11l1ll1_opy_ (u"ࠣࡃࡶࡷࡪࡸࡴࡪࡱࡱࡉࡷࡸ࡯ࡳࠤ጗") if bstack11l1ll1_opy_ (u"ࠤࡄࡷࡸ࡫ࡲࡵ࡫ࡲࡲࠧጘ") in getattr(args[1].excinfo, bstack11l1ll1_opy_ (u"ࠥࡸࡾࡶࡥ࡯ࡣࡰࡩࠧጙ"), bstack11l1ll1_opy_ (u"ࠦࠧጚ")) else bstack11l1ll1_opy_ (u"࡛ࠧ࡮ࡩࡣࡱࡨࡱ࡫ࡤࡆࡴࡵࡳࡷࠨጛ")
        bstack1l1l1l1l11l_opy_ = result.get(bstack11l1ll1_opy_ (u"ࠨ࡯ࡶࡶࡦࡳࡲ࡫ࠢጜ"), TestFramework.bstack1l1l1l1ll1l_opy_)
        if bstack1l1l1l1l11l_opy_ != TestFramework.bstack1l1l1l1ll1l_opy_:
            TestFramework.bstack1111l11l11_opy_(instance, TestFramework.bstack1ll1l1lll1l_opy_, datetime.now(tz=timezone.utc))
        TestFramework.bstack1l1l1l1l111_opy_(instance, {
            TestFramework.bstack1l1llll11ll_opy_: failure,
            TestFramework.bstack1l1l1lllll1_opy_: bstack111l1l1111_opy_,
            TestFramework.bstack1l1lll1ll11_opy_: bstack1l1l1l1l11l_opy_,
        })
    def __1l1ll1ll1ll_opy_(
        self,
        context: bstack1l1l1l11lll_opy_,
        test_framework_state: bstack1llll11llll_opy_,
        test_hook_state: bstack1lll1llll11_opy_,
        *args,
        **kwargs,
    ):
        instance = None
        if test_framework_state == bstack1llll11llll_opy_.SETUP_FIXTURE:
            instance = self.__1l1lll1111l_opy_(context, test_framework_state, test_hook_state, *args, **kwargs)
        else:
            target = None # bstack1l1ll1ll111_opy_ bstack1l1ll11l1l1_opy_ this to be bstack11l1ll1_opy_ (u"ࠢ࡯ࡱࡧࡩ࡮ࡪࠢጝ")
            if test_framework_state == bstack1llll11llll_opy_.INIT_TEST:
                target = args[0] if isinstance(args[0], str) else None
                if target:
                    self.__1l1lll11l1l_opy_(context, test_framework_state, target, *args)
            elif test_framework_state == bstack1llll11llll_opy_.LOG:
                nodeid = getattr(getattr(args[0], bstack11l1ll1_opy_ (u"ࠣࡰࡲࡨࡪࠨጞ"), None), bstack11l1ll1_opy_ (u"ࠤࡱࡳࡩ࡫ࡩࡥࠤጟ"), None) if args else None
                if isinstance(nodeid, str):
                    target = nodeid
            elif getattr(args[0], bstack11l1ll1_opy_ (u"ࠥࡲࡴࡪࡥࡪࡦࠥጠ"), None):
                target = args[0].nodeid
            instance = TestFramework.bstack1111llllll_opy_(target) if target else None
        return instance
    def __1l1ll1l1111_opy_(
        self,
        instance: bstack11111l1l11_opy_,
        test_framework_state: bstack1llll11llll_opy_,
        test_hook_state: bstack1lll1llll11_opy_,
        *args,
    ):
        key = test_framework_state.name
        bstack1l1ll111l1l_opy_ = TestFramework.bstack111l111111_opy_(instance, bstack1lllllll1ll_opy_.bstack1l1l1lll1l1_opy_, {})
        if not key in bstack1l1ll111l1l_opy_:
            bstack1l1ll111l1l_opy_[key] = []
        bstack1l1l1l1llll_opy_ = TestFramework.bstack111l111111_opy_(instance, bstack1lllllll1ll_opy_.bstack1l1ll1lll1l_opy_, {})
        if not key in bstack1l1l1l1llll_opy_:
            bstack1l1l1l1llll_opy_[key] = []
        bstack1l1ll11lll1_opy_ = {
            bstack1lllllll1ll_opy_.bstack1l1l1lll1l1_opy_: bstack1l1ll111l1l_opy_,
            bstack1lllllll1ll_opy_.bstack1l1ll1lll1l_opy_: bstack1l1l1l1llll_opy_,
        }
        if test_hook_state == bstack1lll1llll11_opy_.PRE:
            hook = {
                bstack11l1ll1_opy_ (u"ࠦࡰ࡫ࡹࠣጡ"): key,
                TestFramework.bstack1l1ll11llll_opy_: uuid4().__str__(),
                TestFramework.bstack1l1l1l1lll1_opy_: TestFramework.bstack1l1lll111ll_opy_,
                TestFramework.bstack1l1l1ll11l1_opy_: datetime.now(tz=timezone.utc),
                TestFramework.bstack1l1ll1llll1_opy_: [],
                TestFramework.bstack1l1ll1l111l_opy_: args[1] if len(args) > 1 else bstack11l1ll1_opy_ (u"ࠬ࠭ጢ")
            }
            bstack1l1ll111l1l_opy_[key].append(hook)
            bstack1l1ll11lll1_opy_[bstack1lllllll1ll_opy_.bstack1l1lll11ll1_opy_] = key
        elif test_hook_state == bstack1lll1llll11_opy_.POST:
            bstack1l1ll111l11_opy_ = bstack1l1ll111l1l_opy_.get(key, [])
            hook = bstack1l1ll111l11_opy_.pop() if bstack1l1ll111l11_opy_ else None
            if hook:
                result = self.__1l1lll11l11_opy_(*args)
                if result:
                    bstack1l1l1ll11ll_opy_ = result.get(bstack11l1ll1_opy_ (u"ࠨ࡯ࡶࡶࡦࡳࡲ࡫ࠢጣ"), TestFramework.bstack1l1lll111ll_opy_)
                    if bstack1l1l1ll11ll_opy_ != TestFramework.bstack1l1lll111ll_opy_:
                        hook[TestFramework.bstack1l1l1l1lll1_opy_] = bstack1l1l1ll11ll_opy_
                hook[TestFramework.bstack1l1ll11l111_opy_] = datetime.now(tz=timezone.utc)
                bstack1l1l1l1llll_opy_[key].append(hook)
                bstack1l1ll11lll1_opy_[bstack1lllllll1ll_opy_.bstack1l1ll1111ll_opy_] = key
        TestFramework.bstack1l1l1l1l111_opy_(instance, bstack1l1ll11lll1_opy_)
        self.logger.debug(bstack11l1ll1_opy_ (u"ࠢࡵࡴࡤࡧࡰࡥࡨࡰࡱ࡮ࡣࡪࡼࡥ࡯ࡶ࠽ࠤࡹ࡫ࡳࡵࡡ࡫ࡳࡴࡱ࡟ࡴࡶࡤࡸࡪࡃࡻ࡬ࡧࡼࢁ࠳ࢁࡴࡦࡵࡷࡣ࡭ࡵ࡯࡬ࡡࡶࡸࡦࡺࡥࡾࠢ࡫ࡳࡴࡱࡳࡠࡵࡷࡥࡷࡺࡥࡥ࠿ࡾ࡬ࡴࡵ࡫ࡴࡡࡶࡸࡦࡸࡴࡦࡦࢀࠤ࡭ࡵ࡯࡬ࡵࡢࡪ࡮ࡴࡩࡴࡪࡨࡨࡂࠨጤ") + str(bstack1l1l1l1llll_opy_) + bstack11l1ll1_opy_ (u"ࠣࠤጥ"))
    def __1l1lll1111l_opy_(
        self,
        context: bstack1l1l1l11lll_opy_,
        test_framework_state: bstack1llll11llll_opy_,
        test_hook_state: bstack1lll1llll11_opy_,
        *args,
        **kwargs,
    ):
        fixturedef = TestFramework.bstack1ll11l1l11l_opy_(args[0], [bstack11l1ll1_opy_ (u"ࠤࡶࡧࡴࡶࡥࠣጦ"), bstack11l1ll1_opy_ (u"ࠥࡥࡷ࡭࡮ࡢ࡯ࡨࠦጧ"), bstack11l1ll1_opy_ (u"ࠦࡵࡧࡲࡢ࡯ࡶࠦጨ"), bstack11l1ll1_opy_ (u"ࠧ࡯ࡤࡴࠤጩ"), bstack11l1ll1_opy_ (u"ࠨࡵ࡯࡫ࡷࡸࡪࡹࡴࠣጪ"), bstack11l1ll1_opy_ (u"ࠢࡣࡣࡶࡩ࡮ࡪࠢጫ")]) if len(args) > 0 else {}
        request = args[1] if len(args) > 1 else None
        scope = request.scope if hasattr(request, bstack11l1ll1_opy_ (u"ࠣࡵࡦࡳࡵ࡫ࠢጬ")) else fixturedef.get(bstack11l1ll1_opy_ (u"ࠤࡶࡧࡴࡶࡥࠣጭ"), None)
        fixturename = request.fixturename if hasattr(request, bstack11l1ll1_opy_ (u"ࠥࡪ࡮ࡾࡴࡶࡴࡨࡲࡦࡳࡥࠣጮ")) else None
        node = request.node if hasattr(request, bstack11l1ll1_opy_ (u"ࠦࡳࡵࡤࡦࠤጯ")) else None
        target = request.node.nodeid if hasattr(node, bstack11l1ll1_opy_ (u"ࠧࡴ࡯ࡥࡧ࡬ࡨࠧጰ")) else None
        baseid = fixturedef.get(bstack11l1ll1_opy_ (u"ࠨࡢࡢࡵࡨ࡭ࡩࠨጱ"), None) or bstack11l1ll1_opy_ (u"ࠢࠣጲ")
        if (not target or len(baseid) > 0) and hasattr(request, bstack11l1ll1_opy_ (u"ࠣࡡࡳࡽ࡫ࡻ࡮ࡤ࡫ࡷࡩࡲࠨጳ")):
            target = bstack1lllllll1ll_opy_.__1l1l1llllll_opy_(request._pyfuncitem.location) if hasattr(request._pyfuncitem, bstack11l1ll1_opy_ (u"ࠤ࡯ࡳࡨࡧࡴࡪࡱࡱࠦጴ")) else None
            if target and not TestFramework.bstack1111llllll_opy_(target):
                self.__1l1lll11l1l_opy_(context, test_framework_state, target, (target, request._pyfuncitem.location))
                node = request._pyfuncitem
                self.logger.debug(bstack11l1ll1_opy_ (u"ࠥࡸࡷࡧࡣ࡬ࡡࡩ࡭ࡽࡺࡵࡳࡧࡢࡩࡻ࡫࡮ࡵ࠼ࠣࡪࡦࡲ࡬ࡣࡣࡦ࡯ࠥࡺࡡࡳࡩࡨࡸࡂࢁࡴࡢࡴࡪࡩࡹࢃࠠࡧ࡫ࡻࡸࡺࡸࡥ࡯ࡣࡰࡩࡂࢁࡦࡪࡺࡷࡹࡷ࡫࡮ࡢ࡯ࡨࢁࠥࡴ࡯ࡥࡧࡀࡿࡳࡵࡤࡦࡿࠣࡩࡻ࡫࡮ࡵ࠿ࡾࡸࡪࡹࡴࡠࡨࡵࡥࡲ࡫ࡷࡰࡴ࡮ࡣࡸࡺࡡࡵࡧࢀ࠲ࠧጵ") + str(test_hook_state) + bstack11l1ll1_opy_ (u"ࠦࠧጶ"))
        if not fixturedef or not scope or not target:
            self.logger.warning(bstack11l1ll1_opy_ (u"ࠧࡺࡲࡢࡥ࡮ࡣ࡫࡯ࡸࡵࡷࡵࡩࡤ࡫ࡶࡦࡰࡷ࠾ࠥࡻ࡮ࡩࡣࡱࡨࡱ࡫ࡤࠡࡧࡹࡩࡳࡺ࠽ࡼࡶࡨࡷࡹࡥࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࡡࡶࡸࡦࡺࡥࡾ࠰ࡾࡸࡪࡹࡴࡠࡪࡲࡳࡰࡥࡳࡵࡣࡷࡩࢂࠦࡦࡪࡺࡷࡹࡷ࡫ࡤࡦࡨࡀࡿ࡫࡯ࡸࡵࡷࡵࡩࡩ࡫ࡦࡾࠢࡶࡧࡴࡶࡥ࠾ࡽࡶࡧࡴࡶࡥࡾࠢࡷࡥࡷ࡭ࡥࡵ࠿ࠥጷ") + str(target) + bstack11l1ll1_opy_ (u"ࠨࠢጸ"))
            return None
        instance = TestFramework.bstack1111llllll_opy_(target)
        if not instance:
            self.logger.warning(bstack11l1ll1_opy_ (u"ࠢࡵࡴࡤࡧࡰࡥࡦࡪࡺࡷࡹࡷ࡫࡟ࡦࡸࡨࡲࡹࡀࠠࡶࡰ࡫ࡥࡳࡪ࡬ࡦࡦࠣࡩࡻ࡫࡮ࡵ࠿ࡾࡸࡪࡹࡴࡠࡨࡵࡥࡲ࡫ࡷࡰࡴ࡮ࡣࡸࡺࡡࡵࡧࢀ࠲ࢀࡺࡥࡴࡶࡢ࡬ࡴࡵ࡫ࡠࡵࡷࡥࡹ࡫ࡽࠡࡨ࡬ࡼࡹࡻࡲࡦࡰࡤࡱࡪࡃࡻࡧ࡫ࡻࡸࡺࡸࡥ࡯ࡣࡰࡩࢂࠦࡳࡤࡱࡳࡩࡂࢁࡳࡤࡱࡳࡩࢂࠦࡢࡢࡵࡨ࡭ࡩࡃࡻࡣࡣࡶࡩ࡮ࡪࡽࠡࡶࡤࡶ࡬࡫ࡴ࠾ࠤጹ") + str(target) + bstack11l1ll1_opy_ (u"ࠣࠤጺ"))
            return None
        bstack1l1l1lll11l_opy_ = TestFramework.bstack111l111111_opy_(instance, bstack1lllllll1ll_opy_.bstack1l1ll111lll_opy_, {})
        if os.getenv(bstack11l1ll1_opy_ (u"ࠤࡖࡈࡐࡥࡃࡍࡋࡢࡊࡑࡇࡇࡠࡈࡌ࡜࡙࡛ࡒࡆࡕࠥጻ"), bstack11l1ll1_opy_ (u"ࠥ࠵ࠧጼ")) == bstack11l1ll1_opy_ (u"ࠦ࠶ࠨጽ"):
            bstack1l1lll11lll_opy_ = bstack11l1ll1_opy_ (u"ࠧࡀࠢጾ").join((scope, fixturename))
            bstack1l1l1ll1ll1_opy_ = datetime.now(tz=timezone.utc)
            bstack1l1l1l1l1ll_opy_ = {
                bstack11l1ll1_opy_ (u"ࠨ࡫ࡦࡻࠥጿ"): bstack1l1lll11lll_opy_,
                bstack11l1ll1_opy_ (u"ࠢࡵࡣࡪࡷࠧፀ"): bstack1lllllll1ll_opy_.__1l1ll1l11ll_opy_(request.node),
                bstack11l1ll1_opy_ (u"ࠣࡨ࡬ࡼࡹࡻࡲࡦࠤፁ"): fixturedef,
                bstack11l1ll1_opy_ (u"ࠤࡶࡧࡴࡶࡥࠣፂ"): scope,
                bstack11l1ll1_opy_ (u"ࠥࡸࡾࡶࡥࠣፃ"): None,
            }
            try:
                if test_hook_state == bstack1lll1llll11_opy_.POST and callable(getattr(args[-1], bstack11l1ll1_opy_ (u"ࠦ࡬࡫ࡴࡠࡴࡨࡷࡺࡲࡴࠣፄ"), None)):
                    bstack1l1l1l1l1ll_opy_[bstack11l1ll1_opy_ (u"ࠧࡺࡹࡱࡧࠥፅ")] = TestFramework.bstack1ll1l111111_opy_(args[-1].get_result())
            except Exception as e:
                pass
            if test_hook_state == bstack1lll1llll11_opy_.PRE:
                bstack1l1l1l1l1ll_opy_[bstack11l1ll1_opy_ (u"ࠨࡵࡶ࡫ࡧࠦፆ")] = uuid4().__str__()
                bstack1l1l1l1l1ll_opy_[bstack1lllllll1ll_opy_.bstack1l1l1ll11l1_opy_] = bstack1l1l1ll1ll1_opy_
            elif test_hook_state == bstack1lll1llll11_opy_.POST:
                bstack1l1l1l1l1ll_opy_[bstack1lllllll1ll_opy_.bstack1l1ll11l111_opy_] = bstack1l1l1ll1ll1_opy_
            if bstack1l1lll11lll_opy_ in bstack1l1l1lll11l_opy_:
                bstack1l1l1lll11l_opy_[bstack1l1lll11lll_opy_].update(bstack1l1l1l1l1ll_opy_)
                self.logger.debug(bstack11l1ll1_opy_ (u"ࠢࡶࡲࡧࡥࡹ࡫ࡤࠡࡨ࡬ࡼࡹࡻࡲࡦࡰࡤࡱࡪࡃࡻࡧ࡫ࡻࡸࡺࡸࡥ࡯ࡣࡰࡩࢂࠦࡳࡤࡱࡳࡩࡂࢁࡳࡤࡱࡳࡩࢂࠦࡦࡪࡺࡷࡹࡷ࡫࠽ࠣፇ") + str(bstack1l1l1lll11l_opy_[bstack1l1lll11lll_opy_]) + bstack11l1ll1_opy_ (u"ࠣࠤፈ"))
            else:
                bstack1l1l1lll11l_opy_[bstack1l1lll11lll_opy_] = bstack1l1l1l1l1ll_opy_
                self.logger.debug(bstack11l1ll1_opy_ (u"ࠤࡶࡥࡻ࡫ࡤࠡࡨ࡬ࡼࡹࡻࡲࡦࡰࡤࡱࡪࡃࡻࡧ࡫ࡻࡸࡺࡸࡥ࡯ࡣࡰࡩࢂࠦࡳࡤࡱࡳࡩࡂࢁࡳࡤࡱࡳࡩࢂࠦࡦࡪࡺࡷࡹࡷ࡫࠽ࡼࡶࡨࡷࡹࡥࡦࡪࡺࡷࡹࡷ࡫ࡽࠡࡶࡵࡥࡨࡱࡥࡥࡡࡩ࡭ࡽࡺࡵࡳࡧࡶࡁࠧፉ") + str(len(bstack1l1l1lll11l_opy_)) + bstack11l1ll1_opy_ (u"ࠥࠦፊ"))
        TestFramework.bstack1111l11l11_opy_(instance, bstack1lllllll1ll_opy_.bstack1l1ll111lll_opy_, bstack1l1l1lll11l_opy_)
        self.logger.debug(bstack11l1ll1_opy_ (u"ࠦࡸࡧࡶࡦࡦࠣࡪ࡮ࡾࡴࡶࡴࡨࡷࡂࢁ࡬ࡦࡰࠫࡸࡷࡧࡣ࡬ࡧࡧࡣ࡫࡯ࡸࡵࡷࡵࡩࡸ࠯ࡽࠡ࡫ࡱࡷࡹࡧ࡮ࡤࡧࡀࠦፋ") + str(instance.ref()) + bstack11l1ll1_opy_ (u"ࠧࠨፌ"))
        return instance
    def __1l1lll11l1l_opy_(
        self,
        context: bstack1l1l1l11lll_opy_,
        test_framework_state: bstack1llll11llll_opy_,
        target: Any,
        *args,
    ):
        ctx = bstack1111l1lll1_opy_.create_context(target)
        ob = bstack11111l1l11_opy_(ctx, self.bstack1lll1l1l111_opy_, self.bstack1l1lll1l111_opy_, test_framework_state)
        TestFramework.bstack1l1l1l1l111_opy_(ob, {
            TestFramework.bstack1lll11111l1_opy_: context.test_framework_name,
            TestFramework.bstack1ll1l11llll_opy_: context.test_framework_version,
            TestFramework.bstack1l1ll1l1lll_opy_: [],
            bstack1lllllll1ll_opy_.bstack1l1ll111lll_opy_: {},
            bstack1lllllll1ll_opy_.bstack1l1ll1lll1l_opy_: {},
            bstack1lllllll1ll_opy_.bstack1l1l1lll1l1_opy_: {},
        })
        if len(args) > 1 and isinstance(args[1], tuple):
            TestFramework.bstack1111l11l11_opy_(ob, TestFramework.bstack1l1l1llll1l_opy_, str(args[1][0]))
        if context.platform_index >= 0:
            TestFramework.bstack1111l11l11_opy_(ob, TestFramework.bstack1lll11ll1l1_opy_, context.platform_index)
        TestFramework.bstack1111l1ll11_opy_[ctx.id] = ob
        self.logger.debug(bstack11l1ll1_opy_ (u"ࠨࡳࡢࡸࡨࡨࠥ࡯࡮ࡴࡶࡤࡲࡨ࡫ࠠࡤࡶࡻ࠲࡮ࡪ࠽ࡼࡥࡷࡼ࠳࡯ࡤࡾࠢࡷࡥࡷ࡭ࡥࡵ࠿ࡾࡸࡦࡸࡧࡦࡶࢀࠤࡦࡸࡧࡴ࠿ࡾࡥࡷ࡭ࡳࡾࠢ࡬ࡲࡸࡺࡡ࡯ࡥࡨࡷࡂࠨፍ") + str(TestFramework.bstack1111l1ll11_opy_.keys()) + bstack11l1ll1_opy_ (u"ࠢࠣፎ"))
        return ob
    def bstack1ll11l1l111_opy_(self, instance: bstack11111l1l11_opy_, bstack111l111l1l_opy_: Tuple[bstack1llll11llll_opy_, bstack1lll1llll11_opy_]):
        bstack1l1ll111111_opy_ = (
            bstack1lllllll1ll_opy_.bstack1l1lll11ll1_opy_
            if bstack111l111l1l_opy_[1] == bstack1lll1llll11_opy_.PRE
            else bstack1lllllll1ll_opy_.bstack1l1ll1111ll_opy_
        )
        hook = bstack1lllllll1ll_opy_.bstack1l1ll1l1l1l_opy_(instance, bstack1l1ll111111_opy_)
        entries = hook.get(TestFramework.bstack1l1ll1llll1_opy_, []) if isinstance(hook, dict) else []
        entries.extend(TestFramework.bstack111l111111_opy_(instance, TestFramework.bstack1l1ll1l1lll_opy_, []))
        return entries
    def bstack1ll1l1111l1_opy_(self, instance: bstack11111l1l11_opy_, bstack111l111l1l_opy_: Tuple[bstack1llll11llll_opy_, bstack1lll1llll11_opy_]):
        bstack1l1ll111111_opy_ = (
            bstack1lllllll1ll_opy_.bstack1l1lll11ll1_opy_
            if bstack111l111l1l_opy_[1] == bstack1lll1llll11_opy_.PRE
            else bstack1lllllll1ll_opy_.bstack1l1ll1111ll_opy_
        )
        bstack1lllllll1ll_opy_.bstack1l1ll11ll1l_opy_(instance, bstack1l1ll111111_opy_)
        TestFramework.bstack111l111111_opy_(instance, TestFramework.bstack1l1ll1l1lll_opy_, []).clear()
    @staticmethod
    def bstack1l1ll1l1l1l_opy_(instance: bstack11111l1l11_opy_, bstack1l1ll111111_opy_: str):
        bstack1l1ll11ll11_opy_ = (
            bstack1lllllll1ll_opy_.bstack1l1ll1lll1l_opy_
            if bstack1l1ll111111_opy_ == bstack1lllllll1ll_opy_.bstack1l1ll1111ll_opy_
            else bstack1lllllll1ll_opy_.bstack1l1l1lll1l1_opy_
        )
        bstack1l1lll111l1_opy_ = TestFramework.bstack111l111111_opy_(instance, bstack1l1ll111111_opy_, None)
        bstack1l1l1l11l1l_opy_ = TestFramework.bstack111l111111_opy_(instance, bstack1l1ll11ll11_opy_, None) if bstack1l1lll111l1_opy_ else None
        return (
            bstack1l1l1l11l1l_opy_[bstack1l1lll111l1_opy_][-1]
            if isinstance(bstack1l1l1l11l1l_opy_, dict) and len(bstack1l1l1l11l1l_opy_.get(bstack1l1lll111l1_opy_, [])) > 0
            else None
        )
    @staticmethod
    def bstack1l1ll11ll1l_opy_(instance: bstack11111l1l11_opy_, bstack1l1ll111111_opy_: str):
        hook = bstack1lllllll1ll_opy_.bstack1l1ll1l1l1l_opy_(instance, bstack1l1ll111111_opy_)
        if isinstance(hook, dict):
            hook.get(TestFramework.bstack1l1ll1llll1_opy_, []).clear()
    @staticmethod
    def __1l1ll1lll11_opy_(instance: bstack11111l1l11_opy_, *args):
        if len(args) < 2 or not callable(getattr(args[1], bstack11l1ll1_opy_ (u"ࠣࡩࡨࡸࡤࡸࡥࡤࡱࡵࡨࡸࠨፏ"), None)):
            return
        if os.getenv(bstack11l1ll1_opy_ (u"ࠤࡖࡈࡐࡥࡃࡍࡋࡢࡊࡑࡇࡇࡠࡎࡒࡋࡘࠨፐ"), bstack11l1ll1_opy_ (u"ࠥ࠵ࠧፑ")) != bstack11l1ll1_opy_ (u"ࠦ࠶ࠨፒ"):
            bstack1lllllll1ll_opy_.logger.warning(bstack11l1ll1_opy_ (u"ࠧ࡯ࡧ࡯ࡱࡵ࡭ࡳ࡭ࠠࡤࡣࡳࡰࡴ࡭ࠢፓ"))
            return
        bstack1l1l1ll111l_opy_ = {
            bstack11l1ll1_opy_ (u"ࠨࡳࡦࡶࡸࡴࠧፔ"): (bstack1lllllll1ll_opy_.bstack1l1lll11ll1_opy_, bstack1lllllll1ll_opy_.bstack1l1l1lll1l1_opy_),
            bstack11l1ll1_opy_ (u"ࠢࡵࡧࡤࡶࡩࡵࡷ࡯ࠤፕ"): (bstack1lllllll1ll_opy_.bstack1l1ll1111ll_opy_, bstack1lllllll1ll_opy_.bstack1l1ll1lll1l_opy_),
        }
        for when in (bstack11l1ll1_opy_ (u"ࠣࡵࡨࡸࡺࡶࠢፖ"), bstack11l1ll1_opy_ (u"ࠤࡦࡥࡱࡲࠢፗ"), bstack11l1ll1_opy_ (u"ࠥࡸࡪࡧࡲࡥࡱࡺࡲࠧፘ")):
            bstack1l1l1l11l11_opy_ = args[1].get_records(when)
            if not bstack1l1l1l11l11_opy_:
                continue
            records = [
                bstack1llll111ll1_opy_(
                    kind=TestFramework.bstack1ll1ll1111l_opy_,
                    message=r.message,
                    level=r.levelname if hasattr(r, bstack11l1ll1_opy_ (u"ࠦࡱ࡫ࡶࡦ࡮ࡱࡥࡲ࡫ࠢፙ")) and r.levelname else None,
                    timestamp=(
                        datetime.fromtimestamp(r.created, tz=timezone.utc)
                        if hasattr(r, bstack11l1ll1_opy_ (u"ࠧࡩࡲࡦࡣࡷࡩࡩࠨፚ")) and r.created
                        else None
                    ),
                )
                for r in bstack1l1l1l11l11_opy_
                if isinstance(getattr(r, bstack11l1ll1_opy_ (u"ࠨ࡭ࡦࡵࡶࡥ࡬࡫ࠢ፛"), None), str) and r.message.strip()
            ]
            if not records:
                continue
            bstack1l1ll11l1ll_opy_, bstack1l1ll11ll11_opy_ = bstack1l1l1ll111l_opy_.get(when, (None, None))
            bstack1l1ll11111l_opy_ = TestFramework.bstack111l111111_opy_(instance, bstack1l1ll11l1ll_opy_, None) if bstack1l1ll11l1ll_opy_ else None
            bstack1l1l1l11l1l_opy_ = TestFramework.bstack111l111111_opy_(instance, bstack1l1ll11ll11_opy_, None) if bstack1l1ll11111l_opy_ else None
            if isinstance(bstack1l1l1l11l1l_opy_, dict) and len(bstack1l1l1l11l1l_opy_.get(bstack1l1ll11111l_opy_, [])) > 0:
                hook = bstack1l1l1l11l1l_opy_[bstack1l1ll11111l_opy_][-1]
                if isinstance(hook, dict) and TestFramework.bstack1l1ll1llll1_opy_ in hook:
                    hook[TestFramework.bstack1l1ll1llll1_opy_].extend(records)
                    continue
            logs = TestFramework.bstack111l111111_opy_(instance, TestFramework.bstack1l1ll1l1lll_opy_, [])
            logs.extend(records)
    @staticmethod
    def __1l1l1lll1ll_opy_(test) -> Dict[str, Any]:
        bstack1ll1lllll_opy_ = bstack1lllllll1ll_opy_.__1l1l1llllll_opy_(test.location) if hasattr(test, bstack11l1ll1_opy_ (u"ࠢ࡭ࡱࡦࡥࡹ࡯࡯࡯ࠤ፜")) else getattr(test, bstack11l1ll1_opy_ (u"ࠣࡰࡲࡨࡪ࡯ࡤࠣ፝"), None)
        test_name = test.name if hasattr(test, bstack11l1ll1_opy_ (u"ࠤࡱࡥࡲ࡫ࠢ፞")) else None
        bstack1l1l1l1ll11_opy_ = test.fspath.strpath if hasattr(test, bstack11l1ll1_opy_ (u"ࠥࡪࡸࡶࡡࡵࡪࠥ፟")) and test.fspath else None
        if not bstack1ll1lllll_opy_ or not test_name or not bstack1l1l1l1ll11_opy_:
            return None
        code = None
        if hasattr(test, bstack11l1ll1_opy_ (u"ࠦࡴࡨࡪࠣ፠")):
            try:
                import inspect
                code = inspect.getsource(test.obj)
            except:
                pass
        bstack1l1l1l111l1_opy_ = []
        try:
            bstack1l1l1l111l1_opy_ = bstack11ll1ll1_opy_.bstack111ll1l1ll_opy_(test)
        except:
            bstack1lllllll1ll_opy_.logger.warning(bstack11l1ll1_opy_ (u"࡛ࠧ࡮ࡢࡤ࡯ࡩࠥࡺ࡯ࠡࡨ࡬ࡲࡩࠦࡴࡦࡵࡷࠤࡸࡩ࡯ࡱࡧࡶ࠰ࠥࡺࡥࡴࡶࠣࡷࡨࡵࡰࡦࡵࠣࡻ࡮ࡲ࡬ࠡࡤࡨࠤࡷ࡫ࡳࡰ࡮ࡹࡩࡩࠦࡩ࡯ࠢࡆࡐࡎࠨ፡"))
        return {
            TestFramework.bstack1lll111l1l1_opy_: uuid4().__str__(),
            TestFramework.bstack1l1l1llll11_opy_: bstack1ll1lllll_opy_,
            TestFramework.bstack1lll11ll111_opy_: test_name,
            TestFramework.bstack1ll11l11l1l_opy_: getattr(test, bstack11l1ll1_opy_ (u"ࠨ࡮ࡰࡦࡨ࡭ࡩࠨ።"), None),
            TestFramework.bstack1l1l1lll111_opy_: bstack1l1l1l1ll11_opy_,
            TestFramework.bstack1l1l1l11ll1_opy_: bstack1lllllll1ll_opy_.__1l1ll1l11ll_opy_(test),
            TestFramework.bstack1l1ll1ll1l1_opy_: code,
            TestFramework.bstack1l1lll1ll11_opy_: TestFramework.bstack1l1l1l1ll1l_opy_,
            TestFramework.bstack1l1llll1l11_opy_: bstack1ll1lllll_opy_,
            TestFramework.bstack1l1l1l1111l_opy_: bstack1l1l1l111l1_opy_
        }
    @staticmethod
    def __1l1ll1l11ll_opy_(test) -> List[str]:
        return (
            [getattr(f, bstack11l1ll1_opy_ (u"ࠢ࡯ࡣࡰࡩࠧ፣"), None) for f in test.own_markers if getattr(f, bstack11l1ll1_opy_ (u"ࠣࡰࡤࡱࡪࠨ፤"), None)]
            if isinstance(getattr(test, bstack11l1ll1_opy_ (u"ࠤࡲࡻࡳࡥ࡭ࡢࡴ࡮ࡩࡷࡹࠢ፥"), None), list)
            else []
        )
    @staticmethod
    def __1l1l1llllll_opy_(location):
        return bstack11l1ll1_opy_ (u"ࠥ࠾࠿ࠨ፦").join(filter(lambda x: isinstance(x, str), location))