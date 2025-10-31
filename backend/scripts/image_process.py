from PIL import Image, ImageEnhance, ImageFilter
import cv2
import numpy as np

def preprocess_image(image_path, target_size=(1920, 1080)):
    """
    Preprocess image for better OCR performance
    
    Args:
        image_path: Path to the image file
        target_size: Maximum dimensions (width, height)
    
    Returns:
        Preprocessed PIL Image
    """
    # Open image
    img = Image.open(image_path)
    
    # Convert to RGB if necessary
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    # Resize if too large (maintains aspect ratio)
    img.thumbnail(target_size, Image.Resampling.LANCZOS)
    
    # Convert to OpenCV format for advanced preprocessing
    cv_img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    
    # Convert to grayscale
    gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
    
    # Apply adaptive thresholding for better text contrast
    # This works better than simple thresholding for varying lighting
    binary = cv2.adaptiveThreshold(
        gray, 255, 
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
        cv2.THRESH_BINARY, 
        11, 2
    )
    
    # Denoise
    denoised = cv2.fastNlMeansDenoising(binary, h=10)
    
    # Optional: Sharpen the image
    kernel = np.array([[-1,-1,-1],
                       [-1, 9,-1],
                       [-1,-1,-1]])
    sharpened = cv2.filter2D(denoised, -1, kernel)
    
    # Convert back to PIL
    processed_img = Image.fromarray(sharpened)
    
    return processed_img

def preprocess_image(image_path):
    """Fast image preprocessing for OCR"""
    from PIL import Image
    import cv2
    import numpy as np
    
    img = Image.open(image_path)
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    # Resize if too large (faster processing)
    img.thumbnail((1920, 1080), Image.Resampling.LANCZOS)
    
    # Convert to OpenCV
    cv_img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
    
    # Adaptive thresholding
    binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                   cv2.THRESH_BINARY, 11, 2)
    
    # Denoise
    denoised = cv2.fastNlMeansDenoising(binary, h=10)
    
    # Save preprocessed image
    preprocessed_path = image_path.replace('.', '_preprocessed.')
    cv2.imwrite(preprocessed_path, denoised)
    
    return preprocessed_path