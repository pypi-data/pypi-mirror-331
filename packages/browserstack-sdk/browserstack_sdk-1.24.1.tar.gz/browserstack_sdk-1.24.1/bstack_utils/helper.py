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
import datetime
import json
import os
import platform
import re
import subprocess
import traceback
import tempfile
import multiprocessing
import threading
import sys
import logging
from math import ceil
import urllib
from urllib.parse import urlparse
import git
import requests
from packaging import version
from bstack_utils.config import Config
from bstack_utils.constants import (bstack1111l11l1l_opy_, bstack1lll11l1ll_opy_, bstack1ll1l11111_opy_, bstack11l1l11ll_opy_,
                                    bstack111111lll1_opy_, bstack11111lllll_opy_, bstack111111ll1l_opy_, bstack11111ll11l_opy_)
from bstack_utils.messages import bstack1lll11lll1_opy_, bstack1lll1l11ll_opy_
from bstack_utils.proxy import bstack1l11l111l_opy_, bstack1ll11lll1l_opy_
bstack1l1ll11l1l_opy_ = Config.bstack1l1l11111l_opy_()
logger = logging.getLogger(__name__)
def bstack111l1l1ll1_opy_(config):
    return config[bstack111l11_opy_ (u"ࠬࡻࡳࡦࡴࡑࡥࡲ࡫ࠧᎧ")]
def bstack111l111lll_opy_(config):
    return config[bstack111l11_opy_ (u"࠭ࡡࡤࡥࡨࡷࡸࡑࡥࡺࠩᎨ")]
def bstack1111l1l1_opy_():
    try:
        import playwright
        return True
    except ImportError:
        return False
def bstack1lllll1lll1_opy_(obj):
    values = []
    bstack1llll1l1111_opy_ = re.compile(bstack111l11_opy_ (u"ࡲࠣࡠࡆ࡙ࡘ࡚ࡏࡎࡡࡗࡅࡌࡥ࡜ࡥ࠭ࠧࠦᎩ"), re.I)
    for key in obj.keys():
        if bstack1llll1l1111_opy_.match(key):
            values.append(obj[key])
    return values
def bstack1lll1lll1ll_opy_(config):
    tags = []
    tags.extend(bstack1lllll1lll1_opy_(os.environ))
    tags.extend(bstack1lllll1lll1_opy_(config))
    return tags
def bstack1llllllll11_opy_(markers):
    tags = []
    for marker in markers:
        tags.append(marker.name)
    return tags
def bstack1111111l11_opy_(bstack1llll1lll11_opy_):
    if not bstack1llll1lll11_opy_:
        return bstack111l11_opy_ (u"ࠨࠩᎪ")
    return bstack111l11_opy_ (u"ࠤࡾࢁࠥ࠮ࡻࡾࠫࠥᎫ").format(bstack1llll1lll11_opy_.name, bstack1llll1lll11_opy_.email)
def bstack1111ll1lll_opy_():
    try:
        repo = git.Repo(search_parent_directories=True)
        bstack1llll11ll1l_opy_ = repo.common_dir
        info = {
            bstack111l11_opy_ (u"ࠥࡷ࡭ࡧࠢᎬ"): repo.head.commit.hexsha,
            bstack111l11_opy_ (u"ࠦࡸ࡮࡯ࡳࡶࡢࡷ࡭ࡧࠢᎭ"): repo.git.rev_parse(repo.head.commit, short=True),
            bstack111l11_opy_ (u"ࠧࡨࡲࡢࡰࡦ࡬ࠧᎮ"): repo.active_branch.name,
            bstack111l11_opy_ (u"ࠨࡴࡢࡩࠥᎯ"): repo.git.describe(all=True, tags=True, exact_match=True),
            bstack111l11_opy_ (u"ࠢࡤࡱࡰࡱ࡮ࡺࡴࡦࡴࠥᎰ"): bstack1111111l11_opy_(repo.head.commit.committer),
            bstack111l11_opy_ (u"ࠣࡥࡲࡱࡲ࡯ࡴࡵࡧࡵࡣࡩࡧࡴࡦࠤᎱ"): repo.head.commit.committed_datetime.isoformat(),
            bstack111l11_opy_ (u"ࠤࡤࡹࡹ࡮࡯ࡳࠤᎲ"): bstack1111111l11_opy_(repo.head.commit.author),
            bstack111l11_opy_ (u"ࠥࡥࡺࡺࡨࡰࡴࡢࡨࡦࡺࡥࠣᎳ"): repo.head.commit.authored_datetime.isoformat(),
            bstack111l11_opy_ (u"ࠦࡨࡵ࡭࡮࡫ࡷࡣࡲ࡫ࡳࡴࡣࡪࡩࠧᎴ"): repo.head.commit.message,
            bstack111l11_opy_ (u"ࠧࡸ࡯ࡰࡶࠥᎵ"): repo.git.rev_parse(bstack111l11_opy_ (u"ࠨ࠭࠮ࡵ࡫ࡳࡼ࠳ࡴࡰࡲ࡯ࡩࡻ࡫࡬ࠣᎶ")),
            bstack111l11_opy_ (u"ࠢࡤࡱࡰࡱࡴࡴ࡟ࡨ࡫ࡷࡣࡩ࡯ࡲࠣᎷ"): bstack1llll11ll1l_opy_,
            bstack111l11_opy_ (u"ࠣࡹࡲࡶࡰࡺࡲࡦࡧࡢ࡫࡮ࡺ࡟ࡥ࡫ࡵࠦᎸ"): subprocess.check_output([bstack111l11_opy_ (u"ࠤࡪ࡭ࡹࠨᎹ"), bstack111l11_opy_ (u"ࠥࡶࡪࡼ࠭ࡱࡣࡵࡷࡪࠨᎺ"), bstack111l11_opy_ (u"ࠦ࠲࠳ࡧࡪࡶ࠰ࡧࡴࡳ࡭ࡰࡰ࠰ࡨ࡮ࡸࠢᎻ")]).strip().decode(
                bstack111l11_opy_ (u"ࠬࡻࡴࡧ࠯࠻ࠫᎼ")),
            bstack111l11_opy_ (u"ࠨ࡬ࡢࡵࡷࡣࡹࡧࡧࠣᎽ"): repo.git.describe(tags=True, abbrev=0, always=True),
            bstack111l11_opy_ (u"ࠢࡤࡱࡰࡱ࡮ࡺࡳࡠࡵ࡬ࡲࡨ࡫࡟࡭ࡣࡶࡸࡤࡺࡡࡨࠤᎾ"): repo.git.rev_list(
                bstack111l11_opy_ (u"ࠣࡽࢀ࠲࠳ࢁࡽࠣᎿ").format(repo.head.commit, repo.git.describe(tags=True, abbrev=0, always=True)), count=True)
        }
        remotes = repo.remotes
        bstack1llll11ll11_opy_ = []
        for remote in remotes:
            bstack1lll1lll11l_opy_ = {
                bstack111l11_opy_ (u"ࠤࡱࡥࡲ࡫ࠢᏀ"): remote.name,
                bstack111l11_opy_ (u"ࠥࡹࡷࡲࠢᏁ"): remote.url,
            }
            bstack1llll11ll11_opy_.append(bstack1lll1lll11l_opy_)
        bstack1llll1l11l1_opy_ = {
            bstack111l11_opy_ (u"ࠦࡳࡧ࡭ࡦࠤᏂ"): bstack111l11_opy_ (u"ࠧ࡭ࡩࡵࠤᏃ"),
            **info,
            bstack111l11_opy_ (u"ࠨࡲࡦ࡯ࡲࡸࡪࡹࠢᏄ"): bstack1llll11ll11_opy_
        }
        bstack1llll1l11l1_opy_ = bstack1llll1ll1l1_opy_(bstack1llll1l11l1_opy_)
        return bstack1llll1l11l1_opy_
    except git.InvalidGitRepositoryError:
        return {}
    except Exception as err:
        print(bstack111l11_opy_ (u"ࠢࡆࡺࡦࡩࡵࡺࡩࡰࡰࠣ࡭ࡳࠦࡰࡰࡲࡸࡰࡦࡺࡩ࡯ࡩࠣࡋ࡮ࡺࠠ࡮ࡧࡷࡥࡩࡧࡴࡢࠢࡺ࡭ࡹ࡮ࠠࡦࡴࡵࡳࡷࡀࠠࡼࡿࠥᏅ").format(err))
        return {}
def bstack1llll1ll1l1_opy_(bstack1llll1l11l1_opy_):
    bstack1llll1lll1l_opy_ = bstack1lllll1111l_opy_(bstack1llll1l11l1_opy_)
    if bstack1llll1lll1l_opy_ and bstack1llll1lll1l_opy_ > bstack111111lll1_opy_:
        bstack1llllll1l1l_opy_ = bstack1llll1lll1l_opy_ - bstack111111lll1_opy_
        bstack1lll1llll1l_opy_ = bstack1llll1llll1_opy_(bstack1llll1l11l1_opy_[bstack111l11_opy_ (u"ࠣࡥࡲࡱࡲ࡯ࡴࡠ࡯ࡨࡷࡸࡧࡧࡦࠤᏆ")], bstack1llllll1l1l_opy_)
        bstack1llll1l11l1_opy_[bstack111l11_opy_ (u"ࠤࡦࡳࡲࡳࡩࡵࡡࡰࡩࡸࡹࡡࡨࡧࠥᏇ")] = bstack1lll1llll1l_opy_
        logger.info(bstack111l11_opy_ (u"ࠥࡘ࡭࡫ࠠࡤࡱࡰࡱ࡮ࡺࠠࡩࡣࡶࠤࡧ࡫ࡥ࡯ࠢࡷࡶࡺࡴࡣࡢࡶࡨࡨ࠳ࠦࡓࡪࡼࡨࠤࡴ࡬ࠠࡤࡱࡰࡱ࡮ࡺࠠࡢࡨࡷࡩࡷࠦࡴࡳࡷࡱࡧࡦࡺࡩࡰࡰࠣ࡭ࡸࠦࡻࡾࠢࡎࡆࠧᏈ")
                    .format(bstack1lllll1111l_opy_(bstack1llll1l11l1_opy_) / 1024))
    return bstack1llll1l11l1_opy_
def bstack1lllll1111l_opy_(bstack1ll111llll_opy_):
    try:
        if bstack1ll111llll_opy_:
            bstack1llll1ll11l_opy_ = json.dumps(bstack1ll111llll_opy_)
            bstack1llll1l1l11_opy_ = sys.getsizeof(bstack1llll1ll11l_opy_)
            return bstack1llll1l1l11_opy_
    except Exception as e:
        logger.debug(bstack111l11_opy_ (u"ࠦࡘࡵ࡭ࡦࡶ࡫࡭ࡳ࡭ࠠࡸࡧࡱࡸࠥࡽࡲࡰࡰࡪࠤࡼ࡮ࡩ࡭ࡧࠣࡧࡦࡲࡣࡶ࡮ࡤࡸ࡮ࡴࡧࠡࡵ࡬ࡾࡪࠦ࡯ࡧࠢࡍࡗࡔࡔࠠࡰࡤ࡭ࡩࡨࡺ࠺ࠡࡽࢀࠦᏉ").format(e))
    return -1
def bstack1llll1llll1_opy_(field, bstack1llll111l1l_opy_):
    try:
        bstack1llll1ll111_opy_ = len(bytes(bstack11111lllll_opy_, bstack111l11_opy_ (u"ࠬࡻࡴࡧ࠯࠻ࠫᏊ")))
        bstack11111111l1_opy_ = bytes(field, bstack111l11_opy_ (u"࠭ࡵࡵࡨ࠰࠼ࠬᏋ"))
        bstack111111111l_opy_ = len(bstack11111111l1_opy_)
        bstack1llllll11ll_opy_ = ceil(bstack111111111l_opy_ - bstack1llll111l1l_opy_ - bstack1llll1ll111_opy_)
        if bstack1llllll11ll_opy_ > 0:
            bstack1llll11l111_opy_ = bstack11111111l1_opy_[:bstack1llllll11ll_opy_].decode(bstack111l11_opy_ (u"ࠧࡶࡶࡩ࠱࠽࠭Ꮜ"), errors=bstack111l11_opy_ (u"ࠨ࡫ࡪࡲࡴࡸࡥࠨᏍ")) + bstack11111lllll_opy_
            return bstack1llll11l111_opy_
    except Exception as e:
        logger.debug(bstack111l11_opy_ (u"ࠤࡈࡶࡷࡵࡲࠡࡹ࡫࡭ࡱ࡫ࠠࡵࡴࡸࡲࡨࡧࡴࡪࡰࡪࠤ࡫࡯ࡥ࡭ࡦ࠯ࠤࡳࡵࡴࡩ࡫ࡱ࡫ࠥࡽࡡࡴࠢࡷࡶࡺࡴࡣࡢࡶࡨࡨࠥ࡮ࡥࡳࡧ࠽ࠤࢀࢃࠢᏎ").format(e))
    return field
