import botorch
import sklearn.mixture
import torch
import numpy as np
from copy import deepcopy
from scipy import optimize
import warnings
from typing import List, Literal, Optional

from sklearn.mixture import GaussianMixture
from sklearn.metrics import silhouette_score


class AcqFuncScaling:
    def __init__(self):
        self.scaling = None


# TODO: Update or delete
# class UpperConfidenceBoundRandom(botorch.acquisition.AnalyticAcquisitionFunction):
#     from typing import Optional, Union
#     from torch import Tensor
#     from botorch.models.model import Model
#     from botorch.acquisition.objective import ScalarizedObjective
#     from botorch.utils.transforms import t_batch_mode_transform
#
#     def __init__(
#             self,
#             model: Model,
#             beta: Union[float, Tensor],
#             gamma: Union[float, Tensor],
#             objective: Optional[ScalarizedObjective] = None,
#             maximize: bool = True,
#     ) -> None:
#         super().__init__(model=model, objective=objective)
#         self.maximize = maximize
#         if not torch.is_tensor(beta):
#             beta = torch.tensor(beta)
#         if not torch.is_tensor(gamma):
#             gamma = torch.tensor(gamma)
#         self.register_buffer("beta", beta)
#         self.register_buffer("gamma", gamma)
#
#     @t_batch_mode_transform(expected_q=1)
#     def forward(self, X: Tensor) -> Tensor:
#         r"""Evaluate the Upper Confidence Bound on the candidate set X.
#
#         Args:
#             X: A `(b) x 1 x d`-dim Tensor of `(b)` t-batches of `d`-dim design
#                 points each.
#
#         Returns:
#             A `(b)`-dim Tensor of Upper Confidence Bound values at the given
#             design points `X`.
#         """
#         self.beta = self.beta.to(X)
#         self.gamma = self.gamma.to(X)
#         posterior = self._get_posterior(X=X)
#         batch_shape = X.shape[:-2]
#         mean = posterior.mean.view(batch_shape)
#         variance = posterior.variance.view(batch_shape)
#         delta = self.beta.expand_as(mean) * variance.sqrt()
#         rand_number = (torch.randn(1).to(X) * self.gamma).expand_as(mean)
#         if self.maximize:
#             return mean + delta + rand_number
#         else:
#             return mean - delta + rand_number


