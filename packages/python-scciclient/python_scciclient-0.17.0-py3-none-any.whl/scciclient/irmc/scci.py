# Copyright 2015 FUJITSU LIMITED
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""
SCCI functionalities shared between different iRMC modules.
"""

import functools
import re
import time

import defusedxml.ElementTree as ET
import requests

from scciclient.irmc import ipmi
from scciclient.irmc import snmp

DEBUG = False

S4_PATTERN = re.compile(r"^iRMC\s*S4$")
S5_PATTERN = re.compile(r"^iRMC\s*S5$")
FW_VERSION_HEAD_PATTERN = re.compile(r"^\d[\d.]*")
FW_VERSION_TAIL_PATTERN = re.compile(r"[a-zA-Z]*$")

S4_FD_SUPPORT_UPPER = 9.21
S5_FD_SUPPORT_UPPER = 1.25


class SCCIError(Exception):
    """SCCI Error

    This exception is general exception.
    """
    def __init__(self, message, errorcode=None):
        super(SCCIError, self).__init__(message)


class SCCIInvalidInputError(SCCIError):
    """SCCIInvalidInputError

    This exception is used when invalid inputs are passed to
    the APIs exposed by this module.
    """
    def __init__(self, message):
        super(SCCIInvalidInputError, self).__init__(message)


class SCCIClientError(SCCIError):
    """SCCIClientError

    This exception is used when a problem is encountered in
    executing an operation on the iRMC
    """
    def __init__(self, message):
        super(SCCIClientError, self).__init__(message)


class SCCIRAIDNotReady(SCCIError):
    """SCCIRAIDNotReady

    This exception is used when a mechanism not applied
    into a configuration on the iRMC yet
    """
    def __init__(self, message):
        super(SCCIRAIDNotReady, self).__init__(message)


class SCCISessionTimeout(SCCIError):
    def __init__(self, message):
        super(SCCISessionTimeout, self).__init__(message)


"""
List of iRMC S4/S5 supported SCCI commands

SCCI
OpCode  SCCI Command String      Description
0xE002  ConfigSpace              ConfigSpace Write
0x0111  PowerOnCabinet           Power On the Server
0x0112  PowerOffCabinet          Power Off the Server
0x0113  PowerOffOnCabinet        Power Cycle the Server
0x0204  ResetServer              Hard Reset the Server
0x020C  RaiseNMI                 Pulse the NMI (Non Maskable Interrupt)
0x0205  RequestShutdownAndOff    Graceful Shutdown, requires running Agent
0x0206  RequestShutdownAndReset  Graceful Reboot, requires running Agent
0x0209  ShutdownRequestCancelled Cancel a Shutdown Request
0x0203  ResetFirmware  Perform a BMC Reset
0x0251  ConnectRemoteFdImage     Connect or Disconnect a Floppy Disk image on a
                                 Remote Image Mount (NFS or CIFS Share )

                                 This command was deprecated at following
                                 version:
                                   iRMC S4: 9.62F
                                            (9.21F still supports virtual FD)
                                   iRMC S5: 1.60P
                                            (1.25P still supports virtual FD)

0x0252  ConnectRemoteCdImage     Connect or Disconnect a CD/DVD .iso image on a
                                 Remote Image Mount (NFS or CIFS Share )
0x0253  ConnectRemoteHdImage     Connect or Disconnect a Hard Disk image on a
                                 Remote Image Mount (NFS or CIFS Share )
