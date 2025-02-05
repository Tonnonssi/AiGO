#include <torch/extension.h>
#include <pybind11/pybind11.h>
#include <pybind11/numpy.h> 
#include <vector>
#include <memory>
#include <cmath>
#include "mcts.h"

namespace py = pybind11;

Node::Node(py::object state, float prior_p)
    : state(state), n(0), w(0.0), p(prior_p), child_nodes() { }

float Node::evaluate_value(torch::jit::script::Module& model) {
    bool is_done = state.attr("is_done")().cast<bool>();
    
    if (is_done) {
        // judge current value 
        bool is_lose = state.attr("is_lose")().cast<bool>();
        float value = is_lose ? -1.0f : 0.0f;

        // update value & n_visit 
        n++;
        w += value;

        return value;
    }

    if (child_nodes.empty()) {
        auto prediction = predict(model, state);
        std::vector<float> legal_policy = prediction.first;
        float value = prediction.second;

        // update value & n_visit 
        n++;
        w += value;

        // expand 
        std::vector<int> legal_actions = state.attr("legal_actions").cast<std::vector<int>>();
        for (size_t i = 0; i < legal_actions.size(); i++) {
            child_nodes.emplace_back(std::make_shared<Node>(state.attr("next")(legal_actions[i]), legal_policy[i]));
        }

        return value;

    } else {
        std::shared_ptr<Node> next_node = select_next_child_node();
        float value = - next_node->evaluate_value(model);

        // update value & n_visit 
        n++;
        w += value;

        return value;
    }
}

std::shared_ptr<Node> Node::select_next_child_node() {
    float C_PUCT = 1.0f;

    // count total visits
    int total_visit = 0;
    for (const std::shared_ptr<Node>& child : child_nodes) {
        total_visit += child->n;
    }

    std::vector<float> values;
    for (const std::shared_ptr<Node>& child : child_nodes) {
        float q_value = (child->n > 0) ? -(child->w / child->n) : 0.0f;
        float node_value = q_value + C_PUCT * child->p * std::sqrt(total_visit) / (1 + child->n);
        values.push_back(node_value);
    }

    auto max_it = std::max_element(values.begin(), values.end());
    size_t max_idx = std::distance(values.begin(), max_it);
    
    return child_nodes[max_idx];
}

std::pair<std::vector<float>, float> predict(torch::jit::script::Module& model, py::object state) {
    // setting device 
    auto parms = model.parameters();
    torch::Device device = (*parms.begin()).device();

    // get input value 
    py::array_t<float> state_array = state.attr("__call__")().cast<py::array_t<float>>();
    auto state_buffer = state_array.request(); 

    // array -> tensor 
    torch::Tensor x = torch::from_blob(state_buffer.ptr, {1, state_buffer.shape[0], state_buffer.shape[1], state_buffer.shape[2]}, torch::dtype(torch::kFloat32));
    x = x.clone().to(device);

    // inference setting
    model.eval();
    torch::NoGradGuard no_grad;

    auto outputs = model.forward({x}).toTuple();
    torch::Tensor raw_policy = outputs->elements()[0].toTensor().detach().cpu().reshape({-1});
    torch::Tensor value_tensor = outputs->elements()[1].toTensor().detach();
    float value = value_tensor.item<float>();

    // get legal actions
    std::vector<int> legal_actions = state.attr("legal_actions").cast<std::vector<int>>();

    // calculate legal policy
    std::vector<float> legal_policy;
    float policy_sum = 0.0;

    for (int action : legal_actions) {
        float p = raw_policy[action].item<float>();
        legal_policy.push_back(p);
        policy_sum += p;
    }

    // normalize legal policy
    if (policy_sum > 0) { 
        for (float &p : legal_policy) { 
            p /= policy_sum;
        }
    }

    return {legal_policy, value};
}