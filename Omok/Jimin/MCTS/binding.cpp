#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "mcts.h"

namespace py = pybind11;

PYBIND11_MODULE(MCTS_cpp, m) {
    py::class_<Node, std::shared_ptr<Node>>(m, "Node")
        .def(py::init<py::object, float>())
        .def("evaluate_value", &Node::evaluate_value)
        .def("select_next_child_node", &Node::select_next_child_node)
        .def_readwrite("n", &Node::n)
        .def_readwrite("p", &Node::p)
        .def_readwrite("w", &Node::w)
        .def_readwrite("state", &Node::state)
        .def_readwrite("child_nodes", &Node::child_nodes);

    m.def("predict", &predict);

    py::module_ torch_module = py::module_::import("torch");
    m.attr("jit_load") = torch_module.attr("jit").attr("load");
}