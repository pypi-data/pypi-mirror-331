from typing import Callable

import numpy as np
from joblib import Parallel, delayed
from numpy.typing import ArrayLike
from sklearn.base import clone
from sklearn.ensemble._base import _partition_estimators
from sklearn.model_selection import StratifiedKFold, train_test_split

from ..tree._classes import DTYPE
from .forest import ForestTestResult, build_oob_forest
from .permuteforest import PermutationHonestForestClassifier
from .utils import METRIC_FUNCTIONS, POSITIVE_METRICS


def _parallel_predict_proba(predict_proba, X, indices_test):
    """
    This is a utility function for joblib's Parallel.

    It can't go locally in ForestClassifier or ForestRegressor, because joblib
    complains that it cannot pickle it when placed there.
    """
    # each tree predicts proba with a list of output (n_samples, n_classes[i])
    prediction = predict_proba(X[indices_test, :], check_input=False)
    return prediction


def build_permutation_forest(
    est,
    perm_est,
    X,
    y,
    covariate_index=None,
    metric="s@98",
    n_repeats=500,
    verbose=False,
    seed=None,
    return_posteriors=True,
    **metric_kwargs,
):
    """Build a hypothesis testing forest using a permutation-forest approach.

    The permutation-forest approach stems from standard permutaiton-testing, where
    each forest is trained on a new permutation of the dataset. The original test
    statistic is computed on the original data. Then the pvalue is computed
    by comparing the original test statistic to the null distribution of the
    test statistic computed from the permuted forests.

    Parameters
    ----------
    est : Forest
        The type of forest to use. Must be enabled with ``bootstrap=True``.
    perm_est : Forest
        The forest to use for the permuted dataset. Should be
        ``PermutationHonestForestClassifier``.
    X : ArrayLike of shape (n_samples, n_features)
        Data.
    y : ArrayLike of shape (n_samples, n_outputs)
        Binary target, so ``n_outputs`` should be at most 1.
    covariate_index : ArrayLike, optional of shape (n_covariates,)
        The index array of covariates to shuffle, by default None.
    metric : str, optional
        The metric to compute, by default "s@98", for sensitivity at
        98% specificity.
    n_repeats : int, optional
        Number of times to bootstrap sample the two forests to construct
        the null distribution, by default 10000. The construction of the
        null forests will be parallelized according to the ``n_jobs``
        argument of the ``est`` forest.
    verbose : bool, optional
        Verbosity, by default False.
    seed : int, optional
        Random seed, by default None.
    return_posteriors : bool, optional
        Whether or not to return the posteriors, by default True.
    **metric_kwargs : dict, optional
        Additional keyword arguments to pass to the metric function.

    Returns
    -------
    observe_stat : float
        The test statistic. To compute the test statistic, take
        ``permute_stat_`` and subtract ``observe_stat_``.
    pvalue : float
        The p-value of the test statistic.
    orig_forest_proba : ArrayLike of shape (n_estimators, n_samples, n_outputs)
        The predicted posterior probabilities for each estimator on their
        out of bag samples.
    perm_forest_proba : ArrayLike of shape (n_estimators, n_samples, n_outputs)
        The predicted posterior probabilities for each of the permuted estimators
        on their out of bag samples.

    References
    ----------
    .. footbibliography::
    """
    rng = np.random.default_rng(seed)
    metric_func: Callable[[ArrayLike, ArrayLike], float] = METRIC_FUNCTIONS[metric]

    if covariate_index is None:
        covariate_index = np.arange(X.shape[1], dtype=int)

    if not isinstance(perm_est, PermutationHonestForestClassifier):
        raise RuntimeError(
            f"Permutation forest must be a PermutationHonestForestClassifier, got {type(perm_est)}"
        )

    # train the original forest on unpermuted data
    est, orig_forest_proba = build_oob_forest(est, X, y, verbose=verbose)
    y_pred_proba_orig = np.nanmean(orig_forest_proba, axis=0)
    observe_test_stat = metric_func(y, y_pred_proba_orig, **metric_kwargs)

    # get the number of jobs
    index_arr = np.arange(X.shape[0], dtype=int).reshape(-1, 1)

    # train many null forests
    X_perm = X.copy()
    null_dist = []
    for _ in range(n_repeats):
        rng.shuffle(index_arr)
        perm_X_cov = X_perm[index_arr, covariate_index]
        X_perm[:, covariate_index] = perm_X_cov

        #
        perm_est = clone(perm_est)
        perm_est.set_params(random_state=rng.integers(0, np.iinfo(np.int32).max))

        perm_est, perm_forest_proba = build_oob_forest(
            perm_est, X_perm, y, verbose=verbose, covariate_index=covariate_index
        )

        y_pred_proba_perm = np.nanmean(perm_forest_proba, axis=0)
        permute_stat = metric_func(y, y_pred_proba_perm, **metric_kwargs)
        null_dist.append(permute_stat)

    # compute pvalue, which note is opposite that of the Coleman approach, since
    # we are testing if the null distribution results in a test statistic greater
    if metric in POSITIVE_METRICS:
        pvalue = (1 + (null_dist >= observe_test_stat).sum()) / (1 + n_repeats)
    else:
        pvalue = (1 + (null_dist <= observe_test_stat).sum()) / (1 + n_repeats)

    forest_result = ForestTestResult(observe_test_stat, permute_stat, None, pvalue, null_dist)
    if return_posteriors:
        return forest_result, orig_forest_proba, perm_forest_proba
    else:
        return forest_result


