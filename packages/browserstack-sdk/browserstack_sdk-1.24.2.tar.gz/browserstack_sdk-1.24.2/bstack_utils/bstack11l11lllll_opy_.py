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
from uuid import uuid4
from bstack_utils.helper import bstack1ll1l1ll_opy_, bstack11llll1lll1_opy_
from bstack_utils.bstack1lll11ll11_opy_ import bstack11l1l11ll1l_opy_
class bstack111ll1l1l1_opy_:
    def __init__(self, name=None, code=None, uuid=None, file_path=None, started_at=None, framework=None, tags=[], scope=[], bstack11l11l1111l_opy_=None, bstack11l11l1l11l_opy_=True, bstack1l1ll11l11l_opy_=None, bstack1l11l11l1_opy_=None, result=None, duration=None, bstack11l111ll1l_opy_=None, meta={}):
        self.bstack11l111ll1l_opy_ = bstack11l111ll1l_opy_
        self.name = name
        self.code = code
        self.file_path = file_path
        self.uuid = uuid
        if not self.uuid and bstack11l11l1l11l_opy_:
            self.uuid = uuid4().__str__()
        self.started_at = started_at
        self.framework = framework
        self.tags = tags
        self.scope = scope
        self.bstack11l11l1111l_opy_ = bstack11l11l1111l_opy_
        self.bstack1l1ll11l11l_opy_ = bstack1l1ll11l11l_opy_
        self.bstack1l11l11l1_opy_ = bstack1l11l11l1_opy_
        self.result = result
        self.duration = duration
        self.meta = meta
        self.hooks = []
    def bstack111lll1l1l_opy_(self):
        if self.uuid:
            return self.uuid
        self.uuid = uuid4().__str__()
        return self.uuid
    def bstack11l11ll11l_opy_(self, meta):
        self.meta = meta
    def bstack11l1l111ll_opy_(self, hooks):
        self.hooks = hooks
    def bstack11l11l111l1_opy_(self):
        bstack11l11l1l1l1_opy_ = os.path.relpath(self.file_path, start=os.getcwd())
        return {
            bstack11l1ll1_opy_ (u"ࠫ࡫࡯࡬ࡦࡡࡱࡥࡲ࡫ࠧᰋ"): bstack11l11l1l1l1_opy_,
            bstack11l1ll1_opy_ (u"ࠬࡲ࡯ࡤࡣࡷ࡭ࡴࡴࠧᰌ"): bstack11l11l1l1l1_opy_,
            bstack11l1ll1_opy_ (u"࠭ࡶࡤࡡࡩ࡭ࡱ࡫ࡰࡢࡶ࡫ࠫᰍ"): bstack11l11l1l1l1_opy_
        }
    def set(self, **kwargs):
        for key, val in kwargs.items():
            if not hasattr(self, key):
                raise TypeError(bstack11l1ll1_opy_ (u"ࠢࡖࡰࡨࡼࡵ࡫ࡣࡵࡧࡧࠤࡦࡸࡧࡶ࡯ࡨࡲࡹࡀࠠࠣᰎ") + key)
            setattr(self, key, val)
    def bstack11l11l11ll1_opy_(self):
        return {
            bstack11l1ll1_opy_ (u"ࠨࡰࡤࡱࡪ࠭ᰏ"): self.name,
            bstack11l1ll1_opy_ (u"ࠩࡥࡳࡩࡿࠧᰐ"): {
                bstack11l1ll1_opy_ (u"ࠪࡰࡦࡴࡧࠨᰑ"): bstack11l1ll1_opy_ (u"ࠫࡵࡿࡴࡩࡱࡱࠫᰒ"),
                bstack11l1ll1_opy_ (u"ࠬࡩ࡯ࡥࡧࠪᰓ"): self.code
            },
            bstack11l1ll1_opy_ (u"࠭ࡳࡤࡱࡳࡩࡸ࠭ᰔ"): self.scope,
            bstack11l1ll1_opy_ (u"ࠧࡵࡣࡪࡷࠬᰕ"): self.tags,
            bstack11l1ll1_opy_ (u"ࠨࡨࡵࡥࡲ࡫ࡷࡰࡴ࡮ࠫᰖ"): self.framework,
            bstack11l1ll1_opy_ (u"ࠩࡶࡸࡦࡸࡴࡦࡦࡢࡥࡹ࠭ᰗ"): self.started_at
        }
    def bstack11l11l11l1l_opy_(self):
        return {
         bstack11l1ll1_opy_ (u"ࠪࡱࡪࡺࡡࠨᰘ"): self.meta
        }
    def bstack11l11l111ll_opy_(self):
        return {
            bstack11l1ll1_opy_ (u"ࠫࡨࡻࡳࡵࡱࡰࡖࡪࡸࡵ࡯ࡒࡤࡶࡦࡳࠧᰙ"): {
                bstack11l1ll1_opy_ (u"ࠬࡸࡥࡳࡷࡱࡣࡳࡧ࡭ࡦࠩᰚ"): self.bstack11l11l1111l_opy_
            }
        }
    def bstack11l111ll1ll_opy_(self, bstack11l111lll11_opy_, details):
        step = next(filter(lambda st: st[bstack11l1ll1_opy_ (u"࠭ࡩࡥࠩᰛ")] == bstack11l111lll11_opy_, self.meta[bstack11l1ll1_opy_ (u"ࠧࡴࡶࡨࡴࡸ࠭ᰜ")]), None)
        step.update(details)
    def bstack1ll111l1l1_opy_(self, bstack11l111lll11_opy_):
        step = next(filter(lambda st: st[bstack11l1ll1_opy_ (u"ࠨ࡫ࡧࠫᰝ")] == bstack11l111lll11_opy_, self.meta[bstack11l1ll1_opy_ (u"ࠩࡶࡸࡪࡶࡳࠨᰞ")]), None)
        step.update({
            bstack11l1ll1_opy_ (u"ࠪࡷࡹࡧࡲࡵࡧࡧࡣࡦࡺࠧᰟ"): bstack1ll1l1ll_opy_()
        })
    def bstack11l11lll11_opy_(self, bstack11l111lll11_opy_, result, duration=None):
        bstack1l1ll11l11l_opy_ = bstack1ll1l1ll_opy_()
        if bstack11l111lll11_opy_ is not None and self.meta.get(bstack11l1ll1_opy_ (u"ࠫࡸࡺࡥࡱࡵࠪᰠ")):
            step = next(filter(lambda st: st[bstack11l1ll1_opy_ (u"ࠬ࡯ࡤࠨᰡ")] == bstack11l111lll11_opy_, self.meta[bstack11l1ll1_opy_ (u"࠭ࡳࡵࡧࡳࡷࠬᰢ")]), None)
            step.update({
                bstack11l1ll1_opy_ (u"ࠧࡧ࡫ࡱ࡭ࡸ࡮ࡥࡥࡡࡤࡸࠬᰣ"): bstack1l1ll11l11l_opy_,
                bstack11l1ll1_opy_ (u"ࠨࡦࡸࡶࡦࡺࡩࡰࡰࠪᰤ"): duration if duration else bstack11llll1lll1_opy_(step[bstack11l1ll1_opy_ (u"ࠩࡶࡸࡦࡸࡴࡦࡦࡢࡥࡹ࠭ᰥ")], bstack1l1ll11l11l_opy_),
                bstack11l1ll1_opy_ (u"ࠪࡶࡪࡹࡵ࡭ࡶࠪᰦ"): result.result,
                bstack11l1ll1_opy_ (u"ࠫ࡫ࡧࡩ࡭ࡷࡵࡩࠬᰧ"): str(result.exception) if result.exception else None
            })
    def add_step(self, bstack11l11l11lll_opy_):
        if self.meta.get(bstack11l1ll1_opy_ (u"ࠬࡹࡴࡦࡲࡶࠫᰨ")):
            self.meta[bstack11l1ll1_opy_ (u"࠭ࡳࡵࡧࡳࡷࠬᰩ")].append(bstack11l11l11lll_opy_)
        else:
            self.meta[bstack11l1ll1_opy_ (u"ࠧࡴࡶࡨࡴࡸ࠭ᰪ")] = [ bstack11l11l11lll_opy_ ]
    def bstack11l11l11l11_opy_(self):
        return {
            bstack11l1ll1_opy_ (u"ࠨࡷࡸ࡭ࡩ࠭ᰫ"): self.bstack111lll1l1l_opy_(),
            **self.bstack11l11l11ll1_opy_(),
            **self.bstack11l11l111l1_opy_(),
            **self.bstack11l11l11l1l_opy_()
        }
    def bstack11l11l1ll11_opy_(self):
        if not self.result:
            return {}
        data = {
            bstack11l1ll1_opy_ (u"ࠩࡩ࡭ࡳ࡯ࡳࡩࡧࡧࡣࡦࡺࠧᰬ"): self.bstack1l1ll11l11l_opy_,
            bstack11l1ll1_opy_ (u"ࠪࡨࡺࡸࡡࡵ࡫ࡲࡲࡤ࡯࡮ࡠ࡯ࡶࠫᰭ"): self.duration,
            bstack11l1ll1_opy_ (u"ࠫࡷ࡫ࡳࡶ࡮ࡷࠫᰮ"): self.result.result
        }
        if data[bstack11l1ll1_opy_ (u"ࠬࡸࡥࡴࡷ࡯ࡸࠬᰯ")] == bstack11l1ll1_opy_ (u"࠭ࡦࡢ࡫࡯ࡩࡩ࠭ᰰ"):
            data[bstack11l1ll1_opy_ (u"ࠧࡧࡣ࡬ࡰࡺࡸࡥࡠࡶࡼࡴࡪ࠭ᰱ")] = self.result.bstack111l1l1111_opy_()
            data[bstack11l1ll1_opy_ (u"ࠨࡨࡤ࡭ࡱࡻࡲࡦࠩᰲ")] = [{bstack11l1ll1_opy_ (u"ࠩࡥࡥࡨࡱࡴࡳࡣࡦࡩࠬᰳ"): self.result.bstack1l111111l11_opy_()}]
        return data
    def bstack11l11l11111_opy_(self):
        return {
            bstack11l1ll1_opy_ (u"ࠪࡹࡺ࡯ࡤࠨᰴ"): self.bstack111lll1l1l_opy_(),
            **self.bstack11l11l11ll1_opy_(),
            **self.bstack11l11l111l1_opy_(),
            **self.bstack11l11l1ll11_opy_(),
            **self.bstack11l11l11l1l_opy_()
        }
    def bstack11l111lll1_opy_(self, event, result=None):
        if result:
            self.result = result
        if bstack11l1ll1_opy_ (u"ࠫࡘࡺࡡࡳࡶࡨࡨࠬᰵ") in event:
            return self.bstack11l11l11l11_opy_()
        elif bstack11l1ll1_opy_ (u"ࠬࡌࡩ࡯࡫ࡶ࡬ࡪࡪࠧᰶ") in event:
            return self.bstack11l11l11111_opy_()
    def bstack111llll111_opy_(self):
        pass
    def stop(self, time=None, duration=None, result=None):
        self.bstack1l1ll11l11l_opy_ = time if time else bstack1ll1l1ll_opy_()
        self.duration = duration if duration else bstack11llll1lll1_opy_(self.started_at, self.bstack1l1ll11l11l_opy_)
        if result:
            self.result = result
