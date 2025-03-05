import h5py
import matplotlib.pyplot as plt
import numpy as np

import context

import simim.lightcone as lc
from simim._paths import _paths
from simim.galprops import galprops

def test_lightcone():
    lcgen = lc.make.lightcone('TNG100-3','test1',.25,aspect=1,redshift_max=10,mode='box')
    lcgen.build_lightcones(1,seed=24)
    lcgen.add_properties(['sfr','masscheck'])
    lcgen.add_pos_properties(['v','spin'])


def check_lightcone():
    paths = _paths()
    with h5py.File('/Users/rpkeenan/simim_resources/lightcones/TNG100-3/test1/lc_0000.hdf5','r') as file:
        m = file['Lightcone Basic']['mass'][:]
        mc = file['Lightcone Full']['masscheck'][:]

        print(m.shape,mc.shape)
        print(np.any(m != mc))
        plt.hist(np.log10(m))
        plt.hist(np.log10(mc),histtype='step',color='r')
        plt.show()

        px = file['Lightcone Basic']['pos_x'][:]
        py = file['Lightcone Basic']['pos_y'][:]
        plt.hist(px)
        plt.hist(py,histtype='step',color='r')
        plt.show()

def test_handler():
    handler = lc.handler.lightcone('TNG100-3','test1',0)
    print("All: {}".format(handler.properties_all))
    print("Saved: {}".format(handler.properties_saved))
    print("Loaded: {}".format(handler.properties_loaded.keys()))
    print("Generated: {}".format(handler.properties_generated))

    print("")
    print("Extract keys: {}".format(handler.extract_keys()))

    print("Check property - pos_x: {}".format(handler.has_property('pos_x')))
    print("Check property - sfr: {}".format(handler.has_property('sfr')))
    print("Check property - lco: {}".format(handler.has_property('lco')))

    print("")
    handler.load_property("sfr")
    handler.load_property("sfr")
    print("Loaded sfr")
    print("All: {}".format(handler.properties_all))
    print("Saved: {}".format(handler.properties_saved))
    print("Loaded: {}".format(handler.properties_loaded.keys()))
    print("Generated: {}".format(handler.properties_generated))

    handler.load_property("pos_x","pos_y","pos_z")
    print("Loaded pos")
    print("All: {}".format(handler.properties_all))
    print("Saved: {}".format(handler.properties_saved))
    print("Loaded: {}".format(handler.properties_loaded.keys()))
    print("Generated: {}".format(handler.properties_generated))

    # handler.load_property("v_w","v_x","v_y","v_z")
    # print("Loaded v")
    # print("All: {}".format(handler.properties_all))
    # print("Saved: {}".format(handler.properties_saved))
    # print("Loaded: {}".format(handler.properties_loaded.keys()))
    # print("Generated: {}".format(handler.properties_generated))

    handler.unload_property("pos_x","pos_y","pos_z")
    print("Unloaded pos")
    print("All: {}".format(handler.properties_all))
    print("Saved: {}".format(handler.properties_saved))
    print("Loaded: {}".format(handler.properties_loaded.keys()))
    print("Generated: {}".format(handler.properties_generated))

    x = handler.return_property("pos_x")
    print("Return unloaded prop: type {}, shape {}".format(type(x),x.shape))
    x = handler.return_property("sfr")
    print("Return loaded prop: type {}, shape {}".format(type(x),x.shape))