# class UpperConfidenceBoundRandomVar(botorch.acquisition.AnalyticAcquisitionFunction):
#     from typing import Optional, Union
#     from torch import Tensor
#     from botorch.models.model import Model
#     from botorch.acquisition.objective import ScalarizedObjective
#     from botorch.utils.transforms import t_batch_mode_transform
#
#     def __init__(
#             self,
#             model: Model,
#             beta: Union[float, Tensor],
#             gamma: Union[float, Tensor],
#             objective: Optional[ScalarizedObjective] = None,
#             maximize: bool = True,
#     ) -> None:
#         super().__init__(model=model, objective=objective)
#         self.maximize = maximize
#         if not torch.is_tensor(beta):
#             beta = torch.tensor(beta)
#         if not torch.is_tensor(gamma):
#             gamma = torch.tensor(gamma)
#         self.register_buffer("beta", beta)
#         self.register_buffer("gamma", gamma)
#
#     @t_batch_mode_transform(expected_q=1)
#     def forward(self, X: Tensor) -> Tensor:
#         r"""Evaluate the Upper Confidence Bound on the candidate set X.
#
#         Args:
#             X: A `(b) x 1 x d`-dim Tensor of `(b)` t-batches of `d`-dim design
#                 points each.
#
#         Returns:
#             A `(b)`-dim Tensor of Upper Confidence Bound values at the given
#             design points `X`.
#         """
#         self.beta = self.beta.to(X)
#         self.gamma = self.gamma.to(X)
#         posterior = self._get_posterior(X=X)
#         batch_shape = X.shape[:-2]
#         mean = posterior.mean.view(batch_shape)
#         variance = posterior.variance.view(batch_shape)
#         delta = self.beta.expand_as(mean) * variance.sqrt()
#         rand_number = delta * (torch.randn(1).to(X) * self.gamma).expand_as(mean)
#         if self.maximize:
#             return mean + delta + rand_number
#         else:
#             return mean - delta + rand_number
#
#     def perturb_opt_acq_result(self, candidate_point, bounds, n_initsearch=1000, n_randsearch=5000):
#
#         posterior = self.model.posterior
#
#         post_candidate = posterior(candidate_point)
#         candidate_value = post_candidate.mean
#         candidate_var = post_candidate.variance
#
#         local_bounds = torch.zeros(bounds.shape)
#
#         for parameter_ind in range(len(bounds.T)):
#
#             par_vals = torch.linspace(bounds.T[parameter_ind][0], bounds.T[parameter_ind][1], steps=n_initsearch)
#
#             all_pars_vals = np.repeat(deepcopy(candidate_point), n_initsearch, axis=0)
#             all_pars_vals[:, parameter_ind] = par_vals
#
#             f_0 = candidate_value - candidate_var.sqrt() * (self.beta + self.beta * self.gamma * 1.6)
#
#             post_x = posterior(all_pars_vals)
#
#             g_x = post_x.mean + post_x.variance.sqrt() * (self.beta + self.beta * self.gamma * 1.6)
#
#             # TODO: Debug the bounds, maybe set the 1.6 down a bit? Idk. It's a bit troubling that beta keeps the
#             #  bounds wide even when gamma is low
#
#             lowerbound_ind = np.argmax(g_x > f_0)
#             upperbound_ind = n_initsearch - 1 - torch.tensor(np.argmax(np.flip(np.array(g_x > f_0))))
#
#             local_bounds.T[parameter_ind, 0] = par_vals[int(lowerbound_ind)]
#             local_bounds.T[parameter_ind, 1] = par_vals[upperbound_ind]
#
#         rand_search_pars = torch.rand([n_randsearch, len(bounds.T)])
#
#         for parameter_ind in range(len(bounds.T)):
#             rand_search_pars[:, parameter_ind] = (local_bounds.T[parameter_ind, 1] -
#                                                   local_bounds.T[parameter_ind, 0]) * \
#                                                  rand_search_pars[:, parameter_ind] + local_bounds.T[parameter_ind, 0]
#
#         rand_search_vals = torch.zeros(n_randsearch)
#
#         for par_vals_ind in range(len(rand_search_vals)):
#             rand_search_vals[par_vals_ind] = self.forward(rand_search_pars[par_vals_ind].unsqueeze(0).unsqueeze(0))
#
#         print("Bounds: ", bounds)
#         print("Local Bounds: ", local_bounds)
#
#         return rand_search_pars[rand_search_vals.argmax()].unsqueeze(0)


