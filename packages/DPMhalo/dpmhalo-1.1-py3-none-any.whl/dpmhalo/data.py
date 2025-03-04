import numpy as np
from astropy import units as u
from astropy import constants as const
from dpmhalo import myconstants as myc
from dpmhalo import smhm 
from dpmhalo import myutils
import pandas as pd
import os

rootdir = os.path.dirname(__file__)
DataDir = rootdir + '/Data/'

def Akino_2022_fgas_fit_z0(lM200c,redshift):

    E_z = myutils.E(redshift) # I followed equations but I'm not sure if this evolves correctly, but we are only showing at z=0.  

    alpha = 1.95 #+0.08/-0.08
    beta = 1.29 #+0.16/-0.10

    alpha_hi = 2.03
    beta_hi = 1.45

    alpha_lo = 1.87
    beta_lo = 1.19
    
    lM500c = myutils.lM200c_to_lM500c(lM200c)
    M500c = 10**lM500c*E_z # Note this is how Akino defines masses in their fits.  

    Mgas_500 = np.exp(alpha + beta * np.log(M500c/1e+14))*1e+12/E_z
    fgas_500 = Mgas_500/M500c

    Mgas_500_hi1 = np.exp(alpha_hi + beta_hi * np.log(M500c/1e+14))*1e+12/E_z
    Mgas_500_hi2 = np.exp(alpha_hi + beta_lo * np.log(M500c/1e+14))*1e+12/E_z
    
    Mgas_500_lo1 = np.exp(alpha_lo + beta_lo * np.log(M500c/1e+14))*1e+12/E_z
    Mgas_500_lo2 = np.exp(alpha_lo + beta_hi * np.log(M500c/1e+14))*1e+12/E_z

    Mgas_500_hi = np.max([Mgas_500_hi1,Mgas_500_hi2,Mgas_500_lo1,Mgas_500_lo2])
    Mgas_500_lo = np.min([Mgas_500_lo1,Mgas_500_lo2,Mgas_500_hi1,Mgas_500_hi2])

    fgas_500_hi = Mgas_500_hi/M500c
    fgas_500_lo = Mgas_500_lo/M500c
    
    return(M500c, fgas_500,fgas_500_lo,fgas_500_hi)



def Arnaud_2010_Pe_fit_z0(lM200c,frac_lR200c):

    lM500c = myutils.lM200c_to_lM500c(lM200c)
    
    ###frac_R500c = myutils.R200_to_R500(10**frac_lR200c)
    frac_R500c = myutils.fR200c_to_fR500c(10**frac_lR200c, 10**lM200c)

    x = frac_R500c
    
    h_70 = 1.0
    Mass_exponent = (2/3.+(0.12+0.10)-(0.12+0.10)*(x/0.5)**3/(1+(x/0.5)**3))
    #print("Mass_exponent, lM200c, frac_lR200c, x= ", Mass_exponent, lM200c, frac_lR200c, x)

    P_0 = 8.403*h_70**(-3/2.)
    c_500 = 1.177
    gamma = 0.3081
    alpha = 1.0510
    beta = 5.4905
 
    P_e = 1.65e-03*(10**lM500c/(3e+14/h_70))**Mass_exponent * P_0*h_70**2/((c_500*x)**gamma*(1+(c_500*x)**alpha)**((beta-gamma)/alpha))*myc.K_per_keV

    n_over_ne = 1/(myc.ne_to_nH*myc.XH*myc.mu)
    P = P_e*n_over_ne
    
    return(P_e)

def Ghirardini_2019_ne_fit(frac_lR200c):

    lM200c_Girardini2019 = 14.9 
    frac_R500c = myutils.fR200c_to_fR500c(10**frac_lR200c, 10**lM200c_Girardini2019)
    
    x = frac_R500c

    gamma = 3.
    n_0 = np.exp(-4.4) #10**-4.4
    r_core = np.exp(-3.0) #10**-3.0
    r_scale = np.exp(-0.29) #10**-0.29
    alpha = 0.89
    beta = 0.43
    epsilon = 2.86
    
    n_e_squared = n_0**2 * (x/r_core)**-alpha/(1.+x**2/r_core**2)**(3.*beta-alpha/2.)/(1.+x**gamma/r_scale**gamma)**(epsilon/gamma)
    n_e = np.sqrt(n_e_squared)
    return(n_e)

def Ghirardini_2019_Pe_fit(lM200c,frac_lR200c,redshift,norm_P500=False):

    lM500c = myutils.lM200c_to_lM500c(lM200c)
    ###frac_R500c = myutils.R200_to_R500(10**frac_lR200c)
    frac_R500c = myutils.fR200c_to_fR500c(10**frac_lR200c, 10**lM200c)

    h_70 = 1.0
    E_z = myutils.E(redshift) # XXXXX This is redshift = 0.  

    P_500 = myc.K_per_keV * 3.426e-03 * (10**lM500c/(h_70**-1*10**15.))**(2/3.)*E_z**(8/3.)*(myc.f_b/0.16)*(myc.mu/0.6)*(myc.mu_e/1.14)
    
    x = frac_R500c

    P_0 = 5.68
    c_500 = 1.49
    gamma = 0.43
    alpha = 1.33
    beta = 4.40

    Pe_over_P500 = P_0/(c_500*x)**gamma/(1+(c_500*x)**alpha)**((beta-gamma)/alpha)
    if(norm_P500):
        return(Pe_over_P500)
    else:
        return(Pe_over_P500*P_500)


