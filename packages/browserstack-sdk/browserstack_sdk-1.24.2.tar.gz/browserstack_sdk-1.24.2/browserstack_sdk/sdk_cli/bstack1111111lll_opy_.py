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
import traceback
from typing import Dict, Tuple, Callable, Type, List, Any
from urllib.parse import urlparse
from browserstack_sdk.sdk_cli.bstack1111ll1l11_opy_ import (
    bstack1111llll1l_opy_,
    bstack1111l11l1l_opy_,
    bstack1111ll111l_opy_,
    bstack1111l1l1l1_opy_,
)
import copy
from datetime import datetime, timezone, timedelta
from bstack_utils.bstack1ll111ll1l_opy_ import bstack1llll111lll_opy_
from bstack_utils.constants import EVENTS
class bstack1llllllll1l_opy_(bstack1111llll1l_opy_):
    bstack1l1l11lllll_opy_ = bstack11l1ll1_opy_ (u"ࠦࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡔࡑࡇࡔࡇࡑࡕࡑࡤࡏࡎࡅࡇ࡛ࠦ፧")
    NAME = bstack11l1ll1_opy_ (u"ࠧࡹࡥ࡭ࡧࡱ࡭ࡺࡳࠢ፨")
    bstack1ll1l11l111_opy_ = bstack11l1ll1_opy_ (u"ࠨࡨࡶࡤࡢࡹࡷࡲࠢ፩")
    bstack1ll11l1llll_opy_ = bstack11l1ll1_opy_ (u"ࠢࡧࡴࡤࡱࡪࡽ࡯ࡳ࡭ࡢࡷࡪࡹࡳࡪࡱࡱࡣ࡮ࡪࠢ፪")
    bstack1l1l11ll11l_opy_ = bstack11l1ll1_opy_ (u"ࠣ࡫ࡱࡴࡺࡺ࡟ࡤࡣࡳࡥࡧ࡯࡬ࡪࡶ࡬ࡩࡸࠨ፫")
    bstack1ll1llll111_opy_ = bstack11l1ll1_opy_ (u"ࠤࡦࡥࡵࡧࡢࡪ࡮࡬ࡸ࡮࡫ࡳࠣ፬")
    bstack1ll1l111l1l_opy_ = bstack11l1ll1_opy_ (u"ࠥ࡭ࡸࡥࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡤ࡮ࡵࡣࠤ፭")
    bstack1l1l11l1lll_opy_ = bstack11l1ll1_opy_ (u"ࠦࡸࡺࡡࡳࡶࡨࡨࡤࡧࡴࠣ፮")
    bstack1l1l11l11l1_opy_ = bstack11l1ll1_opy_ (u"ࠧ࡫࡮ࡥࡧࡧࡣࡦࡺࠢ፯")
    bstack1lll11ll1l1_opy_ = bstack11l1ll1_opy_ (u"ࠨࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡠ࡫ࡱࡨࡪࡾࠢ፰")
    bstack1ll111l1l11_opy_ = bstack11l1ll1_opy_ (u"ࠢ࡯ࡧࡺࡷࡪࡹࡳࡪࡱࡱࠦ፱")
    bstack1l1l11l1l11_opy_ = bstack11l1ll1_opy_ (u"ࠣࡩࡨࡸࠧ፲")
    bstack1ll11ll1ll1_opy_ = bstack11l1ll1_opy_ (u"ࠤࡶࡧࡷ࡫ࡥ࡯ࡵ࡫ࡳࡹࠨ፳")
    bstack1l1l11lll1l_opy_ = bstack11l1ll1_opy_ (u"ࠥࡻ࠸ࡩࡥࡹࡧࡦࡹࡹ࡫ࡳࡤࡴ࡬ࡴࡹࠨ፴")
    bstack1l1l11llll1_opy_ = bstack11l1ll1_opy_ (u"ࠦࡼ࠹ࡣࡦࡺࡨࡧࡺࡺࡥࡴࡥࡵ࡭ࡵࡺࡡࡴࡻࡱࡧࠧ፵")
    bstack1l1l11lll11_opy_ = bstack11l1ll1_opy_ (u"ࠧࡷࡵࡪࡶࠥ፶")
    bstack1l1l11l111l_opy_: Dict[str, List[Callable]] = dict()
    bstack1ll11111ll1_opy_: str
    platform_index: int
    options: Any
    desired_capabilities: Any
    bstack1lllll1ll11_opy_: Any
    bstack1l1l1l11111_opy_: Dict
    def __init__(
        self,
        bstack1ll11111ll1_opy_: str,
        platform_index: int,
        framework_name: str,
        framework_version: str,
        classes: List[Type],
        bstack1lllll1ll11_opy_: Dict[str, Any],
        methods=[bstack11l1ll1_opy_ (u"ࠨ࡟ࡠ࡫ࡱ࡭ࡹࡥ࡟ࠣ፷"), bstack11l1ll1_opy_ (u"ࠢࡴࡶࡤࡶࡹࡥࡳࡦࡵࡶ࡭ࡴࡴࠢ፸"), bstack11l1ll1_opy_ (u"ࠣࡧࡻࡩࡨࡻࡴࡦࠤ፹"), bstack11l1ll1_opy_ (u"ࠤࡴࡹ࡮ࡺࠢ፺")],
    ):
        super().__init__(
            framework_name,
            framework_version,
            classes,
        )
        self.bstack1ll11111ll1_opy_ = bstack1ll11111ll1_opy_
        self.platform_index = platform_index
        self.bstack1111l11ll1_opy_(methods)
        self.bstack1lllll1ll11_opy_ = bstack1lllll1ll11_opy_
    @staticmethod
    def session_id(target: object, strict=True):
        return bstack1111llll1l_opy_.get_data(bstack1llllllll1l_opy_.bstack1ll11l1llll_opy_, target, strict)
    @staticmethod
    def hub_url(target: object, strict=True):
        return bstack1111llll1l_opy_.get_data(bstack1llllllll1l_opy_.bstack1ll1l11l111_opy_, target, strict)
    @staticmethod
    def bstack1l1l11l11ll_opy_(target: object, strict=True):
        return bstack1111llll1l_opy_.get_data(bstack1llllllll1l_opy_.bstack1l1l11ll11l_opy_, target, strict)
    @staticmethod
    def capabilities(target: object, strict=True):
        return bstack1111llll1l_opy_.get_data(bstack1llllllll1l_opy_.bstack1ll1llll111_opy_, target, strict)
    @staticmethod
    def bstack1lll111ll1l_opy_(instance: bstack1111l11l1l_opy_) -> bool:
        return bstack1111llll1l_opy_.bstack111l111111_opy_(instance, bstack1llllllll1l_opy_.bstack1ll1l111l1l_opy_, False)
    @staticmethod
    def bstack1lll1111111_opy_(instance: bstack1111l11l1l_opy_, default_value=None):
        return bstack1111llll1l_opy_.bstack111l111111_opy_(instance, bstack1llllllll1l_opy_.bstack1ll1l11l111_opy_, default_value)
    @staticmethod
    def bstack1lll1l11111_opy_(instance: bstack1111l11l1l_opy_, default_value=None):
        return bstack1111llll1l_opy_.bstack111l111111_opy_(instance, bstack1llllllll1l_opy_.bstack1ll1llll111_opy_, default_value)
    @staticmethod
    def bstack1ll1lll1lll_opy_(hub_url: str, bstack1l1l11l1l1l_opy_=bstack11l1ll1_opy_ (u"ࠥ࠲ࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡧࡴࡳࠢ፻")):
        try:
            bstack1l1l11ll1l1_opy_ = str(urlparse(hub_url).netloc) if hub_url else None
            return bstack1l1l11ll1l1_opy_.endswith(bstack1l1l11l1l1l_opy_)
        except:
            pass
        return False
    @staticmethod
    def bstack1lll111lll1_opy_(method_name: str):
        return method_name == bstack11l1ll1_opy_ (u"ࠦࡪࡾࡥࡤࡷࡷࡩࠧ፼")
    @staticmethod
    def bstack1lll1111ll1_opy_(method_name: str, *args):
        return (
            bstack1llllllll1l_opy_.bstack1lll111lll1_opy_(method_name)
            and bstack1llllllll1l_opy_.bstack1ll111l11l1_opy_(*args) == bstack1llllllll1l_opy_.bstack1ll111l1l11_opy_
        )
    @staticmethod
    def bstack1lll1l11l11_opy_(method_name: str, *args):
        if not bstack1llllllll1l_opy_.bstack1lll111lll1_opy_(method_name):
            return False
        if not bstack1llllllll1l_opy_.bstack1l1l11lll1l_opy_ in bstack1llllllll1l_opy_.bstack1ll111l11l1_opy_(*args):
            return False
        bstack1ll1lll1l1l_opy_ = bstack1llllllll1l_opy_.bstack1ll1ll1lll1_opy_(*args)
        return bstack1ll1lll1l1l_opy_ and bstack11l1ll1_opy_ (u"ࠧࡹࡣࡳ࡫ࡳࡸࠧ፽") in bstack1ll1lll1l1l_opy_ and bstack11l1ll1_opy_ (u"ࠨࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡤ࡫ࡸࡦࡥࡸࡸࡴࡸࠢ፾") in bstack1ll1lll1l1l_opy_[bstack11l1ll1_opy_ (u"ࠢࡴࡥࡵ࡭ࡵࡺࠢ፿")]
    @staticmethod
    def bstack1lll1l111ll_opy_(method_name: str, *args):
        if not bstack1llllllll1l_opy_.bstack1lll111lll1_opy_(method_name):
            return False
        if not bstack1llllllll1l_opy_.bstack1l1l11lll1l_opy_ in bstack1llllllll1l_opy_.bstack1ll111l11l1_opy_(*args):
            return False
        bstack1ll1lll1l1l_opy_ = bstack1llllllll1l_opy_.bstack1ll1ll1lll1_opy_(*args)
        return (
            bstack1ll1lll1l1l_opy_
            and bstack11l1ll1_opy_ (u"ࠣࡵࡦࡶ࡮ࡶࡴࠣᎀ") in bstack1ll1lll1l1l_opy_
            and bstack11l1ll1_opy_ (u"ࠤࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡠࡣࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࡠࡣࡸࡸࡴࡳࡡࡵ࡫ࡲࡲࡤࡹࡣࡳ࡫ࡳࡸࠧᎁ") in bstack1ll1lll1l1l_opy_[bstack11l1ll1_opy_ (u"ࠥࡷࡨࡸࡩࡱࡶࠥᎂ")]
        )
    @staticmethod
    def bstack1ll111l11l1_opy_(*args):
        return str(bstack1llllllll1l_opy_.bstack1lll11l11ll_opy_(*args)).lower()
    @staticmethod
    def bstack1lll11l11ll_opy_(*args):
        return args[0] if args and type(args) in [list, tuple] and isinstance(args[0], str) else None
    @staticmethod
    def bstack1ll1ll1lll1_opy_(*args):
        return args[1] if len(args) > 1 and isinstance(args[1], dict) else None
    @staticmethod
    def bstack1l11111l1_opy_(driver):
        command_executor = getattr(driver, bstack11l1ll1_opy_ (u"ࠦࡨࡵ࡭࡮ࡣࡱࡨࡤ࡫ࡸࡦࡥࡸࡸࡴࡸࠢᎃ"), None)
        if not command_executor:
            return None
        hub_url = str(command_executor) if isinstance(command_executor, (str, bytes)) else None
        hub_url = str(command_executor._url) if not hub_url and getattr(command_executor, bstack11l1ll1_opy_ (u"ࠧࡥࡵࡳ࡮ࠥᎄ"), None) else None
        if not hub_url:
            client_config = getattr(command_executor, bstack11l1ll1_opy_ (u"ࠨ࡟ࡤ࡮࡬ࡩࡳࡺ࡟ࡤࡱࡱࡪ࡮࡭ࠢᎅ"), None)
            if not client_config:
                return None
            hub_url = getattr(client_config, bstack11l1ll1_opy_ (u"ࠢࡳࡧࡰࡳࡹ࡫࡟ࡴࡧࡵࡺࡪࡸ࡟ࡢࡦࡧࡶࠧᎆ"), None)
        return hub_url
    def bstack1ll111l111l_opy_(self, instance, driver, hub_url: str):
        result = False
        if not hub_url:
            return result
        command_executor = getattr(driver, bstack11l1ll1_opy_ (u"ࠣࡥࡲࡱࡲࡧ࡮ࡥࡡࡨࡼࡪࡩࡵࡵࡱࡵࠦᎇ"), None)
        if command_executor:
            if isinstance(command_executor, (str, bytes)):
                setattr(driver, bstack11l1ll1_opy_ (u"ࠤࡦࡳࡲࡳࡡ࡯ࡦࡢࡩࡽ࡫ࡣࡶࡶࡲࡶࠧᎈ"), hub_url)
                result = True
            elif hasattr(command_executor, bstack11l1ll1_opy_ (u"ࠥࡣࡺࡸ࡬ࠣᎉ")):
                setattr(command_executor, bstack11l1ll1_opy_ (u"ࠦࡤࡻࡲ࡭ࠤᎊ"), hub_url)
                result = True
        if result:
            self.bstack1ll11111ll1_opy_ = hub_url
            bstack1llllllll1l_opy_.bstack1111l11l11_opy_(instance, bstack1llllllll1l_opy_.bstack1ll1l11l111_opy_, hub_url)
            bstack1llllllll1l_opy_.bstack1111l11l11_opy_(
                instance, bstack1llllllll1l_opy_.bstack1ll1l111l1l_opy_, bstack1llllllll1l_opy_.bstack1ll1lll1lll_opy_(hub_url)
            )
        return result
    @staticmethod
    def bstack1l1l111lll1_opy_(bstack111l111l1l_opy_: Tuple[bstack1111ll111l_opy_, bstack1111l1l1l1_opy_]):
        return bstack11l1ll1_opy_ (u"ࠧࡀࠢᎋ").join((bstack1111ll111l_opy_(bstack111l111l1l_opy_[0]).name, bstack1111l1l1l1_opy_(bstack111l111l1l_opy_[1]).name))
    @staticmethod
    def bstack1lll11llll1_opy_(bstack111l111l1l_opy_: Tuple[bstack1111ll111l_opy_, bstack1111l1l1l1_opy_], callback: Callable):
        bstack1l1l11ll1ll_opy_ = bstack1llllllll1l_opy_.bstack1l1l111lll1_opy_(bstack111l111l1l_opy_)
        if not bstack1l1l11ll1ll_opy_ in bstack1llllllll1l_opy_.bstack1l1l11l111l_opy_:
            bstack1llllllll1l_opy_.bstack1l1l11l111l_opy_[bstack1l1l11ll1ll_opy_] = []
        bstack1llllllll1l_opy_.bstack1l1l11l111l_opy_[bstack1l1l11ll1ll_opy_].append(callback)
    def bstack1111l1ll1l_opy_(self, instance: bstack1111l11l1l_opy_, method_name: str, bstack111l111ll1_opy_: timedelta, *args, **kwargs):
        if not instance or method_name in (bstack11l1ll1_opy_ (u"ࠨࡳࡵࡣࡵࡸࡤࡹࡥࡴࡵ࡬ࡳࡳࠨᎌ")):
            return
        cmd = args[0] if method_name == bstack11l1ll1_opy_ (u"ࠢࡦࡺࡨࡧࡺࡺࡥࠣᎍ") and args and type(args) in [list, tuple] and isinstance(args[0], str) else None
        bstack1l1l111llll_opy_ = bstack11l1ll1_opy_ (u"ࠣ࠼ࠥᎎ").join(map(str, filter(None, [method_name, cmd])))
        instance.bstack111l11l1_opy_(bstack11l1ll1_opy_ (u"ࠤࡧࡶ࡮ࡼࡥࡳ࠼ࠥᎏ") + bstack1l1l111llll_opy_, bstack111l111ll1_opy_)
    def bstack111l111l11_opy_(
        self,
        target: object,
        exec: Tuple[bstack1111l11l1l_opy_, str],
        bstack111l111l1l_opy_: Tuple[bstack1111ll111l_opy_, bstack1111l1l1l1_opy_],
        result: Any,
        *args,
        **kwargs,
    ) -> Callable[..., Any]:
        instance, method_name = exec
        bstack1111l1llll_opy_, bstack1l1l11ll111_opy_ = bstack111l111l1l_opy_
        bstack1l1l11ll1ll_opy_ = bstack1llllllll1l_opy_.bstack1l1l111lll1_opy_(bstack111l111l1l_opy_)
        self.logger.debug(bstack11l1ll1_opy_ (u"ࠥࡳࡳࡥࡨࡰࡱ࡮࠾ࠥࡳࡥࡵࡪࡲࡨࡤࡴࡡ࡮ࡧࡀࡿࡲ࡫ࡴࡩࡱࡧࡣࡳࡧ࡭ࡦࡿࠣ࡬ࡴࡵ࡫ࡠ࡫ࡱࡪࡴࡃࡻࡩࡱࡲ࡯ࡤ࡯࡮ࡧࡱࢀࠤࡦࡸࡧࡴ࠿ࡾࡥࡷ࡭ࡳࡾࠢ࡮ࡻࡦࡸࡧࡴ࠿ࠥ᎐") + str(kwargs) + bstack11l1ll1_opy_ (u"ࠦࠧ᎑"))
        if bstack1111l1llll_opy_ == bstack1111ll111l_opy_.QUIT:
            if bstack1l1l11ll111_opy_ == bstack1111l1l1l1_opy_.PRE:
                bstack1lll11l1l1l_opy_ = bstack1llll111lll_opy_.bstack1lll11l1111_opy_(EVENTS.bstack1ll1l1111l_opy_.value)
                bstack1111llll1l_opy_.bstack1111l11l11_opy_(instance, EVENTS.bstack1ll1l1111l_opy_.value, bstack1lll11l1l1l_opy_)
                self.logger.debug(bstack11l1ll1_opy_ (u"ࠧ࡯࡮ࡴࡶࡤࡲࡨ࡫࠽ࡼࡿࠣࡱࡪࡺࡨࡰࡦࡢࡲࡦࡳࡥ࠾ࡽࢀࠤ࡫ࡸࡡ࡮ࡧࡺࡳࡷࡱ࡟ࡴࡶࡤࡸࡪࡃࡻࡾࠢ࡫ࡳࡴࡱ࡟ࡴࡶࡤࡸࡪࡃࡻࡾࠤ᎒").format(instance, method_name, bstack1111l1llll_opy_, bstack1l1l11ll111_opy_))
        if bstack1111l1llll_opy_ == bstack1111ll111l_opy_.bstack1111ll1ll1_opy_:
            if bstack1l1l11ll111_opy_ == bstack1111l1l1l1_opy_.POST and not bstack1llllllll1l_opy_.bstack1ll11l1llll_opy_ in instance.data:
                session_id = getattr(target, bstack11l1ll1_opy_ (u"ࠨࡳࡦࡵࡶ࡭ࡴࡴ࡟ࡪࡦࠥ᎓"), None)
                if session_id:
                    instance.data[bstack1llllllll1l_opy_.bstack1ll11l1llll_opy_] = session_id
        elif (
            bstack1111l1llll_opy_ == bstack1111ll111l_opy_.bstack1111l1l11l_opy_
            and bstack1llllllll1l_opy_.bstack1ll111l11l1_opy_(*args) == bstack1llllllll1l_opy_.bstack1ll111l1l11_opy_
        ):
            if bstack1l1l11ll111_opy_ == bstack1111l1l1l1_opy_.PRE:
                hub_url = bstack1llllllll1l_opy_.bstack1l11111l1_opy_(target)
                if hub_url:
                    instance.data.update(
                        {
                            bstack1llllllll1l_opy_.bstack1ll1l11l111_opy_: hub_url,
                            bstack1llllllll1l_opy_.bstack1ll1l111l1l_opy_: bstack1llllllll1l_opy_.bstack1ll1lll1lll_opy_(hub_url),
                            bstack1llllllll1l_opy_.bstack1lll11ll1l1_opy_: int(
                                os.environ.get(bstack11l1ll1_opy_ (u"ࠢࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡐࡍࡃࡗࡊࡔࡘࡍࡠࡋࡑࡈࡊ࡞ࠢ᎔"), str(self.platform_index))
                            ),
                        }
                    )
                bstack1ll1lll1l1l_opy_ = bstack1llllllll1l_opy_.bstack1ll1ll1lll1_opy_(*args)
                bstack1l1l11l11ll_opy_ = bstack1ll1lll1l1l_opy_.get(bstack11l1ll1_opy_ (u"ࠣࡥࡤࡴࡦࡨࡩ࡭࡫ࡷ࡭ࡪࡹࠢ᎕"), None) if bstack1ll1lll1l1l_opy_ else None
                if isinstance(bstack1l1l11l11ll_opy_, dict):
                    instance.data[bstack1llllllll1l_opy_.bstack1l1l11ll11l_opy_] = copy.deepcopy(bstack1l1l11l11ll_opy_)
                    instance.data[bstack1llllllll1l_opy_.bstack1ll1llll111_opy_] = bstack1l1l11l11ll_opy_
            elif bstack1l1l11ll111_opy_ == bstack1111l1l1l1_opy_.POST:
                if isinstance(result, dict):
                    framework_session_id = result.get(bstack11l1ll1_opy_ (u"ࠤࡹࡥࡱࡻࡥࠣ᎖"), dict()).get(bstack11l1ll1_opy_ (u"ࠥࡷࡪࡹࡳࡪࡱࡱࡍࡩࠨ᎗"), None)
                    if framework_session_id:
                        instance.data.update(
                            {
                                bstack1llllllll1l_opy_.bstack1ll11l1llll_opy_: framework_session_id,
                                bstack1llllllll1l_opy_.bstack1l1l11l1lll_opy_: datetime.now(tz=timezone.utc),
                            }
                        )
        elif (
            bstack1111l1llll_opy_ == bstack1111ll111l_opy_.bstack1111l1l11l_opy_
            and bstack1llllllll1l_opy_.bstack1ll111l11l1_opy_(*args) == bstack1llllllll1l_opy_.bstack1l1l11lll11_opy_
            and bstack1l1l11ll111_opy_ == bstack1111l1l1l1_opy_.POST
        ):
            instance.data[bstack1llllllll1l_opy_.bstack1l1l11l11l1_opy_] = datetime.now(tz=timezone.utc)
        if bstack1l1l11ll1ll_opy_ in bstack1llllllll1l_opy_.bstack1l1l11l111l_opy_:
            bstack1l1l11l1ll1_opy_ = None
            for callback in bstack1llllllll1l_opy_.bstack1l1l11l111l_opy_[bstack1l1l11ll1ll_opy_]:
                try:
                    bstack1l1l11l1111_opy_ = callback(self, target, exec, bstack111l111l1l_opy_, result, *args, **kwargs)
                    if bstack1l1l11l1ll1_opy_ == None:
                        bstack1l1l11l1ll1_opy_ = bstack1l1l11l1111_opy_
                except Exception as e:
                    self.logger.error(bstack11l1ll1_opy_ (u"ࠦࡪࡸࡲࡰࡴࠣ࡭ࡳࡼ࡯࡬࡫ࡱ࡫ࠥࡩࡡ࡭࡮ࡥࡥࡨࡱ࠺ࠡࠤ᎘") + str(e) + bstack11l1ll1_opy_ (u"ࠧࠨ᎙"))
                    traceback.print_exc()
            if bstack1111l1llll_opy_ == bstack1111ll111l_opy_.QUIT:
                if bstack1l1l11ll111_opy_ == bstack1111l1l1l1_opy_.POST:
                    bstack1lll11l1l1l_opy_ = bstack1111llll1l_opy_.bstack111l111111_opy_(instance, EVENTS.bstack1ll1l1111l_opy_.value)
                    if bstack1lll11l1l1l_opy_!=None:
                        bstack1llll111lll_opy_.end(EVENTS.bstack1ll1l1111l_opy_.value, bstack1lll11l1l1l_opy_+bstack11l1ll1_opy_ (u"ࠨ࠺ࡴࡶࡤࡶࡹࠨ᎚"), bstack1lll11l1l1l_opy_+bstack11l1ll1_opy_ (u"ࠢ࠻ࡧࡱࡨࠧ᎛"), True, None)
            if bstack1l1l11ll111_opy_ == bstack1111l1l1l1_opy_.PRE and callable(bstack1l1l11l1ll1_opy_):
                return bstack1l1l11l1ll1_opy_
            elif bstack1l1l11ll111_opy_ == bstack1111l1l1l1_opy_.POST and bstack1l1l11l1ll1_opy_:
                return bstack1l1l11l1ll1_opy_
    def bstack1111l1l111_opy_(
        self, method_name, previous_state: bstack1111ll111l_opy_, *args, **kwargs
    ) -> bstack1111ll111l_opy_:
        if method_name == bstack11l1ll1_opy_ (u"ࠣࡡࡢ࡭ࡳ࡯ࡴࡠࡡࠥ᎜") or method_name == bstack11l1ll1_opy_ (u"ࠤࡶࡸࡦࡸࡴࡠࡵࡨࡷࡸ࡯࡯࡯ࠤ᎝"):
            return bstack1111ll111l_opy_.bstack1111ll1ll1_opy_
        if method_name == bstack11l1ll1_opy_ (u"ࠥࡵࡺ࡯ࡴࠣ᎞"):
            return bstack1111ll111l_opy_.QUIT
        if method_name == bstack11l1ll1_opy_ (u"ࠦࡪࡾࡥࡤࡷࡷࡩࠧ᎟"):
            if previous_state != bstack1111ll111l_opy_.NONE:
                bstack1lll11ll11l_opy_ = bstack1llllllll1l_opy_.bstack1ll111l11l1_opy_(*args)
                if bstack1lll11ll11l_opy_ == bstack1llllllll1l_opy_.bstack1ll111l1l11_opy_:
                    return bstack1111ll111l_opy_.bstack1111ll1ll1_opy_
            return bstack1111ll111l_opy_.bstack1111l1l11l_opy_
        return bstack1111ll111l_opy_.NONE