# coding: UTF-8
import sys
bstack1l1l1l_opy_ = sys.version_info [0] == 2
bstack111l111_opy_ = 2048
bstack1lll1l_opy_ = 7
def bstack111l11_opy_ (bstack1ll_opy_):
    global bstack111lll1_opy_
    bstack1l11lll_opy_ = ord (bstack1ll_opy_ [-1])
    bstack111ll1_opy_ = bstack1ll_opy_ [:-1]
    bstack111l11l_opy_ = bstack1l11lll_opy_ % len (bstack111ll1_opy_)
    bstack111l1ll_opy_ = bstack111ll1_opy_ [:bstack111l11l_opy_] + bstack111ll1_opy_ [bstack111l11l_opy_:]
    if bstack1l1l1l_opy_:
        bstack11l1l1_opy_ = unicode () .join ([unichr (ord (char) - bstack111l111_opy_ - (bstack1ll1l_opy_ + bstack1l11lll_opy_) % bstack1lll1l_opy_) for bstack1ll1l_opy_, char in enumerate (bstack111l1ll_opy_)])
    else:
        bstack11l1l1_opy_ = str () .join ([chr (ord (char) - bstack111l111_opy_ - (bstack1ll1l_opy_ + bstack1l11lll_opy_) % bstack1lll1l_opy_) for bstack1ll1l_opy_, char in enumerate (bstack111l1ll_opy_)])
    return eval (bstack11l1l1_opy_)
from _pytest import fixtures
from _pytest.python import _call_with_optional_argument
from pytest import Module, Class
from bstack_utils.helper import Result, bstack1llll111ll1_opy_
from browserstack_sdk.bstack1ll11ll11_opy_ import bstack1lll1ll1_opy_
def _1lll1l11l11_opy_(method, this, arg):
    arg_count = method.__code__.co_argcount
    if arg_count > 1:
        method(this, arg)
    else:
        method(this)