def Sun_2011_P(cluster=False, return_P500=False):

    if(cluster):
        lRfrac, lP500_med, lP500_lo, lP500_hi = np.loadtxt("%s/Sun2011_normalizedpressure.groups.dat"%DataDir,usecols=(0,1,2,3),unpack=True)
        M500c_Sun2011 = 5e+14 #XXXX GUESS-FIX
    else:
        lRfrac, lP500_med, lP500_lo, lP500_hi = np.loadtxt("%s/Sun2011_normalizedpressure.clusters.dat"%DataDir,usecols=(0,1,2,3),unpack=True)
        M500c_Sun2011 = 7e+13
        
    #lRfrac_200 = np.log10(myutils.R500_to_R200(10**lRfrac))
    lRfrac_200 = np.log10(myutils.fR500c_to_fR200c(10**lRfrac,M500c_Sun2011))

    redshift_Sun2011 = 0.033 # Not used for plotting since normalized to E(z)^-8/3
    
    lM200c_Sun2011 = myutils.lM500c_to_lM200c(np.log10(M500c_Sun2011))
    
    P500_Sun2011 = myutils.convert_Pe_to_Pe500(1.0,lM200c_Sun2011,0.0,return_only_P500=True)
    
    P_med = 10**lP500_med*P500_Sun2011
    P_lo = 10**lP500_lo*P500_Sun2011
    P_hi = 10**lP500_hi*P500_Sun2011

    if(return_P500):
        return(lRfrac_200,10**lP500_med,10**lP500_lo,10**lP500_hi)
    else:
        return(lRfrac_200,P_med,P_lo,P_hi)

def Sun_2009_ne_Groups():

    M500c_Sun2009 = 5e+13/0.7

    redshift_Sun2009 = 0.033 # Not used for plotting, since normalized to E(z)^-2
    lRfrac, lne_med, lne_lo, lne_hi = np.loadtxt("%s/Sun2009_density.groups.dat"%DataDir,usecols=(0,1,2,3),unpack=True)

    lRfrac_200 = np.log10(myutils.fR500c_to_fR200c(10**lRfrac,M500c_Sun2009))

    lM200c_Sun2009 = myutils.lM500c_to_lM200c(np.log10(M500c_Sun2009))

    return(lRfrac_200,10**lne_med,10**lne_lo,10**lne_hi)
    
def Lovisari_2015_ne_Groups():
    M500c_Lovisari_2015 = 10**13.55 # Need to check.  

    R500_scale_data, ne_med, ne_lo, ne_hi = np.loadtxt("%s/Lovisari2015.ne_groups.dat"%DataDir,usecols=(0,1,2,3),unpack=True)

    R200_scale_data = myutils.fR500c_to_fR200c(R500_scale_data,M500c_Lovisari_2015)
    
    return(R200_scale_data,ne_med,ne_lo,ne_hi)

def Lovisari_2015_M500_LX():
    h_70 = 1.0
    lM500_L15 = np.linspace(13.3,15.0,10)
    M500_L15 = 10**lM500_L15
    a_L15 = 1.39
    b_L15 = -0.12
    C1_L15 = 1e+43*h_70**-2.
    C2_L15 = 5e+13*h_70**-1.
    lLX_L15 = a_L15*np.log10(M500_L15/C2_L15)+b_L15+np.log10(C1_L15)

    return(lM500_L15, lLX_L15)

def Akino_2022_M500_LX(lM200c,redshift):

    
    E_z = myutils.E(redshift) # Evolution appears to agree with DPM redshift evolution.  

    alpha = 0.29 #+0.13/-0.13
    beta = 1.38 #+0.27/-0.18

    alpha_hi = 0.42
    beta_hi = 1.65

    alpha_lo = 0.16
    beta_lo = 1.20
    
    lM500c = myutils.lM200c_to_lM500c(lM200c)
    M500c = 10**lM500c*E_z # Note this is how Akino defines masses in their fits.  
    
    LX_500 = np.exp(alpha + beta * np.log(M500c/1e+14))*1e+43*E_z

    LX_500_hi1 = np.exp(alpha_hi + beta_hi * np.log(M500c/1e+14))*1e+43*E_z
    LX_500_hi2 = np.exp(alpha_hi + beta_lo * np.log(M500c/1e+14))*1e+43*E_z
    
    LX_500_lo1 = np.exp(alpha_lo + beta_lo * np.log(M500c/1e+14))*1e+43*E_z
    LX_500_lo2 = np.exp(alpha_lo + beta_hi * np.log(M500c/1e+14))*1e+43*E_z

    LX_500_hi = np.max([LX_500_hi1,LX_500_hi2,LX_500_lo1,LX_500_lo2])
    LX_500_lo = np.min([LX_500_lo1,LX_500_lo2,LX_500_hi1,LX_500_hi2])

    return(M500c, LX_500,LX_500_lo,LX_500_hi)



def McDonald_2017_ne_MH145_z0(lM200c,lRfrac,R200c_kpc,redshift):

    ###R500c_kpc = myutils.R200_to_R500(R200c_kpc)
    R500c_kpc = myutils.fR200c_to_fR500c(R200c_kpc, lM200c)

    M500c = 10**(myutils.lM200c_to_lM500c(lM200c))
    
    R_kpc = 10**lRfrac * R200c_kpc
    
    R_scale_500 = 10**lRfrac*(R500c_kpc/R200c_kpc) # scaled to R500, so multiply.
    R_scale_500_data, lrho_crit_500_data, err_500 = np.loadtxt("%s/McDonald_2017.rhocrit_r500.dat"%DataDir ,usecols=(0,1,2),unpack=True)
    lrho_crit_500 = np.interp(R_scale_500,R_scale_500_data,lrho_crit_500_data)

    rhocrit_cgs = 1.88e-29*myc.hubbleparam**2*(1+redshift)**3
    rhocrit = rhocrit_cgs/const.m_p.to('g').value

    nH_cgs = 10**lrho_crit_500*rhocrit*myc.XH

    ne_cgs = nH_cgs*myc.ne_to_nH

    R_kpc_return = np.linspace(10.,R200c_kpc,num=50)
    ne_cgs_return = np.interp(R_kpc_return,R_kpc,ne_cgs)

    return(R_kpc_return,ne_cgs_return)

