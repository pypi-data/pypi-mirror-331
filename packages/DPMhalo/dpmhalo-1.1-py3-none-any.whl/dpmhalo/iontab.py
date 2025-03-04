import numpy as np
import trident
from astropy import constants as const
import yt
from yt.units import kpc
from dpmhalo import myconstants as myc 

class Trident:
    def __init__(self, ne, T, Z, redshift):
        self.ne = ne
        self.T = T
        self.Z = Z
        self.redshift = redshift
        
    def returnoxygenions(self,ne,T,Z,redshift): # Used to do initial z=0.0 ascii files.  
        line_list = ['O']
        density = ne/myc.ne_to_nH*const.m_p.to('g')/myc.XH
        ds = trident.utilities.make_onezone_dataset(density=density.value, temperature=T, metallicity=Z, domain_width=1.0)
        ds.current_time = 1/(1+redshift)
        ds.redshift = redshift
        print("redshift,ds.current_time= ",redshift,ds.current_time)
        trident.add_ion_fields(ds,ions=["O VI","O VII","O VIII"])

        ray = trident.make_simple_ray(ds,start_position=[0.,0.,0.],end_position=[1.,0.,0.],redshift=redshift,data_filename="ray.h5",lines=line_list)

        #trident.utilities.make_onezone_ray(density=1e-26, temperature=1000, metallicity=0.3, length=10, redshift=0, filename='ray.h5', column_densities=None)[source]

        #ray = trident.make_onezone_ray(density=density.value, temperature=T, metallicity=Z, redshift=redshift,length=1.0)
        return(ray.r[('gas', 'O_p5_number_density')],ray.r[('gas', 'O_p6_number_density')],ray.r[('gas', 'O_p7_number_density')])

    def returnoxygenions_v3(self,ne,T,Z,redshift):
        line_list = ['O']
        density = ne/myc.ne_to_nH*const.m_p.to('g')/myc.XH
        #ray = trident.make_onezone_ray(density=density.value, temperature=T, metallicity=Z, redshift=redshift,column_densities={'H_p0_number_density': 1e21})
        ray = trident.make_onezone_ray(density=density.value, temperature=T, metallicity=Z, redshift=redshift,column_densities={'O_number_density': 1e18})
        print("ray.r.__dict__= ", ray.r.__dict__)
        print("ray.r= ", ray.r)
        print("ray.r.ds= ", ray.r.ds)
        print("ray.r[('gas', 'O_p6_number_density')]= ", ray.r[('gas', 'O_p6_number_density')])

        return(ray.r[('gas', 'O_p5_number_density')],ray.r[('gas', 'O_p6_number_density')],ray.r[('gas', 'O_p7_number_density')])

    def returnoxygenions_v2(self,ne,T,Z,redshift):
        line_list = ['O']
        density = ne/myc.ne_to_nH*const.m_p.to('g')/myc.XH
        #density = ne/1.2*1.673e-24/0.75
        ds = trident.utilities.make_onezone_dataset(density=density.value, temperature=T, metallicity=Z, domain_width=1.0)
        ds.current_time = 1/(1+redshift)
        trident.add_ion_fields(ds,ions=["O VI","O VII","O VIII"])

        #ray = trident.make_simple_ray(ds,start_position=[0.,0.,0.],end_position=[1.,0.,0.],data_filename="ray.h5",redshift=redshift,lines=line_list)
        ray = trident.make_onezone_ray(density=density.value, temperature=T, metallicity=1.0,length=10,redshift=redshift,filename='ray.h5')#, column_densities={'H_p0_number_density': 1e21})
        print("ray.r.__dict__= ", ray.r.__dict__)
        print("ray.r= ", ray.r)
        print("ray.r[('gas', 'O_p6_number_density')]= ", ray.r[('gas', 'O_p6_number_density')])

        #print("ray.r[('O_p5_number_density')]= ", ray.r['O_p5_number_density'])
        #ray = trident.make_lightray(start_position=[0.,0.,0.],end_position=[1.,0.,0.],data_filename="ray.h5"
        #                            return lr.make_light_ray(start_position=start_position,
        #                                                     end_position=end_position,
        #                                                     trajectory=trajectory,
        #                                                     fields=fields,
        #                                                     setup_function=setup_function,
        #                                                     solution_filename=solution_filename,
        #                                                     data_filename=data_filename,
        #                                                     field_parameters=field_parameters,
        #                                                     redshift=redshift)

        
        
        return(ray.r[('gas', 'O_p5_number_density')],ray.r[('gas', 'O_p6_number_density')],ray.r[('gas', 'O_p7_number_density')])


    

        
    def returnoxygenions_v1(self,ne,T,Z,redshift):
        R = 1.0  # radius of cluster in kpc
        nx = 1
        ddims = (1, 1, 1)
        x, y, z = np.mgrid[-R : R : nx * 1j, -R : R : nx * 1j, -R : R : nx * 1j]
        r = np.sqrt(x**2 + y**2 + z**2)

        density = ne/myc.ne_to_nH*const.m_p.to('g')/myc.XH
        data = {}
        data["density"] = (np.ones(ddims)*density, "g/cm**3")
        data["temperature"] = (np.ones(ddims)*T, "K")
        data["metallicity"] = (np.ones(ddims)*1.0, "Zsun")
        data["velocity_x"] = (np.zeros(ddims), "cm/s")
        data["velocity_y"] = (np.zeros(ddims), "cm/s")
        data["velocity_z"] = (np.zeros(ddims), "cm/s")
        data["redshift"] = (np.ones(ddims)*redshift, "")
        data["redshift_eff"] = (np.ones(ddims)*redshift, "")
        data["current_time"] = (np.ones(ddims)*1/(1+redshift), "")

        #data["current_time"] = (np.ones(1)*1/(1+redshift), "")
        #data["nonsenes"] = (np.ones(ddims), "")
        
        L = (1.0 * R * kpc).to_value("cm")

