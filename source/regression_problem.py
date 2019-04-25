import torch
import os
import tensorboardX
import torch.nn.functional as F

from model_type import ModelType

import chartify
import pandas as pd
import numpy as np


class RegressionProblem(ModelType):
    def __init__(self, config):
        super(RegressionProblem, self).__init__(config)

        self.loss_name = 'MSE Loss'
        self.out_channels = 1

    def out_nonlinearity(self, x):
        return x

    def loss(self, inputs, targets):
        return F.mse_loss(inputs, targets.float(), reduction='mean')

    def out_to_predictions(self, out):
        return out.round()

    def metric(self, predictions, targets):
        correct = torch.squeeze(predictions).eq(targets.float()).sum().item()
        acc = correct / targets.size(0)
        return acc

    def predictions_to_list(self, predictions):
        return torch.squeeze(predictions).tolist()

    def plot_targets_vs_outputs(self, targets, outputs):
        ch = chartify.Chart(blank_labels=True)
        ch.plot.scatter(
            data_frame=pd.DataFrame({'t': targets, 'p': outputs}),
            x_column='t',
            y_column='p',
        ).axes.set_xaxis_label('targets') \
            .axes.set_yaxis_label('predictions') \
            .set_title('Targets vs. Predictions')

        max_val = np.ceil(np.max(np.array([targets, outputs])))
        ch.plot.line(
            data_frame=pd.DataFrame({'x': np.arange(max_val)}),
            x_column='x',
            y_column='x',
        )

        ch.save(filename=os.path.join(self.config.temp_dir, 'targets_vs_outputs_test.png'), format='png')