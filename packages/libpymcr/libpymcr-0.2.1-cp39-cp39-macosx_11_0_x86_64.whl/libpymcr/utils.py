import os
import sys
import glob
import platform
import zipfile
import lzma
import ast
import inspect
import dis
import linecache
import shutil
from pathlib import Path


OPERATOR_NAMES = {
    "CALL_FUNCTION", "CALL_FUNCTION_VAR", "CALL_FUNCTION_KW", "CALL_FUNCTION_VAR_KW", "CALL",
    "UNARY_POSITIVE", "UNARY_NEGATIVE", "UNARY_NOT", "UNARY_CONVERT", "UNARY_INVERT", "GET_ITER",
    "BINARY_POWER", "BINARY_MULTIPLY", "BINARY_DIVIDE", "BINARY_FLOOR_DIVIDE", "BINARY_TRUE_DIVIDE",
    "BINARY_MODULO", "BINARY_ADD", "BINARY_SUBTRACT", "BINARY_SUBSCR", "BINARY_LSHIFT",
    "BINARY_RSHIFT", "BINARY_AND", "BINARY_XOR", "BINARY_OR",
    "INPLACE_POWER", "INPLACE_MULTIPLY", "INPLACE_DIVIDE", "INPLACE_TRUE_DIVIDE", "INPLACE_FLOOR_DIVIDE",
    "INPLACE_MODULO", "INPLACE_ADD", "INPLACE_SUBTRACT", "INPLACE_LSHIFT", "INPLACE_RSHIFT",
    "INPLACE_AND", "INPLACE_XOR", "INPLACE_OR", "COMPARE_OP", "SET_UPDATE", "BUILD_CONST_KEY_MAP",
    "CALL_FUNCTION_EX", "LOAD_METHOD", "CALL_METHOD", "DICT_MERGE", "DICT_UPDATE", "LIST_EXTEND",
}

MLVERDIC = {f'R{rv[0]}{rv[1]}':f'9.{vr}' for rv, vr in zip([[yr, ab] for yr in range(2017,2023) for ab in ['a', 'b']], range(2, 14))}
MLVERDIC.update({'R2023a':'9.14', 'R2023b':'23.2'})
MLVERDIC.update({f'R20{yr}{ab}':f'{yr}.{1 if ab=="a" else 2}' for yr in range(24,26) for ab in ['a','b']})

MLEXEFOUND = {}

def get_nret_from_dis(frame):
    # Tries to get the number of return values for a function
    # Code adapted from Mantid/Framework/PythonInterface/mantid/kernel/funcinspect.py
    ins_stack = []
    call_fun_locs = {}
    start_i = 0
    start_offset = 0
    last_i = frame.f_lasti
    for index, ins in enumerate(dis.get_instructions(frame.f_code)):
        ins_stack.append(ins)
        if ins.opname in OPERATOR_NAMES:
            call_fun_locs[start_offset] = start_i
            start_i = index
            start_offset = ins.offset
    call_fun_locs[start_offset] = start_i
    if last_i not in call_fun_locs:
        return 1  # Some error in the disassembly
    last_fun_offset = call_fun_locs[last_i]
    last_i_name = ins_stack[last_fun_offset].opname
    next_i_name = ins_stack[last_fun_offset + 1].opname
    if last_i_name == 'DICT_MERGE' and next_i_name in OPERATOR_NAMES:
        last_fun_offset += 1
        last_i = ins_stack[last_fun_offset + 1].offset
    res_i_name = ins_stack[last_fun_offset + 1].opname
    if res_i_name == 'POP_TOP':
        return 0
    elif res_i_name == 'STORE_FAST' or res_i_name == 'STORE_NAME':
        return 1
    elif res_i_name == 'UNPACK_SEQUENCE':
        return ins_stack[last_fun_offset + 1].argval
    elif res_i_name == 'LOAD_FAST' or res_i_name == 'LOAD_NAME':
        return 1  # Dot-assigment to a member or in a multi-line call
    elif res_i_name == 'DUP_TOP':
        raise NotImplementedError('libpymcr does not support multiple assignment')
    else:
        return 1  # Probably in a multi-line call


