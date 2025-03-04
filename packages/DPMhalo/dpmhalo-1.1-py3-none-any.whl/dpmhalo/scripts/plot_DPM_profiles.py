import sys
from astropy import constants as const
from astropy import units as u
import h5py
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import dpmhalo
from dpmhalo import data,myutils
from dpmhalo import myconstants as myc

mpl.rc('xtick', labelsize=20) 
mpl.rc('ytick', labelsize=20) 

PlotDir = './'
ModelDir = './'

if(len(sys.argv) < 2):
  print("Usage: plot_DPM_profiles.py 1) ls filename (i.e. .ls file)\n")
  exit()


cm = plt.get_cmap('turbo') 
cmlo = 11.5
cmhi = 15.0

lsfilename = sys.argv[1]

lsfile = open(lsfilename,"r").readlines()

nhalos = len(lsfile)

if(nhalos == 0):
    do_sims = True
    sim = lsfilename.split("_")[1].split(".")[0]
    simshort = sim
else:
    do_sims = False

if("ClusterGroupScaled5" in lsfilename):
    docolorbar = True
else:
    docolorbar = False
    
xinches = 10.0
yinches = 7.5

fig_Phot_norm = plt.figure(figsize=(xinches,yinches))
ax_Phot_norm = fig_Phot_norm.add_subplot(111)

fig_nehot_norm = plt.figure(figsize=(xinches,yinches))
ax_nehot_norm = fig_nehot_norm.add_subplot(111)

fig_Phot_all = plt.figure(figsize=(xinches,yinches))
ax_Phot_all = fig_Phot_all.add_subplot(111)

fig_nehot_all = plt.figure(figsize=(xinches,yinches))
ax_nehot_all = fig_nehot_all.add_subplot(111)

fig_Thot_all = plt.figure(figsize=(xinches,yinches))
ax_Thot_all = fig_Thot_all.add_subplot(111)

fig_Khot_norm = plt.figure(figsize=(xinches,yinches))
ax_Khot_norm = fig_Khot_norm.add_subplot(111)

fig_Zhot_all = plt.figure(figsize=(xinches,yinches))
ax_Zhot_all = fig_Zhot_all.add_subplot(111)

fig_Mcumhot_all = plt.figure(figsize=(xinches,yinches))
ax_Mcumhot_all = fig_Mcumhot_all.add_subplot(111)

fig_ySZ_all = plt.figure(figsize=(xinches,yinches))
ax_ySZ_all = fig_ySZ_all.add_subplot(111)

fig_DM_all = plt.figure(figsize=(xinches,yinches))
ax_DM_all = fig_DM_all.add_subplot(111)

fig_intkSZ_all = plt.figure(figsize=(xinches,yinches))
ax_intkSZ_all = fig_intkSZ_all.add_subplot(111)

fig_inttSZ_all = plt.figure(figsize=(xinches,yinches))
ax_inttSZ_all = fig_inttSZ_all.add_subplot(111)

fig_SoftXray_all = plt.figure(figsize=(xinches,yinches))
ax_SoftXray_all = fig_SoftXray_all.add_subplot(111)

fig_NOVI_all = plt.figure(figsize=(xinches,yinches))
ax_NOVI_all = fig_NOVI_all.add_subplot(111)

fig_NOVII_all = plt.figure(figsize=(xinches,yinches))
ax_NOVII_all = fig_NOVII_all.add_subplot(111)

fig_NOVIII_all = plt.figure(figsize=(xinches,yinches))
ax_NOVIII_all = fig_NOVIII_all.add_subplot(111)

fig_LXsum = plt.figure(figsize=(xinches,yinches))
ax_LXsum = fig_LXsum.add_subplot(111)

fig_fgas = plt.figure(figsize=(xinches,yinches))
ax_fgas = fig_fgas.add_subplot(111)

fig_rhoDM = plt.figure(figsize=(xinches,yinches))
ax_rhoDM = fig_rhoDM.add_subplot(111)


halolabel_array = []
halolabel_object = []
modellabel_array = []
modellabel_object = []
modellabel_pointobject = []

for h in range(nhalos):

    radial_file = lsfile[h].split()[0]
    radial_file = ModelDir + radial_file
    modellabel = lsfile[h].split()[1]
    halolabel = lsfile[h].split()[2]
    lstyle = lsfile[h].split()[4]
    halolabel_bool = int(lsfile[h].split()[5])
    modellabel_bool = int(lsfile[h].split()[6])

    lM200c = float(halolabel)
    colour=cm((lM200c-cmlo)/(cmhi-cmlo))
    halolabelwrite = "log[$M_{\mathrm{200}}$]$=%s$"%(halolabel)
    modellabelwrite = r"$\mathrm{%s}$"%modellabel
    
    if(lstyle==''):
        lstyle = '-'

    # Translation to symbols.  
    if(lstyle=='-'):
        model_symbol = 's'
    if(lstyle=='--'):
        model_symbol = 'o'
    if(lstyle==':'):
        model_symbol = 'X'
        
        
    if(halolabel_bool):
        halolabel_array.extend([halolabelwrite])
        halolabel_object.extend(ax_intkSZ_all.plot(1e+99,1e+99,color=colour,ls='-',lw=4))

    if(modellabel_bool):
        modellabel_array.extend([modellabelwrite])
        modellabel_object.extend(ax_intkSZ_all.plot(1e+99,1e+99,color='k',ls=lstyle,lw=4))
        modellabel_pointobject.extend(ax_intkSZ_all.plot(1e+99,1e+99,color='k',marker=model_symbol,ms=15,ls=''))
        
    
    lM200c, redshift, R, Pe, ne, T, Z, DM, tauSZ, ySZ, SoftXray, N_OVI, N_OVII, N_OVIII, rho_DM = np.loadtxt(radial_file,usecols=(0,1,2,3,4,5,6,7,8,9,10,11,12,13,15),unpack=True)
    if(len(lM200c)==0):
        continue

    redshift_DPM = redshift[0] # we need this later for data, because some data relations use E(z) scaling.  

    E_z = myutils.E(redshift)

    lR = np.log10(R)

    K = T/ne**(2/3.)*myc.keV_per_K
    
    R200c = myutils.R200c_from_lM200c(lM200c[0],redshift[0])
    LXsum = 0.0
    for i in range(len(SoftXray)):
        if((10**(np.log10(R[i])-0.05)>=0.10) & (10**(np.log10(R[i])-0.05)<=0.66)):
           LXsum += ((R200c*10**(np.log10(R[i])+0.05))**2-(R200c*10**(np.log10(R[i])-0.05))**2)*np.pi*10**(np.log10(SoftXray[i])+42.98)
    
    Pe_500 = myutils.convert_Pe_to_Pe500(Pe,lM200c[0],redshift[0])
    K_500 = myutils.convert_K_to_K500(K,lM200c[0],redshift[0])
    
    Yint_SZ = ySZ*0.
    tauint_SZ = ySZ*0.
    for i in range(len(ySZ)):
        for j in range(i):
            Yint_SZ[i] += ((R200c*10**(np.log10(R[j])+0.05))**2-(R200c*10**(np.log10(R[j])-0.05))**2)*np.pi*ySZ[j]
            tauint_SZ[i] += ((R200c*10**(np.log10(R[j])+0.05))**2-(R200c*10**(np.log10(R[j])-0.05))**2)*np.pi*tauSZ[j]
            
    ax_LXsum.plot(lM200c[0], np.log10(LXsum),color=colour,marker=model_symbol,ms=15)

    ax_intkSZ_all.plot(R, np.log10(tauint_SZ), color=colour, lw=4,ls=lstyle,zorder=20-h)
    ax_inttSZ_all.plot(R, np.log10(Yint_SZ) - 2/3.*np.log10(E_z), color=colour, lw=4,ls=lstyle,zorder=20-h)

    ax_Phot_all.plot(R, np.log10(Pe) - 8/3.*np.log10(E_z), color=colour, lw=4,ls=lstyle,zorder=20-h)
    ax_Phot_norm.plot(R, np.log10(Pe_500), color=colour, lw=4,ls=lstyle,zorder=20-h)

    ax_Khot_norm.plot(R, np.log10(K_500), color=colour, lw=4,ls=lstyle,zorder=20-h)
    
    ax_Thot_all.plot(R, np.log10(Pe/ne) - 2/3.*np.log10(E_z), color=colour, lw=4,ls=lstyle,zorder=20-h)
    
    ax_nehot_all.plot(R, np.log10(ne)+(lM200c-12.0) - 2.*np.log10(E_z), color=colour, lw=4,ls=lstyle,zorder=20-h) #label=labelwrite
    ax_nehot_norm.plot(R, np.log10(ne) - 2.*np.log10(E_z), color=colour, lw=4,ls=lstyle,zorder=20-h) #label=labelwrite 

    ax_Zhot_all.plot(R, np.log10(Z), color=colour, lw=4,ls=lstyle,zorder=20-h) #label=labelwrite

    ax_rhoDM.plot(R, np.log10(rho_DM) - 2.*np.log10(E_z), color=colour, lw=4,ls=lstyle,zorder=20-h)
        
    Mcum = R*0.
    for i in range(len(R)):
        Mcum[i] = myutils.calc_spherical_mass(ne,lM200c[i],R,R[i],redshift[i])
        Mcum[i] /= (10**lM200c[i]*const.M_sun.cgs.value)

    M200c_gas = myutils.calc_spherical_mass(ne,lM200c[0],R,1.0,redshift[0])
    M500c_gas = myutils.calc_spherical_mass(ne,lM200c[0],R,1/myutils.fR200c_to_fR500c(1.0,10**lM200c[0],redshift[0]),redshift[0])
    Mvir_gas = myutils.calc_spherical_mass(ne,lM200c[0],R,1/myutils.fR200c_to_fRvir(1.0,10**lM200c[0],redshift[0]),redshift[0])
    
    fgas_200c = M200c_gas/(10**lM200c[0]*const.M_sun.cgs.value) #*myc.f_b)
    fgas_500c = M500c_gas/(10**(myutils.lM200c_to_lM500c(lM200c[0],redshift[0]))*const.M_sun.cgs.value) #*myc.f_b)
    fgas_vir = Mvir_gas/(10**(myutils.lM200c_to_lMvir(lM200c[0],redshift[0]))*const.M_sun.cgs.value) #*myc.f_b)
    if(h==0):
        ax_fgas.plot(lM200c[0], fgas_200c,color=colour,marker=model_symbol,ls='',ms=15,label="Inside $R_{200}$")
        ax_fgas.plot(lM200c[0], fgas_500c,color=colour,marker=model_symbol,fillstyle="none",ls='',ms=15,label="Inside $R_{500}$")         #ax_fgas.plot(lM200c[0], fgas_vir,color=colour,marker='D',ls='',ms=15,label="Inside $R_\mathrm{vir}$")
    else:
        ax_fgas.plot(lM200c[0], fgas_200c,color=colour,marker=model_symbol,ls='',ms=15)
        ax_fgas.plot(lM200c[0], fgas_500c,color=colour,marker=model_symbol,fillstyle="none",ls='',ms=15)
        #ax_fgas.plot(lM200c[0], fgas_vir,color=colour,marker='D',ls='',ms=15)
  
    ax_Mcumhot_all.plot(R, Mcum, color=colour, lw=4,ls=lstyle,zorder=20-h) 
    
    ax_ySZ_all.plot(R, np.log10(ySZ), color=colour, lw=4,ls=lstyle,zorder=20-h) 
    ax_DM_all.plot(R, np.log10(DM), color=colour, lw=4,ls=lstyle,zorder=20-h) 
    ax_SoftXray_all.plot(R, np.log10(SoftXray)+42.98, color=colour, lw=4,ls=lstyle,zorder=20-h) 

    ax_NOVI_all.plot(R, np.log10(N_OVI), color=colour, lw=4,ls=lstyle,zorder=20-h) 
    ax_NOVII_all.plot(R, np.log10(N_OVII), color=colour, lw=4,ls=lstyle,zorder=20-h) 
    ax_NOVIII_all.plot(R, np.log10(N_OVIII), color=colour, lw=4,ls=lstyle,zorder=20-h) 


