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
import copy
import zipfile
import git
import requests
from packaging import version
from bstack_utils.config import Config
from bstack_utils.constants import (bstack1l111ll1l11_opy_, bstack1lll1111l1_opy_, bstack1ll11l1l1l_opy_, bstack11l1l1l1_opy_,
                                    bstack1l11l1l111l_opy_, bstack1l11l1111ll_opy_, bstack1l11l1l11l1_opy_, bstack1l111lll1ll_opy_)
from bstack_utils.measure import measure
from bstack_utils.messages import bstack1l1l11ll_opy_, bstack11ll1l11l1_opy_
from bstack_utils.proxy import bstack1l11l1l1_opy_, bstack1l1ll1lll1_opy_
from bstack_utils.constants import *
from bstack_utils import bstack1ll1ll111_opy_
from browserstack_sdk._version import __version__
bstack1ll1l11l1_opy_ = Config.bstack1l111l1ll1_opy_()
logger = bstack1ll1ll111_opy_.get_logger(__name__, bstack1ll1ll111_opy_.bstack1llll1l1lll_opy_())
def bstack1l11ll11l1l_opy_(config):
    return config[bstack11l1ll1_opy_ (u"ࠬࡻࡳࡦࡴࡑࡥࡲ࡫ࠧᠣ")]
def bstack1l11llll111_opy_(config):
    return config[bstack11l1ll1_opy_ (u"࠭ࡡࡤࡥࡨࡷࡸࡑࡥࡺࠩᠤ")]
def bstack11llll111_opy_():
    try:
        import playwright
        return True
    except ImportError:
        return False
def bstack11lll1l1111_opy_(obj):
    values = []
    bstack1l111l1ll1l_opy_ = re.compile(bstack11l1ll1_opy_ (u"ࡲࠣࡠࡆ࡙ࡘ࡚ࡏࡎࡡࡗࡅࡌࡥ࡜ࡥ࠭ࠧࠦᠥ"), re.I)
    for key in obj.keys():
        if bstack1l111l1ll1l_opy_.match(key):
            values.append(obj[key])
    return values
def bstack1l11lllll1l_opy_(config):
    tags = []
    tags.extend(bstack11lll1l1111_opy_(os.environ))
    tags.extend(bstack11lll1l1111_opy_(config))
    return tags
def bstack1l111l11ll1_opy_(markers):
    tags = []
    for marker in markers:
        tags.append(marker.name)
    return tags
def bstack1l111111lll_opy_(bstack1l111111l1l_opy_):
    if not bstack1l111111l1l_opy_:
        return bstack11l1ll1_opy_ (u"ࠨࠩᠦ")
    return bstack11l1ll1_opy_ (u"ࠤࡾࢁࠥ࠮ࡻࡾࠫࠥᠧ").format(bstack1l111111l1l_opy_.name, bstack1l111111l1l_opy_.email)
def bstack1l1l111l1ll_opy_():
    try:
        repo = git.Repo(search_parent_directories=True)
        bstack11lll1l11ll_opy_ = repo.common_dir
        info = {
            bstack11l1ll1_opy_ (u"ࠥࡷ࡭ࡧࠢᠨ"): repo.head.commit.hexsha,
            bstack11l1ll1_opy_ (u"ࠦࡸ࡮࡯ࡳࡶࡢࡷ࡭ࡧࠢᠩ"): repo.git.rev_parse(repo.head.commit, short=True),
            bstack11l1ll1_opy_ (u"ࠧࡨࡲࡢࡰࡦ࡬ࠧᠪ"): repo.active_branch.name,
            bstack11l1ll1_opy_ (u"ࠨࡴࡢࡩࠥᠫ"): repo.git.describe(all=True, tags=True, exact_match=True),
            bstack11l1ll1_opy_ (u"ࠢࡤࡱࡰࡱ࡮ࡺࡴࡦࡴࠥᠬ"): bstack1l111111lll_opy_(repo.head.commit.committer),
            bstack11l1ll1_opy_ (u"ࠣࡥࡲࡱࡲ࡯ࡴࡵࡧࡵࡣࡩࡧࡴࡦࠤᠭ"): repo.head.commit.committed_datetime.isoformat(),
            bstack11l1ll1_opy_ (u"ࠤࡤࡹࡹ࡮࡯ࡳࠤᠮ"): bstack1l111111lll_opy_(repo.head.commit.author),
            bstack11l1ll1_opy_ (u"ࠥࡥࡺࡺࡨࡰࡴࡢࡨࡦࡺࡥࠣᠯ"): repo.head.commit.authored_datetime.isoformat(),
            bstack11l1ll1_opy_ (u"ࠦࡨࡵ࡭࡮࡫ࡷࡣࡲ࡫ࡳࡴࡣࡪࡩࠧᠰ"): repo.head.commit.message,
            bstack11l1ll1_opy_ (u"ࠧࡸ࡯ࡰࡶࠥᠱ"): repo.git.rev_parse(bstack11l1ll1_opy_ (u"ࠨ࠭࠮ࡵ࡫ࡳࡼ࠳ࡴࡰࡲ࡯ࡩࡻ࡫࡬ࠣᠲ")),
            bstack11l1ll1_opy_ (u"ࠢࡤࡱࡰࡱࡴࡴ࡟ࡨ࡫ࡷࡣࡩ࡯ࡲࠣᠳ"): bstack11lll1l11ll_opy_,
            bstack11l1ll1_opy_ (u"ࠣࡹࡲࡶࡰࡺࡲࡦࡧࡢ࡫࡮ࡺ࡟ࡥ࡫ࡵࠦᠴ"): subprocess.check_output([bstack11l1ll1_opy_ (u"ࠤࡪ࡭ࡹࠨᠵ"), bstack11l1ll1_opy_ (u"ࠥࡶࡪࡼ࠭ࡱࡣࡵࡷࡪࠨᠶ"), bstack11l1ll1_opy_ (u"ࠦ࠲࠳ࡧࡪࡶ࠰ࡧࡴࡳ࡭ࡰࡰ࠰ࡨ࡮ࡸࠢᠷ")]).strip().decode(
                bstack11l1ll1_opy_ (u"ࠬࡻࡴࡧ࠯࠻ࠫᠸ")),
            bstack11l1ll1_opy_ (u"ࠨ࡬ࡢࡵࡷࡣࡹࡧࡧࠣᠹ"): repo.git.describe(tags=True, abbrev=0, always=True),
            bstack11l1ll1_opy_ (u"ࠢࡤࡱࡰࡱ࡮ࡺࡳࡠࡵ࡬ࡲࡨ࡫࡟࡭ࡣࡶࡸࡤࡺࡡࡨࠤᠺ"): repo.git.rev_list(
                bstack11l1ll1_opy_ (u"ࠣࡽࢀ࠲࠳ࢁࡽࠣᠻ").format(repo.head.commit, repo.git.describe(tags=True, abbrev=0, always=True)), count=True)
        }
        remotes = repo.remotes
        bstack1l1111ll11l_opy_ = []
        for remote in remotes:
            bstack1l111l1ll11_opy_ = {
                bstack11l1ll1_opy_ (u"ࠤࡱࡥࡲ࡫ࠢᠼ"): remote.name,
                bstack11l1ll1_opy_ (u"ࠥࡹࡷࡲࠢᠽ"): remote.url,
            }
            bstack1l1111ll11l_opy_.append(bstack1l111l1ll11_opy_)
        bstack11lll1ll1ll_opy_ = {
            bstack11l1ll1_opy_ (u"ࠦࡳࡧ࡭ࡦࠤᠾ"): bstack11l1ll1_opy_ (u"ࠧ࡭ࡩࡵࠤᠿ"),
            **info,
            bstack11l1ll1_opy_ (u"ࠨࡲࡦ࡯ࡲࡸࡪࡹࠢᡀ"): bstack1l1111ll11l_opy_
        }
        bstack11lll1ll1ll_opy_ = bstack1l111l1111l_opy_(bstack11lll1ll1ll_opy_)
        return bstack11lll1ll1ll_opy_
    except git.InvalidGitRepositoryError:
        return {}
    except Exception as err:
        print(bstack11l1ll1_opy_ (u"ࠢࡆࡺࡦࡩࡵࡺࡩࡰࡰࠣ࡭ࡳࠦࡰࡰࡲࡸࡰࡦࡺࡩ࡯ࡩࠣࡋ࡮ࡺࠠ࡮ࡧࡷࡥࡩࡧࡴࡢࠢࡺ࡭ࡹ࡮ࠠࡦࡴࡵࡳࡷࡀࠠࡼࡿࠥᡁ").format(err))
        return {}
def bstack1l111l1111l_opy_(bstack11lll1ll1ll_opy_):
    bstack1l111l11l11_opy_ = bstack11llll11l11_opy_(bstack11lll1ll1ll_opy_)
    if bstack1l111l11l11_opy_ and bstack1l111l11l11_opy_ > bstack1l11l1l111l_opy_:
        bstack11lllll11ll_opy_ = bstack1l111l11l11_opy_ - bstack1l11l1l111l_opy_
        bstack1l1111l111l_opy_ = bstack11lllll1l11_opy_(bstack11lll1ll1ll_opy_[bstack11l1ll1_opy_ (u"ࠣࡥࡲࡱࡲ࡯ࡴࡠ࡯ࡨࡷࡸࡧࡧࡦࠤᡂ")], bstack11lllll11ll_opy_)
        bstack11lll1ll1ll_opy_[bstack11l1ll1_opy_ (u"ࠤࡦࡳࡲࡳࡩࡵࡡࡰࡩࡸࡹࡡࡨࡧࠥᡃ")] = bstack1l1111l111l_opy_
        logger.info(bstack11l1ll1_opy_ (u"ࠥࡘ࡭࡫ࠠࡤࡱࡰࡱ࡮ࡺࠠࡩࡣࡶࠤࡧ࡫ࡥ࡯ࠢࡷࡶࡺࡴࡣࡢࡶࡨࡨ࠳ࠦࡓࡪࡼࡨࠤࡴ࡬ࠠࡤࡱࡰࡱ࡮ࡺࠠࡢࡨࡷࡩࡷࠦࡴࡳࡷࡱࡧࡦࡺࡩࡰࡰࠣ࡭ࡸࠦࡻࡾࠢࡎࡆࠧᡄ")
                    .format(bstack11llll11l11_opy_(bstack11lll1ll1ll_opy_) / 1024))
    return bstack11lll1ll1ll_opy_
def bstack11llll11l11_opy_(bstack1l1111ll_opy_):
    try:
        if bstack1l1111ll_opy_:
            bstack1l11111l111_opy_ = json.dumps(bstack1l1111ll_opy_)
            bstack1l1111llll1_opy_ = sys.getsizeof(bstack1l11111l111_opy_)
            return bstack1l1111llll1_opy_
    except Exception as e:
        logger.debug(bstack11l1ll1_opy_ (u"ࠦࡘࡵ࡭ࡦࡶ࡫࡭ࡳ࡭ࠠࡸࡧࡱࡸࠥࡽࡲࡰࡰࡪࠤࡼ࡮ࡩ࡭ࡧࠣࡧࡦࡲࡣࡶ࡮ࡤࡸ࡮ࡴࡧࠡࡵ࡬ࡾࡪࠦ࡯ࡧࠢࡍࡗࡔࡔࠠࡰࡤ࡭ࡩࡨࡺ࠺ࠡࡽࢀࠦᡅ").format(e))
    return -1
def bstack11lllll1l11_opy_(field, bstack1l1111l11ll_opy_):
    try:
        bstack1l11111ll1l_opy_ = len(bytes(bstack1l11l1111ll_opy_, bstack11l1ll1_opy_ (u"ࠬࡻࡴࡧ࠯࠻ࠫᡆ")))
        bstack1l1111ll111_opy_ = bytes(field, bstack11l1ll1_opy_ (u"࠭ࡵࡵࡨ࠰࠼ࠬᡇ"))
        bstack1l111l1l1ll_opy_ = len(bstack1l1111ll111_opy_)
        bstack11llll1l11l_opy_ = ceil(bstack1l111l1l1ll_opy_ - bstack1l1111l11ll_opy_ - bstack1l11111ll1l_opy_)
        if bstack11llll1l11l_opy_ > 0:
            bstack11llllll1ll_opy_ = bstack1l1111ll111_opy_[:bstack11llll1l11l_opy_].decode(bstack11l1ll1_opy_ (u"ࠧࡶࡶࡩ࠱࠽࠭ᡈ"), errors=bstack11l1ll1_opy_ (u"ࠨ࡫ࡪࡲࡴࡸࡥࠨᡉ")) + bstack1l11l1111ll_opy_
            return bstack11llllll1ll_opy_
    except Exception as e:
        logger.debug(bstack11l1ll1_opy_ (u"ࠤࡈࡶࡷࡵࡲࠡࡹ࡫࡭ࡱ࡫ࠠࡵࡴࡸࡲࡨࡧࡴࡪࡰࡪࠤ࡫࡯ࡥ࡭ࡦ࠯ࠤࡳࡵࡴࡩ࡫ࡱ࡫ࠥࡽࡡࡴࠢࡷࡶࡺࡴࡣࡢࡶࡨࡨࠥ࡮ࡥࡳࡧ࠽ࠤࢀࢃࠢᡊ").format(e))
    return field
