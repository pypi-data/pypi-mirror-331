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
import logging
from enum import Enum
import os
import threading
import traceback
from typing import Dict, List, Any, Callable, Tuple, Union
import abc
from datetime import datetime, timezone
from dataclasses import dataclass
from browserstack_sdk.sdk_cli.bstack1111l11lll_opy_ import bstack1111l1lll1_opy_, bstack111l11111l_opy_
class bstack1lll1llll11_opy_(Enum):
    PRE = 0
    POST = 1
    def __repr__(self) -> str:
        return bstack11l1ll1_opy_ (u"࡚ࠧࡥࡴࡶࡋࡳࡴࡱࡓࡵࡣࡷࡩ࠳ࢁࡽࠣᎠ").format(self.name)
class bstack1llll11llll_opy_(Enum):
    NONE = 0
    BEFORE_ALL = 1
    LOG = 2
    SETUP_FIXTURE = 3
    INIT_TEST = 4
    BEFORE_EACH = 5
    AFTER_EACH = 6
    TEST = 7
    STEP = 8
    LOG_REPORT = 9
    AFTER_ALL = 10
    def __eq__(self, other):
        if self.__class__ is other.__class__:
            return self.value == other.value
        return NotImplemented
    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return self.value < other.value
        return NotImplemented
    def __repr__(self) -> str:
        return bstack11l1ll1_opy_ (u"ࠨࡔࡦࡵࡷࡊࡷࡧ࡭ࡦࡹࡲࡶࡰ࡙ࡴࡢࡶࡨ࠲ࢀࢃࠢᎡ").format(self.name)
class bstack11111l1l11_opy_(bstack1111l1lll1_opy_):
    bstack1lll1l1l111_opy_: List[str]
    bstack1l1lll1l111_opy_: Dict[str, str]
    state: bstack1llll11llll_opy_
    bstack1111llll11_opy_: datetime
    bstack1111ll1l1l_opy_: datetime
    def __init__(
        self,
        context: bstack111l11111l_opy_,
        bstack1lll1l1l111_opy_: List[str],
        bstack1l1lll1l111_opy_: Dict[str, str],
        state=bstack1llll11llll_opy_.NONE,
    ):
        super().__init__(context)
        self.bstack1lll1l1l111_opy_ = bstack1lll1l1l111_opy_
        self.bstack1l1lll1l111_opy_ = bstack1l1lll1l111_opy_
        self.state = state
        self.bstack1111llll11_opy_ = datetime.now(tz=timezone.utc)
        self.bstack1111ll1l1l_opy_ = datetime.now(tz=timezone.utc)
    def bstack1111l11l11_opy_(self, bstack1111lllll1_opy_: bstack1llll11llll_opy_):
        bstack111l1111l1_opy_ = bstack1llll11llll_opy_(bstack1111lllll1_opy_).name
        if not bstack111l1111l1_opy_:
            return False
        if bstack1111lllll1_opy_ == self.state:
            return False
        self.state = bstack1111lllll1_opy_
        self.bstack1111ll1l1l_opy_ = datetime.now(tz=timezone.utc)
        return True
@dataclass
class bstack1l1l1l11lll_opy_:
    test_framework_name: str
    test_framework_version: str
    platform_index: int
@dataclass
class bstack1llll111ll1_opy_:
    kind: str
    message: str
    level: Union[None, str] = None
    timestamp: Union[None, datetime] = datetime.now(tz=timezone.utc)