class bstack1lll1ll1111_opy_:
    def __init__(self, handler):
        self._1lll1l111l1_opy_ = {}
        self._1lll1l1llll_opy_ = {}
        self.handler = handler
        self.patch()
        pass
    def patch(self):
        pytest_version = bstack1lll1ll1_opy_.version()
        if bstack1llll111ll1_opy_(pytest_version, bstack111l11_opy_ (u"ࠥ࠼࠳࠷࠮࠲ࠤᖁ")) >= 0:
            self._1lll1l111l1_opy_[bstack111l11_opy_ (u"ࠫ࡫ࡻ࡮ࡤࡶ࡬ࡳࡳࡥࡦࡪࡺࡷࡹࡷ࡫ࠧᖂ")] = Module._register_setup_function_fixture
            self._1lll1l111l1_opy_[bstack111l11_opy_ (u"ࠬࡳ࡯ࡥࡷ࡯ࡩࡤ࡬ࡩࡹࡶࡸࡶࡪ࠭ᖃ")] = Module._register_setup_module_fixture
            self._1lll1l111l1_opy_[bstack111l11_opy_ (u"࠭ࡣ࡭ࡣࡶࡷࡤ࡬ࡩࡹࡶࡸࡶࡪ࠭ᖄ")] = Class._register_setup_class_fixture
            self._1lll1l111l1_opy_[bstack111l11_opy_ (u"ࠧ࡮ࡧࡷ࡬ࡴࡪ࡟ࡧ࡫ࡻࡸࡺࡸࡥࠨᖅ")] = Class._register_setup_method_fixture
            Module._register_setup_function_fixture = self.bstack1lll1l1l1ll_opy_(bstack111l11_opy_ (u"ࠨࡨࡸࡲࡨࡺࡩࡰࡰࡢࡪ࡮ࡾࡴࡶࡴࡨࠫᖆ"))
            Module._register_setup_module_fixture = self.bstack1lll1l1l1ll_opy_(bstack111l11_opy_ (u"ࠩࡰࡳࡩࡻ࡬ࡦࡡࡩ࡭ࡽࡺࡵࡳࡧࠪᖇ"))
            Class._register_setup_class_fixture = self.bstack1lll1l1l1ll_opy_(bstack111l11_opy_ (u"ࠪࡧࡱࡧࡳࡴࡡࡩ࡭ࡽࡺࡵࡳࡧࠪᖈ"))
            Class._register_setup_method_fixture = self.bstack1lll1l1l1ll_opy_(bstack111l11_opy_ (u"ࠫࡲ࡫ࡴࡩࡱࡧࡣ࡫࡯ࡸࡵࡷࡵࡩࠬᖉ"))
        else:
            self._1lll1l111l1_opy_[bstack111l11_opy_ (u"ࠬ࡬ࡵ࡯ࡥࡷ࡭ࡴࡴ࡟ࡧ࡫ࡻࡸࡺࡸࡥࠨᖊ")] = Module._inject_setup_function_fixture
            self._1lll1l111l1_opy_[bstack111l11_opy_ (u"࠭࡭ࡰࡦࡸࡰࡪࡥࡦࡪࡺࡷࡹࡷ࡫ࠧᖋ")] = Module._inject_setup_module_fixture
            self._1lll1l111l1_opy_[bstack111l11_opy_ (u"ࠧࡤ࡮ࡤࡷࡸࡥࡦࡪࡺࡷࡹࡷ࡫ࠧᖌ")] = Class._inject_setup_class_fixture
            self._1lll1l111l1_opy_[bstack111l11_opy_ (u"ࠨ࡯ࡨࡸ࡭ࡵࡤࡠࡨ࡬ࡼࡹࡻࡲࡦࠩᖍ")] = Class._inject_setup_method_fixture
            Module._inject_setup_function_fixture = self.bstack1lll1l1l1ll_opy_(bstack111l11_opy_ (u"ࠩࡩࡹࡳࡩࡴࡪࡱࡱࡣ࡫࡯ࡸࡵࡷࡵࡩࠬᖎ"))
            Module._inject_setup_module_fixture = self.bstack1lll1l1l1ll_opy_(bstack111l11_opy_ (u"ࠪࡱࡴࡪࡵ࡭ࡧࡢࡪ࡮ࡾࡴࡶࡴࡨࠫᖏ"))
            Class._inject_setup_class_fixture = self.bstack1lll1l1l1ll_opy_(bstack111l11_opy_ (u"ࠫࡨࡲࡡࡴࡵࡢࡪ࡮ࡾࡴࡶࡴࡨࠫᖐ"))
            Class._inject_setup_method_fixture = self.bstack1lll1l1l1ll_opy_(bstack111l11_opy_ (u"ࠬࡳࡥࡵࡪࡲࡨࡤ࡬ࡩࡹࡶࡸࡶࡪ࠭ᖑ"))
    def bstack1lll1ll11l1_opy_(self, bstack1lll1l1l11l_opy_, hook_type):
        bstack1lll1ll111l_opy_ = id(bstack1lll1l1l11l_opy_.__class__)
        if (bstack1lll1ll111l_opy_, hook_type) in self._1lll1l1llll_opy_:
            return
        meth = getattr(bstack1lll1l1l11l_opy_, hook_type, None)
        if meth is not None and fixtures.getfixturemarker(meth) is None:
            self._1lll1l1llll_opy_[(bstack1lll1ll111l_opy_, hook_type)] = meth
            setattr(bstack1lll1l1l11l_opy_, hook_type, self.bstack1lll1l11ll1_opy_(hook_type, bstack1lll1ll111l_opy_))
    def bstack1lll1l11l1l_opy_(self, instance, bstack1lll1l1lll1_opy_):
        if bstack1lll1l1lll1_opy_ == bstack111l11_opy_ (u"ࠨࡦࡶࡰࡦࡸ࡮ࡵ࡮ࡠࡨ࡬ࡼࡹࡻࡲࡦࠤᖒ"):
            self.bstack1lll1ll11l1_opy_(instance.obj, bstack111l11_opy_ (u"ࠢࡴࡧࡷࡹࡵࡥࡦࡶࡰࡦࡸ࡮ࡵ࡮ࠣᖓ"))
            self.bstack1lll1ll11l1_opy_(instance.obj, bstack111l11_opy_ (u"ࠣࡶࡨࡥࡷࡪ࡯ࡸࡰࡢࡪࡺࡴࡣࡵ࡫ࡲࡲࠧᖔ"))
        if bstack1lll1l1lll1_opy_ == bstack111l11_opy_ (u"ࠤࡰࡳࡩࡻ࡬ࡦࡡࡩ࡭ࡽࡺࡵࡳࡧࠥᖕ"):
            self.bstack1lll1ll11l1_opy_(instance.obj, bstack111l11_opy_ (u"ࠥࡷࡪࡺࡵࡱࡡࡰࡳࡩࡻ࡬ࡦࠤᖖ"))
            self.bstack1lll1ll11l1_opy_(instance.obj, bstack111l11_opy_ (u"ࠦࡹ࡫ࡡࡳࡦࡲࡻࡳࡥ࡭ࡰࡦࡸࡰࡪࠨᖗ"))
        if bstack1lll1l1lll1_opy_ == bstack111l11_opy_ (u"ࠧࡩ࡬ࡢࡵࡶࡣ࡫࡯ࡸࡵࡷࡵࡩࠧᖘ"):
            self.bstack1lll1ll11l1_opy_(instance.obj, bstack111l11_opy_ (u"ࠨࡳࡦࡶࡸࡴࡤࡩ࡬ࡢࡵࡶࠦᖙ"))
            self.bstack1lll1ll11l1_opy_(instance.obj, bstack111l11_opy_ (u"ࠢࡵࡧࡤࡶࡩࡵࡷ࡯ࡡࡦࡰࡦࡹࡳࠣᖚ"))
        if bstack1lll1l1lll1_opy_ == bstack111l11_opy_ (u"ࠣ࡯ࡨࡸ࡭ࡵࡤࡠࡨ࡬ࡼࡹࡻࡲࡦࠤᖛ"):
            self.bstack1lll1ll11l1_opy_(instance.obj, bstack111l11_opy_ (u"ࠤࡶࡩࡹࡻࡰࡠ࡯ࡨࡸ࡭ࡵࡤࠣᖜ"))
            self.bstack1lll1ll11l1_opy_(instance.obj, bstack111l11_opy_ (u"ࠥࡸࡪࡧࡲࡥࡱࡺࡲࡤࡳࡥࡵࡪࡲࡨࠧᖝ"))
    @staticmethod
    def bstack1lll1l1l1l1_opy_(hook_type, func, args):
        if hook_type in [bstack111l11_opy_ (u"ࠫࡸ࡫ࡴࡶࡲࡢࡱࡪࡺࡨࡰࡦࠪᖞ"), bstack111l11_opy_ (u"ࠬࡺࡥࡢࡴࡧࡳࡼࡴ࡟࡮ࡧࡷ࡬ࡴࡪࠧᖟ")]:
            _1lll1l11l11_opy_(func, args[0], args[1])
            return
        _call_with_optional_argument(func, args[0])
    def bstack1lll1l11ll1_opy_(self, hook_type, bstack1lll1ll111l_opy_):
        def bstack1lll1l111ll_opy_(arg=None):
            self.handler(hook_type, bstack111l11_opy_ (u"࠭ࡢࡦࡨࡲࡶࡪ࠭ᖠ"))
            result = None
            try:
                bstack1lll1l1l111_opy_ = self._1lll1l1llll_opy_[(bstack1lll1ll111l_opy_, hook_type)]
                self.bstack1lll1l1l1l1_opy_(hook_type, bstack1lll1l1l111_opy_, (arg,))
                result = Result(result=bstack111l11_opy_ (u"ࠧࡱࡣࡶࡷࡪࡪࠧᖡ"))
            except Exception as e:
                result = Result(result=bstack111l11_opy_ (u"ࠨࡨࡤ࡭ࡱ࡫ࡤࠨᖢ"), exception=e)
                self.handler(hook_type, bstack111l11_opy_ (u"ࠩࡤࡪࡹ࡫ࡲࠨᖣ"), result)
                raise e.with_traceback(e.__traceback__)
            self.handler(hook_type, bstack111l11_opy_ (u"ࠪࡥ࡫ࡺࡥࡳࠩᖤ"), result)
        def bstack1lll1l1ll1l_opy_(this, arg=None):
            self.handler(hook_type, bstack111l11_opy_ (u"ࠫࡧ࡫ࡦࡰࡴࡨࠫᖥ"))
            result = None
            exception = None
            try:
                self.bstack1lll1l1l1l1_opy_(hook_type, self._1lll1l1llll_opy_[hook_type], (this, arg))
                result = Result(result=bstack111l11_opy_ (u"ࠬࡶࡡࡴࡵࡨࡨࠬᖦ"))
            except Exception as e:
                result = Result(result=bstack111l11_opy_ (u"࠭ࡦࡢ࡫࡯ࡩࡩ࠭ᖧ"), exception=e)
                self.handler(hook_type, bstack111l11_opy_ (u"ࠧࡢࡨࡷࡩࡷ࠭ᖨ"), result)
                raise e.with_traceback(e.__traceback__)
            self.handler(hook_type, bstack111l11_opy_ (u"ࠨࡣࡩࡸࡪࡸࠧᖩ"), result)
        if hook_type in [bstack111l11_opy_ (u"ࠩࡶࡩࡹࡻࡰࡠ࡯ࡨࡸ࡭ࡵࡤࠨᖪ"), bstack111l11_opy_ (u"ࠪࡸࡪࡧࡲࡥࡱࡺࡲࡤࡳࡥࡵࡪࡲࡨࠬᖫ")]:
            return bstack1lll1l1ll1l_opy_
        return bstack1lll1l111ll_opy_
    def bstack1lll1l1l1ll_opy_(self, bstack1lll1l1lll1_opy_):
        def bstack1lll1l1ll11_opy_(this, *args, **kwargs):
            self.bstack1lll1l11l1l_opy_(this, bstack1lll1l1lll1_opy_)
            self._1lll1l111l1_opy_[bstack1lll1l1lll1_opy_](this, *args, **kwargs)
        return bstack1lll1l1ll11_opy_