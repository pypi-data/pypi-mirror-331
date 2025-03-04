from .base import Surrogate

import numpy as np
from tqdm import tqdm

import torch
import gpytorch
from gpytorch.models.deep_gps import DeepGP
from gpytorch.models import AbstractVariationalGP
from gpytorch.means import ConstantMean, LinearMean
from gpytorch.likelihoods import GaussianLikelihood
from gpytorch.kernels import RBFKernel, ScaleKernel
from gpytorch.distributions import MultivariateNormal
from gpytorch.mlls import VariationalELBO, DeepApproximateMLL
from gpytorch.variational import CholeskyVariationalDistribution, VariationalStrategy


class DGP(Surrogate):
    def __init__(self, **kwargs):
        super(DGP, self).__init__()

        self.name         = 'DGP'
        self.model        = kwargs['model'] if 'model' in kwargs else None
        self.n_epochs     = kwargs['n_epochs'] if 'n_epochs' in kwargs else 100
        self.lr           = kwargs['lr'] if 'lr' in kwargs else 1e-1
        self.verbose      = kwargs['verbose'] if 'verbose' in kwargs else 1
        self.num_inducing = kwargs['num_inducing'] if 'num_inducing' in kwargs else 22
    
    def fit(self, X, y):

        if self.model is None:
            gen = torch.Generator()
            gen.manual_seed(2208060503)
            inducing_points = torch.rand(self.num_inducing, X.shape[1], generator=gen)
            output_inducing = torch.rand(self.num_inducing, y.shape[1], generator=gen) * 10
            self.model = DeepGPModel(inducing_points, output_inducing)
        
        X = torch.tensor(X).float()
        y = torch.tensor(y).float().squeeze()
        
        self.model.train()
        self.model.likelihood.train()
        
        optimizer = torch.optim.Adam(self.model.parameters(), lr=self.lr)

        mll = DeepApproximateMLL(VariationalELBO(self.model.likelihood, self.model, num_data=y.shape[0]))

        if self.verbose > 1:
            pbar = tqdm(range(self.n_epochs), leave=False)
        else:
            pbar = range(self.n_epochs)
        
        for epoch in pbar:
            optimizer.zero_grad()
            output = self.model(X)
            loss = -mll(output, y)
            loss.backward()
            optimizer.step()
            
            if self.verbose > 1:
                pbar.set_description(f'Epoch {epoch + 1}/{self.n_epochs} - Loss: {loss.item():.3f}')

    
    def predict(self, X):

        self.model.eval()
        with torch.no_grad(), gpytorch.settings.fast_pred_var():
            observed_pred = self.model.likelihood(self.model(torch.tensor(X).float()))
            mean = observed_pred.mean
            std = torch.sqrt(observed_pred.variance)

        return mean, std


# Define a single layer GP (inherits from AbstractVariationalGP)
class SingleLayerGP(AbstractVariationalGP):
    def __init__(self, inducing_points, mean='const'):
        variational_distribution = CholeskyVariationalDistribution(inducing_points.size(0))
        variational_strategy = VariationalStrategy(self, inducing_points, variational_distribution)
        super().__init__(variational_strategy)
        self.mean_module = ConstantMean() if mean == 'const' else  LinearMean(inducing_points.size(1))
        self.covar_module = ScaleKernel(RBFKernel(ard_num_dims=inducing_points.size(1)))  # ARD kernel for d-dimensional data

    def forward(self, x):
        mean_x = self.mean_module(x)
        covar_x = self.covar_module(x)
        return MultivariateNormal(mean_x, covar_x)


# class SingleLayerGP(DeepGPLayer):
#     def __init__(self, inducing_points, mean='const'):
#         variational_distribution = CholeskyVariationalDistribution(inducing_points.size(0))
#         variational_strategy = VariationalStrategy(self, inducing_points, variational_distribution)
#         super().__init__(variational_strategy)
#         self.mean_module = ConstantMean() if mean == 'const' else  LinearMean(inducing_points.size(1))
#         self.covar_module = ScaleKernel(RBFKernel(ard_num_dims=inducing_points.size(1)))  # ARD kernel for d-dimensional data

