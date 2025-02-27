import torch_geometric.transforms as T

from .unit_edge_attr_gaussian_noise import UnitEdgeAttrGaussianNoise


class AugmentHemibrain:
    """
    Combines multiple pyg transforms to form the full data augmentation for hemibrain data

    Args:
        config (namespace): global configuration namespace
    """

    def __init__(self, config):
        rotations = [T.RandomRotate(180, axis=i) for i in range(3)]
        translation = T.RandomTranslate(config.augment_translate_limit)
        merge_score_noise = UnitEdgeAttrGaussianNoise(
            mu=0, sigma=config.edge_attr_noise_std)
        self.transform = T.Compose(
            [*rotations, translation, merge_score_noise])

    def __call__(self, data):
        return self.transform(data)

    def __repr__(self):
        return self.transform.__repr__()
