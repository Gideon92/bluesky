"""
This plugin uses an area definition to delete aircraft that exit the area. 
At deletion, flight statistics are stored used the FLSTlog.
In the area, conflicts and intrusion events are logged using CONFlogger and INTRlogger.
File name: area.py
Author: Anouk Scholtes (4139011) adapted from area.py from https://github.com/ProfHoekstra/bluesky
Date created: 09/10/2017
Date last modified: 12/10/2017
Python Version: 3.6
"""

import numpy as np
# Import the global bluesky objects. Uncomment the ones you need
from bluesky import traf, sim, stack  # , settings, navdb, traf, sim, scr, tools
from bluesky.tools import datalog, areafilter, \
    TrafficArrays, RegisterElementParameters
from bluesky import settings
from bluesky.tools import logHeaders

# Global data
area = None


### Initialization function of your plugin. Do not change the name of this
### function, as it is the way BlueSky recognises this file as a plugin.
def init_plugin():
    # Addtional initilisation code
    global area
    area = Area()

    # Configuration parameters
    config = {
        # The name of your plugin
        'plugin_name': 'AREA',

        # The type of this plugin. For now, only simulation plugins are possible.
        'plugin_type': 'sim',

        # Update interval in seconds.
        'update_interval': area.dt,

        # The update function is called after traffic is updated.
        'update': area.update,
    }

    stackfunctions = {
        "AREA": [
            "AREA Shapename/OFF or AREA lat,lon,lat,lon,[top,bottom]",
            "[float/txt,float,float,float,alt,alt]",
            area.set_area,
            "Define experiment area (area of interest)"
        ],
        "TAXI": [
            "TAXI ON/OFF : OFF auto deletes traffic below 1500 ft",
            "onoff",
            area.set_taxi,
            "Switch on/off ground/low altitude mode, prevents auto-delete at 1500 ft"
        ]
    }
    # init_plugin() should always return these two dicts.
    return config, stackfunctions


