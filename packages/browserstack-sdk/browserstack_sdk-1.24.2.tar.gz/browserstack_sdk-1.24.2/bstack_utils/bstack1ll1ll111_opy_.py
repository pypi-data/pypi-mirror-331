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
import sys
import logging
import tarfile
import io
import os
import time
import requests
import re
from requests_toolbelt.multipart.encoder import MultipartEncoder
from bstack_utils.constants import bstack1l111ll1lll_opy_, bstack1l11l1l11l1_opy_
import tempfile
import json
bstack11ll1ll1ll1_opy_ = os.getenv(bstack11l1ll1_opy_ (u"ࠣࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡍࡑࡊࡣࡋࡏࡌࡆࠤᩝ"), None) or os.path.join(tempfile.gettempdir(), bstack11l1ll1_opy_ (u"ࠤࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡦࡨࡦࡺ࡭࠮࡭ࡱࡪࠦᩞ"))
bstack11ll1l11ll1_opy_ = os.path.join(bstack11l1ll1_opy_ (u"ࠥࡰࡴ࡭ࠢ᩟"), bstack11l1ll1_opy_ (u"ࠫࡸࡪ࡫࠮ࡥ࡯࡭࠲ࡪࡥࡣࡷࡪ࠲ࡱࡵࡧࠨ᩠"))
logging.Formatter.converter = time.gmtime
def get_logger(name=__name__, level=None):
  logger = logging.getLogger(name)
  if level:
    logging.basicConfig(
      level=level,
      format=bstack11l1ll1_opy_ (u"ࠬࠫࠨࡢࡵࡦࡸ࡮ࡳࡥࠪࡵࠣ࡟ࠪ࠮࡮ࡢ࡯ࡨ࠭ࡸࡣ࡛ࠦࠪ࡯ࡩࡻ࡫࡬࡯ࡣࡰࡩ࠮ࡹ࡝ࠡ࠯ࠣࠩ࠭ࡳࡥࡴࡵࡤ࡫ࡪ࠯ࡳࠨᩡ"),
      datefmt=bstack11l1ll1_opy_ (u"࡚࠭ࠥ࠯ࠨࡱ࠲ࠫࡤࡕࠧࡋ࠾ࠪࡓ࠺ࠦࡕ࡝ࠫᩢ"),
      stream=sys.stdout
    )
  return logger
def bstack1llll1l1lll_opy_():
  bstack11ll1l1ll1l_opy_ = os.environ.get(bstack11l1ll1_opy_ (u"ࠢࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡂࡊࡐࡄࡖ࡞ࡥࡄࡆࡄࡘࡋࠧᩣ"), bstack11l1ll1_opy_ (u"ࠣࡨࡤࡰࡸ࡫ࠢᩤ"))
  return logging.DEBUG if bstack11ll1l1ll1l_opy_.lower() == bstack11l1ll1_opy_ (u"ࠤࡷࡶࡺ࡫ࠢᩥ") else logging.INFO
def bstack1ll1l1111l1_opy_():
  global bstack11ll1ll1ll1_opy_
  if os.path.exists(bstack11ll1ll1ll1_opy_):
    os.remove(bstack11ll1ll1ll1_opy_)
  if os.path.exists(bstack11ll1l11ll1_opy_):
    os.remove(bstack11ll1l11ll1_opy_)
def bstack1l11l111l_opy_():
  for handler in logging.getLogger().handlers:
    logging.getLogger().removeHandler(handler)
