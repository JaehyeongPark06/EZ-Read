from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
import shutil
import logging
from darkmode import main as darkmode_main
import os

# Logging
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

    input_path = file.filename
    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    presigned_urls = darkmode_main([input_path], dpi_count)
    logger.info(f"Converted PDF available at: {presigned_urls['pdf_url']}")
    logger.info(f"First page image available at: {presigned_urls['first_page_url']}")

    # Clean up
    if os.path.exists(input_path):
        os.remove(input_path)

    return JSONResponse(
        {
            "pdf_url": presigned_urls["pdf_url"],
            "first_page_url": presigned_urls["first_page_url"],
        }
    )