"""

_POWER_CMD = '''
<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>
<CMDSEQ>
  <CMD Context="SCCI" OC="%s" OE="0" OI="0" Type="SET">
  </CMD>
</CMDSEQ>
'''


POWER_ON = _POWER_CMD % "PowerOnCabinet"
POWER_OFF = _POWER_CMD % "PowerOffCabinet"
POWER_CYCLE = _POWER_CMD % "PowerOffOnCabinet"
POWER_RESET = _POWER_CMD % "ResetServer"
POWER_RAISE_NMI = _POWER_CMD % "RaiseNMI"
POWER_SOFT_OFF = _POWER_CMD % "RequestShutdownAndOff"
POWER_SOFT_CYCLE = _POWER_CMD % "RequestShutdownAndReset"
POWER_CANCEL_SHUTDOWN = _POWER_CMD % "ShutdownRequestCancelled"


_VIRTUAL_MEDIA_CMD = '''
<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>
<CMDSEQ>
  <CMD Context="SCCI" OC="%s" OE="0" OI="0" Type="SET">
    <DATA Type="xsd::integer">%d</DATA>
  </CMD>
</CMDSEQ>
'''


MOUNT_CD = _VIRTUAL_MEDIA_CMD % ("ConnectRemoteCdImage", 1)
UNMOUNT_CD = _VIRTUAL_MEDIA_CMD % ("ConnectRemoteCdImage", 0)
MOUNT_FD = _VIRTUAL_MEDIA_CMD % ("ConnectRemoteFdImage", 1)
UNMOUNT_FD = _VIRTUAL_MEDIA_CMD % ("ConnectRemoteFdImage", 0)


_VIRTUAL_MEDIA_CD_SETTINGS = '''
<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>
<CMDSEQ>
  <!-- "ConfBmcMediaOptionsRemoteMediaEnabled" -->
  <!-- Make sure this one is enabled -->
  <CMD Context="SCCI" OC="ConfigSpace" OE="1A80" OI="0" Type="SET">
    <DATA Type="xsd::integer">1</DATA>
  </CMD>
  <!-- "ConfBmcMediaOptionsCdNumber" -->
  <!-- Number of emulated CDROM/DVD Devices -->
  <CMD Context="SCCI" OC="ConfigSpace" OE="1A68" OI="0" Type="SET">
    <DATA Type="xsd::integer">1</DATA>
  </CMD>
  <!-- "ConfBmcRemoteCdImageServer" -->
  <CMD Context="SCCI" OC="ConfigSpace" OE="1A60" OI="0" Type="SET">
    <DATA Type="xsd::string">%s</DATA>
  </CMD>
  <!-- "ConfBmcRemoteCdImageUserDomain" -->
  <CMD Context="SCCI" OC="ConfigSpace" OE="1A63" OI="0" Type="SET">
    <DATA Type="xsd::string">%s</DATA>
  </CMD>
  <!-- "ConfBmcRemoteCdImageShareType" -->
  <!-- 0 = NFS Share / 1 = CIFS Share -->
  <CMD Context="SCCI" OC="ConfigSpace" OE="1A64" OI="0" Type="SET">
    <DATA Type="xsd::integer">%d</DATA>
  </CMD>
  <!-- "ConfBmcRemoteCdImageShareName" -->
  <CMD Context="SCCI" OC="ConfigSpace" OE="1A65" OI="0" Type="SET">
    <DATA Type="xsd::string">%s</DATA>
  </CMD>
  <!-- "ConfBmcRemoteCdImageImageName" -->
  <CMD Context="SCCI" OC="ConfigSpace" OE="1A66" OI="0" Type="SET">
    <DATA Type="xsd::string">%s</DATA>
  </CMD>
  <!-- "ConfBmcRemoteCdImageUserName" -->
  <CMD Context="SCCI" OC="ConfigSpace" OE="1A61" OI="0" Type="SET">
    <DATA Type="xsd::string">%s</DATA>
  </CMD>
  <!-- "ConfBmcRemoteCdImageUserPassword" -->
  <CMD Context="SCCI" OC="ConfigSpace" OE="1A62" OI="0" Type="SET">
    <DATA Type="xsd::string" Encrypted="0">%s</DATA>
  </CMD>
</CMDSEQ>
'''


_VIRTUAL_MEDIA_FD_SETTINGS = '''
<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>
<CMDSEQ>
  <!-- "ConfBmcMediaOptionsRemoteMediaEnabled" -->
  <!-- Make sure this one is enabled -->
  <CMD Context="SCCI" OC="ConfigSpace" OE="1A80" OI="0" Type="SET">
    <DATA Type="xsd::integer">1</DATA>
  </CMD>
  <!-- "ConfBmcMediaOptionsFdNumber" -->
  <!-- Number of emulated FD Devices -->
  <CMD Context="SCCI" OC="ConfigSpace" OE="1A58" OI="0" Type="SET">
    <DATA Type="xsd::integer">1</DATA>
  </CMD>
  <!-- "ConfBmcRemoteFdImageServer" -->
  <CMD Context="SCCI" OC="ConfigSpace" OE="1A50" OI="0" Type="SET">
    <DATA Type="xsd::string">%s</DATA>
  </CMD>
  <!-- "ConfBmcRemoteFdImageUserDomain" -->
  <CMD Context="SCCI" OC="ConfigSpace" OE="1A53" OI="0" Type="SET">
    <DATA Type="xsd::string">%s</DATA>
  </CMD>
  <!-- "ConfBmcRemoteFdImageShareType" -->
  <!-- 0 = NFS Share / 1 = CIFS Share -->
  <CMD Context="SCCI" OC="ConfigSpace" OE="1A54" OI="0" Type="SET">
    <DATA Type="xsd::integer">%d</DATA>
  </CMD>
  <!-- "ConfBmcRemoteFdImageShareName" -->
  <CMD Context="SCCI" OC="ConfigSpace" OE="1A55" OI="0" Type="SET">
    <DATA Type="xsd::string">%s</DATA>
  </CMD>
  <!-- "ConfBmcRemoteFdImageImageName" -->
  <CMD Context="SCCI" OC="ConfigSpace" OE="1A56" OI="0" Type="SET">
    <DATA Type="xsd::string">%s</DATA>
  </CMD>
  <!-- "ConfBmcRemoteFdImageUserName" -->
  <CMD Context="SCCI" OC="ConfigSpace" OE="1A51" OI="0" Type="SET">
    <DATA Type="xsd::string">%s</DATA>
  </CMD>
  <!-- "ConfBmcRemoteFdImageUserPassword" -->
  <CMD Context="SCCI" OC="ConfigSpace" OE="1A52" OI="0" Type="SET">
    <DATA Type="xsd::string" Encrypted="0">%s</DATA>
  </CMD>
</CMDSEQ>
'''


class MetaShareType(type):
    @property
    def nfs(cls):
        return cls.NFS

    @property
    def cifs(cls):
        return cls.CIFS


class ShareType(object, metaclass=MetaShareType):
    """"Virtual Media Share Type."""
    NFS = 0
    CIFS = 1