def bstack11ll1l111_opy_():
    env = os.environ
    if (bstack111l11_opy_ (u"ࠥࡎࡊࡔࡋࡊࡐࡖࡣ࡚ࡘࡌࠣᏏ") in env and len(env[bstack111l11_opy_ (u"ࠦࡏࡋࡎࡌࡋࡑࡗࡤ࡛ࡒࡍࠤᏐ")]) > 0) or (
            bstack111l11_opy_ (u"ࠧࡐࡅࡏࡍࡌࡒࡘࡥࡈࡐࡏࡈࠦᏑ") in env and len(env[bstack111l11_opy_ (u"ࠨࡊࡆࡐࡎࡍࡓ࡙࡟ࡉࡑࡐࡉࠧᏒ")]) > 0):
        return {
            bstack111l11_opy_ (u"ࠢ࡯ࡣࡰࡩࠧᏓ"): bstack111l11_opy_ (u"ࠣࡌࡨࡲࡰ࡯࡮ࡴࠤᏔ"),
            bstack111l11_opy_ (u"ࠤࡥࡹ࡮ࡲࡤࡠࡷࡵࡰࠧᏕ"): env.get(bstack111l11_opy_ (u"ࠥࡆ࡚ࡏࡌࡅࡡࡘࡖࡑࠨᏖ")),
            bstack111l11_opy_ (u"ࠦ࡯ࡵࡢࡠࡰࡤࡱࡪࠨᏗ"): env.get(bstack111l11_opy_ (u"ࠧࡐࡏࡃࡡࡑࡅࡒࡋࠢᏘ")),
            bstack111l11_opy_ (u"ࠨࡢࡶ࡫࡯ࡨࡤࡴࡵ࡮ࡤࡨࡶࠧᏙ"): env.get(bstack111l11_opy_ (u"ࠢࡃࡗࡌࡐࡉࡥࡎࡖࡏࡅࡉࡗࠨᏚ"))
        }
    if env.get(bstack111l11_opy_ (u"ࠣࡅࡌࠦᏛ")) == bstack111l11_opy_ (u"ࠤࡷࡶࡺ࡫ࠢᏜ") and bstack11ll111l11_opy_(env.get(bstack111l11_opy_ (u"ࠥࡇࡎࡘࡃࡍࡇࡆࡍࠧᏝ"))):
        return {
            bstack111l11_opy_ (u"ࠦࡳࡧ࡭ࡦࠤᏞ"): bstack111l11_opy_ (u"ࠧࡉࡩࡳࡥ࡯ࡩࡈࡏࠢᏟ"),
            bstack111l11_opy_ (u"ࠨࡢࡶ࡫࡯ࡨࡤࡻࡲ࡭ࠤᏠ"): env.get(bstack111l11_opy_ (u"ࠢࡄࡋࡕࡇࡑࡋ࡟ࡃࡗࡌࡐࡉࡥࡕࡓࡎࠥᏡ")),
            bstack111l11_opy_ (u"ࠣ࡬ࡲࡦࡤࡴࡡ࡮ࡧࠥᏢ"): env.get(bstack111l11_opy_ (u"ࠤࡆࡍࡗࡉࡌࡆࡡࡍࡓࡇࠨᏣ")),
            bstack111l11_opy_ (u"ࠥࡦࡺ࡯࡬ࡥࡡࡱࡹࡲࡨࡥࡳࠤᏤ"): env.get(bstack111l11_opy_ (u"ࠦࡈࡏࡒࡄࡎࡈࡣࡇ࡛ࡉࡍࡆࡢࡒ࡚ࡓࠢᏥ"))
        }
    if env.get(bstack111l11_opy_ (u"ࠧࡉࡉࠣᏦ")) == bstack111l11_opy_ (u"ࠨࡴࡳࡷࡨࠦᏧ") and bstack11ll111l11_opy_(env.get(bstack111l11_opy_ (u"ࠢࡕࡔࡄ࡚ࡎ࡙ࠢᏨ"))):
        return {
            bstack111l11_opy_ (u"ࠣࡰࡤࡱࡪࠨᏩ"): bstack111l11_opy_ (u"ࠤࡗࡶࡦࡼࡩࡴࠢࡆࡍࠧᏪ"),
            bstack111l11_opy_ (u"ࠥࡦࡺ࡯࡬ࡥࡡࡸࡶࡱࠨᏫ"): env.get(bstack111l11_opy_ (u"࡙ࠦࡘࡁࡗࡋࡖࡣࡇ࡛ࡉࡍࡆࡢ࡛ࡊࡈ࡟ࡖࡔࡏࠦᏬ")),
            bstack111l11_opy_ (u"ࠧࡰ࡯ࡣࡡࡱࡥࡲ࡫ࠢᏭ"): env.get(bstack111l11_opy_ (u"ࠨࡔࡓࡃ࡙ࡍࡘࡥࡊࡐࡄࡢࡒࡆࡓࡅࠣᏮ")),
            bstack111l11_opy_ (u"ࠢࡣࡷ࡬ࡰࡩࡥ࡮ࡶ࡯ࡥࡩࡷࠨᏯ"): env.get(bstack111l11_opy_ (u"ࠣࡖࡕࡅ࡛ࡏࡓࡠࡄࡘࡍࡑࡊ࡟ࡏࡗࡐࡆࡊࡘࠢᏰ"))
        }
    if env.get(bstack111l11_opy_ (u"ࠤࡆࡍࠧᏱ")) == bstack111l11_opy_ (u"ࠥࡸࡷࡻࡥࠣᏲ") and env.get(bstack111l11_opy_ (u"ࠦࡈࡏ࡟ࡏࡃࡐࡉࠧᏳ")) == bstack111l11_opy_ (u"ࠧࡩ࡯ࡥࡧࡶ࡬࡮ࡶࠢᏴ"):
        return {
            bstack111l11_opy_ (u"ࠨ࡮ࡢ࡯ࡨࠦᏵ"): bstack111l11_opy_ (u"ࠢࡄࡱࡧࡩࡸ࡮ࡩࡱࠤ᏶"),
            bstack111l11_opy_ (u"ࠣࡤࡸ࡭ࡱࡪ࡟ࡶࡴ࡯ࠦ᏷"): None,
            bstack111l11_opy_ (u"ࠤ࡭ࡳࡧࡥ࡮ࡢ࡯ࡨࠦᏸ"): None,
            bstack111l11_opy_ (u"ࠥࡦࡺ࡯࡬ࡥࡡࡱࡹࡲࡨࡥࡳࠤᏹ"): None
        }
    if env.get(bstack111l11_opy_ (u"ࠦࡇࡏࡔࡃࡗࡆࡏࡊ࡚࡟ࡃࡔࡄࡒࡈࡎࠢᏺ")) and env.get(bstack111l11_opy_ (u"ࠧࡈࡉࡕࡄࡘࡇࡐࡋࡔࡠࡅࡒࡑࡒࡏࡔࠣᏻ")):
        return {
            bstack111l11_opy_ (u"ࠨ࡮ࡢ࡯ࡨࠦᏼ"): bstack111l11_opy_ (u"ࠢࡃ࡫ࡷࡦࡺࡩ࡫ࡦࡶࠥᏽ"),
            bstack111l11_opy_ (u"ࠣࡤࡸ࡭ࡱࡪ࡟ࡶࡴ࡯ࠦ᏾"): env.get(bstack111l11_opy_ (u"ࠤࡅࡍ࡙ࡈࡕࡄࡍࡈࡘࡤࡍࡉࡕࡡࡋࡘ࡙ࡖ࡟ࡐࡔࡌࡋࡎࡔࠢ᏿")),
            bstack111l11_opy_ (u"ࠥ࡮ࡴࡨ࡟࡯ࡣࡰࡩࠧ᐀"): None,
            bstack111l11_opy_ (u"ࠦࡧࡻࡩ࡭ࡦࡢࡲࡺࡳࡢࡦࡴࠥᐁ"): env.get(bstack111l11_opy_ (u"ࠧࡈࡉࡕࡄࡘࡇࡐࡋࡔࡠࡄࡘࡍࡑࡊ࡟ࡏࡗࡐࡆࡊࡘࠢᐂ"))
        }
    if env.get(bstack111l11_opy_ (u"ࠨࡃࡊࠤᐃ")) == bstack111l11_opy_ (u"ࠢࡵࡴࡸࡩࠧᐄ") and bstack11ll111l11_opy_(env.get(bstack111l11_opy_ (u"ࠣࡆࡕࡓࡓࡋࠢᐅ"))):
        return {
            bstack111l11_opy_ (u"ࠤࡱࡥࡲ࡫ࠢᐆ"): bstack111l11_opy_ (u"ࠥࡈࡷࡵ࡮ࡦࠤᐇ"),
            bstack111l11_opy_ (u"ࠦࡧࡻࡩ࡭ࡦࡢࡹࡷࡲࠢᐈ"): env.get(bstack111l11_opy_ (u"ࠧࡊࡒࡐࡐࡈࡣࡇ࡛ࡉࡍࡆࡢࡐࡎࡔࡋࠣᐉ")),
            bstack111l11_opy_ (u"ࠨࡪࡰࡤࡢࡲࡦࡳࡥࠣᐊ"): None,
            bstack111l11_opy_ (u"ࠢࡣࡷ࡬ࡰࡩࡥ࡮ࡶ࡯ࡥࡩࡷࠨᐋ"): env.get(bstack111l11_opy_ (u"ࠣࡆࡕࡓࡓࡋ࡟ࡃࡗࡌࡐࡉࡥࡎࡖࡏࡅࡉࡗࠨᐌ"))
        }
    if env.get(bstack111l11_opy_ (u"ࠤࡆࡍࠧᐍ")) == bstack111l11_opy_ (u"ࠥࡸࡷࡻࡥࠣᐎ") and bstack11ll111l11_opy_(env.get(bstack111l11_opy_ (u"ࠦࡘࡋࡍࡂࡒࡋࡓࡗࡋࠢᐏ"))):
        return {
            bstack111l11_opy_ (u"ࠧࡴࡡ࡮ࡧࠥᐐ"): bstack111l11_opy_ (u"ࠨࡓࡦ࡯ࡤࡴ࡭ࡵࡲࡦࠤᐑ"),
            bstack111l11_opy_ (u"ࠢࡣࡷ࡬ࡰࡩࡥࡵࡳ࡮ࠥᐒ"): env.get(bstack111l11_opy_ (u"ࠣࡕࡈࡑࡆࡖࡈࡐࡔࡈࡣࡔࡘࡇࡂࡐࡌ࡞ࡆ࡚ࡉࡐࡐࡢ࡙ࡗࡒࠢᐓ")),
            bstack111l11_opy_ (u"ࠤ࡭ࡳࡧࡥ࡮ࡢ࡯ࡨࠦᐔ"): env.get(bstack111l11_opy_ (u"ࠥࡗࡊࡓࡁࡑࡊࡒࡖࡊࡥࡊࡐࡄࡢࡒࡆࡓࡅࠣᐕ")),
            bstack111l11_opy_ (u"ࠦࡧࡻࡩ࡭ࡦࡢࡲࡺࡳࡢࡦࡴࠥᐖ"): env.get(bstack111l11_opy_ (u"࡙ࠧࡅࡎࡃࡓࡌࡔࡘࡅࡠࡌࡒࡆࡤࡏࡄࠣᐗ"))
        }
    if env.get(bstack111l11_opy_ (u"ࠨࡃࡊࠤᐘ")) == bstack111l11_opy_ (u"ࠢࡵࡴࡸࡩࠧᐙ") and bstack11ll111l11_opy_(env.get(bstack111l11_opy_ (u"ࠣࡉࡌࡘࡑࡇࡂࡠࡅࡌࠦᐚ"))):
        return {
            bstack111l11_opy_ (u"ࠤࡱࡥࡲ࡫ࠢᐛ"): bstack111l11_opy_ (u"ࠥࡋ࡮ࡺࡌࡢࡤࠥᐜ"),
            bstack111l11_opy_ (u"ࠦࡧࡻࡩ࡭ࡦࡢࡹࡷࡲࠢᐝ"): env.get(bstack111l11_opy_ (u"ࠧࡉࡉࡠࡌࡒࡆࡤ࡛ࡒࡍࠤᐞ")),
            bstack111l11_opy_ (u"ࠨࡪࡰࡤࡢࡲࡦࡳࡥࠣᐟ"): env.get(bstack111l11_opy_ (u"ࠢࡄࡋࡢࡎࡔࡈ࡟ࡏࡃࡐࡉࠧᐠ")),
            bstack111l11_opy_ (u"ࠣࡤࡸ࡭ࡱࡪ࡟࡯ࡷࡰࡦࡪࡸࠢᐡ"): env.get(bstack111l11_opy_ (u"ࠤࡆࡍࡤࡐࡏࡃࡡࡌࡈࠧᐢ"))
        }
    if env.get(bstack111l11_opy_ (u"ࠥࡇࡎࠨᐣ")) == bstack111l11_opy_ (u"ࠦࡹࡸࡵࡦࠤᐤ") and bstack11ll111l11_opy_(env.get(bstack111l11_opy_ (u"ࠧࡈࡕࡊࡎࡇࡏࡎ࡚ࡅࠣᐥ"))):
        return {
            bstack111l11_opy_ (u"ࠨ࡮ࡢ࡯ࡨࠦᐦ"): bstack111l11_opy_ (u"ࠢࡃࡷ࡬ࡰࡩࡱࡩࡵࡧࠥᐧ"),
            bstack111l11_opy_ (u"ࠣࡤࡸ࡭ࡱࡪ࡟ࡶࡴ࡯ࠦᐨ"): env.get(bstack111l11_opy_ (u"ࠤࡅ࡙ࡎࡒࡄࡌࡋࡗࡉࡤࡈࡕࡊࡎࡇࡣ࡚ࡘࡌࠣᐩ")),
            bstack111l11_opy_ (u"ࠥ࡮ࡴࡨ࡟࡯ࡣࡰࡩࠧᐪ"): env.get(bstack111l11_opy_ (u"ࠦࡇ࡛ࡉࡍࡆࡎࡍ࡙ࡋ࡟ࡍࡃࡅࡉࡑࠨᐫ")) or env.get(bstack111l11_opy_ (u"ࠧࡈࡕࡊࡎࡇࡏࡎ࡚ࡅࡠࡒࡌࡔࡊࡒࡉࡏࡇࡢࡒࡆࡓࡅࠣᐬ")),
            bstack111l11_opy_ (u"ࠨࡢࡶ࡫࡯ࡨࡤࡴࡵ࡮ࡤࡨࡶࠧᐭ"): env.get(bstack111l11_opy_ (u"ࠢࡃࡗࡌࡐࡉࡑࡉࡕࡇࡢࡆ࡚ࡏࡌࡅࡡࡑ࡙ࡒࡈࡅࡓࠤᐮ"))
        }
    if bstack11ll111l11_opy_(env.get(bstack111l11_opy_ (u"ࠣࡖࡉࡣࡇ࡛ࡉࡍࡆࠥᐯ"))):
        return {
            bstack111l11_opy_ (u"ࠤࡱࡥࡲ࡫ࠢᐰ"): bstack111l11_opy_ (u"࡚ࠥ࡮ࡹࡵࡢ࡮ࠣࡗࡹࡻࡤࡪࡱࠣࡘࡪࡧ࡭ࠡࡕࡨࡶࡻ࡯ࡣࡦࡵࠥᐱ"),
            bstack111l11_opy_ (u"ࠦࡧࡻࡩ࡭ࡦࡢࡹࡷࡲࠢᐲ"): bstack111l11_opy_ (u"ࠧࢁࡽࡼࡿࠥᐳ").format(env.get(bstack111l11_opy_ (u"࠭ࡓ࡚ࡕࡗࡉࡒࡥࡔࡆࡃࡐࡊࡔ࡛ࡎࡅࡃࡗࡍࡔࡔࡓࡆࡔ࡙ࡉࡗ࡛ࡒࡊࠩᐴ")), env.get(bstack111l11_opy_ (u"ࠧࡔ࡛ࡖࡘࡊࡓ࡟ࡕࡇࡄࡑࡕࡘࡏࡋࡇࡆࡘࡎࡊࠧᐵ"))),
            bstack111l11_opy_ (u"ࠣ࡬ࡲࡦࡤࡴࡡ࡮ࡧࠥᐶ"): env.get(bstack111l11_opy_ (u"ࠤࡖ࡝ࡘ࡚ࡅࡎࡡࡇࡉࡋࡏࡎࡊࡖࡌࡓࡓࡏࡄࠣᐷ")),
            bstack111l11_opy_ (u"ࠥࡦࡺ࡯࡬ࡥࡡࡱࡹࡲࡨࡥࡳࠤᐸ"): env.get(bstack111l11_opy_ (u"ࠦࡇ࡛ࡉࡍࡆࡢࡆ࡚ࡏࡌࡅࡋࡇࠦᐹ"))
        }
    if bstack11ll111l11_opy_(env.get(bstack111l11_opy_ (u"ࠧࡇࡐࡑࡘࡈ࡝ࡔࡘࠢᐺ"))):
        return {
            bstack111l11_opy_ (u"ࠨ࡮ࡢ࡯ࡨࠦᐻ"): bstack111l11_opy_ (u"ࠢࡂࡲࡳࡺࡪࡿ࡯ࡳࠤᐼ"),
            bstack111l11_opy_ (u"ࠣࡤࡸ࡭ࡱࡪ࡟ࡶࡴ࡯ࠦᐽ"): bstack111l11_opy_ (u"ࠤࡾࢁ࠴ࡶࡲࡰ࡬ࡨࡧࡹ࠵ࡻࡾ࠱ࡾࢁ࠴ࡨࡵࡪ࡮ࡧࡷ࠴ࢁࡽࠣᐾ").format(env.get(bstack111l11_opy_ (u"ࠪࡅࡕࡖࡖࡆ࡛ࡒࡖࡤ࡛ࡒࡍࠩᐿ")), env.get(bstack111l11_opy_ (u"ࠫࡆࡖࡐࡗࡇ࡜ࡓࡗࡥࡁࡄࡅࡒ࡙ࡓ࡚࡟ࡏࡃࡐࡉࠬᑀ")), env.get(bstack111l11_opy_ (u"ࠬࡇࡐࡑࡘࡈ࡝ࡔࡘ࡟ࡑࡔࡒࡎࡊࡉࡔࡠࡕࡏ࡙ࡌ࠭ᑁ")), env.get(bstack111l11_opy_ (u"࠭ࡁࡑࡒ࡙ࡉ࡞ࡕࡒࡠࡄࡘࡍࡑࡊ࡟ࡊࡆࠪᑂ"))),
            bstack111l11_opy_ (u"ࠢ࡫ࡱࡥࡣࡳࡧ࡭ࡦࠤᑃ"): env.get(bstack111l11_opy_ (u"ࠣࡃࡓࡔ࡛ࡋ࡙ࡐࡔࡢࡎࡔࡈ࡟ࡏࡃࡐࡉࠧᑄ")),
            bstack111l11_opy_ (u"ࠤࡥࡹ࡮ࡲࡤࡠࡰࡸࡱࡧ࡫ࡲࠣᑅ"): env.get(bstack111l11_opy_ (u"ࠥࡅࡕࡖࡖࡆ࡛ࡒࡖࡤࡈࡕࡊࡎࡇࡣࡓ࡛ࡍࡃࡇࡕࠦᑆ"))
        }
    if env.get(bstack111l11_opy_ (u"ࠦࡆࡠࡕࡓࡇࡢࡌ࡙࡚ࡐࡠࡗࡖࡉࡗࡥࡁࡈࡇࡑࡘࠧᑇ")) and env.get(bstack111l11_opy_ (u"࡚ࠧࡆࡠࡄࡘࡍࡑࡊࠢᑈ")):
        return {
            bstack111l11_opy_ (u"ࠨ࡮ࡢ࡯ࡨࠦᑉ"): bstack111l11_opy_ (u"ࠢࡂࡼࡸࡶࡪࠦࡃࡊࠤᑊ"),
            bstack111l11_opy_ (u"ࠣࡤࡸ࡭ࡱࡪ࡟ࡶࡴ࡯ࠦᑋ"): bstack111l11_opy_ (u"ࠤࡾࢁࢀࢃ࠯ࡠࡤࡸ࡭ࡱࡪ࠯ࡳࡧࡶࡹࡱࡺࡳࡀࡤࡸ࡭ࡱࡪࡉࡥ࠿ࡾࢁࠧᑌ").format(env.get(bstack111l11_opy_ (u"ࠪࡗ࡞࡙ࡔࡆࡏࡢࡘࡊࡇࡍࡇࡑࡘࡒࡉࡇࡔࡊࡑࡑࡗࡊࡘࡖࡆࡔࡘࡖࡎ࠭ᑍ")), env.get(bstack111l11_opy_ (u"ࠫࡘ࡟ࡓࡕࡇࡐࡣ࡙ࡋࡁࡎࡒࡕࡓࡏࡋࡃࡕࠩᑎ")), env.get(bstack111l11_opy_ (u"ࠬࡈࡕࡊࡎࡇࡣࡇ࡛ࡉࡍࡆࡌࡈࠬᑏ"))),
            bstack111l11_opy_ (u"ࠨࡪࡰࡤࡢࡲࡦࡳࡥࠣᑐ"): env.get(bstack111l11_opy_ (u"ࠢࡃࡗࡌࡐࡉࡥࡂࡖࡋࡏࡈࡎࡊࠢᑑ")),
            bstack111l11_opy_ (u"ࠣࡤࡸ࡭ࡱࡪ࡟࡯ࡷࡰࡦࡪࡸࠢᑒ"): env.get(bstack111l11_opy_ (u"ࠤࡅ࡙ࡎࡒࡄࡠࡄࡘࡍࡑࡊࡉࡅࠤᑓ"))
        }
    if any([env.get(bstack111l11_opy_ (u"ࠥࡇࡔࡊࡅࡃࡗࡌࡐࡉࡥࡂࡖࡋࡏࡈࡤࡏࡄࠣᑔ")), env.get(bstack111l11_opy_ (u"ࠦࡈࡕࡄࡆࡄࡘࡍࡑࡊ࡟ࡓࡇࡖࡓࡑ࡜ࡅࡅࡡࡖࡓ࡚ࡘࡃࡆࡡ࡙ࡉࡗ࡙ࡉࡐࡐࠥᑕ")), env.get(bstack111l11_opy_ (u"ࠧࡉࡏࡅࡇࡅ࡙ࡎࡒࡄࡠࡕࡒ࡙ࡗࡉࡅࡠࡘࡈࡖࡘࡏࡏࡏࠤᑖ"))]):
        return {
            bstack111l11_opy_ (u"ࠨ࡮ࡢ࡯ࡨࠦᑗ"): bstack111l11_opy_ (u"ࠢࡂ࡙ࡖࠤࡈࡵࡤࡦࡄࡸ࡭ࡱࡪࠢᑘ"),
            bstack111l11_opy_ (u"ࠣࡤࡸ࡭ࡱࡪ࡟ࡶࡴ࡯ࠦᑙ"): env.get(bstack111l11_opy_ (u"ࠤࡆࡓࡉࡋࡂࡖࡋࡏࡈࡤࡖࡕࡃࡎࡌࡇࡤࡈࡕࡊࡎࡇࡣ࡚ࡘࡌࠣᑚ")),
            bstack111l11_opy_ (u"ࠥ࡮ࡴࡨ࡟࡯ࡣࡰࡩࠧᑛ"): env.get(bstack111l11_opy_ (u"ࠦࡈࡕࡄࡆࡄࡘࡍࡑࡊ࡟ࡃࡗࡌࡐࡉࡥࡉࡅࠤᑜ")),
            bstack111l11_opy_ (u"ࠧࡨࡵࡪ࡮ࡧࡣࡳࡻ࡭ࡣࡧࡵࠦᑝ"): env.get(bstack111l11_opy_ (u"ࠨࡃࡐࡆࡈࡆ࡚ࡏࡌࡅࡡࡅ࡙ࡎࡒࡄࡠࡋࡇࠦᑞ"))
        }
    if env.get(bstack111l11_opy_ (u"ࠢࡣࡣࡰࡦࡴࡵ࡟ࡣࡷ࡬ࡰࡩࡔࡵ࡮ࡤࡨࡶࠧᑟ")):
        return {
            bstack111l11_opy_ (u"ࠣࡰࡤࡱࡪࠨᑠ"): bstack111l11_opy_ (u"ࠤࡅࡥࡲࡨ࡯ࡰࠤᑡ"),
            bstack111l11_opy_ (u"ࠥࡦࡺ࡯࡬ࡥࡡࡸࡶࡱࠨᑢ"): env.get(bstack111l11_opy_ (u"ࠦࡧࡧ࡭ࡣࡱࡲࡣࡧࡻࡩ࡭ࡦࡕࡩࡸࡻ࡬ࡵࡵࡘࡶࡱࠨᑣ")),
            bstack111l11_opy_ (u"ࠧࡰ࡯ࡣࡡࡱࡥࡲ࡫ࠢᑤ"): env.get(bstack111l11_opy_ (u"ࠨࡢࡢ࡯ࡥࡳࡴࡥࡳࡩࡱࡵࡸࡏࡵࡢࡏࡣࡰࡩࠧᑥ")),
            bstack111l11_opy_ (u"ࠢࡣࡷ࡬ࡰࡩࡥ࡮ࡶ࡯ࡥࡩࡷࠨᑦ"): env.get(bstack111l11_opy_ (u"ࠣࡤࡤࡱࡧࡵ࡯ࡠࡤࡸ࡭ࡱࡪࡎࡶ࡯ࡥࡩࡷࠨᑧ"))
        }
    if env.get(bstack111l11_opy_ (u"ࠤ࡚ࡉࡗࡉࡋࡆࡔࠥᑨ")) or env.get(bstack111l11_opy_ (u"࡛ࠥࡊࡘࡃࡌࡇࡕࡣࡒࡇࡉࡏࡡࡓࡍࡕࡋࡌࡊࡐࡈࡣࡘ࡚ࡁࡓࡖࡈࡈࠧᑩ")):
        return {
            bstack111l11_opy_ (u"ࠦࡳࡧ࡭ࡦࠤᑪ"): bstack111l11_opy_ (u"ࠧ࡝ࡥࡳࡥ࡮ࡩࡷࠨᑫ"),
            bstack111l11_opy_ (u"ࠨࡢࡶ࡫࡯ࡨࡤࡻࡲ࡭ࠤᑬ"): env.get(bstack111l11_opy_ (u"ࠢࡘࡇࡕࡇࡐࡋࡒࡠࡄࡘࡍࡑࡊ࡟ࡖࡔࡏࠦᑭ")),
            bstack111l11_opy_ (u"ࠣ࡬ࡲࡦࡤࡴࡡ࡮ࡧࠥᑮ"): bstack111l11_opy_ (u"ࠤࡐࡥ࡮ࡴࠠࡑ࡫ࡳࡩࡱ࡯࡮ࡦࠤᑯ") if env.get(bstack111l11_opy_ (u"࡛ࠥࡊࡘࡃࡌࡇࡕࡣࡒࡇࡉࡏࡡࡓࡍࡕࡋࡌࡊࡐࡈࡣࡘ࡚ࡁࡓࡖࡈࡈࠧᑰ")) else None,
            bstack111l11_opy_ (u"ࠦࡧࡻࡩ࡭ࡦࡢࡲࡺࡳࡢࡦࡴࠥᑱ"): env.get(bstack111l11_opy_ (u"ࠧ࡝ࡅࡓࡅࡎࡉࡗࡥࡇࡊࡖࡢࡇࡔࡓࡍࡊࡖࠥᑲ"))
        }
    if any([env.get(bstack111l11_opy_ (u"ࠨࡇࡄࡒࡢࡔࡗࡕࡊࡆࡅࡗࠦᑳ")), env.get(bstack111l11_opy_ (u"ࠢࡈࡅࡏࡓ࡚ࡊ࡟ࡑࡔࡒࡎࡊࡉࡔࠣᑴ")), env.get(bstack111l11_opy_ (u"ࠣࡉࡒࡓࡌࡒࡅࡠࡅࡏࡓ࡚ࡊ࡟ࡑࡔࡒࡎࡊࡉࡔࠣᑵ"))]):
        return {
            bstack111l11_opy_ (u"ࠤࡱࡥࡲ࡫ࠢᑶ"): bstack111l11_opy_ (u"ࠥࡋࡴࡵࡧ࡭ࡧࠣࡇࡱࡵࡵࡥࠤᑷ"),
            bstack111l11_opy_ (u"ࠦࡧࡻࡩ࡭ࡦࡢࡹࡷࡲࠢᑸ"): None,
            bstack111l11_opy_ (u"ࠧࡰ࡯ࡣࡡࡱࡥࡲ࡫ࠢᑹ"): env.get(bstack111l11_opy_ (u"ࠨࡐࡓࡑࡍࡉࡈ࡚࡟ࡊࡆࠥᑺ")),
            bstack111l11_opy_ (u"ࠢࡣࡷ࡬ࡰࡩࡥ࡮ࡶ࡯ࡥࡩࡷࠨᑻ"): env.get(bstack111l11_opy_ (u"ࠣࡄࡘࡍࡑࡊ࡟ࡊࡆࠥᑼ"))
        }
    if env.get(bstack111l11_opy_ (u"ࠤࡖࡌࡎࡖࡐࡂࡄࡏࡉࠧᑽ")):
        return {
            bstack111l11_opy_ (u"ࠥࡲࡦࡳࡥࠣᑾ"): bstack111l11_opy_ (u"ࠦࡘ࡮ࡩࡱࡲࡤࡦࡱ࡫ࠢᑿ"),
            bstack111l11_opy_ (u"ࠧࡨࡵࡪ࡮ࡧࡣࡺࡸ࡬ࠣᒀ"): env.get(bstack111l11_opy_ (u"ࠨࡓࡉࡋࡓࡔࡆࡈࡌࡆࡡࡅ࡙ࡎࡒࡄࡠࡗࡕࡐࠧᒁ")),
            bstack111l11_opy_ (u"ࠢ࡫ࡱࡥࡣࡳࡧ࡭ࡦࠤᒂ"): bstack111l11_opy_ (u"ࠣࡌࡲࡦࠥࠩࡻࡾࠤᒃ").format(env.get(bstack111l11_opy_ (u"ࠩࡖࡌࡎࡖࡐࡂࡄࡏࡉࡤࡐࡏࡃࡡࡌࡈࠬᒄ"))) if env.get(bstack111l11_opy_ (u"ࠥࡗࡍࡏࡐࡑࡃࡅࡐࡊࡥࡊࡐࡄࡢࡍࡉࠨᒅ")) else None,
            bstack111l11_opy_ (u"ࠦࡧࡻࡩ࡭ࡦࡢࡲࡺࡳࡢࡦࡴࠥᒆ"): env.get(bstack111l11_opy_ (u"࡙ࠧࡈࡊࡒࡓࡅࡇࡒࡅࡠࡄࡘࡍࡑࡊ࡟ࡏࡗࡐࡆࡊࡘࠢᒇ"))
        }
    if bstack11ll111l11_opy_(env.get(bstack111l11_opy_ (u"ࠨࡎࡆࡖࡏࡍࡋ࡟ࠢᒈ"))):
        return {
            bstack111l11_opy_ (u"ࠢ࡯ࡣࡰࡩࠧᒉ"): bstack111l11_opy_ (u"ࠣࡐࡨࡸࡱ࡯ࡦࡺࠤᒊ"),
            bstack111l11_opy_ (u"ࠤࡥࡹ࡮ࡲࡤࡠࡷࡵࡰࠧᒋ"): env.get(bstack111l11_opy_ (u"ࠥࡈࡊࡖࡌࡐ࡛ࡢ࡙ࡗࡒࠢᒌ")),
            bstack111l11_opy_ (u"ࠦ࡯ࡵࡢࡠࡰࡤࡱࡪࠨᒍ"): env.get(bstack111l11_opy_ (u"࡙ࠧࡉࡕࡇࡢࡒࡆࡓࡅࠣᒎ")),
            bstack111l11_opy_ (u"ࠨࡢࡶ࡫࡯ࡨࡤࡴࡵ࡮ࡤࡨࡶࠧᒏ"): env.get(bstack111l11_opy_ (u"ࠢࡃࡗࡌࡐࡉࡥࡉࡅࠤᒐ"))
        }
    if bstack11ll111l11_opy_(env.get(bstack111l11_opy_ (u"ࠣࡉࡌࡘࡍ࡛ࡂࡠࡃࡆࡘࡎࡕࡎࡔࠤᒑ"))):
        return {
            bstack111l11_opy_ (u"ࠤࡱࡥࡲ࡫ࠢᒒ"): bstack111l11_opy_ (u"ࠥࡋ࡮ࡺࡈࡶࡤࠣࡅࡨࡺࡩࡰࡰࡶࠦᒓ"),
            bstack111l11_opy_ (u"ࠦࡧࡻࡩ࡭ࡦࡢࡹࡷࡲࠢᒔ"): bstack111l11_opy_ (u"ࠧࢁࡽ࠰ࡽࢀ࠳ࡦࡩࡴࡪࡱࡱࡷ࠴ࡸࡵ࡯ࡵ࠲ࡿࢂࠨᒕ").format(env.get(bstack111l11_opy_ (u"࠭ࡇࡊࡖࡋ࡙ࡇࡥࡓࡆࡔ࡙ࡉࡗࡥࡕࡓࡎࠪᒖ")), env.get(bstack111l11_opy_ (u"ࠧࡈࡋࡗࡌ࡚ࡈ࡟ࡓࡇࡓࡓࡘࡏࡔࡐࡔ࡜ࠫᒗ")), env.get(bstack111l11_opy_ (u"ࠨࡉࡌࡘࡍ࡛ࡂࡠࡔࡘࡒࡤࡏࡄࠨᒘ"))),
            bstack111l11_opy_ (u"ࠤ࡭ࡳࡧࡥ࡮ࡢ࡯ࡨࠦᒙ"): env.get(bstack111l11_opy_ (u"ࠥࡋࡎ࡚ࡈࡖࡄࡢ࡛ࡔࡘࡋࡇࡎࡒ࡛ࠧᒚ")),
            bstack111l11_opy_ (u"ࠦࡧࡻࡩ࡭ࡦࡢࡲࡺࡳࡢࡦࡴࠥᒛ"): env.get(bstack111l11_opy_ (u"ࠧࡍࡉࡕࡊࡘࡆࡤࡘࡕࡏࡡࡌࡈࠧᒜ"))
        }
    if env.get(bstack111l11_opy_ (u"ࠨࡃࡊࠤᒝ")) == bstack111l11_opy_ (u"ࠢࡵࡴࡸࡩࠧᒞ") and env.get(bstack111l11_opy_ (u"ࠣࡘࡈࡖࡈࡋࡌࠣᒟ")) == bstack111l11_opy_ (u"ࠤ࠴ࠦᒠ"):
        return {
            bstack111l11_opy_ (u"ࠥࡲࡦࡳࡥࠣᒡ"): bstack111l11_opy_ (u"࡛ࠦ࡫ࡲࡤࡧ࡯ࠦᒢ"),
            bstack111l11_opy_ (u"ࠧࡨࡵࡪ࡮ࡧࡣࡺࡸ࡬ࠣᒣ"): bstack111l11_opy_ (u"ࠨࡨࡵࡶࡳ࠾࠴࠵ࡻࡾࠤᒤ").format(env.get(bstack111l11_opy_ (u"ࠧࡗࡇࡕࡇࡊࡒ࡟ࡖࡔࡏࠫᒥ"))),
            bstack111l11_opy_ (u"ࠣ࡬ࡲࡦࡤࡴࡡ࡮ࡧࠥᒦ"): None,
            bstack111l11_opy_ (u"ࠤࡥࡹ࡮ࡲࡤࡠࡰࡸࡱࡧ࡫ࡲࠣᒧ"): None,
        }
    if env.get(bstack111l11_opy_ (u"ࠥࡘࡊࡇࡍࡄࡋࡗ࡝ࡤ࡜ࡅࡓࡕࡌࡓࡓࠨᒨ")):
        return {
            bstack111l11_opy_ (u"ࠦࡳࡧ࡭ࡦࠤᒩ"): bstack111l11_opy_ (u"࡚ࠧࡥࡢ࡯ࡦ࡭ࡹࡿࠢᒪ"),
            bstack111l11_opy_ (u"ࠨࡢࡶ࡫࡯ࡨࡤࡻࡲ࡭ࠤᒫ"): None,
            bstack111l11_opy_ (u"ࠢ࡫ࡱࡥࡣࡳࡧ࡭ࡦࠤᒬ"): env.get(bstack111l11_opy_ (u"ࠣࡖࡈࡅࡒࡉࡉࡕ࡛ࡢࡔࡗࡕࡊࡆࡅࡗࡣࡓࡇࡍࡆࠤᒭ")),
            bstack111l11_opy_ (u"ࠤࡥࡹ࡮ࡲࡤࡠࡰࡸࡱࡧ࡫ࡲࠣᒮ"): env.get(bstack111l11_opy_ (u"ࠥࡆ࡚ࡏࡌࡅࡡࡑ࡙ࡒࡈࡅࡓࠤᒯ"))
        }
    if any([env.get(bstack111l11_opy_ (u"ࠦࡈࡕࡎࡄࡑࡘࡖࡘࡋࠢᒰ")), env.get(bstack111l11_opy_ (u"ࠧࡉࡏࡏࡅࡒ࡙ࡗ࡙ࡅࡠࡗࡕࡐࠧᒱ")), env.get(bstack111l11_opy_ (u"ࠨࡃࡐࡐࡆࡓ࡚ࡘࡓࡆࡡࡘࡗࡊࡘࡎࡂࡏࡈࠦᒲ")), env.get(bstack111l11_opy_ (u"ࠢࡄࡑࡑࡇࡔ࡛ࡒࡔࡇࡢࡘࡊࡇࡍࠣᒳ"))]):
        return {
            bstack111l11_opy_ (u"ࠣࡰࡤࡱࡪࠨᒴ"): bstack111l11_opy_ (u"ࠤࡆࡳࡳࡩ࡯ࡶࡴࡶࡩࠧᒵ"),
            bstack111l11_opy_ (u"ࠥࡦࡺ࡯࡬ࡥࡡࡸࡶࡱࠨᒶ"): None,
            bstack111l11_opy_ (u"ࠦ࡯ࡵࡢࡠࡰࡤࡱࡪࠨᒷ"): env.get(bstack111l11_opy_ (u"ࠧࡈࡕࡊࡎࡇࡣࡏࡕࡂࡠࡐࡄࡑࡊࠨᒸ")) or None,
            bstack111l11_opy_ (u"ࠨࡢࡶ࡫࡯ࡨࡤࡴࡵ࡮ࡤࡨࡶࠧᒹ"): env.get(bstack111l11_opy_ (u"ࠢࡃࡗࡌࡐࡉࡥࡉࡅࠤᒺ"), 0)
        }
    if env.get(bstack111l11_opy_ (u"ࠣࡉࡒࡣࡏࡕࡂࡠࡐࡄࡑࡊࠨᒻ")):
        return {
            bstack111l11_opy_ (u"ࠤࡱࡥࡲ࡫ࠢᒼ"): bstack111l11_opy_ (u"ࠥࡋࡴࡉࡄࠣᒽ"),
            bstack111l11_opy_ (u"ࠦࡧࡻࡩ࡭ࡦࡢࡹࡷࡲࠢᒾ"): None,
            bstack111l11_opy_ (u"ࠧࡰ࡯ࡣࡡࡱࡥࡲ࡫ࠢᒿ"): env.get(bstack111l11_opy_ (u"ࠨࡇࡐࡡࡍࡓࡇࡥࡎࡂࡏࡈࠦᓀ")),
            bstack111l11_opy_ (u"ࠢࡣࡷ࡬ࡰࡩࡥ࡮ࡶ࡯ࡥࡩࡷࠨᓁ"): env.get(bstack111l11_opy_ (u"ࠣࡉࡒࡣࡕࡏࡐࡆࡎࡌࡒࡊࡥࡃࡐࡗࡑࡘࡊࡘࠢᓂ"))
        }
    if env.get(bstack111l11_opy_ (u"ࠤࡆࡊࡤࡈࡕࡊࡎࡇࡣࡎࡊࠢᓃ")):
        return {
            bstack111l11_opy_ (u"ࠥࡲࡦࡳࡥࠣᓄ"): bstack111l11_opy_ (u"ࠦࡈࡵࡤࡦࡈࡵࡩࡸ࡮ࠢᓅ"),
            bstack111l11_opy_ (u"ࠧࡨࡵࡪ࡮ࡧࡣࡺࡸ࡬ࠣᓆ"): env.get(bstack111l11_opy_ (u"ࠨࡃࡇࡡࡅ࡙ࡎࡒࡄࡠࡗࡕࡐࠧᓇ")),
            bstack111l11_opy_ (u"ࠢ࡫ࡱࡥࡣࡳࡧ࡭ࡦࠤᓈ"): env.get(bstack111l11_opy_ (u"ࠣࡅࡉࡣࡕࡏࡐࡆࡎࡌࡒࡊࡥࡎࡂࡏࡈࠦᓉ")),
            bstack111l11_opy_ (u"ࠤࡥࡹ࡮ࡲࡤࡠࡰࡸࡱࡧ࡫ࡲࠣᓊ"): env.get(bstack111l11_opy_ (u"ࠥࡇࡋࡥࡂࡖࡋࡏࡈࡤࡏࡄࠣᓋ"))
        }
    return {bstack111l11_opy_ (u"ࠦࡧࡻࡩ࡭ࡦࡢࡲࡺࡳࡢࡦࡴࠥᓌ"): None}
