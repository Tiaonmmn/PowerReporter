# -*- coding:utf-8 -*-
import datetime
import os

from Registry import Registry
from loguru import logger


class usbInfo:
    def __init__(self, mountDir, volumeInfo, bias):
        self.mountDir = mountDir
        self.volumeInfo = volumeInfo
        self.bias = bias
        self._mountedDevice = self.getMountedDevice()
        self._lastInserted = self.getUsbStorLastInsteredTime()
        self._firstInserted = self.getUsbStorFirstInstertedTime()

    def getMountedDevice(self):
        output = self.volumeInfo
        result = []
        if "FAT" or "NTFS" in output.split(" ")[0]:
            os.chdir("%s/%s" % (self.mountDir, output.split(" ")[2]))
            if os.access("Windows/System32/config/system", os.F_OK | os.R_OK):
                registry = Registry.Registry("Windows/System32/config/system")
            elif os.access("Windows/System32/config/SYSTEM", os.F_OK | os.R_OK):
                registry = Registry.Registry("Windows/System32/config/SYSTEM")
            else:
                logger.warning("Couldn't find SYSTEM registry file!")
                return None
            open1 = registry.open("MountedDevices")
            '''https://docs.microsoft.com/en-us/windows-hardware/drivers/usbcon/usb-device-specific-registry-settings'''
            logger.info("Now showing Mounted Device registry!")
            for item in open1.values():
                logger.info("{0:60} : {1}".format(item.name(), item.value().decode("utf-16-le")))
                tempResult = dict()
                tempResult['Name'] = item.name()
                tempResult['Value'] = item.value()
                result.append(tempResult)
        return result

    def getUsbStorLastInsteredTime(self):
        #
        # Get USB Info in several steps.
        # 1:get CurrentControlSet\Enum\USBSTOR\{Device Class Name}\{lists of serial number}
        # 2.get CurrentControlSet\Enum\USB\{VID_PID} and check setp1's serial number and get Device Parameters\SymbolicName 's value
        # 3.get CurrentControlSet\Control\DeviceClasses\{SymbolicName} and check if VID_PID are correct.
        #
        output = self.volumeInfo
        usb_serials = []  # [("Name":"Disk&dgrre","serials":["1234312"，“12342134”]),.....]
        usb_vid_pid = []  # [('Name':"VID_0781&PID_5571","4C84654":"\??\USB#VID_0781&PID_5571#4C530012450531101593#{a5dcbf10-6530-11d2-901f-00c04fb951ed}")]
        final_result = []
        try:
            bias = datetime.timedelta(hours=-self.bias)
        except TypeError:
            pass
        if "FAT" or "NTFS" in output.split(" ")[0]:
            os.chdir("%s/%s" % (self.mountDir, output.split(" ")[2]))
            if os.access("Windows/System32/config/system", os.F_OK | os.R_OK):
                registry = Registry.Registry("Windows/System32/config/system")
            elif os.access("Windows/System32/config/SYSTEM", os.F_OK | os.R_OK):
                registry = Registry.Registry("Windows/System32/config/SYSTEM")
            else:
                logger.warning("Couldn't find SYSTEM registry file!")
                return None
            select_current = registry.open("Select").value("Current").value()
            open1 = registry.open("ControlSet00%d\\Enum\\USBSTOR" % select_current)
            for usbstor_item in open1.subkeys():
                tempResult = dict()
                tempResult['Name'] = usbstor_item.name()
                tempResult['serials'] = []
                tempResult['DiskId'] = []
                for device_class_name in usbstor_item.subkeys():
                    tempResult['serials'].append(device_class_name.name().split("&")[0])
                    tempResult['DiskId'].append(
                        device_class_name.subkey("Device Parameters").subkey("Partmgr").value("DiskId").value())
                usb_serials.append(tempResult)
            logger.critical(usb_serials)
            open2 = registry.open("ControlSet00%d\\Enum\\USB" % select_current)
            for usb_item in open2.subkeys():
                tempResult = dict()
                for temp in usb_serials:
                    temp_serialList = temp['serials']
                    try:
                        for temp_serial in temp_serialList:
                            usb_item.find_key(temp_serial)
                            tempResult['vid_pid_name'] = usb_item.name()
                            tempResult[temp_serial] = \
                                usb_item.subkey(temp_serial).subkey("Device Parameters").value("SymbolicName") \
                                    .value().split("#")[-1]

                    except Registry.RegistryKeyNotFoundException:
                        continue
                    usb_vid_pid.append(tempResult)
            logger.critical(usb_vid_pid)
            open3 = registry.open("ControlSet00%d\\Control\\DeviceClasses" % select_current)
            # usb_vid_pid = [] # [('Name':"VID_0781&PID_5571","4C84654":"\??\USB#VID_0781&PID_5571#4C530012450531101593#{a5dcbf10-6530-11d2-901f-00c04fb951ed}")]
            # try:
            for usb_vid_pid_item in usb_vid_pid:
                temp_name_list = []
                for a in range(1, len(list(usb_vid_pid_item.values()))):
                    open4 = open3.subkey(list(usb_vid_pid_item.values())[a])
                    for open4_item in open4.subkeys():
                        for i in range(1, len(list(usb_vid_pid_item.keys()))):
                            temp_final = dict()
                            temp_name = "##?#USB#" + usb_vid_pid_item['vid_pid_name'] + "#" + list(usb_vid_pid_item.keys())[
                                i] + "#" + list(usb_vid_pid_item.values())[i]
                            if temp_name in temp_name_list:
                                continue
                            temp_name_list.append(temp_name)
                            final = open4.subkey(temp_name)
                            temp_final['DeviceName'] = temp_name
                            temp_final['LastTime'] = (final.timestamp() + bias).strftime('%Y %m %d - %H:%M:%S')
                            final_result.append(temp_final)
            # except Registry.RegistryKeyNotFoundException:
            #     pass
            logger.critical(final_result)
            return final_result

    def getUsbStorFirstInstertedTime(self):
        output = self.volumeInfo
        result = []
        try:
            bias = datetime.timedelta(hours=-self.bias)
        except TypeError:
            pass
        if "FAT" or "NTFS" in output.split(" ")[0]:
            os.chdir("%s/%s" % (self.mountDir, output.split(" ")[2]))
            if os.access("Windows/inf/setupapi.dev.log", os.F_OK | os.R_OK):
                pass
            else:
                logger.critical("Couldn't find setupapi.dev.log")
                return None
            setupapi = open('Windows/inf/setupapi.dev.log', 'r').readlines()
            for item in self._lastInserted:
                for a in range(len(setupapi)):
                    if item['DeviceName'].split("#")[4] in setupapi[a] and item['DeviceName'].split("#")[5] in setupapi[a]:
                        if "Section start" in setupapi[a + 1]:
                            tempResult = dict()
                            tempResult['DeviceName'] = item['DeviceName']
                            tempResult['FirstTime'] = (datetime.datetime.strptime(setupapi[a + 1].split(".")[0],
                                                                                  ">>>  Section start %Y/%m/%d %H:%M:%S") + bias).strftime(
                                '%Y %m %d - %H:%M:%S')
                            result.append(tempResult)
                        else:
                            continue
        logger.critical(result)
        return result

    def _getPartmgrAndDeviceSerial(self):
        # Get USB Info in several steps.
        # 1:get CurrentControlSet\Enum\USBSTOR\{Device Class Name}\{lists of serial number}
        # 2.get CurrentControlSet\Enum\USB\{VID_PID} and check setp1's serial number and get Device Parameters\SymbolicName 's value
        # 3.get CurrentControlSet\Control\DeviceClasses\{SymbolicName} and check if VID_PID are correct.
        #
        output = self.volumeInfo
        usb_serials = []  # [("Name":"Disk&dgrre","serials":["1234312"，“12342134”]),.....]
        usb_vid_pid = []  # [('Name':"VID_0781&PID_5571","4C84654":"\??\USB#VID_0781&PID_5571#4C530012450531101593#{a5dcbf10-6530-11d2-901f-00c04fb951ed}")]
        final_result = []
        try:
            bias = datetime.timedelta(hours=-self.bias)
        except TypeError:
            pass
        if "FAT" or "NTFS" in output.split(" ")[0]:
            os.chdir("%s/%s" % (self.mountDir, output.split(" ")[2]))
            if os.access("Windows/System32/config/system", os.F_OK | os.R_OK):
                registry = Registry.Registry("Windows/System32/config/system")
            elif os.access("Windows/System32/config/SYSTEM", os.F_OK | os.R_OK):
                registry = Registry.Registry("Windows/System32/config/SYSTEM")
            else:
                logger.warning("Couldn't find SYSTEM registry file!")
                return None
            select_current = registry.open("Select").value("Current").value()
            open1 = registry.open("ControlSet00%d\\Enum\\USBSTOR" % select_current)
            for usbstor_item in open1.subkeys():
                tempResult = dict()
                tempResult['Name'] = usbstor_item.name()
                tempResult['serials'] = []
                tempResult['DiskId'] = []
                for device_class_name in usbstor_item.subkeys():
                    tempResult['serials'].append(device_class_name.name().split("&")[0])
                    tempResult['DiskId'].append(
                        device_class_name.subkey("Device Parameters").subkey("Partmgr").value("DiskId").value())
                usb_serials.append(tempResult)
            logger.critical(usb_serials)
        return usb_serials

    def getUsbVolumeName(self):
        partMgrAndDeviceName = self._getPartmgrAndDeviceSerial()
        temp_mountData = []
        temp_result = []
        result = []
        output = self.volumeInfo
        try:
            for item in self._mountedDevice:
                temp_mountData.append(item['Value'])
        except (ValueError, TypeError):
            return None
        for a in range(len(temp_mountData)):
            for b in range(len(temp_mountData)):
                if temp_mountData[a] == temp_mountData[b] and a != b:
                    temp_result.append("{0}={1}".format(self._mountedDevice[a]['Name'], self._mountedDevice[b]['Name']))
        if "FAT" or "NTFS" in output.split(" ")[0]:
            os.chdir("%s/%s/" % (self.mountDir, output.split(" ")[2]))
            if os.access("Windows/System32/config/software", os.F_OK | os.R_OK):
                registry = Registry.Registry("Windows/System32/config/software")
            elif os.access("Windows/System32/config/SOFTWARE", os.F_OK | os.R_OK):
                registry = Registry.Registry("Windows/System32/config/SOFTWARE")
            else:
                logger.warning("Couldn't find SOFTWARE registry file!")
                return None
            open1 = registry.open("Microsoft\\Windows Search\\VolumeInfoCache")
            for item in temp_result:
                parts = item.split("=")
                if "DosDevices" in parts[0]:
                    partitionId = parts[0][-2:]
                    guid = parts[1].split("Volume")[1]
                if "DosDevices" in parts[1]:
                    partitionId = parts[1][-2:]
                    guid = parts[0].split("Volume")[0]
                try:
                    tempResult = dict()
                    Label = open1.subkey(partitionId).value("VolumeLabel").value()
                    for parts1 in partMgrAndDeviceName:
                        try:
                            print(parts1['DiskId'])
                            index = parts1['DiskId'].index(guid)
                        except ValueError:
                            logger.critical(guid)
                            continue
                        serial = parts1['serials'][index]
                        for lists in self._lastInserted:
                            if serial in lists['DeviceName']:
                                tempResult['DeviceName'] = lists['DeviceName']
                                tempResult['Label'] = Label
                                result.append(tempResult)
                            else:
                                continue
                except Registry.RegistryKeyNotFoundException:
                    continue
        logger.critical(result)
        return result