def get_share_type(share_type):
    """get share type."""
    return {
        'nfs': ShareType.nfs,
        'cifs': ShareType.cifs
    }[share_type.lower()]


def scci_cmd(host, userid, password, cmd, port=443, auth_method='basic',
             client_timeout=60, do_async=True, verify=False, **kwargs):
    """execute SCCI command

    This function calls SCCI server modules
    :param host: hostname or IP of iRMC
    :param userid: userid for iRMC with administrator privileges
    :param password: password for userid
    :param cmd: SCCI command
    :param port: port number of iRMC
    :param auth_method: irmc_username
    :param client_timeout: timeout for SCCI operations
    :param do_async: async call if True, sync call otherwise
    :param verify: (optional) Either a boolean, in which case it
                    controls whether we verify the server's TLS certificate,
                    or a string, in which case it must be a path to
                    a CA bundle to use. Defaults to ``False``.
    :returns: requests.Response from SCCI server
    :raises: SCCIInvalidInputError if port and/or auth_method params
             are invalid
    :raises: SCCIClientError if SCCI failed
    """
    auth_obj = None
    try:
        protocol = {80: 'http', 443: 'https'}[port]
        auth_obj = {
            'basic': requests.auth.HTTPBasicAuth(userid, password),
            'digest': requests.auth.HTTPDigestAuth(userid, password)
        }[auth_method.lower()]

    except KeyError:
        raise SCCIInvalidInputError(
            ("Invalid port %(port)d or " +
             "auth_method for method %(auth_method)s") %
            {'port': port, 'auth_method': auth_method})

    try:
        header = {'Content-type': 'application/x-www-form-urlencoded'}
        if kwargs.get('upgrade_type') == 'irmc':
            with open(cmd, 'rb') as file:
                data = file.read()
            config_type = '/irmcupdate?flashSelect=255'
        elif kwargs.get('upgrade_type') == 'bios':
            with open(cmd, 'rb') as file:
                data = file.read()
            config_type = '/biosupdate'
        else:
            # For EJECT command, validate parameters to handle abnormal case
            if check_eject_cd_cmd(cmd):
                if not validate_params_cd_fd("cmd_cd", protocol,
                                             host, auth_obj,
                                             do_async, client_timeout,
                                             verify):
                    return
            if check_eject_fd_cmd(cmd):
                if not validate_params_cd_fd("cmd_fd", protocol,
                                             host, auth_obj,
                                             do_async, client_timeout,
                                             verify):
                    return
            data = cmd
            config_type = '/config'

        r = requests.post(protocol + '://' + host + config_type,
                          data=data,
                          headers=header,
                          verify=verify,
                          timeout=client_timeout,
                          allow_redirects=False,
                          auth=auth_obj)

        if not do_async:
            time.sleep(5)
        else:
            # Async mode
            # Even in async mode, return immediately may cause error 5
            # (Input/Output error) for some commands such as POWER_ON,
            # POWER_OFF, POWER_RESET if we perform multiple calls of them
            # in a tight sequence or in parallel.
            # So, we sleep some time for such commands.
            if cmd in (POWER_ON, POWER_OFF, POWER_RESET):
                time.sleep(3)

        if DEBUG:
            print(cmd)
            print(r.text)
            print("do_async = %s" % do_async)
        if r.status_code not in (200, 201):
            raise SCCIClientError(
                ('HTTP PROTOCOL ERROR, STATUS CODE = %s' %
                 str(r.status_code)))

        result_xml = ET.fromstring(r.text)
        status = result_xml.find("./Value")
        # severity = result_xml.find("./Severity")
        error = result_xml.find("./Error")
        message = result_xml.find("./Message")
        if not int(status.text) == 0:
            raise SCCIClientError(
                ('SCCI PROTOCOL ERROR, STATUS CODE = %s, '
                 'ERROR = %s, MESSAGE = %s' %
                 (str(status.text), error.text, message.text)))
        else:
            return r

    except IOError as input_error:
        raise SCCIClientError(input_error)

    except ET.ParseError as parse_error:
        raise SCCIClientError(parse_error)

    except requests.exceptions.RequestException as requests_exception:
        raise SCCIClientError(requests_exception)


