import numpy as np
from dpmhalo import myutils
import os

rootdir = os.path.dirname(__file__)
DataDir = rootdir + '/Data/'

#This is the replacement for the Behroozi2013 code below and includes returning error ranges.  
def Behroozi2019_UNIVERSEMACHINE_return_lM200c(lMStar,err_lMStar,redshift,galaxy_type_tag=''):

    redshift_tag = round(redshift*10)
    
    file_name = '%s/Behroozi_UNIVERSEMACHINE/SMHM_med_cen%s.z0.%d.txt'%(DataDir,galaxy_type_tag,redshift_tag)
    
    lMvir, lMS, lMS_errplus, lMS_errneg = np.loadtxt(file_name,usecols=(0,1,3,4),unpack=True)

    lM200c = myutils.lMvir_to_lM200c(lMvir,redshift)
    
    # Sometimes the error return is negative and unrealistic, so we zero it.  
    lMS_errplus = np.where(lMS_errplus>0,lMS_errplus,0)
    lMS_errneg = np.where(lMS_errneg>0,lMS_errneg,0)

    lMS_max = lMS+lMS_errplus
    lMS_min = lMS-lMS_errneg

    lM200c_med = np.interp(lMStar, lMS, lM200c)

    # This adds errors linearly, not in quadarture, because we are making conservative (wide) errors.  
    lM200c_max = np.interp(lMStar+err_lMStar, lMS_min, lM200c)
    lM200c_min = np.interp(lMStar-err_lMStar, lMS_max, lM200c)

    #print("lM200c_med, lM200c_max-lM200c_med, lM200c_med-lM200c_min= ", lM200c_med, lM200c_max-lM200c_med, lM200c_med-lM200c_min)

    return(lM200c_med, lM200c_max-lM200c_med, lM200c_med-lM200c_min)
    
#This is a very rudimentary code and has been replaced.  
def Behroozi2013_return_mhalo(lMStar_in,z):

    logM_step = 0.05
    logM_lo = 8.0
    logM_hi = 15.0
    logM = np.linspace(logM_lo,logM_hi,int((logM_hi-logM_lo)/logM_step)+1)
    
    mh = 10**logM
    a = 1./(1+z)

    eps0 = -1.785
    epsa = -0.074
    epsz = -0.048
    epsa2 = -0.179
    ml0 = 11.539
    mla = -1.751 
    mlz = -0.329
    alpha0 = -1.474
    alphaa = 1.339
    delta0 = 3.529
    deltaa = 4.152
    deltaz = 1.122
    gamma0 = 0.395
    gammaa = 0.766
    gammaz = 0.435
    nu = np.exp(-4*a**2)
    ml = 10**(ml0+(mla*(a-1)+mlz*z)*nu)
    eps = 10**(eps0 + (epsa*(a-1)+epsz*z)*nu + epsa2*(a-1))
    alpha = alpha0 + alphaa*(a-1)*nu
    delta = delta0 + (deltaa*(a-1)+deltaz*z)*nu
    gammag = gamma0 + (gammaa*(a-1)+gammaz*z)*nu

    x = np.log10(mh/ml)
    f =  -np.log10(10**(alpha*x)+1) + delta * np.log10(1+np.exp(x))**gammag / (1+np.exp(10**-x))
    f0 = -np.log10(10**(alpha*0)+1) + delta * np.log10(1+np.exp(0))**gammag / (1+np.exp(10**-0))
    mstar = 10**(np.log10(eps*ml) + f - f0)


    lmhalo_out = np.zeros(len(lMStar_in))
    for j in range(len(lMStar_in)):
        lmhalo_out[j] = np.interp(lMStar_in[j],np.log10(mstar),logM)
        #for i in range(len(logM)):
            #if(np.log10(mstar[i])>=lMStar_in[j]):
            #    lmhalo_out[j] = logM[i]
            #    lmhalo_out[j] = myutils.lMvir_to_lM200(lmhalo_out[j])
            #    #print("logM= ", logM[i],np.log10(mstar[i]))
            #    break

    return(lmhalo_out)
        
