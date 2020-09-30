import torch.nn as nn
import torch
import random
import copy

class NeuralNetwork(nn.Module):
    def __init__(self, rng_state):
        super().__init__()

        # Inputs to layer linear transformation
        self.input = nn.Linear(in_features=5, out_features=24)
        # Hidden layer
        self.hidden = nn.Linear(in_features=24, out_features=32)
        # Output layer
        self.output = nn.Linear(in_features=32, out_features=2)
        # Define sigmoid activation and softmax output
        self.sigmoid = nn.Sigmoid()

        self.rng_state = rng_state
        torch.manual_seed(rng_state)

        self.evolve_states = []
        self.add_tensors = {}

        for name, tensor in self.named_parameters():
            if tensor.size() not in self.add_tensors:
                self.add_tensors[tensor.size()] = torch.Tensor(tensor.size())
            if 'weight' in name:
                nn.init.kaiming_normal_(tensor)
            else:
                tensor.data.zero_()

    def forward(self, x):
        x = self.input(x)
        x = self.hidden(x)
        x = self.sigmoid(x)
        x = self.output(x)
        return x

    def evolve(self, sigma, rng_state):
        torch.manual_seed(rng_state)
        self.evolve_states.append((sigma, rng_state))

        for name, tensor in sorted(self.named_parameters()):
            to_add = self.add_tensors[tensor.size()]
            to_add.normal_(0.0, sigma)
            tensor.data.add_(to_add)

class CompressedModel:
    def __init__(self, start_rng=None, other_rng=None):
        self.start_rng = start_rng if start_rng is not None else self.random_state()
        self.other_rng = other_rng if other_rng is not None else []

    def random_state(self):
        return random.randint(0, 2 ** 31 - 1)

    def evolve(self, sigma, rng_state=None):
        self.other_rng.append((sigma, rng_state if rng_state is not None else self.random_state()))

    def uncompress_model(self):
        start_rng, other_rng = self.start_rng, self.other_rng
        m = NeuralNetwork(start_rng)
        for sigma, rng in other_rng:
            m.evolve(sigma, rng)

        return m

    def recover_model(self, best_model, start_rng, other_rng, index):
        copy_model = copy.deepcopy(best_model)
        self.start_rng = copy.deepcopy(start_rng)

        if other_rng is not None:
            self.other_rng = copy.deepcopy(other_rng)
            if index > 0:
                for sigma, rng in self.other_rng:
                    copy_model.evolve(sigma, rng)

        return copy_model


# class NetworkLight(nn.Module):
#     def __init__(self):
#         super(NetworkLight, self).__init__()
#         self.conv_layers = nn.Sequential(
#             nn.Conv2d(3, 24, 3, stride=2),
#             nn.ELU(),
#             nn.Conv2d(24, 48, 3, stride=2),
#             nn.MaxPool2d(4, stride=4),
#             nn.Dropout(p=0.25)
#         )
#         self.linear_layers = nn.Sequential(
#             nn.Linear(in_features=48 * 4 * 19, out_features=50),
#             nn.ELU(),
#             nn.Linear(in_features=50, out_features=10),
#             nn.Linear(in_features=10, out_features=1)
#         )
#
#     def forward(self, input):
#         input = input.view(input.size(0), 3, 70, 320)
#         output = self.conv_layers(input)
#         print(output.shape)
#         output = output.view(output.size(0), -1)
#         output = self.linear_layers(output)
#         return output