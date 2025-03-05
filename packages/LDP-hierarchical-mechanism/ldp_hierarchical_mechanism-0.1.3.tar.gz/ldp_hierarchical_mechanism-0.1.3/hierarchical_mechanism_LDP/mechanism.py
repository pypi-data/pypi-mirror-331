from .ldp_protocol import get_client_server
from .bary_tree import TreeBary
from .computeamplification import numericalanalysis, closedformanalysis
import numpy as np
from tqdm import tqdm


class Private_TreeBary(TreeBary):

    def __init__(self, B: int, b: int, eps: float,
                 protocol: str = "unary_encoding",
                 on_all_levels: bool = True):
        """
        Constructor

        :param B: bound of the data
        :param b: branching factor of the tree
        :param eps: privacy parameter
        :param protocol: protocol to use for LDP frequency estimation
        :param on_all_levels: bool, if True the tree is updated on all levels, otherwise it each user select a random level
        of the tree to update

        """
        super().__init__(B, b, set_intervals=False)  # space efficient data structure
        # attributes have the same shape of intervals but initialized with zeros
        self.eps = eps  # privacy budget
        self.on_all_levels = on_all_levels

        self.clients, self.servers = get_client_server(protocol, eps, self.depth, self.b)

        self.N = None  # total number of users that updated the tree
        self.cdf = None  # cumulative distribution function
        self.attributes = None  # attributes of the tree
        # counts how many users updated the tree at each level, used to normalize the data
        # when applying updates with on_all_levels=False
        self.counts = None

    def initialize_clients_servers(self, eps: float, protocol: str):
        """
        Initialize clients and servers for the tree.

        :param eps: privacy parameter
        :param protocol: protocol to use for LDP frequency estimation
        """
        self.clients, self.servers = get_client_server(protocol, eps, self.depth, self.b)

    def update_tree(self, data: np.ndarray,
                    verbose: bool = False):
        """
        Update the tree with the data using the LDP protocol. If post_process is True, the tree is post processed using the
        algorithm provided by Hay et al. (2009).

        LDP protocol functions for the b-ary mechanism. It returns a list of servers with the privatized data for the
        b-adic decomposition of the domain (in intervals).

        Ref: Graham Cormode, Samuel Maddock, and Carsten Maple.
        Frequency Estimation under Local Differential Privacy. PVLDB, 14(11): 2046 - 2058, 2021

        :param data: data to update the tree
        :param verbose: bool, if True a progress bar is shown
        """
        # check if server and client are initialized
        if self.clients is None or self.servers is None:
            raise ValueError(
                "Clients and servers are not initialized, run initialize_clients_servers before updating the tree"
            )

        if not self.on_all_levels:
            # initialize the counts
            self.counts = [0 for _ in range(self.depth - 1)]

        # this counter is used to keep track of the number of users that updated the tree at each level
        iterator = tqdm(range(len(data)), colour='green') if verbose else range(len(data))

        # iterate over the data and privatize it
        for i in iterator:
            user_value = data[i]
            levels = range(1, self.depth) if self.on_all_levels else [np.random.randint(1, self.depth)]
            for level in levels:
                interval_index = self.find_interval_index(user_value, level)
                client = self.clients[level - 1]
                priv_data = client.privatise(interval_index)
                self.servers[level - 1].aggregate(priv_data)
                if not self.on_all_levels:
                    self.counts[level - 1] += 1

        # clients are not needed anymore
        del self.clients

        self.N = len(data)

    def compute_attributes(self, verbose: bool = False) -> None:
        """
        Compute the attributes of the tree. This might be slow for large trees as the levels close to the leaves
        have servers with large dimension, thus it is slow to get an estimate for each element of the interval.

        :param verbose: Show progress bar

        :return:
        """
        self.attributes: list[np.ndarray] = [np.zeros(self.b ** level) for level in range(self.depth)]

        # update the attributes of the Private tree, do not update the root
        if verbose:
            print("\nComputing attributes...")
            iterator = tqdm(enumerate(self.attributes), colour='green', total=self.depth)
        else:
            iterator = enumerate(self.attributes)

        for i, level_attributes in iterator:
            if i == 0:  # the root gets 1.
                self.attributes[i] = np.array([1.])
                continue
            if not self.on_all_levels:
                self.attributes[i] = np.array([get_frequency(self.servers[i - 1], self.counts[i - 1], j)
                                               for j in range(len(level_attributes))])
            else:
                self.attributes[i] = np.array([get_absolute_frequency(self.servers[i - 1], j)
                                               for j in range(len(level_attributes))])

        # servers are not needed anymore
        del self.servers

    def post_process(self, delete_attributes: bool = True):
        """
        Post process the tree by using the algorithm provided in the paper.

        Hay, Michael, et al. "Boosting the accuracy of differentially-private histograms through consistency." arXiv preprint arXiv:0904.0942 (2009).
        """
        if self.attributes is None:
            self.compute_attributes(verbose=True)

        B = self.b
        # Step 1: Weighted Averaging (from leaves not included to root)
        for level in reversed(range(self.depth - 1)):
            i = self.get_height(level)
            factor_1 = (B ** i - B ** (i - 1)) / (B ** i - 1)
            factor_2 = (B ** (i - 1) - 1) / (B ** i - 1)
            children_sum = sum_chunks(np.array(self.attributes[level + 1]), B)
            self.attributes[level] = [
                factor_1 * self.attributes[level][j] + factor_2 * children_sum[j]
                for j in range(len(self.attributes[level]))
            ]

        # Step 2: Mean Consistency (from root not included to leaves)
        for level in range(1, self.depth):
            parent_attributes_rep = np.repeat(self.attributes[level - 1], B)
            children_sum = np.repeat(sum_chunks(np.array(self.attributes[level]), B), B)
            self.attributes[level] = [
                self.attributes[level][j] + (1 / B) * (parent_attributes_rep[j] - children_sum[j])
                for j in range(len(self.attributes[level]))
            ]
        # The order of computation of range query is not important thanks to post-processing
        self.cdf = np.cumsum(self.attributes[-1])

        # attributes are not needed anymore
        if delete_attributes: del self.attributes

    def get_privacy(self, **kwargs) -> tuple[float, str]:
        """
        Return the privacy (epsilon) of the mechanism. If shuffle is True, the privacy is computed using privacy amplification
        by shuffling given a delta parameter and the initial privacy budget used to update the tree.
        If numerical is True, the privacy is computed using numerical analysis, otherwise it is computed using closed form analysis.

        :param kwargs:
            - shuffle: bool, if True the privacy is computed using privacy amplification by shuffling
            - numerical: bool, if True the privacy is computed using numerical analysis
            - delta: float, failure probability
            - num_iterations: int, number of iterations for numerical analysis
            - step: int, step for numerical analysis
            - upperbound: bool, if True the upperbound is computed, otherwise the lowerbound is computed

        :return: upper or lower bound of the privacy, and the method used to compute it
        """
        shuffle = kwargs.get('shuffle', False)
        numerical = kwargs.get('numerical', False)
        delta = kwargs.get('delta', None)

        if not shuffle:
            if self.on_all_levels:
                return self.eps * (self.depth - 1)
            else:
                return self.eps
        if delta is None:
            raise ValueError("Delta must be provided if shuffle is True")

        if not self.on_all_levels:
            raise Exception(
                "the update_tree function was called with on_all_levels=False. "
                "No privacy amplification by shuffling is possible in this case."
            )
        l = self.depth - 1
        num_iterations = kwargs.get('num_iterations', 10)
        step = kwargs.get('step', 100)
        upperbound = kwargs.get('upperbound', True)

        if numerical:
            eps_shuffle = numericalanalysis(self.N, self.eps, delta / (2 * l), num_iterations, step, upperbound)
        else:
            eps_shuffle = closedformanalysis(self.N, self.eps, delta / (2 * l))

        eps_pure = eps_shuffle * l
        eps_advanced = eps_shuffle * l * (np.exp(eps_shuffle) - 1) / (np.exp(eps_shuffle) + 1) + \
                       eps_shuffle * np.sqrt(2 * l * np.log(2 / delta))

        if eps_pure <= eps_advanced:
            if numerical:
                eps_shuffle = numericalanalysis(self.N, self.eps, delta / l, num_iterations, step, upperbound)
            else:
                eps_shuffle = closedformanalysis(self.N, self.eps, delta / l)
            eps_pure = eps_shuffle * l
            return eps_pure, "pure composition"
        else:
            return eps_advanced, "advanced composition"

    #######################
    ### QUERY FUNCTIONS ###
    #######################

    def get_quantile(self, q: float) -> int:
        """
        Get the quantile of the data

        :param q: the quantile to get

        :return: the q-quantile as integer
        """
        assert 0 <= q <= 1, "Quantile must be between 0 and 1"

        if self.cdf is not None:
            # retrive only elements with positive values
            index = np.where(self.cdf - q >= 0)[0]
            # find the minimum index that is closest to the quantile
            return min(index, key=lambda i: self.cdf[i] - q)
        else:
            return self._root_to_leaf(q)

    def get_range_query(self, left: int, right: int, normalized: bool = False) -> float:
        """
        Compute range query
        :param left: left bound of the range
        :param right: right bound of the range
        :param normalized: if True, the result is normalized by the total number of users that updated the tree

        :return: range query
        """

        assert 0 <= left <= right <= self.B, "Left and right must be between 0 and B"

        if self.cdf is not None:
            # compute right quantile
            result_right = self.cdf[right]
            # compute left quantile
            result_left = self.cdf[left]
            if normalized:
                return result_right - result_left
            else:
                return (result_right - result_left) * self.N
        else:
            return self.get_range_query_bary(left, right, normalized)

    def get_bins(self, quantiles: list[float], alpha: float) -> list[tuple[int, int]]:
        """
        Return a list of bins that contains quantiles q-alpha and q+alpha for each quantile q in quantiles.

        :param quantiles: list of quantiles
        :param alpha: error parameter

        :return: list of bins as tuples
        """
        assert 0 <= alpha <= 0.5, "Alpha must be between 0 and 0.5"
        assert all(0 < q < 1 for q in quantiles), "Quantiles must be between 0 and 1"

        # sort the quantiles
        quantiles = sorted(quantiles)
        bins = []
        for q in quantiles:
            # get the left and right quantile
            left = self.get_quantile(max(q - alpha, 0))
            right = self.get_quantile(min(q + alpha, 1))
            # sort left and right (they might be inverted)
            left, right = min(left, right), max(left, right)
            # append the bin
            bins.append((left, right))
        return bins

    def _root_to_leaf(self, q: float) -> int:
        """
        Implementatio of LDPquantile estimation

        Get the q-quantile of the data using the root to leaf approach. Start with the first level below the root and
        get the node that has a cumulative sum greater than the quantile. Then, move to the next level and get the node
        that has a cumulative sum greater than the quantile. Continue until the last level.

        :param q: the quantile to get

        :return: the q-quantile as integer
        """
        assert 0 <= q <= 1, "Quantile must be between 0 and 1"

        if self.on_all_levels:
            target = np.floor(q * self.N)
            estimator = lambda level, item: get_absolute_frequency(self.servers[level - 1], item)
        else:
            target = q
            estimator = lambda level, item: get_frequency(self.servers[level - 1], self.counts[level - 1], item)

        # start from the first level below the root
        def __get_node_at_level(level: int, S: float, offset: int) -> int:
            for i in range(self.b):
                # for sure the estimator is less than N, for either cases
                S_add = min(estimator(level, offset + i), self.N)
                if S + S_add >= target or i == self.b - 1:
                    if level == self.depth - 1:
                        return offset + i
                    else:
                        offset = (offset + i) * self.b
                        return __get_node_at_level(level + 1, S, offset)
                S += S_add

        return __get_node_at_level(1, 0, 0) + 1

    ######################################################
    ### Function useless if the tree is post processed ###
    ######################################################

    def get_range_query_bary(self, left: int, right: int, normalized: bool = False) -> float:
        """
        Compute range query using bary indexing.
        :param left: left bound of the range
        :param right: right bound of the range
        :param normalized: if True, the result is normalized by the total number of users that updated the tree

        :return: range query
        """
        assert 0 <= left <= right <= self.B, "Left and right must be between 0 and B"

        estimator = (lambda level, item: get_absolute_frequency(self.servers[level - 1], item)
                     if self.on_all_levels else
                     lambda level, item: get_frequency(self.servers[level - 1], self.counts[level - 1], item))

        def compute_result(bound: int) -> float:
            result = 0
            for i, j in self.get_bary_decomposition_index(bound):
                result += estimator(i, j)
            return result

        result_right = compute_result(right)
        result_left = compute_result(left)

        if normalized:
            return (result_right - result_left) / self.N if self.on_all_levels else result_right - result_left
        else:
            return result_right - result_left if self.on_all_levels else (result_right - result_left) * self.N

    def compute_cdf(self):
        """
        Compute the CDF of [0, b^(depth + 1)]

        :return:
        """
        cdf = np.zeros(self.b ** self.depth + 1)
        for i in range(self.b ** self.depth + 1):
            indices = self.get_bary_decomposition_index(i)
            cdf[i] = sum(self.attributes[j][k] for j, k in indices)
        self.cdf = cdf


def get_frequency(server, count, item) -> float:
    """
    Estimate the frequency of an item using the server and the count.
    :param server: a server (an instance of LDP Frequency Oracle server of pure_ldp package)
    :param count: the count of the data (server returns absolute frequency)
    :param item: the item to estimate
    """
    return server.estimate(item, suppress_warnings=True) / count


def get_absolute_frequency(server, item) -> float:
    """
    Estimate the absolute frequency of an item using the server.
    :param server: a server (an instance of LDP Frequency Oracle server of pure_ldp package)
    :param item: the item to estimate
    """
    return server.estimate(item, suppress_warnings=True)


def sum_chunks(arr: np.array, chunk_size: int) -> np.array:
    """
    Sums chunks of the array.

    :param arr: Input numpy array
    :param chunk_size: Size of each chunk
    :return: Numpy array with summed chunks
    """
    # Ensure the array length is a multiple of chunk_size
    assert len(arr) % chunk_size == 0, "Array length must be a multiple of chunk size"

    # Reshape the array to have shape (-1, chunk_size)
    reshaped = arr.reshape(-1, chunk_size)
    # Sum along the second axis (axis=1)
    return reshaped.sum(axis=1)
