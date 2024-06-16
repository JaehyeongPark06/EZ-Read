# EZ Read

![Image of a random converted pdf](https://github.com/JaehyeongPark06/EZ-Read/assets/78674944/63cc5623-02c8-4084-8f64-b138ff169050)

## About

A tool that converts PDFs to dark mode in seconds while preserving their original quality and colors. Allows custom quality selection (low, medium, high) (300, 600, 900 dpi respectively).

## Libraries and Tools Used

### Converter

- FastAPI
- NumPy
- Pillow
- Numba (Jit)
- OpenCV

### Web

- Next.js 14 (app router)
- Tailwind CSS
- shadcn ui

## Possible Improvements

- Using a different language for the converter, Python is a bit slow
- Detecting images and text when converting

## Stats

**NOTE: All benchmarks below were tested using a 1 page PDF with an image and using Python={3.12.3}. Additionally, times were recorded using the inubilt logging and time library in Python.**

### High Quality

- **Conversion of PDF to PNGs**: 4.54 seconds
- **Processing with multiprocessing**: 5.64 seconds (1 batch)
- **Processing with threading**: 0.00 seconds (1 batch)
- **Repacking PDFs**: 0.00 seconds

### Medium Quality

- **Conversion of PDF to PNGs**: 2.39 seconds
- **Processing with multiprocessing**: 3.06 seconds (1 batch)
- **Processing with threading**: 0.00 seconds (1 batch)
- **Repacking PDFs**: 0.00 seconds

### Low Quality

- **Conversion of PDF to PNGs**: 0.81 seconds
- **Processing with multiprocessing**: 1.43 seconds (1 batch)
- **Processing with threading**: 0.00 seconds (1 batch)
- **Repacking PDFs**: 0.00 seconds