def validate_params_cd_fd(cmd_type, protocol, host, auth_obj,
                          do_async, client_timeout, verify):
    """Validate parameters of CD/DVD or FD Image Virtual Media in iRMC

    If one of parameters (ImageServer, ImageShareName or ImageName) set in
    ServerView Config Space is empty, and you try to eject virtual FD/CD,
    iRMC returns error. This function determines whether iRMC doesn't return
    error when you try to eject virtual FD/CD.
    :param cmd_type: command type has value switch between "cmd_cd" or "cmd_fd"
    :param protocol:
    :param host: hostname or IP of iRMC
    :param auth_obj: irmc userid/password
    :param do_async: async call if True, sync call otherwise
    :param client_timeout: timeout for SCCI operations
    :param verify: Either a boolean, in which case it
                   controls whether we verify the server's TLS certificate,
                   or a string, in which case it must be a path to
                   a CA bundle to use.
    :return: False if one of param is null. Otherwise, returns True.
    """

    if cmd_type == "cmd_cd":
        oe_image_server = "1A60"
        oe_image_server_share_name = "1A65"
        oe_image_name = "1A66"
    else:
        oe_image_server = "1A50"
        oe_image_server_share_name = "1A55"
        oe_image_name = "1A56"

    try:
        param = {'P45': '1', 'SAVE_DATA': '1'}
        header = {'Content-type': 'application/x-www-form-urlencoded'}
        r = requests.get(protocol + '://' + host + '/iRMC_Settings.pre',
                         params=param,
                         headers=header,
                         verify=verify,
                         timeout=client_timeout,
                         allow_redirects=False,
                         auth=auth_obj)
        if not do_async:
            time.sleep(5)

        if DEBUG:
            print("---------------------------")
            print("Current iRMC configuration:")
            print(r.url)

        if r.status_code not in (200, 201):
            raise SCCIClientError(
                ('HTTP PROTOCOL ERROR, STATUS CODE = %s' %
                 str(r.status_code)))

        result = r.text
        cmdseq = ET.fromstring(result)
        cfg_dict = {}
        for cmd_tag in cmdseq.iter(tag='CMD'):
            oe = cmd_tag.get('OE')
            data = cmd_tag.find('DATA').text
            cfg_dict[oe] = data

        if DEBUG:
            print("Server: ", cfg_dict[oe_image_server])
            print("Share Name: ", cfg_dict[oe_image_server_share_name])
            print("Image Name: ", cfg_dict[oe_image_name])
            print("---------------------------")

        if (cfg_dict[oe_image_server] is None) or \
                (cfg_dict[oe_image_server_share_name] is None) or \
                (cfg_dict[oe_image_name] is None):
            return False

    except ET.ParseError as parse_error:
        raise SCCIClientError(parse_error)
    except requests.exceptions.RequestException as requests_exception:
        raise SCCIClientError(requests_exception)

    return True