#     def forward(self, x):
#         mean_x = self.mean_module(x)
#         covar_x = self.covar_module(x)
#         return MultivariateNormal(mean_x, covar_x)


# Define DeepGP model (inherits from DeepGP)
class DeepGPModel(DeepGP):
    def __init__(self, inducing_points, output_inducing, mean=['const', 'const']):
        super().__init__()
        # Initialize layers with their own inducing points
        self.input_layer = SingleLayerGP(inducing_points, mean=mean[0])
        self.output_layer = SingleLayerGP(output_inducing, mean=mean[1])
        self.likelihood = GaussianLikelihood()

    def forward(self, x):
        hidden_rep = self.input_layer(x).mean
        output = self.output_layer(hidden_rep)
        return output








# import torch
# import gpytorch
# from gpytorch.models import AbstractVariationalGP
# from gpytorch.models.deep_gps import DeepGP
# from gpytorch.variational import CholeskyVariationalDistribution, VariationalStrategy
# from gpytorch.distributions import MultivariateNormal
# from gpytorch.likelihoods import GaussianLikelihood
# from gpytorch.mlls import VariationalELBO
# from gpytorch.means import ConstantMean, LinearMean
# from gpytorch.kernels import RBFKernel, ScaleKernel
# import matplotlib.pyplot as plt
# from torch.utils.data import DataLoader, TensorDataset
# from tqdm import tqdm





# # Generate synthetic d-dimensional data
# def generate_data(n=100, d=2):
#     torch.manual_seed(42)
#     x = torch.rand(n, d) * 10  # Generate random d-dimensional data
#     y = torch.sin(x[:, 0]) + torch.cos(x[:, 1]) + torch.randn(n) * 0.2  # Simple function of d-dimensional data
#     return x, y

# # Training loop
# def train(model, train_x, train_y, n_epochs=100, lr=1e-1):
#     model.train()
#     model.likelihood.train()
    
#     optimizer = torch.optim.Adam([
#         {'params': model.parameters()},
#     ], lr=lr)

#     mll = VariationalELBO(model.likelihood, model, num_data=train_y.shape[0])
#     pbar = tqdm(range(n_epochs))
    
#     for epoch in pbar:
#         optimizer.zero_grad()
#         output = model(train_x)
#         loss = -mll(output, train_y)
#         loss.backward()
#         optimizer.step()
        
#         pbar.set_description(f'Epoch {epoch + 1}/{n_epochs} - Loss: {loss.item():.3f}')

# # Main function to run the code
# def main():
#     # Generate d-dimensional data
#     d = 2  # Number of dimensions
#     train_x, train_y = generate_data(n=100, d=d)
    
#     # Initialize inducing points with the same dimensionality as the input data
#       # 20 inducing points for d-dimensional data
#     output_inducing = torch.rand(20, 1) * 10
    
#     # Initialize the DeepGP model
#     model = DeepGPModel(inducing_points, output_inducing)
    
#     # Train the model
#     train(model, train_x, train_y, n_epochs=200, lr=1e-1)
    
#     test_x = torch.rand(int(1e3), 2) * 10  # Shape [100, D]
#     with torch.no_grad(), gpytorch.settings.fast_pred_var():
#         observed_pred = model.likelihood(model(test_x))
#         mean = observed_pred.mean
#         variance = observed_pred.variance
#         std_dev = torch.sqrt(variance)  # Posterior standard deviation

#     # Plot results (for 2D input)
#     # if d == 2:
#     y_test = torch.sin(test_x[:, 0]) + torch.cos(test_x[:, 1]) + torch.randn(test_x.size(0)) * 0.2
#     err = (y_test - mean.numpy())**2
    
#     plt.figure(figsize=(10, 6))
#     plt.scatter(test_x[:, 0].numpy(), test_x[:, 1].numpy(), c=err, cmap='viridis', label="Mean Prediction")
#     plt.colorbar(label="Mean Prediction")
#     plt.scatter(train_x[:, 0].numpy(), train_x[:, 1].numpy(), c='r', marker='x', label="Training Data")
#     plt.legend()
#     plt.xlabel("x1")
#     plt.ylabel("x2")
#     plt.title("Deep Gaussian Process Regression (2D Input)")
#     plt.show()

# if __name__ == "__main__":
#     main()