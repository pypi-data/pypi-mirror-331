"""Main class ActionRules."""

import itertools
import warnings
from collections import defaultdict
from typing import TYPE_CHECKING, Optional, Union  # noqa

from .candidates.candidate_generator import CandidateGenerator
from .output.output import Output
from .rules.rules import Rules

if TYPE_CHECKING:
    from types import ModuleType  # noqa

    import cudf
    import cupy
    import cupyx
    import numpy
    import pandas
    import scipy


class ActionRules:
    """
    A class used to generate action rules for a given dataset.

    Attributes
    ----------
    min_stable_attributes : int
        The minimum number of stable attributes required.
    min_flexible_attributes : int
        The minimum number of flexible attributes required.
    min_undesired_support : int
        The minimum support for the undesired state.
    min_undesired_confidence : float
        The minimum confidence for the undesired state.
    min_desired_support : int
        The minimum support for the desired state.
    min_desired_confidence : float
        The minimum confidence for the desired state.
    verbose : bool, optional
        If True, enables verbose output.
    rules : Optional[Rules], optional
        Stores the generated rules.
    output : Optional[Output], optional
        Stores the generated action rules.
    np : Optional[ModuleType], optional
        The numpy or cupy module used for array operations.
    pd : Optional[ModuleType], optional
        The pandas or cudf module used for DataFrame operations.
    is_gpu_np : bool
        Indicates whether GPU-accelerated numpy (cupy) is used.
    is_gpu_pd : bool
        Indicates whether GPU-accelerated pandas (cudf) is used.
    intrinsic_utility_table : dict, optional
        (attribute, value) -> float
        A lookup table for the intrinsic utility of each attribute-value pair.
        If None, no intrinsic utility is considered.
    transition_utility_table : dict, optional
        (attribute, from_value, to_value) -> float
        A lookup table for cost/gain of transitions between values.
        If None, no transition utility is considered.

    Methods
    -------
    fit(data, stable_attributes, flexible_attributes, target, undesired_state, desired_state, use_sparse_matrix=False,
    use_gpu=False)
        Generates action rules based on the provided dataset and parameters.
    get_bindings(data, stable_attributes, flexible_attributes, target)
        Binds attributes to corresponding columns in the dataset.
    get_stop_list(stable_items_binding, flexible_items_binding)
        Generates a stop list to prevent certain combinations of attributes.
    get_split_tables(data, target_items_binding, target)
        Splits the dataset into tables based on target item bindings.
    get_rules()
        Returns the generated action rules if available.
    predict(frame_row)
        Predicts recommended actions based on the provided row of data.
    """

    def __init__(
        self,
        min_stable_attributes: int,
        min_flexible_attributes: int,
        min_undesired_support: int,
        min_undesired_confidence: float,
        min_desired_support: int,
        min_desired_confidence: float,
        verbose=False,
        intrinsic_utility_table: Optional[dict] = None,
        transition_utility_table: Optional[dict] = None,
    ):
        """
        Initialize the ActionRules class with the specified parameters.

        Parameters
        ----------
        min_stable_attributes : int
            The minimum number of stable attributes required.
        min_flexible_attributes : int
            The minimum number of flexible attributes required.
        min_undesired_support : int
            The minimum support for the undesired state.
        min_undesired_confidence : float
            The minimum confidence for the undesired state.
        min_desired_support : int
            The minimum support for the desired state.
        min_desired_confidence : float
            The minimum confidence for the desired state.
        verbose : bool, optional
            If True, enables verbose output. Default is False.
        intrinsic_utility_table : dict, optional
            (attribute, value) -> float
            A lookup table for the intrinsic utility of each attribute-value pair.
            If None, no intrinsic utility is considered.
        transition_utility_table : dict, optional
            (attribute, from_value, to_value) -> float
            A lookup table for cost/gain of transitions between values.
            If None, no transition utility is considered.

        Notes
        -----
        The `verbose` parameter can be used to enable detailed output during the rule generation process.
        """
        self.min_stable_attributes = min_stable_attributes
        self.min_flexible_attributes = min_flexible_attributes
        self.min_undesired_support = min_undesired_support
        self.min_desired_support = min_desired_support
        self.min_undesired_confidence = min_undesired_confidence
        self.min_desired_confidence = min_desired_confidence
        self.verbose = verbose
        self.rules = None  # type: Optional[Rules]
        self.output = None  # type: Optional[Output]
        self.np = None  # type: Optional[ModuleType]
        self.pd = None  # type: Optional[ModuleType]
        self.is_gpu_np = False
        self.is_gpu_pd = False
        self.is_onehot = False
        self.intrinsic_utility_table = intrinsic_utility_table or {}
        self.transition_utility_table = transition_utility_table or {}

    def count_max_nodes(self, stable_items_binding: dict, flexible_items_binding: dict) -> int:
        """
        Calculate the maximum number of nodes based on the given item bindings.

        This function takes two dictionaries, `stable_items_binding` and `flexible_items_binding`,
        which map attributes to lists of items. It calculates the total number of nodes by considering
        all possible combinations of the lengths of these item lists and summing the product of each combination.

        Parameters
        ----------
        stable_items_binding : dict
            A dictionary where keys are attributes and values are lists of stable items.
        flexible_items_binding : dict
            A dictionary where keys are attributes and values are lists of flexible items.

        Returns
        -------
        int
            The total number of nodes calculated by summing the product of lengths of all combinations of item lists.

        Notes
        -----
        - The function first combines the lengths of item lists from both dictionaries.
        - It then calculates the sum of the products of all possible combinations of these lengths.
        """
        import numpy

        values_in_attribute = []
        for items in list(stable_items_binding.values()) + list(flexible_items_binding.values()):
            values_in_attribute.append(len(items))

        sum_nodes = 0
        for i in range(len(values_in_attribute)):
            for comb in itertools.combinations(values_in_attribute, i + 1):
                sum_nodes += int(numpy.prod(comb))
        return sum_nodes

    def set_array_library(self, use_gpu: bool, df: Union['cudf.DataFrame', 'pandas.DataFrame']):
        """
        Set the appropriate array and DataFrame libraries (cuDF or pandas) based on the user's preference.

        Parameters
        ----------
        use_gpu : bool
            Indicates whether to use GPU (cuDF) for data processing if available.
        df : Union[cudf.DataFrame, pandas.DataFrame]
            The DataFrame to convert.

        Raises
        ------
        ImportError
            If `use_gpu` is True but cuDF is not available and pandas cannot be imported as fallback.

        Warnings
        --------
        UserWarning
            If `use_gpu` is True but cuDF is not available, a warning is issued indicating fallback to pandas.

        Notes
        -----
        This method determines whether to use GPU-accelerated libraries for processing data, falling back to CPU-based
        libraries if necessary.
        """
        if use_gpu:
            try:
                import cupy as np

                is_gpu_np = True
            except ImportError:
                warnings.warn("CuPy is not available. Falling back to Numpy.")
                import numpy as np

                is_gpu_np = False
        else:
            import numpy as np

            is_gpu_np = False

        df_library_imported = False
        try:
            import pandas as pd

            if isinstance(df, pd.DataFrame):
                is_gpu_pd = False
                df_library_imported = True
        except ImportError:
            df_library_imported = False

        if not df_library_imported:
            try:
                import cudf as pd

                if isinstance(df, pd.DataFrame):
                    is_gpu_pd = True
                    df_library_imported = True
            except ImportError:
                df_library_imported = False

        if not df_library_imported:
            raise ImportError('Just Pandas or cuDF dataframes are supported.')

        self.np = np
        self.pd = pd
        self.is_gpu_np = is_gpu_np
        self.is_gpu_pd = is_gpu_pd

    def df_to_array(self, df: Union['cudf.DataFrame', 'pandas.DataFrame'], use_sparse_matrix: bool = False) -> tuple:
        """
        Convert a DataFrame to a numpy or CuPy array.

        Parameters
        ----------
        df : Union[cudf.DataFrame, pandas.DataFrame]
            The DataFrame to convert.
        use_sparse_matrix : bool, optional
            If True, a sparse matrix is used. Default is False.

        Returns
        -------
        tuple
            A tuple containing the transposed array and the DataFrame columns.

        Notes
        -----
        The data is converted to an unsigned 8-bit integer array (`np.uint8`). If `use_gpu` is True,
        the array is further converted to a CuPy array.
        """
        columns = list(df.columns)
        # cuDF and CuPy
        if self.is_gpu_np and self.is_gpu_pd:
            if use_sparse_matrix:
                from cupyx.scipy.sparse import csr_matrix

                data = csr_matrix(df.values, dtype=self.np.float32).T  # type: ignore
            else:
                data = self.np.asarray(df.values, dtype=self.np.uint8).T  # type: ignore
        # Pandas and CuPy
        elif self.is_gpu_np and not self.is_gpu_pd:
            if use_sparse_matrix:
                from cupyx.scipy.sparse import csr_matrix
                from scipy.sparse import csr_matrix as scipy_csr_matrix

                scipy_matrix = scipy_csr_matrix(df.values).T
                data = csr_matrix(scipy_matrix, dtype=float)
            else:
                data = self.np.asarray(df.values, dtype=self.np.uint8).T  # type: ignore
        # cuDF and Numpy
        elif not self.is_gpu_np and self.is_gpu_pd:
            if use_sparse_matrix:
                from scipy.sparse import csr_matrix

                data = csr_matrix(df.to_numpy(), dtype=self.np.uint8).T  # type: ignore
            else:
                data = df.to_numpy().T  # type: ignore
        # Pandas and Numpy
        else:
            if use_sparse_matrix:
                from scipy.sparse import csr_matrix

                data = csr_matrix(df.values, dtype=self.np.uint8).T  # type: ignore
            else:
                data = df.to_numpy(dtype=self.np.uint8).T  # type: ignore
        return data, columns

    def one_hot_encode(
        self,
        data: Union['cudf.DataFrame', 'pandas.DataFrame'],
        stable_attributes: list,
        flexible_attributes: list,
        target: str,
    ) -> Union['cudf.DataFrame', 'pandas.DataFrame']:
        """
        Perform one-hot encoding on the specified stable, flexible, and target attributes of the DataFrame.

        Parameters
        ----------
        data : Union[cudf.DataFrame, pandas.DataFrame]
            The input DataFrame containing the data to be encoded.
        stable_attributes : list
            List of stable attributes to be one-hot encoded.
        flexible_attributes : list
            List of flexible attributes to be one-hot encoded.
        target : str
            The target attribute to be one-hot encoded.

        Returns
        -------
        Union[cudf.DataFrame, pandas.DataFrame]
            A DataFrame with the specified attributes one-hot encoded.

        Notes
        -----
        The input data is first converted to string type to ensure consistent encoding. The stable attributes,
        flexible attributes, and target attribute are then one-hot encoded separately and concatenated into a
        single DataFrame.
        """
        data = data.astype(str)
        to_concat = []
        if len(stable_attributes) > 0:
            data_stable = self.pd.get_dummies(  # type: ignore
                data[stable_attributes], sparse=False, prefix_sep='_<item_stable>_'
            )
            to_concat.append(data_stable)
        if len(flexible_attributes) > 0:
            data_flexible = self.pd.get_dummies(  # type: ignore
                data[flexible_attributes], sparse=False, prefix_sep='_<item_flexible>_'
            )
            to_concat.append(data_flexible)
        data_target = self.pd.get_dummies(data[[target]], sparse=False, prefix_sep='_<item_target>_')  # type: ignore
        to_concat.append(data_target)
        data = self.pd.concat(to_concat, axis=1)  # type: ignore
        return data

    def fit_onehot(
        self,
        data: Union['cudf.DataFrame', 'pandas.DataFrame'],
        stable_attributes: dict,
        flexible_attributes: dict,
        target: dict,
        target_undesired_state: str,
        target_desired_state: str,
        use_sparse_matrix: bool = False,
        use_gpu: bool = False,
    ):
        """
        Preprocess and fit the model using one-hot encoded attributes.

        This method prepares the dataset for generating action rules by
        performing one-hot encoding on the specified stable, flexible,
        and target attributes. The resulting dataset is then used to fit
        the model using the `fit` method.

        Parameters
        ----------
        data : Union[cudf.DataFrame, pandas.DataFrame]
            The dataset to be processed and used for fitting the model.
        stable_attributes : dict
            A dictionary mapping stable attribute names to lists of column
            names corresponding to those attributes.
        flexible_attributes : dict
            A dictionary mapping flexible attribute names to lists of column
            names corresponding to those attributes.
        target : dict
            A dictionary mapping the target attribute name to a list of
            column names corresponding to that attribute.
        target_undesired_state : str
            The undesired state of the target attribute, used in action rule generation.
        target_desired_state : str
            The desired state of the target attribute, used in action rule generation.
        use_sparse_matrix : bool, optional
            If True, a sparse matrix is used in the fitting process. Default is False.
        use_gpu : bool, optional
            If True, the GPU (cuDF) is used for data processing if available.
            Default is False.

        Notes
        -----
        The method modifies the dataset by:
        1. Renaming columns according to the stable, flexible, and target attributes.
        2. Removing columns that are not associated with any of these attributes.
        3. Passing the processed dataset and relevant attribute lists to the `fit` method
           to generate action rules.

        This method ensures that the dataset is correctly preprocessed for rule
        generation, focusing on the specified attributes and their one-hot encoded forms.
        """
        self.is_onehot = True
        data = data.copy()
        data = data.astype('bool')
        new_labels = []
        attributes_stable = set([])
        attribtes_flexible = set([])
        attribute_target = ''
        remove_cols = []
        for label in data.columns:
            to_remove = True
            for attribute, columns in stable_attributes.items():
                if label in columns:
                    new_labels.append(attribute + '_<item_stable>_' + label)
                    attributes_stable.add(attribute)
                    to_remove = False
            for attribute, columns in flexible_attributes.items():
                if label in columns:
                    new_labels.append(attribute + '_<item_flexible>_' + label)
                    attribtes_flexible.add(attribute)
                    to_remove = False
            for attribute, columns in target.items():
                if label in columns:
                    new_labels.append(attribute + '_<item_target>_' + label)
                    attribute_target = attribute
                    to_remove = False
            if to_remove:
                new_labels.append(label)
                remove_cols.append(label)
        data.columns = new_labels
        data = data.drop(columns=remove_cols)
        self.fit(
            data,
            list(attributes_stable),
            list(attribtes_flexible),
            attribute_target,
            target_undesired_state,
            target_desired_state,
            use_sparse_matrix,
            use_gpu,
        )

    def fit(
        self,
        data: Union['cudf.DataFrame', 'pandas.DataFrame'],
        stable_attributes: list,
        flexible_attributes: list,
        target: str,
        target_undesired_state: str,
        target_desired_state: str,
        use_sparse_matrix: bool = False,
        use_gpu: bool = False,
    ):
        """
        Generate action rules based on the provided dataset and parameters.

        Parameters
        ----------
        data : Union[cudf.DataFrame, pandas.DataFrame]
            The dataset to generate action rules from.
        stable_attributes : list
            List of stable attributes.
        flexible_attributes : list
            List of flexible attributes.
        target : str
            The target attribute.
        target_undesired_state : str
            The undesired state of the target attribute.
        target_desired_state : str
            The desired state of the target attribute.
        use_sparse_matrix : bool, optional
            If True, a sparse matrix is used. Default is False.
        use_gpu : bool, optional
            Use GPU (cuDF) for data processing if available. Default is False.

        Raises
        ------
        RuntimeError
            If the model has already been fitted.

        Notes
        -----
        This method performs one-hot encoding on the specified attributes, converts the DataFrame to an array,
        and generates action rules by iterating over candidate rules and pruning them based on the given parameters.
        """
        if self.output is not None:
            raise RuntimeError("The model is already fit.")
        self.set_array_library(use_gpu, data)
        if not self.is_onehot:
            data = self.one_hot_encode(data, stable_attributes, flexible_attributes, target)
        data, columns = self.df_to_array(data, use_sparse_matrix)

        stable_items_binding, flexible_items_binding, target_items_binding, column_values = self.get_bindings(
            columns, stable_attributes, flexible_attributes, target
        )

        self.intrinsic_utility_table, self.transition_utility_table = self.remap_utility_tables(column_values)

        if self.verbose:
            print('Maximum number of nodes to check for support:')
            print('_____________________________________________')
            print(self.count_max_nodes(stable_items_binding, flexible_items_binding))
            print('')
        stop_list = self.get_stop_list(stable_items_binding, flexible_items_binding)
        frames = self.get_split_tables(data, target_items_binding, target, use_sparse_matrix)
        undesired_state = columns.index(target + '_<item_target>_' + str(target_undesired_state))
        desired_state = columns.index(target + '_<item_target>_' + str(target_desired_state))

        stop_list_itemset = []  # type: list

        candidates_queue = [
            {
                'ar_prefix': tuple(),
                'itemset_prefix': tuple(),
                'stable_items_binding': stable_items_binding,
                'flexible_items_binding': flexible_items_binding,
                'undesired_mask': None,
                'desired_mask': None,
                'actionable_attributes': 0,
            }
        ]
        k = 0
        self.rules = Rules(
            undesired_state,
            desired_state,
            columns,
            data.shape[1],
            self.intrinsic_utility_table,
            self.transition_utility_table,
        )
        candidate_generator = CandidateGenerator(
            frames,
            self.min_stable_attributes,
            self.min_flexible_attributes,
            self.min_undesired_support,
            self.min_desired_support,
            self.min_undesired_confidence,
            self.min_desired_confidence,
            undesired_state,
            desired_state,
            self.rules,
            use_sparse_matrix,
        )
        while len(candidates_queue) > 0:
            candidate = candidates_queue.pop(0)
            if len(candidate['ar_prefix']) > k:
                k += 1
                self.rules.prune_classification_rules(k, stop_list)
            new_candidates = candidate_generator.generate_candidates(
                **candidate,
                stop_list=stop_list,
                stop_list_itemset=stop_list_itemset,
                undesired_state=undesired_state,
                desired_state=desired_state,
                verbose=self.verbose,
            )
            candidates_queue += new_candidates
        self.rules.generate_action_rules()
        self.output = Output(
            self.rules.action_rules, target, stable_items_binding, flexible_items_binding, column_values
        )
        del data
        if self.is_gpu_np:
            self.np.get_default_memory_pool().free_all_blocks()  # type: ignore

    def get_bindings(
        self,
        columns: list,
        stable_attributes: list,
        flexible_attributes: list,
        target: str,
    ) -> tuple:
        """
        Bind attributes to corresponding columns in the dataset.

        Parameters
        ----------
        columns : list
            List of column names in the dataset.
        stable_attributes : list
            List of stable attributes.
        flexible_attributes : list
            List of flexible attributes.
        target : str
            The target attribute.

        Returns
        -------
        tuple
            A tuple containing the bindings for stable attributes, flexible attributes, and target items.

        Notes
        -----
        The method generates mappings from column indices to attribute values for stable, flexible, and target
        attributes.
        """
        stable_items_binding = defaultdict(lambda: [])
        flexible_items_binding = defaultdict(lambda: [])
        target_items_binding = defaultdict(lambda: [])
        column_values = {}

        for i, col in enumerate(columns):
            is_continue = False
            # stable
            for attribute in stable_attributes:
                if col.startswith(attribute + '_<item_stable>_'):
                    stable_items_binding[attribute].append(i)
                    column_values[i] = (attribute, col.split('_<item_stable>_', 1)[1])
                    is_continue = True
                    break
            if is_continue is True:
                continue
            # flexible
            for attribute in flexible_attributes:
                if col.startswith(attribute + '_<item_flexible>_'):
                    flexible_items_binding[attribute].append(i)
                    column_values[i] = (attribute, col.split('_<item_flexible>_', 1)[1])
                    is_continue = True
                    break
            if is_continue is True:
                continue
            # target
            if col.startswith(target + '_<item_target>_'):
                target_items_binding[target].append(i)
                column_values[i] = (target, col.split('_<item_target>_', 1)[1])
        return stable_items_binding, flexible_items_binding, target_items_binding, column_values

    def get_stop_list(self, stable_items_binding: dict, flexible_items_binding: dict) -> list:
        """
        Generate a stop list to prevent certain combinations of attributes.

        Parameters
        ----------
        stable_items_binding : dict
            Dictionary containing bindings for stable items.
        flexible_items_binding : dict
            Dictionary containing bindings for flexible items.

        Returns
        -------
        list
            A list of stop combinations.

        Notes
        -----
        The stop list is generated by creating pairs of stable item indices and ensuring flexible items do not repeat.
        """
        stop_list = []
        for items in stable_items_binding.values():
            for stop_couple in itertools.product(items, repeat=2):
                stop_list.append(tuple(stop_couple))
        for item in flexible_items_binding.keys():
            stop_list.append(tuple([item, item]))
        return stop_list

    def get_split_tables(
        self,
        data: Union['numpy.ndarray', 'cupy.ndarray', 'cupyx.scipy.sparse.csr_matrix', 'scipy.sparse.csr_matrix'],
        target_items_binding: dict,
        target: str,
        use_sparse_matrix: bool = False,
    ) -> dict:
        """
        Split the dataset into tables based on target item bindings.

        Parameters
        ----------
        data : Union['numpy.ndarray', 'cupy.ndarray', 'cupyx.scipy.sparse.csr_matrix', 'scipy.sparse.csr_matrix']
            The dataset to be split.
        target_items_binding : dict
            Dictionary containing bindings for target items.
        target : str
            The target attribute.
        use_sparse_matrix : bool, optional
            If True, a sparse matrix is used. Default is False.

        Returns
        -------
        dict
            A dictionary containing the split tables.

        Notes
        -----
        The method creates masks for the target items and splits the data accordingly.
        """
        frames = {}
        for item in target_items_binding[target]:
            mask = data[item] == 1
            if use_sparse_matrix:
                frames[item] = data.multiply(mask)  # type: ignore
            else:
                frames[item] = data[:, mask]
        return frames

    def get_rules(self) -> Output:
        """
        Return the generated action rules if available.

        Raises
        ------
        RuntimeError
            If the model has not been fitted.

        Returns
        -------
        Output
            The generated action rules.

        Notes
        -----
        This method returns the `Output` object containing the generated action rules.
        """
        if self.output is None:
            raise RuntimeError("The model is not fit.")
        return self.output

    def predict(self, frame_row: Union['cudf.Series', 'pandas.Series']) -> Union['cudf.DataFrame', 'pandas.DataFrame']:
        """
        Predict recommended actions based on the provided row of data.

        This method applies the fitted action rules to the given row of data and generates
        a DataFrame with recommended actions if any of the action rules are triggered.

        Parameters
        ----------
        frame_row : Union['cudf.Series', 'pandas.Series']
            A row of data in the form of a cuDF or pandas Series. The Series should
            contain the features required by the action rules.

        Returns
        -------
        Union['cudf.DataFrame', 'pandas.DataFrame']
            A DataFrame with the recommended actions. The DataFrame includes the following columns:
            - The original attributes with recommended changes.
            - 'ActionRules_RuleIndex': Index of the action rule applied.
            - 'ActionRules_UndesiredSupport': Support of the undesired part of the rule.
            - 'ActionRules_DesiredSupport': Support of the desired part of the rule.
            - 'ActionRules_UndesiredConfidence': Confidence of the undesired part of the rule.
            - 'ActionRules_DesiredConfidence': Confidence of the desired part of the rule.
            - 'ActionRules_Uplift': Uplift value of the rule.

        Raises
        ------
        RuntimeError
            If the model has not been fitted.

        Notes
        -----
        The method compares the given row of data against the undesired itemsets of the action rules.
        If a match is found, it applies the desired itemset changes and records the action rule's
        metadata. The result is a DataFrame with one or more rows representing the recommended actions
        for the given data.
        """
        if self.output is None:
            raise RuntimeError("The model is not fit.")
        index_value_tuples = list(zip(frame_row.index, frame_row))
        values = []
        column_values = self.output.column_values
        for index_value_tuple in index_value_tuples:
            values.append(list(column_values.keys())[list(column_values.values()).index(index_value_tuple)])
        new_values = tuple(values)
        predicted = []
        for i, action_rule in enumerate(self.output.action_rules):
            if set(action_rule['undesired']['itemset']) <= set(new_values):
                predicted_row = frame_row.copy()
                for recommended in set(action_rule['desired']['itemset']) - set(new_values):
                    attribute, value = column_values[recommended]
                    predicted_row[attribute + ' (Recommended)'] = value
                predicted_row['ActionRules_RuleIndex'] = i
                predicted_row['ActionRules_UndesiredSupport'] = action_rule['undesired']['support']
                predicted_row['ActionRules_DesiredSupport'] = action_rule['desired']['support']
                predicted_row['ActionRules_UndesiredConfidence'] = action_rule['undesired']['confidence']
                predicted_row['ActionRules_DesiredConfidence'] = action_rule['desired']['confidence']
                predicted_row['ActionRules_Uplift'] = action_rule['uplift']
                predicted.append(predicted_row)
        return self.pd.DataFrame(predicted)  # type: ignore

    def remap_utility_tables(self, column_values):
        """
        Remap the keys of intrinsic and transition utility tables using the provided column mapping.

        The function uses `column_values`, a dictionary mapping internal column indices to
        (attribute, value) tuples, to invert the mapping so that utility table keys are replaced
        with the corresponding integer index (for intrinsic utilities) or a tuple of integer indices
        (for transition utilities).

        Parameters
        ----------
        column_values : dict
            Dictionary mapping integer column indices to (attribute, value) pairs.
            Example: {0: ('Age', 'O'), 1: ('Age', 'Y'), 2: ('Sex', 'F'), ...}

        Returns
        -------
        tuple
            A tuple (remapped_intrinsic, remapped_transition) where:
              - remapped_intrinsic is a dict mapping integer column index to utility value.
              - remapped_transition is a dict mapping (from_index, to_index) to utility value.

        Notes
        -----
        - The method performs case-insensitive matching by converting attribute names and values to lowercase.
        - If a key in a utility table does not have a corresponding entry in column_values, it is skipped.
        """
        # Invert column_values to map (attribute.lower(), value.lower()) -> column index.
        inv_map = {(attr.lower(), val.lower()): idx for idx, (attr, val) in column_values.items()}

        remapped_intrinsic = {}
        # Remap intrinsic utility table keys: ('Attribute', 'Value') -> utility
        for key, utility in self.intrinsic_utility_table.items():
            # Normalize key to lowercase
            attr, val = key
            lookup_key = (attr.lower(), val.lower())
            # Look up the corresponding column index; if not found, skip this key.
            if lookup_key in inv_map:
                col_index = inv_map[lookup_key]
                remapped_intrinsic[col_index] = utility
            # Else: optionally, one could log or warn about a missing mapping.

        remapped_transition = {}
        # Remap transition utility table keys: ('Attribute', from_value, to_value) -> utility
        for key, utility in self.transition_utility_table.items():
            attr, from_val, to_val = key
            lookup_from = (attr.lower(), from_val.lower())
            lookup_to = (attr.lower(), to_val.lower())
            # Only remap if both the from and to values exist in inv_map.
            if lookup_from in inv_map and lookup_to in inv_map:
                from_index = inv_map[lookup_from]
                to_index = inv_map[lookup_to]
                remapped_transition[(from_index, to_index)] = utility
            # Else: skip or log missing mapping.

        return remapped_intrinsic, remapped_transition
