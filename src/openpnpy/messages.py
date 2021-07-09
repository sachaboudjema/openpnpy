"""This module provides functions to build PnP messages to sent to the device's 
PnP agent.
The functions only build the message's body part, without a correlator attribute.
"""
from xml.etree import ElementTree
from contextlib import contextmanager
from collections import namedtuple


__all__ = ['backoff', 'device_info', 'config_upgrade', 'bye', 'cli_config', 'raises']


class ContextualTreeBuilder(ElementTree.TreeBuilder):
    """Convinience class to allow using contexts with TreeBuilder.
    """
    @contextmanager
    def start(self, tag, attrib={}):
        try:
            yield super().start(tag, attrib)
        finally:
            super().end(tag)


def backoff(hours=0, minutes=0, seconds=0, default_minutes=0, terminate=False, reason='No Reason'):
    """Inform the PnP agent to connect back after some time.

    :param hours: Hours to wait before connecting back (0 to 47), defaults to 0
    :type hours: int, optional
    :param minutes: Minutes to wait before connecting back (0 to 59), defaults to 0
    :type minutes: int, optional
    :param seconds: Seconds to wait before connecting back  (0 to 59), defaults to 0
    :type seconds: int, optional
    :param default_minutes: Change default backoff timer to this value (1 to 2880), 
        defaults to 0
    :type default_minutes: int, optional
    :param terminate: Ask agent to not connect to server ever again and remove 
        any PnP profile/configuration., defaults to False
    :type terminate: bool, optional
    :param reason: Reason of the backoff request, defaults to 'No Reason'
    :type reason: str, optional
    :return: XML element to be used as a PnP message body
    :rtype: xml.etree.ElementTree.Element
    :raises ValueError: If neither timer, default timer or terminate is specified

    .. note:: Timer values, default timer and terminate are mutualy exclusive
    """
    ctb = ContextualTreeBuilder()
    with ctb.start('{urn:cisco:pnp:backoff}request'):
        with ctb.start('backoff'):
            with ctb.start('reason'):
                ctb.data(reason)
            if terminate:
                with ctb.start('terminate'):
                    pass
            elif default_minutes:
                with ctb.start('defaultMinutes'):
                    ctb.data(str(default_minutes))
            elif hours or minutes or seconds:
                with ctb.start('callBackAfter'):
                    if hours:
                        with ctb.start('hours'):
                            ctb.data(str(hours))
                    if minutes:
                        with ctb.start('minutes'):
                            ctb.data(str(minutes))
                    if seconds:
                        with ctb.start('seconds'):
                            ctb.data(str(seconds))
    return ctb.close()


def device_info(type='all'):
    """Request to obtain device’s profile which includes device UDI, filesytem, 
    hardware info and etc.

    :param type: Info sections to be sent, can be 'image', 'hardware', 'filesystem', 
        'udi', 'profile' or 'all', defaults to 'all'
    :type type: str, optional
    :return: XML element to be used as a PnP message body
    :rtype: xml.etree.ElementTree.Element
    """
    ctb = ContextualTreeBuilder()
    with ctb.start('{urn:cisco:pnp:device-info}request'):
        with ctb.start('deviceInfo', {'type': type}):
            pass
    return ctb.close()


def config_upgrade(location, details='all', apply_to='startup', abort_on_fault=True,
                   checksum='', reload=True, reload_reason='PnP config upgrade',
                   reload_delay=0, reload_user='PnP Agent', reload_save=True):
    """Download and update the configuration on the device with the specified 
    configuration.

    :param location: Config file url
    :type location: str
    :param details: Level of error details reported, can be 'biref', 'errors' or
        'all', defaults to 'all'
    :type details: str, optional
    :param apply_to: Configuration to modified, can be 'startup', 'running' or 'AP', 
        defaults to 'startup'
    :type apply_to: str, optional
    :param abort_on_fault: Wether the agent should abort execution when encountering 
        a syntaxt error, defaults to True
    :type abort_on_fault: bool, optional
    :param checksum: Checksum to validate the config file, ignored if empty, 
        defaults to ''
    :type checksum: str, optional
    :param reload: Wether the device should reload after the operation, defaults 
        to True
    :type reload: bool, optional
    :param reload_reason: Reason for the device reload, defaults to 'PnP config 
        upgrade'
    :type reload_reason: str, optional
    :param reload_delay: Time to wait (units unknown) before reloading the device, 
        defaults to 0
    :type reload_delay: int, optional
    :param reload_user: User that initiated the reload, defaults to 'PnP Agent'
    :type reload_user: str, optional
    :param reload_save: Wether to save the config before reloading the device, 
        defaults to True
    :type reload_save: bool, optional
    :return: XML element to be used as a PnP message body
    :rtype: xml.etree.ElementTree.Element
    """
    ctb = ContextualTreeBuilder()
    with ctb.start('{urn:cisco:pnp:config-upgrade}request'):
        with ctb.start('config', {'details': details}):
            with ctb.start('copy'):
                with ctb.start('source'):
                    with ctb.start('location'):
                        ctb.data(location)
                    if checksum:
                        with ctb.start('checksum'):
                            ctb.data(checksum)
                with ctb.start('applyTo'):
                    ctb.data(apply_to)
        if reload:
            with ctb.start('reload'):
                with ctb.start('reason'):
                    ctb.data(reload_reason)
                with ctb.start('delayIn'):
                    ctb.data(str(reload_delay))
                with ctb.start('user'):
                    ctb.data(reload_user)
                with ctb.start('saveConfig'):
                    ctb.data(str(int(reload_save)))
        else:
            with ctb.start('noReload'):
                pass
        if abort_on_fault:
            with ctb.start('abortOnSyntaxFault'):
                pass
    return ctb.close()