class Area(TrafficArrays):
    """ Traffic area: delete traffic when it leaves this area (so not when outside)"""

    def __init__(self):
        super(Area, self).__init__()
        # Parameters of area
        self.active = False
        self.dt = 1  # 5   # [s] frequency of area check (simtime)
        self.name = None
        self.swtaxi = False  # Default OFF: Doesn't do anything. See comments of set_taxi fucntion below.
        self.logconflist = []
        self.logintrlist = []
        self.logallconflicts = []
        self.logallintrusions = []

        # The FLST logger
        self.FLSTlogger = datalog.defineLogger('FLSTLOG', logHeaders.FLSTheader)

        with RegisterElementParameters(self):
            self.inside = np.array([], dtype=np.bool)  # In test area or not
            self.distance2D = np.array([])
            self.distance3D = np.array([])
            self.work = np.array([])
            self.fuel = np.array([])
            self.mass = np.array([])
            self.create_time = np.array([])

        self.CONFlogger = datalog.defineLogger('CONFLOG', logHeaders.CONFheader)
        self.INTRlogger = datalog.defineLogger('INTRLOG', logHeaders.INTRheader)

    def create(self, n=1):
        super(Area, self).create(n)
        self.create_time[-n:] = sim.simt

    def update(self):
        ''' Update all loggers '''
        if not self.active:
            return

        area.updateEfficiency()

        # ToDo: Add autodelete for descending with swTaxi:
        if self.swtaxi:
            pass  # To be added!!!

        # Find out which aircraft are currently inside the experiment area, and
        # determine which aircraft need to be deleted.
        inside = areafilter.checkInside(self.name, traf.lat, traf.lon, traf.alt)
        delidx = np.intersect1d(np.where(np.array(self.inside) == True), np.where(np.array(inside) == False))
        self.inside = inside

        # If aircraft are about to be deleted, remove them from the asas lists to assure logging
        if len(delidx) > 0:
            area.updateAsasLists(delidx)

        # Log created and deleted conflicts & intrusions
        area.updateCONFlog()
        area.updateINTRlog()

        # Log flight statistics of aircraft that are about to be deleted
        if len(delidx) > 0:
            area.updateFLSTlog(delidx)

        # Delete the aircraft (conversion required since names shift if multipe are deleted at once)
        delac = np.array(traf.id)[delidx]
        for ac in delac:
            traf.delete(traf.id2idx(ac))

    def set_area(self, *args):
        ''' Set Experiment Area. Aicraft leaving the experiment area are deleted.
        Input can be exisiting shape name, or a box with optional altitude constrainsts.'''

        # if all args are empty, then print out the current area status
        if not args:
            return True, "Area is currently " + ("ON" if self.active else "OFF") + \
                   "\nCurrent Area name is: " + str(self.name)

        # start by checking if the first argument is a string -> then it is an area name
        if isinstance(args[0], str) and len(args) == 1:
            if areafilter.hasArea(args[0]):
                # switch on Area, set it to the shape name
                self.name = args[0]
                self.active = True
                self.FLSTlogger.start()
                self.CONFlogger.start()
                self.INTRlogger.start()
                return True, "Area is set to " + str(self.name)
            if args[0] == 'OFF' or args[0] == 'OF':
                # switch off the area
                areafilter.deleteArea(self.name)
                self.FLSTlogger.reset()
                self.CONFlogger.reset()
                self.INTRlogger.reset()
                self.active = False
                self.name = None
                return True, "Area is switched OFF"

            # shape name is unknown
            return False, "Shapename unknown. " + \
                   "Please create shapename first or shapename is misspelled!"
        # if first argument is a float -> then make a box with the arguments
        if isinstance(args[0], (float, int)) and 4 <= len(args) <= 6:
            self.active = True
            self.name = 'DELAREA'
            areafilter.defineArea(self.name, 'BOX', args[:4], *args[4:])
            self.FLSTlogger.start()
            self.CONFlogger.start()
            self.INTRlogger.start()
            return True, "Area is ON. Area name is: " + str(self.name)

        return False, "Incorrect arguments" + \
               "\nAREA Shapename/OFF or\n Area lat,lon,lat,lon,[top,bottom]"

    def set_taxi(self, flag):
        """ If you want to delete below 1500ft,
            make an box with the bottom at 1500ft and set it to Area.
            This is because taxi does nothing. """
        self.swtaxi = flag

    def updateEfficiency(self):
        ''' Update flight efficiency metrics
            2D and 3D distance [m], and work done (force*distance) [J] '''
        resultantspd = np.sqrt(traf.gs * traf.gs + traf.vs * traf.vs)
        self.distance2D += self.dt * traf.gs
        self.distance3D += self.dt * resultantspd

        if settings.performance_model == 'nap':
            self.work += (traf.perf.thrust * self.dt * resultantspd)
        else:
            self.work += (traf.perf.Thr * self.dt * resultantspd)
            self.fuel += traf.perf.ff * self.dt
            self.mass = traf.perf.mass
            # print(self.mass)
            # print(self.fuel)


    def updateAsasLists(self, delidx):
        """ Before aircraft are actually deleted, make sure they are removed 
        from the conflict and intrusion lists already, to ensure that the end 
        of the conflict or intrusion is also logged """

        # Required to do this since asas-time is 1 second, so more than the simdt
        for idx in delidx:
            # If in conflict, remove conflict first by looping through conflicts
            for i in range(len(traf.asas.iconf[idx])):
                # Sort conf-pair
                srt = sorted(traf.asas.confpairs[traf.asas.iconf[idx][i]])
                # Entry in conflist
                entry = srt[0] + " " + srt[1]
                # Could be that the conflict-pair is already removed from list
                if entry in traf.asas.conflist_now:
                    # Remove from conflist_now
                    traf.asas.conflist_now.remove(entry)

            # If in LoSs, remove LoS first by looping through LoSs
            for i in range(len(traf.asas.ilos[idx])):
                # Sort los-pair, idx refers to confpairs!
                srt = sorted(traf.asas.confpairs[traf.asas.ilos[idx][i]])
                # Entry in conflist
                entry = srt[0] + " " + srt[1]
                # Could be that the LoS-pair is already removed from list
                if entry in traf.asas.LOSlist_now:
                    # Remove from losflist_all
                    traf.asas.LOSlist_now.remove(entry)

    def updateCONFlog(self):
        """ Register newly generated or deleted conflicts and send input to the logger"""

        createdConf = [x for x in traf.asas.conflist_now if x not in self.logconflist]
        deletedConf = [x for x in self.logconflist if x not in traf.asas.conflist_now]
        newConfs = [x for x in traf.asas.conflist_reallyall if x not in self.logallconflicts]

        # If aircraft conflict is created and deleted at the same timestep, make sure it is logged properly
        if newConfs != []:
            for newConf in newConfs:
                if newConf not in createdConf:
                    createdConf.append(newConf)
                    deletedConf.append(newConf)

        self.logconflist = traf.asas.conflist_now[:]
        self.logallconflicts = traf.asas.conflist_reallyall[:]

        # Check if there are created conflicts
        if len(createdConf) > 0:
            for confpair in createdConf:
                ac1, ac2 = confpair.split(' ')
                idx1 = traf.id2idx(ac1)
                idx2 = traf.id2idx(ac2)
                area.logConflict('CRE', idx1, idx2)

        # Check if there are deleted conflicts
        if len(deletedConf) > 0:
            for confpair in deletedConf:
                ac1, ac2 = confpair.split(' ')
                idx1 = traf.id2idx(ac1)
                idx2 = traf.id2idx(ac2)
                area.logConflict('DEL', idx1, idx2)

    def logConflict(self, eventstr, idx1, idx2):
        """ Send input to the CONFlogger """
        self.CONFlogger.log(
            np.array([eventstr]),
            np.array(traf.id)[idx1],
            np.array(traf.type)[idx1],
            self.create_time[idx1],
            traf.asas.tinconf[idx1, idx2],
            traf.asas.toutconf[idx1, idx2],
            traf.asas.tcpa[idx1, idx2],
            traf.lat[idx1],
            traf.lon[idx1],
            traf.alt[idx1],
            traf.tas[idx1],
            traf.vs[idx1],
            traf.hdg[idx1],
            traf.asas.active[idx1],
            traf.pilot.alt[idx1],
            traf.pilot.tas[idx1],
            traf.pilot.vs[idx1],
            traf.pilot.hdg[idx1],
            np.array(traf.id)[idx2],
            np.array(traf.type)[idx2],
            self.create_time[idx2],
            traf.asas.tinconf[idx2, idx1],
            traf.asas.toutconf[idx2, idx1],
            traf.asas.tcpa[idx2, idx1],
            traf.lat[idx2],
            traf.lon[idx2],
            traf.alt[idx2],
            traf.tas[idx2],
            traf.vs[idx2],
            traf.hdg[idx2],
            traf.asas.active[idx2],
            traf.pilot.alt[idx2],
            traf.pilot.tas[idx2],
            traf.pilot.vs[idx2],
            traf.pilot.hdg[idx2],
            np.array([traf.asas.confcount])
        )

    def updateINTRlog(self):
        """ Register newly generated or deleted intrusions and send input to the logger"""

        createdIntr = [x for x in traf.asas.LOSlist_now if x not in self.logintrlist]
        deletedIntr = [x for x in self.logintrlist if x not in traf.asas.LOSlist_now]
        newIntrs = [x for x in traf.asas.LOSlist_all if x not in self.logallintrusions]

        # If aircraft intrusion is created and deleted at the same timestep, make sure it is logged properly
        if newIntrs != []:
            for newIntr in newIntrs:
                if newIntr not in createdIntr:
                    createdIntr.append(newIntr)
                    deletedIntr.append(newIntr)

        self.logintrlist = traf.asas.LOSlist_now[:]
        self.logallintrusions = traf.asas.LOSlist_all[:]

        # Check if there are created intrusion
        if len(createdIntr) > 0:
            for intrpair in createdIntr:
                ac1, ac2 = intrpair.split(' ')
                idx1 = traf.id2idx(ac1)
                idx2 = traf.id2idx(ac2)
                area.logIntrusion('CRE', intrpair, idx1, idx2)

        # Check if there are deleted conflicts
        if len(deletedIntr) > 0:
            for intrpair in deletedIntr:
                ac1, ac2 = intrpair.split(' ')
                idx1 = traf.id2idx(ac1)
                idx2 = traf.id2idx(ac2)
                area.logIntrusion('DEL', intrpair, idx1, idx2)

    def logIntrusion(self, eventstr, intrpair, idx1, idx2):
        # print('Losmaxs: ', traf.asas.LOSmaxsev)
        # print('idx1: ', idx1)
        # print('acid: ', traf.id[idx1])
        """ Send input to the INTRlogger """
        self.INTRlogger.log(
            np.array([eventstr]),
            np.array(traf.id)[idx1],
            np.array(traf.type)[idx1],
            self.create_time[idx1],
            traf.asas.tinconf[idx1, idx2],
            traf.asas.toutconf[idx1, idx2],
            traf.asas.tcpa[idx1, idx2],
            traf.lat[idx1],
            traf.lon[idx1],
            traf.alt[idx1],
            traf.tas[idx1],
            traf.vs[idx1],
            traf.hdg[idx1],
            traf.asas.active[idx1],
            traf.pilot.alt[idx1],
            traf.pilot.tas[idx1],
            traf.pilot.vs[idx1],
            traf.pilot.hdg[idx1],
            np.array(traf.id)[idx2],
            np.array(traf.type)[idx2],
            self.create_time[idx2],
            traf.asas.tinconf[idx2, idx1],
            traf.asas.toutconf[idx2, idx1],
            traf.asas.tcpa[idx2, idx1],
            traf.lat[idx2],
            traf.lon[idx2],
            traf.alt[idx2],
            traf.tas[idx2],
            traf.vs[idx2],
            traf.hdg[idx2],
            traf.asas.active[idx2],
            traf.pilot.alt[idx2],
            traf.pilot.tas[idx2],
            traf.pilot.vs[idx2],
            traf.pilot.hdg[idx2],
            traf.asas.LOSmaxsev[-1],
            traf.asas.LOShmaxsev[-1],
            traf.asas.LOSvmaxsev[-1],
            np.array([traf.asas.LOScount])
        )

    def updateFLSTlog(self, delidx):
        """ Log flight statistics in the FLST logger before the aircraft is deleted """

        self.FLSTlogger.log(
            np.array(traf.id)[delidx],
            np.array(traf.type)[delidx],
            self.create_time[delidx],
            sim.simt - self.create_time[delidx],
            self.distance2D[delidx],
            self.distance3D[delidx],
            self.work[delidx],
            self.fuel[delidx],
            traf.CRElat[delidx],
            traf.CRElon[delidx],
            traf.CREalt[delidx],
            traf.lat[delidx],
            traf.lon[delidx],
            traf.alt[delidx],
            traf.tas[delidx],
            traf.vs[delidx],
            traf.hdg[delidx],
            traf.asas.active[delidx],
            traf.pilot.alt[delidx],
            traf.pilot.tas[delidx],
            traf.pilot.vs[delidx],
            traf.pilot.hdg[delidx],
            np.array([traf.asas.confcount] * len(delidx)),
            np.array([traf.asas.LOScount] * len(delidx)),
        )
