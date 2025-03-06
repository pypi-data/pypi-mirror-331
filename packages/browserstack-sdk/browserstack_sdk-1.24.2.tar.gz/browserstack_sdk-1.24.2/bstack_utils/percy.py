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
import re
import sys
import json
import time
import shutil
import tempfile
import requests
import subprocess
from threading import Thread
from os.path import expanduser
from bstack_utils.constants import *
from requests.auth import HTTPBasicAuth
from bstack_utils.helper import bstack1llll1ll11_opy_, bstack1l1111l1l_opy_
from bstack_utils.measure import measure
class bstack111l1l11l_opy_:
  working_dir = os.getcwd()
  bstack1lll111l1l_opy_ = False
  config = {}
  binary_path = bstack11l1ll1_opy_ (u"ࠩࠪ᫪")
  bstack11l1llllll1_opy_ = bstack11l1ll1_opy_ (u"ࠪࠫ᫫")
  bstack111ll11ll_opy_ = False
  bstack11ll11l1111_opy_ = None
  bstack11ll11l1lll_opy_ = {}
  bstack11ll1111ll1_opy_ = 300
  bstack11ll111l1l1_opy_ = False
  logger = None
  bstack11ll11ll111_opy_ = False
  bstack11lllll1_opy_ = False
  percy_build_id = None
  bstack11l1ll1ll1l_opy_ = bstack11l1ll1_opy_ (u"ࠫࠬ᫬")
  bstack11l1ll1lll1_opy_ = {
    bstack11l1ll1_opy_ (u"ࠬࡩࡨࡳࡱࡰࡩࠬ᫭") : 1,
    bstack11l1ll1_opy_ (u"࠭ࡦࡪࡴࡨࡪࡴࡾࠧ᫮") : 2,
    bstack11l1ll1_opy_ (u"ࠧࡦࡦࡪࡩࠬ᫯") : 3,
    bstack11l1ll1_opy_ (u"ࠨࡵࡤࡪࡦࡸࡩࠨ᫰") : 4
  }
  def __init__(self) -> None: pass
  def bstack11l1lll11l1_opy_(self):
    bstack11ll1l11111_opy_ = bstack11l1ll1_opy_ (u"ࠩࠪ᫱")
    bstack11ll11l111l_opy_ = sys.platform
    bstack11l1llll1l1_opy_ = bstack11l1ll1_opy_ (u"ࠪࡴࡪࡸࡣࡺࠩ᫲")
    if re.match(bstack11l1ll1_opy_ (u"ࠦࡩࡧࡲࡸ࡫ࡱࢀࡲࡧࡣࠡࡱࡶࠦ᫳"), bstack11ll11l111l_opy_) != None:
      bstack11ll1l11111_opy_ = bstack1l111ll111l_opy_ + bstack11l1ll1_opy_ (u"ࠧ࠵ࡰࡦࡴࡦࡽ࠲ࡵࡳࡹ࠰ࡽ࡭ࡵࠨ᫴")
      self.bstack11l1ll1ll1l_opy_ = bstack11l1ll1_opy_ (u"࠭࡭ࡢࡥࠪ᫵")
    elif re.match(bstack11l1ll1_opy_ (u"ࠢ࡮ࡵࡺ࡭ࡳࢂ࡭ࡴࡻࡶࢀࡲ࡯࡮ࡨࡹࡿࡧࡾ࡭ࡷࡪࡰࡿࡦࡨࡩࡷࡪࡰࡿࡻ࡮ࡴࡣࡦࡾࡨࡱࡨࢂࡷࡪࡰ࠶࠶ࠧ᫶"), bstack11ll11l111l_opy_) != None:
      bstack11ll1l11111_opy_ = bstack1l111ll111l_opy_ + bstack11l1ll1_opy_ (u"ࠣ࠱ࡳࡩࡷࡩࡹ࠮ࡹ࡬ࡲ࠳ࢀࡩࡱࠤ᫷")
      bstack11l1llll1l1_opy_ = bstack11l1ll1_opy_ (u"ࠤࡳࡩࡷࡩࡹ࠯ࡧࡻࡩࠧ᫸")
      self.bstack11l1ll1ll1l_opy_ = bstack11l1ll1_opy_ (u"ࠪࡻ࡮ࡴࠧ᫹")
    else:
      bstack11ll1l11111_opy_ = bstack1l111ll111l_opy_ + bstack11l1ll1_opy_ (u"ࠦ࠴ࡶࡥࡳࡥࡼ࠱ࡱ࡯࡮ࡶࡺ࠱ࡾ࡮ࡶࠢ᫺")
      self.bstack11l1ll1ll1l_opy_ = bstack11l1ll1_opy_ (u"ࠬࡲࡩ࡯ࡷࡻࠫ᫻")
    return bstack11ll1l11111_opy_, bstack11l1llll1l1_opy_
  def bstack11ll11ll1ll_opy_(self):
    try:
      bstack11ll111llll_opy_ = [os.path.join(expanduser(bstack11l1ll1_opy_ (u"ࠨࡾࠣ᫼")), bstack11l1ll1_opy_ (u"ࠧ࠯ࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࠧ᫽")), self.working_dir, tempfile.gettempdir()]
      for path in bstack11ll111llll_opy_:
        if(self.bstack11ll11l1l11_opy_(path)):
          return path
      raise bstack11l1ll1_opy_ (u"ࠣࡗࡱࡥࡱࡨࡥࠡࡶࡲࠤࡩࡵࡷ࡯࡮ࡲࡥࡩࠦࡰࡦࡴࡦࡽࠥࡨࡩ࡯ࡣࡵࡽࠧ᫾")
    except Exception as e:
      self.logger.error(bstack11l1ll1_opy_ (u"ࠤࡉࡥ࡮ࡲࡥࡥࠢࡷࡳࠥ࡬ࡩ࡯ࡦࠣࡥࡻࡧࡩ࡭ࡣࡥࡰࡪࠦࡰࡢࡶ࡫ࠤ࡫ࡵࡲࠡࡲࡨࡶࡨࡿࠠࡥࡱࡺࡲࡱࡵࡡࡥ࠮ࠣࡉࡽࡩࡥࡱࡶ࡬ࡳࡳࠦ࠭ࠡࡽࢀࠦ᫿").format(e))
  def bstack11ll11l1l11_opy_(self, path):
    try:
      if not os.path.exists(path):
        os.makedirs(path)
      return True
    except:
      return False
  @measure(event_name=EVENTS.bstack1l111llll1l_opy_, stage=STAGE.bstack1l1ll1llll_opy_)
  def bstack11ll11ll11l_opy_(self, bstack11ll1l11111_opy_, bstack11l1llll1l1_opy_):
    try:
      bstack11ll11l11l1_opy_ = self.bstack11ll11ll1ll_opy_()
      bstack11ll11lllll_opy_ = os.path.join(bstack11ll11l11l1_opy_, bstack11l1ll1_opy_ (u"ࠪࡴࡪࡸࡣࡺ࠰ࡽ࡭ࡵ࠭ᬀ"))
      bstack11ll1111lll_opy_ = os.path.join(bstack11ll11l11l1_opy_, bstack11l1llll1l1_opy_)
      if os.path.exists(bstack11ll1111lll_opy_):
        self.logger.info(bstack11l1ll1_opy_ (u"ࠦࡕ࡫ࡲࡤࡻࠣࡦ࡮ࡴࡡࡳࡻࠣࡪࡴࡻ࡮ࡥࠢ࡬ࡲࠥࢁࡽ࠭ࠢࡶ࡯࡮ࡶࡰࡪࡰࡪࠤࡩࡵࡷ࡯࡮ࡲࡥࡩࠨᬁ").format(bstack11ll1111lll_opy_))
        return bstack11ll1111lll_opy_
      if os.path.exists(bstack11ll11lllll_opy_):
        self.logger.info(bstack11l1ll1_opy_ (u"ࠧࡖࡥࡳࡥࡼࠤࡿ࡯ࡰࠡࡨࡲࡹࡳࡪࠠࡪࡰࠣࡿࢂ࠲ࠠࡶࡰࡽ࡭ࡵࡶࡩ࡯ࡩࠥᬂ").format(bstack11ll11lllll_opy_))
        return self.bstack11ll111ll11_opy_(bstack11ll11lllll_opy_, bstack11l1llll1l1_opy_)
      self.logger.info(bstack11l1ll1_opy_ (u"ࠨࡄࡰࡹࡱࡰࡴࡧࡤࡪࡰࡪࠤࡵ࡫ࡲࡤࡻࠣࡦ࡮ࡴࡡࡳࡻࠣࡪࡷࡵ࡭ࠡࡽࢀࠦᬃ").format(bstack11ll1l11111_opy_))
      response = bstack1l1111l1l_opy_(bstack11l1ll1_opy_ (u"ࠧࡈࡇࡗࠫᬄ"), bstack11ll1l11111_opy_, {}, {})
      if response.status_code == 200:
        with open(bstack11ll11lllll_opy_, bstack11l1ll1_opy_ (u"ࠨࡹࡥࠫᬅ")) as file:
          file.write(response.content)
        self.logger.info(bstack11l1ll1_opy_ (u"ࠤࡇࡳࡼࡴ࡬ࡰࡣࡧࡩࡩࠦࡰࡦࡴࡦࡽࠥࡨࡩ࡯ࡣࡵࡽࠥࡧ࡮ࡥࠢࡶࡥࡻ࡫ࡤࠡࡣࡷࠤࢀࢃࠢᬆ").format(bstack11ll11lllll_opy_))
        return self.bstack11ll111ll11_opy_(bstack11ll11lllll_opy_, bstack11l1llll1l1_opy_)
      else:
        raise(bstack11l1ll1_opy_ (u"ࠥࡊࡦ࡯࡬ࡦࡦࠣࡸࡴࠦࡤࡰࡹࡱࡰࡴࡧࡤࠡࡶ࡫ࡩࠥ࡬ࡩ࡭ࡧ࠱ࠤࡘࡺࡡࡵࡷࡶࠤࡨࡵࡤࡦ࠼ࠣࡿࢂࠨᬇ").format(response.status_code))
    except Exception as e:
      self.logger.error(bstack11l1ll1_opy_ (u"࡚ࠦࡴࡡࡣ࡮ࡨࠤࡹࡵࠠࡥࡱࡺࡲࡱࡵࡡࡥࠢࡳࡩࡷࡩࡹࠡࡤ࡬ࡲࡦࡸࡹ࠻ࠢࡾࢁࠧᬈ").format(e))
  def bstack11l1llll1ll_opy_(self, bstack11ll1l11111_opy_, bstack11l1llll1l1_opy_):
    try:
      retry = 2
      bstack11ll1111lll_opy_ = None
      bstack11l1lll1111_opy_ = False
      while retry > 0:
        bstack11ll1111lll_opy_ = self.bstack11ll11ll11l_opy_(bstack11ll1l11111_opy_, bstack11l1llll1l1_opy_)
        bstack11l1lll1111_opy_ = self.bstack11ll111lll1_opy_(bstack11ll1l11111_opy_, bstack11l1llll1l1_opy_, bstack11ll1111lll_opy_)
        if bstack11l1lll1111_opy_:
          break
        retry -= 1
      return bstack11ll1111lll_opy_, bstack11l1lll1111_opy_
    except Exception as e:
      self.logger.error(bstack11l1ll1_opy_ (u"࡛ࠧ࡮ࡢࡤ࡯ࡩࠥࡺ࡯ࠡࡩࡨࡸࠥࡶࡥࡳࡥࡼࠤࡧ࡯࡮ࡢࡴࡼࠤࡵࡧࡴࡩࠤᬉ").format(e))
    return bstack11ll1111lll_opy_, False
  def bstack11ll111lll1_opy_(self, bstack11ll1l11111_opy_, bstack11l1llll1l1_opy_, bstack11ll1111lll_opy_, bstack11l1lllllll_opy_ = 0):
    if bstack11l1lllllll_opy_ > 1:
      return False
    if bstack11ll1111lll_opy_ == None or os.path.exists(bstack11ll1111lll_opy_) == False:
      self.logger.warn(bstack11l1ll1_opy_ (u"ࠨࡐࡦࡴࡦࡽࠥࡶࡡࡵࡪࠣࡲࡴࡺࠠࡧࡱࡸࡲࡩ࠲ࠠࡳࡧࡷࡶࡾ࡯࡮ࡨࠢࡧࡳࡼࡴ࡬ࡰࡣࡧࠦᬊ"))
      return False
    bstack11l1llll111_opy_ = bstack11l1ll1_opy_ (u"ࠢ࡟࠰࠭ࡄࡵ࡫ࡲࡤࡻ࡟࠳ࡨࡲࡩࠡ࡞ࡧ࠲ࡡࡪࠫ࠯࡞ࡧ࠯ࠧᬋ")
    command = bstack11l1ll1_opy_ (u"ࠨࡽࢀࠤ࠲࠳ࡶࡦࡴࡶ࡭ࡴࡴࠧᬌ").format(bstack11ll1111lll_opy_)
    bstack11ll11l11ll_opy_ = subprocess.check_output(command, shell=True, text=True)
    if re.match(bstack11l1llll111_opy_, bstack11ll11l11ll_opy_) != None:
      return True
    else:
      self.logger.error(bstack11l1ll1_opy_ (u"ࠤࡓࡩࡷࡩࡹࠡࡸࡨࡶࡸ࡯࡯࡯ࠢࡦ࡬ࡪࡩ࡫ࠡࡨࡤ࡭ࡱ࡫ࡤࠣᬍ"))
      return False
  def bstack11ll111ll11_opy_(self, bstack11ll11lllll_opy_, bstack11l1llll1l1_opy_):
    try:
      working_dir = os.path.dirname(bstack11ll11lllll_opy_)
      shutil.unpack_archive(bstack11ll11lllll_opy_, working_dir)
      bstack11ll1111lll_opy_ = os.path.join(working_dir, bstack11l1llll1l1_opy_)
      os.chmod(bstack11ll1111lll_opy_, 0o755)
      return bstack11ll1111lll_opy_
    except Exception as e:
      self.logger.error(bstack11l1ll1_opy_ (u"࡙ࠥࡳࡧࡢ࡭ࡧࠣࡸࡴࠦࡵ࡯ࡼ࡬ࡴࠥࡶࡥࡳࡥࡼࠤࡧ࡯࡮ࡢࡴࡼࠦᬎ"))
  def bstack11ll111l111_opy_(self):
    try:
      bstack11l1ll1ll11_opy_ = self.config.get(bstack11l1ll1_opy_ (u"ࠫࡵ࡫ࡲࡤࡻࠪᬏ"))
      bstack11ll111l111_opy_ = bstack11l1ll1ll11_opy_ or (bstack11l1ll1ll11_opy_ is None and self.bstack1lll111l1l_opy_)
      if not bstack11ll111l111_opy_ or self.config.get(bstack11l1ll1_opy_ (u"ࠬ࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫ࠨᬐ"), None) not in bstack1l11l11l1ll_opy_:
        return False
      self.bstack111ll11ll_opy_ = True
      return True
    except Exception as e:
      self.logger.error(bstack11l1ll1_opy_ (u"ࠨࡕ࡯ࡣࡥࡰࡪࠦࡴࡰࠢࡧࡩࡹ࡫ࡣࡵࠢࡳࡩࡷࡩࡹ࠭ࠢࡈࡼࡨ࡫ࡰࡵ࡫ࡲࡲࠥࢁࡽࠣᬑ").format(e))
  def bstack11ll11lll1l_opy_(self):
    try:
      bstack11ll11lll1l_opy_ = self.percy_capture_mode
      return bstack11ll11lll1l_opy_
    except Exception as e:
      self.logger.error(bstack11l1ll1_opy_ (u"ࠢࡖࡰࡤࡦࡱ࡫ࠠࡵࡱࠣࡨࡪࡺࡥࡤࡶࠣࡴࡪࡸࡣࡺࠢࡦࡥࡵࡺࡵࡳࡧࠣࡱࡴࡪࡥ࠭ࠢࡈࡼࡨ࡫ࡰࡵ࡫ࡲࡲࠥࢁࡽࠣᬒ").format(e))
  def init(self, bstack1lll111l1l_opy_, config, logger):
    self.bstack1lll111l1l_opy_ = bstack1lll111l1l_opy_
    self.config = config
    self.logger = logger
    if not self.bstack11ll111l111_opy_():
      return
    self.bstack11ll11l1lll_opy_ = config.get(bstack11l1ll1_opy_ (u"ࠨࡲࡨࡶࡨࡿࡏࡱࡶ࡬ࡳࡳࡹࠧᬓ"), {})
    self.percy_capture_mode = config.get(bstack11l1ll1_opy_ (u"ࠩࡳࡩࡷࡩࡹࡄࡣࡳࡸࡺࡸࡥࡎࡱࡧࡩࠬᬔ"))
    try:
      bstack11ll1l11111_opy_, bstack11l1llll1l1_opy_ = self.bstack11l1lll11l1_opy_()
      bstack11ll1111lll_opy_, bstack11l1lll1111_opy_ = self.bstack11l1llll1ll_opy_(bstack11ll1l11111_opy_, bstack11l1llll1l1_opy_)
      if bstack11l1lll1111_opy_:
        self.binary_path = bstack11ll1111lll_opy_
        thread = Thread(target=self.bstack11ll111l1ll_opy_)
        thread.start()
      else:
        self.bstack11ll11ll111_opy_ = True
        self.logger.error(bstack11l1ll1_opy_ (u"ࠥࡍࡳࡼࡡ࡭࡫ࡧࠤࡵ࡫ࡲࡤࡻࠣࡴࡦࡺࡨࠡࡨࡲࡹࡳࡪࠠ࠮ࠢࡾࢁ࠱ࠦࡕ࡯ࡣࡥࡰࡪࠦࡴࡰࠢࡶࡸࡦࡸࡴࠡࡒࡨࡶࡨࡿࠢᬕ").format(bstack11ll1111lll_opy_))
    except Exception as e:
      self.logger.error(bstack11l1ll1_opy_ (u"࡚ࠦࡴࡡࡣ࡮ࡨࠤࡹࡵࠠࡴࡶࡤࡶࡹࠦࡰࡦࡴࡦࡽ࠱ࠦࡅࡹࡥࡨࡴࡹ࡯࡯࡯ࠢࡾࢁࠧᬖ").format(e))
  def bstack11ll11l1ll1_opy_(self):
    try:
      logfile = os.path.join(self.working_dir, bstack11l1ll1_opy_ (u"ࠬࡲ࡯ࡨࠩᬗ"), bstack11l1ll1_opy_ (u"࠭ࡰࡦࡴࡦࡽ࠳ࡲ࡯ࡨࠩᬘ"))
      os.makedirs(os.path.dirname(logfile)) if not os.path.exists(os.path.dirname(logfile)) else None
      self.logger.debug(bstack11l1ll1_opy_ (u"ࠢࡑࡷࡶ࡬࡮ࡴࡧࠡࡲࡨࡶࡨࡿࠠ࡭ࡱࡪࡷࠥࡧࡴࠡࡽࢀࠦᬙ").format(logfile))
      self.bstack11l1llllll1_opy_ = logfile
    except Exception as e:
      self.logger.error(bstack11l1ll1_opy_ (u"ࠣࡗࡱࡥࡧࡲࡥࠡࡶࡲࠤࡸ࡫ࡴࠡࡲࡨࡶࡨࡿࠠ࡭ࡱࡪࠤࡵࡧࡴࡩ࠮ࠣࡉࡽࡩࡥࡱࡶ࡬ࡳࡳࠦࡻࡾࠤᬚ").format(e))
  @measure(event_name=EVENTS.bstack1l111ll1ll1_opy_, stage=STAGE.bstack1l1ll1llll_opy_)
  def bstack11ll111l1ll_opy_(self):
    bstack11l1lll1ll1_opy_ = self.bstack11ll111l11l_opy_()
    if bstack11l1lll1ll1_opy_ == None:
      self.bstack11ll11ll111_opy_ = True
      self.logger.error(bstack11l1ll1_opy_ (u"ࠤࡓࡩࡷࡩࡹࠡࡶࡲ࡯ࡪࡴࠠ࡯ࡱࡷࠤ࡫ࡵࡵ࡯ࡦ࠯ࠤࡋࡧࡩ࡭ࡧࡧࠤࡹࡵࠠࡴࡶࡤࡶࡹࠦࡰࡦࡴࡦࡽࠧᬛ"))
      return False
    command_args = [bstack11l1ll1_opy_ (u"ࠥࡥࡵࡶ࠺ࡦࡺࡨࡧ࠿ࡹࡴࡢࡴࡷࠦᬜ") if self.bstack1lll111l1l_opy_ else bstack11l1ll1_opy_ (u"ࠫࡪࡾࡥࡤ࠼ࡶࡸࡦࡸࡴࠨᬝ")]
    bstack11ll1lll111_opy_ = self.bstack11l1ll1llll_opy_()
    if bstack11ll1lll111_opy_ != None:
      command_args.append(bstack11l1ll1_opy_ (u"ࠧ࠳ࡣࠡࡽࢀࠦᬞ").format(bstack11ll1lll111_opy_))
    env = os.environ.copy()
    env[bstack11l1ll1_opy_ (u"ࠨࡐࡆࡔࡆ࡝ࡤ࡚ࡏࡌࡇࡑࠦᬟ")] = bstack11l1lll1ll1_opy_
    env[bstack11l1ll1_opy_ (u"ࠢࡕࡊࡢࡆ࡚ࡏࡌࡅࡡࡘ࡙ࡎࡊࠢᬠ")] = os.environ.get(bstack11l1ll1_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡕࡇࡖࡘࡍ࡛ࡂࡠࡗࡘࡍࡉ࠭ᬡ"), bstack11l1ll1_opy_ (u"ࠩࠪᬢ"))
    bstack11l1lllll11_opy_ = [self.binary_path]
    self.bstack11ll11l1ll1_opy_()
    self.bstack11ll11l1111_opy_ = self.bstack11l1lll111l_opy_(bstack11l1lllll11_opy_ + command_args, env)
    self.logger.debug(bstack11l1ll1_opy_ (u"ࠥࡗࡹࡧࡲࡵ࡫ࡱ࡫ࠥࡎࡥࡢ࡮ࡷ࡬ࠥࡉࡨࡦࡥ࡮ࠦᬣ"))
    bstack11l1lllllll_opy_ = 0
    while self.bstack11ll11l1111_opy_.poll() == None:
      bstack11ll1111l1l_opy_ = self.bstack11ll111111l_opy_()
      if bstack11ll1111l1l_opy_:
        self.logger.debug(bstack11l1ll1_opy_ (u"ࠦࡍ࡫ࡡ࡭ࡶ࡫ࠤࡈ࡮ࡥࡤ࡭ࠣࡷࡺࡩࡣࡦࡵࡶࡪࡺࡲࠢᬤ"))
        self.bstack11ll111l1l1_opy_ = True
        return True
      bstack11l1lllllll_opy_ += 1
      self.logger.debug(bstack11l1ll1_opy_ (u"ࠧࡎࡥࡢ࡮ࡷ࡬ࠥࡉࡨࡦࡥ࡮ࠤࡗ࡫ࡴࡳࡻࠣ࠱ࠥࢁࡽࠣᬥ").format(bstack11l1lllllll_opy_))
      time.sleep(2)
    self.logger.error(bstack11l1ll1_opy_ (u"ࠨࡆࡢ࡫࡯ࡩࡩࠦࡴࡰࠢࡶࡸࡦࡸࡴࠡࡲࡨࡶࡨࡿࠬࠡࡊࡨࡥࡱࡺࡨࠡࡅ࡫ࡩࡨࡱࠠࡇࡣ࡬ࡰࡪࡪࠠࡢࡨࡷࡩࡷࠦࡻࡾࠢࡤࡸࡹ࡫࡭ࡱࡶࡶࠦᬦ").format(bstack11l1lllllll_opy_))
    self.bstack11ll11ll111_opy_ = True
    return False
  def bstack11ll111111l_opy_(self, bstack11l1lllllll_opy_ = 0):
    if bstack11l1lllllll_opy_ > 10:
      return False
    try:
      bstack11ll1111l11_opy_ = os.environ.get(bstack11l1ll1_opy_ (u"ࠧࡑࡇࡕࡇ࡞ࡥࡓࡆࡔ࡙ࡉࡗࡥࡁࡅࡆࡕࡉࡘ࡙ࠧᬧ"), bstack11l1ll1_opy_ (u"ࠨࡪࡷࡸࡵࡀ࠯࠰࡮ࡲࡧࡦࡲࡨࡰࡵࡷ࠾࠺࠹࠳࠹ࠩᬨ"))
      bstack11l1lll1l1l_opy_ = bstack11ll1111l11_opy_ + bstack1l11l1l1111_opy_
      response = requests.get(bstack11l1lll1l1l_opy_)
      data = response.json()
      self.percy_build_id = data.get(bstack11l1ll1_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࠨᬩ"), {}).get(bstack11l1ll1_opy_ (u"ࠪ࡭ࡩ࠭ᬪ"), None)
      return True
    except:
      self.logger.debug(bstack11l1ll1_opy_ (u"ࠦࡊࡸࡲࡰࡴࠣࡳࡨࡩࡵࡳࡴࡨࡨࠥࡽࡨࡪ࡮ࡨࠤࡵࡸ࡯ࡤࡧࡶࡷ࡮ࡴࡧࠡࡪࡨࡥࡱࡺࡨࠡࡥ࡫ࡩࡨࡱࠠࡳࡧࡶࡴࡴࡴࡳࡦࠤᬫ"))
      return False
  def bstack11ll111l11l_opy_(self):
    bstack11ll11111l1_opy_ = bstack11l1ll1_opy_ (u"ࠬࡧࡰࡱࠩᬬ") if self.bstack1lll111l1l_opy_ else bstack11l1ll1_opy_ (u"࠭ࡡࡶࡶࡲࡱࡦࡺࡥࠨᬭ")
    bstack11l1llll11l_opy_ = bstack11l1ll1_opy_ (u"ࠢࡶࡰࡧࡩ࡫࡯࡮ࡦࡦࠥᬮ") if self.config.get(bstack11l1ll1_opy_ (u"ࠨࡲࡨࡶࡨࡿࠧᬯ")) is None else True
    bstack11lllll1l1l_opy_ = bstack11l1ll1_opy_ (u"ࠤࡤࡴ࡮࠵ࡡࡱࡲࡢࡴࡪࡸࡣࡺ࠱ࡪࡩࡹࡥࡰࡳࡱ࡭ࡩࡨࡺ࡟ࡵࡱ࡮ࡩࡳࡅ࡮ࡢ࡯ࡨࡁࢀࢃࠦࡵࡻࡳࡩࡂࢁࡽࠧࡲࡨࡶࡨࡿ࠽ࡼࡿࠥᬰ").format(self.config[bstack11l1ll1_opy_ (u"ࠪࡴࡷࡵࡪࡦࡥࡷࡒࡦࡳࡥࠨᬱ")], bstack11ll11111l1_opy_, bstack11l1llll11l_opy_)
    if self.percy_capture_mode:
      bstack11lllll1l1l_opy_ += bstack11l1ll1_opy_ (u"ࠦࠫࡶࡥࡳࡥࡼࡣࡨࡧࡰࡵࡷࡵࡩࡤࡳ࡯ࡥࡧࡀࡿࢂࠨᬲ").format(self.percy_capture_mode)
    uri = bstack1llll1ll11_opy_(bstack11lllll1l1l_opy_)
    try:
      response = bstack1l1111l1l_opy_(bstack11l1ll1_opy_ (u"ࠬࡍࡅࡕࠩᬳ"), uri, {}, {bstack11l1ll1_opy_ (u"࠭ࡡࡶࡶ࡫᬴ࠫ"): (self.config[bstack11l1ll1_opy_ (u"ࠧࡶࡵࡨࡶࡓࡧ࡭ࡦࠩᬵ")], self.config[bstack11l1ll1_opy_ (u"ࠨࡣࡦࡧࡪࡹࡳࡌࡧࡼࠫᬶ")])})
      if response.status_code == 200:
        data = response.json()
        self.bstack111ll11ll_opy_ = data.get(bstack11l1ll1_opy_ (u"ࠩࡶࡹࡨࡩࡥࡴࡵࠪᬷ"))
        self.percy_capture_mode = data.get(bstack11l1ll1_opy_ (u"ࠪࡴࡪࡸࡣࡺࡡࡦࡥࡵࡺࡵࡳࡧࡢࡱࡴࡪࡥࠨᬸ"))
        os.environ[bstack11l1ll1_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡔࡊࡘࡃ࡚ࠩᬹ")] = str(self.bstack111ll11ll_opy_)
        os.environ[bstack11l1ll1_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡕࡋࡒࡄ࡛ࡢࡇࡆࡖࡔࡖࡔࡈࡣࡒࡕࡄࡆࠩᬺ")] = str(self.percy_capture_mode)
        if bstack11l1llll11l_opy_ == bstack11l1ll1_opy_ (u"ࠨࡵ࡯ࡦࡨࡪ࡮ࡴࡥࡥࠤᬻ") and str(self.bstack111ll11ll_opy_).lower() == bstack11l1ll1_opy_ (u"ࠢࡵࡴࡸࡩࠧᬼ"):
          self.bstack11lllll1_opy_ = True
        if bstack11l1ll1_opy_ (u"ࠣࡶࡲ࡯ࡪࡴࠢᬽ") in data:
          return data[bstack11l1ll1_opy_ (u"ࠤࡷࡳࡰ࡫࡮ࠣᬾ")]
        else:
          raise bstack11l1ll1_opy_ (u"ࠪࡘࡴࡱࡥ࡯ࠢࡑࡳࡹࠦࡆࡰࡷࡱࡨࠥ࠳ࠠࡼࡿࠪᬿ").format(data)
      else:
        raise bstack11l1ll1_opy_ (u"ࠦࡋࡧࡩ࡭ࡧࡧࠤࡹࡵࠠࡧࡧࡷࡧ࡭ࠦࡰࡦࡴࡦࡽࠥࡺ࡯࡬ࡧࡱ࠰ࠥࡘࡥࡴࡲࡲࡲࡸ࡫ࠠࡴࡶࡤࡸࡺࡹࠠ࠮ࠢࡾࢁ࠱ࠦࡒࡦࡵࡳࡳࡳࡹࡥࠡࡄࡲࡨࡾࠦ࠭ࠡࡽࢀࠦᭀ").format(response.status_code, response.json())
    except Exception as e:
      self.logger.error(bstack11l1ll1_opy_ (u"ࠧࡋࡸࡤࡧࡳࡸ࡮ࡵ࡮ࠡ࡫ࡱࠤࡨࡸࡥࡢࡶ࡬ࡲ࡬ࠦࡰࡦࡴࡦࡽࠥࡶࡲࡰ࡬ࡨࡧࡹࠨᭁ").format(e))
  def bstack11l1ll1llll_opy_(self):
    bstack11l1lll11ll_opy_ = os.path.join(tempfile.gettempdir(), bstack11l1ll1_opy_ (u"ࠨࡰࡦࡴࡦࡽࡈࡵ࡮ࡧ࡫ࡪ࠲࡯ࡹ࡯࡯ࠤᭂ"))
    try:
      if bstack11l1ll1_opy_ (u"ࠧࡷࡧࡵࡷ࡮ࡵ࡮ࠨᭃ") not in self.bstack11ll11l1lll_opy_:
        self.bstack11ll11l1lll_opy_[bstack11l1ll1_opy_ (u"ࠨࡸࡨࡶࡸ࡯࡯࡯᭄ࠩ")] = 2
      with open(bstack11l1lll11ll_opy_, bstack11l1ll1_opy_ (u"ࠩࡺࠫᭅ")) as fp:
        json.dump(self.bstack11ll11l1lll_opy_, fp)
      return bstack11l1lll11ll_opy_
    except Exception as e:
      self.logger.error(bstack11l1ll1_opy_ (u"࡙ࠥࡳࡧࡢ࡭ࡧࠣࡸࡴࠦࡣࡳࡧࡤࡸࡪࠦࡰࡦࡴࡦࡽࠥࡩ࡯࡯ࡨ࠯ࠤࡊࡾࡣࡦࡲࡷ࡭ࡴࡴࠠࡼࡿࠥᭆ").format(e))
  def bstack11l1lll111l_opy_(self, cmd, env = os.environ.copy()):
    try:
      if self.bstack11l1ll1ll1l_opy_ == bstack11l1ll1_opy_ (u"ࠫࡼ࡯࡮ࠨᭇ"):
        bstack11ll11l1l1l_opy_ = [bstack11l1ll1_opy_ (u"ࠬࡩ࡭ࡥ࠰ࡨࡼࡪ࠭ᭈ"), bstack11l1ll1_opy_ (u"࠭࠯ࡤࠩᭉ")]
        cmd = bstack11ll11l1l1l_opy_ + cmd
      cmd = bstack11l1ll1_opy_ (u"ࠧࠡࠩᭊ").join(cmd)
      self.logger.debug(bstack11l1ll1_opy_ (u"ࠣࡔࡸࡲࡳ࡯࡮ࡨࠢࡾࢁࠧᭋ").format(cmd))
      with open(self.bstack11l1llllll1_opy_, bstack11l1ll1_opy_ (u"ࠤࡤࠦᭌ")) as bstack11ll11lll11_opy_:
        process = subprocess.Popen(cmd, shell=True, stdout=bstack11ll11lll11_opy_, text=True, stderr=bstack11ll11lll11_opy_, env=env, universal_newlines=True)
      return process
    except Exception as e:
      self.bstack11ll11ll111_opy_ = True
      self.logger.error(bstack11l1ll1_opy_ (u"ࠥࡊࡦ࡯࡬ࡦࡦࠣࡸࡴࠦࡳࡵࡣࡵࡸࠥࡶࡥࡳࡥࡼࠤࡼ࡯ࡴࡩࠢࡦࡱࡩࠦ࠭ࠡࡽࢀ࠰ࠥࡋࡸࡤࡧࡳࡸ࡮ࡵ࡮࠻ࠢࡾࢁࠧ᭍").format(cmd, e))
  def shutdown(self):
    try:
      if self.bstack11ll111l1l1_opy_:
        self.logger.info(bstack11l1ll1_opy_ (u"ࠦࡘࡺ࡯ࡱࡲ࡬ࡲ࡬ࠦࡐࡦࡴࡦࡽࠧ᭎"))
        cmd = [self.binary_path, bstack11l1ll1_opy_ (u"ࠧ࡫ࡸࡦࡥ࠽ࡷࡹࡵࡰࠣ᭏")]
        self.bstack11l1lll111l_opy_(cmd)
        self.bstack11ll111l1l1_opy_ = False
    except Exception as e:
      self.logger.error(bstack11l1ll1_opy_ (u"ࠨࡆࡢ࡫࡯ࡩࡩࠦࡴࡰࠢࡶࡸࡴࡶࠠࡴࡧࡶࡷ࡮ࡵ࡮ࠡࡹ࡬ࡸ࡭ࠦࡣࡰ࡯ࡰࡥࡳࡪࠠ࠮ࠢࡾࢁ࠱ࠦࡅࡹࡥࡨࡴࡹ࡯࡯࡯࠼ࠣࡿࢂࠨ᭐").format(cmd, e))
  def bstack1ll1111l_opy_(self):
    if not self.bstack111ll11ll_opy_:
      return
    try:
      bstack11ll11111ll_opy_ = 0
      while not self.bstack11ll111l1l1_opy_ and bstack11ll11111ll_opy_ < self.bstack11ll1111ll1_opy_:
        if self.bstack11ll11ll111_opy_:
          self.logger.info(bstack11l1ll1_opy_ (u"ࠢࡑࡧࡵࡧࡾࠦࡳࡦࡶࡸࡴࠥ࡬ࡡࡪ࡮ࡨࡨࠧ᭑"))
          return
        time.sleep(1)
        bstack11ll11111ll_opy_ += 1
      os.environ[bstack11l1ll1_opy_ (u"ࠨࡒࡈࡖࡈ࡟࡟ࡃࡇࡖࡘࡤࡖࡌࡂࡖࡉࡓࡗࡓࠧ᭒")] = str(self.bstack11ll11llll1_opy_())
      self.logger.info(bstack11l1ll1_opy_ (u"ࠤࡓࡩࡷࡩࡹࠡࡵࡨࡸࡺࡶࠠࡤࡱࡰࡴࡱ࡫ࡴࡦࡦࠥ᭓"))
    except Exception as e:
      self.logger.error(bstack11l1ll1_opy_ (u"࡙ࠥࡳࡧࡢ࡭ࡧࠣࡸࡴࠦࡳࡦࡶࡸࡴࠥࡶࡥࡳࡥࡼ࠰ࠥࡋࡸࡤࡧࡳࡸ࡮ࡵ࡮ࠡࡽࢀࠦ᭔").format(e))
  def bstack11ll11llll1_opy_(self):
    if self.bstack1lll111l1l_opy_:
      return
    try:
      bstack11ll111ll1l_opy_ = [platform[bstack11l1ll1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡓࡧ࡭ࡦࠩ᭕")].lower() for platform in self.config.get(bstack11l1ll1_opy_ (u"ࠬࡶ࡬ࡢࡶࡩࡳࡷࡳࡳࠨ᭖"), [])]
      bstack11ll11ll1l1_opy_ = sys.maxsize
      bstack11l1lllll1l_opy_ = bstack11l1ll1_opy_ (u"࠭ࠧ᭗")
      for browser in bstack11ll111ll1l_opy_:
        if browser in self.bstack11l1ll1lll1_opy_:
          bstack11l1lll1l11_opy_ = self.bstack11l1ll1lll1_opy_[browser]
        if bstack11l1lll1l11_opy_ < bstack11ll11ll1l1_opy_:
          bstack11ll11ll1l1_opy_ = bstack11l1lll1l11_opy_
          bstack11l1lllll1l_opy_ = browser
      return bstack11l1lllll1l_opy_
    except Exception as e:
      self.logger.error(bstack11l1ll1_opy_ (u"ࠢࡖࡰࡤࡦࡱ࡫ࠠࡵࡱࠣࡪ࡮ࡴࡤࠡࡤࡨࡷࡹࠦࡰ࡭ࡣࡷࡪࡴࡸ࡭࠭ࠢࡈࡼࡨ࡫ࡰࡵ࡫ࡲࡲࠥࢁࡽࠣ᭘").format(e))
  @classmethod
  def bstack1l1111111_opy_(self):
    return os.getenv(bstack11l1ll1_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡑࡇࡕࡇ࡞࠭᭙"), bstack11l1ll1_opy_ (u"ࠩࡉࡥࡱࡹࡥࠨ᭚")).lower()
  @classmethod
  def bstack111llll1l_opy_(self):
    return os.getenv(bstack11l1ll1_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡓࡉࡗࡉ࡙ࡠࡅࡄࡔ࡙࡛ࡒࡆࡡࡐࡓࡉࡋࠧ᭛"), bstack11l1ll1_opy_ (u"ࠫࠬ᭜"))
  @classmethod
  def bstack1ll11l111l1_opy_(cls, value):
    cls.bstack11lllll1_opy_ = value
  @classmethod
  def bstack11ll1111111_opy_(cls):
    return cls.bstack11lllll1_opy_
  @classmethod
  def bstack1ll11l111ll_opy_(cls, value):
    cls.percy_build_id = value
  @classmethod
  def bstack11l1lll1lll_opy_(cls):
    return cls.percy_build_id