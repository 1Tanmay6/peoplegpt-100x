import * as React from "react";
import { ArrowUpIcon, DocumentIcon } from "@heroicons/react/24/outline";
import { ReloadIcon } from "@radix-ui/react-icons";
import { v4 as uuidv4 } from "uuid";
import { Topbar } from "@/components/Topbar";
import { useEffect } from 'react';
import { captureEvent } from '@/lib/posthog';
import { useNavigate } from "react-router-dom";

interface FileUploadResponse {
  job_id: string;
  message: string;
}

export default function HomePage() {
  const [prompt, setPrompt] = React.useState<string>("");
  const [zipFile, setZipFile] = React.useState<File | null>(null);
  const [loading, setLoading] = React.useState<boolean>(false);
  const navigate = useNavigate();

  useEffect(() => {
    captureEvent('home_page_loaded');
    return () => {
      captureEvent('home_page_unloaded');
    };
  }, []);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      setZipFile(selectedFile);
      captureEvent('file_selected', {
        fileSize: selectedFile.size,
        fileType: selectedFile.type
      });
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!zipFile) return;

    setLoading(true);
    const formData = new FormData();
    formData.append("zip_file", zipFile);
    formData.append("prompt", prompt);
    formData.append("job_id", uuidv4());

    try {
      captureEvent('upload_started', {
        hasPrompt: Boolean(prompt)
      });

      const response = await fetch("http://localhost:8000/upload_and_run", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) throw new Error('Upload failed');

      const data: FileUploadResponse = await response.json();
      
      captureEvent('upload_completed', {
        jobId: data.job_id
      });

      navigate("/history");
    } catch (error) {
      captureEvent('upload_error', {
        error: error instanceof Error ? error.message : 'Unknown error'
      });
      console.error("Error:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <Topbar />
      <main className="min-h-screen flex flex-col items-center justify-center bg-white px-4">
        <h1 className="text-6xl font-extrabold text-gray-900 mb-15">PeopleGPT</h1>
        <form onSubmit={handleSubmit} className="w-full max-w-3xl space-y-6">
          <div className="flex flex-col md:flex-row items-center w-full max-w-3xl space-y-4 md:space-y-0 md:space-x-4">
            <label htmlFor="zip-upload" className="flex-1 w-full">
              <div className="flex justify-center w-full h-32 px-4 transition bg-white border-2 border-gray-300 border-dashed rounded-md appearance-none cursor-pointer hover:border-gray-400 focus:outline-none">
                <span className="flex items-center space-x-2">
                  <ArrowUpIcon className="w-6 h-6 text-gray-600" />
                  <span className="font-medium text-gray-600">
                    {zipFile ? zipFile.name : "Drop files to Attach, or browse"}
                  </span>
                </span>
              </div>
            </label>
            <input
              id="zip-upload"
              type="file"
              accept=".zip"
              onChange={handleFileChange}
              className="hidden"
            />
          </div>

          <div className="flex items-center space-x-4">
            <input
              type="text"
              placeholder="Enter your job description prompt..."
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              className="flex-1 p-4 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button
              type="submit"
              disabled={!zipFile || loading}
              className={`px-8 py-4 rounded-lg text-white font-medium ${
                loading || !zipFile
                  ? "bg-gray-400 cursor-not-allowed"
                  : "bg-blue-600 hover:bg-blue-700"
              }`}
            >
              {loading ? (
                <ReloadIcon className="w-6 h-6 animate-spin" />
              ) : (
                <DocumentIcon className="w-6 h-6" />
              )}
            </button>
          </div>
        </form>

        <p className="mx-auto mt-4 text-center text-gray-500 text-base leading-tight max-w-xs">
          Upload a zip file containing resumes to analyze
        </p>
      </main>
    </>
  );
}
