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
from datetime import datetime
import os
from browserstack_sdk.sdk_cli.bstack1111ll1l11_opy_ import (
    bstack1111ll111l_opy_,
    bstack1111l1l1l1_opy_,
    bstack1111llll1l_opy_,
    bstack1111l11l1l_opy_,
)
from browserstack_sdk.sdk_cli.bstack1111111lll_opy_ import bstack1llllllll1l_opy_
from browserstack_sdk.sdk_cli.test_framework import TestFramework, bstack1llll11llll_opy_, bstack1lll1llll11_opy_, bstack11111l1l11_opy_
from typing import Tuple, Dict, Any, List, Union
from browserstack_sdk import sdk_pb2 as structs
from browserstack_sdk.sdk_cli.bstack1llll11111l_opy_ import bstack1111111l1l_opy_
from browserstack_sdk.sdk_cli.bstack1lllll1l1l1_opy_ import bstack1llll111l11_opy_
from bstack_utils.measure import measure
from bstack_utils.constants import *
from bstack_utils.bstack1ll111ll1l_opy_ import bstack1llll111lll_opy_
import grpc
import traceback
class bstack111111l111_opy_(bstack1111111l1l_opy_):
    bstack1lll11l1l11_opy_ = False
    bstack1lll111111l_opy_ = bstack11l1ll1_opy_ (u"ࠨࡳࡦ࡮ࡨࡲ࡮ࡻ࡭࠯ࡹࡨࡦࡩࡸࡩࡷࡧࡵࠦႭ")
    bstack1lll111l11l_opy_ = bstack11l1ll1_opy_ (u"ࠢࡳࡧࡰࡳࡹ࡫࠮ࡸࡧࡥࡨࡷ࡯ࡶࡦࡴࠥႮ")
    bstack1ll1lllll11_opy_ = bstack11l1ll1_opy_ (u"ࠣࡣࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࡠ࡫ࡱ࡭ࡹࠨႯ")
    bstack1lll1l11lll_opy_ = bstack11l1ll1_opy_ (u"ࠤࡤࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࡡ࡬ࡷࡤࡹࡣࡢࡰࡱ࡭ࡳ࡭ࠢႰ")
    bstack1lll1l111l1_opy_ = bstack11l1ll1_opy_ (u"ࠥࡨࡷ࡯ࡶࡦࡴࡢ࡬ࡦࡹ࡟ࡶࡴ࡯ࠦႱ")
    scripts: Dict[str, Dict[str, str]]
    commands: Dict[str, Dict[str, Dict[str, List[str]]]]
    def __init__(self):
        super().__init__()
        self.scripts = dict()
        self.commands = dict()
        self.accessibility = False
        if not self.is_enabled():
            return
        bstack1llllllll1l_opy_.bstack1lll11llll1_opy_((bstack1111ll111l_opy_.bstack1111l1l11l_opy_, bstack1111l1l1l1_opy_.PRE), self.bstack1lll1l1111l_opy_)
        TestFramework.bstack1lll11llll1_opy_((bstack1llll11llll_opy_.TEST, bstack1lll1llll11_opy_.PRE), self.bstack1lll11l1lll_opy_)
        TestFramework.bstack1lll11llll1_opy_((bstack1llll11llll_opy_.TEST, bstack1lll1llll11_opy_.POST), self.bstack1ll1llll11l_opy_)
    def is_enabled(self) -> bool:
        return True
    def bstack1lll11l1lll_opy_(
        self,
        f: TestFramework,
        instance: bstack11111l1l11_opy_,
        bstack111l111l1l_opy_: Tuple[bstack1llll11llll_opy_, bstack1lll1llll11_opy_],
        *args,
        **kwargs,
    ):
        tags = self._1ll1lllllll_opy_(instance, args)
        test_framework = f.bstack111l111111_opy_(instance, TestFramework.bstack1lll11111l1_opy_)
        if bstack11l1ll1_opy_ (u"ࠫࡵࡿࡴࡦࡵࡷ࠱ࡧࡪࡤࠨႲ") in instance.bstack1lll1l1l111_opy_:
            platform_index = f.bstack111l111111_opy_(instance, TestFramework.bstack1lll11ll1l1_opy_)
            self.accessibility = self.bstack1lllll11l_opy_(tags) and self.bstack11llllll_opy_(self.config[bstack11l1ll1_opy_ (u"ࠬࡶ࡬ࡢࡶࡩࡳࡷࡳࡳࠨႳ")][platform_index])
        else:
            bstack1lll1111l11_opy_ = f.bstack111l111111_opy_(instance, bstack1llll111l11_opy_.bstack1lll1l11ll1_opy_, [])
            if not bstack1lll1111l11_opy_:
                self.logger.debug(bstack11l1ll1_opy_ (u"ࠨ࡯࡯ࡡࡥࡩ࡫ࡵࡲࡦࡡࡷࡩࡸࡺ࠺ࠡࡰࡲࠤࡩࡸࡩࡷࡧࡵࡷࠥ࡬࡯ࡳࠢ࡫ࡳࡴࡱ࡟ࡪࡰࡩࡳࡂࢁࡨࡰࡱ࡮ࡣ࡮ࡴࡦࡰࡿࠣࡥࡷ࡭ࡳ࠾ࡽࡤࡶ࡬ࡹࡽࠡ࡭ࡺࡥࡷ࡭ࡳ࠾ࠤႴ") + str(kwargs) + bstack11l1ll1_opy_ (u"ࠢࠣႵ"))
                return
            if len(bstack1lll1111l11_opy_) > 1:
                self.logger.debug(bstack11l1ll1_opy_ (u"ࠣࡱࡱࡣࡧ࡫ࡦࡰࡴࡨࡣࡹ࡫ࡳࡵ࠼ࠣࡿࡱ࡫࡮ࠩࡦࡵ࡭ࡻ࡫ࡲࡠ࡫ࡱࡷࡹࡧ࡮ࡤࡧࡶ࠭ࢂࠦࡤࡳ࡫ࡹࡩࡷࡹࠠࡧࡱࡵࠤ࡭ࡵ࡯࡬ࡡ࡬ࡲ࡫ࡵ࠽ࡼࡪࡲࡳࡰࡥࡩ࡯ࡨࡲࢁࠥࡧࡲࡨࡵࡀࡿࡦࡸࡧࡴࡿࠣ࡯ࡼࡧࡲࡨࡵࡀࠦႶ") + str(kwargs) + bstack11l1ll1_opy_ (u"ࠤࠥႷ"))
            bstack1lll11lll1l_opy_, bstack1lll111l111_opy_ = bstack1lll1111l11_opy_[0]
            driver = bstack1lll11lll1l_opy_()
            if not driver:
                self.logger.debug(bstack11l1ll1_opy_ (u"ࠥࡳࡳࡥࡢࡦࡨࡲࡶࡪࡥࡴࡦࡵࡷ࠾ࠥࡴ࡯ࠡࡦࡵ࡭ࡻ࡫ࡲࠡࡨࡲࡶࠥ࡮࡯ࡰ࡭ࡢ࡭ࡳ࡬࡯࠾ࡽ࡫ࡳࡴࡱ࡟ࡪࡰࡩࡳࢂࠦࡡࡳࡩࡶࡁࢀࡧࡲࡨࡵࢀࠤࡰࡽࡡࡳࡩࡶࡁࠧႸ") + str(kwargs) + bstack11l1ll1_opy_ (u"ࠦࠧႹ"))
                return
            capabilities = f.bstack111l111111_opy_(bstack1lll111l111_opy_, bstack1llllllll1l_opy_.bstack1ll1llll111_opy_)
            if not capabilities:
                self.logger.debug(bstack11l1ll1_opy_ (u"ࠧࡵ࡮ࡠࡤࡨࡪࡴࡸࡥࡠࡶࡨࡷࡹࡀࠠ࡯ࡱࠣࡧࡦࡶࡡࡣ࡫࡯࡭ࡹ࡯ࡥࡴࠢࡩࡳࡺࡴࡤࠡࡨࡲࡶࠥ࡮࡯ࡰ࡭ࡢ࡭ࡳ࡬࡯࠾ࡽ࡫ࡳࡴࡱ࡟ࡪࡰࡩࡳࢂࠦࡡࡳࡩࡶࡁࢀࡧࡲࡨࡵࢀࠤࡰࡽࡡࡳࡩࡶࡁࠧႺ") + str(kwargs) + bstack11l1ll1_opy_ (u"ࠨࠢႻ"))
                return
            self.accessibility = self.bstack1lllll11l_opy_(tags) and self.bstack11llllll_opy_(capabilities[bstack11l1ll1_opy_ (u"ࠧࡢ࡮ࡺࡥࡾࡹࡍࡢࡶࡦ࡬ࠬႼ")])
        self.logger.debug(bstack11l1ll1_opy_ (u"ࠣࡵ࡫ࡳࡺࡲࡤࠡࡴࡸࡲࠥࡧࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠥࡼࡡ࡭ࡷࡨࡁࠧႽ") + str(self.accessibility) + bstack11l1ll1_opy_ (u"ࠤࠥႾ"))
    def bstack1lll1l1111l_opy_(
        self,
        f: bstack1llllllll1l_opy_,
        driver: object,
        exec: Tuple[bstack1111l11l1l_opy_, str],
        bstack111l111l1l_opy_: Tuple[bstack1111ll111l_opy_, bstack1111l1l1l1_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
        bstack1l1l1ll111_opy_ = datetime.now()
        self.bstack1lll11lllll_opy_(f, exec, *args, **kwargs)
        instance, method_name = exec
        instance.bstack111l11l1_opy_(bstack11l1ll1_opy_ (u"ࠥࡥ࠶࠷ࡹ࠻࡫ࡱ࡭ࡹࡥࡡࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾࡥࡣࡰࡰࡩ࡭࡬ࠨႿ"), datetime.now() - bstack1l1l1ll111_opy_)
        if (
            not f.bstack1lll111lll1_opy_(method_name)
            or f.bstack1lll1l11l11_opy_(method_name, *args)
            or f.bstack1lll1l111ll_opy_(method_name, *args)
        ):
            return
        if not f.bstack111l111111_opy_(instance, bstack111111l111_opy_.bstack1ll1lllll11_opy_, False):
            if not bstack111111l111_opy_.bstack1lll11l1l11_opy_:
                self.logger.warning(bstack11l1ll1_opy_ (u"ࠦࡠࡶ࡬ࡢࡶࡩࡳࡷࡳ࡟ࡪࡰࡧࡩࡽࡃࠢჀ") + str(f.platform_index) + bstack11l1ll1_opy_ (u"ࠧࡣࠠࡢ࠳࠴ࡽࠥࡩࡡࡱࡣࡥ࡭ࡱ࡯ࡴࡪࡧࡶࠤ࡭ࡧࡶࡦࠢࡱࡳࡹࠦࡢࡦࡧࡱࠤࡸ࡫ࡴࠡࡨࡲࡶࠥࡺࡨࡪࡵࠣࡷࡪࡹࡳࡪࡱࡱࠦჁ"))
                bstack111111l111_opy_.bstack1lll11l1l11_opy_ = True
            return
        bstack1ll1llll1l1_opy_ = self.scripts.get(f.framework_name, {})
        if not bstack1ll1llll1l1_opy_:
            platform_index = f.bstack111l111111_opy_(instance, bstack1llllllll1l_opy_.bstack1lll11ll1l1_opy_, 0)
            self.logger.debug(bstack11l1ll1_opy_ (u"ࠨ࡮ࡰࠢࡤ࠵࠶ࡿࠠࡴࡥࡵ࡭ࡵࡺࡳࠡࡨࡲࡶࠥࡶ࡬ࡢࡶࡩࡳࡷࡳ࡟ࡪࡰࡧࡩࡽࡃࡻࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡡ࡬ࡲࡩ࡫ࡸࡾࠢࡩࡶࡦࡳࡥࡸࡱࡵ࡯ࡤࡴࡡ࡮ࡧࡀࠦჂ") + str(f.framework_name) + bstack11l1ll1_opy_ (u"ࠢࠣჃ"))
            return
        bstack1lll11ll11l_opy_ = f.bstack1lll11l11ll_opy_(*args)
        if not bstack1lll11ll11l_opy_:
            self.logger.debug(bstack11l1ll1_opy_ (u"ࠣ࡯࡬ࡷࡸ࡯࡮ࡨࠢࡦࡳࡲࡳࡡ࡯ࡦࡢࡲࡦࡳࡥࠡࡨࡲࡶࠥ࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫ࡠࡰࡤࡱࡪࡃࡻࡧ࠰ࡩࡶࡦࡳࡥࡸࡱࡵ࡯ࡤࡴࡡ࡮ࡧࢀࠤࡲ࡫ࡴࡩࡱࡧࡣࡳࡧ࡭ࡦ࠿ࠥჄ") + str(method_name) + bstack11l1ll1_opy_ (u"ࠤࠥჅ"))
            return
        bstack1lll11l111l_opy_ = f.bstack111l111111_opy_(instance, bstack111111l111_opy_.bstack1lll1l111l1_opy_, False)
        if bstack1lll11ll11l_opy_ == bstack11l1ll1_opy_ (u"ࠥ࡫ࡪࡺࠢ჆") and not bstack1lll11l111l_opy_:
            f.bstack1111l11l11_opy_(instance, bstack111111l111_opy_.bstack1lll1l111l1_opy_, True)
        if not bstack1lll11l111l_opy_:
            self.logger.debug(bstack11l1ll1_opy_ (u"ࠦࡳࡵࠠࡖࡔࡏࠤࡱࡵࡡࡥࡧࡧࠤ࡫ࡸࡡ࡮ࡧࡺࡳࡷࡱ࡟࡯ࡣࡰࡩࡂࢁࡦ࠯ࡨࡵࡥࡲ࡫ࡷࡰࡴ࡮ࡣࡳࡧ࡭ࡦࡿࠣࡧࡴࡳ࡭ࡢࡰࡧࡣࡳࡧ࡭ࡦ࠿ࠥჇ") + str(bstack1lll11ll11l_opy_) + bstack11l1ll1_opy_ (u"ࠧࠨ჈"))
            return
        scripts_to_run = self.commands.get(f.framework_name, {}).get(method_name, {}).get(bstack1lll11ll11l_opy_, [])
        if not scripts_to_run:
            self.logger.debug(bstack11l1ll1_opy_ (u"ࠨ࡮ࡰࠢࡤ࠵࠶ࡿࠠࡴࡥࡵ࡭ࡵࡺࡳࠡࡨࡲࡶࠥ࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫ࡠࡰࡤࡱࡪࡃࡻࡧ࠰ࡩࡶࡦࡳࡥࡸࡱࡵ࡯ࡤࡴࡡ࡮ࡧࢀࠤࡨࡵ࡭࡮ࡣࡱࡨࡤࡴࡡ࡮ࡧࡀࠦ჉") + str(bstack1lll11ll11l_opy_) + bstack11l1ll1_opy_ (u"ࠢࠣ჊"))
            return
        self.logger.info(bstack11l1ll1_opy_ (u"ࠣࡴࡸࡲࡳ࡯࡮ࡨࠢࡾࡰࡪࡴࠨࡴࡥࡵ࡭ࡵࡺࡳࡠࡶࡲࡣࡷࡻ࡮ࠪࡿࠣࡷࡨࡸࡩࡱࡶࡶࠤ࡫ࡸࡡ࡮ࡧࡺࡳࡷࡱ࡟࡯ࡣࡰࡩࡂࢁࡦ࠯ࡨࡵࡥࡲ࡫ࡷࡰࡴ࡮ࡣࡳࡧ࡭ࡦࡿࠣࡧࡴࡳ࡭ࡢࡰࡧࡣࡳࡧ࡭ࡦ࠿ࠥ჋") + str(bstack1lll11ll11l_opy_) + bstack11l1ll1_opy_ (u"ࠤࠥ჌"))
        scripts = [(s, bstack1ll1llll1l1_opy_[s]) for s in scripts_to_run if s in bstack1ll1llll1l1_opy_]
        for bstack1lll111ll11_opy_, bstack1lll1111l1l_opy_ in scripts:
            try:
                bstack1l1l1ll111_opy_ = datetime.now()
                if bstack1lll111ll11_opy_ == bstack11l1ll1_opy_ (u"ࠥࡷࡨࡧ࡮ࠣჍ"):
                    result = self.perform_scan(driver, method=bstack1lll11ll11l_opy_, framework_name=f.framework_name)
                instance.bstack111l11l1_opy_(bstack11l1ll1_opy_ (u"ࠦࡦ࠷࠱ࡺ࠼ࠥ჎") + bstack1lll111ll11_opy_, datetime.now() - bstack1l1l1ll111_opy_)
                if isinstance(result, dict) and not result.get(bstack11l1ll1_opy_ (u"ࠧࡹࡵࡤࡥࡨࡷࡸࠨ჏"), True):
                    self.logger.warning(bstack11l1ll1_opy_ (u"ࠨࡳ࡬࡫ࡳࠤࡪࡾࡥࡤࡷࡷ࡭ࡳ࡭ࠠࡳࡧࡰࡥ࡮ࡴࡩ࡯ࡩࠣࡷࡨࡸࡩࡱࡶࡶ࠾ࠥࠨა") + str(result) + bstack11l1ll1_opy_ (u"ࠢࠣბ"))
                    break
            except Exception as e:
                self.logger.error(bstack11l1ll1_opy_ (u"ࠣࡧࡵࡶࡴࡸࠠࡦࡺࡨࡧࡺࡺࡩ࡯ࡩࠣࡷࡨࡸࡩࡱࡶࡀࡿࡸࡩࡲࡪࡲࡷࡣࡳࡧ࡭ࡦࡿࠣࡩࡷࡸ࡯ࡳ࠿ࠥგ") + str(e) + bstack11l1ll1_opy_ (u"ࠤࠥდ"))
    def bstack1ll1llll11l_opy_(
        self,
        f: TestFramework,
        instance: bstack11111l1l11_opy_,
        bstack111l111l1l_opy_: Tuple[bstack1llll11llll_opy_, bstack1lll1llll11_opy_],
        *args,
        **kwargs,
    ):
        if not self.accessibility:
            self.logger.debug(bstack11l1ll1_opy_ (u"ࠥࡳࡳࡥࡡࡧࡶࡨࡶࡤࡺࡥࡴࡶ࠽ࠤࡦ࠷࠱ࡺࠢࡱࡳࡹࠦࡥ࡯ࡣࡥࡰࡪࡪࠢე"))
            return
        bstack1lll1111l11_opy_ = f.bstack111l111111_opy_(instance, bstack1llll111l11_opy_.bstack1lll1l11ll1_opy_, [])
        if not bstack1lll1111l11_opy_:
            self.logger.debug(bstack11l1ll1_opy_ (u"ࠦࡴࡴ࡟ࡢࡨࡷࡩࡷࡥࡴࡦࡵࡷ࠾ࠥࡴ࡯ࠡࡦࡵ࡭ࡻ࡫ࡲࡴࠢࡩࡳࡷࠦࡨࡰࡱ࡮ࡣ࡮ࡴࡦࡰ࠿ࡾ࡬ࡴࡵ࡫ࡠ࡫ࡱࡪࡴࢃࠠࡢࡴࡪࡷࡂࢁࡡࡳࡩࡶࢁࠥࡱࡷࡢࡴࡪࡷࡂࠨვ") + str(kwargs) + bstack11l1ll1_opy_ (u"ࠧࠨზ"))
            return
        if len(bstack1lll1111l11_opy_) > 1:
            self.logger.debug(bstack11l1ll1_opy_ (u"ࠨ࡯࡯ࡡࡤࡪࡹ࡫ࡲࡠࡶࡨࡷࡹࡀࠠࡼ࡮ࡨࡲ࠭ࡪࡲࡪࡸࡨࡶࡤ࡯࡮ࡴࡶࡤࡲࡨ࡫ࡳࠪࡿࠣࡨࡷ࡯ࡶࡦࡴࡶࠤ࡫ࡵࡲࠡࡪࡲࡳࡰࡥࡩ࡯ࡨࡲࡁࢀ࡮࡯ࡰ࡭ࡢ࡭ࡳ࡬࡯ࡾࠢࡤࡶ࡬ࡹ࠽ࡼࡣࡵ࡫ࡸࢃࠠ࡬ࡹࡤࡶ࡬ࡹ࠽ࠣთ") + str(kwargs) + bstack11l1ll1_opy_ (u"ࠢࠣი"))
        bstack1lll11lll1l_opy_, bstack1lll111l111_opy_ = bstack1lll1111l11_opy_[0]
        driver = bstack1lll11lll1l_opy_()
        if not driver:
            self.logger.debug(bstack11l1ll1_opy_ (u"ࠣࡱࡱࡣࡦ࡬ࡴࡦࡴࡢࡸࡪࡹࡴ࠻ࠢࡱࡳࠥࡪࡲࡪࡸࡨࡶࠥ࡬࡯ࡳࠢ࡫ࡳࡴࡱ࡟ࡪࡰࡩࡳࡂࢁࡨࡰࡱ࡮ࡣ࡮ࡴࡦࡰࡿࠣࡥࡷ࡭ࡳ࠾ࡽࡤࡶ࡬ࡹࡽࠡ࡭ࡺࡥࡷ࡭ࡳ࠾ࠤკ") + str(kwargs) + bstack11l1ll1_opy_ (u"ࠤࠥლ"))
            return
        test_name = f.bstack111l111111_opy_(instance, TestFramework.bstack1lll11ll111_opy_)
        if not test_name:
            self.logger.debug(bstack11l1ll1_opy_ (u"ࠥࡳࡳࡥࡡࡧࡶࡨࡶࡤࡺࡥࡴࡶ࠽ࠤࡲ࡯ࡳࡴ࡫ࡱ࡫ࠥࡺࡥࡴࡶࠣࡲࡦࡳࡥࠣმ"))
            return
        test_uuid = f.bstack111l111111_opy_(instance, TestFramework.bstack1lll111l1l1_opy_)
        if not test_uuid:
            self.logger.debug(bstack11l1ll1_opy_ (u"ࠦࡴࡴ࡟ࡢࡨࡷࡩࡷࡥࡴࡦࡵࡷ࠾ࠥࡳࡩࡴࡵ࡬ࡲ࡬ࠦࡴࡦࡵࡷࠤࡺࡻࡩࡥࠤნ"))
            return
        return self.bstack11111111l_opy_(driver, test_name, bstack1lll111l111_opy_.framework_name, test_uuid)
    def perform_scan(self, driver: object, method: Union[None, str], framework_name: str):
        bstack1lll11l1l1l_opy_ = bstack1llll111lll_opy_.bstack1lll11l1111_opy_(EVENTS.bstack11l1ll1111_opy_.value)
        if not self.accessibility:
            self.logger.debug(bstack11l1ll1_opy_ (u"ࠧࡶࡥࡳࡨࡲࡶࡲࡥࡳࡤࡣࡱ࠾ࠥࡧ࠱࠲ࡻࠣࡲࡴࡺࠠࡦࡰࡤࡦࡱ࡫ࡤࠡࡨࡵࡥࡲ࡫ࡷࡰࡴ࡮ࡣࡳࡧ࡭ࡦ࠿ࡾࡪࡷࡧ࡭ࡦࡹࡲࡶࡰࡥ࡮ࡢ࡯ࡨࢁࠥࠨო"))
            return
        bstack1l1l1ll111_opy_ = datetime.now()
        bstack1lll1111l1l_opy_ = self.scripts.get(framework_name, {}).get(bstack11l1ll1_opy_ (u"ࠨࡳࡤࡣࡱࠦპ"), None)
        if not bstack1lll1111l1l_opy_:
            self.logger.debug(bstack11l1ll1_opy_ (u"ࠢࡱࡧࡵࡪࡴࡸ࡭ࡠࡵࡦࡥࡳࡀࠠ࡮࡫ࡶࡷ࡮ࡴࡧࠡࠩࡶࡧࡦࡴࠧࠡࡵࡦࡶ࡮ࡶࡴࠡࡨࡲࡶࠥ࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫ࡠࡰࡤࡱࡪࡃࠢჟ") + str(framework_name) + bstack11l1ll1_opy_ (u"ࠣࠢࠥრ"))
            return
        instance = bstack1111llll1l_opy_.bstack1111llllll_opy_(driver)
        if instance:
            if not bstack1111llll1l_opy_.bstack111l111111_opy_(instance, bstack111111l111_opy_.bstack1lll1l11lll_opy_, False):
                bstack1111llll1l_opy_.bstack1111l11l11_opy_(instance, bstack111111l111_opy_.bstack1lll1l11lll_opy_, True)
            else:
                self.logger.info(bstack11l1ll1_opy_ (u"ࠤࡳࡩࡷ࡬࡯ࡳ࡯ࡢࡷࡨࡧ࡮࠻ࠢࡤࡰࡷ࡫ࡡࡥࡻࠣ࡭ࡳࠦࡰࡳࡱࡪࡶࡪࡹࡳࠡࡨࡵࡥࡲ࡫ࡷࡰࡴ࡮ࡣࡳࡧ࡭ࡦ࠿ࡾࡪࡷࡧ࡭ࡦࡹࡲࡶࡰࡥ࡮ࡢ࡯ࡨࢁࠥࡳࡥࡵࡪࡲࡨࡂࠨს") + str(method) + bstack11l1ll1_opy_ (u"ࠥࠦტ"))
                return
        self.logger.info(bstack11l1ll1_opy_ (u"ࠦࡵ࡫ࡲࡧࡱࡵࡱࡤࡹࡣࡢࡰ࠽ࠤ࡫ࡸࡡ࡮ࡧࡺࡳࡷࡱ࡟࡯ࡣࡰࡩࡂࢁࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࡡࡱࡥࡲ࡫ࡽࠡ࡯ࡨࡸ࡭ࡵࡤ࠾ࠤუ") + str(method) + bstack11l1ll1_opy_ (u"ࠧࠨფ"))
        result = driver.execute_async_script(bstack1lll1111l1l_opy_, {bstack11l1ll1_opy_ (u"ࠨ࡭ࡦࡶ࡫ࡳࡩࠨქ"): method if method else bstack11l1ll1_opy_ (u"ࠢࠣღ")})
        bstack1llll111lll_opy_.end(EVENTS.bstack11l1ll1111_opy_.value, bstack1lll11l1l1l_opy_+bstack11l1ll1_opy_ (u"ࠣ࠼ࡶࡸࡦࡸࡴࠣყ"), bstack1lll11l1l1l_opy_+bstack11l1ll1_opy_ (u"ࠤ࠽ࡩࡳࡪࠢშ"), True, None, command=method)
        if instance:
            bstack1111llll1l_opy_.bstack1111l11l11_opy_(instance, bstack111111l111_opy_.bstack1lll1l11lll_opy_, False)
            instance.bstack111l11l1_opy_(bstack11l1ll1_opy_ (u"ࠥࡥ࠶࠷ࡹ࠻ࡲࡨࡶ࡫ࡵࡲ࡮ࡡࡶࡧࡦࡴࠢჩ"), datetime.now() - bstack1l1l1ll111_opy_)
        return result
    @measure(event_name=EVENTS.bstack1ll11lllll_opy_, stage=STAGE.bstack1l1ll1llll_opy_)
    def get_accessibility_results(self, driver: object, framework_name):
        if not self.accessibility:
            self.logger.debug(bstack11l1ll1_opy_ (u"ࠦ࡬࡫ࡴࡠࡣࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࡠࡴࡨࡷࡺࡲࡴࡴ࠼ࠣࡥ࠶࠷ࡹࠡࡰࡲࡸࠥ࡫࡮ࡢࡤ࡯ࡩࡩࠨც"))
            return
        bstack1lll1111l1l_opy_ = self.scripts.get(framework_name, {}).get(bstack11l1ll1_opy_ (u"ࠧ࡭ࡥࡵࡔࡨࡷࡺࡲࡴࡴࠤძ"), None)
        if not bstack1lll1111l1l_opy_:
            self.logger.debug(bstack11l1ll1_opy_ (u"ࠨ࡭ࡪࡵࡶ࡭ࡳ࡭ࠠࠨࡩࡨࡸࡗ࡫ࡳࡶ࡮ࡷࡷࠬࠦࡳࡤࡴ࡬ࡴࡹࠦࡦࡰࡴࠣࡪࡷࡧ࡭ࡦࡹࡲࡶࡰࡥ࡮ࡢ࡯ࡨࡁࠧწ") + str(framework_name) + bstack11l1ll1_opy_ (u"ࠢࠣჭ"))
            return
        self.perform_scan(driver, method=None, framework_name=framework_name)
        bstack1l1l1ll111_opy_ = datetime.now()
        result = driver.execute_async_script(bstack1lll1111l1l_opy_)
        instance = bstack1111llll1l_opy_.bstack1111llllll_opy_(driver)
        if instance:
            instance.bstack111l11l1_opy_(bstack11l1ll1_opy_ (u"ࠣࡣ࠴࠵ࡾࡀࡧࡦࡶࡢࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࡢࡶࡪࡹࡵ࡭ࡶࡶࠦხ"), datetime.now() - bstack1l1l1ll111_opy_)
        return result
    @measure(event_name=EVENTS.bstack11l1ll11l1_opy_, stage=STAGE.bstack1l1ll1llll_opy_)
    def get_accessibility_results_summary(self, driver: object, framework_name):
        if not self.accessibility:
            self.logger.debug(bstack11l1ll1_opy_ (u"ࠤࡪࡩࡹࡥࡡࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾࡥࡲࡦࡵࡸࡰࡹࡹ࡟ࡴࡷࡰࡱࡦࡸࡹ࠻ࠢࡤ࠵࠶ࡿࠠ࡯ࡱࡷࠤࡪࡴࡡࡣ࡮ࡨࡨࠧჯ"))
            return
        bstack1lll1111l1l_opy_ = self.scripts.get(framework_name, {}).get(bstack11l1ll1_opy_ (u"ࠥ࡫ࡪࡺࡒࡦࡵࡸࡰࡹࡹࡓࡶ࡯ࡰࡥࡷࡿࠢჰ"), None)
        if not bstack1lll1111l1l_opy_:
            self.logger.debug(bstack11l1ll1_opy_ (u"ࠦࡲ࡯ࡳࡴ࡫ࡱ࡫ࠥ࠭ࡧࡦࡶࡕࡩࡸࡻ࡬ࡵࡵࡖࡹࡲࡳࡡࡳࡻࠪࠤࡸࡩࡲࡪࡲࡷࠤ࡫ࡵࡲࠡࡨࡵࡥࡲ࡫ࡷࡰࡴ࡮ࡣࡳࡧ࡭ࡦ࠿ࠥჱ") + str(framework_name) + bstack11l1ll1_opy_ (u"ࠧࠨჲ"))
            return
        self.perform_scan(driver, method=None, framework_name=framework_name)
        bstack1l1l1ll111_opy_ = datetime.now()
        result = driver.execute_async_script(bstack1lll1111l1l_opy_)
        instance = bstack1111llll1l_opy_.bstack1111llllll_opy_(driver)
        if instance:
            instance.bstack111l11l1_opy_(bstack11l1ll1_opy_ (u"ࠨࡡ࠲࠳ࡼ࠾࡬࡫ࡴࡠࡣࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࡠࡴࡨࡷࡺࡲࡴࡴࡡࡶࡹࡲࡳࡡࡳࡻࠥჳ"), datetime.now() - bstack1l1l1ll111_opy_)
        return result
    @measure(event_name=EVENTS.bstack1lll11lll11_opy_, stage=STAGE.bstack1l1ll1llll_opy_)
    def bstack1lll11l11l1_opy_(
        self,
        platform_index: int,
        framework_name: str,
        framework_version: str,
        hub_url: str,
    ):
        self.bstack1lll111l1ll_opy_()
        req = structs.AccessibilityConfigRequest()
        req.bin_session_id = self.bin_session_id
        req.platform_index = platform_index
        req.framework_name = framework_name
        req.framework_version = framework_version
        req.hub_url = hub_url
        try:
            r = self.bstack11111111l1_opy_.AccessibilityConfig(req)
            if not r.success:
                self.logger.debug(bstack11l1ll1_opy_ (u"ࠢࡳࡧࡦࡩ࡮ࡼࡥࡥࠢࡩࡶࡴࡳࠠࡴࡧࡵࡺࡪࡸ࠺ࠡࠤჴ") + str(r) + bstack11l1ll1_opy_ (u"ࠣࠤჵ"))
            else:
                self.bstack1lll111llll_opy_(framework_name, r)
            return r
        except grpc.RpcError as e:
            self.logger.error(bstack11l1ll1_opy_ (u"ࠤࡵࡴࡨ࠳ࡥࡳࡴࡲࡶ࠿ࠦࠢჶ") + str(e) + bstack11l1ll1_opy_ (u"ࠥࠦჷ"))
            traceback.print_exc()
            raise e
    def bstack1lll111llll_opy_(self, framework_name: str, result: structs.AccessibilityConfigResponse) -> bool:
        if not result.success or not result.accessibility.success:
            self.logger.debug(bstack11l1ll1_opy_ (u"ࠦࡱࡵࡡࡥࡡࡦࡳࡳ࡬ࡩࡨ࠼ࠣࡥ࠶࠷ࡹࠡࡰࡲࡸࠥ࡬࡯ࡶࡰࡧࠦჸ"))
            return False
        if result.accessibility.options:
            options = result.accessibility.options
            if options.scripts:
                self.scripts[framework_name] = {row.name: row.command for row in options.scripts}
            if options.commands_to_wrap and options.commands_to_wrap.commands:
                scripts_to_run = [s for s in options.commands_to_wrap.scripts_to_run]
                if not scripts_to_run:
                    return False
                bstack1ll1lllll1l_opy_ = dict()
                for command in options.commands_to_wrap.commands:
                    if command.library == self.bstack1lll111111l_opy_ and command.module == self.bstack1lll111l11l_opy_:
                        if command.method and not command.method in bstack1ll1lllll1l_opy_:
                            bstack1ll1lllll1l_opy_[command.method] = dict()
                        if command.name and not command.name in bstack1ll1lllll1l_opy_[command.method]:
                            bstack1ll1lllll1l_opy_[command.method][command.name] = list()
                        bstack1ll1lllll1l_opy_[command.method][command.name].extend(scripts_to_run)
                self.commands[framework_name] = bstack1ll1lllll1l_opy_
        return bool(self.commands.get(framework_name, None))
    def bstack1lll11lllll_opy_(
        self,
        f: bstack1llllllll1l_opy_,
        exec: Tuple[bstack1111l11l1l_opy_, str],
        *args,
        **kwargs,
    ):
        instance, method_name = exec
        if bstack1111llll1l_opy_.bstack111l1111ll_opy_(instance, bstack111111l111_opy_.bstack1ll1lllll11_opy_):
            return
        if not f.bstack1lll111ll1l_opy_(instance):
            if not bstack111111l111_opy_.bstack1lll11l1l11_opy_:
                self.logger.warning(bstack11l1ll1_opy_ (u"ࠧࡧ࠱࠲ࡻࠣࡪࡱࡵࡷࠡࡦ࡬ࡷࡦࡨ࡬ࡦࡦࠣࡪࡴࡸࠠ࡯ࡱࡱ࠱ࡇࡸ࡯ࡸࡵࡨࡶࡘࡺࡡࡤ࡭ࠣ࡭ࡳ࡬ࡲࡢࠤჹ"))
                bstack111111l111_opy_.bstack1lll11l1l11_opy_ = True
            return
        if f.bstack1lll1111ll1_opy_(method_name, *args):
            bstack1ll1llll1ll_opy_ = False
            desired_capabilities = f.bstack1lll1l11111_opy_(instance)
            if isinstance(desired_capabilities, dict):
                hub_url = f.bstack1lll1111111_opy_(instance)
                platform_index = f.bstack111l111111_opy_(instance, bstack1llllllll1l_opy_.bstack1lll11ll1l1_opy_, 0)
                bstack1lll11ll1ll_opy_ = datetime.now()
                r = self.bstack1lll11l11l1_opy_(platform_index, f.framework_name, f.framework_version, hub_url)
                instance.bstack111l11l1_opy_(bstack11l1ll1_opy_ (u"ࠨࡧࡳࡲࡦ࠾ࡦࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࡣࡨࡵ࡮ࡧ࡫ࡪࠦჺ"), datetime.now() - bstack1lll11ll1ll_opy_)
                bstack1ll1llll1ll_opy_ = r.success
            else:
                self.logger.error(bstack11l1ll1_opy_ (u"ࠢ࡮࡫ࡶࡷ࡮ࡴࡧࠡࡦࡨࡷ࡮ࡸࡥࡥࠢࡦࡥࡵࡧࡢࡪ࡮࡬ࡸ࡮࡫ࡳ࠾ࠤ჻") + str(desired_capabilities) + bstack11l1ll1_opy_ (u"ࠣࠤჼ"))
            f.bstack1111l11l11_opy_(instance, bstack111111l111_opy_.bstack1ll1lllll11_opy_, bstack1ll1llll1ll_opy_)
    def bstack1lllll11l_opy_(self, test_tags):
        bstack1lll11l11l1_opy_ = self.config.get(bstack11l1ll1_opy_ (u"ࠩࡤࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࡑࡳࡸ࡮ࡵ࡮ࡴࠩჽ"))
        if not bstack1lll11l11l1_opy_:
            return True
        try:
            include_tags = bstack1lll11l11l1_opy_[bstack11l1ll1_opy_ (u"ࠪ࡭ࡳࡩ࡬ࡶࡦࡨࡘࡦ࡭ࡳࡊࡰࡗࡩࡸࡺࡩ࡯ࡩࡖࡧࡴࡶࡥࠨჾ")] if bstack11l1ll1_opy_ (u"ࠫ࡮ࡴࡣ࡭ࡷࡧࡩ࡙ࡧࡧࡴࡋࡱࡘࡪࡹࡴࡪࡰࡪࡗࡨࡵࡰࡦࠩჿ") in bstack1lll11l11l1_opy_ and isinstance(bstack1lll11l11l1_opy_[bstack11l1ll1_opy_ (u"ࠬ࡯࡮ࡤ࡮ࡸࡨࡪ࡚ࡡࡨࡵࡌࡲ࡙࡫ࡳࡵ࡫ࡱ࡫ࡘࡩ࡯ࡱࡧࠪᄀ")], list) else []
            exclude_tags = bstack1lll11l11l1_opy_[bstack11l1ll1_opy_ (u"࠭ࡥࡹࡥ࡯ࡹࡩ࡫ࡔࡢࡩࡶࡍࡳ࡚ࡥࡴࡶ࡬ࡲ࡬࡙ࡣࡰࡲࡨࠫᄁ")] if bstack11l1ll1_opy_ (u"ࠧࡦࡺࡦࡰࡺࡪࡥࡕࡣࡪࡷࡎࡴࡔࡦࡵࡷ࡭ࡳ࡭ࡓࡤࡱࡳࡩࠬᄂ") in bstack1lll11l11l1_opy_ and isinstance(bstack1lll11l11l1_opy_[bstack11l1ll1_opy_ (u"ࠨࡧࡻࡧࡱࡻࡤࡦࡖࡤ࡫ࡸࡏ࡮ࡕࡧࡶࡸ࡮ࡴࡧࡔࡥࡲࡴࡪ࠭ᄃ")], list) else []
            excluded = any(tag in exclude_tags for tag in test_tags)
            included = len(include_tags) == 0 or any(tag in include_tags for tag in test_tags)
            return not excluded and included
        except Exception as error:
            self.logger.debug(bstack11l1ll1_opy_ (u"ࠤࡈࡶࡷࡵࡲࠡࡹ࡫࡭ࡱ࡫ࠠࡷࡣ࡯࡭ࡩࡧࡴࡪࡰࡪࠤࡹ࡫ࡳࡵࠢࡦࡥࡸ࡫ࠠࡧࡱࡵࠤࡦࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࠤࡧ࡫ࡦࡰࡴࡨࠤࡸࡩࡡ࡯ࡰ࡬ࡲ࡬࠴ࠠࡆࡴࡵࡳࡷࠦ࠺ࠡࠤᄄ") + str(error))
        return False
    def bstack11llllll_opy_(self, caps):
        try:
            bstack1ll1llllll1_opy_ = caps.get(bstack11l1ll1_opy_ (u"ࠪࡦࡸࡺࡡࡤ࡭࠽ࡳࡵࡺࡩࡰࡰࡶࠫᄅ"), {}).get(bstack11l1ll1_opy_ (u"ࠫࡩ࡫ࡶࡪࡥࡨࡒࡦࡳࡥࠨᄆ"), caps.get(bstack11l1ll1_opy_ (u"ࠬࡪࡥࡷ࡫ࡦࡩࠬᄇ"), bstack11l1ll1_opy_ (u"࠭ࠧᄈ")))
            if bstack1ll1llllll1_opy_:
                self.logger.warning(bstack11l1ll1_opy_ (u"ࠢࡂࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࠠࡂࡷࡷࡳࡲࡧࡴࡪࡱࡱࠤࡼ࡯࡬࡭ࠢࡵࡹࡳࠦ࡯࡯࡮ࡼࠤࡴࡴࠠࡅࡧࡶ࡯ࡹࡵࡰࠡࡤࡵࡳࡼࡹࡥࡳࡵ࠱ࠦᄉ"))
                return False
            browser = caps.get(bstack11l1ll1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡐࡤࡱࡪ࠭ᄊ"), bstack11l1ll1_opy_ (u"ࠩࠪᄋ")).lower()
            if browser != bstack11l1ll1_opy_ (u"ࠪࡧ࡭ࡸ࡯࡮ࡧࠪᄌ"):
                self.logger.warning(bstack11l1ll1_opy_ (u"ࠦࡆࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࠤࡆࡻࡴࡰ࡯ࡤࡸ࡮ࡵ࡮ࠡࡹ࡬ࡰࡱࠦࡲࡶࡰࠣࡳࡳࡲࡹࠡࡱࡱࠤࡈ࡮ࡲࡰ࡯ࡨࠤࡧࡸ࡯ࡸࡵࡨࡶࡸ࠴ࠢᄍ"))
                return False
            browser_version = caps.get(bstack11l1ll1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷ࡜ࡥࡳࡵ࡬ࡳࡳ࠭ᄎ"))
            if browser_version and browser_version != bstack11l1ll1_opy_ (u"࠭࡬ࡢࡶࡨࡷࡹ࠭ᄏ") and int(browser_version.split(bstack11l1ll1_opy_ (u"ࠧ࠯ࠩᄐ"))[0]) <= 98:
                self.logger.warning(bstack11l1ll1_opy_ (u"ࠣࡃࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࠡࡃࡸࡸࡴࡳࡡࡵ࡫ࡲࡲࠥࡽࡩ࡭࡮ࠣࡶࡺࡴࠠࡰࡰ࡯ࡽࠥࡵ࡮ࠡࡅ࡫ࡶࡴࡳࡥࠡࡤࡵࡳࡼࡹࡥࡳࠢࡹࡩࡷࡹࡩࡰࡰࠣ࡫ࡷ࡫ࡡࡵࡧࡵࠤࡹ࡮ࡡ࡯ࠢ࠼࠼࠳ࠨᄑ"))
                return False
            bstack1lll1l11l1l_opy_ = caps.get(bstack11l1ll1_opy_ (u"ࠩࡥࡷࡹࡧࡣ࡬࠼ࡲࡴࡹ࡯࡯࡯ࡵࠪᄒ"), {}).get(bstack11l1ll1_opy_ (u"ࠪࡧ࡭ࡸ࡯࡮ࡧࡒࡴࡹ࡯࡯࡯ࡵࠪᄓ"))
            if bstack1lll1l11l1l_opy_ and bstack11l1ll1_opy_ (u"ࠫ࠲࠳ࡨࡦࡣࡧࡰࡪࡹࡳࠨᄔ") in bstack1lll1l11l1l_opy_.get(bstack11l1ll1_opy_ (u"ࠬࡧࡲࡨࡵࠪᄕ"), []):
                self.logger.warning(bstack11l1ll1_opy_ (u"ࠨࡁࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾࠦࡁࡶࡶࡲࡱࡦࡺࡩࡰࡰࠣࡻ࡮ࡲ࡬ࠡࡰࡲࡸࠥࡸࡵ࡯ࠢࡲࡲࠥࡲࡥࡨࡣࡦࡽࠥ࡮ࡥࡢࡦ࡯ࡩࡸࡹࠠ࡮ࡱࡧࡩ࠳ࠦࡓࡸ࡫ࡷࡧ࡭ࠦࡴࡰࠢࡱࡩࡼࠦࡨࡦࡣࡧࡰࡪࡹࡳࠡ࡯ࡲࡨࡪࠦ࡯ࡳࠢࡤࡺࡴ࡯ࡤࠡࡷࡶ࡭ࡳ࡭ࠠࡩࡧࡤࡨࡱ࡫ࡳࡴࠢࡰࡳࡩ࡫࠮ࠣᄖ"))
                return False
            return True
        except Exception as error:
            self.logger.debug(bstack11l1ll1_opy_ (u"ࠢࡆࡺࡦࡩࡵࡺࡩࡰࡰࠣ࡭ࡳࠦࡶࡢ࡮࡬ࡨࡦࡺࡥࠡࡣ࠴࠵ࡾࠦࡳࡶࡲࡳࡳࡷࡺࠠ࠻ࠤᄗ") + str(error))
            return False
    def bstack11111111l_opy_(self, driver: object, name: str, framework_name: str, test_uuid: str):
        bstack1lll11l1l1l_opy_ = None
        try:
            bstack1lll11l1ll1_opy_ = {
                bstack11l1ll1_opy_ (u"ࠨࡶ࡫ࡘࡪࡹࡴࡓࡷࡱ࡙ࡺ࡯ࡤࠨᄘ"): test_uuid,
                bstack11l1ll1_opy_ (u"ࠩࡷ࡬ࡇࡻࡩ࡭ࡦࡘࡹ࡮ࡪࠧᄙ"): os.environ.get(bstack11l1ll1_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡗࡉࡘ࡚ࡈࡖࡄࡢ࡙࡚ࡏࡄࠨᄚ"), bstack11l1ll1_opy_ (u"ࠫࠬᄛ")),
                bstack11l1ll1_opy_ (u"ࠬࡺࡨࡋࡹࡷࡘࡴࡱࡥ࡯ࠩᄜ"): os.environ.get(bstack11l1ll1_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤ࡚ࡅࡔࡖࡋ࡙ࡇࡥࡊࡘࡖࠪᄝ"), bstack11l1ll1_opy_ (u"ࠧࠨᄞ"))
            }
            self.logger.debug(bstack11l1ll1_opy_ (u"ࠨࡒࡨࡶ࡫ࡵࡲ࡮࡫ࡱ࡫ࠥࡹࡣࡢࡰࠣࡦࡪ࡬࡯ࡳࡧࠣࡷࡦࡼࡩ࡯ࡩࠣࡶࡪࡹࡵ࡭ࡶࡶࠫᄟ") + str(bstack1lll11l1ll1_opy_))
            self.perform_scan(driver, name, framework_name=framework_name)
            bstack1lll1111l1l_opy_ = self.scripts.get(framework_name, {}).get(bstack11l1ll1_opy_ (u"ࠤࡶࡥࡻ࡫ࡒࡦࡵࡸࡰࡹࡹࠢᄠ"), None)
            if not bstack1lll1111l1l_opy_:
                self.logger.debug(bstack11l1ll1_opy_ (u"ࠥࡴࡪࡸࡦࡰࡴࡰࡣࡸࡩࡡ࡯࠼ࠣࡱ࡮ࡹࡳࡪࡰࡪࠤࠬࡹࡡࡷࡧࡕࡩࡸࡻ࡬ࡵࡵࠪࠤࡸࡩࡲࡪࡲࡷࠤ࡫ࡵࡲࠡࡨࡵࡥࡲ࡫ࡷࡰࡴ࡮ࡣࡳࡧ࡭ࡦ࠿ࠥᄡ") + str(framework_name) + bstack11l1ll1_opy_ (u"ࠦࠥࠨᄢ"))
                return
            bstack1lll11l1l1l_opy_ = bstack1llll111lll_opy_.bstack1lll11l1111_opy_(EVENTS.bstack1lll1111lll_opy_.value)
            self.logger.debug(driver.execute_async_script(bstack1lll1111l1l_opy_, bstack1lll11l1ll1_opy_))
            self.logger.info(bstack11l1ll1_opy_ (u"ࠧࡇࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠥࡺࡥࡴࡶ࡬ࡲ࡬ࠦࡦࡰࡴࠣࡸ࡭࡯ࡳࠡࡶࡨࡷࡹࠦࡣࡢࡵࡨࠤ࡭ࡧࡳࠡࡧࡱࡨࡪࡪ࠮ࠣᄣ"))
            bstack1llll111lll_opy_.end(EVENTS.bstack1lll1111lll_opy_.value, bstack1lll11l1l1l_opy_+bstack11l1ll1_opy_ (u"ࠨ࠺ࡴࡶࡤࡶࡹࠨᄤ"), bstack1lll11l1l1l_opy_+bstack11l1ll1_opy_ (u"ࠢ࠻ࡧࡱࡨࠧᄥ"), True, None, command=bstack11l1ll1_opy_ (u"ࠨࡵࡤࡺࡪࡘࡥࡴࡷ࡯ࡸࡸ࠭ᄦ"),test_name=name)
        except Exception as bstack1lll11111ll_opy_:
            self.logger.error(bstack11l1ll1_opy_ (u"ࠤࡄࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࠢࡵࡩࡸࡻ࡬ࡵࡵࠣࡧࡴࡻ࡬ࡥࠢࡱࡳࡹࠦࡢࡦࠢࡳࡶࡴࡩࡥࡴࡵࡨࡨࠥ࡬࡯ࡳࠢࡷ࡬ࡪࠦࡴࡦࡵࡷࠤࡨࡧࡳࡦ࠼ࠣࠦᄧ") + bstack11l1ll1_opy_ (u"ࠥࡷࡹࡸࠨࡱࡣࡷ࡬࠮ࠨᄨ") + bstack11l1ll1_opy_ (u"ࠦࠥࡋࡲࡳࡱࡵࠤ࠿ࠨᄩ") + str(bstack1lll11111ll_opy_))
            bstack1llll111lll_opy_.end(EVENTS.bstack1lll1111lll_opy_.value, bstack1lll11l1l1l_opy_+bstack11l1ll1_opy_ (u"ࠧࡀࡳࡵࡣࡵࡸࠧᄪ"), bstack1lll11l1l1l_opy_+bstack11l1ll1_opy_ (u"ࠨ࠺ࡦࡰࡧࠦᄫ"), False, bstack1lll11111ll_opy_, command=bstack11l1ll1_opy_ (u"ࠧࡴࡣࡹࡩࡗ࡫ࡳࡶ࡮ࡷࡷࠬᄬ"),test_name=name)
    def _1ll1lllllll_opy_(self, instance: bstack11111l1l11_opy_, args: Tuple) -> list:
        bstack11l1ll1_opy_ (u"ࠣࠤࠥࡉࡽࡺࡲࡢࡥࡷࠤࡹࡧࡧࡴࠢࡥࡥࡸ࡫ࡤࠡࡱࡱࠤࡹ࡮ࡥࠡࡶࡨࡷࡹࠦࡦࡳࡣࡰࡩࡼࡵࡲ࡬࠰ࠥࠦࠧᄭ")
        if bstack11l1ll1_opy_ (u"ࠩࡳࡽࡹ࡫ࡳࡵ࠯ࡥࡨࡩ࠭ᄮ") in instance.bstack1lll1l1l111_opy_:
            return args[2].tags if hasattr(args[2], bstack11l1ll1_opy_ (u"ࠪࡸࡦ࡭ࡳࠨᄯ")) else []
        if hasattr(args[0], bstack11l1ll1_opy_ (u"ࠫࡴࡽ࡮ࡠ࡯ࡤࡶࡰ࡫ࡲࡴࠩᄰ")):
            return [marker.name for marker in args[0].own_markers]
        return []