def test_handler_indexing():
    handler = lc.handler.lightcone('TNG100-3','test1',0)
    print("Indices - all: {}".format(handler.inds_all))
    print("Indices - active: {}".format(handler.inds_active))
    print("Indices - all length: {}".format(handler.inds_all.shape))
    print("Indices - active length: {}".format(handler.inds_active.shape))
    if handler.inds_active.shape == handler.inds_all.shape:
        print("Indices - are the same: {}".format(np.all(handler.inds_active==handler.inds_all)))
    else:
        print("Indices - are the same: False")

    handler.set_property_range("redshift",.1,.5,reset=True)
    print("\nset redshift")
    print("Indices - all length: {}".format(handler.inds_all.shape))
    print("Indices - active length: {}".format(handler.inds_active.shape))
    if handler.inds_active.shape == handler.inds_all.shape:
        print("Indices - are the same: {}".format(np.all(handler.inds_active==handler.inds_all)))
    else:
        print("Indices - are the same: False")

    print("\nreset")
    handler.set_property_range()
    print("Indices - all length: {}".format(handler.inds_all.shape))
    print("Indices - active length: {}".format(handler.inds_active.shape))
    if handler.inds_active.shape == handler.inds_all.shape:
        print("Indices - are the same: {}".format(np.all(handler.inds_active==handler.inds_all)))
    else:
        print("Indices - are the same: False")

    print("\nset bad redshifts")
    handler.set_property_range("redshift",.1,.5,reset=True)
    handler.set_property_range("redshift",3,4,reset=False)
    print("Indices - all length: {}".format(handler.inds_all.shape))
    print("Indices - active length: {}".format(handler.inds_active.shape))
    if handler.inds_active.shape == handler.inds_all.shape:
        print("Indices - are the same: {}".format(np.all(handler.inds_active==handler.inds_all)))
    else:
        print("Indices - are the same: False")

    print("\nset redshifts, masses, velocities")
    handler.set_property_range("redshift",.1,.5,reset=True)
    handler.set_property_range("mass",1e12,1e14,reset=False)
    handler.set_property_range("v_x",-np.inf,0,reset=False)
    print("Indices - all length: {}".format(handler.inds_all.shape))
    print("Indices - active length: {}".format(handler.inds_active.shape))
    if handler.inds_active.shape == handler.inds_all.shape:
        print("Indices - are the same: {}".format(np.all(handler.inds_active==handler.inds_all)))
    else:
        print("Indices - are the same: False")

    x = handler.return_property("redshift")
    redshift_check = np.all(((x>=.1) & (x<=.5)))
    x = handler.return_property("mass")
    mass_check = np.all(((x>=1e12) & (x<=1e14)))
    x = handler.return_property("v_x")
    vel_check = np.all(((x<=0)))
    print("Default return, acceptable redshift: {}".format(redshift_check))
    print("Default return, acceptable mass: {}".format(mass_check))
    print("Default return, acceptable velocity: {}".format(vel_check))

    x = handler.return_property("redshift",use_all_inds=True)
    # print(np.amax(x[x<1]))
    # print(np.amin(x[x>2]))
    redshift_check = np.all(((x>=.1) & (x<=.5)))
    x = handler.return_property("mass",use_all_inds=True)
    mass_check = np.all(((x>=1e12) & (x<=1e14)))
    x = handler.return_property("v_x",use_all_inds=True)
    vel_check = np.all(((x<=0)))
    print("All return, acceptable redshift: {}".format(redshift_check))
    print("All return, acceptable mass: {}".format(mass_check))
    print("All return, acceptable velocity: {}".format(vel_check))

def test_handler_plots():
    handler = lc.handler.lightcone('TNG100-3','test1',0)

    handler.plot('redshift','pos_x')

    handler.plot('redshift','pos_x',
                 axkws={'xlabel':'redshift',
                        'ylabel':'x position [Mpc/h]'},
                 plotkws={'color':'k'})

    handler.set_property_range('redshift',.1,.5)
    handler.plot('redshift','pos_x')
    handler.plot('redshift','pos_x',use_all_inds=True)
    handler.plot('redshift','pos_x',use_all_inds='compare')

    handler.set_property_range()
    handler.hist('redshift')
    handler.hist('mass')
    handler.hist('mass',logtransform=True,plotkws={'bins':np.linspace(9,15,7)})

    handler.animate()

