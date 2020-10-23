import copy
import torch

#
#
#  -------- cross -----------
#
@torch.no_grad()
def cross(
    dom_network,
    rec_network,
    dominance: float = 0.5,
):

    child_network = copy.deepcopy(dom_network)

    for c_layer, r_layer in zip(
        child_network.parameters(),
        rec_network.parameters(),
    ):

        mask_positive = (
            torch.FloatTensor(c_layer.shape).uniform_() > dominance
        ).int()

        mask_negativ = torch.abs(mask_positive - 1)

        c_layer.data = c_layer * mask_positive + r_layer * mask_negativ

    return child_network
