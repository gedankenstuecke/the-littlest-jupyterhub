"""
Bootstrap an installation of TLJH.

Sets up just enough TLJH environments to invoke tljh.installer.

This script is run as:

    curl <script-url> | sudo python3 -

Constraints:
  - Be compatible with Python 3.4 (since we support Ubuntu 16.04)
  - Use stdlib modules only
"""
import os
import subprocess
import urllib.request
import contextlib
import hashlib
import tempfile
import sys


def md5_file(fname):
    """
    Return md5 of a given filename

    Copied from https://stackoverflow.com/a/3431838
    """
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def check_miniconda_version(prefix, version):
    """
    Return true if a miniconda install with version exists at prefix
    """
    try:
        return subprocess.check_output([
            os.path.join(prefix, 'bin', 'conda'),
            '-V'
        ]).decode().strip() == 'conda {}'.format(version)
    except (subprocess.CalledProcessError, FileNotFoundError):
        # Conda doesn't exist, or wrong version
        return False


@contextlib.contextmanager
def download_miniconda_installer(version, md5sum):
    """
    Context manager to download miniconda installer of given version.

    This should be used as a contextmanager. It downloads miniconda installer
    of given version, verifies the md5sum & provides path to it to the `with`
    block to run.
    """
    with tempfile.NamedTemporaryFile() as f:
        installer_url = "https://github.com/jjhelmus/berryconda/releases/download/v{}/Berryconda3-{}}-Linux-armv6l.sh".format(version)
        # installer_url = "https://repo.continuum.io/miniconda/Miniconda3-{}-Linux-x86_64.sh".format(version)
        urllib.request.urlretrieve(installer_url, f.name)

        if md5_file(f.name) != md5sum:
            raise Exception('md5 hash mismatch! Downloaded file corrupted')

        yield f.name


def install_miniconda(installer_path, prefix):
    """
    Install miniconda with installer at installer_path under prefix
    """
    subprocess.check_output([
        '/bin/bash',
        installer_path,
        '-u', '-b',
        '-p', prefix
    ], stderr=subprocess.STDOUT)


def pip_install(prefix, packages, editable=False):
    """
    Install pip packages in the conda environment under prefix.

    Packages are upgraded if possible.

    Set editable=True to add '--editable' to the pip install commandline.
    Very useful when doing active development
    """
    flags = ['--no-cache-dir', '--upgrade']
    if editable:
        flags.append('--editable')
    subprocess.check_output([
        os.path.join(prefix, 'bin', 'python3'),
        '-m', 'pip',
        'install',
    ] + flags + packages)


def main():
    install_prefix = os.environ.get('TLJH_INSTALL_PREFIX', '/opt/tljh')
    hub_prefix = os.path.join(install_prefix, 'hub')
    miniconda_version = '2.0.0'
    miniconda_installer_md5 = "7219c31fa9cc580ec7715242e84e3c21"

    print('Checking if TLJH is already installed...')
    if not check_miniconda_version(hub_prefix, miniconda_version):
        initial_setup = True
        print('Downloading & setting up hub environment...')
        with download_miniconda_installer(miniconda_version, miniconda_installer_md5) as installer_path:
            install_miniconda(installer_path, hub_prefix)
        print('Hub environment set up!')
    else:
        initial_setup = False
        print('TLJH is already installed, will try to upgrade')

    if initial_setup:
        print('Setting up TLJH installer...')
    else:
        print('Upgrading TLJH installer...')

    is_dev = os.environ.get('TLJH_BOOTSTRAP_DEV', 'no') == 'yes'
    tljh_repo_path = os.environ.get(
        'TLJH_BOOTSTRAP_PIP_SPEC',
        'git+https://github.com/gedankenstuecke/the-littlest-jupyterhub.git@berryconda'
    )

    pip_install(hub_prefix, [tljh_repo_path], editable=is_dev)

    print('Starting TLJH installer...')
    os.execv(
        os.path.join(hub_prefix, 'bin', 'python3'),
        [
            os.path.join(hub_prefix, 'bin', 'python3'),
            '-m',
            'tljh.installer',
        ] + sys.argv[1:]
    )


if __name__ == '__main__':
    main()
