# EZ Read

![Image of a random converted pdf](https://github.com/JaehyeongPark06/EZ-Read/assets/78674944/63cc5623-02c8-4084-8f64-b138ff169050)

## About

A tool that converts PDFs to dark mode in seconds while preserving their original quality and colors. Allows custom quality selection (low, medium, high) (300, 600, 900 dpi respectively).

## Libraries and Tools Used

### Converter

- [FastAPI](https://fastapi.tiangolo.com/)
- [NumPy](https://numpy.org/)
- [Pillow](https://python-pillow.org/)
- [Numba (Jit)](https://numba.pydata.org/)
- [OpenCV](https://opencv.org/)

### Web

- [Next.js 14 (app router)](https://nextjs.org/docs/app)
- [Tailwind CSS](https://tailwindcss.com/)
- [Shadcn UI](https://ui.shadcn.dev/)
- [AWS S3](https://aws.amazon.com/s3/)

## Possible Improvements

- Using a different language for the converter, Python is a bit slow
- Detecting images and text when converting
- Making final PDF size smaller

## Stats

**NOTE: All benchmarks below were tested using a 1 page PDF with an image and using Python={3.12.3}. Times were recorded using the inubilt logging and time library in Python.**

| Quality Level | Conversion of PDF to PNGs (seconds) | Processing with multiprocessing (seconds) | Processing with threading (seconds) | Repacking PDFs (seconds) |
|---------------|-------------------------------------|--------------------------------------------|-------------------------------------|--------------------------|
| High          | 4.54                                | 5.64                                       | 0.00                                | 0.00                     |
| Medium        | 2.39                                | 3.06                                       | 0.00                                | 0.00                     |
| Low           | 0.81                                | 1.43                                       | 0.00                                | 0.00                     |

