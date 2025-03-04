import numpy as np
import sys
import dpmhalo
from dpmhalo import myutils,darkmatter,modelprofiles

ModelDir = './'

if(len(sys.argv) < 3):
  print("Usage: run_DPM_profile.py 1) model name, 2) log(M200c), Optional: 3) redshift (default 0.0)\n model names: Model1, Model2, Model3, Model1ldsip, Model2ldisp, Model3ldisp, Model3disp\n")
  exit()

modelID = sys.argv[1]
lMhalo = float(sys.argv[2])
Mhalo = 10**lMhalo
if(len(sys.argv)>3):
  redshift = float(sys.argv[3])
else:
  redshift = 0.0

Pnorm12,alphatrP12,alphahiP12,alphaloP12,c500P,alphatrPMvar,alphahiPMvar,alphaloPMvar,betaP,gammaP,nenorm12,alphatrne12,alphahine12,alphalone12,c500ne,alphatrneMvar,alphahineMvar,alphaloneMvar,betane,gammane,sigmalogne,Znorm12,alphatrZ12,alphahiZ12,alphaloZ12,c500Z,alphatrZMvar,alphahiZMvar,alphaloZMvar,betaZ,gammaZ = modelprofiles.returnmodelparams(modelID)
  
ModelMFlexGNFWParams = dpmhalo.ModelMFlexGNFW(Mhalo,redshift,Pnorm12,alphatrP12,alphahiP12,alphaloP12,c500P,alphatrPMvar,alphahiPMvar,alphaloPMvar,betaP,gammaP,nenorm12,alphatrne12,alphahine12,alphalone12,c500ne,alphatrneMvar,alphahineMvar,alphaloneMvar,betane,gammane,sigmalogne,Znorm12,alphatrZ12,alphahiZ12,alphaloZ12,c500Z,alphatrZMvar,alphahiZMvar,alphaloZMvar,betaZ,gammaZ)

fout = open("%s/ModelMFlexGNFW%s.M%5.2f.z%4.2f.dat"%(ModelDir,modelID,lMhalo,redshift),"w")
fout.write("#lM200c z R/R200c P n_e[cm^-3] T[K] Z DM[pc/cm^3] tau_SZ y_SZ SB_SoftXray[erg/s/kpc^2] N_OVI[cm^-2] N_OVII[cm^-2] N_OVIII[cm^-2] sigma^n_e rho_DM[g/cm^3]\n")

R200c_kpc = myutils.R200c_from_lM200c(np.log10(Mhalo),redshift)

for i in range(0,24,1): 
  R = 10**(-2.0+i*0.1)
  ne = ModelMFlexGNFWParams.calcne(R,Mhalo,redshift)
  x_kpc = R*R200c_kpc
  maxR_kpc = 3.0*R200c_kpc

  if(x_kpc<10.0/(1+redshift)): continue
  
  DM = ModelMFlexGNFWParams.AbelTransform("FRB",x_kpc,maxR_kpc,R200c_kpc,Mhalo,redshift)
  ySZ = ModelMFlexGNFWParams.AbelTransform("tSZ",x_kpc,maxR_kpc,R200c_kpc,Mhalo,redshift)
  tauSZ = ModelMFlexGNFWParams.AbelTransform("kSZ",x_kpc,maxR_kpc,R200c_kpc,Mhalo,redshift)
  SoftXray = ModelMFlexGNFWParams.AbelTransform("SoftXray",x_kpc,maxR_kpc,R200c_kpc,Mhalo,redshift)
  NOVI = ModelMFlexGNFWParams.AbelTransform("NOVI",x_kpc,maxR_kpc,R200c_kpc,Mhalo,redshift)
  NOVII = ModelMFlexGNFWParams.AbelTransform("NOVII",x_kpc,maxR_kpc,R200c_kpc,Mhalo,redshift)
  NOVIII = ModelMFlexGNFWParams.AbelTransform("NOVIII",x_kpc,maxR_kpc,R200c_kpc,Mhalo,redshift)
  
  P = ModelMFlexGNFWParams.calcP(R,Mhalo,redshift)
  Z = ModelMFlexGNFWParams.calcZ(R,Mhalo,redshift)
  Pe = P
  T = Pe/ne

  rho_DM = darkmatter.return_DMrho_for_R(R,np.log10(Mhalo),redshift)

  print("%5.2f %5.2f %5.3e %5.3e %5.3e %5.3e %5.3e %5.1f %5.3e %5.3e %5.3e %5.3e %5.3e %5.3e %4.2f %5.3e"%(np.log10(Mhalo),redshift,R,P,ne,T,Z,DM.value,tauSZ.value,ySZ.value,SoftXray.value,NOVI.value,NOVII.value,NOVIII.value,sigmalogne,rho_DM))
  fout.write("%5.2f %5.2f %5.3e %5.3e %5.3e %5.3e %5.3e %5.1f %5.3e %5.3e %5.3e %5.3e %5.3e %5.3e %4.2f %5.3e\n"%(np.log10(Mhalo),redshift,R,P,ne,T,Z,DM.value,tauSZ.value,ySZ.value,SoftXray.value,NOVI.value,NOVII.value,NOVIII.value,sigmalogne,rho_DM))

fout.close()
