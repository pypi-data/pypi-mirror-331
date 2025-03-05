import numpy as np
import pandas as pd
from ddsketch.ddsketch import DDSketch

from vajra._native.metrics_store import Metric

from ..datastores.base_cdf_datastore import BaseCDFDataStore
from ..datastores.base_datastore import BaseDataStore

SKETCH_RELATIVE_ACCURACY = 0.001
SKETCH_NUM_QUANTILES_IN_DF = 101


class UnlabeledCDFDataStore(BaseCDFDataStore):

    def __init__(
        self,
        metric: Metric,
        plot_dir: str,
        store_png: bool = False,
    ) -> None:
        super().__init__(metric, plot_dir, store_png)

        assert not metric.requires_label

        # metrics are a data series of two-dimensional (x, y) data points
        self.sketch = DDSketch(relative_accuracy=SKETCH_RELATIVE_ACCURACY)

    def sum(self) -> float:
        return self.sketch.sum

    def __len__(self):
        return int(self.sketch.count)

    def merge(self, other: BaseDataStore) -> None:
        assert isinstance(other, UnlabeledCDFDataStore)
        assert self == other

        self.sketch.merge(other.sketch)

    def put(self, label: str, value: float) -> None:
        self.sketch.add(value)

    def to_series(self) -> pd.Series:
        # get quantiles at 1% intervals
        quantiles = np.linspace(0, 1, num=SKETCH_NUM_QUANTILES_IN_DF)
        # get quantile values
        quantile_values = [self.sketch.get_quantile_value(q) for q in quantiles]
        # create dataframe
        series = pd.Series(quantile_values, name=self.metric.name)

        series *= self.value_multiplier

        return series

    def to_df(self) -> pd.DataFrame:
        return self.to_series().to_frame()
