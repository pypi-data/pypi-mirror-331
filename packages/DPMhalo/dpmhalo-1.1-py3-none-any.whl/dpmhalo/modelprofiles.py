import numpy as np
from astropy import constants as const
from astropy import units as u
from dpmhalo import gaussian
from dpmhalo import lookuptables
from dpmhalo import myconstants as myc
import trident
import colossus
from colossus.cosmology import cosmology

cosmo = cosmology.setCosmology('planck18')

SoftXray_lookupTable = lookuptables.load_grid("SoftXray",0.0)  

class ModelMFlexGNFW:
  
  def __init__(self, Mhalo, redshift, Pnorm12, alphatrP12, alphahiP12, alphaloP12, c500P, alphatrPMvar, alphahiPMvar, alphaloPMvar, betaP, gammaP, nenorm12, alphatrne12, alphahine12, alphalone12, c500ne, alphatrneMvar, alphahineMvar, alphaloneMvar, betane, gammane, sigmalogne, Znorm12, alphatrZ12, alphahiZ12, alphaloZ12, c500Z, alphatrZMvar, alphahiZMvar, alphaloZMvar, betaZ, gammaZ):
    self.Mhalo = Mhalo
    self.redshift = redshift
    self.Pnorm12 = Pnorm12
    self.alphatrP12 = alphatrP12
    self.alphahiP12 = alphahiP12
    self.alphaloP12 = alphaloP12
    self.c500P = c500P
    self.alphatrPMvar = alphatrPMvar
    self.alphahiPMvar = alphahiPMvar
    self.alphaloPMvar = alphaloPMvar
    self.betaP = betaP
    self.gammaP = gammaP
    self.nenorm12 = nenorm12
    self.sigmalogne = sigmalogne
    self.alphatrne12 = alphatrne12
    self.alphahine12 = alphahine12
    self.alphalone12 = alphalone12
    self.c500ne = c500ne
    self.alphatrneMvar = alphatrneMvar
    self.alphahineMvar = alphahineMvar
    self.alphaloneMvar = alphaloneMvar
    self.betane = betane
    self.gammane = gammane
    self.Znorm12 = Znorm12
    self.alphatrZ12 = alphatrZ12
    self.alphahiZ12 = alphahiZ12
    self.alphaloZ12 = alphaloZ12
    self.c500Z = c500Z
    self.alphatrZMvar = alphatrZMvar
    self.alphahiZMvar = alphahiZMvar
    self.alphaloZMvar = alphaloZMvar
    self.betaZ = betaZ
    self.gammaZ = gammaZ

  def E(self,redshift):
    #return(np.sqrt(myc.OmegaM*(1+redshift)**3+myc.OmegaL))
    return(np.sqrt(cosmo.Om0*(1+redshift)**3+(1-cosmo.Om0)))

  def calcP(self,R,Mhalo,redshift):
    x = (R*1.54)*self.c500P
    xR0p3 = (0.3*1.54)*self.c500P
    alphatrP = self.alphatrP12+(np.log10(Mhalo)-12.0)*self.alphatrPMvar
    alphahiP = self.alphahiP12+(np.log10(Mhalo)-12.0)*self.alphahiPMvar
    alphaloP = self.alphaloP12+(np.log10(Mhalo)-12.0)*self.alphaloPMvar
    Pnorm12_c500P = 1 / (xR0p3**alphaloP*(1+xR0p3**alphatrP)**((alphahiP-alphaloP)/alphatrP))
    self.P = (self.Pnorm12/Pnorm12_c500P) / (x**alphaloP * (1+x**alphatrP)**((alphahiP-alphaloP)/alphatrP)) * (Mhalo/1e+12)**self.betaP * self.E(redshift)**self.gammaP
    return(self.P)

  def calcne(self,R,Mhalo,redshift):
    x = (R*1.54)*self.c500ne
    xR0p3 = (0.3*1.54)*self.c500ne
    alphatrne = self.alphatrne12+(np.log10(Mhalo)-12.0)*self.alphatrneMvar
    alphahine = self.alphahine12+(np.log10(Mhalo)-12.0)*self.alphahineMvar
    alphalone = self.alphalone12+(np.log10(Mhalo)-12.0)*self.alphaloneMvar
    nenorm12_c500ne = 1 / (xR0p3**alphalone*(1+xR0p3**alphatrne)**((alphahine-alphalone)/alphatrne))
    self.ne = (self.nenorm12/nenorm12_c500ne) / (x**alphalone * (1+x**alphatrne)**((alphahine-alphalone)/alphatrne)) * (Mhalo/1e+12)**self.betane * self.E(redshift)**self.gammane
    return(self.ne)
  
  def calcZ(self,R,Mhalo,redshift):
    x = (R*1.54)*self.c500Z
    xR0p3 = (0.3*1.54)*self.c500Z
    alphatrZ = self.alphatrZ12+(np.log10(Mhalo)-12.0)*self.alphatrZMvar
    alphahiZ = self.alphahiZ12+(np.log10(Mhalo)-12.0)*self.alphahiZMvar
    alphaloZ = self.alphaloZ12+(np.log10(Mhalo)-12.0)*self.alphaloZMvar
    Znorm12_c500Z = 1 / (xR0p3**alphaloZ*(1+xR0p3**alphatrZ)**((alphahiZ-alphaloZ)/alphatrZ))
    self.Z = (self.Znorm12/Znorm12_c500Z) / (x**alphaloZ * (1+x**alphatrZ)**((alphahiZ-alphaloZ)/alphatrZ)) * (Mhalo/1e+12)**self.betaZ * self.E(redshift)**self.gammaZ
    return(self.Z)