def bstack11l1ll1lll_opy_():
    env = os.environ
    if (bstack11l1ll1_opy_ (u"ࠥࡎࡊࡔࡋࡊࡐࡖࡣ࡚ࡘࡌࠣᡋ") in env and len(env[bstack11l1ll1_opy_ (u"ࠦࡏࡋࡎࡌࡋࡑࡗࡤ࡛ࡒࡍࠤᡌ")]) > 0) or (
            bstack11l1ll1_opy_ (u"ࠧࡐࡅࡏࡍࡌࡒࡘࡥࡈࡐࡏࡈࠦᡍ") in env and len(env[bstack11l1ll1_opy_ (u"ࠨࡊࡆࡐࡎࡍࡓ࡙࡟ࡉࡑࡐࡉࠧᡎ")]) > 0):
        return {
            bstack11l1ll1_opy_ (u"ࠢ࡯ࡣࡰࡩࠧᡏ"): bstack11l1ll1_opy_ (u"ࠣࡌࡨࡲࡰ࡯࡮ࡴࠤᡐ"),
            bstack11l1ll1_opy_ (u"ࠤࡥࡹ࡮ࡲࡤࡠࡷࡵࡰࠧᡑ"): env.get(bstack11l1ll1_opy_ (u"ࠥࡆ࡚ࡏࡌࡅࡡࡘࡖࡑࠨᡒ")),
            bstack11l1ll1_opy_ (u"ࠦ࡯ࡵࡢࡠࡰࡤࡱࡪࠨᡓ"): env.get(bstack11l1ll1_opy_ (u"ࠧࡐࡏࡃࡡࡑࡅࡒࡋࠢᡔ")),
            bstack11l1ll1_opy_ (u"ࠨࡢࡶ࡫࡯ࡨࡤࡴࡵ࡮ࡤࡨࡶࠧᡕ"): env.get(bstack11l1ll1_opy_ (u"ࠢࡃࡗࡌࡐࡉࡥࡎࡖࡏࡅࡉࡗࠨᡖ"))
        }
    if env.get(bstack11l1ll1_opy_ (u"ࠣࡅࡌࠦᡗ")) == bstack11l1ll1_opy_ (u"ࠤࡷࡶࡺ࡫ࠢᡘ") and bstack111l1l111_opy_(env.get(bstack11l1ll1_opy_ (u"ࠥࡇࡎࡘࡃࡍࡇࡆࡍࠧᡙ"))):
        return {
            bstack11l1ll1_opy_ (u"ࠦࡳࡧ࡭ࡦࠤᡚ"): bstack11l1ll1_opy_ (u"ࠧࡉࡩࡳࡥ࡯ࡩࡈࡏࠢᡛ"),
            bstack11l1ll1_opy_ (u"ࠨࡢࡶ࡫࡯ࡨࡤࡻࡲ࡭ࠤᡜ"): env.get(bstack11l1ll1_opy_ (u"ࠢࡄࡋࡕࡇࡑࡋ࡟ࡃࡗࡌࡐࡉࡥࡕࡓࡎࠥᡝ")),
            bstack11l1ll1_opy_ (u"ࠣ࡬ࡲࡦࡤࡴࡡ࡮ࡧࠥᡞ"): env.get(bstack11l1ll1_opy_ (u"ࠤࡆࡍࡗࡉࡌࡆࡡࡍࡓࡇࠨᡟ")),
            bstack11l1ll1_opy_ (u"ࠥࡦࡺ࡯࡬ࡥࡡࡱࡹࡲࡨࡥࡳࠤᡠ"): env.get(bstack11l1ll1_opy_ (u"ࠦࡈࡏࡒࡄࡎࡈࡣࡇ࡛ࡉࡍࡆࡢࡒ࡚ࡓࠢᡡ"))
        }
    if env.get(bstack11l1ll1_opy_ (u"ࠧࡉࡉࠣᡢ")) == bstack11l1ll1_opy_ (u"ࠨࡴࡳࡷࡨࠦᡣ") and bstack111l1l111_opy_(env.get(bstack11l1ll1_opy_ (u"ࠢࡕࡔࡄ࡚ࡎ࡙ࠢᡤ"))):
        return {
            bstack11l1ll1_opy_ (u"ࠣࡰࡤࡱࡪࠨᡥ"): bstack11l1ll1_opy_ (u"ࠤࡗࡶࡦࡼࡩࡴࠢࡆࡍࠧᡦ"),
            bstack11l1ll1_opy_ (u"ࠥࡦࡺ࡯࡬ࡥࡡࡸࡶࡱࠨᡧ"): env.get(bstack11l1ll1_opy_ (u"࡙ࠦࡘࡁࡗࡋࡖࡣࡇ࡛ࡉࡍࡆࡢ࡛ࡊࡈ࡟ࡖࡔࡏࠦᡨ")),
            bstack11l1ll1_opy_ (u"ࠧࡰ࡯ࡣࡡࡱࡥࡲ࡫ࠢᡩ"): env.get(bstack11l1ll1_opy_ (u"ࠨࡔࡓࡃ࡙ࡍࡘࡥࡊࡐࡄࡢࡒࡆࡓࡅࠣᡪ")),
            bstack11l1ll1_opy_ (u"ࠢࡣࡷ࡬ࡰࡩࡥ࡮ࡶ࡯ࡥࡩࡷࠨᡫ"): env.get(bstack11l1ll1_opy_ (u"ࠣࡖࡕࡅ࡛ࡏࡓࡠࡄࡘࡍࡑࡊ࡟ࡏࡗࡐࡆࡊࡘࠢᡬ"))
        }
    if env.get(bstack11l1ll1_opy_ (u"ࠤࡆࡍࠧᡭ")) == bstack11l1ll1_opy_ (u"ࠥࡸࡷࡻࡥࠣᡮ") and env.get(bstack11l1ll1_opy_ (u"ࠦࡈࡏ࡟ࡏࡃࡐࡉࠧᡯ")) == bstack11l1ll1_opy_ (u"ࠧࡩ࡯ࡥࡧࡶ࡬࡮ࡶࠢᡰ"):
        return {
            bstack11l1ll1_opy_ (u"ࠨ࡮ࡢ࡯ࡨࠦᡱ"): bstack11l1ll1_opy_ (u"ࠢࡄࡱࡧࡩࡸ࡮ࡩࡱࠤᡲ"),
            bstack11l1ll1_opy_ (u"ࠣࡤࡸ࡭ࡱࡪ࡟ࡶࡴ࡯ࠦᡳ"): None,
            bstack11l1ll1_opy_ (u"ࠤ࡭ࡳࡧࡥ࡮ࡢ࡯ࡨࠦᡴ"): None,
            bstack11l1ll1_opy_ (u"ࠥࡦࡺ࡯࡬ࡥࡡࡱࡹࡲࡨࡥࡳࠤᡵ"): None
        }
    if env.get(bstack11l1ll1_opy_ (u"ࠦࡇࡏࡔࡃࡗࡆࡏࡊ࡚࡟ࡃࡔࡄࡒࡈࡎࠢᡶ")) and env.get(bstack11l1ll1_opy_ (u"ࠧࡈࡉࡕࡄࡘࡇࡐࡋࡔࡠࡅࡒࡑࡒࡏࡔࠣᡷ")):
        return {
            bstack11l1ll1_opy_ (u"ࠨ࡮ࡢ࡯ࡨࠦᡸ"): bstack11l1ll1_opy_ (u"ࠢࡃ࡫ࡷࡦࡺࡩ࡫ࡦࡶࠥ᡹"),
            bstack11l1ll1_opy_ (u"ࠣࡤࡸ࡭ࡱࡪ࡟ࡶࡴ࡯ࠦ᡺"): env.get(bstack11l1ll1_opy_ (u"ࠤࡅࡍ࡙ࡈࡕࡄࡍࡈࡘࡤࡍࡉࡕࡡࡋࡘ࡙ࡖ࡟ࡐࡔࡌࡋࡎࡔࠢ᡻")),
            bstack11l1ll1_opy_ (u"ࠥ࡮ࡴࡨ࡟࡯ࡣࡰࡩࠧ᡼"): None,
            bstack11l1ll1_opy_ (u"ࠦࡧࡻࡩ࡭ࡦࡢࡲࡺࡳࡢࡦࡴࠥ᡽"): env.get(bstack11l1ll1_opy_ (u"ࠧࡈࡉࡕࡄࡘࡇࡐࡋࡔࡠࡄࡘࡍࡑࡊ࡟ࡏࡗࡐࡆࡊࡘࠢ᡾"))
        }
    if env.get(bstack11l1ll1_opy_ (u"ࠨࡃࡊࠤ᡿")) == bstack11l1ll1_opy_ (u"ࠢࡵࡴࡸࡩࠧᢀ") and bstack111l1l111_opy_(env.get(bstack11l1ll1_opy_ (u"ࠣࡆࡕࡓࡓࡋࠢᢁ"))):
        return {
            bstack11l1ll1_opy_ (u"ࠤࡱࡥࡲ࡫ࠢᢂ"): bstack11l1ll1_opy_ (u"ࠥࡈࡷࡵ࡮ࡦࠤᢃ"),
            bstack11l1ll1_opy_ (u"ࠦࡧࡻࡩ࡭ࡦࡢࡹࡷࡲࠢᢄ"): env.get(bstack11l1ll1_opy_ (u"ࠧࡊࡒࡐࡐࡈࡣࡇ࡛ࡉࡍࡆࡢࡐࡎࡔࡋࠣᢅ")),
            bstack11l1ll1_opy_ (u"ࠨࡪࡰࡤࡢࡲࡦࡳࡥࠣᢆ"): None,
            bstack11l1ll1_opy_ (u"ࠢࡣࡷ࡬ࡰࡩࡥ࡮ࡶ࡯ࡥࡩࡷࠨᢇ"): env.get(bstack11l1ll1_opy_ (u"ࠣࡆࡕࡓࡓࡋ࡟ࡃࡗࡌࡐࡉࡥࡎࡖࡏࡅࡉࡗࠨᢈ"))
        }
    if env.get(bstack11l1ll1_opy_ (u"ࠤࡆࡍࠧᢉ")) == bstack11l1ll1_opy_ (u"ࠥࡸࡷࡻࡥࠣᢊ") and bstack111l1l111_opy_(env.get(bstack11l1ll1_opy_ (u"ࠦࡘࡋࡍࡂࡒࡋࡓࡗࡋࠢᢋ"))):
        return {
            bstack11l1ll1_opy_ (u"ࠧࡴࡡ࡮ࡧࠥᢌ"): bstack11l1ll1_opy_ (u"ࠨࡓࡦ࡯ࡤࡴ࡭ࡵࡲࡦࠤᢍ"),
            bstack11l1ll1_opy_ (u"ࠢࡣࡷ࡬ࡰࡩࡥࡵࡳ࡮ࠥᢎ"): env.get(bstack11l1ll1_opy_ (u"ࠣࡕࡈࡑࡆࡖࡈࡐࡔࡈࡣࡔࡘࡇࡂࡐࡌ࡞ࡆ࡚ࡉࡐࡐࡢ࡙ࡗࡒࠢᢏ")),
            bstack11l1ll1_opy_ (u"ࠤ࡭ࡳࡧࡥ࡮ࡢ࡯ࡨࠦᢐ"): env.get(bstack11l1ll1_opy_ (u"ࠥࡗࡊࡓࡁࡑࡊࡒࡖࡊࡥࡊࡐࡄࡢࡒࡆࡓࡅࠣᢑ")),
            bstack11l1ll1_opy_ (u"ࠦࡧࡻࡩ࡭ࡦࡢࡲࡺࡳࡢࡦࡴࠥᢒ"): env.get(bstack11l1ll1_opy_ (u"࡙ࠧࡅࡎࡃࡓࡌࡔࡘࡅࡠࡌࡒࡆࡤࡏࡄࠣᢓ"))
        }
    if env.get(bstack11l1ll1_opy_ (u"ࠨࡃࡊࠤᢔ")) == bstack11l1ll1_opy_ (u"ࠢࡵࡴࡸࡩࠧᢕ") and bstack111l1l111_opy_(env.get(bstack11l1ll1_opy_ (u"ࠣࡉࡌࡘࡑࡇࡂࡠࡅࡌࠦᢖ"))):
        return {
            bstack11l1ll1_opy_ (u"ࠤࡱࡥࡲ࡫ࠢᢗ"): bstack11l1ll1_opy_ (u"ࠥࡋ࡮ࡺࡌࡢࡤࠥᢘ"),
            bstack11l1ll1_opy_ (u"ࠦࡧࡻࡩ࡭ࡦࡢࡹࡷࡲࠢᢙ"): env.get(bstack11l1ll1_opy_ (u"ࠧࡉࡉࡠࡌࡒࡆࡤ࡛ࡒࡍࠤᢚ")),
            bstack11l1ll1_opy_ (u"ࠨࡪࡰࡤࡢࡲࡦࡳࡥࠣᢛ"): env.get(bstack11l1ll1_opy_ (u"ࠢࡄࡋࡢࡎࡔࡈ࡟ࡏࡃࡐࡉࠧᢜ")),
            bstack11l1ll1_opy_ (u"ࠣࡤࡸ࡭ࡱࡪ࡟࡯ࡷࡰࡦࡪࡸࠢᢝ"): env.get(bstack11l1ll1_opy_ (u"ࠤࡆࡍࡤࡐࡏࡃࡡࡌࡈࠧᢞ"))
        }
    if env.get(bstack11l1ll1_opy_ (u"ࠥࡇࡎࠨᢟ")) == bstack11l1ll1_opy_ (u"ࠦࡹࡸࡵࡦࠤᢠ") and bstack111l1l111_opy_(env.get(bstack11l1ll1_opy_ (u"ࠧࡈࡕࡊࡎࡇࡏࡎ࡚ࡅࠣᢡ"))):
        return {
            bstack11l1ll1_opy_ (u"ࠨ࡮ࡢ࡯ࡨࠦᢢ"): bstack11l1ll1_opy_ (u"ࠢࡃࡷ࡬ࡰࡩࡱࡩࡵࡧࠥᢣ"),
            bstack11l1ll1_opy_ (u"ࠣࡤࡸ࡭ࡱࡪ࡟ࡶࡴ࡯ࠦᢤ"): env.get(bstack11l1ll1_opy_ (u"ࠤࡅ࡙ࡎࡒࡄࡌࡋࡗࡉࡤࡈࡕࡊࡎࡇࡣ࡚ࡘࡌࠣᢥ")),
            bstack11l1ll1_opy_ (u"ࠥ࡮ࡴࡨ࡟࡯ࡣࡰࡩࠧᢦ"): env.get(bstack11l1ll1_opy_ (u"ࠦࡇ࡛ࡉࡍࡆࡎࡍ࡙ࡋ࡟ࡍࡃࡅࡉࡑࠨᢧ")) or env.get(bstack11l1ll1_opy_ (u"ࠧࡈࡕࡊࡎࡇࡏࡎ࡚ࡅࡠࡒࡌࡔࡊࡒࡉࡏࡇࡢࡒࡆࡓࡅࠣᢨ")),
            bstack11l1ll1_opy_ (u"ࠨࡢࡶ࡫࡯ࡨࡤࡴࡵ࡮ࡤࡨࡶᢩࠧ"): env.get(bstack11l1ll1_opy_ (u"ࠢࡃࡗࡌࡐࡉࡑࡉࡕࡇࡢࡆ࡚ࡏࡌࡅࡡࡑ࡙ࡒࡈࡅࡓࠤᢪ"))
        }
    if bstack111l1l111_opy_(env.get(bstack11l1ll1_opy_ (u"ࠣࡖࡉࡣࡇ࡛ࡉࡍࡆࠥ᢫"))):
        return {
            bstack11l1ll1_opy_ (u"ࠤࡱࡥࡲ࡫ࠢ᢬"): bstack11l1ll1_opy_ (u"࡚ࠥ࡮ࡹࡵࡢ࡮ࠣࡗࡹࡻࡤࡪࡱࠣࡘࡪࡧ࡭ࠡࡕࡨࡶࡻ࡯ࡣࡦࡵࠥ᢭"),
            bstack11l1ll1_opy_ (u"ࠦࡧࡻࡩ࡭ࡦࡢࡹࡷࡲࠢ᢮"): bstack11l1ll1_opy_ (u"ࠧࢁࡽࡼࡿࠥ᢯").format(env.get(bstack11l1ll1_opy_ (u"࠭ࡓ࡚ࡕࡗࡉࡒࡥࡔࡆࡃࡐࡊࡔ࡛ࡎࡅࡃࡗࡍࡔࡔࡓࡆࡔ࡙ࡉࡗ࡛ࡒࡊࠩᢰ")), env.get(bstack11l1ll1_opy_ (u"ࠧࡔ࡛ࡖࡘࡊࡓ࡟ࡕࡇࡄࡑࡕࡘࡏࡋࡇࡆࡘࡎࡊࠧᢱ"))),
            bstack11l1ll1_opy_ (u"ࠣ࡬ࡲࡦࡤࡴࡡ࡮ࡧࠥᢲ"): env.get(bstack11l1ll1_opy_ (u"ࠤࡖ࡝ࡘ࡚ࡅࡎࡡࡇࡉࡋࡏࡎࡊࡖࡌࡓࡓࡏࡄࠣᢳ")),
            bstack11l1ll1_opy_ (u"ࠥࡦࡺ࡯࡬ࡥࡡࡱࡹࡲࡨࡥࡳࠤᢴ"): env.get(bstack11l1ll1_opy_ (u"ࠦࡇ࡛ࡉࡍࡆࡢࡆ࡚ࡏࡌࡅࡋࡇࠦᢵ"))
        }
    if bstack111l1l111_opy_(env.get(bstack11l1ll1_opy_ (u"ࠧࡇࡐࡑࡘࡈ࡝ࡔࡘࠢᢶ"))):
        return {
            bstack11l1ll1_opy_ (u"ࠨ࡮ࡢ࡯ࡨࠦᢷ"): bstack11l1ll1_opy_ (u"ࠢࡂࡲࡳࡺࡪࡿ࡯ࡳࠤᢸ"),
            bstack11l1ll1_opy_ (u"ࠣࡤࡸ࡭ࡱࡪ࡟ࡶࡴ࡯ࠦᢹ"): bstack11l1ll1_opy_ (u"ࠤࡾࢁ࠴ࡶࡲࡰ࡬ࡨࡧࡹ࠵ࡻࡾ࠱ࡾࢁ࠴ࡨࡵࡪ࡮ࡧࡷ࠴ࢁࡽࠣᢺ").format(env.get(bstack11l1ll1_opy_ (u"ࠪࡅࡕࡖࡖࡆ࡛ࡒࡖࡤ࡛ࡒࡍࠩᢻ")), env.get(bstack11l1ll1_opy_ (u"ࠫࡆࡖࡐࡗࡇ࡜ࡓࡗࡥࡁࡄࡅࡒ࡙ࡓ࡚࡟ࡏࡃࡐࡉࠬᢼ")), env.get(bstack11l1ll1_opy_ (u"ࠬࡇࡐࡑࡘࡈ࡝ࡔࡘ࡟ࡑࡔࡒࡎࡊࡉࡔࡠࡕࡏ࡙ࡌ࠭ᢽ")), env.get(bstack11l1ll1_opy_ (u"࠭ࡁࡑࡒ࡙ࡉ࡞ࡕࡒࡠࡄࡘࡍࡑࡊ࡟ࡊࡆࠪᢾ"))),
            bstack11l1ll1_opy_ (u"ࠢ࡫ࡱࡥࡣࡳࡧ࡭ࡦࠤᢿ"): env.get(bstack11l1ll1_opy_ (u"ࠣࡃࡓࡔ࡛ࡋ࡙ࡐࡔࡢࡎࡔࡈ࡟ࡏࡃࡐࡉࠧᣀ")),
            bstack11l1ll1_opy_ (u"ࠤࡥࡹ࡮ࡲࡤࡠࡰࡸࡱࡧ࡫ࡲࠣᣁ"): env.get(bstack11l1ll1_opy_ (u"ࠥࡅࡕࡖࡖࡆ࡛ࡒࡖࡤࡈࡕࡊࡎࡇࡣࡓ࡛ࡍࡃࡇࡕࠦᣂ"))
        }
    if env.get(bstack11l1ll1_opy_ (u"ࠦࡆࡠࡕࡓࡇࡢࡌ࡙࡚ࡐࡠࡗࡖࡉࡗࡥࡁࡈࡇࡑࡘࠧᣃ")) and env.get(bstack11l1ll1_opy_ (u"࡚ࠧࡆࡠࡄࡘࡍࡑࡊࠢᣄ")):
        return {
            bstack11l1ll1_opy_ (u"ࠨ࡮ࡢ࡯ࡨࠦᣅ"): bstack11l1ll1_opy_ (u"ࠢࡂࡼࡸࡶࡪࠦࡃࡊࠤᣆ"),
            bstack11l1ll1_opy_ (u"ࠣࡤࡸ࡭ࡱࡪ࡟ࡶࡴ࡯ࠦᣇ"): bstack11l1ll1_opy_ (u"ࠤࡾࢁࢀࢃ࠯ࡠࡤࡸ࡭ࡱࡪ࠯ࡳࡧࡶࡹࡱࡺࡳࡀࡤࡸ࡭ࡱࡪࡉࡥ࠿ࡾࢁࠧᣈ").format(env.get(bstack11l1ll1_opy_ (u"ࠪࡗ࡞࡙ࡔࡆࡏࡢࡘࡊࡇࡍࡇࡑࡘࡒࡉࡇࡔࡊࡑࡑࡗࡊࡘࡖࡆࡔࡘࡖࡎ࠭ᣉ")), env.get(bstack11l1ll1_opy_ (u"ࠫࡘ࡟ࡓࡕࡇࡐࡣ࡙ࡋࡁࡎࡒࡕࡓࡏࡋࡃࡕࠩᣊ")), env.get(bstack11l1ll1_opy_ (u"ࠬࡈࡕࡊࡎࡇࡣࡇ࡛ࡉࡍࡆࡌࡈࠬᣋ"))),
            bstack11l1ll1_opy_ (u"ࠨࡪࡰࡤࡢࡲࡦࡳࡥࠣᣌ"): env.get(bstack11l1ll1_opy_ (u"ࠢࡃࡗࡌࡐࡉࡥࡂࡖࡋࡏࡈࡎࡊࠢᣍ")),
            bstack11l1ll1_opy_ (u"ࠣࡤࡸ࡭ࡱࡪ࡟࡯ࡷࡰࡦࡪࡸࠢᣎ"): env.get(bstack11l1ll1_opy_ (u"ࠤࡅ࡙ࡎࡒࡄࡠࡄࡘࡍࡑࡊࡉࡅࠤᣏ"))
        }
    if any([env.get(bstack11l1ll1_opy_ (u"ࠥࡇࡔࡊࡅࡃࡗࡌࡐࡉࡥࡂࡖࡋࡏࡈࡤࡏࡄࠣᣐ")), env.get(bstack11l1ll1_opy_ (u"ࠦࡈࡕࡄࡆࡄࡘࡍࡑࡊ࡟ࡓࡇࡖࡓࡑ࡜ࡅࡅࡡࡖࡓ࡚ࡘࡃࡆࡡ࡙ࡉࡗ࡙ࡉࡐࡐࠥᣑ")), env.get(bstack11l1ll1_opy_ (u"ࠧࡉࡏࡅࡇࡅ࡙ࡎࡒࡄࡠࡕࡒ࡙ࡗࡉࡅࡠࡘࡈࡖࡘࡏࡏࡏࠤᣒ"))]):
        return {
            bstack11l1ll1_opy_ (u"ࠨ࡮ࡢ࡯ࡨࠦᣓ"): bstack11l1ll1_opy_ (u"ࠢࡂ࡙ࡖࠤࡈࡵࡤࡦࡄࡸ࡭ࡱࡪࠢᣔ"),
            bstack11l1ll1_opy_ (u"ࠣࡤࡸ࡭ࡱࡪ࡟ࡶࡴ࡯ࠦᣕ"): env.get(bstack11l1ll1_opy_ (u"ࠤࡆࡓࡉࡋࡂࡖࡋࡏࡈࡤࡖࡕࡃࡎࡌࡇࡤࡈࡕࡊࡎࡇࡣ࡚ࡘࡌࠣᣖ")),
            bstack11l1ll1_opy_ (u"ࠥ࡮ࡴࡨ࡟࡯ࡣࡰࡩࠧᣗ"): env.get(bstack11l1ll1_opy_ (u"ࠦࡈࡕࡄࡆࡄࡘࡍࡑࡊ࡟ࡃࡗࡌࡐࡉࡥࡉࡅࠤᣘ")),
            bstack11l1ll1_opy_ (u"ࠧࡨࡵࡪ࡮ࡧࡣࡳࡻ࡭ࡣࡧࡵࠦᣙ"): env.get(bstack11l1ll1_opy_ (u"ࠨࡃࡐࡆࡈࡆ࡚ࡏࡌࡅࡡࡅ࡙ࡎࡒࡄࡠࡋࡇࠦᣚ"))
        }
    if env.get(bstack11l1ll1_opy_ (u"ࠢࡣࡣࡰࡦࡴࡵ࡟ࡣࡷ࡬ࡰࡩࡔࡵ࡮ࡤࡨࡶࠧᣛ")):
        return {
            bstack11l1ll1_opy_ (u"ࠣࡰࡤࡱࡪࠨᣜ"): bstack11l1ll1_opy_ (u"ࠤࡅࡥࡲࡨ࡯ࡰࠤᣝ"),
            bstack11l1ll1_opy_ (u"ࠥࡦࡺ࡯࡬ࡥࡡࡸࡶࡱࠨᣞ"): env.get(bstack11l1ll1_opy_ (u"ࠦࡧࡧ࡭ࡣࡱࡲࡣࡧࡻࡩ࡭ࡦࡕࡩࡸࡻ࡬ࡵࡵࡘࡶࡱࠨᣟ")),
            bstack11l1ll1_opy_ (u"ࠧࡰ࡯ࡣࡡࡱࡥࡲ࡫ࠢᣠ"): env.get(bstack11l1ll1_opy_ (u"ࠨࡢࡢ࡯ࡥࡳࡴࡥࡳࡩࡱࡵࡸࡏࡵࡢࡏࡣࡰࡩࠧᣡ")),
            bstack11l1ll1_opy_ (u"ࠢࡣࡷ࡬ࡰࡩࡥ࡮ࡶ࡯ࡥࡩࡷࠨᣢ"): env.get(bstack11l1ll1_opy_ (u"ࠣࡤࡤࡱࡧࡵ࡯ࡠࡤࡸ࡭ࡱࡪࡎࡶ࡯ࡥࡩࡷࠨᣣ"))
        }
    if env.get(bstack11l1ll1_opy_ (u"ࠤ࡚ࡉࡗࡉࡋࡆࡔࠥᣤ")) or env.get(bstack11l1ll1_opy_ (u"࡛ࠥࡊࡘࡃࡌࡇࡕࡣࡒࡇࡉࡏࡡࡓࡍࡕࡋࡌࡊࡐࡈࡣࡘ࡚ࡁࡓࡖࡈࡈࠧᣥ")):
        return {
            bstack11l1ll1_opy_ (u"ࠦࡳࡧ࡭ࡦࠤᣦ"): bstack11l1ll1_opy_ (u"ࠧ࡝ࡥࡳࡥ࡮ࡩࡷࠨᣧ"),
            bstack11l1ll1_opy_ (u"ࠨࡢࡶ࡫࡯ࡨࡤࡻࡲ࡭ࠤᣨ"): env.get(bstack11l1ll1_opy_ (u"ࠢࡘࡇࡕࡇࡐࡋࡒࡠࡄࡘࡍࡑࡊ࡟ࡖࡔࡏࠦᣩ")),
            bstack11l1ll1_opy_ (u"ࠣ࡬ࡲࡦࡤࡴࡡ࡮ࡧࠥᣪ"): bstack11l1ll1_opy_ (u"ࠤࡐࡥ࡮ࡴࠠࡑ࡫ࡳࡩࡱ࡯࡮ࡦࠤᣫ") if env.get(bstack11l1ll1_opy_ (u"࡛ࠥࡊࡘࡃࡌࡇࡕࡣࡒࡇࡉࡏࡡࡓࡍࡕࡋࡌࡊࡐࡈࡣࡘ࡚ࡁࡓࡖࡈࡈࠧᣬ")) else None,
            bstack11l1ll1_opy_ (u"ࠦࡧࡻࡩ࡭ࡦࡢࡲࡺࡳࡢࡦࡴࠥᣭ"): env.get(bstack11l1ll1_opy_ (u"ࠧ࡝ࡅࡓࡅࡎࡉࡗࡥࡇࡊࡖࡢࡇࡔࡓࡍࡊࡖࠥᣮ"))
        }
    if any([env.get(bstack11l1ll1_opy_ (u"ࠨࡇࡄࡒࡢࡔࡗࡕࡊࡆࡅࡗࠦᣯ")), env.get(bstack11l1ll1_opy_ (u"ࠢࡈࡅࡏࡓ࡚ࡊ࡟ࡑࡔࡒࡎࡊࡉࡔࠣᣰ")), env.get(bstack11l1ll1_opy_ (u"ࠣࡉࡒࡓࡌࡒࡅࡠࡅࡏࡓ࡚ࡊ࡟ࡑࡔࡒࡎࡊࡉࡔࠣᣱ"))]):
        return {
            bstack11l1ll1_opy_ (u"ࠤࡱࡥࡲ࡫ࠢᣲ"): bstack11l1ll1_opy_ (u"ࠥࡋࡴࡵࡧ࡭ࡧࠣࡇࡱࡵࡵࡥࠤᣳ"),
            bstack11l1ll1_opy_ (u"ࠦࡧࡻࡩ࡭ࡦࡢࡹࡷࡲࠢᣴ"): None,
            bstack11l1ll1_opy_ (u"ࠧࡰ࡯ࡣࡡࡱࡥࡲ࡫ࠢᣵ"): env.get(bstack11l1ll1_opy_ (u"ࠨࡐࡓࡑࡍࡉࡈ࡚࡟ࡊࡆࠥ᣶")),
            bstack11l1ll1_opy_ (u"ࠢࡣࡷ࡬ࡰࡩࡥ࡮ࡶ࡯ࡥࡩࡷࠨ᣷"): env.get(bstack11l1ll1_opy_ (u"ࠣࡄࡘࡍࡑࡊ࡟ࡊࡆࠥ᣸"))
        }
    if env.get(bstack11l1ll1_opy_ (u"ࠤࡖࡌࡎࡖࡐࡂࡄࡏࡉࠧ᣹")):
        return {
            bstack11l1ll1_opy_ (u"ࠥࡲࡦࡳࡥࠣ᣺"): bstack11l1ll1_opy_ (u"ࠦࡘ࡮ࡩࡱࡲࡤࡦࡱ࡫ࠢ᣻"),
            bstack11l1ll1_opy_ (u"ࠧࡨࡵࡪ࡮ࡧࡣࡺࡸ࡬ࠣ᣼"): env.get(bstack11l1ll1_opy_ (u"ࠨࡓࡉࡋࡓࡔࡆࡈࡌࡆࡡࡅ࡙ࡎࡒࡄࡠࡗࡕࡐࠧ᣽")),
            bstack11l1ll1_opy_ (u"ࠢ࡫ࡱࡥࡣࡳࡧ࡭ࡦࠤ᣾"): bstack11l1ll1_opy_ (u"ࠣࡌࡲࡦࠥࠩࡻࡾࠤ᣿").format(env.get(bstack11l1ll1_opy_ (u"ࠩࡖࡌࡎࡖࡐࡂࡄࡏࡉࡤࡐࡏࡃࡡࡌࡈࠬᤀ"))) if env.get(bstack11l1ll1_opy_ (u"ࠥࡗࡍࡏࡐࡑࡃࡅࡐࡊࡥࡊࡐࡄࡢࡍࡉࠨᤁ")) else None,
            bstack11l1ll1_opy_ (u"ࠦࡧࡻࡩ࡭ࡦࡢࡲࡺࡳࡢࡦࡴࠥᤂ"): env.get(bstack11l1ll1_opy_ (u"࡙ࠧࡈࡊࡒࡓࡅࡇࡒࡅࡠࡄࡘࡍࡑࡊ࡟ࡏࡗࡐࡆࡊࡘࠢᤃ"))
        }
    if bstack111l1l111_opy_(env.get(bstack11l1ll1_opy_ (u"ࠨࡎࡆࡖࡏࡍࡋ࡟ࠢᤄ"))):
        return {
            bstack11l1ll1_opy_ (u"ࠢ࡯ࡣࡰࡩࠧᤅ"): bstack11l1ll1_opy_ (u"ࠣࡐࡨࡸࡱ࡯ࡦࡺࠤᤆ"),
            bstack11l1ll1_opy_ (u"ࠤࡥࡹ࡮ࡲࡤࡠࡷࡵࡰࠧᤇ"): env.get(bstack11l1ll1_opy_ (u"ࠥࡈࡊࡖࡌࡐ࡛ࡢ࡙ࡗࡒࠢᤈ")),
            bstack11l1ll1_opy_ (u"ࠦ࡯ࡵࡢࡠࡰࡤࡱࡪࠨᤉ"): env.get(bstack11l1ll1_opy_ (u"࡙ࠧࡉࡕࡇࡢࡒࡆࡓࡅࠣᤊ")),
            bstack11l1ll1_opy_ (u"ࠨࡢࡶ࡫࡯ࡨࡤࡴࡵ࡮ࡤࡨࡶࠧᤋ"): env.get(bstack11l1ll1_opy_ (u"ࠢࡃࡗࡌࡐࡉࡥࡉࡅࠤᤌ"))
        }
    if bstack111l1l111_opy_(env.get(bstack11l1ll1_opy_ (u"ࠣࡉࡌࡘࡍ࡛ࡂࡠࡃࡆࡘࡎࡕࡎࡔࠤᤍ"))):
        return {
            bstack11l1ll1_opy_ (u"ࠤࡱࡥࡲ࡫ࠢᤎ"): bstack11l1ll1_opy_ (u"ࠥࡋ࡮ࡺࡈࡶࡤࠣࡅࡨࡺࡩࡰࡰࡶࠦᤏ"),
            bstack11l1ll1_opy_ (u"ࠦࡧࡻࡩ࡭ࡦࡢࡹࡷࡲࠢᤐ"): bstack11l1ll1_opy_ (u"ࠧࢁࡽ࠰ࡽࢀ࠳ࡦࡩࡴࡪࡱࡱࡷ࠴ࡸࡵ࡯ࡵ࠲ࡿࢂࠨᤑ").format(env.get(bstack11l1ll1_opy_ (u"࠭ࡇࡊࡖࡋ࡙ࡇࡥࡓࡆࡔ࡙ࡉࡗࡥࡕࡓࡎࠪᤒ")), env.get(bstack11l1ll1_opy_ (u"ࠧࡈࡋࡗࡌ࡚ࡈ࡟ࡓࡇࡓࡓࡘࡏࡔࡐࡔ࡜ࠫᤓ")), env.get(bstack11l1ll1_opy_ (u"ࠨࡉࡌࡘࡍ࡛ࡂࡠࡔࡘࡒࡤࡏࡄࠨᤔ"))),
            bstack11l1ll1_opy_ (u"ࠤ࡭ࡳࡧࡥ࡮ࡢ࡯ࡨࠦᤕ"): env.get(bstack11l1ll1_opy_ (u"ࠥࡋࡎ࡚ࡈࡖࡄࡢ࡛ࡔࡘࡋࡇࡎࡒ࡛ࠧᤖ")),
            bstack11l1ll1_opy_ (u"ࠦࡧࡻࡩ࡭ࡦࡢࡲࡺࡳࡢࡦࡴࠥᤗ"): env.get(bstack11l1ll1_opy_ (u"ࠧࡍࡉࡕࡊࡘࡆࡤࡘࡕࡏࡡࡌࡈࠧᤘ"))
        }
    if env.get(bstack11l1ll1_opy_ (u"ࠨࡃࡊࠤᤙ")) == bstack11l1ll1_opy_ (u"ࠢࡵࡴࡸࡩࠧᤚ") and env.get(bstack11l1ll1_opy_ (u"ࠣࡘࡈࡖࡈࡋࡌࠣᤛ")) == bstack11l1ll1_opy_ (u"ࠤ࠴ࠦᤜ"):
        return {
            bstack11l1ll1_opy_ (u"ࠥࡲࡦࡳࡥࠣᤝ"): bstack11l1ll1_opy_ (u"࡛ࠦ࡫ࡲࡤࡧ࡯ࠦᤞ"),
            bstack11l1ll1_opy_ (u"ࠧࡨࡵࡪ࡮ࡧࡣࡺࡸ࡬ࠣ᤟"): bstack11l1ll1_opy_ (u"ࠨࡨࡵࡶࡳ࠾࠴࠵ࡻࡾࠤᤠ").format(env.get(bstack11l1ll1_opy_ (u"ࠧࡗࡇࡕࡇࡊࡒ࡟ࡖࡔࡏࠫᤡ"))),
            bstack11l1ll1_opy_ (u"ࠣ࡬ࡲࡦࡤࡴࡡ࡮ࡧࠥᤢ"): None,
            bstack11l1ll1_opy_ (u"ࠤࡥࡹ࡮ࡲࡤࡠࡰࡸࡱࡧ࡫ࡲࠣᤣ"): None,
        }
    if env.get(bstack11l1ll1_opy_ (u"ࠥࡘࡊࡇࡍࡄࡋࡗ࡝ࡤ࡜ࡅࡓࡕࡌࡓࡓࠨᤤ")):
        return {
            bstack11l1ll1_opy_ (u"ࠦࡳࡧ࡭ࡦࠤᤥ"): bstack11l1ll1_opy_ (u"࡚ࠧࡥࡢ࡯ࡦ࡭ࡹࡿࠢᤦ"),
            bstack11l1ll1_opy_ (u"ࠨࡢࡶ࡫࡯ࡨࡤࡻࡲ࡭ࠤᤧ"): None,
            bstack11l1ll1_opy_ (u"ࠢ࡫ࡱࡥࡣࡳࡧ࡭ࡦࠤᤨ"): env.get(bstack11l1ll1_opy_ (u"ࠣࡖࡈࡅࡒࡉࡉࡕ࡛ࡢࡔࡗࡕࡊࡆࡅࡗࡣࡓࡇࡍࡆࠤᤩ")),
            bstack11l1ll1_opy_ (u"ࠤࡥࡹ࡮ࡲࡤࡠࡰࡸࡱࡧ࡫ࡲࠣᤪ"): env.get(bstack11l1ll1_opy_ (u"ࠥࡆ࡚ࡏࡌࡅࡡࡑ࡙ࡒࡈࡅࡓࠤᤫ"))
        }
    if any([env.get(bstack11l1ll1_opy_ (u"ࠦࡈࡕࡎࡄࡑࡘࡖࡘࡋࠢ᤬")), env.get(bstack11l1ll1_opy_ (u"ࠧࡉࡏࡏࡅࡒ࡙ࡗ࡙ࡅࡠࡗࡕࡐࠧ᤭")), env.get(bstack11l1ll1_opy_ (u"ࠨࡃࡐࡐࡆࡓ࡚ࡘࡓࡆࡡࡘࡗࡊࡘࡎࡂࡏࡈࠦ᤮")), env.get(bstack11l1ll1_opy_ (u"ࠢࡄࡑࡑࡇࡔ࡛ࡒࡔࡇࡢࡘࡊࡇࡍࠣ᤯"))]):
        return {
            bstack11l1ll1_opy_ (u"ࠣࡰࡤࡱࡪࠨᤰ"): bstack11l1ll1_opy_ (u"ࠤࡆࡳࡳࡩ࡯ࡶࡴࡶࡩࠧᤱ"),
            bstack11l1ll1_opy_ (u"ࠥࡦࡺ࡯࡬ࡥࡡࡸࡶࡱࠨᤲ"): None,
            bstack11l1ll1_opy_ (u"ࠦ࡯ࡵࡢࡠࡰࡤࡱࡪࠨᤳ"): env.get(bstack11l1ll1_opy_ (u"ࠧࡈࡕࡊࡎࡇࡣࡏࡕࡂࡠࡐࡄࡑࡊࠨᤴ")) or None,
            bstack11l1ll1_opy_ (u"ࠨࡢࡶ࡫࡯ࡨࡤࡴࡵ࡮ࡤࡨࡶࠧᤵ"): env.get(bstack11l1ll1_opy_ (u"ࠢࡃࡗࡌࡐࡉࡥࡉࡅࠤᤶ"), 0)
        }
    if env.get(bstack11l1ll1_opy_ (u"ࠣࡉࡒࡣࡏࡕࡂࡠࡐࡄࡑࡊࠨᤷ")):
        return {
            bstack11l1ll1_opy_ (u"ࠤࡱࡥࡲ࡫ࠢᤸ"): bstack11l1ll1_opy_ (u"ࠥࡋࡴࡉࡄ᤹ࠣ"),
            bstack11l1ll1_opy_ (u"ࠦࡧࡻࡩ࡭ࡦࡢࡹࡷࡲࠢ᤺"): None,
            bstack11l1ll1_opy_ (u"ࠧࡰ࡯ࡣࡡࡱࡥࡲ࡫᤻ࠢ"): env.get(bstack11l1ll1_opy_ (u"ࠨࡇࡐࡡࡍࡓࡇࡥࡎࡂࡏࡈࠦ᤼")),
            bstack11l1ll1_opy_ (u"ࠢࡣࡷ࡬ࡰࡩࡥ࡮ࡶ࡯ࡥࡩࡷࠨ᤽"): env.get(bstack11l1ll1_opy_ (u"ࠣࡉࡒࡣࡕࡏࡐࡆࡎࡌࡒࡊࡥࡃࡐࡗࡑࡘࡊࡘࠢ᤾"))
        }
    if env.get(bstack11l1ll1_opy_ (u"ࠤࡆࡊࡤࡈࡕࡊࡎࡇࡣࡎࡊࠢ᤿")):
        return {
            bstack11l1ll1_opy_ (u"ࠥࡲࡦࡳࡥࠣ᥀"): bstack11l1ll1_opy_ (u"ࠦࡈࡵࡤࡦࡈࡵࡩࡸ࡮ࠢ᥁"),
            bstack11l1ll1_opy_ (u"ࠧࡨࡵࡪ࡮ࡧࡣࡺࡸ࡬ࠣ᥂"): env.get(bstack11l1ll1_opy_ (u"ࠨࡃࡇࡡࡅ࡙ࡎࡒࡄࡠࡗࡕࡐࠧ᥃")),
            bstack11l1ll1_opy_ (u"ࠢ࡫ࡱࡥࡣࡳࡧ࡭ࡦࠤ᥄"): env.get(bstack11l1ll1_opy_ (u"ࠣࡅࡉࡣࡕࡏࡐࡆࡎࡌࡒࡊࡥࡎࡂࡏࡈࠦ᥅")),
            bstack11l1ll1_opy_ (u"ࠤࡥࡹ࡮ࡲࡤࡠࡰࡸࡱࡧ࡫ࡲࠣ᥆"): env.get(bstack11l1ll1_opy_ (u"ࠥࡇࡋࡥࡂࡖࡋࡏࡈࡤࡏࡄࠣ᥇"))
        }
    return {bstack11l1ll1_opy_ (u"ࠦࡧࡻࡩ࡭ࡦࡢࡲࡺࡳࡢࡦࡴࠥ᥈"): None}
