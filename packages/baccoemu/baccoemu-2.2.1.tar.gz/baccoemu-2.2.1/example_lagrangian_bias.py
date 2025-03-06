import baccoemu
import numpy as np
import matplotlib.pyplot as plt

pars = {
    'omega_cold' : 0.32,
    'omega_baryon' : 0.05,
    'hubble' : 0.67,
    'ns' : 0.96,
    'sigma8_cold' : 0.83,
    'neutrino_mass' : 0.0,
    'w0' : -1,
    'wa' : 0,
    'expfactor' : 1
}

# load the emulators
lbias = baccoemu.Lbias_expansion()

#####################################################################################################

k, pnn = lbias.get_nonlinear_pnn(k=None, **pars) # this calls the emulator of the nonlinear 15 lagrangian bias expansion terms
k, plpt = lbias.get_lpt_pk(k=k, **pars) # this calls the emulator of the LPT-predicted 15 lagrangian bias expansion terms

fig, ax = plt.subplots(1, 3, figsize=(18, 8), sharey=True, gridspec_kw={'wspace' : 0})

labels = lbias.lb_term_labels

for i in range(len(pnn)):
    axi = np.int(i / 5)
    ax[axi].loglog(k, abs(pnn[i]), lw=3, alpha=0.5, color=f'C{i}', label=labels[i])
    ax[axi].loglog(k, abs(plpt[i]), lw=3, ls='--', alpha=0.5, color=f'C{i}')
ax[0].set_xlabel(r'$k \,\, [h \,\, \mathrm{Mpc}^{-1}]$', fontsize=20)
ax[1].set_xlabel(r'$k \,\, [h \,\, \mathrm{Mpc}^{-1}]$', fontsize=20)
ax[2].set_xlabel(r'$k \,\, [h \,\, \mathrm{Mpc}^{-1}]$', fontsize=20)
ax[0].set_ylabel(r'$|P_{ij}| \,\, [h^{-3} \,\, \mathrm{Mpc}^3]$', fontsize=20)
_l = [plt.Line2D([], [], lw=3, ls='-', color='k', label='LPT'), plt.Line2D([], [], lw=3, ls='--', color='k', label='nonlinear')]
_l = ax[0].legend(handles=_l, loc='lower right')
ax[0].add_artist(_l)
for _ax in ax:
    _ax.legend()
plt.show()

#####################################################################################################

# this is a quick way to get the galaxy-galaxy and galaxy-matter power spectra, given a set of bias
# and cosmological parameters (it internally combines the 15 terms)

bias = [0.75, 0.25, 0.1, 1.4] # b1, b2, bs2, blaplacian
kgal, pgalauto, pgalcross = lbias.get_galaxy_real_pk(bias=bias, k=None, **pars)

fig, ax = plt.subplots(1, 4, figsize=(15, 5), sharey=True, gridspec_kw={'wspace' : 0})

bb = [np.linspace(0.3, 1.7, 5), np.linspace(-0.6, 0.6, 5), np.linspace(-0.6, 0.6, 5), np.linspace(-20, 1, 5)]
labels = [r'$b_{1}$', r'$b_{2}$', r'$b_{s^2}$', r'$b_{\nabla^2\delta}$']

for i, bbi in enumerate(bb):
    for bi in bbi:
        this_bias = np.copy(bias)
        this_bias[i] = bi
        res = lbias.get_galaxy_real_pk(bias=this_bias, k=None, **pars)
        ax[i].loglog(kgal, res[1], lw=3, alpha=0.5)
        ax[i].set_xlabel(r'$k \,\, [h \,\, \mathrm{Mpc}^{-1}]$', fontsize=20)
        ax[i].set_title(labels[i], fontsize=20)
ax[0].set_ylabel(r'$P(k) \,\, [h^{-3} \,\, \mathrm{Mpc}^3]$', fontsize=20)
plt.show()
