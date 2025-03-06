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
import atexit
import datetime
import inspect
import logging
import signal
import threading
from uuid import uuid4
from bstack_utils.measure import bstack1ll111ll1l_opy_
from bstack_utils.percy_sdk import PercySDK
import pytest
from packaging import version
from browserstack_sdk.__init__ import (bstack1l11llll1l_opy_, bstack1l11l11ll_opy_, update, bstack11l1ll1l1_opy_,
                                       bstack1l111lll_opy_, bstack1l1111llll_opy_, bstack1l1111111l_opy_, bstack1ll111lll_opy_,
                                       bstack11lll1llll_opy_, bstack11lll1l11_opy_, bstack1ll11lll1_opy_, bstack1ll11111ll_opy_,
                                       bstack1l11l1l111_opy_, getAccessibilityResults, getAccessibilityResultsSummary, perform_scan, bstack1llll1lll1_opy_)
from browserstack_sdk.bstack11lll111l_opy_ import bstack11l111lll_opy_
from browserstack_sdk._version import __version__
from bstack_utils import bstack1ll1ll111_opy_
from bstack_utils.capture import bstack11l1l1l11l_opy_
from bstack_utils.config import Config
from bstack_utils.percy import *
from bstack_utils.constants import bstack11l1l1lll_opy_, bstack11llll11_opy_, bstack1llll111l_opy_, \
    bstack1l11lll1_opy_
from bstack_utils.helper import bstack1ll1l1lll_opy_, bstack1l11111l1l1_opy_, bstack111ll1l111_opy_, bstack11l11lll_opy_, bstack1ll1l1l11ll_opy_, bstack1ll1l1ll_opy_, \
    bstack11lll1llll1_opy_, \
    bstack1l111l11ll1_opy_, bstack1ll111111l_opy_, bstack1l11111l1_opy_, bstack11lllll1lll_opy_, bstack1l11ll1l1_opy_, Notset, \
    bstack1l1lll1l1l_opy_, bstack11llll1lll1_opy_, bstack1l1111ll1ll_opy_, Result, bstack1l111l1l1l1_opy_, bstack11llll1l111_opy_, bstack111llll1ll_opy_, \
    bstack1l1111l11_opy_, bstack1l1ll11lll_opy_, bstack111l1l111_opy_, bstack1l111l11lll_opy_
from bstack_utils.bstack11lll1111l1_opy_ import bstack11lll11111l_opy_
from bstack_utils.messages import bstack11l11ll1l_opy_, bstack1ll1111l1_opy_, bstack1ll1ll11_opy_, bstack11ll111l11_opy_, bstack1ll1l1l111_opy_, \
    bstack11ll1l11l1_opy_, bstack11l1l111l_opy_, bstack1llll11l1l_opy_, bstack1111l1l1_opy_, bstack1l1ll111l_opy_, \
    bstack1llll1lll_opy_, bstack1ll1l1111_opy_
from bstack_utils.proxy import bstack1l1ll1lll1_opy_, bstack111l111ll_opy_
from bstack_utils.bstack1lll11ll11_opy_ import bstack11l1l11l1l1_opy_, bstack11l1l111ll1_opy_, bstack11l1l111lll_opy_, bstack11l1l11l11l_opy_, \
    bstack11l1l111111_opy_, bstack11l1l111l11_opy_, bstack11l1l111l1l_opy_, bstack11l1ll1l_opy_, bstack11l1l11l1ll_opy_
from bstack_utils.bstack11ll1l11ll_opy_ import bstack1l111111ll_opy_
from bstack_utils.bstack1l111l1l_opy_ import bstack1lll111ll_opy_, bstack1l1l111lll_opy_, bstack11ll1lllll_opy_, \
    bstack1ll1llllll_opy_, bstack11l1111l1_opy_
from bstack_utils.bstack11l11lllll_opy_ import bstack11l1l11lll_opy_
from bstack_utils.bstack11l11l1lll_opy_ import bstack11ll1ll1_opy_
import bstack_utils.accessibility as bstack11lll11ll1_opy_
from bstack_utils.bstack11l11l11l1_opy_ import bstack11111l1l1_opy_
from bstack_utils.bstack1l1ll1111l_opy_ import bstack1l1ll1111l_opy_
from browserstack_sdk.__init__ import bstack11l11l11_opy_
from browserstack_sdk.sdk_cli.bstack11111l1l1l_opy_ import bstack1llll1l1l11_opy_
from browserstack_sdk.sdk_cli.bstack1l1l11lll1_opy_ import bstack1l1l11lll1_opy_, bstack1ll1ll1l11_opy_, bstack1llll11111_opy_
from browserstack_sdk.sdk_cli.test_framework import bstack1l1l1l11lll_opy_, bstack1llll11llll_opy_, bstack1lll1llll11_opy_
from browserstack_sdk.sdk_cli.cli import cli
from browserstack_sdk.sdk_cli.bstack1l1l11lll1_opy_ import bstack1l1l11lll1_opy_, bstack1ll1ll1l11_opy_, bstack1llll11111_opy_
bstack11lll111ll_opy_ = None
bstack1llll11l_opy_ = None
bstack1lllll1l11_opy_ = None
bstack11ll111l1l_opy_ = None
bstack111lllll_opy_ = None
bstack111ll1lll_opy_ = None
bstack1llll111ll_opy_ = None
bstack1l1llll1ll_opy_ = None
bstack1lllll11ll_opy_ = None
bstack1lllll1ll1_opy_ = None
bstack11l1lllll1_opy_ = None
bstack1l1l111l1_opy_ = None
bstack1lll1lll11_opy_ = None
bstack111111ll1_opy_ = bstack11l1ll1_opy_ (u"ࠨࠩᵦ")
CONFIG = {}
bstack11ll11ll1_opy_ = False
bstack1l1ll11ll1_opy_ = bstack11l1ll1_opy_ (u"ࠩࠪᵧ")
bstack1ll1lll1ll_opy_ = bstack11l1ll1_opy_ (u"ࠪࠫᵨ")
bstack11ll1ll1l1_opy_ = False
bstack1l1ll1l1l1_opy_ = []
bstack1111llll_opy_ = bstack11l1l1lll_opy_
bstack111lllll1ll_opy_ = bstack11l1ll1_opy_ (u"ࠫࡵࡿࡴࡦࡵࡷࠫᵩ")
bstack1llll111l1_opy_ = {}
bstack1lll1l11l_opy_ = None
bstack11ll1l1lll_opy_ = False
logger = bstack1ll1ll111_opy_.get_logger(__name__, bstack1111llll_opy_)
store = {
    bstack11l1ll1_opy_ (u"ࠬࡩࡵࡳࡴࡨࡲࡹࡥࡨࡰࡱ࡮ࡣࡺࡻࡩࡥࠩᵪ"): []
}
bstack111llllll1l_opy_ = False
try:
    from playwright.sync_api import (
        BrowserContext,
        Page
    )
except:
    pass
import json
_11l111l1ll_opy_ = {}
current_test_uuid = None
cli_context = bstack1l1l1l11lll_opy_(
    test_framework_name=bstack11ll1111_opy_[bstack11l1ll1_opy_ (u"࠭ࡐ࡚ࡖࡈࡗ࡙࠳ࡂࡅࡆࠪᵫ")] if bstack1l11ll1l1_opy_() else bstack11ll1111_opy_[bstack11l1ll1_opy_ (u"ࠧࡑ࡛ࡗࡉࡘ࡚ࠧᵬ")],
    test_framework_version=pytest.__version__,
    platform_index=-1,
)
def bstack1ll1l111l_opy_(page, bstack1l1llllll_opy_):
    try:
        page.evaluate(bstack11l1ll1_opy_ (u"ࠣࡡࠣࡁࡃࠦࡻࡾࠤᵭ"),
                      bstack11l1ll1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡠࡧࡻࡩࡨࡻࡴࡰࡴ࠽ࠤࢀࠨࡡࡤࡶ࡬ࡳࡳࠨ࠺ࠡࠤࡶࡩࡹ࡙ࡥࡴࡵ࡬ࡳࡳࡔࡡ࡮ࡧࠥ࠰ࠥࠨࡡࡳࡩࡸࡱࡪࡴࡴࡴࠤ࠽ࠤࢀࠨ࡮ࡢ࡯ࡨࠦ࠿࠭ᵮ") + json.dumps(
                          bstack1l1llllll_opy_) + bstack11l1ll1_opy_ (u"ࠥࢁࢂࠨᵯ"))
    except Exception as e:
        print(bstack11l1ll1_opy_ (u"ࠦࡪࡾࡣࡦࡲࡷ࡭ࡴࡴࠠࡪࡰࠣࡴࡱࡧࡹࡸࡴ࡬࡫࡭ࡺࠠࡴࡧࡶࡷ࡮ࡵ࡮ࠡࡰࡤࡱࡪࠦࡻࡾࠤᵰ"), e)
def bstack1ll1111l1l_opy_(page, message, level):
    try:
        page.evaluate(bstack11l1ll1_opy_ (u"ࠧࡥࠠ࠾ࡀࠣࡿࢂࠨᵱ"), bstack11l1ll1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡤ࡫ࡸࡦࡥࡸࡸࡴࡸ࠺ࠡࡽࠥࡥࡨࡺࡩࡰࡰࠥ࠾ࠥࠨࡡ࡯ࡰࡲࡸࡦࡺࡥࠣ࠮ࠣࠦࡦࡸࡧࡶ࡯ࡨࡲࡹࡹࠢ࠻ࠢࡾࠦࡩࡧࡴࡢࠤ࠽ࠫᵲ") + json.dumps(
            message) + bstack11l1ll1_opy_ (u"ࠧ࠭ࠤ࡯ࡩࡻ࡫࡬ࠣ࠼ࠪᵳ") + json.dumps(level) + bstack11l1ll1_opy_ (u"ࠨࡿࢀࠫᵴ"))
    except Exception as e:
        print(bstack11l1ll1_opy_ (u"ࠤࡨࡼࡨ࡫ࡰࡵ࡫ࡲࡲࠥ࡯࡮ࠡࡲ࡯ࡥࡾࡽࡲࡪࡩ࡫ࡸࠥࡧ࡮࡯ࡱࡷࡥࡹ࡯࡯࡯ࠢࡾࢁࠧᵵ"), e)