def WuMcQuinn_2023_FRB(lMvir):

    lmvirlo,lmvirhi,frvirlo,frvirhi,DM,DMerr = np.loadtxt("%s/WuMcQuinn_2023.FRB.dat"%DataDir,usecols=(0,1,2,3,4,5),unpack=True)
    lmvirmed = (lmvirlo+lmvirhi)/2.
    frvirmed = (frvirlo+frvirhi)/2.
    
    indexes = np.where((lMvir>lmvirlo) & (lMvir<lmvirhi))
    lmvirmed = lmvirmed[indexes]
    frvirmed = frvirmed[indexes]
    DM = DM[indexes]
    DMerr = DMerr[indexes]

    return(lmvirmed,frvirmed,DM,DMerr)

def Pratt_2021_tSZ():

    M500c_Pratt = 10**13.75
    R500_scale_data, ySZ_data, ySZ_err = np.loadtxt("%s/Pratt_2021.groups_stack.dat"%DataDir ,usecols=(0,1,2),unpack=True)
    ###R200_scale_data = myutils.R500_to_R200(R500_scale_data)
    R200_scale_data = myutils.fR500c_to_fR200c(R500_scale_data,M500c_Pratt)

    return(R200_scale_data,ySZ_data,ySZ_err)

def Bregman_2022_tSZ():

    R_kpc, ySZ_med, ySZ_errneg, ySZ_errpos = np.loadtxt("%s/NoN891_wbs_radial_shiftedBetaP2020_bootstrap_Jan2021.txt"%DataDir, usecols=(0,1,2,3),unpack=True)
    
    ySZ_med *= 1.90 # 10/3/24- erratum
    ySZ_errneg *= 1.90 # 10/3/24- erratum 
    ySZ_errpos *= 1.90 # 10/3/24- erratum 

    return(R_kpc,ySZ_med,ySZ_errpos,ySZ_errneg)

def Schaan_2021_tSZ_CMASS(muK=True): #If muK is false, then it's just arcmin2.  
    R_arcmin, y_CAP_data_ster, y_CAP_err_ster = np.loadtxt("%s/data_schaan21/diskring_tsz_uniformweight_measured.txt"%DataDir,usecols=(0,1,2),unpack=True)

    y_CAP_data_arcmin2 = y_CAP_data_ster*60**2*(180/np.pi)**2
    y_CAP_err_arcmin2 = y_CAP_err_ster*60**2*(180/np.pi)**2

    # Use 2.59e+06 muK for temperature at 150 Ghz.  
    deltaT_CAP_data_muKarcmin2 = -y_CAP_data_ster*60**2*(180/np.pi)**2*2.59e+06 #Fig. 8 of Schaan2021
    deltaT_CAP_err_muKarcmin2 = y_CAP_err_ster*60**2*(180/np.pi)**2*2.59e+06 #Fig. 8 of Schaan2021

    if(muK):
        return(R_arcmin,deltaT_CAP_data_muKarcmin2,deltaT_CAP_err_muKarcmin2)
    else:
        return(R_arcmin,y_CAP_data_arcmin2,y_CAP_err_arcmin2)

def Schaan_2021_kSZ_CMASS(muK=True):
    R_arcmin_f090, TkSZ_data_f090, TkSZ_err_f090 = np.loadtxt("%s/data_schaan21/f090/diskring_ksz_varweight_measured.txt"%DataDir,usecols=(0,1,2),unpack=True)
    R_arcmin_f150, TkSZ_data_f150, TkSZ_err_f150 = np.loadtxt("%s/data_schaan21/f150/diskring_ksz_varweight_measured.txt"%DataDir,usecols=(0,1,2),unpack=True)

    tau_CAP_data_f090_arcmin2 = TkSZ_data_f090*60**2*(180/np.pi)**2/(2.726e+06*(313/2.998e+05))
    tau_CAP_err_f090_arcmin2 = TkSZ_err_f090*60**2*(180/np.pi)**2/(2.726e+06*(313/2.998e+05))

    tau_CAP_data_f150_arcmin2 = TkSZ_data_f150*60**2*(180/np.pi)**2/(2.726e+06*(313/2.998e+05))
    tau_CAP_err_f150_arcmin2 = TkSZ_err_f150*60**2*(180/np.pi)**2/(2.726e+06*(313/2.998e+05))

    deltaT_CAP_data_f090_muKarcmin2 = TkSZ_data_f090*60**2*(180/np.pi)**2 #Fig. 7 of Schaan2021
    deltaT_CAP_err_f090_muKarcmin2 = TkSZ_err_f090*60**2*(180/np.pi)**2 #Fig. 7 of Schaan2021
    
    deltaT_CAP_data_f150_muKarcmin2 = TkSZ_data_f150*60**2*(180/np.pi)**2 #Fig. 7 of Schaan2021
    deltaT_CAP_err_f150_muKarcmin2 = TkSZ_err_f150*60**2*(180/np.pi)**2 #Fig. 7 of Schaan2021
    
    if(muK):
        return(R_arcmin_f090,deltaT_CAP_data_f090_muKarcmin2,deltaT_CAP_err_f090_muKarcmin2,R_arcmin_f150,deltaT_CAP_data_f150_muKarcmin2,deltaT_CAP_err_f150_muKarcmin2)
    else:
        return(R_arcmin_f090,tau_CAP_data_f090_arcmin2,tau_CAP_err_f090_arcmin2,R_arcmin_f150,tau_CAP_data_f150_arcmin2,tau_CAP_err_f150_arcmin2)