def get_host_info():
    return {
        bstack11l1ll1_opy_ (u"ࠧ࡮࡯ࡴࡶࡱࡥࡲ࡫ࠢ᥉"): platform.node(),
        bstack11l1ll1_opy_ (u"ࠨࡰ࡭ࡣࡷࡪࡴࡸ࡭ࠣ᥊"): platform.system(),
        bstack11l1ll1_opy_ (u"ࠢࡵࡻࡳࡩࠧ᥋"): platform.machine(),
        bstack11l1ll1_opy_ (u"ࠣࡸࡨࡶࡸ࡯࡯࡯ࠤ᥌"): platform.version(),
        bstack11l1ll1_opy_ (u"ࠤࡤࡶࡨ࡮ࠢ᥍"): platform.architecture()[0]
    }
def bstack11l11lll_opy_():
    try:
        import selenium
        return True
    except ImportError:
        return False
def bstack11lll1l1l1l_opy_():
    if bstack1ll1l11l1_opy_.get_property(bstack11l1ll1_opy_ (u"ࠪࡦࡸࡺࡡࡤ࡭ࡢࡷࡪࡹࡳࡪࡱࡱࠫ᥎")):
        return bstack11l1ll1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࠪ᥏")
    return bstack11l1ll1_opy_ (u"ࠬࡻ࡮࡬ࡰࡲࡻࡳࡥࡧࡳ࡫ࡧࠫᥐ")
