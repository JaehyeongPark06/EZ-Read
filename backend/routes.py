from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse, FileResponse
import os
import shutil
import logging
from darkmode import Darkmode, main as darkmode_main

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/convert-pdf/")
async def convert_pdf(file: UploadFile = File(...), quality: str = Form(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(
            status_code=400, detail="Invalid file type. Only PDFs are allowed."
        )

    if quality == "high":
        dpi_count = 900
    elif quality == "medium":
        dpi_count = 600
    elif quality == "low":
        dpi_count = 300

    input_path = f"temp_{file.filename}"
    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    output_path, first_page_image = darkmode_main([input_path], dpi_count)
    logger.info(f"Converted PDF: {output_path}")
    logger.info(f"First page image: {first_page_image}")
    return JSONResponse(
        {
            "pdf_url": f"/download/{os.path.basename(output_path)}",
            "image_url": f"/image/{os.path.basename(first_page_image)}",
        }
    )


@router.get("/download/{file_path}")
async def download_file(file_path: str):
    return FileResponse(path=file_path, filename=file_path)


@router.get("/image/{image_path}")
async def get_image(image_path: str):
    return FileResponse(path=image_path, filename=image_path)
