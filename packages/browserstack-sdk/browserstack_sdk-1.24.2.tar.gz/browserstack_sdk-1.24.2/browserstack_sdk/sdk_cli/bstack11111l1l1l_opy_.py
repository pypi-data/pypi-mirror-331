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
from datetime import datetime, timezone
import os
from typing import Any, Tuple, Callable, List
from browserstack_sdk.sdk_cli.bstack1111ll1l11_opy_ import bstack1111l11l1l_opy_, bstack1111ll111l_opy_, bstack1111l1l1l1_opy_
from browserstack_sdk.sdk_cli.bstack1llll11111l_opy_ import bstack1111111l1l_opy_
from browserstack_sdk.sdk_cli.bstack1lllll1l1l1_opy_ import bstack1llll111l11_opy_
from browserstack_sdk.sdk_cli.bstack1111111lll_opy_ import bstack1llllllll1l_opy_
from browserstack_sdk.sdk_cli.test_framework import TestFramework, bstack1llll11llll_opy_, bstack11111l1l11_opy_, bstack1lll1llll11_opy_, bstack1llll111ll1_opy_
from json import dumps, JSONEncoder
import grpc
from browserstack_sdk import sdk_pb2 as structs
import sys
import traceback
import time
import json
from bstack_utils.helper import bstack1ll1l1l11ll_opy_
from bstack_utils.measure import measure
from bstack_utils.constants import *
bstack1ll1l1111ll_opy_ = [bstack11l1ll1_opy_ (u"ࠣࡰࡤࡱࡪࠨᅞ"), bstack11l1ll1_opy_ (u"ࠤࡳࡥࡷ࡫࡮ࡵࠤᅟ"), bstack11l1ll1_opy_ (u"ࠥࡧࡴࡴࡦࡪࡩࠥᅠ"), bstack11l1ll1_opy_ (u"ࠦࡸ࡫ࡳࡴ࡫ࡲࡲࠧᅡ"), bstack11l1ll1_opy_ (u"ࠧࡶࡡࡵࡪࠥᅢ")]
bstack1ll1l11l1ll_opy_ = {
    bstack11l1ll1_opy_ (u"ࠨࡰࡺࡶࡨࡷࡹ࠴ࡰࡺࡶ࡫ࡳࡳ࠴ࡉࡵࡧࡰࠦᅣ"): bstack1ll1l1111ll_opy_,
    bstack11l1ll1_opy_ (u"ࠢࡱࡻࡷࡩࡸࡺ࠮ࡱࡻࡷ࡬ࡴࡴ࠮ࡑࡣࡦ࡯ࡦ࡭ࡥࠣᅤ"): bstack1ll1l1111ll_opy_,
    bstack11l1ll1_opy_ (u"ࠣࡲࡼࡸࡪࡹࡴ࠯ࡲࡼࡸ࡭ࡵ࡮࠯ࡏࡲࡨࡺࡲࡥࠣᅥ"): bstack1ll1l1111ll_opy_,
    bstack11l1ll1_opy_ (u"ࠤࡳࡽࡹ࡫ࡳࡵ࠰ࡳࡽࡹ࡮࡯࡯࠰ࡆࡰࡦࡹࡳࠣᅦ"): bstack1ll1l1111ll_opy_,
    bstack11l1ll1_opy_ (u"ࠥࡴࡾࡺࡥࡴࡶ࠱ࡴࡾࡺࡨࡰࡰ࠱ࡊࡺࡴࡣࡵ࡫ࡲࡲࠧᅧ"): bstack1ll1l1111ll_opy_
    + [
        bstack11l1ll1_opy_ (u"ࠦࡴࡸࡩࡨ࡫ࡱࡥࡱࡴࡡ࡮ࡧࠥᅨ"),
        bstack11l1ll1_opy_ (u"ࠧࡱࡥࡺࡹࡲࡶࡩࡹࠢᅩ"),
        bstack11l1ll1_opy_ (u"ࠨࡦࡪࡺࡷࡹࡷ࡫ࡩ࡯ࡨࡲࠦᅪ"),
        bstack11l1ll1_opy_ (u"ࠢ࡬ࡧࡼࡻࡴࡸࡤࡴࠤᅫ"),
        bstack11l1ll1_opy_ (u"ࠣࡥࡤࡰࡱࡹࡰࡦࡥࠥᅬ"),
        bstack11l1ll1_opy_ (u"ࠤࡦࡥࡱࡲ࡯ࡣ࡬ࠥᅭ"),
        bstack11l1ll1_opy_ (u"ࠥࡷࡹࡧࡲࡵࠤᅮ"),
        bstack11l1ll1_opy_ (u"ࠦࡸࡺ࡯ࡱࠤᅯ"),
        bstack11l1ll1_opy_ (u"ࠧࡪࡵࡳࡣࡷ࡭ࡴࡴࠢᅰ"),
        bstack11l1ll1_opy_ (u"ࠨࡷࡩࡧࡱࠦᅱ"),
    ],
    bstack11l1ll1_opy_ (u"ࠢࡱࡻࡷࡩࡸࡺ࠮࡮ࡣ࡬ࡲ࠳࡙ࡥࡴࡵ࡬ࡳࡳࠨᅲ"): [bstack11l1ll1_opy_ (u"ࠣࡵࡷࡥࡷࡺࡰࡢࡶ࡫ࠦᅳ"), bstack11l1ll1_opy_ (u"ࠤࡷࡩࡸࡺࡳࡧࡣ࡬ࡰࡪࡪࠢᅴ"), bstack11l1ll1_opy_ (u"ࠥࡸࡪࡹࡴࡴࡥࡲࡰࡱ࡫ࡣࡵࡧࡧࠦᅵ"), bstack11l1ll1_opy_ (u"ࠦ࡮ࡺࡥ࡮ࡵࠥᅶ")],
    bstack11l1ll1_opy_ (u"ࠧࡶࡹࡵࡧࡶࡸ࠳ࡩ࡯࡯ࡨ࡬࡫࠳ࡉ࡯࡯ࡨ࡬࡫ࠧᅷ"): [bstack11l1ll1_opy_ (u"ࠨࡩ࡯ࡸࡲࡧࡦࡺࡩࡰࡰࡢࡴࡦࡸࡡ࡮ࡵࠥᅸ"), bstack11l1ll1_opy_ (u"ࠢࡢࡴࡪࡷࠧᅹ")],
    bstack11l1ll1_opy_ (u"ࠣࡲࡼࡸࡪࡹࡴ࠯ࡨ࡬ࡼࡹࡻࡲࡦࡵ࠱ࡊ࡮ࡾࡴࡶࡴࡨࡈࡪ࡬ࠢᅺ"): [bstack11l1ll1_opy_ (u"ࠤࡶࡧࡴࡶࡥࠣᅻ"), bstack11l1ll1_opy_ (u"ࠥࡥࡷ࡭࡮ࡢ࡯ࡨࠦᅼ"), bstack11l1ll1_opy_ (u"ࠦ࡫ࡻ࡮ࡤࠤᅽ"), bstack11l1ll1_opy_ (u"ࠧࡶࡡࡳࡣࡰࡷࠧᅾ"), bstack11l1ll1_opy_ (u"ࠨࡵ࡯࡫ࡷࡸࡪࡹࡴࠣᅿ"), bstack11l1ll1_opy_ (u"ࠢࡪࡦࡶࠦᆀ")],
    bstack11l1ll1_opy_ (u"ࠣࡲࡼࡸࡪࡹࡴ࠯ࡨ࡬ࡼࡹࡻࡲࡦࡵ࠱ࡗࡺࡨࡒࡦࡳࡸࡩࡸࡺࠢᆁ"): [bstack11l1ll1_opy_ (u"ࠤࡩ࡭ࡽࡺࡵࡳࡧࡱࡥࡲ࡫ࠢᆂ"), bstack11l1ll1_opy_ (u"ࠥࡴࡦࡸࡡ࡮ࠤᆃ"), bstack11l1ll1_opy_ (u"ࠦࡵࡧࡲࡢ࡯ࡢ࡭ࡳࡪࡥࡹࠤᆄ")],
    bstack11l1ll1_opy_ (u"ࠧࡶࡹࡵࡧࡶࡸ࠳ࡸࡵ࡯ࡰࡨࡶ࠳ࡉࡡ࡭࡮ࡌࡲ࡫ࡵࠢᆅ"): [bstack11l1ll1_opy_ (u"ࠨࡷࡩࡧࡱࠦᆆ"), bstack11l1ll1_opy_ (u"ࠢࡳࡧࡶࡹࡱࡺࠢᆇ")],
    bstack11l1ll1_opy_ (u"ࠣࡲࡼࡸࡪࡹࡴ࠯࡯ࡤࡶࡰ࠴ࡳࡵࡴࡸࡧࡹࡻࡲࡦࡵ࠱ࡒࡴࡪࡥࡌࡧࡼࡻࡴࡸࡤࡴࠤᆈ"): [bstack11l1ll1_opy_ (u"ࠤࡱࡳࡩ࡫ࠢᆉ"), bstack11l1ll1_opy_ (u"ࠥࡴࡦࡸࡥ࡯ࡶࠥᆊ")],
    bstack11l1ll1_opy_ (u"ࠦࡵࡿࡴࡦࡵࡷ࠲ࡲࡧࡲ࡬࠰ࡶࡸࡷࡻࡣࡵࡷࡵࡩࡸ࠴ࡍࡢࡴ࡮ࠦᆋ"): [bstack11l1ll1_opy_ (u"ࠧࡴࡡ࡮ࡧࠥᆌ"), bstack11l1ll1_opy_ (u"ࠨࡡࡳࡩࡶࠦᆍ"), bstack11l1ll1_opy_ (u"ࠢ࡬ࡹࡤࡶ࡬ࡹࠢᆎ")],
}
class bstack1llll1l1l11_opy_(bstack1111111l1l_opy_):
    bstack1ll1l1l11l1_opy_ = bstack11l1ll1_opy_ (u"ࠣࡶࡨࡷࡹࡥࡤࡦࡨࡨࡶࡷ࡫ࡤࠣᆏ")
    bstack1ll11ll11l1_opy_ = bstack11l1ll1_opy_ (u"ࠤࡌࡒࡋࡕࠢᆐ")
    bstack1ll11l1lll1_opy_ = bstack11l1ll1_opy_ (u"ࠥࡉࡗࡘࡏࡓࠤᆑ")
    bstack1ll11ll11ll_opy_: Callable
    bstack1ll11llllll_opy_: Callable
    def __init__(self):
        super().__init__()
        if os.getenv(bstack11l1ll1_opy_ (u"ࠦࡘࡊࡋࡠࡅࡏࡍࡤࡌࡌࡂࡉࡢࡓ࠶࠷࡙ࠣᆒ"), bstack11l1ll1_opy_ (u"ࠧ࠷ࠢᆓ")) != bstack11l1ll1_opy_ (u"ࠨ࠱ࠣᆔ") or not self.is_enabled():
            self.logger.warning(bstack11l1ll1_opy_ (u"ࠢࠣᆕ") + str(self.__class__.__name__) + bstack11l1ll1_opy_ (u"ࠣࠢࡧ࡭ࡸࡧࡢ࡭ࡧࡧࠦᆖ"))
            return
        TestFramework.bstack1lll11llll1_opy_((bstack1llll11llll_opy_.TEST, bstack1lll1llll11_opy_.PRE), self.bstack1lll11l1lll_opy_)
        TestFramework.bstack1lll11llll1_opy_((bstack1llll11llll_opy_.TEST, bstack1lll1llll11_opy_.POST), self.bstack1ll1llll11l_opy_)
        for event in bstack1llll11llll_opy_:
            for state in bstack1lll1llll11_opy_:
                TestFramework.bstack1lll11llll1_opy_((event, state), self.bstack1ll11lll11l_opy_)
        bstack1llllllll1l_opy_.bstack1lll11llll1_opy_((bstack1111ll111l_opy_.bstack1111l1l11l_opy_, bstack1111l1l1l1_opy_.POST), self.bstack1ll11ll1l1l_opy_)
        self.bstack1ll11ll11ll_opy_ = sys.stdout.write
        sys.stdout.write = self.bstack1ll1l11l11l_opy_(bstack1llll1l1l11_opy_.bstack1ll11ll11l1_opy_, self.bstack1ll11ll11ll_opy_)
        self.bstack1ll11llllll_opy_ = sys.stderr.write
        sys.stderr.write = self.bstack1ll1l11l11l_opy_(bstack1llll1l1l11_opy_.bstack1ll11l1lll1_opy_, self.bstack1ll11llllll_opy_)
    def is_enabled(self) -> bool:
        return True
    def bstack1ll11lll11l_opy_(
        self,
        f: TestFramework,
        instance: bstack11111l1l11_opy_,
        bstack111l111l1l_opy_: Tuple[bstack1llll11llll_opy_, bstack1lll1llll11_opy_],
        *args,
        **kwargs,
    ):
        if f.bstack1ll11l1ll11_opy_() and instance:
            bstack1ll1l1ll111_opy_ = datetime.now()
            test_framework_state, test_hook_state = bstack111l111l1l_opy_
            if test_framework_state == bstack1llll11llll_opy_.SETUP_FIXTURE:
                return
            elif test_framework_state == bstack1llll11llll_opy_.LOG:
                bstack1l1l1ll111_opy_ = datetime.now()
                entries = f.bstack1ll11l1l111_opy_(instance, bstack111l111l1l_opy_)
                if entries:
                    self.bstack1ll1ll11111_opy_(instance, entries)
                    instance.bstack111l11l1_opy_(bstack11l1ll1_opy_ (u"ࠤࡪࡶࡵࡩ࠺ࡴࡧࡱࡨࡤࡲ࡯ࡨࡡࡦࡶࡪࡧࡴࡦࡦࡢࡩࡻ࡫࡮ࡵࠤᆗ"), datetime.now() - bstack1l1l1ll111_opy_)
                    f.bstack1ll1l1111l1_opy_(instance, bstack111l111l1l_opy_)
                instance.bstack111l11l1_opy_(bstack11l1ll1_opy_ (u"ࠥࡳ࠶࠷ࡹ࠻ࡱࡱࡣࡦࡲ࡬ࡠࡶࡨࡷࡹࡥࡥࡷࡧࡱࡸࡸࠨᆘ"), datetime.now() - bstack1ll1l1ll111_opy_)
                return # do not send this event with the bstack1ll1l1ll1l1_opy_ bstack1ll1l1lllll_opy_
            elif (
                test_framework_state == bstack1llll11llll_opy_.TEST
                and test_hook_state == bstack1lll1llll11_opy_.POST
                and not f.bstack111l1111ll_opy_(instance, TestFramework.bstack1ll1l1lll1l_opy_)
            ):
                self.logger.warning(bstack11l1ll1_opy_ (u"ࠦࡩࡸ࡯ࡱࡲ࡬ࡲ࡬ࠦࡤࡶࡧࠣࡸࡴࠦ࡬ࡢࡥ࡮ࠤࡴ࡬ࠠࡳࡧࡶࡹࡱࡺࡳࠡࠤᆙ") + str(TestFramework.bstack111l1111ll_opy_(instance, TestFramework.bstack1ll1l1lll1l_opy_)) + bstack11l1ll1_opy_ (u"ࠧࠨᆚ"))
                f.bstack1111l11l11_opy_(instance, bstack1llll1l1l11_opy_.bstack1ll1l1l11l1_opy_, True)
                return # do not send this event bstack1ll1l1lll11_opy_ bstack1ll1l11l1l1_opy_
            elif (
                f.bstack111l111111_opy_(instance, bstack1llll1l1l11_opy_.bstack1ll1l1l11l1_opy_, False)
                and test_framework_state == bstack1llll11llll_opy_.LOG_REPORT
                and test_hook_state == bstack1lll1llll11_opy_.POST
                and f.bstack111l1111ll_opy_(instance, TestFramework.bstack1ll1l1lll1l_opy_)
            ):
                self.logger.warning(bstack11l1ll1_opy_ (u"ࠨࡩ࡯࡬ࡨࡧࡹ࡯࡮ࡨࠢࡗࡩࡸࡺࡆࡳࡣࡰࡩࡼࡵࡲ࡬ࡕࡷࡥࡹ࡫࠮ࡕࡇࡖࡘ࠱ࠦࡔࡦࡵࡷࡌࡴࡵ࡫ࡔࡶࡤࡸࡪ࠴ࡐࡐࡕࡗࠤࠧᆛ") + str(TestFramework.bstack111l1111ll_opy_(instance, TestFramework.bstack1ll1l1lll1l_opy_)) + bstack11l1ll1_opy_ (u"ࠢࠣᆜ"))
                self.bstack1ll11lll11l_opy_(f, instance, (bstack1llll11llll_opy_.TEST, bstack1lll1llll11_opy_.POST), *args, **kwargs)
            bstack1l1l1ll111_opy_ = datetime.now()
            data = instance.data.copy()
            bstack1ll1l1l1l11_opy_ = sorted(
                filter(lambda x: x.get(bstack11l1ll1_opy_ (u"ࠣࡧࡹࡩࡳࡺ࡟ࡴࡶࡤࡶࡹ࡫ࡤࡠࡣࡷࠦᆝ"), None), data.pop(bstack11l1ll1_opy_ (u"ࠤࡷࡩࡸࡺ࡟ࡧ࡫ࡻࡸࡺࡸࡥࡴࠤᆞ"), {}).values()),
                key=lambda x: x[bstack11l1ll1_opy_ (u"ࠥࡩࡻ࡫࡮ࡵࡡࡶࡸࡦࡸࡴࡦࡦࡢࡥࡹࠨᆟ")],
            )
            if bstack1llll111l11_opy_.bstack1lll1l11ll1_opy_ in data:
                data.pop(bstack1llll111l11_opy_.bstack1lll1l11ll1_opy_)
            data.update({bstack11l1ll1_opy_ (u"ࠦࡹ࡫ࡳࡵࡡࡩ࡭ࡽࡺࡵࡳࡧࡶࠦᆠ"): bstack1ll1l1l1l11_opy_})
            instance.bstack111l11l1_opy_(bstack11l1ll1_opy_ (u"ࠧࡰࡳࡰࡰ࠽ࡸࡪࡹࡴࡠࡨ࡬ࡼࡹࡻࡲࡦࡵࠥᆡ"), datetime.now() - bstack1l1l1ll111_opy_)
            bstack1l1l1ll111_opy_ = datetime.now()
            event_json = dumps(data, cls=bstack1ll1l1l1lll_opy_)
            instance.bstack111l11l1_opy_(bstack11l1ll1_opy_ (u"ࠨࡪࡴࡱࡱ࠾ࡴࡴ࡟ࡢ࡮࡯ࡣࡹ࡫ࡳࡵࡡࡨࡺࡪࡴࡴࡴࠤᆢ"), datetime.now() - bstack1l1l1ll111_opy_)
            self.bstack1ll1l1lllll_opy_(instance, bstack111l111l1l_opy_, event_json=event_json)
            instance.bstack111l11l1_opy_(bstack11l1ll1_opy_ (u"ࠢࡰ࠳࠴ࡽ࠿ࡵ࡮ࡠࡣ࡯ࡰࡤࡺࡥࡴࡶࡢࡩࡻ࡫࡮ࡵࡵࠥᆣ"), datetime.now() - bstack1ll1l1ll111_opy_)
    def bstack1lll11l1lll_opy_(
        self,
        f: TestFramework,
        instance: bstack11111l1l11_opy_,
        bstack111l111l1l_opy_: Tuple[bstack1llll11llll_opy_, bstack1lll1llll11_opy_],
        *args,
        **kwargs,
    ):
        from bstack_utils.bstack1ll111ll1l_opy_ import bstack1llll111lll_opy_
        bstack1lll1111l11_opy_ = [d for d, _ in f.bstack111l111111_opy_(instance, bstack1llll111l11_opy_.bstack1lll1l11ll1_opy_, [])]
        if not bstack1lll1111l11_opy_:
            return
        if not bstack1ll1l1l11ll_opy_():
            return
        for bstack1ll11ll111l_opy_ in bstack1lll1111l11_opy_:
            driver = bstack1ll11ll111l_opy_()
            if not driver:
                continue
            timestamp = int(time.time() * 1000)
            data = bstack11l1ll1_opy_ (u"ࠣࡑࡥࡷࡪࡸࡶࡢࡤ࡬ࡰ࡮ࡺࡹࡔࡻࡱࡧ࠿ࠨᆤ") + str(timestamp)
            bstack1lll11l1l1l_opy_ = bstack1llll111lll_opy_.bstack1lll11l1111_opy_(EVENTS.bstack1llll1111_opy_.value)
            driver.execute_script(
                bstack11l1ll1_opy_ (u"ࠤࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡠࡧࡻࡩࡨࡻࡴࡰࡴ࠽ࠤࢀࢃࠢᆥ").format(
                    json.dumps(
                        {
                            bstack11l1ll1_opy_ (u"ࠥࡥࡨࡺࡩࡰࡰࠥᆦ"): bstack11l1ll1_opy_ (u"ࠦࡦࡴ࡮ࡰࡶࡤࡸࡪࠨᆧ"),
                            bstack11l1ll1_opy_ (u"ࠧࡧࡲࡨࡷࡰࡩࡳࡺࡳࠣᆨ"): {
                                bstack11l1ll1_opy_ (u"ࠨࡴࡺࡲࡨࠦᆩ"): bstack11l1ll1_opy_ (u"ࠢࡂࡰࡱࡳࡹࡧࡴࡪࡱࡱࠦᆪ"),
                                bstack11l1ll1_opy_ (u"ࠣࡦࡤࡸࡦࠨᆫ"): data,
                                bstack11l1ll1_opy_ (u"ࠤ࡯ࡩࡻ࡫࡬ࠣᆬ"): bstack11l1ll1_opy_ (u"ࠥࡨࡪࡨࡵࡨࠤᆭ")
                            }
                        }
                    )
                )
            )
            bstack1llll111lll_opy_.end(EVENTS.bstack1llll1111_opy_.value, bstack1lll11l1l1l_opy_ + bstack11l1ll1_opy_ (u"ࠦ࠿ࡹࡴࡢࡴࡷࠦᆮ"), bstack1lll11l1l1l_opy_ + bstack11l1ll1_opy_ (u"ࠧࡀࡥ࡯ࡦࠥᆯ"), status=True, failure=None, test_name=None)
    def bstack1ll1llll11l_opy_(
        self,
        f: TestFramework,
        instance: bstack11111l1l11_opy_,
        bstack111l111l1l_opy_: Tuple[bstack1llll11llll_opy_, bstack1lll1llll11_opy_],
        *args,
        **kwargs,
    ):
        keys = [
            bstack1llll111l11_opy_.bstack1lll1l11ll1_opy_,
            bstack1llll111l11_opy_.bstack1ll11lll1ll_opy_,
        ]
        bstack1lll1111l11_opy_ = [
            d for key in keys for _, d in f.bstack111l111111_opy_(instance, key, [])
        ]
        if not bstack1lll1111l11_opy_:
            self.logger.debug(bstack11l1ll1_opy_ (u"ࠨ࡯࡯ࡡࡤࡪࡹ࡫ࡲࡠࡶࡨࡷࡹࡀࠠࡶࡰࡤࡦࡱ࡫ࠠࡵࡱࠣࡪ࡮ࡴࡤࠡࡣࡱࡽࠥࡹࡥࡴࡵ࡬ࡳࡳࡹࠠࡵࡱࠣࡰ࡮ࡴ࡫ࠣᆰ"))
            return
        self.bstack1ll11lll1l1_opy_(f, instance, bstack1lll1111l11_opy_, bstack111l111l1l_opy_)
    @measure(event_name=EVENTS.bstack1ll11lll111_opy_, stage=STAGE.bstack1l1ll1llll_opy_)
    def bstack1ll11lll1l1_opy_(
        self,
        f: TestFramework,
        instance: bstack11111l1l11_opy_,
        bstack1lll1111l11_opy_: List[bstack1111l11l1l_opy_],
        bstack111l111l1l_opy_: Tuple[bstack1llll11llll_opy_, bstack1lll1llll11_opy_],
    ):
        if f.bstack111l111111_opy_(instance, bstack1llll111l11_opy_.bstack1ll1l1ll1ll_opy_, False):
            return
        self.bstack1lll111l1ll_opy_()
        bstack1l1l1ll111_opy_ = datetime.now()
        req = structs.TestSessionEventRequest()
        req.bin_session_id = self.bin_session_id
        req.platform_index = TestFramework.bstack111l111111_opy_(instance, TestFramework.bstack1lll11ll1l1_opy_)
        req.test_framework_name = TestFramework.bstack111l111111_opy_(instance, TestFramework.bstack1lll11111l1_opy_)
        req.test_framework_version = TestFramework.bstack111l111111_opy_(instance, TestFramework.bstack1ll1l11llll_opy_)
        req.test_framework_state = bstack111l111l1l_opy_[0].name
        req.test_hook_state = bstack111l111l1l_opy_[1].name
        req.test_uuid = TestFramework.bstack111l111111_opy_(instance, TestFramework.bstack1lll111l1l1_opy_)
        for driver in bstack1lll1111l11_opy_:
            session = req.automation_sessions.add()
            session.provider = (
                bstack11l1ll1_opy_ (u"ࠢࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࠨᆱ")
                if bstack1llllllll1l_opy_.bstack111l111111_opy_(driver, bstack1llllllll1l_opy_.bstack1ll1l111l1l_opy_, False)
                else bstack11l1ll1_opy_ (u"ࠣࡷࡱ࡯ࡳࡵࡷ࡯ࡡࡪࡶ࡮ࡪࠢᆲ")
            )
            session.ref = driver.ref()
            session.hub_url = bstack1llllllll1l_opy_.bstack111l111111_opy_(driver, bstack1llllllll1l_opy_.bstack1ll1l11l111_opy_, bstack11l1ll1_opy_ (u"ࠤࠥᆳ"))
            session.framework_name = driver.framework_name
            session.framework_version = driver.framework_version
            session.framework_session_id = bstack1llllllll1l_opy_.bstack111l111111_opy_(driver, bstack1llllllll1l_opy_.bstack1ll11l1llll_opy_, bstack11l1ll1_opy_ (u"ࠥࠦᆴ"))
        req.execution_context.hash = str(instance.context.hash)
        req.execution_context.thread_id = str(instance.context.thread_id)
        req.execution_context.process_id = str(instance.context.process_id)
        try:
            r = self.bstack11111111l1_opy_.TestSessionEvent(req)
            instance.bstack111l11l1_opy_(bstack11l1ll1_opy_ (u"ࠦ࡬ࡸࡰࡤ࠼ࡶࡩࡳࡪ࡟ࡵࡧࡶࡸࡤࡹࡥࡴࡵ࡬ࡳࡳࡥࡥࡷࡧࡱࡸࠧᆵ"), datetime.now() - bstack1l1l1ll111_opy_)
            f.bstack1111l11l11_opy_(instance, bstack1llll111l11_opy_.bstack1ll1l1ll1ll_opy_, r.success)
            if not r.success:
                self.logger.info(bstack11l1ll1_opy_ (u"ࠧࡸࡥࡤࡧ࡬ࡺࡪࡪࠠࡧࡴࡲࡱࠥࡹࡥࡳࡸࡨࡶ࠿ࠦࠢᆶ") + str(r) + bstack11l1ll1_opy_ (u"ࠨࠢᆷ"))
        except grpc.RpcError as e:
            self.logger.error(bstack11l1ll1_opy_ (u"ࠢࡳࡲࡦ࠱ࡪࡸࡲࡰࡴ࠽ࠤࠧᆸ") + str(e) + bstack11l1ll1_opy_ (u"ࠣࠤᆹ"))
            traceback.print_exc()
            raise e
    def bstack1ll11ll1l1l_opy_(
        self,
        f: bstack1llllllll1l_opy_,
        _driver: object,
        exec: Tuple[bstack1111l11l1l_opy_, str],
        _1ll1l11ll1l_opy_: Tuple[bstack1111ll111l_opy_, bstack1111l1l1l1_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
        instance, method_name = exec
        if not bstack1llllllll1l_opy_.bstack1lll111lll1_opy_(method_name):
            return
        if f.bstack1lll11l11ll_opy_(*args) != bstack1llllllll1l_opy_.bstack1ll11ll1ll1_opy_:
            return
        bstack1ll1l1ll111_opy_ = datetime.now()
        screenshot = result.get(bstack11l1ll1_opy_ (u"ࠤࡹࡥࡱࡻࡥࠣᆺ"), None) if isinstance(result, dict) else None
        if not isinstance(screenshot, str) or len(screenshot) <= 0:
            self.logger.warning(bstack11l1ll1_opy_ (u"ࠥ࡭ࡳࡼࡡ࡭࡫ࡧࠤࡸࡩࡲࡦࡧࡱࡷ࡭ࡵࡴࠡ࡫ࡰࡥ࡬࡫ࠠࡣࡣࡶࡩ࠻࠺ࠠࡴࡶࡵࠦᆻ"))
            return
        bstack1ll1l1l111l_opy_ = self.bstack1ll11ll1111_opy_(instance)
        if bstack1ll1l1l111l_opy_:
            entry = bstack1llll111ll1_opy_(TestFramework.bstack1ll11l1ll1l_opy_, screenshot)
            self.bstack1ll1ll11111_opy_(bstack1ll1l1l111l_opy_, [entry])
            instance.bstack111l11l1_opy_(bstack11l1ll1_opy_ (u"ࠦࡴ࠷࠱ࡺ࠼ࡲࡲࡤࡧࡦࡵࡧࡵࡣࡪࡾࡥࡤࡷࡷࡩࠧᆼ"), datetime.now() - bstack1ll1l1ll111_opy_)
        else:
            self.logger.warning(bstack11l1ll1_opy_ (u"ࠧࡻ࡮ࡢࡤ࡯ࡩࠥࡺ࡯ࠡࡦࡨࡸࡪࡸ࡭ࡪࡰࡨࠤࡹ࡫ࡳࡵࠢࡩࡳࡷࠦࡷࡩ࡫ࡦ࡬ࠥࡺࡨࡪࡵࠣࡷࡨࡸࡥࡦࡰࡶ࡬ࡴࡺࠠࡸࡣࡶࠤࡹࡧ࡫ࡦࡰࠣࡦࡾࠦࡤࡳ࡫ࡹࡩࡷࡃࠢᆽ") + str(instance.ref()) + bstack11l1ll1_opy_ (u"ࠨࠢᆾ"))
    @measure(event_name=EVENTS.bstack1ll1l11111l_opy_, stage=STAGE.bstack1l1ll1llll_opy_)
    def bstack1ll1ll11111_opy_(
        self,
        bstack1ll1l1l111l_opy_: bstack11111l1l11_opy_,
        entries: List[bstack1llll111ll1_opy_],
    ):
        self.bstack1lll111l1ll_opy_()
        req = structs.LogCreatedEventRequest()
        req.bin_session_id = self.bin_session_id
        req.platform_index = TestFramework.bstack111l111111_opy_(bstack1ll1l1l111l_opy_, TestFramework.bstack1lll11ll1l1_opy_)
        req.execution_context.hash = str(bstack1ll1l1l111l_opy_.context.hash)
        req.execution_context.thread_id = str(bstack1ll1l1l111l_opy_.context.thread_id)
        req.execution_context.process_id = str(bstack1ll1l1l111l_opy_.context.process_id)
        for entry in entries:
            log_entry = req.logs.add()
            log_entry.test_framework_name = TestFramework.bstack111l111111_opy_(bstack1ll1l1l111l_opy_, TestFramework.bstack1lll11111l1_opy_)
            log_entry.test_framework_version = TestFramework.bstack111l111111_opy_(bstack1ll1l1l111l_opy_, TestFramework.bstack1ll1l11llll_opy_)
            log_entry.uuid = TestFramework.bstack111l111111_opy_(bstack1ll1l1l111l_opy_, TestFramework.bstack1lll111l1l1_opy_)
            log_entry.test_framework_state = bstack1ll1l1l111l_opy_.state.name
            log_entry.message = entry.message.encode(bstack11l1ll1_opy_ (u"ࠢࡶࡶࡩ࠱࠽ࠨᆿ"))
            log_entry.kind = entry.kind
            log_entry.timestamp = (
                entry.timestamp.isoformat()
                if isinstance(entry.timestamp, datetime)
                else datetime.now(tz=timezone.utc).isoformat()
            )
            if isinstance(entry.level, str) and len(entry.level.strip()) > 0:
                log_entry.level = entry.level.strip()
        def bstack1ll1l1ll11l_opy_():
            bstack1l1l1ll111_opy_ = datetime.now()
            try:
                self.bstack11111111l1_opy_.LogCreatedEvent(req)
                if entry.kind == TestFramework.bstack1ll11l1ll1l_opy_:
                    bstack1ll1l1l111l_opy_.bstack111l11l1_opy_(bstack11l1ll1_opy_ (u"ࠣࡩࡵࡴࡨࡀࡳࡦࡰࡧࡣࡱࡵࡧࡠࡥࡵࡩࡦࡺࡥࡥࡡࡨࡺࡪࡴࡴࡠࡵࡦࡶࡪ࡫࡮ࡴࡪࡲࡸࠧᇀ"), datetime.now() - bstack1l1l1ll111_opy_)
                else:
                    bstack1ll1l1l111l_opy_.bstack111l11l1_opy_(bstack11l1ll1_opy_ (u"ࠤࡪࡶࡵࡩ࠺ࡴࡧࡱࡨࡤࡲ࡯ࡨࡡࡦࡶࡪࡧࡴࡦࡦࡢࡩࡻ࡫࡮ࡵࡡ࡯ࡳ࡬ࠨᇁ"), datetime.now() - bstack1l1l1ll111_opy_)
            except grpc.RpcError as e:
                self.log_error(bstack11l1ll1_opy_ (u"ࠥࡶࡵࡩ࠭ࡦࡴࡵࡳࡷࡀࠠࠣᇂ") + str(e))
                traceback.print_exc()
                raise e
        self.bstack111l11l111_opy_.enqueue(bstack1ll1l1ll11l_opy_)
    @measure(event_name=EVENTS.bstack1ll11ll1lll_opy_, stage=STAGE.bstack1l1ll1llll_opy_)
    def bstack1ll1l1lllll_opy_(
        self,
        instance: bstack11111l1l11_opy_,
        bstack111l111l1l_opy_: Tuple[bstack1llll11llll_opy_, bstack1lll1llll11_opy_],
        event_json=None,
    ):
        self.bstack1lll111l1ll_opy_()
        req = structs.TestFrameworkEventRequest()
        req.bin_session_id = self.bin_session_id
        req.platform_index = TestFramework.bstack111l111111_opy_(instance, TestFramework.bstack1lll11ll1l1_opy_)
        req.test_framework_name = TestFramework.bstack111l111111_opy_(instance, TestFramework.bstack1lll11111l1_opy_)
        req.test_framework_version = TestFramework.bstack111l111111_opy_(instance, TestFramework.bstack1ll1l11llll_opy_)
        req.test_framework_state = bstack111l111l1l_opy_[0].name
        req.test_hook_state = bstack111l111l1l_opy_[1].name
        started_at = TestFramework.bstack111l111111_opy_(instance, TestFramework.bstack1ll11ll1l11_opy_, None)
        if started_at:
            req.started_at = started_at.isoformat()
        ended_at = TestFramework.bstack111l111111_opy_(instance, TestFramework.bstack1ll1l111l11_opy_, None)
        if ended_at:
            req.ended_at = ended_at.isoformat()
        req.uuid = instance.ref()
        req.event_json = (event_json if event_json else dumps(instance.data, cls=bstack1ll1l1l1lll_opy_)).encode(bstack11l1ll1_opy_ (u"ࠦࡺࡺࡦ࠮࠺ࠥᇃ"))
        req.execution_context.hash = str(instance.context.hash)
        req.execution_context.thread_id = str(instance.context.thread_id)
        req.execution_context.process_id = str(instance.context.process_id)
        def bstack1ll1l1ll11l_opy_():
            bstack1l1l1ll111_opy_ = datetime.now()
            try:
                self.bstack11111111l1_opy_.TestFrameworkEvent(req)
                instance.bstack111l11l1_opy_(bstack11l1ll1_opy_ (u"ࠧ࡭ࡲࡱࡥ࠽ࡷࡪࡴࡤࡠࡶࡨࡷࡹࡥࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࡡࡨࡺࡪࡴࡴࠣᇄ"), datetime.now() - bstack1l1l1ll111_opy_)
            except grpc.RpcError as e:
                self.log_error(bstack11l1ll1_opy_ (u"ࠨࡲࡱࡥ࠰ࡩࡷࡸ࡯ࡳ࠼ࠣࠦᇅ") + str(e))
                traceback.print_exc()
                raise e
        self.bstack111l11l111_opy_.enqueue(bstack1ll1l1ll11l_opy_)
    def bstack1ll11l1l1ll_opy_(self, event_url: str, bstack11l1111lll_opy_: dict) -> bool:
        return True # always return True so that old bstack1ll1l11lll1_opy_ bstack1ll11l1l1l1_opy_'t bstack1ll1l111lll_opy_
    def bstack1ll11ll1111_opy_(self, instance: bstack1111l11l1l_opy_):
        bstack1ll1l11ll11_opy_ = TestFramework.bstack1111lll1ll_opy_(instance.context)
        for t in bstack1ll1l11ll11_opy_:
            bstack1lll1111l11_opy_ = TestFramework.bstack111l111111_opy_(t, bstack1llll111l11_opy_.bstack1lll1l11ll1_opy_, [])
            if any(instance is d[1] for d in bstack1lll1111l11_opy_):
                return t
    def bstack1ll1l1l1111_opy_(self, message):
        self.bstack1ll11ll11ll_opy_(message + bstack11l1ll1_opy_ (u"ࠢ࡝ࡰࠥᇆ"))
    def log_error(self, message):
        self.bstack1ll11llllll_opy_(message + bstack11l1ll1_opy_ (u"ࠣ࡞ࡱࠦᇇ"))
    def bstack1ll1l11l11l_opy_(self, level, original_func):
        def bstack1ll1l1l1ll1_opy_(*args):
            return_value = original_func(*args)
            if not args or not isinstance(args[0], str) or not args[0].strip():
                return return_value
            message = args[0].strip()
            bstack1ll1l11ll11_opy_ = TestFramework.bstack1ll1l1l1l1l_opy_()
            if not bstack1ll1l11ll11_opy_:
                return return_value
            bstack1ll1l1l111l_opy_ = next(
                (
                    instance
                    for instance in bstack1ll1l11ll11_opy_
                    if TestFramework.bstack111l1111ll_opy_(instance, TestFramework.bstack1lll111l1l1_opy_)
                ),
                None,
            )
            if not bstack1ll1l1l111l_opy_:
                return
            entry = bstack1llll111ll1_opy_(TestFramework.bstack1ll1ll1111l_opy_, message, level)
            self.bstack1ll1ll11111_opy_(bstack1ll1l1l111l_opy_, [entry])
            return return_value
        return bstack1ll1l1l1ll1_opy_
class bstack1ll1l1l1lll_opy_(JSONEncoder):
    def __init__(self, **kwargs):
        self.bstack1ll11lllll1_opy_ = set()
        kwargs[bstack11l1ll1_opy_ (u"ࠤࡶ࡯࡮ࡶ࡫ࡦࡻࡶࠦᇈ")] = True
        super().__init__(**kwargs)
    def default(self, obj):
        return bstack1ll1l1llll1_opy_(obj, self.bstack1ll11lllll1_opy_)
def bstack1ll11llll11_opy_(obj):
    return isinstance(obj, (str, int, float, bool, type(None)))
def bstack1ll1l1llll1_opy_(obj, bstack1ll11lllll1_opy_=None, max_depth=3):
    if bstack1ll11lllll1_opy_ is None:
        bstack1ll11lllll1_opy_ = set()
    if id(obj) in bstack1ll11lllll1_opy_ or max_depth <= 0:
        return None
    max_depth -= 1
    bstack1ll11lllll1_opy_.add(id(obj))
    if isinstance(obj, datetime):
        return obj.isoformat()
    bstack1ll1l111ll1_opy_ = TestFramework.bstack1ll1l111111_opy_(obj)
    bstack1ll11llll1l_opy_ = next((k.lower() in bstack1ll1l111ll1_opy_.lower() for k in bstack1ll1l11l1ll_opy_.keys()), None)
    if bstack1ll11llll1l_opy_:
        obj = TestFramework.bstack1ll11l1l11l_opy_(obj, bstack1ll1l11l1ll_opy_[bstack1ll11llll1l_opy_])
    if not isinstance(obj, dict):
        keys = []
        if hasattr(obj, bstack11l1ll1_opy_ (u"ࠥࡣࡤࡹ࡬ࡰࡶࡶࡣࡤࠨᇉ")):
            keys = getattr(obj, bstack11l1ll1_opy_ (u"ࠦࡤࡥࡳ࡭ࡱࡷࡷࡤࡥࠢᇊ"), [])
        elif hasattr(obj, bstack11l1ll1_opy_ (u"ࠧࡥ࡟ࡥ࡫ࡦࡸࡤࡥࠢᇋ")):
            keys = getattr(obj, bstack11l1ll1_opy_ (u"ࠨ࡟ࡠࡦ࡬ࡧࡹࡥ࡟ࠣᇌ"), {}).keys()
        else:
            keys = dir(obj)
        obj = {k: getattr(obj, k, None) for k in keys if not str(k).startswith(bstack11l1ll1_opy_ (u"ࠢࡠࠤᇍ"))}
        if not obj and bstack1ll1l111ll1_opy_ == bstack11l1ll1_opy_ (u"ࠣࡲࡤࡸ࡭ࡲࡩࡣ࠰ࡓࡳࡸ࡯ࡸࡑࡣࡷ࡬ࠧᇎ"):
            obj = {bstack11l1ll1_opy_ (u"ࠤࡳࡥࡹ࡮ࠢᇏ"): str(obj)}
    result = {}
    for key, value in obj.items():
        if not bstack1ll11llll11_opy_(key) or str(key).startswith(bstack11l1ll1_opy_ (u"ࠥࡣࠧᇐ")):
            continue
        if value is not None and bstack1ll11llll11_opy_(value):
            result[key] = value
        elif isinstance(value, dict):
            r = bstack1ll1l1llll1_opy_(value, bstack1ll11lllll1_opy_, max_depth)
            if r is not None:
                result[key] = r
        elif isinstance(value, (list, tuple, set, frozenset)):
            result[key] = list(filter(None, [bstack1ll1l1llll1_opy_(o, bstack1ll11lllll1_opy_, max_depth) for o in value]))
    return result or None