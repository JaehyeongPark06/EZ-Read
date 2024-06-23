"use client";

import { Button } from "@/components/ui/button";
import Image from "next/image";
import { Loader2 } from "lucide-react";

const Icons = {
  spinner: Loader2,
};

interface PDFPreviewProps {
  imageFileUrl: string | null;
  pdfFileUrl: string | null;
  isConverting: boolean;
}

const PDFPreview = ({
  imageFileUrl,
  pdfFileUrl,
  isConverting,
}: PDFPreviewProps) => {
  const handleDownload = async () => {
    if (!pdfFileUrl) return;

    const response = await fetch(pdfFileUrl);

    console.log(response);
    if (!response.ok) {
      console.error("Failed to download PDF");
      return;
    }
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);

    // Extract filename from URL without query string
    const urlParts = pdfFileUrl.split("?")[0].split("/");
    const filename = urlParts[urlParts.length - 1];

    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.URL.revokeObjectURL(url);
  };

  return (
    <div className="w-full flex flex-col items-center justify-center gap-8">
      {isConverting ? (
        <Icons.spinner className="h-7 w-7 animate-spin text-white m-auto mb-[8px]" />
      ) : imageFileUrl ? (
        <Image
          width={0}
          height={0}
          sizes="90vw"
          src={imageFileUrl}
          alt="Converted PDF First Page"
          className="rounded-2xl mx-auto flex max-w-screen-sm"
          style={{ width: "100%", height: "auto" }}
          placeholder="empty"
        />
      ) : null}
      <Button onClick={handleDownload} disabled={!pdfFileUrl} variant="outline">
        Download PDF
      </Button>
    </div>
  );
};

export default PDFPreview;