lM500c_Akino = [13.0,13.1,13.2,13.3,13.4,13.5,13.6,13.7,13.8,14.2,14.3,14.4,14.5,14.6,14.7,14.8,14.9,15.0]
lM200c_Akino = []
fgas500_Akino = []
fgas500_lo_Akino = []
fgas500_hi_Akino = []
for h in range(len(lM500c_Akino)):
    lM200c_hold = myutils.lM500c_to_lM200c(lM500c_Akino[h])
    M500c_hold, fgas, fgas_lo, fgas_hi = data.Akino_2022_fgas_fit_z0(lM200c_hold,redshift_DPM)
    lM200c_Akino.append(myutils.lM500c_to_lM200c(np.log10(M500c_hold)))
    fgas500_Akino.append(fgas)
    fgas500_lo_Akino.append(fgas_lo)
    fgas500_hi_Akino.append(fgas_hi)

ax_fgas.plot(lM200c_Akino,fgas500_Akino, color='k', lw = 2, alpha=1.0, ls='--',zorder=30,label="Akino+2022")
ax_fgas.plot(lM200c_Akino,fgas500_lo_Akino, color='k', lw = 1, alpha=1.0, ls='--',zorder=30)
ax_fgas.plot(lM200c_Akino,fgas500_hi_Akino, color='k', lw = 1, alpha=1.0, ls='--',zorder=30)

lfR200c_Sun2009, ne_med_Sun2009, ne_lo_Sun2009, ne_hi_Sun2009 = data.Sun_2009_ne_Groups()
lM200c_Sun2009 = 13.65 - np.log10(0.7) #Using lM500=13.5
colour_Sun2009_ne_Groups = cm((lM200c_Sun2009-cmlo)/(cmhi-cmlo))
ax_nehot_all.plot(10**lfR200c_Sun2009,np.log10(ne_med_Sun2009)+(lM200c_Sun2009-12.0), color=colour_Sun2009_ne_Groups, lw=2,alpha=1.0,ls='-',zorder=30,label="Sun+2009 $Gr$")
ax_nehot_all.fill_between(10**lfR200c_Sun2009,np.log10(ne_lo_Sun2009)+(lM200c_Sun2009-12.0),np.log10(ne_hi_Sun2009)+(lM200c_Sun2009-12.0), color=colour_Sun2009_ne_Groups, alpha=0.2, zorder=30)

ax_nehot_norm.plot(10**lfR200c_Sun2009,np.log10(ne_med_Sun2009), color=colour_Sun2009_ne_Groups, lw=2,alpha=1.0,ls='-',zorder=30,label="Sun+2009 $Gr$")
ax_nehot_norm.fill_between(10**lfR200c_Sun2009,np.log10(ne_lo_Sun2009),np.log10(ne_hi_Sun2009), color=colour_Sun2009_ne_Groups, alpha=0.2, zorder=30)

lM200c_Arnaud_plot = [15.0,14.5,14.0] #[15.16,14.66,14.16]
for h in range(len(lM200c_Arnaud_plot)):
    lR = np.linspace(-2.0,0.0,21)
    Pe_Arnaud_MH150_cgs = data.Arnaud_2010_Pe_fit_z0(lM200c_Arnaud_plot[h],lR)
    colour_Arnaud=cm((lM200c_Arnaud_plot[h]-cmlo)/(cmhi-cmlo))
    if(h==0):
        ax_Phot_all.plot(10**lR, np.log10(Pe_Arnaud_MH150_cgs), color=colour_Arnaud, lw=2,alpha=1.0,ls=':',zorder=30,label="Arnaud+2010 $Cl$")
        ax_Phot_norm.plot(10**lR, np.log10(myutils.convert_Pe_to_Pe500(Pe_Arnaud_MH150_cgs,lM200c_Arnaud_plot[h],redshift[0])), color=colour_Arnaud, lw=2,alpha=1.0,ls=':',zorder=30,label="Arnaud+2010 $Cl$")

    else:
        ax_Phot_all.plot(10**lR, np.log10(Pe_Arnaud_MH150_cgs), color=colour_Arnaud, lw=2,alpha=1.0,ls=':',zorder=30)
        ax_Phot_norm.plot(10**lR, np.log10(myutils.convert_Pe_to_Pe500(Pe_Arnaud_MH150_cgs,lM200c_Arnaud_plot[h],redshift[0])), color=colour_Arnaud, lw=2,alpha=1.0,ls=':',zorder=30)

lM500c_Sun2011 = np.log10(7e+13)
redshift_Sun2011 = 0.033 # XXXX Check
lM200c_Sun2011 = myutils.lM500c_to_lM200c(lM500c_Sun2011,redshift_Sun2011)
lR, P_med, P_lo, P_hi = data.Sun_2011_P()
colour_Sun2011_P_Groups = cm((lM200c_Sun2011-cmlo)/(cmhi-cmlo))
ax_Phot_all.plot(10**lR,np.log10(P_med), color=colour_Sun2011_P_Groups, lw=2,alpha=1.0,ls='-.',zorder=30,label="Sun+2011 $Gr$")
ax_Phot_all.fill_between(10**lR,np.log10(P_lo),np.log10(P_hi), color=colour_Sun2011_P_Groups, alpha=0.2, zorder=30)
lR, P500_med, P500_lo, P500_hi = data.Sun_2011_P(return_P500=True)
ax_Phot_norm.plot(10**lR,np.log10(P500_med), color=colour_Sun2011_P_Groups, lw=2,alpha=1.0,ls='-.',zorder=30,label="Sun+2011 $Gr$")
ax_Phot_norm.fill_between(10**lR,np.log10(P500_lo),np.log10(P500_hi), color=colour_Sun2011_P_Groups, alpha=0.2, zorder=30)        

fR200c_Lovisari2015, ne_med_Lovisari2015, ne_lo_Lovisari2015, ne_hi_Lovisari2015 = data.Lovisari_2015_ne_Groups()
lM200c_Lovisari2015 = 13.7 #An assumption, maybe needs to be higher based on M_500, I'm going to move to 13.7.  Note the 20 groups here have a median of M500 at about 4e+13, so that is 13.6 and at + 0.15, so 13.7 is fine.  
colour_Lovisari2015_ne_Groups = cm((lM200c_Lovisari2015-cmlo)/(cmhi-cmlo))
ax_nehot_all.plot(fR200c_Lovisari2015,np.log10(ne_med_Lovisari2015)+(lM200c_Lovisari2015-12.0), color=colour_Lovisari2015_ne_Groups, lw=2,alpha=1.0,ls='-.',zorder=30,label="Lovisari+2015 $Gr$")
ax_nehot_all.fill_between(fR200c_Lovisari2015,np.log10(ne_lo_Lovisari2015)+(lM200c_Lovisari2015-12.0),np.log10(ne_hi_Lovisari2015)+(lM200c_Lovisari2015-12.0), color=colour_Lovisari2015_ne_Groups, alpha=0.2, zorder=30)

ax_nehot_norm.plot(fR200c_Lovisari2015,np.log10(ne_med_Lovisari2015), color=colour_Lovisari2015_ne_Groups, lw=2,alpha=1.0,ls='-.',zorder=30,label="Lovisari+2015 $Gr$")
ax_nehot_norm.fill_between(fR200c_Lovisari2015,np.log10(ne_lo_Lovisari2015),np.log10(ne_hi_Lovisari2015), color=colour_Lovisari2015_ne_Groups, alpha=0.2, zorder=30)

###Mcum_Lovisari2015 = R_Lovisari2015*0.
###for i in range(len(R_Lovisari2015)):
###    Mcum_Lovisari2015[i] = myutils.calc_spherical_mass(ne_med_Lovisari2015,lM200c_Lovisari2015,R_Lovisari2015,R_Lovisari2015[i],0.0)
###    Mcum_Lovisari2015[i] /= (10**lM200c_Lovisari2015*const.M_sun.cgs.value)
###ax_Mcumhot_all.plot(R_Lovisari2015, Mcum_Lovisari2015, color=colour_Lovisari2015_ne_Groups, lw=2,ls=':',alpha=1.0,zorder=30,label="Lovisari 2015 $Gr$")


redshift_McDonald = 0.0
R_200_MH145_kpc = 1.63e-02*(10**14.5*myc.hubbleparam)**0.333/myc.hubbleparam
lR = np.linspace(-2.0,0.0,21)
R_McDonald_MH145_cgs, ne_McDonald_MH145_cgs = data.McDonald_2017_ne_MH145_z0(14.5,lR,R_200_MH145_kpc,redshift_McDonald)
colour_McDonald=cm((14.5-cmlo)/(cmhi-cmlo))
ax_nehot_all.plot(R_McDonald_MH145_cgs/(R_200_MH145_kpc), np.log10(ne_McDonald_MH145_cgs)+(14.5-12.0), color=colour_McDonald, lw=2,alpha=1.0,ls=':',zorder=30,label="McDonald+2017 $Cl$")
ax_nehot_norm.plot(R_McDonald_MH145_cgs/(R_200_MH145_kpc), np.log10(ne_McDonald_MH145_cgs), color=colour_McDonald, lw=2,alpha=1.0,ls=':',zorder=30,label="McDonald+2017 $Cl$")

