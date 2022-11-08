#!/usr/bin/env python

#NATIVE PYTHON IMPORTS
import math

#INSTALLED PACKAGE IMPORTS

#IMPORTS FROM THIS PACKAGE

class GaussianParameters:
    def __init__(self, mu: float, sigma: float):
        self.mu = mu
        self.sigma = sigma
    
    @staticmethod
    def pdf(x: float, mu: float = None, sigma: float = None) -> float:
        def compute_pdf(x:float) -> float:
            return math.exp(-x*x/2)/math.sqrt(2*math.pi)
        if(mu is None and sigma is None):
            return compute_pdf(x)
        else:
            return compute_pdf((x-mu)/sigma)/sigma
    
    @staticmethod
    def cdf(z: float, mu: float = None, sigma: float = None) -> float:
        def compute_cdf(z: float):
            if(z < -8.0): return 0.0
            if(z > 8.0): return 1.0
            sum = 0.0
            term = z
            i = 3
            while(sum + term != sum):
                sum = sum + term
                term = term * z * z / i
                i += 2
            return 0.5 + sum * GaussianParameters.pdf(z)
        if(mu is None and sigma is None):
            return compute_cdf(z)
        else:
            return compute_cdf((z-mu)/sigma)

    @staticmethod
    def cdf_in_range(lower_limit: float, upper_limit: float, mu: float, sigma: float) -> float:
        if(upper_limit<lower_limit):
            raise Exception("upper_limit < lower_limit in cdf_in_range()")
        if(upper_limit == lower_limit): return 0
        d_u = GaussianParameters.cdf(upper_limit,mu,sigma)
        if(d_u <= 0): return 0 #theoretically a negative cdf is impossible, but the Taylor series impl makes it possible
        d_l = GaussianParameters.cdf(lower_limit,mu,sigma)
        if(d_l < 0): return 0 #theoretically a negative cdf is impossible, but the Taylor series impl makes it possible
        diff = d_u - d_l
        if(diff<0):
            raise Exception("diff < 0 in cdf_in_range() even though d_u > 0")
        return diff
    
    @staticmethod
    def round(d: float, nRoundDigits: int) -> float:
        dFactor = math.pow(10, nRoundDigits)
        d = dFactor * d
        n = int(d+0.5)
        d = float(n)/dFactor
        return d
