"""various utilities for the VRE middleware"""
import os
import logging
import time
import json
import subprocess as sp
from virtmat.middleware.exceptions import SlurmError

LOGGING_LEVELS = ('NOTSET', 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')


def get_logger(name, default_level=logging.ERROR):
    """return a custom logger object"""
    logger = logging.getLogger(name)
    if not logger.hasHandlers():
        fstr = '%(asctime)s %(levelname)s %(name)s: %(message)s'
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(fstr))
        logger.addHandler(handler)
        logger.setLevel(default_level)
    return logger


def get_slurm_job_state(*args, method='json', **kwargs):
    """select the method to get the SLURM job state"""
    if method == 'parse':
        return get_slurm_job_state_parse(*args, **kwargs)
    if method == 'json':
        return get_slurm_job_state_json(*args, **kwargs)
    raise ValueError(f'unknown method {method}')


def get_slurm_job_state_json(res_id, max_trials=3, trial_delay=3, trial=0):
    """extract the SLURM job state using the sacct command"""
    if trial > max_trials:
        msg = f'cannot get SLURM job state after {max_trials} trials'
        raise SlurmError(msg)
    command = f'sacct -j {res_id} --json'
    sacct_out = json.loads(sp.getoutput(command))  # nosec B605
    if len(sacct_out['jobs']) == 0:
        time.sleep(trial_delay)
        return get_slurm_job_state(res_id, max_trials, trial_delay, trial+1)
    assert sacct_out['jobs'][0]['job_id'] == int(res_id)
    assert isinstance(sacct_out['jobs'][0]['state']['current'], list)
    assert len(sacct_out['jobs'][0]['state']['current']) == 1
    return sacct_out['jobs'][0]['state']['current'][0]


def get_slurm_job_state_parse(res_id, max_trials=10, trial_delay=3, trial=0):
    """extract the SLURM job state using the sacct command"""
    if trial > max_trials:
        msg = f'cannot get SLURM job state after {max_trials} trials'
        raise SlurmError(msg)
    command = f'sacct -j {res_id} -n -o state'
    state = sp.getoutput(command).strip()  # nosec B605
    if len(state) == 0:
        time.sleep(trial_delay)
        return get_slurm_job_state(res_id, max_trials, trial_delay, trial+1)
    return state


def await_slurm_job_state(res_id, state, sleep_time=10):
    """return when a specified SLURM job state has been reached"""
    while get_slurm_job_state(res_id) != state:
        time.sleep(sleep_time)


def lmod_env_module(command):
    """Process lmod modules list and spider commands and return modules

    Due to ambiguous format of provided input it is assumed that the last
    division is the module version in the case of more than one division.

    Args:
        command (str): either 'list' or 'spider'

    Returns:
        (dict): {prefix/.../name: [version1, ...]} in case of more divisions
                {'name': []} in case of one division

    """
    assert isinstance(command, str) and command in ('list', 'spider')
    lmod_cmd = os.environ.get('LMOD_CMD')
    if lmod_cmd is None:
        return None
    full_command = [lmod_cmd, 'bash', '-t', command]
    with sp.Popen(full_command, stdout=sp.DEVNULL, stderr=sp.PIPE) as proc:  # nosec B603
        string = proc.stderr.read().decode()
    if string.strip() == 'No modules loaded':
        return None
    mods_lst = string.strip().split('\n')
    mods_dct = {}
    for mod in mods_lst:
        divisions = mod.split('/')
        name = '/'.join(divisions[:-1]) if len(divisions) > 1 else divisions[0]
        mods_dct[name] = []
    for mod in mods_lst:
        divisions = mod.split('/')
        if len(divisions) > 1:
            version = divisions[-1]
            if version:
                mods_dct['/'.join(divisions[:-1])].append(version)
    return mods_dct


def format_warning_wrapper(func):
    """format user warnings, leave python warnings unchanged"""
    def wrapper(*args, **kwargs):
        warning = args[0]
        warning_cls = args[1]
        if isinstance(warning, UserWarning):
            assert warning_cls is UserWarning
            return 'Warning: ' + str(warning) + '\n'
        return func(*args, **kwargs)
    return wrapper


def exec_cancel(res_id):
    """
    Execute the Slurm cancel command

    Args:
        res_id (int): reservation ID (=Slurm JobID)

    Raises:
        SlurmError: if the command returns an error code
    """
    logger = get_logger(__name__)
    command = ['/usr/bin/scancel', res_id]
    cancel_cmd = sp.run(command, shell=False, check=True)  # nosec B603
    if cancel_cmd.returncode != 0:
        msg = 'could not execute scancel command'
        logger.error(msg)
        raise SlurmError(msg)
    new_state = get_slurm_job_state(res_id)
    if new_state != 'CANCELLED':  # not covered
        msg = f'job could not be cancelled, new state {new_state}'
        logger.error(msg)
        raise RuntimeError(msg)
    logger.info('Cancelled res_id: %d', res_id)