#Not plotting McDonald cumulative mass.  
Mcum_McDonald_MH145 = R_McDonald_MH145_cgs*0.
R_McDonald_MH145_frac = R_McDonald_MH145_cgs/(R_200_MH145_kpc) #*myc.cm_per_kpc)
redshift_McDonald = 0.0 # XXX- CHeck
for i in range(len(R_McDonald_MH145_cgs)):
    Mcum_McDonald_MH145[i] = myutils.calc_spherical_mass(ne_McDonald_MH145_cgs,14.5,R_McDonald_MH145_frac,R_McDonald_MH145_frac[i],redshift_McDonald)
    Mcum_McDonald_MH145[i] /= (10**14.5*const.M_sun.cgs.value)
    #ax_Mcumhot_all.plot(R_McDonald_MH145_frac, Mcum_McDonald_MH145, color=colour_McDonald, lw=2,ls=':',alpha=1.0,zorder=30,label="McDonald+2017 $Cl$")

lM200c_Ghirardini2019 = [14.9]
redshift_Ghirardini2019 = [0.0]
lM500c_Ghirardini2019 = myutils.lM200c_to_lM500c(lM200c_Ghirardini2019[0],redshift_Ghirardini2019[0])
lR_500 = np.linspace(-2.0,0.3,24)
lR_Ghirardini2019 = np.log10(myutils.fR500c_to_fR200c(10**lR_500,10**lM500c_Ghirardini2019,redshift_Ghirardini2019[0]))
colour_Ghirardini2019=cm((lM200c_Ghirardini2019[0]-cmlo)/(cmhi-cmlo))
Pe_Ghirardini2019_cgs = data.Ghirardini_2019_Pe_fit(lM200c_Ghirardini2019[0],lR_Ghirardini2019,redshift_Ghirardini2019[0])
ax_Phot_all.plot(10**lR_Ghirardini2019, np.log10(Pe_Ghirardini2019_cgs), color=colour_Ghirardini2019, lw=2,alpha=1.0,ls='--',zorder=30,label="Ghirardini+2019 $Cl$")
Pe_Ghirardini2019_norm = data.Ghirardini_2019_Pe_fit(lM200c_Ghirardini2019[0],lR_Ghirardini2019,redshift_Ghirardini2019[0],norm_P500=True)
ax_Phot_norm.plot(10**lR_Ghirardini2019, np.log10(Pe_Ghirardini2019_norm), color=colour_Ghirardini2019, lw=2,alpha=1.0,ls='--',zorder=30,label="Ghirardini+2019 $Cl$")

lM200c_Ghirardini2019 = [14.9]
redshift_Ghirardini2019 = [0.0]
lM500c_Ghirardini2019 = myutils.lM200c_to_lM500c(lM200c_Ghirardini2019[0],redshift_Ghirardini2019[0])
lR_500 = np.linspace(-2.0,0.3,24)
lR_Ghirardini2019 = np.log10(myutils.fR500c_to_fR200c(10**lR_500,10**lM500c_Ghirardini2019,redshift_Ghirardini2019[0]))
colour_Ghirardini2019=cm((lM200c_Ghirardini2019[0]-cmlo)/(cmhi-cmlo))
ne_Ghirardini2019_cgs = data.Ghirardini_2019_ne_fit(lR_Ghirardini2019)
ax_nehot_all.plot(10**lR_Ghirardini2019, np.log10(ne_Ghirardini2019_cgs)+(lM200c_Ghirardini2019[0]-12.0), color=colour_Ghirardini2019, lw=2,alpha=1.0,ls='--',zorder=30,label="Ghirardini+2019 $Cl$")
ax_nehot_norm.plot(10**lR_Ghirardini2019, np.log10(ne_Ghirardini2019_cgs), color=colour_Ghirardini2019, lw=2,alpha=1.0,ls='--',zorder=30,label="Ghirardini+2019 $Cl$")

Mcum_Ghirardini2019 = lR_Ghirardini2019*0.
R_Ghirardini2019 = 10**lR_Ghirardini2019
redshift_Ghirardini2019 = 0.0 
for i in range(len(R_Ghirardini2019)):
    Mcum_Ghirardini2019[i] = myutils.calc_spherical_mass(ne_Ghirardini2019_cgs,lM200c_Ghirardini2019[0],R_Ghirardini2019,R_Ghirardini2019[i],redshift_Ghirardini2019)
    Mcum_Ghirardini2019[i] /= (10**lM200c_Ghirardini2019[0]*const.M_sun.cgs.value)
ax_Mcumhot_all.plot(R_Ghirardini2019, Mcum_Ghirardini2019, color=colour_Ghirardini2019, lw=2,ls='--',alpha=1.0,zorder=30,label="Ghirardini+2019 $Cl$")


lM200c_XGAP = [13.6, 13.9, 14.3]
redshift_XGAP = [0.0, 0.0, 0.0]
# We are not going to plot XGAP.  
lM200c_XGAP = []
redshift_XGAP = []

for i in range(len(lM200c_XGAP)):
    colour_XGAP = cm((lM200c_XGAP[i]-cmlo)/(cmhi-cmlo))
    R_XGAP, lPe_XGAP, lPelo_XGAP, lPehi_XGAP = data.XGAP_profiles(lM200c_XGAP[i],return_P=True)
    lPe_500_XGAP = np.log10(myutils.convert_Pe_to_Pe500(10**lPe_XGAP,lM200c_XGAP[i],redshift_XGAP[i]))
    lPelo_500_XGAP = np.log10(myutils.convert_Pe_to_Pe500(10**lPelo_XGAP,lM200c_XGAP[i],redshift_XGAP[i]))
    lPehi_500_XGAP = np.log10(myutils.convert_Pe_to_Pe500(10**lPehi_XGAP,lM200c_XGAP[i],redshift_XGAP[i]))

    if(i==0):
        ax_Phot_all.plot(R_XGAP, lPe_XGAP, color=colour_XGAP, lw=2, alpha=1.0, ls='--',zorder=30,label="X-GAP")
        ax_Phot_norm.plot(R_XGAP, lPe_500_XGAP, color=colour_XGAP, lw=2, alpha=1.0, ls='--',zorder=30,label="X-GAP")
    else:
        ax_Phot_all.plot(R_XGAP, lPe_XGAP, color=colour_XGAP, lw=2, alpha=1.0, ls='--',zorder=30-i)
        ax_Phot_norm.plot(R_XGAP, lPe_500_XGAP, color=colour_XGAP, lw=2, alpha=1.0, ls='--',zorder=30-i)

    ax_Phot_all.fill_between(R_XGAP,lPelo_XGAP,lPehi_XGAP, color=colour_XGAP, alpha=0.2, zorder=30-i)
    ax_Phot_norm.fill_between(R_XGAP,lPelo_500_XGAP,lPehi_500_XGAP, color=colour_XGAP, alpha=0.2, zorder=30-i)
    
    R_XGAP, lne_XGAP, lnelo_XGAP, lnehi_XGAP = data.XGAP_profiles(lM200c_XGAP[i],return_ne=True)
    if(i==0):
        ax_nehot_norm.plot(R_XGAP, lne_XGAP, color=colour_XGAP, lw=2, alpha=1.0, ls='--',zorder=30,label="X-GAP")
        ax_nehot_all.plot(R_XGAP, lne_XGAP+(lM200c_XGAP[i]-12.0), color=colour_XGAP, lw=2, alpha=1.0, ls='--',zorder=30,label="X-GAP")

    else:
        ax_nehot_norm.plot(R_XGAP, lne_XGAP, color=colour_XGAP, lw=2, alpha=1.0, ls='--',zorder=30-i)
        ax_nehot_all.plot(R_XGAP, lne_XGAP+(lM200c_XGAP[i]-12.0), color=colour_XGAP, lw=2, alpha=1.0, ls='--',zorder=30-i)

    ax_nehot_norm.fill_between(R_XGAP,lnelo_XGAP,lnehi_XGAP, color=colour_XGAP, alpha=0.2, zorder=30-i)
    ax_nehot_all.fill_between(R_XGAP,lnelo_XGAP+(lM200c_XGAP[i]-12.0),lnehi_XGAP+(lM200c_XGAP[i]-12.0), color=colour_XGAP, alpha=0.2, zorder=30-i)

# 6-6-24 X-GAP metallicities taken out.  
#    R_XGAP, lZFe_XGAP, lZFelo_XGAP, lZFehi_XGAP = data.XGAP_profiles(lM200c_XGAP[i],return_ZFe=True)
#    if(i==0):
#        ax_Zhot_all.plot(R_XGAP, lZFe_XGAP, color=colour_XGAP, lw=2, alpha=1.0, ls='--',zorder=30,label="X-GAP")
#    else:
#        ax_Zhot_all.plot(R_XGAP, lZFe_XGAP, color=colour_XGAP, lw=2, alpha=1.0, ls='--',zorder=30-i)

#    ax_Zhot_all.fill_between(R_XGAP,lZFelo_XGAP,lZFehi_XGAP, color=colour_XGAP, alpha=0.2, zorder=30-i)



lMvir_Wu = [11.5,12.5]
redshift_Wu = [0.0, 0.0]
for i in range(len(lMvir_Wu)):
    lMvir,fRvir,DM,DMerr =  data.WuMcQuinn_2023_FRB(lMvir_Wu[i])
    logerr_positive_DM = np.log10(DM+DMerr)-np.log10(DM)
    logerr_negative_DM = np.where(np.isfinite(np.log10(DM)-np.log10(DM-DMerr)), np.log10(DM)-np.log10(DM-DMerr),0.0001)
    fR200c_Wu = myutils.fRvir_to_fR200c(fRvir,10**lMvir,redshift_Wu[i])
    lM200c_Wu = myutils.lMvir_to_lM200c(lMvir,redshift_Wu[i])
    colour_DM = cm((lM200c_Wu[0]-cmlo)/(cmhi-cmlo))
    DM = np.where(DM>0,DM,0.0001)
    if(i==0):
        ax_DM_all.errorbar(fR200c_Wu,np.log10(DM),[logerr_negative_DM,logerr_positive_DM],color=colour_DM,ls='',marker='D',ms=10,zorder=30,alpha=1.0,label="Wu/McQuinn+2023")
    else:
        ax_DM_all.errorbar(fR200c_Wu,np.log10(DM),[logerr_negative_DM,logerr_positive_DM],color=colour_DM,ls='',marker='D',ms=10,zorder=30,alpha=1.0)

lM200c_Pratt2021 = 13.9
R200c_Pratt2021, ySZ_data_Pratt2021, ySZ_err_Pratt2021 = data.Pratt_2021_tSZ()
logerr_positive_Pratt2021 = np.log10(ySZ_data_Pratt2021+ySZ_err_Pratt2021)-np.log10(ySZ_data_Pratt2021)
logerr_negative_Pratt2021 = np.where(np.isfinite(np.log10(ySZ_data_Pratt2021)-np.log10(ySZ_data_Pratt2021-ySZ_err_Pratt2021)), np.log10(ySZ_data_Pratt2021)-np.log10(ySZ_data_Pratt2021-ySZ_err_Pratt2021),10)
colour_Pratt=cm((lM200c_Pratt2021-cmlo)/(cmhi-cmlo))
ax_ySZ_all.errorbar(R200c_Pratt2021[np.where(R200c_Pratt2021<=2.0)],np.log10(ySZ_data_Pratt2021[np.where(R200c_Pratt2021<=2.0)]),[logerr_negative_Pratt2021[np.where(R200c_Pratt2021<=2.0)],logerr_positive_Pratt2021[np.where(R200c_Pratt2021<=2.0)]], color=colour_Pratt,ls='',marker='o',zorder=30,alpha=1.0,label="Pratt+2021 $Gr$")