def get_nlhs(name=None):
    # Tries to get the number of return values for a named (Matlab) function
    # Assumes that it's called as a method of the `m` or Matlab() object

    def get_branch_of_call(astobj, parent=[]):
        if isinstance(astobj, ast.Call) and isinstance(astobj.func, ast.Attribute) and astobj.func.attr == name:
            return astobj
        for x in ast.iter_child_nodes(astobj):
            rv = get_branch_of_call(x, parent)
            if rv:
                parent.append(astobj)
                return parent
        raise SyntaxError('Empty syntax tree')

    def get_nret_from_call(caller):
        if isinstance(caller, ast.Call):
            return 1                              # f1(m.<func>())
        elif isinstance(caller, ast.Assign):
            targ = caller.targets[0]
            if isinstance(targ, ast.Tuple):
                return len(targ.elts)             # x, y = m.<func>()
            elif isinstance(targ, ast.Name):
                return 1                          # x = m.<func>()
        elif isinstance(caller, ast.Expr):
            return 0                              # m.<func>()
        elif isinstance(caller, ast.Compare):
            return 1                              # x == m.<func>()
        else:
            return 1

    # First gets the Python line where its called, then convert it to an abstract syntax
    # tree and parse that to get the branch which leads to this call (in reverse order)
    # The first element of this branch is the direct caller of this function
    frame = inspect.currentframe().f_back.f_back
    call_line = linecache.getline(frame.f_code.co_filename, frame.f_lineno)
    try:
        ast_branch = get_branch_of_call(ast.parse(call_line))
    except SyntaxError:
        return get_nret_from_dis(frame)
    else:
        return get_nret_from_call(ast_branch[0])


def get_version_from_ctf(ctffile):
    with zipfile.ZipFile(ctffile, 'r') as ctf:
        manifest = ctf.read('.META/manifest.xml').decode('ascii')
        for tag in manifest.split('><'):
            if 'mcr-major-version' in tag:
                ver = dict([v.split("=") for v in tag.split() if 'mcr' in v])
                ver = [ver[v].replace('"', '') for v in ['mcr-major-version', 'mcr-minor-version']]
                return "{}.{}".format(*ver)


def get_matlab_from_registry(version=None):
    # Searches for the Mathworks registry key and finds the Matlab path from that
    if version is not None and version.startswith('R') and version in MLVERDIC.keys():
        version = MLVERDIC[version]
    retval = []
    try:
        import winreg
    except ImportError:
        return None
    for installation in ['MATLAB', 'MATLAB Runtime', 'MATLAB Compiler Runtime']:
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, f'SOFTWARE\\MathWorks\\{installation}') as key:
                versions = [winreg.EnumKey(key, k) for k in range(winreg.QueryInfoKey(key)[0])]
        except (FileNotFoundError, OSError):
            pass
        else:
            if version is not None:
                versions = [v for v in versions if v == version]
            for v in versions:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, f'SOFTWARE\\MathWorks\\{installation}\\{v}') as key:
                    retval.append(winreg.QueryValueEx(key, 'MATLABROOT')[0])
    return retval


