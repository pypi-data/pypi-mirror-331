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
from urllib.parse import urlparse
from bstack_utils.config import Config
from bstack_utils.messages import bstack11ll1l11l1l_opy_
bstack1ll1l11l1_opy_ = Config.bstack1l111l1ll1_opy_()
def bstack11l1l1l11ll_opy_(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False
def bstack11l1l1l111l_opy_(bstack11l1l11llll_opy_, bstack11l1l11lll1_opy_):
    from pypac import get_pac
    from pypac import PACSession
    from pypac.parser import PACFile
    import socket
    if os.path.isfile(bstack11l1l11llll_opy_):
        with open(bstack11l1l11llll_opy_) as f:
            pac = PACFile(f.read())
    elif bstack11l1l1l11ll_opy_(bstack11l1l11llll_opy_):
        pac = get_pac(url=bstack11l1l11llll_opy_)
    else:
        raise Exception(bstack11l1ll1_opy_ (u"ࠪࡔࡦࡩࠠࡧ࡫࡯ࡩࠥࡪ࡯ࡦࡵࠣࡲࡴࡺࠠࡦࡺ࡬ࡷࡹࡀࠠࡼࡿࠪ᭷").format(bstack11l1l11llll_opy_))
    session = PACSession(pac)
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect((bstack11l1ll1_opy_ (u"ࠦ࠽࠴࠸࠯࠺࠱࠼ࠧ᭸"), 80))
        bstack11l1l1l1l11_opy_ = s.getsockname()[0]
        s.close()
    except:
        bstack11l1l1l1l11_opy_ = bstack11l1ll1_opy_ (u"ࠬ࠶࠮࠱࠰࠳࠲࠵࠭᭹")
    proxy_url = session.get_pac().find_proxy_for_url(bstack11l1l11lll1_opy_, bstack11l1l1l1l11_opy_)
    return proxy_url
def bstack1lll11lll1_opy_(config):
    return bstack11l1ll1_opy_ (u"࠭ࡨࡵࡶࡳࡔࡷࡵࡸࡺࠩ᭺") in config or bstack11l1ll1_opy_ (u"ࠧࡩࡶࡷࡴࡸࡖࡲࡰࡺࡼࠫ᭻") in config
def bstack1l1ll1lll1_opy_(config):
    if not bstack1lll11lll1_opy_(config):
        return
    if config.get(bstack11l1ll1_opy_ (u"ࠨࡪࡷࡸࡵࡖࡲࡰࡺࡼࠫ᭼")):
        return config.get(bstack11l1ll1_opy_ (u"ࠩ࡫ࡸࡹࡶࡐࡳࡱࡻࡽࠬ᭽"))
    if config.get(bstack11l1ll1_opy_ (u"ࠪ࡬ࡹࡺࡰࡴࡒࡵࡳࡽࡿࠧ᭾")):
        return config.get(bstack11l1ll1_opy_ (u"ࠫ࡭ࡺࡴࡱࡵࡓࡶࡴࡾࡹࠨ᭿"))
def bstack1l11l1l1_opy_(config, bstack11l1l11lll1_opy_):
    proxy = bstack1l1ll1lll1_opy_(config)
    proxies = {}
    if config.get(bstack11l1ll1_opy_ (u"ࠬ࡮ࡴࡵࡲࡓࡶࡴࡾࡹࠨᮀ")) or config.get(bstack11l1ll1_opy_ (u"࠭ࡨࡵࡶࡳࡷࡕࡸ࡯ࡹࡻࠪᮁ")):
        if proxy.endswith(bstack11l1ll1_opy_ (u"ࠧ࠯ࡲࡤࡧࠬᮂ")):
            proxies = bstack111l111ll_opy_(proxy, bstack11l1l11lll1_opy_)
        else:
            proxies = {
                bstack11l1ll1_opy_ (u"ࠨࡪࡷࡸࡵࡹࠧᮃ"): proxy
            }
    bstack1ll1l11l1_opy_.bstack1l111llll1_opy_(bstack11l1ll1_opy_ (u"ࠩࡳࡶࡴࡾࡹࡔࡧࡷࡸ࡮ࡴࡧࡴࠩᮄ"), proxies)
    return proxies
def bstack111l111ll_opy_(bstack11l1l11llll_opy_, bstack11l1l11lll1_opy_):
    proxies = {}
    global bstack11l1l1l1111_opy_
    if bstack11l1ll1_opy_ (u"ࠪࡔࡆࡉ࡟ࡑࡔࡒ࡜࡞࠭ᮅ") in globals():
        return bstack11l1l1l1111_opy_
    try:
        proxy = bstack11l1l1l111l_opy_(bstack11l1l11llll_opy_, bstack11l1l11lll1_opy_)
        if bstack11l1ll1_opy_ (u"ࠦࡉࡏࡒࡆࡅࡗࠦᮆ") in proxy:
            proxies = {}
        elif bstack11l1ll1_opy_ (u"ࠧࡎࡔࡕࡒࠥᮇ") in proxy or bstack11l1ll1_opy_ (u"ࠨࡈࡕࡖࡓࡗࠧᮈ") in proxy or bstack11l1ll1_opy_ (u"ࠢࡔࡑࡆࡏࡘࠨᮉ") in proxy:
            bstack11l1l1l11l1_opy_ = proxy.split(bstack11l1ll1_opy_ (u"ࠣࠢࠥᮊ"))
            if bstack11l1ll1_opy_ (u"ࠤ࠽࠳࠴ࠨᮋ") in bstack11l1ll1_opy_ (u"ࠥࠦᮌ").join(bstack11l1l1l11l1_opy_[1:]):
                proxies = {
                    bstack11l1ll1_opy_ (u"ࠫ࡭ࡺࡴࡱࡵࠪᮍ"): bstack11l1ll1_opy_ (u"ࠧࠨᮎ").join(bstack11l1l1l11l1_opy_[1:])
                }
            else:
                proxies = {
                    bstack11l1ll1_opy_ (u"࠭ࡨࡵࡶࡳࡷࠬᮏ"): str(bstack11l1l1l11l1_opy_[0]).lower() + bstack11l1ll1_opy_ (u"ࠢ࠻࠱࠲ࠦᮐ") + bstack11l1ll1_opy_ (u"ࠣࠤᮑ").join(bstack11l1l1l11l1_opy_[1:])
                }
        elif bstack11l1ll1_opy_ (u"ࠤࡓࡖࡔ࡞࡙ࠣᮒ") in proxy:
            bstack11l1l1l11l1_opy_ = proxy.split(bstack11l1ll1_opy_ (u"ࠥࠤࠧᮓ"))
            if bstack11l1ll1_opy_ (u"ࠦ࠿࠵࠯ࠣᮔ") in bstack11l1ll1_opy_ (u"ࠧࠨᮕ").join(bstack11l1l1l11l1_opy_[1:]):
                proxies = {
                    bstack11l1ll1_opy_ (u"࠭ࡨࡵࡶࡳࡷࠬᮖ"): bstack11l1ll1_opy_ (u"ࠢࠣᮗ").join(bstack11l1l1l11l1_opy_[1:])
                }
            else:
                proxies = {
                    bstack11l1ll1_opy_ (u"ࠨࡪࡷࡸࡵࡹࠧᮘ"): bstack11l1ll1_opy_ (u"ࠤ࡫ࡸࡹࡶ࠺࠰࠱ࠥᮙ") + bstack11l1ll1_opy_ (u"ࠥࠦᮚ").join(bstack11l1l1l11l1_opy_[1:])
                }
        else:
            proxies = {
                bstack11l1ll1_opy_ (u"ࠫ࡭ࡺࡴࡱࡵࠪᮛ"): proxy
            }
    except Exception as e:
        print(bstack11l1ll1_opy_ (u"ࠧࡹ࡯࡮ࡧࠣࡩࡷࡸ࡯ࡳࠤᮜ"), bstack11ll1l11l1l_opy_.format(bstack11l1l11llll_opy_, str(e)))
    bstack11l1l1l1111_opy_ = proxies
    return proxies