ax_ySZ_all.errorbar(R200c_Pratt2021[np.where(R200c_Pratt2021>2.0)],np.log10(ySZ_data_Pratt2021[np.where(R200c_Pratt2021>2.0)]),[logerr_negative_Pratt2021[np.where(R200c_Pratt2021>2.0)],logerr_positive_Pratt2021[np.where(R200c_Pratt2021>2.0)]], color=colour_Pratt,ls='',marker='o',zorder=30,alpha=0.2)

lM200c_Bregman2022 = 12.5
Rkpc_Bregman2022,ySZ_med_Bregman2022,ySZ_err_Bregman2022 = data.Bregman_2022_tSZ()
logerr_positive_Bregman2022 = np.log10(ySZ_med_Bregman2022+ySZ_err_Bregman2022)-np.log10(ySZ_med_Bregman2022)
logerr_negative_Bregman2022 = np.where(np.isfinite(np.log10(ySZ_med_Bregman2022)-np.log10(ySZ_med_Bregman2022-ySZ_err_Bregman2022)), np.log10(ySZ_med_Bregman2022)-np.log10(ySZ_med_Bregman2022-ySZ_err_Bregman2022),10)
colour_Bregman=cm((lM200c_Bregman2022-cmlo)/(cmhi-cmlo))

R200c_Bregman2022 = Rkpc_Bregman2022/myutils.R200c_from_lM200c(lM200c_Bregman2022)

ax_ySZ_all.errorbar(R200c_Bregman2022[np.where(R200c_Bregman2022<=2.0)],np.log10(ySZ_med_Bregman2022[np.where(R200c_Bregman2022<=2.0)]),[logerr_negative_Bregman2022[np.where(R200c_Bregman2022<=2.0)],logerr_positive_Bregman2022[np.where(R200c_Bregman2022<=2.0)]], color=colour_Bregman,marker='o',ls='',zorder=30,alpha=1.0,label="Bregman+2022 L*")
ax_ySZ_all.errorbar(R200c_Bregman2022[np.where(R200c_Bregman2022>2.0)],np.log10(ySZ_med_Bregman2022[np.where(R200c_Bregman2022>2.0)]),[logerr_negative_Bregman2022[np.where(R200c_Bregman2022>2.0)],logerr_positive_Bregman2022[np.where(R200c_Bregman2022>2.0)]], color=colour_Bregman,marker='o',ls='',zorder=30,alpha=0.2)

R200c_Lovisari2019, Z_data_Lovisari2019, Z_err_Lovisari2019 = data.Lovisari_2019_Z(combined=True)
logerr_positive_Lovisari2019 = np.log10(Z_data_Lovisari2019+Z_err_Lovisari2019)-np.log10(Z_data_Lovisari2019)
logerr_negative_Lovisari2019 = np.log10(Z_data_Lovisari2019)-np.log10(Z_data_Lovisari2019-Z_err_Lovisari2019)
colour_Lovisari=cm((13.7-cmlo)/(cmhi-cmlo))
ax_Zhot_all.plot(R200c_Lovisari2019,np.log10(Z_data_Lovisari2019), color=colour_Lovisari, marker='o',alpha=1.0,ls='',zorder=30,label="Lovisari+2019 $Gr$")
ax_Zhot_all.errorbar(R200c_Lovisari2019,np.log10(Z_data_Lovisari2019),[logerr_negative_Lovisari2019,logerr_positive_Lovisari2019], color=colour_Lovisari,ls='',zorder=30,alpha=1.0)

R200c_Ghizzardi2021, Z_data_Ghizzardi2021, Z_err_Ghizzardi2021 = data.Ghizzardi_2021_Z()
logerr_positive_Ghizzardi2021 = np.log10(Z_data_Ghizzardi2021+Z_err_Ghizzardi2021)-np.log10(Z_data_Ghizzardi2021)
logerr_negative_Ghizzardi2021 = np.log10(Z_data_Ghizzardi2021)-np.log10(Z_data_Ghizzardi2021-Z_err_Ghizzardi2021)
colour_Lovisari=cm((14.9-cmlo)/(cmhi-cmlo))
ax_Zhot_all.plot(R200c_Ghizzardi2021,np.log10(Z_data_Ghizzardi2021), color=colour_Lovisari, marker='s',alpha=1.0,ls='',zorder=30,label="Ghizzardi+2021 $Cl$")
ax_Zhot_all.errorbar(R200c_Ghizzardi2021,np.log10(Z_data_Ghizzardi2021),[logerr_negative_Ghizzardi2021,logerr_positive_Ghizzardi2021], color=colour_Lovisari,ls='',zorder=30,alpha=1.0)


massbinname = ["MW","M31","2M31"]
redshift_Zhang = [0.09, 0.12, 0.14]

massbinname = ["hMW","MW","M31","2M31","4M31"]
redshift_Zhang = [0.06,0.09,0.12,0.14,0.16]
for i in range(len(massbinname)):
    
    Rproj_eRASS4, XSB_eRASS4, Rprojlo_eRASS4, Rprojhi_eRASS4, XSBerr_eRASS4, lM_200m = data.Zhang_2024_eRASS4_Xray(massbinname[i])
    lM200c = myutils.lM200m_to_lM200c(lM_200m,redshift_Zhang[i])
    R200c = myutils.R200c_from_lM200c(lM200c,redshift_Zhang[i])
    
    R200c_frac_eRASS4 = Rproj_eRASS4/R200c
    Rlo200c_frac_eRASS4 = Rprojlo_eRASS4/R200c
    Rhi200c_frac_eRASS4 = Rprojhi_eRASS4/R200c
    logerr_positive_eRASS4 = np.log10(XSB_eRASS4+XSBerr_eRASS4)-np.log10(XSB_eRASS4)
    logerr_negative_eRASS4 = np.log10(XSB_eRASS4)-np.log10(XSB_eRASS4-XSBerr_eRASS4)

    colour_Zhang=cm((lM200c-cmlo)/(cmhi-cmlo))

    R200m = myutils.R200c_to_R200m(R200c,redshift_Zhang[i])
    
    if(i==0):
        ax_SoftXray_all.errorbar(R200c_frac_eRASS4[np.where(R200c_frac_eRASS4<=R200m/R200c)],np.log10(XSB_eRASS4[np.where(R200c_frac_eRASS4<=R200m/R200c)]), yerr=[logerr_negative_eRASS4[np.where(R200c_frac_eRASS4<=R200m/R200c)],logerr_positive_eRASS4[np.where(R200c_frac_eRASS4<=R200m/R200c)]],xerr=[Rlo200c_frac_eRASS4[np.where(R200c_frac_eRASS4<=R200m/R200c)],Rhi200c_frac_eRASS4[np.where(R200c_frac_eRASS4<=R200m/R200c)]], lw=1, ls='',fmt='o',color=colour_Zhang,label="Zhang+2024a", zorder=30, alpha=1.0)
    else:
        ax_SoftXray_all.errorbar(R200c_frac_eRASS4[np.where(R200c_frac_eRASS4<=R200m/R200c)],np.log10(XSB_eRASS4[np.where(R200c_frac_eRASS4<=R200m/R200c)]), yerr=[logerr_negative_eRASS4[np.where(R200c_frac_eRASS4<=R200m/R200c)],logerr_positive_eRASS4[np.where(R200c_frac_eRASS4<=R200m/R200c)]],xerr=[Rlo200c_frac_eRASS4[np.where(R200c_frac_eRASS4<=R200m/R200c)],Rhi200c_frac_eRASS4[np.where(R200c_frac_eRASS4<=R200m/R200c)]], lw=1, ls='',fmt='o',color=colour_Zhang, zorder=30, alpha=1.0)


    ax_SoftXray_all.errorbar(R200c_frac_eRASS4[np.where(R200c_frac_eRASS4>R200m/R200c)],np.log10(XSB_eRASS4[np.where(R200c_frac_eRASS4>R200m/R200c)]), yerr=[logerr_negative_eRASS4[np.where(R200c_frac_eRASS4>R200m/R200c)],logerr_positive_eRASS4[np.where(R200c_frac_eRASS4>R200m/R200c)]],xerr=[Rlo200c_frac_eRASS4[np.where(R200c_frac_eRASS4>R200m/R200c)],Rhi200c_frac_eRASS4[np.where(R200c_frac_eRASS4>R200m/R200c)]], lw=1, ls='',fmt='o',color=colour_Zhang, zorder=30, alpha=0.2)


#M500c_eRASS4, LX_eRASS4, M500c_errlo_eRASS4, M500c_errhi_eRASS4, LX_err_eRASS4 = data.Zhang_2024b_eRASS4_LX()
M500c_eRASS4, M500c_errlo_eRASS4, M500c_errhi_eRASS4, LX_eRASS4, LX_err_eRASS4 = data.Zhang_2024b_eRASS4_LX()

logerr_positive_eRASS4_M500c = np.log10(M500c_eRASS4+M500c_errhi_eRASS4)-np.log10(M500c_eRASS4)
logerr_negative_eRASS4_M500c = np.log10(M500c_eRASS4)-np.log10(M500c_eRASS4-M500c_errlo_eRASS4)

logerr_positive_eRASS4_LX = np.log10(LX_eRASS4+LX_err_eRASS4)-np.log10(LX_eRASS4)
logerr_negative_eRASS4_LX = np.log10(LX_eRASS4)-np.log10(LX_eRASS4-LX_err_eRASS4)

redshift_eRASS4 = 0.1 # Changed as of 9/25/24 XXX, make more dynamic redshifts?  XXX

#print(np.log10(M500c_eRASS4)-np.log10(M500c_errlo_eRASS4),np.log10(M500c_errhi_eRASS4)-np.log10(M500c_eRASS4),np.log10(LX_err_eRASS4)-np.log10(LX_eRASS4))
#ax_LXsum.plot(myutils.lM500_to_lM200(np.log10(M500c_eRASS4)), np.log10(LX_eRASS4), lw=4, ls='',marker='x',ms=20,color='k',label="Zhang 2024",zorder=30,alpha=1.0)
ax_LXsum.errorbar(myutils.lM500c_to_lM200c(np.log10(M500c_eRASS4),redshift_eRASS4), np.log10(LX_eRASS4), xerr=[logerr_negative_eRASS4_M500c,logerr_positive_eRASS4_M500c],yerr=[logerr_negative_eRASS4_LX,logerr_positive_eRASS4_LX],lw=1,ls='',fmt='o',color='k',label="Zhang+2024b",zorder=30,alpha=1.0)