#        data = {"density"            : yt.YTArray([density.value], "g/cm**3"),# (np.ones((1))*density, "g/cm**3"),
#                "metallicity"        : yt.YTArray(1.0, "Zsun"),
#                "dl"                 : L,
#                "temperature"        : yt.YTArray([T], "K"),
#                "redshift"           : np.array([redshift]),
#                "redshift_eff"       : np.array([redshift]),
#                "velocity_los"       : yt.YTArray([0.], "cm/s"),
#                "x": L/2, "dx": L,
#                "y": L/2, "dy": L,
#                "z": L/2, "dz": L
#        }

        
        bbox = np.array(
            [[-1.0, 1.0], [-1.0, 1.0], [-1.0, 1.0]]
        )  # The bounding box of the domain in code units
        
        ds = yt.load_uniform_grid(data, ddims, L, bbox=bbox)
        print("BOUND ONE")
        ds.current_time = 1/(1+redshift)
        ds.redshift = redshift
        ds.redshift_eff = redshift
        yt.save_as_dataset(ds, "random_data.h5", data)
        ds = yt.load("random_data.h5")

        line_list = ['O']
        density = ne/myc.ne_to_nH*const.m_p.to('g')/myc.XH
        #density = ne/1.2*1.673e-24/0.75

        trident.add_ion_fields(ds,ions=["O VI","O VII","O VIII"])

        ray = trident.make_simple_ray(ds,start_position=[0.,0.,0.],end_position=[1.,0.,0.],data_filename="ray.h5",redshift=redshift,lines=line_list)

        #ray = trident.make_lightray(start_position=[0.,0.,0.],end_position=[1.,0.,0.],data_filename="ray.h5"
        #                            return lr.make_light_ray(start_position=start_position,
        #                                                     end_position=end_position,
        #                                                     trajectory=trajectory,
        #                                                     fields=fields,
        #                                                     setup_function=setup_function,
        #                                                     solution_filename=solution_filename,
        #                                                     data_filename=data_filename,
        #                                                     field_parameters=field_parameters,
        #                                                     redshift=redshift)

        
        
        return(ray.r[('gas', 'O_p5_number_density')],ray.r[('gas', 'O_p6_number_density')],ray.r[('gas', 'O_p7_number_density')])


    

        