def bye():
    """Acknowledge the receipt of PnP response and signal the end of the transaction.
    This is applicable only when the transport protocol is HTTP and HTTPS.

    :return: XML element to be used as a PnP message body
    :rtype: xml.etree.ElementTree.Element
    """
    ctb = ContextualTreeBuilder()
    with ctb.start('{urn:cisco:pnp:work-info}info'):
        with ctb.start('workInfo'):
            with ctb.start('bye'):
                pass
    return ctb.close()


def capability():
    """Request to query what services are supported by the agent.
    
    :raises NotImplementedError: Yet to be implemented
    """
    raise NotImplementedError


def certificate_install():
    """Request the agent to install a trustpoint or trustpool certificate into 
    the devices.
    
    :raises NotImplementedError: Yet to be implemented
    """
    raise NotImplementedError


def cli_config(commands, details='all', check=False, on_fail='continue', write=False):
    """Request to execute a configuration CLI.

    :param commands: List of commands to be executed
    :type commands: list
    :param details: Level of error details reported, can be 'biref', 'errors' or
        'all', defaults to 'all'
    :type details: str, optional
    :param check: Do syntax-check only without applying the config change , defaults 
        to False
    :type check: bool, optional
    :param on_fail: Action to take if a configuration command fails - 'continue' i.e. 
        configure all commands in the request recording status of each command 
        - 'stop' i.e. stop configuring on first failure - 'rollback' i.e. stop 
        configuring at the first error and restore configuration to the state 
        before any configuration was applied (this is only enabled if the archive 
        Cisco IOS CLI is configured0, defaults to 'continue'
    :type on_fail: str, optional
    :param write: Save running config to startup config, defaults to False
    :type write: bool, optional
    :return: XML element to be used as a PnP message body
    :rtype: xml.etree.ElementTree.Element

    .. note:: Extended non-IOS config service not supported
    .. note:: CLI data block not supported
    .. note:: XML data config not supported
    """
    if check:
        config_type = 'configTest', {'details': details}
    else:
        config_type = 'configApply', {'details': details, 'action-on-fail': on_fail}
    ctb = ContextualTreeBuilder()
    with ctb.start('{urn:cisco:pnp:cli-config}request'):
        with ctb.start(*config_type):
            with ctb.start('config-data'):
                with ctb.start('cli-config-data'):
                    for cmd in commands:
                        with ctb.start('cmd'):
                            ctb.data(cmd)
        if write and not check:
            with ctb.start('configPersist'):
                pass
    return ctb.close()


def cli_exec(commands, details='all', max_wait=10, max_size=0, check=False):
    """Request to execute an exec level CLI.

    :param commands: [description]
    :type commands: [type]
    :param details: [description], defaults to 'all'
    :type details: str, optional
    :param max_wait: [description], defaults to 0
    :type max_wait: int, optional
    :param max_size: [description], defaults to 0
    :type max_size: int, optional
    :param check: [description], defaults to False
    :type check: bool, optional
    :raises NotImplementedError: [description]

    .. note:: Return in XLM-PI format not supported
    """
    Dialog = namedtuple(
        'Dialog', ['expect', 'reply', 'match', 'case_sensitive', 'repeat'], 
        defaults=['exact', True, 1]
    )
    ctb = ContextualTreeBuilder()
    with ctb.start('{urn:cisco:pnp:cli-exec}request'):
        if check:
            with ctb.start('execTest', {'details': details}):
                with ctb.start('exec-data'):
                    with ctb.start('cli-exec-data'):
                        for cmd in commands:
                            if isinstance(cmd, str):
                                with ctb.start('cmd'):
                                    ctb.data(cmd)
        else:
            with ctb.start('execCLI', {
                    'maxWait': f'PT{max_wait}S',
                    'maxResponseSize': max_size
                }):
                for cmd in commands:
                    if isinstance(cmd, str):
                        with ctb.start('cmd'):
                            ctb.data(cmd)
                    else:
                        dialog = Dialog(*cmd)
                        with ctb.start('dialog', {'repeat': str(dialog.repeat)}):
                            with ctb.start('expect', {
                                    'match': dialog.match,
                                    'caseSensitive': dialog.case_sensitive
                                }):
                                ctb.data(dialog.expect)
                            with ctb.start('reply'):
                                ctb.data(dialog.reply)
    return ctb.close()


def device_authentication():
    """Request to authenticate the device.
    
    :raises NotImplementedError: Yet to be implemented
    """
    raise NotImplementedError


def file_transfer():
    """Request to copy a file.
    
    :raises NotImplementedError: Yet to be implemented
    """
    raise NotImplementedError


def image_install():
    """Request the agent to install a new image.
    
    :raises NotImplementedError: Yet to be implemented
    """
    raise NotImplementedError


def licensing():
    """Request to install and configure new license.
    
    :raises NotImplementedError: Yet to be implemented
    """
    raise NotImplementedError


def redirection():
    """Request to redirect PnP Profile to use another PnP server.
    
    :raises NotImplementedError: Yet to be implemented
    """
    raise NotImplementedError


def reload():
    """Request the agent to reload.
    
    :raises NotImplementedError: Yet to be implemented
    """
    raise NotImplementedError


def script():
    """Request to execute a script.
    
    :raises NotImplementedError: Yet to be implemented
    """
    raise NotImplementedError


def smu():
    """Request to install a SMU.
    
    :raises NotImplementedError: Yet to be implemented
    """
    raise NotImplementedError


def topology():
    """Request topology of the device.
    
    :raises NotImplementedError: Yet to be implemented
    """
    raise NotImplementedError