class bstack11l1l11lll_opy_(bstack111ll1l1l1_opy_):
    def __init__(self, hooks=[], bstack11l11l1ll1_opy_={}, *args, **kwargs):
        self.hooks = hooks
        self.bstack11l11l1ll1_opy_ = bstack11l11l1ll1_opy_
        super().__init__(*args, **kwargs, bstack1l11l11l1_opy_=bstack11l1ll1_opy_ (u"࠭ࡴࡦࡵࡷ᰷ࠫ"))
    @classmethod
    def bstack11l111lllll_opy_(cls, scenario, feature, test, **kwargs):
        steps = []
        for step in scenario.steps:
            steps.append({
                bstack11l1ll1_opy_ (u"ࠧࡪࡦࠪ᰸"): id(step),
                bstack11l1ll1_opy_ (u"ࠨࡶࡨࡼࡹ࠭᰹"): step.name,
                bstack11l1ll1_opy_ (u"ࠩ࡮ࡩࡾࡽ࡯ࡳࡦࠪ᰺"): step.keyword,
            })
        return bstack11l1l11lll_opy_(
            **kwargs,
            meta={
                bstack11l1ll1_opy_ (u"ࠪࡪࡪࡧࡴࡶࡴࡨࠫ᰻"): {
                    bstack11l1ll1_opy_ (u"ࠫࡳࡧ࡭ࡦࠩ᰼"): feature.name,
                    bstack11l1ll1_opy_ (u"ࠬࡶࡡࡵࡪࠪ᰽"): feature.filename,
                    bstack11l1ll1_opy_ (u"࠭ࡤࡦࡵࡦࡶ࡮ࡶࡴࡪࡱࡱࠫ᰾"): feature.description
                },
                bstack11l1ll1_opy_ (u"ࠧࡴࡥࡨࡲࡦࡸࡩࡰࠩ᰿"): {
                    bstack11l1ll1_opy_ (u"ࠨࡰࡤࡱࡪ࠭᱀"): scenario.name
                },
                bstack11l1ll1_opy_ (u"ࠩࡶࡸࡪࡶࡳࠨ᱁"): steps,
                bstack11l1ll1_opy_ (u"ࠪࡩࡽࡧ࡭ࡱ࡮ࡨࡷࠬ᱂"): bstack11l1l11ll1l_opy_(test)
            }
        )
    def bstack11l111lll1l_opy_(self):
        return {
            bstack11l1ll1_opy_ (u"ࠫ࡭ࡵ࡯࡬ࡵࠪ᱃"): self.hooks
        }
    def bstack11l111llll1_opy_(self):
        if self.bstack11l11l1ll1_opy_:
            return {
                bstack11l1ll1_opy_ (u"ࠬ࡯࡮ࡵࡧࡪࡶࡦࡺࡩࡰࡰࡶࠫ᱄"): self.bstack11l11l1ll1_opy_
            }
        return {}
    def bstack11l11l11111_opy_(self):
        return {
            **super().bstack11l11l11111_opy_(),
            **self.bstack11l111lll1l_opy_()
        }
    def bstack11l11l11l11_opy_(self):
        return {
            **super().bstack11l11l11l11_opy_(),
            **self.bstack11l111llll1_opy_()
        }
    def bstack111llll111_opy_(self):
        return bstack11l1ll1_opy_ (u"࠭ࡴࡦࡵࡷࡣࡷࡻ࡮ࠨ᱅")
