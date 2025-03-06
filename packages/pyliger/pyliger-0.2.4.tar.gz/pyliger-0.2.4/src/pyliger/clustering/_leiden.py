import lazy_loader as lazy
leidenalg = lazy.load("leidenalg", error_on_import=True)
np = lazy.load("numpy", error_on_import=True)

from pyliger.clustering._utilities import (
    _assign_cluster,
    build_igraph,
    compute_snn,
    run_knn,
)


def leiden_cluster(
    liger_object,
    resolution=1.0,
    k=20,
    prune=1 / 15,
    random_seed=1,
    n_iterations=-1,
    n_starts=10,
):
    """Leiden algorithm for community detection

    After quantile normalization, users can additionally run the Leiden algorithm
    for community detection.

    Parameters
    ----------
    liger_object : liger object
        Should run quantile_norm before calling.
    resolution : float, optional
        Value of the resolution parameter, use a value above (below) 1.0 if you want
        to obtain a larger (smaller) number of communities (the default is 1.0).
    k : int, optional
        The maximum number of nearest neighbours to compute (the default is 20).
    prune : float, optional
        Sets the cutoff for acceptable Jaccard index when
        computing the neighborhood overlap for the SNN construction. Any edges with
        values less than or equal to this will be set to 0 and removed from the SNN
        graph. Essentially sets the strigency of pruning (0 --- no pruning, 1 ---
        prune everything) (the default is 1/15).
    random_seed : int, optional
        Seed of the random number generator (the default is 1).
    n_iterations : TYPE, optional
        The number of iterations to run the Leiden algorithm.
        A negative value indicates the Leiden algorithm runs until one iterration
        that has no improvement. (the default is -1)
    n_starts : int, optional
        The number of random starts to be used (the default is 10).

    Returns
    -------
    liger_object : liger object
        object with refined 'cluster'.

    Examples
    --------
    >>> ligerex = leiden_cluster(ligerex, resulotion = 0.25) # liger object, factorization complete
    """
    ### 1. Compute snn
    H_norm = np.vstack([adata.obsm["H_norm"] for adata in liger_object.adata_list])
    knn = run_knn(H_norm, k)
    snn = compute_snn(knn, prune=prune)

    ### 2. Get igraph from snn
    g = build_igraph(snn)

    ### 3. Run louvain
    np.random.seed(random_seed)
    max_quality = -1
    # random starts to improve stability
    for i in range(n_starts):
        seed = np.random.randint(0, 1000)
        kwargs = {
            "weights": g.es["weight"],
            "resolution_parameter": resolution,
            "seed": seed,
        }  # parameters setting
        part = leidenalg.find_partition(
            g,
            leidenalg.RBConfigurationVertexPartition,
            n_iterations=n_iterations,
            **kwargs,
        )

        if part.quality() > max_quality:
            cluster = part.membership
            max_quality = part.quality()

    ### 4. Assign cluster results
    _assign_cluster(cluster, liger_object)

    return None
