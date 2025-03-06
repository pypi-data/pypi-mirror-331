import pytest
import torch.distributed

from vajra._native.configs import ReplicaResourceConfig, TransferEngineConfig
from vajra._native.transfer_engine import (
    TransferBackendType,
    TransferEngine,
)
from vajra.config import ModelConfig, ParallelConfig
from vajra.datatypes import CommInfo
from vajra.utils import get_ip


@pytest.mark.unit
def test_can_create_transfer_engine():
    """Tests can create a Transfer Engine."""
    model_config = ModelConfig(
        model="meta-llama/Meta-Llama-3-8B", override_num_layers=12
    )
    model_config_c = model_config.native_handle
    parallel_config = ParallelConfig(
        pipeline_parallel_size=1,
        tensor_parallel_size=1,
        kv_parallel_size=1,
        enable_sequence_pipeline_parallel=True,
    )
    parallel_config_c = parallel_config.native_handle
    replica_resource_mapping = [
        ReplicaResourceConfig(parallel_config_c, model_config_c)
    ]
    comm_info = CommInfo(get_ip())
    global_rank = 0
    torch.distributed.init_process_group(
        backend="nccl",
        world_size=parallel_config.world_size,
        rank=global_rank,
        init_method=comm_info.distributed_init_method,
    )
    transfer_engine_config = TransferEngineConfig(
        TransferBackendType.TORCH,
        global_rank,
        replica_resource_mapping,
        torch.distributed.group.WORLD,
    )
    transfer_engine = TransferEngine.create_from(transfer_engine_config)
    assert transfer_engine is not None
