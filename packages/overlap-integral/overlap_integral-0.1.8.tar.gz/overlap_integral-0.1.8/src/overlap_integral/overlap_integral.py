import numpy as np
from scipy.integrate import quad
from scipy.stats import norm, gaussian_kde
import plotly.graph_objects as go
from typing import Optional, Union, Callable

class OverlapIntegral:
    def __init__(self):
        pass

    def pdf_gaussian(self, x: float, mu: float, sigma: float) -> float:
        """
        Compute the value of a Gaussian (Normal) probability density function (PDF) at a given point.

        This function evaluates the standard Gaussian PDF formula:

            f(x) = (1 / (sigma * sqrt(2 * pi))) * exp(-0.5 * ((x - mu) / sigma)²)

        Parameters:
        ----------
        x : float
            The point at which to evaluate the Gaussian PDF.
        mu : float
            The mean (center) of the Gaussian distribution.
        sigma : float
            The standard deviation (spread) of the Gaussian distribution.

        Returns:
        -------
        float
            The probability density function value at `x`.

        Raises:
        ------
        ValueError
            If `sigma` is not positive, as a standard deviation must be greater than zero.
        """

        if sigma <= 0:
            raise ValueError("The standard deviation (sigma) must be greater than zero.")
        return norm.pdf(x, mu, sigma)

    def pdf_from_kde(self, data: np.ndarray, bw_method: Optional[Union[str, float, Callable]] = None, 
                    weights: Optional[Union[np.ndarray]] = None) -> gaussian_kde:
        """
        Generate a Kernel Density Estimation (KDE)-based probability density function (PDF) from the input data.

        This method fits a KDE to the provided data, allowing estimation of the probability density 
        at any point within the data's support. The resulting `gaussian_kde` object can be called as a 
        function to evaluate the estimated PDF at specific x-values.

        Parameters:
        ----------
        data : np.ndarray
            A 1D array of numerical data points used for estimating the probability density function.
            The data should represent the samples from the distribution you want to estimate.

        bw_method : Optional[Union[str, float, Callable]], default=None
            Specifies the method for bandwidth estimation. It can be:
            - A string ('scott', 'silverman') for predefined methods,
            - A float to specify the bandwidth directly, or
            - A callable to define a custom bandwidth function.

        weights : Optional[Union[np.ndarray]], default=None
            Weights for the data points. This must have the same shape as the `data` array. 
            If set to `None` (default), all data points are assumed to have equal weight.

        Returns:
        -------
        gaussian_kde
            A `gaussian_kde` object representing the estimated probability density function based on the 
            input data. This object can be called to evaluate the PDF at any point within the data range.
        """
        if data.ndim != 1:
            raise ValueError("The input data must be a 1D array.")
        kde = gaussian_kde(data, bw_method=bw_method, weights=weights)
        return kde

    def minimum_between_two_pdfs(self, x: float, pdf_1: callable, pdf_2: callable) -> float:
        """
        Compute the minimum value between two probability density functions (PDFs) at a given point.

        Parameters:
        ----------
        x : float
            The point at which both PDFs are evaluated.
        pdf_1 : callable
            The first probability density function.
        pdf_2 : callable
            The second probability density function.

        Returns:
        -------
        float
            The minimum value between `pdf_1(x)` and `pdf_2(x)`, representing their local overlap.

        Raises:
        ------
        ValueError
            If either `pdf_1` or `pdf_2` is not a callable function.
        """  

        if not (callable(pdf_1) and callable(pdf_2)):
            raise ValueError("Both pdf_1 and pdf_2 must be callable functions")
        return np.minimum(pdf_1(x), pdf_2(x)).item()
    
    def _integrand(self, x: float, pdf_1: callable, pdf_2: callable) -> float:
        """
        Compute the integrand function for the overlap integral.

        Parameters:
        ----------
        x : float
            The point at which the integrand is evaluated.
        pdf_1 : callable
            The first probability density function.
        pdf_2 : callable
            The second probability density function.

        Returns:
        -------
        float
            The minimum value between `pdf_1(x)` and `pdf_2(x)`, representing the overlap at `x`.
        """

        return self.minimum_between_two_pdfs(x, pdf_1, pdf_2)

    def overlap_integral(self, pdf_1: callable, pdf_2: callable, lower_limit: float, upper_limit: float) -> tuple[float, float]:
        """
        Compute the overlap integral between two probability density functions (PDFs) over a given range.

        Parameters:
        ----------
        pdf_1 : callable
            The first probability density function.
        pdf_2 : callable
            The second probability density function.
        lower_limit : float
            The lower bound of the integration interval.
        upper_limit : float
            The upper bound of the integration interval.

        Returns:
        -------
        tuple[float, float]
            A tuple containing:
            - The computed overlap integral (float).
            - The estimated numerical integration error (float).

        Raises:
        ------
        ValueError
            If either `pdf_1` or `pdf_2` is not a callable function.
        """ 

        if not (callable(pdf_1) and callable(pdf_2)):
            raise ValueError("Both pdf_1 and pdf_2 must be callable functions")
        integral, error = quad(self._integrand, lower_limit, upper_limit, args=(pdf_1, pdf_2))
        return integral, error

    def get_pdf(self, data: np.ndarray, pdf_type: str = 'kde', mu: float = None, sigma: float = None) -> callable:
        """
        Generate a probability density function (PDF) based on the specified method and input data.

        This method supports two types of PDF estimation:
        1. **Kernel Density Estimation (KDE)**: Uses a non-parametric approach to estimate the PDF based on the provided data.
        2. **Gaussian Distribution**: Assumes a Gaussian (normal) distribution, where the mean and standard deviation can be either provided or estimated from the data.

        Parameters:
            data (np.ndarray): A 1D array of numerical data points used to estimate the PDF.
            pdf_type (str, optional): The method used for PDF estimation. 
                - `'kde'` for Kernel Density Estimation (default).
                - `'gaussian'` for Gaussian distribution.
            mu (float, optional): The mean of the Gaussian distribution. This is required if `pdf_type` is `'gaussian'`.
            sigma (float, optional): The standard deviation of the Gaussian distribution. This is required if `pdf_type` is `'gaussian'`.

        Returns:
            callable: A function that takes a single argument `x` and returns the estimated PDF value at `x`.

        Raises:
            ValueError: If an unsupported PDF method is provided (i.e., anything other than `'kde'` or `'gaussian'`).
            ValueError: If `mu` or `sigma` are missing when `pdf_type` is `'gaussian'`.

        Notes:
            - If `pdf_type` is `'kde'`, the method uses the `pdf_from_kde` function to estimate the PDF.
            - If `pdf_type` is `'gaussian'`, the method uses the specified or computed mean (`mu`) and standard deviation (`sigma`) to define a Gaussian PDF.
        """

        if pdf_type == 'kde':
            return self.pdf_from_kde(data, None, None)
        elif pdf_type == 'gaussian':
            if mu is None or sigma is None:
                mu, sigma = np.mean(data), np.std(data)
            return lambda x: self.pdf_gaussian(x, mu, sigma)
        else:
            raise ValueError("Unsupported PDF method. Use 'kde' or 'gaussian'.")

    def plot_distributions(self, pdf_1: callable, pdf_2: callable, integral: float, error: float, x_range: tuple = (-10, 10)) -> go.Figure:
        """
        Plot two probability distributions and their overlap area.

        This method generates a plot comparing two probability distributions `pdf_1` and `pdf_2`, and highlights 
        their overlap area. The overlap area is shaded and the integral of the overlap, as well as the error value, 
        are displayed in the plot title.

        Parameters:
            pdf_1 (callable): A function representing the first probability density function (PDF).
            pdf_2 (callable): A function representing the second probability density function (PDF).
            integral (float): The integral of the overlap between the two distributions, representing the area 
                            of their intersection.
            error (float): The error value associated with the overlap integral, which quantifies the accuracy 
                        or uncertainty of the overlap calculation.
            x_range (tuple, optional): The range of x-values over which the distributions will be evaluated 
                                        and plotted. Defaults to (-10, 10).

        Returns:
            go.Figure: A Plotly `Figure` object containing the plot of the two distributions, their overlap, and 
                    the relevant annotations. The figure can be displayed using Plotly's rendering methods.

        Notes:
            - The plot will include:
                - A blue line for the first PDF (`pdf_1`),
                - An orange line for the second PDF (`pdf_2`),
                - A shaded area representing the overlap of the two distributions.
            - The title of the plot includes the computed overlap integral and error value, formatted to four decimal places.
            - An annotation is added to the plot with the formula for the overlap integral.

        Example:
            fig = plot_distributions(pdf_1, pdf_2, integral, error)
            fig.show()
        """

        x_range = np.linspace(x_range[0], x_range[1], 1000)
        y_pdf_1 = pdf_1(x_range)
        y_pdf_2 = pdf_2(x_range)
        y_overlap = np.minimum(y_pdf_1, y_pdf_2)

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=x_range, y=y_pdf_1, mode='lines', name='f(x)', line=dict(color='blue')))
        fig.add_trace(go.Scatter(x=x_range, y=y_pdf_2, mode='lines', name='g(x)', line=dict(color='orange')))
        fig.add_trace(go.Scatter(x=x_range, y=y_overlap, fill='tozeroy', mode='none', name=r"$\theta$", fillcolor='rgba(0,100,80,0.2)'))

        fig.update_layout(
            title=f'Overlap Integral: {integral:.4f}; \n Error: {error:.4f}',
            xaxis_title='x',
            yaxis_title='Probability Density',
            legend_title='Distributions',
        )

        fig.add_annotation(
            text=r"$\theta = \int_{a}^{b} \min(f(x), g(x)) \, dx$",
            xref="paper",
            yref="paper",
            x=0.8,
            y=0.95,
            showarrow=False,
            font=dict(size=16)
        )

        return fig