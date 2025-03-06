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
from typing import Dict, Tuple, Callable, Type, List, Any
import abc
from datetime import datetime, timezone, timedelta
from browserstack_sdk.sdk_cli.bstack1111l11lll_opy_ import bstack1111l1lll1_opy_, bstack111l11111l_opy_
class bstack1111l1l1l1_opy_(Enum):
    PRE = 0
    POST = 1
    def __repr__(self) -> str:
        return bstack11l1ll1_opy_ (u"ࠨࡈࡰࡱ࡮ࡗࡹࡧࡴࡦ࠰ࡾࢁࠧ࿍").format(self.name)
class bstack1111ll111l_opy_(Enum):
    NONE = 0
    bstack1111ll1ll1_opy_ = 1
    bstack1111l1l11l_opy_ = 2
    bstack1111lll1l1_opy_ = 3
    QUIT = 4
    def __eq__(self, other):
        if self.__class__ is other.__class__:
            return self.value == other.value
        return NotImplemented
    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return self.value < other.value
        return NotImplemented
    def __repr__(self) -> str:
        return bstack11l1ll1_opy_ (u"ࠢࡂࡷࡷࡳࡲࡧࡴࡪࡱࡱࡊࡷࡧ࡭ࡦࡹࡲࡶࡰ࡙ࡴࡢࡶࡨ࠲ࢀࢃࠢ࿎").format(self.name)
class bstack1111l11l1l_opy_(bstack1111l1lll1_opy_):
    framework_name: str
    framework_version: str
    state: bstack1111ll111l_opy_
    previous_state: bstack1111ll111l_opy_
    bstack1111llll11_opy_: datetime
    bstack1111ll1l1l_opy_: datetime
    def __init__(
        self,
        context: bstack111l11111l_opy_,
        framework_name: str,
        framework_version: str,
        state=bstack1111ll111l_opy_.NONE,
    ):
        super().__init__(context)
        self.framework_name = framework_name
        self.framework_version = framework_version
        self.state = state
        self.previous_state = bstack1111ll111l_opy_.NONE
        self.bstack1111llll11_opy_ = datetime.now(tz=timezone.utc)
        self.bstack1111ll1l1l_opy_ = datetime.now(tz=timezone.utc)
    def bstack1111l11l11_opy_(self, bstack1111lllll1_opy_: bstack1111ll111l_opy_):
        bstack111l1111l1_opy_ = bstack1111ll111l_opy_(bstack1111lllll1_opy_).name
        if not bstack111l1111l1_opy_:
            return False
        if bstack1111lllll1_opy_ == self.state:
            return False
        if (
            bstack1111lllll1_opy_ == bstack1111ll111l_opy_.NONE
            or (self.state != bstack1111ll111l_opy_.NONE and bstack1111lllll1_opy_ == bstack1111ll111l_opy_.bstack1111ll1ll1_opy_)
            or (self.state < bstack1111ll111l_opy_.bstack1111ll1ll1_opy_ and bstack1111lllll1_opy_ == bstack1111ll111l_opy_.bstack1111l1l11l_opy_)
            or (self.state < bstack1111ll111l_opy_.bstack1111ll1ll1_opy_ and bstack1111lllll1_opy_ == bstack1111ll111l_opy_.QUIT)
        ):
            raise ValueError(bstack11l1ll1_opy_ (u"ࠣ࡫ࡱࡺࡦࡲࡩࡥࠢࡶࡸࡦࡺࡥࠡࡶࡵࡥࡳࡹࡩࡵ࡫ࡲࡲ࠿ࠦࠢ࿏") + str(self.state) + bstack11l1ll1_opy_ (u"ࠤࠣࡁࡃࠦࠢ࿐") + str(bstack1111lllll1_opy_))
        self.previous_state = self.state
        self.state = bstack1111lllll1_opy_
        self.bstack1111ll1l1l_opy_ = datetime.now(tz=timezone.utc)
        return True