def get_host_info():
    return {
        bstack111l11_opy_ (u"ࠧ࡮࡯ࡴࡶࡱࡥࡲ࡫ࠢᓍ"): platform.node(),
        bstack111l11_opy_ (u"ࠨࡰ࡭ࡣࡷࡪࡴࡸ࡭ࠣᓎ"): platform.system(),
        bstack111l11_opy_ (u"ࠢࡵࡻࡳࡩࠧᓏ"): platform.machine(),
        bstack111l11_opy_ (u"ࠣࡸࡨࡶࡸ࡯࡯࡯ࠤᓐ"): platform.version(),
        bstack111l11_opy_ (u"ࠤࡤࡶࡨ࡮ࠢᓑ"): platform.architecture()[0]
    }
def bstack1lllll11l_opy_():
    try:
        import selenium
        return True
    except ImportError:
        return False
def bstack1llll11llll_opy_():
    if bstack1l1ll11l1l_opy_.get_property(bstack111l11_opy_ (u"ࠪࡦࡸࡺࡡࡤ࡭ࡢࡷࡪࡹࡳࡪࡱࡱࠫᓒ")):
        return bstack111l11_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࠪᓓ")
    return bstack111l11_opy_ (u"ࠬࡻ࡮࡬ࡰࡲࡻࡳࡥࡧࡳ࡫ࡧࠫᓔ")
