from seaborn import diverging_palette

_cmap = diverging_palette(240, 10, sep=10, n=21, as_cmap=True)

def bg(style, subset=None, rev=True, axis=0):
    """Show style with highlights per column"""
    if subset is None:
        subset = style.data.columns

    cmap = _cmap.reversed() if rev else _cmap

    return style \
        .background_gradient(cmap=cmap, subset=subset, axis=axis)