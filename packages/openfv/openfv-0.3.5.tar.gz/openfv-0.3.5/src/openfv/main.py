import numpy as np
from scipy import fftpack
import scipy.signal
import scipy.ndimage
import cv2

## -----------------------------------------------------
def ww_phase_discrepancy(img1, img2):
    """
    두 이미지 간의 phase discrepancy를 계산하는 함수
    
    Args:
        img1: 첫 번째 이미지 (BGR 형식)
        img2: 두 번째 이미지 (BGR 형식)
        
    Returns:
        phase discrepancy 결과 이미지 (uint8)
    """
    # 그레이스케일로 변환
    img1_gray = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    img2_gray = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

    # 푸리에 변환
    d1 = np.fft.fft2(img1_gray)
    d2 = np.fft.fft2(img2_gray)

    # 위상과 진폭 추출
    phase1 = np.angle(d1)
    amp1 = np.abs(d1)
    phase2 = np.angle(d2)
    amp2 = np.abs(d2)

    # 복소수 재구성
    def complex_numpy(real, imag):
        return real * np.exp(1j * imag)

    z1 = complex_numpy((amp1-amp2), phase1)
    z2 = complex_numpy((amp2-amp1), phase2)

    # 역 푸리에 변환
    m1 = np.fft.ifft2(z1)
    m2 = np.fft.ifft2(z2)

    # 결과 처리
    m11 = np.abs(m1)
    m22 = np.abs(m2)
    m12 = np.multiply(m11, m22)
    
    # 정규화 및 uint8 변환
    result = np.interp(m12, (m12.min(), m12.max()), (0, 255)).astype(np.uint8)
    
    return result

