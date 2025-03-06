import matplotlib.pyplot as plt
import numpy as np
import baccoemu

#Calling baccoemu to compute the nonlinear power spectrum

params = {
    'omega_cold'  :  0.315,
    'A_s'            :  2.e-9,
    'omega_baryon'  :  0.05,
    'ns'            :  0.96,
    'hubble'        :  0.67,
    'neutrino_mass' :  0.0,
    'w0'            : -1.0,
    'wa'            :  0.0,
    'expfactor'     :  1
}

emulator = baccoemu.Matter_powerspectrum()
k, Q = emulator.get_nonlinear_boost(**params)

print('# k        Q(k)')
for _k, _Q in zip(k, Q):
    print('{:.5f}    {:.5f}'.format(_k, _Q))

k, pk = emulator.get_linear_pk(k=k, **params)
k, pknl = emulator.get_nonlinear_pk(baryonic_boost=False, **params)

plt.loglog(k, pk, label='emulated linear')
plt.loglog(k, pknl, label='emulated nonlinear')
plt.xlabel(r'$k \, [h \, \mathrm{Mpc}^{-1}]$')
plt.ylabel(r'$P(k) \, [h^{-3} \, \mathrm{Mpc}^{3}]$')
plt.legend()
plt.show()

#Iincluding baryonic effects in the non linear power spectrum

bcm_params = {
    'M_c'           :  14,
    'eta'           : -0.3,
    'beta'          : -0.22,
    'M1_z0_cen'     : 10.5,
    'theta_out'     : 0.25,
    'theta_inn'     : -0.86,
    'M_inn'         : 13.4
}


k, pknl_b = emulator.get_nonlinear_pk(baryonic_boost=True, **{**params, **bcm_params})

plt.loglog(k, pk, label='emulated linear')
plt.loglog(k, pknl, label='emulated nonlinear')
plt.loglog(k, pknl_b, label='emulated nonlinear with baryons')
plt.xlabel(r'$k \, [h \, \mathrm{Mpc}^{-1}]$')
plt.ylabel(r'$P(k) \, [h^{-3} \, \mathrm{Mpc}^{3}]$')
plt.legend()
plt.show()

#Plotting the baryonic boost function and the fraction of gas as a function of the halo mass.
k, S = emulator.get_baryonic_boost(**{**params,**bcm_params})

print('# k        S(k)')
for _k, _S in zip(k, S):
    print('{:.5f}    {:.5f}'.format(_k, _S))


M_200 = np.logspace(12,15)
fracs = baccoemu.get_baryon_fractions(M_200, **{**params,**bcm_params})

fig, ax = plt.subplots(1,2, figsize=(12,6))

ax[0].semilogx(k, S)
ax[0].axhline(1,c='k')

ax[1].semilogx(M_200, fracs['bo_gas'], label='bound gas fraction')
ax[1].semilogx(M_200, fracs['ej_gas'], label='ejected gas fraction')
ax[1].axhline(fracs['baryon'],c='k',label=r'$\Omega_b/\Omega_m$')
ax[0].set_xlabel(r'$k \, [h \, \mathrm{Mpc}^{-1}]$')
ax[0].set_ylabel(r'$S(k)$')
ax[1].set_xlabel(r'$M_{200} \, [h^{-1} \, \mathrm{M_{\odot}}]$')
ax[1].set_ylabel(r'$f_{gas}(M)$')
ax[1].legend(prop={'size':12})
plt.tight_layout()
plt.show()
