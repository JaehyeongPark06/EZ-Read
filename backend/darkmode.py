# Heavily modified version of https://github.com/JustinTheWhale/PDF-Dark-Mode/

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
import boto3
import threading
import tempfile
from urllib.parse import urlparse
import os
from dotenv import load_dotenv
from s3_utils import generate_presigned_url
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# S3 config
s3_client = boto3.client("s3")
load_dotenv()
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")


class Darkmode:
    def __init__(self) -> None:
        self.threads = min(mp.cpu_count(), 16)
        self.pdfs = []
        self.pngs = []
        self.temp_pdfs = []
        self.first_page_image = None
        self.schedule_bucket_cleanup()  # Start the cleanup process

    def upload_to_s3(self, local_file_path: str, s3_key: str) -> None:
        s3_client.upload_file(local_file_path, S3_BUCKET_NAME, s3_key)

    def download_from_s3(self, s3_key: str, suffix: str) -> str:
        tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        s3_client.download_file(S3_BUCKET_NAME, s3_key, tmp_file.name)
        return tmp_file.name

    def pdf_to_png(self, dpi_count: int) -> None:
        for file in self.pdfs:
            try:
                local_pdf = self.download_from_s3(file, ".pdf")
                pages = convert_from_path(
                    local_pdf, dpi_count, thread_count=self.threads
                )
                os.remove(local_pdf)
                new_name = file[:-4]
                for i, page in enumerate(pages):
                    name = f"{new_name}_page_{i:03d}_converted.png"
                    with tempfile.NamedTemporaryFile(
                        delete=False, suffix=".png"
                    ) as tmp_file:
                        page.save(tmp_file.name, "PNG", optimize=True, compress_level=9)
                        self.upload_to_s3(tmp_file.name, name)
                    self.pngs.append(name)
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
                tmp_file = self.download_from_s3(file, ".png")
                color_array = cv2.imread(tmp_file)
                color_array = self.speed(color_array)
                cv2.imwrite(tmp_file, color_array, [cv2.IMWRITE_PNG_COMPRESSION, 9])
                self.upload_to_s3(tmp_file, file)
                os.remove(tmp_file)
            except Exception as e:
                logger.error(f"Error in black_to_grey conversion for {file}: {e}")

    def png_to_pdf(self, files: List[str]) -> None:
        for png in files:
            try:
                tmp_file = self.download_from_s3(png, ".png")
                image = Image.open(tmp_file)
                width, height = image.size
                pdf = FPDF(unit="pt", format=[width, height])
                pdf.add_page()
                pdf.image(tmp_file, 0, 0, width, height)
                name = png.replace(".png", "_converted.pdf")
                pdf_tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
                pdf.output(pdf_tmp_file.name, "F")
                self.temp_pdfs.append(name)
                self.upload_to_s3(pdf_tmp_file.name, name)
                os.remove(tmp_file)
                os.remove(pdf_tmp_file.name)
            except Exception as e:
                logger.error(f"Error converting PNG to PDF for {png}: e")

    def schedule_deletion(self, s3_key: str) -> None:
        def delete_file():
            try:
                s3_client.delete_object(Bucket=S3_BUCKET_NAME, Key=s3_key)
                logger.info(f"Deleted {s3_key} from S3.")
            except Exception as e:
                logger.error(f"Error deleting {s3_key} from S3: {e}")

        delay = 3600  # 1 hour
        threading.Timer(delay, delete_file).start()

    def repack(self, original_pdf: str) -> str:
        pdf = original_pdf.split(".pdf")[0]
        merger = PdfMerger()
        for file in sorted(self.temp_pdfs):
            tmp_file = self.download_from_s3(file, ".pdf")
            merger.append(tmp_file)
            os.remove(tmp_file)
        converted_pdf = f"{pdf}_converted.pdf"
        converted_pdf_tmp_file = tempfile.NamedTemporaryFile(
            delete=False, suffix=".pdf"
        )
        merger.write(converted_pdf_tmp_file.name)
        merger.close()
        self.upload_to_s3(converted_pdf_tmp_file.name, converted_pdf)
        os.remove(converted_pdf_tmp_file.name)
        for temp_pdf in self.temp_pdfs:
            s3_client.delete_object(Bucket=S3_BUCKET_NAME, Key=temp_pdf)
        for png in self.pngs:
            if png != self.first_page_image:
                s3_client.delete_object(Bucket=S3_BUCKET_NAME, Key=png)
        s3_client.delete_object(Bucket=S3_BUCKET_NAME, Key=original_pdf)
        logger.info(f"Repacked all temporary PDFs into {converted_pdf}.")
        return converted_pdf

    def process_and_upload(self, files: List[str], dpi_count: int) -> dict:
        # Upload the original PDF to S3
        for file in files:
            s3_key = os.path.basename(file)
            self.upload_to_s3(file, s3_key)
            self.pdfs.append(s3_key)
            os.remove(file)  # Remove the original PDF after uploading

        self.pdf_to_png(dpi_count)
        self.start_processes()
        self.start_threads()
        converted_pdf_url = self.repack(self.pdfs[0])

        # Extract the key from the URL
        converted_pdf_key = urlparse(converted_pdf_url).path.lstrip("/")
        first_page_key = self.first_page_image

        logging.info(f"Converted PDF Key: {converted_pdf_key}")
        logging.info(f"First page image key: {first_page_key}")

        presigned_urls = {
            "pdf_url": generate_presigned_url(converted_pdf_key),
            "first_page_url": generate_presigned_url(first_page_key),
        }

        self.schedule_deletion(self.first_page_image)

        # Delete the original PDF from S3
        for s3_key in self.pdfs:
            s3_client.delete_object(Bucket=S3_BUCKET_NAME, Key=s3_key)

        return presigned_urls

    def delete_all_s3_contents(self):
        try:
            objects = s3_client.list_objects_v2(Bucket=S3_BUCKET_NAME).get(
                "Contents", []
            )
            if objects:
                keys = [{"Key": obj["Key"]} for obj in objects]
                s3_client.delete_objects(
                    Bucket=S3_BUCKET_NAME, Delete={"Objects": keys}
                )
                logger.info(f"Deleted all contents from S3 bucket {S3_BUCKET_NAME}.")
            else:
                logger.info(f"No contents to delete in S3 bucket {S3_BUCKET_NAME}.")
        except Exception as e:
            logger.error(f"Error deleting contents from S3 bucket: {e}")

    def schedule_bucket_cleanup(self):
        def cleanup():
            while True:
                self.delete_all_s3_contents()
                time.sleep(3600)  # Wait for 1 hour

        cleanup_thread = threading.Thread(target=cleanup, daemon=True)
        cleanup_thread.start()


def main(files: List[str], dpi_count: int) -> dict:
    darkmode_generator = Darkmode()
    return darkmode_generator.process_and_upload(files, dpi_count)