def Lovisari_2019_Z(combined=False):

    M500c_Lovisari_2019 = 10**13.55
    R500_lo_data, R500_hi_data, Z_relax_data, sig_relax_data, Z_dist_data, sig_dist_data = np.loadtxt("%s/Lovisari_2019.Groups_Z.dat"%DataDir, usecols=(0,1,2,3,4,5),unpack=True) # Metallicities are in Asplund abundances.  

    
    R200_scale_data = myutils.fR500c_to_fR200c((R500_hi_data+R500_lo_data)/2.,M500c_Lovisari_2019)

    if(combined is True):
        Z_combined_data = (Z_relax_data+Z_dist_data)/2.
        sig_combined_data = (sig_relax_data+sig_dist_data)/2.
        return(R200_scale_data,Z_combined_data,sig_combined_data)
    else:
        #Return relaxed groups only
        return(R200_scale_data,Z_relax_data,sig_relax_data)

def Ghizzardi_2021_Z():
    M500c_Ghizzardi_2021 = 10**14.75 #XXX CHECK
    R500c_lo_data, R500c_hi_data, ZFe_med_data, ZFe_err_data = np.loadtxt("%s/Ghizzardi_2021.Cluster_Z.dat"%DataDir, usecols=(0,1,5,6),unpack=True)
    R500c_scale_data = (R500c_lo_data+R500c_hi_data)/2.
    ###R200_scale_data = myutils.R500_to_R200(R500_scale_data)
    R200_scale_data = myutils.fR500c_to_fR200c(R500c_scale_data,M500c_Ghizzardi_2021)

    ZFe_med_data *= 10**7.51/10**7.50 # Normalize to Asplund (very minor)  
    ZFe_err_data *= 10**7.51/10**7.50 # Normalize to Asplund (very minor) 

    return(R200_scale_data,ZFe_med_data,ZFe_err_data)

def XGAP_profiles(lM200c, return_ne=True,return_P=False,return_ZFe=False):

    lM500c_read, ngal, frac_lR500c_lo, frac_lR500c_hi, lPmed, lPlo, lPhi, lnemed, lnelo, lnehi, lTmed, lTlo, lThi = np.loadtxt("%s/XGAP_median_profiles.dat"%DataDir, usecols=(0,1,2,3,4,5,6,7,8,9,10,11,12), unpack=True)
    frac_lR500c = (frac_lR500c_lo+frac_lR500c_hi)/2.

    lPmed = lPmed + np.log10(myc.K_per_keV)
    lPlo = lPlo + np.log10(myc.K_per_keV)
    lPhi = lPhi + np.log10(myc.K_per_keV)

    lM500c = myutils.lM200c_to_lM500c(lM200c)
    if((lM500c>=13.2) & (lM500c<13.53333)):
        lM500clo = 13.2
        lM500chi = 13.53333
    if((lM500c>=13.5333) & (lM500c<13.86667)):
        lM500clo = 13.53333
        lM500chi = 13.86667
    if((lM500c>=13.86667) & (lM500c<=14.2)):
        lM500clo = 13.86667
        lM500chi = 14.2

    indexes_return = np.where((lM500c_read>=lM500clo) & (lM500c_read<lM500chi))

    ###frac_R200c = myutils.R500_to_R200(10**frac_lR500c)
    frac_R200c = myutils.fR500c_to_fR200c(10**frac_lR500c,10**lM500c)

    if(return_ZFe):
        lM500c_read, ngal, frac_R500c_lo, frac_R500c_hi, lZmed, lZlo, lZhi = np.loadtxt("%s/XGAP_median_Fe_profiles.dat"%DataDir, usecols=(0,1,2,3,4,5,6), unpack=True)
        frac_R500c = (frac_R500c_lo+frac_R500c_hi)/2.
        indexes_return = np.where((lM500c_read>=lM500clo) & (lM500c_read<lM500chi))

        ###frac_R200c = myutils.R500_to_R200(frac_R500c)
        frac_R200c = myutils.fR500c_to_fR200c(frac_R500c,10**lM500c)

        return(frac_R200c[indexes_return],lZmed[indexes_return],lZlo[indexes_return],lZhi[indexes_return])
    if(return_P):
        return(frac_R200c[indexes_return],lPmed[indexes_return],lPlo[indexes_return],lPhi[indexes_return])
    if(return_ne):
        return(frac_R200c[indexes_return],lnemed[indexes_return],lnelo[indexes_return],lnehi[indexes_return])

