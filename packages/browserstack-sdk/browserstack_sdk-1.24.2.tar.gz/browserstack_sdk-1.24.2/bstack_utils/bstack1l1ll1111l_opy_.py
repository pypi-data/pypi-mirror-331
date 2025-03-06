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
import json
class bstack1l11l1lll1l_opy_(object):
  bstack1l11l1llll_opy_ = os.path.join(os.path.expanduser(bstack11l1ll1_opy_ (u"ࠧࡿࠩᓈ")), bstack11l1ll1_opy_ (u"ࠨ࠰ࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࠨᓉ"))
  bstack1l11l1lllll_opy_ = os.path.join(bstack1l11l1llll_opy_, bstack11l1ll1_opy_ (u"ࠩࡦࡳࡲࡳࡡ࡯ࡦࡶ࠲࡯ࡹ࡯࡯ࠩᓊ"))
  commands_to_wrap = None
  perform_scan = None
  bstack11l1l11l1_opy_ = None
  bstack11l1lll1l_opy_ = None
  bstack1l11ll11l11_opy_ = None
  def __new__(cls):
    if not hasattr(cls, bstack11l1ll1_opy_ (u"ࠪ࡭ࡳࡹࡴࡢࡰࡦࡩࠬᓋ")):
      cls.instance = super(bstack1l11l1lll1l_opy_, cls).__new__(cls)
      cls.instance.bstack1l11l1llll1_opy_()
    return cls.instance
  def bstack1l11l1llll1_opy_(self):
    try:
      with open(self.bstack1l11l1lllll_opy_, bstack11l1ll1_opy_ (u"ࠫࡷ࠭ᓌ")) as bstack1ll1llll_opy_:
        bstack1l11l1lll11_opy_ = bstack1ll1llll_opy_.read()
        data = json.loads(bstack1l11l1lll11_opy_)
        if bstack11l1ll1_opy_ (u"ࠬࡩ࡯࡮࡯ࡤࡲࡩࡹࠧᓍ") in data:
          self.bstack1l11lll1111_opy_(data[bstack11l1ll1_opy_ (u"࠭ࡣࡰ࡯ࡰࡥࡳࡪࡳࠨᓎ")])
        if bstack11l1ll1_opy_ (u"ࠧࡴࡥࡵ࡭ࡵࡺࡳࠨᓏ") in data:
          self.bstack1l11ll111ll_opy_(data[bstack11l1ll1_opy_ (u"ࠨࡵࡦࡶ࡮ࡶࡴࡴࠩᓐ")])
    except:
      pass
  def bstack1l11ll111ll_opy_(self, scripts):
    if scripts != None:
      self.perform_scan = scripts[bstack11l1ll1_opy_ (u"ࠩࡶࡧࡦࡴࠧᓑ")]
      self.bstack11l1l11l1_opy_ = scripts[bstack11l1ll1_opy_ (u"ࠪ࡫ࡪࡺࡒࡦࡵࡸࡰࡹࡹࠧᓒ")]
      self.bstack11l1lll1l_opy_ = scripts[bstack11l1ll1_opy_ (u"ࠫ࡬࡫ࡴࡓࡧࡶࡹࡱࡺࡳࡔࡷࡰࡱࡦࡸࡹࠨᓓ")]
      self.bstack1l11ll11l11_opy_ = scripts[bstack11l1ll1_opy_ (u"ࠬࡹࡡࡷࡧࡕࡩࡸࡻ࡬ࡵࡵࠪᓔ")]
  def bstack1l11lll1111_opy_(self, commands_to_wrap):
    if commands_to_wrap != None and len(commands_to_wrap) != 0:
      self.commands_to_wrap = commands_to_wrap
  def store(self):
    try:
      with open(self.bstack1l11l1lllll_opy_, bstack11l1ll1_opy_ (u"࠭ࡷࠨᓕ")) as file:
        json.dump({
          bstack11l1ll1_opy_ (u"ࠢࡤࡱࡰࡱࡦࡴࡤࡴࠤᓖ"): self.commands_to_wrap,
          bstack11l1ll1_opy_ (u"ࠣࡵࡦࡶ࡮ࡶࡴࡴࠤᓗ"): {
            bstack11l1ll1_opy_ (u"ࠤࡶࡧࡦࡴࠢᓘ"): self.perform_scan,
            bstack11l1ll1_opy_ (u"ࠥ࡫ࡪࡺࡒࡦࡵࡸࡰࡹࡹࠢᓙ"): self.bstack11l1l11l1_opy_,
            bstack11l1ll1_opy_ (u"ࠦ࡬࡫ࡴࡓࡧࡶࡹࡱࡺࡳࡔࡷࡰࡱࡦࡸࡹࠣᓚ"): self.bstack11l1lll1l_opy_,
            bstack11l1ll1_opy_ (u"ࠧࡹࡡࡷࡧࡕࡩࡸࡻ࡬ࡵࡵࠥᓛ"): self.bstack1l11ll11l11_opy_
          }
        }, file)
    except:
      pass
  def bstack11l1l1111_opy_(self, bstack1lll11ll11l_opy_):
    try:
      return any(command.get(bstack11l1ll1_opy_ (u"࠭࡮ࡢ࡯ࡨࠫᓜ")) == bstack1lll11ll11l_opy_ for command in self.commands_to_wrap)
    except:
      return False
bstack1l1ll1111l_opy_ = bstack1l11l1lll1l_opy_()