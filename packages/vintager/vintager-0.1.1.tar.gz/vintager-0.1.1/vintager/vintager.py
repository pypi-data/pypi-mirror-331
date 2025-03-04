from PIL import Image, ImageOps
import argparse
import numpy as np

VINTAGE_COLOR_LEVELS = {
    'r': np.array([0, 0, 0, 1, 1, 2, 3, 3, 3, 4, 4, 4, 5, 5, 5, 6, 6, 7, 7, 7, 7, 8, 8, 8, 9, 9, 9, 9, 10, 10, 10, 10, 11, 11, 12, 12, 12, 12, 13, 13, 13, 14, 14, 15, 15, 16, 16, 17, 17, 17, 18, 19, 19, 20, 21, 22, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 39, 40, 41, 42, 44, 45, 47, 48, 49, 52, 54, 55, 57, 59, 60, 62, 65, 67, 69, 70, 72, 74, 77, 79, 81, 83, 86, 88, 90, 92, 94, 97, 99, 101, 103, 107, 109, 111, 112, 116, 118, 120, 124, 126, 127, 129, 133, 135, 136, 140, 142, 143, 145, 149, 150, 152, 155, 157, 159, 162, 163, 165, 167, 170, 171, 173, 176, 177, 178, 180, 183, 184, 185, 188, 189, 190, 192, 194, 195, 196, 198, 200, 201, 202, 203, 204, 206, 207, 208, 209, 211, 212, 213, 214, 215, 216, 218, 219, 219, 220, 221, 222, 223, 224, 225, 226, 227, 227, 228, 229, 229, 230, 231, 232, 232, 233, 234, 234, 235, 236, 236, 237, 238, 238, 239, 239, 240, 241, 241, 242, 242, 243, 244, 244, 245, 245, 245, 246, 247, 247, 248, 248, 249, 249, 249, 250, 251, 251, 252, 252, 252, 253, 254, 254, 254, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255]),
    'g' : np.array([0, 0, 1, 2, 2, 3, 5, 5, 6, 7, 8, 8, 10, 11, 11, 12, 13, 15, 15, 16, 17, 18, 18, 19, 21, 22, 22, 23, 24, 26, 26, 27, 28, 29, 31, 31, 32, 33, 34, 35, 35, 37, 38, 39, 40, 41, 43, 44, 44, 45, 46, 47, 48, 50, 51, 52, 53, 54, 56, 57, 58, 59, 60, 61, 63, 64, 65, 66, 67, 68, 69, 71, 72, 73, 74, 75, 76, 77, 79, 80, 81, 83, 84, 85, 86, 88, 89, 90, 92, 93, 94, 95, 96, 97, 100, 101, 102, 103, 105, 106, 107, 108, 109, 111, 113, 114, 115, 117, 118, 119, 120, 122, 123, 124, 126, 127, 128, 129, 131, 132, 133, 135, 136, 137, 138, 140, 141, 142, 144, 145, 146, 148, 149, 150, 151, 153, 154, 155, 157, 158, 159, 160, 162, 163, 164, 166, 167, 168, 169, 171, 172, 173, 174, 175, 176, 177, 178, 179, 181, 182, 183, 184, 186, 186, 187, 188, 189, 190, 192, 193, 194, 195, 195, 196, 197, 199, 200, 201, 202, 202, 203, 204, 205, 206, 207, 208, 208, 209, 210, 211, 212, 213, 214, 214, 215, 216, 217, 218, 219, 219, 220, 221, 222, 223, 223, 224, 225, 226, 226, 227, 228, 228, 229, 230, 231, 232, 232, 232, 233, 234, 235, 235, 236, 236, 237, 238, 238, 239, 239, 240, 240, 241, 242, 242, 242, 243, 244, 245, 245, 246, 246, 247, 247, 248, 249, 249, 249, 250, 251, 251, 252, 252, 252, 253, 254, 255]),
    'b' : np.array([53, 53, 53, 54, 54, 54, 55, 55, 55, 56, 57, 57, 57, 58, 58, 58, 59, 59, 59, 60, 61, 61, 61, 62, 62, 63, 63, 63, 64, 65, 65, 65, 66, 66, 67, 67, 67, 68, 69, 69, 69, 70, 70, 71, 71, 72, 73, 73, 73, 74, 74, 75, 75, 76, 77, 77, 78, 78, 79, 79, 80, 81, 81, 82, 82, 83, 83, 84, 85, 85, 86, 86, 87, 87, 88, 89, 89, 90, 90, 91, 91, 93, 93, 94, 94, 95, 95, 96, 97, 98, 98, 99, 99, 100, 101, 102, 102, 103, 104, 105, 105, 106, 106, 107, 108, 109, 109, 110, 111, 111, 112, 113, 114, 114, 115, 116, 117, 117, 118, 119, 119, 121, 121, 122, 122, 123, 124, 125, 126, 126, 127, 128, 129, 129, 130, 131, 132, 132, 133, 134, 134, 135, 136, 137, 137, 138, 139, 140, 140, 141, 142, 142, 143, 144, 145, 145, 146, 146, 148, 148, 149, 149, 150, 151, 152, 152, 153, 153, 154, 155, 156, 156, 157, 157, 158, 159, 160, 160, 161, 161, 162, 162, 163, 164, 164, 165, 165, 166, 166, 167, 168, 168, 169, 169, 170, 170, 171, 172, 172, 173, 173, 174, 174, 175, 176, 176, 177, 177, 177, 178, 178, 179, 180, 180, 181, 181, 181, 182, 182, 183, 184, 184, 184, 185, 185, 186, 186, 186, 187, 188, 188, 188, 189, 189, 189, 190, 190, 191, 191, 192, 192, 193, 193, 193, 194, 194, 194, 195, 196, 196, 196, 197, 197, 197, 198, 199])
    }

