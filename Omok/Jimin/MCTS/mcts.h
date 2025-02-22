#ifndef MCTS_H
#define MCTS_H

#include <vector>
#include <cmath>
#include <algorithm>
#include <numeric>
#include <torch/extension.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

namespace py = pybind11; // as py로 명명 

class Node {
public:
    // 생성자
    Node(py::object state, float prior_p); 

    // attributes 
    py::object state;
    int n;
    float p;
    float w;
    std::vector<std::shared_ptr<Node>> child_nodes;

    // methods
    float evaluate_value(torch::jit::script::Module& model);
    
    std::shared_ptr<Node> select_next_child_node();
    
};

std::pair<std::vector<float>, float> predict(torch::jit::script::Module& model, py::object state);
#endif