def check_eject_cd_cmd(xml_cmd):
    """To check command is MOUNT or UNMOUNT

    :param xml_cmd: the command
    :return: true if this is UNMOUNT command. Otherwise, return false.
    """

    try:
        cmdseq = ET.fromstring(xml_cmd.strip())
        cmd = cmdseq.find("./CMD")
        data = cmd.find("./DATA")
        if cmd.get("OC") == "ConnectRemoteCdImage" and \
                cmd.get("Type") == "SET" and data.text == "0":
            return True
    except ET.ParseError as parse_error:
        raise SCCIClientError(parse_error)
    return False


def check_eject_fd_cmd(xml_cmd):
    """To check command is MOUNT or UNMOUNT

    :param xml_cmd: the command
    :return: true if this is UNMOUNT command. Otherwise, return false.
    """
    try:
        cmdseq = ET.fromstring(xml_cmd.strip())
        cmd = cmdseq.find("./CMD")
        data = cmd.find("./DATA")
        if cmd.get("OC") == "ConnectRemoteFdImage" and \
                cmd.get("Type") == "SET" and data.text == "0":
            return True
    except ET.ParseError as parse_error:
        raise SCCIClientError(parse_error)
    return False


def get_client(host, userid, password, port=443, auth_method='basic',
               client_timeout=60, verify=False, **kwargs):
    """get SCCI command partial function

    This function returns SCCI command partial function
    :param host: hostname or IP of iRMC
    :param userid: userid for iRMC with administrator privileges
    :param password: password for userid
    :param port: port number of iRMC
    :param auth_method: irmc_username
    :param client_timeout: timeout for SCCI operations
    :param verify: (optional) Either a boolean, in which case it
                    controls whether we verify the server's TLS certificate,
                    or a string, in which case it must be a path to
                    a CA bundle to use. Defaults to ``False``.
    :returns: scci_cmd partial function which takes a SCCI command param
    """

    return functools.partial(scci_cmd, host, userid, password,
                             port=port, auth_method=auth_method,
                             client_timeout=client_timeout,
                             verify=verify, **kwargs)


def get_virtual_cd_set_params_cmd(remote_image_server,
                                  remote_image_user_domain,
                                  remote_image_share_type,
                                  remote_image_share_name,
                                  remote_image_deploy_iso,
                                  remote_image_username,
                                  remote_image_user_password):
    """get Virtual CD Media Set Parameters Command

    This function returns Virtual CD Media Set Parameters Command
    :param remote_image_server: remote image server name or IP
    :param remote_image_user_domain: domain name of remote image server
    :param remote_image_share_type: share type of ShareType
    :param remote_image_share_name: share name
    :param remote_image_deploy_iso: deploy ISO image file name
    :param remote_image_username: username of remote image server
    :param remote_image_user_password: password of the username
    :returns: SCCI command
    """

    cmd = _VIRTUAL_MEDIA_CD_SETTINGS % (
        remote_image_server,
        remote_image_user_domain,
        remote_image_share_type,
        remote_image_share_name,
        remote_image_deploy_iso,
        remote_image_username,
        remote_image_user_password)

    return cmd


def get_virtual_fd_set_params_cmd(remote_image_server,
                                  remote_image_user_domain,
                                  remote_image_share_type,
                                  remote_image_share_name,
                                  remote_image_floppy_fat,
                                  remote_image_username,
                                  remote_image_user_password):
    """get Virtual FD Media Set Parameters Command

    This function returns Virtual FD Media Set Parameters Command
    :param remote_image_server: remote image server name or IP
    :param remote_image_user_domain: domain name of remote image server
    :param remote_image_share_type: share type of ShareType
    :param remote_image_share_name: share name
    :param remote_image_deploy_iso: deploy ISO image file name
    :param remote_image_username: username of remote image server
    :param remote_image_user_password: password of the username
    :returns: SCCI command
    """
    cmd = _VIRTUAL_MEDIA_FD_SETTINGS % (
        remote_image_server,
        remote_image_user_domain,
        remote_image_share_type,
        remote_image_share_name,
        remote_image_floppy_fat,
        remote_image_username,
        remote_image_user_password)

    return cmd