def Voit_logU_to_logP(logU,redshift):

    #redshift_vec = [ 0.0 , 0.4 ] # OLD FROM VOIT19 
    #log_nph_vec = [ -5.97 , -5.42 ] # HM05  # OLD FROM VOIT19
    redshift_vec = [ 0.0 , 0.2114, 0.5396, 1.053 ]
    #log_nph_vec = [ -5.81, -5.53, -5.20, -4.87 ] # HM05 recalculated 
    log_nph_vec = [ -6.48, -6.10, -5.65, -5.18 ] # HM12 recalculated

    log_nph  = np.interp(redshift, redshift_vec, log_nph_vec)

    nH = 10**log_nph/10.0**logU

    #logU_vec = np.flip([-1.42, -1.67, -1.92, -2.17, -2.42, -2.67, -2.92, -3.17, -3.42, -3.67, -3.92, -4.17, -4.42, -4.67, -4.92, -5.17, -5.42 ]) # OLD FROM VOIT19
    #logT_vec = np.flip([ 4.342, 4.291, 4.291, 4.192, 4.146, 4.105, 4.071, 4.044, 4.022, 4.000, 3.977, 3.954, 3.932, 3.911, 3.888, 3.861, 3.827]) # OLD FROM VOIT19
    #log_T = np.interp(logU, logU_vec, logT_vec) # OLD FROM VOIT19

    lognH_vec = [-5.0,-4.5,-4.0,-3.5,-3.0,-2.5,-2.0,-1.46,-0.88] # Assume HM12 Z=0.3Zsolar, z=0.2
    logT_vec = [4.495,4.395,4.315,4.235,4.145,4.075,4.005,3.955,3.875] # Assume HM12 Z=0.3Zsolar, z=0.2 
    log_T = np.interp(log_nph-logU, lognH_vec, logT_vec)

    T = 10**log_T
    ne = nH*myc.ne_to_nH
    
    Ptherm = T*ne

    return(np.log10(Ptherm))
    
def Voit_lognH_to_logP(lognH,redshift):

    lognH_vec = [-5.0,-4.5,-4.0,-3.5,-3.0,-2.5,-2.0,-1.46,-0.88] # Assume HM12 Z=0.3Zsolar, z=0.2
    logT_vec =  [4.495,4.395,4.315,4.235,4.145,4.075,4.005,3.955,3.875] # Assume HM12 Z=0.3Zsolar, z=0.2 
    log_T = np.interp(lognH, lognH_vec, logT_vec)

    T = 10**log_T
    ne = 10**lognH*myc.ne_to_nH

    Ptherm = T*ne
    return(np.log10(Ptherm))

def Voit_LogU(survey_return):

    survey_ID,logU_max,logU,logU_hi,logU_lo,Rproj,lMStar_pub,redshift,fracRvir = np.loadtxt("%s/LogU_table.csv"%DataDir, usecols=(0,1,2,3,4,5,6,7,8), delimiter=',',unpack=True, encoding='utf-8-sig')

    lMStar_err = 0.2

    lM200 = lMStar_pub*0.
    lM200_errpos = lMStar_pub*0.
    lM200_errneg = lMStar_pub*0.
    survey_name_array = ["COS-LRG","COS-GTO-10.2-11.3","COS-GTO-9.4-9.8","COS-Halos-9.5-10.3","COS-Halos-10.3-11.4"]
    survey_ID_array = [1,2,3,4,5]
    #reorganization_survey_name_array = ["COS-Halos SF", "COS-Halos Q", "COS-LRG", "COS-GTO SF", "COS-GTO Q"]
    #reorganization_survey_ID_array = [4,5,1,2,3]
                    
    Rproj_return = []
    logU_return = []
    logU_hi_return = []
    logU_lo_return = []
    lM200_return = []
    lM200_errpos_return = []
    lM200_errneg_return = []
    redshift_return = []

    for i in range(len(lMStar_pub)):
        for j in range(len(survey_ID_array)):
            if(survey_ID[i] == survey_ID_array[j]):
                survey_name = survey_name_array[j]
                
        if(survey_return in survey_name):
            if(logU_max[i]==1):
                lM200[i], lM200_errpos[i], lM200_errneg[i] = smhm.Behroozi2019_UNIVERSEMACHINE_return_lM200c(lMStar_pub[i],lMStar_err,redshift[i])
                Rproj_return.append(Rproj[i])
                logU_return.append(logU[i])
                logU_hi_return.append(logU_hi[i])
                logU_lo_return.append(logU_lo[i])
                lM200_return.append(lM200[i])
                lM200_errpos_return.append(lM200_errpos[i])
                lM200_errneg_return.append(lM200_errneg[i])
                redshift_return.append(redshift[i])
            
    return(np.asarray(Rproj_return),np.asarray(logU_return),np.asarray(logU_hi_return),np.asarray(logU_lo_return),np.asarray(lM200_return),np.asarray(lM200_errpos_return),np.asarray(lM200_errneg_return),np.asarray(redshift_return))
    #return(Rproj,logU,logU_hi,logU_lo,lM200,lM200_errpos,lM200_errneg,redshift)

