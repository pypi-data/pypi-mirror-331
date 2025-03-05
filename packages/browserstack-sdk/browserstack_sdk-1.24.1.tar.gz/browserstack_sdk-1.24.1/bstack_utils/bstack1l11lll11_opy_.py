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
from browserstack_sdk.bstack1ll11ll11_opy_ import bstack1lll1ll1_opy_
from browserstack_sdk.bstack11l11lllll_opy_ import RobotHandler
def bstack1l1lll1lll_opy_(framework):
    if framework.lower() == bstack111l11_opy_ (u"ࠧࡱࡻࡷࡩࡸࡺࠧ᎛"):
        return bstack1lll1ll1_opy_.version()
    elif framework.lower() == bstack111l11_opy_ (u"ࠨࡴࡲࡦࡴࡺࠧ᎜"):
        return RobotHandler.version()
    elif framework.lower() == bstack111l11_opy_ (u"ࠩࡥࡩ࡭ࡧࡶࡦࠩ᎝"):
        import behave
        return behave.__version__
    else:
        return bstack111l11_opy_ (u"ࠪࡹࡳࡱ࡮ࡰࡹࡱࠫ᎞")
def bstack1ll11lll1_opy_():
    import importlib.metadata
    framework_name = []
    bstack111111l11l_opy_ = []
    try:
        from selenium import webdriver
        framework_name.append(bstack111l11_opy_ (u"ࠫࡸ࡫࡬ࡦࡰ࡬ࡹࡲ࠭᎟"))
        bstack111111l11l_opy_.append(importlib.metadata.version(bstack111l11_opy_ (u"ࠧࡹࡥ࡭ࡧࡱ࡭ࡺࡳࠢᎠ")))
    except:
        pass
    try:
        import playwright
        framework_name.append(bstack111l11_opy_ (u"࠭ࡰ࡭ࡣࡼࡻࡷ࡯ࡧࡩࡶࠪᎡ"))
        bstack111111l11l_opy_.append(importlib.metadata.version(bstack111l11_opy_ (u"ࠢࡱ࡮ࡤࡽࡼࡸࡩࡨࡪࡷࠦᎢ")))
    except:
        pass
    return {
        bstack111l11_opy_ (u"ࠨࡰࡤࡱࡪ࠭Ꭳ"): bstack111l11_opy_ (u"ࠩࡢࠫᎤ").join(framework_name),
        bstack111l11_opy_ (u"ࠪࡺࡪࡸࡳࡪࡱࡱࠫᎥ"): bstack111l11_opy_ (u"ࠫࡤ࠭Ꭶ").join(bstack111111l11l_opy_)
    }