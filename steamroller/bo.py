from steamroller.utils import get_site_packages_dir, ConfigMap
from steamroller.utils import get_pip_path
from paver.defaults import sh
from paver.runtime import debug
from functools import partial
import pkg_resources
import sys
import os
import shutil

def create_fake_buildout():
    root = sys.prefix
    fake_buildout = dict(buildout=dict())
    fake_buildout['buildout']['parts-directory'] = root
    fake_buildout['buildout']['directory'] = root
    fake_buildout['buildout']['offline'] = 'false'

    # FAKE OUT buildout python abstraction
    fake_buildout['buildout']['python'] = 'paver_python'
    fake_buildout.setdefault('paver_python', dict(executable=sys.executable))
    fake_buildout['buildout']['eggs-directory'] = get_site_packages_dir()
    fake_buildout['buildout']['develop-eggs-directory'] = get_site_packages_dir()
    return fake_buildout

def make_POpts():
    # create a options class that does nt require "seen"
    from zc.buildout.buildout import Options, MissingOption
    import zc.buildout
    
    class POpts(Options):

        def __init__(self, buildout, section, data):
            Options.__init__(self, buildout, section, data)
            self.sub_all()

        def sub_all(self):
            for k, v in self._raw.items():
                if '${' in v:
                    self._dosub(k, v)

        def _sub(self, template, seen):
            value = self._template_split(template)
            subs = []
            for ref in value[1::2]:
                s = tuple(ref[2:-1].split(':'))
                if not self._valid(ref):
                    if len(s) < 2:
                        raise zc.buildout.UserError("The substitution, %s,\n"
                                                    "doesn't contain a colon."
                                                    % ref)
                    if len(s) > 2:
                        raise zc.buildout.UserError("The substitution, %s,\n"
                                                    "has too many colons."
                                                    % ref)
                    if not self._simple(s[0]):
                        raise zc.buildout.UserError(
                            "The section name in substitution, %s,\n"
                            "has invalid characters."
                            % ref)
                    if not self._simple(s[1]):
                        raise zc.buildout.UserError(
                            "The option name in substitution, %s,\n"
                            "has invalid characters."
                            % ref)
                # only change from original  (no seen)
                v = self.buildout[s[0]].get(s[1], None)
                if v is None:
                    raise MissingOption("Referenced option does not exist:", *s)
                subs.append(v)
            subs.append('')

            return ''.join([''.join(v) for v in zip(value[::2], subs)])
    return POpts

class BuildoutCfg(object):
    def __init__(self, configmap):
        self.configmap = configmap
        
    def section_get(self, section):
        return partial(self.configmap.parser.get, section)

    def section_dict(self, section, vars=None):
        return dict(self.configmap.get(section, vars=vars))

    @classmethod
    def loadfn(cls, fn):
        return cls(ConfigMap.load(fn))

def hexagonit_cmmi(section, buildoutcfg):
    section_dict = buildoutcfg.section_dict(section)
    root = sys.prefix
    install_dir = os.path.join(root, 'lib', section)
    comp_dir = install_dir + "__compile__"
    if os.path.exists(comp_dir):
        shutil.rmtree(comp_dir)
    if os.path.exists(install_dir):
        debug("Remove %s if you need to reinstall %s" %(install_dir, section))
    else:
        fake_buildout = create_fake_buildout()
        from hexagonit.recipe.cmmi import Recipe
        spi_opt = buildoutcfg.section_get('libspatialindex')
        options = dict(url=spi_opt('url'))

        recipe = Recipe(fake_buildout, section, options)
        recipe.options['location']=install_dir
        recipe.options['prefix']=install_dir
        recipe.options['compile-directory']=comp_dir
        
        recipe.install()

def custom_egg_brute_install(section, bocfg, mod_buildout=None):
    """
    Hack to install packages that may have extensions issues when
    installing.  Reads a zc.recipe.egg:custom buildout section to
    figure out what to do.

    Example buildout config::
    
    [install_it]
    recipe = zc.recipe.egg:custom
    egg = SomePkg
    include-dirs = ${c_dependency:location}/include
    library-dirs = ${c_dependency:location}/lib
    rpath = ${c_dependency:location}/lib
    libraries = c_dependency
    """

    section_dict = bocfg.section_dict(section)
    pkgname = section_dict['egg']
    fake_buildout = create_fake_buildout()
    if callable(mod_buildout):
        fake_buildout = mod_buildout(fake_buildout)

    #@@ buildout must have some sort of req parser???
    rec_klass = pkg_resources.load_entry_point("zc.recipe.egg", 'zc.buildout', 'custom')

    POpts = make_POpts()
    opts = POpts(fake_buildout, section, section_dict)
    recipe = rec_klass(fake_buildout, section, opts)

    sh(get_pip_path() + " install --no-install %s" %pkgname)
    pkg_src = os.path.join(sys.prefix, 'build', pkgname)
    setup_cfg = os.path.join(pkg_src, 'setup.cfg')

    import setuptools.command.setopt
    setuptools.command.setopt.edit_config(setup_cfg, dict(build_ext=recipe.build_ext))

    sh('cd %s; %s setup.py install' %(pkg_src, sys.executable))


