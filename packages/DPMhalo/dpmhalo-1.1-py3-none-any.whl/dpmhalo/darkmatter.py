from dpmhalo import myconstants as myc
from dpmhalo import myutils
from astropy import constants as const
from colossus.halo import concentration
from colossus.halo import profile_nfw
from colossus.cosmology import cosmology

cosmo = cosmology.setCosmology('planck18')

def return_DMrho_for_R(R,lM200c, redshift=0.0):
    M200c = 10**lM200c
    R200c_kpc = myutils.R200c_from_lM200c(lM200c,redshift)
    M200c_h = M200c*myc.hubbleparam
    R_h_kpc = R200c_kpc*R*myc.hubbleparam
    c200c = concentration.concentration(M200c, '200c', redshift)
    p_nfw = profile_nfw.NFWProfile(M = M200c_h, c = c200c, z = redshift, mdef = '200c')
    rho_nfw = p_nfw.density(R_h_kpc) # in Msolar h^2/kpc^3
    rho_nfw_cgs = rho_nfw*(myc.hubbleparam)**2*const.M_sun.cgs.value/(myc.cm_per_kpc)**3
    rho_DM_nfw_cgs = (cosmo.Om0-cosmo.Ob0)/cosmo.Om0*rho_nfw_cgs
    return(rho_DM_nfw_cgs)
