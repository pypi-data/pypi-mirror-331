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
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include "native/core/BlockSpaceManager.h"

namespace py = pybind11;

void InitCorePybindSubmodule(py::module& pm) {
  auto m = pm.def_submodule("core", "Core submodule");

  py::class_<vajra::BlockSpaceManager,
             std::shared_ptr<vajra::BlockSpaceManager>>(m, "BlockSpaceManager")
      .def(py::init<int, int, int, float>(), py::arg("block_size"),
           py::arg("num_gpu_blocks"), py::arg("max_model_len"),
           py::arg("watermark") = 0.01f)
      .def("can_allocate_blocks", &vajra::BlockSpaceManager::CanAllocateBlocks)
      .def("allocate", &vajra::BlockSpaceManager::Allocate)
      .def("allocate_delta", &vajra::BlockSpaceManager::AllocateDelta)
      .def("can_append_slot", &vajra::BlockSpaceManager::CanAppendSlot)
      .def("append_slot", &vajra::BlockSpaceManager::AppendSlot)
      .def("free", &vajra::BlockSpaceManager::Free)
      .def("get_block_table", &vajra::BlockSpaceManager::GetBlockTableCopy)
      .def("is_allocated", &vajra::BlockSpaceManager::IsAllocated);
}