# TODO: Change or delete
# class qUpperConfidenceBoundRandomVar(botorch.acquisition.monte_carlo.MCAcquisitionFunction):
#     r"""MC-based batch Upper Confidence Bound.
#     NB: With noise! :D
#
#     Uses a reparameterization to extend UCB to qUCB for q > 1 (See Appendix A
#     of [Wilson2017reparam].)
#
#     `qUCB = E(max(mu + |Y_tilde - mu|))`, where `Y_tilde ~ N(mu, beta pi/2 Sigma)`
#     and `f(X)` has distribution `N(mu, Sigma)`.
#
#     Example:
#         >>> model = SingleTaskGP(train_X, train_Y)
#         >>> sampler = SobolQMCNormalSampler(1000)
#         >>> qUCB = qUpperConfidenceBound(model, 0.1, sampler)
#         >>> qucb = qUCB(test_X)
#     """
#     from typing import Optional, Union
#     from torch import Tensor
#     from botorch.models.model import Model
#     from botorch.acquisition.monte_carlo import MCSampler, MCAcquisitionObjective
#     from botorch.utils.transforms import t_batch_mode_transform, concatenate_pending_points
#
#     def __init__(
#         self,
#         model: Model,
#         beta: float,
#         gamma: float,
#         sampler: Optional[MCSampler] = None,
#         objective: Optional[MCAcquisitionObjective] = None,
#         X_pending: Optional[Tensor] = None,
#     ) -> None:
#         r"""q-Upper Confidence Bound.
#
#         Args:
#             model: A fitted model.
#             beta: Controls tradeoff between mean and standard deviation in UCB.
#             sampler: The sampler used to draw base samples. Defaults to
#                 `SobolQMCNormalSampler(num_samples=500, collapse_batch_dims=True)`
#             objective: The MCAcquisitionObjective under which the samples are
#                 evaluated. Defaults to `IdentityMCObjective()`.
#             X_pending:  A `m x d`-dim Tensor of `m` design points that have
#                 points that have been submitted for function evaluation
#                 but have not yet been evaluated.  Concatenated into X upon
#                 forward call.  Copied and set to have no gradient.
#         """
#         super().__init__(
#             model=model, sampler=sampler, objective=objective, X_pending=X_pending
#         )
#         import math
#         self.beta_prime = math.sqrt(beta * math.pi / 2)
#         self.gamma = gamma
#
#     @concatenate_pending_points
#     @t_batch_mode_transform()
#     def forward(self, X: Tensor) -> Tensor:
#         r"""Evaluate qUpperConfidenceBound on the candidate set `X`.
#
#         Args:
#             X: A `(b) x q x d`-dim Tensor of `(b)` t-batches with `q` `d`-dim
#                 design points each.
#
#         Returns:
#             A `(b)`-dim Tensor of Upper Confidence Bound values at the given
#             design points `X`.
#         """
#         posterior = self.model.posterior(X)
#         samples = self.sampler(posterior)
#         obj = self.objective(samples)
#         mean = obj.mean(dim=0)
#         rand_number = self.beta_prime * (obj - mean).abs() * (torch.randn(1).to(X) * self.gamma).expand_as(mean)
#         ucb_samples = mean + self.beta_prime * (obj - mean).abs() + rand_number
#         return ucb_samples.max(dim=-1)[0].mean(dim=0)


# TODO: Review if neccesary, maybe delete?
# class UpperConfidenceBoundRandomVarDist(botorch.acquisition.AnalyticAcquisitionFunction):
#     from typing import Optional, Union
#     from torch import Tensor
#     from botorch.models.model import Model
#     from botorch.acquisition.objective import ScalarizedObjective
#     from botorch.utils.transforms import t_batch_mode_transform
#
#     def __init__(
#             self,
#             model: Model,
#             beta: Union[float, Tensor],
#             gamma: Union[float, Tensor],
#             alpha: Union[float, Tensor],
#             omega: Union[float, Tensor],
#             objective: Optional[ScalarizedObjective] = None,
#             maximize: bool = True,
#     ) -> None:
#         super().__init__(model=model, objective=objective)
#         self.maximize = maximize
#         if not torch.is_tensor(beta):
#             beta = torch.tensor(beta)
#         if not torch.is_tensor(gamma):
#             gamma = torch.tensor(gamma)
#         if not torch.is_tensor(alpha):
#             alpha = torch.tensor(alpha)
#         if not torch.is_tensor(omega):
#             omega = torch.tensor(omega)
#         self.register_buffer("beta", beta)
#         self.register_buffer("gamma", gamma)
#         self.register_buffer("alpha", alpha)
#         self.register_buffer("omega", omega)
#
#     # @t_batch_mode_transform(expected_q=1)
#     def forward(self, X: Tensor, other_points=None) -> Tensor:
#         r"""Evaluate the Upper Confidence Bound on the candidate set X.
#
#         Args:
#             X: A `(b) x 1 x d`-dim Tensor of `(b)` t-batches of `d`-dim design
#                 points each.
#             other_points: List containing the other points chosen in this step
#
#         Returns:
#             A `(b)`-dim Tensor of Upper Confidence Bound values at the given
#             design points `X`.
#         """
#         if other_points is None:
#             other_points = []
#         X = X if X.dim() > 2 else X.unsqueeze(0)
#         self.beta = self.beta.to(X)
#         self.gamma = self.gamma.to(X)
#         self.alpha = self.alpha.to(X)
#         self.omega = self.omega.to(X)
#         posterior = self._get_posterior(X=X)
#         batch_shape = X.shape[:-2]
#         mean = posterior.mean.view(batch_shape)
#         variance = posterior.variance.view(batch_shape)
#         delta = self.beta.expand_as(mean) * variance.sqrt()
#         rand_number = delta * (torch.randn(1).to(X) * self.gamma).expand_as(mean)
#
#         # TODO: Check computations
#         # TODO: THIS IS WRONG. ADD ALPHA
#         proximity_punish = torch.tensor([0.0])
#         scaling = (mean + delta) * self.omega
#         for point in other_points:
#             proximity_punish += scaling * torch.exp(-((torch.sum(X - point) / self.alpha)**2))
#
#         if self.maximize:
#             return mean + delta + rand_number - proximity_punish
#         else:
#             return mean - delta + rand_number + proximity_punish


