from steamroller.utils import get_site_packages_dir
from functools import partial
import sys

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
        return partial(self, self.configmap.parser.get, section)

    def section_dict(self, section, vars=None):
        return dict(self.configmap.get(section, vars=vars))
