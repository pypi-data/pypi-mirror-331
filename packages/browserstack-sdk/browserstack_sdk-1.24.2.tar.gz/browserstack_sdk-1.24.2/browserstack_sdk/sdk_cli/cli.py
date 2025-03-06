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
import subprocess
import threading
import time
import sys
import grpc
from browserstack_sdk import sdk_pb2_grpc
from browserstack_sdk import sdk_pb2 as structs
from browserstack_sdk.sdk_cli.bstack111l11l111_opy_ import bstack111l111lll_opy_
from browserstack_sdk.sdk_cli.bstack1llll11111l_opy_ import bstack1111111l1l_opy_
from browserstack_sdk.sdk_cli.bstack11111llll1_opy_ import bstack111111l111_opy_
from browserstack_sdk.sdk_cli.bstack1llll111l1l_opy_ import bstack1lll1lll1l1_opy_
from browserstack_sdk.sdk_cli.bstack1lll1ll11l1_opy_ import bstack1lll1lllll1_opy_
from browserstack_sdk.sdk_cli.bstack1llllllll11_opy_ import bstack1lll1ll1lll_opy_
from browserstack_sdk.sdk_cli.bstack1lllll1l1l1_opy_ import bstack1llll111l11_opy_
from browserstack_sdk.sdk_cli.bstack11111l1l1l_opy_ import bstack1llll1l1l11_opy_
from browserstack_sdk.sdk_cli.bstack1l1l11lll1_opy_ import bstack1l1l11lll1_opy_, bstack1ll1ll1l11_opy_, bstack1llll11111_opy_
from browserstack_sdk.sdk_cli.pytest_bdd_framework import PytestBDDFramework
from browserstack_sdk.sdk_cli.bstack1lllll1l111_opy_ import bstack1lllllll1ll_opy_
from browserstack_sdk.sdk_cli.bstack1111111lll_opy_ import bstack1llllllll1l_opy_
from browserstack_sdk.sdk_cli.bstack1111ll1l11_opy_ import bstack1111llll1l_opy_
from browserstack_sdk.sdk_cli.test_framework import TestFramework
from bstack_utils.helper import Notset, bstack1111111111_opy_, get_cli_dir, bstack1lllll1111l_opy_, bstack1l11ll1l1_opy_, bstack1l1111l1l_opy_, bstack1llll1ll11_opy_, bstack11llll111_opy_
from browserstack_sdk.sdk_cli.test_framework import TestFramework, bstack1llll11llll_opy_, bstack11111l1l11_opy_, bstack1lll1llll11_opy_, bstack1llll111ll1_opy_
from browserstack_sdk.sdk_cli.bstack1111ll1l11_opy_ import bstack1111l11l1l_opy_, bstack1111ll111l_opy_, bstack1111l1l1l1_opy_
from bstack_utils.constants import *
from bstack_utils import bstack1ll1ll111_opy_
from typing import Any, List, Union, Dict
import traceback
from google.protobuf.json_format import MessageToDict
from datetime import datetime, timedelta
from collections import defaultdict
from pathlib import Path
from functools import wraps
from bstack_utils.measure import measure
from bstack_utils.messages import bstack1l11l1111l_opy_, bstack1ll11111_opy_
logger = bstack1ll1ll111_opy_.get_logger(__name__, bstack1ll1ll111_opy_.bstack1llll1l1lll_opy_())
def bstack1llll11ll11_opy_(bs_config):
    bstack1lllll1lll1_opy_ = None
    bstack1111l111ll_opy_ = None
    try:
        bstack1111l111ll_opy_ = get_cli_dir()
        bstack1lllll1lll1_opy_ = bstack1lllll1111l_opy_(bstack1111l111ll_opy_)
        bstack1llll1l1111_opy_ = bstack1111111111_opy_(bstack1lllll1lll1_opy_, bstack1111l111ll_opy_, bs_config)
        bstack1lllll1lll1_opy_ = bstack1llll1l1111_opy_ if bstack1llll1l1111_opy_ else bstack1lllll1lll1_opy_
        if not bstack1lllll1lll1_opy_:
            raise ValueError(bstack11l1ll1_opy_ (u"࡙ࠥࡳࡧࡢ࡭ࡧࠣࡸࡴࠦࡦࡪࡰࡧࠤࡘࡊࡋࡠࡅࡏࡍࡤࡈࡉࡏࡡࡓࡅ࡙ࡎࠢ࿟"))
    except Exception as ex:
        logger.debug(bstack11l1ll1_opy_ (u"ࠦࡊࡸࡲࡰࡴࠣࡻ࡭࡯࡬ࡦࠢࡧࡳࡼࡴ࡬ࡰࡣࡧ࡭ࡳ࡭ࠠࡵࡪࡨࠤࡱࡧࡴࡦࡵࡷࠤࡧ࡯࡮ࡢࡴࡼࠤࢀࢃࠢ࿠").format(ex))
        bstack1lllll1lll1_opy_ = os.environ.get(bstack11l1ll1_opy_ (u"࡙ࠧࡄࡌࡡࡆࡐࡎࡥࡂࡊࡐࡢࡔࡆ࡚ࡈࠣ࿡"))
        if bstack1lllll1lll1_opy_:
            logger.debug(bstack11l1ll1_opy_ (u"ࠨࡆࡢ࡮࡯࡭ࡳ࡭ࠠࡣࡣࡦ࡯ࠥࡺ࡯ࠡࡕࡇࡏࡤࡉࡌࡊࡡࡅࡍࡓࡥࡐࡂࡖࡋࠤ࡫ࡸ࡯࡮ࠢࡨࡲࡻ࡯ࡲࡰࡰࡰࡩࡳࡺ࠺ࠡࠤ࿢") + str(bstack1lllll1lll1_opy_) + bstack11l1ll1_opy_ (u"ࠢࠣ࿣"))
        else:
            logger.debug(bstack11l1ll1_opy_ (u"ࠣࡐࡲࠤࡻࡧ࡬ࡪࡦࠣࡗࡉࡑ࡟ࡄࡎࡌࡣࡇࡏࡎࡠࡒࡄࡘࡍࠦࡦࡰࡷࡱࡨࠥ࡯࡮ࠡࡧࡱࡺ࡮ࡸ࡯࡯࡯ࡨࡲࡹࡁࠠࡴࡧࡷࡹࡵࠦ࡭ࡢࡻࠣࡦࡪࠦࡩ࡯ࡥࡲࡱࡵࡲࡥࡵࡧ࠱ࠦ࿤"))
    return bstack1lllll1lll1_opy_, bstack1111l111ll_opy_
