import React, { useState } from 'react';
import './FileUpload.css';

function FileUpload({ label, evidenceType, applicationId, onUploadSuccess, onUploadError }) {
  const [uploading, setUploading] = useState(false);
  const [uploadedFile, setUploadedFile] = useState(null);
  const [error, setError] = useState(null);

  const handleFileChange = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    // Validate file size (max 10MB)
    const maxSize = 10 * 1024 * 1024;
    if (file.size > maxSize) {
      setError('File too large (max 10MB)');
      return;
    }

    // Validate file type
    const allowedTypes = ['application/pdf', 'image/jpeg', 'image/png', 'image/jpg'];
    if (!allowedTypes.includes(file.type)) {
      setError('Only PDF, JPG, PNG files allowed');
      return;
    }

    setError(null);
    setUploading(true);

    try {
      // Upload file
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch(
        `http://localhost:8000/api/evidence/upload/${applicationId}?evidence_type=${evidenceType}`,
        {
          method: 'POST',
          body: formData,
        }
      );

      if (!response.ok) {
        throw new Error('Upload failed');
      }

      const result = await response.json();
      setUploadedFile({
        name: file.name,
        size: file.size,
        uploadedAt: new Date().toLocaleString(),
      });

      if (onUploadSuccess) {
        onUploadSuccess(result);
      }
    } catch (err) {
      const errorMsg = err.message || 'Upload failed';
      setError(errorMsg);
      if (onUploadError) {
        onUploadError(errorMsg);
      }
    } finally {
      setUploading(false);
    }
  };

  const handleRemove = async () => {
    try {
      const response = await fetch(
        `http://localhost:8000/api/evidence/${applicationId}/${evidenceType}`,
        { method: 'DELETE' }
      );

      if (response.ok) {
        setUploadedFile(null);
        setError(null);
      }
    } catch (err) {
      setError('Failed to remove file');
    }
  };

  return (
    <div className="file-upload-container">
      <div className="file-upload-wrapper">
        <label className="file-upload-label">
          <input
            type="file"
            onChange={handleFileChange}
            disabled={uploading}
            accept=".pdf,.jpg,.jpeg,.png"
            style={{ display: 'none' }}
          />
          <div className="file-upload-input">
            <div className="file-upload-icon">📎</div>
            <div className="file-upload-text">
              {uploading ? 'Uploading...' : 'Click to upload or drag file'}
            </div>
            <div className="file-upload-hint">{label}</div>
          </div>
        </label>
      </div>

      {uploadedFile && (
        <div className="file-uploaded-success">
          <div className="file-info">
            <span className="file-icon">✅</span>
            <div className="file-details">
              <div className="file-name">{uploadedFile.name}</div>
              <div className="file-size">{(uploadedFile.size / 1024).toFixed(2)} KB</div>
            </div>
          </div>
          <button
            className="file-remove-btn"
            onClick={handleRemove}
            type="button"
          >
            Remove
          </button>
        </div>
      )}

      {error && (
        <div className="file-upload-error">
          <span className="error-icon">⚠️</span>
          {error}
        </div>
      )}
    </div>
  );
}

export default FileUpload;
