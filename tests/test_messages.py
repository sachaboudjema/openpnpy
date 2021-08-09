from openpnpy.messages import PnpMessage, device_info_dict


class TestPnpDeviceInfo:

    def test_to_dict(self):
        info = device_info_dict(PnpMessage.from_string('''
            <pnp udi="PID:CISCO3945-CHASSIS,VID:V02,SN:FTX1503AH3V" version="1.0" xmlns="urn:cisco:pnp">
                <response correlator="CiscoPnP-1.0-40830" success="1" xmlns="urn:cisco:pnp:device-info">
                    <udi>
                        <primary-chassis>PID:CISCO3945-CHASSIS,VID:V02,SN:FTX1503AH3V</primary-chassis>
                    </udi>
                    <imageInfo>
                        <versionString>15.5(20140930:030825)</versionString>
                        <imageFile>flash0:c3900-ipbasek9-mz.SSA</imageFile>
                        <imageHash/>
                        <returnToRomReason>reload</returnToRomReason>
                        <bootVariable>flash0:c3900-ipbasek9-mz.SSA,12;</bootVariable>
                        <bootLdrVariable/>
                        <configVariable/>
                        <configReg>0x0</configReg>
                        <configRegNext/>
                    </imageInfo>
                    <hardwareInfo>
                        <hostname>WSMA-3945</hostname>
                        <vendor>Cisco</vendor>
                        <platformName>CISCO3945-CHASSIS</platformName>
                        <processorType/>
                        <hwRevision>1.0</hwRevision>
                        <mainMemSize>1010827264</mainMemSize>
                        <ioMemSize>0</ioMemSize>
                        <boardId>FTX1503AH3V</boardId>
                        <boardReworkId/>
                        <processorRev/>
                        <midplaneVersion/>
                        <location/>
                    </hardwareInfo>
                    <fileSystemList>
                        <fileSystem freespace="141590528" name="flash0" readable="true" size="512065536" type="disk" writable="true"/>
                    </fileSystemList>
                    <profileInfo>
                        <profile profile-name="pnp_profile" created-by='PnP-DHCP' discovery-created="true">
                            <primary-server>
                                <protocol>http</protocol>
                                <server-address>
                                    <ipv4>10.0.0.1</ipv4>
                                </server-address>
                            </primary-server>
                            <backup-server>
                                <protocol>http</protocol>
                                <server-address>
                                    <ipv4>10.0.0.2</ipv4>
                                    <port>8080</port>
                                </server-address>
                            </backup-server>
                        </profile>
                    </profileInfo>
                </response>
            </pnp>
            '''))
        assert info['PID'] == 'CISCO3945-CHASSIS'
        assert info['VID'] == 'V02'
        assert info['SN'] == 'FTX1503AH3V'
        assert info['primary-chassis']['PID'] == 'CISCO3945-CHASSIS'
        assert info['primary-chassis']['VID'] == 'V02'
        assert info['primary-chassis']['SN'] == 'FTX1503AH3V'
        assert info['versionString'] == '15.5(20140930:030825)'
        assert info['imageFile'] == 'flash0:c3900-ipbasek9-mz.SSA'
        assert info['bootVariable'] == 'flash0:c3900-ipbasek9-mz.SSA,12;'
        assert info['returnToRomReason'] == 'reload'
        assert info['bootLdrVariable'] is None
        assert info['configReg'] == '0x0'
        assert info['imageHash'] is None
        assert info['configVariable'] is None
        assert info['configRegNext'] is None
        assert info['hostname'] == 'WSMA-3945'
        assert info['vendor'] == 'Cisco'
        assert info['platformName'] == 'CISCO3945-CHASSIS'
        assert info['hwRevision'] == '1.0'
        assert info['mainMemSize'] == '1010827264'
        assert info['ioMemSize'] == '0'
        assert info['boardId'] == 'FTX1503AH3V'
        assert info['boardReworkId'] is None
        assert info['processorRev'] is None
        assert info['midplaneVersion'] is None
        assert info['location'] is None
        assert info['processorType'] is None
        assert info['fileSystemList'][0]['name'] == 'flash0'
        assert info['fileSystemList'][0]['freespace'] == '141590528'
        assert info['fileSystemList'][0]['readable'] == 'true'
        assert info['fileSystemList'][0]['size'] == '512065536'
        assert info['fileSystemList'][0]['type'] == 'disk'
        assert info['fileSystemList'][0]['writable'] == 'true'
        assert info['profileInfo'][0]['profile-name'] == 'pnp_profile'
        assert info['profileInfo'][0]['created-by'] == 'PnP-DHCP'
        assert info['profileInfo'][0]['discovery-created'] == 'true'
        assert info['profileInfo'][0]['primary-server']['protocol'] == 'http'
        assert info['profileInfo'][0]['primary-server']['server-address'] == '10.0.0.1'
        assert info['profileInfo'][0]['backup-server']['protocol'] == 'http'
        assert info['profileInfo'][0]['backup-server']['server-address'] == '10.0.0.2'
        assert info['profileInfo'][0]['backup-server']['port'] == '8080'