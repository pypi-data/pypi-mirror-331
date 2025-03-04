from __future__ import annotations
from typing import List, Iterable
from feast import FeatureView, FeatureService, FeatureStore


def get_feature_views_from_feature_service(
    store: FeatureStore, feature_service: FeatureService
) -> List[FeatureView]:
    feature_views: Iterable[FeatureView] = [
        store.get_feature_view(projection.name)
        for projection in feature_service.feature_view_projections
    ]
    return feature_views