class OptimiseWithDistPunish:
    def __init__(
            self,
            alpha: float,
            omega: float,
            scaling_class: AcqFuncScaling
    ):
        self.alpha = alpha
        self.omega = omega
        self.scaling_class = scaling_class

    def add_dist_punishment(
            self,
            x: torch.tensor,
            acq_func_val: torch.tensor,
            other_points
    ):

        # TODO: Get the math completely solid
        #   - We are scaling the y axis but assuming range from zero and up. Not necessarily the case
        #   - We should scale with the x axis in case we don't normalise

        # TODO: Make awesome lovely unit tests that confirm that this scales with coordinates + acq func value

        # TODO: Write some good tests for this one, it has previously behaved strangely

        proximity_punish = torch.zeros(len(acq_func_val))
        # scaling = torch.abs(acq_func_val.detach() * self.omega)
        scaling = self.omega * self.scaling_class.scaling
        for point in other_points:
            proximity_punish += scaling * np.exp(-(torch.sum((x - point)**2, dim=1) / (self.alpha**2)))

        return acq_func_val.detach() - proximity_punish


class AcqOptimiser:
    def __init__(self, bounds, function, n_objs, n_evals_per_step=1, params=None):  # , serial_opt=False
        self.bounds = bounds
        self.n_evals_per_step = n_evals_per_step

        self.n_objs = n_objs
        if self.n_objs > 1:
            self.multi_obj = True
        else:
            self.multi_obj = False

        if params is None:
            self.params = {}
        else:
            self.params = params

        self.function = function

    def optimise(self, acq_func):
        return self.function(acq_func)

    def set_params(self, par_name, value):
        self.params[par_name] = value