class bstack11l1l1111l_opy_(bstack111ll1l1l1_opy_):
    def __init__(self, hook_type, *args,bstack11l11l1ll1_opy_={}, **kwargs):
        self.hook_type = hook_type
        self.bstack11l11l1l1ll_opy_ = None
        self.bstack11l11l1ll1_opy_ = bstack11l11l1ll1_opy_
        super().__init__(*args, **kwargs, bstack1l11l11l1_opy_=bstack11l1ll1_opy_ (u"ࠧࡩࡱࡲ࡯ࠬ᱆"))
    def bstack11l111l111_opy_(self):
        return self.hook_type
    def bstack11l11l1l111_opy_(self):
        return {
            bstack11l1ll1_opy_ (u"ࠨࡪࡲࡳࡰࡥࡴࡺࡲࡨࠫ᱇"): self.hook_type
        }
    def bstack11l11l11111_opy_(self):
        return {
            **super().bstack11l11l11111_opy_(),
            **self.bstack11l11l1l111_opy_()
        }
    def bstack11l11l11l11_opy_(self):
        return {
            **super().bstack11l11l11l11_opy_(),
            bstack11l1ll1_opy_ (u"ࠩࡷࡩࡸࡺ࡟ࡳࡷࡱࡣ࡮ࡪࠧ᱈"): self.bstack11l11l1l1ll_opy_,
            **self.bstack11l11l1l111_opy_()
        }
    def bstack111llll111_opy_(self):
        return bstack11l1ll1_opy_ (u"ࠪ࡬ࡴࡵ࡫ࡠࡴࡸࡲࠬ᱉")
    def bstack11l1l11l11_opy_(self, bstack11l11l1l1ll_opy_):
        self.bstack11l11l1l1ll_opy_ = bstack11l11l1l1ll_opy_