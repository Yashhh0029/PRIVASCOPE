import React, { useState } from 'react';
import { Eye, FileText, Image as ImageIcon, ZoomIn, ZoomOut, AlertCircle } from 'lucide-react';
import { DetectedEntity } from '../types';
import { API_BASE } from '../services/api';

interface DocumentViewerProps {
  documentId?: string;
  fileType?: string;
  filename?: string;
  entities: DetectedEntity[];
  selectedEntityId?: string | null;
}

export const DocumentViewer: React.FC<DocumentViewerProps> = ({
  documentId,
  fileType,
  filename,
  entities,
  selectedEntityId,
}) => {
  const [zoom, setZoom] = useState<number>(100);
  const [currentPage, setCurrentPage] = useState<number>(1);
  const [previewError, setPreviewError] = useState<boolean>(false);

  const isVisualFormat = fileType && ['pdf', 'png', 'jpg', 'jpeg'].includes(fileType.toLowerCase());

  const token = localStorage.getItem('privascope_token');
  const previewUrl = documentId
    ? `${API_BASE}/documents/${documentId}/preview?page=${currentPage}&token=${token}`
    : null;

  return (
    <div className="border border-priva-border rounded-xl bg-priva-card overflow-hidden flex flex-col h-[520px]">
      {/* Top Bar Controls */}
      <div className="px-4 py-2.5 bg-priva-bg/80 border-b border-priva-border flex items-center justify-between text-xs">
        <div className="flex items-center gap-2 text-priva-muted">
          {isVisualFormat ? <ImageIcon className="w-4 h-4 text-priva-primary" /> : <FileText className="w-4 h-4 text-priva-primary" />}
          <span className="font-mono text-white truncate max-w-xs">{filename || "Document Preview"}</span>
          <span className="text-[10px] uppercase px-1.5 py-0.5 rounded bg-priva-border text-priva-muted">
            {fileType || "TXT"}
          </span>
        </div>

        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1 bg-priva-card border border-priva-border rounded px-2 py-0.5">
            <button
              onClick={() => setZoom(Math.max(60, zoom - 15))}
              className="hover:text-white text-priva-muted p-0.5"
              title="Zoom out"
            >
              <ZoomOut className="w-3.5 h-3.5" />
            </button>
            <span className="text-[11px] font-mono w-10 text-center">{zoom}%</span>
            <button
              onClick={() => setZoom(Math.min(160, zoom + 15))}
              className="hover:text-white text-priva-muted p-0.5"
              title="Zoom in"
            >
              <ZoomIn className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </div>

      {/* Main Viewport */}
      <div className="flex-1 overflow-auto bg-slate-950/80 p-4 flex items-center justify-center relative">
        {isVisualFormat && previewUrl && !previewError ? (
          <div
            className="relative transition-transform duration-200 origin-center max-w-full"
            style={{ transform: `scale(${zoom / 100})` }}
          >
            <img
              src={previewUrl}
              alt="Document Scan Preview"
              onError={() => setPreviewError(true)}
              className="rounded shadow-xl max-h-[440px] w-auto border border-priva-border object-contain"
            />

            {/* Bounding Box Heatmap Overlays */}
            {entities.map((e) => {
              if (!e.location_data || !e.location_data.bbox) return null;
              const [x, y, w, h] = e.location_data.bbox;
              const isSelected = selectedEntityId === e.id;
              
              const borderCol = e.risk_level === 'CRITICAL' ? 'border-red-500 bg-red-500/20'
                : e.risk_level === 'HIGH' ? 'border-orange-500 bg-orange-500/20'
                : 'border-amber-500 bg-amber-500/20';

              return (
                <div
                  key={e.id}
                  style={{
                    position: 'absolute',
                    left: `${x}px`,
                    top: `${y}px`,
                    width: `${Math.max(20, w)}px`,
                    height: `${Math.max(14, h)}px`,
                  }}
                  className={`border-2 rounded-sm transition-all pointer-events-none ${borderCol} ${
                    isSelected ? 'ring-2 ring-blue-400 ring-offset-1 ring-offset-black' : ''
                  }`}
                  title={`${e.entity_type}: ${e.masked_preview}`}
                />
              );
            })}
          </div>
        ) : (
          <div className="text-center p-8 space-y-3 max-w-md">
            <div className="w-12 h-12 rounded-full bg-priva-primary/10 border border-priva-primary/30 flex items-center justify-center text-priva-primary mx-auto">
              <FileText className="w-6 h-6" />
            </div>
            <h4 className="text-sm font-semibold text-white">Structured / Tabular Document</h4>
            <p className="text-xs text-priva-muted leading-relaxed">
              Detected {entities.length} sensitive Indian personal records. Review target cells and coordinates in the Findings Table below or apply masking to download the sanitized copy.
            </p>
          </div>
        )}
      </div>
    </div>
  );
};
