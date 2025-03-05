from __future__ import annotations
import sys
import os
from pathlib import Path
import re
import shutil
import json
import argparse
import shlex
import warnings
from subprocess import check_output, check_call, CalledProcessError

#===============================================================================
_PY = f"{'.'.join(str(v) for v in sys.version_info[:2])}"
_CONFIG_DIR = Path.home()/'.config'/'partis-basis'
_CONFIG_FILE = _CONFIG_DIR/'config.json'

#===============================================================================
# directory for Container Device Interface (CDI) configs
_CDI_DIR = _CONFIG_DIR/'cdi'
_CDI_DIRS = [_CDI_DIR, Path('/etc/cdi'), Path('/var/run/cdi')]

if not _CDI_DIR.exists():
  _CDI_DIR.mkdir(exist_ok=True, parents=True)

#===============================================================================
_CONFIG = {}
_CONFIG_DEFAULTS = {
  "default_image": "library://kcdodd/basis/ubuntu-22.04-basis:0.0.4"}

if _CONFIG_FILE.exists():
  _CONFIG = json.loads(_CONFIG_FILE.read_bytes())

_CONFIG = _CONFIG_DEFAULTS|_CONFIG

#===============================================================================
APPS = ['bash', 'fish', 'manage']

PASS_ENV = frozenset([
  'PATH',
  'LD_LIBRARY_PATH',
  'USER',
  'LOGNAME',
  'LANG',
  'LANGUAGE',
  'LC_CTYPE',
  'TERM',
  'COLORFGBG',
  'COLORTERM',
  'LSCOLORS',
  'LS_COLORS',
  'DISPLAY',
  'NO_COLOR',
  'PY_COLORS',
  'CLICOLOR',
  'CLICOLOR_FORCE',
  'FORCE_COLOR',
  'NOHM_MIN_LOG_LEVEL',
  'BASIS_DEBUG',
  'XLA_PYTHON_CLIENT_ALLOCATOR',
  'XLA_PYTHON_CLIENT_PREALLOCATE',
  'TF_CPP_MIN_LOG_LEVEL',
  'TF_CPP_MAX_VLOG_LEVEL',
  'TF_CPP_VMODULE',
  'PJRT_NPROC',
  'XLA_FLAGS'])

MPI_ENV_REC = re.compile('|'.join([
  # OpenMPI:
  r'(OMPI_*\w+)',
  r'(PMIX_*\w+)',
  r'(OPAL_*\w+)',
  r'(ORTE_*\w+)',

  # MPICH:
  r'(MPIR_*\w+)',
  r'(PMI_*\w+)',
  r'(PMIX_*\w+)',
  r'(HYDRA_*\w+)',

  # Intel MPI:
  r'(I_MPI_*\w+)',
  r'(MPIR_*\w+)',
  r'(PMI_*\w+)',
  r'(PMIX_*\w+)',
  r'(HYDRA_*\w+)',

  # MVAPICH2:
  r'(MV2_*\w+)',
  r'(MPIR_*\w+)',
  r'(PMI_*\w+)',
  r'(PMIX_*\w+)',
  r'(HYDRA_*\w+)']))

#===============================================================================
_nvidia_ctk = shutil.which('nvidia-ctk')

if _nvidia_ctk is not None:
  name = 'nvidia.yaml'

  # if nvidia container tooklkit is installed, check/generate CDI config
  for dir in _CDI_DIRS:
    if (dir/name).exists():
      break

  else:
    _nvidia_cdi = _CDI_DIR/name

    try:
      check_call([_nvidia_ctk, 'cdi', 'generate', f'--output={_nvidia_cdi}'])
    except Exception as e:
      warnings.warn(f"Could not create nvidia Container Device Interface (CDI) config: {e}")

#===============================================================================
def _basis(*,
    image: str|None = None,
    basis: Path|None = None,
    create: bool = True) -> tuple[str, Path, Path]:

  if basis is None:
    venv: str|Path = os.environ.get('VIRTUAL_ENV', '')

    if venv:
      venv = Path(venv).resolve()

    if not (venv and venv.exists()):
      raise FileNotFoundError(f"No active virtual environment: {venv}")

    basis = venv/'.basis'

  default = basis/'mods'/'environment'/'.version'
  created = False

  if create and not basis.exists():
    basis.mkdir(parents=True)
    created = True

  basis_config_file = basis/'.config'/'basis'

  if basis_config_file.exists():
    basis_config = json.loads(basis_config_file.read_text())
    _image = basis_config['image']

    if image is None:
      # image originally used to create basis directory
      image = _image

    elif image != _image:
      print("Warning: Basis directory originally created using different image, behavior may be undefined.")
      print(f" original imag: {_image!r}")

  else:
    basis_config_file.parent.mkdir(exist_ok=True, parents=True)

    if created:
      if image is None:
        image = _CONFIG.get('default_image')

      basis_config_file.write_text(json.dumps({
        'image': str(image)}))

    else:
      # fixup environment created without config file
      # NOTE: hardcoded assumption that all older versions created with this image
      basis_config_file.write_text(json.dumps({
        'image': "library://kcdodd/basis/ubuntu-22.04-basis:0.0.2"}))

  assert isinstance(image, str)

  return image, basis, default

