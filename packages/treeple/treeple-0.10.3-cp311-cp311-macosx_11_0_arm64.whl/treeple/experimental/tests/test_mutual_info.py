import numpy as np


def nonlinear_gaussian_with_additive_noise():
    """Nonlinear no-noise function with additive Gaussian noise.

    See: https://github.com/BiuBiuBiLL/NPEET_LNC/issues/4
    """
    # first simulate multivariate Gaussian without noise

    # then add the noise

    # compute MI by computing the H(Y|X) and H(X)
    # H(Y|X) = np.log(noise_std)
    # H(X) = kNN K-L estimate with large # of samples
    pass


def main():
    d1 = [1, 1, 0]
    d2 = [1, 0, 1]
    d3 = [0, 1, 1]
    mat = [d1, d2, d3]
    tmat = np.transpose(mat)
    diag = [[3, 0, 0], [0, 1, 0], [0, 0, 1]]
    # mean = np.array([0, 0, 0])
    cov = np.dot(tmat, np.dot(diag, mat))
    print("covariance matrix")
    print(cov)
    print(tmat)


def test_mi():
    d1 = [1, 1, 0]
    d2 = [1, 0, 1]
    d3 = [0, 1, 1]
    mat = [d1, d2, d3]
    tmat = np.transpose(mat)
    diag = [[3, 0, 0], [0, 1, 0], [0, 0, 1]]
    # mean = np.array([0, 0, 0])
    cov = np.dot(tmat, np.dot(diag, mat))
    print("covariance matrix")
    print(cov)
    trueent = -0.5 * (3 + np.log(8.0 * np.pi * np.pi * np.pi * np.linalg.det(cov)))
    trueent += -0.5 * (1 + np.log(2.0 * np.pi * cov[2][2]))  # z sub
    trueent += 0.5 * (
        2
        + np.log(
            4.0 * np.pi * np.pi * np.linalg.det([[cov[0][0], cov[0][2]], [cov[2][0], cov[2][2]]])
        )
    )  # xz sub
    trueent += 0.5 * (
        2
        + np.log(
            4.0 * np.pi * np.pi * np.linalg.det([[cov[1][1], cov[1][2]], [cov[2][1], cov[2][2]]])
        )
    )  # yz sub
    print("true CMI(x:y|x)", trueent / np.log(2))
