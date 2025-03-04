from rvv.base import BaseRVV

class FWiden(BaseRVV):
    
    def vfwadd_vv(self, vd, op1, op2, masked=False):
        vvd, vop1, vop2, mask = self._init_ops(vd, op1, op2, 'wvv', 'fff', masked)
        vvd[mask] = (self._WSEWC.fdtype(vop1) + self._WSEWC.fdtype(vop2))[mask]
        self._post_op()
    
    def vfwadd_vf(self, vd, op1, op2, masked=False):
        vvd, vop1, fop2, mask = self._init_ops(vd, op1, op2, 'wvf', 'fff', masked)
        vvd[mask] = (self._WSEWC.fdtype(vop1) + self._WSEWC.fdtype(fop2))[mask]
        self._post_op()
    
    def vfwadd_wv(self, vd, op1, op2, masked=False):
        vvd, vop1, vop2, mask = self._init_ops(vd, op1, op2, 'wwv', 'fff', masked)
        vvd[mask] = (vop1 + self._WSEWC.fdtype(vop2))[mask]
        self._post_op()
    
    def vfwadd_wf(self, vd, op1, op2, masked=False):
        vvd, vop1, fop2, mask = self._init_ops(vd, op1, op2, 'wwf', 'fff', masked)
        vvd[mask] = (vop1 + self._WSEWC.fdtype(fop2))[mask]
        self._post_op()
    
    def vfwsub_vv(self, vd, op1, op2, masked=False):
        vvd, vop1, vop2, mask = self._init_ops(vd, op1, op2, 'wvv', 'fff', masked)
        vvd[mask] = (self._WSEWC.fdtype(vop1) - self._WSEWC.fdtype(vop2))[mask]
        self._post_op()
    
    def vfwsub_vf(self, vd, op1, op2, masked=False):
        vvd, vop1, fop2, mask = self._init_ops(vd, op1, op2, 'wvf', 'fff', masked)
        vvd[mask] = (self._WSEWC.fdtype(vop1) - self._WSEWC.fdtype(fop2))[mask]
        self._post_op()
    
    def vfwsub_wv(self, vd, op1, op2, masked=False):
        vvd, vop1, vop2, mask = self._init_ops(vd, op1, op2, 'wwv', 'fff', masked)
        vvd[mask] = (vop1 - self._WSEWC.fdtype(vop2))[mask]
        self._post_op()
    
    def vfwsub_wf(self, vd, op1, op2, masked=False):
        vvd, vop1, fop2, mask = self._init_ops(vd, op1, op2, 'wwf', 'fff', masked)
        vvd[mask] = (vop1 - self._WSEWC.fdtype(fop2))[mask]
        self._post_op()
    
    def vfwmul_vv(self, vd, op1, op2, masked=False):
        vvd, vop1, vop2, mask = self._init_ops(vd, op1, op2, 'wvv', 'fff', masked)
        vvd[mask] = (self._WSEWC.fdtype(vop1) * self._WSEWC.fdtype(vop2))[mask]
        self._post_op()
    
    def vfwmul_vf(self, vd, op1, op2, masked=False):
        vvd, vop1, fop2, mask = self._init_ops(vd, op1, op2, 'wvf', 'fff', masked)
        vvd[mask] = (self._WSEWC.fdtype(vop1) * self._WSEWC.fdtype(fop2))[mask]
        self._post_op()
    
    def vfwmacc_vv(self, vd, op1, op2, masked=False):
        vvd, vop1, vop2, mask = self._init_ops(vd, op1, op2, 'wvv', 'fff', masked)
        vvd[mask] = ((self._WSEWC.fdtype(vop1) * self._WSEWC.fdtype(vop2)) + vd)[mask]
        self._post_op()
    
    def vfwmacc_vf(self, vd, op1, op2, masked=False):
        vvd, fop1, vop2, mask = self._init_ops(vd, op1, op2, 'wfv', 'fff', masked)
        vvd[mask] = ((self._WSEWC.fdtype(fop1) * self._WSEWC.fdtype(vop2)) + vd)[mask]
        self._post_op()
    
    def vfwnmacc_vv(self, vd, op1, op2, masked=False):
        vvd, vop1, vop2, mask = self._init_ops(vd, op1, op2, 'wvv', 'fff', masked)
        vvd[mask] = (-(self._WSEWC.fdtype(vop1) * self._WSEWC.fdtype(vop2)) - vd)[mask]
        self._post_op()
    
    def vfwnmacc_vf(self, vd, op1, op2, masked=False):
        vvd, fop1, vop2, mask = self._init_ops(vd, op1, op2, 'wfv', 'fff', masked)
        vvd[mask] = (-(self._WSEWC.fdtype(fop1) * self._WSEWC.fdtype(vop2)) - vd)[mask]
        self._post_op()
    
    def vfwmsac_vv(self, vd, op1, op2, masked=False):
        vvd, vop1, vop2, mask = self._init_ops(vd, op1, op2, 'wvv', 'fff', masked)
        vvd[mask] = ((self._WSEWC.fdtype(vop1) * self._WSEWC.fdtype(vop2)) - vd)[mask]
        self._post_op()
    
    def vfwmsac_vf(self, vd, op1, op2, masked=False):
        vvd, fop1, vop2, mask = self._init_ops(vd, op1, op2, 'wfv', 'fff', masked)
        vvd[mask] = ((self._WSEWC.fdtype(fop1) * self._WSEWC.fdtype(vop2)) - vd)[mask]
        self._post_op()
    
    def vfwnmsac_vv(self, vd, op1, op2, masked=False):
        vvd, vop1, vop2, mask = self._init_ops(vd, op1, op2, 'wvv', 'fff', masked)
        vvd[mask] = (-(self._WSEWC.fdtype(vop1) * self._WSEWC.fdtype(vop2)) + vd)[mask]
        self._post_op()
    
    def vfwnmsac_vf(self, vd, op1, op2, masked=False):
        vvd, fop1, vop2, mask = self._init_ops(vd, op1, op2, 'wfv', 'fff', masked)
        vvd[mask] = (-(self._WSEWC.fdtype(fop1) * self._WSEWC.fdtype(vop2)) + vd)[mask]
        self._post_op()
    
    
