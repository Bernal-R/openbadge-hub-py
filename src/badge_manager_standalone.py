from __future__ import absolute_import, division, print_function
import os
import re
import logging

from badge import Badge,now_utc_epoch
from settings import DATA_DIR, LOG_DIR, CONFIG_DIR

devices_file = CONFIG_DIR + 'devices.txt'


class BadgeManagerStandalone():
    def __init__(self, logger,timestamp):
        self._badges= None
        self.logger = logger
        self._device_file = devices_file

        if timestamp:
            self._init_ts = timestamp
            self._init_ts_fract = 0
        else:
            self._init_ts, self._init_ts_fract = now_utc_epoch()
            self._init_ts -= 5 * 60 # start pulling data from the 5 minutes
        logger.debug("Standalone version. Will request data since {} {}".format(self._init_ts,self._init_ts_fract))

    def _read_file(self,device_file):
        """
        refreshes an internal list of devices included in device_macs.txt
        Format is device_mac<space>badge_id<space>project_id<space>device_name
        :param device_file:
        :return:
        """
        if not os.path.isfile(device_file):
            self.logger.error("Cannot find devices file: {}".format(device_file))
            exit(1)
        self.logger.info("Reading devices from file: {}".format(device_file))

        #extracting badge id, project id and mac address
        with open(device_file, 'r') as devices_macs:

            badge_project_ids =[]
            devices = []

            for line in devices_macs:
                    if not line.lstrip().startswith('#'):
                        device_details = line.split()
                        devices.append(device_details[0])
                        badge_project_ids.append(device_details[1:3])
                    
        
        #mapping badge id and project id to mac address
        mac_id_map = {}    
        for i in range(len(devices)):
            mac_id_map[devices[i]] = badge_project_ids[i]
        
        for d in devices:
            self.logger.debug("    {}".format(d))

        badges = {mac: Badge(mac,
                                       self.logger,
                                       key=mac,  # using mac as key since no other key exists
                                       badge_id =mac_id_map[mac][0],
                                       project_id =mac_id_map[mac][1],
                                       init_audio_ts_int=self._init_ts,
                                       init_audio_ts_fract=self._init_ts_fract,
                                       init_proximity_ts=self._init_ts,
                                       ) for mac in mac_id_map.keys()    
                        }

        return badges

    def pull_badges_list(self):
        # first time we read as is
        if self._badges is None:
            file_badges = self._read_file(self._device_file)
            self._badges = file_badges
        else:
            # update list
            file_badges = self._read_file(self._device_file)
            for mac in file_badges:
                if mac not in self._badges:
                    # new badge
                    self.logger.debug("Found new badge in file: {}".format(mac))
                    self._badges[mac] = file_badges[mac]

    def pull_badge(self, mac):
        """
        Contacts to server (if responding) and updates the given badge data
        :param mac:
        :return:
        """
        pass # not implemented

    def send_badge(self, mac):
        """
        Sends timestamps of the given badge to the server
        :param mac:
        :return:
        """
        try:
            badge = self._badges[mac]
            data = {
                'last_audio_ts': badge.last_audio_ts_int,
                'last_audio_ts_fract': badge.last_audio_ts_fract,
                'last_proximity_ts': badge.last_proximity_ts,
                'last_voltage': badge.last_voltage,
                'last_seen_ts': badge.last_seen_ts,
            }

            self.logger.debug("Sending update badge data to server, badge {} : {}".format(badge.key, data))
            response = requests.patch(BADGE_ENDPOINT(badge.key), data=data, headers=request_headers())
            if response.ok is False:
                if response.status_code == 400:
                    self.logger.debug("Server had more recent date, badge {} : {}".format(badge.key, response.text))
                else:
                    raise Exception('Server sent a {} status code instead of 200: {}'.format(response.status_code,
                                                                                         response.text))
        except Exception as e:
            self.logger.error('Error sending updated badge into to server: {}'.format(e))

            

    def create_badge(self, name, email, mac):
        """
        Creates a badge using the giving information
        :param name: user name
        :param email: user email
        :param mac: badge mac
        :return:
        """
        self.logger.debug("Command 'create_badge' is not implemented for standalone mode'")
        pass # not implemented in standalone


    @property
    def badges(self):
        if self._badges is None:
            raise Exception('Badges list has not been initialized yet')
        return self._badges

if __name__ == "__main__":
    logging.basicConfig()
    logger = logging.getLogger('badge_server')
    logger.setLevel(logging.DEBUG)

    mgr = BadgeManagerStandalone(logger=logger,timestamp=1415463675)
    mgr.pull_badges_list()
    print(mgr.badges)