def get_report(host, userid, password,
               port=443, auth_method='basic', client_timeout=60, verify=False):
    """get iRMC report

    This function returns iRMC report in XML format
    :param host: hostname or IP of iRMC
    :param userid: userid for iRMC with administrator privileges
    :param password: password for userid
    :param port: port number of iRMC
    :param auth_method: irmc_username
    :param client_timeout: timeout for SCCI operations
    :param verify: (optional) Either a boolean, in which case it
                    controls whether we verify the server's TLS certificate,
                    or a string, in which case it must be a path to
                    a CA bundle to use. Defaults to ``False``.
    :returns: root element of SCCI report
    :raises: ISCCIInvalidInputError if port and/or auth_method params
             are invalid
    :raises: SCCIClientError if SCCI failed
    """

    auth_obj = None
    try:
        protocol = {80: 'http', 443: 'https'}[port]
        auth_obj = {
            'basic': requests.auth.HTTPBasicAuth(userid, password),
            'digest': requests.auth.HTTPDigestAuth(userid, password)
        }[auth_method.lower()]

    except KeyError:
        raise SCCIInvalidInputError(
            ("Invalid port %(port)d or " +
             "auth_method for method %(auth_method)s") %
            {'port': port, 'auth_method': auth_method})

    try:
        r = requests.get(protocol + '://' + host + '/report.xml',
                         verify=verify,
                         timeout=(10, client_timeout),
                         allow_redirects=False,
                         auth=auth_obj)

        if r.status_code not in (200, 201):
            raise SCCIClientError(
                ('HTTP PROTOCOL ERROR, STATUS CODE = %s' %
                 str(r.status_code)))

        root = ET.fromstring(r.text)
        return root

    except ET.ParseError as parse_error:
        raise SCCIClientError(parse_error)

    except requests.exceptions.RequestException as requests_exception:
        raise SCCIClientError(requests_exception)


def get_sensor_data_records(report):
    """get sensor data

    This function returns sensor data in XML
    :param report: SCCI report element
    :returns: sensor element of SCCI report, or None
    """

    sensor = report.find("./System/SensorDataRecords")
    return sensor


def get_irmc_version(report):
    """get iRMC version

    This function returns iRMC version number
    :param report: SCCI report element
    :returns: version element of SCCI report, or None
    """

    version = report.find("./System/ManagementControllers/iRMC")
    return version


def get_irmc_version_str(report):
    """extract iRMC OS and iRMC firmware version from SCCI report

    This function returns iRMC OS name and iRMC firmware version
    :param report: SCCI report element
    :returns: a tuple of string (iRMC OS name, iRMC FW version)
    """

    version = get_irmc_version(report)
    return version.get('Name'), version.find('Firmware').text


def support_virtual_fd_str(irmc_os, fw_version):
    """determine iRMC supports virtual floppy disk

    This function determines whether iRMC supports virtual floppy disk
    based on provided iRMC OS & iRMC firmware version
    :param irmc_os: string representing iRMC OS
    :param fw_version: string representing iRMC firmware version
    :returns: boolean
    """

    version_head = FW_VERSION_HEAD_PATTERN.match(fw_version)

    if S4_PATTERN.match(irmc_os):
        if version_head and float(version_head.group()) <= S4_FD_SUPPORT_UPPER:
            return True
    elif S5_PATTERN.match(irmc_os):
        if version_head and float(version_head.group()) <= S5_FD_SUPPORT_UPPER:
            return True

    return False


def support_virtual_fd(report):
    """determine iRMC supports virtual floppy disk

    This function determines whether iRMC supports virtual floppy disk
    based on SCCI report
    :param report: SCCI report element
    :returns: boolean
    """

    irmc_os, fwv = get_irmc_version_str(report)
    return support_virtual_fd_str(irmc_os, fwv)


