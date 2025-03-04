from typing import Union, List

from feast import FeatureStore
import ray.data
import pandas as pd
import polars as pl
from feast.feature_service import FeatureService
from feast.infra.offline_stores.offline_store import RetrievalJob
from feast.infra.offline_stores.bigquery import BigQueryRetrievalJob


def materialize_to_ray_dataset(
    store: FeatureStore,
    entity_df: pd.DataFrame,
    features: Union[List[str], FeatureService],
) -> ray.data.Dataset:
    """Materialize historical features to a Ray Dataset.

    Returns:
        ray.data.Dataset: Returns a ray dataset with the features
    """
    retrieval_job: RetrievalJob = store.get_historical_features(
        entity_df=entity_df,
        features=features,
    )
    ray_dataset: ray.data.Dataset = ray.data.from_arrow(retrieval_job.to_arrow())
    return ray_dataset


def materialize_to_polars(
    store: FeatureStore,
    entity_df: pd.DataFrame,
    features: Union[List[str], FeatureService],
) -> pl.DataFrame:
    """Materialize historical features to a Polars DataFrame.

    Returns:
        pl.DataFrame: Returns a Polars DataFrame with the features
    """
    retrieval_job: BigQueryRetrievalJob = store.get_historical_features(
        entity_df=entity_df,
        features=features,
    )
    polars_df: pl.DataFrame = pl.from_arrow(retrieval_job.to_arrow())
    return polars_df