class PredefinedAcqOptimiser(AcqOptimiser):
    def __init__(
            self,
            bounds,
            n_objs,
            n_evals_per_step=1,
            optimiser_name=None,
            seq_dist_punish=True,
            params_seq_opt=None
    ):

        if optimiser_name is None:
            if n_evals_per_step > 1:
                if seq_dist_punish:
                    self.optimiser_name = 'dual_annealing'
                else:
                    self.optimiser_name = 'botorch'
            else:
                self.optimiser_name = 'dual_annealing'

        else:
            self.optimiser_name = optimiser_name

        if params_seq_opt is None and seq_dist_punish is True:
            raise RuntimeError("Parameters for seq opt must be set up in acq func")

        if self.optimiser_name == 'dual_annealing':
            function = self.dual_annealing

        elif self.optimiser_name == 'botorch':
            function = self.botorch_optim

        else:
            raise ValueError(f"Acquisition function optimiser name '{optimiser_name}' not recognised")

        if n_evals_per_step == 1:
            self.seq_dist_punish = False
        else:
            self.seq_dist_punish = seq_dist_punish

        if self.seq_dist_punish is True:
            self.seq_optimiser = OptimiseWithDistPunish(
                alpha=params_seq_opt['alpha'],
                omega=params_seq_opt['omega'],
                scaling_class=params_seq_opt['scaling']
            )

        super(PredefinedAcqOptimiser, self).__init__(
            bounds,
            function,
            n_objs,
            n_evals_per_step=n_evals_per_step,
            params=params_seq_opt
        )

    def optimise(self, acq_func):
        if not self.seq_dist_punish:
            return self.function(acq_func)
        else:
            return self.optimise_sequentially_w_dist_punisher(acq_func)

    def optimise_sequentially_w_dist_punisher(self, acq_func):

        def dist_punish_wrapper(x, other_points):
            acq_func_val = acq_func(x)

            new_acq_func_val = self.seq_optimiser.add_dist_punishment(x, acq_func_val, other_points)

            return new_acq_func_val

        # TODO: DEBUG THIS
        #  (Currently the first two points are always the same)

        candidates = []
        for candidate_no in range(self.n_evals_per_step):
            candidates.append(self.function(lambda x: dist_punish_wrapper(x, candidates)))
            print(f"Found point {candidate_no + 1} of {self.n_evals_per_step}.")

        candidates = torch.stack(candidates, dim=1).squeeze(0)

        return candidates

    # TODO: Expand to support an arbitrary scipy optimiser
    def dual_annealing(self, acq_func):

        acq_opt_result = optimize.dual_annealing(
            func=lambda x: -acq_func(torch.tensor(x).unsqueeze(0)).detach().numpy(),
            bounds=self.bounds.T,
            maxiter=1000
        )

        candidates, acq_fun_value = [torch.tensor(acq_opt_result.x).unsqueeze(0),
                                     -torch.tensor(acq_opt_result.fun).unsqueeze(0)]
        return candidates

    def botorch_optim(self, acq_func):
        # TODO: Make these parameters changeable from the outside
        # restarts = 10
        # raw_samples = 500
        # restarts = 2
        # raw_samples = 50
        # restarts = 50
        # raw_samples = 1000

        restarts = 500
        raw_samples = 10000

        method = "L-BFGS-B"

        candidates, acq_fun_value = botorch.optim.optimize.optimize_acqf(
            acq_function=acq_func,
            bounds=self.bounds,
            q=self.n_evals_per_step,
            num_restarts=restarts,
            raw_samples=raw_samples,  # used for intialization heuristic
            options={
                "method": method
            }
        )

        return candidates

    def set_params(self, par_name, value):

        self.params[par_name] = value

        if par_name in ["alpha", "omega"]:
            self.seq_optimiser.alpha = value

        elif par_name == "omega":
            self.seq_optimiser.omega = value


class AcqFunction:
    def __init__(
            self,
            function_class,
            bounds,
            n_objs,
            optimiser: AcqOptimiser = None,
            params=None,
            n_evals_per_step=1,
            acqfunc_name=None
    ):

        self.function_class = function_class
        self.bounds = bounds

        if optimiser is None:
            self.optimiser = PredefinedAcqOptimiser(bounds, n_objs, n_evals_per_step=n_evals_per_step)
        else:
            self.optimiser = optimiser

        self.n_objs = n_objs
        if self.n_objs > 1:
            self.multi_obj = True
        else:
            self.multi_obj = False

        if params is None:
            self.params = {}
        else:
            self.params = params

        self.n_evals_per_step = n_evals_per_step
        self.acqfunc_name = acqfunc_name

        self.function = None

    def refresh(self, model, **kwargs):
        if self.params is None:
            # TODO: Check that it's safe to get rid of this option, then delete it
            self.function = self.function_class(model=model, **kwargs)
        else:
            self.function = self.function_class(model=model, **self.params, **kwargs)

    def suggest_point(self):
        return self.optimiser.optimise(self.function)

    def change_bounds(self, new_bounds):
        self.bounds = new_bounds
        self.optimiser.bounds = new_bounds

    def set_params(self, par_name, value):
        self.params[par_name] = value


