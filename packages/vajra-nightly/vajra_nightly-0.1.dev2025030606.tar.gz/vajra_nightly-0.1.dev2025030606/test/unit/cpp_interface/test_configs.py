import copy
import pickle

import pytest

from vajra._native.configs import ReplicaResourceConfig
from vajra.config import ModelConfig, ParallelConfig


@pytest.mark.parametrize(
    "model, num_layers",
    [("meta-llama/Meta-Llama-3-8B", 12), ("meta-llama/Meta-Llama-3-70B", 24)],
)
@pytest.mark.unit
def test_valid_model_config_creation(model, num_layers):
    """Tests creating valid ModelConfig objects and accessing their properties."""
    model_config = ModelConfig(model=model, override_num_layers=num_layers)
    model_config_c = model_config.native_handle
    assert model_config.model == model_config_c.model


@pytest.mark.parametrize(
    "tensor_parallel_size, pipeline_parallel_size, kv_parallel_size",
    [(1, 1, 1), (4, 2, 1)],
)
@pytest.mark.unit
def test_valid_parallel_config_creation(
    tensor_parallel_size, pipeline_parallel_size, kv_parallel_size
):
    """Tests creating valid ParallelConfig objects and accessing their properties."""
    parallel_config = ParallelConfig(
        pipeline_parallel_size=pipeline_parallel_size,
        tensor_parallel_size=tensor_parallel_size,
        kv_parallel_size=kv_parallel_size,
        enable_sequence_pipeline_parallel=True,
    )
    parallel_config_c = parallel_config.native_handle
    assert pipeline_parallel_size == parallel_config_c.pipeline_parallel_size
    assert tensor_parallel_size == parallel_config_c.tensor_parallel_size
    assert kv_parallel_size == parallel_config_c.kv_parallel_size


@pytest.mark.parametrize(
    "model, num_layers, tensor_parallel_size, pipeline_parallel_size, kv_parallel_size",
    [
        ("meta-llama/Meta-Llama-3-8B", 12, 1, 1, 1),
        ("meta-llama/Meta-Llama-3-70B", 24, 4, 2, 1),
    ],
)
@pytest.mark.unit
def test_valid_replica_parallel_config_creation(
    model,
    num_layers,
    tensor_parallel_size,
    pipeline_parallel_size,
    kv_parallel_size,
):
    """Tests creating valid ReplicaResourceConfig objects and accessing their properties."""
    parallel_config = ParallelConfig(
        pipeline_parallel_size=pipeline_parallel_size,
        tensor_parallel_size=tensor_parallel_size,
        kv_parallel_size=kv_parallel_size,
        enable_sequence_pipeline_parallel=True,
    )
    model_config = ModelConfig(model=model, override_num_layers=num_layers)
    model_config_c = model_config.native_handle
    parallel_config_c = parallel_config.native_handle

    replica_parallel_config = ReplicaResourceConfig(parallel_config_c, model_config_c)
    assert pipeline_parallel_size == replica_parallel_config.pipeline_parallel_size
    assert tensor_parallel_size == replica_parallel_config.tensor_parallel_size
    assert kv_parallel_size == replica_parallel_config.kv_parallel_size
    assert parallel_config.world_size == replica_parallel_config.world_size
    assert num_layers == replica_parallel_config.total_num_layers
    assert (
        num_layers / pipeline_parallel_size == replica_parallel_config.local_num_layers
    )


@pytest.mark.parametrize(
    "tensor_parallel_size, pipeline_parallel_size, kv_parallel_size",
    [(1, 1, 1), (4, 2, 1)],
)
@pytest.mark.unit
def test_can_deep_copy_parallel_config(
    tensor_parallel_size, pipeline_parallel_size, kv_parallel_size
):
    """Tests deep copying valid ParallelConfig objects and accessing their properties."""
    parallel_config = ParallelConfig(
        pipeline_parallel_size=pipeline_parallel_size,
        tensor_parallel_size=tensor_parallel_size,
        kv_parallel_size=kv_parallel_size,
        enable_sequence_pipeline_parallel=True,
    )
    parallel_config_deep_copy = copy.deepcopy(parallel_config)
    assert pipeline_parallel_size == parallel_config_deep_copy.pipeline_parallel_size
    assert tensor_parallel_size == parallel_config_deep_copy.tensor_parallel_size
    assert kv_parallel_size == parallel_config_deep_copy.kv_parallel_size


@pytest.mark.parametrize(
    "model, num_layers",
    [("meta-llama/Meta-Llama-3-8B", 12), ("meta-llama/Meta-Llama-3-70B", 24)],
)
@pytest.mark.unit
def test_can_deep_copy_model_config(model, num_layers):
    """Tests deep copying valid ModelConfig objects and accessing their properties."""
    model_config = ModelConfig(model=model, override_num_layers=num_layers)
    model_config_deep_copy = copy.deepcopy(model_config)
    assert model_config.model == model_config_deep_copy.model


@pytest.mark.parametrize(
    "tensor_parallel_size, pipeline_parallel_size, kv_parallel_size",
    [(1, 1, 1), (4, 2, 1)],
)
@pytest.mark.unit
def test_can_pickle_parallel_config(
    tensor_parallel_size, pipeline_parallel_size, kv_parallel_size
):
    """Tests pickling ParallelConfig objects and accessing their properties."""
    parallel_config = ParallelConfig(
        pipeline_parallel_size=pipeline_parallel_size,
        tensor_parallel_size=tensor_parallel_size,
        kv_parallel_size=kv_parallel_size,
        enable_sequence_pipeline_parallel=True,
    )

    # Pickle the object
    pickled_config = pickle.dumps(parallel_config)

    # Unpickle the object
    parallel_config_from_pickle = pickle.loads(pickled_config)

    assert pipeline_parallel_size == parallel_config_from_pickle.pipeline_parallel_size
    assert tensor_parallel_size == parallel_config_from_pickle.tensor_parallel_size
    assert kv_parallel_size == parallel_config_from_pickle.kv_parallel_size


@pytest.mark.parametrize(
    "model, num_layers",
    [("meta-llama/Meta-Llama-3-8B", 12), ("meta-llama/Meta-Llama-3-70B", 24)],
)
@pytest.mark.unit
def test_can_pickle_model_config(model, num_layers):
    """Tests pickling ModelConfig objects and accessing their properties."""
    model_config = ModelConfig(model=model, override_num_layers=num_layers)

    # Pickle the object
    pickled_config = pickle.dumps(model_config)

    # Unpickle the object
    model_config_from_pickle = pickle.loads(pickled_config)

    assert model_config.model == model_config_from_pickle.model
