# Heavily modified version of https://github.com/JustinTheWhale/PDF-Dark-Mode/
import os
import multiprocessing as mp
from concurrent.futures import ThreadPoolExecutor
from typing import List
import cv2
import numpy as np
from fpdf import FPDF
from numba import jit
from pdf2image import convert_from_path
from PIL import Image
from PyPDF2 import PdfMerger
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Darkmode:
    def __init__(self) -> None:
        self.threads = min(mp.cpu_count(), 16)
        self.pdfs = []
        self.pngs = []
        self.temp_pdfs = []
        self.first_page_image = None

    def pdf_to_png(self, dpi_count: int) -> None:
        for file in self.pdfs:
            try:
                pages = convert_from_path(
                    file, dpi=dpi_count, thread_count=self.threads
                )
                new_name = file[:-4]
                for i, page in enumerate(pages):
                    name = f"{new_name}_page_{i:03d}_converted.png"
                    self.pngs.append(name)
                    page.save(name, "PNG", optimize=True, compress_level=9)
                    if i == 0:
                        self.first_page_image = name
                logger.info(f"Converted {len(pages)} pages of {file} to PNGs.")
            except Exception as e:
                logger.error(f"Error converting PDF to PNG: {e}")

    def make_batches(self, task_list: List) -> List[List[str]]:
        if len(task_list) <= self.threads:
            return [task_list]
        else:
            return [
                task_list[i : i + self.threads]
                for i in range(0, len(task_list), self.threads)
            ]

    def start_processes(self) -> None:
        batches = self.make_batches(self.pngs)
        with mp.Pool(processes=self.threads) as pool:
            pool.map(self.black_to_grey, batches)
        logger.info(f"Processed {len(batches)} batches with multiprocessing.")

    def start_threads(self) -> None:
        batches = self.make_batches(self.pngs)
        with ThreadPoolExecutor(self.threads) as pool:
            pool.map(self.png_to_pdf, batches)
        logger.info(f"Processed {len(batches)} batches with threading.")

    @staticmethod
    @jit(nopython=True, cache=True, fastmath=True)
    def speed(image: np.ndarray) -> np.ndarray:
        grey = np.array([40, 40, 40], dtype=np.uint8)
        white = np.array([255, 255, 255], dtype=np.uint8)
        for i in range(len(image)):
            for j in range(len(image[0])):
                pixel = image[i, j]
                if np.all(pixel == 255):
                    image[i, j] = grey
                elif np.all(pixel == 0):
                    image[i, j] = white
        return image

    def black_to_grey(self, files: List[str]) -> None:
        for file in files:
            try:
                color_array = cv2.imread(file)
                color_array = self.speed(color_array)
                cv2.imwrite(file, color_array, [cv2.IMWRITE_PNG_COMPRESSION, 9])
            except Exception as e:
                logger.error(f"Error in black_to_grey conversion for {file}: {e}")

    def png_to_pdf(self, files: List[str]) -> None:
        for png in files:
            try:
                image = Image.open(png)
                width, height = image.size
                pdf = FPDF(unit="pt", format=[width, height])
                pdf.add_page()
                pdf.image(png, 0, 0, width, height)
                name = png.replace(".png", "_temp_converted.pdf")
                pdf.output(name, "F")
                self.temp_pdfs.append(name)
            except Exception as e:
                logger.error(f"Error converting PNG to PDF for {png}: {e}")

    def repack(self, original_pdf: str) -> str:
        pdf = original_pdf.split(".pdf")[0]
        merger = PdfMerger()
        for file in sorted(self.temp_pdfs):
            merger.append(file)
        converted_pdf = f"{pdf}_converted.pdf"
        merger.write(converted_pdf)
        merger.close()
        for temp_pdf in self.temp_pdfs:
            os.remove(temp_pdf)
        for png in self.pngs:
            if png != self.first_page_image:
                os.remove(png)
        os.remove(original_pdf)
        logger.info(f"Repacked all temporary PDFs into {converted_pdf}.")
        return converted_pdf


def main(files: List[str], dpi_count: int) -> str:
    darkmode_generator = Darkmode()
    for file in files:
        darkmode_generator.pdfs.append(file)

    darkmode_generator.pdf_to_png(dpi_count)
    darkmode_generator.start_processes()
    darkmode_generator.start_threads()
    converted_pdf = darkmode_generator.repack(files[0])

    return converted_pdf, darkmode_generator.first_page_image