def test_mass():
    handler = lc.handler.lightcone('TNG100-3','test1',0)

    handler.plot('redshift','mass',
                 axkws={'xlabel':'redshift',
                        'ylabel':'mass [Msun/h]',
                        'yscale':'log'},
                 plotkws={'color':'k','markersize':1})

    handler.plot('masscheck','mass',
                 axkws={'xlabel':'mass [Msun/h]',
                        'ylabel':'mass [Msun/h]',
                        'yscale':'log','xscale':'log'},
                 plotkws={'color':'k','markersize':1})

    handler.plot('redshift','spin_x',
                 axkws={'xlabel':'redshift',
                        'ylabel':'x spin'},
                 plotkws={'color':'k','markersize':1})
    handler.plot('redshift','spin_y',
                 axkws={'xlabel':'redshift',
                        'ylabel':'y spin'},
                 plotkws={'color':'k','markersize':1})
    handler.plot('redshift','spin_z',
                 axkws={'xlabel':'redshift',
                        'ylabel':'z spin'},
                 plotkws={'color':'k','markersize':1})

    handler.plot('redshift','v_x',
                 axkws={'xlabel':'redshift',
                        'ylabel':'x vel [km/s]'},
                 plotkws={'color':'k','markersize':1})
    handler.plot('redshift','v_y',
                 axkws={'xlabel':'redshift',
                        'ylabel':'y vel [km/s]'},
                 plotkws={'color':'k','markersize':1})
    handler.plot('redshift','v_z',
                 axkws={'xlabel':'redshift',
                        'ylabel':'los vel [km/s]'},
                 plotkws={'color':'k','markersize':1})

def test_handler_newprops():
    prop = galprops.prop_li_co

    handler = lc.handler.lightcone('TNG100-3','test1',0)
    print("All: {}".format(handler.properties_all))
    print("Saved: {}".format(handler.properties_saved))
    print("Loaded: {}".format(handler.properties_loaded.keys()))
    print("Generated: {}".format(handler.properties_generated))

    print("")

    print("Add LCO")
    handler.make_property(prop,overwrite=True)
    print("All: {}".format(handler.properties_all))
    print("Saved: {}".format(handler.properties_saved))
    print("Loaded: {}".format(handler.properties_loaded.keys()))
    print("Generated: {}".format(handler.properties_generated))

    print("Save LCO")
    handler.write_property('LCO',overwrite=True)
    print("All: {}".format(handler.properties_all))
    print("Saved: {}".format(handler.properties_saved))
    print("Loaded: {}".format(handler.properties_loaded.keys()))
    print("Generated: {}".format(handler.properties_generated))

    print("")
    print("New instance")
    handler = lc.handler.lightcone('TNG100-3','test1',0)
    print("All: {}".format(handler.properties_all))
    print("Saved: {}".format(handler.properties_saved))
    print("Loaded: {}".format(handler.properties_loaded.keys()))
    print("Generated: {}".format(handler.properties_generated))

    print("Delete LCO")
    handler.delete_property('LCO')
    print("All: {}".format(handler.properties_all))
    print("Saved: {}".format(handler.properties_saved))
    print("Loaded: {}".format(handler.properties_loaded.keys()))
    print("Generated: {}".format(handler.properties_generated))

    print("")
    print("New instance")
    handler = lc.handler.lightcone('TNG100-3','test1',0)
    print("All: {}".format(handler.properties_all))
    print("Saved: {}".format(handler.properties_saved))
    print("Loaded: {}".format(handler.properties_loaded.keys()))
    print("Generated: {}".format(handler.properties_generated))

def test_handler_lco_plot():
    prop = galprops.prop_li_co

    handler = lc.handler.lightcone('TNG100-3','test1',0)

    handler.make_property(prop)

    handler.plot('mass','LCO',
                 axkws={'xlabel':'Mass [Msun/h]',
                        'ylabel':'CO Luminosity [Lsun/h]',
                        'xscale':'log','yscale':'log'},
                 plotkws={'color':'k','markersize':1})

    handler.plot('sfr','LCO',
                 axkws={'xlabel':'SFR [Msun/yr]',
                        'ylabel':'CO Luminosity [Lsun/h]',
                        'xscale':'log','yscale':'log'},
                 plotkws={'color':'k','markersize':1})

def test_stats():
    def sfrmean(sfr):
        return np.mean(sfr)

    handler = lc.handler.lightcone('TNG100-3','test1',0)
    for z in [.05,.15,.25,.35,.45]:
        handler.set_property_range('redshift',z-.05,z+.05)
        print(handler.eval_stat(sfrmean,['sfr']))


# test_lightcone()
# check_lightcone()
# test_mass()
# test_handler()
# test_handler_indexing()
test_handler_plots()
# test_handler_newprops()
# test_handler_lco_plot()
# test_stats()
