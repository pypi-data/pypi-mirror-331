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
from _pytest import fixtures
from _pytest.python import _call_with_optional_argument
from pytest import Module, Class
from bstack_utils.helper import Result, bstack11lll1l1lll_opy_
from browserstack_sdk.bstack11lll111l_opy_ import bstack11l111lll_opy_
def _11lll111l1l_opy_(method, this, arg):
    arg_count = method.__code__.co_argcount
    if arg_count > 1:
        method(this, arg)
    else:
        method(this)
class bstack11lll11111l_opy_:
    def __init__(self, handler):
        self._11lll1111ll_opy_ = {}
        self._11lll11l111_opy_ = {}
        self.handler = handler
        self.patch()
        pass
    def patch(self):
        pytest_version = bstack11l111lll_opy_.version()
        if bstack11lll1l1lll_opy_(pytest_version, bstack11l1ll1_opy_ (u"ࠢ࠹࠰࠴࠲࠶ࠨᨲ")) >= 0:
            self._11lll1111ll_opy_[bstack11l1ll1_opy_ (u"ࠨࡨࡸࡲࡨࡺࡩࡰࡰࡢࡪ࡮ࡾࡴࡶࡴࡨࠫᨳ")] = Module._register_setup_function_fixture
            self._11lll1111ll_opy_[bstack11l1ll1_opy_ (u"ࠩࡰࡳࡩࡻ࡬ࡦࡡࡩ࡭ࡽࡺࡵࡳࡧࠪᨴ")] = Module._register_setup_module_fixture
            self._11lll1111ll_opy_[bstack11l1ll1_opy_ (u"ࠪࡧࡱࡧࡳࡴࡡࡩ࡭ࡽࡺࡵࡳࡧࠪᨵ")] = Class._register_setup_class_fixture
            self._11lll1111ll_opy_[bstack11l1ll1_opy_ (u"ࠫࡲ࡫ࡴࡩࡱࡧࡣ࡫࡯ࡸࡵࡷࡵࡩࠬᨶ")] = Class._register_setup_method_fixture
            Module._register_setup_function_fixture = self.bstack11lll11ll11_opy_(bstack11l1ll1_opy_ (u"ࠬ࡬ࡵ࡯ࡥࡷ࡭ࡴࡴ࡟ࡧ࡫ࡻࡸࡺࡸࡥࠨᨷ"))
            Module._register_setup_module_fixture = self.bstack11lll11ll11_opy_(bstack11l1ll1_opy_ (u"࠭࡭ࡰࡦࡸࡰࡪࡥࡦࡪࡺࡷࡹࡷ࡫ࠧᨸ"))
            Class._register_setup_class_fixture = self.bstack11lll11ll11_opy_(bstack11l1ll1_opy_ (u"ࠧࡤ࡮ࡤࡷࡸࡥࡦࡪࡺࡷࡹࡷ࡫ࠧᨹ"))
            Class._register_setup_method_fixture = self.bstack11lll11ll11_opy_(bstack11l1ll1_opy_ (u"ࠨ࡯ࡨࡸ࡭ࡵࡤࡠࡨ࡬ࡼࡹࡻࡲࡦࠩᨺ"))
        else:
            self._11lll1111ll_opy_[bstack11l1ll1_opy_ (u"ࠩࡩࡹࡳࡩࡴࡪࡱࡱࡣ࡫࡯ࡸࡵࡷࡵࡩࠬᨻ")] = Module._inject_setup_function_fixture
            self._11lll1111ll_opy_[bstack11l1ll1_opy_ (u"ࠪࡱࡴࡪࡵ࡭ࡧࡢࡪ࡮ࡾࡴࡶࡴࡨࠫᨼ")] = Module._inject_setup_module_fixture
            self._11lll1111ll_opy_[bstack11l1ll1_opy_ (u"ࠫࡨࡲࡡࡴࡵࡢࡪ࡮ࡾࡴࡶࡴࡨࠫᨽ")] = Class._inject_setup_class_fixture
            self._11lll1111ll_opy_[bstack11l1ll1_opy_ (u"ࠬࡳࡥࡵࡪࡲࡨࡤ࡬ࡩࡹࡶࡸࡶࡪ࠭ᨾ")] = Class._inject_setup_method_fixture
            Module._inject_setup_function_fixture = self.bstack11lll11ll11_opy_(bstack11l1ll1_opy_ (u"࠭ࡦࡶࡰࡦࡸ࡮ࡵ࡮ࡠࡨ࡬ࡼࡹࡻࡲࡦࠩᨿ"))
            Module._inject_setup_module_fixture = self.bstack11lll11ll11_opy_(bstack11l1ll1_opy_ (u"ࠧ࡮ࡱࡧࡹࡱ࡫࡟ࡧ࡫ࡻࡸࡺࡸࡥࠨᩀ"))
            Class._inject_setup_class_fixture = self.bstack11lll11ll11_opy_(bstack11l1ll1_opy_ (u"ࠨࡥ࡯ࡥࡸࡹ࡟ࡧ࡫ࡻࡸࡺࡸࡥࠨᩁ"))
            Class._inject_setup_method_fixture = self.bstack11lll11ll11_opy_(bstack11l1ll1_opy_ (u"ࠩࡰࡩࡹ࡮࡯ࡥࡡࡩ࡭ࡽࡺࡵࡳࡧࠪᩂ"))
    def bstack11ll1lllll1_opy_(self, bstack11lll111l11_opy_, hook_type):
        bstack11ll1llll1l_opy_ = id(bstack11lll111l11_opy_.__class__)
        if (bstack11ll1llll1l_opy_, hook_type) in self._11lll11l111_opy_:
            return
        meth = getattr(bstack11lll111l11_opy_, hook_type, None)
        if meth is not None and fixtures.getfixturemarker(meth) is None:
            self._11lll11l111_opy_[(bstack11ll1llll1l_opy_, hook_type)] = meth
            setattr(bstack11lll111l11_opy_, hook_type, self.bstack11ll1llllll_opy_(hook_type, bstack11ll1llll1l_opy_))
    def bstack11lll111111_opy_(self, instance, bstack11lll11l11l_opy_):
        if bstack11lll11l11l_opy_ == bstack11l1ll1_opy_ (u"ࠥࡪࡺࡴࡣࡵ࡫ࡲࡲࡤ࡬ࡩࡹࡶࡸࡶࡪࠨᩃ"):
            self.bstack11ll1lllll1_opy_(instance.obj, bstack11l1ll1_opy_ (u"ࠦࡸ࡫ࡴࡶࡲࡢࡪࡺࡴࡣࡵ࡫ࡲࡲࠧᩄ"))
            self.bstack11ll1lllll1_opy_(instance.obj, bstack11l1ll1_opy_ (u"ࠧࡺࡥࡢࡴࡧࡳࡼࡴ࡟ࡧࡷࡱࡧࡹ࡯࡯࡯ࠤᩅ"))
        if bstack11lll11l11l_opy_ == bstack11l1ll1_opy_ (u"ࠨ࡭ࡰࡦࡸࡰࡪࡥࡦࡪࡺࡷࡹࡷ࡫ࠢᩆ"):
            self.bstack11ll1lllll1_opy_(instance.obj, bstack11l1ll1_opy_ (u"ࠢࡴࡧࡷࡹࡵࡥ࡭ࡰࡦࡸࡰࡪࠨᩇ"))
            self.bstack11ll1lllll1_opy_(instance.obj, bstack11l1ll1_opy_ (u"ࠣࡶࡨࡥࡷࡪ࡯ࡸࡰࡢࡱࡴࡪࡵ࡭ࡧࠥᩈ"))
        if bstack11lll11l11l_opy_ == bstack11l1ll1_opy_ (u"ࠤࡦࡰࡦࡹࡳࡠࡨ࡬ࡼࡹࡻࡲࡦࠤᩉ"):
            self.bstack11ll1lllll1_opy_(instance.obj, bstack11l1ll1_opy_ (u"ࠥࡷࡪࡺࡵࡱࡡࡦࡰࡦࡹࡳࠣᩊ"))
            self.bstack11ll1lllll1_opy_(instance.obj, bstack11l1ll1_opy_ (u"ࠦࡹ࡫ࡡࡳࡦࡲࡻࡳࡥࡣ࡭ࡣࡶࡷࠧᩋ"))
        if bstack11lll11l11l_opy_ == bstack11l1ll1_opy_ (u"ࠧࡳࡥࡵࡪࡲࡨࡤ࡬ࡩࡹࡶࡸࡶࡪࠨᩌ"):
            self.bstack11ll1lllll1_opy_(instance.obj, bstack11l1ll1_opy_ (u"ࠨࡳࡦࡶࡸࡴࡤࡳࡥࡵࡪࡲࡨࠧᩍ"))
            self.bstack11ll1lllll1_opy_(instance.obj, bstack11l1ll1_opy_ (u"ࠢࡵࡧࡤࡶࡩࡵࡷ࡯ࡡࡰࡩࡹ࡮࡯ࡥࠤᩎ"))
    @staticmethod
    def bstack11lll111lll_opy_(hook_type, func, args):
        if hook_type in [bstack11l1ll1_opy_ (u"ࠨࡵࡨࡸࡺࡶ࡟࡮ࡧࡷ࡬ࡴࡪࠧᩏ"), bstack11l1ll1_opy_ (u"ࠩࡷࡩࡦࡸࡤࡰࡹࡱࡣࡲ࡫ࡴࡩࡱࡧࠫᩐ")]:
            _11lll111l1l_opy_(func, args[0], args[1])
            return
        _call_with_optional_argument(func, args[0])
    def bstack11ll1llllll_opy_(self, hook_type, bstack11ll1llll1l_opy_):
        def bstack11lll11l1l1_opy_(arg=None):
            self.handler(hook_type, bstack11l1ll1_opy_ (u"ࠪࡦࡪ࡬࡯ࡳࡧࠪᩑ"))
            result = None
            try:
                bstack1111ll11l1_opy_ = self._11lll11l111_opy_[(bstack11ll1llll1l_opy_, hook_type)]
                self.bstack11lll111lll_opy_(hook_type, bstack1111ll11l1_opy_, (arg,))
                result = Result(result=bstack11l1ll1_opy_ (u"ࠫࡵࡧࡳࡴࡧࡧࠫᩒ"))
            except Exception as e:
                result = Result(result=bstack11l1ll1_opy_ (u"ࠬ࡬ࡡࡪ࡮ࡨࡨࠬᩓ"), exception=e)
                self.handler(hook_type, bstack11l1ll1_opy_ (u"࠭ࡡࡧࡶࡨࡶࠬᩔ"), result)
                raise e.with_traceback(e.__traceback__)
            self.handler(hook_type, bstack11l1ll1_opy_ (u"ࠧࡢࡨࡷࡩࡷ࠭ᩕ"), result)
        def bstack11lll11l1ll_opy_(this, arg=None):
            self.handler(hook_type, bstack11l1ll1_opy_ (u"ࠨࡤࡨࡪࡴࡸࡥࠨᩖ"))
            result = None
            exception = None
            try:
                self.bstack11lll111lll_opy_(hook_type, self._11lll11l111_opy_[hook_type], (this, arg))
                result = Result(result=bstack11l1ll1_opy_ (u"ࠩࡳࡥࡸࡹࡥࡥࠩᩗ"))
            except Exception as e:
                result = Result(result=bstack11l1ll1_opy_ (u"ࠪࡪࡦ࡯࡬ࡦࡦࠪᩘ"), exception=e)
                self.handler(hook_type, bstack11l1ll1_opy_ (u"ࠫࡦ࡬ࡴࡦࡴࠪᩙ"), result)
                raise e.with_traceback(e.__traceback__)
            self.handler(hook_type, bstack11l1ll1_opy_ (u"ࠬࡧࡦࡵࡧࡵࠫᩚ"), result)
        if hook_type in [bstack11l1ll1_opy_ (u"࠭ࡳࡦࡶࡸࡴࡤࡳࡥࡵࡪࡲࡨࠬᩛ"), bstack11l1ll1_opy_ (u"ࠧࡵࡧࡤࡶࡩࡵࡷ࡯ࡡࡰࡩࡹ࡮࡯ࡥࠩᩜ")]:
            return bstack11lll11l1ll_opy_
        return bstack11lll11l1l1_opy_
    def bstack11lll11ll11_opy_(self, bstack11lll11l11l_opy_):
        def bstack11lll111ll1_opy_(this, *args, **kwargs):
            self.bstack11lll111111_opy_(this, bstack11lll11l11l_opy_)
            self._11lll1111ll_opy_[bstack11lll11l11l_opy_](this, *args, **kwargs)
        return bstack11lll111ll1_opy_