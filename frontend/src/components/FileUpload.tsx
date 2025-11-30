"use client"

import React, { useCallback, useState } from 'react'
import { useDropzone } from 'react-dropzone'
import { Upload, File, X } from 'lucide-react'

export function FileUpload() {
  const [files, setFiles] = useState<File[]>([])
  const [uploading, setUploading] = useState(false)
  const [status, setStatus] = useState<string>("")

  const onDrop = useCallback((acceptedFiles: File[]) => {
    setFiles(prev => [...prev, ...acceptedFiles])
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({ onDrop })

  const handleUpload = async () => {
    if (files.length === 0) return

    setUploading(true)
    setStatus("Uploading to GCS...")

    try {
      // 1. Upload Files
      const formData = new FormData()
      files.forEach(file => {
        formData.append('files', file)
      })

      const uploadRes = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'}/upload`, {
        method: 'POST',
        body: formData,
      })

      if (!uploadRes.ok) throw new Error('Upload failed')

      const { uris } = await uploadRes.json()
      setStatus(`Uploaded ${uris.length} files. Starting extraction...`)

      // 2. Trigger Extraction
      const extractRes = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'}/extract`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ file_uris: uris }),
      })

      if (!extractRes.ok) throw new Error('Extraction failed')

      const result = await extractRes.json()
      console.log("Extraction Result:", result)
      setStatus("Extraction Complete! Check console for details.")

    } catch (e) {
      console.error(e)
      setStatus(`Error: ${e instanceof Error ? e.message : 'Unknown error'}`)
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="w-full max-w-md mx-auto p-6 bg-white rounded-xl shadow-md space-y-4">
      <h2 className="text-xl font-bold text-gray-800">Document Upload</h2>

      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors
            ${isDragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-blue-400'}`}
      >
        <input {...getInputProps()} />
        <Upload className="mx-auto h-12 w-12 text-gray-400 mb-3" />
        {isDragActive ? (
          <p className="text-blue-500">Drop the files here...</p>
        ) : (
          <p className="text-gray-500">Drag & drop files here, or click to select</p>
        )}
      </div>

      {files.length > 0 && (
        <div className="space-y-2">
          <h3 className="text-sm font-medium text-gray-700">Selected Files:</h3>
          {files.map((file, i) => (
            <div key={i} className="flex items-center justify-between p-2 bg-gray-50 rounded text-sm">
              <div className="flex items-center space-x-2 truncate">
                <File className="h-4 w-4 text-gray-500" />
                <span className="truncate max-w-[200px]">{file.name}</span>
              </div>
              <span className="text-gray-400 text-xs">{(file.size / 1024).toFixed(0)} KB</span>
            </div>
          ))}

          <button
            onClick={handleUpload}
            disabled={uploading}
            className="w-full mt-4 bg-black text-white py-2 rounded-lg font-medium hover:bg-gray-800 disabled:opacity-50 transition-colors"
          >
            {uploading ? 'Processing...' : 'Start Extraction'}
          </button>
        </div>
      )}

      {status && (
        <div className="mt-4 p-3 bg-blue-50 text-blue-700 rounded text-center text-sm">
          {status}
        </div>
      )}
    </div>
  )
}
