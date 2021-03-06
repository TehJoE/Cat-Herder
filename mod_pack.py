import os

from file_handling import mkdir
from mod_file import Mod_File
from pprint import pprint
from operator import itemgetter


class Mod_Pack(dict):
    attribs = sorted(('pack_name',
                      'pack_version',
                      'download_cache_folder',
                      'install_folder',
                      'minecraft_version'))

    def __init__(self, pack_name, pack_version, download_cache_folder, install_folder, minecraft_version):
        for a in self.attribs:
            self[a] = None
        self.mod_files = list()
        self['pack_name'] = pack_name
        self['pack_version'] = pack_version
        self['download_cache_folder'] = download_cache_folder
        self['install_folder'] = install_folder
        self['minecraft_version'] = minecraft_version

    def install_server(self):
        self.mod_files.append(self.minecraft_server_jar())

        for f in self.mod_files:
            if not f['required_on_server']:
                # pass - note that currently, there are some files (i.e. authlib-1.5.13.jar) which don't have an install path, so can't be handled.
                continue

            try:
                f.validate_attributes()
            except AssertionError:
                print ("INSTALLATION FAILED - MOD FILE DEFINITION INVALID.")
                import pprint

                pprint.pprint(f)
                return 'FAILURE'

            print ('-')

            mkdir(self['download_cache_folder'])
            os.chdir(self['download_cache_folder'])
            f.download("server")

            mkdir(self['install_folder'])
            os.chdir(self['install_folder'])
            f.install(self, "server")

        print ('-\r\nWriting eula.txt')
        os.chdir(self['install_folder'])
        with open('eula.txt', 'w') as eula:
            eula.write("eula=true")


    def minecraft_server_jar(self):
        ver = self['minecraft_version']
        mf = Mod_File()
        mf[
            'download_url_primary'] = "http://s3.amazonaws.com/Minecraft.Download/versions/{v}/minecraft_server.{v}.jar".format(
            v=ver)
        mf['install_filename'] = 'minecraft_server.{v}.jar'.format(v=ver)
        mf['required_on_server'] = True
        mf['required_on_client'] = False
        mf['name'] = "Minecraft Server Jar"
        mf['install_method'] = 'copy'
        mf['install_path'] = './'
        mf['optional?'] = False
        mf['install_optional?'] = True
        return mf

    def print_mod_files_list(self):
        s = sorted(self.mod_files, key=itemgetter('optional?','install_optional?'))
        print"""
--------------------------------------------------------------------------------
Mod pack component listing
i = selected for install.
o = optional mod.
S = server mod.
C = client mod.
--------------------------------------------------------------------------------"""
        bits = [' ',]*5
        for m in s:
            bits[0] = 'i' if m['install_optional?'] else ' '
            bits[1] = 'o' if m['optional?'] else ' '
            bits[2] = 'S' if m['required_on_server'] else ' '
            bits[3] = 'C' if m['required_on_client'] else ' '

            print ''.join(bits) + m['install_filename']