class DistPunishAcqFunction(AcqFunction):

    def __init__(
            self,
            function_class,
            bounds,
            n_objs: int,
            seq_dist_punish: bool,
            scaling_class: Optional[AcqFuncScaling],
            optimiser: AcqOptimiser = None,
            params=None,
            n_evals_per_step: int = 1,
            acqfunc_name: Optional[str] = None,
            mode: Literal['simple', 'advanced'] = 'advanced'
    ):

        self.seq_dist_punish = seq_dist_punish
        self.scaling_class = scaling_class

        if seq_dist_punish is True:
            assert scaling_class is not None

        assert mode in ['simple', 'advanced']
        self.mode = mode

        super().__init__(
            function_class=function_class,
            bounds=bounds,
            n_objs=n_objs,
            optimiser=optimiser,
            params=params,
            n_evals_per_step=n_evals_per_step,
            acqfunc_name=acqfunc_name,
        )

    def refresh(self, model, **kwargs):
        super().refresh(model, **kwargs)

        if self.seq_dist_punish:

            if self.mode == 'simple':
                self.refresh_scaling_simple()

            elif self.mode == 'advanced':
                self.refresh_scaling_advanced()

    def sample_acq_func(self):
        n_acq_func_samples = 1000
        n_params = self.bounds.shape[1]

        random_coordinates = (
                (self.bounds[1] - self.bounds[0]) * torch.rand(n_acq_func_samples, n_params)
                + self.bounds[0]
        )

        random_coordinates = random_coordinates.unsqueeze(0)

        samples = np.zeros(n_acq_func_samples)

        for coord_ind in range(n_acq_func_samples):
            sample = self.function(random_coordinates[:, coord_ind:coord_ind+1, :])
            samples[coord_ind] = sample.detach().numpy()  # If this is not detached, it causes a memory leak o:)

        return samples

    def refresh_scaling_simple(self):

        acq_func_samples = self.sample_acq_func()

        sampled_std = acq_func_samples.std()

        self.scaling_class.scaling = sampled_std

    def refresh_scaling_advanced(self):

        acq_func_samples = self.sample_acq_func()
        acq_func_samples = np.expand_dims(acq_func_samples, 1)

        min_clusters = 1
        min_scored_clusters = 2
        max_clusters = 7

        gaussian_fitters = {
            n_clusters: GaussianMixture(n_components=n_clusters)
            for n_clusters in range(min_clusters, max_clusters + 1)
        }
        scores = {
            n_clusters: 0.0
            for n_clusters in range(min_scored_clusters, max_clusters + 1)
        }

        for n_clusters in range(min_clusters, max_clusters + 1):

            gaussian_fitters[n_clusters].fit(acq_func_samples)

            if n_clusters >= min_scored_clusters:

                predictions = gaussian_fitters[n_clusters].predict(acq_func_samples)

                if np.unique(predictions).size > 1:
                    scores[n_clusters] = silhouette_score(
                        X=acq_func_samples,
                        labels=predictions
                    )
                else:
                    # TODO: Verify that this is okay
                    scores[n_clusters] = 0.0

        # Someone please make a prettier version of this >:)
        best_score_n_clusters = list(scores.keys())[np.array(list(scores.values())).argmax()]
        best_fitter = gaussian_fitters[best_score_n_clusters]

        # TODO: Finetune and test criterion for n_c=1
        if best_fitter.covariances_.max() * 3 > gaussian_fitters[1].covariances_[0]:
            best_score_n_clusters = 1
            best_fitter = gaussian_fitters[best_score_n_clusters]

        top_cluster_ind = best_fitter.means_.argmax()

        self.scaling_class.scaling = 2 * float(np.sqrt(best_fitter.covariances_[top_cluster_ind]))


