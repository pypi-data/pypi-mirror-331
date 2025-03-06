from __future__ import annotations

import multiprocessing
import random

import numpy as np
import pandas as pd
from threadpoolctl import threadpool_limits

from dataclr._console_ui import console_ui
from dataclr._evaluate import train_eval
from dataclr.feature_selector._graph import Graph
from dataclr.methods import FilterMethod, WrapperMethod
from dataclr.methods._method_list import (
    fast_filter_classes,
    filter_classes,
    super_fast_filter_classes,
    wrapper_classes,
)
from dataclr.methods.method import DataSplits
from dataclr.metrics import Metric
from dataclr.models import BaseModel
from dataclr.results import MethodResult


class FeatureSelector:
    """
    A class for selecting the best features from a dataset using a combination of filter
    and wrapper methods.

    The ``FeatureSelector`` evaluates the base performance of a model, applies various
    feature selection techniques, and determines the optimal set of features based on
    the given metric. It also ensures that the data is properly preprocessed, encoded,
    and scaled for optimal performance.

    Args:
        model (:class:`~dataclr.models.BaseModel`): The model to be used for evaluation.
        metric (:data:`~dataclr.metrics.Metric`): The metric used to assess model
            performance.
        X_train (pd.DataFrame): Training feature data. Must be numeric and either
            normalized or standardized.
        X_test (pd.DataFrame): Testing feature data. Must be numeric and either
            normalized or standardized.
        y_train (pd.Series): Training target data.
        y_test (pd.Series): Testing target data.

    Raises:
        ValueError: If `X_train` contains non-numeric data.
        ValueError: If `X_train` is not normalized or standardized.
        ValueError: If `X_train` or `X_test` contains incompatible features
            that cannot be aligned.

    Notes:
        - Features with only a single unique value are removed.
        - It is necessary to preprocess the data (e.g., encoding, scaling) prior to
        passing it to this class for feature selection.
    """

    def __init__(
        self,
        model: BaseModel,
        metric: Metric,
        X_train: pd.DataFrame,
        X_test: pd.DataFrame,
        y_train: pd.Series,
        y_test: pd.Series,
    ) -> None:
        self.model: BaseModel = model
        self.metric: Metric = metric

        if not all(np.issubdtype(dtype, np.number) for dtype in X_train.dtypes):
            raise ValueError(
                "X_train contains non-numeric data. Ensure all data is properly encoded"
            )

        X_train = X_train.loc[:, X_train.nunique() > 1]
        X_test = X_test.loc[:, X_test.nunique() > 1]
        X_train, X_test = X_train.align(X_test, join="inner", axis=1)

        self.data_splits: DataSplits = {
            "X_train": X_train,
            "y_train": y_train,
            "X_test": X_test,
            "y_test": y_test,
        }

    def select_features(
        self,
        n_results: int = 3,
        max_depth: int = 3,
        max_method_results: int = 2,
        start_wrappers: bool = True,
        level_wrapper_results: int = 1,
        final_wrapper_results: int = 2,
        level_cutoff_threshold: int = 100,
        filter_methods: list[FilterMethod] = None,
        wrapper_methods: list[WrapperMethod] = None,
        verbose: bool = True,
        n_jobs: int = -1,
        seed: int = None,
        max_console_width: int = 110,
        keep_features: list[str] = [],
        max_features: int = -1,
        features_remove_coeff: float = 1.5,
        mode: str = "normal",
    ) -> list[MethodResult]:
        """
        Selects the best features using filter and wrapper methods and evaluates
        performance.

        This method evaluates the base performance of the provided model on the dataset.
        It then applies a combination of feature selection methods to identify the
        optimal feature set. The best results are extracted and printed.

        Steps:
            - Compute the base model performance.
            - Construct a ``Graph`` object with filter and wrapper methods.
            - Retrieve and display the best results from the graph.

        Args:
            n_results (int): The number of top results to return. Defaults to 3.
            seed (int): Number determining the randomness.
            max_depth (int): The maximum depth of exploration for the graph. Defaults
                to 3.
            max_method_results (int): The maximum number of results returned by a single
                method. Defaults to 2.
            start_wrappers (bool): Whether to initiate wrapper methods at the beginning.
                Defaults to True.
            level_wrapper_results (int): The number of top results to be used for
                running wrapper methods after entering a new level in the graph.
                Defaults to 0.
            final_wrapper_results (int): The number of top results to be used for
                running wrapper methods after the graph exploration ends. Defaults to 2.
            level_cutoff_threshold (int): The threshold for stopping exploration at the
                current level after a specified number of runs with no improvement.
                Defaults to 100.
            filter_methods (list[:class:`dataclr.methods.FilterMethod`]): A set of
                filtering methods to be applied. Defaults to `filter_classes`.
            wrapper_methods (list[:class:`dataclr.methods.WrapperMethod`]): A set of
                wrapper methods to be applied. Defaults to `wrapper_classes`.
            verbose (bool): Whether to display a UI with a progress bar during
                the algorithm's runtime. Defaults to True.
            n_jobs (int): The number of parallel jobs to use. Set to -1 to
                utilize all available processors. Defaults to -1.
            max_console_width (int): The maximum width of the console output
                for UI display purposes. Defaults to 110.
            keep_features (list[str]): List of features not to be dropped. Defaults to
                empty.
            max_features (int): Number of max features list in end results. Defaults to
                -1 (all features number).
            features_remove_coeff (float): Coefficient that will be used to determine
                how much features can be o result on specified level. The exact formula
                is max_features*(features_remove_coeff)^(remaining_levels_count). Defaults to
                1.5.
            mode (str): Determines how time-consuming methods will be used in feature selection.
                Possible values: 'normal', 'fast', 'super_fast'.
                'normal' is the best choice for datasets with up to a few hundred features.
                'fast' is suitable for datasets with fewer than a thousand features.
                'super_fast' is scalable for datasets with more than a few thousand features.
                Defaults to 'normal'.

        Returns:
            list[:class:`~dataclr.results.MethodResult`]: A list of the best results
            encapsulated as :class:`~dataclr.results.MethodResult` objects.
        """

        with threadpool_limits(limits=1, user_api="blas"):
            if keep_features:
                missing_features = [
                    feature
                    for feature in keep_features
                    if feature not in self.data_splits["X_train"].columns
                ]
                if missing_features:
                    for feature in missing_features:
                        print(f"Invalid feature '{feature}' in keep_features.")
                    return []

            if filter_methods is None:
                if mode == "fast":
                    filter_methods = fast_filter_classes
                elif mode == "super_fast":
                    filter_methods = super_fast_filter_classes
                elif mode == "normal":
                    filter_methods = filter_classes
                else:
                    filter_methods = filter_classes

            if wrapper_methods is None:
                wrapper_methods = wrapper_classes

            np.random.seed(seed)
            random.seed(seed)

            console_ui.reset_ui()
            console_ui.max_line_length = max_console_width
            performance = train_eval(self.model, self.metric, self.data_splits)

            if n_jobs == -1:
                n_jobs = multiprocessing.cpu_count()

            if verbose:
                print("Base performance:", performance)

            graph = Graph(
                data_splits=self.data_splits,
                metric=self.metric,
                method_set={
                    filter_class(
                        self.model,
                        self.metric,
                        n_results=max_method_results,
                        seed=seed,
                    )
                    for filter_class in filter_methods
                },
                wrapper_method_set={
                    wrapper_class(
                        self.model,
                        self.metric,
                        n_results=max_method_results,
                        seed=seed,
                    )
                    for wrapper_class in wrapper_methods
                },
                n_wrapper_results=final_wrapper_results,
                n_jobs=n_jobs,
                level_wrapper_results=level_wrapper_results,
                verbose=verbose,
                max_depth=max_depth,
                start_wrappers=start_wrappers,
                level_cutoff_threshold=level_cutoff_threshold,
                keep_features=keep_features,
                max_features=max_features,
                features_remove_coeff=features_remove_coeff,
            )

            return [MethodResult(node) for node in graph._get_best_results(n_results)]