def bstack1lll1ll11ll_opy_(driver):
    info = {
        bstack111l11_opy_ (u"࠭ࡣࡢࡲࡤࡦ࡮ࡲࡩࡵ࡫ࡨࡷࠬᓕ"): driver.capabilities,
        bstack111l11_opy_ (u"ࠧࡴࡧࡶࡷ࡮ࡵ࡮ࡠ࡫ࡧࠫᓖ"): driver.session_id,
        bstack111l11_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࠩᓗ"): driver.capabilities.get(bstack111l11_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡑࡥࡲ࡫ࠧᓘ"), None),
        bstack111l11_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡣࡻ࡫ࡲࡴ࡫ࡲࡲࠬᓙ"): driver.capabilities.get(bstack111l11_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶ࡛࡫ࡲࡴ࡫ࡲࡲࠬᓚ"), None),
        bstack111l11_opy_ (u"ࠬࡶ࡬ࡢࡶࡩࡳࡷࡳࠧᓛ"): driver.capabilities.get(bstack111l11_opy_ (u"࠭ࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡏࡣࡰࡩࠬᓜ"), None),
    }
    if bstack1llll11llll_opy_() == bstack111l11_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠭ᓝ"):
        if bstack1l11lll11l_opy_():
            info[bstack111l11_opy_ (u"ࠨࡲࡵࡳࡩࡻࡣࡵࠩᓞ")] = bstack111l11_opy_ (u"ࠩࡤࡴࡵ࠳ࡡࡶࡶࡲࡱࡦࡺࡥࠨᓟ")
        elif driver.capabilities.get(bstack111l11_opy_ (u"ࠪࡦࡸࡺࡡࡤ࡭࠽ࡳࡵࡺࡩࡰࡰࡶࠫᓠ"), {}).get(bstack111l11_opy_ (u"ࠫࡹࡻࡲࡣࡱࡶࡧࡦࡲࡥࠨᓡ"), False):
            info[bstack111l11_opy_ (u"ࠬࡶࡲࡰࡦࡸࡧࡹ࠭ᓢ")] = bstack111l11_opy_ (u"࠭ࡴࡶࡴࡥࡳࡸࡩࡡ࡭ࡧࠪᓣ")
        else:
            info[bstack111l11_opy_ (u"ࠧࡱࡴࡲࡨࡺࡩࡴࠨᓤ")] = bstack111l11_opy_ (u"ࠨࡣࡸࡸࡴࡳࡡࡵࡧࠪᓥ")
    return info
