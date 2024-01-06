import os


def get_cluster_and_shard_for_guild_id(guild_id: int) -> tuple[str, str]:
    shard_id = (guild_id >> 22) % int(os.environ["TOTAL_SHARDS"])
    number_of_shards_per_cluster = int(os.environ["SHARDS_PER_CLUSTER"])
    clusters = {
        cid: [
            i
            for i in range(
                (cid - 1) * number_of_shards_per_cluster,
                ((cid - 1) * number_of_shards_per_cluster)
                + number_of_shards_per_cluster,
            )
        ]
        for cid in range(1, 25)  # Arb number of clusters
    }

    for cluster, shards in clusters.items():
        if shard_id in shards:
            return str(cluster), str(shard_id)

    raise ValueError("Maths went wrong")


def get_dev_cluster() -> str:
    cluster, _ = get_cluster_and_shard_for_guild_id(601219766258106399)
    return cluster
