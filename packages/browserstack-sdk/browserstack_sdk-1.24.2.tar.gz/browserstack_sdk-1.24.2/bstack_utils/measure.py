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
from functools import wraps
from typing import Optional
from bstack_utils.constants import EVENTS, STAGE
from bstack_utils.bstack1ll1ll111_opy_ import get_logger
from bstack_utils.bstack1ll111ll1l_opy_ import bstack1llll111lll_opy_
bstack1ll111ll1l_opy_ = bstack1llll111lll_opy_()
logger = get_logger(__name__)
def measure(event_name: EVENTS, stage: STAGE, hook_type: Optional[str] = None, bstack1l11l1ll_opy_: Optional[str] = None):
    bstack11l1ll1_opy_ (u"ࠤࠥࠦࠏࠦࠠࠡࠢࡇࡩࡨࡵࡲࡢࡶࡲࡶࠥࡺ࡯ࠡ࡮ࡲ࡫ࠥࡺࡨࡦࠢࡶࡸࡦࡸࡴࠡࡶ࡬ࡱࡪࠦ࡯ࡧࠢࡤࠤ࡫ࡻ࡮ࡤࡶ࡬ࡳࡳࠦࡥࡹࡧࡦࡹࡹ࡯࡯࡯ࠌࠣࠤࠥࠦࡡ࡭ࡱࡱ࡫ࠥࡽࡩࡵࡪࠣࡩࡻ࡫࡮ࡵࠢࡱࡥࡲ࡫ࠠࡢࡰࡧࠤࡸࡺࡡࡨࡧ࠱ࠎࠥࠦࠠࠡࠤࠥࠦ᪝")
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            label: str = event_name.value
            bstack1lll11l1l1l_opy_: str = bstack1ll111ll1l_opy_.bstack1l11ll1l1ll_opy_(label)
            start_mark: str = label + bstack11l1ll1_opy_ (u"ࠥ࠾ࡸࡺࡡࡳࡶࠥ᪞")
            end_mark: str = label + bstack11l1ll1_opy_ (u"ࠦ࠿࡫࡮ࡥࠤ᪟")
            result = None
            try:
                if stage.value == STAGE.bstack11111l1l_opy_.value:
                    bstack1ll111ll1l_opy_.mark(start_mark)
                    result = func(*args, **kwargs)
                elif stage.value == STAGE.END.value:
                    result = func(*args, **kwargs)
                    bstack1ll111ll1l_opy_.end(label, start_mark, end_mark, status=True, failure=None,hook_type=hook_type,test_name=bstack1l11l1ll_opy_)
                elif stage.value == STAGE.bstack1l1ll1llll_opy_.value:
                    start_mark: str = bstack1lll11l1l1l_opy_ + bstack11l1ll1_opy_ (u"ࠧࡀࡳࡵࡣࡵࡸࠧ᪠")
                    end_mark: str = bstack1lll11l1l1l_opy_ + bstack11l1ll1_opy_ (u"ࠨ࠺ࡦࡰࡧࠦ᪡")
                    bstack1ll111ll1l_opy_.mark(start_mark)
                    result = func(*args, **kwargs)
                    bstack1ll111ll1l_opy_.end(label, start_mark, end_mark, status=True, failure=None, hook_type=hook_type,test_name=bstack1l11l1ll_opy_)
            except Exception as e:
                bstack1ll111ll1l_opy_.end(label, start_mark, end_mark, status=False, failure=str(e), hook_type=hook_type,
                                       test_name=bstack1l11l1ll_opy_)
            return result
        return wrapper
    return decorator