import numpy as np
import pyxsim
import trident
import yt
from yt.units import kpc
from astropy import constants as const
from dpmhalo import myconstants as myc

class pyXSIM:
    def __init__(self, ne, T, Z, redshift):
        self.ne = ne
        self.T = T
        self.Z = Z
        self.redshift = redshift

    def returnsoftxray(self,ne,T,Z,redshift):

        R = 1.0  # radius of cluster in kpc
        nx = 1
        ddims = (1, 1, 1)
        x, y, z = np.mgrid[-R : R : nx * 1j, -R : R : nx * 1j, -R : R : nx * 1j]
        r = np.sqrt(x**2 + y**2 + z**2)
        #dens[r <= R] = rho_c * (1.0 + (r[r <= R] / r_c) ** 2) ** (-1.5 * beta)
        #dens[r > R] = 0.0
        
        #temp = (kT * keV).to_value("K", "thermal") * np.ones(ddims)

        density = ne/myc.ne_to_nH*const.m_p.to('g')/myc.XH
        print("density= ", density)
        data = {}
        data["density"] = (np.ones(ddims)*density, "g/cm**3")
        data["temperature"] = (np.ones(ddims)*T, "K")
        data["velocity_x"] = (np.zeros(ddims), "cm/s")
        data["velocity_y"] = (np.zeros(ddims), "cm/s")
        data["velocity_z"] = (np.zeros(ddims), "cm/s")
        bbox = np.array(
            [[-1.0, 1.0], [-1.0, 1.0], [-1.0, 1.0]]
        )  # The bounding box of the domain in code units

        L = (1.0 * R * kpc).to_value("cm")

        # We have to set default_species_fields="ionized" because
        # we didn't create any species fields above
        ds = yt.load_uniform_grid(data, ddims, L, bbox=bbox, default_species_fields="ionized")

        #trident.add_ion_fields(ds,ions=["O VI","O VII","O VIII"])
        #source_model = pyxsim.CIESourceModel(
        #    model='apec',
        #    emin=0.5,
        #    emax=2.0,
        #    nbins=150, # Note this is not 4000
        #    Zmet=Z, #("hot_gas", "metallicity"),
            #binscale="log",
            #resonant_scattering=True,
            #cxb_factor=0.5,
        #    kT_max=30.0#,
            #nh_field=("hot_gas", "H_nuclei_density"),
            #temperature_field=("hot_gas", "temperature"),
            #emission_measure_field=("hot_gas", "emission_measure"),
            #var_elem=var_elem            
        #    )
        source_model = pyxsim.IGMSourceModel(
            0.5,
            2.0,
            150, # Note this is not 4000
            Z#, #("hot_gas", "metallicity"),
            #binscale="log",
            #resonant_scattering=True,
            #cxb_factor=0.5,
            #kT_max=30.0#,
            #nh_field=("hot_gas", "H_nuclei_density"),
            #temperature_field=("hot_gas", "temperature"),
            #emission_measure_field=("hot_gas", "emission_measure"),
            #var_elem=var_elem            
            )

        
        xray_fields = source_model.make_source_fields(ds, 0.5, 2.0)
        #print("ds.derived_field_list[('gas', 'xray_emissivity_0.5_2.0_keV')]= ", ds.derived_field_list[('gas', 'xray_emissivity_0.5_2.0_keV')])
        print("xray_fields= ", xray_fields)
        ad = ds.all_data()
        print("xray_emissivity_0.5_2.0_keV, xray_luminosity_0.5_2.0_keV, xray_photon_emissivity_0.5_2.0_keV, xray_photon_count_rate_0.5_2.0_keV, density, temperature =", ad['gas','xray_emissivity_0.5_2.0_keV'], ad['gas','xray_luminosity_0.5_2.0_keV'], ad['gas','xray_photon_emissivity_0.5_2.0_keV'], ad['gas','xray_photon_count_rate_0.5_2.0_keV'], ad['gas','density'], ad['gas','temperature'])#, ad['gas','metallicity'])
        #print("ds.fields.gas.xray_emissivity_0.5_2.0_keV.value= ",ds[('gas', 'xray_emissivity_0.5_2.0_keV')])
        return(ad['gas', 'xray_emissivity_0.5_2.0_keV'])
