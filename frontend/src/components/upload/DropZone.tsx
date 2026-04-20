import { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, FileText, X } from 'lucide-react';
import { getFileValidationError } from '../../utils/validators';
import { formatFileSize } from '../../utils/formatters';
import UploadProgress from './UploadProgress';

interface DropZoneProps {
  onUpload: (file: File) => Promise<void>;
  isUploading?: boolean;
}

export default function DropZone({ onUpload, isUploading = false }: DropZoneProps) {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [progress, setProgress] = useState(0);

  const onDrop = useCallback(
    (acceptedFiles: File[]) => {
      setError(null);
      const file = acceptedFiles[0];
      if (!file) return;

      const validationError = getFileValidationError(file);
      if (validationError) {
        setError(validationError);
        return;
      }

      setSelectedFile(file);
    },
    []
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'text/plain': ['.txt'],
    },
    maxFiles: 1,
    disabled: isUploading,
  });

  const handleUpload = async () => {
    if (!selectedFile) return;
    setProgress(10);
    try {
      // Simulate progress since axios doesn't give us upload progress with the current setup
      const progressInterval = setInterval(() => {
        setProgress((prev) => Math.min(prev + 15, 90));
      }, 300);

      await onUpload(selectedFile);

      clearInterval(progressInterval);
      setProgress(100);
      setTimeout(() => {
        setSelectedFile(null);
        setProgress(0);
      }, 1000);
    } catch {
      setProgress(0);
    }
  };

  const clearFile = () => {
    setSelectedFile(null);
    setError(null);
    setProgress(0);
  };

  return (
    <div className="w-full">
      <div
        {...getRootProps()}
        className={`cursor-pointer rounded-lg border-2 border-dashed p-8 text-center transition-colors ${
          isDragActive
            ? 'border-indigo-500 bg-indigo-50 dark:bg-indigo-900/20'
            : 'border-gray-300 hover:border-indigo-400 dark:border-gray-600 dark:hover:border-indigo-500'
        } ${isUploading ? 'pointer-events-none opacity-50' : ''}`}
      >
        <input {...getInputProps()} />
        <Upload className="mx-auto mb-3 h-10 w-10 text-gray-400 dark:text-gray-500" />
        {isDragActive ? (
          <p className="text-sm text-indigo-600 dark:text-indigo-400">Drop the file here...</p>
        ) : (
          <>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Drag & drop a document here, or click to browse
            </p>
            <p className="mt-1 text-xs text-gray-400 dark:text-gray-500">
              PDF, DOCX, or TXT — up to 20 MB
            </p>
          </>
        )}
      </div>

      {error && (
        <p className="mt-2 text-sm text-red-600 dark:text-red-400">{error}</p>
      )}

      {selectedFile && !isUploading && progress === 0 && (
        <div className="mt-4 flex items-center justify-between rounded-lg border border-gray-200 bg-gray-50 px-4 py-3 dark:border-gray-700 dark:bg-gray-800">
          <div className="flex items-center gap-3">
            <FileText className="h-5 w-5 text-indigo-600 dark:text-indigo-400" />
            <div>
              <p className="text-sm font-medium text-gray-900 dark:text-white">
                {selectedFile.name}
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                {formatFileSize(selectedFile.size)}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={clearFile}
              className="rounded p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
              aria-label="Remove file"
            >
              <X className="h-4 w-4" />
            </button>
            <button
              onClick={handleUpload}
              className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700"
            >
              Upload
            </button>
          </div>
        </div>
      )}

      {(isUploading || progress > 0) && progress < 100 && (
        <div className="mt-4">
          <UploadProgress progress={progress} label="Uploading..." />
        </div>
      )}
    </div>
  );
}