class TestFramework(abc.ABC):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    bstack1lll111l1l1_opy_ = bstack11l1ll1_opy_ (u"ࠢࡵࡧࡶࡸࡤࡻࡵࡪࡦࠥᎢ")
    bstack1l1l1llll11_opy_ = bstack11l1ll1_opy_ (u"ࠣࡶࡨࡷࡹࡥࡩࡥࠤᎣ")
    bstack1lll11ll111_opy_ = bstack11l1ll1_opy_ (u"ࠤࡷࡩࡸࡺ࡟࡯ࡣࡰࡩࠧᎤ")
    bstack1l1l1lll111_opy_ = bstack11l1ll1_opy_ (u"ࠥࡸࡪࡹࡴࡠࡨ࡬ࡰࡪࡥࡰࡢࡶ࡫ࠦᎥ")
    bstack1l1l1l11ll1_opy_ = bstack11l1ll1_opy_ (u"ࠦࡹ࡫ࡳࡵࡡࡷࡥ࡬ࡹࠢᎦ")
    bstack1l1lll1ll11_opy_ = bstack11l1ll1_opy_ (u"ࠧࡺࡥࡴࡶࡢࡶࡪࡹࡵ࡭ࡶࠥᎧ")
    bstack1ll1l1lll1l_opy_ = bstack11l1ll1_opy_ (u"ࠨࡴࡦࡵࡷࡣࡷ࡫ࡳࡶ࡮ࡷࡣࡦࡺࠢᎨ")
    bstack1ll11ll1l11_opy_ = bstack11l1ll1_opy_ (u"ࠢࡵࡧࡶࡸࡤࡹࡴࡢࡴࡷࡩࡩࡥࡡࡵࠤᎩ")
    bstack1ll1l111l11_opy_ = bstack11l1ll1_opy_ (u"ࠣࡶࡨࡷࡹࡥࡥ࡯ࡦࡨࡨࡤࡧࡴࠣᎪ")
    bstack1l1l1llll1l_opy_ = bstack11l1ll1_opy_ (u"ࠤࡷࡩࡸࡺ࡟࡭ࡱࡦࡥࡹ࡯࡯࡯ࠤᎫ")
    bstack1lll11111l1_opy_ = bstack11l1ll1_opy_ (u"ࠥࡸࡪࡹࡴࡠࡨࡵࡥࡲ࡫ࡷࡰࡴ࡮ࡣࡳࡧ࡭ࡦࠤᎬ")
    bstack1ll1l11llll_opy_ = bstack11l1ll1_opy_ (u"ࠦࡹ࡫ࡳࡵࡡࡩࡶࡦࡳࡥࡸࡱࡵ࡯ࡤࡼࡥࡳࡵ࡬ࡳࡳࠨᎭ")
    bstack1l1ll1ll1l1_opy_ = bstack11l1ll1_opy_ (u"ࠧࡺࡥࡴࡶࡢࡧࡴࡪࡥࠣᎮ")
    bstack1ll11l11l1l_opy_ = bstack11l1ll1_opy_ (u"ࠨࡴࡦࡵࡷࡣࡷ࡫ࡲࡶࡰࡢࡲࡦࡳࡥࠣᎯ")
    bstack1lll11ll1l1_opy_ = bstack11l1ll1_opy_ (u"ࠢࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡡ࡬ࡲࡩ࡫ࡸࠣᎰ")
    bstack1l1llll11ll_opy_ = bstack11l1ll1_opy_ (u"ࠣࡶࡨࡷࡹࡥࡦࡢ࡫࡯ࡹࡷ࡫ࠢᎱ")
    bstack1l1l1lllll1_opy_ = bstack11l1ll1_opy_ (u"ࠤࡷࡩࡸࡺ࡟ࡧࡣ࡬ࡰࡺࡸࡥࡠࡶࡼࡴࡪࠨᎲ")
    bstack1l1ll1l1lll_opy_ = bstack11l1ll1_opy_ (u"ࠥࡸࡪࡹࡴࡠ࡮ࡲ࡫ࡸࠨᎳ")
    bstack1l1l1l1l1l1_opy_ = bstack11l1ll1_opy_ (u"ࠦࡹ࡫ࡳࡵࡡࡰࡩࡹࡧࠢᎴ")
    bstack1l1l1l1111l_opy_ = bstack11l1ll1_opy_ (u"ࠬࡺࡥࡴࡶࡢࡷࡨࡵࡰࡦࡵࠪᎵ")
    bstack1l1llll1l11_opy_ = bstack11l1ll1_opy_ (u"ࠨࡡࡶࡶࡲࡱࡦࡺࡥࡠࡵࡨࡷࡸ࡯࡯࡯ࡡࡱࡥࡲ࡫ࠢᎶ")
    bstack1l1l1ll11l1_opy_ = bstack11l1ll1_opy_ (u"ࠢࡦࡸࡨࡲࡹࡥࡳࡵࡣࡵࡸࡪࡪ࡟ࡢࡶࠥᎷ")
    bstack1l1ll11l111_opy_ = bstack11l1ll1_opy_ (u"ࠣࡧࡹࡩࡳࡺ࡟ࡦࡰࡧࡩࡩࡥࡡࡵࠤᎸ")
    bstack1l1ll11llll_opy_ = bstack11l1ll1_opy_ (u"ࠤ࡫ࡳࡴࡱ࡟ࡪࡦࠥᎹ")
    bstack1l1l1l1lll1_opy_ = bstack11l1ll1_opy_ (u"ࠥ࡬ࡴࡵ࡫ࡠࡴࡨࡷࡺࡲࡴࠣᎺ")
    bstack1l1ll1llll1_opy_ = bstack11l1ll1_opy_ (u"ࠦ࡭ࡵ࡯࡬ࡡ࡯ࡳ࡬ࡹࠢᎻ")
    bstack1l1ll1l111l_opy_ = bstack11l1ll1_opy_ (u"ࠧ࡮࡯ࡰ࡭ࡢࡲࡦࡳࡥࠣᎼ")
    bstack1l1l1l1ll1l_opy_ = bstack11l1ll1_opy_ (u"ࠨࡰࡦࡰࡧ࡭ࡳ࡭ࠢᎽ")
    bstack1l1lll111ll_opy_ = bstack11l1ll1_opy_ (u"ࠢࡱࡧࡱࡨ࡮ࡴࡧࠣᎾ")
    bstack1ll11l1ll1l_opy_ = bstack11l1ll1_opy_ (u"ࠣࡖࡈࡗ࡙ࡥࡓࡄࡔࡈࡉࡓ࡙ࡈࡐࡖࠥᎿ")
    bstack1ll1ll1111l_opy_ = bstack11l1ll1_opy_ (u"ࠤࡗࡉࡘ࡚࡟ࡍࡑࡊࠦᏀ")
    bstack1111l1ll11_opy_: Dict[str, bstack11111l1l11_opy_] = dict()
    bstack1l1l11l111l_opy_: Dict[str, List[Callable]] = dict()
    bstack1lll1l1l111_opy_: List[str]
    bstack1l1lll1l111_opy_: Dict[str, str]
    def __init__(
        self,
        bstack1lll1l1l111_opy_: List[str],
        bstack1l1lll1l111_opy_: Dict[str, str],
    ):
        self.bstack1lll1l1l111_opy_ = bstack1lll1l1l111_opy_
        self.bstack1l1lll1l111_opy_ = bstack1l1lll1l111_opy_
    def track_event(
        self,
        context: bstack1l1l1l11lll_opy_,
        test_framework_state: bstack1llll11llll_opy_,
        test_hook_state: bstack1lll1llll11_opy_,
        *args,
        **kwargs,
    ):
        self.logger.debug(bstack11l1ll1_opy_ (u"ࠥࡸࡷࡧࡣ࡬ࡡࡨࡺࡪࡴࡴ࠻ࠢࡷࡩࡸࡺ࡟ࡧࡴࡤࡱࡪࡽ࡯ࡳ࡭ࡢࡷࡹࡧࡴࡦ࠿ࡾࡸࡪࡹࡴࡠࡨࡵࡥࡲ࡫ࡷࡰࡴ࡮ࡣࡸࡺࡡࡵࡧࢀࠤࡹ࡫ࡳࡵࡡ࡫ࡳࡴࡱ࡟ࡴࡶࡤࡸࡪࡃࡻࡵࡧࡶࡸࡤ࡮࡯ࡰ࡭ࡢࡷࡹࡧࡴࡦࡿࠣࡥࡷ࡭ࡳ࠾ࡽࡤࡶ࡬ࡹࡽࠡ࡭ࡺࡥࡷ࡭ࡳ࠾ࠤᏁ") + str(kwargs) + bstack11l1ll1_opy_ (u"ࠦࠧᏂ"))
    def bstack1l1lll11111_opy_(
        self,
        instance: bstack11111l1l11_opy_,
        bstack111l111l1l_opy_: Tuple[bstack1llll11llll_opy_, bstack1lll1llll11_opy_],
        *args,
        **kwargs,
    ):
        bstack1l1l11ll1ll_opy_ = TestFramework.bstack1l1l111lll1_opy_(bstack111l111l1l_opy_)
        if not bstack1l1l11ll1ll_opy_ in TestFramework.bstack1l1l11l111l_opy_:
            return
        self.logger.debug(bstack11l1ll1_opy_ (u"ࠧ࡯࡮ࡷࡱ࡮࡭ࡳ࡭ࠠࠣᏃ") + str(len(TestFramework.bstack1l1l11l111l_opy_[bstack1l1l11ll1ll_opy_])) + bstack11l1ll1_opy_ (u"ࠨࠠࡤࡣ࡯ࡰࡧࡧࡣ࡬ࡵࠥᏄ"))
        for callback in TestFramework.bstack1l1l11l111l_opy_[bstack1l1l11ll1ll_opy_]:
            try:
                callback(self, instance, bstack111l111l1l_opy_, *args, **kwargs)
            except Exception as e:
                self.logger.error(bstack11l1ll1_opy_ (u"ࠢࡦࡴࡵࡳࡷࠦࡩ࡯ࡸࡲ࡯࡮ࡴࡧࠡࡥࡤࡰࡱࡨࡡࡤ࡭࠽ࠤࠧᏅ") + str(e) + bstack11l1ll1_opy_ (u"ࠣࠤᏆ"))
                traceback.print_exc()
    @abc.abstractmethod
    def bstack1ll11l1ll11_opy_(self):
        return
    @abc.abstractmethod
    def bstack1ll11l1l111_opy_(self, instance, bstack111l111l1l_opy_):
        return
    @abc.abstractmethod
    def bstack1ll1l1111l1_opy_(self, instance, bstack111l111l1l_opy_):
        return
    @staticmethod
    def bstack1111llllll_opy_(target: object, strict=True):
        if target is None:
            return None
        ctx = bstack1111l1lll1_opy_.create_context(target)
        instance = TestFramework.bstack1111l1ll11_opy_.get(ctx.id, None)
        if instance and instance.bstack1111lll111_opy_(target):
            return instance
        return instance if instance and not strict else None
    @staticmethod
    def bstack1ll1l1l1l1l_opy_(reverse=True) -> List[bstack11111l1l11_opy_]:
        thread_id = threading.get_ident()
        process_id = os.getpid()
        return sorted(
            filter(
                lambda t: t.context.thread_id == thread_id
                and t.context.process_id == process_id,
                TestFramework.bstack1111l1ll11_opy_.values(),
            ),
            key=lambda t: t.bstack1111llll11_opy_,
            reverse=reverse,
        )
    @staticmethod
    def bstack1111lll1ll_opy_(ctx: bstack111l11111l_opy_, reverse=True) -> List[bstack11111l1l11_opy_]:
        return sorted(
            filter(
                lambda t: t.context.thread_id == ctx.thread_id
                and t.context.process_id == ctx.process_id,
                TestFramework.bstack1111l1ll11_opy_.values(),
            ),
            key=lambda t: t.bstack1111llll11_opy_,
            reverse=reverse,
        )
    @staticmethod
    def bstack111l1111ll_opy_(instance: bstack11111l1l11_opy_, key: str):
        return instance and key in instance.data
    @staticmethod
    def bstack111l111111_opy_(instance: bstack11111l1l11_opy_, key: str, default_value=None):
        return instance.data.get(key, default_value) if instance else default_value
    @staticmethod
    def bstack1111l11l11_opy_(instance: bstack11111l1l11_opy_, key: str, value: Any):
        TestFramework.logger.debug(bstack11l1ll1_opy_ (u"ࠤࡶࡩࡹࡥࡳࡵࡣࡷࡩ࠿ࠦࡩ࡯ࡵࡷࡥࡳࡩࡥ࠾ࡽ࡬ࡲࡸࡺࡡ࡯ࡥࡨ࠲ࡷ࡫ࡦࠩࠫࢀࠤࡰ࡫ࡹ࠾ࡽ࡮ࡩࡾࢃࠠࡷࡣ࡯ࡹࡪࡃࠢᏇ") + str(value) + bstack11l1ll1_opy_ (u"ࠥࠦᏈ"))
        instance.data[key] = value
        return True
    @staticmethod
    def bstack1l1l1l1l111_opy_(instance: bstack11111l1l11_opy_, entries: Dict[str, Any]):
        TestFramework.logger.debug(bstack11l1ll1_opy_ (u"ࠦࡸ࡫ࡴࡠࡵࡷࡥࡹ࡫࡟ࡦࡰࡷࡶ࡮࡫ࡳ࠻ࠢ࡬ࡲࡸࡺࡡ࡯ࡥࡨࡁࢀ࡯࡮ࡴࡶࡤࡲࡨ࡫࠮ࡳࡧࡩࠬ࠮ࢃࠠࡦࡰࡷࡶ࡮࡫ࡳ࠾ࠤᏉ") + str(entries) + bstack11l1ll1_opy_ (u"ࠧࠨᏊ"))
        instance.data.update(entries)
        return True
    @staticmethod
    def bstack1l1l111ll1l_opy_(instance: bstack1llll11llll_opy_, key: str, value: Any):
        TestFramework.logger.debug(bstack11l1ll1_opy_ (u"ࠨࡵࡱࡦࡤࡸࡪࡥࡳࡵࡣࡷࡩ࠿ࠦࡩ࡯ࡵࡷࡥࡳࡩࡥ࠾ࡽ࡬ࡲࡸࡺࡡ࡯ࡥࡨ࠲ࡷ࡫ࡦࠩࠫࢀࠤࡰ࡫ࡹ࠾ࡽ࡮ࡩࡾࢃࠠࡷࡣ࡯ࡹࡪࡃࠢᏋ") + str(value) + bstack11l1ll1_opy_ (u"ࠢࠣᏌ"))
        instance.data.update(key, value)
        return True
    @staticmethod
    def get_data(key: str, target: object, strict=True, default_value=None):
        instance = TestFramework.bstack1111llllll_opy_(target, strict)
        return TestFramework.bstack111l111111_opy_(instance, key, default_value)
    @staticmethod
    def set_data(key: str, value: Any, target: object, strict=True):
        instance = TestFramework.bstack1111llllll_opy_(target, strict)
        if not instance:
            return False
        instance.data[key] = value
        return True
    @staticmethod
    def bstack1l1ll1l1l11_opy_(instance: bstack11111l1l11_opy_, key: str, value: object):
        if instance == None:
            return
        instance.data[key] = value
    @staticmethod
    def bstack1l1ll1111l1_opy_(instance: bstack11111l1l11_opy_, key: str):
        return instance.data[key]
    @staticmethod
    def bstack1l1l111lll1_opy_(bstack111l111l1l_opy_: Tuple[bstack1llll11llll_opy_, bstack1lll1llll11_opy_]):
        return bstack11l1ll1_opy_ (u"ࠣ࠼ࠥᏍ").join((bstack1llll11llll_opy_(bstack111l111l1l_opy_[0]).name, bstack1lll1llll11_opy_(bstack111l111l1l_opy_[1]).name))
    @staticmethod
    def bstack1lll11llll1_opy_(bstack111l111l1l_opy_: Tuple[bstack1llll11llll_opy_, bstack1lll1llll11_opy_], callback: Callable):
        bstack1l1l11ll1ll_opy_ = TestFramework.bstack1l1l111lll1_opy_(bstack111l111l1l_opy_)
        TestFramework.logger.debug(bstack11l1ll1_opy_ (u"ࠤࡶࡩࡹࡥࡨࡰࡱ࡮ࡣࡨࡧ࡬࡭ࡤࡤࡧࡰࡀࠠࡩࡱࡲ࡯ࡤࡸࡥࡨ࡫ࡶࡸࡷࡿ࡟࡬ࡧࡼࡁࠧᏎ") + str(bstack1l1l11ll1ll_opy_) + bstack11l1ll1_opy_ (u"ࠥࠦᏏ"))
        if not bstack1l1l11ll1ll_opy_ in TestFramework.bstack1l1l11l111l_opy_:
            TestFramework.bstack1l1l11l111l_opy_[bstack1l1l11ll1ll_opy_] = []
        TestFramework.bstack1l1l11l111l_opy_[bstack1l1l11ll1ll_opy_].append(callback)
    @staticmethod
    def bstack1ll1l111111_opy_(o):
        klass = o.__class__
        module = klass.__module__
        if module == bstack11l1ll1_opy_ (u"ࠦࡧࡻࡩ࡭ࡶ࡬ࡲࡸࠨᏐ"):
            return klass.__qualname__
        return module + bstack11l1ll1_opy_ (u"ࠧ࠴ࠢᏑ") + klass.__qualname__
    @staticmethod
    def bstack1ll11l1l11l_opy_(obj, keys, default_value=None):
        return {k: getattr(obj, k, default_value) for k in keys}