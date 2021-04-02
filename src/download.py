"""
Download files from figshare

Examples
--------
>>> from src import download as dl
>>> files = dl.download_files('data.zip', chunk_size=10)
>>> dl.unzip(p=files[0], p_dst='csv', delete=False)
"""

import shutil
from pathlib import Path
from typing import Union

import requests
from nicenumber import nicenumber as nn
from tqdm import tqdm

from .__init__ import getlog

log = getlog(__name__)

# set data dir for downloads
p_data = Path(__file__).parents[1] / 'data'

def download_file(url: str, name: str, chunk_size: int=1):
    """Download single file in chunks

    Parameters
    ----------
    url : str
        download url
    name : str
        filename to save
    chunk_size : int, optional
        chunk size in mb to download, by default 1mb
    """    
    p = p_data / name
    chunk_size = chunk_size * 1024 * 1024 # convert to bytes

    if not p_data.exists():
        p_data.mkdir(parents=True)

    # ask if okay to overwrite
    if p.exists():
        ans = _input(msg=f'Data file {p.name} already exists, overwrite?')
        if not ans:
            log.info('User declined to overwrite.')
            return
        else:
            log.info('Overwriting data.')

    resp = requests.get(url, stream=True, allow_redirects=True)
    size_bytes = int(resp.headers.get('content-length', 0))

    size_human = nn.to_human(size_bytes, family='filesize')
    size_human_chunk = nn.to_human(chunk_size, family='filesize')
    log.info(f'Downloading {size_human} file in {size_human_chunk} chunks.')

    progress_bar = tqdm(total=size_bytes, unit='iB', unit_scale=True)

    with open(p, 'wb') as file:
        for data in resp.iter_content(chunk_size=chunk_size):
            progress_bar.update(len(data))
            if data:
                file.write(data)
    
    progress_bar.close()
    log.info(f'File downloaded to: {p}')

    return p

def download_files(dl_files: Union[list, str]=None, article_id: str='14096681', **kw):
    """Download list of files

    Parameters
    ----------
    dl_files : Union[list, str], optional
        files to download, by default None
    article_id : str, optional
        default '14096681'

    Returns
    -------
    requests.respons
        json response obj
    """
    if dl_files is None:
        dl_files = ['environment.yml']
    elif not isinstance(dl_files, list):
        dl_files = [dl_files]
    
    url = f'https://api.figshare.com/v2/articles/{article_id}'

    resp = requests.get(url).json()
    
    # filter list of files to download
    m_info = list(filter(lambda x: [name for name in dl_files if name in x['name']], resp['files']))

    files = []
    for m in m_info:
        p = download_file(url=m['download_url'], name=m['name'], **kw)

        if p:
            files.append(p)

    return files

def unzip(p: Path, p_dst: Union[Path, str]=None, delete=False) -> Path:
    """Simple wrapper for shultil unpack_archive with default unzip dir

    Parameters
    ----------
    p : Path
        File to unzip
    p_dst : Union[Path, str], optional
        Unzip in different dir, by default parent dir
    delete : bool, optional
        Delete original zip after unpack, by default False
    """
    if p_dst is None:
        p_dst = p.parent
    elif isinstance(p_dst, str):
        p_dst = p.parent / p_dst

    log.info(f'Unpacking zip to: {p_dst}')
    shutil.unpack_archive(p, p_dst)

    if delete:
        p.unlink()

    return p

def _input(msg : str) -> bool:
    """Get yes/no answer from user in terminal

    Parameters
    ----------
    msg : str
        Prompt to ask user

    Returns
    -------
    bool
        User's answer y/n, True/False
    """    
    reply = str(input(msg + ' (y/n): ')).lower().strip()
    if len(reply) <= 0:
        return False

    if reply[0] == 'y':
        return True
    elif reply[0] == 'n':
        return False
    else:
        return False
