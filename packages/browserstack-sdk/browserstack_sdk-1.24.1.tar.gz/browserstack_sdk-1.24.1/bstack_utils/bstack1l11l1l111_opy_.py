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
import json
class bstack1111ll111l_opy_(object):
  bstack1llll1l1l1_opy_ = os.path.join(os.path.expanduser(bstack111l11_opy_ (u"ࠧࡿࠩၨ")), bstack111l11_opy_ (u"ࠨ࠰ࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࠨၩ"))
  bstack1111ll1l11_opy_ = os.path.join(bstack1llll1l1l1_opy_, bstack111l11_opy_ (u"ࠩࡦࡳࡲࡳࡡ࡯ࡦࡶ࠲࡯ࡹ࡯࡯ࠩၪ"))
  bstack1111ll11ll_opy_ = None
  perform_scan = None
  bstack1l11111lll_opy_ = None
  bstack1l111ll1l1_opy_ = None
  bstack111l1111ll_opy_ = None
  def __new__(cls):
    if not hasattr(cls, bstack111l11_opy_ (u"ࠪ࡭ࡳࡹࡴࡢࡰࡦࡩࠬၫ")):
      cls.instance = super(bstack1111ll111l_opy_, cls).__new__(cls)
      cls.instance.bstack1111ll1111_opy_()
    return cls.instance
  def bstack1111ll1111_opy_(self):
    try:
      with open(self.bstack1111ll1l11_opy_, bstack111l11_opy_ (u"ࠫࡷ࠭ၬ")) as bstack1l1111111l_opy_:
        bstack1111ll11l1_opy_ = bstack1l1111111l_opy_.read()
        data = json.loads(bstack1111ll11l1_opy_)
        if bstack111l11_opy_ (u"ࠬࡩ࡯࡮࡯ࡤࡲࡩࡹࠧၭ") in data:
          self.bstack111l11l1ll_opy_(data[bstack111l11_opy_ (u"࠭ࡣࡰ࡯ࡰࡥࡳࡪࡳࠨၮ")])
        if bstack111l11_opy_ (u"ࠧࡴࡥࡵ࡭ࡵࡺࡳࠨၯ") in data:
          self.bstack111l1l1lll_opy_(data[bstack111l11_opy_ (u"ࠨࡵࡦࡶ࡮ࡶࡴࡴࠩၰ")])
    except:
      pass
  def bstack111l1l1lll_opy_(self, scripts):
    if scripts != None:
      self.perform_scan = scripts[bstack111l11_opy_ (u"ࠩࡶࡧࡦࡴࠧၱ")]
      self.bstack1l11111lll_opy_ = scripts[bstack111l11_opy_ (u"ࠪ࡫ࡪࡺࡒࡦࡵࡸࡰࡹࡹࠧၲ")]
      self.bstack1l111ll1l1_opy_ = scripts[bstack111l11_opy_ (u"ࠫ࡬࡫ࡴࡓࡧࡶࡹࡱࡺࡳࡔࡷࡰࡱࡦࡸࡹࠨၳ")]
      self.bstack111l1111ll_opy_ = scripts[bstack111l11_opy_ (u"ࠬࡹࡡࡷࡧࡕࡩࡸࡻ࡬ࡵࡵࠪၴ")]
  def bstack111l11l1ll_opy_(self, bstack1111ll11ll_opy_):
    if bstack1111ll11ll_opy_ != None and len(bstack1111ll11ll_opy_) != 0:
      self.bstack1111ll11ll_opy_ = bstack1111ll11ll_opy_
  def store(self):
    try:
      with open(self.bstack1111ll1l11_opy_, bstack111l11_opy_ (u"࠭ࡷࠨၵ")) as file:
        json.dump({
          bstack111l11_opy_ (u"ࠢࡤࡱࡰࡱࡦࡴࡤࡴࠤၶ"): self.bstack1111ll11ll_opy_,
          bstack111l11_opy_ (u"ࠣࡵࡦࡶ࡮ࡶࡴࡴࠤၷ"): {
            bstack111l11_opy_ (u"ࠤࡶࡧࡦࡴࠢၸ"): self.perform_scan,
            bstack111l11_opy_ (u"ࠥ࡫ࡪࡺࡒࡦࡵࡸࡰࡹࡹࠢၹ"): self.bstack1l11111lll_opy_,
            bstack111l11_opy_ (u"ࠦ࡬࡫ࡴࡓࡧࡶࡹࡱࡺࡳࡔࡷࡰࡱࡦࡸࡹࠣၺ"): self.bstack1l111ll1l1_opy_,
            bstack111l11_opy_ (u"ࠧࡹࡡࡷࡧࡕࡩࡸࡻ࡬ࡵࡵࠥၻ"): self.bstack111l1111ll_opy_
          }
        }, file)
    except:
      pass
  def bstack111l1l11l_opy_(self, bstack1111l1llll_opy_):
    try:
      return any(command.get(bstack111l11_opy_ (u"࠭࡮ࡢ࡯ࡨࠫၼ")) == bstack1111l1llll_opy_ for command in self.bstack1111ll11ll_opy_)
    except:
      return False
bstack1l11l1l111_opy_ = bstack1111ll111l_opy_()