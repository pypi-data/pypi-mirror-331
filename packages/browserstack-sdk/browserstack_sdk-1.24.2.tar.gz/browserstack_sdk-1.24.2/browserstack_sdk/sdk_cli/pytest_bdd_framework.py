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
from pyexpat import features
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
class PytestBDDFramework(TestFramework):
    bstack1l1ll111lll_opy_ = bstack11l1ll1_opy_ (u"ࠣࡶࡨࡷࡹࡥࡦࡪࡺࡷࡹࡷ࡫ࡳࠣቚ")
    bstack1l1l1lll1l1_opy_ = bstack11l1ll1_opy_ (u"ࠤࡷࡩࡸࡺ࡟ࡩࡱࡲ࡯ࡸࡥࡳࡵࡣࡵࡸࡪࡪࠢቛ")
    bstack1l1ll1lll1l_opy_ = bstack11l1ll1_opy_ (u"ࠥࡸࡪࡹࡴࡠࡪࡲࡳࡰࡹ࡟ࡧ࡫ࡱ࡭ࡸ࡮ࡥࡥࠤቜ")
    bstack1l1lll11ll1_opy_ = bstack11l1ll1_opy_ (u"ࠦࡹ࡫ࡳࡵࡡ࡫ࡳࡴࡱ࡟࡭ࡣࡶࡸࡤࡹࡴࡢࡴࡷࡩࡩࠨቝ")
    bstack1l1ll1111ll_opy_ = bstack11l1ll1_opy_ (u"ࠧࡺࡥࡴࡶࡢ࡬ࡴࡵ࡫ࡠ࡮ࡤࡷࡹࡥࡦࡪࡰ࡬ࡷ࡭࡫ࡤࠣ቞")
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
        bstack1lll1l1l111_opy_: List[str]=[bstack11l1ll1_opy_ (u"ࠨࡰࡺࡶࡨࡷࡹ࠳ࡢࡥࡦࠥ቟")],
    ):
        super().__init__(bstack1lll1l1l111_opy_, bstack1l1lll1l111_opy_)
        self.bstack1l1l1ll1l1l_opy_ = any(bstack11l1ll1_opy_ (u"ࠢࡱࡻࡷࡩࡸࡺ࠭ࡣࡦࡧࠦበ") in item.lower() for item in bstack1lll1l1l111_opy_)
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
            self.logger.warning(bstack11l1ll1_opy_ (u"ࠣ࡫ࡪࡲࡴࡸࡥࡥࠢࡦࡥࡱࡲࡢࡢࡥ࡮ࠤࡹ࡫ࡳࡵࡡࡩࡶࡦࡳࡥࡸࡱࡵ࡯ࡤࡹࡴࡢࡶࡨࡁࢀࡺࡥࡴࡶࡢࡪࡷࡧ࡭ࡦࡹࡲࡶࡰࡥࡳࡵࡣࡷࡩࢂࠦࡴࡦࡵࡷࡣ࡭ࡵ࡯࡬ࡡࡶࡸࡦࡺࡥ࠾ࠤቡ") + str(test_hook_state) + bstack11l1ll1_opy_ (u"ࠤࠥቢ"))
            return
        if not self.bstack1l1l1ll1l1l_opy_:
            self.logger.warning(bstack11l1ll1_opy_ (u"ࠥࡸࡷࡧࡣ࡬ࡡࡨࡺࡪࡴࡴ࠻ࠢࡸࡲࡸࡻࡰࡱࡱࡵࡸࡪࡪࠠࡧࡴࡤࡱࡪࡽ࡯ࡳ࡭ࡀࠦባ") + str(str(self.bstack1lll1l1l111_opy_)) + bstack11l1ll1_opy_ (u"ࠦࠧቤ"))
            return
        if not isinstance(args, tuple) or len(args) == 0:
            self.logger.warning(bstack11l1ll1_opy_ (u"ࠧࡺࡲࡢࡥ࡮ࡣࡪࡼࡥ࡯ࡶ࠽ࠤࡺࡴࡥࡹࡲࡨࡧࡹ࡫ࡤࠡࡣࡵ࡫ࡸࡃࡻࡢࡴࡪࡷࢂࠦ࡫ࡸࡣࡵ࡫ࡸࡃࠢብ") + str(kwargs) + bstack11l1ll1_opy_ (u"ࠨࠢቦ"))
            return
        instance = self.__1l1ll1ll1ll_opy_(context, test_framework_state, test_hook_state, *args, **kwargs)
        if not instance:
            self.logger.debug(bstack11l1ll1_opy_ (u"ࠢࡵࡴࡤࡧࡰࡥࡥࡷࡧࡱࡸ࠿ࠦࡵ࡯ࡪࡤࡲࡩࡲࡥࡥࠢࡨࡺࡪࡴࡴ࠾ࡽࡷࡩࡸࡺ࡟ࡧࡴࡤࡱࡪࡽ࡯ࡳ࡭ࡢࡷࡹࡧࡴࡦࡿ࠱ࡿࡹ࡫ࡳࡵࡡ࡫ࡳࡴࡱ࡟ࡴࡶࡤࡸࡪࢃࠠࡢࡴࡪࡷࡂࠨቧ") + str(args) + bstack11l1ll1_opy_ (u"ࠣࠤቨ"))
            return
        try:
            if instance!= None and test_framework_state in PytestBDDFramework.bstack1l1l1ll1lll_opy_ and test_hook_state == bstack1lll1llll11_opy_.PRE:
                bstack1lll11l1l1l_opy_ = bstack1llll111lll_opy_.bstack1lll11l1111_opy_(EVENTS.bstack1lll111l11_opy_.value)
                name = str(EVENTS.bstack1lll111l11_opy_.name)+bstack11l1ll1_opy_ (u"ࠤ࠽ࠦቩ")+str(test_framework_state.name)
                TestFramework.bstack1l1ll1l1l11_opy_(instance, name, bstack1lll11l1l1l_opy_)
        except Exception as e:
            self.logger.debug(bstack11l1ll1_opy_ (u"ࠥࡉࡽࡩࡥࡱࡶ࡬ࡳࡳࠦࡩ࡯ࠢ࡫ࡳࡴࡱࠠࡦࡴࡵࡳࡷࠦࡰࡳࡧ࠽ࠤࢀࢃࠢቪ").format(e))
        try:
            if test_framework_state == bstack1llll11llll_opy_.TEST:
                if not TestFramework.bstack111l1111ll_opy_(instance, TestFramework.bstack1l1l1llll11_opy_) and test_hook_state == bstack1lll1llll11_opy_.PRE:
                    if not (len(args) >= 3):
                        return
                    test = PytestBDDFramework.__1l1l1lll1ll_opy_(args)
                    if test:
                        instance.data.update(test)
                        self.logger.debug(bstack11l1ll1_opy_ (u"ࠦࡱࡵࡡࡥࡧࡧࠤ࡮ࡴࡳࡵࡣࡱࡧࡪࡃࡻࡪࡰࡶࡸࡦࡴࡣࡦ࠰ࡵࡩ࡫࠮ࠩࡾࠢࡨࡺࡪࡴࡴ࠾ࡽࡷࡩࡸࡺ࡟ࡧࡴࡤࡱࡪࡽ࡯ࡳ࡭ࡢࡷࡹࡧࡴࡦࡿ࠱ࠦቫ") + str(test_hook_state) + bstack11l1ll1_opy_ (u"ࠧࠨቬ"))
                if test_hook_state == bstack1lll1llll11_opy_.PRE and not TestFramework.bstack111l1111ll_opy_(instance, TestFramework.bstack1ll11ll1l11_opy_):
                    TestFramework.bstack1111l11l11_opy_(instance, TestFramework.bstack1ll11ll1l11_opy_, datetime.now(tz=timezone.utc))
                    PytestBDDFramework.__1l1l1l111ll_opy_(instance, args)
                    self.logger.debug(bstack11l1ll1_opy_ (u"ࠨࡳࡦࡶࠣࡸࡪࡹࡴ࠮ࡵࡷࡥࡷࡺࠠࡧࡱࡵࠤ࡮ࡴࡳࡵࡣࡱࡧࡪࡃࡻࡪࡰࡶࡸࡦࡴࡣࡦ࠰ࡵࡩ࡫࠮ࠩࡾࠢࡨࡺࡪࡴࡴ࠾ࡽࡷࡩࡸࡺ࡟ࡧࡴࡤࡱࡪࡽ࡯ࡳ࡭ࡢࡷࡹࡧࡴࡦࡿ࠱ࠦቭ") + str(test_hook_state) + bstack11l1ll1_opy_ (u"ࠢࠣቮ"))
                elif test_hook_state == bstack1lll1llll11_opy_.POST and not TestFramework.bstack111l1111ll_opy_(instance, TestFramework.bstack1ll1l111l11_opy_):
                    TestFramework.bstack1111l11l11_opy_(instance, TestFramework.bstack1ll1l111l11_opy_, datetime.now(tz=timezone.utc))
                    self.logger.debug(bstack11l1ll1_opy_ (u"ࠣࡵࡨࡸࠥࡺࡥࡴࡶ࠰ࡩࡳࡪࠠࡧࡱࡵࠤ࡮ࡴࡳࡵࡣࡱࡧࡪࡃࡻࡪࡰࡶࡸࡦࡴࡣࡦ࠰ࡵࡩ࡫࠮ࠩࡾࠢࡨࡺࡪࡴࡴ࠾ࡽࡷࡩࡸࡺ࡟ࡧࡴࡤࡱࡪࡽ࡯ࡳ࡭ࡢࡷࡹࡧࡴࡦࡿ࠱ࠦቯ") + str(test_hook_state) + bstack11l1ll1_opy_ (u"ࠤࠥተ"))
            elif test_framework_state == bstack1llll11llll_opy_.STEP:
                if test_hook_state == bstack1lll1llll11_opy_.PRE:
                    PytestBDDFramework.__1l1ll1lllll_opy_(instance, args)
                elif test_hook_state == bstack1lll1llll11_opy_.POST:
                    PytestBDDFramework.__1l1l1ll1111_opy_(instance, args)
            elif test_framework_state == bstack1llll11llll_opy_.LOG and test_hook_state == bstack1lll1llll11_opy_.POST:
                PytestBDDFramework.__1l1ll1lll11_opy_(instance, *args)
            elif test_framework_state == bstack1llll11llll_opy_.LOG_REPORT and test_hook_state == bstack1lll1llll11_opy_.POST:
                self.__1l1ll1ll11l_opy_(instance, *args)
            elif test_framework_state in PytestBDDFramework.bstack1l1l1ll1lll_opy_:
                self.__1l1ll1l1111_opy_(instance, test_framework_state, test_hook_state, *args)
            self.logger.debug(bstack11l1ll1_opy_ (u"ࠥࡸࡷࡧࡣ࡬ࡡࡨࡺࡪࡴࡴ࠻ࠢ࡫ࡥࡳࡪ࡬ࡦࡦࠣࡩࡻ࡫࡮ࡵ࠿ࡾࡸࡪࡹࡴࡠࡨࡵࡥࡲ࡫ࡷࡰࡴ࡮ࡣࡸࡺࡡࡵࡧࢀ࠲ࢀࡺࡥࡴࡶࡢ࡬ࡴࡵ࡫ࡠࡵࡷࡥࡹ࡫ࡽࠡ࡫ࡱࡷࡹࡧ࡮ࡤࡧࡀࠦቱ") + str(instance.ref()) + bstack11l1ll1_opy_ (u"ࠦࠧቲ"))
        except Exception as e:
            self.logger.error(e)
            traceback.print_exc()
        self.bstack1l1lll11111_opy_(instance, (test_framework_state, test_hook_state), *args, **kwargs)
        try:
            if instance!= None and test_framework_state in PytestBDDFramework.bstack1l1l1ll1lll_opy_ and test_hook_state == bstack1lll1llll11_opy_.POST:
                name = str(EVENTS.bstack1lll111l11_opy_.name)+bstack11l1ll1_opy_ (u"ࠧࡀࠢታ")+str(test_framework_state.name)
                bstack1lll11l1l1l_opy_ = TestFramework.bstack1l1ll1111l1_opy_(instance, name)
                bstack1llll111lll_opy_.end(EVENTS.bstack1lll111l11_opy_.value, bstack1lll11l1l1l_opy_+bstack11l1ll1_opy_ (u"ࠨ࠺ࡴࡶࡤࡶࡹࠨቴ"), bstack1lll11l1l1l_opy_+bstack11l1ll1_opy_ (u"ࠢ࠻ࡧࡱࡨࠧት"), True, None, test_framework_state.name)
        except Exception as e:
            self.logger.debug(bstack11l1ll1_opy_ (u"ࠣࡇࡻࡧࡪࡶࡴࡪࡱࡱࠤ࡮ࡴࠠࡩࡱࡲ࡯ࠥ࡫ࡲࡳࡱࡵ࠾ࠥࢁࡽࠣቶ").format(e))
    def bstack1ll11l1ll11_opy_(self):
        return self.bstack1l1l1ll1l1l_opy_
    def __1l1lll11l11_opy_(self, *args):
        if len(args) > 2 and callable(getattr(args[2], bstack11l1ll1_opy_ (u"ࠤࡪࡩࡹࡥࡲࡦࡵࡸࡰࡹࠨቷ"), None)):
            rep = args[2].get_result()
            if rep:
                return TestFramework.bstack1ll11l1l11l_opy_(rep, [bstack11l1ll1_opy_ (u"ࠥࡻ࡭࡫࡮ࠣቸ"), bstack11l1ll1_opy_ (u"ࠦࡴࡻࡴࡤࡱࡰࡩࠧቹ"), bstack11l1ll1_opy_ (u"ࠧࡶࡡࡴࡵࡨࡨࠧቺ"), bstack11l1ll1_opy_ (u"ࠨࡦࡢ࡫࡯ࡩࡩࠨቻ"), bstack11l1ll1_opy_ (u"ࠢࡴ࡭࡬ࡴࡵ࡫ࡤࠣቼ"), bstack11l1ll1_opy_ (u"ࠣ࡮ࡲࡲ࡬ࡸࡥࡱࡴࡷࡩࡽࡺࠢች")])
        return None
    def __1l1ll1ll11l_opy_(self, instance: bstack11111l1l11_opy_, *args):
        result = self.__1l1lll11l11_opy_(*args)
        if not result:
            return
        failure = None
        bstack111l1l1111_opy_ = None
        if result.get(bstack11l1ll1_opy_ (u"ࠤࡲࡹࡹࡩ࡯࡮ࡧࠥቾ"), None) == bstack11l1ll1_opy_ (u"ࠥࡪࡦ࡯࡬ࡦࡦࠥቿ") and len(args) > 1 and getattr(args[1], bstack11l1ll1_opy_ (u"ࠦࡪࡾࡣࡪࡰࡩࡳࠧኀ"), None) is not None:
            failure = [{bstack11l1ll1_opy_ (u"ࠬࡨࡡࡤ࡭ࡷࡶࡦࡩࡥࠨኁ"): [args[1].excinfo.exconly(), result.get(bstack11l1ll1_opy_ (u"ࠨ࡬ࡰࡰࡪࡶࡪࡶࡲࡵࡧࡻࡸࠧኂ"), None)]}]
            bstack111l1l1111_opy_ = bstack11l1ll1_opy_ (u"ࠢࡂࡵࡶࡩࡷࡺࡩࡰࡰࡈࡶࡷࡵࡲࠣኃ") if bstack11l1ll1_opy_ (u"ࠣࡃࡶࡷࡪࡸࡴࡪࡱࡱࠦኄ") in getattr(args[1].excinfo, bstack11l1ll1_opy_ (u"ࠤࡷࡽࡵ࡫࡮ࡢ࡯ࡨࠦኅ"), bstack11l1ll1_opy_ (u"ࠥࠦኆ")) else bstack11l1ll1_opy_ (u"࡚ࠦࡴࡨࡢࡰࡧࡰࡪࡪࡅࡳࡴࡲࡶࠧኇ")
        bstack1l1l1l1l11l_opy_ = result.get(bstack11l1ll1_opy_ (u"ࠧࡵࡵࡵࡥࡲࡱࡪࠨኈ"), TestFramework.bstack1l1l1l1ll1l_opy_)
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
            target = None # bstack1l1ll1ll111_opy_ bstack1l1ll11l1l1_opy_ this to be bstack11l1ll1_opy_ (u"ࠨ࡮ࡰࡦࡨ࡭ࡩࠨ኉")
            if test_framework_state == bstack1llll11llll_opy_.INIT_TEST:
                target = args[0] if isinstance(args[0], str) else None
                if target:
                    self.__1l1lll11l1l_opy_(context, test_framework_state, target, *args)
            elif test_framework_state == bstack1llll11llll_opy_.LOG:
                nodeid = getattr(getattr(args[0], bstack11l1ll1_opy_ (u"ࠢ࡯ࡱࡧࡩࠧኊ"), None), bstack11l1ll1_opy_ (u"ࠣࡰࡲࡨࡪ࡯ࡤࠣኋ"), None) if args else None
                if isinstance(nodeid, str):
                    target = nodeid
            elif getattr(args[0], bstack11l1ll1_opy_ (u"ࠤࡱࡳࡩ࡫ࠢኌ"), None):
                target = args[0].node.nodeid
            elif getattr(args[0], bstack11l1ll1_opy_ (u"ࠥࡲࡴࡪࡥࡪࡦࠥኍ"), None):
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
        bstack1l1ll111l1l_opy_ = TestFramework.bstack111l111111_opy_(instance, PytestBDDFramework.bstack1l1l1lll1l1_opy_, {})
        if not key in bstack1l1ll111l1l_opy_:
            bstack1l1ll111l1l_opy_[key] = []
        bstack1l1l1l1llll_opy_ = TestFramework.bstack111l111111_opy_(instance, PytestBDDFramework.bstack1l1ll1lll1l_opy_, {})
        if not key in bstack1l1l1l1llll_opy_:
            bstack1l1l1l1llll_opy_[key] = []
        bstack1l1ll11lll1_opy_ = {
            PytestBDDFramework.bstack1l1l1lll1l1_opy_: bstack1l1ll111l1l_opy_,
            PytestBDDFramework.bstack1l1ll1lll1l_opy_: bstack1l1l1l1llll_opy_,
        }
        if test_hook_state == bstack1lll1llll11_opy_.PRE:
            hook_name = args[1] if len(args) > 1 else None
            hook = {
                bstack11l1ll1_opy_ (u"ࠦࡰ࡫ࡹࠣ኎"): key,
                TestFramework.bstack1l1ll11llll_opy_: uuid4().__str__(),
                TestFramework.bstack1l1l1l1lll1_opy_: TestFramework.bstack1l1lll111ll_opy_,
                TestFramework.bstack1l1l1ll11l1_opy_: datetime.now(tz=timezone.utc),
                TestFramework.bstack1l1ll1llll1_opy_: [],
                TestFramework.bstack1l1ll1l111l_opy_: hook_name
            }
            bstack1l1ll111l1l_opy_[key].append(hook)
            bstack1l1ll11lll1_opy_[PytestBDDFramework.bstack1l1lll11ll1_opy_] = key
        elif test_hook_state == bstack1lll1llll11_opy_.POST:
            bstack1l1ll111l11_opy_ = bstack1l1ll111l1l_opy_.get(key, [])
            hook = bstack1l1ll111l11_opy_.pop() if bstack1l1ll111l11_opy_ else None
            if hook:
                result = self.__1l1lll11l11_opy_(*args)
                if result:
                    bstack1l1l1ll11ll_opy_ = result.get(bstack11l1ll1_opy_ (u"ࠧࡵࡵࡵࡥࡲࡱࡪࠨ኏"), TestFramework.bstack1l1lll111ll_opy_)
                    if bstack1l1l1ll11ll_opy_ != TestFramework.bstack1l1lll111ll_opy_:
                        hook[TestFramework.bstack1l1l1l1lll1_opy_] = bstack1l1l1ll11ll_opy_
                hook[TestFramework.bstack1l1ll11l111_opy_] = datetime.now(tz=timezone.utc)
                bstack1l1l1l1llll_opy_[key].append(hook)
                bstack1l1ll11lll1_opy_[PytestBDDFramework.bstack1l1ll1111ll_opy_] = key
        TestFramework.bstack1l1l1l1l111_opy_(instance, bstack1l1ll11lll1_opy_)
        self.logger.debug(bstack11l1ll1_opy_ (u"ࠨࡴࡳࡣࡦ࡯ࡤ࡮࡯ࡰ࡭ࡢࡩࡻ࡫࡮ࡵ࠼ࠣࡸࡪࡹࡴࡠࡪࡲࡳࡰࡥࡳࡵࡣࡷࡩࡂࢁ࡫ࡦࡻࢀ࠲ࢀࡺࡥࡴࡶࡢ࡬ࡴࡵ࡫ࡠࡵࡷࡥࡹ࡫ࡽࠡࡪࡲࡳࡰࡹ࡟ࡴࡶࡤࡶࡹ࡫ࡤ࠾ࡽ࡫ࡳࡴࡱࡳࡠࡵࡷࡥࡷࡺࡥࡥࡿࠣ࡬ࡴࡵ࡫ࡴࡡࡩ࡭ࡳ࡯ࡳࡩࡧࡧࡁࠧነ") + str(bstack1l1l1l1llll_opy_) + bstack11l1ll1_opy_ (u"ࠢࠣኑ"))
    def __1l1lll1111l_opy_(
        self,
        context: bstack1l1l1l11lll_opy_,
        test_framework_state: bstack1llll11llll_opy_,
        test_hook_state: bstack1lll1llll11_opy_,
        *args,
        **kwargs,
    ):
        fixturedef = TestFramework.bstack1ll11l1l11l_opy_(args[0], [bstack11l1ll1_opy_ (u"ࠣࡵࡦࡳࡵ࡫ࠢኒ"), bstack11l1ll1_opy_ (u"ࠤࡤࡶ࡬ࡴࡡ࡮ࡧࠥና"), bstack11l1ll1_opy_ (u"ࠥࡴࡦࡸࡡ࡮ࡵࠥኔ"), bstack11l1ll1_opy_ (u"ࠦ࡮ࡪࡳࠣን"), bstack11l1ll1_opy_ (u"ࠧࡻ࡮ࡪࡶࡷࡩࡸࡺࠢኖ"), bstack11l1ll1_opy_ (u"ࠨࡢࡢࡵࡨ࡭ࡩࠨኗ")]) if len(args) > 0 else {}
        request = args[0] if len(args) > 1 else None
        scenario = args[2] if len(args) == 3 else None
        scope = request.scope if hasattr(request, bstack11l1ll1_opy_ (u"ࠢࡴࡥࡲࡴࡪࠨኘ")) else fixturedef.get(bstack11l1ll1_opy_ (u"ࠣࡵࡦࡳࡵ࡫ࠢኙ"), None)
        fixturename = request.fixturename if hasattr(request, bstack11l1ll1_opy_ (u"ࠤࡩ࡭ࡽࡺࡵࡳࡧࡱࡥࡲ࡫ࠢኚ")) else None
        node = request.node if hasattr(request, bstack11l1ll1_opy_ (u"ࠥࡲࡴࡪࡥࠣኛ")) else None
        target = request.node.nodeid if hasattr(node, bstack11l1ll1_opy_ (u"ࠦࡳࡵࡤࡦ࡫ࡧࠦኜ")) else None
        baseid = fixturedef.get(bstack11l1ll1_opy_ (u"ࠧࡨࡡࡴࡧ࡬ࡨࠧኝ"), None) or bstack11l1ll1_opy_ (u"ࠨࠢኞ")
        if (not target or len(baseid) > 0) and hasattr(request, bstack11l1ll1_opy_ (u"ࠢࡠࡲࡼࡪࡺࡴࡣࡪࡶࡨࡱࠧኟ")):
            target = PytestBDDFramework.__1l1l1llllll_opy_(request._pyfuncitem.location) if hasattr(request._pyfuncitem, bstack11l1ll1_opy_ (u"ࠣ࡮ࡲࡧࡦࡺࡩࡰࡰࠥአ")) else None
            if target and not TestFramework.bstack1111llllll_opy_(target):
                self.__1l1lll11l1l_opy_(context, test_framework_state, target, (target, request._pyfuncitem.location))
                node = request._pyfuncitem
                self.logger.debug(bstack11l1ll1_opy_ (u"ࠤࡷࡶࡦࡩ࡫ࡠࡨ࡬ࡼࡹࡻࡲࡦࡡࡨࡺࡪࡴࡴ࠻ࠢࡩࡥࡱࡲࡢࡢࡥ࡮ࠤࡹࡧࡲࡨࡧࡷࡁࢀࡺࡡࡳࡩࡨࡸࢂࠦࡦࡪࡺࡷࡹࡷ࡫࡮ࡢ࡯ࡨࡁࢀ࡬ࡩࡹࡶࡸࡶࡪࡴࡡ࡮ࡧࢀࠤࡳࡵࡤࡦ࠿ࡾࡲࡴࡪࡥࡾࠢࡨࡺࡪࡴࡴ࠾ࡽࡷࡩࡸࡺ࡟ࡧࡴࡤࡱࡪࡽ࡯ࡳ࡭ࡢࡷࡹࡧࡴࡦࡿ࠱ࠦኡ") + str(test_hook_state) + bstack11l1ll1_opy_ (u"ࠥࠦኢ"))
        if not fixturedef or not scope or not target:
            self.logger.warning(bstack11l1ll1_opy_ (u"ࠦࡹࡸࡡࡤ࡭ࡢࡪ࡮ࡾࡴࡶࡴࡨࡣࡪࡼࡥ࡯ࡶ࠽ࠤࡺࡴࡨࡢࡰࡧࡰࡪࡪࠠࡦࡸࡨࡲࡹࡃࡻࡵࡧࡶࡸࡤ࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫ࡠࡵࡷࡥࡹ࡫ࡽ࠯ࡽࡷࡩࡸࡺ࡟ࡩࡱࡲ࡯ࡤࡹࡴࡢࡶࡨࢁࠥ࡬ࡩࡹࡶࡸࡶࡪࡪࡥࡧ࠿ࡾࡪ࡮ࡾࡴࡶࡴࡨࡨࡪ࡬ࡽࠡࡵࡦࡳࡵ࡫࠽ࡼࡵࡦࡳࡵ࡫ࡽࠡࡶࡤࡶ࡬࡫ࡴ࠾ࠤኣ") + str(target) + bstack11l1ll1_opy_ (u"ࠧࠨኤ"))
            return None
        instance = TestFramework.bstack1111llllll_opy_(target)
        if not instance:
            self.logger.warning(bstack11l1ll1_opy_ (u"ࠨࡴࡳࡣࡦ࡯ࡤ࡬ࡩࡹࡶࡸࡶࡪࡥࡥࡷࡧࡱࡸ࠿ࠦࡵ࡯ࡪࡤࡲࡩࡲࡥࡥࠢࡨࡺࡪࡴࡴ࠾ࡽࡷࡩࡸࡺ࡟ࡧࡴࡤࡱࡪࡽ࡯ࡳ࡭ࡢࡷࡹࡧࡴࡦࡿ࠱ࡿࡹ࡫ࡳࡵࡡ࡫ࡳࡴࡱ࡟ࡴࡶࡤࡸࡪࢃࠠࡧ࡫ࡻࡸࡺࡸࡥ࡯ࡣࡰࡩࡂࢁࡦࡪࡺࡷࡹࡷ࡫࡮ࡢ࡯ࡨࢁࠥࡹࡣࡰࡲࡨࡁࢀࡹࡣࡰࡲࡨࢁࠥࡨࡡࡴࡧ࡬ࡨࡂࢁࡢࡢࡵࡨ࡭ࡩࢃࠠࡵࡣࡵ࡫ࡪࡺ࠽ࠣእ") + str(target) + bstack11l1ll1_opy_ (u"ࠢࠣኦ"))
            return None
        bstack1l1l1lll11l_opy_ = TestFramework.bstack111l111111_opy_(instance, PytestBDDFramework.bstack1l1ll111lll_opy_, {})
        if os.getenv(bstack11l1ll1_opy_ (u"ࠣࡕࡇࡏࡤࡉࡌࡊࡡࡉࡐࡆࡍ࡟ࡇࡋ࡛ࡘ࡚ࡘࡅࡔࠤኧ"), bstack11l1ll1_opy_ (u"ࠤ࠴ࠦከ")) == bstack11l1ll1_opy_ (u"ࠥ࠵ࠧኩ"):
            bstack1l1lll11lll_opy_ = bstack11l1ll1_opy_ (u"ࠦ࠿ࠨኪ").join((scope, fixturename))
            bstack1l1l1ll1ll1_opy_ = datetime.now(tz=timezone.utc)
            bstack1l1l1l1l1ll_opy_ = {
                bstack11l1ll1_opy_ (u"ࠧࡱࡥࡺࠤካ"): bstack1l1lll11lll_opy_,
                bstack11l1ll1_opy_ (u"ࠨࡴࡢࡩࡶࠦኬ"): PytestBDDFramework.__1l1ll1l11ll_opy_(request.node, scenario),
                bstack11l1ll1_opy_ (u"ࠢࡧ࡫ࡻࡸࡺࡸࡥࠣክ"): fixturedef,
                bstack11l1ll1_opy_ (u"ࠣࡵࡦࡳࡵ࡫ࠢኮ"): scope,
                bstack11l1ll1_opy_ (u"ࠤࡷࡽࡵ࡫ࠢኯ"): None,
            }
            try:
                if test_hook_state == bstack1lll1llll11_opy_.POST and callable(getattr(args[-1], bstack11l1ll1_opy_ (u"ࠥ࡫ࡪࡺ࡟ࡳࡧࡶࡹࡱࡺࠢኰ"), None)):
                    bstack1l1l1l1l1ll_opy_[bstack11l1ll1_opy_ (u"ࠦࡹࡿࡰࡦࠤ኱")] = TestFramework.bstack1ll1l111111_opy_(args[-1].get_result())
            except Exception as e:
                pass
            if test_hook_state == bstack1lll1llll11_opy_.PRE:
                bstack1l1l1l1l1ll_opy_[bstack11l1ll1_opy_ (u"ࠧࡻࡵࡪࡦࠥኲ")] = uuid4().__str__()
                bstack1l1l1l1l1ll_opy_[PytestBDDFramework.bstack1l1l1ll11l1_opy_] = bstack1l1l1ll1ll1_opy_
            elif test_hook_state == bstack1lll1llll11_opy_.POST:
                bstack1l1l1l1l1ll_opy_[PytestBDDFramework.bstack1l1ll11l111_opy_] = bstack1l1l1ll1ll1_opy_
            if bstack1l1lll11lll_opy_ in bstack1l1l1lll11l_opy_:
                bstack1l1l1lll11l_opy_[bstack1l1lll11lll_opy_].update(bstack1l1l1l1l1ll_opy_)
                self.logger.debug(bstack11l1ll1_opy_ (u"ࠨࡵࡱࡦࡤࡸࡪࡪࠠࡧ࡫ࡻࡸࡺࡸࡥ࡯ࡣࡰࡩࡂࢁࡦࡪࡺࡷࡹࡷ࡫࡮ࡢ࡯ࡨࢁࠥࡹࡣࡰࡲࡨࡁࢀࡹࡣࡰࡲࡨࢁࠥ࡬ࡩࡹࡶࡸࡶࡪࡃࠢኳ") + str(bstack1l1l1lll11l_opy_[bstack1l1lll11lll_opy_]) + bstack11l1ll1_opy_ (u"ࠢࠣኴ"))
            else:
                bstack1l1l1lll11l_opy_[bstack1l1lll11lll_opy_] = bstack1l1l1l1l1ll_opy_
                self.logger.debug(bstack11l1ll1_opy_ (u"ࠣࡵࡤࡺࡪࡪࠠࡧ࡫ࡻࡸࡺࡸࡥ࡯ࡣࡰࡩࡂࢁࡦࡪࡺࡷࡹࡷ࡫࡮ࡢ࡯ࡨࢁࠥࡹࡣࡰࡲࡨࡁࢀࡹࡣࡰࡲࡨࢁࠥ࡬ࡩࡹࡶࡸࡶࡪࡃࡻࡵࡧࡶࡸࡤ࡬ࡩࡹࡶࡸࡶࡪࢃࠠࡵࡴࡤࡧࡰ࡫ࡤࡠࡨ࡬ࡼࡹࡻࡲࡦࡵࡀࠦኵ") + str(len(bstack1l1l1lll11l_opy_)) + bstack11l1ll1_opy_ (u"ࠤࠥ኶"))
        TestFramework.bstack1111l11l11_opy_(instance, PytestBDDFramework.bstack1l1ll111lll_opy_, bstack1l1l1lll11l_opy_)
        self.logger.debug(bstack11l1ll1_opy_ (u"ࠥࡷࡦࡼࡥࡥࠢࡩ࡭ࡽࡺࡵࡳࡧࡶࡁࢀࡲࡥ࡯ࠪࡷࡶࡦࡩ࡫ࡦࡦࡢࡪ࡮ࡾࡴࡶࡴࡨࡷ࠮ࢃࠠࡪࡰࡶࡸࡦࡴࡣࡦ࠿ࠥ኷") + str(instance.ref()) + bstack11l1ll1_opy_ (u"ࠦࠧኸ"))
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
            PytestBDDFramework.bstack1l1ll111lll_opy_: {},
            PytestBDDFramework.bstack1l1ll1lll1l_opy_: {},
            PytestBDDFramework.bstack1l1l1lll1l1_opy_: {},
        })
        if len(args) > 1 and isinstance(args[1], tuple):
            TestFramework.bstack1111l11l11_opy_(ob, TestFramework.bstack1l1l1llll1l_opy_, str(args[1][0]))
        if context.platform_index >= 0:
            TestFramework.bstack1111l11l11_opy_(ob, TestFramework.bstack1lll11ll1l1_opy_, context.platform_index)
        TestFramework.bstack1111l1ll11_opy_[ctx.id] = ob
        self.logger.debug(bstack11l1ll1_opy_ (u"ࠧࡹࡡࡷࡧࡧࠤ࡮ࡴࡳࡵࡣࡱࡧࡪࠦࡣࡵࡺ࠱࡭ࡩࡃࡻࡤࡶࡻ࠲࡮ࡪࡽࠡࡶࡤࡶ࡬࡫ࡴ࠾ࡽࡷࡥࡷ࡭ࡥࡵࡿࠣࡥࡷ࡭ࡳ࠾ࡽࡤࡶ࡬ࡹࡽࠡ࡫ࡱࡷࡹࡧ࡮ࡤࡧࡶࡁࠧኹ") + str(TestFramework.bstack1111l1ll11_opy_.keys()) + bstack11l1ll1_opy_ (u"ࠨࠢኺ"))
        return ob
    @staticmethod
    def __1l1l1l111ll_opy_(instance, args):
        request, feature, scenario = args
        steps = []
        for step in scenario.steps:
            steps.append({
                bstack11l1ll1_opy_ (u"ࠧࡪࡦࠪኻ"): id(step),
                bstack11l1ll1_opy_ (u"ࠨࡶࡨࡼࡹ࠭ኼ"): step.name,
                bstack11l1ll1_opy_ (u"ࠩ࡮ࡩࡾࡽ࡯ࡳࡦࠪኽ"): step.keyword,
            })
        meta = {
            bstack11l1ll1_opy_ (u"ࠪࡪࡪࡧࡴࡶࡴࡨࠫኾ"): {
                bstack11l1ll1_opy_ (u"ࠫࡳࡧ࡭ࡦࠩ኿"): feature.name,
                bstack11l1ll1_opy_ (u"ࠬࡶࡡࡵࡪࠪዀ"): feature.filename,
                bstack11l1ll1_opy_ (u"࠭ࡤࡦࡵࡦࡶ࡮ࡶࡴࡪࡱࡱࠫ዁"): feature.description
            },
            bstack11l1ll1_opy_ (u"ࠧࡴࡥࡨࡲࡦࡸࡩࡰࠩዂ"): {
                bstack11l1ll1_opy_ (u"ࠨࡰࡤࡱࡪ࠭ዃ"): scenario.name
            },
            bstack11l1ll1_opy_ (u"ࠩࡶࡸࡪࡶࡳࠨዄ"): steps,
            bstack11l1ll1_opy_ (u"ࠪࡩࡽࡧ࡭ࡱ࡮ࡨࡷࠬዅ"): PytestBDDFramework.__1l1lll1l11l_opy_(request.node)
        }
        instance.data.update(
            {
                TestFramework.bstack1l1l1l1l1l1_opy_: meta
            }
        )
    @staticmethod
    def __1l1ll1lllll_opy_(instance, args):
        request, bstack1l1ll1l1ll1_opy_ = args
        bstack1l1l1ll1l11_opy_ = id(bstack1l1ll1l1ll1_opy_)
        bstack1l1ll1l11l1_opy_ = instance.data[TestFramework.bstack1l1l1l1l1l1_opy_]
        step = next(filter(lambda st: st[bstack11l1ll1_opy_ (u"ࠫ࡮ࡪࠧ዆")] == bstack1l1l1ll1l11_opy_, bstack1l1ll1l11l1_opy_[bstack11l1ll1_opy_ (u"ࠬࡹࡴࡦࡲࡶࠫ዇")]), None)
        step.update({
            bstack11l1ll1_opy_ (u"࠭ࡳࡵࡣࡵࡸࡪࡪ࡟ࡢࡶࠪወ"): datetime.now(tz=timezone.utc)
        })
        index = next((i for i, st in enumerate(bstack1l1ll1l11l1_opy_[bstack11l1ll1_opy_ (u"ࠧࡴࡶࡨࡴࡸ࠭ዉ")]) if st[bstack11l1ll1_opy_ (u"ࠨ࡫ࡧࠫዊ")] == step[bstack11l1ll1_opy_ (u"ࠩ࡬ࡨࠬዋ")]), None)
        if index is not None:
            bstack1l1ll1l11l1_opy_[bstack11l1ll1_opy_ (u"ࠪࡷࡹ࡫ࡰࡴࠩዌ")][index] = step
        instance.data[TestFramework.bstack1l1l1l1l1l1_opy_] = bstack1l1ll1l11l1_opy_
    @staticmethod
    def __1l1l1ll1111_opy_(instance, args):
        bstack11l1ll1_opy_ (u"ࠦࠧࠨࠊࠡࠢࠣࠤࠥࠦࠠࠡࡹ࡫ࡩࡳࠦ࡬ࡦࡰࠣࡥࡷ࡭ࡳࠡ࡫ࡶࠤ࠷࠲ࠠࡪࡶࠣࡷ࡮࡭࡮ࡪࡨ࡬ࡩࡸࠦࡴࡩࡧࡵࡩࠥ࡯ࡳࠡࡰࡲࠤࡪࡾࡣࡦࡲࡷ࡭ࡴࡴࠊࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࡧࡲࡨࡵࠣࡥࡷ࡫ࠠ࠮ࠢ࡞ࡶࡪࡷࡵࡦࡵࡷ࠰ࠥࡹࡴࡦࡲࡠࠎࠥࠦࠠࠡࠢࠣࠤࠥ࡯ࡦࠡࡣࡵ࡫ࡸࠦࡡࡳࡧࠣ࠷ࠥࡺࡨࡦࡰࠣࡸ࡭࡫ࠠ࡭ࡣࡶࡸࠥࡼࡡ࡭ࡷࡨࠤ࡮ࡹࠠࡦࡺࡦࡩࡵࡺࡩࡰࡰࠍࠤࠥࠦࠠࠡࠢࠣࠤࠧࠨࠢው")
        bstack1l1ll11l11l_opy_ = datetime.now(tz=timezone.utc)
        request = args[0]
        bstack1l1ll1l1ll1_opy_ = args[1]
        bstack1l1l1ll1l11_opy_ = id(bstack1l1ll1l1ll1_opy_)
        bstack1l1ll1l11l1_opy_ = instance.data[TestFramework.bstack1l1l1l1l1l1_opy_]
        step = None
        if bstack1l1l1ll1l11_opy_ is not None and bstack1l1ll1l11l1_opy_.get(bstack11l1ll1_opy_ (u"ࠬࡹࡴࡦࡲࡶࠫዎ")):
            step = next(filter(lambda st: st[bstack11l1ll1_opy_ (u"࠭ࡩࡥࠩዏ")] == bstack1l1l1ll1l11_opy_, bstack1l1ll1l11l1_opy_[bstack11l1ll1_opy_ (u"ࠧࡴࡶࡨࡴࡸ࠭ዐ")]), None)
            step.update({
                bstack11l1ll1_opy_ (u"ࠨࡨ࡬ࡲ࡮ࡹࡨࡦࡦࡢࡥࡹ࠭ዑ"): bstack1l1ll11l11l_opy_,
            })
        if len(args) > 2:
            exception = args[2]
            step.update({
                bstack11l1ll1_opy_ (u"ࠩࡵࡩࡸࡻ࡬ࡵࠩዒ"): bstack11l1ll1_opy_ (u"ࠪࡪࡦ࡯࡬ࡦࡦࠪዓ"),
                bstack11l1ll1_opy_ (u"ࠫ࡫ࡧࡩ࡭ࡷࡵࡩࠬዔ"): str(exception)
            })
        else:
            if step is not None:
                step.update({
                    bstack11l1ll1_opy_ (u"ࠬࡸࡥࡴࡷ࡯ࡸࠬዕ"): bstack11l1ll1_opy_ (u"࠭ࡰࡢࡵࡶࡩࡩ࠭ዖ"),
                })
        index = next((i for i, st in enumerate(bstack1l1ll1l11l1_opy_[bstack11l1ll1_opy_ (u"ࠧࡴࡶࡨࡴࡸ࠭዗")]) if st[bstack11l1ll1_opy_ (u"ࠨ࡫ࡧࠫዘ")] == step[bstack11l1ll1_opy_ (u"ࠩ࡬ࡨࠬዙ")]), None)
        if index is not None:
            bstack1l1ll1l11l1_opy_[bstack11l1ll1_opy_ (u"ࠪࡷࡹ࡫ࡰࡴࠩዚ")][index] = step
        instance.data[TestFramework.bstack1l1l1l1l1l1_opy_] = bstack1l1ll1l11l1_opy_
    @staticmethod
    def __1l1lll1l11l_opy_(node):
        try:
            examples = []
            if hasattr(node, bstack11l1ll1_opy_ (u"ࠫࡨࡧ࡬࡭ࡵࡳࡩࡨ࠭ዛ")):
                examples = list(node.callspec.params[bstack11l1ll1_opy_ (u"ࠬࡥࡰࡺࡶࡨࡷࡹࡥࡢࡥࡦࡢࡩࡽࡧ࡭ࡱ࡮ࡨࠫዜ")].values())
            return examples
        except:
            return []
    def bstack1ll11l1l111_opy_(self, instance: bstack11111l1l11_opy_, bstack111l111l1l_opy_: Tuple[bstack1llll11llll_opy_, bstack1lll1llll11_opy_]):
        bstack1l1ll111111_opy_ = (
            PytestBDDFramework.bstack1l1lll11ll1_opy_
            if bstack111l111l1l_opy_[1] == bstack1lll1llll11_opy_.PRE
            else PytestBDDFramework.bstack1l1ll1111ll_opy_
        )
        hook = PytestBDDFramework.bstack1l1ll1l1l1l_opy_(instance, bstack1l1ll111111_opy_)
        entries = hook.get(TestFramework.bstack1l1ll1llll1_opy_, []) if isinstance(hook, dict) else []
        entries.extend(TestFramework.bstack111l111111_opy_(instance, TestFramework.bstack1l1ll1l1lll_opy_, []))
        return entries
    def bstack1ll1l1111l1_opy_(self, instance: bstack11111l1l11_opy_, bstack111l111l1l_opy_: Tuple[bstack1llll11llll_opy_, bstack1lll1llll11_opy_]):
        bstack1l1ll111111_opy_ = (
            PytestBDDFramework.bstack1l1lll11ll1_opy_
            if bstack111l111l1l_opy_[1] == bstack1lll1llll11_opy_.PRE
            else PytestBDDFramework.bstack1l1ll1111ll_opy_
        )
        PytestBDDFramework.bstack1l1ll11ll1l_opy_(instance, bstack1l1ll111111_opy_)
        TestFramework.bstack111l111111_opy_(instance, TestFramework.bstack1l1ll1l1lll_opy_, []).clear()
    @staticmethod
    def bstack1l1ll1l1l1l_opy_(instance: bstack11111l1l11_opy_, bstack1l1ll111111_opy_: str):
        bstack1l1ll11ll11_opy_ = (
            PytestBDDFramework.bstack1l1ll1lll1l_opy_
            if bstack1l1ll111111_opy_ == PytestBDDFramework.bstack1l1ll1111ll_opy_
            else PytestBDDFramework.bstack1l1l1lll1l1_opy_
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
        hook = PytestBDDFramework.bstack1l1ll1l1l1l_opy_(instance, bstack1l1ll111111_opy_)
        if isinstance(hook, dict):
            hook.get(TestFramework.bstack1l1ll1llll1_opy_, []).clear()
    @staticmethod
    def __1l1ll1lll11_opy_(instance: bstack11111l1l11_opy_, *args):
        if len(args) < 2 or not callable(getattr(args[1], bstack11l1ll1_opy_ (u"ࠨࡧࡦࡶࡢࡶࡪࡩ࡯ࡳࡦࡶࠦዝ"), None)):
            return
        if os.getenv(bstack11l1ll1_opy_ (u"ࠢࡔࡆࡎࡣࡈࡒࡉࡠࡈࡏࡅࡌࡥࡌࡐࡉࡖࠦዞ"), bstack11l1ll1_opy_ (u"ࠣ࠳ࠥዟ")) != bstack11l1ll1_opy_ (u"ࠤ࠴ࠦዠ"):
            PytestBDDFramework.logger.warning(bstack11l1ll1_opy_ (u"ࠥ࡭࡬ࡴ࡯ࡳ࡫ࡱ࡫ࠥࡩࡡࡱ࡮ࡲ࡫ࠧዡ"))
            return
        bstack1l1l1ll111l_opy_ = {
            bstack11l1ll1_opy_ (u"ࠦࡸ࡫ࡴࡶࡲࠥዢ"): (PytestBDDFramework.bstack1l1lll11ll1_opy_, PytestBDDFramework.bstack1l1l1lll1l1_opy_),
            bstack11l1ll1_opy_ (u"ࠧࡺࡥࡢࡴࡧࡳࡼࡴࠢዣ"): (PytestBDDFramework.bstack1l1ll1111ll_opy_, PytestBDDFramework.bstack1l1ll1lll1l_opy_),
        }
        for when in (bstack11l1ll1_opy_ (u"ࠨࡳࡦࡶࡸࡴࠧዤ"), bstack11l1ll1_opy_ (u"ࠢࡤࡣ࡯ࡰࠧዥ"), bstack11l1ll1_opy_ (u"ࠣࡶࡨࡥࡷࡪ࡯ࡸࡰࠥዦ")):
            bstack1l1l1l11l11_opy_ = args[1].get_records(when)
            if not bstack1l1l1l11l11_opy_:
                continue
            records = [
                bstack1llll111ll1_opy_(
                    kind=TestFramework.bstack1ll1ll1111l_opy_,
                    message=r.message,
                    level=r.levelname if hasattr(r, bstack11l1ll1_opy_ (u"ࠤ࡯ࡩࡻ࡫࡬࡯ࡣࡰࡩࠧዧ")) and r.levelname else None,
                    timestamp=(
                        datetime.fromtimestamp(r.created, tz=timezone.utc)
                        if hasattr(r, bstack11l1ll1_opy_ (u"ࠥࡧࡷ࡫ࡡࡵࡧࡧࠦየ")) and r.created
                        else None
                    ),
                )
                for r in bstack1l1l1l11l11_opy_
                if isinstance(getattr(r, bstack11l1ll1_opy_ (u"ࠦࡲ࡫ࡳࡴࡣࡪࡩࠧዩ"), None), str) and r.message.strip()
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
    def __1l1l1lll1ll_opy_(args) -> Dict[str, Any]:
        request, feature, scenario = args
        bstack1ll1lllll_opy_ = request.node.nodeid
        test_name = PytestBDDFramework.__1l1ll111ll1_opy_(request.node, scenario)
        bstack1l1l1l1ll11_opy_ = feature.filename
        if not bstack1ll1lllll_opy_ or not test_name or not bstack1l1l1l1ll11_opy_:
            return None
        code = None
        return {
            TestFramework.bstack1lll111l1l1_opy_: uuid4().__str__(),
            TestFramework.bstack1l1l1llll11_opy_: bstack1ll1lllll_opy_,
            TestFramework.bstack1lll11ll111_opy_: test_name,
            TestFramework.bstack1ll11l11l1l_opy_: bstack1ll1lllll_opy_,
            TestFramework.bstack1l1l1lll111_opy_: bstack1l1l1l1ll11_opy_,
            TestFramework.bstack1l1l1l11ll1_opy_: PytestBDDFramework.__1l1ll1l11ll_opy_(feature, scenario),
            TestFramework.bstack1l1ll1ll1l1_opy_: code,
            TestFramework.bstack1l1lll1ll11_opy_: TestFramework.bstack1l1l1l1ll1l_opy_,
            TestFramework.bstack1l1llll1l11_opy_: test_name
        }
    @staticmethod
    def __1l1ll111ll1_opy_(node, scenario):
        if hasattr(node, bstack11l1ll1_opy_ (u"ࠬࡩࡡ࡭࡮ࡶࡴࡪࡩࠧዪ")):
            parts = node.nodeid.rsplit(bstack11l1ll1_opy_ (u"ࠨ࡛ࠣያ"))
            params = parts[-1]
            return bstack11l1ll1_opy_ (u"ࠢࡼࡿࠣ࡟ࢀࢃࠢዬ").format(scenario.name, params)
        return scenario.name
    @staticmethod
    def __1l1ll1l11ll_opy_(feature, scenario) -> List[str]:
        return list(feature.tags) + list(scenario.tags)
    @staticmethod
    def __1l1l1llllll_opy_(location):
        return bstack11l1ll1_opy_ (u"ࠣ࠼࠽ࠦይ").join(filter(lambda x: isinstance(x, str), location))