def bstack11l1ll111_opy_(config, log_level):
  bstack11ll1l1ll11_opy_ = log_level
  if bstack11l1ll1_opy_ (u"ࠪࡰࡴ࡭ࡌࡦࡸࡨࡰࠬᩦ") in config and config[bstack11l1ll1_opy_ (u"ࠫࡱࡵࡧࡍࡧࡹࡩࡱ࠭ᩧ")] in bstack1l111ll1lll_opy_:
    bstack11ll1l1ll11_opy_ = bstack1l111ll1lll_opy_[config[bstack11l1ll1_opy_ (u"ࠬࡲ࡯ࡨࡎࡨࡺࡪࡲࠧᩨ")]]
  if config.get(bstack11l1ll1_opy_ (u"࠭ࡤࡪࡵࡤࡦࡱ࡫ࡁࡶࡶࡲࡇࡦࡶࡴࡶࡴࡨࡐࡴ࡭ࡳࠨᩩ"), False):
    logging.getLogger().setLevel(bstack11ll1l1ll11_opy_)
    return bstack11ll1l1ll11_opy_
  global bstack11ll1ll1ll1_opy_
  bstack1l11l111l_opy_()
  bstack11ll1ll111l_opy_ = logging.Formatter(
    fmt=bstack11l1ll1_opy_ (u"ࠧࠦࠪࡤࡷࡨࡺࡩ࡮ࡧࠬࡷࠥࡡࠥࠩࡰࡤࡱࡪ࠯ࡳ࡞࡝ࠨࠬࡱ࡫ࡶࡦ࡮ࡱࡥࡲ࡫ࠩࡴ࡟ࠣ࠱ࠥࠫࠨ࡮ࡧࡶࡷࡦ࡭ࡥࠪࡵࠪᩪ"),
    datefmt=bstack11l1ll1_opy_ (u"ࠨࠧ࡜࠱ࠪࡳ࠭ࠦࡦࡗࠩࡍࡀࠥࡎ࠼ࠨࡗ࡟࠭ᩫ"),
  )
  bstack11ll1l1lll1_opy_ = logging.StreamHandler(sys.stdout)
  file_handler = logging.FileHandler(bstack11ll1ll1ll1_opy_)
  file_handler.setFormatter(bstack11ll1ll111l_opy_)
  bstack11ll1l1lll1_opy_.setFormatter(bstack11ll1ll111l_opy_)
  file_handler.setLevel(logging.DEBUG)
  bstack11ll1l1lll1_opy_.setLevel(log_level)
  file_handler.addFilter(lambda r: r.name != bstack11l1ll1_opy_ (u"ࠩࡶࡩࡱ࡫࡮ࡪࡷࡰ࠲ࡼ࡫ࡢࡥࡴ࡬ࡺࡪࡸ࠮ࡳࡧࡰࡳࡹ࡫࠮ࡳࡧࡰࡳࡹ࡫࡟ࡤࡱࡱࡲࡪࡩࡴࡪࡱࡱࠫᩬ"))
  logging.getLogger().setLevel(logging.DEBUG)
  bstack11ll1l1lll1_opy_.setLevel(bstack11ll1l1ll11_opy_)
  logging.getLogger().addHandler(bstack11ll1l1lll1_opy_)
  logging.getLogger().addHandler(file_handler)
  return bstack11ll1l1ll11_opy_