def get_essential_properties(report, prop_keys):
    """get essential properties

    This function returns a dictionary which contains keys as in
    prop_keys and its values from the report.

    :param report: SCCI report element
    :param prop_keys: a list of keys for essential properties
    :returns: a dictionary which contains keys as in
              prop_keys and its values.
    """
    v = {}
    v['memory_mb'] = int(report.find('./System/Memory/Installed').text)
    v['local_gb'] = sum(
        [int(int(size.text) / 1024)
         for size in report.findall('.//PhysicalDrive/ConfigurableSize')])
    v['cpus'] = sum([int(cpu.find('./CoreNumber').text)
                     for cpu in report.find('./System/Processor')
                     if cpu.find('./CoreNumber') is not None])
    # v['cpus'] = sum([int(cpu.find('./LogicalCpuNumber').text)
    #                 for cpu in report.find('./System/Processor')])
    v['cpu_arch'] = 'x86_64'

    return {k: v[k] for k in prop_keys}


def get_capabilities_properties(d_info,
                                capa_keys,
                                gpu_ids,
                                fpga_ids=None,
                                **kwargs):
    """get capabilities properties

    This function returns a dictionary which contains keys
    and their values from the report.


    :param d_info: the dictionary of ipmitool parameters for accessing a node.
    :param capa_keys: a list of keys for additional capabilities properties.
    :param gpu_ids: the list of string contains <vendorID>/<deviceID>
    for GPU.
    :param fpga_ids: the list of string contains <vendorID>/<deviceID>
    for CPU FPGA.
    :param kwargs: additional arguments passed to scciclient.
    :returns: a dictionary which contains keys and their values.
    """

    snmp_client = snmp.SNMPClient(
        address=d_info['irmc_address'],
        port=d_info['irmc_snmp_port'],
        version=d_info['irmc_snmp_version'],
        read_community=d_info['irmc_snmp_community'],
        user=d_info.get('irmc_snmp_user'),
        auth_proto=d_info.get('irmc_snmp_auth_proto'),
        auth_key=d_info.get('irmc_snmp_auth_password'),
        priv_proto=d_info.get('irmc_snmp_priv_proto'),
        priv_key=d_info.get('irmc_snmp_priv_password'))

    try:
        v = {}
        if 'rom_firmware_version' in capa_keys:
            v['rom_firmware_version'] = \
                snmp.get_bios_firmware_version(snmp_client)

        if 'irmc_firmware_version' in capa_keys:
            v['irmc_firmware_version'] = \
                snmp.get_irmc_firmware_version(snmp_client)

        if 'server_model' in capa_keys:
            v['server_model'] = snmp.get_server_model(snmp_client)

        # Sometime the server started but PCI device list building is
        # still in progress so system will response error. We have to wait
        # for some more seconds.
        if kwargs.get('sleep_flag', False) and \
                any(k in capa_keys for k in ('pci_gpu_devices', 'cpu_fpga')):
            time.sleep(5)

        if 'pci_gpu_devices' in capa_keys:
            v['pci_gpu_devices'] = ipmi.get_pci_device(d_info, gpu_ids)

        if fpga_ids is not None and 'cpu_fpga' in capa_keys:
            v['cpu_fpga'] = ipmi.get_pci_device(d_info, fpga_ids)

        if 'trusted_boot' in capa_keys:
            v['trusted_boot'] = ipmi.get_tpm_status(d_info)

        return v
    except (snmp.SNMPFailure, ipmi.IPMIFailure) as err:
        raise SCCIClientError('Capabilities inspection failed: %s' % err)


def process_session_status(irmc_info, session_timeout, upgrade_type):
    """process session for Bios config backup/restore or RAID config operation

    :param irmc_info: node info
    :param session_timeout: session timeout
    :param upgrade_type: flag to check upgrade with bios or irmc
    :return: a dict with following values:
        {
            'upgrade_message': <Message of firmware upgrade mechanism>,
            'upgrade_status'
        }
    """
    session_expiration = time.time() + session_timeout

    while time.time() < session_expiration:
        try:
            # Get session status to check
            session = get_firmware_upgrade_status(irmc_info, upgrade_type)
        except SCCIClientError:
            # Ignore checking during rebooted server
            time.sleep(10)
            continue

        status = session.find("./Value").text
        severity = session.find("./Severity").text
        message = session.find("./Message").text
        result = {}

        if severity == 'Information' and status != '0':
            if 'FLASH successful' in message:
                result['upgrade_status'] = 'Complete'
                return result
            # Sleep a bit
            time.sleep(5)
        elif severity == 'Error':
            result['upgrade_status'] = 'Error'
            return result
        else:
            # Error occurred, get session log to see what happened
            session_log = message
            raise SCCIClientError('Failed to set firmware upgrade. '
                                  'Session log is %s.' % session_log)

    else:
        raise SCCISessionTimeout('Failed to time out mechanism with %s.'
                                 % session_expiration)