bstack1111111ll1_opy_ = bstack11l1ll1_opy_ (u"ࠤ࠼࠽࠾࠿ࠢ࿥")
bstack1llll1ll1l1_opy_ = bstack11l1ll1_opy_ (u"ࠥࡶࡪࡧࡤࡺࠤ࿦")
bstack1lllllllll1_opy_ = bstack11l1ll1_opy_ (u"ࠦࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡇࡑࡏ࡟ࡃࡋࡑࡣࡘࡋࡓࡔࡋࡒࡒࡤࡏࡄࠣ࿧")
bstack111111llll_opy_ = bstack11l1ll1_opy_ (u"ࠧࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡈࡒࡉࡠࡄࡌࡒࡤࡒࡉࡔࡖࡈࡒࡤࡇࡄࡅࡔࠥ࿨")
bstack1111l1111_opy_ = bstack11l1ll1_opy_ (u"ࠨࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡇࡕࡕࡑࡐࡅ࡙ࡏࡏࡏࠤ࿩")
bstack1lll1ll1ll1_opy_ = re.compile(bstack11l1ll1_opy_ (u"ࡲࠣࠪࡂ࡭࠮࠴ࠪࠩࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑࡼࡃࡕࠬ࠲࠯ࠨ࿪"))
bstack1llllll111l_opy_ = bstack11l1ll1_opy_ (u"ࠣࡦࡨࡺࡪࡲ࡯ࡱ࡯ࡨࡲࡹࠨ࿫")
bstack1llllll1l11_opy_ = [
    bstack1ll1ll1l11_opy_.bstack1llllll1l_opy_,
    bstack1ll1ll1l11_opy_.CONNECT,
    bstack1ll1ll1l11_opy_.bstack11lll1l111_opy_,
]
class SDKCLI:
    _11111ll1l1_opy_ = None
    process: Union[None, Any]
    bstack1111l11111_opy_: bool
    bstack1111111l11_opy_: bool
    bstack1llll1ll11l_opy_: bool
    bin_session_id: Union[None, str]
    cli_bin_session_id: Union[None, str]
    cli_listen_addr: Union[None, str]
    bstack11111111ll_opy_: Union[None, grpc.Channel]
    bstack111111l11l_opy_: str
    test_framework: TestFramework
    bstack1111ll1l11_opy_: bstack1111llll1l_opy_
    config: Union[None, Dict[str, Any]]
    web_driver: bstack1lll1ll1lll_opy_
    bstack1llll11l11l_opy_: bstack1llll111l11_opy_
    bstack11111l1lll_opy_: bstack1llll1l1l11_opy_
    accessibility: bstack111111l111_opy_
    ai: bstack1lll1lll1l1_opy_
    bstack1lllll1ll1l_opy_: bstack1lll1lllll1_opy_
    bstack1llll1lll11_opy_: List[bstack1111111l1l_opy_]
    config_testhub: Any
    config_observability: Any
    config_accessibility: Any
    bstack11111ll111_opy_: Any
    bstack11111lll1l_opy_: Dict[str, timedelta]
    bstack11111lllll_opy_: str
    bstack111l11l111_opy_: bstack111l111lll_opy_
    def __new__(cls):
        if not cls._11111ll1l1_opy_:
            cls._11111ll1l1_opy_ = super(SDKCLI, cls).__new__(cls)
        return cls._11111ll1l1_opy_
    def __init__(self):
        self.process = None
        self.bstack1111l11111_opy_ = False
        self.bstack11111111ll_opy_ = None
        self.bstack11111111l1_opy_ = None
        self.cli_bin_session_id = None
        self.cli_listen_addr = os.environ.get(bstack111111llll_opy_, None)
        self.bstack1llll1ll1ll_opy_ = os.environ.get(bstack1lllllllll1_opy_, bstack11l1ll1_opy_ (u"ࠤࠥ࿬")) == bstack11l1ll1_opy_ (u"ࠥࠦ࿭")
        self.bstack1111111l11_opy_ = False
        self.bstack1llll1ll11l_opy_ = False
        self.config = None
        self.config_testhub = None
        self.config_observability = None
        self.config_accessibility = None
        self.bstack11111ll111_opy_ = None
        self.test_framework = None
        self.bstack1111ll1l11_opy_ = None
        self.bstack111111l11l_opy_=bstack11l1ll1_opy_ (u"ࠦࠧ࿮")
        self.logger = bstack1ll1ll111_opy_.get_logger(self.__class__.__name__, bstack1ll1ll111_opy_.bstack1llll1l1lll_opy_())
        self.bstack11111lll1l_opy_ = defaultdict(lambda: timedelta(microseconds=0))
        self.bstack111l11l111_opy_ = bstack111l111lll_opy_()
        self.web_driver = bstack1lll1ll1lll_opy_()
        self.bstack1llll11l11l_opy_ = bstack1llll111l11_opy_()
        self.bstack11111l1lll_opy_ = None
        self.accessibility = None
        self.ai = None
        self.percy = None
        self.bstack1llll1lll11_opy_ = [
            self.web_driver,
            self.bstack1llll11l11l_opy_,
        ]
    def bstack1ll111111_opy_(self):
        return os.environ.get(bstack1111l1111_opy_).lower().__eq__(bstack11l1ll1_opy_ (u"ࠧࡺࡲࡶࡧࠥ࿯"))
    def is_enabled(self, config):
        if bstack11l1ll1_opy_ (u"࠭ࡴࡶࡴࡥࡳࡘࡩࡡ࡭ࡧࠪ࿰") in config and str(config[bstack11l1ll1_opy_ (u"ࠧࡵࡷࡵࡦࡴ࡙ࡣࡢ࡮ࡨࠫ࿱")]).lower() != bstack11l1ll1_opy_ (u"ࠨࡨࡤࡰࡸ࡫ࠧ࿲"):
            return False
        bstack1llllll1l1l_opy_ = [bstack11l1ll1_opy_ (u"ࠤࡳࡽࡹ࡫ࡳࡵࠤ࿳"), bstack11l1ll1_opy_ (u"ࠥࡴࡾࡺࡥࡴࡶ࠰ࡦࡩࡪࠢ࿴")]
        bstack1llll1l11l1_opy_ = config.get(bstack11l1ll1_opy_ (u"ࠦ࡫ࡸࡡ࡮ࡧࡺࡳࡷࡱࠢ࿵")) in bstack1llllll1l1l_opy_ or os.environ.get(bstack11l1ll1_opy_ (u"ࠬࡌࡒࡂࡏࡈ࡛ࡔࡘࡋࡠࡗࡖࡉࡉ࠭࿶")) in bstack1llllll1l1l_opy_
        if(bstack11llll111_opy_()):
            logger.debug(bstack11l1ll1_opy_ (u"ࠨࡄࡪࡵࡤࡦࡱ࡯࡮ࡨࠢࡆࡐࡎࠦࡦࡰࡴࠣࡴࡱࡧࡹࡸࡴ࡬࡫࡭ࡺ࠮ࠣ࿷"))
            bstack1llll1l11l1_opy_ = False
        os.environ[bstack11l1ll1_opy_ (u"ࠢࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡂࡊࡐࡄࡖ࡞ࡥࡉࡔࡡࡕ࡙ࡓࡔࡉࡏࡉࠥ࿸")] = str(bstack1llll1l11l1_opy_) # bstack111111ll1l_opy_ bstack1lll1ll11ll_opy_ VAR to bstack1lllll11ll1_opy_ is binary running
        return bstack1llll1l11l1_opy_
    def bstack1l111111l_opy_(self):
        for event in bstack1llllll1l11_opy_:
            bstack1l1l11lll1_opy_.register(
                event, lambda event_name, *args, **kwargs: bstack1l1l11lll1_opy_.logger.debug(bstack11l1ll1_opy_ (u"ࠣࡽࡨࡺࡪࡴࡴࡠࡰࡤࡱࡪࢃࠠ࠾ࡀࠣࡿࡦࡸࡧࡴࡿࠣࠦ࿹") + str(kwargs) + bstack11l1ll1_opy_ (u"ࠤࠥ࿺"))
            )
        bstack1l1l11lll1_opy_.register(bstack1ll1ll1l11_opy_.bstack1llllll1l_opy_, self.__1lll1lll11l_opy_)
        bstack1l1l11lll1_opy_.register(bstack1ll1ll1l11_opy_.CONNECT, self.__1lllll11lll_opy_)
        bstack1l1l11lll1_opy_.register(bstack1ll1ll1l11_opy_.bstack11lll1l111_opy_, self.__1llll11lll1_opy_)
        bstack1l1l11lll1_opy_.register(bstack1ll1ll1l11_opy_.bstack1ll1ll11ll_opy_, self.__1lllllll11l_opy_)
    def bstack11ll1llll1_opy_(self):
        return not self.bstack1llll1ll1ll_opy_ and os.environ.get(bstack1lllllllll1_opy_, bstack11l1ll1_opy_ (u"ࠥࠦ࿻")) != bstack11l1ll1_opy_ (u"ࠦࠧ࿼")
    def is_running(self):
        if self.bstack1llll1ll1ll_opy_:
            return self.bstack1111l11111_opy_
        else:
            return bool(self.bstack11111111ll_opy_)
    def bstack11111lll11_opy_(self, module):
        return any(isinstance(m, module) for m in self.bstack1llll1lll11_opy_) and cli.is_running()
    def __1lllll11111_opy_(self, bstack1lll1llllll_opy_=10):
        if self.bstack11111111l1_opy_:
            return
        bstack1l1l1ll111_opy_ = datetime.now()
        cli_listen_addr = os.environ.get(bstack111111llll_opy_, self.cli_listen_addr)
        self.logger.debug(bstack11l1ll1_opy_ (u"ࠧࡡࠢ࿽") + str(id(self)) + bstack11l1ll1_opy_ (u"ࠨ࡝ࠡࡥࡲࡲࡳ࡫ࡣࡵ࡫ࡱ࡫ࠧ࿾"))
        channel = grpc.insecure_channel(cli_listen_addr, options=[(bstack11l1ll1_opy_ (u"ࠢࡨࡴࡳࡧ࠳࡫࡮ࡢࡤ࡯ࡩࡤ࡮ࡴࡵࡲࡢࡴࡷࡵࡸࡺࠤ࿿"), 0), (bstack11l1ll1_opy_ (u"ࠣࡩࡵࡴࡨ࠴ࡥ࡯ࡣࡥࡰࡪࡥࡨࡵࡶࡳࡷࡤࡶࡲࡰࡺࡼࠦက"), 0)])
        grpc.channel_ready_future(channel).result(timeout=bstack1lll1llllll_opy_)
        self.bstack11111111ll_opy_ = channel
        self.bstack11111111l1_opy_ = sdk_pb2_grpc.SDKStub(self.bstack11111111ll_opy_)
        self.bstack111l11l1_opy_(bstack11l1ll1_opy_ (u"ࠤࡪࡶࡵࡩ࠺ࡤࡱࡱࡲࡪࡩࡴࠣခ"), datetime.now() - bstack1l1l1ll111_opy_)
        self.cli_listen_addr = cli_listen_addr
        os.environ[bstack111111llll_opy_] = self.cli_listen_addr
        self.logger.debug(bstack11l1ll1_opy_ (u"ࠥ࡟ࢀ࡯ࡤࠩࡵࡨࡰ࡫࠯ࡽ࡞ࠢࡦࡳࡳࡴࡥࡤࡶࡨࡨ࠿ࠦࡩࡴࡡࡦ࡬࡮ࡲࡤࡠࡲࡵࡳࡨ࡫ࡳࡴ࠿ࠥဂ") + str(self.bstack11ll1llll1_opy_()) + bstack11l1ll1_opy_ (u"ࠦࠧဃ"))
    def __1llll11lll1_opy_(self, event_name):
        if self.bstack11ll1llll1_opy_():
            self.logger.debug(bstack11l1ll1_opy_ (u"ࠧࡩࡨࡪ࡮ࡧ࠱ࡵࡸ࡯ࡤࡧࡶࡷ࠿ࠦࡳࡵࡱࡳࡴ࡮ࡴࡧࠡࡅࡏࡍࠧင"))
        self.__111111111l_opy_()
    def __1lllllll11l_opy_(self, event_name, bstack1llll11ll1l_opy_ = None, bstack1l11lll1ll_opy_=1):
        if bstack1l11lll1ll_opy_ == 1:
            self.logger.error(bstack11l1ll1_opy_ (u"ࠨࡓࡰ࡯ࡨࡸ࡭࡯࡮ࡨࠢࡺࡩࡳࡺࠠࡸࡴࡲࡲ࡬ࠨစ"))
        bstack11111l11ll_opy_ = Path(bstack11111l1ll1_opy_ (u"ࠢࡼࡵࡨࡰ࡫࠴ࡣ࡭࡫ࡢࡨ࡮ࡸࡽ࠰ࡷࡱ࡬ࡦࡴࡤ࡭ࡧࡧࡉࡷࡸ࡯ࡳࡵ࠱࡮ࡸࡵ࡮ࠣဆ"))
        if self.bstack1111l111ll_opy_ and bstack11111l11ll_opy_.exists():
            with open(bstack11111l11ll_opy_, bstack11l1ll1_opy_ (u"ࠨࡴࠪဇ"), encoding=bstack11l1ll1_opy_ (u"ࠩࡸࡸ࡫࠳࠸ࠨဈ")) as fp:
                data = json.load(fp)
                try:
                    bstack1l1111l1l_opy_(bstack11l1ll1_opy_ (u"ࠪࡔࡔ࡙ࡔࠨဉ"), bstack1llll1ll11_opy_(bstack1lll1ll1l_opy_), data, {
                        bstack11l1ll1_opy_ (u"ࠫࡦࡻࡴࡩࠩည"): (self.config[bstack11l1ll1_opy_ (u"ࠬࡻࡳࡦࡴࡑࡥࡲ࡫ࠧဋ")], self.config[bstack11l1ll1_opy_ (u"࠭ࡡࡤࡥࡨࡷࡸࡑࡥࡺࠩဌ")])
                    })
                except Exception as e:
                    logger.debug(bstack1ll11111_opy_.format(str(e)))
            bstack11111l11ll_opy_.unlink()
        sys.exit(bstack1l11lll1ll_opy_)
    @measure(event_name=EVENTS.bstack111111l1ll_opy_, stage=STAGE.bstack1l1ll1llll_opy_)
    def __1lll1lll11l_opy_(self, event_name: str, data):
        from bstack_utils.bstack1ll111ll1l_opy_ import bstack1llll111lll_opy_
        self.bstack111111l11l_opy_, self.bstack1111l111ll_opy_ = bstack1llll11ll11_opy_(data.bs_config)
        os.environ[bstack11l1ll1_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡗࡓࡋࡗࡅࡇࡒࡅࡠࡆࡌࡖࠬဍ")] = self.bstack1111l111ll_opy_
        if not self.bstack111111l11l_opy_ or not self.bstack1111l111ll_opy_:
            raise ValueError(bstack11l1ll1_opy_ (u"ࠣࡗࡱࡥࡧࡲࡥࠡࡶࡲࠤ࡫࡯࡮ࡥࠢࡷ࡬ࡪࠦࡓࡅࡍࠣࡇࡑࡏࠠࡣ࡫ࡱࡥࡷࡿࠢဎ"))
        if self.bstack11ll1llll1_opy_():
            self.__1lllll11lll_opy_(event_name, bstack1llll11111_opy_())
            return
        try:
            bstack1llll111lll_opy_.end(EVENTS.bstack1l111l11l_opy_.value, EVENTS.bstack1l111l11l_opy_.value + bstack11l1ll1_opy_ (u"ࠤ࠽ࡷࡹࡧࡲࡵࠤဏ"), EVENTS.bstack1l111l11l_opy_.value + bstack11l1ll1_opy_ (u"ࠥ࠾ࡪࡴࡤࠣတ"), status=True, failure=None, test_name=None)
            logger.debug(bstack11l1ll1_opy_ (u"ࠦࡈࡵ࡭ࡱ࡮ࡨࡸࡪࠦࡓࡅࡍࠣࡗࡪࡺࡵࡱ࠰ࠥထ"))
        except Exception as e:
            logger.debug(bstack11l1ll1_opy_ (u"ࠧࡋࡸࡤࡧࡳࡸ࡮ࡵ࡮ࠡࡹ࡫࡭ࡱ࡫ࠠ࡮ࡣࡵ࡯࡮ࡴࡧࠡ࡭ࡨࡽࠥࡳࡥࡵࡴ࡬ࡧࡸࠦࡻࡾࠤဒ").format(e))
        start = datetime.now()
        is_started = self.__11111l111l_opy_()
        self.bstack111l11l1_opy_(bstack11l1ll1_opy_ (u"ࠨࡳࡱࡣࡺࡲࡤࡺࡩ࡮ࡧࠥဓ"), datetime.now() - start)
        if is_started:
            start = datetime.now()
            self.__1lllll11111_opy_()
            self.bstack111l11l1_opy_(bstack11l1ll1_opy_ (u"ࠢࡤࡱࡱࡲࡪࡩࡴࡠࡶ࡬ࡱࡪࠨန"), datetime.now() - start)
            start = datetime.now()
            self.__1lllll1l11l_opy_(data)
            self.bstack111l11l1_opy_(bstack11l1ll1_opy_ (u"ࠣࡵࡷࡥࡷࡺ࡟ࡴࡧࡶࡷ࡮ࡵ࡮ࡠࡶ࡬ࡱࡪࠨပ"), datetime.now() - start)
    @measure(event_name=EVENTS.bstack1llllll1ll1_opy_, stage=STAGE.bstack1l1ll1llll_opy_)
    def __1lllll11lll_opy_(self, event_name: str, data: bstack1llll11111_opy_):
        if not self.bstack11ll1llll1_opy_():
            self.logger.debug(bstack11l1ll1_opy_ (u"ࠤࡩࡥ࡮ࡲࡥࡥࠢࡷࡳࠥࡩ࡯࡯ࡰࡨࡧࡹࡀࠠ࡯ࡱࡷࠤࡦࠦࡣࡩ࡫࡯ࡨ࠲ࡶࡲࡰࡥࡨࡷࡸࠨဖ"))
            return
        bin_session_id = os.environ.get(bstack1lllllllll1_opy_)
        start = datetime.now()
        self.__1lllll11111_opy_()
        self.bstack111l11l1_opy_(bstack11l1ll1_opy_ (u"ࠥࡧࡴࡴ࡮ࡦࡥࡷࡣࡹ࡯࡭ࡦࠤဗ"), datetime.now() - start)
        self.cli_bin_session_id = bin_session_id
        self.logger.debug(bstack11l1ll1_opy_ (u"ࠦࡠࢁࡩࡥࠪࡶࡩࡱ࡬ࠩࡾ࡟ࠣࡧ࡭࡯࡬ࡥ࠯ࡳࡶࡴࡩࡥࡴࡵ࠽ࠤࡨࡵ࡮࡯ࡧࡦࡸࡪࡪࠠࡵࡱࠣࡩࡽ࡯ࡳࡵ࡫ࡱ࡫ࠥࡉࡌࡊࠢࠥဘ") + str(bin_session_id) + bstack11l1ll1_opy_ (u"ࠧࠨမ"))
        start = datetime.now()
        self.__1llll11l111_opy_()
        self.bstack111l11l1_opy_(bstack11l1ll1_opy_ (u"ࠨࡳࡵࡣࡵࡸࡤࡹࡥࡴࡵ࡬ࡳࡳࡥࡴࡪ࡯ࡨࠦယ"), datetime.now() - start)
    def __1lll1lll111_opy_(self):
        if not self.bstack11111111l1_opy_ or not self.cli_bin_session_id:
            self.logger.debug(bstack11l1ll1_opy_ (u"ࠢࡤࡣࡱࡲࡴࡺࠠࡤࡱࡱࡪ࡮࡭ࡵࡳࡧࠣࡱࡴࡪࡵ࡭ࡧࡶࠦရ"))
            return
        if not self.bstack11111l1lll_opy_ and self.config_observability and self.config_observability.success: # bstack1llll1llll1_opy_
            self.bstack11111l1lll_opy_ = bstack1llll1l1l11_opy_() # bstack111111l1l1_opy_
            self.bstack1llll1lll11_opy_.append(self.bstack11111l1lll_opy_)
        if not self.accessibility and self.config_accessibility and self.config_accessibility.success:
            self.accessibility = bstack111111l111_opy_()
            self.bstack1llll1lll11_opy_.append(self.accessibility)
        if not self.ai and isinstance(self.config, dict) and self.config.get(bstack11l1ll1_opy_ (u"ࠣࡵࡨࡰ࡫ࡎࡥࡢ࡮ࠥလ"), False) == True:
            self.ai = bstack1lll1lll1l1_opy_()
            self.bstack1llll1lll11_opy_.append(self.ai)
        if not self.percy and self.bstack11111ll111_opy_ and self.bstack11111ll111_opy_.success:
            self.percy = bstack1lll1lllll1_opy_(self.bstack11111ll111_opy_)
            self.bstack1llll1lll11_opy_.append(self.percy)
        for mod in self.bstack1llll1lll11_opy_:
            if not mod.bstack1lll1ll111l_opy_():
                mod.configure(self.bstack11111111l1_opy_, self.config, self.cli_bin_session_id, self.bstack111l11l111_opy_)
    def __1llllll11l1_opy_(self):
        for mod in self.bstack1llll1lll11_opy_:
            if mod.bstack1lll1ll111l_opy_():
                mod.configure(self.bstack11111111l1_opy_, None, None, None)
    @measure(event_name=EVENTS.bstack1llll1111l1_opy_, stage=STAGE.bstack1l1ll1llll_opy_)
    def __1lllll1l11l_opy_(self, data):
        if not self.cli_bin_session_id or self.bstack1111111l11_opy_:
            return
        self.__1llllll1lll_opy_(data)
        bstack1l1l1ll111_opy_ = datetime.now()
        req = structs.StartBinSessionRequest()
        req.bin_session_id = self.cli_bin_session_id
        req.path_project = os.getcwd()
        req.language = bstack11l1ll1_opy_ (u"ࠤࡳࡽࡹ࡮࡯࡯ࠤဝ")
        req.sdk_language = bstack11l1ll1_opy_ (u"ࠥࡴࡾࡺࡨࡰࡰࠥသ")
        req.path_config = data.path_config
        req.sdk_version = data.sdk_version
        req.test_framework = data.test_framework
        req.frameworks.extend(data.frameworks)
        req.framework_versions.update(data.framework_versions)
        req.env_vars.update({key: value for key, value in os.environ.items() if bool(bstack1lll1ll1ll1_opy_.search(key))})
        req.cli_args.extend(sys.argv)
        try:
            self.logger.debug(bstack11l1ll1_opy_ (u"ࠦࡠࠨဟ") + str(id(self)) + bstack11l1ll1_opy_ (u"ࠧࡣࠠ࡮ࡣ࡬ࡲ࠲ࡶࡲࡰࡥࡨࡷࡸࡀࠠࡴࡶࡤࡶࡹࡥࡢࡪࡰࡢࡷࡪࡹࡳࡪࡱࡱࠦဠ"))
            r = self.bstack11111111l1_opy_.StartBinSession(req)
            self.bstack111l11l1_opy_(bstack11l1ll1_opy_ (u"ࠨࡧࡳࡲࡦ࠾ࡸࡺࡡࡳࡶࡢࡦ࡮ࡴ࡟ࡴࡧࡶࡷ࡮ࡵ࡮ࠣအ"), datetime.now() - bstack1l1l1ll111_opy_)
            os.environ[bstack1lllllllll1_opy_] = r.bin_session_id
            self.__111111ll11_opy_(r)
            self.__1lll1lll111_opy_()
            self.bstack111l11l111_opy_.start()
            self.bstack1111111l11_opy_ = True
            self.logger.debug(bstack11l1ll1_opy_ (u"ࠢ࡜ࠤဢ") + str(id(self)) + bstack11l1ll1_opy_ (u"ࠣ࡟ࠣࡱࡦ࡯࡮࠮ࡲࡵࡳࡨ࡫ࡳࡴ࠼ࠣࡧࡴࡴ࡮ࡦࡥࡷࡩࡩࠨဣ"))
        except grpc.bstack1lllllll111_opy_ as bstack1llllllllll_opy_:
            self.logger.error(bstack11l1ll1_opy_ (u"ࠤ࡞ࡿ࡮ࡪࠨࡴࡧ࡯ࡪ࠮ࢃ࡝ࠡࡶ࡬ࡱࡪࡵࡥࡶࡶ࠰ࡩࡷࡸ࡯ࡳ࠼ࠣࠦဤ") + str(bstack1llllllllll_opy_) + bstack11l1ll1_opy_ (u"ࠥࠦဥ"))
            traceback.print_exc()
            raise bstack1llllllllll_opy_
        except grpc.RpcError as e:
            self.logger.error(bstack11l1ll1_opy_ (u"ࠦࡠࢁࡩࡥࠪࡶࡩࡱ࡬ࠩࡾ࡟ࠣࡶࡵࡩ࠭ࡦࡴࡵࡳࡷࡀࠠࠣဦ") + str(e) + bstack11l1ll1_opy_ (u"ࠧࠨဧ"))
            traceback.print_exc()
            raise e
    @measure(event_name=EVENTS.bstack1llll111111_opy_, stage=STAGE.bstack1l1ll1llll_opy_)
    def __1llll11l111_opy_(self):
        if not self.bstack11ll1llll1_opy_() or not self.cli_bin_session_id or self.bstack1llll1ll11l_opy_:
            return
        bstack1l1l1ll111_opy_ = datetime.now()
        req = structs.ConnectBinSessionRequest()
        req.bin_session_id = self.cli_bin_session_id
        req.platform_index = int(os.environ.get(bstack11l1ll1_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡖࡌࡂࡖࡉࡓࡗࡓ࡟ࡊࡐࡇࡉ࡝࠭ဨ"), bstack11l1ll1_opy_ (u"ࠧ࠱ࠩဩ")))
        try:
            self.logger.debug(bstack11l1ll1_opy_ (u"ࠣ࡝ࠥဪ") + str(id(self)) + bstack11l1ll1_opy_ (u"ࠤࡠࠤࡨ࡮ࡩ࡭ࡦ࠰ࡴࡷࡵࡣࡦࡵࡶ࠾ࠥࡩ࡯࡯ࡰࡨࡧࡹࡥࡢࡪࡰࡢࡷࡪࡹࡳࡪࡱࡱࠦါ"))
            r = self.bstack11111111l1_opy_.ConnectBinSession(req)
            self.bstack111l11l1_opy_(bstack11l1ll1_opy_ (u"ࠥ࡫ࡷࡶࡣ࠻ࡥࡲࡲࡳ࡫ࡣࡵࡡࡥ࡭ࡳࡥࡳࡦࡵࡶ࡭ࡴࡴࠢာ"), datetime.now() - bstack1l1l1ll111_opy_)
            self.__111111ll11_opy_(r)
            self.__1lll1lll111_opy_()
            self.bstack111l11l111_opy_.start()
            self.bstack1llll1ll11l_opy_ = True
            self.logger.debug(bstack11l1ll1_opy_ (u"ࠦࡠࠨိ") + str(id(self)) + bstack11l1ll1_opy_ (u"ࠧࡣࠠࡤࡪ࡬ࡰࡩ࠳ࡰࡳࡱࡦࡩࡸࡹ࠺ࠡࡥࡲࡲࡳ࡫ࡣࡵࡧࡧࠦီ"))
        except grpc.bstack1lllllll111_opy_ as bstack1llllllllll_opy_:
            self.logger.error(bstack11l1ll1_opy_ (u"ࠨ࡛ࡼ࡫ࡧࠬࡸ࡫࡬ࡧࠫࢀࡡࠥࡺࡩ࡮ࡧࡲࡩࡺࡺ࠭ࡦࡴࡵࡳࡷࡀࠠࠣု") + str(bstack1llllllllll_opy_) + bstack11l1ll1_opy_ (u"ࠢࠣူ"))
            traceback.print_exc()
            raise bstack1llllllllll_opy_
        except grpc.RpcError as e:
            self.logger.error(bstack11l1ll1_opy_ (u"ࠣ࡝ࡾ࡭ࡩ࠮ࡳࡦ࡮ࡩ࠭ࢂࡣࠠࡳࡲࡦ࠱ࡪࡸࡲࡰࡴ࠽ࠤࠧေ") + str(e) + bstack11l1ll1_opy_ (u"ࠤࠥဲ"))
            traceback.print_exc()
            raise e
    def __111111ll11_opy_(self, r):
        self.bstack1llll1l111l_opy_(r)
        if not r.bin_session_id or not r.config or not isinstance(r.config, str):
            raise ValueError(bstack11l1ll1_opy_ (u"ࠥࡹࡳ࡫ࡸࡱࡧࡦࡸࡪࡪࠠࡴࡧࡵࡺࡪࡸࠠࡳࡧࡶࡴࡴࡴࡳࡦࠤဳ") + str(r))
        self.config = json.loads(r.config)
        if not self.config:
            raise ValueError(bstack11l1ll1_opy_ (u"ࠦࡪࡳࡰࡵࡻࠣࡧࡴࡴࡦࡪࡩࠣࡪࡴࡻ࡮ࡥࠤဴ"))
        self.config_testhub = r.testhub
        self.config_observability = r.observability
        self.config_accessibility = r.accessibility
        bstack11l1ll1_opy_ (u"ࠧࠨࠢࠋࠢࠣࠤࠥࠦࠠࠡࠢࡓࡩࡷࡩࡹࠡ࡫ࡶࠤࡸ࡫࡮ࡵࠢࡲࡲࡱࡿࠠࡢࡵࠣࡴࡦࡸࡴࠡࡱࡩࠤࡹ࡮ࡥࠡࠤࡆࡳࡳࡴࡥࡤࡶࡅ࡭ࡳ࡙ࡥࡴࡵ࡬ࡳࡳ࠲ࠢࠡࡣࡱࡨࠥࡺࡨࡪࡵࠣࡪࡺࡴࡣࡵ࡫ࡲࡲࠥ࡯ࡳࠡࡣ࡯ࡷࡴࠦࡵࡴࡧࡧࠤࡧࡿࠠࡔࡶࡤࡶࡹࡈࡩ࡯ࡕࡨࡷࡸ࡯࡯࡯࠰ࠍࠤࠥࠦࠠࠡࠢࠣࠤ࡙࡮ࡥࡳࡧࡩࡳࡷ࡫ࠬࠡࡐࡲࡲࡪࠦࡨࡢࡰࡧࡰ࡮ࡴࡧࠡ࡫ࡶࠤ࡮ࡳࡰ࡭ࡧࡰࡩࡳࡺࡥࡥ࠰ࠍࠤࠥࠦࠠࠡࠢࠣࠤࠧࠨࠢဵ")
        self.bstack11111ll111_opy_ = getattr(r, bstack11l1ll1_opy_ (u"࠭ࡰࡦࡴࡦࡽࠬံ"), None)
        self.cli_bin_session_id = r.bin_session_id
        os.environ[bstack11l1ll1_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡔࡆࡕࡗࡌ࡚ࡈ࡟ࡋ࡙ࡗ့ࠫ")] = self.config_testhub.jwt
        os.environ[bstack11l1ll1_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡕࡇࡖࡘࡍ࡛ࡂࡠࡗࡘࡍࡉ࠭း")] = self.config_testhub.build_hashed_id
    def bstack1lllll11l1l_opy_(event_name: EVENTS, stage: STAGE):
        def decorator(func):
            @wraps(func)
            def wrapper(self, *args, **kwargs):
                if self.bstack1111l11111_opy_:
                    return func(self, *args, **kwargs)
                @measure(event_name=event_name, stage=stage)
                def bstack1llll1lll1l_opy_(*a, **kw):
                    return func(self, *a, **kw)
                return bstack1llll1lll1l_opy_(*args, **kwargs)
            return wrapper
        return decorator
    @bstack1lllll11l1l_opy_(event_name=EVENTS.bstack1lllll111l1_opy_, stage=STAGE.bstack1l1ll1llll_opy_)
    def __11111l111l_opy_(self, bstack1lll1llllll_opy_=10):
        if self.bstack1111l11111_opy_:
            self.logger.debug(bstack11l1ll1_opy_ (u"ࠤࡶࡸࡦࡸࡴ࠻ࠢࡤࡰࡷ࡫ࡡࡥࡻࠣࡶࡺࡴ࡮ࡪࡰࡪ္ࠦ"))
            return True
        self.logger.debug(bstack11l1ll1_opy_ (u"ࠥࡷࡹࡧࡲࡵࠤ်"))
        if os.getenv(bstack11l1ll1_opy_ (u"ࠦࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡇࡑࡏ࡟ࡆࡐ࡙ࠦျ")) == bstack1llllll111l_opy_:
            self.cli_bin_session_id = bstack1llllll111l_opy_
            self.cli_listen_addr = bstack11l1ll1_opy_ (u"ࠧࡻ࡮ࡪࡺ࠽࠳ࡹࡳࡰ࠰ࡵࡧ࡯࠲ࡶ࡬ࡢࡶࡩࡳࡷࡳ࠭ࠦࡵ࠱ࡷࡴࡩ࡫ࠣြ") % (self.cli_bin_session_id)
            self.bstack1111l11111_opy_ = True
            return True
        self.process = subprocess.Popen(
            [self.bstack111111l11l_opy_, bstack11l1ll1_opy_ (u"ࠨࡳࡥ࡭ࠥွ")],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=dict(os.environ),
            text=True,
            universal_newlines=True, # bstack11111ll1ll_opy_ compat for text=True in bstack1llll11l1ll_opy_ python
            encoding=bstack11l1ll1_opy_ (u"ࠢࡶࡶࡩ࠱࠽ࠨှ"),
            bufsize=1,
            close_fds=True,
        )
        bstack1lll1lll1ll_opy_ = threading.Thread(target=self.__1llll1l1l1l_opy_, args=(bstack1lll1llllll_opy_,))
        bstack1lll1lll1ll_opy_.start()
        bstack1lll1lll1ll_opy_.join()
        if self.process.returncode is not None:
            self.logger.debug(bstack11l1ll1_opy_ (u"ࠣ࡝ࡾ࡭ࡩ࠮ࡳࡦ࡮ࡩ࠭ࢂࡣࠠࡴࡲࡤࡻࡳࡀࠠࡳࡧࡷࡹࡷࡴࡣࡰࡦࡨࡁࢀࡹࡥ࡭ࡨ࠱ࡴࡷࡵࡣࡦࡵࡶ࠲ࡷ࡫ࡴࡶࡴࡱࡧࡴࡪࡥࡾࠢࡲࡹࡹࡃࡻࡴࡧ࡯ࡪ࠳ࡶࡲࡰࡥࡨࡷࡸ࠴ࡳࡵࡦࡲࡹࡹ࠴ࡲࡦࡣࡧࠬ࠮ࢃࠠࡦࡴࡵࡁࠧဿ") + str(self.process.stderr.read()) + bstack11l1ll1_opy_ (u"ࠤࠥ၀"))
        if not self.bstack1111l11111_opy_:
            self.logger.debug(bstack11l1ll1_opy_ (u"ࠥ࡟ࠧ၁") + str(id(self)) + bstack11l1ll1_opy_ (u"ࠦࡢࠦࡣ࡭ࡧࡤࡲࡺࡶࠢ၂"))
            self.__111111111l_opy_()
        self.logger.debug(bstack11l1ll1_opy_ (u"ࠧࡡࡻࡪࡦࠫࡷࡪࡲࡦࠪࡿࡠࠤࡵࡸ࡯ࡤࡧࡶࡷࡤࡸࡥࡢࡦࡼ࠾ࠥࠨ၃") + str(self.bstack1111l11111_opy_) + bstack11l1ll1_opy_ (u"ࠨࠢ၄"))
        return self.bstack1111l11111_opy_
    def __1llll1l1l1l_opy_(self, bstack1llll1111ll_opy_=10):
        bstack1llll1ll111_opy_ = time.time()
        while self.process and time.time() - bstack1llll1ll111_opy_ < bstack1llll1111ll_opy_:
            try:
                line = self.process.stdout.readline()
                if bstack11l1ll1_opy_ (u"ࠢࡪࡦࡀࠦ၅") in line:
                    self.cli_bin_session_id = line.split(bstack11l1ll1_opy_ (u"ࠣ࡫ࡧࡁࠧ၆"))[-1:][0].strip()
                    self.logger.debug(bstack11l1ll1_opy_ (u"ࠤࡦࡰ࡮ࡥࡢࡪࡰࡢࡷࡪࡹࡳࡪࡱࡱࡣ࡮ࡪ࠺ࠣ၇") + str(self.cli_bin_session_id) + bstack11l1ll1_opy_ (u"ࠥࠦ၈"))
                    continue
                if bstack11l1ll1_opy_ (u"ࠦࡱ࡯ࡳࡵࡧࡱࡁࠧ၉") in line:
                    self.cli_listen_addr = line.split(bstack11l1ll1_opy_ (u"ࠧࡲࡩࡴࡶࡨࡲࡂࠨ၊"))[-1:][0].strip()
                    self.logger.debug(bstack11l1ll1_opy_ (u"ࠨࡣ࡭࡫ࡢࡰ࡮ࡹࡴࡦࡰࡢࡥࡩࡪࡲ࠻ࠤ။") + str(self.cli_listen_addr) + bstack11l1ll1_opy_ (u"ࠢࠣ၌"))
                    continue
                if bstack11l1ll1_opy_ (u"ࠣࡲࡲࡶࡹࡃࠢ၍") in line:
                    port = line.split(bstack11l1ll1_opy_ (u"ࠤࡳࡳࡷࡺ࠽ࠣ၎"))[-1:][0].strip()
                    self.logger.debug(bstack11l1ll1_opy_ (u"ࠥࡴࡴࡸࡴ࠻ࠤ၏") + str(port) + bstack11l1ll1_opy_ (u"ࠦࠧၐ"))
                    continue
                if line.strip() == bstack1llll1ll1l1_opy_ and self.cli_bin_session_id and self.cli_listen_addr:
                    if os.getenv(bstack11l1ll1_opy_ (u"࡙ࠧࡄࡌࡡࡆࡐࡎࡥࡆࡍࡃࡊࡣࡎࡕ࡟ࡔࡖࡕࡉࡆࡓࠢၑ"), bstack11l1ll1_opy_ (u"ࠨ࠱ࠣၒ")) == bstack11l1ll1_opy_ (u"ࠢ࠲ࠤၓ"):
                        if not self.process.stdout.closed:
                            self.process.stdout.close()
                        if not self.process.stderr.closed:
                            self.process.stderr.close()
                    self.bstack1111l11111_opy_ = True
                    return True
            except Exception as e:
                self.logger.debug(bstack11l1ll1_opy_ (u"ࠣࡧࡵࡶࡴࡸ࠺ࠡࠤၔ") + str(e) + bstack11l1ll1_opy_ (u"ࠤࠥၕ"))
        return False
    @measure(event_name=EVENTS.bstack1lll1llll1l_opy_, stage=STAGE.bstack1l1ll1llll_opy_)
    def __111111111l_opy_(self):
        if self.bstack11111111ll_opy_:
            self.bstack111l11l111_opy_.stop()
            start = datetime.now()
            if self.bstack11111l1111_opy_():
                self.cli_bin_session_id = None
                if self.bstack1llll1ll11l_opy_:
                    self.bstack111l11l1_opy_(bstack11l1ll1_opy_ (u"ࠥࡷࡹࡵࡰࡠࡵࡨࡷࡸ࡯࡯࡯ࡡࡷ࡭ࡲ࡫ࠢၖ"), datetime.now() - start)
                else:
                    self.bstack111l11l1_opy_(bstack11l1ll1_opy_ (u"ࠦࡸࡺ࡯ࡱࡡࡶࡩࡸࡹࡩࡰࡰࡢࡸ࡮ࡳࡥࠣၗ"), datetime.now() - start)
            self.__1llllll11l1_opy_()
            start = datetime.now()
            self.bstack11111111ll_opy_.close()
            self.bstack111l11l1_opy_(bstack11l1ll1_opy_ (u"ࠧࡪࡩࡴࡥࡲࡲࡳ࡫ࡣࡵࡡࡷ࡭ࡲ࡫ࠢၘ"), datetime.now() - start)
            self.bstack11111111ll_opy_ = None
        if self.process:
            self.logger.debug(bstack11l1ll1_opy_ (u"ࠨࡳࡵࡱࡳࠦၙ"))
            start = datetime.now()
            self.process.terminate()
            self.bstack111l11l1_opy_(bstack11l1ll1_opy_ (u"ࠢ࡬࡫࡯ࡰࡤࡺࡩ࡮ࡧࠥၚ"), datetime.now() - start)
            self.process = None
            if self.bstack1llll1ll1ll_opy_ and self.config_observability and self.config_testhub and self.config_testhub.testhub_events:
                self.bstack1l1l11111l_opy_()
                self.logger.info(
                    bstack11l1ll1_opy_ (u"ࠣࡘ࡬ࡷ࡮ࡺࠠࡩࡶࡷࡴࡸࡀ࠯࠰ࡱࡥࡷࡪࡸࡶࡢࡤ࡬ࡰ࡮ࡺࡹ࠯ࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡤࡱࡰ࠳ࡧࡻࡩ࡭ࡦࡶ࠳ࢀࢃࠠࡵࡱࠣࡺ࡮࡫ࡷࠡࡤࡸ࡭ࡱࡪࠠࡳࡧࡳࡳࡷࡺࠬࠡ࡫ࡱࡷ࡮࡭ࡨࡵࡵ࠯ࠤࡦࡴࡤࠡ࡯ࡤࡲࡾࠦ࡭ࡰࡴࡨࠤࡩ࡫ࡢࡶࡩࡪ࡭ࡳ࡭ࠠࡪࡰࡩࡳࡷࡳࡡࡵ࡫ࡲࡲࠥࡧ࡬࡭ࠢࡤࡸࠥࡵ࡮ࡦࠢࡳࡰࡦࡩࡥࠢ࡞ࡱࠦၛ").format(
                        self.config_testhub.build_hashed_id
                    )
                )
                os.environ[bstack11l1ll1_opy_ (u"ࠩࡅࡗࡤ࡚ࡅࡔࡖࡒࡔࡘࡥࡂࡖࡋࡏࡈࡤࡎࡁࡔࡊࡈࡈࡤࡏࡄࠨၜ")] = self.config_testhub.build_hashed_id
        self.bstack1111l11111_opy_ = False
    def __1llllll1lll_opy_(self, data):
        try:
            import selenium
            data.framework_versions[bstack11l1ll1_opy_ (u"ࠥࡷࡪࡲࡥ࡯࡫ࡸࡱࠧၝ")] = selenium.__version__
            data.frameworks.append(bstack11l1ll1_opy_ (u"ࠦࡸ࡫࡬ࡦࡰ࡬ࡹࡲࠨၞ"))
        except:
            pass
    def bstack1llllll1111_opy_(self, hub_url: str, platform_index: int, bstack11l1ll1l1_opy_: Any):
        if self.bstack1111ll1l11_opy_:
            self.logger.debug(bstack11l1ll1_opy_ (u"ࠧࡹ࡫ࡪࡲࡳࡩࡩࠦࡳࡦࡶࡸࡴࠥࡹࡥ࡭ࡧࡱ࡭ࡺࡳ࠺ࠡࡣ࡯ࡶࡪࡧࡤࡺࠢࡶࡩࡹࠦࡵࡱࠤၟ"))
            return
        try:
            bstack1l1l1ll111_opy_ = datetime.now()
            import selenium
            from selenium.webdriver.remote.webdriver import WebDriver
            from selenium.webdriver.common.service import Service
            framework = bstack11l1ll1_opy_ (u"ࠨࡳࡦ࡮ࡨࡲ࡮ࡻ࡭ࠣၠ")
            self.bstack1111ll1l11_opy_ = bstack1llllllll1l_opy_(
                hub_url,
                platform_index,
                framework_name=framework,
                framework_version=selenium.__version__,
                classes=[WebDriver],
                bstack1lllll1ll11_opy_={bstack11l1ll1_opy_ (u"ࠢࡤࡴࡨࡥࡹ࡫࡟ࡰࡲࡷ࡭ࡴࡴࡳࡠࡨࡵࡳࡲࡥࡣࡢࡲࡶࠦၡ"): bstack11l1ll1l1_opy_}
            )
            def bstack1lllllll1l1_opy_(self):
                return
            if self.config.get(bstack11l1ll1_opy_ (u"ࠣࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࡁࡶࡶࡲࡱࡦࡺࡩࡰࡰࠥၢ"), True):
                Service.start = bstack1lllllll1l1_opy_
                Service.stop = bstack1lllllll1l1_opy_
            def get_accessibility_results(driver):
                if self.accessibility and self.accessibility.is_enabled():
                    return self.accessibility.get_accessibility_results(driver, framework_name=framework)
            def get_accessibility_results_summary(driver):
                if self.accessibility and self.accessibility.is_enabled():
                    return self.accessibility.get_accessibility_results_summary(driver, framework_name=framework)
            def perform_scan(driver):
                if self.accessibility and self.accessibility.is_enabled():
                    return self.accessibility.perform_scan(driver, method=None, framework_name=framework)
            WebDriver.getAccessibilityResults = get_accessibility_results
            WebDriver.get_accessibility_results = get_accessibility_results
            WebDriver.getAccessibilityResultsSummary = get_accessibility_results_summary
            WebDriver.get_accessibility_results_summary = get_accessibility_results_summary
            WebDriver.performScan = perform_scan
            WebDriver.perform_scan = perform_scan
            self.bstack111l11l1_opy_(bstack11l1ll1_opy_ (u"ࠤࡶࡩࡹࡻࡰࡠࡵࡨࡰࡪࡴࡩࡶ࡯ࠥၣ"), datetime.now() - bstack1l1l1ll111_opy_)
        except Exception as e:
            self.logger.error(bstack11l1ll1_opy_ (u"ࠥࡪࡦ࡯࡬ࡦࡦࠣࡸࡴࠦࡳࡦࡶࡸࡴࠥࡹࡥ࡭ࡧࡱ࡭ࡺࡳ࠺ࠡࠤၤ") + str(e) + bstack11l1ll1_opy_ (u"ࠦࠧၥ"))
    def bstack1lllll111ll_opy_(self):
        if self.test_framework:
            self.logger.debug(bstack11l1ll1_opy_ (u"ࠧࡹ࡫ࡪࡲࡳࡩࡩࠦࡳࡦࡶࡸࡴࠥࡶࡹࡵࡧࡶࡸ࠿ࠦࡡ࡭ࡴࡨࡥࡩࡿࠠࡴࡧࡷࠤࡺࡶࠢၦ"))
            return
        if bstack1l11ll1l1_opy_():
            import pytest
            self.test_framework = PytestBDDFramework({ bstack11l1ll1_opy_ (u"ࠨࡰࡺࡶࡨࡷࡹࠨၧ"): pytest.__version__ }, [bstack11l1ll1_opy_ (u"ࠢࡱࡻࡷࡩࡸࡺ࠭ࡣࡦࡧࠦၨ")])
            return
        try:
            import pytest
            self.test_framework = bstack1lllllll1ll_opy_({ bstack11l1ll1_opy_ (u"ࠣࡲࡼࡸࡪࡹࡴࠣၩ"): pytest.__version__ }, [bstack11l1ll1_opy_ (u"ࠤࡳࡽࡹ࡫ࡳࡵࠤၪ")])
        except Exception as e:
            self.logger.error(bstack11l1ll1_opy_ (u"ࠥࡪࡦ࡯࡬ࡦࡦࠣࡸࡴࠦࡳࡦࡶࡸࡴࠥࡶࡹࡵࡧࡶࡸ࠿ࠦࠢၫ") + str(e) + bstack11l1ll1_opy_ (u"ࠦࠧၬ"))
        self.bstack1111l111l1_opy_()
    def bstack1111l111l1_opy_(self):
        if not self.bstack1ll111111_opy_():
            return
        bstack11l1lllll1_opy_ = None
        def bstack1l111lll_opy_(config, startdir):
            return bstack11l1ll1_opy_ (u"ࠧࡪࡲࡪࡸࡨࡶ࠿ࠦࡻ࠱ࡿࠥၭ").format(bstack11l1ll1_opy_ (u"ࠨࡂࡳࡱࡺࡷࡪࡸࡓࡵࡣࡦ࡯ࠧၮ"))
        def bstack1l1111llll_opy_():
            return
        def bstack1ll11l1ll_opy_(self, name: str, default=Notset(), skip: bool = False):
            if str(name).lower() == bstack11l1ll1_opy_ (u"ࠧࡥࡴ࡬ࡺࡪࡸࠧၯ"):
                return bstack11l1ll1_opy_ (u"ࠣࡄࡵࡳࡼࡹࡥࡳࡕࡷࡥࡨࡱࠢၰ")
            else:
                return bstack11l1lllll1_opy_(self, name, default, skip)
        try:
            from pytest_selenium import pytest_selenium
            from _pytest.config import Config
            bstack11l1lllll1_opy_ = Config.getoption
            pytest_selenium.pytest_report_header = bstack1l111lll_opy_
            from pytest_selenium.drivers import browserstack
            browserstack.pytest_selenium_runtest_makereport = bstack1l1111llll_opy_
            Config.getoption = bstack1ll11l1ll_opy_
        except Exception as e:
            self.logger.error(bstack11l1ll1_opy_ (u"ࠤࡉࡥ࡮ࡲࡥࡥࠢࡷࡳࠥࡶࡡࡵࡥ࡫ࠤࡵࡿࡴࡦࡵࡷࠤࡸ࡫࡬ࡦࡰ࡬ࡹࡲࠦࡦࡰࡴࠣࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠼ࠣࠦၱ") + str(e) + bstack11l1ll1_opy_ (u"ࠥࠦၲ"))
    def bstack1llll1l11ll_opy_(self):
        bstack1lll1ll1l11_opy_ = MessageToDict(cli.config_testhub, preserving_proto_field_name=True)
        if isinstance(bstack1lll1ll1l11_opy_, dict):
            if cli.config_observability:
                bstack1lll1ll1l11_opy_.update(
                    {bstack11l1ll1_opy_ (u"ࠦࡴࡨࡳࡦࡴࡹࡥࡧ࡯࡬ࡪࡶࡼࠦၳ"): MessageToDict(cli.config_observability, preserving_proto_field_name=True)}
                )
            if cli.config_accessibility:
                accessibility = MessageToDict(cli.config_accessibility, preserving_proto_field_name=True)
                if isinstance(accessibility, dict) and bstack11l1ll1_opy_ (u"ࠧࡩ࡯࡮࡯ࡤࡲࡩࡹ࡟ࡵࡱࡢࡻࡷࡧࡰࠣၴ") in accessibility.get(bstack11l1ll1_opy_ (u"ࠨ࡯ࡱࡶ࡬ࡳࡳࡹࠢၵ"), {}):
                    bstack1llll11l1l1_opy_ = accessibility.get(bstack11l1ll1_opy_ (u"ࠢࡰࡲࡷ࡭ࡴࡴࡳࠣၶ"))
                    bstack1llll11l1l1_opy_.update({ bstack11l1ll1_opy_ (u"ࠣࡥࡲࡱࡲࡧ࡮ࡥࡵࡗࡳ࡜ࡸࡡࡱࠤၷ"): bstack1llll11l1l1_opy_.pop(bstack11l1ll1_opy_ (u"ࠤࡦࡳࡲࡳࡡ࡯ࡦࡶࡣࡹࡵ࡟ࡸࡴࡤࡴࠧၸ")) })
                bstack1lll1ll1l11_opy_.update({bstack11l1ll1_opy_ (u"ࠥࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࠥၹ"): accessibility })
        return bstack1lll1ll1l11_opy_
    @measure(event_name=EVENTS.bstack1lllll11l11_opy_, stage=STAGE.bstack1l1ll1llll_opy_)
    def bstack11111l1111_opy_(self, bstack1lll1ll1l1l_opy_: str = None, bstack1llll1l1ll1_opy_: str = None, bstack1l11lll1ll_opy_: int = None):
        if not self.cli_bin_session_id or not self.bstack11111111l1_opy_:
            return
        bstack1l1l1ll111_opy_ = datetime.now()
        req = structs.StopBinSessionRequest()
        req.bin_session_id = self.cli_bin_session_id
        if bstack1l11lll1ll_opy_:
            req.bstack1l11lll1ll_opy_ = bstack1l11lll1ll_opy_
        if bstack1lll1ll1l1l_opy_:
            req.bstack1lll1ll1l1l_opy_ = bstack1lll1ll1l1l_opy_
        if bstack1llll1l1ll1_opy_:
            req.bstack1llll1l1ll1_opy_ = bstack1llll1l1ll1_opy_
        try:
            r = self.bstack11111111l1_opy_.StopBinSession(req)
            self.bstack111l11l1_opy_(bstack11l1ll1_opy_ (u"ࠦ࡬ࡸࡰࡤ࠼ࡶࡸࡴࡶ࡟ࡣ࡫ࡱࡣࡸ࡫ࡳࡴ࡫ࡲࡲࠧၺ"), datetime.now() - bstack1l1l1ll111_opy_)
            return r.success
        except grpc.RpcError as e:
            traceback.print_exc()
            raise e
    def bstack111l11l1_opy_(self, key: str, value: timedelta):
        tag = bstack11l1ll1_opy_ (u"ࠧࡩࡨࡪ࡮ࡧ࠱ࡵࡸ࡯ࡤࡧࡶࡷࠧၻ") if self.bstack11ll1llll1_opy_() else bstack11l1ll1_opy_ (u"ࠨ࡭ࡢ࡫ࡱ࠱ࡵࡸ࡯ࡤࡧࡶࡷࠧၼ")
        self.bstack11111lll1l_opy_[bstack11l1ll1_opy_ (u"ࠢ࠻ࠤၽ").join([tag + bstack11l1ll1_opy_ (u"ࠣ࠯ࠥၾ") + str(id(self)), key])] += value
    def bstack1l1l11111l_opy_(self):
        if not os.getenv(bstack11l1ll1_opy_ (u"ࠤࡇࡉࡇ࡛ࡇࡠࡒࡈࡖࡋࠨၿ"), bstack11l1ll1_opy_ (u"ࠥ࠴ࠧႀ")) == bstack11l1ll1_opy_ (u"ࠦ࠶ࠨႁ"):
            return
        bstack1llll1lllll_opy_ = dict()
        bstack1111l1ll11_opy_ = []
        if self.test_framework:
            bstack1111l1ll11_opy_.extend(list(self.test_framework.bstack1111l1ll11_opy_.values()))
        if self.bstack1111ll1l11_opy_:
            bstack1111l1ll11_opy_.extend(list(self.bstack1111ll1l11_opy_.bstack1111l1ll11_opy_.values()))
        for instance in bstack1111l1ll11_opy_:
            if not instance.platform_index in bstack1llll1lllll_opy_:
                bstack1llll1lllll_opy_[instance.platform_index] = defaultdict(lambda: timedelta(microseconds=0))
            report = bstack1llll1lllll_opy_[instance.platform_index]
            for k, v in instance.bstack1lllll1llll_opy_().items():
                report[k] += v
                report[k.split(bstack11l1ll1_opy_ (u"ࠧࡀࠢႂ"))[0]] += v
        bstack1llllll11ll_opy_ = sorted([(k, v) for k, v in self.bstack11111lll1l_opy_.items()], key=lambda o: o[1], reverse=True)
        bstack11111ll11l_opy_ = 0
        for r in bstack1llllll11ll_opy_:
            bstack111111lll1_opy_ = r[1].total_seconds()
            bstack11111ll11l_opy_ += bstack111111lll1_opy_
            self.logger.debug(bstack11l1ll1_opy_ (u"ࠨ࡛ࡱࡧࡵࡪࡢࠦࡣ࡭࡫࠽ࡿࡷࡡ࠰࡞ࡿࡀࠦႃ") + str(bstack111111lll1_opy_) + bstack11l1ll1_opy_ (u"ࠢࠣႄ"))
        self.logger.debug(bstack11l1ll1_opy_ (u"ࠣ࠯࠰ࠦႅ"))
        bstack1lllll1l1ll_opy_ = []
        for platform_index, report in bstack1llll1lllll_opy_.items():
            bstack1lllll1l1ll_opy_.extend([(platform_index, k, v) for k, v in report.items()])
        bstack1lllll1l1ll_opy_.sort(key=lambda o: o[2], reverse=True)
        bstack1ll1l1l1_opy_ = set()
        bstack1111l1111l_opy_ = 0
        for r in bstack1lllll1l1ll_opy_:
            bstack111111lll1_opy_ = r[2].total_seconds()
            bstack1111l1111l_opy_ += bstack111111lll1_opy_
            bstack1ll1l1l1_opy_.add(r[0])
            self.logger.debug(bstack11l1ll1_opy_ (u"ࠤ࡞ࡴࡪࡸࡦ࡞ࠢࡷࡩࡸࡺ࠺ࡱ࡮ࡤࡸ࡫ࡵࡲ࡮࠯ࡾࡶࡠ࠶࡝ࡾ࠼ࡾࡶࡠ࠷࡝ࡾ࠿ࠥႆ") + str(bstack111111lll1_opy_) + bstack11l1ll1_opy_ (u"ࠥࠦႇ"))
        if self.bstack11ll1llll1_opy_():
            self.logger.debug(bstack11l1ll1_opy_ (u"ࠦ࠲࠳ࠢႈ"))
            self.logger.debug(bstack11l1ll1_opy_ (u"ࠧࡡࡰࡦࡴࡩࡡࠥࡩ࡬ࡪ࠼ࡦ࡬࡮ࡲࡤ࠮ࡲࡵࡳࡨ࡫ࡳࡴ࠿ࡾࡸࡴࡺࡡ࡭ࡡࡦࡰ࡮ࢃࠠࡵࡧࡶࡸ࠿ࡶ࡬ࡢࡶࡩࡳࡷࡳࡳ࠮ࡽࡶࡸࡷ࠮ࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡴࠫࢀࡁࠧႉ") + str(bstack1111l1111l_opy_) + bstack11l1ll1_opy_ (u"ࠨࠢႊ"))
        else:
            self.logger.debug(bstack11l1ll1_opy_ (u"ࠢ࡜ࡲࡨࡶ࡫ࡣࠠࡤ࡮࡬࠾ࡲࡧࡩ࡯࠯ࡳࡶࡴࡩࡥࡴࡵࡀࠦႋ") + str(bstack11111ll11l_opy_) + bstack11l1ll1_opy_ (u"ࠣࠤႌ"))
        self.logger.debug(bstack11l1ll1_opy_ (u"ࠤ࠰࠱ႍࠧ"))
    def bstack1llll1l111l_opy_(self, r):
        if r is not None and getattr(r, bstack11l1ll1_opy_ (u"ࠪࡸࡪࡹࡴࡩࡷࡥࠫႎ"), None) and getattr(r.testhub, bstack11l1ll1_opy_ (u"ࠫࡪࡸࡲࡰࡴࡶࠫႏ"), None):
            errors = json.loads(r.testhub.errors.decode(bstack11l1ll1_opy_ (u"ࠧࡻࡴࡧ࠯࠻ࠦ႐")))
            for bstack11111l11l1_opy_, err in errors.items():
                if err[bstack11l1ll1_opy_ (u"࠭ࡴࡺࡲࡨࠫ႑")] == bstack11l1ll1_opy_ (u"ࠧࡪࡰࡩࡳࠬ႒"):
                    self.logger.info(err[bstack11l1ll1_opy_ (u"ࠨ࡯ࡨࡷࡸࡧࡧࡦࠩ႓")])
                else:
                    self.logger.error(err[bstack11l1ll1_opy_ (u"ࠩࡰࡩࡸࡹࡡࡨࡧࠪ႔")])
cli = SDKCLI()