class bstack1111llll1l_opy_(abc.ABC):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    bstack1111l1ll11_opy_: Dict[str, bstack1111l11l1l_opy_] = dict()
    framework_name: str
    framework_version: str
    classes: List[Type]
    def __init__(
        self,
        framework_name: str,
        framework_version: str,
        classes: List[Type],
    ):
        self.framework_name = framework_name
        self.framework_version = framework_version
        self.classes = classes
    @abc.abstractmethod
    def bstack1111l1ll1l_opy_(self, instance: bstack1111l11l1l_opy_, method_name: str, bstack111l111ll1_opy_: timedelta, *args, **kwargs):
        return
    @abc.abstractmethod
    def bstack1111l1l111_opy_(
        self, method_name, previous_state: bstack1111ll111l_opy_, *args, **kwargs
    ) -> bstack1111ll111l_opy_:
        return
    @abc.abstractmethod
    def bstack111l111l11_opy_(
        self,
        target: object,
        exec: Tuple[bstack1111l11l1l_opy_, str],
        bstack111l111l1l_opy_: Tuple[bstack1111ll111l_opy_, bstack1111l1l1l1_opy_],
        result: Any,
        *args,
        **kwargs,
    ) -> Callable:
        return
    def bstack1111l11ll1_opy_(self, bstack1111lll11l_opy_: List[str]):
        for clazz in self.classes:
            for method_name in bstack1111lll11l_opy_:
                bstack1111ll11l1_opy_ = getattr(clazz, method_name, None)
                if not callable(bstack1111ll11l1_opy_):
                    self.logger.warning(bstack11l1ll1_opy_ (u"ࠥࡹࡳࡶࡡࡵࡥ࡫ࡩࡩࠦ࡭ࡦࡶ࡫ࡳࡩࡀࠠࠣ࿑") + str(method_name) + bstack11l1ll1_opy_ (u"ࠦࠧ࿒"))
                    continue
                bstack1111l1llll_opy_ = self.bstack1111l1l111_opy_(
                    method_name, previous_state=bstack1111ll111l_opy_.NONE
                )
                bstack1111ll11ll_opy_ = self.bstack1111ll1lll_opy_(
                    method_name,
                    (bstack1111l1llll_opy_ if bstack1111l1llll_opy_ else bstack1111ll111l_opy_.NONE),
                    bstack1111ll11l1_opy_,
                )
                if not callable(bstack1111ll11ll_opy_):
                    self.logger.warning(bstack11l1ll1_opy_ (u"ࠧࡳࡥࡵࡪࡲࡨࠥࡴ࡯ࡵࠢࡳࡥࡹࡩࡨࡦࡦ࠽ࠤࢀࡳࡥࡵࡪࡲࡨࡤࡴࡡ࡮ࡧࢀࠤ࠭ࢁࡳࡦ࡮ࡩ࠲࡫ࡸࡡ࡮ࡧࡺࡳࡷࡱ࡟࡯ࡣࡰࡩࢂࡀࠠࠣ࿓") + str(self.framework_version) + bstack11l1ll1_opy_ (u"ࠨࠩࠣ࿔"))
                    continue
                setattr(clazz, method_name, bstack1111ll11ll_opy_)
    def bstack1111ll1lll_opy_(
        self,
        method_name: str,
        bstack1111l1llll_opy_: bstack1111ll111l_opy_,
        bstack1111ll11l1_opy_: Callable,
    ):
        def wrapped(target, *args, **kwargs):
            bstack1l1l1ll111_opy_ = datetime.now()
            (bstack1111l1llll_opy_,) = wrapped.__vars__
            bstack1111l1llll_opy_ = (
                bstack1111l1llll_opy_
                if bstack1111l1llll_opy_ and bstack1111l1llll_opy_ != bstack1111ll111l_opy_.NONE
                else self.bstack1111l1l111_opy_(method_name, previous_state=bstack1111l1llll_opy_, *args, **kwargs)
            )
            if bstack1111l1llll_opy_ == bstack1111ll111l_opy_.bstack1111ll1ll1_opy_:
                ctx = bstack1111l1lll1_opy_.create_context(target)
                bstack1111llll1l_opy_.bstack1111l1ll11_opy_[ctx.id] = bstack1111l11l1l_opy_(
                    ctx, self.framework_name, self.framework_version, bstack1111l1llll_opy_
                )
                self.logger.debug(bstack11l1ll1_opy_ (u"ࠢࡸࡴࡤࡴࡵ࡫ࡤࠡ࡯ࡨࡸ࡭ࡵࡤࠡࡥࡵࡩࡦࡺࡥࡥ࠼ࠣࡿࡹࡧࡲࡨࡧࡷ࠲ࡤࡥࡣ࡭ࡣࡶࡷࡤࡥࡽࠡ࡯ࡨࡸ࡭ࡵࡤࡠࡰࡤࡱࡪࡃࡻ࡮ࡧࡷ࡬ࡴࡪ࡟࡯ࡣࡰࡩࢂࠦࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࡡࡶࡸࡦࡺࡥ࠾ࡽࡩࡶࡦࡳࡥࡸࡱࡵ࡯ࡤࡹࡴࡢࡶࡨࢁࠥࡩࡴࡹ࠿ࡾࡧࡹࡾ࠮ࡪࡦࢀࠤ࡮ࡴࡳࡵࡣࡱࡧࡪࡹ࠽ࠣ࿕") + str(bstack1111llll1l_opy_.bstack1111l1ll11_opy_.keys()) + bstack11l1ll1_opy_ (u"ࠣࠤ࿖"))
            else:
                self.logger.debug(bstack11l1ll1_opy_ (u"ࠤࡺࡶࡦࡶࡰࡦࡦࠣࡱࡪࡺࡨࡰࡦࠣ࡭ࡳࡼ࡯࡬ࡧࡧ࠾ࠥࢁࡴࡢࡴࡪࡩࡹ࠴࡟ࡠࡥ࡯ࡥࡸࡹ࡟ࡠࡿࠣࡱࡪࡺࡨࡰࡦࡢࡲࡦࡳࡥ࠾ࡽࡰࡩࡹ࡮࡯ࡥࡡࡱࡥࡲ࡫ࡽࠡࡨࡵࡥࡲ࡫ࡷࡰࡴ࡮ࡣࡸࡺࡡࡵࡧࡀࡿ࡫ࡸࡡ࡮ࡧࡺࡳࡷࡱ࡟ࡴࡶࡤࡸࡪࢃࠠࡪࡰࡶࡸࡦࡴࡣࡦࡵࡀࠦ࿗") + str(bstack1111llll1l_opy_.bstack1111l1ll11_opy_.keys()) + bstack11l1ll1_opy_ (u"ࠥࠦ࿘"))
            instance = bstack1111llll1l_opy_.bstack1111llllll_opy_(target)
            if bstack1111l1llll_opy_ == bstack1111ll111l_opy_.NONE or not instance:
                ctx = bstack1111l1lll1_opy_.create_context(target)
                self.logger.warning(bstack11l1ll1_opy_ (u"ࠦࡼࡸࡡࡱࡲࡨࡨࠥࡳࡥࡵࡪࡲࡨࠥࡻ࡮ࡵࡴࡤࡧࡰ࡫ࡤ࠻ࠢࡾࡱࡪࡺࡨࡰࡦࡢࡲࡦࡳࡥࡾࠢࡩࡶࡦࡳࡥࡸࡱࡵ࡯ࡤࡹࡴࡢࡶࡨࡁࢀ࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫ࡠࡵࡷࡥࡹ࡫ࡽࠡࡥࡷࡼࡂࢁࡣࡵࡺࢀࠤ࡮ࡴࡳࡵࡣࡱࡧࡪࡹ࠽ࠣ࿙") + str(bstack1111llll1l_opy_.bstack1111l1ll11_opy_.keys()) + bstack11l1ll1_opy_ (u"ࠧࠨ࿚"))
                return bstack1111ll11l1_opy_(target, *args, **kwargs)
            bstack1111l1l1ll_opy_ = self.bstack111l111l11_opy_(
                target,
                (instance, method_name),
                (bstack1111l1llll_opy_, bstack1111l1l1l1_opy_.PRE),
                None,
                *args,
                **kwargs,
            )
            if instance.bstack1111l11l11_opy_(bstack1111l1llll_opy_):
                self.logger.debug(bstack11l1ll1_opy_ (u"ࠨࡡࡱࡲ࡯࡭ࡪࡪࠠࡴࡶࡤࡸࡪ࠳ࡴࡳࡣࡱࡷ࡮ࡺࡩࡰࡰ࠽ࠤࢀ࡯࡮ࡴࡶࡤࡲࡨ࡫࠮ࡱࡴࡨࡺ࡮ࡵࡵࡴࡡࡶࡸࡦࡺࡥࡾࠢࡀࡂࠥࢁࡩ࡯ࡵࡷࡥࡳࡩࡥ࠯ࡵࡷࡥࡹ࡫ࡽࠡࠪࡾࡸࡾࡶࡥࠩࡶࡤࡶ࡬࡫ࡴࠪࡿ࠱ࡿࡲ࡫ࡴࡩࡱࡧࡣࡳࡧ࡭ࡦࡿࠣࡿࡦࡸࡧࡴࡿࠬࠤࡠࠨ࿛") + str(instance.ref()) + bstack11l1ll1_opy_ (u"ࠢ࡞ࠤ࿜"))
            result = (
                bstack1111l1l1ll_opy_(target, bstack1111ll11l1_opy_, *args, **kwargs)
                if callable(bstack1111l1l1ll_opy_)
                else bstack1111ll11l1_opy_(target, *args, **kwargs)
            )
            bstack1111ll1111_opy_ = self.bstack111l111l11_opy_(
                target,
                (instance, method_name),
                (bstack1111l1llll_opy_, bstack1111l1l1l1_opy_.POST),
                result,
                *args,
                **kwargs,
            )
            self.bstack1111l1ll1l_opy_(instance, method_name, datetime.now() - bstack1l1l1ll111_opy_, *args, **kwargs)
            return bstack1111ll1111_opy_ if bstack1111ll1111_opy_ else result
        wrapped.__name__ = method_name
        wrapped.__vars__ = (bstack1111l1llll_opy_,)
        return wrapped
    @staticmethod
    def bstack1111llllll_opy_(target: object, strict=True):
        ctx = bstack1111l1lll1_opy_.create_context(target)
        instance = bstack1111llll1l_opy_.bstack1111l1ll11_opy_.get(ctx.id, None)
        if instance and instance.bstack1111lll111_opy_(target):
            return instance
        return instance if instance and not strict else None
    @staticmethod
    def bstack1111lll1ll_opy_(
        ctx: bstack111l11111l_opy_, state: bstack1111ll111l_opy_, reverse=True
    ) -> List[bstack1111l11l1l_opy_]:
        return sorted(
            filter(
                lambda t: t.state == state
                and t.context.thread_id == ctx.thread_id
                and t.context.process_id == ctx.process_id,
                bstack1111llll1l_opy_.bstack1111l1ll11_opy_.values(),
            ),
            key=lambda t: t.bstack1111llll11_opy_,
            reverse=reverse,
        )
    @staticmethod
    def bstack111l1111ll_opy_(instance: bstack1111l11l1l_opy_, key: str):
        return instance and key in instance.data
    @staticmethod
    def bstack111l111111_opy_(instance: bstack1111l11l1l_opy_, key: str, default_value=None):
        return instance.data.get(key, default_value) if instance else default_value
    @staticmethod
    def bstack1111l11l11_opy_(instance: bstack1111l11l1l_opy_, key: str, value: Any) -> bool:
        instance.data[key] = value
        bstack1111llll1l_opy_.logger.debug(bstack11l1ll1_opy_ (u"ࠣࡵࡨࡸࡤࡹࡴࡢࡶࡨ࠾ࠥ࡯࡮ࡴࡶࡤࡲࡨ࡫࠽ࡼ࡫ࡱࡷࡹࡧ࡮ࡤࡧ࠱ࡶࡪ࡬ࠨࠪࡿࠣ࡯ࡪࡿ࠽ࡼ࡭ࡨࡽࢂࠦࡶࡢ࡮ࡸࡩࡂࠨ࿝") + str(value) + bstack11l1ll1_opy_ (u"ࠤࠥ࿞"))
        return True
    @staticmethod
    def get_data(key: str, target: object, strict=True, default_value=None):
        instance = bstack1111llll1l_opy_.bstack1111llllll_opy_(target, strict)
        return bstack1111llll1l_opy_.bstack111l111111_opy_(instance, key, default_value)
    @staticmethod
    def set_data(key: str, value: Any, target: object, strict=True):
        instance = bstack1111llll1l_opy_.bstack1111llllll_opy_(target, strict)
        if not instance:
            return False
        instance.data[key] = value
        return True