def Voit_LogP(survey_return):

    old_survey_ID,logU_primary,survey_ID,logU,logU_hi,logU_lo,Rproj,lMStar_V19,lMStar_T22,lMStar_Wakker,redshift,lMStar_P17,Rproj_P17,lognH_lo,lognH_med,lognH_hi,passive = np.loadtxt("%s/LogU_table.nullfilled.csv"%DataDir, usecols=(0,1,2,3,4,5,6,7,8,9,11,19,21,22,23,24,26), delimiter=',',unpack=True, encoding='utf-8-sig')

    lMStar_err = 0.2

    lM200 = lMStar_T22*0.
    lM200_errpos = lMStar_T22*0.
    lM200_errneg = lMStar_T22*0.
    lMStar_favorite = lMStar_V19
    #orig_survey_name_array = ["COS-LRG","COS-GTO-10.2-11.3","COS-GTO-9.4-9.8","COS-Halos-9.5-10.3","COS-Halos-10.3-11.4"]
    #orig_survey_ID_array = [1,2,3,4,5]
    survey_name_array = ["COS-Halos-SF", "COS-Halos-Q", "COS-LRG", "COS-GTO-SF", "COS-GTO-Q"]
    survey_ID_array = [4,5,1,2,3]

    Rproj_return = []
    logU_return = []
    logU_hi_return = []
    logU_lo_return = []
    lM200_return = []
    lM200_errpos_return = []
    lM200_errneg_return = []
    redshift_return = []
    logP_return = []
    logP_hi_return = []
    logP_lo_return = []
    passive_return = []
    
    for i in range(len(lMStar_T22)):
        if(lMStar_T22[i]>7):
            lMStar_favorite[i] = lMStar_T22[i] # We will use lMStar_T22 where available.
        for j in range(len(survey_ID_array)):
            if(survey_ID[i] == survey_ID_array[j]):
                survey_name = survey_name_array[j]
                
        if(survey_return in survey_name):
            if(logU_primary[i]==1):
                if(passive[i] == 1):
                    lM200[i], lM200_errpos[i], lM200_errneg[i] = smhm.Behroozi2019_UNIVERSEMACHINE_return_lM200c(lMStar_favorite[i],lMStar_err,redshift[i],galaxy_type_tag='_q')
                else:
                    lM200[i], lM200_errpos[i], lM200_errneg[i] = smhm.Behroozi2019_UNIVERSEMACHINE_return_lM200c(lMStar_favorite[i],lMStar_err,redshift[i],galaxy_type_tag='_sf')

                Rproj_return.append(Rproj[i])
                logU_return.append(logU[i])
                logU_hi_return.append(logU_hi[i])
                logU_lo_return.append(logU_lo[i])
                lM200_return.append(lM200[i])
                
                logP = Voit_logU_to_logP(logU[i],redshift[i])
                logP_hi = Voit_logU_to_logP(logU_hi[i],redshift[i])
                logP_lo = Voit_logU_to_logP(logU_lo[i],redshift[i])
                #print("i, lognH_med= ",i, lognH_med[i])
                #if((lognH_med[i] < 0) & (lognH_med[i] > -10)): # New nH values from P17 exist, but we still use Voit2019 pressures, so we take this out.  
                if((logP > 50) | (logP < -50)): # There can be -99 values in pressure (only one I believe), so we change to P17.  
                    logP_P17 = Voit_lognH_to_logP(lognH_med[i],redshift[i])
                    logP_hi_P17 = Voit_lognH_to_logP(lognH_hi[i],redshift[i])
                    logP_lo_P17 = Voit_lognH_to_logP(lognH_lo[i],redshift[i])
                    #print("Replacing old logP= % 4.2f +%4.2f -%4.2f  with new logP= % 4.2f +%4.2f -%4.2f"%(logP,logP_hi-logP,logP-logP_lo,logP_P17,logP_hi_P17-logP_P17,logP_P17-logP_lo_P17))
                    logP = logP_P17
                    logP_hi = logP_hi_P17
                    logP_lo = logP_lo_P17
                logP_return.append(logP)
                logP_hi_return.append(logP_hi)
                logP_lo_return.append(logP_lo)
                
                lM200_errpos_return.append(lM200_errpos[i])
                lM200_errneg_return.append(lM200_errneg[i])
                redshift_return.append(redshift[i])
                passive_return.append(passive[i])

    return(np.asarray(Rproj_return),np.asarray(logP_return),np.asarray(logP_hi_return),np.asarray(logP_lo_return),np.asarray(lM200_return),np.asarray(lM200_errpos_return),np.asarray(lM200_errneg_return),np.asarray(redshift_return),np.asarray(passive_return))
    #return(Rproj,logU,logU_hi,logU_lo,lM200,lM200_errpos,lM200_errneg,redshift)
    
def Prochaska_2017_Densities():
    lMStar_pub, sSFR_pub, Rproj, lognH_lo, lognH, lognH_hi = np.loadtxt("%s/Prochaska_2017.COS-Halos.dat"%DataDir, usecols=(2,3,4,5,6,7), unpack=True)
    # We should read redshift, but it's weird... not really needed for lognH, unlike logU.   
    redshift = lMStar_pub*0 + 0.2
    lMStar_err = 0.2
    
    lM200 = lMStar_pub*0.
    lM200_errpos = lMStar_pub*0.
    lM200_errneg = lMStar_pub*0.
    for i in range(len(lMStar_pub)):
        lM200[i], lM200_errpos[i], lM200_errneg[i] = smhm.Behroozi2019_UNIVERSEMACHINE_return_lM200c(lMStar_pub[i],lMStar_err,redshift[i])
        
    return(Rproj, lognH, lognH_lo, lognH_hi, lM200,lM200_errpos,lM200_errneg, redshift)

