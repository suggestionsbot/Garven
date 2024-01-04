import os


def get_dev_cluster() -> str:
    guild_id = 601219766258106399
    shard_id = (guild_id >> 22) % int(os.environ["TOTAL_SHARDS"])
    number_of_shards_per_cluster = 5
    clusters = {
        cid: [
            i
            for i in range(
                (cid - 1) * number_of_shards_per_cluster,
                ((cid - 1) * number_of_shards_per_cluster)
                + number_of_shards_per_cluster,
            )
        ]
        for cid in range(1, 20)
    }

    for cluster, shards in clusters.items():
        if shard_id in shards:
            return str(cluster)

    raise ValueError("Maths went wrong")
