# Log parameters for the flight statistics log
FLSTheader = \
    "#######################################################\r\n" + \
    "FLST LOG\r\n" + \
    "Event logging of deleted aircraft \r\n" + \
    "#######################################################\r\n\r\n" + \
    "Parameters [Units]:\r\n" + \
    "Deletion Time [s], " + \
    "Call sign [-], " + \
    "Aircraft Type [-], " + \
    "Spawn Time [s], " + \
    "Flight time [s], " + \
    "Actual Distance 2D [m], " + \
    "Actual Distance 3D [m], " + \
    "Work Done [J], " + \
    "Fuel[kg], " + \
    "Create latitude [deg], " + \
    "Create longitude [deg], " + \
    "Create altitude [m], " + \
    "Latitude [deg], " + \
    "Longitude [deg], " + \
    "Altitude [m], " + \
    "TAS [m/s], " + \
    "Vertical Speed [m/s], " + \
    "Heading [deg], " + \
    "ASAS Active [bool], " + \
    "Pilot ALT [m], " + \
    "Pilot SPD (TAS) [m/s], " + \
    "Pilot VS [m/s], "  + \
    "Pilot HDG [deg], " + \
    "Total no conflicts [-], " + \
    "Total no LOS [-], " + \
    "\r\n"

CONFheader = \
    "#######################################################\r\n" + \
    "CONF LOG \r\n" + \
    "Event logging of conflict events \r\n" + \
    "#######################################################\r\n\r\n" + \
    "Parameters [Units]:\r\n" + \
    "Logging time [s], " + \
    "Event type [-], " + \
    "Call sign ac1 [-], " + \
    "Traffic type ac1 [-], " + \
    "Spawn time ac1 [s], " + \
    "tinconf ac1 [s], " + \
    "toutconf ac1 [s], " + \
    "tcpa ac1 [s], " + \
    "Latitude ac1 [deg], " + \
    "Longitude ac1 [deg], " + \
    "Altitude ac1 [m], " + \
    "TAS ac1 [m/s], " + \
    "Vertical speed ac1 [m/s], " + \
    "Heading ac1 [deg], " + \
    "ASAS Active ac1 [bool], " + \
    "Pilot Alt ac1 [m], " + \
    "Pilot SPD (TAS) ac1 [m/s], " + \
    "Pilot VS ac1 [m/s], "  + \
    "Pilot HDG ac1 [deg], " + \
    "Call sign ac2 [-], " + \
    "Traffic type ac2 [-], " + \
    "Spawn time ac2 [s], " + \
    "tinconf ac2 [s], " + \
    "toutconf ac2 [s], " + \
    "tcpa ac2 [s], " + \
    "Latitude ac2 [deg], " + \
    "Longitude ac2 [deg], " + \
    "Altitude ac2 [m], " + \
    "TAS ac2 [m/s], " + \
    "Vertical speed ac2 [m/s], " + \
    "Heading ac2 [deg], " + \
    "ASAS Active ac2 [bool], " + \
    "Pilot Alt ac2 [m], " + \
    "Pilot SPD (TAS) ac2 [m/s], " + \
    "Pilot VS ac2 [m/s], "  + \
    "Pilot HDG ac2 [deg], " + \
    "Sum of conflicts [-], " + \
    "\r\n"

INTRheader = \
    "#######################################################\r\n" + \
    "INTR LOG \r\n" + \
    "Event logging of intrusion events \r\n" + \
    "#######################################################\r\n\r\n" + \
    "Parameters [Units]:\r\n" + \
    "Logging time [s], " + \
    "Event type [-], " + \
    "Call sign ac1 [-], " + \
    "Traffic type ac1 [-], " + \
    "Spawn time ac1 [s], " + \
    "tinconf ac1 [s], " + \
    "toutconf ac1 [s], " + \
    "tcpa ac1 [s], " + \
    "Latitude ac1 [deg], " + \
    "Longitude ac1 [deg], " + \
    "Altitude ac1 [m], " + \
    "TAS ac1 [m/s], " + \
    "Vertical speed ac1 [m/s], " + \
    "Heading ac1 [deg], " + \
    "ASAS Active ac1 [bool], " + \
    "Pilot Alt ac1 [m], " + \
    "Pilot SPD (TAS) ac1 [m/s], " + \
    "Pilot VS ac1 [m/s], "  + \
    "Pilot HDG ac1 [deg], " + \
    "Call sign ac2 [-], " + \
    "Traffic type ac2 [-], " + \
    "Spawn time ac2 [s], " + \
    "tinconf ac2 [s], " + \
    "toutconf ac2 [s], " + \
    "tcpa ac2 [s], " + \
    "Latitude ac2 [deg], " + \
    "Longitude ac2 [deg], " + \
    "Altitude ac2 [m], " + \
    "TAS ac2 [m/s], " + \
    "Vertical speed ac2 [m/s], " + \
    "Heading ac2 [deg], " + \
    "ASAS Active ac2 [bool], " + \
    "Pilot Alt ac2 [m], " + \
    "Pilot SPD (TAS) ac2 [m/s], " + \
    "Pilot VS ac2 [m/s], "  + \
    "Pilot HDG ac2 [deg], " + \
    "Max intrusion severity [-], " + \
    "Horizontal intrusion severity at max IS [-], " + \
    "Vertical intrusion severity at max IS [-], " + \
    "Sum of LOS [-], " + \
    "\r\n"