def bstack11ll1lll1l1_opy_(config):
  try:
    bstack11ll1ll1lll_opy_ = set(bstack1l11l1l11l1_opy_)
    bstack11ll1l1l1ll_opy_ = bstack11l1ll1_opy_ (u"ࠪࠫᩭ")
    with open(bstack11l1ll1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡽࡲࡲࠧᩮ")) as bstack11ll1ll1l1l_opy_:
      bstack11ll1ll1l11_opy_ = bstack11ll1ll1l1l_opy_.read()
      bstack11ll1l1l1ll_opy_ = re.sub(bstack11l1ll1_opy_ (u"ࡷ࠭࡞ࠩ࡞ࡶ࠯࠮ࡅࠣ࠯ࠬࠧࡠࡳ࠭ᩯ"), bstack11l1ll1_opy_ (u"࠭ࠧᩰ"), bstack11ll1ll1l11_opy_, flags=re.M)
      bstack11ll1l1l1ll_opy_ = re.sub(
        bstack11l1ll1_opy_ (u"ࡲࠨࡠࠫࡠࡸ࠱ࠩࡀࠪࠪᩱ") + bstack11l1ll1_opy_ (u"ࠨࡾࠪᩲ").join(bstack11ll1ll1lll_opy_) + bstack11l1ll1_opy_ (u"ࠩࠬ࠲࠯ࠪࠧᩳ"),
        bstack11l1ll1_opy_ (u"ࡵࠫࡡ࠸࠺ࠡ࡝ࡕࡉࡉࡇࡃࡕࡇࡇࡡࠬᩴ"),
        bstack11ll1l1l1ll_opy_, flags=re.M | re.I
      )
    def bstack11ll1l1l111_opy_(dic):
      bstack11ll1ll11l1_opy_ = {}
      for key, value in dic.items():
        if key in bstack11ll1ll1lll_opy_:
          bstack11ll1ll11l1_opy_[key] = bstack11l1ll1_opy_ (u"ࠫࡠࡘࡅࡅࡃࡆࡘࡊࡊ࡝ࠨ᩵")
        else:
          if isinstance(value, dict):
            bstack11ll1ll11l1_opy_[key] = bstack11ll1l1l111_opy_(value)
          else:
            bstack11ll1ll11l1_opy_[key] = value
      return bstack11ll1ll11l1_opy_
    bstack11ll1ll11l1_opy_ = bstack11ll1l1l111_opy_(config)
    return {
      bstack11l1ll1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡾࡳ࡬ࠨ᩶"): bstack11ll1l1l1ll_opy_,
      bstack11l1ll1_opy_ (u"࠭ࡦࡪࡰࡤࡰࡨࡵ࡮ࡧ࡫ࡪ࠲࡯ࡹ࡯࡯ࠩ᩷"): json.dumps(bstack11ll1ll11l1_opy_)
    }
  except Exception as e:
    return {}
def bstack11ll1lll1ll_opy_(inipath, rootpath):
  log_dir = os.path.join(os.getcwd(), bstack11l1ll1_opy_ (u"ࠧ࡭ࡱࡪࠫ᩸"))
  if not os.path.exists(log_dir):
    os.makedirs(log_dir)
  bstack11ll1lll111_opy_ = os.path.join(log_dir, bstack11l1ll1_opy_ (u"ࠨࡲࡼࡸࡪࡹࡴࡠࡥࡲࡲ࡫࡯ࡧࡴࠩ᩹"))
  if not os.path.exists(bstack11ll1lll111_opy_):
    bstack11ll1l11lll_opy_ = {
      bstack11l1ll1_opy_ (u"ࠤ࡬ࡲ࡮ࡶࡡࡵࡪࠥ᩺"): str(inipath),
      bstack11l1ll1_opy_ (u"ࠥࡶࡴࡵࡴࡱࡣࡷ࡬ࠧ᩻"): str(rootpath)
    }
    with open(os.path.join(log_dir, bstack11l1ll1_opy_ (u"ࠫࡵࡿࡴࡦࡵࡷࡣࡨࡵ࡮ࡧ࡫ࡪࡷ࠳ࡰࡳࡰࡰࠪ᩼")), bstack11l1ll1_opy_ (u"ࠬࡽࠧ᩽")) as bstack11ll1l1llll_opy_:
      bstack11ll1l1llll_opy_.write(json.dumps(bstack11ll1l11lll_opy_))
def bstack11ll1llll11_opy_():
  try:
    bstack11ll1lll111_opy_ = os.path.join(os.getcwd(), bstack11l1ll1_opy_ (u"࠭࡬ࡰࡩࠪ᩾"), bstack11l1ll1_opy_ (u"ࠧࡱࡻࡷࡩࡸࡺ࡟ࡤࡱࡱࡪ࡮࡭ࡳ࠯࡬ࡶࡳࡳ᩿࠭"))
    if os.path.exists(bstack11ll1lll111_opy_):
      with open(bstack11ll1lll111_opy_, bstack11l1ll1_opy_ (u"ࠨࡴࠪ᪀")) as bstack11ll1l1llll_opy_:
        bstack11ll1l1l1l1_opy_ = json.load(bstack11ll1l1llll_opy_)
      return bstack11ll1l1l1l1_opy_.get(bstack11l1ll1_opy_ (u"ࠩ࡬ࡲ࡮ࡶࡡࡵࡪࠪ᪁"), bstack11l1ll1_opy_ (u"ࠪࠫ᪂")), bstack11ll1l1l1l1_opy_.get(bstack11l1ll1_opy_ (u"ࠫࡷࡵ࡯ࡵࡲࡤࡸ࡭࠭᪃"), bstack11l1ll1_opy_ (u"ࠬ࠭᪄"))
  except:
    pass
  return None, None
def bstack11ll1ll1111_opy_():
  try:
    bstack11ll1lll111_opy_ = os.path.join(os.getcwd(), bstack11l1ll1_opy_ (u"࠭࡬ࡰࡩࠪ᪅"), bstack11l1ll1_opy_ (u"ࠧࡱࡻࡷࡩࡸࡺ࡟ࡤࡱࡱࡪ࡮࡭ࡳ࠯࡬ࡶࡳࡳ࠭᪆"))
    if os.path.exists(bstack11ll1lll111_opy_):
      os.remove(bstack11ll1lll111_opy_)
  except:
    pass
def bstack1l1l1lll1l_opy_(config):
  from bstack_utils.helper import bstack1ll1l11l1_opy_
  global bstack11ll1ll1ll1_opy_
  try:
    if config.get(bstack11l1ll1_opy_ (u"ࠨࡦ࡬ࡷࡦࡨ࡬ࡦࡃࡸࡸࡴࡉࡡࡱࡶࡸࡶࡪࡒ࡯ࡨࡵࠪ᪇"), False):
      return
    uuid = os.getenv(bstack11l1ll1_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡖࡈࡗ࡙ࡎࡕࡃࡡࡘ࡙ࡎࡊࠧ᪈")) if os.getenv(bstack11l1ll1_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡗࡉࡘ࡚ࡈࡖࡄࡢ࡙࡚ࡏࡄࠨ᪉")) else bstack1ll1l11l1_opy_.get_property(bstack11l1ll1_opy_ (u"ࠦࡸࡪ࡫ࡓࡷࡱࡍࡩࠨ᪊"))
    if not uuid or uuid == bstack11l1ll1_opy_ (u"ࠬࡴࡵ࡭࡮ࠪ᪋"):
      return
    bstack11ll1l1l11l_opy_ = [bstack11l1ll1_opy_ (u"࠭ࡲࡦࡳࡸ࡭ࡷ࡫࡭ࡦࡰࡷࡷ࠳ࡺࡸࡵࠩ᪌"), bstack11l1ll1_opy_ (u"ࠧࡑ࡫ࡳࡪ࡮ࡲࡥࠨ᪍"), bstack11l1ll1_opy_ (u"ࠨࡲࡼࡴࡷࡵࡪࡦࡥࡷ࠲ࡹࡵ࡭࡭ࠩ᪎"), bstack11ll1ll1ll1_opy_, bstack11ll1l11ll1_opy_]
    bstack11ll1ll11ll_opy_, root_path = bstack11ll1llll11_opy_()
    if bstack11ll1ll11ll_opy_ != None:
      bstack11ll1l1l11l_opy_.append(bstack11ll1ll11ll_opy_)
    if root_path != None:
      bstack11ll1l1l11l_opy_.append(os.path.join(root_path, bstack11l1ll1_opy_ (u"ࠩࡦࡳࡳ࡬ࡴࡦࡵࡷ࠲ࡵࡿࠧ᪏")))
    bstack1l11l111l_opy_()
    logging.shutdown()
    output_file = os.path.join(tempfile.gettempdir(), bstack11l1ll1_opy_ (u"ࠪࡦࡸࡺࡡࡤ࡭࠰ࡰࡴ࡭ࡳ࠮ࠩ᪐") + uuid + bstack11l1ll1_opy_ (u"ࠫ࠳ࡺࡡࡳ࠰ࡪࡾࠬ᪑"))
    with tarfile.open(output_file, bstack11l1ll1_opy_ (u"ࠧࡽ࠺ࡨࡼࠥ᪒")) as archive:
      for file in filter(lambda f: os.path.exists(f), bstack11ll1l1l11l_opy_):
        try:
          archive.add(file,  arcname=os.path.basename(file))
        except:
          pass
      for name, data in bstack11ll1lll1l1_opy_(config).items():
        tarinfo = tarfile.TarInfo(name)
        bstack11ll1lll11l_opy_ = data.encode()
        tarinfo.size = len(bstack11ll1lll11l_opy_)
        archive.addfile(tarinfo, io.BytesIO(bstack11ll1lll11l_opy_))
    bstack111llll1_opy_ = MultipartEncoder(
      fields= {
        bstack11l1ll1_opy_ (u"࠭ࡤࡢࡶࡤࠫ᪓"): (os.path.basename(output_file), open(os.path.abspath(output_file), bstack11l1ll1_opy_ (u"ࠧࡳࡤࠪ᪔")), bstack11l1ll1_opy_ (u"ࠨࡣࡳࡴࡱ࡯ࡣࡢࡶ࡬ࡳࡳ࠵ࡸ࠮ࡩࡽ࡭ࡵ࠭᪕")),
        bstack11l1ll1_opy_ (u"ࠩࡦࡰ࡮࡫࡮ࡵࡄࡸ࡭ࡱࡪࡕࡶ࡫ࡧࠫ᪖"): uuid
      }
    )
    response = requests.post(
      bstack11l1ll1_opy_ (u"ࠥ࡬ࡹࡺࡰࡴ࠼࠲࠳ࡺࡶ࡬ࡰࡣࡧ࠱ࡴࡨࡳࡦࡴࡹࡥࡧ࡯࡬ࡪࡶࡼ࠲ࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡧࡴࡳ࠯ࡤ࡮࡬ࡩࡳࡺ࠭࡭ࡱࡪࡷ࠴ࡻࡰ࡭ࡱࡤࡨࠧ᪗"),
      data=bstack111llll1_opy_,
      headers={bstack11l1ll1_opy_ (u"ࠫࡈࡵ࡮ࡵࡧࡱࡸ࠲࡚ࡹࡱࡧࠪ᪘"): bstack111llll1_opy_.content_type},
      auth=(config[bstack11l1ll1_opy_ (u"ࠬࡻࡳࡦࡴࡑࡥࡲ࡫ࠧ᪙")], config[bstack11l1ll1_opy_ (u"࠭ࡡࡤࡥࡨࡷࡸࡑࡥࡺࠩ᪚")])
    )
    os.remove(output_file)
    if response.status_code != 200:
      get_logger().debug(bstack11l1ll1_opy_ (u"ࠧࡆࡴࡵࡳࡷࠦࡵࡱ࡮ࡲࡥࡩࠦ࡬ࡰࡩࡶ࠾ࠥ࠭᪛") + response.status_code)
  except Exception as e:
    get_logger().debug(bstack11l1ll1_opy_ (u"ࠨࡇࡻࡧࡪࡶࡴࡪࡱࡱࠤ࡮ࡴࠠࡴࡧࡱࡨ࡮ࡴࡧࠡ࡮ࡲ࡫ࡸࡀࠧ᪜") + str(e))
  finally:
    try:
      bstack1ll1l1111l1_opy_()
      bstack11ll1ll1111_opy_()
    except:
      pass