def get_raid_fgi_status(report):
    """Gather fgi(foreground initialization) information of raid configuration

    This function returns a fgi status which contains activity status
    and its values from the report.

    :param report: SCCI report information
    :returns: dict of fgi status of logical_drives, such as Initializing (10%)
              or Idle. e.g: {'0': 'Idle', '1': 'Initializing (10%)'}
    :raises: SCCIInvalidInputError: fail report input.
             SCCIRAIDNotReady: waiting for RAID configuration to complete.
    """
    fgi_status = {}
    raid_path = "./Software/ServerView/ServerViewRaid"

    if not report.find(raid_path):
        raise SCCIInvalidInputError(
            "ServerView RAID not available in Bare metal Server")
    if not report.find(raid_path + "/amEMSV/System/Adapter/LogicalDrive"):
        raise SCCIRAIDNotReady(
            "RAID configuration not configure in Bare metal Server yet")

    logical_drives = report.findall(raid_path +
                                    "/amEMSV/System/Adapter/LogicalDrive")
    for logical_drive_name in logical_drives:
        status = logical_drive_name.find("./Activity").text
        name = logical_drive_name.find("./LogDriveNumber").text
        fgi_status.update({name: status})

    return fgi_status


def get_firmware_upgrade_status(irmc_info, upgrade_type):
    """get firmware upgrade status of bios or irmc

    :param irmc_info: dict of iRMC params to access the server node
        {
          'irmc_address': host,
          'irmc_username': user_id,
          'irmc_password': password,
          'irmc_port': 80 or 443, default is 443,
          'irmc_auth_method': 'basic' or 'digest', default is 'digest',
          'irmc_client_timeout': timeout, default is 60,
          'irmc_verify_ca': (optional) Either a boolean, in which case it
                            controls whether we verify the server's TLS
                            certificate, or a string, in which case it
                            must be a path to a CA bundle to use.
                            Defaults to ``False``.
          ...
        }
    :param upgrade_type: flag to check upgrade with bios or irmc
    :raises: ISCCIInvalidInputError if port and/or auth_method params
             are invalid
    :raises: SCCIClientError if SCCI failed
    """

    host = irmc_info.get('irmc_address')
    userid = irmc_info.get('irmc_username')
    password = irmc_info.get('irmc_password')
    port = irmc_info.get('irmc_port', 443)
    auth_method = irmc_info.get('irmc_auth_method', 'digest')
    client_timeout = irmc_info.get('irmc_client_timeout', 60)
    verify = irmc_info.get('irmc_verify_ca', False)

    auth_obj = None
    try:
        protocol = {80: 'http', 443: 'https'}[port]
        auth_obj = {
            'basic': requests.auth.HTTPBasicAuth(userid, password),
            'digest': requests.auth.HTTPDigestAuth(userid, password)
        }[auth_method.lower()]
    except KeyError:
        raise SCCIInvalidInputError(
            ("Invalid port %(port)d or " +
             "auth_method for method %(auth_method)s") %
            {'port': port, 'auth_method': auth_method})
    try:
        if upgrade_type == 'bios':
            upgrade_type = '/biosprogress'
        elif upgrade_type == 'irmc':
            upgrade_type = '/irmcprogress'
        r = requests.get(protocol + '://' + host + upgrade_type,
                         verify=verify,
                         timeout=(10, client_timeout),
                         allow_redirects=False,
                         auth=auth_obj)

        if r.status_code not in (200, 201):
            raise SCCIClientError(
                ('HTTP PROTOCOL ERROR, STATUS CODE = %s' %
                 str(r.status_code)))

        upgrade_status_xml = ET.fromstring(r.text)
        return upgrade_status_xml
    except ET.ParseError as parse_error:
        raise SCCIClientError(parse_error)
    except requests.RequestException as requests_exception:
        raise SCCIClientError(requests_exception)
