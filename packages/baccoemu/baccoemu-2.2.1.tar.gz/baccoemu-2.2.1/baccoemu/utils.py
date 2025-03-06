import numpy as np
import copy
import progressbar
import hashlib
from tensorflow.keras import backend as K


def _md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def _transform_space(x, space_rotation=False, rotation=None, bounds=None):
    """Normalize coordinates to [0,1] intervals and if necessary apply a
    rotation

    :param x: coordinates in parameter space
    :type x: ndarray
    :param space_rotation: whether to apply the rotation matrix defined through
                           the rotation keyword, defaults to False
    :type space_rotation: bool, optional
    :param rotation: rotation matrix, defaults to None
    :type rotation: ndarray, optional
    :param bounds: ranges within which the emulator hypervolume is defined,
                   defaults to None
    :type bounds: ndarray, optional
    :return: normalized and (if required) rotated coordinates
    :rtype: ndarray
    """
    if space_rotation:
        # Get x into the eigenbasis
        R = rotation['rotation_matrix'].T
        xR = copy.deepcopy(np.array([np.dot(R, xi)
                                     for xi in x]))
        xR = xR - rotation['rot_points_means']
        xR = xR/rotation['rot_points_stddevs']
        return xR
    else:
        return (x - bounds[:, 0])/(bounds[:, 1] - bounds[:, 0])


def accuracy_exp_002(y_true, y_pred):
    dataset = K.abs(K.exp(y_pred)/K.exp(y_true)-1)
    tot = dataset >= 0
    sel = dataset <= 0.002
    return K.shape(dataset[sel])[0] / K.shape(dataset[tot])[0]


def accuracy_exp_005(y_true, y_pred):
    dataset = K.abs(K.exp(y_pred)/K.exp(y_true)-1)
    tot = dataset >= 0
    sel = dataset <= 0.005
    return K.shape(dataset[sel])[0] / K.shape(dataset[tot])[0]


def accuracy_exp_01(y_true, y_pred):
    dataset = K.abs(K.exp(y_pred)/K.exp(y_true)-1)
    tot = dataset >= 0
    sel = dataset <= 0.01
    return K.shape(dataset[sel])[0] / K.shape(dataset[tot])[0]


def mean_absolute_exp_percentage_error(y_true, y_pred):
    diff = K.abs((K.exp(y_true) - K.exp(y_pred)) / K.clip(K.exp(y_true),
                                                          K.epsilon(), None))
    return K.mean(diff, axis=-1)


class MyProgressBar():
    def __init__(self):
        self.pbar = None

    def __call__(self, block_num, block_size, total_size):
        if not self.pbar:
            self.pbar = progressbar.ProgressBar(maxval=total_size)
            self.pbar.start()

        downloaded = block_num * block_size
        if downloaded < total_size:
            self.pbar.update(downloaded)
        else:
            self.pbar.finish()

def pkmulti(kk, mu, pk2d, nmodes=None, mode='reimann_sum', nthreads=None, verbose=None, pmulti_interp='polyfit', return_ell6=False):
    import scipy

    if mode not in ['reimann_sum', 'gl_quad']:
        raise ValueError('Please, specify a mode between reimann_sum and gl_quad')
    mode = {'reimann_sum' : 0, 'gl_quad' : 1}[mode]

    if nmodes is None:
        nmodes = np.repeat(1,len(kk))



    if return_ell6:
        num_mult = 4
    else:
        num_mult = 3
    moments = np.zeros((num_mult, len(kk)))
    p2ds = np.zeros((len(mu), len(kk)))
    No = 8
    p16_roots = [
        0.09501251, 0.28160355, 0.45801678, 0.61787624,
        0.75540441, 0.8656312, 0.94457502, 0.98940093]

    p16_w = [
        0.189450610455069,
        0.182603415044924,
        0.169156519395003,
        0.149595988816577,
        0.124628971255534,
        0.095158511682493,
        0.062253523938648,
        0.027152459411754]

    for ik in range(len(kk)):
        if nmodes[ik]>0:
            mask = pk2d[:, ik] != 0.0
            know = kk[ik]
            npoints = sum(mask)
            if npoints > 1:
                deg = np.min((4,npoints))
                cc = np.polyfit(mu[mask], pk2d[:, ik][mask], deg=deg)
                pmu_lin_interp = scipy.interpolate.interp1d(
                    mu[mask], pk2d[:, ik][mask], kind='linear')

                def _p_at_mu(mui):
                    if pmulti_interp == 'linear':
                        return pmu_lin_interp(mui)
                    elif pmulti_interp == 'polyfit':
                        return np.sum([cc[i] * mui**(deg - i)
                                        for i in range(len(cc))], axis=0)
                    elif pmulti_interp == 'mix':
                        if know < 0.5 * knl:
                            return np.sum([cc[i] * mui**(deg - i)
                                            for i in range(len(cc))], axis=0)
                        else:
                            return pmu_lin_interp(mui)
                    else:
                        raise ValueError(
                            'Illegal choice for pmulti_interp: choose between linear, polyfit and mix')

                for ell in range(num_mult):
                    result = 0.0
                    for io in range(No):
                        result += p16_w[io] * \
                            p16_roots[io]**(2 * ell) * _p_at_mu(p16_roots[io])
                    moments[ell, ik] = result
                p2ds[:, ik] = _p_at_mu(mu)
            else:
                logger.info(
                    'pk multipoles at k {0} set to zero: it seems you have a lot of bins for this grid size'.format(know))


        multi = np.zeros((num_mult, len(kk)))
        multi[0, :] = moments[0, :]
        multi[1, :] = (5.0 / 2.0) * (3.0 * moments[1, :] - moments[0, :])
        multi[2, :] = (9.0 / 8.0) * (35 * moments[2, :] - 30.0 *
                                 moments[1, :] + 3.0 * moments[0, :])
        if return_ell6:
            multi[3, :] = (13.0 / 32.0) * (231 * moments[3, :] - 315.0 *
                                 moments[2, :] + 105.0 * moments[1, :] - 5.0 * moments[0, :])

    return multi, p2ds, moments

class coevolution_relations:
    """ Coevolution reltions from https://arxiv.org/abs/2110.05408
    """
    def halo_b1L_nu(nu):
        return -0.00951 * nu**3 + 0.4873 * nu**2 - 0.1395 * nu - 0.4383

    def halo_b2L_b1L(b1L):
        return -0.09143 * b1L**3 + 0.7093 * b1L**2 - 0.2607 * b1L - 0.3469

    def halo_bs2L_b1L(b1L):
        return 0.02278 * b1L**3 - 0.005503 * b1L**2 - 0.5904 * b1L - 0.1174

    def halo_blL_b1L(b1L):
        return -0.6971 * b1L**3 + 0.7892 * b1L**2 + 0.5882 * b1L - 0.1072

    def gal_b2L_b1L(b1L):
        return 0.01677 * b1L**3 - 0.005116 * b1L**2 + 0.4279 * b1L - 0.1635

    def gal_bs2L_b1L(b1L):
        return -0.3605 * b1L**3 + 0.5649 * b1L**2 - 0.1412 * b1L - 0.01318

    def gal_blL_b1L(b1L):
        return 0.2298 * b1L**3 - 2.096 * b1L**2 + 0.7816 * b1L - 0.1545
