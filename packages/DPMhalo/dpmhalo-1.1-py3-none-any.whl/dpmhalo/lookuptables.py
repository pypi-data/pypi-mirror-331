import numpy as np
import dpmhalo
from dpmhalo import iontab
from dpmhalo import emissiontab
from scipy.interpolate import RegularGridInterpolator
import os 

lnelo = -8.0
lnehi = 0.0
lnestep = 0.25
lTlo = 4.0
lThi = 9.0
lTstep = 0.05
lZlo = -2.0
lZhi = 0.5
lZstep = 0.25
#zlo = 0.0
#zhi = 0.5
#zstep = 0.1

nne = int((lnehi-lnelo)/lnestep+1)
nT = int((lThi-lTlo)/lTstep+1)
nZ = int((lZhi-lZlo)/lZstep+1)
nredshifts = 1

lne_array = np.linspace(lnelo,lnehi,num=nne)
lT_array = np.linspace(lTlo,lThi,num=nT)
lZ_array = np.linspace(lZlo,lZhi,num=nZ)

def write_ascii_files(redshift, do_oxy=True,do_softxray=False):

    if(do_oxy):
        foxy = open("oxygen_ions.z%5.3f.ascii"%redshift, "w")
    if(do_softxray):
        fsoftxray = open("softxray.z%5.3f.ascii"%redshift, "w")

    for l in range(nredshifts):
        trident = iontab.Trident(10**lne_array[0],10**lT_array[0],10**lZ_array[0],redshift)
        pyxsim = emissiontab.pyXSIM(10**lne_array[0],10**lT_array[0],10**lZ_array[0],redshift)
        for i in range(nne):
            for j in range(nT):
                if(do_oxy):
                    no6, no7, no8 = trident.returnoxygenions(10**lne_array[i],10**lT_array[j],1.0,redshift)
                    print(no6,no7,no8,10**lne_array[i],10**lT_array[j])
                    foxy.write("% 5.3f %5.3f % 5.3f %5.2f % 5.3e % 5.3e % 5.3e\n"%(lne_array[i],lT_array[j],0.0,redshift,no6,no7,no8))
                if(do_softxray):
                    for k in range(nZ):
                        softxray = pyxsim.returnsoftxray(10**lne_array[i],10**lT_array[j],10**lZ_array[k],redshift)
                        fsoftxray.write("% 5.3f %5.3f % 5.3f %5.2f % 5.3e\n"%(lne_array[i],lT_array[j],lZ_array[k],redshift,softxray))

    if(do_oxy):                        
        foxy.close()
    if(do_softxray):
        fsoftxray.close()

def write_npy_tables(band,redshift):

    if(band=="SoftXray"):
        softxray = np.loadtxt("softxray.z%5.3f.ascii"%redshift,usecols=(4),unpack=True) # 4/23/24 Added in redshift
    else:
        o6,o7,o8 = np.loadtxt("oxygen_ions.z%5.3f.ascii"%redshift,usecols=(4,5,6),unpack=True)  # 4/23/24 Added in redshfit

    if(band=="SoftXray"):
        grid = np.zeros((nne, nT, nZ))
    else:
        grid = np.zeros((nne, nT))
        
    for i in range(nne):
        for j in range(nT):
            if(band == "OVI"):
                grid[i,j] = o6[i*nT+j]
            if(band == "OVII"):
                grid[i,j] = o7[i*nT+j]
            if(band == "OVIII"):
                grid[i,j] = o8[i*nT+j]
            if(band == "SoftXray"):
                for k in range(nZ):
                    grid[i,j,k] = softxray[i*nT*nZ+j*nZ+k]
        
    print("writing npy file")

    np.save("%s_z%5.3f.npy"%(band,redshift),grid)

def load_grid(band,redshift):

    path = dpmhalo.__path__[0]
    
    grid = np.load(path + "/lookuptables/%s_z%5.3f.npy"%(band,redshift))

    return(grid)
             
def interpolate_lookuptable(band, grid, lne, lT, lZ, redshift):

    lne_array = np.linspace(lnelo,lnehi,num=nne)
    lT_array = np.linspace(lTlo,lThi,num=nT)
    if(band=="SoftXray"):
        lZ_array = np.linspace(lZlo,lZhi,num=nZ)

    #print("Interpolate= ", lne, lT, lZ)
    if(band=="SoftXray"):
        fn = RegularGridInterpolator((lne_array,lT_array,lZ_array), grid,bounds_error=False, fill_value=0.0)
        val = fn([lne, lT, lZ])
    else:
        fn = RegularGridInterpolator((lne_array,lT_array), grid,bounds_error=False, fill_value=0.0)
        val = fn([lne, lT])
        val *= 10**lZ

    return(val.item())