#Replaced by Akino 2022.  
#lM500_L15, lLX_L15 = data.Lovisari_2015_M500_LX()
#redshift_L15 = 0.0 # XXX Check
#print("Ml500_L15,lLX_L15= ",lM500_L15,lLX_L15)
#ax_LXsum.plot(myutils.lM500c_to_lM200c(lM500_L15,redshift_L15),lLX_L15,lw=2,ls="--",color="k",label="Lovisari+2015",zorder=30,alpha=1.0)

lM500c_Akino = [13.0,13.1,13.2,13.3,13.4,13.5,13.6,13.7,13.8,14.2,14.3,14.4,14.5,14.6,14.7,14.8,14.9,15.0]
lM200c_Akino = []
LX500_Akino = []
LX500_lo_Akino = []
LX500_hi_Akino = []
for h in range(len(lM500c_Akino)):
    lM200c_hold = myutils.lM500c_to_lM200c(lM500c_Akino[h])
    M500c_hold, LX, LX_lo, LX_hi = data.Akino_2022_M500_LX(lM200c_hold,redshift_DPM)
    lM200c_Akino.append(myutils.lM500c_to_lM200c(np.log10(M500c_hold)))          
    LX500_Akino.append(LX)
    LX500_lo_Akino.append(LX_lo)
    LX500_hi_Akino.append(LX_hi)

ax_LXsum.plot(lM200c_Akino,np.log10(LX500_Akino), color='k', lw = 2, alpha=1.0, ls='--',zorder=30,label="Akino+2022")
ax_LXsum.plot(lM200c_Akino,np.log10(LX500_lo_Akino), color='k', lw = 1, alpha=1.0, ls='--',zorder=30)
ax_LXsum.plot(lM200c_Akino,np.log10(LX500_hi_Akino), color='k', lw = 1, alpha=1.0, ls='--',zorder=30)

Voit_surveys = ["COS-Halos-SF", "COS-Halos-Q", "COS-LRG", "COS-GTO-SF", "COS-GTO-Q"]
Voit_symbols = ['s', 'D', '*','P','X']


for k in range(len(Voit_surveys)):
    #Rproj_Voit,logU_Voit, logUhi_Voit, logUlo_Voit, lM200c_Voit, lM200c_errpos_Voit, lM200c_errneg_Voit, redshift_Voit = data.Voit_LogU(Voit_surveys[k])
    Rproj_Voit,logP_v2_Voit, logPhi_v2_Voit, logPlo_v2_Voit, lM200c_Voit, lM200c_errpos_Voit, lM200c_errneg_Voit, redshift_Voit, passive_Voit = data.Voit_LogP(Voit_surveys[k])  

    R200c_Voit = myutils.R200c_from_lM200c(lM200c_Voit, redshift_Voit)
    R200c_errpos_Voit = myutils.R200c_from_lM200c(lM200c_Voit+lM200c_errpos_Voit, redshift_Voit)
    R200c_errneg_Voit = myutils.R200c_from_lM200c(lM200c_Voit-lM200c_errneg_Voit, redshift_Voit)

    R200frac_Voit = Rproj_Voit/R200c_Voit

    R200frac_Voit = Rproj_Voit/R200c_Voit
    R200frac_errpos_Voit = Rproj_Voit/R200c_errpos_Voit
    R200frac_errneg_Voit = Rproj_Voit/R200c_errneg_Voit

    colour_Voit=cm((lM200c_Voit-cmlo)/(cmhi-cmlo))
    colour_errpos_Voit = cm((lM200c_Voit+lM200c_errpos_Voit-cmlo)/(cmhi-cmlo))
    colour_errneg_Voit = cm((lM200c_Voit-lM200c_errneg_Voit-cmlo)/(cmhi-cmlo))

    for i in range(len(Rproj_Voit)):
        #logP = data.Voit_logU_to_logP(logU_Voit[i],redshift_Voit[i])
        #logPlo = data.Voit_logU_to_logP(logUhi_Voit[i],redshift_Voit[i])
        #logPhi = data.Voit_logU_to_logP(logUlo_Voit[i],redshift_Voit[i])

        if(i==0): 
            ax_Phot_all.errorbar(R200frac_Voit[i], logP_v2_Voit[i], lw=1,ls='',fmt=Voit_symbols[k],color=colour_Voit[i],zorder=30, label="%s"%Voit_surveys[k])
        else:
            ax_Phot_all.errorbar(R200frac_Voit[i], logP_v2_Voit[i], lw=1,ls='',fmt=Voit_symbols[k],color=colour_Voit[i],zorder=30)
        #ax_Phot_all.arrow(R200frac_Voit[i], logP, 0.15*R200frac_Voit[i], 0.0, color=colour_Voit[i],width=0.02,head_width=0.1,head_length=0.05*R200frac_Voit[i],zorder=30)

        #print("R200frac_Voit med,max,min, logP, logM med,max,min= ",R200frac_Voit[i],R200frac_errpos_Voit[i],R200frac_errneg_Voit[i],logP_v2_Voit[i],lM200c_Voit[i]+lM200c_errpos_Voit[i],lM200c_Voit[i]-lM200c_errneg_Voit[i])
        ax_Phot_all.errorbar(R200frac_Voit[i], logP_v2_Voit[i], xerr=[[R200frac_Voit[i]-R200frac_errpos_Voit[i]],[0]],lw=1,ls='',color=colour_errpos_Voit[i],zorder=30)
        #ax_Phot_all.errorbar(R200frac_Voit[i], logP_v2_Voit[i], xerr=[[0],[R200frac_errneg_Voit[i]-R200frac_Voit[i]]],lw=1,ls='',color=colour_errneg_Voit[i],zorder=30)
        ax_Phot_all.arrow(R200frac_Voit[i], logP_v2_Voit[i], R200frac_errneg_Voit[i]-R200frac_Voit[i], 0.0, color=colour_errneg_Voit[i],width=0.01,head_width=0.1,head_length=0.05*R200frac_Voit[i],zorder=30)


Rproj_P17,lognH_P17, lognHlo_P17, lognHhi_P17, lM200c_P17, lM200c_errpos_P17, lM200c_errneg_P17, redshift_P17 = data.Prochaska_2017_Densities()

lognH_P17 = [] # Effectively does not plot Prochaska because it is now combined with Voit+19 9/5/24

#lM200c_P17 = np.where(lM200c_P17>13.3,13.3,lM200c_P17)  # Upper limit.  # Taken out as of 8/10/24

R200c_P17 = myutils.R200c_from_lM200c(lM200c_P17, redshift_P17)
R200c_errpos_P17 = myutils.R200c_from_lM200c(lM200c_P17+lM200c_errpos_P17, redshift_P17)
R200c_errneg_P17 = myutils.R200c_from_lM200c(lM200c_P17-lM200c_errneg_P17, redshift_P17)

R200frac_P17 = Rproj_P17/R200c_P17
R200frac_errpos_P17 = Rproj_P17/R200c_errpos_P17
R200frac_errneg_P17 = Rproj_P17/R200c_errneg_P17

colour_P17=cm((lM200c_P17-cmlo)/(cmhi-cmlo))
colour_errpos_P17 = cm((lM200c_P17+lM200c_errpos_P17-cmlo)/(cmhi-cmlo))
colour_errneg_P17 = cm((lM200c_P17-lM200c_errneg_P17-cmlo)/(cmhi-cmlo))

for i in range(len(lognH_P17)):
    logP = data.Voit_lognH_to_logP(lognH_P17[i],redshift_P17[i])
    logPlo = data.Voit_lognH_to_logP(lognHhi_P17[i],redshift_P17[i])
    logPhi = data.Voit_lognH_to_logP(lognHlo_P17[i],redshift_P17[i])

    if(i==0): 
        ax_Phot_all.errorbar(R200frac_P17[i], logP, lw=1,ls='',fmt='o',color=colour_P17[i],zorder=30,label="COS-Halos")
    else:
        ax_Phot_all.errorbar(R200frac_P17[i], logP, lw=1,ls='',fmt='o',color=colour_P17[i],zorder=30)
    #ax_Phot_all.arrow(R200frac_P17[i], logP, 0.15*R200frac_P17[i], 0.0, color=colour_P17[i],width=0.02,head_width=0.1,head_length=0.05*R200frac_P17[i],zorder=30)
    ax_Phot_all.errorbar(R200frac_P17[i], logP, xerr=[[R200frac_P17[i]-R200frac_errpos_P17[i]],[0]],lw=1,ls='',color=colour_errpos_P17[i],zorder=30)    
    #ax_Phot_all.errorbar(R200frac_P17[i], logP, xerr=[[0],[R200frac_errneg_P17[i]-R200frac_P17[i]]],lw=1,ls='',color=colour_errneg_P17[i],zorder=30)
    ax_Phot_all.arrow(R200frac_P17[i], logP, R200frac_errneg_P17[i]-R200frac_P17[i], 0.0, color=colour_errneg_P17[i],width=0.01,head_width=0.1,head_length=0.05*R200frac_P17[i],zorder=30)

    
T22_surveys = ["COS-Halos","CGM^2","COS-LRG","COS-GTO-17","COS-GTO-18","eCGM","RDR","QSAGE","Johnson+2017"]
T22_symbols = ['s','o','*','P','X','p','h','8','d']