def modify_all_pixels(im, pixel_callback):
    """
    Modify all pixels in an image using a callback function.
    
    Args:
        im (PIL.Image): The image object to modify.
        pixel_callback (function): The function that processes individual pixels.
        
    Returns:
        PIL.Image: A modified image object.
    """
    arr = np.array(im)

    def wrapper(p):
        if len(p) == 4:
            r, g, b, a = p
            r, g, b = pixel_callback(0, 0, r, g, b)
            return [r, g, b, a] 
        else:  # RGB
            return pixel_callback(0, 0, *p)

    arr = np.apply_along_axis(wrapper, 2, arr)
    return Image.fromarray(arr.astype(np.uint8))

def vintage_colors(arr, color_map = VINTAGE_COLOR_LEVELS):
    """
    Apply vintage color mapping to the RGB channels of an image array.
    
    Args:
        arr (np.ndarray): The image array in RGB format.
        color_map (dict, optional): Dictionary mapping RGB channels to vintage color levels.
        
    Returns:
        np.ndarray: The modified image array with vintage color effects.
    """
    r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
    arr[:, :, 0] = color_map['r'][r]
    arr[:, :, 1] = color_map['g'][g]
    arr[:, :, 2] = color_map['b'][b]
    return arr

def add_grain(arr, noise_level=50):
    """
    Add noise (grain) to the image.
    
    Args:
        arr (np.ndarray): The image array to which noise will be added.
        noise_level (int, optional): The intensity of the grain noise to apply.
        
    Returns:
        np.ndarray: The image array with added noise.
    """
    noise = np.random.randint(-noise_level//2, noise_level//2, arr.shape[:2], dtype=np.int16)
    arr[:, :, 0:3] = np.clip(arr[:, :, 0:3] + noise[:, :, None], 0, 255)
    return arr

def to_black_and_white(im):
    """
    Convert an image to black and white (grayscale).
    
    Args:
        im (PIL.Image): The image object to convert.
        
    Returns:
        PIL.Image: The converted black and white image.
    """
    return ImageOps.grayscale(im).convert("RGB")

def adjust_contrast(arr, factor=1.3):
    """Increase contrast by stretching the histogram."""
    mean = np.mean(arr, axis=(0, 1), keepdims=True)
    arr = mean + (arr - mean) * factor
    return np.clip(arr, 0, 255).astype(np.uint8)


def apply_sepia_tone(arr, intensity=1.2, contrast=1.3):

    tr = (0.393 * arr[:, :, 0] + 0.769 * arr[:, :, 1] + 0.189 * arr[:, :, 2]) * intensity
    tg = (0.349 * arr[:, :, 0] + 0.686 * arr[:, :, 1] + 0.168 * arr[:, :, 2]) * intensity
    tb = (0.272 * arr[:, :, 0] + 0.534 * arr[:, :, 1] + 0.131 * arr[:, :, 2]) * intensity

    arr[:, :, 0] = np.clip(tr, 0, 255)
    arr[:, :, 1] = np.clip(tg, 0, 255)
    arr[:, :, 2] = np.clip(tb, 0, 255)

    # Apply contrast correction
    arr = adjust_contrast(arr, contrast)

    return arr


def convert(
        image_path: str, 
        output_path: str, 
        black_and_white: bool = False,
        high_contrast_black_and_white: bool = False, 
        apply_sepia: bool = False, 
        apply_vintage=True, 
        apply_grain=True, 
        noise_level=50
        ):
    """
    Convert an image to a vintage-styled image with optional effects like black and white, sepia, and grain.
    
    Args:
        image_path (str): Path to the input image.
        output_path (str): Path where the output image will be saved.
        high_contrast_black_and_white (bool, optional): Apply high contrast black and white effect. Default is False.
        apply_vintage (bool, optional): Apply vintage color effect. Default is True.
        apply_grain (bool, optional): Add grain to the image. Default is True.
        noise_level (int, optional): The noise intensity for the grain effect. Default is 50.
        
    Returns:
        PIL.Image: The converted image.
    """

    if high_contrast_black_and_white: # Yeap, same effect as using sepia with black and white
        black_and_white = True
        apply_sepia = True
    try:
        im = Image.open(image_path).convert("RGB")
    except Exception as e:
        print(f'Vintager error loading image: {e}')
        return
    
    arr = np.array(im, dtype=np.uint8)

    if apply_vintage:
        arr = vintage_colors(arr)
    if apply_grain:
        arr = add_grain(arr, noise_level)
    if apply_sepia:
        arr = apply_sepia_tone(arr, intensity=1, contrast=1.3)

    im = Image.fromarray(arr)

    if black_and_white:
        im = to_black_and_white(im)
    
    if output_path:
        im.save(output_path, optimize=True, compress_level=9)

    return im

def main():
    parser = argparse.ArgumentParser(description='Convert images to vintage style with various effects.')
    parser.add_argument('image_path', type=str, help='Path to the input image')
    parser.add_argument('output_path', type=str, help='Path to save the output image')
    parser.add_argument('--black_and_white', action='store_true', default=False, help='Apply black and white effect')
    parser.add_argument('--apply_sepia', action='store_true', default=False, help='Apply sepia effect')
    parser.add_argument('--high_contrast_black_and_white', action='store_true', help='Apply high contrast black and white effect')
    parser.add_argument('--apply_vintage', action='store_true', default= True, help='Apply vintage effect')
    parser.add_argument('--apply_grain', action='store_true', default= True, help='Add grain to the image')
    parser.add_argument('--noise_level', type=int, default=50, help='Intensity of grain effect')
    
    args = parser.parse_args()

    convert(args.image_path, args.output_path, 
            black_and_white=args.black_and_white,
            high_contrast_black_and_white=args.high_contrast_black_and_white,
            apply_sepia=args.apply_sepia,
            apply_vintage=args.apply_vintage,
            apply_grain=args.apply_grain,
            noise_level=args.noise_level
            )

if __name__ == '__main__':
    main()