class DetectMatlab(object):
    def __init__(self, version=None):
        self.ver = version
        self.PLATFORM_DICT = {'Windows': ['PATH', 'dll', '', '.exe', ';'], 'Linux': ['LD_LIBRARY_PATH', 'so', 'libmw', '', ':'],
                              'Darwin': ['DYLD_LIBRARY_PATH', 'dylib', 'libmw', '', ':']}
        # Note that newer Matlabs are 64-bit only
        self.ARCH_DICT = {'Windows': {'64bit': 'win64', '32bit': 'pcwin32'},
                          'Linux': {'64bit': 'glnxa64', '32bit': 'glnx86'},
                          'Darwin': {'64bit': 'maci64', '32bit': 'maci'}}
        # https://uk.mathworks.com/help/compiler/mcr-path-settings-for-run-time-deployment.html
        DIRS = ['runtime', os.path.join('sys', 'os'), 'bin', os.path.join('extern', 'bin')]
        self.REQ_DIRS = {'Windows':[DIRS[0]], 'Darwin':DIRS[:3], 'Linux':DIRS}
        self.system = platform.system()
        if self.system not in self.PLATFORM_DICT:
            raise RuntimeError(f'Operating system {self.system} is not supported.')
        (self.path_var, self.ext, self.lib_prefix, self.exe_ext, self.sep) = self.PLATFORM_DICT[self.system]
        self.arch = self.ARCH_DICT[self.system][platform.architecture()[0]]
        self.required_dirs = self.REQ_DIRS[self.system]
        self.dirlevel = ('..', '..')
        self.matlab_exe = ''.join(('matlab', self.exe_ext))
        if self.ver is None:
            self.file_to_find = self.matlab_exe
            self.dirlevel = ('..',)
        elif self.system == 'Windows':
            self.file_to_find = ''.join((self.lib_prefix, 'mclmcrrt', self.ver.replace('.','_'), '.', self.ext))
        elif self.system == 'Linux':
            self.file_to_find = ''.join((self.lib_prefix, 'mclmcrrt', '.', self.ext, '.', self.ver))
        elif self.system == 'Darwin':
            self.file_to_find = ''.join((self.lib_prefix, 'mclmcrrt', '.', self.ver, '.', self.ext))

    @property
    def ver(self):
        return self._ver

    @ver.setter
    def ver(self, val):
        if val is None:
            self._ver = None
        else:
            self._ver = str(val)
            if self._ver.startswith('R') and self._ver in MLVERDIC.keys():
                self._ver = MLVERDIC[self._ver]

    def _append_exe(self, exe_file):
        if exe_file is not None:
            global MLEXEFOUND
            if self.ver not in MLEXEFOUND:
                MLEXEFOUND[self.ver] = os.path.abspath(Path(exe_file).parents[1])

    def find_version(self, root_dir, suppress_output=False):
        if not suppress_output:
            print(f'Searching for Matlab {self.ver} in {root_dir}')
        def find_file(path, filename, max_depth=3):
            """ Finds a file, will return first match"""
            for depth in range(max_depth + 1):
                dirglobs = f'*{os.sep}'*depth
                files = glob.glob(f'{path}{os.sep}{dirglobs}{filename}')
                files = list(filter(os.path.isfile, files))
                if len(files) > 0:
                    return files[0]
            return None
        lib_file = find_file(root_dir, self.file_to_find)
        if lib_file is not None:
            ml_path = os.path.abspath(os.path.join(os.path.dirname(lib_file), *self.dirlevel))
            if not suppress_output:
                print(f'Found Matlab {self.ver} {self.arch} at {ml_path}')
            return ml_path
        else:
            self._append_exe(find_file(root_dir, self.matlab_exe))
            return None

    def guess_path(self, mlPath=[], suppress_output=False):
        GUESSES = {'Windows': [r'C:\Program Files\MATLAB', r'C:\Program Files (x86)\MATLAB',
                               r'C:\Program Files\MATLAB\MATLAB Runtime', r'C:\Program Files (x86)\MATLAB\MATLAB Runtime'],
                   'Linux': ['/usr/local/MATLAB', '/opt/MATLAB', '/opt', '/usr/local/MATLAB/MATLAB_Runtime'],
                   'Darwin': ['/Applications/MATLAB', '/Applications/']}
        if self.system == 'Windows':
            mlPath += get_matlab_from_registry(self.ver) + GUESSES['Windows']
        if 'MATLABEXECUTABLE' in os.environ: # Running in CI
            ml_env = os.environ['MATLABEXECUTABLE']
            if self.system == 'Windows' and ':' not in ml_env:
                pp = ml_env.split('/')[1:]
                ml_env = pp[0] + ':\\' + '\\'.join(pp[1:])
            mlPath += [os.path.abspath(os.path.join(ml_env, *self.dirlevel))]
        for possible_dir in mlPath + GUESSES[self.system]:
            if os.path.isdir(possible_dir):
                rv = self.find_version(possible_dir, suppress_output)
                if rv is not None:
                   return rv
        return None

    def guess_from_env(self, ld_path=None):
        if ld_path is None:
            ld_path = os.getenv(self.path_var)
        if ld_path is None:
            return None
        for possible_dir in ld_path.split(self.sep):
            if os.path.exists(os.path.join(possible_dir, self.file_to_find)):
                return os.path.abspath(os.path.join(possible_dir, *self.dirlevel))
        return None

    def guess_from_syspath(self, suppress_output=False):
        matlab_exe = shutil.which('matlab')
        if matlab_exe is None:
            return None if self.system == 'Windows' else self.guess_from_env('PATH')
        mlbinpath = os.path.dirname(os.path.realpath(matlab_exe))
        return self.find_version(os.path.abspath(os.path.join(mlbinpath, '..')), suppress_output)

    #def env_not_set(self, suppress_output=False):
    #    # Determines if the environment variables required by the MCR are set
    #    if self.path_var not in os.environ:
    #        return True
    #    rt = os.path.join('runtime', self.arch)
    #    pv = os.getenv(self.path_var).split(self.sep)
    #    for path in [dd for dd in pv if rt in dd]:
    #        if self.find_version(os.path.join(path, *self.dirlevel), suppress_output) is not None:
    #            return False
    #    return True

    #def set_environment(self, mlPath=None):
    #    if mlPath is None:
    #        mlPath = self.guess_path()
    #    if mlPath is None:
    #        raise RuntimeError('Could not find Matlab')
    #    req_matlab_dirs = self.sep.join([os.path.join(mlPath, sub, self.arch) for sub in self.required_dirs])
    #    if self.path_var not in os.environ:
    #        os.environ[self.path_var] = req_matlab_dirs
    #    else:
    #        os.environ[self.path_var] += self.sep + req_matlab_dirs
    #    return None


