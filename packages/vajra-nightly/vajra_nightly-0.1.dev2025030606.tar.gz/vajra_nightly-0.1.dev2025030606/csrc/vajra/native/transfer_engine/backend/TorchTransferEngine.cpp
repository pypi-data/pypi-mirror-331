//==============================================================================
// Copyright 2025 Vajra Team; Georgia Institute of Technology
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
//==============================================================================
#include "native/transfer_engine/backend/TorchTransferEngine.h"

#include "commons/StdCommon.h"
#include "native/transfer_engine/backend/TorchTransferWork.h"
//==============================================================================
using vajra::TorchTransferEngine;
using vajra::TorchTransferWork;
using vajra::TransferWork;
//==============================================================================
TorchTransferEngine::TorchTransferEngine(
    std::size_t global_rank, const ReplicaResourceMapping& replica_mapping,
    c10::intrusive_ptr<c10d::ProcessGroup> global_process_group)
    : global_rank_(global_rank),
      replica_id_(0),
      replica_mapping_(replica_mapping),
      global_process_group_(global_process_group) {
  // TODO(Kasra): more asserts as the impl comes through
}
//==============================================================================
// TODO(Kasra): Transfer Engine implementation
std::unique_ptr<TransferWork> TorchTransferEngine::AsyncSend(
    std::size_t dst_replica_id, torch::Tensor const& page_tensor,
    const std::vector<std::size_t>& page_list, std::size_t layer_id) {
  return std::make_unique<TorchTransferWork>();
}
//==============================================================================
std::unique_ptr<TransferWork> TorchTransferEngine::AsyncRecv(
    std::size_t src_replica_id, torch::Tensor const& page_tensor,
    const std::vector<std::size_t>& page_list, std::size_t layer_id) {
  return std::make_unique<TorchTransferWork>();
}
//==============================================================================
