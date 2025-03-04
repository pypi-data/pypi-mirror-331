[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![CircleCI](https://circleci.com/gh/neurodata/treeple/tree/main.svg?style=svg)](https://circleci.com/gh/neurodata/treeple/tree/main)
[![Main](https://github.com/neurodata/treeple/actions/workflows/main.yml/badge.svg?branch=main)](https://github.com/neurodata/treeple/actions/workflows/main.yml)
[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)
[![codecov](https://codecov.io/gh/neurodata/treeple/branch/main/graph/badge.svg?token=H1reh7Qwf4)](https://codecov.io/gh/neurodata/treeple)
[![PyPI Download count](https://img.shields.io/pypi/dm/treeple.svg)](https://pypistats.org/packages/treeple)
[![Latest PyPI release](https://img.shields.io/pypi/v/treeple.svg)](https://pypi.org/project/treeple/)
[![DOI](https://zenodo.org/badge/491260497.svg)](https://zenodo.org/doi/10.5281/zenodo.8412279)

treeple
=======

treeple is a scikit-learn compatible API for building state-of-the-art decision trees. These include unsupervised trees, oblique trees, uncertainty trees, quantile trees and causal trees.

Tree-models have withstood the test of time, and are consistently used for modern-day data science and machine learning applications. They especially perform well when there are limited samples for a problem and are flexible learners that can be applied to a wide variety of different settings, such as tabular, images, time-series, genomics, EEG data and more.

Note that this package was originally named ``scikit-tree`` but was renamed to ``treeple`` after version 0.8.0. version <0.8.0 is still available at <https://pypi.org/project/scikit-tree/>.

Documentation
=============

See here for the documentation for our dev version: <https://docs.neurodata.io/treeple/dev/index.html>

Is treeple useful for me?
=========================

1. If you use decision tree models (random forest, extra trees, isolation forests, etc.) in your work, treeple is a good package to try out. We have a variety of better tree models that are not available in scikit-learn, and we are always looking for new tree models to implement. For example, oblique decision trees are in general better than their axis-aligned counterparts.

2. If you are interested in extending the decision tree API in scikit-learn, treeple is a good package to try out. We have a variety of internal APIs that are not available in scikit-learn, and are able to support new decision tree models easier.

Why oblique trees and why trees beyond those in scikit-learn?
=============================================================

In 2001, Leo Breiman proposed two types of Random Forests. One was known as ``Forest-RI``, which is the axis-aligned traditional random forest. One was known as ``Forest-RC``, which is the random oblique linear combinations random forest. This leveraged random combinations of features to perform splits. [MORF](1) builds upon ``Forest-RC`` by proposing additional functions to combine features. Other modern tree variants such as Canonical Correlation Forests (CCF), Extended Isolation Forests, Quantile Forests, or unsupervised random forests are also important at solving real-world problems using robust decision tree models.

Installation
============

Our installation will try to follow scikit-learn installation as close as possible, as we contain Cython code subclassed, or inspired by the scikit-learn tree submodule.

Dependencies
------------

We minimally require:

    * Python (>=3.9)
    * numpy
    * scipy
    * scikit-learn

Installation with Pip (<https://pypi.org/project/treeple/>)
-------------------------------------------------------------

Installing with pip on a conda environment is the recommended route.

    pip install treeple

Development
===========

We welcome contributions for modern tree-based algorithms. We use Cython to achieve fast C/C++ speeds, while abiding by a scikit-learn compatible (tested) API. We also will welcome contributions in C/C++ if they improve the extensibility, or runtime performance of the codebase. Our Cython internals are easily extensible because they follow the internal Cython API of scikit-learn as well.

Due to the current state of scikit-learn's internal Cython code for trees, we have to instead leverage a fork of scikit-learn at <https://github.com/neurodata/scikit-learn> when
extending the decision tree model API of scikit-learn. Specifically, we extend the Python and Cython API of the tree submodule in scikit-learn in our submodule, so we can introduce the tree models housed in this package. Thus these extend the functionality of decision-tree based models in a way that is not possible yet in scikit-learn itself. As one example, we introduce an abstract API to allow users to implement their own oblique splits. Our plan in the future is to benchmark these functionalities and introduce them upstream to scikit-learn where applicable and inclusion criterion are met.

References
==========

[1]: [`Li, Adam, et al. "Manifold Oblique Random Forests: Towards Closing the Gap on Convolutional Deep Networks" SIAM Journal on Mathematics of Data Science, 5(1), 77-96, 2023`](https://doi.org/10.1137/21M1449117)
