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
import os
from urllib.parse import urlparse
from bstack_utils.config import Config
from bstack_utils.messages import bstack1lll111l11l_opy_
bstack1l1ll11l1l_opy_ = Config.bstack1l1l11111l_opy_()
def bstack1ll11lll111_opy_(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False
def bstack1ll11lll11l_opy_(bstack1ll11lllll1_opy_, bstack1ll11lll1ll_opy_):
    from pypac import get_pac
    from pypac import PACSession
    from pypac.parser import PACFile
    import socket
    if os.path.isfile(bstack1ll11lllll1_opy_):
        with open(bstack1ll11lllll1_opy_) as f:
            pac = PACFile(f.read())
    elif bstack1ll11lll111_opy_(bstack1ll11lllll1_opy_):
        pac = get_pac(url=bstack1ll11lllll1_opy_)
    else:
        raise Exception(bstack111l11_opy_ (u"ࠪࡔࡦࡩࠠࡧ࡫࡯ࡩࠥࡪ࡯ࡦࡵࠣࡲࡴࡺࠠࡦࡺ࡬ࡷࡹࡀࠠࡼࡿࠪᚵ").format(bstack1ll11lllll1_opy_))
    session = PACSession(pac)
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect((bstack111l11_opy_ (u"ࠦ࠽࠴࠸࠯࠺࠱࠼ࠧᚶ"), 80))
        bstack1ll11lll1l1_opy_ = s.getsockname()[0]
        s.close()
    except:
        bstack1ll11lll1l1_opy_ = bstack111l11_opy_ (u"ࠬ࠶࠮࠱࠰࠳࠲࠵࠭ᚷ")
    proxy_url = session.get_pac().find_proxy_for_url(bstack1ll11lll1ll_opy_, bstack1ll11lll1l1_opy_)
    return proxy_url
def bstack1111ll11_opy_(config):
    return bstack111l11_opy_ (u"࠭ࡨࡵࡶࡳࡔࡷࡵࡸࡺࠩᚸ") in config or bstack111l11_opy_ (u"ࠧࡩࡶࡷࡴࡸࡖࡲࡰࡺࡼࠫᚹ") in config
def bstack1ll11lll1l_opy_(config):
    if not bstack1111ll11_opy_(config):
        return
    if config.get(bstack111l11_opy_ (u"ࠨࡪࡷࡸࡵࡖࡲࡰࡺࡼࠫᚺ")):
        return config.get(bstack111l11_opy_ (u"ࠩ࡫ࡸࡹࡶࡐࡳࡱࡻࡽࠬᚻ"))
    if config.get(bstack111l11_opy_ (u"ࠪ࡬ࡹࡺࡰࡴࡒࡵࡳࡽࡿࠧᚼ")):
        return config.get(bstack111l11_opy_ (u"ࠫ࡭ࡺࡴࡱࡵࡓࡶࡴࡾࡹࠨᚽ"))
def bstack1l11l111l_opy_(config, bstack1ll11lll1ll_opy_):
    proxy = bstack1ll11lll1l_opy_(config)
    proxies = {}
    if config.get(bstack111l11_opy_ (u"ࠬ࡮ࡴࡵࡲࡓࡶࡴࡾࡹࠨᚾ")) or config.get(bstack111l11_opy_ (u"࠭ࡨࡵࡶࡳࡷࡕࡸ࡯ࡹࡻࠪᚿ")):
        if proxy.endswith(bstack111l11_opy_ (u"ࠧ࠯ࡲࡤࡧࠬᛀ")):
            proxies = bstack11l1l11l_opy_(proxy, bstack1ll11lll1ll_opy_)
        else:
            proxies = {
                bstack111l11_opy_ (u"ࠨࡪࡷࡸࡵࡹࠧᛁ"): proxy
            }
    bstack1l1ll11l1l_opy_.bstack11lll11l1l_opy_(bstack111l11_opy_ (u"ࠩࡳࡶࡴࡾࡹࡔࡧࡷࡸ࡮ࡴࡧࡴࠩᛂ"), proxies)
    return proxies
def bstack11l1l11l_opy_(bstack1ll11lllll1_opy_, bstack1ll11lll1ll_opy_):
    proxies = {}
    global bstack1ll11llll1l_opy_
    if bstack111l11_opy_ (u"ࠪࡔࡆࡉ࡟ࡑࡔࡒ࡜࡞࠭ᛃ") in globals():
        return bstack1ll11llll1l_opy_
    try:
        proxy = bstack1ll11lll11l_opy_(bstack1ll11lllll1_opy_, bstack1ll11lll1ll_opy_)
        if bstack111l11_opy_ (u"ࠦࡉࡏࡒࡆࡅࡗࠦᛄ") in proxy:
            proxies = {}
        elif bstack111l11_opy_ (u"ࠧࡎࡔࡕࡒࠥᛅ") in proxy or bstack111l11_opy_ (u"ࠨࡈࡕࡖࡓࡗࠧᛆ") in proxy or bstack111l11_opy_ (u"ࠢࡔࡑࡆࡏࡘࠨᛇ") in proxy:
            bstack1ll11llll11_opy_ = proxy.split(bstack111l11_opy_ (u"ࠣࠢࠥᛈ"))
            if bstack111l11_opy_ (u"ࠤ࠽࠳࠴ࠨᛉ") in bstack111l11_opy_ (u"ࠥࠦᛊ").join(bstack1ll11llll11_opy_[1:]):
                proxies = {
                    bstack111l11_opy_ (u"ࠫ࡭ࡺࡴࡱࡵࠪᛋ"): bstack111l11_opy_ (u"ࠧࠨᛌ").join(bstack1ll11llll11_opy_[1:])
                }
            else:
                proxies = {
                    bstack111l11_opy_ (u"࠭ࡨࡵࡶࡳࡷࠬᛍ"): str(bstack1ll11llll11_opy_[0]).lower() + bstack111l11_opy_ (u"ࠢ࠻࠱࠲ࠦᛎ") + bstack111l11_opy_ (u"ࠣࠤᛏ").join(bstack1ll11llll11_opy_[1:])
                }
        elif bstack111l11_opy_ (u"ࠤࡓࡖࡔ࡞࡙ࠣᛐ") in proxy:
            bstack1ll11llll11_opy_ = proxy.split(bstack111l11_opy_ (u"ࠥࠤࠧᛑ"))
            if bstack111l11_opy_ (u"ࠦ࠿࠵࠯ࠣᛒ") in bstack111l11_opy_ (u"ࠧࠨᛓ").join(bstack1ll11llll11_opy_[1:]):
                proxies = {
                    bstack111l11_opy_ (u"࠭ࡨࡵࡶࡳࡷࠬᛔ"): bstack111l11_opy_ (u"ࠢࠣᛕ").join(bstack1ll11llll11_opy_[1:])
                }
            else:
                proxies = {
                    bstack111l11_opy_ (u"ࠨࡪࡷࡸࡵࡹࠧᛖ"): bstack111l11_opy_ (u"ࠤ࡫ࡸࡹࡶ࠺࠰࠱ࠥᛗ") + bstack111l11_opy_ (u"ࠥࠦᛘ").join(bstack1ll11llll11_opy_[1:])
                }
        else:
            proxies = {
                bstack111l11_opy_ (u"ࠫ࡭ࡺࡴࡱࡵࠪᛙ"): proxy
            }
    except Exception as e:
        print(bstack111l11_opy_ (u"ࠧࡹ࡯࡮ࡧࠣࡩࡷࡸ࡯ࡳࠤᛚ"), bstack1lll111l11l_opy_.format(bstack1ll11lllll1_opy_, str(e)))
    bstack1ll11llll1l_opy_ = proxies
    return proxies