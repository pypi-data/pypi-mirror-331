import numpy as np
from astropy import constants as const
from dpmhalo import myconstants as myc
import astropy.units as u
import colossus
from colossus.halo import mass_so
from colossus.halo import mass_defs
from colossus.halo import mass_adv


def lM500c_to_lM200c(lM500c, redshift=0.0):
    M500c_h = 10**lM500c*myc.hubbleparam
    M200c_h, R200c_h, R200c = mass_adv.changeMassDefinitionCModel(M500c_h, redshift, '500c', '200c')
    return(np.log10(M200c_h/myc.hubbleparam))

def lM200c_to_lM500c(lM200c, redshift=0.0):
    M200c_h = 10**lM200c*myc.hubbleparam
    M500c_h, R500c_h, R500c = mass_adv.changeMassDefinitionCModel(M200c_h, redshift, '200c', '500c')
    return(np.log10(M500c_h/myc.hubbleparam))

def lMvir_to_lM200c(lMvir, redshift=0.0):
    Mvir_h = 10**lMvir*myc.hubbleparam
    M200c_h, R200c_h, R200c = mass_adv.changeMassDefinitionCModel(Mvir_h, redshift, 'vir', '200c')
    return(np.log10(M200c_h/myc.hubbleparam))

def lM200c_to_lMvir(lM200c, redshift=0.0):
    M200c_h = 10**lM200c*myc.hubbleparam
    Mvir_h, Rvir_h, Rvir = mass_adv.changeMassDefinitionCModel(M200c_h, redshift, '200c', 'vir')
    return(np.log10(Mvir_h/myc.hubbleparam))

def lM200m_to_lM200c(lM200m, redshift=0.0):
    M200m_h = 10**lM200m*myc.hubbleparam
    M200c_h, R200c_h, R200c = mass_adv.changeMassDefinitionCModel(M200m_h, redshift, '200m', '200c')
    return(np.log10(M200c_h/myc.hubbleparam))


def R200c_to_Rvir(R200c, redshift=0.0):
    R200c_h = R200c*myc.hubbleparam
    M200c_h = mass_so.R_to_M(R200c_h, redshift, '200c')
    Mvir_h, Rvir_h, cvir = mass_adv.changeMassDefinitionCModel(M200c_h, redshift, '200c', 'vir')
    return(Rvir_h/myc.hubbleparam)

def R200c_to_R500c(R200c, M200c, redshift=0.0):
    R200c_h = R200c*myc.hubbleparam
    M200c_h = mass_so.R_to_M(R200c_h, redshift, '200c')
    M500c_h, R500c_h, c500c = mass_adv.changeMassDefinitionCModel(M200c_h, redshift, '200c', '500c')
    return(R500c_h/myc.hubbleparam)

def R200c_to_R200m(R200c, M200c, redshift=0.0):
    R200c_h = R200c*myc.hubbleparam
    M200c_h = mass_so.R_to_M(R200c_h, redshift, '200c')
    M200m_h, R200m_h, c200m = mass_adv.changeMassDefinitionCModel(M200c_h, redshift, '200c', '200m')
    return(R200m_h/myc.hubbleparam)


def R500c_to_R200c(R500c, redshift=0.0):
    R500c_h = R500c*myc.hubbleparam
    M500c_h = mass_so.R_to_M(R500c_h, redshift, '200c')
    M200c_h, R200c_h, c200c = mass_adv.changeMassDefinitionCModel(M500c_h, redshift, '500c', '200c')
    return(R200c_h/myc.hubbleparam)


def fR200c_to_fRvir(fR200c, M200c, redshift=0.0):
    M200c_h = M200c*myc.hubbleparam
    R200c_h = mass_so.M_to_R(M200c_h, redshift, '200c')
    Mvir_h, Rvir_h, cvir = mass_adv.changeMassDefinitionCModel(M200c_h, redshift, '200c', 'vir')
    return(fR200c*R200c_h/Rvir_h)

def fRvir_to_fR200c(fRvir, Mvir, redshift=0.0):
    Mvir_h = Mvir*myc.hubbleparam
    Rvir_h = mass_so.M_to_R(Mvir_h, redshift, 'vir')
    M200c_h, R200c_h, c200c = mass_adv.changeMassDefinitionCModel(Mvir_h, redshift, 'vir', '200c')
    return(fRvir*Rvir_h/R200c_h)

    
def fR200c_to_fR500c(fR200c, M200c, redshift=0.0):
    M200c_h = M200c*myc.hubbleparam
    R200c_h = mass_so.M_to_R(M200c_h, redshift, '200c')
    M500c_h, R500c_h, c500c = mass_adv.changeMassDefinitionCModel(M200c_h, redshift, '200c', '500c')
    return(fR200c*R200c_h/R500c_h)

def fR500c_to_fR200c(fR500c, M500c, redshift=0.0):
    M500c_h = M500c*myc.hubbleparam
    R500c_h = mass_so.M_to_R(M500c_h, redshift, '500c')
    M200c_h, R200c_h, c200c = mass_adv.changeMassDefinitionCModel(M500c_h, redshift, '500c', '200c')
    return(fR500c*R500c_h/R200c_h)