for k in range(len(T22_surveys)):
    #Rproj_T22, R200c_T22, lNOVI_T22, OVIflag_T22, lMStar_T22, redshift_T22 = data.Tchernyshyov_2022_NOVI(T22_surveys[i])
    #lM200c_T22 = myutils.lM200c_from_R200c(R200c_T22,redshift_T22)

    Rproj_T22, R200c_T22, lNOVI_T22, OVIflag_T22, lM200c_T22, lM200c_errpos_T22, lM200c_errneg_T22, redshift_T22, galaxy_type_T22 = data.Tchernyshyov_2022_NOVI(T22_surveys[k])

    R200c_T22_given = R200c_T22 # Now deriving R200c_T22 ourselves from stellar mass.  
    
    R200c_T22 = myutils.R200c_from_lM200c(lM200c_T22, redshift_T22)
    R200c_errpos_T22 = myutils.R200c_from_lM200c(lM200c_T22+lM200c_errpos_T22, redshift_T22)
    R200c_errneg_T22 = myutils.R200c_from_lM200c(lM200c_T22-lM200c_errneg_T22, redshift_T22)

    R200frac_T22 = Rproj_T22/R200c_T22
    R200frac_errpos_T22 = Rproj_T22/R200c_errpos_T22
    R200frac_errneg_T22 = Rproj_T22/R200c_errneg_T22

    colour_T22=cm((lM200c_T22-cmlo)/(cmhi-cmlo))
    colour_errpos_T22 = cm((lM200c_T22+lM200c_errpos_T22-cmlo)/(cmhi-cmlo))
    colour_errneg_T22 = cm((lM200c_T22-lM200c_errneg_T22-cmlo)/(cmhi-cmlo))
    
    #colour_T22 = cm((lM200c_T22-cmlo)/(cmhi-cmlo))
    legend_done = 0
    for i in range(len(Rproj_T22)):
        if(lM200c_T22[i]<11.5): continue # Do not plot below lM200c = 11.5
        if(legend_done==0):
            if(OVIflag_T22[i]==0):
                legend_done = 1
                ax_NOVI_all.plot(Rproj_T22[i]/R200c_T22[i], lNOVI_T22[i], color=colour_T22[i], lw=1, ls='', marker=T22_symbols[k],zorder=30,label=T22_surveys[k])
            else:
                ax_NOVI_all.plot(Rproj_T22[i]/R200c_T22[i], lNOVI_T22[i], color=colour_T22[i], lw=1, ls='', marker=T22_symbols[k], fillstyle="none",zorder=30)

        else:
            if(OVIflag_T22[i]==0):
                ax_NOVI_all.plot(Rproj_T22[i]/R200c_T22[i], lNOVI_T22[i], color=colour_T22[i], lw=1, ls='', marker=T22_symbols[k],zorder=30) 
            else:
                ax_NOVI_all.plot(Rproj_T22[i]/R200c_T22[i], lNOVI_T22[i], color=colour_T22[i], lw=1, ls='', marker=T22_symbols[k], fillstyle="none",zorder=30)

        ax_NOVI_all.errorbar(R200frac_T22[i], lNOVI_T22[i], xerr=[[R200frac_T22[i]-R200frac_errpos_T22[i]],[0]],lw=1,ls='',color=colour_errpos_T22[i],zorder=30)
        ax_NOVI_all.errorbar(R200frac_T22[i], lNOVI_T22[i], xerr=[[0],[R200frac_errneg_T22[i]-R200frac_T22[i]]],lw=1,ls='',color=colour_errneg_T22[i],zorder=30)
        #print("R200c_T22_given, R200c_T22, R200c_T22/R200c_T22_given= ",R200c_T22_given[i], R200c_T22[i], R200c_T22[i]/R200c_T22_given[i],i,j)
    
R_200c = 10**(np.linspace(-2.0,0.0,21))
R_500c = myutils.fR200c_to_fR500c(R_200c,10**15.0,redshift[0]) # XXXX NOTE this redshift is from the loop, but outside of it.
ax_Khot_norm.plot(R_200c, np.log10(1.32/1.09 * (R_500c)**1.1),color="gray",lw=2,ls=":",label="Voit+ (2005)")

fbar = myc.Omegab/myc.OmegaM
ax_fgas.plot([10.0,16.0],[fbar,fbar],color="gray",lw=2,ls="--")

lRlow = -1.5
lRhigh = 1.4

#modellegend = ax_Phot_all.legend(modellabel_object, modellabel_array, loc='upper right',fontsize=16)
#fig_Phot_all.gca().add_artist(modellegend)

#halolegend = ax_Phot_all.legend(halolabel_object, halolabel_array, loc='center right',fontsize=16)
#fig_Phot_all.gca().add_artist(halolegend)

label_array = []
label_array.extend(halolabel_array)
label_array.extend(modellabel_array)
label_object = []
label_object.extend(halolabel_object)
label_object.extend(modellabel_object)

#halolabel_array.extend(["Inside $R_{500}$","Inside $R_{200}$"])
#halolabel_object.extend([ax_intkSZ_all.plot(1e+99,1e+99,marker='o',fill="none",color='k',ls='',ms=15),ax_intkSZ_all.plot(1e+99,1e+99,marker='o',color='k',ls='',ms=15)])

label_point_array = []
label_point_array.extend(modellabel_array)
label_point_object = []
label_point_object.extend(modellabel_pointobject)

label_fgas_array = []
#label_fgas_array.extend(["Inside $R_{500}$","Inside $R_{200}$"])
label_fgas_array.extend(label_point_array)
label_fgas_object = []
#label_fgas_object.extend(ax_intkSZ_all.plot(1e+99,1e+99,marker='o',fillstyle="none",color='k',ls='',ms=15))
#label_fgas_object.extend(ax_intkSZ_all.plot(1e+99,1e+99,marker='o',color='k',ls='',ms=15))
label_fgas_object.extend(label_point_object)

#label_fgas_array = label_point_array
#label_fgas_array.extend(["Inside $R_{500}$","Inside $R_{200}$"])
#label_fgas_object = label_point_object
#label_fgas_object.extend(ax_intkSZ_all.plot(1e+99,1e+99,marker='o',fillstyle="none",color='k',ls='',ms=15))
#label_fgas_object.extend(ax_intkSZ_all.plot(1e+99,1e+99,marker='o',color='k',ls='',ms=15))

#label_fgas_array = []
#label_fgas_array.extend(modellabel_array)
#label_fgas_array.extend(["Inside $R_{500}$","Inside $R_{200}$"])
#label_fgas_object = []        
#label_fgas_object.extend(modellabel_pointobject) 
#label_fgas_object.extend(ax_intkSZ_all.plot(1e+99,1e+99,marker='o',fillstyle="none",color='k',ls='',ms=15))
#label_fgas_object.extend(ax_intkSZ_all.plot(1e+99,1e+99,marker='o',color='k',ls='',ms=15))

lM200c_plotR500c_frac = [13.5] #[12.0,13.5,15.0]
fR500c = np.zeros(len(lM200c_plotR500c_frac))
for i in range(len(lM200c_plotR500c_frac)):
    fR500c[i] = myutils.fR500c_to_fR200c(1.0,10**lM200c_plotR500c_frac[i],redshift[0])

file_output_type = ".png"


ax_Phot_all.set_xscale('log')
ax_Phot_all.set_xlim(10**lRlow,10**lRhigh)
ylo = -0.5
yhi = 6.0
ax_Phot_all.set_ylim(ylo,yhi)
ax_Phot_all.set_xticks([0.03,0.1,0.3,1.0,2.0])
ax_Phot_all.get_xaxis().set_major_formatter(mpl.ticker.ScalarFormatter())
ax_Phot_all.set_xlabel('$r/R_{200}$',fontsize=24)
ax_Phot_all.set_ylabel('log $P$ $E(z)^{-8/3}$ [cm$^{-3}$ K]',fontsize=24)
ax_Phot_all.plot([1,1],[-10,100],color='k',lw=1,ls=':')
#ax_Phot_all.text(0.90,(yhi-ylo)*0.95+ylo,r"$R_{200}$",rotation=90,color='black')
for i in range(len(lM200c_plotR500c_frac)):
    ax_Phot_all.plot([fR500c[i],fR500c[i]],[-10,100],lw=1,ls=':',color='gray')#,color=cm((lM200c_plotR500c_frac[i]-cmlo)/(cmhi-cmlo)))
    ax_Phot_all.text(fR500c[i]-0.08,(yhi-ylo)*0.95+ylo,r"$R_{500}$",rotation=90,color='gray')
legend = ax_Phot_all.legend(label_object, label_array, loc='upper right',fontsize=16)
fig_Phot_all.gca().add_artist(legend)
ax_Phot_all.legend(loc="lower right", ncol=1,fontsize=16)
fig_Phot_all.subplots_adjust(left=0.14, bottom=0.13,top=0.98,right=0.98)
fig_Phot_all.savefig(PlotDir + 'P_hot_all.' + lsfilename + file_output_type)

ax_Phot_norm.set_xscale('log')
ax_Phot_norm.set_xlim(10**lRlow,10**lRhigh)
ylo = -3.0
yhi = 2.0
ax_Phot_norm.set_ylim(ylo,yhi)
ax_Phot_norm.set_xticks([0.03,0.1,0.3,1.0,2.0])
ax_Phot_norm.get_xaxis().set_major_formatter(mpl.ticker.ScalarFormatter())
ax_Phot_norm.set_xlabel('$r/R_{200}$',fontsize=24)
ax_Phot_norm.set_ylabel('log $P/P_{500}$',fontsize=24)
ax_Phot_norm.plot([1,1],[-10,100],color='k',lw=1,ls=':')
for i in range(len(lM200c_plotR500c_frac)):
    ax_Phot_norm.plot([fR500c[i],fR500c[i]],[-10,100],lw=1,ls=':',color='gray')#,color=cm((lM200c_plotR500c_frac[i]-cmlo)/(cmhi-cmlo)))
    ax_Phot_norm.text(fR500c[i]-0.08,(yhi-ylo)*0.95+ylo,r"$R_{500}$",rotation=90,color='gray')
#ax_Phot_norm.plot([-10,100],[0,0],color='k',lw=1,ls=':')
if(docolorbar):
    cax = fig_Phot_norm.add_axes([0.85,0.42,0.03,0.52])
    sm = plt.cm.ScalarMappable(cmap=cm, norm=mpl.colors.Normalize(vmin=cmlo, vmax=cmhi))
    cb = fig_Phot_norm.colorbar(sm,cax=cax)
    cb.ax.tick_params(labelsize=16)
    cb.ax.set_ylabel(r'log $M_{200}/{\rm M_{\odot}}$',labelpad=4,fontsize=16)
else:
    legend = ax_Phot_norm.legend(label_object, label_array, loc='upper right',fontsize=16)
    fig_Phot_norm.gca().add_artist(legend)    
ax_Phot_norm.legend(loc="lower right", ncol=1,fontsize=16)
fig_Phot_norm.subplots_adjust(left=0.14, bottom=0.13,top=0.98,right=0.98)
fig_Phot_norm.savefig(PlotDir + 'P_hot_norm.' + lsfilename + file_output_type)

ax_nehot_norm.set_xscale('log')
ax_nehot_norm.set_xlim(10**lRlow,10**lRhigh)
ylo = -5.0
yhi = -1.5
ax_nehot_norm.set_ylim(ylo,yhi)
ax_nehot_norm.set_xticks([0.03,0.1,0.3,1.0,2.0])
ax_nehot_norm.get_xaxis().set_major_formatter(mpl.ticker.ScalarFormatter())
ax_nehot_norm.set_xlabel('$r/R_{200}$',fontsize=24)
ax_nehot_norm.set_ylabel('log $n_\mathrm{e}$ $E(z)^{-2}$ [cm$^{-3}$]',fontsize=24)
ax_nehot_norm.plot([1,1],[-10,100],color='k',lw=1,ls=':')
for i in range(len(lM200c_plotR500c_frac)):
    ax_nehot_norm.plot([fR500c[i],fR500c[i]],[-10,100],lw=1,ls=':',color='gray')#,color=cm((lM200c_plotR500c_frac[i]-cmlo)/(cmhi-cmlo)))
    ax_nehot_norm.text(fR500c[i]-0.08,(yhi-ylo)*0.95+ylo,r"$R_{500}$",rotation=90,color='gray')
