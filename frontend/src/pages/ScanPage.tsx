import React, { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  UploadCloud,
  FileText,
  AlertCircle,
  FileSpreadsheet,
  FileCode,
  Image as ImageIcon,
  CheckCircle2,
  Cpu
} from 'lucide-react';
import { api } from '../services/api';
import { ScanningProgress } from '../components/ScanningProgress';
import { ScanStage } from '../types';

export const ScanPage: React.FC = () => {
  const navigate = useNavigate();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [activeTab, setActiveTab] = useState<'upload' | 'paste'>('upload');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [dragActive, setDragActive] = useState<boolean>(false);
  const [pastedText, setPastedText] = useState<string>('');

  const [isScanning, setIsScanning] = useState<boolean>(false);
  const [sharingPurpose, setSharingPurpose] = useState<string>('General Sharing');
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [stages, setStages] = useState<ScanStage[]>([]);
  const [ocrStatus, setOcrStatus] = useState<string>('');

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setSelectedFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
    }
  };

  const startScan = async () => {
    setErrorMsg(null);
    setIsScanning(true);

    // Initial default pending stages for visual start
    setStages([
      { name: 'validating', label: 'Validating file integrity', status: 'processing' },
      { name: 'extracting', label: 'Extracting document content', status: 'pending' },
      { name: 'ocr', label: 'OCR & optical analysis', status: 'pending' },
      { name: 'detecting', label: 'Detecting sensitive Indian PII', status: 'pending' },
      { name: 'context', label: 'Analyzing semantic & structural context', status: 'pending' },
      { name: 'risk', label: 'Evaluating multi-factor privacy risk', status: 'pending' },
      { name: 'completed', label: 'Scan report generated', status: 'pending' },
    ]);

    try {
      if (activeTab === 'upload') {
        if (!selectedFile) {
          setErrorMsg("Please select a file to scan.");
          setIsScanning(false);
          return;
        }

        // 1. Upload to backend
        const doc = await api.uploadDocument(selectedFile);

        // 2. Trigger scan
        const scan = await api.scanDocument(doc.id, sharingPurpose);
        setStages(scan.stages);
        setOcrStatus(scan.ocr_status);

        // Navigate to result
        setTimeout(() => {
          navigate(`/scan/${scan.id}`);
        }, 600);
      } else {
        if (!pastedText.trim()) {
          setErrorMsg("Please paste or type text to scan.");
          setIsScanning(false);
          return;
        }

        const scan = await api.scanText(pastedText, sharingPurpose);
        setStages(scan.stages);
        setTimeout(() => {
          navigate(`/scan/${scan.id}`);
        }, 600);
      }
    } catch (err: any) {
      setErrorMsg(err.response?.data?.detail || "Scan pipeline failed to complete.");
      setIsScanning(false);
    }
  };

  return (
    <div className="flex-1 px-3.5 py-6 sm:p-8 max-w-4xl mx-auto w-full space-y-6 sm:space-y-8">
      <div>
        <h1 className="text-xl sm:text-2xl font-bold text-white tracking-tight">Initiate Privacy Scan</h1>
        <p className="text-xs text-priva-muted">
          Upload documents or paste text to detect Indian personal identifiers and assess exposure.
        </p>
      </div>

      {isScanning ? (
        <ScanningProgress
          stages={stages}
          filename={selectedFile?.name || "Pasted Text Analysis"}
          ocrStatus={ocrStatus}
        />
      ) : (
        <div className="space-y-6">
          {/* Sharing Purpose Context Selector */}
          <div className="p-4 rounded-xl bg-priva-card/60 border border-priva-border space-y-2">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
              <div>
                <label className="text-xs font-semibold text-white">Intended Document Sharing Purpose</label>
                <p className="text-[11px] text-priva-muted">
                  PRIVASCOPE adapts its KEEP vs PROTECT policy based on legitimate business context.
                </p>
              </div>
              <select
                value={sharingPurpose}
                onChange={(e) => setSharingPurpose(e.target.value)}
                className="w-full sm:w-auto bg-priva-bg border border-priva-border text-xs text-priva-primary font-medium rounded-lg px-3 py-2 focus:outline-none focus:border-priva-primary shrink-0"
              >
                <option value="General Sharing">General Sharing (Default: Protect All PII)</option>
                <option value="Job Application">Job Application (Keep Phone/Email/ID, Protect Aadhaar/Bank)</option>
                <option value="College Admission">College Admission (Keep Student ID/Email, Protect Financial)</option>
                <option value="Scholarship">Scholarship (Keep Student ID, Protect Financial/Aadhaar)</option>
                <option value="Bank Verification">Bank Verification (Keep KYC coordinates, Protect irrelevant PII)</option>
                <option value="Medical Document">Medical Document (Keep Emergency Phone, Protect Aadhaar)</option>
                <option value="Government Form">Government Form (Keep Official IDs, Protect Private Coordinates)</option>
                <option value="Custom">Custom / Strict Protection</option>
              </select>
            </div>
          </div>

          {/* Tab selector */}
          <div className="flex items-center gap-2 border-b border-priva-border pb-3">
            <button
              onClick={() => setActiveTab('upload')}
              className={`px-4 py-2 rounded-lg text-xs font-mono font-medium transition-colors ${
                activeTab === 'upload'
                  ? 'bg-priva-primary text-white'
                  : 'bg-priva-card text-priva-muted hover:text-white border border-priva-border'
              }`}
            >
              Upload Document
            </button>
            <button
              onClick={() => setActiveTab('paste')}
              className={`px-4 py-2 rounded-lg text-xs font-mono font-medium transition-colors ${
                activeTab === 'paste'
                  ? 'bg-priva-primary text-white'
                  : 'bg-priva-card text-priva-muted hover:text-white border border-priva-border'
              }`}
            >
              Paste Raw Text
            </button>
          </div>

          {errorMsg && (
            <div className="p-3 rounded-lg border border-priva-critical/30 bg-priva-critical/10 text-priva-critical text-xs flex items-center gap-2">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{errorMsg}</span>
            </div>
          )}

          {activeTab === 'upload' ? (
            <div className="space-y-4">
              <div
                onDragEnter={handleDrag}
                onDragOver={handleDrag}
                onDragLeave={handleDrag}
                onDrop={handleDrop}
                onClick={() => fileInputRef.current?.click()}
                className={`border-2 border-dashed rounded-2xl p-6 sm:p-10 text-center cursor-pointer transition-all ${
                  dragActive
                    ? 'border-priva-primary bg-priva-primary/10'
                    : 'border-priva-border bg-priva-card/50 hover:bg-priva-card hover:border-priva-borderLight'
                }`}
              >
                <input
                  ref={fileInputRef}
                  type="file"
                  onChange={handleFileChange}
                  accept=".pdf,.docx,.xlsx,.csv,.txt,.png,.jpg,.jpeg"
                  className="hidden"
                />

                <div className="w-14 h-14 rounded-2xl bg-priva-primary/10 border border-priva-primary/30 flex items-center justify-center text-priva-primary mx-auto mb-4">
                  <UploadCloud className="w-7 h-7" />
                </div>

                <h3 className="text-base font-semibold text-white">
                  {selectedFile ? selectedFile.name : "Drag & drop your document here"}
                </h3>
                <p className="text-xs text-priva-muted mt-1">
                  {selectedFile
                    ? `${(selectedFile.size / 1024).toFixed(1)} KB selected`
                    : "or click to browse local files"}
                </p>

                <div className="flex items-center justify-center gap-2 mt-6 flex-wrap">
                  {['PDF', 'DOCX', 'XLSX', 'CSV', 'TXT', 'PNG', 'JPG'].map((fmt) => (
                    <span
                      key={fmt}
                      className="px-2 py-0.5 rounded text-[10px] font-mono border border-priva-border bg-priva-bg text-priva-muted"
                    >
                      {fmt}
                    </span>
                  ))}
                </div>
              </div>

              <div className="flex items-center justify-between text-xs text-priva-muted">
                <span>Maximum file size: 25MB</span>
                <button
                  type="button"
                  disabled={!selectedFile}
                  onClick={startScan}
                  className="px-6 py-2.5 rounded-lg bg-priva-primary hover:bg-priva-primaryHover disabled:opacity-40 text-white font-medium text-xs shadow-md shadow-priva-primary/20 transition-all"
                >
                  Start Firewall Scan
                </button>
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              <div className="space-y-2">
                <label className="text-xs font-mono text-priva-muted">
                  Paste Document Text / Record Log
                </label>
                <textarea
                  rows={10}
                  value={pastedText}
                  onChange={(e) => setPastedText(e.target.value)}
                  placeholder="Paste student, KYC, financial, or employee text records here..."
                  className="w-full p-4 rounded-xl bg-priva-bg border border-priva-border text-sm text-white font-mono focus:outline-none focus:border-priva-primary"
                />
              </div>

              <div className="flex items-center justify-between text-xs text-priva-muted">
                <span>Length: {pastedText.length} characters</span>
                <button
                  type="button"
                  disabled={!pastedText.trim()}
                  onClick={startScan}
                  className="px-6 py-2.5 rounded-lg bg-priva-primary hover:bg-priva-primaryHover disabled:opacity-40 text-white font-medium text-xs shadow-md shadow-priva-primary/20 transition-all"
                >
                  Start Text Analysis
                </button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
