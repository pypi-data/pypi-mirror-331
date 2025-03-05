# Vintager
Lightweight Python library to convert photos to a vintage style.
| Original                                                                                                    | Vintage Sepia                                                                                                         |
|-------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------|
| ![](https://raw.githubusercontent.com/Fran-98/vintager/refs/heads/main/assets/original.jpg)                 | ![](https://raw.githubusercontent.com/Fran-98/vintager/refs/heads/main/assets/sepia.jpg)                                                                                        |
| Black and white high contrast                                                                               | Film                                                                                                          |
| ![](https://raw.githubusercontent.com/Fran-98/vintager/refs/heads/main/assets/black_and_white_contrast.jpg) | ![](https://raw.githubusercontent.com/Fran-98/vintager/refs/heads/main/assets/all.jpg)                                                                                          |


## Installation

Just use:

```bash
pip install vintager
```

To install locally this package, you can run:

```bash
git clone https://github.com/Fran-98/vintager
pip install .
```

## Use

```python
from vintager.vintager import convert

im = convert(<image_path>, 
        <image_output_path>, 
        black_and_white=False, 
        high_contrast_black_and_white=False, 
        apply_sepia=False, 
        apply_vintage=True, 
        apply_grain=True, 
        noise_level=100
        )
```

Or from cli using `vintager <image_path> <image_output_path>` (use --help for optional parameters)