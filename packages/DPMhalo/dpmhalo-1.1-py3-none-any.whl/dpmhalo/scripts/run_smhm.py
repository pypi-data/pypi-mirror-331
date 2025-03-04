import sys
from dpmhalo import smhm
from dpmhalo import myutils

if(len(sys.argv) < 4):
  print("Usage: run_smhm.py 1) log M_Star, 2) error log M_Star, 3) redshift")
  exit()

lMstar = float(sys.argv[1])
err_lMstar = float(sys.argv[2])
redshift = float(sys.argv[3])

GalType = '' # Assume general SMHM, can do '_sf' and '_q' as well.  

lM200c_smhm, lM200c_errpos_smhm, lM200c_errneg_smhm = smhm.Behroozi2019_UNIVERSEMACHINE_return_lM200c(lMstar,err_lMstar,redshift,galaxy_type_tag=GalType)
print("lM200c = %5.2f +%4.2f -%4.2f"%(lM200c_smhm, lM200c_errpos_smhm, lM200c_errneg_smhm))

R200c = myutils.R200c_from_lM200c(lM200c_smhm,redshift)
R200c_errpos = myutils.R200c_from_lM200c(lM200c_smhm+lM200c_errpos_smhm,redshift)
R200c_errneg = myutils.R200c_from_lM200c(lM200c_smhm-lM200c_errneg_smhm,redshift)
print("R200c med,hi,lo = %5.1f %5.1f %5.1f"%(R200c,R200c_errpos,R200c_errneg))
