# OpenFV
A Python package for computer vision in Frequency Domain.

## Installation
You can install the package using pip:

## bash
pip install openfv

## Usage
- Demo videos: https://www.youtube.com/@sheekjegal/videos
- Here's a basic example of how to use the package:

import openfv as fv

# Load an image
image = cv2.imread('your_image.png')
image2 = cv2.imread('your_image2.png')

# Homomorphic filtering
filtered_image = fv.ww_homomorphic_filter(image, d0=30, rh=2.0, rl=0.5, c=2)

# Amplitude spectrum calculation
spectrum_image = fv.ww_amplitude_spectrum(image)

# Spectral residual saliency map generation
saliency_map = fv.ww_spectral_residual_saliency(image, size=64)

# phase congruency edge
edge_map = fv.ww_phase_congruency_edge(image,
    nscale=4, 
    norient=4,         
    minWaveLength=3,   
    mult=1.2,          
    sigmaOnf=0.9,     
    k=9.0,             
    cutOff=0.5,      
    g=9.0,          
    epsilon=0.01
)

# deblur restoration
restored_image = fv.ww_tikhonov_regularization(image, psf=3, lambda_value=0.01)

# phase only correlation
y, x, corr_ratio = fv.ww_phase_only_correlation(image, image2, window=True)

# band pass filtering
bpf_image = fv.ww_apply_bandpass_filter(image, low_freq, high_freq)

# spectral emboss filtering
image_path= "/Users/user_name/Desktop/filename.jpg"
_, _, _, filtered_image = fv.ww_emboss_filter_frequency_domain(image_path, direction="Vertical")

# phase discrepancy
phase_discrepancy_map = fv.ww_phase_discrepancy(image, image2) 

# fast Radon transform
sinogram = fv.ww_fast_radon_transform(image, num_angles=180)

## Input
- NumPy array representing an image
- Supports both 2D (grayscale) and 3D (RGB) arrays
- For functions requiring grayscale input (e.g., ww_homomorphic_filter), RGB images must be converted to grayscale.
- For functions supporting RGB input (e.g., ww_amplitude_spectrum), RGB images are processed directly.

## Output
- uint8 grayscale image (for most functions)
- Check specific function documentation for exceptions.

## Dependencies
- numpy (tested with 1.19.0 or later)
- scipy (tested with 1.15.1 or later)
- cv2 (tested with 4.11.0 or later)

## License
This project is licensed under the MIT License - see the LICENSE file for details.
Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

## Author
Wonwoo Park (bemore.one@gmail.com)

## Version History
- 0.3.6: fast radon transform added
- 0.3.5: phase discrepancy added
- 0.3.4: spectral emboss filter added
- 0.3.3: band pass filter added 
- 0.3.2: phase only correlation added
- 0.3.1: tikhonov_regularization added
- 0.3.0: phase congruency edge added
- 0.2.1: hann window function added in SRSM function
- 0.2.0: spectral residual saliency map added
- 0.1.9: amplitude spectrum added
- 0.1.5: homomorphic filter added
- 0.1.0: Initial release