#  def R_to_x_kpc(self,R,Mhalo,redshift):
#    hparam=0.7
#    omegaM = 0.3
#    omegaL = 1-omegaM
#    omegaratio = (omegaM+omegaL/(1+redshift)**3)              
#    r200c = 1.63e-2*(Mhalo*hparam)**0.333/omegaratio**0.333/(1+redshift)/hparam
#    return(R*r200c)

  def AbelTransform(self,obs_type,x_kpc,Rmax_kpc,R200c_kpc,Mhalo,redshift):
    
    step_kpc = 1.
    Integral = 0.
    r_kpc = x_kpc
    step_kpc = r_kpc/10.
    step_kpc = r_kpc/50.
    ##step_kpc = 0.01

    logne_step = 0.05
    logne_nsigma = 3
    logne_nstep = round(self.sigmalogne*logne_nsigma*2/logne_step)


    while r_kpc < Rmax_kpc:
      if(r_kpc+step_kpc > Rmax_kpc):
        step_kpc = Rmax_kpc-r_kpc
      midpoint_kpc = r_kpc+step_kpc*0.5
      path_cm = step_kpc*(midpoint_kpc)/np.sqrt((midpoint_kpc)*(midpoint_kpc)-x_kpc*x_kpc)*const.kpc.to('cm')
      if(obs_type=="FRB"):
        for i in range(logne_nstep+1):
          logne = np.log10(self.calcne((midpoint_kpc)/R200c_kpc,Mhalo,redshift))+logne_step*(i-logne_nstep/2.)
          ne = 10**logne
          frac_vol = gaussian.fractional_volume(np.log10(self.calcne((midpoint_kpc)/R200c_kpc,Mhalo,redshift)),self.sigmalogne,logne,logne_step,logne_nsigma)
          Integral += 2*path_cm*u.cm * self.Upsilon_FRB(ne,redshift) * frac_vol
      if(obs_type=="tSZ"):
        Integral += 2*path_cm*u.cm * self.Upsilon_tSZ(self.calcP((midpoint_kpc)/R200c_kpc,Mhalo,redshift),redshift)
      if(obs_type=="kSZ"):
        for i in range(logne_nstep+1):
          logne = np.log10(self.calcne((midpoint_kpc)/R200c_kpc,Mhalo,redshift))+logne_step*(i-logne_nstep/2.)
          ne = 10**logne
          frac_vol = gaussian.fractional_volume(np.log10(self.calcne((midpoint_kpc)/R200c_kpc,Mhalo,redshift)),self.sigmalogne,logne,logne_step,logne_nsigma)
          Integral += 2*path_cm*u.cm * self.Upsilon_kSZ(ne,redshift) * frac_vol
      if(obs_type=="NOVI"):
        for i in range(logne_nstep+1):
          logne = np.log10(self.calcne((midpoint_kpc)/R200c_kpc,Mhalo,redshift))+logne_step*(i-logne_nstep/2.)
          ne = 10**logne
          frac_vol = gaussian.fractional_volume(np.log10(self.calcne((midpoint_kpc)/R200c_kpc,Mhalo,redshift)),self.sigmalogne,logne,logne_step,logne_nsigma)
          Integral += 2*path_cm*u.cm * self.Upsilon_NO("O VI",self.calcP((midpoint_kpc)/R200c_kpc,Mhalo,redshift),ne,self.calcZ((midpoint_kpc)/R200c_kpc,Mhalo,redshift),redshift) * frac_vol
      if(obs_type=="NOVII"):
        for i in range(logne_nstep+1):
          logne = np.log10(self.calcne((midpoint_kpc)/R200c_kpc,Mhalo,redshift))+logne_step*(i-logne_nstep/2.)
          ne = 10**logne
          frac_vol = gaussian.fractional_volume(np.log10(self.calcne((midpoint_kpc)/R200c_kpc,Mhalo,redshift)),self.sigmalogne,logne,logne_step,logne_nsigma)
          Integral += 2*path_cm*u.cm * self.Upsilon_NO("O VII",self.calcP((midpoint_kpc)/R200c_kpc,Mhalo,redshift),ne,self.calcZ((midpoint_kpc)/R200c_kpc,Mhalo,redshift),redshift) * frac_vol
      if(obs_type=="NOVIII"):
        for i in range(logne_nstep+1):
          logne = np.log10(self.calcne((midpoint_kpc)/R200c_kpc,Mhalo,redshift))+logne_step*(i-logne_nstep/2.)
          ne = 10**logne
          frac_vol = gaussian.fractional_volume(np.log10(self.calcne((midpoint_kpc)/R200c_kpc,Mhalo,redshift)),self.sigmalogne,logne,logne_step,logne_nsigma)
          Integral += 2*path_cm*u.cm * self.Upsilon_NO("O VIII",self.calcP((midpoint_kpc)/R200c_kpc,Mhalo,redshift),ne,self.calcZ((midpoint_kpc)/R200c_kpc,Mhalo,redshift),redshift) * frac_vol        
      if(obs_type=="SoftXray"):
        for i in range(logne_nstep+1):
          logne = np.log10(self.calcne((midpoint_kpc)/R200c_kpc,Mhalo,redshift))+logne_step*(i-logne_nstep/2.)
          ne = 10**logne
          frac_vol = gaussian.fractional_volume(np.log10(self.calcne((midpoint_kpc)/R200c_kpc,Mhalo,redshift)),self.sigmalogne,logne,logne_step,logne_nsigma)
          Integral += 2*path_cm*u.cm * self.Upsilon_Xray("0.5_2.0keV",self.calcP((midpoint_kpc)/R200c_kpc,Mhalo,redshift),ne,self.calcZ((midpoint_kpc)/R200c_kpc,Mhalo,redshift),redshift) * frac_vol
      step_kpc = r_kpc/50. # We integrate using 1/50th the step kpc size.  Can be made less to run faster. 
      r_kpc += step_kpc
      
    return(Integral)

  def Upsilon_FRB(self,ne,redshift):
    return(ne*u.cm**-3/(1+redshift)/const.pc.to('cm')*u.pc/u.cm )

  def Upsilon_tSZ(self,PT,redshift):
    return(PT*u.cm**-3*u.K*const.k_B.to('g*cm**2*s**-2*K**-1')*const.sigma_T.to('cm**2')/(const.m_e.to('g')*const.c.to('cm/s')**2)/u.cm)  # XXX This last 1/u.cm doesn't seem right.  

  def Upsilon_kSZ(self,ne,redshift):
    return(ne*u.cm**-3*const.sigma_T.to('cm**2'))
  
  def Upsilon_NO(self,ion,PT,ne,Z,redshift):
    T = PT/ne
    nH = ne/myc.ne_to_nH ### check!!!
    
    Ofrac = trident.calculate_ion_fraction(ion, nH, T, redshift)

    nO = nH*myc.nO_per_nH_Zsolar*Z*Ofrac

    return(nO)

  def Upsilon_Xray(self,band,PT,ne,Z,redshift):
    T = PT/ne

    lookuptable = SoftXray_lookupTable
    softxray = lookuptables.interpolate_lookuptable("SoftXray",lookuptable,np.log10(ne),np.log10(T),np.log10(Z),redshift)
    
    return(softxray)
