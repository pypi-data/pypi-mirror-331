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
    bstack1111l11l1l_opy_,
)
from browserstack_sdk.sdk_cli.bstack1111111lll_opy_ import bstack1llllllll1l_opy_
from typing import Tuple, Callable, Any
import grpc
from browserstack_sdk import sdk_pb2 as structs
from browserstack_sdk.sdk_cli.bstack1llll11111l_opy_ import bstack1111111l1l_opy_
from bstack_utils.measure import measure
from bstack_utils.constants import *
import traceback
import os
import time
class bstack1lll1lll1l1_opy_(bstack1111111l1l_opy_):
    bstack1lll11l1l11_opy_ = False
    def __init__(self):
        super().__init__()
        bstack1llllllll1l_opy_.bstack1lll11llll1_opy_((bstack1111ll111l_opy_.bstack1111l1l11l_opy_, bstack1111l1l1l1_opy_.PRE), self.bstack1ll1lll11ll_opy_)
    def is_enabled(self) -> bool:
        return True
    def bstack1ll1lll11ll_opy_(
        self,
        f: bstack1llllllll1l_opy_,
        driver: object,
        exec: Tuple[bstack1111l11l1l_opy_, str],
        bstack111l111l1l_opy_: Tuple[bstack1111ll111l_opy_, bstack1111l1l1l1_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
        hub_url = f.hub_url(driver)
        if f.bstack1ll1lll1lll_opy_(hub_url):
            if not bstack1lll1lll1l1_opy_.bstack1lll11l1l11_opy_:
                self.logger.warning(bstack11l1ll1_opy_ (u"ࠧࡲ࡯ࡤࡣ࡯ࠤࡸ࡫࡬ࡧ࠯࡫ࡩࡦࡲࠠࡧ࡮ࡲࡻࠥࡪࡩࡴࡣࡥࡰࡪࡪࠠࡧࡱࡵࠤࡇࡸ࡯ࡸࡵࡨࡶࡘࡺࡡࡤ࡭ࠣ࡭ࡳ࡬ࡲࡢࠢࡶࡩࡸࡹࡩࡰࡰࡶࠤ࡭ࡻࡢࡠࡷࡵࡰࡂࠨᄱ") + str(hub_url) + bstack11l1ll1_opy_ (u"ࠨࠢᄲ"))
                bstack1lll1lll1l1_opy_.bstack1lll11l1l11_opy_ = True
            return
        bstack1lll11ll11l_opy_ = f.bstack1lll11l11ll_opy_(*args)
        bstack1ll1lll1l1l_opy_ = f.bstack1ll1ll1lll1_opy_(*args)
        if bstack1lll11ll11l_opy_ and bstack1lll11ll11l_opy_.lower() == bstack11l1ll1_opy_ (u"ࠢࡧ࡫ࡱࡨࡪࡲࡥ࡮ࡧࡱࡸࠧᄳ") and bstack1ll1lll1l1l_opy_:
            framework_session_id = f.session_id(driver)
            locator_type, locator_value = bstack1ll1lll1l1l_opy_.get(bstack11l1ll1_opy_ (u"ࠣࡷࡶ࡭ࡳ࡭ࠢᄴ"), None), bstack1ll1lll1l1l_opy_.get(bstack11l1ll1_opy_ (u"ࠤࡹࡥࡱࡻࡥࠣᄵ"), None)
            if not framework_session_id or not locator_type or not locator_value:
                self.logger.warning(bstack11l1ll1_opy_ (u"ࠥࡿࡨࡵ࡭࡮ࡣࡱࡨࡤࡴࡡ࡮ࡧࢀ࠾ࠥࡳࡩࡴࡵ࡬ࡲ࡬ࠦࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࡡࡶࡩࡸࡹࡩࡰࡰࡢ࡭ࡩࠦ࡯ࡳࠢࡤࡶ࡬ࡹ࠮ࡶࡵ࡬ࡲ࡬ࡃࡻ࡭ࡱࡦࡥࡹࡵࡲࡠࡶࡼࡴࡪࢃࠠࡰࡴࠣࡥࡷ࡭ࡳ࠯ࡸࡤࡰࡺ࡫࠽ࠣᄶ") + str(locator_value) + bstack11l1ll1_opy_ (u"ࠦࠧᄷ"))
                return
            def bstack1111l1l1ll_opy_(driver, bstack1ll1ll1llll_opy_, *args, **kwargs):
                from selenium.common.exceptions import NoSuchElementException
                try:
                    result = bstack1ll1ll1llll_opy_(driver, *args, **kwargs)
                    response = self.bstack1ll1lll1l11_opy_(
                        framework_session_id=framework_session_id,
                        is_success=True,
                        locator_type=locator_type,
                        locator_value=locator_value,
                    )
                    if response and response.execute_script:
                        driver.execute_script(response.execute_script)
                        self.logger.info(bstack11l1ll1_opy_ (u"ࠧࡹࡵࡤࡥࡨࡷࡸ࠳ࡳࡤࡴ࡬ࡴࡹࡀࠠ࡭ࡱࡦࡥࡹࡵࡲࡠࡶࡼࡴࡪࡃࡻ࡭ࡱࡦࡥࡹࡵࡲࡠࡶࡼࡴࡪࢃࠠ࡭ࡱࡦࡥࡹࡵࡲࡠࡸࡤࡰࡺ࡫࠽ࠣᄸ") + str(locator_value) + bstack11l1ll1_opy_ (u"ࠨࠢᄹ"))
                    else:
                        self.logger.warning(bstack11l1ll1_opy_ (u"ࠢࡴࡷࡦࡧࡪࡹࡳ࠮ࡰࡲ࠱ࡸࡩࡲࡪࡲࡷ࠾ࠥࡲ࡯ࡤࡣࡷࡳࡷࡥࡴࡺࡲࡨࡁࢀࡲ࡯ࡤࡣࡷࡳࡷࡥࡴࡺࡲࡨࢁࠥࡲ࡯ࡤࡣࡷࡳࡷࡥࡶࡢ࡮ࡸࡩࡂࢁ࡬ࡰࡥࡤࡸࡴࡸ࡟ࡷࡣ࡯ࡹࡪࢃࠠࡳࡧࡶࡴࡴࡴࡳࡦ࠿ࠥᄺ") + str(response) + bstack11l1ll1_opy_ (u"ࠣࠤᄻ"))
                    return result
                except NoSuchElementException as e:
                    locator = (locator_type, locator_value)
                    return self.__1ll1lll111l_opy_(
                        driver, bstack1ll1ll1llll_opy_, e, framework_session_id, locator, *args, **kwargs
                    )
            bstack1111l1l1ll_opy_.__name__ = bstack1lll11ll11l_opy_
            return bstack1111l1l1ll_opy_
    def __1ll1lll111l_opy_(
        self,
        driver,
        bstack1ll1ll1llll_opy_: Callable,
        exception,
        framework_session_id: str,
        locator: Tuple[str, str],
        *args,
        **kwargs,
    ):
        try:
            locator_type, locator_value = locator
            response = self.bstack1ll1lll1l11_opy_(
                framework_session_id=framework_session_id,
                is_success=False,
                locator_type=locator_type,
                locator_value=locator_value,
            )
            if response and response.execute_script:
                driver.execute_script(response.execute_script)
                self.logger.info(bstack11l1ll1_opy_ (u"ࠤࡩࡥ࡮ࡲࡵࡳࡧ࠰࡬ࡪࡧ࡬ࡪࡰࡪ࠱ࡹࡸࡩࡨࡩࡨࡶࡪࡪ࠺ࠡ࡮ࡲࡧࡦࡺ࡯ࡳࡡࡷࡽࡵ࡫࠽ࡼ࡮ࡲࡧࡦࡺ࡯ࡳࡡࡷࡽࡵ࡫ࡽࠡ࡮ࡲࡧࡦࡺ࡯ࡳࡡࡹࡥࡱࡻࡥ࠾ࠤᄼ") + str(locator_value) + bstack11l1ll1_opy_ (u"ࠥࠦᄽ"))
                bstack1ll1lll11l1_opy_ = self.bstack1ll1lll1ll1_opy_(
                    framework_session_id=framework_session_id,
                    locator_type=locator_type,
                )
                self.logger.info(bstack11l1ll1_opy_ (u"ࠦ࡫ࡧࡩ࡭ࡷࡵࡩ࠲࡮ࡥࡢ࡮࡬ࡲ࡬࠳ࡲࡦࡵࡸࡰࡹࡀࠠ࡭ࡱࡦࡥࡹࡵࡲࡠࡶࡼࡴࡪࡃࡻ࡭ࡱࡦࡥࡹࡵࡲࡠࡶࡼࡴࡪࢃࠠ࡭ࡱࡦࡥࡹࡵࡲࡠࡸࡤࡰࡺ࡫࠽ࡼ࡮ࡲࡧࡦࡺ࡯ࡳࡡࡹࡥࡱࡻࡥࡾࠢ࡫ࡩࡦࡲࡩ࡯ࡩࡢࡶࡪࡹࡵ࡭ࡶࡀࠦᄾ") + str(bstack1ll1lll11l1_opy_) + bstack11l1ll1_opy_ (u"ࠧࠨᄿ"))
                if bstack1ll1lll11l1_opy_.success and args and len(args) > 1:
                    args[1].update(
                        {
                            bstack11l1ll1_opy_ (u"ࠨࡵࡴ࡫ࡱ࡫ࠧᅀ"): bstack1ll1lll11l1_opy_.locator_type,
                            bstack11l1ll1_opy_ (u"ࠢࡷࡣ࡯ࡹࡪࠨᅁ"): bstack1ll1lll11l1_opy_.locator_value,
                        }
                    )
                    return bstack1ll1ll1llll_opy_(driver, *args, **kwargs)
                elif os.environ.get(bstack11l1ll1_opy_ (u"ࠣࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡂࡋࡢࡈࡊࡈࡕࡈࠤᅂ"), False):
                    self.logger.info(bstack11111l1ll1_opy_ (u"ࠤࡩࡥ࡮ࡲࡵࡳࡧ࠰࡬ࡪࡧ࡬ࡪࡰࡪ࠱ࡷ࡫ࡳࡶ࡮ࡷ࠱ࡲ࡯ࡳࡴ࡫ࡱ࡫࠿ࠦࡳ࡭ࡧࡨࡴ࠭࠹࠰ࠪࠢ࡯ࡩࡹࡺࡩ࡯ࡩࠣࡽࡴࡻࠠࡪࡰࡶࡴࡪࡩࡴࠡࡶ࡫ࡩࠥࡨࡲࡰࡹࡶࡩࡷࠦࡥࡹࡶࡨࡲࡸ࡯࡯࡯ࠢ࡯ࡳ࡬ࡹࠢᅃ"))
                    time.sleep(300)
            else:
                self.logger.warning(bstack11l1ll1_opy_ (u"ࠥࡪࡦ࡯࡬ࡶࡴࡨ࠱ࡳࡵ࠭ࡴࡥࡵ࡭ࡵࡺ࠺ࠡ࡮ࡲࡧࡦࡺ࡯ࡳࡡࡷࡽࡵ࡫࠽ࡼ࡮ࡲࡧࡦࡺ࡯ࡳࡡࡷࡽࡵ࡫ࡽࠡ࡮ࡲࡧࡦࡺ࡯ࡳࡡࡹࡥࡱࡻࡥ࠾ࡽ࡯ࡳࡨࡧࡴࡰࡴࡢࡺࡦࡲࡵࡦࡿࠣࡶࡪࡹࡰࡰࡰࡶࡩࡂࠨᅄ") + str(response) + bstack11l1ll1_opy_ (u"ࠦࠧᅅ"))
        except Exception as err:
            self.logger.warning(bstack11l1ll1_opy_ (u"ࠧ࡬ࡡࡪ࡮ࡸࡶࡪ࠳ࡨࡦࡣ࡯࡭ࡳ࡭࠭ࡳࡧࡶࡹࡱࡺ࠺ࠡࡧࡵࡶࡴࡸ࠺ࠡࠤᅆ") + str(err) + bstack11l1ll1_opy_ (u"ࠨࠢᅇ"))
        raise exception
    @measure(event_name=EVENTS.bstack1ll1lll1111_opy_, stage=STAGE.bstack1l1ll1llll_opy_)
    def bstack1ll1lll1l11_opy_(
        self,
        framework_session_id: str,
        is_success: bool,
        locator_type: str,
        locator_value: str,
        platform_index=bstack11l1ll1_opy_ (u"ࠢ࠱ࠤᅈ"),
    ):
        self.bstack1lll111l1ll_opy_()
        req = structs.AISelfHealStepRequest()
        req.bin_session_id = self.bin_session_id
        req.platform_index = platform_index
        req.framework_session_id = framework_session_id
        req.is_success = is_success
        req.test_name = bstack11l1ll1_opy_ (u"ࠣࠤᅉ")
        req.locator_type = locator_type
        req.locator_value = locator_value
        try:
            r = self.bstack11111111l1_opy_.AISelfHealStep(req)
            self.logger.info(bstack11l1ll1_opy_ (u"ࠤࡵࡩࡨ࡫ࡩࡷࡧࡧࠤ࡫ࡸ࡯࡮ࠢࡶࡩࡷࡼࡥࡳ࠼ࠣࠦᅊ") + str(r) + bstack11l1ll1_opy_ (u"ࠥࠦᅋ"))
            return r
        except grpc.RpcError as e:
            self.logger.error(bstack11l1ll1_opy_ (u"ࠦࡷࡶࡣ࠮ࡧࡵࡶࡴࡸ࠺ࠡࠤᅌ") + str(e) + bstack11l1ll1_opy_ (u"ࠧࠨᅍ"))
            traceback.print_exc()
            raise e
    @measure(event_name=EVENTS.bstack1ll1ll1ll1l_opy_, stage=STAGE.bstack1l1ll1llll_opy_)
    def bstack1ll1lll1ll1_opy_(self, framework_session_id: str, locator_type: str, platform_index=bstack11l1ll1_opy_ (u"ࠨ࠰ࠣᅎ")):
        self.bstack1lll111l1ll_opy_()
        req = structs.AISelfHealGetRequest()
        req.bin_session_id = self.bin_session_id
        req.platform_index = platform_index
        req.framework_session_id = framework_session_id
        req.locator_type = locator_type
        try:
            r = self.bstack11111111l1_opy_.AISelfHealGetResult(req)
            self.logger.info(bstack11l1ll1_opy_ (u"ࠢࡳࡧࡦࡩ࡮ࡼࡥࡥࠢࡩࡶࡴࡳࠠࡴࡧࡵࡺࡪࡸ࠺ࠡࠤᅏ") + str(r) + bstack11l1ll1_opy_ (u"ࠣࠤᅐ"))
            return r
        except grpc.RpcError as e:
            self.logger.error(bstack11l1ll1_opy_ (u"ࠤࡵࡴࡨ࠳ࡥࡳࡴࡲࡶ࠿ࠦࠢᅑ") + str(e) + bstack11l1ll1_opy_ (u"ࠥࠦᅒ"))
            traceback.print_exc()
            raise e