def checkPath(runtime_version, mlPath=None, error_if_not_found=True, suppress_output=False):
    """
    Sets the environmental variables for Win, Mac, Linux

    :param mlPath: Path to the SDK i.e. '/MATLAB/MATLAB_Runtime/v96' or to the location where matlab is installed
    (MATLAB root directory)
    :return: None
    """

    # We use a class to try to get the necessary variables.
    obj = DetectMatlab(runtime_version)

    if mlPath:
        if not os.path.exists(os.path.join(mlPath)):
            if not os.path.exists(mlPath):
                raise FileNotFoundError(f'Input Matlab folder {mlPath} not found')
    else:
        mlPath = obj.guess_from_env()
        if mlPath is None:
            mlPath = obj.guess_from_syspath()
        if mlPath is None:
            mlPath = obj.guess_path()
            if mlPath is not None:
                ld_path = obj.sep.join([os.path.join(mlPath, sub, obj.arch) for sub in obj.required_dirs])
                os.environ[obj.path_var] = ld_path
                #print('Set ' + os.environ.get(obj.path_var))
            elif error_if_not_found:
                if obj.ver in MLEXEFOUND:
                    raise RuntimeError(f'Found Matlab executable for version {runtime_version} ' \
                                        'but could not find Compiler Runtime libraries.\n' \
                                        'Please install the Matlab Compiler Runtime SDK toolbox ' \
                                        'for this version of Matlab')
                else:
                    raise RuntimeError(f'Cannot find Matlab version {runtime_version}')
        #else:
        #    print('Found: ' + os.environ.get(obj.path_var))

    return mlPath


def _tobestripped(info):
    if '.mex' in info.filename and 'auth' not in info.filename:
        return True
    elif info.filename.endswith('mcstas'):
        return True
    elif info.filename.endswith('exe'):
        return True
    elif info.filename.endswith('libmpi.so.0'):
        return True
    return False


def stripmex(version_string, ctfdir='CTF', writemex=False, prefix='pace'):
    # Strips out mex and large files from a zipped CTF.
    ctffile = os.path.join(ctfdir, f'{prefix}_{version_string[1:]}.ctf')
    if not os.path.exists(ctffile):
        raise RuntimeError(f'CTF "{ctffile}" not created.')
    with zipfile.ZipFile(ctffile, 'r') as ctf_in:
        if writemex:
            with lzma.open(os.path.join(ctfdir, f'mexes.xz'), 'w') as xzf:
                with zipfile.ZipFile(xzf, 'w', zipfile.ZIP_STORED) as ctf_out:
                    for info in [v for v in ctf_in.infolist() if _tobestripped(v)]:
                        ctf_out.writestr(info, ctf_in.read(info))
        with lzma.open(os.path.join(ctfdir, f'nomex_{version_string[1:]}.xz'), 'w') as xzf:
            with zipfile.ZipFile(xzf, 'w', zipfile.ZIP_STORED) as ctf_out:
                for info in [v for v in ctf_in.infolist() if not _tobestripped(v)]:
                    ctf_out.writestr(info, ctf_in.read(info))


def recombinemex(version_string, ctfdir, prefix='pace', outfilename=None):
    mexes = os.path.join(ctfdir, 'mexes.xz')
    ctfstub = os.path.join(ctfdir, f'nomex_{version_string[1:]}.xz')
    if not os.path.exists(mexes) or not os.path.exists(ctfstub):
        raise RuntimeError(f'Mexes archive "{mexes}" or ctf stub "{ctfstub}" does not exist.')
    if outfilename is None:
        outfilename = os.path.join(ctfdir, f'{prefix}_{version_string[1:]}.ctf')
    with zipfile.ZipFile(outfilename, 'w', zipfile.ZIP_DEFLATED) as ctf_out:
        with lzma.open(ctfstub, 'r') as xz_stub:
            with zipfile.ZipFile(xz_stub, 'r') as zip_in:
                for info in [v for v in zip_in.infolist()]:
                    ctf_out.writestr(info, zip_in.read(info))
        with lzma.open(mexes, 'r') as xz_mex:
            with zipfile.ZipFile(xz_mex, 'r') as zip_in:
                for info in [v for v in zip_in.infolist()]:
                    if info.filename.startswith(f'fsroot/{prefix}'):
                        info.filename = f'fsroot/{prefix}_{version_string[1:]}/' + '/'.join(info.filename.split('/')[2:])
                    ctf_out.writestr(info, zip_in.read(info))

