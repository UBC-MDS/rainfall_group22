from seaborn import diverging_palette
from pathlib import Path

_cmap = diverging_palette(240, 10, sep=10, n=21, as_cmap=True)

def bg(style, subset=None, rev=True, axis=0):
    """Show style with highlights per column"""
    if subset is None:
        subset = style.data.columns

    cmap = _cmap.reversed() if rev else _cmap

    return style \
        .background_gradient(cmap=cmap, subset=subset, axis=axis)

def calc_size(p : Path, nice=True):
    """Calculate size of directory and all subdirs

    Parameters
    ----------
    p : Path
        [description]
    nice : bool, optional
        return raw float or nicely formatted string, default False

    Returns
    -------
    int | string
        size of folder
    """    
    _size = sum(_p.stat().st_size for _p in p.glob('**/*') if _p.is_file())
    return _size