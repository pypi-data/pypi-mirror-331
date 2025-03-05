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
import logging
from functools import wraps
from typing import Optional
from bstack_utils.constants import EVENTS, STAGE
from bstack_utils.bstack1lll1ll1ll_opy_ import get_logger
from bstack_utils.bstack1lll1llll1_opy_ import bstack111l1l11l1_opy_
bstack1lll1llll1_opy_ = bstack111l1l11l1_opy_()
logger = get_logger(__name__)
def measure(event_name: EVENTS, stage: STAGE, hook_type: Optional[str] = None, bstack11lllll11_opy_: Optional[str] = None):
    bstack111l11_opy_ (u"ࠨࠢࠣࠌࠣࠤࠥࠦࡄࡦࡥࡲࡶࡦࡺ࡯ࡳࠢࡷࡳࠥࡲ࡯ࡨࠢࡷ࡬ࡪࠦࡳࡵࡣࡵࡸࠥࡺࡩ࡮ࡧࠣࡳ࡫ࠦࡡࠡࡨࡸࡲࡨࡺࡩࡰࡰࠣࡩࡽ࡫ࡣࡶࡶ࡬ࡳࡳࠐࠠࠡࠢࠣࡥࡱࡵ࡮ࡨࠢࡺ࡭ࡹ࡮ࠠࡦࡸࡨࡲࡹࠦ࡮ࡢ࡯ࡨࠤࡦࡴࡤࠡࡵࡷࡥ࡬࡫࠮ࠋࠢࠣࠤࠥࠨࠢࠣᗦ")
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            label: str = event_name.value
            bstack1111lll1ll_opy_: str = bstack1lll1llll1_opy_.bstack111l1ll111_opy_(label)
            start_mark: str = label + bstack111l11_opy_ (u"ࠢ࠻ࡵࡷࡥࡷࡺࠢᗧ")
            end_mark: str = label + bstack111l11_opy_ (u"ࠣ࠼ࡨࡲࡩࠨᗨ")
            result = None
            try:
                if stage.value == STAGE.bstack1llll111l1_opy_.value:
                    bstack1lll1llll1_opy_.mark(start_mark)
                    result = func(*args, **kwargs)
                elif stage.value == STAGE.END.value:
                    result = func(*args, **kwargs)
                    bstack1lll1llll1_opy_.end(label, start_mark, end_mark, status=True, failure=None,hook_type=hook_type,test_name=bstack11lllll11_opy_)
                elif stage.value == STAGE.SINGLE.value:
                    start_mark: str = bstack1111lll1ll_opy_ + bstack111l11_opy_ (u"ࠤ࠽ࡷࡹࡧࡲࡵࠤᗩ")
                    end_mark: str = bstack1111lll1ll_opy_ + bstack111l11_opy_ (u"ࠥ࠾ࡪࡴࡤࠣᗪ")
                    bstack1lll1llll1_opy_.mark(start_mark)
                    result = func(*args, **kwargs)
                    bstack1lll1llll1_opy_.end(label, start_mark, end_mark, status=True, failure=None, hook_type=hook_type,test_name=bstack11lllll11_opy_)
            except Exception as e:
                bstack1lll1llll1_opy_.end(label, start_mark, end_mark, status=False, failure=str(e), hook_type=hook_type,
                                       test_name=bstack11lllll11_opy_)
            return result
        return wrapper
    return decorator