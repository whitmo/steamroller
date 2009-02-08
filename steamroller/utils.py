import os
import sys
from pkg_resources import working_set
from ConfigParser import ConfigParser as CP

def get_site_packages_dir():
    return os.path.dirname(os.__file__) +'/site-packages/'

def get_easy_install_path():
    return os.path.join(sys.prefix, 'bin', 'easy_install')

def get_pip_path():
    return os.path.join(sys.prefix, 'bin', 'pip')

def add_to_sys_path(package):
    site_packages_dir = os.path.dirname(os.__file__) +'/site-packages/'
    for path in os.listdir(site_packages_dir):
        if path.startswith(package):
            newpath = site_packages_dir+path
            if path.endswith('.egg-link'):
                newpath = open(newpath).readline().strip() 
            sys.path.append(newpath)
            working_set.add_entry(newpath)
            
            return
        
def egg_distribution(egg_path):
    if os.path.isdir(egg_path):
        metadata = PathMetadata(egg_path,os.path.join(egg_path,'EGG-INFO'))
    else:
        metadata = EggMetadata(zipimport.zipimporter(egg_path))
    return Distribution.from_filename(egg_path,metadata=metadata)

def update_pth(egg_path):
    spd = get_site_packages_dir()
    easy_install_pth = os.path.join(spd, "easy-install.pth")
    distros = PthDistributions(easy_install_pth)
    distros.add(egg_distribution(egg_path))
    distros.save()

def sjoin(*args):
    return " ".join(args)    

class ConfigMap(object):

    def __init__(self, parser):
        self.parser = parser
        self.sects = parser.sections()

    def __iter__(self):
        for sname in self.sects:
            yield sname
            
    def __getitem__(self, idx):
        return dict(self.get(idx))

    def get(self, idx, vars=None):
        return self.parser.items(idx, vars=vars)

    @classmethod
    def load(cls, fname):
        parser = CP()
        parser.read(fname)
        return cls(parser)