def Tchernyshyov_2022_NOVI(survey_return):

    types = ["|S12", "float", "float", "float", "|S2", "float", "float","|S1"]

    survey,redshift,R,lMStar, GalType,R200c,lNOVI,OVI_flag = np.genfromtxt("%s/Tchernyshyov_2022.Table3.tsv"%DataDir,delimiter=';',dtype=types,usecols=(0,4,5,6,7,8,9,10),unpack=True)

    lMStar_err = 0.2
    
    R_return = []
    redshift_return = []
    R200c_return = []
    lMStar_return = []
    lNOVI_return = []
    OVI_flag_int_return = []
    lM200c_smhm_return = []
    lM200c_errpos_smhm_return = []
    lM200c_errneg_smhm_return = []
    galaxy_type = []
    survey_str = [None]*len(lNOVI)
    OVI_flag_int = np.zeros(len(lNOVI))
    for i in range(len(survey)):
        survey_str[i] = survey[i].decode("utf-8")
        GalType_str = GalType[i].decode("utf-8")
        if(OVI_flag[i].decode("utf-8")=="<"):
            OVI_flag_int[i] = 1
        else:
            OVI_flag_int[i] = 0
        if survey_return in survey_str[i]:
            #print(redshift[i],R[i]/R200c[i],lMStar[i])
            if(GalType[i]=='SF'):
                lM200c_smhm, lM200c_errpos_smhm, lM200c_errneg_smhm = smhm.Behroozi2019_UNIVERSEMACHINE_return_lM200c(lMStar[i],lMStar_err,redshift[i],galaxy_type_tag='_sf')
            else:
                lM200c_smhm, lM200c_errpos_smhm, lM200c_errneg_smhm = smhm.Behroozi2019_UNIVERSEMACHINE_return_lM200c(lMStar[i],lMStar_err,redshift[i],galaxy_type_tag='_q')

            redshift_return.append(redshift[i])
            R_return.append(R[i])
            lMStar_return.append(lMStar[i])
            R200c_return.append(R200c[i])
            lNOVI_return.append(lNOVI[i])
            OVI_flag_int_return.append(OVI_flag_int[i])
            lM200c_smhm_return.append(lM200c_smhm)
            lM200c_errpos_smhm_return.append(lM200c_errpos_smhm)
            lM200c_errneg_smhm_return.append(lM200c_errneg_smhm)
            galaxy_type.append(GalType_str)
            #print("T22 i,lNOVI,lMStar= ", i,lNOVI[i],lMStar[i])

    #return(np.asarray(R_return), np.asarray(R200c_return), np.asarray(lNOVI_return), np.asarray(OVI_flag_int_return), np.asarray(lMStar_return), np.asarray(redshift_return))
    return(np.asarray(R_return), np.asarray(R200c_return), np.asarray(lNOVI_return), np.asarray(OVI_flag_int_return), np.asarray(lM200c_smhm_return), np.asarray(lM200c_errpos_smhm_return), np.asarray(lM200c_errpos_smhm_return), np.asarray(redshift_return),np.asarray(galaxy_type))
    
def Tchernyshyov_Voit_CrossMatch():

    types = ["|S12", "|S24", "float", "float", "float", "|S2", "float", "float","|S1"]
    Tchernyshyov_survey_name_array = ["COS-Halos","CGM^2","eCGM","COS-LRG","Johnson+2017","COS-GTO-1","COS-GTO-2","RDR","QSAGE"]
    survey_T22,los_T22,redshift_T22,R_T22,lMStar_T22, GalType_T22,R200c,lNOVI,OVI_flag = np.genfromtxt("%s/Tchernyshyov_2022.Table3.tsv"%DataDir,delimiter=';',dtype=types,usecols=(0,1,4,5,6,7,8,9,10),unpack=True)
    
    old_survey_ID,logU_primary,survey_ID_V19,logU,logU_hi,logU_lo,R_V19,lMStar_V19,redshift_V19,MStar_P17,Rproj_P17,lognH_lo,lognH_med,lognH_hi,passive = np.loadtxt("%s/LogU_table.nullfilled.csv"%DataDir, usecols=(0,1,2,3,4,5,6,7,10,18,20,21,22,23,25), delimiter=',',unpack=True, encoding='utf-8-sig')
    los_V19 = np.genfromtxt("%s/LogU_table.nullfilled.csv"%DataDir,delimiter=',',dtype=["|S10"], usecols=(16),unpack=True)
    print("los_V19= ", los_V19)
    Voit_survey_name_array = ["COS-Halos-SF", "COS-Halos-Q", "COS-LRG", "COS-GTO-SF", "COS-GTO-Q"]
    Voit_survey_ID_array = [4,5,1,2,3]

    simple_survey_name_array = ["COS-Halos", "COS-LRG", "COS-GTO"]

    for k in range(len(simple_survey_name_array)):
        for i in range(len(lMStar_T22)):
            survey_str_T22 = survey_T22[i].decode("utf-8")
            if(simple_survey_name_array[k] in survey_str_T22):
                for j in range(len(lMStar_V19)):
                    for jj in range(len(Voit_survey_ID_array)):
                        if(survey_ID_V19[j] == Voit_survey_ID_array[jj]):
                            Voit_survey_name = Voit_survey_name_array[jj]
                    if(simple_survey_name_array[k] in Voit_survey_name):
                        if(np.fabs(redshift_T22[i]-redshift_V19[j])<0.005):
                            if(np.fabs(1-R_T22[i]/R_V19[j])<0.1):
                                if(np.fabs(lMStar_T22[i]-lMStar_V19[j])<0.5):
                                    #print("Match= ", k, i, los_T22[i].decode("utf-8"),lMStar_T22[i],redshift_T22[i],R_T22[i],los_V19[j],lMStar_V19[j],redshift_V19[j],R_V19[j])
                                    print("%1d %3d %3d %10s %10s %5.2f %5.2f %5.3f %5.3f %5.1f %5.1f"%(k, i, j, los_T22[i].decode("utf-8"),los_V19[j].decode("utf-8"),lMStar_T22[i],lMStar_V19[j],redshift_T22[i],redshift_V19[j],R_T22[i],R_V19[j]))

