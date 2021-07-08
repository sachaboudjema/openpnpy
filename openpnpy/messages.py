from xml.etree import ElementTree
from contextlib import contextmanager


__all__ = ['backoff', 'device_info', 'config_upgrade']


class ContextualTreeBuilder(ElementTree.TreeBuilder):
    """Convinience class to allow using contexts with TreeBuilder.
    """
    @contextmanager
    def start(self, tag, attrib={}):
        try:
            yield super().start(tag, attrib)
        finally:
            super().end(tag)


def backoff(seconds=0, reason='No Reason'):
    """Inform the PnP agent to connect back after some time.

    :param seconds: Seconds to wait before connecting back, defaults to 0
    :type seconds: int, optional
    :param reason: Reason of the backoff request, defaults to 'No Reason'
    :type reason: str, optional
    :return: XML element to be used as a PnP message body
    :rtype: xml.etree.ElementTree.Element
    """
    ctb = ContextualTreeBuilder()
    with ctb.start('{urn:cisco:pnp:backoff}request'):
        with ctb.start('backoff'):
            with ctb.start('reason'):
                ctb.data(reason)
            with ctb.start('callBackAfter'):
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


def cli_config():
    """Request to execute a configuration CLI.
    
    :raises NotImplementedError: Yet to be implemented
    """
    raise NotImplementedError


def cli_exec():
    """Request to execute a exec level CLI.
    
    :raises NotImplementedError: Yet to be implemented
    """
    raise NotImplementedError


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