def bstack11lll11ll1l_opy_(driver):
    info = {
        bstack11l1ll1_opy_ (u"࠭ࡣࡢࡲࡤࡦ࡮ࡲࡩࡵ࡫ࡨࡷࠬᥑ"): driver.capabilities,
        bstack11l1ll1_opy_ (u"ࠧࡴࡧࡶࡷ࡮ࡵ࡮ࡠ࡫ࡧࠫᥒ"): driver.session_id,
        bstack11l1ll1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࠩᥓ"): driver.capabilities.get(bstack11l1ll1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡑࡥࡲ࡫ࠧᥔ"), None),
        bstack11l1ll1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡣࡻ࡫ࡲࡴ࡫ࡲࡲࠬᥕ"): driver.capabilities.get(bstack11l1ll1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶ࡛࡫ࡲࡴ࡫ࡲࡲࠬᥖ"), None),
        bstack11l1ll1_opy_ (u"ࠬࡶ࡬ࡢࡶࡩࡳࡷࡳࠧᥗ"): driver.capabilities.get(bstack11l1ll1_opy_ (u"࠭ࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡏࡣࡰࡩࠬᥘ"), None),
    }
    if bstack11lll1l1l1l_opy_() == bstack11l1ll1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠭ᥙ"):
        if bstack1lll111l1l_opy_():
            info[bstack11l1ll1_opy_ (u"ࠨࡲࡵࡳࡩࡻࡣࡵࠩᥚ")] = bstack11l1ll1_opy_ (u"ࠩࡤࡴࡵ࠳ࡡࡶࡶࡲࡱࡦࡺࡥࠨᥛ")
        elif driver.capabilities.get(bstack11l1ll1_opy_ (u"ࠪࡦࡸࡺࡡࡤ࡭࠽ࡳࡵࡺࡩࡰࡰࡶࠫᥜ"), {}).get(bstack11l1ll1_opy_ (u"ࠫࡹࡻࡲࡣࡱࡶࡧࡦࡲࡥࠨᥝ"), False):
            info[bstack11l1ll1_opy_ (u"ࠬࡶࡲࡰࡦࡸࡧࡹ࠭ᥞ")] = bstack11l1ll1_opy_ (u"࠭ࡴࡶࡴࡥࡳࡸࡩࡡ࡭ࡧࠪᥟ")
        else:
            info[bstack11l1ll1_opy_ (u"ࠧࡱࡴࡲࡨࡺࡩࡴࠨᥠ")] = bstack11l1ll1_opy_ (u"ࠨࡣࡸࡸࡴࡳࡡࡵࡧࠪᥡ")
    return info