## -----------------------------------------------------
def ww_emboss_filter_frequency_domain(image_path, direction="Vertical"):
    # Read image (grayscale)
    img = cv2.imread(image_path, 0)
    
    if img is None:
        messagebox.showerror("Error", "Could not load the image.")
        return None
    
    # Get image dimensions
    rows, cols = img.shape
    
    # Pad image to optimal size for FFT
    optimal_size = cv2.getOptimalDFTSize(rows), cv2.getOptimalDFTSize(cols)
    padded = np.zeros(optimal_size, dtype=np.float32)
    padded[:rows, :cols] = img
    
    # Perform FFT
    dft = cv2.dft(np.float32(padded), flags=cv2.DFT_COMPLEX_OUTPUT)
    dft_shift = np.fft.fftshift(dft)  # Shift frequencies (low freq to center)
    
    # Visualize frequency domain (log scale)
    magnitude_spectrum = 20 * np.log(cv2.magnitude(dft_shift[:,:,0], dft_shift[:,:,1]) + 1)
    
    # Create emboss filter (frequency domain)
    centerX, centerY = optimal_size[0] // 2, optimal_size[1] // 2
    emboss_filter = np.zeros((optimal_size[0], optimal_size[1], 2), dtype=np.float32)
    
    # Generate filter
    for i in range(optimal_size[0]):
        for j in range(optimal_size[1]):
            # Directional filter (set direction for emboss effect)
            if direction == "Vertical":
                # Vertical emboss (same as original code)
                phase = np.arctan2(i - centerX, j - centerY)
            else:  # Horizontal direction
                # Horizontal emboss (swap x and y axes)
                phase = np.arctan2(j - centerY, i - centerX)
            
            # Phase adjustment for emboss effect
            factor = np.sin(phase)
            
            # Attenuation based on distance
            dist = np.sqrt((i - centerX)**2 + (j - centerY)**2)
            gaussian = np.exp(-(dist**2) / (2 * (min(optimal_size)/4)**2))
            
            # Apply filter to real and imaginary parts
            emboss_filter[i, j, 0] = factor * gaussian # Real part
            emboss_filter[i, j, 1] = 0  # Imaginary part
    
    # Apply filter (multiply in frequency domain)
    filtered_dft = np.zeros_like(dft_shift)
    filtered_dft[:,:,0] = dft_shift[:,:,0] * emboss_filter[:,:,0] - dft_shift[:,:,1] * emboss_filter[:,:,1]
    filtered_dft[:,:,1] = dft_shift[:,:,0] * emboss_filter[:,:,1] + dft_shift[:,:,1] * emboss_filter[:,:,0]
    
    # Inverse shift
    filtered_dft_shift = np.fft.ifftshift(filtered_dft)
    
    # Perform inverse FFT
    img_back = cv2.idft(filtered_dft_shift)
    img_back = cv2.magnitude(img_back[:,:,0], img_back[:,:,1])
    
    # Crop to original image size
    img_back = img_back[:rows, :cols]
    
    # Normalize image
    img_back = cv2.normalize(img_back + 127, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    
    return img, magnitude_spectrum, emboss_filter, img_back

## -----------------------------------------------------
def ww_apply_bandpass_filter(image, low_freq, high_freq):
    # Transform image to frequency domain (FFT)
    f_transform = np.fft.fft2(image)
    f_shift = np.fft.fftshift(f_transform)
    
    rows, cols = image.shape
    crow, ccol = rows // 2, cols // 2
    
    # Create filter mask
    mask = np.zeros((rows, cols), np.uint8)
    
    # Bandpass filter
    for i in range(rows):
        for j in range(cols):
            d = np.sqrt((i-crow)**2 + (j-ccol)**2)
            if low_freq <= d <= high_freq:
                mask[i, j] = 1
    
    # Apply filter
    f_shift_filtered = f_shift * mask
    
    # Inverse transform
    f_ishift = np.fft.ifftshift(f_shift_filtered)
    img_back = np.fft.ifft2(f_ishift)
    img_back = np.abs(img_back)
    
    # Normalize
    img_back = cv2.normalize(img_back, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    
    return img_back

## -----------------------------------------------------
def ww_phase_only_correlation(img1, img2, window=True):
    """Phase Only Correlation을 이용한 이미지 정합 알고리즘"""
    # 이미지를 그레이스케일로 변환
    if len(img1.shape) == 3:
        img1_gray = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    else:
        img1_gray = img1
    
    if len(img2.shape) == 3:
        img2_gray = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
    else:
        img2_gray = img2
    
    # 이미지 크기를 동일하게 조정 (2의 거듭제곱 크기로 패딩)
    height = max(img1_gray.shape[0], img2_gray.shape[0])
    width = max(img1_gray.shape[1], img2_gray.shape[1])
    
    # 2의 거듭제곱 크기로 조정
    h_pad = 2**int(np.ceil(np.log2(height)))
    w_pad = 2**int(np.ceil(np.log2(width)))
    
    # 패딩된 이미지 생성
    img1_padded = np.zeros((h_pad, w_pad), dtype=np.float32)
    img2_padded = np.zeros((h_pad, w_pad), dtype=np.float32)
    
    img1_padded[:img1_gray.shape[0], :img1_gray.shape[1]] = img1_gray
    img2_padded[:img2_gray.shape[0], :img2_gray.shape[1]] = img2_gray
    
    # 윈도우 함수 적용 (가장자리 효과 줄이기)
    if window:
        window_func = np.outer(np.hanning(h_pad), np.hanning(w_pad))
        img1_padded = img1_padded * window_func
        img2_padded = img2_padded * window_func
    
    # FFT 적용
    f1 = np.fft.fft2(img1_padded)
    f2 = np.fft.fft2(img2_padded)
    
    # Phase Only Correlation (위상만 사용)
    eps = 1e-10  # 0으로 나누는 것 방지
    poc = (f1 * f2.conj()) / (np.abs(f1) * np.abs(f2) + eps)
    
    # 역 FFT
    correlation = np.fft.ifft2(poc)
    correlation = np.abs(correlation)
    
    # 서브픽셀 정확도를 위한 보간
    y, x = np.unravel_index(np.argmax(correlation), correlation.shape)
    
    # 서브픽셀 정확도 계산
    if 0 < y < h_pad-1 and 0 < x < w_pad-1:
        # 주변 픽셀값으로 2차 보간
        dx = 0.5 * (correlation[y, x+1] - correlation[y, x-1]) / (2*correlation[y, x] - correlation[y, x+1] - correlation[y, x-1] + eps)
        dy = 0.5 * (correlation[y+1, x] - correlation[y-1, x]) / (2*correlation[y, x] - correlation[y+1, x] - correlation[y-1, x] + eps)
        x = x + dx
        y = y + dy
    
    # 이미지 크기에 맞게 변환
    if y > h_pad // 2:
        y = y - h_pad
    if x > w_pad // 2:
        x = x - w_pad
    
    return y, x, correlation

## -----------------------------------------------------
def ww_tikhonov_regularization(degraded_image, psf=3, lambda_value=0.01):
   degraded_freq = np.fft.fft2(degraded_image)
   psf_freq = np.fft.fft2(psf, degraded_image.shape)
   restored_freq = np.conj(psf_freq) / (np.abs(psf_freq)**2 + lambda_value)
   restored_freq *= degraded_freq
   restored = np.fft.ifft2(restored_freq)
   restored = np.abs(restored)
   restored = (255 * restored).astype(np.uint8)
   return restored

## -----------------------------------------------------
def ww_spectral_residual_saliency(image, size=64):
    # Ensure image is grayscale
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    else:
        gray = image
    
    # Image smoothing
    width = height = size
    kernel = np.ones((5, 5), np.float32) / 25.0
    smoothed = cv2.filter2D(gray, -1, kernel)
    
    # Resize to 128x128
    resized = cv2.resize(smoothed, (width, height), interpolation=cv2.INTER_CUBIC)
    
    # Get Log Amplitude
    ffted = np.fft.fft2(resized)
    mag = np.log1p(np.abs(np.fft.fftshift(ffted)))
    
    # Get Phase
    phase = np.angle(ffted)
    
    # Get Residual of Spectral
    SR = mag - cv2.filter2D(mag, -1, kernel)
    
    # Get Saliency Map
    SRSM = np.abs(np.fft.ifft2(mag * np.exp(1j * phase)))
    
    # After Effect
    SM = cv2.GaussianBlur(SRSM, (11, 11), 3)
    
    # Normalize and resize back to original size
    SM = (SM - SM.min()) / (SM.max() - SM.min())
    SM = cv2.resize(SM, (image.shape[1], image.shape[0]), interpolation=cv2.INTER_LINEAR)
    SM = (255 * SM).astype(np.uint8)
    return SM

## ------------------------------------------------
def ww_homomorphic_filter(image, d0=30, rh=2.0, rl=0.5, c=2):
    """
    Homomorphic filtering of an input image.
    
    Parameters:
    -----------
    image : ndarray
        Input image (grayscale)
    d0 : float
        Cutoff distance (default: 30)
    rh : float
        High frequency gain (default: 2.0)
    rl : float
        Low frequency gain (default: 0.5)
    c : float
        Constant controlling filter sharpness (default: 2)
        
    Returns:
    --------
    ndarray
        Filtered image
    """
    # Convert RGB to grayscale if needed
    if len(image.shape) == 3:
        image = np.mean(image, axis=2)
    
    # Take log of image
    image_log = np.log1p(np.array(image, dtype="float"))
    
    # Get image size
    rows, cols = image_log.shape
    
    # Create meshgrid for filter
    u = np.arange(rows)
    v = np.arange(cols)
    u, v = np.meshgrid(u, v, indexing='ij')
    
    # Center coordinates
    u = u - rows//2
    v = v - cols//2
    
    # Calculate distances from center
    D = np.sqrt(u**2 + v**2)
    
    # Create homomorphic filter
    H = (rh - rl) * (1 - np.exp(-c * (D**2 / d0**2))) + rl
    
    # Apply FFT
    image_fft = fftpack.fft2(image_log)
    image_fft_shifted = fftpack.fftshift(image_fft)
    
    # Apply filter
    filtered_image = H * image_fft_shifted
    
    # Inverse FFT
    filtered_image_unshifted = fftpack.ifftshift(filtered_image)
    filtered_image_ifft = fftpack.ifft2(filtered_image_unshifted)
    
    # Take exp and return real part
    result = np.expm1(np.real(filtered_image_ifft))
    
    # Normalize to [0, 255]
    result = result - np.min(result)
    result = result / np.max(result) * 255
    
    return result.astype(np.uint8)

## -----------------------------------------------------
def ww_amplitude_spectrum(image):
    """
    입력 이미지의 2D 푸리에 변환을 수행하고 진폭 스펙트럼을 반환합니다.
    
    Parameters:
        image (numpy.ndarray): 입력 이미지 배열 (2D grayscale 또는 3D RGB)
        
    Returns:
        numpy.ndarray: 정규화된 진폭 스펙트럼 이미지
    """
    # 입력 이미지가 3D(RGB)인 경우 grayscale로 변환
    if len(image.shape) == 3:
        image = np.mean(image, axis=2)
    
    # 2D 푸리에 변환 수행
    f_transform = np.fft.fft2(image)
    
    # 주파수 성분을 중앙으로 이동
    f_shift = np.fft.fftshift(f_transform)
    
    # 진폭 스펙트럼 계산
    amplitude_spectrum = np.abs(f_shift)
    
    # log scale로 변환하여 시각화 개선
    amplitude_spectrum = np.log1p(amplitude_spectrum)
    
    # 0-1 범위로 정규화
    amplitude_spectrum = (amplitude_spectrum - np.min(amplitude_spectrum)) / \
                        (np.max(amplitude_spectrum) - np.min(amplitude_spectrum))
    
    spectrum_8bit = (amplitude_spectrum * 255).astype(np.uint8)
    
    return spectrum_8bit

## -----------------------------------------------------
def ww_phase_congruency_edge(    image,
    nscale=4,          # 스케일 수를 줄임 (4 → 3)
    norient=4,         # 방향 수를 늘림 (6 → 8)
    minWaveLength=3,   # 최소 파장을 줄임 (3 → 2)
    mult=1.2,          # 파장 증가 배수를 줄임 (2.1 → 1.8)
    sigmaOnf=0.9,     # 필터 대역폭을 줄임 (0.55 → 0.35)
    k=9.0,             # 노이즈 임계값을 높임 (2.0 → 3.0)
    cutOff=0.5,        # 컷오프 임계값을 낮춤 (0.5 → 0.3)
    g=9.0,            # 기울기를 높임 (10.0 → 15.0)
    epsilon=0.01    # 작은 값을 더 작게 (0.0001 → 0.00001)
):
    """
    C++ 구현을 기반으로 한 Phase Congruency 에지 검출
    
    Parameters:
    -----------
    image : ndarray
        입력 이미지 (grayscale 또는 RGB)
    nscale : int
        스케일의 수 (기본값: 4)
    norient : int
        방향의 수 (기본값: 6)
    기타 매개변수들은 Phase Congruency 계산에 필요한 상수들
    """
    if len(image.shape) == 3:
        image = np.mean(image, axis=2)
    
    # 이미지를 float로 변환
    image = image.astype(np.float64) / 255.0
    rows, cols = image.shape
    
    # DFT를 위한 최적 크기 계산
    dft_rows = cv2.getOptimalDFTSize(rows)
    dft_cols = cv2.getOptimalDFTSize(cols)
    
    # 이미지 패딩
    padded = np.zeros((dft_rows, dft_cols))
    padded[:rows, :cols] = image
    
    # FFT 계산
    dft = np.fft.fft2(padded)
    dft_shift = np.fft.fftshift(dft)
    
    # 좌표 그리드 생성
    y, x = np.meshgrid(np.arange(dft_rows) - dft_rows//2,
                      np.arange(dft_cols) - dft_cols//2,
                      indexing='ij')
    radius = np.sqrt(x**2 + y**2)
    theta = np.arctan2(-x, y)
    
    # 반지름 정규화
    radius = radius / (min(dft_rows, dft_cols) / 2)
    
    # 로그 가보르 필터 생성
    log_gabor = []
    for s in range(nscale):
        wavelength = minWaveLength * mult**s
        fo = 1.0 / wavelength
        log_gabor.append(np.exp(-(np.log(radius/fo + epsilon))**2 / (2 * sigmaOnf**2)))
        log_gabor[-1][dft_rows//2, dft_cols//2] = 0
    
    # 각 방향에 대한 처리
    pc_sum = np.zeros((rows, cols))
    
    for o in range(norient):
        # 방향 필터 생성
        angle = o * np.pi / norient
        ds = np.cos(theta - angle)
        dc = np.sin(theta - angle)
        spread = np.exp(-(theta - angle)**2 / (2 * (np.pi/norient)**2))
        
        energy = np.zeros((rows, cols))
        sum_e = np.zeros((rows, cols), dtype=complex)
        
        # 각 스케일에 대한 처리
        for s in range(nscale):
            # 필터 적용
            filt = log_gabor[s] * spread
            result = np.fft.ifft2(np.fft.ifftshift(dft_shift * filt))
            result = result[:rows, :cols]
            
            # 에너지 누적
            if s == 0:
                sum_e = result
                max_an = np.abs(result)
                sum_an = max_an
            else:
                sum_e += result
                sum_an += np.abs(result)
                max_an = np.maximum(max_an, np.abs(result))
        
        # Phase Congruency 계산
        abs_e = np.abs(sum_e) + epsilon
        energy = np.real(sum_e) / abs_e
        
        # 노이즈 제거
        t = np.mean(abs_e) * k
        energy = np.maximum(energy - t, 0)
        
        # 가중치 적용
        weight = 1.0 / (1.0 + np.exp(g * (cutOff - sum_an / (max_an + epsilon))))
        pc_sum += energy * weight
    
    # 결과 정규화
    pc_sum = (pc_sum - np.min(pc_sum)) / (np.max(pc_sum) - np.min(pc_sum)) * 255
    
    return pc_sum.astype(np.uint8)