class PredefinedAcqFunction(DistPunishAcqFunction):
    def __init__(
            self,
            bounds,
            n_objs,
            n_evals_per_step,
            acqfunc_name=None,
            optimiser_name=None,
            seq_dist_punish=True,
            **kwargs
    ):

        # TODO: Are we potentially missing some asserts for amount of objectives at some of these?

        if acqfunc_name is None:
            if n_objs > 1:
                acqfunc_name = "qLogEHVI"
            else:
                acqfunc_name = "UCB"

        params = {}

        if acqfunc_name == "EI":
            if n_evals_per_step == 1 or seq_dist_punish:
                acq_func_class = botorch.acquisition.analytic.LogExpectedImprovement
            else:
                acq_func_class = botorch.acquisition.monte_carlo.qExpectedImprovement

        elif acqfunc_name == "UCB":

            if "beta" in kwargs:
                beta = kwargs["beta"]
            else:
                beta = 3.0

            params["beta"] = beta

            if n_evals_per_step == 1 or seq_dist_punish:

                acq_func_class = botorch.acquisition.analytic.UpperConfidenceBound

            else:
                acq_func_class = botorch.acquisition.monte_carlo.qUpperConfidenceBound

        elif acqfunc_name == "UCB_Var":

            if "beta" in kwargs:
                beta = kwargs["beta"]
            else:
                beta = 3.0

            if "gamma" in kwargs:
                gamma = kwargs["gamma"]
            else:
                gamma = 0.01

            params["beta"] = beta
            params["gamma"] = gamma

            if n_evals_per_step == 1 or seq_dist_punish:

                raise NotImplementedError("This acquistion function is not available in the current version of veropt.")

                # acq_func_class = UpperConfidenceBoundRandomVar

            else:

                # TODO: Either delete this functionality or review error message (Must specify an objective or a
                #  posterior transform when using a multi-output model.)

                raise NotImplementedError(
                    "This acquistion function is not available in the current version of veropt."
                )

                # acq_func_class = qUpperConfidenceBoundRandomVar

        # TODO: Check whether there's too many objectives for EHVI? (And maybe for the q ver too)
        #  - can then recommend 'qLogEHVI' if this is the case
        elif acqfunc_name == "EHVI":
            acq_func_class = botorch.acquisition.multi_objective.analytic.ExpectedHypervolumeImprovement

        elif acqfunc_name == 'qEHVI':
            acq_func_class = botorch.acquisition.multi_objective.monte_carlo.qExpectedHypervolumeImprovement

        elif acqfunc_name == 'qLogEHVI':
            acq_func_class = botorch.acquisition.multi_objective.logei.qLogExpectedHypervolumeImprovement

        else:
            raise ValueError(f"Acquisition function name '{acqfunc_name}' is not recognised.")

        self.seq_dist_punish = seq_dist_punish

        if seq_dist_punish is True:

            scaling_class = AcqFuncScaling()

            if "alpha" in kwargs:
                alpha = kwargs["alpha"]
            else:
                alpha = 1.0

            if "omega" in kwargs:
                omega = kwargs["omega"]
            else:
                omega = 1.0

            params_seq_opt = {
                "alpha": alpha,
                "omega": omega,
                "scaling": scaling_class
            }
        else:
            scaling_class = None
            params_seq_opt = None

        optimiser = PredefinedAcqOptimiser(
            bounds=bounds,
            n_objs=n_objs,
            n_evals_per_step=n_evals_per_step,
            optimiser_name=optimiser_name,
            seq_dist_punish=seq_dist_punish,
            params_seq_opt=params_seq_opt
        )

        super().__init__(
            function_class=acq_func_class,
            bounds=bounds,
            n_objs=n_objs,
            seq_dist_punish=seq_dist_punish,
            scaling_class=scaling_class,
            optimiser=optimiser,
            n_evals_per_step=n_evals_per_step,
            acqfunc_name=acqfunc_name,
            params=params
        )