#===============================================================================
def init(image, basis, cwd, python):
  name = 'init'

  singularity = shutil.which('singularity')

  if not singularity:
    print("Error: Program 'singularity' not found")
    return 1

  image, basis, default = _basis(basis=basis, image=image)
  env_dir = basis/'envs'/name

  if env_dir.is_dir() and any(env_dir.iterdir()):
    print(f"Cannot initialize non-empty directory: {env_dir}")
    return 1

  pwd = str(cwd)
  env = {
    k:v
    for k,v in os.environ.items()
    if k in PASS_ENV or MPI_ENV_REC.fullmatch(k)}

  def _run(*cmd):
    check_call([
      singularity,
      'run',
      '--app', 'manage',
      '--no-home',
      '--pwd', str(pwd),
      '--bind', f"{basis}:/basis",
      str(image),
      *cmd],
      env=env)

  _run('create', name, str(python))

  default.write_text(f'#%Module\nset ModulesVersion {name}')

  return 0

#===============================================================================
def run(image, basis, app, work, cwd, cmd, device):
  singularity = shutil.which('singularity')
  oci_mode = False

  # nvccli = shutil.which('nvidia-container-cli')

  if not singularity:
    print("Error: Program 'singularity' not found")
    return 1

  _owner = Path(singularity).owner()

  if _owner != 'root' and _owner == os.getlogin():
    oci_mode = True

  # if nvccli:
  #   runhelp = check_output([singularity, 'run', '--help']).decode('utf-8')

  #   if '--nvccli' not in runhelp:
  #     print("Warning: singularity version must be >= 3.9 to utilize nvidia-container-toolkit found on host")
  #     nvccli = None

  work = work.resolve()

  image, basis, default = _basis(basis=basis, image=image)

  env = {
    k:v
    for k,v in os.environ.items()
    if k in PASS_ENV or MPI_ENV_REC.fullmatch(k)}

  pwd = str(cwd)

  extra_args = []

  # if nvccli:
  #   # generate
  #   extra_args.extend(['--nv', '--nvccli', '--oci'])

  if device:
    # currently CDI device only supported in OCI mode
    oci_mode = True
    extra_args.extend([
      '--device', device])

  if oci_mode:
    extra_args.extend([
      '--oci',
      '--no-compat',
      '--cdi-dirs', ','.join(str(v) for v in _CDI_DIRS)])

  cmd_singularity = [
    singularity,
    'run',
    '--app',
    app,
    *extra_args,
    '--no-home',
    '--pwd', str(pwd),
    '--bind', f"{basis}:/basis",
    '--bind', f"{work}:/work",
    '--bind', f"{pwd}:{pwd}",
    str(image),
    *cmd]

  print(f"image: {image}")
  print(f"  app: {app}")
  print(f"basis: {basis}")
  print(f" work: {work}")
  print(f"  cwd: {cwd}")
  print(f" exec: {shlex.join(cmd)}")
  print(f"Running: {shlex.join(cmd_singularity[1:])}")

  # flush stdout before replacing process
  sys.stdout.flush()
  sys.stderr.flush()
  os.execve(cmd_singularity[0], cmd_singularity, env)

#===============================================================================
def _cuda_info(nvccli):
  info = check_output([nvccli, 'info', '--csv']).decode('utf-8')
  lines = info.splitlines()
  nvrm_version, cuda_version = lines[1].split(',')

  nvrm_version = tuple(int(v) for v in nvrm_version.split('.'))
  cuda_version = tuple(int(v) for v in cuda_version.split('.'))

  return nvrm_version, cuda_version

#===============================================================================
def main():

  parser = argparse.ArgumentParser(
      description="partis-basis runner for singularity container based environments")

  parser.add_argument(
      '-i', '--image',
      help="",
      type=str,
      default=None)

  parser.add_argument(
      '-a', '--app',
      help=f"{', '.join(APPS)}",
      choices=APPS,
      default='bash')

  parser.add_argument(
      '-b', '--basis',
      help="",
      type=Path,
      default=None)

  parser.add_argument(
      '--init',
      dest='init',
      action='store_true',
      help="Create and initialize basis directory if it doesn't exist")

  parser.add_argument(
    '--python',
    type=str,
    default=_PY)

  parser.add_argument(
    '--device',
    type=str,
    default=None)

  parser.add_argument(
      '-w', '--work',
      help="",
      type=Path,
      default=Path('/'))

  parser.add_argument(
      '-c', '--cwd',
      help="",
      type=Path,
      default=Path.cwd())

  # cmd (positional, collects all remaining)
  # Using REMAINDER so everything after this argument is captured "as-is."
  parser.add_argument(
    'cmd',
    nargs='*',
    help="Command and its arguments")

  args = parser.parse_args()

  if args.init:
    image = args.image

    if image is None:
      image = _CONFIG.get('default_image')

    if init(
      image = image,
      basis = args.basis,
      cwd = args.cwd,
      python = args.python):

      return 1

  return run(
    image = args.image,
    basis = args.basis,
    app = args.app,
    work = args.work,
    cwd = args.cwd,
    cmd = args.cmd,
    device = args.device)

#===============================================================================
exit(main())
