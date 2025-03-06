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
#include "native/configs/ConfigsPybind.h"

#include "commons/Logging.h"
#include "native/configs/ModelConfig.h"
#include "native/configs/ParallelConfig.h"
#include "native/configs/ReplicaResourceMapping.h"
#include "native/configs/TransferEngineConfig.h"

//==============================================================================
void InitConfigsPybindSubmodule(py::module_& pm) {
  auto m = pm.def_submodule("configs", "Configs submodule");

  py::class_<vajra::ModelConfig>(m, "ModelConfig")
      .def(py::init<std::string, bool, std::optional<std::string>, std::string,
                    std::string, std::size_t, std::optional<std::string>,
                    std::size_t, std::size_t>(),
           py::arg("model"), py::arg("trust_remote_code"),
           py::arg("download_dir"), py::arg("load_format"), py::arg("dtype"),
           py::arg("seed"), py::arg("revision"), py::arg("max_model_len"),
           py::arg("total_num_layers"))
      .def_readonly("model", &vajra::ModelConfig::model)
      .def_readonly("trust_remote_code", &vajra::ModelConfig::trust_remote_code)
      .def_readonly("download_dir", &vajra::ModelConfig::download_dir)
      .def_readonly("load_format", &vajra::ModelConfig::load_format)
      .def_readonly("dtype", &vajra::ModelConfig::dtype)
      .def_readonly("seed", &vajra::ModelConfig::seed)
      .def_readonly("revision", &vajra::ModelConfig::revision)
      .def_readonly("max_model_len", &vajra::ModelConfig::max_model_len)
      .def_readonly("total_num_layers", &vajra::ModelConfig::total_num_layers)
      .def("__copy__",
           [](const vajra::ModelConfig& self) {
             return vajra::ModelConfig(self);
           })
      .def("__deepcopy__", [](const vajra::ModelConfig& self,
                              py::dict) { return vajra::ModelConfig(self); })
      .def(py::pickle(
          [](const vajra::ModelConfig& p) {  // __getstate__
            return py::make_tuple(p.model, p.trust_remote_code, p.download_dir,
                                  p.load_format, p.dtype, p.seed, p.revision,
                                  p.max_model_len, p.total_num_layers);
          },
          [](py::tuple t) {  // __setstate__
            ASSERT_VALID_RUNTIME(t.size() == 9,
                                 "Invalid pickled state for ModelConfig!");

            return vajra::ModelConfig(
                t[0].cast<std::string>(), t[1].cast<bool>(),
                t[2].cast<std::optional<std::string>>(),
                t[3].cast<std::string>(), t[4].cast<std::string>(),
                t[5].cast<std::size_t>(),
                t[6].cast<std::optional<std::string>>(),
                t[7].cast<std::size_t>(), t[8].cast<std::size_t>());
          }));

  //==============================================================================
  py::class_<vajra::ParallelConfig>(m, "ParallelConfig")
      .def(py::init<std::size_t, std::size_t, bool, bool, bool, std::size_t,
                    std::size_t>(),
           py::arg("pipeline_parallel_size"), py::arg("tensor_parallel_size"),
           py::arg("enable_expert_parallel"),
           py::arg("enable_sequence_pipeline_parallel"),
           py::arg("enable_chunked_pipeline_comm_opt"),
           py::arg("kv_parallel_size"), py::arg("max_num_tokens_per_kvp_group"))
      .def_readonly("pipeline_parallel_size",
                    &vajra::ParallelConfig::pipeline_parallel_size)
      .def_readonly("tensor_parallel_size",
                    &vajra::ParallelConfig::tensor_parallel_size)
      .def_readonly("enable_expert_parallel",
                    &vajra::ParallelConfig::enable_expert_parallel)
      .def_readonly("enable_sequence_pipeline_parallel",
                    &vajra::ParallelConfig::enable_sequence_pipeline_parallel)
      .def_readonly("enable_chunked_pipeline_comm_opt",
                    &vajra::ParallelConfig::enable_chunked_pipeline_comm_opt)
      .def_readonly("kv_parallel_size",
                    &vajra::ParallelConfig::kv_parallel_size)
      .def_readonly("max_num_tokens_per_kvp_group",
                    &vajra::ParallelConfig::max_num_tokens_per_kvp_group)
      .def_readonly("world_size", &vajra::ParallelConfig::world_size)
      .def("__copy__",
           [](const vajra::ParallelConfig& self) {
             return vajra::ParallelConfig(self);
           })
      .def("__deepcopy__", [](const vajra::ParallelConfig& self,
                              py::dict) { return vajra::ParallelConfig(self); })
      .def(py::pickle(
          [](const vajra::ParallelConfig& p) {
            return py::make_tuple(
                p.pipeline_parallel_size, p.tensor_parallel_size,
                p.enable_expert_parallel, p.enable_sequence_pipeline_parallel,
                p.enable_chunked_pipeline_comm_opt, p.kv_parallel_size,
                p.max_num_tokens_per_kvp_group);
          },
          [](py::tuple t) {
            ASSERT_VALID_RUNTIME(t.size() == 7,
                                 "Invalid pickled state for ParallelConfig!");

            return vajra::ParallelConfig(
                t[0].cast<std::size_t>(), t[1].cast<std::size_t>(),
                t[2].cast<bool>(), t[3].cast<bool>(), t[4].cast<bool>(),
                t[5].cast<std::size_t>(), t[6].cast<std::size_t>());
          }));

  //==============================================================================
  py::class_<vajra::ReplicaResourceConfig>(m, "ReplicaResourceConfig")
      .def(py::init<vajra::ParallelConfig&, vajra::ModelConfig&>(),
           py::arg("parallel_config"), py::arg("model_config"))
      .def("__str__", &vajra::ReplicaResourceConfig::ToString)
      .def("__repr__", &vajra::ReplicaResourceConfig::ToString)
      .def_readonly("tensor_parallel_size",
                    &vajra::ReplicaResourceConfig::tensor_parallel_size)
      .def_readonly("pipeline_parallel_size",
                    &vajra::ReplicaResourceConfig::pipeline_parallel_size)
      .def_readonly("kv_parallel_size",
                    &vajra::ReplicaResourceConfig::kv_parallel_size)
      .def_readonly("local_num_layers",
                    &vajra::ReplicaResourceConfig::local_num_layers)
      .def_readonly("total_num_layers",
                    &vajra::ReplicaResourceConfig::total_num_layers)
      .def_readonly("world_size", &vajra::ReplicaResourceConfig::world_size);

  //==============================================================================
  py::class_<vajra::TransferEngineConfig>(m, "TransferEngineConfig")
      .def(py::init<vajra::TransferBackendType, std::size_t,
                    const vajra::ReplicaResourceMapping&,
                    c10::intrusive_ptr<c10d::ProcessGroup>>(),
           py::arg("transfer_backend_type"), py::arg("global_rank"),
           py::arg("replica_mapping"), py::arg("global_process_group"))
      .def_readonly("transfer_backend_type",
                    &vajra::TransferEngineConfig::transfer_backend_type)
      .def_readonly("global_rank", &vajra::TransferEngineConfig::global_rank)
      .def_readonly("replica_mapping",
                    &vajra::TransferEngineConfig::replica_mapping)
      .def_readonly("global_process_group",
                    &vajra::TransferEngineConfig::global_process_group);
}
//==============================================================================
