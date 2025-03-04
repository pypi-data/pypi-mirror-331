import math
import numpy as np

# This function returns the analytical solution to sqrt(2/Pi)/sigma exp(-(x-mu)^2/(2*sigma^2))/10^x, i.e. a Gaussian distribution times volume, parametrized by 1/10^x where x is log density and mu and sigma are in log density.  
#def volume_weight_old(mu, sigma, value):
#
#    return(np.exp(sigma**2*(np.log(10))**2/2)*math.erf((value+sigma**2*np.log(10)-mu)/(np.sqrt(2)*sigma))/10**mu)

# This function returns the analytical solution to a log normal distribution: 1/(x*sigma*sqrt(2*pi)) exp(-(ln(x)-mu)**2/(2*sigma**2))
def volume_weight(mu, sigma, value):
    #Note mu and sigma is in log_10(ne).  The lognormal mu and sigma are different.  
    sigma_lognormal = sigma*np.log(10.)
    mu_lognormal = np.log(10**mu)-sigma_lognormal**2/2.
    #print("sigma, mu, sigma_lognormal, mu_lognormal, value= ", sigma, mu, sigma_lognormal, mu_lognormal,value)
    return(1/2.*math.erf((np.log(10**value)-mu_lognormal)/(sigma_lognormal*np.sqrt(2))))

def normalized_volume(mu, sigma, nsigma, width):

    norm = (volume_weight(mu,sigma,mu+nsigma*sigma+width/2.)-volume_weight(mu,sigma,mu-nsigma*sigma-width/2.))
    return(norm)

def fractional_volume(mu, sigma, value, width, nsigma):

    frac_vol = (volume_weight(mu,sigma,value+width/2.)-volume_weight(mu,sigma,value-width/2.))/normalized_volume(mu, sigma, nsigma, width)
    return(frac_vol)