if(docolorbar):    
    cax = fig_nehot_norm.add_axes([0.85,0.42,0.03,0.52]) 
    sm = plt.cm.ScalarMappable(cmap=cm, norm=mpl.colors.Normalize(vmin=cmlo, vmax=cmhi))
    cb = fig_nehot_norm.colorbar(sm,cax=cax)
    cb.ax.tick_params(labelsize=16)
    cb.ax.set_ylabel(r'log $M_{200}/{\rm M_{\odot}}$',labelpad=4,fontsize=16)
else:
    legend = ax_nehot_norm.legend(label_object, label_array, loc='upper right',fontsize=16)
    fig_nehot_norm.gca().add_artist(legend)
ax_nehot_norm.legend(loc="lower right", ncol=1,fontsize=16)
fig_nehot_norm.subplots_adjust(left=0.14, bottom=0.13,top=0.98,right=0.98)
fig_nehot_norm.savefig(PlotDir + 'ne_hot_norm.' + lsfilename + file_output_type)

ax_nehot_all.set_xscale('log')
ax_nehot_all.set_xlim(10**lRlow,10**lRhigh)
ylo = -5.0
yhi = 4.0
ax_nehot_all.set_ylim(ylo,yhi)
ax_nehot_all.set_xticks([0.03,0.1,0.3,1.0,2.0])
ax_nehot_all.get_xaxis().set_major_formatter(mpl.ticker.ScalarFormatter())
ax_nehot_all.set_xlabel('$r/R_{200}$',fontsize=24)
ax_nehot_all.set_ylabel(r'log $n_\mathrm{e} \times M_{200}/10^{12}$ $E(z)^{-2}$ [cm$^{-3}$]',fontsize=24)
###ax_nehot_all.set_ylabel(r'log $n_\mathrm{e}$ [cm$^{-3}$]',fontsize=24)
ax_nehot_all.plot([1,1],[-10,100],color='k',lw=1,ls=':')
for i in range(len(lM200c_plotR500c_frac)):
    ax_nehot_all.plot([fR500c[i],fR500c[i]],[-10,100],lw=1,ls=':',color='gray')#,color=cm((lM200c_plotR500c_frac[i]-cmlo)/(cmhi-cmlo)))
    ax_nehot_all.text(fR500c[i]-0.08,(yhi-ylo)*0.95+ylo,r"$R_{500}$",rotation=90,color='gray')
legend = ax_nehot_all.legend(label_object, label_array, loc='upper right',fontsize=16)
fig_nehot_all.gca().add_artist(legend)
ax_nehot_all.legend(loc="lower right", ncol=1,fontsize=16)
fig_nehot_all.subplots_adjust(left=0.14, bottom=0.13,top=0.98,right=0.98)
fig_nehot_all.savefig(PlotDir + 'ne_hot_all.' + lsfilename + file_output_type)

ax_Khot_norm.set_xscale('log')
ax_Khot_norm.set_xlim(10**lRlow,10**lRhigh)
ylo = -1.5
yhi = 1.2
ax_Khot_norm.set_ylim(ylo,yhi)
ax_Khot_norm.set_xticks([0.03,0.1,0.3,1.0,2.0])
ax_Khot_norm.get_xaxis().set_major_formatter(mpl.ticker.ScalarFormatter())
ax_Khot_norm.set_xlabel('$r/R_{200}$',fontsize=24)
ax_Khot_norm.set_ylabel('log $K/K_{500}$',fontsize=24)
ax_Khot_norm.plot([1,1],[-10,100],color='k',lw=1,ls=':')
for i in range(len(lM200c_plotR500c_frac)):
    ax_Khot_norm.plot([fR500c[i],fR500c[i]],[-10,100],lw=1,ls=':',color='gray')#,color=cm((lM200c_plotR500c_frac[i]-cmlo)/(cmhi-cmlo)))
    ax_Khot_norm.text(fR500c[i]-0.08,(yhi-ylo)*0.95+ylo,r"$R_{500}$",rotation=90,color='gray')
#ax_Khot_norm.plot([-10,100],[0,0],color='k',lw=1,ls=':')
legend = ax_Khot_norm.legend(label_object, label_array, loc='upper right',fontsize=16)
fig_Khot_norm.gca().add_artist(legend)
ax_Khot_norm.legend(loc="lower right", ncol=1,fontsize=16)
fig_Khot_norm.subplots_adjust(left=0.14, bottom=0.13,top=0.98,right=0.98)
fig_Khot_norm.savefig(PlotDir + 'K_hot_norm.' + lsfilename + file_output_type)


ax_Mcumhot_all.set_xscale('log')
ax_Mcumhot_all.set_xlim(10**lRlow,10**lRhigh)
ylo = 0
yhi = 0.25
ax_Mcumhot_all.set_ylim(ylo,yhi)
ax_Mcumhot_all.set_xticks([0.03,0.1,0.3,1.0,2.0])
ax_Mcumhot_all.get_xaxis().set_major_formatter(mpl.ticker.ScalarFormatter())
ax_Mcumhot_all.set_xlabel('$r/R_{200}$',fontsize=24)
ax_Mcumhot_all.set_ylabel(r'$M_\mathrm{gas}(<r)/M_{200}$',fontsize=24)
ax_Mcumhot_all.plot([1,1],[-10,100],color='k',lw=1,ls=':')
for i in range(len(lM200c_plotR500c_frac)):
    ax_Mcumhot_all.plot([fR500c[i],fR500c[i]],[-10,100],lw=1,ls=':',color='gray')#,color=cm((lM200c_plotR500c_frac[i]-cmlo)/(cmhi-cmlo)))
    ax_Mcumhot_all.text(fR500c[i]-0.08,(yhi-ylo)*0.95+ylo,r"$R_{500}$",rotation=90,color='gray')
ax_Mcumhot_all.plot([-10,100],[0.16,0.16],color='gray',lw=2,ls='--')
legend = ax_Mcumhot_all.legend(label_object, label_array, loc='upper right',fontsize=16)
fig_Mcumhot_all.gca().add_artist(legend)
ax_Mcumhot_all.legend(loc="lower right", ncol=1,fontsize=16)
fig_Mcumhot_all.subplots_adjust(left=0.14, bottom=0.13,top=0.98,right=0.98)
fig_Mcumhot_all.savefig(PlotDir + 'Mcum_hot_all.' + lsfilename + file_output_type)

ax_Zhot_all.set_xscale('log')
ax_Zhot_all.set_xlim(10**lRlow,10**lRhigh)
ylo = -1.2
yhi = 0.0
ax_Zhot_all.set_ylim(ylo,yhi)
ax_Zhot_all.set_xticks([0.03,0.1,0.3,1.0,2.0])
ax_Zhot_all.get_xaxis().set_major_formatter(mpl.ticker.ScalarFormatter())
ax_Zhot_all.set_xlabel('$r/R_{200}$',fontsize=24)
ax_Zhot_all.set_ylabel(r'log $Z/Z_{\odot}$',fontsize=24)
ax_Zhot_all.plot([1,1],[-10,100],color='k',lw=1,ls=':')
for i in range(len(lM200c_plotR500c_frac)):
    ax_Zhot_all.plot([fR500c[i],fR500c[i]],[-10,100],lw=1,ls=':',color='gray')#,color=cm((lM200c_plotR500c_frac[i]-cmlo)/(cmhi-cmlo)))
    ax_Zhot_all.text(fR500c[i]-0.08,(yhi-ylo)*0.95+ylo,r"$R_{500}$",rotation=90,color='gray')
legend = ax_Zhot_all.legend(label_object, label_array, loc='upper right',fontsize=16)
fig_Zhot_all.gca().add_artist(legend)
ax_Zhot_all.legend(loc="lower right", ncol=1,fontsize=16)
fig_Zhot_all.subplots_adjust(left=0.14, bottom=0.13,top=0.98,right=0.98)
fig_Zhot_all.savefig(PlotDir + 'Z_hot_all.' + lsfilename + file_output_type)

ax_Thot_all.set_xscale('log')
ax_Thot_all.set_xlim(10**lRlow,10**lRhigh)
ylo = 4.0
yhi = 8.0
ax_Thot_all.set_ylim(ylo,yhi)
ax_Thot_all.set_xticks([0.03,0.1,0.3,1.0,2.0])
ax_Thot_all.get_xaxis().set_major_formatter(mpl.ticker.ScalarFormatter())
ax_Thot_all.set_xlabel('$r/R_{200}$',fontsize=24)
ax_Thot_all.set_ylabel('log $T$ $E(z)^{-2/3}$ [K]',fontsize=24)
ax_Thot_all.plot([1,1],[-10,100],color='k',lw=1,ls=':')
for i in range(len(lM200c_plotR500c_frac)):
    ax_Thot_all.plot([fR500c[i],fR500c[i]],[-10,100],lw=1,ls=':',color='gray')#,color=cm((lM200c_plotR500c_frac[i]-cmlo)/(cmhi-cmlo)))
    ax_Thot_all.text(fR500c[i]-0.08,(yhi-ylo)*0.95+ylo,r"$R_{500}$",rotation=90,color='gray')
legend = ax_Thot_all.legend(label_object, label_array, loc='upper right',fontsize=16)
fig_Thot_all.gca().add_artist(legend)
#ax_Thot_all.legend(loc="lower right", ncol=1,fontsize=16)
fig_Thot_all.subplots_adjust(left=0.14, bottom=0.13,top=0.98,right=0.98)
fig_Thot_all.savefig(PlotDir + 'T_hot_all.' + lsfilename + file_output_type)


ax_NOVI_all.set_xscale('log')
ax_NOVI_all.set_xlim(10**lRlow,10**lRhigh)
ylo = 12.0
yhi = 17.0
ax_NOVI_all.set_ylim(ylo,yhi)
ax_NOVI_all.set_xticks([0.03,0.1,0.3,1.0,2.0])
ax_NOVI_all.get_xaxis().set_major_formatter(mpl.ticker.ScalarFormatter())
ax_NOVI_all.set_xlabel('$r_{\perp}/R_{200}$',fontsize=24)
ax_NOVI_all.set_ylabel('log $N_{OVI}$ [cm$^{-2}$]',fontsize=24)
legend = ax_NOVI_all.legend(label_object, label_array, loc='upper right',fontsize=16)
fig_NOVI_all.gca().add_artist(legend)
ax_NOVI_all.legend(loc="lower right", ncol=1,fontsize=16)
fig_NOVI_all.subplots_adjust(left=0.14, bottom=0.13,top=0.98,right=0.98)
fig_NOVI_all.savefig(PlotDir + 'NOVI_all.' + lsfilename + file_output_type)