def bstack1lll111l1l_opy_():
    if bstack1ll1l11l1_opy_.get_property(bstack11l1ll1_opy_ (u"ࠩࡤࡴࡵࡥࡡࡶࡶࡲࡱࡦࡺࡥࠨᥢ")):
        return True
    if bstack111l1l111_opy_(os.environ.get(bstack11l1ll1_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡌࡗࡤࡇࡐࡑࡡࡄ࡙࡙ࡕࡍࡂࡖࡈࠫᥣ"), None)):
        return True
    return False
def bstack1l1111l1l_opy_(bstack11lll1ll111_opy_, url, data, config):
    headers = config.get(bstack11l1ll1_opy_ (u"ࠫ࡭࡫ࡡࡥࡧࡵࡷࠬᥤ"), None)
    proxies = bstack1l11l1l1_opy_(config, url)
    auth = config.get(bstack11l1ll1_opy_ (u"ࠬࡧࡵࡵࡪࠪᥥ"), None)
    response = requests.request(
            bstack11lll1ll111_opy_,
            url=url,
            headers=headers,
            auth=auth,
            json=data,
            proxies=proxies
        )
    return response
def bstack1ll11ll11_opy_(bstack1l1llll1_opy_, size):
    bstack1lll1111_opy_ = []
    while len(bstack1l1llll1_opy_) > size:
        bstack1ll1l11111_opy_ = bstack1l1llll1_opy_[:size]
        bstack1lll1111_opy_.append(bstack1ll1l11111_opy_)
        bstack1l1llll1_opy_ = bstack1l1llll1_opy_[size:]
    bstack1lll1111_opy_.append(bstack1l1llll1_opy_)
    return bstack1lll1111_opy_
def bstack1l1l1111111_opy_(message, bstack1l111111ll1_opy_=False):
    os.write(1, bytes(message, bstack11l1ll1_opy_ (u"࠭ࡵࡵࡨ࠰࠼ࠬᥦ")))
    os.write(1, bytes(bstack11l1ll1_opy_ (u"ࠧ࡝ࡰࠪᥧ"), bstack11l1ll1_opy_ (u"ࠨࡷࡷࡪ࠲࠾ࠧᥨ")))
    if bstack1l111111ll1_opy_:
        with open(bstack11l1ll1_opy_ (u"ࠩࡥࡷࡹࡧࡣ࡬࠯ࡲ࠵࠶ࡿ࠭ࠨᥩ") + os.environ[bstack11l1ll1_opy_ (u"ࠪࡆࡘࡥࡔࡆࡕࡗࡓࡕ࡙࡟ࡃࡗࡌࡐࡉࡥࡈࡂࡕࡋࡉࡉࡥࡉࡅࠩᥪ")] + bstack11l1ll1_opy_ (u"ࠫ࠳ࡲ࡯ࡨࠩᥫ"), bstack11l1ll1_opy_ (u"ࠬࡧࠧᥬ")) as f:
            f.write(message + bstack11l1ll1_opy_ (u"࠭࡜࡯ࠩᥭ"))
def bstack1ll1l1l11ll_opy_():
    return os.environ[bstack11l1ll1_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡁࡖࡖࡒࡑࡆ࡚ࡉࡐࡐࠪ᥮")].lower() == bstack11l1ll1_opy_ (u"ࠨࡶࡵࡹࡪ࠭᥯")
def bstack1llll1ll11_opy_(bstack11lllll1l1l_opy_):
    return bstack11l1ll1_opy_ (u"ࠩࡾࢁ࠴ࢁࡽࠨᥰ").format(bstack1l111ll1l11_opy_, bstack11lllll1l1l_opy_)
def bstack1ll1l1ll_opy_():
    return bstack111ll1l111_opy_().replace(tzinfo=None).isoformat() + bstack11l1ll1_opy_ (u"ࠪ࡞ࠬᥱ")
def bstack11llll1lll1_opy_(start, finish):
    return (datetime.datetime.fromisoformat(finish.rstrip(bstack11l1ll1_opy_ (u"ࠫ࡟࠭ᥲ"))) - datetime.datetime.fromisoformat(start.rstrip(bstack11l1ll1_opy_ (u"ࠬࡠࠧᥳ")))).total_seconds() * 1000
def bstack1l111l1l1l1_opy_(timestamp):
    return bstack1l11111l1l1_opy_(timestamp).isoformat() + bstack11l1ll1_opy_ (u"࡚࠭ࠨᥴ")
def bstack1l1111l1l1l_opy_(bstack11lll1l1l11_opy_):
    date_format = bstack11l1ll1_opy_ (u"࡛ࠧࠦࠨࡱࠪࡪࠠࠦࡊ࠽ࠩࡒࡀࠥࡔ࠰ࠨࡪࠬ᥵")
    bstack11lll1ll1l1_opy_ = datetime.datetime.strptime(bstack11lll1l1l11_opy_, date_format)
    return bstack11lll1ll1l1_opy_.isoformat() + bstack11l1ll1_opy_ (u"ࠨ࡜ࠪ᥶")
def bstack11lll1llll1_opy_(outcome):
    _, exception, _ = outcome.excinfo or (None, None, None)
    if exception:
        return bstack11l1ll1_opy_ (u"ࠩࡩࡥ࡮ࡲࡥࡥࠩ᥷")
    else:
        return bstack11l1ll1_opy_ (u"ࠪࡴࡦࡹࡳࡦࡦࠪ᥸")
def bstack111l1l111_opy_(val):
    if val is None:
        return False
    return val.__str__().lower() == bstack11l1ll1_opy_ (u"ࠫࡹࡸࡵࡦࠩ᥹")
def bstack11llll111l1_opy_(val):
    return val.__str__().lower() == bstack11l1ll1_opy_ (u"ࠬ࡬ࡡ࡭ࡵࡨࠫ᥺")
def bstack111llll1ll_opy_(bstack1l11111l1ll_opy_=Exception, class_method=False, default_value=None):
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except bstack1l11111l1ll_opy_ as e:
                print(bstack11l1ll1_opy_ (u"ࠨࡅࡹࡥࡨࡴࡹ࡯࡯࡯ࠢ࡬ࡲࠥ࡬ࡵ࡯ࡥࡷ࡭ࡴࡴࠠࡼࡿࠣ࠱ࡃࠦࡻࡾ࠼ࠣࡿࢂࠨ᥻").format(func.__name__, bstack1l11111l1ll_opy_.__name__, str(e)))
                return default_value
        return wrapper
    def bstack11llll1l1ll_opy_(bstack11llllll111_opy_):
        def wrapped(cls, *args, **kwargs):
            try:
                return bstack11llllll111_opy_(cls, *args, **kwargs)
            except bstack1l11111l1ll_opy_ as e:
                print(bstack11l1ll1_opy_ (u"ࠢࡆࡺࡦࡩࡵࡺࡩࡰࡰࠣ࡭ࡳࠦࡦࡶࡰࡦࡸ࡮ࡵ࡮ࠡࡽࢀࠤ࠲ࡄࠠࡼࡿ࠽ࠤࢀࢃࠢ᥼").format(bstack11llllll111_opy_.__name__, bstack1l11111l1ll_opy_.__name__, str(e)))
                return default_value
        return wrapped
    if class_method:
        return bstack11llll1l1ll_opy_
    else:
        return decorator
def bstack1ll111111_opy_(bstack111l1lll1l_opy_):
    if os.getenv(bstack11l1ll1_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡂࡗࡗࡓࡒࡇࡔࡊࡑࡑࠫ᥽")) is not None:
        return bstack111l1l111_opy_(os.getenv(bstack11l1ll1_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡃࡘࡘࡔࡓࡁࡕࡋࡒࡒࠬ᥾")))
    if bstack11l1ll1_opy_ (u"ࠪࡥࡺࡺ࡯࡮ࡣࡷ࡭ࡴࡴࠧ᥿") in bstack111l1lll1l_opy_ and bstack11llll111l1_opy_(bstack111l1lll1l_opy_[bstack11l1ll1_opy_ (u"ࠫࡦࡻࡴࡰ࡯ࡤࡸ࡮ࡵ࡮ࠨᦀ")]):
        return False
    if bstack11l1ll1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡅࡺࡺ࡯࡮ࡣࡷ࡭ࡴࡴࠧᦁ") in bstack111l1lll1l_opy_ and bstack11llll111l1_opy_(bstack111l1lll1l_opy_[bstack11l1ll1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡆࡻࡴࡰ࡯ࡤࡸ࡮ࡵ࡮ࠨᦂ")]):
        return False
    return True
def bstack1l11ll1l1_opy_():
    try:
        from pytest_bdd import reporting
        bstack1l1111lll11_opy_ = os.environ.get(bstack11l1ll1_opy_ (u"ࠢࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡕࡔࡇࡕࡣࡋࡘࡁࡎࡇ࡚ࡓࡗࡑࠢᦃ"), None)
        return bstack1l1111lll11_opy_ is None or bstack1l1111lll11_opy_ == bstack11l1ll1_opy_ (u"ࠣࡲࡼࡸࡪࡹࡴ࠮ࡤࡧࡨࠧᦄ")
    except Exception as e:
        return False
def bstack1l11111l1_opy_(hub_url, CONFIG):
    if bstack1ll111111l_opy_() <= version.parse(bstack11l1ll1_opy_ (u"ࠩ࠶࠲࠶࠹࠮࠱ࠩᦅ")):
        if hub_url:
            return bstack11l1ll1_opy_ (u"ࠥ࡬ࡹࡺࡰ࠻࠱࠲ࠦᦆ") + hub_url + bstack11l1ll1_opy_ (u"ࠦ࠿࠾࠰࠰ࡹࡧ࠳࡭ࡻࡢࠣᦇ")
        return bstack1ll11l1l1l_opy_
    if hub_url:
        return bstack11l1ll1_opy_ (u"ࠧ࡮ࡴࡵࡲࡶ࠾࠴࠵ࠢᦈ") + hub_url + bstack11l1ll1_opy_ (u"ࠨ࠯ࡸࡦ࠲࡬ࡺࡨࠢᦉ")
    return bstack11l1l1l1_opy_
def bstack11lllll1lll_opy_():
    return isinstance(os.getenv(bstack11l1ll1_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡐ࡚ࡖࡈࡗ࡙ࡥࡐࡍࡗࡊࡍࡓ࠭ᦊ")), str)
def bstack1l1ll11l11_opy_(url):
    return urlparse(url).hostname
def bstack1l11llll1_opy_(hostname):
    for bstack1l1l111ll_opy_ in bstack1lll1111l1_opy_:
        regex = re.compile(bstack1l1l111ll_opy_)
        if regex.match(hostname):
            return True
    return False
def bstack1l11111111l_opy_(bstack11lllllll11_opy_, file_name, logger):
    bstack1l11l1llll_opy_ = os.path.join(os.path.expanduser(bstack11l1ll1_opy_ (u"ࠨࢀࠪᦋ")), bstack11lllllll11_opy_)
    try:
        if not os.path.exists(bstack1l11l1llll_opy_):
            os.makedirs(bstack1l11l1llll_opy_)
        file_path = os.path.join(os.path.expanduser(bstack11l1ll1_opy_ (u"ࠩࢁࠫᦌ")), bstack11lllllll11_opy_, file_name)
        if not os.path.isfile(file_path):
            with open(file_path, bstack11l1ll1_opy_ (u"ࠪࡻࠬᦍ")):
                pass
            with open(file_path, bstack11l1ll1_opy_ (u"ࠦࡼ࠱ࠢᦎ")) as outfile:
                json.dump({}, outfile)
        return file_path
    except Exception as e:
        logger.debug(bstack1l1l11ll_opy_.format(str(e)))
def bstack11lll1l11l1_opy_(file_name, key, value, logger):
    file_path = bstack1l11111111l_opy_(bstack11l1ll1_opy_ (u"ࠬ࠴ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࠬᦏ"), file_name, logger)
    if file_path != None:
        if os.path.exists(file_path):
            bstack11lll11l_opy_ = json.load(open(file_path, bstack11l1ll1_opy_ (u"࠭ࡲࡣࠩᦐ")))
        else:
            bstack11lll11l_opy_ = {}
        bstack11lll11l_opy_[key] = value
        with open(file_path, bstack11l1ll1_opy_ (u"ࠢࡸ࠭ࠥᦑ")) as outfile:
            json.dump(bstack11lll11l_opy_, outfile)
def bstack1l11l11l1l_opy_(file_name, logger):
    file_path = bstack1l11111111l_opy_(bstack11l1ll1_opy_ (u"ࠨ࠰ࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࠨᦒ"), file_name, logger)
    bstack11lll11l_opy_ = {}
    if file_path != None and os.path.exists(file_path):
        with open(file_path, bstack11l1ll1_opy_ (u"ࠩࡵࠫᦓ")) as bstack1ll1llll_opy_:
            bstack11lll11l_opy_ = json.load(bstack1ll1llll_opy_)
    return bstack11lll11l_opy_
def bstack11lllll11l_opy_(file_path, logger):
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        logger.debug(bstack11l1ll1_opy_ (u"ࠪࡉࡷࡸ࡯ࡳࠢ࡬ࡲࠥࡪࡥ࡭ࡧࡷ࡭ࡳ࡭ࠠࡧ࡫࡯ࡩ࠿ࠦࠧᦔ") + file_path + bstack11l1ll1_opy_ (u"ࠫࠥ࠭ᦕ") + str(e))
def bstack1ll111111l_opy_():
    from selenium import webdriver
    return version.parse(webdriver.__version__)
class Notset:
    def __repr__(self):
        return bstack11l1ll1_opy_ (u"ࠧࡂࡎࡐࡖࡖࡉ࡙ࡄࠢᦖ")
def bstack1l1lll1l1l_opy_(config):
    if bstack11l1ll1_opy_ (u"࠭ࡩࡴࡒ࡯ࡥࡾࡽࡲࡪࡩ࡫ࡸࠬᦗ") in config:
        del (config[bstack11l1ll1_opy_ (u"ࠧࡪࡵࡓࡰࡦࡿࡷࡳ࡫ࡪ࡬ࡹ࠭ᦘ")])
        return False
    if bstack1ll111111l_opy_() < version.parse(bstack11l1ll1_opy_ (u"ࠨ࠵࠱࠸࠳࠶ࠧᦙ")):
        return False
    if bstack1ll111111l_opy_() >= version.parse(bstack11l1ll1_opy_ (u"ࠩ࠷࠲࠶࠴࠵ࠨᦚ")):
        return True
    if bstack11l1ll1_opy_ (u"ࠪࡹࡸ࡫ࡗ࠴ࡅࠪᦛ") in config and config[bstack11l1ll1_opy_ (u"ࠫࡺࡹࡥࡘ࠵ࡆࠫᦜ")] is False:
        return False
    else:
        return True
def bstack11l111ll_opy_(args_list, bstack11lllll1ll1_opy_):
    index = -1
    for value in bstack11lllll1ll1_opy_:
        try:
            index = args_list.index(value)
            return index
        except Exception as e:
            return index
    return index
class Result:
    def __init__(self, result=None, duration=None, exception=None, bstack11l11l11ll_opy_=None):
        self.result = result
        self.duration = duration
        self.exception = exception
        self.exception_type = type(self.exception).__name__ if exception else None
        self.bstack11l11l11ll_opy_ = bstack11l11l11ll_opy_
    @classmethod
    def passed(cls):
        return Result(result=bstack11l1ll1_opy_ (u"ࠬࡶࡡࡴࡵࡨࡨࠬᦝ"))
    @classmethod
    def failed(cls, exception=None):
        return Result(result=bstack11l1ll1_opy_ (u"࠭ࡦࡢ࡫࡯ࡩࡩ࠭ᦞ"), exception=exception)
    def bstack111l1l1111_opy_(self):
        if self.result != bstack11l1ll1_opy_ (u"ࠧࡧࡣ࡬ࡰࡪࡪࠧᦟ"):
            return None
        if isinstance(self.exception_type, str) and bstack11l1ll1_opy_ (u"ࠣࡃࡶࡷࡪࡸࡴࡪࡱࡱࠦᦠ") in self.exception_type:
            return bstack11l1ll1_opy_ (u"ࠤࡄࡷࡸ࡫ࡲࡵ࡫ࡲࡲࡊࡸࡲࡰࡴࠥᦡ")
        return bstack11l1ll1_opy_ (u"࡙ࠥࡳ࡮ࡡ࡯ࡦ࡯ࡩࡩࡋࡲࡳࡱࡵࠦᦢ")
    def bstack1l111111l11_opy_(self):
        if self.result != bstack11l1ll1_opy_ (u"ࠫ࡫ࡧࡩ࡭ࡧࡧࠫᦣ"):
            return None
        if self.bstack11l11l11ll_opy_:
            return self.bstack11l11l11ll_opy_
        return bstack1l1111ll1ll_opy_(self.exception)
def bstack1l1111ll1ll_opy_(exc):
    return [traceback.format_exception(exc)]
def bstack11llll1l111_opy_(message):
    if isinstance(message, str):
        return not bool(message and message.strip())
    return True
def bstack1ll1l1lll_opy_(object, key, default_value):
    if not object or not object.__dict__:
        return default_value
    if key in object.__dict__.keys():
        return object.__dict__.get(key)
    return default_value
def bstack11lllll1l_opy_(config, logger):
    try:
        import playwright
        bstack1l1111l1lll_opy_ = playwright.__file__
        bstack1l111l111l1_opy_ = os.path.split(bstack1l1111l1lll_opy_)
        bstack11llllll11l_opy_ = bstack1l111l111l1_opy_[0] + bstack11l1ll1_opy_ (u"ࠬ࠵ࡤࡳ࡫ࡹࡩࡷ࠵ࡰࡢࡥ࡮ࡥ࡬࡫࠯࡭࡫ࡥ࠳ࡨࡲࡩ࠰ࡥ࡯࡭࠳ࡰࡳࠨᦤ")
        os.environ[bstack11l1ll1_opy_ (u"࠭ࡇࡍࡑࡅࡅࡑࡥࡁࡈࡇࡑࡘࡤࡎࡔࡕࡒࡢࡔࡗࡕࡘ࡚ࠩᦥ")] = bstack1l1ll1lll1_opy_(config)
        with open(bstack11llllll11l_opy_, bstack11l1ll1_opy_ (u"ࠧࡳࠩᦦ")) as f:
            bstack1l1l1111l1_opy_ = f.read()
            bstack1l111l1lll1_opy_ = bstack11l1ll1_opy_ (u"ࠨࡩ࡯ࡳࡧࡧ࡬࠮ࡣࡪࡩࡳࡺࠧᦧ")
            bstack1l1111l1l11_opy_ = bstack1l1l1111l1_opy_.find(bstack1l111l1lll1_opy_)
            if bstack1l1111l1l11_opy_ == -1:
              process = subprocess.Popen(bstack11l1ll1_opy_ (u"ࠤࡱࡴࡲࠦࡩ࡯ࡵࡷࡥࡱࡲࠠࡨ࡮ࡲࡦࡦࡲ࠭ࡢࡩࡨࡲࡹࠨᦨ"), shell=True, cwd=bstack1l111l111l1_opy_[0])
              process.wait()
              bstack11llll1llll_opy_ = bstack11l1ll1_opy_ (u"ࠪࠦࡺࡹࡥࠡࡵࡷࡶ࡮ࡩࡴࠣ࠽ࠪᦩ")
              bstack11llll1ll1l_opy_ = bstack11l1ll1_opy_ (u"ࠦࠧࠨࠠ࡝ࠤࡸࡷࡪࠦࡳࡵࡴ࡬ࡧࡹࡢࠢ࠼ࠢࡦࡳࡳࡹࡴࠡࡽࠣࡦࡴࡵࡴࡴࡶࡵࡥࡵࠦࡽࠡ࠿ࠣࡶࡪࡷࡵࡪࡴࡨࠬࠬ࡭࡬ࡰࡤࡤࡰ࠲ࡧࡧࡦࡰࡷࠫ࠮ࡁࠠࡪࡨࠣࠬࡵࡸ࡯ࡤࡧࡶࡷ࠳࡫࡮ࡷ࠰ࡊࡐࡔࡈࡁࡍࡡࡄࡋࡊࡔࡔࡠࡊࡗࡘࡕࡥࡐࡓࡑ࡛࡝࠮ࠦࡢࡰࡱࡷࡷࡹࡸࡡࡱࠪࠬ࠿ࠥࠨࠢࠣᦪ")
              bstack11lll1l1ll1_opy_ = bstack1l1l1111l1_opy_.replace(bstack11llll1llll_opy_, bstack11llll1ll1l_opy_)
              with open(bstack11llllll11l_opy_, bstack11l1ll1_opy_ (u"ࠬࡽࠧᦫ")) as f:
                f.write(bstack11lll1l1ll1_opy_)
    except Exception as e:
        logger.error(bstack11ll1l11l1_opy_.format(str(e)))
def bstack11111ll1l_opy_():
  try:
    bstack1l1111l11l1_opy_ = os.path.join(tempfile.gettempdir(), bstack11l1ll1_opy_ (u"࠭࡯ࡱࡶ࡬ࡱࡦࡲ࡟ࡩࡷࡥࡣࡺࡸ࡬࠯࡬ࡶࡳࡳ࠭᦬"))
    bstack11lll1lll11_opy_ = []
    if os.path.exists(bstack1l1111l11l1_opy_):
      with open(bstack1l1111l11l1_opy_) as f:
        bstack11lll1lll11_opy_ = json.load(f)
      os.remove(bstack1l1111l11l1_opy_)
    return bstack11lll1lll11_opy_
  except:
    pass
  return []
def bstack1l1111l11_opy_(bstack1lll1lllll_opy_):
  try:
    bstack11lll1lll11_opy_ = []
    bstack1l1111l11l1_opy_ = os.path.join(tempfile.gettempdir(), bstack11l1ll1_opy_ (u"ࠧࡰࡲࡷ࡭ࡲࡧ࡬ࡠࡪࡸࡦࡤࡻࡲ࡭࠰࡭ࡷࡴࡴࠧ᦭"))
    if os.path.exists(bstack1l1111l11l1_opy_):
      with open(bstack1l1111l11l1_opy_) as f:
        bstack11lll1lll11_opy_ = json.load(f)
    bstack11lll1lll11_opy_.append(bstack1lll1lllll_opy_)
    with open(bstack1l1111l11l1_opy_, bstack11l1ll1_opy_ (u"ࠨࡹࠪ᦮")) as f:
        json.dump(bstack11lll1lll11_opy_, f)
  except:
    pass
def bstack1l1ll11lll_opy_(logger, bstack1l111111111_opy_ = False):
  try:
    test_name = os.environ.get(bstack11l1ll1_opy_ (u"ࠩࡓ࡝࡙ࡋࡓࡕࡡࡗࡉࡘ࡚࡟ࡏࡃࡐࡉࠬ᦯"), bstack11l1ll1_opy_ (u"ࠪࠫᦰ"))
    if test_name == bstack11l1ll1_opy_ (u"ࠫࠬᦱ"):
        test_name = threading.current_thread().__dict__.get(bstack11l1ll1_opy_ (u"ࠬࡶࡹࡵࡧࡶࡸࡇࡪࡤࡠࡶࡨࡷࡹࡥ࡮ࡢ࡯ࡨࠫᦲ"), bstack11l1ll1_opy_ (u"࠭ࠧᦳ"))
    bstack11llll1ll11_opy_ = bstack11l1ll1_opy_ (u"ࠧ࠭ࠢࠪᦴ").join(threading.current_thread().bstackTestErrorMessages)
    if bstack1l111111111_opy_:
        bstack1ll1lll1l_opy_ = os.environ.get(bstack11l1ll1_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡑࡎࡄࡘࡋࡕࡒࡎࡡࡌࡒࡉࡋࡘࠨᦵ"), bstack11l1ll1_opy_ (u"ࠩ࠳ࠫᦶ"))
        bstack1l11l1ll11_opy_ = {bstack11l1ll1_opy_ (u"ࠪࡲࡦࡳࡥࠨᦷ"): test_name, bstack11l1ll1_opy_ (u"ࠫࡪࡸࡲࡰࡴࠪᦸ"): bstack11llll1ll11_opy_, bstack11l1ll1_opy_ (u"ࠬ࡯࡮ࡥࡧࡻࠫᦹ"): bstack1ll1lll1l_opy_}
        bstack11lllllll1l_opy_ = []
        bstack11llll11ll1_opy_ = os.path.join(tempfile.gettempdir(), bstack11l1ll1_opy_ (u"࠭ࡰࡺࡶࡨࡷࡹࡥࡰࡱࡲࡢࡩࡷࡸ࡯ࡳࡡ࡯࡭ࡸࡺ࠮࡫ࡵࡲࡲࠬᦺ"))
        if os.path.exists(bstack11llll11ll1_opy_):
            with open(bstack11llll11ll1_opy_) as f:
                bstack11lllllll1l_opy_ = json.load(f)
        bstack11lllllll1l_opy_.append(bstack1l11l1ll11_opy_)
        with open(bstack11llll11ll1_opy_, bstack11l1ll1_opy_ (u"ࠧࡸࠩᦻ")) as f:
            json.dump(bstack11lllllll1l_opy_, f)
    else:
        bstack1l11l1ll11_opy_ = {bstack11l1ll1_opy_ (u"ࠨࡰࡤࡱࡪ࠭ᦼ"): test_name, bstack11l1ll1_opy_ (u"ࠩࡨࡶࡷࡵࡲࠨᦽ"): bstack11llll1ll11_opy_, bstack11l1ll1_opy_ (u"ࠪ࡭ࡳࡪࡥࡹࠩᦾ"): str(multiprocessing.current_process().name)}
        if bstack11l1ll1_opy_ (u"ࠫࡧࡹࡴࡢࡥ࡮ࡣࡪࡸࡲࡰࡴࡢࡰ࡮ࡹࡴࠨᦿ") not in multiprocessing.current_process().__dict__.keys():
            multiprocessing.current_process().bstack_error_list = []
        multiprocessing.current_process().bstack_error_list.append(bstack1l11l1ll11_opy_)
  except Exception as e:
      logger.warn(bstack11l1ll1_opy_ (u"࡛ࠧ࡮ࡢࡤ࡯ࡩࠥࡺ࡯ࠡࡵࡷࡳࡷ࡫ࠠࡱࡻࡷࡩࡸࡺࠠࡧࡷࡱࡲࡪࡲࠠࡥࡣࡷࡥ࠿ࠦࡻࡾࠤᧀ").format(e))
def bstack1ll1l11l1l_opy_(error_message, test_name, index, logger):
  try:
    bstack1l1111lll1l_opy_ = []
    bstack1l11l1ll11_opy_ = {bstack11l1ll1_opy_ (u"࠭࡮ࡢ࡯ࡨࠫᧁ"): test_name, bstack11l1ll1_opy_ (u"ࠧࡦࡴࡵࡳࡷ࠭ᧂ"): error_message, bstack11l1ll1_opy_ (u"ࠨ࡫ࡱࡨࡪࡾࠧᧃ"): index}
    bstack1l1111111ll_opy_ = os.path.join(tempfile.gettempdir(), bstack11l1ll1_opy_ (u"ࠩࡵࡳࡧࡵࡴࡠࡧࡵࡶࡴࡸ࡟࡭࡫ࡶࡸ࠳ࡰࡳࡰࡰࠪᧄ"))
    if os.path.exists(bstack1l1111111ll_opy_):
        with open(bstack1l1111111ll_opy_) as f:
            bstack1l1111lll1l_opy_ = json.load(f)
    bstack1l1111lll1l_opy_.append(bstack1l11l1ll11_opy_)
    with open(bstack1l1111111ll_opy_, bstack11l1ll1_opy_ (u"ࠪࡻࠬᧅ")) as f:
        json.dump(bstack1l1111lll1l_opy_, f)
  except Exception as e:
    logger.warn(bstack11l1ll1_opy_ (u"࡚ࠦࡴࡡࡣ࡮ࡨࠤࡹࡵࠠࡴࡶࡲࡶࡪࠦࡲࡰࡤࡲࡸࠥ࡬ࡵ࡯ࡰࡨࡰࠥࡪࡡࡵࡣ࠽ࠤࢀࢃࠢᧆ").format(e))
def bstack1l1111l1_opy_(bstack1ll11l11l_opy_, name, logger):
  try:
    bstack1l11l1ll11_opy_ = {bstack11l1ll1_opy_ (u"ࠬࡴࡡ࡮ࡧࠪᧇ"): name, bstack11l1ll1_opy_ (u"࠭ࡥࡳࡴࡲࡶࠬᧈ"): bstack1ll11l11l_opy_, bstack11l1ll1_opy_ (u"ࠧࡪࡰࡧࡩࡽ࠭ᧉ"): str(threading.current_thread()._name)}
    return bstack1l11l1ll11_opy_
  except Exception as e:
    logger.warn(bstack11l1ll1_opy_ (u"ࠣࡗࡱࡥࡧࡲࡥࠡࡶࡲࠤࡸࡺ࡯ࡳࡧࠣࡦࡪ࡮ࡡࡷࡧࠣࡪࡺࡴ࡮ࡦ࡮ࠣࡨࡦࡺࡡ࠻ࠢࡾࢁࠧ᧊").format(e))
  return
def bstack1l111l11lll_opy_():
    return platform.system() == bstack11l1ll1_opy_ (u"࡚ࠩ࡭ࡳࡪ࡯ࡸࡵࠪ᧋")
def bstack11ll11l1_opy_(bstack11lll1lllll_opy_, config, logger):
    bstack11llll1111l_opy_ = {}
    try:
        return {key: config[key] for key in config if bstack11lll1lllll_opy_.match(key)}
    except Exception as e:
        logger.debug(bstack11l1ll1_opy_ (u"࡙ࠥࡳࡧࡢ࡭ࡧࠣࡸࡴࠦࡦࡪ࡮ࡷࡩࡷࠦࡣࡰࡰࡩ࡭࡬ࠦ࡫ࡦࡻࡶࠤࡧࡿࠠࡳࡧࡪࡩࡽࠦ࡭ࡢࡶࡦ࡬࠿ࠦࡻࡾࠤ᧌").format(e))
    return bstack11llll1111l_opy_
def bstack11lll1l1lll_opy_(bstack1l1111l1111_opy_, bstack1l111l1l111_opy_):
    bstack11lll11lll1_opy_ = version.parse(bstack1l1111l1111_opy_)
    bstack1l111l111ll_opy_ = version.parse(bstack1l111l1l111_opy_)
    if bstack11lll11lll1_opy_ > bstack1l111l111ll_opy_:
        return 1
    elif bstack11lll11lll1_opy_ < bstack1l111l111ll_opy_:
        return -1
    else:
        return 0
def bstack111ll1l111_opy_():
    return datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
def bstack1l11111l1l1_opy_(timestamp):
    return datetime.datetime.fromtimestamp(timestamp, datetime.timezone.utc).replace(tzinfo=None)
def bstack1l1111lllll_opy_(framework):
    from browserstack_sdk._version import __version__
    return str(framework) + str(__version__)
def bstack1l1ll11l_opy_(options, framework, bstack1l11l1ll1_opy_={}):
    if options is None:
        return
    if getattr(options, bstack11l1ll1_opy_ (u"ࠫ࡬࡫ࡴࠨ᧍"), None):
        caps = options
    else:
        caps = options.to_capabilities()
    bstack1lll111111_opy_ = caps.get(bstack11l1ll1_opy_ (u"ࠬࡨࡳࡵࡣࡦ࡯࠿ࡵࡰࡵ࡫ࡲࡲࡸ࠭᧎"))
    bstack11llll11111_opy_ = True
    bstack11ll1ll11l_opy_ = os.environ[bstack11l1ll1_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤ࡚ࡅࡔࡖࡋ࡙ࡇࡥࡕࡖࡋࡇࠫ᧏")]
    if bstack11llll111l1_opy_(caps.get(bstack11l1ll1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡵࡴࡧ࡚࠷ࡈ࠭᧐"))) or bstack11llll111l1_opy_(caps.get(bstack11l1ll1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡶࡵࡨࡣࡼ࠹ࡣࠨ᧑"))):
        bstack11llll11111_opy_ = False
    if bstack1l1lll1l1l_opy_({bstack11l1ll1_opy_ (u"ࠤࡸࡷࡪ࡝࠳ࡄࠤ᧒"): bstack11llll11111_opy_}):
        bstack1lll111111_opy_ = bstack1lll111111_opy_ or {}
        bstack1lll111111_opy_[bstack11l1ll1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡕࡇࡏࠬ᧓")] = bstack1l1111lllll_opy_(framework)
        bstack1lll111111_opy_[bstack11l1ll1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡄࡹࡹࡵ࡭ࡢࡶ࡬ࡳࡳ࠭᧔")] = bstack1ll1l1l11ll_opy_()
        bstack1lll111111_opy_[bstack11l1ll1_opy_ (u"ࠬࡺࡥࡴࡶ࡫ࡹࡧࡈࡵࡪ࡮ࡧ࡙ࡺ࡯ࡤࠨ᧕")] = bstack11ll1ll11l_opy_
        bstack1lll111111_opy_[bstack11l1ll1_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡕࡸ࡯ࡥࡷࡦࡸࡒࡧࡰࠨ᧖")] = bstack1l11l1ll1_opy_
        if getattr(options, bstack11l1ll1_opy_ (u"ࠧࡴࡧࡷࡣࡨࡧࡰࡢࡤ࡬ࡰ࡮ࡺࡹࠨ᧗"), None):
            options.set_capability(bstack11l1ll1_opy_ (u"ࠨࡤࡶࡸࡦࡩ࡫࠻ࡱࡳࡸ࡮ࡵ࡮ࡴࠩ᧘"), bstack1lll111111_opy_)
        else:
            options[bstack11l1ll1_opy_ (u"ࠩࡥࡷࡹࡧࡣ࡬࠼ࡲࡴࡹ࡯࡯࡯ࡵࠪ᧙")] = bstack1lll111111_opy_
    else:
        if getattr(options, bstack11l1ll1_opy_ (u"ࠪࡷࡪࡺ࡟ࡤࡣࡳࡥࡧ࡯࡬ࡪࡶࡼࠫ᧚"), None):
            options.set_capability(bstack11l1ll1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡕࡇࡏࠬ᧛"), bstack1l1111lllll_opy_(framework))
            options.set_capability(bstack11l1ll1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡄࡹࡹࡵ࡭ࡢࡶ࡬ࡳࡳ࠭᧜"), bstack1ll1l1l11ll_opy_())
            options.set_capability(bstack11l1ll1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡺࡥࡴࡶ࡫ࡹࡧࡈࡵࡪ࡮ࡧ࡙ࡺ࡯ࡤࠨ᧝"), bstack11ll1ll11l_opy_)
            options.set_capability(bstack11l1ll1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡢࡶ࡫࡯ࡨࡕࡸ࡯ࡥࡷࡦࡸࡒࡧࡰࠨ᧞"), bstack1l11l1ll1_opy_)
        else:
            options[bstack11l1ll1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࡙ࡄࡌࠩ᧟")] = bstack1l1111lllll_opy_(framework)
            options[bstack11l1ll1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࡁࡶࡶࡲࡱࡦࡺࡩࡰࡰࠪ᧠")] = bstack1ll1l1l11ll_opy_()
            options[bstack11l1ll1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡷࡩࡸࡺࡨࡶࡤࡅࡹ࡮ࡲࡤࡖࡷ࡬ࡨࠬ᧡")] = bstack11ll1ll11l_opy_
            options[bstack11l1ll1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡦࡺ࡯࡬ࡥࡒࡵࡳࡩࡻࡣࡵࡏࡤࡴࠬ᧢")] = bstack1l11l1ll1_opy_
    return options
def bstack11llll11lll_opy_(bstack11lllll11l1_opy_, framework):
    bstack1l11l1ll1_opy_ = bstack1ll1l11l1_opy_.get_property(bstack11l1ll1_opy_ (u"ࠧࡖࡌࡂ࡛࡚ࡖࡎࡍࡈࡕࡡࡓࡖࡔࡊࡕࡄࡖࡢࡑࡆࡖࠢ᧣"))
    if bstack11lllll11l1_opy_ and len(bstack11lllll11l1_opy_.split(bstack11l1ll1_opy_ (u"࠭ࡣࡢࡲࡶࡁࠬ᧤"))) > 1:
        ws_url = bstack11lllll11l1_opy_.split(bstack11l1ll1_opy_ (u"ࠧࡤࡣࡳࡷࡂ࠭᧥"))[0]
        if bstack11l1ll1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡤࡱࡰࠫ᧦") in ws_url:
            from browserstack_sdk._version import __version__
            bstack11lllll111l_opy_ = json.loads(urllib.parse.unquote(bstack11lllll11l1_opy_.split(bstack11l1ll1_opy_ (u"ࠩࡦࡥࡵࡹ࠽ࠨ᧧"))[1]))
            bstack11lllll111l_opy_ = bstack11lllll111l_opy_ or {}
            bstack11ll1ll11l_opy_ = os.environ[bstack11l1ll1_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡗࡉࡘ࡚ࡈࡖࡄࡢ࡙࡚ࡏࡄࠨ᧨")]
            bstack11lllll111l_opy_[bstack11l1ll1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡕࡇࡏࠬ᧩")] = str(framework) + str(__version__)
            bstack11lllll111l_opy_[bstack11l1ll1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡄࡹࡹࡵ࡭ࡢࡶ࡬ࡳࡳ࠭᧪")] = bstack1ll1l1l11ll_opy_()
            bstack11lllll111l_opy_[bstack11l1ll1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡺࡥࡴࡶ࡫ࡹࡧࡈࡵࡪ࡮ࡧ࡙ࡺ࡯ࡤࠨ᧫")] = bstack11ll1ll11l_opy_
            bstack11lllll111l_opy_[bstack11l1ll1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡢࡶ࡫࡯ࡨࡕࡸ࡯ࡥࡷࡦࡸࡒࡧࡰࠨ᧬")] = bstack1l11l1ll1_opy_
            bstack11lllll11l1_opy_ = bstack11lllll11l1_opy_.split(bstack11l1ll1_opy_ (u"ࠨࡥࡤࡴࡸࡃࠧ᧭"))[0] + bstack11l1ll1_opy_ (u"ࠩࡦࡥࡵࡹ࠽ࠨ᧮") + urllib.parse.quote(json.dumps(bstack11lllll111l_opy_))
    return bstack11lllll11l1_opy_
def bstack1l1ll1l1l_opy_():
    global bstack1l1ll1l1_opy_
    from playwright._impl._browser_type import BrowserType
    bstack1l1ll1l1_opy_ = BrowserType.connect
    return bstack1l1ll1l1_opy_
def bstack1l11lll111_opy_(framework_name):
    global bstack111111ll1_opy_
    bstack111111ll1_opy_ = framework_name
    return framework_name
def bstack11lll1ll1_opy_(self, *args, **kwargs):
    global bstack1l1ll1l1_opy_
    try:
        global bstack111111ll1_opy_
        if bstack11l1ll1_opy_ (u"ࠪࡻࡸࡋ࡮ࡥࡲࡲ࡭ࡳࡺࠧ᧯") in kwargs:
            kwargs[bstack11l1ll1_opy_ (u"ࠫࡼࡹࡅ࡯ࡦࡳࡳ࡮ࡴࡴࠨ᧰")] = bstack11llll11lll_opy_(
                kwargs.get(bstack11l1ll1_opy_ (u"ࠬࡽࡳࡆࡰࡧࡴࡴ࡯࡮ࡵࠩ᧱"), None),
                bstack111111ll1_opy_
            )
    except Exception as e:
        logger.error(bstack11l1ll1_opy_ (u"ࠨࡅࡳࡴࡲࡶࠥࡽࡨࡦࡰࠣࡴࡷࡵࡣࡦࡵࡶ࡭ࡳ࡭ࠠࡔࡆࡎࠤࡨࡧࡰࡴ࠼ࠣࡿࢂࠨ᧲").format(str(e)))
    return bstack1l1ll1l1_opy_(self, *args, **kwargs)
def bstack1l111l11l1l_opy_(bstack1l11111ll11_opy_, proxies):
    proxy_settings = {}
    try:
        if not proxies:
            proxies = bstack1l11l1l1_opy_(bstack1l11111ll11_opy_, bstack11l1ll1_opy_ (u"ࠢࠣ᧳"))
        if proxies and proxies.get(bstack11l1ll1_opy_ (u"ࠣࡪࡷࡸࡵࡹࠢ᧴")):
            parsed_url = urlparse(proxies.get(bstack11l1ll1_opy_ (u"ࠤ࡫ࡸࡹࡶࡳࠣ᧵")))
            if parsed_url and parsed_url.hostname: proxy_settings[bstack11l1ll1_opy_ (u"ࠪࡴࡷࡵࡸࡺࡊࡲࡷࡹ࠭᧶")] = str(parsed_url.hostname)
            if parsed_url and parsed_url.port: proxy_settings[bstack11l1ll1_opy_ (u"ࠫࡵࡸ࡯ࡹࡻࡓࡳࡷࡺࠧ᧷")] = str(parsed_url.port)
            if parsed_url and parsed_url.username: proxy_settings[bstack11l1ll1_opy_ (u"ࠬࡶࡲࡰࡺࡼ࡙ࡸ࡫ࡲࠨ᧸")] = str(parsed_url.username)
            if parsed_url and parsed_url.password: proxy_settings[bstack11l1ll1_opy_ (u"࠭ࡰࡳࡱࡻࡽࡕࡧࡳࡴࠩ᧹")] = str(parsed_url.password)
        return proxy_settings
    except:
        return proxy_settings
def bstack11l1ll11l_opy_(bstack1l11111ll11_opy_):
    bstack11lll1ll11l_opy_ = {
        bstack1l111lll1ll_opy_[bstack11lll11llll_opy_]: bstack1l11111ll11_opy_[bstack11lll11llll_opy_]
        for bstack11lll11llll_opy_ in bstack1l11111ll11_opy_
        if bstack11lll11llll_opy_ in bstack1l111lll1ll_opy_
    }
    bstack11lll1ll11l_opy_[bstack11l1ll1_opy_ (u"ࠢࡱࡴࡲࡼࡾ࡙ࡥࡵࡶ࡬ࡲ࡬ࡹࠢ᧺")] = bstack1l111l11l1l_opy_(bstack1l11111ll11_opy_, bstack1ll1l11l1_opy_.get_property(bstack11l1ll1_opy_ (u"ࠣࡲࡵࡳࡽࡿࡓࡦࡶࡷ࡭ࡳ࡭ࡳࠣ᧻")))
    bstack1l111l1l11l_opy_ = [element.lower() for element in bstack1l11l1l11l1_opy_]
    bstack1l111l11111_opy_(bstack11lll1ll11l_opy_, bstack1l111l1l11l_opy_)
    return bstack11lll1ll11l_opy_
def bstack1l111l11111_opy_(d, keys):
    for key in list(d.keys()):
        if key.lower() in keys:
            d[key] = bstack11l1ll1_opy_ (u"ࠤ࠭࠮࠯࠰ࠢ᧼")
    for value in d.values():
        if isinstance(value, dict):
            bstack1l111l11111_opy_(value, keys)
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    bstack1l111l11111_opy_(item, keys)
def bstack11llll1l1l1_opy_():
    bstack1l11111lll1_opy_ = [os.environ.get(bstack11l1ll1_opy_ (u"ࠥࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡉࡍࡑࡋࡓࡠࡆࡌࡖࠧ᧽")), os.path.join(os.path.expanduser(bstack11l1ll1_opy_ (u"ࠦࢃࠨ᧾")), bstack11l1ll1_opy_ (u"ࠬ࠴ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࠬ᧿")), os.path.join(bstack11l1ll1_opy_ (u"࠭࠯ࡵ࡯ࡳࠫᨀ"), bstack11l1ll1_opy_ (u"ࠧ࠯ࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࠧᨁ"))]
    for path in bstack1l11111lll1_opy_:
        if path is None:
            continue
        try:
            if os.path.exists(path):
                logger.debug(bstack11l1ll1_opy_ (u"ࠣࡈ࡬ࡰࡪࠦࠧࠣᨂ") + str(path) + bstack11l1ll1_opy_ (u"ࠤࠪࠤࡪࡾࡩࡴࡶࡶ࠲ࠧᨃ"))
                if not os.access(path, os.W_OK):
                    logger.debug(bstack11l1ll1_opy_ (u"ࠥࡋ࡮ࡼࡩ࡯ࡩࠣࡴࡪࡸ࡭ࡪࡵࡶ࡭ࡴࡴࡳࠡࡨࡲࡶࠥ࠭ࠢᨄ") + str(path) + bstack11l1ll1_opy_ (u"ࠦࠬࠨᨅ"))
                    os.chmod(path, 0o777)
                else:
                    logger.debug(bstack11l1ll1_opy_ (u"ࠧࡌࡩ࡭ࡧࠣࠫࠧᨆ") + str(path) + bstack11l1ll1_opy_ (u"ࠨࠧࠡࡣ࡯ࡶࡪࡧࡤࡺࠢ࡫ࡥࡸࠦࡴࡩࡧࠣࡶࡪࡷࡵࡪࡴࡨࡨࠥࡶࡥࡳ࡯࡬ࡷࡸ࡯࡯࡯ࡵ࠱ࠦᨇ"))
            else:
                logger.debug(bstack11l1ll1_opy_ (u"ࠢࡄࡴࡨࡥࡹ࡯࡮ࡨࠢࡩ࡭ࡱ࡫ࠠࠨࠤᨈ") + str(path) + bstack11l1ll1_opy_ (u"ࠣࠩࠣࡻ࡮ࡺࡨࠡࡹࡵ࡭ࡹ࡫ࠠࡱࡧࡵࡱ࡮ࡹࡳࡪࡱࡱ࠲ࠧᨉ"))
                os.makedirs(path, exist_ok=True)
                os.chmod(path, 0o777)
            logger.debug(bstack11l1ll1_opy_ (u"ࠤࡒࡴࡪࡸࡡࡵ࡫ࡲࡲࠥࡹࡵࡤࡥࡨࡩࡩ࡫ࡤࠡࡨࡲࡶࠥ࠭ࠢᨊ") + str(path) + bstack11l1ll1_opy_ (u"ࠥࠫ࠳ࠨᨋ"))
            return path
        except Exception as e:
            logger.debug(bstack11l1ll1_opy_ (u"ࠦࡋࡧࡩ࡭ࡧࡧࠤࡹࡵࠠࡴࡧࡷࠤࡺࡶࠠࡧ࡫࡯ࡩࠥ࠭ࡻࡱࡣࡷ࡬ࢂ࠭࠺ࠡࠤᨌ") + str(e) + bstack11l1ll1_opy_ (u"ࠧࠨᨍ"))
    logger.debug(bstack11l1ll1_opy_ (u"ࠨࡁ࡭࡮ࠣࡴࡦࡺࡨࡴࠢࡩࡥ࡮ࡲࡥࡥ࠰ࠥᨎ"))
    return None
@measure(event_name=EVENTS.bstack1l11l11111l_opy_, stage=STAGE.bstack1l1ll1llll_opy_)
def bstack1111111111_opy_(binary_path, bstack1111l111ll_opy_, bs_config):
    logger.debug(bstack11l1ll1_opy_ (u"ࠢࡄࡷࡵࡶࡪࡴࡴࠡࡅࡏࡍࠥࡖࡡࡵࡪࠣࡪࡴࡻ࡮ࡥ࠼ࠣࡿࢂࠨᨏ").format(binary_path))
    bstack11llllll1l1_opy_ = bstack11l1ll1_opy_ (u"ࠨࠩᨐ")
    bstack11lllll1111_opy_ = {
        bstack11l1ll1_opy_ (u"ࠩࡶࡨࡰࡥࡶࡦࡴࡶ࡭ࡴࡴࠧᨑ"): __version__,
        bstack11l1ll1_opy_ (u"ࠥࡳࡸࠨᨒ"): platform.system(),
        bstack11l1ll1_opy_ (u"ࠦࡴࡹ࡟ࡢࡴࡦ࡬ࠧᨓ"): platform.machine(),
        bstack11l1ll1_opy_ (u"ࠧࡩ࡬ࡪࡡࡹࡩࡷࡹࡩࡰࡰࠥᨔ"): bstack11l1ll1_opy_ (u"࠭࠰ࠨᨕ"),
        bstack11l1ll1_opy_ (u"ࠢࡴࡦ࡮ࡣࡱࡧ࡮ࡨࡷࡤ࡫ࡪࠨᨖ"): bstack11l1ll1_opy_ (u"ࠨࡲࡼࡸ࡭ࡵ࡮ࠨᨗ")
    }
    try:
        if binary_path:
            bstack11lllll1111_opy_[bstack11l1ll1_opy_ (u"ࠩࡦࡰ࡮ࡥࡶࡦࡴࡶ࡭ࡴࡴᨘࠧ")] = subprocess.check_output([binary_path, bstack11l1ll1_opy_ (u"ࠥࡺࡪࡸࡳࡪࡱࡱࠦᨙ")]).strip().decode(bstack11l1ll1_opy_ (u"ࠫࡺࡺࡦ࠮࠺ࠪᨚ"))
        response = requests.request(
            bstack11l1ll1_opy_ (u"ࠬࡍࡅࡕࠩᨛ"),
            url=bstack1llll1ll11_opy_(bstack1l11l11llll_opy_),
            headers=None,
            auth=(bs_config[bstack11l1ll1_opy_ (u"࠭ࡵࡴࡧࡵࡒࡦࡳࡥࠨ᨜")], bs_config[bstack11l1ll1_opy_ (u"ࠧࡢࡥࡦࡩࡸࡹࡋࡦࡻࠪ᨝")]),
            json=None,
            params=bstack11lllll1111_opy_
        )
        data = response.json()
        if response.status_code == 200 and bstack11l1ll1_opy_ (u"ࠨࡷࡵࡰࠬ᨞") in data.keys() and bstack11l1ll1_opy_ (u"ࠩࡸࡴࡩࡧࡴࡦࡦࡢࡧࡱ࡯࡟ࡷࡧࡵࡷ࡮ࡵ࡮ࠨ᨟") in data.keys():
            logger.debug(bstack11l1ll1_opy_ (u"ࠥࡒࡪ࡫ࡤࠡࡶࡲࠤࡺࡶࡤࡢࡶࡨࠤࡧ࡯࡮ࡢࡴࡼ࠰ࠥࡩࡵࡳࡴࡨࡲࡹࠦࡢࡪࡰࡤࡶࡾࠦࡶࡦࡴࡶ࡭ࡴࡴ࠺ࠡࡽࢀࠦᨠ").format(bstack11lllll1111_opy_[bstack11l1ll1_opy_ (u"ࠫࡨࡲࡩࡠࡸࡨࡶࡸ࡯࡯࡯ࠩᨡ")]))
            bstack11lllllllll_opy_ = bstack1l11111l11l_opy_(data[bstack11l1ll1_opy_ (u"ࠬࡻࡲ࡭ࠩᨢ")], bstack1111l111ll_opy_)
            bstack11llllll1l1_opy_ = os.path.join(bstack1111l111ll_opy_, bstack11lllllllll_opy_)
            os.chmod(bstack11llllll1l1_opy_, 0o777) # bstack1l1111111l1_opy_ permission
            return bstack11llllll1l1_opy_
    except Exception as e:
        logger.debug(bstack11l1ll1_opy_ (u"ࠨࡅࡳࡴࡲࡶࠥࡽࡨࡪ࡮ࡨࠤࡩࡵࡷ࡯࡮ࡲࡥࡩ࡯࡮ࡨࠢࡱࡩࡼࠦࡓࡅࡍࠣࡿࢂࠨᨣ").format(e))
    return binary_path
@measure(event_name=EVENTS.bstack1l11l11l111_opy_, stage=STAGE.bstack1l1ll1llll_opy_)
def bstack1l11111l11l_opy_(bstack1l1111ll1l1_opy_, bstack11llllllll1_opy_):
    logger.debug(bstack11l1ll1_opy_ (u"ࠢࡅࡱࡺࡲࡱࡵࡡࡥ࡫ࡱ࡫࡙ࠥࡄࡌࠢࡥ࡭ࡳࡧࡲࡺࠢࡩࡶࡴࡳ࠺ࠡࠤᨤ") + str(bstack1l1111ll1l1_opy_) + bstack11l1ll1_opy_ (u"ࠣࠤᨥ"))
    zip_path = os.path.join(bstack11llllllll1_opy_, bstack11l1ll1_opy_ (u"ࠤࡧࡳࡼࡴ࡬ࡰࡣࡧࡩࡩࡥࡦࡪ࡮ࡨ࠲ࡿ࡯ࡰࠣᨦ"))
    bstack11lllllllll_opy_ = bstack11l1ll1_opy_ (u"ࠪࠫᨧ")
    with requests.get(bstack1l1111ll1l1_opy_, stream=True) as response:
        response.raise_for_status()
        with open(zip_path, bstack11l1ll1_opy_ (u"ࠦࡼࡨࠢᨨ")) as file:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    file.write(chunk)
        logger.debug(bstack11l1ll1_opy_ (u"ࠧࡌࡩ࡭ࡧࠣࡨࡴࡽ࡮࡭ࡱࡤࡨࡪࡪࠠࡴࡷࡦࡧࡪࡹࡳࡧࡷ࡯ࡰࡾ࠴ࠢᨩ"))
    with zipfile.ZipFile(zip_path, bstack11l1ll1_opy_ (u"࠭ࡲࠨᨪ")) as zip_ref:
        bstack11lll1l111l_opy_ = zip_ref.namelist()
        if len(bstack11lll1l111l_opy_) > 0:
            bstack11lllllllll_opy_ = bstack11lll1l111l_opy_[0] # bstack11llll11l1l_opy_ bstack1l11l111111_opy_ will be bstack11llll111ll_opy_ 1 file i.e. the binary in the zip
        zip_ref.extractall(bstack11llllllll1_opy_)
        logger.debug(bstack11l1ll1_opy_ (u"ࠢࡇ࡫࡯ࡩࡸࠦࡳࡶࡥࡦࡩࡸࡹࡦࡶ࡮࡯ࡽࠥ࡫ࡸࡵࡴࡤࡧࡹ࡫ࡤࠡࡶࡲࠤࠬࠨᨫ") + str(bstack11llllllll1_opy_) + bstack11l1ll1_opy_ (u"ࠣࠩࠥᨬ"))
    os.remove(zip_path)
    return bstack11lllllllll_opy_
def get_cli_dir():
    bstack1l1111l1ll1_opy_ = bstack11llll1l1l1_opy_()
    if bstack1l1111l1ll1_opy_:
        bstack1111l111ll_opy_ = os.path.join(bstack1l1111l1ll1_opy_, bstack11l1ll1_opy_ (u"ࠤࡦࡰ࡮ࠨᨭ"))
        if not os.path.exists(bstack1111l111ll_opy_):
            os.makedirs(bstack1111l111ll_opy_, mode=0o777, exist_ok=True)
        return bstack1111l111ll_opy_
    else:
        raise FileNotFoundError(bstack11l1ll1_opy_ (u"ࠥࡒࡴࠦࡷࡳ࡫ࡷࡥࡧࡲࡥࠡࡦ࡬ࡶࡪࡩࡴࡰࡴࡼࠤࡦࡼࡡࡪ࡮ࡤࡦࡱ࡫ࠠࡧࡱࡵࠤࡹ࡮ࡥࠡࡕࡇࡏࠥࡨࡩ࡯ࡣࡵࡽ࠳ࠨᨮ"))
def bstack1lllll1111l_opy_(bstack1111l111ll_opy_):
    bstack11l1ll1_opy_ (u"ࠦࠧࠨࡇࡦࡶࠣࡸ࡭࡫ࠠࡱࡣࡷ࡬ࠥ࡬࡯ࡳࠢࡷ࡬ࡪࠦࡂࡳࡱࡺࡷࡪࡸࡓࡵࡣࡦ࡯࡙ࠥࡄࡌࠢࡥ࡭ࡳࡧࡲࡺࠢ࡬ࡲࠥࡧࠠࡸࡴ࡬ࡸࡦࡨ࡬ࡦࠢࡧ࡭ࡷ࡫ࡣࡵࡱࡵࡽ࠳ࠨࠢࠣᨯ")
    bstack11lll1lll1l_opy_ = [
        os.path.join(bstack1111l111ll_opy_, f)
        for f in os.listdir(bstack1111l111ll_opy_)
        if os.path.isfile(os.path.join(bstack1111l111ll_opy_, f)) and f.startswith(bstack11l1ll1_opy_ (u"ࠧࡨࡩ࡯ࡣࡵࡽ࠲ࠨᨰ"))
    ]
    if len(bstack11lll1lll1l_opy_) > 0:
        return max(bstack11lll1lll1l_opy_, key=os.path.getmtime) # get bstack1l11111llll_opy_ binary
    return bstack11l1ll1_opy_ (u"ࠨࠢᨱ")