def pytest_configure(config):
    global bstack1l1ll11ll1_opy_
    global CONFIG
    bstack1ll1l11l1_opy_ = Config.bstack1l111l1ll1_opy_()
    config.args = bstack11ll1ll1_opy_.bstack111llllllll_opy_(config.args)
    bstack1ll1l11l1_opy_.bstack1l1l11l111_opy_(bstack111l1l111_opy_(config.getoption(bstack11l1ll1_opy_ (u"ࠪࡷࡰ࡯ࡰࡔࡧࡶࡷ࡮ࡵ࡮ࡔࡶࡤࡸࡺࡹࠧᵶ"))))
    try:
        bstack1ll1ll111_opy_.bstack11ll1lll1ll_opy_(config.inipath, config.rootpath)
    except:
        pass
    if cli.is_running():
        bstack1l1l11lll1_opy_.invoke(bstack1ll1ll1l11_opy_.CONNECT, bstack1llll11111_opy_())
        cli_context.platform_index = int(os.environ.get(bstack11l1ll1_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡔࡑࡇࡔࡇࡑࡕࡑࡤࡏࡎࡅࡇ࡛ࠫᵷ"), bstack11l1ll1_opy_ (u"ࠬ࠶ࠧᵸ")))
        config = json.loads(os.environ.get(bstack11l1ll1_opy_ (u"ࠨࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡉࡏࡏࡈࡌࡋࠧᵹ"), bstack11l1ll1_opy_ (u"ࠢࡼࡿࠥᵺ")))
        cli.bstack1llllll1111_opy_(bstack1l11111l1_opy_(bstack1l1ll11ll1_opy_, CONFIG), cli_context.platform_index, bstack11l1ll1l1_opy_)
    if cli.bstack11111lll11_opy_(bstack1llll1l1l11_opy_):
        cli.bstack1lllll111ll_opy_()
        logger.debug(bstack11l1ll1_opy_ (u"ࠣࡅࡏࡍࠥ࡯ࡳࠡࡣࡦࡸ࡮ࡼࡥࠡࡨࡲࡶࠥࡶ࡬ࡢࡶࡩࡳࡷࡳ࡟ࡪࡰࡧࡩࡽࡃࠢᵻ") + str(cli_context.platform_index) + bstack11l1ll1_opy_ (u"ࠤࠥᵼ"))
        cli.test_framework.track_event(cli_context, bstack1llll11llll_opy_.BEFORE_ALL, bstack1lll1llll11_opy_.PRE, config)
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    when = getattr(call, bstack11l1ll1_opy_ (u"ࠥࡻ࡭࡫࡮ࠣᵽ"), None)
    if cli.bstack11111lll11_opy_(bstack1llll1l1l11_opy_) and when == bstack11l1ll1_opy_ (u"ࠦࡨࡧ࡬࡭ࠤᵾ"):
        cli.test_framework.track_event(cli_context, bstack1llll11llll_opy_.LOG_REPORT, bstack1lll1llll11_opy_.PRE, item, call)
    outcome = yield
    if cli.bstack11111lll11_opy_(bstack1llll1l1l11_opy_):
        if when == bstack11l1ll1_opy_ (u"ࠧࡹࡥࡵࡷࡳࠦᵿ"):
            cli.test_framework.track_event(cli_context, bstack1llll11llll_opy_.BEFORE_EACH, bstack1lll1llll11_opy_.POST, item, call, outcome)
        elif when == bstack11l1ll1_opy_ (u"ࠨࡣࡢ࡮࡯ࠦᶀ"):
            cli.test_framework.track_event(cli_context, bstack1llll11llll_opy_.LOG_REPORT, bstack1lll1llll11_opy_.POST, item, call, outcome)
        elif when == bstack11l1ll1_opy_ (u"ࠢࡵࡧࡤࡶࡩࡵࡷ࡯ࠤᶁ"):
            cli.test_framework.track_event(cli_context, bstack1llll11llll_opy_.AFTER_EACH, bstack1lll1llll11_opy_.POST, item, call, outcome)
        return # skip all existing bstack111lll1l1ll_opy_
    bstack111lll1l111_opy_ = item.config.getoption(bstack11l1ll1_opy_ (u"ࠨࡵ࡮࡭ࡵ࡙ࡥࡴࡵ࡬ࡳࡳࡔࡡ࡮ࡧࠪᶂ"))
    plugins = item.config.getoption(bstack11l1ll1_opy_ (u"ࠤࡳࡰࡺ࡭ࡩ࡯ࡵࠥᶃ"))
    report = outcome.get_result()
    bstack111lllll1l1_opy_(item, call, report)
    if bstack11l1ll1_opy_ (u"ࠥࡴࡾࡺࡥࡴࡶࡢࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡲ࡯ࡹ࡬࡯࡮ࠣᶄ") not in plugins or bstack1l11ll1l1_opy_():
        return
    summary = []
    driver = getattr(item, bstack11l1ll1_opy_ (u"ࠦࡤࡪࡲࡪࡸࡨࡶࠧᶅ"), None)
    page = getattr(item, bstack11l1ll1_opy_ (u"ࠧࡥࡰࡢࡩࡨࠦᶆ"), None)
    try:
        if (driver == None or driver.session_id == None):
            driver = threading.current_thread().bstackSessionDriver
    except:
        pass
    item._driver = driver
    if (driver is not None or cli.is_running()):
        bstack111ll1lllll_opy_(item, report, summary, bstack111lll1l111_opy_)
    if (page is not None):
        bstack111lll11ll1_opy_(item, report, summary, bstack111lll1l111_opy_)
def bstack111ll1lllll_opy_(item, report, summary, bstack111lll1l111_opy_):
    if report.when == bstack11l1ll1_opy_ (u"࠭ࡳࡦࡶࡸࡴࠬᶇ") and report.skipped:
        bstack11l1l11l1ll_opy_(report)
    if report.when in [bstack11l1ll1_opy_ (u"ࠢࡴࡧࡷࡹࡵࠨᶈ"), bstack11l1ll1_opy_ (u"ࠣࡶࡨࡥࡷࡪ࡯ࡸࡰࠥᶉ")]:
        return
    if not bstack1ll1l1l11ll_opy_():
        return
    try:
        if (str(bstack111lll1l111_opy_).lower() != bstack11l1ll1_opy_ (u"ࠩࡷࡶࡺ࡫ࠧᶊ") and not cli.is_running()):
            item._driver.execute_script(
                bstack11l1ll1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡡࡨࡼࡪࡩࡵࡵࡱࡵ࠾ࠥࢁࠢࡢࡥࡷ࡭ࡴࡴࠢ࠻ࠢࠥࡷࡪࡺࡓࡦࡵࡶ࡭ࡴࡴࡎࡢ࡯ࡨࠦ࠱ࠦࠢࡢࡴࡪࡹࡲ࡫࡮ࡵࡵࠥ࠾ࠥࢁࠢ࡯ࡣࡰࡩࠧࡀࠠࠨᶋ") + json.dumps(
                    report.nodeid) + bstack11l1ll1_opy_ (u"ࠫࢂࢃࠧᶌ"))
        os.environ[bstack11l1ll1_opy_ (u"ࠬࡖ࡙ࡕࡇࡖࡘࡤ࡚ࡅࡔࡖࡢࡒࡆࡓࡅࠨᶍ")] = report.nodeid
    except Exception as e:
        summary.append(
            bstack11l1ll1_opy_ (u"ࠨࡗࡂࡔࡑࡍࡓࡍ࠺ࠡࡈࡤ࡭ࡱ࡫ࡤࠡࡶࡲࠤࡲࡧࡲ࡬ࠢࡶࡩࡸࡹࡩࡰࡰࠣࡲࡦࡳࡥ࠻ࠢࡾ࠴ࢂࠨᶎ").format(e)
        )
    passed = report.passed or report.skipped or (report.failed and hasattr(report, bstack11l1ll1_opy_ (u"ࠢࡸࡣࡶࡼ࡫ࡧࡩ࡭ࠤᶏ")))
    bstack1lll1l1ll1_opy_ = bstack11l1ll1_opy_ (u"ࠣࠤᶐ")
    bstack11l1l11l1ll_opy_(report)
    if not passed:
        try:
            bstack1lll1l1ll1_opy_ = report.longrepr.reprcrash
        except Exception as e:
            summary.append(
                bstack11l1ll1_opy_ (u"ࠤ࡚ࡅࡗࡔࡉࡏࡉ࠽ࠤࡋࡧࡩ࡭ࡧࡧࠤࡹࡵࠠࡥࡧࡷࡩࡷࡳࡩ࡯ࡧࠣࡪࡦ࡯࡬ࡶࡴࡨࠤࡷ࡫ࡡࡴࡱࡱ࠾ࠥࢁ࠰ࡾࠤᶑ").format(e)
            )
        try:
            if (threading.current_thread().bstackTestErrorMessages == None):
                threading.current_thread().bstackTestErrorMessages = []
        except Exception as e:
            threading.current_thread().bstackTestErrorMessages = []
        threading.current_thread().bstackTestErrorMessages.append(str(bstack1lll1l1ll1_opy_))
    if not report.skipped:
        passed = report.passed or (report.failed and hasattr(report, bstack11l1ll1_opy_ (u"ࠥࡻࡦࡹࡸࡧࡣ࡬ࡰࠧᶒ")))
        bstack1lll1l1ll1_opy_ = bstack11l1ll1_opy_ (u"ࠦࠧᶓ")
        if not passed:
            try:
                bstack1lll1l1ll1_opy_ = report.longrepr.reprcrash
            except Exception as e:
                summary.append(
                    bstack11l1ll1_opy_ (u"ࠧ࡝ࡁࡓࡐࡌࡒࡌࡀࠠࡇࡣ࡬ࡰࡪࡪࠠࡵࡱࠣࡨࡪࡺࡥࡳ࡯࡬ࡲࡪࠦࡦࡢ࡫࡯ࡹࡷ࡫ࠠࡳࡧࡤࡷࡴࡴ࠺ࠡࡽ࠳ࢁࠧᶔ").format(e)
                )
            try:
                if (threading.current_thread().bstackTestErrorMessages == None):
                    threading.current_thread().bstackTestErrorMessages = []
            except Exception as e:
                threading.current_thread().bstackTestErrorMessages = []
            threading.current_thread().bstackTestErrorMessages.append(str(bstack1lll1l1ll1_opy_))
        try:
            if passed:
                item._driver.execute_script(
                    bstack11l1ll1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡤ࡫ࡸࡦࡥࡸࡸࡴࡸ࠺ࠡࡽ࡟ࠎࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠧࡧࡣࡵ࡫ࡲࡲࠧࡀࠠࠣࡣࡱࡲࡴࡺࡡࡵࡧࠥ࠰ࠥࡢࠊࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠣࡣࡵ࡫ࡺࡳࡥ࡯ࡶࡶࠦ࠿ࠦࡻ࡝ࠌࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠢ࡭ࡧࡹࡩࡱࠨ࠺ࠡࠤ࡬ࡲ࡫ࡵࠢ࠭ࠢ࡟ࠎࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠤࡧࡥࡹࡧࠢ࠻ࠢࠪᶕ")
                    + json.dumps(bstack11l1ll1_opy_ (u"ࠢࡱࡣࡶࡷࡪࡪࠡࠣᶖ"))
                    + bstack11l1ll1_opy_ (u"ࠣ࡞ࠍࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࢁࡡࠐࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࢀࠦᶗ")
                )
            else:
                item._driver.execute_script(
                    bstack11l1ll1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡠࡧࡻࡩࡨࡻࡴࡰࡴ࠽ࠤࢀࡢࠊࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠣࡣࡦࡸ࡮ࡵ࡮ࠣ࠼ࠣࠦࡦࡴ࡮ࡰࡶࡤࡸࡪࠨࠬࠡ࡞ࠍࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠦࡦࡸࡧࡶ࡯ࡨࡲࡹࡹࠢ࠻ࠢࡾࡠࠏࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠥࡰࡪࡼࡥ࡭ࠤ࠽ࠤࠧ࡫ࡲࡳࡱࡵࠦ࠱ࠦ࡜ࠋࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠨࡤࡢࡶࡤࠦ࠿ࠦࠧᶘ")
                    + json.dumps(str(bstack1lll1l1ll1_opy_))
                    + bstack11l1ll1_opy_ (u"ࠥࡠࠏࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࢃ࡜ࠋࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࢂࠨᶙ")
                )
        except Exception as e:
            summary.append(bstack11l1ll1_opy_ (u"ࠦ࡜ࡇࡒࡏࡋࡑࡋ࠿ࠦࡆࡢ࡫࡯ࡩࡩࠦࡴࡰࠢࡤࡲࡳࡵࡴࡢࡶࡨ࠾ࠥࢁ࠰ࡾࠤᶚ").format(e))
def bstack111llll1111_opy_(test_name, error_message):
    try:
        bstack111lll1l11l_opy_ = []
        bstack1ll1lll1l_opy_ = os.environ.get(bstack11l1ll1_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡕࡒࡁࡕࡈࡒࡖࡒࡥࡉࡏࡆࡈ࡜ࠬᶛ"), bstack11l1ll1_opy_ (u"࠭࠰ࠨᶜ"))
        bstack1l11l1ll11_opy_ = {bstack11l1ll1_opy_ (u"ࠧ࡯ࡣࡰࡩࠬᶝ"): test_name, bstack11l1ll1_opy_ (u"ࠨࡧࡵࡶࡴࡸࠧᶞ"): error_message, bstack11l1ll1_opy_ (u"ࠩ࡬ࡲࡩ࡫ࡸࠨᶟ"): bstack1ll1lll1l_opy_}
        bstack111lll1llll_opy_ = os.path.join(tempfile.gettempdir(), bstack11l1ll1_opy_ (u"ࠪࡴࡼࡥࡰࡺࡶࡨࡷࡹࡥࡥࡳࡴࡲࡶࡤࡲࡩࡴࡶ࠱࡮ࡸࡵ࡮ࠨᶠ"))
        if os.path.exists(bstack111lll1llll_opy_):
            with open(bstack111lll1llll_opy_) as f:
                bstack111lll1l11l_opy_ = json.load(f)
        bstack111lll1l11l_opy_.append(bstack1l11l1ll11_opy_)
        with open(bstack111lll1llll_opy_, bstack11l1ll1_opy_ (u"ࠫࡼ࠭ᶡ")) as f:
            json.dump(bstack111lll1l11l_opy_, f)
    except Exception as e:
        logger.debug(bstack11l1ll1_opy_ (u"ࠬࡋࡲࡳࡱࡵࠤ࡮ࡴࠠࡱࡧࡵࡷ࡮ࡹࡴࡪࡰࡪࠤࡵࡲࡡࡺࡹࡵ࡭࡬࡮ࡴࠡࡲࡼࡸࡪࡹࡴࠡࡧࡵࡶࡴࡸࡳ࠻ࠢࠪᶢ") + str(e))
def bstack111lll11ll1_opy_(item, report, summary, bstack111lll1l111_opy_):
    if report.when in [bstack11l1ll1_opy_ (u"ࠨࡳࡦࡶࡸࡴࠧᶣ"), bstack11l1ll1_opy_ (u"ࠢࡵࡧࡤࡶࡩࡵࡷ࡯ࠤᶤ")]:
        return
    if (str(bstack111lll1l111_opy_).lower() != bstack11l1ll1_opy_ (u"ࠨࡶࡵࡹࡪ࠭ᶥ")):
        bstack1ll1l111l_opy_(item._page, report.nodeid)
    passed = report.passed or report.skipped or (report.failed and hasattr(report, bstack11l1ll1_opy_ (u"ࠤࡺࡥࡸࡾࡦࡢ࡫࡯ࠦᶦ")))
    bstack1lll1l1ll1_opy_ = bstack11l1ll1_opy_ (u"ࠥࠦᶧ")
    bstack11l1l11l1ll_opy_(report)
    if not report.skipped:
        if not passed:
            try:
                bstack1lll1l1ll1_opy_ = report.longrepr.reprcrash
            except Exception as e:
                summary.append(
                    bstack11l1ll1_opy_ (u"ࠦ࡜ࡇࡒࡏࡋࡑࡋ࠿ࠦࡆࡢ࡫࡯ࡩࡩࠦࡴࡰࠢࡧࡩࡹ࡫ࡲ࡮࡫ࡱࡩࠥ࡬ࡡࡪ࡮ࡸࡶࡪࠦࡲࡦࡣࡶࡳࡳࡀࠠࡼ࠲ࢀࠦᶨ").format(e)
                )
        try:
            if passed:
                bstack11l1111l1_opy_(getattr(item, bstack11l1ll1_opy_ (u"ࠬࡥࡰࡢࡩࡨࠫᶩ"), None), bstack11l1ll1_opy_ (u"ࠨࡰࡢࡵࡶࡩࡩࠨᶪ"))
            else:
                error_message = bstack11l1ll1_opy_ (u"ࠧࠨᶫ")
                if bstack1lll1l1ll1_opy_:
                    bstack1ll1111l1l_opy_(item._page, str(bstack1lll1l1ll1_opy_), bstack11l1ll1_opy_ (u"ࠣࡧࡵࡶࡴࡸࠢᶬ"))
                    bstack11l1111l1_opy_(getattr(item, bstack11l1ll1_opy_ (u"ࠩࡢࡴࡦ࡭ࡥࠨᶭ"), None), bstack11l1ll1_opy_ (u"ࠥࡪࡦ࡯࡬ࡦࡦࠥᶮ"), str(bstack1lll1l1ll1_opy_))
                    error_message = str(bstack1lll1l1ll1_opy_)
                else:
                    bstack11l1111l1_opy_(getattr(item, bstack11l1ll1_opy_ (u"ࠫࡤࡶࡡࡨࡧࠪᶯ"), None), bstack11l1ll1_opy_ (u"ࠧ࡬ࡡࡪ࡮ࡨࡨࠧᶰ"))
                bstack111llll1111_opy_(report.nodeid, error_message)
        except Exception as e:
            summary.append(bstack11l1ll1_opy_ (u"ࠨࡗࡂࡔࡑࡍࡓࡍ࠺ࠡࡈࡤ࡭ࡱ࡫ࡤࠡࡶࡲࠤࡺࡶࡤࡢࡶࡨࠤࡸ࡫ࡳࡴ࡫ࡲࡲࠥࡹࡴࡢࡶࡸࡷ࠿ࠦࡻ࠱ࡿࠥᶱ").format(e))
try:
    from typing import Generator
    import pytest_playwright.pytest_playwright as p
    @pytest.fixture
    def page(context: BrowserContext, request: pytest.FixtureRequest) -> Generator[Page, None, None]:
        page = context.new_page()
        request.node._page = page
        yield page
except:
    pass
def pytest_addoption(parser):
    parser.addoption(bstack11l1ll1_opy_ (u"ࠢ࠮࠯ࡶ࡯࡮ࡶࡓࡦࡵࡶ࡭ࡴࡴࡎࡢ࡯ࡨࠦᶲ"), default=bstack11l1ll1_opy_ (u"ࠣࡈࡤࡰࡸ࡫ࠢᶳ"), help=bstack11l1ll1_opy_ (u"ࠤࡄࡹࡹࡵ࡭ࡢࡶ࡬ࡧࠥࡹࡥࡵࠢࡶࡩࡸࡹࡩࡰࡰࠣࡲࡦࡳࡥࠣᶴ"))
    parser.addoption(bstack11l1ll1_opy_ (u"ࠥ࠱࠲ࡹ࡫ࡪࡲࡖࡩࡸࡹࡩࡰࡰࡖࡸࡦࡺࡵࡴࠤᶵ"), default=bstack11l1ll1_opy_ (u"ࠦࡋࡧ࡬ࡴࡧࠥᶶ"), help=bstack11l1ll1_opy_ (u"ࠧࡇࡵࡵࡱࡰࡥࡹ࡯ࡣࠡࡵࡨࡸࠥࡹࡥࡴࡵ࡬ࡳࡳࠦ࡮ࡢ࡯ࡨࠦᶷ"))
    try:
        import pytest_selenium.pytest_selenium
    except:
        parser.addoption(bstack11l1ll1_opy_ (u"ࠨ࠭࠮ࡦࡵ࡭ࡻ࡫ࡲࠣᶸ"), action=bstack11l1ll1_opy_ (u"ࠢࡴࡶࡲࡶࡪࠨᶹ"), default=bstack11l1ll1_opy_ (u"ࠣࡥ࡫ࡶࡴࡳࡥࠣᶺ"),
                         help=bstack11l1ll1_opy_ (u"ࠤࡇࡶ࡮ࡼࡥࡳࠢࡷࡳࠥࡸࡵ࡯ࠢࡷࡩࡸࡺࡳࠣᶻ"))
def bstack11l1l11ll1_opy_(log):
    if not (log[bstack11l1ll1_opy_ (u"ࠪࡱࡪࡹࡳࡢࡩࡨࠫᶼ")] and log[bstack11l1ll1_opy_ (u"ࠫࡲ࡫ࡳࡴࡣࡪࡩࠬᶽ")].strip()):
        return
    active = bstack11l1l11l1l_opy_()
    log = {
        bstack11l1ll1_opy_ (u"ࠬࡲࡥࡷࡧ࡯ࠫᶾ"): log[bstack11l1ll1_opy_ (u"࠭࡬ࡦࡸࡨࡰࠬᶿ")],
        bstack11l1ll1_opy_ (u"ࠧࡵ࡫ࡰࡩࡸࡺࡡ࡮ࡲࠪ᷀"): bstack111ll1l111_opy_().isoformat() + bstack11l1ll1_opy_ (u"ࠨ࡜ࠪ᷁"),
        bstack11l1ll1_opy_ (u"ࠩࡰࡩࡸࡹࡡࡨࡧ᷂ࠪ"): log[bstack11l1ll1_opy_ (u"ࠪࡱࡪࡹࡳࡢࡩࡨࠫ᷃")],
    }
    if active:
        if active[bstack11l1ll1_opy_ (u"ࠫࡹࡿࡰࡦࠩ᷄")] == bstack11l1ll1_opy_ (u"ࠬ࡮࡯ࡰ࡭ࠪ᷅"):
            log[bstack11l1ll1_opy_ (u"࠭ࡨࡰࡱ࡮ࡣࡷࡻ࡮ࡠࡷࡸ࡭ࡩ࠭᷆")] = active[bstack11l1ll1_opy_ (u"ࠧࡩࡱࡲ࡯ࡤࡸࡵ࡯ࡡࡸࡹ࡮ࡪࠧ᷇")]
        elif active[bstack11l1ll1_opy_ (u"ࠨࡶࡼࡴࡪ࠭᷈")] == bstack11l1ll1_opy_ (u"ࠩࡷࡩࡸࡺࠧ᷉"):
            log[bstack11l1ll1_opy_ (u"ࠪࡸࡪࡹࡴࡠࡴࡸࡲࡤࡻࡵࡪࡦ᷊ࠪ")] = active[bstack11l1ll1_opy_ (u"ࠫࡹ࡫ࡳࡵࡡࡵࡹࡳࡥࡵࡶ࡫ࡧࠫ᷋")]
    bstack11111l1l1_opy_.bstack1l1l1lll1l_opy_([log])
def bstack11l1l11l1l_opy_():
    if len(store[bstack11l1ll1_opy_ (u"ࠬࡩࡵࡳࡴࡨࡲࡹࡥࡨࡰࡱ࡮ࡣࡺࡻࡩࡥࠩ᷌")]) > 0 and store[bstack11l1ll1_opy_ (u"࠭ࡣࡶࡴࡵࡩࡳࡺ࡟ࡩࡱࡲ࡯ࡤࡻࡵࡪࡦࠪ᷍")][-1]:
        return {
            bstack11l1ll1_opy_ (u"ࠧࡵࡻࡳࡩ᷎ࠬ"): bstack11l1ll1_opy_ (u"ࠨࡪࡲࡳࡰ᷏࠭"),
            bstack11l1ll1_opy_ (u"ࠩ࡫ࡳࡴࡱ࡟ࡳࡷࡱࡣࡺࡻࡩࡥ᷐ࠩ"): store[bstack11l1ll1_opy_ (u"ࠪࡧࡺࡸࡲࡦࡰࡷࡣ࡭ࡵ࡯࡬ࡡࡸࡹ࡮ࡪࠧ᷑")][-1]
        }
    if store.get(bstack11l1ll1_opy_ (u"ࠫࡨࡻࡲࡳࡧࡱࡸࡤࡺࡥࡴࡶࡢࡹࡺ࡯ࡤࠨ᷒"), None):
        return {
            bstack11l1ll1_opy_ (u"ࠬࡺࡹࡱࡧࠪᷓ"): bstack11l1ll1_opy_ (u"࠭ࡴࡦࡵࡷࠫᷔ"),
            bstack11l1ll1_opy_ (u"ࠧࡵࡧࡶࡸࡤࡸࡵ࡯ࡡࡸࡹ࡮ࡪࠧᷕ"): store[bstack11l1ll1_opy_ (u"ࠨࡥࡸࡶࡷ࡫࡮ࡵࡡࡷࡩࡸࡺ࡟ࡶࡷ࡬ࡨࠬᷖ")]
        }
    return None
def pytest_runtest_logstart(nodeid, location):
    if cli.bstack11111lll11_opy_(bstack1llll1l1l11_opy_):
        cli.test_framework.track_event(cli_context, bstack1llll11llll_opy_.INIT_TEST, bstack1lll1llll11_opy_.PRE, nodeid, location)
def pytest_runtest_logfinish(nodeid, location):
    if cli.bstack11111lll11_opy_(bstack1llll1l1l11_opy_):
        cli.test_framework.track_event(cli_context, bstack1llll11llll_opy_.INIT_TEST, bstack1lll1llll11_opy_.POST, nodeid, location)
def pytest_runtest_call(item):
    if cli.bstack11111lll11_opy_(bstack1llll1l1l11_opy_):
        cli.test_framework.track_event(cli_context, bstack1llll11llll_opy_.TEST, bstack1lll1llll11_opy_.PRE, item)
        return
    try:
        global CONFIG
        item._111lllll11l_opy_ = True
        bstack1l11l1l1l_opy_ = bstack11lll11ll1_opy_.bstack1lllll11l_opy_(bstack1l111l11ll1_opy_(item.own_markers))
        if not cli.bstack11111lll11_opy_(bstack1llll1l1l11_opy_):
            item._a11y_test_case = bstack1l11l1l1l_opy_
            if bstack1ll1l1lll_opy_(threading.current_thread(), bstack11l1ll1_opy_ (u"ࠩࡤ࠵࠶ࡿࡐ࡭ࡣࡷࡪࡴࡸ࡭ࠨᷗ"), None):
                driver = getattr(item, bstack11l1ll1_opy_ (u"ࠪࡣࡩࡸࡩࡷࡧࡵࠫᷘ"), None)
                item._a11y_started = bstack11lll11ll1_opy_.bstack1l1ll1l111_opy_(driver, bstack1l11l1l1l_opy_)
        if not bstack11111l1l1_opy_.on() or bstack111lllll1ll_opy_ != bstack11l1ll1_opy_ (u"ࠫࡵࡿࡴࡦࡵࡷࠫᷙ"):
            return
        global current_test_uuid #, bstack11l11l1l11_opy_
        bstack111lll11ll_opy_ = {
            bstack11l1ll1_opy_ (u"ࠬࡻࡵࡪࡦࠪᷚ"): uuid4().__str__(),
            bstack11l1ll1_opy_ (u"࠭ࡳࡵࡣࡵࡸࡪࡪ࡟ࡢࡶࠪᷛ"): bstack111ll1l111_opy_().isoformat() + bstack11l1ll1_opy_ (u"࡛ࠧࠩᷜ")
        }
        current_test_uuid = bstack111lll11ll_opy_[bstack11l1ll1_opy_ (u"ࠨࡷࡸ࡭ࡩ࠭ᷝ")]
        store[bstack11l1ll1_opy_ (u"ࠩࡦࡹࡷࡸࡥ࡯ࡶࡢࡸࡪࡹࡴࡠࡷࡸ࡭ࡩ࠭ᷞ")] = bstack111lll11ll_opy_[bstack11l1ll1_opy_ (u"ࠪࡹࡺ࡯ࡤࠨᷟ")]
        threading.current_thread().current_test_uuid = current_test_uuid
        _11l111l1ll_opy_[item.nodeid] = {**_11l111l1ll_opy_[item.nodeid], **bstack111lll11ll_opy_}
        bstack111llll1ll1_opy_(item, _11l111l1ll_opy_[item.nodeid], bstack11l1ll1_opy_ (u"࡙ࠫ࡫ࡳࡵࡔࡸࡲࡘࡺࡡࡳࡶࡨࡨࠬᷠ"))
    except Exception as err:
        print(bstack11l1ll1_opy_ (u"ࠬࡋࡸࡤࡧࡳࡸ࡮ࡵ࡮ࠡ࡫ࡱࠤࡵࡿࡴࡦࡵࡷࡣࡷࡻ࡮ࡵࡧࡶࡸࡤࡩࡡ࡭࡮࠽ࠤࢀࢃࠧᷡ"), str(err))
def pytest_runtest_setup(item):
    store[bstack11l1ll1_opy_ (u"࠭ࡣࡶࡴࡵࡩࡳࡺ࡟ࡵࡧࡶࡸࡤ࡯ࡴࡦ࡯ࠪᷢ")] = item
    if cli.bstack11111lll11_opy_(bstack1llll1l1l11_opy_):
        cli.test_framework.track_event(cli_context, bstack1llll11llll_opy_.BEFORE_EACH, bstack1lll1llll11_opy_.PRE, item, bstack11l1ll1_opy_ (u"ࠧࡴࡧࡷࡹࡵ࠭ᷣ"))
        return # skip all existing bstack111lll1l1ll_opy_
    global bstack111llllll1l_opy_
    threading.current_thread().percySessionName = item.nodeid
    if bstack11lllll1lll_opy_():
        atexit.register(bstack1ll111ll11_opy_)
        if not bstack111llllll1l_opy_:
            try:
                bstack111lll1ll1l_opy_ = [signal.SIGINT, signal.SIGTERM]
                if not bstack1l111l11lll_opy_():
                    bstack111lll1ll1l_opy_.extend([signal.SIGHUP, signal.SIGQUIT])
                for s in bstack111lll1ll1l_opy_:
                    signal.signal(s, bstack111llll111l_opy_)
                bstack111llllll1l_opy_ = True
            except Exception as e:
                logger.debug(
                    bstack11l1ll1_opy_ (u"ࠣࡇࡵࡶࡴࡸࠠࡪࡰࠣࡶࡪ࡭ࡩࡴࡶࡨࡶࠥࡹࡩࡨࡰࡤࡰࠥ࡮ࡡ࡯ࡦ࡯ࡩࡷࡹ࠺ࠡࠤᷤ") + str(e))
        try:
            item.config.hook.pytest_selenium_runtest_makereport = bstack11l1l11l1l1_opy_
        except Exception as err:
            threading.current_thread().testStatus = bstack11l1ll1_opy_ (u"ࠩࡳࡥࡸࡹࡥࡥࠩᷥ")
    try:
        if not bstack11111l1l1_opy_.on():
            return
        uuid = uuid4().__str__()
        bstack111lll11ll_opy_ = {
            bstack11l1ll1_opy_ (u"ࠪࡹࡺ࡯ࡤࠨᷦ"): uuid,
            bstack11l1ll1_opy_ (u"ࠫࡸࡺࡡࡳࡶࡨࡨࡤࡧࡴࠨᷧ"): bstack111ll1l111_opy_().isoformat() + bstack11l1ll1_opy_ (u"ࠬࡠࠧᷨ"),
            bstack11l1ll1_opy_ (u"࠭ࡴࡺࡲࡨࠫᷩ"): bstack11l1ll1_opy_ (u"ࠧࡩࡱࡲ࡯ࠬᷪ"),
            bstack11l1ll1_opy_ (u"ࠨࡪࡲࡳࡰࡥࡴࡺࡲࡨࠫᷫ"): bstack11l1ll1_opy_ (u"ࠩࡅࡉࡋࡕࡒࡆࡡࡈࡅࡈࡎࠧᷬ"),
            bstack11l1ll1_opy_ (u"ࠪ࡬ࡴࡵ࡫ࡠࡰࡤࡱࡪ࠭ᷭ"): bstack11l1ll1_opy_ (u"ࠫࡸ࡫ࡴࡶࡲࠪᷮ")
        }
        threading.current_thread().current_hook_uuid = uuid
        threading.current_thread().current_test_item = item
        store[bstack11l1ll1_opy_ (u"ࠬࡩࡵࡳࡴࡨࡲࡹࡥࡴࡦࡵࡷࡣ࡮ࡺࡥ࡮ࠩᷯ")] = item
        store[bstack11l1ll1_opy_ (u"࠭ࡣࡶࡴࡵࡩࡳࡺ࡟ࡩࡱࡲ࡯ࡤࡻࡵࡪࡦࠪᷰ")] = [uuid]
        if not _11l111l1ll_opy_.get(item.nodeid, None):
            _11l111l1ll_opy_[item.nodeid] = {bstack11l1ll1_opy_ (u"ࠧࡩࡱࡲ࡯ࡸ࠭ᷱ"): [], bstack11l1ll1_opy_ (u"ࠨࡨ࡬ࡼࡹࡻࡲࡦࡵࠪᷲ"): []}
        _11l111l1ll_opy_[item.nodeid][bstack11l1ll1_opy_ (u"ࠩ࡫ࡳࡴࡱࡳࠨᷳ")].append(bstack111lll11ll_opy_[bstack11l1ll1_opy_ (u"ࠪࡹࡺ࡯ࡤࠨᷴ")])
        _11l111l1ll_opy_[item.nodeid + bstack11l1ll1_opy_ (u"ࠫ࠲ࡹࡥࡵࡷࡳࠫ᷵")] = bstack111lll11ll_opy_
        bstack111lll11lll_opy_(item, bstack111lll11ll_opy_, bstack11l1ll1_opy_ (u"ࠬࡎ࡯ࡰ࡭ࡕࡹࡳ࡙ࡴࡢࡴࡷࡩࡩ࠭᷶"))
    except Exception as err:
        print(bstack11l1ll1_opy_ (u"࠭ࡅࡹࡥࡨࡴࡹ࡯࡯࡯ࠢ࡬ࡲࠥࡶࡹࡵࡧࡶࡸࡤࡸࡵ࡯ࡶࡨࡷࡹࡥࡳࡦࡶࡸࡴ࠿ࠦࡻࡾ᷷ࠩ"), str(err))
def pytest_runtest_teardown(item):
    if cli.bstack11111lll11_opy_(bstack1llll1l1l11_opy_):
        cli.test_framework.track_event(cli_context, bstack1llll11llll_opy_.TEST, bstack1lll1llll11_opy_.POST, item)
        cli.test_framework.track_event(cli_context, bstack1llll11llll_opy_.AFTER_EACH, bstack1lll1llll11_opy_.PRE, item, bstack11l1ll1_opy_ (u"ࠧࡵࡧࡤࡶࡩࡵࡷ࡯᷸ࠩ"))
        return # skip all existing bstack111lll1l1ll_opy_
    try:
        global bstack1llll111l1_opy_
        bstack1ll1lll1l_opy_ = 0
        if bstack11ll1ll1l1_opy_ is True:
            bstack1ll1lll1l_opy_ = int(os.environ.get(bstack11l1ll1_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡑࡎࡄࡘࡋࡕࡒࡎࡡࡌࡒࡉࡋࡘࠨ᷹")))
        if bstack111l1l11l_opy_.bstack1l1111111_opy_() == bstack11l1ll1_opy_ (u"ࠤࡷࡶࡺ࡫᷺ࠢ"):
            if bstack111l1l11l_opy_.bstack111llll1l_opy_() == bstack11l1ll1_opy_ (u"ࠥࡸࡪࡹࡴࡤࡣࡶࡩࠧ᷻"):
                bstack111lll111ll_opy_ = bstack1ll1l1lll_opy_(threading.current_thread(), bstack11l1ll1_opy_ (u"ࠫࡵ࡫ࡲࡤࡻࡖࡩࡸࡹࡩࡰࡰࡑࡥࡲ࡫ࠧ᷼"), None)
                bstack1llll1llll_opy_ = bstack111lll111ll_opy_ + bstack11l1ll1_opy_ (u"ࠧ࠳ࡴࡦࡵࡷࡧࡦࡹࡥ᷽ࠣ")
                driver = getattr(item, bstack11l1ll1_opy_ (u"࠭࡟ࡥࡴ࡬ࡺࡪࡸࠧ᷾"), None)
                bstack1llll1l11l_opy_ = getattr(item, bstack11l1ll1_opy_ (u"ࠧ࡯ࡣࡰࡩ᷿ࠬ"), None)
                bstack111l1ll11_opy_ = getattr(item, bstack11l1ll1_opy_ (u"ࠨࡷࡸ࡭ࡩ࠭Ḁ"), None)
                PercySDK.screenshot(driver, bstack1llll1llll_opy_, bstack1llll1l11l_opy_=bstack1llll1l11l_opy_, bstack111l1ll11_opy_=bstack111l1ll11_opy_, bstack1l1lll1ll1_opy_=bstack1ll1lll1l_opy_)
        if not cli.bstack11111lll11_opy_(bstack1llll1l1l11_opy_):
            if getattr(item, bstack11l1ll1_opy_ (u"ࠩࡢࡥ࠶࠷ࡹࡠࡵࡷࡥࡷࡺࡥࡥࠩḁ"), False):
                bstack11l111lll_opy_.bstack1l1l1l11ll_opy_(getattr(item, bstack11l1ll1_opy_ (u"ࠪࡣࡩࡸࡩࡷࡧࡵࠫḂ"), None), bstack1llll111l1_opy_, logger, item)
        if not bstack11111l1l1_opy_.on():
            return
        bstack111lll11ll_opy_ = {
            bstack11l1ll1_opy_ (u"ࠫࡺࡻࡩࡥࠩḃ"): uuid4().__str__(),
            bstack11l1ll1_opy_ (u"ࠬࡹࡴࡢࡴࡷࡩࡩࡥࡡࡵࠩḄ"): bstack111ll1l111_opy_().isoformat() + bstack11l1ll1_opy_ (u"࡚࠭ࠨḅ"),
            bstack11l1ll1_opy_ (u"ࠧࡵࡻࡳࡩࠬḆ"): bstack11l1ll1_opy_ (u"ࠨࡪࡲࡳࡰ࠭ḇ"),
            bstack11l1ll1_opy_ (u"ࠩ࡫ࡳࡴࡱ࡟ࡵࡻࡳࡩࠬḈ"): bstack11l1ll1_opy_ (u"ࠪࡅࡋ࡚ࡅࡓࡡࡈࡅࡈࡎࠧḉ"),
            bstack11l1ll1_opy_ (u"ࠫ࡭ࡵ࡯࡬ࡡࡱࡥࡲ࡫ࠧḊ"): bstack11l1ll1_opy_ (u"ࠬࡺࡥࡢࡴࡧࡳࡼࡴࠧḋ")
        }
        _11l111l1ll_opy_[item.nodeid + bstack11l1ll1_opy_ (u"࠭࠭ࡵࡧࡤࡶࡩࡵࡷ࡯ࠩḌ")] = bstack111lll11ll_opy_
        bstack111lll11lll_opy_(item, bstack111lll11ll_opy_, bstack11l1ll1_opy_ (u"ࠧࡉࡱࡲ࡯ࡗࡻ࡮ࡔࡶࡤࡶࡹ࡫ࡤࠨḍ"))
    except Exception as err:
        print(bstack11l1ll1_opy_ (u"ࠨࡇࡻࡧࡪࡶࡴࡪࡱࡱࠤ࡮ࡴࠠࡱࡻࡷࡩࡸࡺ࡟ࡳࡷࡱࡸࡪࡹࡴࡠࡶࡨࡥࡷࡪ࡯ࡸࡰ࠽ࠤࢀࢃࠧḎ"), str(err))
@pytest.hookimpl(hookwrapper=True)
def pytest_fixture_setup(fixturedef, request):
    if bstack11l1l11l11l_opy_(fixturedef.argname):
        store[bstack11l1ll1_opy_ (u"ࠩࡦࡹࡷࡸࡥ࡯ࡶࡢࡱࡴࡪࡵ࡭ࡧࡢ࡭ࡹ࡫࡭ࠨḏ")] = request.node
    elif bstack11l1l111111_opy_(fixturedef.argname):
        store[bstack11l1ll1_opy_ (u"ࠪࡧࡺࡸࡲࡦࡰࡷࡣࡨࡲࡡࡴࡵࡢ࡭ࡹ࡫࡭ࠨḐ")] = request.node
    if not bstack11111l1l1_opy_.on():
        if cli.bstack11111lll11_opy_(bstack1llll1l1l11_opy_):
            cli.test_framework.track_event(cli_context, bstack1llll11llll_opy_.SETUP_FIXTURE, bstack1lll1llll11_opy_.PRE, fixturedef, request)
        outcome = yield
        if cli.bstack11111lll11_opy_(bstack1llll1l1l11_opy_):
            cli.test_framework.track_event(cli_context, bstack1llll11llll_opy_.SETUP_FIXTURE, bstack1lll1llll11_opy_.POST, fixturedef, request, outcome)
        return # skip all existing bstack111lll1l1ll_opy_
    start_time = datetime.datetime.now()
    if cli.bstack11111lll11_opy_(bstack1llll1l1l11_opy_):
        cli.test_framework.track_event(cli_context, bstack1llll11llll_opy_.SETUP_FIXTURE, bstack1lll1llll11_opy_.PRE, fixturedef, request)
    outcome = yield
    if cli.bstack11111lll11_opy_(bstack1llll1l1l11_opy_):
        cli.test_framework.track_event(cli_context, bstack1llll11llll_opy_.SETUP_FIXTURE, bstack1lll1llll11_opy_.POST, fixturedef, request, outcome)
        return # skip all existing bstack111lll1l1ll_opy_
    try:
        fixture = {
            bstack11l1ll1_opy_ (u"ࠫࡳࡧ࡭ࡦࠩḑ"): fixturedef.argname,
            bstack11l1ll1_opy_ (u"ࠬࡸࡥࡴࡷ࡯ࡸࠬḒ"): bstack11lll1llll1_opy_(outcome),
            bstack11l1ll1_opy_ (u"࠭ࡤࡶࡴࡤࡸ࡮ࡵ࡮ࠨḓ"): (datetime.datetime.now() - start_time).total_seconds() * 1000
        }
        current_test_item = store[bstack11l1ll1_opy_ (u"ࠧࡤࡷࡵࡶࡪࡴࡴࡠࡶࡨࡷࡹࡥࡩࡵࡧࡰࠫḔ")]
        if not _11l111l1ll_opy_.get(current_test_item.nodeid, None):
            _11l111l1ll_opy_[current_test_item.nodeid] = {bstack11l1ll1_opy_ (u"ࠨࡨ࡬ࡼࡹࡻࡲࡦࡵࠪḕ"): []}
        _11l111l1ll_opy_[current_test_item.nodeid][bstack11l1ll1_opy_ (u"ࠩࡩ࡭ࡽࡺࡵࡳࡧࡶࠫḖ")].append(fixture)
    except Exception as err:
        logger.debug(bstack11l1ll1_opy_ (u"ࠪࡉࡽࡩࡥࡱࡶ࡬ࡳࡳࠦࡩ࡯ࠢࡳࡽࡹ࡫ࡳࡵࡡࡩ࡭ࡽࡺࡵࡳࡧࡢࡷࡪࡺࡵࡱ࠼ࠣࡿࢂ࠭ḗ"), str(err))
if bstack1l11ll1l1_opy_() and bstack11111l1l1_opy_.on():
    def pytest_bdd_before_step(request, step):
        if cli.bstack11111lll11_opy_(bstack1llll1l1l11_opy_):
            cli.test_framework.track_event(cli_context, bstack1llll11llll_opy_.STEP, bstack1lll1llll11_opy_.PRE, request, step)
            return
        try:
            _11l111l1ll_opy_[request.node.nodeid][bstack11l1ll1_opy_ (u"ࠫࡹ࡫ࡳࡵࡡࡧࡥࡹࡧࠧḘ")].bstack1ll111l1l1_opy_(id(step))
        except Exception as err:
            print(bstack11l1ll1_opy_ (u"ࠬࡋࡸࡤࡧࡳࡸ࡮ࡵ࡮ࠡ࡫ࡱࠤࡵࡿࡴࡦࡵࡷࡣࡧࡪࡤࡠࡤࡨࡪࡴࡸࡥࡠࡵࡷࡩࡵࡀࠠࡼࡿࠪḙ"), str(err))
    def pytest_bdd_step_error(request, step, exception):
        if cli.bstack11111lll11_opy_(bstack1llll1l1l11_opy_):
            cli.test_framework.track_event(cli_context, bstack1llll11llll_opy_.STEP, bstack1lll1llll11_opy_.POST, request, step, exception)
            return
        try:
            _11l111l1ll_opy_[request.node.nodeid][bstack11l1ll1_opy_ (u"࠭ࡴࡦࡵࡷࡣࡩࡧࡴࡢࠩḚ")].bstack11l11lll11_opy_(id(step), Result.failed(exception=exception))
        except Exception as err:
            print(bstack11l1ll1_opy_ (u"ࠧࡆࡺࡦࡩࡵࡺࡩࡰࡰࠣ࡭ࡳࠦࡰࡺࡶࡨࡷࡹࡥࡢࡥࡦࡢࡷࡹ࡫ࡰࡠࡧࡵࡶࡴࡸ࠺ࠡࡽࢀࠫḛ"), str(err))
    def pytest_bdd_after_step(request, step):
        if cli.bstack11111lll11_opy_(bstack1llll1l1l11_opy_):
            cli.test_framework.track_event(cli_context, bstack1llll11llll_opy_.STEP, bstack1lll1llll11_opy_.POST, request, step)
            return
        try:
            bstack11l11lllll_opy_: bstack11l1l11lll_opy_ = _11l111l1ll_opy_[request.node.nodeid][bstack11l1ll1_opy_ (u"ࠨࡶࡨࡷࡹࡥࡤࡢࡶࡤࠫḜ")]
            bstack11l11lllll_opy_.bstack11l11lll11_opy_(id(step), Result.passed())
        except Exception as err:
            print(bstack11l1ll1_opy_ (u"ࠩࡈࡼࡨ࡫ࡰࡵ࡫ࡲࡲࠥ࡯࡮ࠡࡲࡼࡸࡪࡹࡴࡠࡤࡧࡨࡤࡹࡴࡦࡲࡢࡩࡷࡸ࡯ࡳ࠼ࠣࡿࢂ࠭ḝ"), str(err))
    def pytest_bdd_before_scenario(request, feature, scenario):
        global bstack111lllll1ll_opy_
        try:
            if not bstack11111l1l1_opy_.on() or bstack111lllll1ll_opy_ != bstack11l1ll1_opy_ (u"ࠪࡴࡾࡺࡥࡴࡶ࠰ࡦࡩࡪࠧḞ"):
                return
            if cli.bstack11111lll11_opy_(bstack1llll1l1l11_opy_):
                cli.test_framework.track_event(cli_context, bstack1llll11llll_opy_.TEST, bstack1lll1llll11_opy_.PRE, request, feature, scenario)
                return
            driver = bstack1ll1l1lll_opy_(threading.current_thread(), bstack11l1ll1_opy_ (u"ࠫࡧࡹࡴࡢࡥ࡮ࡗࡪࡹࡳࡪࡱࡱࡈࡷ࡯ࡶࡦࡴࠪḟ"), None)
            if not _11l111l1ll_opy_.get(request.node.nodeid, None):
                _11l111l1ll_opy_[request.node.nodeid] = {}
            bstack11l11lllll_opy_ = bstack11l1l11lll_opy_.bstack11l111lllll_opy_(
                scenario, feature, request.node,
                name=bstack11l1l111l11_opy_(request.node, scenario),
                started_at=bstack1ll1l1ll_opy_(),
                file_path=feature.filename,
                scope=[feature.name],
                framework=bstack11l1ll1_opy_ (u"ࠬࡖࡹࡵࡧࡶࡸ࠲ࡩࡵࡤࡷࡰࡦࡪࡸࠧḠ"),
                tags=bstack11l1l111l1l_opy_(feature, scenario),
                bstack11l11l1ll1_opy_=bstack11111l1l1_opy_.bstack11l11lll1l_opy_(driver) if driver and driver.session_id else {}
            )
            _11l111l1ll_opy_[request.node.nodeid][bstack11l1ll1_opy_ (u"࠭ࡴࡦࡵࡷࡣࡩࡧࡴࡢࠩḡ")] = bstack11l11lllll_opy_
            bstack111lll1l1l1_opy_(bstack11l11lllll_opy_.uuid)
            bstack11111l1l1_opy_.bstack11l11ll1l1_opy_(bstack11l1ll1_opy_ (u"ࠧࡕࡧࡶࡸࡗࡻ࡮ࡔࡶࡤࡶࡹ࡫ࡤࠨḢ"), bstack11l11lllll_opy_)
        except Exception as err:
            print(bstack11l1ll1_opy_ (u"ࠨࡇࡻࡧࡪࡶࡴࡪࡱࡱࠤ࡮ࡴࠠࡱࡻࡷࡩࡸࡺ࡟ࡣࡦࡧࡣࡧ࡫ࡦࡰࡴࡨࡣࡸࡩࡥ࡯ࡣࡵ࡭ࡴࡀࠠࡼࡿࠪḣ"), str(err))
def bstack111lll111l1_opy_(bstack11l11l1l1l_opy_):
    if bstack11l11l1l1l_opy_ in store[bstack11l1ll1_opy_ (u"ࠩࡦࡹࡷࡸࡥ࡯ࡶࡢ࡬ࡴࡵ࡫ࡠࡷࡸ࡭ࡩ࠭Ḥ")]:
        store[bstack11l1ll1_opy_ (u"ࠪࡧࡺࡸࡲࡦࡰࡷࡣ࡭ࡵ࡯࡬ࡡࡸࡹ࡮ࡪࠧḥ")].remove(bstack11l11l1l1l_opy_)
def bstack111lll1l1l1_opy_(test_uuid):
    store[bstack11l1ll1_opy_ (u"ࠫࡨࡻࡲࡳࡧࡱࡸࡤࡺࡥࡴࡶࡢࡹࡺ࡯ࡤࠨḦ")] = test_uuid
    threading.current_thread().current_test_uuid = test_uuid
@bstack11111l1l1_opy_.bstack11l1111l1l1_opy_
def bstack111lllll1l1_opy_(item, call, report):
    logger.debug(bstack11l1ll1_opy_ (u"ࠬ࡮ࡡ࡯ࡦ࡯ࡩࡤࡵ࠱࠲ࡻࡢࡸࡪࡹࡴࡠࡧࡹࡩࡳࡺ࠺ࠡࡵࡷࡥࡷࡺࠧḧ"))
    global bstack111lllll1ll_opy_
    bstack1lllllllll_opy_ = bstack1ll1l1ll_opy_()
    if hasattr(report, bstack11l1ll1_opy_ (u"࠭ࡳࡵࡱࡳࠫḨ")):
        bstack1lllllllll_opy_ = bstack1l111l1l1l1_opy_(report.stop)
    elif hasattr(report, bstack11l1ll1_opy_ (u"ࠧࡴࡶࡤࡶࡹ࠭ḩ")):
        bstack1lllllllll_opy_ = bstack1l111l1l1l1_opy_(report.start)
    try:
        if getattr(report, bstack11l1ll1_opy_ (u"ࠨࡹ࡫ࡩࡳ࠭Ḫ"), bstack11l1ll1_opy_ (u"ࠩࠪḫ")) == bstack11l1ll1_opy_ (u"ࠪࡧࡦࡲ࡬ࠨḬ"):
            logger.debug(bstack11l1ll1_opy_ (u"ࠫ࡭ࡧ࡮ࡥ࡮ࡨࡣࡴ࠷࠱ࡺࡡࡷࡩࡸࡺ࡟ࡦࡸࡨࡲࡹࡀࠠࡴࡶࡤࡸࡪࠦ࠭ࠡࡽࢀ࠰ࠥ࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫ࠡ࠯ࠣࡿࢂ࠭ḭ").format(getattr(report, bstack11l1ll1_opy_ (u"ࠬࡽࡨࡦࡰࠪḮ"), bstack11l1ll1_opy_ (u"࠭ࠧḯ")).__str__(), bstack111lllll1ll_opy_))
            if bstack111lllll1ll_opy_ == bstack11l1ll1_opy_ (u"ࠧࡱࡻࡷࡩࡸࡺࠧḰ"):
                _11l111l1ll_opy_[item.nodeid][bstack11l1ll1_opy_ (u"ࠨࡨ࡬ࡲ࡮ࡹࡨࡦࡦࡢࡥࡹ࠭ḱ")] = bstack1lllllllll_opy_
                bstack111llll1ll1_opy_(item, _11l111l1ll_opy_[item.nodeid], bstack11l1ll1_opy_ (u"ࠩࡗࡩࡸࡺࡒࡶࡰࡉ࡭ࡳ࡯ࡳࡩࡧࡧࠫḲ"), report, call)
                store[bstack11l1ll1_opy_ (u"ࠪࡧࡺࡸࡲࡦࡰࡷࡣࡹ࡫ࡳࡵࡡࡸࡹ࡮ࡪࠧḳ")] = None
            elif bstack111lllll1ll_opy_ == bstack11l1ll1_opy_ (u"ࠦࡵࡿࡴࡦࡵࡷ࠱ࡧࡪࡤࠣḴ"):
                bstack11l11lllll_opy_ = _11l111l1ll_opy_[item.nodeid][bstack11l1ll1_opy_ (u"ࠬࡺࡥࡴࡶࡢࡨࡦࡺࡡࠨḵ")]
                bstack11l11lllll_opy_.set(hooks=_11l111l1ll_opy_[item.nodeid].get(bstack11l1ll1_opy_ (u"࠭ࡨࡰࡱ࡮ࡷࠬḶ"), []))
                exception, bstack11l11l11ll_opy_ = None, None
                if call.excinfo:
                    exception = call.excinfo.value
                    bstack11l11l11ll_opy_ = [call.excinfo.exconly(), getattr(report, bstack11l1ll1_opy_ (u"ࠧ࡭ࡱࡱ࡫ࡷ࡫ࡰࡳࡶࡨࡼࡹ࠭ḷ"), bstack11l1ll1_opy_ (u"ࠨࠩḸ"))]
                bstack11l11lllll_opy_.stop(time=bstack1lllllllll_opy_, result=Result(result=getattr(report, bstack11l1ll1_opy_ (u"ࠩࡲࡹࡹࡩ࡯࡮ࡧࠪḹ"), bstack11l1ll1_opy_ (u"ࠪࡴࡦࡹࡳࡦࡦࠪḺ")), exception=exception, bstack11l11l11ll_opy_=bstack11l11l11ll_opy_))
                bstack11111l1l1_opy_.bstack11l11ll1l1_opy_(bstack11l1ll1_opy_ (u"࡙ࠫ࡫ࡳࡵࡔࡸࡲࡋ࡯࡮ࡪࡵ࡫ࡩࡩ࠭ḻ"), _11l111l1ll_opy_[item.nodeid][bstack11l1ll1_opy_ (u"ࠬࡺࡥࡴࡶࡢࡨࡦࡺࡡࠨḼ")])
        elif getattr(report, bstack11l1ll1_opy_ (u"࠭ࡷࡩࡧࡱࠫḽ"), bstack11l1ll1_opy_ (u"ࠧࠨḾ")) in [bstack11l1ll1_opy_ (u"ࠨࡵࡨࡸࡺࡶࠧḿ"), bstack11l1ll1_opy_ (u"ࠩࡷࡩࡦࡸࡤࡰࡹࡱࠫṀ")]:
            logger.debug(bstack11l1ll1_opy_ (u"ࠪ࡬ࡦࡴࡤ࡭ࡧࡢࡳ࠶࠷ࡹࡠࡶࡨࡷࡹࡥࡥࡷࡧࡱࡸ࠿ࠦࡳࡵࡣࡷࡩࠥ࠳ࠠࡼࡿ࠯ࠤ࡫ࡸࡡ࡮ࡧࡺࡳࡷࡱࠠ࠮ࠢࡾࢁࠬṁ").format(getattr(report, bstack11l1ll1_opy_ (u"ࠫࡼ࡮ࡥ࡯ࠩṂ"), bstack11l1ll1_opy_ (u"ࠬ࠭ṃ")).__str__(), bstack111lllll1ll_opy_))
            bstack11l1l1l1l1_opy_ = item.nodeid + bstack11l1ll1_opy_ (u"࠭࠭ࠨṄ") + getattr(report, bstack11l1ll1_opy_ (u"ࠧࡸࡪࡨࡲࠬṅ"), bstack11l1ll1_opy_ (u"ࠨࠩṆ"))
            if getattr(report, bstack11l1ll1_opy_ (u"ࠩࡶ࡯࡮ࡶࡰࡦࡦࠪṇ"), False):
                hook_type = bstack11l1ll1_opy_ (u"ࠪࡆࡊࡌࡏࡓࡇࡢࡉࡆࡉࡈࠨṈ") if getattr(report, bstack11l1ll1_opy_ (u"ࠫࡼ࡮ࡥ࡯ࠩṉ"), bstack11l1ll1_opy_ (u"ࠬ࠭Ṋ")) == bstack11l1ll1_opy_ (u"࠭ࡳࡦࡶࡸࡴࠬṋ") else bstack11l1ll1_opy_ (u"ࠧࡂࡈࡗࡉࡗࡥࡅࡂࡅࡋࠫṌ")
                _11l111l1ll_opy_[bstack11l1l1l1l1_opy_] = {
                    bstack11l1ll1_opy_ (u"ࠨࡷࡸ࡭ࡩ࠭ṍ"): uuid4().__str__(),
                    bstack11l1ll1_opy_ (u"ࠩࡶࡸࡦࡸࡴࡦࡦࡢࡥࡹ࠭Ṏ"): bstack1lllllllll_opy_,
                    bstack11l1ll1_opy_ (u"ࠪ࡬ࡴࡵ࡫ࡠࡶࡼࡴࡪ࠭ṏ"): hook_type
                }
            _11l111l1ll_opy_[bstack11l1l1l1l1_opy_][bstack11l1ll1_opy_ (u"ࠫ࡫࡯࡮ࡪࡵ࡫ࡩࡩࡥࡡࡵࠩṐ")] = bstack1lllllllll_opy_
            bstack111lll111l1_opy_(_11l111l1ll_opy_[bstack11l1l1l1l1_opy_][bstack11l1ll1_opy_ (u"ࠬࡻࡵࡪࡦࠪṑ")])
            bstack111lll11lll_opy_(item, _11l111l1ll_opy_[bstack11l1l1l1l1_opy_], bstack11l1ll1_opy_ (u"࠭ࡈࡰࡱ࡮ࡖࡺࡴࡆࡪࡰ࡬ࡷ࡭࡫ࡤࠨṒ"), report, call)
            if getattr(report, bstack11l1ll1_opy_ (u"ࠧࡸࡪࡨࡲࠬṓ"), bstack11l1ll1_opy_ (u"ࠨࠩṔ")) == bstack11l1ll1_opy_ (u"ࠩࡶࡩࡹࡻࡰࠨṕ"):
                if getattr(report, bstack11l1ll1_opy_ (u"ࠪࡳࡺࡺࡣࡰ࡯ࡨࠫṖ"), bstack11l1ll1_opy_ (u"ࠫࡵࡧࡳࡴࡧࡧࠫṗ")) == bstack11l1ll1_opy_ (u"ࠬ࡬ࡡࡪ࡮ࡨࡨࠬṘ"):
                    bstack111lll11ll_opy_ = {
                        bstack11l1ll1_opy_ (u"࠭ࡵࡶ࡫ࡧࠫṙ"): uuid4().__str__(),
                        bstack11l1ll1_opy_ (u"ࠧࡴࡶࡤࡶࡹ࡫ࡤࡠࡣࡷࠫṚ"): bstack1ll1l1ll_opy_(),
                        bstack11l1ll1_opy_ (u"ࠨࡨ࡬ࡲ࡮ࡹࡨࡦࡦࡢࡥࡹ࠭ṛ"): bstack1ll1l1ll_opy_()
                    }
                    _11l111l1ll_opy_[item.nodeid] = {**_11l111l1ll_opy_[item.nodeid], **bstack111lll11ll_opy_}
                    bstack111llll1ll1_opy_(item, _11l111l1ll_opy_[item.nodeid], bstack11l1ll1_opy_ (u"ࠩࡗࡩࡸࡺࡒࡶࡰࡖࡸࡦࡸࡴࡦࡦࠪṜ"))
                    bstack111llll1ll1_opy_(item, _11l111l1ll_opy_[item.nodeid], bstack11l1ll1_opy_ (u"ࠪࡘࡪࡹࡴࡓࡷࡱࡊ࡮ࡴࡩࡴࡪࡨࡨࠬṝ"), report, call)
    except Exception as err:
        print(bstack11l1ll1_opy_ (u"ࠫࡊࡾࡣࡦࡲࡷ࡭ࡴࡴࠠࡪࡰࠣ࡬ࡦࡴࡤ࡭ࡧࡢࡳ࠶࠷ࡹࡠࡶࡨࡷࡹࡥࡥࡷࡧࡱࡸ࠿ࠦࡻࡾࠩṞ"), str(err))
def bstack111lll1lll1_opy_(test, bstack111lll11ll_opy_, result=None, call=None, bstack1l11l11l1_opy_=None, outcome=None):
    file_path = os.path.relpath(test.fspath.strpath, start=os.getcwd())
    bstack11l11lllll_opy_ = {
        bstack11l1ll1_opy_ (u"ࠬࡻࡵࡪࡦࠪṟ"): bstack111lll11ll_opy_[bstack11l1ll1_opy_ (u"࠭ࡵࡶ࡫ࡧࠫṠ")],
        bstack11l1ll1_opy_ (u"ࠧࡵࡻࡳࡩࠬṡ"): bstack11l1ll1_opy_ (u"ࠨࡶࡨࡷࡹ࠭Ṣ"),
        bstack11l1ll1_opy_ (u"ࠩࡱࡥࡲ࡫ࠧṣ"): test.name,
        bstack11l1ll1_opy_ (u"ࠪࡦࡴࡪࡹࠨṤ"): {
            bstack11l1ll1_opy_ (u"ࠫࡱࡧ࡮ࡨࠩṥ"): bstack11l1ll1_opy_ (u"ࠬࡶࡹࡵࡪࡲࡲࠬṦ"),
            bstack11l1ll1_opy_ (u"࠭ࡣࡰࡦࡨࠫṧ"): inspect.getsource(test.obj)
        },
        bstack11l1ll1_opy_ (u"ࠧࡪࡦࡨࡲࡹ࡯ࡦࡪࡧࡵࠫṨ"): test.name,
        bstack11l1ll1_opy_ (u"ࠨࡵࡦࡳࡵ࡫ࠧṩ"): test.name,
        bstack11l1ll1_opy_ (u"ࠩࡶࡧࡴࡶࡥࡴࠩṪ"): bstack11ll1ll1_opy_.bstack111ll1l1ll_opy_(test),
        bstack11l1ll1_opy_ (u"ࠪࡪ࡮ࡲࡥࡠࡰࡤࡱࡪ࠭ṫ"): file_path,
        bstack11l1ll1_opy_ (u"ࠫࡱࡵࡣࡢࡶ࡬ࡳࡳ࠭Ṭ"): file_path,
        bstack11l1ll1_opy_ (u"ࠬࡸࡥࡴࡷ࡯ࡸࠬṭ"): bstack11l1ll1_opy_ (u"࠭ࡰࡦࡰࡧ࡭ࡳ࡭ࠧṮ"),
        bstack11l1ll1_opy_ (u"ࠧࡷࡥࡢࡪ࡮ࡲࡥࡱࡣࡷ࡬ࠬṯ"): file_path,
        bstack11l1ll1_opy_ (u"ࠨࡵࡷࡥࡷࡺࡥࡥࡡࡤࡸࠬṰ"): bstack111lll11ll_opy_[bstack11l1ll1_opy_ (u"ࠩࡶࡸࡦࡸࡴࡦࡦࡢࡥࡹ࠭ṱ")],
        bstack11l1ll1_opy_ (u"ࠪࡪࡷࡧ࡭ࡦࡹࡲࡶࡰ࠭Ṳ"): bstack11l1ll1_opy_ (u"ࠫࡕࡿࡴࡦࡵࡷࠫṳ"),
        bstack11l1ll1_opy_ (u"ࠬࡩࡵࡴࡶࡲࡱࡗ࡫ࡲࡶࡰࡓࡥࡷࡧ࡭ࠨṴ"): {
            bstack11l1ll1_opy_ (u"࠭ࡲࡦࡴࡸࡲࡤࡴࡡ࡮ࡧࠪṵ"): test.nodeid
        },
        bstack11l1ll1_opy_ (u"ࠧࡵࡣࡪࡷࠬṶ"): bstack1l111l11ll1_opy_(test.own_markers)
    }
    if bstack1l11l11l1_opy_ in [bstack11l1ll1_opy_ (u"ࠨࡖࡨࡷࡹࡘࡵ࡯ࡕ࡮࡭ࡵࡶࡥࡥࠩṷ"), bstack11l1ll1_opy_ (u"ࠩࡗࡩࡸࡺࡒࡶࡰࡉ࡭ࡳ࡯ࡳࡩࡧࡧࠫṸ")]:
        bstack11l11lllll_opy_[bstack11l1ll1_opy_ (u"ࠪࡱࡪࡺࡡࠨṹ")] = {
            bstack11l1ll1_opy_ (u"ࠫ࡫࡯ࡸࡵࡷࡵࡩࡸ࠭Ṻ"): bstack111lll11ll_opy_.get(bstack11l1ll1_opy_ (u"ࠬ࡬ࡩࡹࡶࡸࡶࡪࡹࠧṻ"), [])
        }
    if bstack1l11l11l1_opy_ == bstack11l1ll1_opy_ (u"࠭ࡔࡦࡵࡷࡖࡺࡴࡓ࡬࡫ࡳࡴࡪࡪࠧṼ"):
        bstack11l11lllll_opy_[bstack11l1ll1_opy_ (u"ࠧࡳࡧࡶࡹࡱࡺࠧṽ")] = bstack11l1ll1_opy_ (u"ࠨࡵ࡮࡭ࡵࡶࡥࡥࠩṾ")
        bstack11l11lllll_opy_[bstack11l1ll1_opy_ (u"ࠩ࡫ࡳࡴࡱࡳࠨṿ")] = bstack111lll11ll_opy_[bstack11l1ll1_opy_ (u"ࠪ࡬ࡴࡵ࡫ࡴࠩẀ")]
        bstack11l11lllll_opy_[bstack11l1ll1_opy_ (u"ࠫ࡫࡯࡮ࡪࡵ࡫ࡩࡩࡥࡡࡵࠩẁ")] = bstack111lll11ll_opy_[bstack11l1ll1_opy_ (u"ࠬ࡬ࡩ࡯࡫ࡶ࡬ࡪࡪ࡟ࡢࡶࠪẂ")]
    if result:
        bstack11l11lllll_opy_[bstack11l1ll1_opy_ (u"࠭ࡲࡦࡵࡸࡰࡹ࠭ẃ")] = result.outcome
        bstack11l11lllll_opy_[bstack11l1ll1_opy_ (u"ࠧࡥࡷࡵࡥࡹ࡯࡯࡯ࡡ࡬ࡲࡤࡳࡳࠨẄ")] = result.duration * 1000
        bstack11l11lllll_opy_[bstack11l1ll1_opy_ (u"ࠨࡨ࡬ࡲ࡮ࡹࡨࡦࡦࡢࡥࡹ࠭ẅ")] = bstack111lll11ll_opy_[bstack11l1ll1_opy_ (u"ࠩࡩ࡭ࡳ࡯ࡳࡩࡧࡧࡣࡦࡺࠧẆ")]
        if result.failed:
            bstack11l11lllll_opy_[bstack11l1ll1_opy_ (u"ࠪࡪࡦ࡯࡬ࡶࡴࡨࡣࡹࡿࡰࡦࠩẇ")] = bstack11111l1l1_opy_.bstack111l1l1111_opy_(call.excinfo.typename)
            bstack11l11lllll_opy_[bstack11l1ll1_opy_ (u"ࠫ࡫ࡧࡩ࡭ࡷࡵࡩࠬẈ")] = bstack11111l1l1_opy_.bstack11l11111ll1_opy_(call.excinfo, result)
        bstack11l11lllll_opy_[bstack11l1ll1_opy_ (u"ࠬ࡮࡯ࡰ࡭ࡶࠫẉ")] = bstack111lll11ll_opy_[bstack11l1ll1_opy_ (u"࠭ࡨࡰࡱ࡮ࡷࠬẊ")]
    if outcome:
        bstack11l11lllll_opy_[bstack11l1ll1_opy_ (u"ࠧࡳࡧࡶࡹࡱࡺࠧẋ")] = bstack11lll1llll1_opy_(outcome)
        bstack11l11lllll_opy_[bstack11l1ll1_opy_ (u"ࠨࡦࡸࡶࡦࡺࡩࡰࡰࡢ࡭ࡳࡥ࡭ࡴࠩẌ")] = 0
        bstack11l11lllll_opy_[bstack11l1ll1_opy_ (u"ࠩࡩ࡭ࡳ࡯ࡳࡩࡧࡧࡣࡦࡺࠧẍ")] = bstack111lll11ll_opy_[bstack11l1ll1_opy_ (u"ࠪࡪ࡮ࡴࡩࡴࡪࡨࡨࡤࡧࡴࠨẎ")]
        if bstack11l11lllll_opy_[bstack11l1ll1_opy_ (u"ࠫࡷ࡫ࡳࡶ࡮ࡷࠫẏ")] == bstack11l1ll1_opy_ (u"ࠬ࡬ࡡࡪ࡮ࡨࡨࠬẐ"):
            bstack11l11lllll_opy_[bstack11l1ll1_opy_ (u"࠭ࡦࡢ࡫࡯ࡹࡷ࡫࡟ࡵࡻࡳࡩࠬẑ")] = bstack11l1ll1_opy_ (u"ࠧࡖࡰ࡫ࡥࡳࡪ࡬ࡦࡦࡈࡶࡷࡵࡲࠨẒ")  # bstack111llllll11_opy_
            bstack11l11lllll_opy_[bstack11l1ll1_opy_ (u"ࠨࡨࡤ࡭ࡱࡻࡲࡦࠩẓ")] = [{bstack11l1ll1_opy_ (u"ࠩࡥࡥࡨࡱࡴࡳࡣࡦࡩࠬẔ"): [bstack11l1ll1_opy_ (u"ࠪࡷࡴࡳࡥࠡࡧࡵࡶࡴࡸࠧẕ")]}]
        bstack11l11lllll_opy_[bstack11l1ll1_opy_ (u"ࠫ࡭ࡵ࡯࡬ࡵࠪẖ")] = bstack111lll11ll_opy_[bstack11l1ll1_opy_ (u"ࠬ࡮࡯ࡰ࡭ࡶࠫẗ")]
    return bstack11l11lllll_opy_
def bstack111lll1111l_opy_(test, bstack111ll1ll11_opy_, bstack1l11l11l1_opy_, result, call, outcome, bstack111lll11111_opy_):
    file_path = os.path.relpath(test.fspath.strpath, start=os.getcwd())
    hook_type = bstack111ll1ll11_opy_[bstack11l1ll1_opy_ (u"࠭ࡨࡰࡱ࡮ࡣࡹࡿࡰࡦࠩẘ")]
    hook_name = bstack111ll1ll11_opy_[bstack11l1ll1_opy_ (u"ࠧࡩࡱࡲ࡯ࡤࡴࡡ࡮ࡧࠪẙ")]
    hook_data = {
        bstack11l1ll1_opy_ (u"ࠨࡷࡸ࡭ࡩ࠭ẚ"): bstack111ll1ll11_opy_[bstack11l1ll1_opy_ (u"ࠩࡸࡹ࡮ࡪࠧẛ")],
        bstack11l1ll1_opy_ (u"ࠪࡸࡾࡶࡥࠨẜ"): bstack11l1ll1_opy_ (u"ࠫ࡭ࡵ࡯࡬ࠩẝ"),
        bstack11l1ll1_opy_ (u"ࠬࡴࡡ࡮ࡧࠪẞ"): bstack11l1ll1_opy_ (u"࠭ࡻࡾࠩẟ").format(bstack11l1l111ll1_opy_(hook_name)),
        bstack11l1ll1_opy_ (u"ࠧࡣࡱࡧࡽࠬẠ"): {
            bstack11l1ll1_opy_ (u"ࠨ࡮ࡤࡲ࡬࠭ạ"): bstack11l1ll1_opy_ (u"ࠩࡳࡽࡹ࡮࡯࡯ࠩẢ"),
            bstack11l1ll1_opy_ (u"ࠪࡧࡴࡪࡥࠨả"): None
        },
        bstack11l1ll1_opy_ (u"ࠫࡸࡩ࡯ࡱࡧࠪẤ"): test.name,
        bstack11l1ll1_opy_ (u"ࠬࡹࡣࡰࡲࡨࡷࠬấ"): bstack11ll1ll1_opy_.bstack111ll1l1ll_opy_(test, hook_name),
        bstack11l1ll1_opy_ (u"࠭ࡦࡪ࡮ࡨࡣࡳࡧ࡭ࡦࠩẦ"): file_path,
        bstack11l1ll1_opy_ (u"ࠧ࡭ࡱࡦࡥࡹ࡯࡯࡯ࠩầ"): file_path,
        bstack11l1ll1_opy_ (u"ࠨࡴࡨࡷࡺࡲࡴࠨẨ"): bstack11l1ll1_opy_ (u"ࠩࡳࡩࡳࡪࡩ࡯ࡩࠪẩ"),
        bstack11l1ll1_opy_ (u"ࠪࡺࡨࡥࡦࡪ࡮ࡨࡴࡦࡺࡨࠨẪ"): file_path,
        bstack11l1ll1_opy_ (u"ࠫࡸࡺࡡࡳࡶࡨࡨࡤࡧࡴࠨẫ"): bstack111ll1ll11_opy_[bstack11l1ll1_opy_ (u"ࠬࡹࡴࡢࡴࡷࡩࡩࡥࡡࡵࠩẬ")],
        bstack11l1ll1_opy_ (u"࠭ࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࠩậ"): bstack11l1ll1_opy_ (u"ࠧࡑࡻࡷࡩࡸࡺ࠭ࡤࡷࡦࡹࡲࡨࡥࡳࠩẮ") if bstack111lllll1ll_opy_ == bstack11l1ll1_opy_ (u"ࠨࡲࡼࡸࡪࡹࡴ࠮ࡤࡧࡨࠬắ") else bstack11l1ll1_opy_ (u"ࠩࡓࡽࡹ࡫ࡳࡵࠩẰ"),
        bstack11l1ll1_opy_ (u"ࠪ࡬ࡴࡵ࡫ࡠࡶࡼࡴࡪ࠭ằ"): hook_type
    }
    bstack11l11l1l1ll_opy_ = bstack11l111111l_opy_(_11l111l1ll_opy_.get(test.nodeid, None))
    if bstack11l11l1l1ll_opy_:
        hook_data[bstack11l1ll1_opy_ (u"ࠫࡹ࡫ࡳࡵࡡࡵࡹࡳࡥࡩࡥࠩẲ")] = bstack11l11l1l1ll_opy_
    if result:
        hook_data[bstack11l1ll1_opy_ (u"ࠬࡸࡥࡴࡷ࡯ࡸࠬẳ")] = result.outcome
        hook_data[bstack11l1ll1_opy_ (u"࠭ࡤࡶࡴࡤࡸ࡮ࡵ࡮ࡠ࡫ࡱࡣࡲࡹࠧẴ")] = result.duration * 1000
        hook_data[bstack11l1ll1_opy_ (u"ࠧࡧ࡫ࡱ࡭ࡸ࡮ࡥࡥࡡࡤࡸࠬẵ")] = bstack111ll1ll11_opy_[bstack11l1ll1_opy_ (u"ࠨࡨ࡬ࡲ࡮ࡹࡨࡦࡦࡢࡥࡹ࠭Ặ")]
        if result.failed:
            hook_data[bstack11l1ll1_opy_ (u"ࠩࡩࡥ࡮ࡲࡵࡳࡧࡢࡸࡾࡶࡥࠨặ")] = bstack11111l1l1_opy_.bstack111l1l1111_opy_(call.excinfo.typename)
            hook_data[bstack11l1ll1_opy_ (u"ࠪࡪࡦ࡯࡬ࡶࡴࡨࠫẸ")] = bstack11111l1l1_opy_.bstack11l11111ll1_opy_(call.excinfo, result)
    if outcome:
        hook_data[bstack11l1ll1_opy_ (u"ࠫࡷ࡫ࡳࡶ࡮ࡷࠫẹ")] = bstack11lll1llll1_opy_(outcome)
        hook_data[bstack11l1ll1_opy_ (u"ࠬࡪࡵࡳࡣࡷ࡭ࡴࡴ࡟ࡪࡰࡢࡱࡸ࠭Ẻ")] = 100
        hook_data[bstack11l1ll1_opy_ (u"࠭ࡦࡪࡰ࡬ࡷ࡭࡫ࡤࡠࡣࡷࠫẻ")] = bstack111ll1ll11_opy_[bstack11l1ll1_opy_ (u"ࠧࡧ࡫ࡱ࡭ࡸ࡮ࡥࡥࡡࡤࡸࠬẼ")]
        if hook_data[bstack11l1ll1_opy_ (u"ࠨࡴࡨࡷࡺࡲࡴࠨẽ")] == bstack11l1ll1_opy_ (u"ࠩࡩࡥ࡮ࡲࡥࡥࠩẾ"):
            hook_data[bstack11l1ll1_opy_ (u"ࠪࡪࡦ࡯࡬ࡶࡴࡨࡣࡹࡿࡰࡦࠩế")] = bstack11l1ll1_opy_ (u"࡚ࠫࡴࡨࡢࡰࡧࡰࡪࡪࡅࡳࡴࡲࡶࠬỀ")  # bstack111llllll11_opy_
            hook_data[bstack11l1ll1_opy_ (u"ࠬ࡬ࡡࡪ࡮ࡸࡶࡪ࠭ề")] = [{bstack11l1ll1_opy_ (u"࠭ࡢࡢࡥ࡮ࡸࡷࡧࡣࡦࠩỂ"): [bstack11l1ll1_opy_ (u"ࠧࡴࡱࡰࡩࠥ࡫ࡲࡳࡱࡵࠫể")]}]
    if bstack111lll11111_opy_:
        hook_data[bstack11l1ll1_opy_ (u"ࠨࡴࡨࡷࡺࡲࡴࠨỄ")] = bstack111lll11111_opy_.result
        hook_data[bstack11l1ll1_opy_ (u"ࠩࡧࡹࡷࡧࡴࡪࡱࡱࡣ࡮ࡴ࡟࡮ࡵࠪễ")] = bstack11llll1lll1_opy_(bstack111ll1ll11_opy_[bstack11l1ll1_opy_ (u"ࠪࡷࡹࡧࡲࡵࡧࡧࡣࡦࡺࠧỆ")], bstack111ll1ll11_opy_[bstack11l1ll1_opy_ (u"ࠫ࡫࡯࡮ࡪࡵ࡫ࡩࡩࡥࡡࡵࠩệ")])
        hook_data[bstack11l1ll1_opy_ (u"ࠬ࡬ࡩ࡯࡫ࡶ࡬ࡪࡪ࡟ࡢࡶࠪỈ")] = bstack111ll1ll11_opy_[bstack11l1ll1_opy_ (u"࠭ࡦࡪࡰ࡬ࡷ࡭࡫ࡤࡠࡣࡷࠫỉ")]
        if hook_data[bstack11l1ll1_opy_ (u"ࠧࡳࡧࡶࡹࡱࡺࠧỊ")] == bstack11l1ll1_opy_ (u"ࠨࡨࡤ࡭ࡱ࡫ࡤࠨị"):
            hook_data[bstack11l1ll1_opy_ (u"ࠩࡩࡥ࡮ࡲࡵࡳࡧࡢࡸࡾࡶࡥࠨỌ")] = bstack11111l1l1_opy_.bstack111l1l1111_opy_(bstack111lll11111_opy_.exception_type)
            hook_data[bstack11l1ll1_opy_ (u"ࠪࡪࡦ࡯࡬ࡶࡴࡨࠫọ")] = [{bstack11l1ll1_opy_ (u"ࠫࡧࡧࡣ࡬ࡶࡵࡥࡨ࡫ࠧỎ"): bstack1l1111ll1ll_opy_(bstack111lll11111_opy_.exception)}]
    return hook_data
def bstack111llll1ll1_opy_(test, bstack111lll11ll_opy_, bstack1l11l11l1_opy_, result=None, call=None, outcome=None):
    logger.debug(bstack11l1ll1_opy_ (u"ࠬࡹࡥ࡯ࡦࡢࡸࡪࡹࡴࡠࡴࡸࡲࡤ࡫ࡶࡦࡰࡷ࠾ࠥࡇࡴࡵࡧࡰࡴࡹ࡯࡮ࡨࠢࡷࡳࠥ࡭ࡥ࡯ࡧࡵࡥࡹ࡫ࠠࡵࡧࡶࡸࠥࡪࡡࡵࡣࠣࡪࡴࡸࠠࡦࡸࡨࡲࡹࡥࡴࡺࡲࡨࠤ࠲ࠦࡻࡾࠩỏ").format(bstack1l11l11l1_opy_))
    bstack11l11lllll_opy_ = bstack111lll1lll1_opy_(test, bstack111lll11ll_opy_, result, call, bstack1l11l11l1_opy_, outcome)
    driver = getattr(test, bstack11l1ll1_opy_ (u"࠭࡟ࡥࡴ࡬ࡺࡪࡸࠧỐ"), None)
    if bstack1l11l11l1_opy_ == bstack11l1ll1_opy_ (u"ࠧࡕࡧࡶࡸࡗࡻ࡮ࡔࡶࡤࡶࡹ࡫ࡤࠨố") and driver:
        bstack11l11lllll_opy_[bstack11l1ll1_opy_ (u"ࠨ࡫ࡱࡸࡪ࡭ࡲࡢࡶ࡬ࡳࡳࡹࠧỒ")] = bstack11111l1l1_opy_.bstack11l11lll1l_opy_(driver)
    if bstack1l11l11l1_opy_ == bstack11l1ll1_opy_ (u"ࠩࡗࡩࡸࡺࡒࡶࡰࡖ࡯࡮ࡶࡰࡦࡦࠪồ"):
        bstack1l11l11l1_opy_ = bstack11l1ll1_opy_ (u"ࠪࡘࡪࡹࡴࡓࡷࡱࡊ࡮ࡴࡩࡴࡪࡨࡨࠬỔ")
    bstack111ll1lll1_opy_ = {
        bstack11l1ll1_opy_ (u"ࠫࡪࡼࡥ࡯ࡶࡢࡸࡾࡶࡥࠨổ"): bstack1l11l11l1_opy_,
        bstack11l1ll1_opy_ (u"ࠬࡺࡥࡴࡶࡢࡶࡺࡴࠧỖ"): bstack11l11lllll_opy_
    }
    bstack11111l1l1_opy_.bstack11111ll1_opy_(bstack111ll1lll1_opy_)
    if bstack1l11l11l1_opy_ == bstack11l1ll1_opy_ (u"࠭ࡔࡦࡵࡷࡖࡺࡴࡓࡵࡣࡵࡸࡪࡪࠧỗ"):
        threading.current_thread().bstackTestMeta = {bstack11l1ll1_opy_ (u"ࠧࡴࡶࡤࡸࡺࡹࠧỘ"): bstack11l1ll1_opy_ (u"ࠨࡲࡨࡲࡩ࡯࡮ࡨࠩộ")}
    elif bstack1l11l11l1_opy_ == bstack11l1ll1_opy_ (u"ࠩࡗࡩࡸࡺࡒࡶࡰࡉ࡭ࡳ࡯ࡳࡩࡧࡧࠫỚ"):
        threading.current_thread().bstackTestMeta = {bstack11l1ll1_opy_ (u"ࠪࡷࡹࡧࡴࡶࡵࠪớ"): getattr(result, bstack11l1ll1_opy_ (u"ࠫࡴࡻࡴࡤࡱࡰࡩࠬỜ"), bstack11l1ll1_opy_ (u"ࠬ࠭ờ"))}
def bstack111lll11lll_opy_(test, bstack111lll11ll_opy_, bstack1l11l11l1_opy_, result=None, call=None, outcome=None, bstack111lll11111_opy_=None):
    logger.debug(bstack11l1ll1_opy_ (u"࠭ࡳࡦࡰࡧࡣ࡭ࡵ࡯࡬ࡡࡵࡹࡳࡥࡥࡷࡧࡱࡸ࠿ࠦࡁࡵࡶࡨࡱࡵࡺࡩ࡯ࡩࠣࡸࡴࠦࡧࡦࡰࡨࡶࡦࡺࡥࠡࡪࡲࡳࡰࠦࡤࡢࡶࡤ࠰ࠥ࡫ࡶࡦࡰࡷࡘࡾࡶࡥࠡ࠯ࠣࡿࢂ࠭Ở").format(bstack1l11l11l1_opy_))
    hook_data = bstack111lll1111l_opy_(test, bstack111lll11ll_opy_, bstack1l11l11l1_opy_, result, call, outcome, bstack111lll11111_opy_)
    bstack111ll1lll1_opy_ = {
        bstack11l1ll1_opy_ (u"ࠧࡦࡸࡨࡲࡹࡥࡴࡺࡲࡨࠫở"): bstack1l11l11l1_opy_,
        bstack11l1ll1_opy_ (u"ࠨࡪࡲࡳࡰࡥࡲࡶࡰࠪỠ"): hook_data
    }
    bstack11111l1l1_opy_.bstack11111ll1_opy_(bstack111ll1lll1_opy_)
def bstack11l111111l_opy_(bstack111lll11ll_opy_):
    if not bstack111lll11ll_opy_:
        return None
    if bstack111lll11ll_opy_.get(bstack11l1ll1_opy_ (u"ࠩࡷࡩࡸࡺ࡟ࡥࡣࡷࡥࠬỡ"), None):
        return getattr(bstack111lll11ll_opy_[bstack11l1ll1_opy_ (u"ࠪࡸࡪࡹࡴࡠࡦࡤࡸࡦ࠭Ợ")], bstack11l1ll1_opy_ (u"ࠫࡺࡻࡩࡥࠩợ"), None)
    return bstack111lll11ll_opy_.get(bstack11l1ll1_opy_ (u"ࠬࡻࡵࡪࡦࠪỤ"), None)
@pytest.fixture(autouse=True)
def second_fixture(caplog, request):
    if cli.bstack11111lll11_opy_(bstack1llll1l1l11_opy_):
        cli.test_framework.track_event(cli_context, bstack1llll11llll_opy_.LOG, bstack1lll1llll11_opy_.PRE, request, caplog)
    yield
    if cli.bstack11111lll11_opy_(bstack1llll1l1l11_opy_):
        cli.test_framework.track_event(cli_context, bstack1llll11llll_opy_.LOG, bstack1lll1llll11_opy_.POST, request, caplog)
        return # skip all existing bstack111lll1l1ll_opy_
    try:
        if not bstack11111l1l1_opy_.on():
            return
        places = [bstack11l1ll1_opy_ (u"࠭ࡳࡦࡶࡸࡴࠬụ"), bstack11l1ll1_opy_ (u"ࠧࡤࡣ࡯ࡰࠬỦ"), bstack11l1ll1_opy_ (u"ࠨࡶࡨࡥࡷࡪ࡯ࡸࡰࠪủ")]
        logs = []
        for bstack111llll11ll_opy_ in places:
            records = caplog.get_records(bstack111llll11ll_opy_)
            bstack111llll1lll_opy_ = bstack11l1ll1_opy_ (u"ࠩࡷࡩࡸࡺ࡟ࡳࡷࡱࡣࡺࡻࡩࡥࠩỨ") if bstack111llll11ll_opy_ == bstack11l1ll1_opy_ (u"ࠪࡧࡦࡲ࡬ࠨứ") else bstack11l1ll1_opy_ (u"ࠫ࡭ࡵ࡯࡬ࡡࡵࡹࡳࡥࡵࡶ࡫ࡧࠫỪ")
            bstack111llll1l11_opy_ = request.node.nodeid + (bstack11l1ll1_opy_ (u"ࠬ࠭ừ") if bstack111llll11ll_opy_ == bstack11l1ll1_opy_ (u"࠭ࡣࡢ࡮࡯ࠫỬ") else bstack11l1ll1_opy_ (u"ࠧ࠮ࠩử") + bstack111llll11ll_opy_)
            test_uuid = bstack11l111111l_opy_(_11l111l1ll_opy_.get(bstack111llll1l11_opy_, None))
            if not test_uuid:
                continue
            for record in records:
                if bstack11llll1l111_opy_(record.message):
                    continue
                logs.append({
                    bstack11l1ll1_opy_ (u"ࠨࡶ࡬ࡱࡪࡹࡴࡢ࡯ࡳࠫỮ"): bstack1l11111l1l1_opy_(record.created).isoformat() + bstack11l1ll1_opy_ (u"ࠩ࡝ࠫữ"),
                    bstack11l1ll1_opy_ (u"ࠪࡰࡪࡼࡥ࡭ࠩỰ"): record.levelname,
                    bstack11l1ll1_opy_ (u"ࠫࡲ࡫ࡳࡴࡣࡪࡩࠬự"): record.message,
                    bstack111llll1lll_opy_: test_uuid
                })
        if len(logs) > 0:
            bstack11111l1l1_opy_.bstack1l1l1lll1l_opy_(logs)
    except Exception as err:
        print(bstack11l1ll1_opy_ (u"ࠬࡋࡸࡤࡧࡳࡸ࡮ࡵ࡮ࠡ࡫ࡱࠤࡸ࡫ࡣࡰࡰࡧࡣ࡫࡯ࡸࡵࡷࡵࡩ࠿ࠦࡻࡾࠩỲ"), str(err))
def bstack1l1ll1111_opy_(sequence, driver_command, response=None, driver = None, args = None):
    global bstack11ll1l1lll_opy_
    bstack1l1111ll1_opy_ = bstack1ll1l1lll_opy_(threading.current_thread(), bstack11l1ll1_opy_ (u"࠭ࡩࡴࡃ࠴࠵ࡾ࡚ࡥࡴࡶࠪỳ"), None) and bstack1ll1l1lll_opy_(
            threading.current_thread(), bstack11l1ll1_opy_ (u"ࠧࡢ࠳࠴ࡽࡕࡲࡡࡵࡨࡲࡶࡲ࠭Ỵ"), None)
    bstack11ll1l1l_opy_ = getattr(driver, bstack11l1ll1_opy_ (u"ࠨࡤࡶࡸࡦࡩ࡫ࡂ࠳࠴ࡽࡘ࡮࡯ࡶ࡮ࡧࡗࡨࡧ࡮ࠨỵ"), None) != None and getattr(driver, bstack11l1ll1_opy_ (u"ࠩࡥࡷࡹࡧࡣ࡬ࡃ࠴࠵ࡾ࡙ࡨࡰࡷ࡯ࡨࡘࡩࡡ࡯ࠩỶ"), None) == True
    if sequence == bstack11l1ll1_opy_ (u"ࠪࡦࡪ࡬࡯ࡳࡧࠪỷ") and driver != None:
      if not bstack11ll1l1lll_opy_ and bstack1ll1l1l11ll_opy_() and bstack11l1ll1_opy_ (u"ࠫࡦࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࠫỸ") in CONFIG and CONFIG[bstack11l1ll1_opy_ (u"ࠬࡧࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠬỹ")] == True and bstack1l1ll1111l_opy_.bstack11l1l1111_opy_(driver_command) and (bstack11ll1l1l_opy_ or bstack1l1111ll1_opy_) and not bstack1llll1lll1_opy_(args):
        try:
          bstack11ll1l1lll_opy_ = True
          logger.debug(bstack11l1ll1_opy_ (u"࠭ࡐࡦࡴࡩࡳࡷࡳࡩ࡯ࡩࠣࡷࡨࡧ࡮ࠡࡨࡲࡶࠥࢁࡽࠨỺ").format(driver_command))
          logger.debug(perform_scan(driver, driver_command=driver_command))
        except Exception as err:
          logger.debug(bstack11l1ll1_opy_ (u"ࠧࡇࡣ࡬ࡰࡪࡪࠠࡵࡱࠣࡴࡪࡸࡦࡰࡴࡰࠤࡸࡩࡡ࡯ࠢࡾࢁࠬỻ").format(str(err)))
        bstack11ll1l1lll_opy_ = False
    if sequence == bstack11l1ll1_opy_ (u"ࠨࡣࡩࡸࡪࡸࠧỼ"):
        if driver_command == bstack11l1ll1_opy_ (u"ࠩࡶࡧࡷ࡫ࡥ࡯ࡵ࡫ࡳࡹ࠭ỽ"):
            bstack11111l1l1_opy_.bstack1lllll1l1l_opy_({
                bstack11l1ll1_opy_ (u"ࠪ࡭ࡲࡧࡧࡦࠩỾ"): response[bstack11l1ll1_opy_ (u"ࠫࡻࡧ࡬ࡶࡧࠪỿ")],
                bstack11l1ll1_opy_ (u"ࠬࡺࡥࡴࡶࡢࡶࡺࡴ࡟ࡶࡷ࡬ࡨࠬἀ"): store[bstack11l1ll1_opy_ (u"࠭ࡣࡶࡴࡵࡩࡳࡺ࡟ࡵࡧࡶࡸࡤࡻࡵࡪࡦࠪἁ")]
            })
def bstack1ll111ll11_opy_():
    global bstack1l1ll1l1l1_opy_
    bstack1ll1ll111_opy_.bstack1l11l111l_opy_()
    logging.shutdown()
    bstack11111l1l1_opy_.bstack11l1111111_opy_()
    for driver in bstack1l1ll1l1l1_opy_:
        try:
            driver.quit()
        except Exception as e:
            pass
def bstack111llll111l_opy_(*args):
    global bstack1l1ll1l1l1_opy_
    bstack11111l1l1_opy_.bstack11l1111111_opy_()
    for driver in bstack1l1ll1l1l1_opy_:
        try:
            driver.quit()
        except Exception as e:
            pass
@measure(event_name=EVENTS.bstack1l11ll1111_opy_, stage=STAGE.bstack1l1ll1llll_opy_, bstack1l11l1ll_opy_=bstack1lll1l11l_opy_)
def bstack11llll1111_opy_(self, *args, **kwargs):
    bstack1llll1ll_opy_ = bstack11lll111ll_opy_(self, *args, **kwargs)
    bstack1ll1l1l1l_opy_ = getattr(threading.current_thread(), bstack11l1ll1_opy_ (u"ࠧࡣࡵࡷࡥࡨࡱࡔࡦࡵࡷࡑࡪࡺࡡࠨἂ"), None)
    if bstack1ll1l1l1l_opy_ and bstack1ll1l1l1l_opy_.get(bstack11l1ll1_opy_ (u"ࠨࡵࡷࡥࡹࡻࡳࠨἃ"), bstack11l1ll1_opy_ (u"ࠩࠪἄ")) == bstack11l1ll1_opy_ (u"ࠪࡴࡪࡴࡤࡪࡰࡪࠫἅ"):
        bstack11111l1l1_opy_.bstack1111l11l1_opy_(self)
    return bstack1llll1ll_opy_
@measure(event_name=EVENTS.bstack1l111l11l_opy_, stage=STAGE.bstack11111l1l_opy_, bstack1l11l1ll_opy_=bstack1lll1l11l_opy_)
def bstack1l1lll11_opy_(framework_name):
    from bstack_utils.config import Config
    bstack1ll1l11l1_opy_ = Config.bstack1l111l1ll1_opy_()
    if bstack1ll1l11l1_opy_.get_property(bstack11l1ll1_opy_ (u"ࠫࡧࡹࡴࡢࡥ࡮ࡣࡲࡵࡤࡠࡥࡤࡰࡱ࡫ࡤࠨἆ")):
        return
    bstack1ll1l11l1_opy_.bstack1l111llll1_opy_(bstack11l1ll1_opy_ (u"ࠬࡨࡳࡵࡣࡦ࡯ࡤࡳ࡯ࡥࡡࡦࡥࡱࡲࡥࡥࠩἇ"), True)
    global bstack111111ll1_opy_
    global bstack1111111ll_opy_
    bstack111111ll1_opy_ = framework_name
    logger.info(bstack1ll1l1111_opy_.format(bstack111111ll1_opy_.split(bstack11l1ll1_opy_ (u"࠭࠭ࠨἈ"))[0]))
    try:
        from selenium import webdriver
        from selenium.webdriver.common.service import Service
        from selenium.webdriver.remote.webdriver import WebDriver
        if bstack1ll1l1l11ll_opy_():
            Service.start = bstack1l1111111l_opy_
            Service.stop = bstack1ll111lll_opy_
            webdriver.Remote.get = bstack1l11lllll_opy_
            webdriver.Remote.__init__ = bstack11l111111_opy_
            if not isinstance(os.getenv(bstack11l1ll1_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡐ࡚ࡖࡈࡗ࡙ࡥࡐࡂࡔࡄࡐࡑࡋࡌࠨἉ")), str):
                return
            WebDriver.close = bstack11lll1llll_opy_
            WebDriver.quit = bstack1l1l1l11_opy_
            WebDriver.getAccessibilityResults = getAccessibilityResults
            WebDriver.get_accessibility_results = getAccessibilityResults
            WebDriver.getAccessibilityResultsSummary = getAccessibilityResultsSummary
            WebDriver.get_accessibility_results_summary = getAccessibilityResultsSummary
            WebDriver.performScan = perform_scan
            WebDriver.perform_scan = perform_scan
        elif bstack11111l1l1_opy_.on():
            webdriver.Remote.__init__ = bstack11llll1111_opy_
        bstack1111111ll_opy_ = True
    except Exception as e:
        pass
    bstack11lll1l1ll_opy_()
    if os.environ.get(bstack11l1ll1_opy_ (u"ࠨࡕࡈࡐࡊࡔࡉࡖࡏࡢࡓࡗࡥࡐࡍࡃ࡜࡛ࡗࡏࡇࡉࡖࡢࡍࡓ࡙ࡔࡂࡎࡏࡉࡉ࠭Ἂ")):
        bstack1111111ll_opy_ = eval(os.environ.get(bstack11l1ll1_opy_ (u"ࠩࡖࡉࡑࡋࡎࡊࡗࡐࡣࡔࡘ࡟ࡑࡎࡄ࡝࡜ࡘࡉࡈࡊࡗࡣࡎࡔࡓࡕࡃࡏࡐࡊࡊࠧἋ")))
    if not bstack1111111ll_opy_:
        bstack1ll11lll1_opy_(bstack11l1ll1_opy_ (u"ࠥࡔࡦࡩ࡫ࡢࡩࡨࡷࠥࡴ࡯ࡵࠢ࡬ࡲࡸࡺࡡ࡭࡮ࡨࡨࠧἌ"), bstack1llll1lll_opy_)
    if bstack1l1ll1lll_opy_():
        try:
            from selenium.webdriver.remote.remote_connection import RemoteConnection
            RemoteConnection._11ll1lll_opy_ = bstack11lll1ll1l_opy_
        except Exception as e:
            logger.error(bstack11ll1l11l1_opy_.format(str(e)))
    if bstack11l1ll1_opy_ (u"ࠫࡵࡿࡴࡦࡵࡷࠫἍ") in str(framework_name).lower():
        if not bstack1ll1l1l11ll_opy_():
            return
        try:
            from pytest_selenium import pytest_selenium
            from _pytest.config import Config
            pytest_selenium.pytest_report_header = bstack1l111lll_opy_
            from pytest_selenium.drivers import browserstack
            browserstack.pytest_selenium_runtest_makereport = bstack1l1111llll_opy_
            Config.getoption = bstack1ll11l1ll_opy_
        except Exception as e:
            pass
        try:
            from pytest_bdd import reporting
            reporting.runtest_makereport = bstack1l1lll11l_opy_
        except Exception as e:
            pass
@measure(event_name=EVENTS.bstack1ll1l1111l_opy_, stage=STAGE.bstack1l1ll1llll_opy_, bstack1l11l1ll_opy_=bstack1lll1l11l_opy_)
def bstack1l1l1l11_opy_(self):
    global bstack111111ll1_opy_
    global bstack1l1l1ll1_opy_
    global bstack1llll11l_opy_
    try:
        if bstack11l1ll1_opy_ (u"ࠬࡶࡹࡵࡧࡶࡸࠬἎ") in bstack111111ll1_opy_ and self.session_id != None and bstack1ll1l1lll_opy_(threading.current_thread(), bstack11l1ll1_opy_ (u"࠭ࡴࡦࡵࡷࡗࡹࡧࡴࡶࡵࠪἏ"), bstack11l1ll1_opy_ (u"ࠧࠨἐ")) != bstack11l1ll1_opy_ (u"ࠨࡵ࡮࡭ࡵࡶࡥࡥࠩἑ"):
            bstack1l111ll1l1_opy_ = bstack11l1ll1_opy_ (u"ࠩࡳࡥࡸࡹࡥࡥࠩἒ") if len(threading.current_thread().bstackTestErrorMessages) == 0 else bstack11l1ll1_opy_ (u"ࠪࡪࡦ࡯࡬ࡦࡦࠪἓ")
            bstack1l1ll11lll_opy_(logger, True)
            if self != None:
                bstack1ll1llllll_opy_(self, bstack1l111ll1l1_opy_, bstack11l1ll1_opy_ (u"ࠫ࠱ࠦࠧἔ").join(threading.current_thread().bstackTestErrorMessages))
        if not cli.bstack11111lll11_opy_(bstack1llll1l1l11_opy_):
            item = store.get(bstack11l1ll1_opy_ (u"ࠬࡩࡵࡳࡴࡨࡲࡹࡥࡴࡦࡵࡷࡣ࡮ࡺࡥ࡮ࠩἕ"), None)
            if item is not None and bstack1ll1l1lll_opy_(threading.current_thread(), bstack11l1ll1_opy_ (u"࠭ࡡ࠲࠳ࡼࡔࡱࡧࡴࡧࡱࡵࡱࠬ἖"), None):
                bstack11l111lll_opy_.bstack1l1l1l11ll_opy_(self, bstack1llll111l1_opy_, logger, item)
        threading.current_thread().testStatus = bstack11l1ll1_opy_ (u"ࠧࠨ἗")
    except Exception as e:
        logger.debug(bstack11l1ll1_opy_ (u"ࠣࡇࡵࡶࡴࡸࠠࡸࡪ࡬ࡰࡪࠦ࡭ࡢࡴ࡮࡭ࡳ࡭ࠠࡴࡶࡤࡸࡺࡹ࠺ࠡࠤἘ") + str(e))
    bstack1llll11l_opy_(self)
    self.session_id = None
@measure(event_name=EVENTS.bstack1l1ll1ll1_opy_, stage=STAGE.bstack1l1ll1llll_opy_, bstack1l11l1ll_opy_=bstack1lll1l11l_opy_)
def bstack11l111111_opy_(self, command_executor,
             desired_capabilities=None, browser_profile=None, proxy=None,
             keep_alive=True, file_detector=None, options=None):
    global CONFIG
    global bstack1l1l1ll1_opy_
    global bstack1lll1l11l_opy_
    global bstack11ll1ll1l1_opy_
    global bstack111111ll1_opy_
    global bstack11lll111ll_opy_
    global bstack1l1ll1l1l1_opy_
    global bstack1l1ll11ll1_opy_
    global bstack1ll1lll1ll_opy_
    global bstack1llll111l1_opy_
    CONFIG[bstack11l1ll1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡔࡆࡎࠫἙ")] = str(bstack111111ll1_opy_) + str(__version__)
    command_executor = bstack1l11111l1_opy_(bstack1l1ll11ll1_opy_, CONFIG)
    logger.debug(bstack11ll111l11_opy_.format(command_executor))
    proxy = bstack1l11l1l111_opy_(CONFIG, proxy)
    bstack1ll1lll1l_opy_ = 0
    try:
        if bstack11ll1ll1l1_opy_ is True:
            bstack1ll1lll1l_opy_ = int(os.environ.get(bstack11l1ll1_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡓࡐࡆ࡚ࡆࡐࡔࡐࡣࡎࡔࡄࡆ࡚ࠪἚ")))
    except:
        bstack1ll1lll1l_opy_ = 0
    bstack11l11ll1_opy_ = bstack1l11llll1l_opy_(CONFIG, bstack1ll1lll1l_opy_)
    logger.debug(bstack1llll11l1l_opy_.format(str(bstack11l11ll1_opy_)))
    bstack1llll111l1_opy_ = CONFIG.get(bstack11l1ll1_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲࡹࠧἛ"))[bstack1ll1lll1l_opy_]
    if bstack11l1ll1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡐࡴࡩࡡ࡭ࠩἜ") in CONFIG and CONFIG[bstack11l1ll1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡑࡵࡣࡢ࡮ࠪἝ")]:
        bstack11ll1lllll_opy_(bstack11l11ll1_opy_, bstack1ll1lll1ll_opy_)
    if bstack11lll11ll1_opy_.bstack111l1l1l_opy_(CONFIG, bstack1ll1lll1l_opy_) and bstack11lll11ll1_opy_.bstack11llllll_opy_(bstack11l11ll1_opy_, options, desired_capabilities):
        threading.current_thread().a11yPlatform = True
        if not cli.bstack11111lll11_opy_(bstack1llll1l1l11_opy_):
            bstack11lll11ll1_opy_.set_capabilities(bstack11l11ll1_opy_, CONFIG)
    if desired_capabilities:
        bstack1111l111_opy_ = bstack1l11l11ll_opy_(desired_capabilities)
        bstack1111l111_opy_[bstack11l1ll1_opy_ (u"ࠧࡶࡵࡨ࡛࠸ࡉࠧ἞")] = bstack1l1lll1l1l_opy_(CONFIG)
        bstack1l11lllll1_opy_ = bstack1l11llll1l_opy_(bstack1111l111_opy_)
        if bstack1l11lllll1_opy_:
            bstack11l11ll1_opy_ = update(bstack1l11lllll1_opy_, bstack11l11ll1_opy_)
        desired_capabilities = None
    if options:
        bstack11lll1l11_opy_(options, bstack11l11ll1_opy_)
    if not options:
        options = bstack11l1ll1l1_opy_(bstack11l11ll1_opy_)
    if proxy and bstack1ll111111l_opy_() >= version.parse(bstack11l1ll1_opy_ (u"ࠨ࠶࠱࠵࠵࠴࠰ࠨ἟")):
        options.proxy(proxy)
    if options and bstack1ll111111l_opy_() >= version.parse(bstack11l1ll1_opy_ (u"ࠩ࠶࠲࠽࠴࠰ࠨἠ")):
        desired_capabilities = None
    if (
            not options and not desired_capabilities
    ) or (
            bstack1ll111111l_opy_() < version.parse(bstack11l1ll1_opy_ (u"ࠪ࠷࠳࠾࠮࠱ࠩἡ")) and not desired_capabilities
    ):
        desired_capabilities = {}
        desired_capabilities.update(bstack11l11ll1_opy_)
    logger.info(bstack1ll1ll11_opy_)
    bstack1ll111ll1l_opy_.end(EVENTS.bstack1l111l11l_opy_.value, EVENTS.bstack1l111l11l_opy_.value + bstack11l1ll1_opy_ (u"ࠦ࠿ࡹࡴࡢࡴࡷࠦἢ"),
                               EVENTS.bstack1l111l11l_opy_.value + bstack11l1ll1_opy_ (u"ࠧࡀࡥ࡯ࡦࠥἣ"), True, None)
    if bstack1ll111111l_opy_() >= version.parse(bstack11l1ll1_opy_ (u"࠭࠴࠯࠳࠳࠲࠵࠭ἤ")):
        bstack11lll111ll_opy_(self, command_executor=command_executor,
                  options=options, keep_alive=keep_alive, file_detector=file_detector)
    elif bstack1ll111111l_opy_() >= version.parse(bstack11l1ll1_opy_ (u"ࠧ࠴࠰࠻࠲࠵࠭ἥ")):
        bstack11lll111ll_opy_(self, command_executor=command_executor,
                  desired_capabilities=desired_capabilities, options=options,
                  browser_profile=browser_profile, proxy=proxy,
                  keep_alive=keep_alive, file_detector=file_detector)
    elif bstack1ll111111l_opy_() >= version.parse(bstack11l1ll1_opy_ (u"ࠨ࠴࠱࠹࠸࠴࠰ࠨἦ")):
        bstack11lll111ll_opy_(self, command_executor=command_executor,
                  desired_capabilities=desired_capabilities,
                  browser_profile=browser_profile, proxy=proxy,
                  keep_alive=keep_alive, file_detector=file_detector)
    else:
        bstack11lll111ll_opy_(self, command_executor=command_executor,
                  desired_capabilities=desired_capabilities,
                  browser_profile=browser_profile, proxy=proxy,
                  keep_alive=keep_alive)
    try:
        bstack1lll1lllll_opy_ = bstack11l1ll1_opy_ (u"ࠩࠪἧ")
        if bstack1ll111111l_opy_() >= version.parse(bstack11l1ll1_opy_ (u"ࠪ࠸࠳࠶࠮࠱ࡤ࠴ࠫἨ")):
            bstack1lll1lllll_opy_ = self.caps.get(bstack11l1ll1_opy_ (u"ࠦࡴࡶࡴࡪ࡯ࡤࡰࡍࡻࡢࡖࡴ࡯ࠦἩ"))
        else:
            bstack1lll1lllll_opy_ = self.capabilities.get(bstack11l1ll1_opy_ (u"ࠧࡵࡰࡵ࡫ࡰࡥࡱࡎࡵࡣࡗࡵࡰࠧἪ"))
        if bstack1lll1lllll_opy_:
            bstack1l1111l11_opy_(bstack1lll1lllll_opy_)
            if bstack1ll111111l_opy_() <= version.parse(bstack11l1ll1_opy_ (u"࠭࠳࠯࠳࠶࠲࠵࠭Ἣ")):
                self.command_executor._url = bstack11l1ll1_opy_ (u"ࠢࡩࡶࡷࡴ࠿࠵࠯ࠣἬ") + bstack1l1ll11ll1_opy_ + bstack11l1ll1_opy_ (u"ࠣ࠼࠻࠴࠴ࡽࡤ࠰ࡪࡸࡦࠧἭ")
            else:
                self.command_executor._url = bstack11l1ll1_opy_ (u"ࠤ࡫ࡸࡹࡶࡳ࠻࠱࠲ࠦἮ") + bstack1lll1lllll_opy_ + bstack11l1ll1_opy_ (u"ࠥ࠳ࡼࡪ࠯ࡩࡷࡥࠦἯ")
            logger.debug(bstack1ll1111l1_opy_.format(bstack1lll1lllll_opy_))
        else:
            logger.debug(bstack11l11ll1l_opy_.format(bstack11l1ll1_opy_ (u"ࠦࡔࡶࡴࡪ࡯ࡤࡰࠥࡎࡵࡣࠢࡱࡳࡹࠦࡦࡰࡷࡱࡨࠧἰ")))
    except Exception as e:
        logger.debug(bstack11l11ll1l_opy_.format(e))
    bstack1l1l1ll1_opy_ = self.session_id
    if bstack11l1ll1_opy_ (u"ࠬࡶࡹࡵࡧࡶࡸࠬἱ") in bstack111111ll1_opy_:
        threading.current_thread().bstackSessionId = self.session_id
        threading.current_thread().bstackSessionDriver = self
        threading.current_thread().bstackTestErrorMessages = []
        item = store.get(bstack11l1ll1_opy_ (u"࠭ࡣࡶࡴࡵࡩࡳࡺ࡟ࡵࡧࡶࡸࡤ࡯ࡴࡦ࡯ࠪἲ"), None)
        if item:
            bstack111lllll111_opy_ = getattr(item, bstack11l1ll1_opy_ (u"ࠧࡠࡶࡨࡷࡹࡥࡣࡢࡵࡨࡣࡸࡺࡡࡳࡶࡨࡨࠬἳ"), False)
            if not getattr(item, bstack11l1ll1_opy_ (u"ࠨࡡࡧࡶ࡮ࡼࡥࡳࠩἴ"), None) and bstack111lllll111_opy_:
                setattr(store[bstack11l1ll1_opy_ (u"ࠩࡦࡹࡷࡸࡥ࡯ࡶࡢࡸࡪࡹࡴࡠ࡫ࡷࡩࡲ࠭ἵ")], bstack11l1ll1_opy_ (u"ࠪࡣࡩࡸࡩࡷࡧࡵࠫἶ"), self)
        bstack1ll1l1l1l_opy_ = getattr(threading.current_thread(), bstack11l1ll1_opy_ (u"ࠫࡧࡹࡴࡢࡥ࡮ࡘࡪࡹࡴࡎࡧࡷࡥࠬἷ"), None)
        if bstack1ll1l1l1l_opy_ and bstack1ll1l1l1l_opy_.get(bstack11l1ll1_opy_ (u"ࠬࡹࡴࡢࡶࡸࡷࠬἸ"), bstack11l1ll1_opy_ (u"࠭ࠧἹ")) == bstack11l1ll1_opy_ (u"ࠧࡱࡧࡱࡨ࡮ࡴࡧࠨἺ"):
            bstack11111l1l1_opy_.bstack1111l11l1_opy_(self)
    bstack1l1ll1l1l1_opy_.append(self)
    if bstack11l1ll1_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶࠫἻ") in CONFIG and bstack11l1ll1_opy_ (u"ࠩࡶࡩࡸࡹࡩࡰࡰࡑࡥࡲ࡫ࠧἼ") in CONFIG[bstack11l1ll1_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱࡸ࠭Ἵ")][bstack1ll1lll1l_opy_]:
        bstack1lll1l11l_opy_ = CONFIG[bstack11l1ll1_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲࡹࠧἾ")][bstack1ll1lll1l_opy_][bstack11l1ll1_opy_ (u"ࠬࡹࡥࡴࡵ࡬ࡳࡳࡔࡡ࡮ࡧࠪἿ")]
    logger.debug(bstack1l1ll111l_opy_.format(bstack1l1l1ll1_opy_))
@measure(event_name=EVENTS.bstack11111ll11_opy_, stage=STAGE.bstack1l1ll1llll_opy_, bstack1l11l1ll_opy_=bstack1lll1l11l_opy_)
def bstack1l11lllll_opy_(self, url):
    global bstack1lllll11ll_opy_
    global CONFIG
    try:
        bstack1l1l111lll_opy_(url, CONFIG, logger)
    except Exception as err:
        logger.debug(bstack1111l1l1_opy_.format(str(err)))
    try:
        bstack1lllll11ll_opy_(self, url)
    except Exception as e:
        try:
            bstack1l111ll1ll_opy_ = str(e)
            if any(err_msg in bstack1l111ll1ll_opy_ for err_msg in bstack1llll111l_opy_):
                bstack1l1l111lll_opy_(url, CONFIG, logger, True)
        except Exception as err:
            logger.debug(bstack1111l1l1_opy_.format(str(err)))
        raise e
def bstack1111l11ll_opy_(item, when):
    global bstack1l1l111l1_opy_
    try:
        bstack1l1l111l1_opy_(item, when)
    except Exception as e:
        pass
def bstack1l1lll11l_opy_(item, call, rep):
    global bstack1lll1lll11_opy_
    global bstack1l1ll1l1l1_opy_
    name = bstack11l1ll1_opy_ (u"࠭ࠧὀ")
    try:
        if rep.when == bstack11l1ll1_opy_ (u"ࠧࡤࡣ࡯ࡰࠬὁ"):
            bstack1l1l1ll1_opy_ = threading.current_thread().bstackSessionId
            bstack111lll1l111_opy_ = item.config.getoption(bstack11l1ll1_opy_ (u"ࠨࡵ࡮࡭ࡵ࡙ࡥࡴࡵ࡬ࡳࡳࡔࡡ࡮ࡧࠪὂ"))
            try:
                if (str(bstack111lll1l111_opy_).lower() != bstack11l1ll1_opy_ (u"ࠩࡷࡶࡺ࡫ࠧὃ")):
                    name = str(rep.nodeid)
                    bstack1lll1lll1l_opy_ = bstack1lll111ll_opy_(bstack11l1ll1_opy_ (u"ࠪࡷࡪࡺࡓࡦࡵࡶ࡭ࡴࡴࡎࡢ࡯ࡨࠫὄ"), name, bstack11l1ll1_opy_ (u"ࠫࠬὅ"), bstack11l1ll1_opy_ (u"ࠬ࠭὆"), bstack11l1ll1_opy_ (u"࠭ࠧ὇"), bstack11l1ll1_opy_ (u"ࠧࠨὈ"))
                    os.environ[bstack11l1ll1_opy_ (u"ࠨࡒ࡜ࡘࡊ࡙ࡔࡠࡖࡈࡗ࡙ࡥࡎࡂࡏࡈࠫὉ")] = name
                    for driver in bstack1l1ll1l1l1_opy_:
                        if bstack1l1l1ll1_opy_ == driver.session_id:
                            driver.execute_script(bstack1lll1lll1l_opy_)
            except Exception as e:
                logger.debug(bstack11l1ll1_opy_ (u"ࠩࡈࡶࡷࡵࡲࠡ࡫ࡱࠤࡸ࡫ࡴࡵ࡫ࡱ࡫ࠥࡹࡥࡴࡵ࡬ࡳࡳࡔࡡ࡮ࡧࠣࡪࡴࡸࠠࡱࡻࡷࡩࡸࡺ࠭ࡣࡦࡧࠤࡸ࡫ࡳࡴ࡫ࡲࡲ࠿ࠦࡻࡾࠩὊ").format(str(e)))
            try:
                bstack11l1ll1l_opy_(rep.outcome.lower())
                if rep.outcome.lower() != bstack11l1ll1_opy_ (u"ࠪࡷࡰ࡯ࡰࡱࡧࡧࠫὋ"):
                    status = bstack11l1ll1_opy_ (u"ࠫ࡫ࡧࡩ࡭ࡧࡧࠫὌ") if rep.outcome.lower() == bstack11l1ll1_opy_ (u"ࠬ࡬ࡡࡪ࡮ࡨࡨࠬὍ") else bstack11l1ll1_opy_ (u"࠭ࡰࡢࡵࡶࡩࡩ࠭὎")
                    reason = bstack11l1ll1_opy_ (u"ࠧࠨ὏")
                    if status == bstack11l1ll1_opy_ (u"ࠨࡨࡤ࡭ࡱ࡫ࡤࠨὐ"):
                        reason = rep.longrepr.reprcrash.message
                        if (not threading.current_thread().bstackTestErrorMessages):
                            threading.current_thread().bstackTestErrorMessages = []
                        threading.current_thread().bstackTestErrorMessages.append(reason)
                    level = bstack11l1ll1_opy_ (u"ࠩ࡬ࡲ࡫ࡵࠧὑ") if status == bstack11l1ll1_opy_ (u"ࠪࡴࡦࡹࡳࡦࡦࠪὒ") else bstack11l1ll1_opy_ (u"ࠫࡪࡸࡲࡰࡴࠪὓ")
                    data = name + bstack11l1ll1_opy_ (u"ࠬࠦࡰࡢࡵࡶࡩࡩࠧࠧὔ") if status == bstack11l1ll1_opy_ (u"࠭ࡰࡢࡵࡶࡩࡩ࠭ὕ") else name + bstack11l1ll1_opy_ (u"ࠧࠡࡨࡤ࡭ࡱ࡫ࡤࠢࠢࠪὖ") + reason
                    bstack11l1ll1ll1_opy_ = bstack1lll111ll_opy_(bstack11l1ll1_opy_ (u"ࠨࡣࡱࡲࡴࡺࡡࡵࡧࠪὗ"), bstack11l1ll1_opy_ (u"ࠩࠪ὘"), bstack11l1ll1_opy_ (u"ࠪࠫὙ"), bstack11l1ll1_opy_ (u"ࠫࠬ὚"), level, data)
                    for driver in bstack1l1ll1l1l1_opy_:
                        if bstack1l1l1ll1_opy_ == driver.session_id:
                            driver.execute_script(bstack11l1ll1ll1_opy_)
            except Exception as e:
                logger.debug(bstack11l1ll1_opy_ (u"ࠬࡋࡲࡳࡱࡵࠤ࡮ࡴࠠࡴࡧࡷࡸ࡮ࡴࡧࠡࡵࡨࡷࡸ࡯࡯࡯ࠢࡦࡳࡳࡺࡥࡹࡶࠣࡪࡴࡸࠠࡱࡻࡷࡩࡸࡺ࠭ࡣࡦࡧࠤࡸ࡫ࡳࡴ࡫ࡲࡲ࠿ࠦࡻࡾࠩὛ").format(str(e)))
    except Exception as e:
        logger.debug(bstack11l1ll1_opy_ (u"࠭ࡅࡳࡴࡲࡶࠥ࡯࡮ࠡࡩࡨࡸࡹ࡯࡮ࡨࠢࡶࡸࡦࡺࡥࠡ࡫ࡱࠤࡵࡿࡴࡦࡵࡷ࠱ࡧࡪࡤࠡࡶࡨࡷࡹࠦࡳࡵࡣࡷࡹࡸࡀࠠࡼࡿࠪ὜").format(str(e)))
    bstack1lll1lll11_opy_(item, call, rep)
notset = Notset()
def bstack1ll11l1ll_opy_(self, name: str, default=notset, skip: bool = False):
    global bstack11l1lllll1_opy_
    if str(name).lower() == bstack11l1ll1_opy_ (u"ࠧࡥࡴ࡬ࡺࡪࡸࠧὝ"):
        return bstack11l1ll1_opy_ (u"ࠣࡄࡵࡳࡼࡹࡥࡳࡕࡷࡥࡨࡱࠢ὞")
    else:
        return bstack11l1lllll1_opy_(self, name, default, skip)
def bstack11lll1ll1l_opy_(self):
    global CONFIG
    global bstack1llll111ll_opy_
    try:
        proxy = bstack1l1ll1lll1_opy_(CONFIG)
        if proxy:
            if proxy.endswith(bstack11l1ll1_opy_ (u"ࠩ࠱ࡴࡦࡩࠧὟ")):
                proxies = bstack111l111ll_opy_(proxy, bstack1l11111l1_opy_())
                if len(proxies) > 0:
                    protocol, bstack1lll1l1l1l_opy_ = proxies.popitem()
                    if bstack11l1ll1_opy_ (u"ࠥ࠾࠴࠵ࠢὠ") in bstack1lll1l1l1l_opy_:
                        return bstack1lll1l1l1l_opy_
                    else:
                        return bstack11l1ll1_opy_ (u"ࠦ࡭ࡺࡴࡱ࠼࠲࠳ࠧὡ") + bstack1lll1l1l1l_opy_
            else:
                return proxy
    except Exception as e:
        logger.error(bstack11l1ll1_opy_ (u"ࠧࡋࡲࡳࡱࡵࠤ࡮ࡴࠠࡴࡧࡷࡸ࡮ࡴࡧࠡࡲࡵࡳࡽࡿࠠࡶࡴ࡯ࠤ࠿ࠦࡻࡾࠤὢ").format(str(e)))
    return bstack1llll111ll_opy_(self)
def bstack1l1ll1lll_opy_():
    return (bstack11l1ll1_opy_ (u"࠭ࡨࡵࡶࡳࡔࡷࡵࡸࡺࠩὣ") in CONFIG or bstack11l1ll1_opy_ (u"ࠧࡩࡶࡷࡴࡸࡖࡲࡰࡺࡼࠫὤ") in CONFIG) and bstack11l11lll_opy_() and bstack1ll111111l_opy_() >= version.parse(
        bstack11llll11_opy_)
def bstack1ll1ll1l1l_opy_(self,
               executablePath=None,
               channel=None,
               args=None,
               ignoreDefaultArgs=None,
               handleSIGINT=None,
               handleSIGTERM=None,
               handleSIGHUP=None,
               timeout=None,
               env=None,
               headless=None,
               devtools=None,
               proxy=None,
               downloadsPath=None,
               slowMo=None,
               tracesDir=None,
               chromiumSandbox=None,
               firefoxUserPrefs=None
               ):
    global CONFIG
    global bstack1lll1l11l_opy_
    global bstack11ll1ll1l1_opy_
    global bstack111111ll1_opy_
    CONFIG[bstack11l1ll1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࡓࡅࡍࠪὥ")] = str(bstack111111ll1_opy_) + str(__version__)
    bstack1ll1lll1l_opy_ = 0
    try:
        if bstack11ll1ll1l1_opy_ is True:
            bstack1ll1lll1l_opy_ = int(os.environ.get(bstack11l1ll1_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡒࡏࡅ࡙ࡌࡏࡓࡏࡢࡍࡓࡊࡅ࡙ࠩὦ")))
    except:
        bstack1ll1lll1l_opy_ = 0
    CONFIG[bstack11l1ll1_opy_ (u"ࠥ࡭ࡸࡖ࡬ࡢࡻࡺࡶ࡮࡭ࡨࡵࠤὧ")] = True
    bstack11l11ll1_opy_ = bstack1l11llll1l_opy_(CONFIG, bstack1ll1lll1l_opy_)
    logger.debug(bstack1llll11l1l_opy_.format(str(bstack11l11ll1_opy_)))
    if CONFIG.get(bstack11l1ll1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡏࡳࡨࡧ࡬ࠨὨ")):
        bstack11ll1lllll_opy_(bstack11l11ll1_opy_, bstack1ll1lll1ll_opy_)
    if bstack11l1ll1_opy_ (u"ࠬࡶ࡬ࡢࡶࡩࡳࡷࡳࡳࠨὩ") in CONFIG and bstack11l1ll1_opy_ (u"࠭ࡳࡦࡵࡶ࡭ࡴࡴࡎࡢ࡯ࡨࠫὪ") in CONFIG[bstack11l1ll1_opy_ (u"ࠧࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡵࠪὫ")][bstack1ll1lll1l_opy_]:
        bstack1lll1l11l_opy_ = CONFIG[bstack11l1ll1_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶࠫὬ")][bstack1ll1lll1l_opy_][bstack11l1ll1_opy_ (u"ࠩࡶࡩࡸࡹࡩࡰࡰࡑࡥࡲ࡫ࠧὭ")]
    import urllib
    import json
    if bstack11l1ll1_opy_ (u"ࠪࡸࡺࡸࡢࡰࡕࡦࡥࡱ࡫ࠧὮ") in CONFIG and str(CONFIG[bstack11l1ll1_opy_ (u"ࠫࡹࡻࡲࡣࡱࡖࡧࡦࡲࡥࠨὯ")]).lower() != bstack11l1ll1_opy_ (u"ࠬ࡬ࡡ࡭ࡵࡨࠫὰ"):
        bstack1l111lll1_opy_ = bstack11l11l11_opy_()
        bstack1l11111l_opy_ = bstack1l111lll1_opy_ + urllib.parse.quote(json.dumps(bstack11l11ll1_opy_))
    else:
        bstack1l11111l_opy_ = bstack11l1ll1_opy_ (u"࠭ࡷࡴࡵ࠽࠳࠴ࡩࡤࡱ࠰ࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡥࡲࡱ࠴ࡶ࡬ࡢࡻࡺࡶ࡮࡭ࡨࡵࡁࡦࡥࡵࡹ࠽ࠨά") + urllib.parse.quote(json.dumps(bstack11l11ll1_opy_))
    browser = self.connect(bstack1l11111l_opy_)
    return browser
def bstack11lll1l1ll_opy_():
    global bstack1111111ll_opy_
    global bstack111111ll1_opy_
    try:
        from playwright._impl._browser_type import BrowserType
        from bstack_utils.helper import bstack11lll1ll1_opy_
        if not bstack1ll1l1l11ll_opy_():
            global bstack1l1ll1l1_opy_
            if not bstack1l1ll1l1_opy_:
                from bstack_utils.helper import bstack1l1ll1l1l_opy_, bstack1l11lll111_opy_
                bstack1l1ll1l1_opy_ = bstack1l1ll1l1l_opy_()
                bstack1l11lll111_opy_(bstack111111ll1_opy_)
            BrowserType.connect = bstack11lll1ll1_opy_
            return
        BrowserType.launch = bstack1ll1ll1l1l_opy_
        bstack1111111ll_opy_ = True
    except Exception as e:
        pass
def bstack111llll11l1_opy_():
    global CONFIG
    global bstack11ll11ll1_opy_
    global bstack1l1ll11ll1_opy_
    global bstack1ll1lll1ll_opy_
    global bstack11ll1ll1l1_opy_
    global bstack1111llll_opy_
    CONFIG = json.loads(os.environ.get(bstack11l1ll1_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡃࡐࡐࡉࡍࡌ࠭ὲ")))
    bstack11ll11ll1_opy_ = eval(os.environ.get(bstack11l1ll1_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡊࡕࡢࡅࡕࡖ࡟ࡂࡗࡗࡓࡒࡇࡔࡆࠩέ")))
    bstack1l1ll11ll1_opy_ = os.environ.get(bstack11l1ll1_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡊࡘࡆࡤ࡛ࡒࡍࠩὴ"))
    bstack1ll11111ll_opy_(CONFIG, bstack11ll11ll1_opy_)
    bstack1111llll_opy_ = bstack1ll1ll111_opy_.bstack11l1ll111_opy_(CONFIG, bstack1111llll_opy_)
    if cli.bstack11ll1llll1_opy_():
        bstack1l1l11lll1_opy_.invoke(bstack1ll1ll1l11_opy_.CONNECT, bstack1llll11111_opy_())
        cli_context.platform_index = int(os.environ.get(bstack11l1ll1_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡓࡐࡆ࡚ࡆࡐࡔࡐࡣࡎࡔࡄࡆ࡚ࠪή"), bstack11l1ll1_opy_ (u"ࠫ࠵࠭ὶ")))
        cli.bstack1llllll1111_opy_(bstack1l11111l1_opy_(bstack1l1ll11ll1_opy_, CONFIG), cli_context.platform_index, bstack11l1ll1l1_opy_)
        cli.bstack1lllll111ll_opy_()
        logger.debug(bstack11l1ll1_opy_ (u"ࠧࡉࡌࡊࠢ࡬ࡷࠥࡧࡣࡵ࡫ࡹࡩࠥ࡬࡯ࡳࠢࡳࡰࡦࡺࡦࡰࡴࡰࡣ࡮ࡴࡤࡦࡺࡀࠦί") + str(cli_context.platform_index) + bstack11l1ll1_opy_ (u"ࠨࠢὸ"))
        return # skip all existing bstack111lll1l1ll_opy_
    global bstack11lll111ll_opy_
    global bstack1llll11l_opy_
    global bstack1lllll1l11_opy_
    global bstack11ll111l1l_opy_
    global bstack111lllll_opy_
    global bstack111ll1lll_opy_
    global bstack1l1llll1ll_opy_
    global bstack1lllll11ll_opy_
    global bstack1llll111ll_opy_
    global bstack11l1lllll1_opy_
    global bstack1l1l111l1_opy_
    global bstack1lll1lll11_opy_
    try:
        from selenium import webdriver
        from selenium.webdriver.remote.webdriver import WebDriver
        bstack11lll111ll_opy_ = webdriver.Remote.__init__
        bstack1llll11l_opy_ = WebDriver.quit
        bstack1l1llll1ll_opy_ = WebDriver.close
        bstack1lllll11ll_opy_ = WebDriver.get
    except Exception as e:
        pass
    if (bstack11l1ll1_opy_ (u"ࠧࡩࡶࡷࡴࡕࡸ࡯ࡹࡻࠪό") in CONFIG or bstack11l1ll1_opy_ (u"ࠨࡪࡷࡸࡵࡹࡐࡳࡱࡻࡽࠬὺ") in CONFIG) and bstack11l11lll_opy_():
        if bstack1ll111111l_opy_() < version.parse(bstack11llll11_opy_):
            logger.error(bstack11l1l111l_opy_.format(bstack1ll111111l_opy_()))
        else:
            try:
                from selenium.webdriver.remote.remote_connection import RemoteConnection
                bstack1llll111ll_opy_ = RemoteConnection._11ll1lll_opy_
            except Exception as e:
                logger.error(bstack11ll1l11l1_opy_.format(str(e)))
    try:
        from _pytest.config import Config
        bstack11l1lllll1_opy_ = Config.getoption
        from _pytest import runner
        bstack1l1l111l1_opy_ = runner._update_current_test_var
    except Exception as e:
        logger.warn(e, bstack1ll1l1l111_opy_)
    try:
        from pytest_bdd import reporting
        bstack1lll1lll11_opy_ = reporting.runtest_makereport
    except Exception as e:
        logger.debug(bstack11l1ll1_opy_ (u"ࠩࡓࡰࡪࡧࡳࡦࠢ࡬ࡲࡸࡺࡡ࡭࡮ࠣࡴࡾࡺࡥࡴࡶ࠰ࡦࡩࡪࠠࡵࡱࠣࡶࡺࡴࠠࡱࡻࡷࡩࡸࡺ࠭ࡣࡦࡧࠤࡹ࡫ࡳࡵࡵࠪύ"))
    bstack1ll1lll1ll_opy_ = CONFIG.get(bstack11l1ll1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡗࡹࡧࡣ࡬ࡎࡲࡧࡦࡲࡏࡱࡶ࡬ࡳࡳࡹࠧὼ"), {}).get(bstack11l1ll1_opy_ (u"ࠫࡱࡵࡣࡢ࡮ࡌࡨࡪࡴࡴࡪࡨ࡬ࡩࡷ࠭ώ"))
    bstack11ll1ll1l1_opy_ = True
    bstack1l1lll11_opy_(bstack1l11lll1_opy_)
if (bstack11lllll1lll_opy_()):
    bstack111llll11l1_opy_()
@bstack111llll1ll_opy_(class_method=False)
def bstack111lll11l1l_opy_(hook_name, event, bstack1l1l1ll11ll_opy_=None):
    if hook_name not in [bstack11l1ll1_opy_ (u"ࠬࡹࡥࡵࡷࡳࡣ࡫ࡻ࡮ࡤࡶ࡬ࡳࡳ࠭὾"), bstack11l1ll1_opy_ (u"࠭ࡴࡦࡣࡵࡨࡴࡽ࡮ࡠࡨࡸࡲࡨࡺࡩࡰࡰࠪ὿"), bstack11l1ll1_opy_ (u"ࠧࡴࡧࡷࡹࡵࡥ࡭ࡰࡦࡸࡰࡪ࠭ᾀ"), bstack11l1ll1_opy_ (u"ࠨࡶࡨࡥࡷࡪ࡯ࡸࡰࡢࡱࡴࡪࡵ࡭ࡧࠪᾁ"), bstack11l1ll1_opy_ (u"ࠩࡶࡩࡹࡻࡰࡠࡥ࡯ࡥࡸࡹࠧᾂ"), bstack11l1ll1_opy_ (u"ࠪࡸࡪࡧࡲࡥࡱࡺࡲࡤࡩ࡬ࡢࡵࡶࠫᾃ"), bstack11l1ll1_opy_ (u"ࠫࡸ࡫ࡴࡶࡲࡢࡱࡪࡺࡨࡰࡦࠪᾄ"), bstack11l1ll1_opy_ (u"ࠬࡺࡥࡢࡴࡧࡳࡼࡴ࡟࡮ࡧࡷ࡬ࡴࡪࠧᾅ")]:
        return
    node = store[bstack11l1ll1_opy_ (u"࠭ࡣࡶࡴࡵࡩࡳࡺ࡟ࡵࡧࡶࡸࡤ࡯ࡴࡦ࡯ࠪᾆ")]
    if hook_name in [bstack11l1ll1_opy_ (u"ࠧࡴࡧࡷࡹࡵࡥ࡭ࡰࡦࡸࡰࡪ࠭ᾇ"), bstack11l1ll1_opy_ (u"ࠨࡶࡨࡥࡷࡪ࡯ࡸࡰࡢࡱࡴࡪࡵ࡭ࡧࠪᾈ")]:
        node = store[bstack11l1ll1_opy_ (u"ࠩࡦࡹࡷࡸࡥ࡯ࡶࡢࡱࡴࡪࡵ࡭ࡧࡢ࡭ࡹ࡫࡭ࠨᾉ")]
    elif hook_name in [bstack11l1ll1_opy_ (u"ࠪࡷࡪࡺࡵࡱࡡࡦࡰࡦࡹࡳࠨᾊ"), bstack11l1ll1_opy_ (u"ࠫࡹ࡫ࡡࡳࡦࡲࡻࡳࡥࡣ࡭ࡣࡶࡷࠬᾋ")]:
        node = store[bstack11l1ll1_opy_ (u"ࠬࡩࡵࡳࡴࡨࡲࡹࡥࡣ࡭ࡣࡶࡷࡤ࡯ࡴࡦ࡯ࠪᾌ")]
    hook_type = bstack11l1l111lll_opy_(hook_name)
    if event == bstack11l1ll1_opy_ (u"࠭ࡢࡦࡨࡲࡶࡪ࠭ᾍ"):
        if cli.bstack11111lll11_opy_(bstack1llll1l1l11_opy_):
            cli.test_framework.track_event(cli_context, bstack1llll11llll_opy_[hook_type], bstack1lll1llll11_opy_.PRE, node, hook_name)
            return
        uuid = uuid4().__str__()
        bstack111ll1ll11_opy_ = {
            bstack11l1ll1_opy_ (u"ࠧࡶࡷ࡬ࡨࠬᾎ"): uuid,
            bstack11l1ll1_opy_ (u"ࠨࡵࡷࡥࡷࡺࡥࡥࡡࡤࡸࠬᾏ"): bstack1ll1l1ll_opy_(),
            bstack11l1ll1_opy_ (u"ࠩࡷࡽࡵ࡫ࠧᾐ"): bstack11l1ll1_opy_ (u"ࠪ࡬ࡴࡵ࡫ࠨᾑ"),
            bstack11l1ll1_opy_ (u"ࠫ࡭ࡵ࡯࡬ࡡࡷࡽࡵ࡫ࠧᾒ"): hook_type,
            bstack11l1ll1_opy_ (u"ࠬ࡮࡯ࡰ࡭ࡢࡲࡦࡳࡥࠨᾓ"): hook_name
        }
        store[bstack11l1ll1_opy_ (u"࠭ࡣࡶࡴࡵࡩࡳࡺ࡟ࡩࡱࡲ࡯ࡤࡻࡵࡪࡦࠪᾔ")].append(uuid)
        bstack111lll1ll11_opy_ = node.nodeid
        if hook_type == bstack11l1ll1_opy_ (u"ࠧࡃࡇࡉࡓࡗࡋ࡟ࡆࡃࡆࡌࠬᾕ"):
            if not _11l111l1ll_opy_.get(bstack111lll1ll11_opy_, None):
                _11l111l1ll_opy_[bstack111lll1ll11_opy_] = {bstack11l1ll1_opy_ (u"ࠨࡪࡲࡳࡰࡹࠧᾖ"): []}
            _11l111l1ll_opy_[bstack111lll1ll11_opy_][bstack11l1ll1_opy_ (u"ࠩ࡫ࡳࡴࡱࡳࠨᾗ")].append(bstack111ll1ll11_opy_[bstack11l1ll1_opy_ (u"ࠪࡹࡺ࡯ࡤࠨᾘ")])
        _11l111l1ll_opy_[bstack111lll1ll11_opy_ + bstack11l1ll1_opy_ (u"ࠫ࠲࠭ᾙ") + hook_name] = bstack111ll1ll11_opy_
        bstack111lll11lll_opy_(node, bstack111ll1ll11_opy_, bstack11l1ll1_opy_ (u"ࠬࡎ࡯ࡰ࡭ࡕࡹࡳ࡙ࡴࡢࡴࡷࡩࡩ࠭ᾚ"))
    elif event == bstack11l1ll1_opy_ (u"࠭ࡡࡧࡶࡨࡶࠬᾛ"):
        if cli.bstack11111lll11_opy_(bstack1llll1l1l11_opy_):
            cli.test_framework.track_event(cli_context, bstack1llll11llll_opy_[hook_type], bstack1lll1llll11_opy_.POST, node, None, bstack1l1l1ll11ll_opy_)
            return
        bstack11l1l1l1l1_opy_ = node.nodeid + bstack11l1ll1_opy_ (u"ࠧ࠮ࠩᾜ") + hook_name
        _11l111l1ll_opy_[bstack11l1l1l1l1_opy_][bstack11l1ll1_opy_ (u"ࠨࡨ࡬ࡲ࡮ࡹࡨࡦࡦࡢࡥࡹ࠭ᾝ")] = bstack1ll1l1ll_opy_()
        bstack111lll111l1_opy_(_11l111l1ll_opy_[bstack11l1l1l1l1_opy_][bstack11l1ll1_opy_ (u"ࠩࡸࡹ࡮ࡪࠧᾞ")])
        bstack111lll11lll_opy_(node, _11l111l1ll_opy_[bstack11l1l1l1l1_opy_], bstack11l1ll1_opy_ (u"ࠪࡌࡴࡵ࡫ࡓࡷࡱࡊ࡮ࡴࡩࡴࡪࡨࡨࠬᾟ"), bstack111lll11111_opy_=bstack1l1l1ll11ll_opy_)
def bstack111llll1l1l_opy_():
    global bstack111lllll1ll_opy_
    if bstack1l11ll1l1_opy_():
        bstack111lllll1ll_opy_ = bstack11l1ll1_opy_ (u"ࠫࡵࡿࡴࡦࡵࡷ࠱ࡧࡪࡤࠨᾠ")
    else:
        bstack111lllll1ll_opy_ = bstack11l1ll1_opy_ (u"ࠬࡶࡹࡵࡧࡶࡸࠬᾡ")
@bstack11111l1l1_opy_.bstack11l1111l1l1_opy_
def bstack111lll11l11_opy_():
    bstack111llll1l1l_opy_()
    if cli.bstack11111lll11_opy_(bstack1llll1l1l11_opy_):
        try:
            bstack11lll11111l_opy_(bstack111lll11l1l_opy_)
        except Exception as e:
            logger.debug(bstack11l1ll1_opy_ (u"ࠨࡅࡹࡥࡨࡴࡹ࡯࡯࡯ࠢ࡬ࡲࠥ࡮࡯ࡰ࡭ࡶࠤࡵࡧࡴࡤࡪ࠽ࠤࢀࢃࠢᾢ").format(e))
        return
    if bstack11l11lll_opy_():
        bstack1ll1l11l1_opy_ = Config.bstack1l111l1ll1_opy_()
        bstack11l1ll1_opy_ (u"ࠧࠨࠩࠍࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࡈࡲࡶࠥࡶࡰࡱࠢࡀࠤ࠶࠲ࠠ࡮ࡱࡧࡣࡪࡾࡥࡤࡷࡷࡩࠥ࡭ࡥࡵࡵࠣࡹࡸ࡫ࡤࠡࡨࡲࡶࠥࡧ࠱࠲ࡻࠣࡧࡴࡳ࡭ࡢࡰࡧࡷ࠲ࡽࡲࡢࡲࡳ࡭ࡳ࡭ࠊࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࡌ࡯ࡳࠢࡳࡴࡵࠦ࠾ࠡ࠳࠯ࠤࡲࡵࡤࡠࡧࡻࡩࡨࡻࡴࡦࠢࡧࡳࡪࡹࠠ࡯ࡱࡷࠤࡷࡻ࡮ࠡࡤࡨࡧࡦࡻࡳࡦࠢ࡬ࡸࠥ࡯ࡳࠡࡲࡤࡸࡨ࡮ࡥࡥࠢ࡬ࡲࠥࡧࠠࡥ࡫ࡩࡪࡪࡸࡥ࡯ࡶࠣࡴࡷࡵࡣࡦࡵࡶࠤ࡮ࡪࠊࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤ࡚ࠥࡨࡶࡵࠣࡻࡪࠦ࡮ࡦࡧࡧࠤࡹࡵࠠࡶࡵࡨࠤࡘ࡫࡬ࡦࡰ࡬ࡹࡲࡖࡡࡵࡥ࡫ࠬࡸ࡫࡬ࡦࡰ࡬ࡹࡲࡥࡨࡢࡰࡧࡰࡪࡸࠩࠡࡨࡲࡶࠥࡶࡰࡱࠢࡁࠤ࠶ࠐࠠࠡࠢࠣࠤࠥࠦࠠࠨࠩࠪᾣ")
        if bstack1ll1l11l1_opy_.get_property(bstack11l1ll1_opy_ (u"ࠨࡤࡶࡸࡦࡩ࡫ࡠ࡯ࡲࡨࡤࡩࡡ࡭࡮ࡨࡨࠬᾤ")):
            if CONFIG.get(bstack11l1ll1_opy_ (u"ࠩࡳࡥࡷࡧ࡬࡭ࡧ࡯ࡷࡕ࡫ࡲࡑ࡮ࡤࡸ࡫ࡵࡲ࡮ࠩᾥ")) is not None and int(CONFIG[bstack11l1ll1_opy_ (u"ࠪࡴࡦࡸࡡ࡭࡮ࡨࡰࡸࡖࡥࡳࡒ࡯ࡥࡹ࡬࡯ࡳ࡯ࠪᾦ")]) > 1:
                bstack1l111111ll_opy_(bstack1l1ll1111_opy_)
            return
        bstack1l111111ll_opy_(bstack1l1ll1111_opy_)
    try:
        bstack11lll11111l_opy_(bstack111lll11l1l_opy_)
    except Exception as e:
        logger.debug(bstack11l1ll1_opy_ (u"ࠦࡊࡾࡣࡦࡲࡷ࡭ࡴࡴࠠࡪࡰࠣ࡬ࡴࡵ࡫ࡴࠢࡳࡥࡹࡩࡨ࠻ࠢࡾࢁࠧᾧ").format(e))
bstack111lll11l11_opy_()