def build_cv_forest(
    est,
    X,
    y,
    cv=5,
    test_size=0.2,
    verbose=False,
    return_indices=False,
    seed=None,
):
    """Build a hypothesis testing forest using using cross-validation.

    Parameters
    ----------
    est : Forest
        The type of forest to use. Must be enabled with ``bootstrap=True``.
    X : ArrayLike of shape (n_samples, n_features)
        Data.
    y : ArrayLike of shape (n_samples, n_outputs)
        Binary target, so ``n_outputs`` should be at most 1.
    cv : int, optional
        Number of folds to use for cross-validation, by default 5.
    test_size : float, optional
        Proportion of samples per tree to use for the test set, by default 0.2.
    verbose : bool, optional
        Verbosity, by default False.
    return_indices : bool, optional
        Whether or not to return the train and test indices, by default False.
    seed : int, optional
        Random seed, by default None.

    Returns
    -------
    est : Forest
        Fitted forest.
    all_proba_list : list of ArrayLike of shape (n_estimators, n_samples, n_outputs)
        The predicted posterior probabilities for each estimator on their
        out of bag samples. Length of list is equal to the number of splits.
    train_idx_list : list of ArrayLike of shape (n_samples,)
        The training indices for each split.
    test_idx_list : list of ArrayLike of shape (n_samples,)
        The testing indices for each split.
    """
    X = X.astype(np.float32)
    if cv is not None:
        cv = StratifiedKFold(n_splits=cv, shuffle=True, random_state=seed)
        n_splits = cv.get_n_splits()
        train_idx_list, test_idx_list = [], []
        for train_idx, test_idx in cv.split(X, y):
            train_idx_list.append(train_idx)
            test_idx_list.append(test_idx)
    else:
        n_samples_idx = np.arange(len(y))
        train_idx, test_idx = train_test_split(
            n_samples_idx, test_size=test_size, random_state=seed, shuffle=True, stratify=y
        )

        train_idx_list = [train_idx]
        test_idx_list = [test_idx]
        n_splits = 1

    est_list = []
    all_proba_list = []
    for isplit in range(n_splits):
        # clone the estimator to remove all fitted attributes
        est = clone(est)

        X_train, y_train = X[train_idx_list[isplit], :], y[train_idx_list[isplit]]
        # X_test = X[test_idx_list[isplit], :]

        # build forest
        est.fit(X_train, y_train)

        # now evaluate
        X = est._validate_X_predict(X)

        # if we trained a binning tree, then we should re-bin the data
        # XXX: this is inefficient and should be improved to be in line with what
        # the Histogram Gradient Boosting Tree does, where the binning thresholds
        # are passed into the tree itself, thus allowing us to set the node feature
        # value thresholds within the tree itself.
        if est.max_bins is not None:
            X = est._bin_data(X, is_training_data=False).astype(DTYPE)

        # Assign chunk of trees to jobs
        n_jobs, _, _ = _partition_estimators(est.n_estimators, est.n_jobs)

        # avoid storing the output of every estimator by summing them here
        all_proba = Parallel(n_jobs=n_jobs, verbose=verbose)(
            delayed(_parallel_predict_proba)(e.predict_proba, X, test_idx_list[isplit])
            for e in est.estimators_
        )
        posterior_arr = np.full((est.n_estimators, X.shape[0], est.n_classes_), np.nan)
        for itree, (proba) in enumerate(all_proba):
            posterior_arr[itree, test_idx_list[isplit], ...] = proba.reshape(-1, est.n_classes_)

        all_proba_list.append(posterior_arr)
        est_list.append(est)

    if return_indices:
        return est_list, all_proba_list, train_idx_list, test_idx_list

    return est_list, all_proba_list
