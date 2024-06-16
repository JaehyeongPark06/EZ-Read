"use client";

import PDFHandler from "./PDFHandler";
import PDFPreview from "./PDFPreview";
import { useState } from "react";

const PDFUpload = () => {
  const [imageFileUrl, setImageFileUrl] = useState<string | null>(null);
  const [pdfFileUrl, setPdfFileUrl] = useState<string | null>(null);
  const [fileName, setFileName] = useState<string | null>(null);
  const [isConverting, setIsConverting] = useState<boolean>(false);

  return (
    <div className="flex flex-col items-center justify-center gap-10">
      <PDFHandler
        setImageFileUrl={setImageFileUrl}
        setFileName={setFileName}
        setIsConverting={setIsConverting}
        setPdfFileUrl={setPdfFileUrl}
      />
      <PDFPreview
        imageFileUrl={imageFileUrl}
        isConverting={isConverting}
        pdfFileUrl={pdfFileUrl}
      />
    </div>
  );
};

export default PDFUpload;
