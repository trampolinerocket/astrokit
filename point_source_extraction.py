#!/usr/bin/env python2.7
'''
Point-source extraction.

Usage: python point_source_extraction.py myimage.fits
'''

import argparse
import json
import sys
import tempfile
import urllib

import matplotlib.pylab as plt
import numpy as np

from astropy.io import fits
from astropy.stats import sigma_clipped_stats
from astropy.visualization import SqrtStretch
from astropy.visualization.mpl_normalize import ImageNormalize
from photutils import CircularAperture
from photutils import datasets, daofind
from photutils.psf import subtract_psf

def compute(data):
    mean, median, std = sigma_clipped_stats(data, sigma=3.0, iters=5)
    sources = daofind(data - median, fwhm=3.0, threshold=5.*std)

    print sources
    print len(sources), 'sources'
    print np.where(sources['mag'] > 0)
    return sources

def plot(sources, data, path):
    positions = (sources['xcentroid'], sources['ycentroid'])
    apertures = CircularAperture(positions, r=4.)
    norm = ImageNormalize(stretch=SqrtStretch())
    plt.imshow(data, cmap='Greys', origin='lower', norm=norm)
    apertures.plot(color='blue', lw=1.5, alpha=0.5)

    plt.savefig(path)

def save_fits(sources, path):
    col_x = fits.Column(name='field_x', format='E', array=sources['xcentroid'])
    col_y = fits.Column(name='field_y', format='E', array=sources['ycentroid'])
    est_flux = fits.Column(name='est_flux', format='E', array=sources['flux'])
    est_mag = fits.Column(name='est_mag', format='E', array=sources['mag'])

    cols = fits.ColDefs([col_x, col_y, est_flux, est_mag])
    tbhdu = fits.BinTableHDU.from_columns(cols)
    tbhdu.writeto(path)

def save_json(sources, path):
    field_x = sources['xcentroid']
    field_y = sources['ycentroid']
    est_flux = sources['flux']
    est_mag = sources['mag']

    out = []
    for i in xrange(len(field_x)):
        out.append({
            'field_x': field_x[i],
            'field_y': field_y[i],
            'est_flux': est_flux[i],
            'est_mag': est_mag[i],
        })

    with open(path, 'w') as f:
        f.write(json.dumps(out, indent=2))

def compute_psf_flux(image_data, sources, \
        scatter_output_path=None, bar_output_path=None, residual_path=None):
    print 'Computing flux...'

    import astropy.units as u
    from photutils.psf import psf_photometry, GaussianPSF

    coords = zip(sources['xcentroid'], sources['ycentroid'])

    psf_gaussian = GaussianPSF(1)
    computed_fluxes = psf_photometry(image_data, coords, psf_gaussian)

    if scatter_output_path:
        print 'Saving scatter plot...'
        plt.close('all')
        plt.scatter(sorted(sources['flux']), sorted(computed_fluxes))
        plt.xlabel('Fluxes catalog')
        plt.ylabel('Fluxes photutils')
        plt.savefig(scatter_output_path)

    if bar_output_path:
        print 'Saving bar chart...'
        plt.close('all')
        plt.bar(xrange(len(computed_fluxes)), computed_fluxes)
        plt.ylabel('Count')
        plt.xlabel('Flux')
        plt.savefig(bar_output_path)

    if residual_path:
        residuals = subtract_psf(np.float64(image_data.copy()), psf_gaussian, coords, computed_fluxes)

        # Plot it.
        plt.close('all')
        plt.figure(figsize=(16, 12))
        plt.imshow(residuals, cmap='hot', vmin=-1, vmax=10, interpolation='None', origin='lower')
        plt.plot(coords[0], coords[1], marker='o', markerfacecolor='None', markeredgecolor='y', linestyle='None')
        plt.xlim(0, 1024)
        plt.ylim(0, 512)
        plt.colorbar(orientation='horizontal')
        plt.savefig(residual_path)

def load_image(path):
    im = fits.open(path)
    data = im[0].data[2]
    return data

def load_url(url):
    page = urllib.urlopen(url)
    content = page.read()
    return load_data_as_fits(content)

def load_data_as_fits(content):
    try:
        temp = tempfile.NamedTemporaryFile(delete=True)
        temp.write(content)

        im = fits.open(temp.name)
        data = im[0].data[2]
    finally:
        temp.close()

    return data

def get_args():
    parser = argparse.ArgumentParser('Extract point sources from image.')
    parser.add_argument('image', help='filesystem path or url to input image')
    parser.add_argument('--coords_plot', help='path to output overlay plot')
    parser.add_argument('--coords_fits', help='path to output point source coords to')
    parser.add_argument('--coords_json', help='path to output point source coords to')
    parser.add_argument('--psf', help='whether to compute flux via PSF', action='store_true')
    parser.add_argument('--psf_scatter', help='output path for scatterplot of fluxes')
    parser.add_argument('--psf_bar', help='output path for distribution plot of fluxes')
    parser.add_argument('--psf_residual', help='output path for residual image with PSF subtracted')
    return parser.parse_args()

if __name__ == '__main__':
    args = get_args()
    if args.image.startswith('http:'):
        image_data = load_url(args.image)
    else:
        image_data = load_image(args.image)
    sources = compute(image_data)

    # Coords.
    if args.coords_plot:
        plot(sources, image_data, args.coords_plot)
    if args.coords_fits:
        save_fits(sources, args.coords_fits)
    if args.coords_json:
        save_json(sources, args.coords_json)

    # PSF.
    if args.psf_scatter or args.psf_bar or args.psf_residual:
        compute_psf_flux(image_data, sources, \
                args.psf_scatter, args.psf_bar, args.psf_residual)
    print 'Done.'