def Tchernyshyov_Wakker_CrossMatch():

    types = ["|S12", "|S24", "float", "float", "float", "|S2", "float", "float","|S1"]
    Tchernyshyov_survey_name_array = ["COS-Halos","CGM^2","eCGM","COS-LRG","Johnson+2017","COS-GTO-1","COS-GTO-2","RDR","QSAGE"]
    survey_T22,los_T22,redshift_T22,R_T22,lMStar_T22, GalType_T22,R200c,lNOVI,OVI_flag = np.genfromtxt("%s/Tchernyshyov_2022.Table3.tsv"%DataDir,delimiter=';',dtype=types,usecols=(0,1,4,5,6,7,8,9,10),unpack=True)

    Wakker_file_name = "GALAXYINFO.Wakker_COSHalos.dat"
    zQSO_W,redshift_W,R_W,lMStar_W = np.loadtxt("%s/%s"%(DataDir,Wakker_file_name), usecols=(1,11,12,21),unpack=True)
    los_W,survey_W = np.genfromtxt("%s/%s"%(DataDir,Wakker_file_name), dtype=["|S24","|S6"],usecols=(0,27),unpack=True)

    for i in range(len(lMStar_T22)):
        survey_str_T22 = survey_T22[i].decode("utf-8")
        for j in range(len(lMStar_W)):
            if(np.fabs(redshift_T22[i]-redshift_W[j])<=0.001):
                if(np.fabs(1-R_T22[i]/R_W[j])<0.1):
                    if(np.fabs(lMStar_T22[i]-lMStar_W[j])<1.0):
                        #print("Match= ", k, i, los_T22[i].decode("utf-8"),lMStar_T22[i],redshift_T22[i],R_T22[i],los_V19[j],lMStar_V19[j],redshift_V19[j],R_V19[j])
                        print("%4d %4d  %5.2f %5.2f  %5.3f %5.3f  %5.1f %5.1f  %24s %24s"%(i, j,lMStar_T22[i],lMStar_W[j],redshift_T22[i],redshift_W[j],R_T22[i],R_W[j],los_T22[i].decode("utf-8"),los_W[j].decode("utf-8")))




def Miller_2015_nH_fit_MW(lM200c,lR,R200c):

    R200c_kpc = R200c*1e+03
    r_kpc = 10**lR * R200c_kpc
    ne_over_nh = 1.16
    
    n0_rc_normed = 1.35e-02
    correction = 1./0.3
    #correction = 1.1e-04/1.54e-05 # Corrected to Faerman LMC e^-2 value. 
    beta= 0.50
    
    n_e = n0_rc_normed*correction/(r_kpc)**(3*beta)

    print("r_kpc = ", r_kpc)
    print("n_e = ", n_e)

    nH = n_e/ne_over_nh

    M_200_hot = myutils.calc_spherical_mass(nH,r_kpc,R200c_kpc)
    print("M_200_hot_Miller = ", M_200_hot)
    return(nH)

def Bregman_2018_nH_fit_MW(lM200c,lR,R200c):
    #n(r) = n_0 r_c^(3*beta)/r^(3*beta)
    #n_0 r_c^(3*beta) = 1.20e-02 (+2.13,-0.82)
    #beta = 0.56 (+0.10,-0.12)
    # Is this electron density?  XXX

    R200c_kpc = R200c*1e+03
    r_kpc = 10**lR * R200c_kpc
    ne_over_nh = 1.16
    
    n0_rc_normed = 1.2e-02
    correction = 1.1e-04/1.54e-05 # Corrected to Faerman LMC e^-2 value. 
    beta= 0.56
    
    n_e = n0_rc_normed*correction/(r_kpc)**(3*beta)

    nH = n_e/ne_over_nh

    M_200_hot = myutils.calc_spherical_mass(nH,r_kpc,R200c_kpc)
    return(nH)

def Zhang_2024_eRASS4_Xray(massbinname):

    #data_file = ModelDir + '/profiles_feb21_forErwin/profile_CENhalo_CGM_XRB_%s.txt'%massbinname
    data_file = DataDir + '/profile_CENhalo_CGM_XRB_%s.txt'%massbinname
    if(massbinname=="hMW"):
        M_200m = 5.5e+11
    if(massbinname=="MW"):
        M_200m = 1.7e+12
    if(massbinname=="M31"):
        M_200m = 5.0e+12
    if(massbinname=="2M31"):
        M_200m = 1.6e+13
    if(massbinname=="4M31"):
        M_200m = 4.8e+13

    lM_200m = np.log10(M_200m)
    
    bins_mean,bins_low,bins_up,profile_gal_cen,profile_gal_cen_err,psf_gal_cen=np.transpose(np.loadtxt(data_file,unpack=True))[:6]
    profile_subsatboost=np.transpose(np.loadtxt(data_file,unpack=True))[6:]

    x_bin = bins_mean
    y_bin = profile_subsatboost[2]
    xerrlo_bin =  bins_low
    xerrhi_bin =  bins_up
    yerr_bin = profile_subsatboost[3]

    return(x_bin, y_bin, xerrlo_bin, xerrhi_bin, yerr_bin, lM_200m)
    
def Zhang_2024b_eRASS4_LX():
    data = pd.read_csv('%s/Zhang2024b_Table3.txt'%DataDir, index_col=0, header=None).T
    M200m, M200m_errlo, M200m_errhi, M500c, M500c_errlo, M500c_errhi, LX, LX_err = data

    M200m = M200m.split(" ")
    M200m = np.asarray(M200m, dtype=float)
    M200m_errlo = M200m_errlo.split(" ")
    M200m_errlo = np.asarray(M200m_errlo, dtype=float)
    M200m_errhi = M200m_errhi.split(" ")
    M200m_errhi = np.asarray(M200m_errhi, dtype=float)
    M500c = M500c.split(" ")
    M500c = np.asarray(M500c, dtype=float)
    M500c_errlo = M500c_errlo.split(" ")
    M500c_errlo = np.asarray(M500c_errlo, dtype=float)
    M500c_errhi = M500c_errhi.split(" ")
    M500c_errhi = np.asarray(M500c_errhi, dtype=float)
    LX = LX.split(" ")
    LX = np.asarray(LX, dtype=float)
    LX_err = LX_err.split(" ")
    LX_err = np.asarray(LX_err, dtype=float)

    return(M500c,M500c_errlo,M500c_errhi,LX, LX_err)
