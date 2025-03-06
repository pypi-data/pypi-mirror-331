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
import os
import grpc
from browserstack_sdk import sdk_pb2 as structs
from packaging import version
import traceback
from browserstack_sdk.sdk_cli.bstack1llll11111l_opy_ import bstack1111111l1l_opy_
from browserstack_sdk.sdk_cli.bstack1111ll1l11_opy_ import (
    bstack1111ll111l_opy_,
    bstack1111l1l1l1_opy_,
    bstack1111l11l1l_opy_,
)
from browserstack_sdk.sdk_cli.bstack1111111lll_opy_ import bstack1llllllll1l_opy_
from datetime import datetime
from typing import Tuple, Any
from bstack_utils.messages import bstack1ll1ll11_opy_
from bstack_utils.measure import measure
from bstack_utils.constants import *
import threading
import os
from bstack_utils.bstack1ll111ll1l_opy_ import bstack1llll111lll_opy_
class bstack1lll1ll1lll_opy_(bstack1111111l1l_opy_):
    bstack1ll111lll11_opy_ = bstack11l1ll1_opy_ (u"ࠨࡲࡦࡩ࡬ࡷࡹ࡫ࡲࡠ࡫ࡱ࡭ࡹࠨᇨ")
    bstack1ll111ll111_opy_ = bstack11l1ll1_opy_ (u"ࠢࡳࡧࡪ࡭ࡸࡺࡥࡳࡡࡶࡸࡦࡸࡴࠣᇩ")
    bstack1ll111ll1l1_opy_ = bstack11l1ll1_opy_ (u"ࠣࡴࡨ࡫࡮ࡹࡴࡦࡴࡢࡷࡹࡵࡰࠣᇪ")
    def __init__(self):
        super().__init__()
        bstack1llllllll1l_opy_.bstack1lll11llll1_opy_((bstack1111ll111l_opy_.bstack1111ll1ll1_opy_, bstack1111l1l1l1_opy_.PRE), self.bstack1ll111l1111_opy_)
        bstack1llllllll1l_opy_.bstack1lll11llll1_opy_((bstack1111ll111l_opy_.bstack1111l1l11l_opy_, bstack1111l1l1l1_opy_.PRE), self.bstack1ll1lll11ll_opy_)
        bstack1llllllll1l_opy_.bstack1lll11llll1_opy_((bstack1111ll111l_opy_.bstack1111l1l11l_opy_, bstack1111l1l1l1_opy_.POST), self.bstack1ll1111111l_opy_)
        bstack1llllllll1l_opy_.bstack1lll11llll1_opy_((bstack1111ll111l_opy_.bstack1111l1l11l_opy_, bstack1111l1l1l1_opy_.POST), self.bstack1ll1111ll11_opy_)
        bstack1llllllll1l_opy_.bstack1lll11llll1_opy_((bstack1111ll111l_opy_.QUIT, bstack1111l1l1l1_opy_.POST), self.bstack1ll1111l111_opy_)
    def is_enabled(self) -> bool:
        return True
    def bstack1ll111l1111_opy_(
        self,
        f: bstack1llllllll1l_opy_,
        driver: object,
        exec: Tuple[bstack1111l11l1l_opy_, str],
        bstack111l111l1l_opy_: Tuple[bstack1111ll111l_opy_, bstack1111l1l1l1_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
        instance, method_name = exec
        if method_name != bstack11l1ll1_opy_ (u"ࠤࡢࡣ࡮ࡴࡩࡵࡡࡢࠦᇫ"):
            return
        def wrapped(driver, init, *args, **kwargs):
            self.bstack1ll111l1ll1_opy_(instance, f, kwargs)
            self.logger.debug(bstack11l1ll1_opy_ (u"ࠥࡨࡷ࡯ࡶࡦࡴ࠱ࡿࡲ࡫ࡴࡩࡱࡧࡣࡳࡧ࡭ࡦࡿࠣࡴࡱࡧࡴࡧࡱࡵࡱࡤ࡯࡮ࡥࡧࡻࡁࢀ࡬࠮ࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡡ࡬ࡲࡩ࡫ࡸࡾ࠼ࠣࡥࡷ࡭ࡳ࠾ࡽࡤࡶ࡬ࡹࡽࠡ࡭ࡺࡥࡷ࡭ࡳ࠾ࠤᇬ") + str(kwargs) + bstack11l1ll1_opy_ (u"ࠦࠧᇭ"))
            threading.current_thread().bstackSessionDriver = driver
            return init(driver, *args, **kwargs)
        return wrapped
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
        instance, method_name = exec
        if f.bstack111l111111_opy_(instance, bstack1lll1ll1lll_opy_.bstack1ll111lll11_opy_, False):
            return
        if not f.bstack111l1111ll_opy_(instance, bstack1llllllll1l_opy_.bstack1lll11ll1l1_opy_):
            return
        platform_index = f.bstack111l111111_opy_(instance, bstack1llllllll1l_opy_.bstack1lll11ll1l1_opy_)
        if f.bstack1lll1111ll1_opy_(method_name, *args) and len(args) > 1:
            bstack1l1l1ll111_opy_ = datetime.now()
            hub_url = bstack1llllllll1l_opy_.hub_url(driver)
            self.logger.warning(bstack11l1ll1_opy_ (u"ࠧ࡮ࡵࡣࡡࡸࡶࡱࡃࠢᇮ") + str(hub_url) + bstack11l1ll1_opy_ (u"ࠨࠢᇯ"))
            bstack1ll1111l1ll_opy_ = args[1][bstack11l1ll1_opy_ (u"ࠢࡤࡣࡳࡥࡧ࡯࡬ࡪࡶ࡬ࡩࡸࠨᇰ")] if isinstance(args[1], dict) and bstack11l1ll1_opy_ (u"ࠣࡥࡤࡴࡦࡨࡩ࡭࡫ࡷ࡭ࡪࡹࠢᇱ") in args[1] else None
            bstack1ll11111l11_opy_ = bstack11l1ll1_opy_ (u"ࠤࡤࡰࡼࡧࡹࡴࡏࡤࡸࡨ࡮ࠢᇲ")
            if isinstance(bstack1ll1111l1ll_opy_, dict):
                bstack1l1l1ll111_opy_ = datetime.now()
                r = self.bstack1ll1111ll1l_opy_(
                    instance.ref(),
                    platform_index,
                    f.framework_name,
                    f.framework_version,
                    hub_url
                )
                instance.bstack111l11l1_opy_(bstack11l1ll1_opy_ (u"ࠥ࡫ࡷࡶࡣ࠻ࡴࡨ࡫࡮ࡹࡴࡦࡴࡢ࡭ࡳ࡯ࡴࠣᇳ"), datetime.now() - bstack1l1l1ll111_opy_)
                try:
                    if not r.success:
                        self.logger.info(bstack11l1ll1_opy_ (u"ࠦࡸࡵ࡭ࡦࡶ࡫࡭ࡳ࡭ࠠࡸࡧࡱࡸࠥࡽࡲࡰࡰࡪ࠾ࠥࠨᇴ") + str(r) + bstack11l1ll1_opy_ (u"ࠧࠨᇵ"))
                        return
                    if r.hub_url:
                        f.bstack1ll111l111l_opy_(instance, driver, r.hub_url)
                        f.bstack1111l11l11_opy_(instance, bstack1lll1ll1lll_opy_.bstack1ll111lll11_opy_, True)
                except Exception as e:
                    self.logger.error(bstack11l1ll1_opy_ (u"ࠨࡥࡳࡴࡲࡶࠧᇶ"), e)
    def bstack1ll1111111l_opy_(
        self,
        f: bstack1llllllll1l_opy_,
        driver: object,
        exec: Tuple[bstack1111l11l1l_opy_, str],
        bstack111l111l1l_opy_: Tuple[bstack1111ll111l_opy_, bstack1111l1l1l1_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
            session_id = bstack1llllllll1l_opy_.session_id(driver)
            if session_id:
                bstack1l1llllllll_opy_ = bstack11l1ll1_opy_ (u"ࠢࡼࡿ࠽ࡷࡹࡧࡲࡵࠤᇷ").format(session_id)
                bstack1llll111lll_opy_.mark(bstack1l1llllllll_opy_)
    def bstack1ll1111ll11_opy_(
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
        if f.bstack111l111111_opy_(instance, bstack1lll1ll1lll_opy_.bstack1ll111ll111_opy_, False):
            return
        ref = instance.ref()
        hub_url = bstack1llllllll1l_opy_.hub_url(driver)
        if not hub_url:
            self.logger.warning(bstack11l1ll1_opy_ (u"ࠣࡨࡤ࡭ࡱ࡫ࡤࠡࡶࡲࠤࡵࡧࡲࡴࡧࠣ࡬ࡺࡨ࡟ࡶࡴ࡯ࡁࠧᇸ") + str(hub_url) + bstack11l1ll1_opy_ (u"ࠤࠥᇹ"))
            return
        framework_session_id = bstack1llllllll1l_opy_.session_id(driver)
        if not framework_session_id:
            self.logger.warning(bstack11l1ll1_opy_ (u"ࠥࡪࡦ࡯࡬ࡦࡦࠣࡸࡴࠦࡰࡢࡴࡶࡩࠥ࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫ࡠࡵࡨࡷࡸ࡯࡯࡯ࡡ࡬ࡨࡂࠨᇺ") + str(framework_session_id) + bstack11l1ll1_opy_ (u"ࠦࠧᇻ"))
            return
        if bstack1llllllll1l_opy_.bstack1ll111l11l1_opy_(*args) == bstack1llllllll1l_opy_.bstack1ll111l1l11_opy_:
            bstack1l1lllllll1_opy_ = bstack11l1ll1_opy_ (u"ࠧࢁࡽ࠻ࡧࡱࡨࠧᇼ").format(framework_session_id)
            bstack1l1llllllll_opy_ = bstack11l1ll1_opy_ (u"ࠨࡻࡾ࠼ࡶࡸࡦࡸࡴࠣᇽ").format(framework_session_id)
            bstack1llll111lll_opy_.end(
                label=bstack11l1ll1_opy_ (u"ࠢࡴࡦ࡮࠾ࡩࡸࡩࡷࡧࡵ࠾ࡵࡵࡳࡵ࠯࡬ࡲ࡮ࡺࡩࡢ࡮࡬ࡾࡦࡺࡩࡰࡰࠥᇾ"),
                start=bstack1l1llllllll_opy_,
                end=bstack1l1lllllll1_opy_,
                status=True,
                failure=None
            )
            bstack1l1l1ll111_opy_ = datetime.now()
            r = self.bstack1ll11111111_opy_(
                ref,
                f.bstack111l111111_opy_(instance, bstack1llllllll1l_opy_.bstack1lll11ll1l1_opy_, 0),
                f.framework_name,
                f.framework_version,
                framework_session_id,
                hub_url,
            )
            instance.bstack111l11l1_opy_(bstack11l1ll1_opy_ (u"ࠣࡩࡵࡴࡨࡀࡲࡦࡩ࡬ࡷࡹ࡫ࡲࡠࡵࡷࡥࡷࡺࠢᇿ"), datetime.now() - bstack1l1l1ll111_opy_)
            f.bstack1111l11l11_opy_(instance, bstack1lll1ll1lll_opy_.bstack1ll111ll111_opy_, r.success)
    def bstack1ll1111l111_opy_(
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
        if f.bstack111l111111_opy_(instance, bstack1lll1ll1lll_opy_.bstack1ll111ll1l1_opy_, False):
            return
        ref = instance.ref()
        framework_session_id = bstack1llllllll1l_opy_.session_id(driver)
        hub_url = bstack1llllllll1l_opy_.hub_url(driver)
        bstack1l1l1ll111_opy_ = datetime.now()
        r = self.bstack1ll111l1l1l_opy_(
            ref,
            f.bstack111l111111_opy_(instance, bstack1llllllll1l_opy_.bstack1lll11ll1l1_opy_, 0),
            f.framework_name,
            f.framework_version,
            framework_session_id,
            hub_url,
        )
        instance.bstack111l11l1_opy_(bstack11l1ll1_opy_ (u"ࠤࡪࡶࡵࡩ࠺ࡳࡧࡪ࡭ࡸࡺࡥࡳࡡࡶࡸࡴࡶࠢሀ"), datetime.now() - bstack1l1l1ll111_opy_)
        f.bstack1111l11l11_opy_(instance, bstack1lll1ll1lll_opy_.bstack1ll111ll1l1_opy_, r.success)
    @measure(event_name=EVENTS.bstack11111ll11_opy_, stage=STAGE.bstack1l1ll1llll_opy_)
    def bstack1ll1111llll_opy_(self, platform_index: int, ref, user_input_params: bytes):
        req = structs.DriverInitRequest()
        req.bin_session_id = self.bin_session_id
        req.platform_index = platform_index
        req.user_input_params = user_input_params
        req.ref = ref
        self.logger.debug(bstack11l1ll1_opy_ (u"ࠥࡶࡪ࡭ࡩࡴࡶࡨࡶࡤࡽࡥࡣࡦࡵ࡭ࡻ࡫ࡲࡠ࡫ࡱ࡭ࡹࡀࠠࠣሁ") + str(req) + bstack11l1ll1_opy_ (u"ࠦࠧሂ"))
        try:
            r = self.bstack11111111l1_opy_.DriverInit(req)
            if not r.success:
                self.logger.debug(bstack11l1ll1_opy_ (u"ࠧࡸࡥࡤࡧ࡬ࡺࡪࡪࠠࡧࡴࡲࡱࠥࡹࡥࡳࡸࡨࡶ࠿ࠦࡳࡶࡥࡦࡩࡸࡹ࠽ࠣሃ") + str(r.success) + bstack11l1ll1_opy_ (u"ࠨࠢሄ"))
            return r
        except grpc.RpcError as e:
            self.logger.error(bstack11l1ll1_opy_ (u"ࠢࡳࡲࡦ࠱ࡪࡸࡲࡰࡴ࠽ࠤࠧህ") + str(e) + bstack11l1ll1_opy_ (u"ࠣࠤሆ"))
            traceback.print_exc()
            raise e
    @measure(event_name=EVENTS.bstack1l1llllll1l_opy_, stage=STAGE.bstack1l1ll1llll_opy_)
    def bstack1ll1111ll1l_opy_(
        self,
        ref: str,
        platform_index: int,
        framework_name: str,
        framework_version: str,
        hub_url: str
    ):
        self.bstack1lll111l1ll_opy_()
        req = structs.AutomationFrameworkInitRequest()
        req.ref = ref
        req.bin_session_id = self.bin_session_id
        req.platform_index = platform_index
        req.framework_name = framework_name
        req.framework_version = framework_version
        req.hub_url = hub_url
        self.logger.debug(bstack11l1ll1_opy_ (u"ࠤࡵࡩ࡬࡯ࡳࡵࡧࡵࡣ࡮ࡴࡩࡵ࠼ࠣࠦሇ") + str(req) + bstack11l1ll1_opy_ (u"ࠥࠦለ"))
        try:
            r = self.bstack11111111l1_opy_.AutomationFrameworkInit(req)
            if not r.success:
                self.logger.debug(bstack11l1ll1_opy_ (u"ࠦࡷ࡫ࡣࡦ࡫ࡹࡩࡩࠦࡦࡳࡱࡰࠤࡸ࡫ࡲࡷࡧࡵ࠾ࠥࡹࡵࡤࡥࡨࡷࡸࡃࠢሉ") + str(r.success) + bstack11l1ll1_opy_ (u"ࠧࠨሊ"))
            return r
        except grpc.RpcError as e:
            self.logger.error(bstack11l1ll1_opy_ (u"ࠨࡲࡱࡥ࠰ࡩࡷࡸ࡯ࡳ࠼ࠣࠦላ") + str(e) + bstack11l1ll1_opy_ (u"ࠢࠣሌ"))
            traceback.print_exc()
            raise e
    @measure(event_name=EVENTS.bstack1l1llllll11_opy_, stage=STAGE.bstack1l1ll1llll_opy_)
    def bstack1ll11111111_opy_(
        self,
        ref: str,
        platform_index: int,
        framework_name: str,
        framework_version: str,
        framework_session_id: str,
        hub_url: str,
    ):
        self.bstack1lll111l1ll_opy_()
        req = structs.AutomationFrameworkStartRequest()
        req.ref = ref
        req.bin_session_id = self.bin_session_id
        req.platform_index = platform_index
        req.framework_name = framework_name
        req.framework_version = framework_version
        req.framework_session_id = framework_session_id
        req.hub_url = hub_url
        self.logger.debug(bstack11l1ll1_opy_ (u"ࠣࡴࡨ࡫࡮ࡹࡴࡦࡴࡢࡷࡹࡧࡲࡵ࠼ࠣࠦል") + str(req) + bstack11l1ll1_opy_ (u"ࠤࠥሎ"))
        try:
            r = self.bstack11111111l1_opy_.AutomationFrameworkStart(req)
            if not r.success:
                self.logger.debug(bstack11l1ll1_opy_ (u"ࠥࡶࡪࡩࡥࡪࡸࡨࡨࠥ࡬ࡲࡰ࡯ࠣࡷࡪࡸࡶࡦࡴ࠽ࠤࠧሏ") + str(r) + bstack11l1ll1_opy_ (u"ࠦࠧሐ"))
            return r
        except grpc.RpcError as e:
            self.logger.error(bstack11l1ll1_opy_ (u"ࠧࡸࡰࡤ࠯ࡨࡶࡷࡵࡲ࠻ࠢࠥሑ") + str(e) + bstack11l1ll1_opy_ (u"ࠨࠢሒ"))
            traceback.print_exc()
            raise e
    @measure(event_name=EVENTS.bstack1ll111ll1ll_opy_, stage=STAGE.bstack1l1ll1llll_opy_)
    def bstack1ll111l1l1l_opy_(
        self,
        ref: str,
        platform_index: int,
        framework_name: str,
        framework_version: str,
        framework_session_id: str,
        hub_url: str,
    ):
        self.bstack1lll111l1ll_opy_()
        req = structs.AutomationFrameworkStopRequest()
        req.ref = ref
        req.bin_session_id = self.bin_session_id
        req.platform_index = platform_index
        req.framework_name = framework_name
        req.framework_version = framework_version
        req.framework_session_id = framework_session_id
        req.hub_url = hub_url
        self.logger.debug(bstack11l1ll1_opy_ (u"ࠢࡳࡧࡪ࡭ࡸࡺࡥࡳࡡࡶࡸࡴࡶ࠺ࠡࠤሓ") + str(req) + bstack11l1ll1_opy_ (u"ࠣࠤሔ"))
        try:
            r = self.bstack11111111l1_opy_.AutomationFrameworkStop(req)
            if not r.success:
                self.logger.debug(bstack11l1ll1_opy_ (u"ࠤࡵࡩࡨ࡫ࡩࡷࡧࡧࠤ࡫ࡸ࡯࡮ࠢࡶࡩࡷࡼࡥࡳ࠼ࠣࠦሕ") + str(r) + bstack11l1ll1_opy_ (u"ࠥࠦሖ"))
            return r
        except grpc.RpcError as e:
            self.logger.error(bstack11l1ll1_opy_ (u"ࠦࡷࡶࡣ࠮ࡧࡵࡶࡴࡸ࠺ࠡࠤሗ") + str(e) + bstack11l1ll1_opy_ (u"ࠧࠨመ"))
            traceback.print_exc()
            raise e
    @measure(event_name=EVENTS.bstack1l1ll1ll1_opy_, stage=STAGE.bstack1l1ll1llll_opy_)
    def bstack1ll111l1ll1_opy_(self, instance: bstack1111l11l1l_opy_, f: bstack1llllllll1l_opy_, kwargs):
        bstack1ll111111ll_opy_ = version.parse(f.framework_version)
        bstack1ll1111l1l1_opy_ = kwargs.get(bstack11l1ll1_opy_ (u"ࠨ࡯ࡱࡶ࡬ࡳࡳࡹࠢሙ"))
        bstack1ll1111lll1_opy_ = kwargs.get(bstack11l1ll1_opy_ (u"ࠢࡥࡧࡶ࡭ࡷ࡫ࡤࡠࡥࡤࡴࡦࡨࡩ࡭࡫ࡷ࡭ࡪࡹࠢሚ"))
        bstack1ll11111l1l_opy_ = {}
        bstack1ll111l1lll_opy_ = {}
        bstack1ll111l11ll_opy_ = None
        bstack1ll111111l1_opy_ = {}
        if bstack1ll1111lll1_opy_ is not None or bstack1ll1111l1l1_opy_ is not None: # check top level caps
            if bstack1ll1111lll1_opy_ is not None:
                bstack1ll111111l1_opy_[bstack11l1ll1_opy_ (u"ࠨࡦࡨࡷ࡮ࡸࡥࡥࡡࡦࡥࡵࡧࡢࡪ࡮࡬ࡸ࡮࡫ࡳࠨማ")] = bstack1ll1111lll1_opy_
            if bstack1ll1111l1l1_opy_ is not None and callable(getattr(bstack1ll1111l1l1_opy_, bstack11l1ll1_opy_ (u"ࠤࡷࡳࡤࡩࡡࡱࡣࡥ࡭ࡱ࡯ࡴࡪࡧࡶࠦሜ"))):
                bstack1ll111111l1_opy_[bstack11l1ll1_opy_ (u"ࠪࡳࡵࡺࡩࡰࡰࡶࡣࡦࡹ࡟ࡤࡣࡳࡥࡧ࡯࡬ࡪࡶ࡬ࡩࡸ࠭ም")] = bstack1ll1111l1l1_opy_.to_capabilities()
        response = self.bstack1ll1111llll_opy_(f.platform_index, instance.ref(), json.dumps(bstack1ll111111l1_opy_).encode(bstack11l1ll1_opy_ (u"ࠦࡺࡺࡦ࠮࠺ࠥሞ")))
        if response is not None and response.capabilities:
            bstack1ll11111l1l_opy_ = json.loads(response.capabilities.decode(bstack11l1ll1_opy_ (u"ࠧࡻࡴࡧ࠯࠻ࠦሟ")))
            if not bstack1ll11111l1l_opy_: # empty caps bstack1ll11111lll_opy_ bstack1ll1111l11l_opy_ bstack1ll111ll11l_opy_ bstack1llll1llll1_opy_ or error in processing
                return
            bstack1ll111l11ll_opy_ = f.bstack1lllll1ll11_opy_[bstack11l1ll1_opy_ (u"ࠨࡣࡳࡧࡤࡸࡪࡥ࡯ࡱࡶ࡬ࡳࡳࡹ࡟ࡧࡴࡲࡱࡤࡩࡡࡱࡵࠥሠ")](bstack1ll11111l1l_opy_)
        if bstack1ll1111l1l1_opy_ is not None and bstack1ll111111ll_opy_ >= version.parse(bstack11l1ll1_opy_ (u"ࠧ࠴࠰࠻࠲࠵࠭ሡ")):
            bstack1ll111l1lll_opy_ = None
        if (
                not bstack1ll1111l1l1_opy_ and not bstack1ll1111lll1_opy_
        ) or (
                bstack1ll111111ll_opy_ < version.parse(bstack11l1ll1_opy_ (u"ࠨ࠵࠱࠼࠳࠶ࠧሢ"))
        ):
            bstack1ll111l1lll_opy_ = {}
            bstack1ll111l1lll_opy_.update(bstack1ll11111l1l_opy_)
        self.logger.info(bstack1ll1ll11_opy_)
        if os.environ.get(bstack11l1ll1_opy_ (u"ࠤࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡃࡘࡘࡔࡓࡁࡕࡋࡒࡒࠧሣ")).lower().__eq__(bstack11l1ll1_opy_ (u"ࠥࡸࡷࡻࡥࠣሤ")):
            kwargs.update(
                {
                    bstack11l1ll1_opy_ (u"ࠦࡨࡵ࡭࡮ࡣࡱࡨࡤ࡫ࡸࡦࡥࡸࡸࡴࡸࠢሥ"): f.bstack1ll11111ll1_opy_,
                }
            )
        if bstack1ll111111ll_opy_ >= version.parse(bstack11l1ll1_opy_ (u"ࠬ࠺࠮࠲࠲࠱࠴ࠬሦ")):
            if bstack1ll1111lll1_opy_ is not None:
                del kwargs[bstack11l1ll1_opy_ (u"ࠨࡤࡦࡵ࡬ࡶࡪࡪ࡟ࡤࡣࡳࡥࡧ࡯࡬ࡪࡶ࡬ࡩࡸࠨሧ")]
            kwargs.update(
                {
                    bstack11l1ll1_opy_ (u"ࠢࡰࡲࡷ࡭ࡴࡴࡳࠣረ"): bstack1ll111l11ll_opy_,
                    bstack11l1ll1_opy_ (u"ࠣ࡭ࡨࡩࡵࡥࡡ࡭࡫ࡹࡩࠧሩ"): True,
                    bstack11l1ll1_opy_ (u"ࠤࡩ࡭ࡱ࡫࡟ࡥࡧࡷࡩࡨࡺ࡯ࡳࠤሪ"): None,
                }
            )
        elif bstack1ll111111ll_opy_ >= version.parse(bstack11l1ll1_opy_ (u"ࠪ࠷࠳࠾࠮࠱ࠩራ")):
            kwargs.update(
                {
                    bstack11l1ll1_opy_ (u"ࠦࡩ࡫ࡳࡪࡴࡨࡨࡤࡩࡡࡱࡣࡥ࡭ࡱ࡯ࡴࡪࡧࡶࠦሬ"): bstack1ll111l1lll_opy_,
                    bstack11l1ll1_opy_ (u"ࠧࡵࡰࡵ࡫ࡲࡲࡸࠨር"): bstack1ll111l11ll_opy_,
                    bstack11l1ll1_opy_ (u"ࠨ࡫ࡦࡧࡳࡣࡦࡲࡩࡷࡧࠥሮ"): True,
                    bstack11l1ll1_opy_ (u"ࠢࡧ࡫࡯ࡩࡤࡪࡥࡵࡧࡦࡸࡴࡸࠢሯ"): None,
                }
            )
        elif bstack1ll111111ll_opy_ >= version.parse(bstack11l1ll1_opy_ (u"ࠨ࠴࠱࠹࠸࠴࠰ࠨሰ")):
            kwargs.update(
                {
                    bstack11l1ll1_opy_ (u"ࠤࡧࡩࡸ࡯ࡲࡦࡦࡢࡧࡦࡶࡡࡣ࡫࡯࡭ࡹ࡯ࡥࡴࠤሱ"): bstack1ll111l1lll_opy_,
                    bstack11l1ll1_opy_ (u"ࠥ࡯ࡪ࡫ࡰࡠࡣ࡯࡭ࡻ࡫ࠢሲ"): True,
                    bstack11l1ll1_opy_ (u"ࠦ࡫࡯࡬ࡦࡡࡧࡩࡹ࡫ࡣࡵࡱࡵࠦሳ"): None,
                }
            )
        else:
            kwargs.update(
                {
                    bstack11l1ll1_opy_ (u"ࠧࡪࡥࡴ࡫ࡵࡩࡩࡥࡣࡢࡲࡤࡦ࡮ࡲࡩࡵ࡫ࡨࡷࠧሴ"): bstack1ll111l1lll_opy_,
                    bstack11l1ll1_opy_ (u"ࠨ࡫ࡦࡧࡳࡣࡦࡲࡩࡷࡧࠥስ"): True,
                    bstack11l1ll1_opy_ (u"ࠢࡧ࡫࡯ࡩࡤࡪࡥࡵࡧࡦࡸࡴࡸࠢሶ"): None,
                }
            )