import { useState } from "react";
import JSZip from "jszip";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { DocumentIcon } from "@heroicons/react/24/outline";
import { ArrowUpIcon } from "@heroicons/react/24/outline";
import { captureEvent } from "@/lib/posthog";


export function UploadForm() {
  const [zipFile, setZipFile] = useState<File | null>(null);
  const [fileNames, setFileNames] = useState<string[]>([]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const selectedFile = e.target.files[0];
      if (selectedFile && selectedFile.name.endsWith(".zip")) {
        setZipFile(selectedFile);
        setFileNames([]);
        captureEvent('zip_file_selected', {
          fileName: selectedFile.name,
          fileSize: selectedFile.size,
          fileType: selectedFile.type
        });
      } else {
        alert("Please upload a valid ZIP file.");
        captureEvent('invalid_file_upload_attempt', {
          fileName: selectedFile?.name,
          fileType: selectedFile?.type
        });
      }
    }
  };

  const handleUpload = async () => {
    if (zipFile) {
      captureEvent('upload_started', {
        fileName: zipFile.name,
        fileSize: zipFile.size
      });
      
      try {
        const zip = new JSZip();
        const zipContent = await zip.loadAsync(zipFile);
        const files: string[] = [];
        zipContent.forEach((relativePath) => {
          files.push(relativePath);
        });
        setFileNames(files);
        
        captureEvent('zip_contents_processed', {
          fileName: zipFile.name,
          fileCount: files.length
        });
      } catch (error) {
        captureEvent('zip_processing_error', {
          fileName: zipFile.name,
          error: (error as Error).message
        });
      }
    }
  };

  return (
    <div className="flex items-center justify-center space-x-4">
      {/* Input Field */}
      <Input
        type="text"
        placeholder="Enter text here"
        className="w-[60vw] p-4 text-lg border-2 border-gray-300 rounded-md"
      />

      {/* File Upload Button */}
      <label htmlFor="zip-upload">
        <Button
          variant="outline"
          className="flex items-center space-x-2 p-4"
        >
          <DocumentIcon className="w-6 h-6" />
          <span>Upload ZIP</span>
        </Button>
      </label>
      <input
        id="zip-upload"
        type="file"
        accept=".zip"
        onChange={handleFileChange}
        className="hidden"
      />

      {/* Final Button */}
      <button
        className="w-12 h-12 bg-black text-white flex items-center justify-center rounded"
        aria-label="Start Process"
        onClick={handleUpload}
      >
        <ArrowUpIcon className="w-6 h-6" />
      </button>
      {/* Display File Names */}
      {fileNames.length > 0 && (
        <div className="mt-4">
          <h3 className="text-lg font-semibold">Uploaded Files:</h3>
          <ul className="list-disc pl-5">
            {fileNames.map((fileName, index) => (
              <li key={index}>{fileName}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