def return_lMratio_Rratio(lM200c, redshift, new_radius):

    M200c = 10**lM200c
    M200c_h = M200c*myc.hubbleparam
    R200c_h = mass_so.M_to_R(M200c_h, redshift, '200c')
    R200c = R200c_h/myc.hubbleparam

    Mnew_h, Rnew_h, cnew = mass_adv.changeMassDefinitionCModel(M200c_h, redshift, '200c', new_radius)
    Mnew = Mnew_h/myc.hubbleparam
    Rnew = Rnew_h/myc.hubbleparam
    
    return(np.log10(Mnew/M200c), Rnew/R200c)


def R200c_from_lM200c(lM200c, redshift=0.0):
    M200c = 10**lM200c
    M200c_h = M200c*myc.hubbleparam
    R200c_h = mass_so.M_to_R(M200c_h, redshift, '200c')
    R200c = R200c_h/myc.hubbleparam

    return(R200c)

def R200c_from_lM200c_in_cm(lM200c, redshift=0.0):
   
    R200c = R200c_from_lM200c(lM200c,redshift)
    R200c_cm = R200c*myc.cm_per_kpc
    return(R200c_cm)

def lM200c_from_R200c(R200c, redshift=0.0):

    R200c_h = R200c*myc.hubbleparam
    M200c_h = mass_so.R_to_M(R200c_h, redshift, '200c')
    M200c = M200c_h/myc.hubbleparam
    lM200c = np.log10(M200c)

    return(lM200c)

def E(redshift):
    return(np.sqrt(myc.OmegaM*(1+redshift)**3+(1-myc.OmegaM)))

def return_P500_z0(lM200c):
    
    P500c = 3/(8*np.pi)*(500*const.G.cgs**(-1/4.)*(myc.HubbleParam/myc.km_per_Mpc/u.s)**2/4.)**(4/3.)*myc.mu/myc.mu_e*myc.f_b*(10**lM200c_to_lM500c(lM200c)*const.M_sun.cgs)**(2/3.)/const.k_B.cgs
    return(P500c)

def convert_Pe_to_Pe500(Pe, lM200c, redshift, return_only_P500=False):

    rho_crit = 1.88e-29*myc.hubbleparam**2*(1+redshift)**3
    ne_500c = 500.*myc.f_b*rho_crit/(myc.mu_e*const.m_p.to('g').value) # cm^-3
    rho_500c = 500.*rho_crit
    M_500c = 10**lM200c_to_lM500c(lM200c)
    R_500c = (M_500c*const.M_sun.cgs/rho_500c*(3/(4*np.pi)))**0.3333   # cm
    T_500c = (const.G.cgs.value*(10**lM200c_to_lM500c(lM200c)*const.M_sun.cgs)*myc.mu*const.m_p.to('g').value/(2*R_500c*const.k_B.cgs))
    Pe_500c = ne_500c*T_500c
    Pe_500c = Pe_500c.value

    if(return_only_P500==True):
        return(Pe_500c)
    else:
        return(Pe/Pe_500c)
    
def convert_K_to_K500(K, lM200c,redshift, return_only_K500=False):

    rho_crit = 1.88e-29*myc.hubbleparam**2*(1+redshift)**3
    ne_500c = 500.*myc.f_b*rho_crit/(myc.mu_e*const.m_p.to('g').value) # cm^-3
    rho_500c = 500.*rho_crit
    M_500c = 10**lM200c_to_lM500c(lM200c)
    R_500c = (M_500c*const.M_sun.cgs/rho_500c*(3/(4*np.pi)))**0.3333   # cm
    T_500c = (const.G.cgs.value*(10**lM200c_to_lM500c(lM200c)*const.M_sun.cgs)*myc.mu*const.m_p.to('g').value/(2*R_500c*const.k_B.cgs))
    K_500c = T_500c/ne_500c**(2/3.)
    K_500c = K_500c.value*myc.keV_per_K

    if(return_only_K500==True):
        return(K_500c)
    else:
        return(K/K_500c)

    
def calc_spherical_mass(ne,lM_200,R,R_outer,redshift):

    R200c_cm = R200c_from_lM200c_in_cm(lM_200,redshift)

    M_sum = 0.0
    r_cm = R * R200c_cm
    r_outer_cm = R_outer*R200c_cm
    
    for i in range(len(r_cm)):
        if((i>0) & (r_cm[i]<r_outer_cm)):
            M_sum += 4*np.pi/3.*(r_cm[i]**3-r_cm[i-1]**3)*(ne[i]+ne[i-1])/2.*const.m_p.to('g').value/myc.ne_to_nH/myc.XH
        if((r_cm[i]>r_outer_cm) & (r_cm[i-1]<r_outer_cm)):
            ne_200 = 10**(np.log10(ne[i-1]) + (np.log10(ne[i])-np.log10(ne[i-1]))*(r_outer_cm-r_cm[i-1])/(r_cm[i]-r_cm[i-1]))
            M_sum_old = M_sum
            M_sum += 4*np.pi/3.*((r_outer_cm)**3-r_cm[i-1]**3)*(ne_200+ne[i-1])/2.*const.m_p.to('g').value/myc.ne_to_nH/myc.XH

    return(M_sum )