def bstack1l11lll11l_opy_():
    if bstack1l1ll11l1l_opy_.get_property(bstack111l11_opy_ (u"ࠩࡤࡴࡵࡥࡡࡶࡶࡲࡱࡦࡺࡥࠨᓦ")):
        return True
    if bstack11ll111l11_opy_(os.environ.get(bstack111l11_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡌࡗࡤࡇࡐࡑࡡࡄ࡙࡙ࡕࡍࡂࡖࡈࠫᓧ"), None)):
        return True
    return False
def bstack11llllll_opy_(bstack1lll1lllll1_opy_, url, data, config):
    headers = config.get(bstack111l11_opy_ (u"ࠫ࡭࡫ࡡࡥࡧࡵࡷࠬᓨ"), None)
    proxies = bstack1l11l111l_opy_(config, url)
    auth = config.get(bstack111l11_opy_ (u"ࠬࡧࡵࡵࡪࠪᓩ"), None)
    response = requests.request(
            bstack1lll1lllll1_opy_,
            url=url,
            headers=headers,
            auth=auth,
            json=data,
            proxies=proxies
        )
    return response
def bstack11llllll11_opy_(bstack1l1l1l111_opy_, size):
    bstack1l11ll1ll_opy_ = []
    while len(bstack1l1l1l111_opy_) > size:
        bstack1llll1lll1_opy_ = bstack1l1l1l111_opy_[:size]
        bstack1l11ll1ll_opy_.append(bstack1llll1lll1_opy_)
        bstack1l1l1l111_opy_ = bstack1l1l1l111_opy_[size:]
    bstack1l11ll1ll_opy_.append(bstack1l1l1l111_opy_)
    return bstack1l11ll1ll_opy_
def bstack1llll1ll1ll_opy_(message, bstack1lllll1l1l1_opy_=False):
    os.write(1, bytes(message, bstack111l11_opy_ (u"࠭ࡵࡵࡨ࠰࠼ࠬᓪ")))
    os.write(1, bytes(bstack111l11_opy_ (u"ࠧ࡝ࡰࠪᓫ"), bstack111l11_opy_ (u"ࠨࡷࡷࡪ࠲࠾ࠧᓬ")))
    if bstack1lllll1l1l1_opy_:
        with open(bstack111l11_opy_ (u"ࠩࡥࡷࡹࡧࡣ࡬࠯ࡲ࠵࠶ࡿ࠭ࠨᓭ") + os.environ[bstack111l11_opy_ (u"ࠪࡆࡘࡥࡔࡆࡕࡗࡓࡕ࡙࡟ࡃࡗࡌࡐࡉࡥࡈࡂࡕࡋࡉࡉࡥࡉࡅࠩᓮ")] + bstack111l11_opy_ (u"ࠫ࠳ࡲ࡯ࡨࠩᓯ"), bstack111l11_opy_ (u"ࠬࡧࠧᓰ")) as f:
            f.write(message + bstack111l11_opy_ (u"࠭࡜࡯ࠩᓱ"))
def bstack1lll1ll1l1l_opy_():
    return os.environ[bstack111l11_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡁࡖࡖࡒࡑࡆ࡚ࡉࡐࡐࠪᓲ")].lower() == bstack111l11_opy_ (u"ࠨࡶࡵࡹࡪ࠭ᓳ")
def bstack11llll1l1_opy_(bstack1lllllll111_opy_):
    return bstack111l11_opy_ (u"ࠩࡾࢁ࠴ࢁࡽࠨᓴ").format(bstack1111l11l1l_opy_, bstack1lllllll111_opy_)
def bstack1lll111ll_opy_():
    return bstack11l11l1l11_opy_().replace(tzinfo=None).isoformat() + bstack111l11_opy_ (u"ࠪ࡞ࠬᓵ")
def bstack1llllllllll_opy_(start, finish):
    return (datetime.datetime.fromisoformat(finish.rstrip(bstack111l11_opy_ (u"ࠫ࡟࠭ᓶ"))) - datetime.datetime.fromisoformat(start.rstrip(bstack111l11_opy_ (u"ࠬࡠࠧᓷ")))).total_seconds() * 1000
def bstack1111111l1l_opy_(timestamp):
    return bstack1lllll1l11l_opy_(timestamp).isoformat() + bstack111l11_opy_ (u"࡚࠭ࠨᓸ")
def bstack1llll11l1l1_opy_(bstack1llll1l1l1l_opy_):
    date_format = bstack111l11_opy_ (u"࡛ࠧࠦࠨࡱࠪࡪࠠࠦࡊ࠽ࠩࡒࡀࠥࡔ࠰ࠨࡪࠬᓹ")
    bstack1lll1ll1l11_opy_ = datetime.datetime.strptime(bstack1llll1l1l1l_opy_, date_format)
    return bstack1lll1ll1l11_opy_.isoformat() + bstack111l11_opy_ (u"ࠨ࡜ࠪᓺ")
def bstack1lll1lll1l1_opy_(outcome):
    _, exception, _ = outcome.excinfo or (None, None, None)
    if exception:
        return bstack111l11_opy_ (u"ࠩࡩࡥ࡮ࡲࡥࡥࠩᓻ")
    else:
        return bstack111l11_opy_ (u"ࠪࡴࡦࡹࡳࡦࡦࠪᓼ")
def bstack11ll111l11_opy_(val):
    if val is None:
        return False
    return val.__str__().lower() == bstack111l11_opy_ (u"ࠫࡹࡸࡵࡦࠩᓽ")
def bstack1lllll11l1l_opy_(val):
    return val.__str__().lower() == bstack111l11_opy_ (u"ࠬ࡬ࡡ࡭ࡵࡨࠫᓾ")
def bstack111lll1lll_opy_(bstack1llll1111l1_opy_=Exception, class_method=False, default_value=None):
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except bstack1llll1111l1_opy_ as e:
                print(bstack111l11_opy_ (u"ࠨࡅࡹࡥࡨࡴࡹ࡯࡯࡯ࠢ࡬ࡲࠥ࡬ࡵ࡯ࡥࡷ࡭ࡴࡴࠠࡼࡿࠣ࠱ࡃࠦࡻࡾ࠼ࠣࡿࢂࠨᓿ").format(func.__name__, bstack1llll1111l1_opy_.__name__, str(e)))
                return default_value
        return wrapper
    def bstack1lllllll1ll_opy_(bstack1llllll1lll_opy_):
        def wrapped(cls, *args, **kwargs):
            try:
                return bstack1llllll1lll_opy_(cls, *args, **kwargs)
            except bstack1llll1111l1_opy_ as e:
                print(bstack111l11_opy_ (u"ࠢࡆࡺࡦࡩࡵࡺࡩࡰࡰࠣ࡭ࡳࠦࡦࡶࡰࡦࡸ࡮ࡵ࡮ࠡࡽࢀࠤ࠲ࡄࠠࡼࡿ࠽ࠤࢀࢃࠢᔀ").format(bstack1llllll1lll_opy_.__name__, bstack1llll1111l1_opy_.__name__, str(e)))
                return default_value
        return wrapped
    if class_method:
        return bstack1lllllll1ll_opy_
    else:
        return decorator
def bstack1l111lll11_opy_(bstack111ll1111l_opy_):
    if bstack111l11_opy_ (u"ࠨࡣࡸࡸࡴࡳࡡࡵ࡫ࡲࡲࠬᔁ") in bstack111ll1111l_opy_ and bstack1lllll11l1l_opy_(bstack111ll1111l_opy_[bstack111l11_opy_ (u"ࠩࡤࡹࡹࡵ࡭ࡢࡶ࡬ࡳࡳ࠭ᔂ")]):
        return False
    if bstack111l11_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡃࡸࡸࡴࡳࡡࡵ࡫ࡲࡲࠬᔃ") in bstack111ll1111l_opy_ and bstack1lllll11l1l_opy_(bstack111ll1111l_opy_[bstack111l11_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡄࡹࡹࡵ࡭ࡢࡶ࡬ࡳࡳ࠭ᔄ")]):
        return False
    return True