ax_NOVII_all.set_xscale('log')
ax_NOVII_all.set_xlim(10**lRlow,10**lRhigh)
ylo = 12.0
yhi = 17.0
ax_NOVII_all.set_ylim(ylo,yhi)
ax_NOVII_all.set_xticks([0.03,0.1,0.3,1.0,2.0])
ax_NOVII_all.get_xaxis().set_major_formatter(mpl.ticker.ScalarFormatter())
ax_NOVII_all.set_xlabel('$r_{\perp}/R_{200}$',fontsize=24)
ax_NOVII_all.set_ylabel('log $N_{OVII}$ [cm$^{-2}$]',fontsize=24)
legend = ax_NOVII_all.legend(label_object, label_array, loc='upper right',fontsize=16)
fig_NOVII_all.gca().add_artist(legend)
#ax_NOVII_all.legend(loc="center right", ncol=1,fontsize=16)
fig_NOVII_all.subplots_adjust(left=0.14, bottom=0.13,top=0.98,right=0.98)
fig_NOVII_all.savefig(PlotDir + 'NOVII_all.' + lsfilename + file_output_type)

ax_NOVIII_all.set_xscale('log')
ax_NOVIII_all.set_xlim(10**lRlow,10**lRhigh)
ylo = 12.0
yhi = 17.0
ax_NOVIII_all.set_ylim(ylo,yhi)
ax_NOVIII_all.set_xticks([0.03,0.1,0.3,1.0,2.0])
ax_NOVIII_all.get_xaxis().set_major_formatter(mpl.ticker.ScalarFormatter())
ax_NOVIII_all.set_xlabel('$r_{\perp}/R_{200}$',fontsize=24)
ax_NOVIII_all.set_ylabel('log $N_{OVIII}$ [cm$^{-2}$]',fontsize=24)
legend = ax_NOVIII_all.legend(label_object, label_array, loc='upper right',fontsize=16)
fig_NOVIII_all.gca().add_artist(legend)
#ax_NOVIII_all.legend(loc="center right", ncol=1,fontsize=16)
fig_NOVIII_all.subplots_adjust(left=0.14, bottom=0.13,top=0.98,right=0.98)
fig_NOVIII_all.savefig(PlotDir + 'NOVIII_all.' + lsfilename + file_output_type)

ax_ySZ_all.set_xscale('log')
ax_ySZ_all.set_xlim(10**lRlow,10**lRhigh)
ylo = -10.0
yhi = -4.0
ax_ySZ_all.set_ylim(ylo,yhi)
ax_ySZ_all.set_xticks([0.03,0.1,0.3,1.0,2.0])
ax_ySZ_all.get_xaxis().set_major_formatter(mpl.ticker.ScalarFormatter())
ax_ySZ_all.set_xlabel('$r_{\perp}/R_{200}$',fontsize=24)
ax_ySZ_all.set_ylabel('log $y$ $E(z)^{-2}$ [unitless]',fontsize=24)
legend = ax_ySZ_all.legend(label_object, label_array, loc='upper right',fontsize=16)
fig_ySZ_all.gca().add_artist(legend)
ax_ySZ_all.legend(loc="lower right", ncol=1,fontsize=16)
fig_ySZ_all.subplots_adjust(left=0.14, bottom=0.13,top=0.98,right=0.98)
fig_ySZ_all.savefig(PlotDir + 'ySZ_all.' + lsfilename + file_output_type)

ax_DM_all.set_xscale('log')
ax_DM_all.set_xlim(10**lRlow,10**lRhigh)
ylo = 0.0
yhi = 4.0
ax_DM_all.set_ylim(ylo,yhi)
ax_DM_all.set_xticks([0.03,0.1,0.3,1.0,2.0])
ax_DM_all.get_xaxis().set_major_formatter(mpl.ticker.ScalarFormatter())
ax_DM_all.set_xlabel('$r_{\perp}/R_{200}$',fontsize=24)
ax_DM_all.set_ylabel('log $DM$ [pc cm$^{-3}$]',fontsize=24)
legend = ax_DM_all.legend(label_object, label_array, loc='upper right',fontsize=16)
fig_DM_all.gca().add_artist(legend)
ax_DM_all.legend(loc="lower right", ncol=1,fontsize=16)
fig_DM_all.subplots_adjust(left=0.14, bottom=0.13,top=0.98,right=0.98)
fig_DM_all.savefig(PlotDir + 'DM_all.' + lsfilename + file_output_type)

ax_intkSZ_all.set_xscale('log')
ax_intkSZ_all.set_xlim(10**lRlow,10**lRhigh)
ylo = -2.0
yhi = 6.0
ax_intkSZ_all.set_ylim(ylo,yhi)
ax_intkSZ_all.set_xticks([0.03,0.1,0.3,1.0,2.0])
ax_intkSZ_all.get_xaxis().set_major_formatter(mpl.ticker.ScalarFormatter())
ax_intkSZ_all.set_xlabel('$r_{\perp}/R_{200}$',fontsize=24)
ax_intkSZ_all.set_ylabel(r'log $\tau_\mathrm{Int}$ [kpc$^2$]',fontsize=24)
legend = ax_intkSZ_all.legend(label_object, label_array, loc='upper right',fontsize=16)
fig_intkSZ_all.gca().add_artist(legend)
#ax_intkSZ_all.legend(loc="lower right", ncol=1,fontsize=16)
fig_intkSZ_all.subplots_adjust(left=0.14, bottom=0.13,top=0.98,right=0.98)
fig_intkSZ_all.savefig(PlotDir + 'intkSZ_all.' + lsfilename + file_output_type)

ax_inttSZ_all.set_xscale('log')
ax_inttSZ_all.set_xlim(10**lRlow,10**lRhigh)
ylo = -6.0
yhi = 4.0
ax_inttSZ_all.set_ylim(ylo,yhi)
ax_inttSZ_all.set_xticks([0.03,0.1,0.3,1.0,2.0])
ax_inttSZ_all.get_xaxis().set_major_formatter(mpl.ticker.ScalarFormatter())
ax_inttSZ_all.set_xlabel('$r_{\perp}/R_{200}$',fontsize=24)
ax_inttSZ_all.set_ylabel('log $Y_\mathrm{Int}$ $E(z)^{-2/3}$ [kpc$^2$]',fontsize=24)
legend = ax_inttSZ_all.legend(label_object, label_array, loc='upper right',fontsize=16)
fig_inttSZ_all.gca().add_artist(legend)
#ax_inttSZ_all.legend(loc="lower right", ncol=1,fontsize=16)
fig_inttSZ_all.subplots_adjust(left=0.14, bottom=0.13,top=0.98,right=0.98)
fig_inttSZ_all.savefig(PlotDir + 'inttSZ_all.' + lsfilename + file_output_type)

ax_SoftXray_all.set_xscale('log')
ax_SoftXray_all.set_xlim(10**lRlow,10**lRhigh)
ylo = 34.0
yhi = 39.0
ax_SoftXray_all.set_ylim(ylo,yhi)
ax_SoftXray_all.set_xticks([0.03,0.1,0.3,1.0,2.0])
ax_SoftXray_all.get_xaxis().set_major_formatter(mpl.ticker.ScalarFormatter())
ax_SoftXray_all.set_xlabel('$r_{\perp}/R_{200}$',fontsize=24)
ax_SoftXray_all.set_ylabel('log $X_\mathrm{SB}$ [erg s$^{-1}$ kpc$^{-2}$]',fontsize=24)
legend = ax_SoftXray_all.legend(label_object, label_array, loc='upper right',fontsize=16)
fig_SoftXray_all.gca().add_artist(legend)
ax_SoftXray_all.legend(loc="lower right", ncol=1,fontsize=16)
fig_SoftXray_all.subplots_adjust(left=0.14, bottom=0.13,top=0.98,right=0.98)
fig_SoftXray_all.savefig(PlotDir + 'SoftXray_all.' + lsfilename + file_output_type)

ax_LXsum.set_xlim(11.3, 15.2)
ax_LXsum.set_ylim(38,45.6)
#ax_LXsum.get_xaxis().set_major_formatter(mpl.ticker.ScalarFormatter())
ax_LXsum.set_xlabel('log $M_{200}$ [$M_{\odot}$]',fontsize=24)
ax_LXsum.set_ylabel('log $L_X$ [erg s$^{-1}$]',fontsize=24)
legend = ax_LXsum.legend(label_point_object, label_point_array, loc='lower right',fontsize=16)
fig_LXsum.gca().add_artist(legend)
ax_LXsum.legend(loc="upper left", ncol=1,fontsize=16)
ax_LXsum.grid(color='grey', linestyle='-', linewidth=1)
fig_LXsum.subplots_adjust(left=0.14, bottom=0.13,top=0.98,right=0.98)
fig_LXsum.savefig(PlotDir + 'LXsum.' + lsfilename + file_output_type)

ax_fgas.set_xlim(11.3, 15.2)
ax_fgas.set_ylim(0.0,0.18)
#ax_fgas.get_xaxis().set_major_formatter(mpl.ticker.ScalarFormatter())
ax_fgas.set_xlabel('log $M_{200}$ [$M_{\odot}$]',fontsize=24)
ax_fgas.set_ylabel('$f_\mathrm{gas}$',fontsize=24)
legend = ax_fgas.legend(label_fgas_object, label_fgas_array, loc='lower right',fontsize=16)
fig_fgas.gca().add_artist(legend)
ax_fgas.legend(loc="center left", ncol=1,fontsize=16)
ax_fgas.grid(color='grey', linestyle='-', linewidth=1)
fig_fgas.subplots_adjust(left=0.14, bottom=0.13,top=0.98,right=0.98)
fig_fgas.savefig(PlotDir + 'fgas.' + lsfilename + file_output_type)

ax_rhoDM.set_xscale('log')
ax_rhoDM.set_xlim(10**lRlow,10**lRhigh)
ylo = -29.0
yhi = -23.5
ax_rhoDM.set_ylim(ylo,yhi)
ax_rhoDM.set_xticks([0.03,0.1,0.3,1.0,2.0])
ax_rhoDM.get_xaxis().set_major_formatter(mpl.ticker.ScalarFormatter())
ax_rhoDM.set_xlabel('$r/R_{200}$',fontsize=24)
ax_rhoDM.set_ylabel(r'log $\rho_\mathrm{DM}$ $E(z)^{-2}$ [g cm$^{-3}$]',fontsize=24)
ax_rhoDM.plot([1,1],[-100,100],color='k',lw=1,ls=':')
for i in range(len(lM200c_plotR500c_frac)):
    ax_rhoDM.plot([fR500c[i],fR500c[i]],[-100,100],lw=1,ls=':',color='gray')#,color=cm((lM200c_plotR500c_frac[i]-cmlo)/(cmhi-cmlo)))
    ax_rhoDM.text(fR500c[i]-0.08,(yhi-ylo)*0.95+ylo,r"$R_{500}$",rotation=90,color='gray')
legend = ax_rhoDM.legend(label_object, label_array, loc='upper right',fontsize=16)
fig_rhoDM.gca().add_artist(legend)
ax_rhoDM.legend(loc="lower right", ncol=1,fontsize=16)
fig_rhoDM.subplots_adjust(left=0.14, bottom=0.13,top=0.98,right=0.98)
fig_rhoDM.savefig(PlotDir + 'rhoDM.' + lsfilename + file_output_type)

