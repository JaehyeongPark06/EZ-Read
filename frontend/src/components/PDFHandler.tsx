"use client";

import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectLabel,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useRef, useState } from "react";

import { Button } from "@/components/ui/button";
import axios from "axios";

interface PDFHandlerProps {
  setImageFileUrl: (url: string) => void;
  setPdfFileUrl: (url: string) => void;
  setFileName: (filename: string) => void;
  setIsConverting: (isConverting: boolean) => void;
}

const PDFHandler = ({
  setImageFileUrl,
  setPdfFileUrl,
  setFileName,
  setIsConverting,
}: PDFHandlerProps) => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [quality, setQuality] = useState<string>("");
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  const handleButtonClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setFileName(file.name);
      setSelectedFile(file);
    }
  };

  const handleConvert = async () => {
    if (!selectedFile || !quality) return;

    const formData = new FormData();
    formData.append("file", selectedFile);
    formData.append("quality", quality);

    setIsConverting(true);
    try {
      const response = await axios.post(
        "http://127.0.0.1:8000/convert-pdf/",
        formData,
        { headers: { "Content-Type": "multipart/form-data" } }
      );
      const { pdf_url, image_url } = response.data;
      setPdfFileUrl(pdf_url); // Set the PDF file URL
      setImageFileUrl(image_url);
    } catch (error) {
      if (axios.isAxiosError(error)) {
        console.error("Axios error uploading file:", error);
      } else {
        console.error("Error uploading file:", error);
      }
    } finally {
      setIsConverting(false);
    }
  };

  return (
    <div className="flex flex-col gap-4 w-full">
      <div className="flex flex-col w-full items-center gap-2">
        <Button variant="secondary" onClick={handleButtonClick}>
          Browse
        </Button>
        <input
          type="file"
          ref={fileInputRef}
          accept="application/pdf"
          className="hidden"
          onChange={handleFileChange}
        />
        <div className="w-full text-base text-white font-normal text-center mt-2">
          {selectedFile ? selectedFile.name : "No file selected"}
        </div>
        <Select onValueChange={(value) => setQuality(value)}>
          <SelectTrigger className="w-[180px] my-2">
            <SelectValue placeholder="Select quality" />
          </SelectTrigger>
          <SelectContent>
            <SelectGroup>
              <SelectLabel>Qualities</SelectLabel>
              <SelectItem value="high">High</SelectItem>
              <SelectItem value="medium">Medium</SelectItem>
              <SelectItem value="low">Low</SelectItem>
            </SelectGroup>
          </SelectContent>
        </Select>
      </div>
      <div className="flex flex-col items-center gap-2">
        <Button
          variant="destructive"
          onClick={handleConvert}
          disabled={!selectedFile || !quality}
        >
          Convert
        </Button>
      </div>
    </div>
  );
};

export default PDFHandler;