def bstack1l111l11ll_opy_():
    try:
        from pytest_bdd import reporting
        bstack1lllllll1l1_opy_ = os.environ.get(bstack111l11_opy_ (u"ࠧࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣ࡚࡙ࡅࡓࡡࡉࡖࡆࡓࡅࡘࡑࡕࡏࠧᔅ"), None)
        return bstack1lllllll1l1_opy_ is None or bstack1lllllll1l1_opy_ == bstack111l11_opy_ (u"ࠨࡰࡺࡶࡨࡷࡹ࠳ࡢࡥࡦࠥᔆ")
    except Exception as e:
        return False
def bstack111l111ll_opy_(hub_url, CONFIG):
    if bstack11ll11111l_opy_() <= version.parse(bstack111l11_opy_ (u"ࠧ࠴࠰࠴࠷࠳࠶ࠧᔇ")):
        if hub_url != bstack111l11_opy_ (u"ࠨࠩᔈ"):
            return bstack111l11_opy_ (u"ࠤ࡫ࡸࡹࡶ࠺࠰࠱ࠥᔉ") + hub_url + bstack111l11_opy_ (u"ࠥ࠾࠽࠶࠯ࡸࡦ࠲࡬ࡺࡨࠢᔊ")
        return bstack1ll1l11111_opy_
    if hub_url != bstack111l11_opy_ (u"ࠫࠬᔋ"):
        return bstack111l11_opy_ (u"ࠧ࡮ࡴࡵࡲࡶ࠾࠴࠵ࠢᔌ") + hub_url + bstack111l11_opy_ (u"ࠨ࠯ࡸࡦ࠲࡬ࡺࡨࠢᔍ")
    return bstack11l1l11ll_opy_
