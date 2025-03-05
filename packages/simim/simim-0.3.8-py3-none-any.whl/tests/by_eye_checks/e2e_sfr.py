import matplotlib.pyplot as plt
import numpy as np

from simim.galprops.sfr_bethermin17 import bethermin17_base
from simim.galprops.sfr_ir import g13irlf_base

b17 = bethermin17_base('UniverseMachine-BolshoiPlanck',
                       sm_comp=True,
                       sm_remake=False,
                       sm_haloprop='mass',
                       sm_halomassmin=1e10)


g13 = g13irlf_base('UniverseMachine-BolshoiPlanck',
                   comp=True,remake=False,haloprop='mass')


### Reproduce G13 figure 9 to verify implementation ###
fig, axes = plt.subplots(2,1,figsize=(4,4))
fig.subplots_adjust(hspace=0)
axes[0].grid()
axes[1].grid()

axes[0].set(ylabel='log L$_*$',xlim=(0,4),ylim=(9.6,12.6))
plt.setp(axes[0].get_xticklabels(),visible=False)
axes[1].set(xlabel='z',ylabel='log $\Phi_*$',xlim=(0,4),ylim=(-4,-2))

z=np.linspace(0,4)
p,l,a,s = g13.get_irlf_pars(z)
axes[0].plot(z,np.log10(l),'k-')
axes[0].errorbar([0.15,0.375,0.525,0.7,0.9,1.1,1.45,1.85,2.25,2.75,3.6],
                 [10.12,10.41,10.55,10.71,10.97,11.13,11.37,11.50,11.60,11.92,11.90],
                 [0.16,0.03,0.03,0.03,0.04,0.04,0.03,0.03,0.03,0.08,0.16],
                 color='.5',marker='o',capsize=3,ls='none')
axes[1].plot(z,np.log10(p),'k-')
axes[1].errorbar([0.15,0.375,0.525,0.7,0.9,1.1,1.45,1.85,2.25,2.75,3.6],
                 [-2.29,-2.31,-2.35,-2.35,-2.40,-2.43,-2.70,-3.00,-3.01,-3.27,-3.74],
                 [0.06,0.03,0.05,0.06,0.05,0.04,0.04,0.03,0.11,0.18,0.30],
                 color='.5',marker='o',capsize=3,ls='none')
plt.show()