def bstack1lllll1llll_opy_():
    return isinstance(os.getenv(bstack111l11_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡐ࡚ࡖࡈࡗ࡙ࡥࡐࡍࡗࡊࡍࡓ࠭ᔎ")), str)
def bstack1lllllllll_opy_(url):
    return urlparse(url).hostname
def bstack11111l11l_opy_(hostname):
    for bstack1ll11ll1_opy_ in bstack1lll11l1ll_opy_:
        regex = re.compile(bstack1ll11ll1_opy_)
        if regex.match(hostname):
            return True
    return False
def bstack1lll1llllll_opy_(bstack1lllll1l111_opy_, file_name, logger):
    bstack1llll1l1l1_opy_ = os.path.join(os.path.expanduser(bstack111l11_opy_ (u"ࠨࢀࠪᔏ")), bstack1lllll1l111_opy_)
    try:
        if not os.path.exists(bstack1llll1l1l1_opy_):
            os.makedirs(bstack1llll1l1l1_opy_)
        file_path = os.path.join(os.path.expanduser(bstack111l11_opy_ (u"ࠩࢁࠫᔐ")), bstack1lllll1l111_opy_, file_name)
        if not os.path.isfile(file_path):
            with open(file_path, bstack111l11_opy_ (u"ࠪࡻࠬᔑ")):
                pass
            with open(file_path, bstack111l11_opy_ (u"ࠦࡼ࠱ࠢᔒ")) as outfile:
                json.dump({}, outfile)
        return file_path
    except Exception as e:
        logger.debug(bstack1lll11lll1_opy_.format(str(e)))
def bstack1lllllllll1_opy_(file_name, key, value, logger):
    file_path = bstack1lll1llllll_opy_(bstack111l11_opy_ (u"ࠬ࠴ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࠬᔓ"), file_name, logger)
    if file_path != None:
        if os.path.exists(file_path):
            bstack11111111l_opy_ = json.load(open(file_path, bstack111l11_opy_ (u"࠭ࡲࡣࠩᔔ")))
        else:
            bstack11111111l_opy_ = {}
        bstack11111111l_opy_[key] = value
        with open(file_path, bstack111l11_opy_ (u"ࠢࡸ࠭ࠥᔕ")) as outfile:
            json.dump(bstack11111111l_opy_, outfile)
def bstack1ll11llll_opy_(file_name, logger):
    file_path = bstack1lll1llllll_opy_(bstack111l11_opy_ (u"ࠨ࠰ࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࠨᔖ"), file_name, logger)
    bstack11111111l_opy_ = {}
    if file_path != None and os.path.exists(file_path):
        with open(file_path, bstack111l11_opy_ (u"ࠩࡵࠫᔗ")) as bstack1l1111111l_opy_:
            bstack11111111l_opy_ = json.load(bstack1l1111111l_opy_)
    return bstack11111111l_opy_
def bstack1l1ll1ll11_opy_(file_path, logger):
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        logger.debug(bstack111l11_opy_ (u"ࠪࡉࡷࡸ࡯ࡳࠢ࡬ࡲࠥࡪࡥ࡭ࡧࡷ࡭ࡳ࡭ࠠࡧ࡫࡯ࡩ࠿ࠦࠧᔘ") + file_path + bstack111l11_opy_ (u"ࠫࠥ࠭ᔙ") + str(e))
def bstack11ll11111l_opy_():
    from selenium import webdriver
    return version.parse(webdriver.__version__)
class Notset:
    def __repr__(self):
        return bstack111l11_opy_ (u"ࠧࡂࡎࡐࡖࡖࡉ࡙ࡄࠢᔚ")
def bstack1llll1111l_opy_(config):
    if bstack111l11_opy_ (u"࠭ࡩࡴࡒ࡯ࡥࡾࡽࡲࡪࡩ࡫ࡸࠬᔛ") in config:
        del (config[bstack111l11_opy_ (u"ࠧࡪࡵࡓࡰࡦࡿࡷࡳ࡫ࡪ࡬ࡹ࠭ᔜ")])
        return False
    if bstack11ll11111l_opy_() < version.parse(bstack111l11_opy_ (u"ࠨ࠵࠱࠸࠳࠶ࠧᔝ")):
        return False
    if bstack11ll11111l_opy_() >= version.parse(bstack111l11_opy_ (u"ࠩ࠷࠲࠶࠴࠵ࠨᔞ")):
        return True
    if bstack111l11_opy_ (u"ࠪࡹࡸ࡫ࡗ࠴ࡅࠪᔟ") in config and config[bstack111l11_opy_ (u"ࠫࡺࡹࡥࡘ࠵ࡆࠫᔠ")] is False:
        return False
    else:
        return True
def bstack11ll11llll_opy_(args_list, bstack1lllll11ll1_opy_):
    index = -1
    for value in bstack1lllll11ll1_opy_:
        try:
            index = args_list.index(value)
            return index
        except Exception as e:
            return index
    return index
class Result:
    def __init__(self, result=None, duration=None, exception=None, bstack11l1lll111_opy_=None):
        self.result = result
        self.duration = duration
        self.exception = exception
        self.exception_type = type(self.exception).__name__ if exception else None
        self.bstack11l1lll111_opy_ = bstack11l1lll111_opy_
    @classmethod
    def passed(cls):
        return Result(result=bstack111l11_opy_ (u"ࠬࡶࡡࡴࡵࡨࡨࠬᔡ"))
    @classmethod
    def failed(cls, exception=None):
        return Result(result=bstack111l11_opy_ (u"࠭ࡦࡢ࡫࡯ࡩࡩ࠭ᔢ"), exception=exception)
    def bstack111l1lll11_opy_(self):
        if self.result != bstack111l11_opy_ (u"ࠧࡧࡣ࡬ࡰࡪࡪࠧᔣ"):
            return None
        if isinstance(self.exception_type, str) and bstack111l11_opy_ (u"ࠣࡃࡶࡷࡪࡸࡴࡪࡱࡱࠦᔤ") in self.exception_type:
            return bstack111l11_opy_ (u"ࠤࡄࡷࡸ࡫ࡲࡵ࡫ࡲࡲࡊࡸࡲࡰࡴࠥᔥ")
        return bstack111l11_opy_ (u"࡙ࠥࡳ࡮ࡡ࡯ࡦ࡯ࡩࡩࡋࡲࡳࡱࡵࠦᔦ")
    def bstack1llll11l11l_opy_(self):
        if self.result != bstack111l11_opy_ (u"ࠫ࡫ࡧࡩ࡭ࡧࡧࠫᔧ"):
            return None
        if self.bstack11l1lll111_opy_:
            return self.bstack11l1lll111_opy_
        return bstack1lll1ll1lll_opy_(self.exception)
def bstack1lll1ll1lll_opy_(exc):
    return [traceback.format_exception(exc)]
def bstack1lllllll11l_opy_(message):
    if isinstance(message, str):
        return not bool(message and message.strip())
    return True
def bstack1l1l11ll11_opy_(object, key, default_value):
    if not object or not object.__dict__:
        return default_value
    if key in object.__dict__.keys():
        return object.__dict__.get(key)
    return default_value
def bstack1llll11ll_opy_(config, logger):
    try:
        import playwright
        bstack1111111ll1_opy_ = playwright.__file__
        bstack1llllll1l11_opy_ = os.path.split(bstack1111111ll1_opy_)
        bstack1llllll11l1_opy_ = bstack1llllll1l11_opy_[0] + bstack111l11_opy_ (u"ࠬ࠵ࡤࡳ࡫ࡹࡩࡷ࠵ࡰࡢࡥ࡮ࡥ࡬࡫࠯࡭࡫ࡥ࠳ࡨࡲࡩ࠰ࡥ࡯࡭࠳ࡰࡳࠨᔨ")
        os.environ[bstack111l11_opy_ (u"࠭ࡇࡍࡑࡅࡅࡑࡥࡁࡈࡇࡑࡘࡤࡎࡔࡕࡒࡢࡔࡗࡕࡘ࡚ࠩᔩ")] = bstack1ll11lll1l_opy_(config)
        with open(bstack1llllll11l1_opy_, bstack111l11_opy_ (u"ࠧࡳࠩᔪ")) as f:
            bstack1ll1ll1111_opy_ = f.read()
            bstack1llll11l1ll_opy_ = bstack111l11_opy_ (u"ࠨࡩ࡯ࡳࡧࡧ࡬࠮ࡣࡪࡩࡳࡺࠧᔫ")
            bstack111111l111_opy_ = bstack1ll1ll1111_opy_.find(bstack1llll11l1ll_opy_)
            if bstack111111l111_opy_ == -1:
              process = subprocess.Popen(bstack111l11_opy_ (u"ࠤࡱࡴࡲࠦࡩ࡯ࡵࡷࡥࡱࡲࠠࡨ࡮ࡲࡦࡦࡲ࠭ࡢࡩࡨࡲࡹࠨᔬ"), shell=True, cwd=bstack1llllll1l11_opy_[0])
              process.wait()
              bstack1llll11111l_opy_ = bstack111l11_opy_ (u"ࠪࠦࡺࡹࡥࠡࡵࡷࡶ࡮ࡩࡴࠣ࠽ࠪᔭ")
              bstack1lll1llll11_opy_ = bstack111l11_opy_ (u"ࠦࠧࠨࠠ࡝ࠤࡸࡷࡪࠦࡳࡵࡴ࡬ࡧࡹࡢࠢ࠼ࠢࡦࡳࡳࡹࡴࠡࡽࠣࡦࡴࡵࡴࡴࡶࡵࡥࡵࠦࡽࠡ࠿ࠣࡶࡪࡷࡵࡪࡴࡨࠬࠬ࡭࡬ࡰࡤࡤࡰ࠲ࡧࡧࡦࡰࡷࠫ࠮ࡁࠠࡪࡨࠣࠬࡵࡸ࡯ࡤࡧࡶࡷ࠳࡫࡮ࡷ࠰ࡊࡐࡔࡈࡁࡍࡡࡄࡋࡊࡔࡔࡠࡊࡗࡘࡕࡥࡐࡓࡑ࡛࡝࠮ࠦࡢࡰࡱࡷࡷࡹࡸࡡࡱࠪࠬ࠿ࠥࠨࠢࠣᔮ")
              bstack1lll1ll1ll1_opy_ = bstack1ll1ll1111_opy_.replace(bstack1llll11111l_opy_, bstack1lll1llll11_opy_)
              with open(bstack1llllll11l1_opy_, bstack111l11_opy_ (u"ࠬࡽࠧᔯ")) as f:
                f.write(bstack1lll1ll1ll1_opy_)
    except Exception as e:
        logger.error(bstack1lll1l11ll_opy_.format(str(e)))
def bstack1l11111ll1_opy_():
  try:
    bstack1llll1l1ll1_opy_ = os.path.join(tempfile.gettempdir(), bstack111l11_opy_ (u"࠭࡯ࡱࡶ࡬ࡱࡦࡲ࡟ࡩࡷࡥࡣࡺࡸ࡬࠯࡬ࡶࡳࡳ࠭ᔰ"))
    bstack1lllll11lll_opy_ = []
    if os.path.exists(bstack1llll1l1ll1_opy_):
      with open(bstack1llll1l1ll1_opy_) as f:
        bstack1lllll11lll_opy_ = json.load(f)
      os.remove(bstack1llll1l1ll1_opy_)
    return bstack1lllll11lll_opy_
  except:
    pass
  return []
def bstack1lll11l1l1_opy_(bstack111ll11l1_opy_):
  try:
    bstack1lllll11lll_opy_ = []
    bstack1llll1l1ll1_opy_ = os.path.join(tempfile.gettempdir(), bstack111l11_opy_ (u"ࠧࡰࡲࡷ࡭ࡲࡧ࡬ࡠࡪࡸࡦࡤࡻࡲ࡭࠰࡭ࡷࡴࡴࠧᔱ"))
    if os.path.exists(bstack1llll1l1ll1_opy_):
      with open(bstack1llll1l1ll1_opy_) as f:
        bstack1lllll11lll_opy_ = json.load(f)
    bstack1lllll11lll_opy_.append(bstack111ll11l1_opy_)
    with open(bstack1llll1l1ll1_opy_, bstack111l11_opy_ (u"ࠨࡹࠪᔲ")) as f:
        json.dump(bstack1lllll11lll_opy_, f)
  except:
    pass
def bstack11lllll11l_opy_(logger, bstack1llllllll1l_opy_ = False):
  try:
    test_name = os.environ.get(bstack111l11_opy_ (u"ࠩࡓ࡝࡙ࡋࡓࡕࡡࡗࡉࡘ࡚࡟ࡏࡃࡐࡉࠬᔳ"), bstack111l11_opy_ (u"ࠪࠫᔴ"))
    if test_name == bstack111l11_opy_ (u"ࠫࠬᔵ"):
        test_name = threading.current_thread().__dict__.get(bstack111l11_opy_ (u"ࠬࡶࡹࡵࡧࡶࡸࡇࡪࡤࡠࡶࡨࡷࡹࡥ࡮ࡢ࡯ࡨࠫᔶ"), bstack111l11_opy_ (u"࠭ࠧᔷ"))
    bstack11111111ll_opy_ = bstack111l11_opy_ (u"ࠧ࠭ࠢࠪᔸ").join(threading.current_thread().bstackTestErrorMessages)
    if bstack1llllllll1l_opy_:
        bstack111ll111_opy_ = os.environ.get(bstack111l11_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡑࡎࡄࡘࡋࡕࡒࡎࡡࡌࡒࡉࡋࡘࠨᔹ"), bstack111l11_opy_ (u"ࠩ࠳ࠫᔺ"))
        bstack11ll1ll11_opy_ = {bstack111l11_opy_ (u"ࠪࡲࡦࡳࡥࠨᔻ"): test_name, bstack111l11_opy_ (u"ࠫࡪࡸࡲࡰࡴࠪᔼ"): bstack11111111ll_opy_, bstack111l11_opy_ (u"ࠬ࡯࡮ࡥࡧࡻࠫᔽ"): bstack111ll111_opy_}
        bstack1llll1lllll_opy_ = []
        bstack1lllll111l1_opy_ = os.path.join(tempfile.gettempdir(), bstack111l11_opy_ (u"࠭ࡰࡺࡶࡨࡷࡹࡥࡰࡱࡲࡢࡩࡷࡸ࡯ࡳࡡ࡯࡭ࡸࡺ࠮࡫ࡵࡲࡲࠬᔾ"))
        if os.path.exists(bstack1lllll111l1_opy_):
            with open(bstack1lllll111l1_opy_) as f:
                bstack1llll1lllll_opy_ = json.load(f)
        bstack1llll1lllll_opy_.append(bstack11ll1ll11_opy_)
        with open(bstack1lllll111l1_opy_, bstack111l11_opy_ (u"ࠧࡸࠩᔿ")) as f:
            json.dump(bstack1llll1lllll_opy_, f)
    else:
        bstack11ll1ll11_opy_ = {bstack111l11_opy_ (u"ࠨࡰࡤࡱࡪ࠭ᕀ"): test_name, bstack111l11_opy_ (u"ࠩࡨࡶࡷࡵࡲࠨᕁ"): bstack11111111ll_opy_, bstack111l11_opy_ (u"ࠪ࡭ࡳࡪࡥࡹࠩᕂ"): str(multiprocessing.current_process().name)}
        if bstack111l11_opy_ (u"ࠫࡧࡹࡴࡢࡥ࡮ࡣࡪࡸࡲࡰࡴࡢࡰ࡮ࡹࡴࠨᕃ") not in multiprocessing.current_process().__dict__.keys():
            multiprocessing.current_process().bstack_error_list = []
        multiprocessing.current_process().bstack_error_list.append(bstack11ll1ll11_opy_)
  except Exception as e:
      logger.warn(bstack111l11_opy_ (u"࡛ࠧ࡮ࡢࡤ࡯ࡩࠥࡺ࡯ࠡࡵࡷࡳࡷ࡫ࠠࡱࡻࡷࡩࡸࡺࠠࡧࡷࡱࡲࡪࡲࠠࡥࡣࡷࡥ࠿ࠦࡻࡾࠤᕄ").format(e))
def bstack11l111l1l_opy_(error_message, test_name, index, logger):
  try:
    bstack1llll111lll_opy_ = []
    bstack11ll1ll11_opy_ = {bstack111l11_opy_ (u"࠭࡮ࡢ࡯ࡨࠫᕅ"): test_name, bstack111l11_opy_ (u"ࠧࡦࡴࡵࡳࡷ࠭ᕆ"): error_message, bstack111l11_opy_ (u"ࠨ࡫ࡱࡨࡪࡾࠧᕇ"): index}
    bstack1llll11lll1_opy_ = os.path.join(tempfile.gettempdir(), bstack111l11_opy_ (u"ࠩࡵࡳࡧࡵࡴࡠࡧࡵࡶࡴࡸ࡟࡭࡫ࡶࡸ࠳ࡰࡳࡰࡰࠪᕈ"))
    if os.path.exists(bstack1llll11lll1_opy_):
        with open(bstack1llll11lll1_opy_) as f:
            bstack1llll111lll_opy_ = json.load(f)
    bstack1llll111lll_opy_.append(bstack11ll1ll11_opy_)
    with open(bstack1llll11lll1_opy_, bstack111l11_opy_ (u"ࠪࡻࠬᕉ")) as f:
        json.dump(bstack1llll111lll_opy_, f)
  except Exception as e:
    logger.warn(bstack111l11_opy_ (u"࡚ࠦࡴࡡࡣ࡮ࡨࠤࡹࡵࠠࡴࡶࡲࡶࡪࠦࡲࡰࡤࡲࡸࠥ࡬ࡵ࡯ࡰࡨࡰࠥࡪࡡࡵࡣ࠽ࠤࢀࢃࠢᕊ").format(e))
def bstack1l1lll11l_opy_(bstack1ll1ll1ll_opy_, name, logger):
  try:
    bstack11ll1ll11_opy_ = {bstack111l11_opy_ (u"ࠬࡴࡡ࡮ࡧࠪᕋ"): name, bstack111l11_opy_ (u"࠭ࡥࡳࡴࡲࡶࠬᕌ"): bstack1ll1ll1ll_opy_, bstack111l11_opy_ (u"ࠧࡪࡰࡧࡩࡽ࠭ᕍ"): str(threading.current_thread()._name)}
    return bstack11ll1ll11_opy_
  except Exception as e:
    logger.warn(bstack111l11_opy_ (u"ࠣࡗࡱࡥࡧࡲࡥࠡࡶࡲࠤࡸࡺ࡯ࡳࡧࠣࡦࡪ࡮ࡡࡷࡧࠣࡪࡺࡴ࡮ࡦ࡮ࠣࡨࡦࡺࡡ࠻ࠢࡾࢁࠧᕎ").format(e))
  return
def bstack1lllll11l11_opy_():
    return platform.system() == bstack111l11_opy_ (u"࡚ࠩ࡭ࡳࡪ࡯ࡸࡵࠪᕏ")
def bstack1ll1111ll_opy_(bstack1111111lll_opy_, config, logger):
    bstack1llll1l1lll_opy_ = {}
    try:
        return {key: config[key] for key in config if bstack1111111lll_opy_.match(key)}
    except Exception as e:
        logger.debug(bstack111l11_opy_ (u"࡙ࠥࡳࡧࡢ࡭ࡧࠣࡸࡴࠦࡦࡪ࡮ࡷࡩࡷࠦࡣࡰࡰࡩ࡭࡬ࠦ࡫ࡦࡻࡶࠤࡧࡿࠠࡳࡧࡪࡩࡽࠦ࡭ࡢࡶࡦ࡬࠿ࠦࡻࡾࠤᕐ").format(e))
    return bstack1llll1l1lll_opy_
def bstack1llll111ll1_opy_(bstack1llllll111l_opy_, bstack1lll1lll111_opy_):
    bstack1llll1l111l_opy_ = version.parse(bstack1llllll111l_opy_)
    bstack1llll1111ll_opy_ = version.parse(bstack1lll1lll111_opy_)
    if bstack1llll1l111l_opy_ > bstack1llll1111ll_opy_:
        return 1
    elif bstack1llll1l111l_opy_ < bstack1llll1111ll_opy_:
        return -1
    else:
        return 0
def bstack11l11l1l11_opy_():
    return datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
def bstack1lllll1l11l_opy_(timestamp):
    return datetime.datetime.fromtimestamp(timestamp, datetime.timezone.utc).replace(tzinfo=None)
def bstack1111111111_opy_(framework):
    from browserstack_sdk._version import __version__
    return str(framework) + str(__version__)
def bstack1l1l11lll1_opy_(options, framework, bstack1lll11l11_opy_={}):
    if options is None:
        return
    if getattr(options, bstack111l11_opy_ (u"ࠫ࡬࡫ࡴࠨᕑ"), None):
        caps = options
    else:
        caps = options.to_capabilities()
    bstack1lllllll1_opy_ = caps.get(bstack111l11_opy_ (u"ࠬࡨࡳࡵࡣࡦ࡯࠿ࡵࡰࡵ࡫ࡲࡲࡸ࠭ᕒ"))
    bstack1llll111111_opy_ = True
    bstack1l1111llll_opy_ = os.environ[bstack111l11_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤ࡚ࡅࡔࡖࡋ࡙ࡇࡥࡕࡖࡋࡇࠫᕓ")]
    if bstack1lllll11l1l_opy_(caps.get(bstack111l11_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡵࡴࡧ࡚࠷ࡈ࠭ᕔ"))) or bstack1lllll11l1l_opy_(caps.get(bstack111l11_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡶࡵࡨࡣࡼ࠹ࡣࠨᕕ"))):
        bstack1llll111111_opy_ = False
    if bstack1llll1111l_opy_({bstack111l11_opy_ (u"ࠤࡸࡷࡪ࡝࠳ࡄࠤᕖ"): bstack1llll111111_opy_}):
        bstack1lllllll1_opy_ = bstack1lllllll1_opy_ or {}
        bstack1lllllll1_opy_[bstack111l11_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡕࡇࡏࠬᕗ")] = bstack1111111111_opy_(framework)
        bstack1lllllll1_opy_[bstack111l11_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡄࡹࡹࡵ࡭ࡢࡶ࡬ࡳࡳ࠭ᕘ")] = bstack1lll1ll1l1l_opy_()
        bstack1lllllll1_opy_[bstack111l11_opy_ (u"ࠬࡺࡥࡴࡶ࡫ࡹࡧࡈࡵࡪ࡮ࡧ࡙ࡺ࡯ࡤࠨᕙ")] = bstack1l1111llll_opy_
        bstack1lllllll1_opy_[bstack111l11_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡕࡸ࡯ࡥࡷࡦࡸࡒࡧࡰࠨᕚ")] = bstack1lll11l11_opy_
        if getattr(options, bstack111l11_opy_ (u"ࠧࡴࡧࡷࡣࡨࡧࡰࡢࡤ࡬ࡰ࡮ࡺࡹࠨᕛ"), None):
            options.set_capability(bstack111l11_opy_ (u"ࠨࡤࡶࡸࡦࡩ࡫࠻ࡱࡳࡸ࡮ࡵ࡮ࡴࠩᕜ"), bstack1lllllll1_opy_)
        else:
            options[bstack111l11_opy_ (u"ࠩࡥࡷࡹࡧࡣ࡬࠼ࡲࡴࡹ࡯࡯࡯ࡵࠪᕝ")] = bstack1lllllll1_opy_
    else:
        if getattr(options, bstack111l11_opy_ (u"ࠪࡷࡪࡺ࡟ࡤࡣࡳࡥࡧ࡯࡬ࡪࡶࡼࠫᕞ"), None):
            options.set_capability(bstack111l11_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡕࡇࡏࠬᕟ"), bstack1111111111_opy_(framework))
            options.set_capability(bstack111l11_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡄࡹࡹࡵ࡭ࡢࡶ࡬ࡳࡳ࠭ᕠ"), bstack1lll1ll1l1l_opy_())
            options.set_capability(bstack111l11_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡺࡥࡴࡶ࡫ࡹࡧࡈࡵࡪ࡮ࡧ࡙ࡺ࡯ࡤࠨᕡ"), bstack1l1111llll_opy_)
            options.set_capability(bstack111l11_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡢࡶ࡫࡯ࡨࡕࡸ࡯ࡥࡷࡦࡸࡒࡧࡰࠨᕢ"), bstack1lll11l11_opy_)
        else:
            options[bstack111l11_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࡙ࡄࡌࠩᕣ")] = bstack1111111111_opy_(framework)
            options[bstack111l11_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࡁࡶࡶࡲࡱࡦࡺࡩࡰࡰࠪᕤ")] = bstack1lll1ll1l1l_opy_()
            options[bstack111l11_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡷࡩࡸࡺࡨࡶࡤࡅࡹ࡮ࡲࡤࡖࡷ࡬ࡨࠬᕥ")] = bstack1l1111llll_opy_
            options[bstack111l11_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡦࡺ࡯࡬ࡥࡒࡵࡳࡩࡻࡣࡵࡏࡤࡴࠬᕦ")] = bstack1lll11l11_opy_
    return options
def bstack1lllll1l1ll_opy_(bstack1llll111l11_opy_, framework):
    bstack1lll11l11_opy_ = bstack1l1ll11l1l_opy_.get_property(bstack111l11_opy_ (u"ࠧࡖࡌࡂ࡛࡚ࡖࡎࡍࡈࡕࡡࡓࡖࡔࡊࡕࡄࡖࡢࡑࡆࡖࠢᕧ"))
    if bstack1llll111l11_opy_ and len(bstack1llll111l11_opy_.split(bstack111l11_opy_ (u"࠭ࡣࡢࡲࡶࡁࠬᕨ"))) > 1:
        ws_url = bstack1llll111l11_opy_.split(bstack111l11_opy_ (u"ࠧࡤࡣࡳࡷࡂ࠭ᕩ"))[0]
        if bstack111l11_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡤࡱࡰࠫᕪ") in ws_url:
            from browserstack_sdk._version import __version__
            bstack1lllll1ll11_opy_ = json.loads(urllib.parse.unquote(bstack1llll111l11_opy_.split(bstack111l11_opy_ (u"ࠩࡦࡥࡵࡹ࠽ࠨᕫ"))[1]))
            bstack1lllll1ll11_opy_ = bstack1lllll1ll11_opy_ or {}
            bstack1l1111llll_opy_ = os.environ[bstack111l11_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡗࡉࡘ࡚ࡈࡖࡄࡢ࡙࡚ࡏࡄࠨᕬ")]
            bstack1lllll1ll11_opy_[bstack111l11_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡕࡇࡏࠬᕭ")] = str(framework) + str(__version__)
            bstack1lllll1ll11_opy_[bstack111l11_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡄࡹࡹࡵ࡭ࡢࡶ࡬ࡳࡳ࠭ᕮ")] = bstack1lll1ll1l1l_opy_()
            bstack1lllll1ll11_opy_[bstack111l11_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡺࡥࡴࡶ࡫ࡹࡧࡈࡵࡪ࡮ࡧ࡙ࡺ࡯ࡤࠨᕯ")] = bstack1l1111llll_opy_
            bstack1lllll1ll11_opy_[bstack111l11_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡢࡶ࡫࡯ࡨࡕࡸ࡯ࡥࡷࡦࡸࡒࡧࡰࠨᕰ")] = bstack1lll11l11_opy_
            bstack1llll111l11_opy_ = bstack1llll111l11_opy_.split(bstack111l11_opy_ (u"ࠨࡥࡤࡴࡸࡃࠧᕱ"))[0] + bstack111l11_opy_ (u"ࠩࡦࡥࡵࡹ࠽ࠨᕲ") + urllib.parse.quote(json.dumps(bstack1lllll1ll11_opy_))
    return bstack1llll111l11_opy_
def bstack1l11ll1111_opy_():
    global bstack111llll1l_opy_
    from playwright._impl._browser_type import BrowserType
    bstack111llll1l_opy_ = BrowserType.connect
    return bstack111llll1l_opy_
def bstack11l1llllll_opy_(framework_name):
    global bstack1lll1l1ll_opy_
    bstack1lll1l1ll_opy_ = framework_name
    return framework_name
def bstack1ll1l1l1ll_opy_(self, *args, **kwargs):
    global bstack111llll1l_opy_
    try:
        global bstack1lll1l1ll_opy_
        if bstack111l11_opy_ (u"ࠪࡻࡸࡋ࡮ࡥࡲࡲ࡭ࡳࡺࠧᕳ") in kwargs:
            kwargs[bstack111l11_opy_ (u"ࠫࡼࡹࡅ࡯ࡦࡳࡳ࡮ࡴࡴࠨᕴ")] = bstack1lllll1l1ll_opy_(
                kwargs.get(bstack111l11_opy_ (u"ࠬࡽࡳࡆࡰࡧࡴࡴ࡯࡮ࡵࠩᕵ"), None),
                bstack1lll1l1ll_opy_
            )
    except Exception as e:
        logger.error(bstack111l11_opy_ (u"ࠨࡅࡳࡴࡲࡶࠥࡽࡨࡦࡰࠣࡴࡷࡵࡣࡦࡵࡶ࡭ࡳ࡭ࠠࡔࡆࡎࠤࡨࡧࡰࡴ࠼ࠣࡿࢂࠨᕶ").format(str(e)))
    return bstack111llll1l_opy_(self, *args, **kwargs)
def bstack1lllll1ll1l_opy_(bstack1lllll11111_opy_, proxies):
    proxy_settings = {}
    try:
        if not proxies:
            proxies = bstack1l11l111l_opy_(bstack1lllll11111_opy_, bstack111l11_opy_ (u"ࠢࠣᕷ"))
        if proxies and proxies.get(bstack111l11_opy_ (u"ࠣࡪࡷࡸࡵࡹࠢᕸ")):
            parsed_url = urlparse(proxies.get(bstack111l11_opy_ (u"ࠤ࡫ࡸࡹࡶࡳࠣᕹ")))
            if parsed_url and parsed_url.hostname: proxy_settings[bstack111l11_opy_ (u"ࠪࡴࡷࡵࡸࡺࡊࡲࡷࡹ࠭ᕺ")] = str(parsed_url.hostname)
            if parsed_url and parsed_url.port: proxy_settings[bstack111l11_opy_ (u"ࠫࡵࡸ࡯ࡹࡻࡓࡳࡷࡺࠧᕻ")] = str(parsed_url.port)
            if parsed_url and parsed_url.username: proxy_settings[bstack111l11_opy_ (u"ࠬࡶࡲࡰࡺࡼ࡙ࡸ࡫ࡲࠨᕼ")] = str(parsed_url.username)
            if parsed_url and parsed_url.password: proxy_settings[bstack111l11_opy_ (u"࠭ࡰࡳࡱࡻࡽࡕࡧࡳࡴࠩᕽ")] = str(parsed_url.password)
        return proxy_settings
    except:
        return proxy_settings
def bstack111l1111_opy_(bstack1lllll11111_opy_):
    bstack1llllll1111_opy_ = {
        bstack11111ll11l_opy_[bstack1llll1l11ll_opy_]: bstack1lllll11111_opy_[bstack1llll1l11ll_opy_]
        for bstack1llll1l11ll_opy_ in bstack1lllll11111_opy_
        if bstack1llll1l11ll_opy_ in bstack11111ll11l_opy_
    }
    bstack1llllll1111_opy_[bstack111l11_opy_ (u"ࠢࡱࡴࡲࡼࡾ࡙ࡥࡵࡶ࡬ࡲ࡬ࡹࠢᕾ")] = bstack1lllll1ll1l_opy_(bstack1lllll11111_opy_, bstack1l1ll11l1l_opy_.get_property(bstack111l11_opy_ (u"ࠣࡲࡵࡳࡽࡿࡓࡦࡶࡷ࡭ࡳ࡭ࡳࠣᕿ")))
    bstack1llllll1ll1_opy_ = [element.lower() for element in bstack111111ll1l_opy_]
    bstack1lllll111ll_opy_(bstack1llllll1111_opy_, bstack1llllll1ll1_opy_)
    return bstack1llllll1111_opy_
def bstack1lllll111ll_opy_(d, keys):
    for key in list(d.keys()):
        if key.lower() in keys:
            d[key] = bstack111l11_opy_ (u"ࠤ࠭࠮࠯࠰ࠢᖀ")
    for value in d.values():
        if isinstance(value, dict):
            bstack1lllll111ll_opy_(value, keys)
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    bstack1lllll111ll_opy_(item, keys)