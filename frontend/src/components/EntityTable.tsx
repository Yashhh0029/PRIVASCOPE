import React, { useState } from 'react';
import { ShieldAlert, Info, Filter, CheckCircle2 } from 'lucide-react';
import { DetectedEntity } from '../types';

interface EntityTableProps {
  entities: DetectedEntity[];
  onSelectEntity?: (entity: DetectedEntity) => void;
  selectedEntityId?: string | null;
}

export const EntityTable: React.FC<EntityTableProps> = ({ entities, onSelectEntity, selectedEntityId }) => {
  const [filterType, setFilterType] = useState<string>('ALL');
  const [activeSignalEntity, setActiveSignalEntity] = useState<DetectedEntity | null>(null);

  const filterOptions = ['ALL', 'AADHAAR', 'PAN', 'BANK_ACCOUNT', 'PHONE', 'EMAIL', 'UPI', 'IFSC', 'STUDENT_ID'];

  const filteredEntities = filterType === 'ALL'
    ? entities
    : entities.filter(e => e.entity_type === filterType);

  const getRiskBadgeColor = (risk: string) => {
    switch (risk) {
      case 'CRITICAL':
        return 'text-priva-critical bg-priva-critical/10 border-priva-critical/30';
      case 'HIGH':
        return 'text-priva-high bg-priva-high/10 border-priva-high/30';
      case 'MEDIUM':
        return 'text-priva-medium bg-priva-medium/10 border-priva-medium/30';
      default:
        return 'text-priva-low bg-priva-low/10 border-priva-low/30';
    }
  };

  return (
    <div className="space-y-4">
      {/* Category Filter Bar */}
      <div className="flex items-center justify-between flex-wrap gap-2">
        <div className="flex items-center gap-1.5 overflow-x-auto pb-1 max-w-full">
          <Filter className="w-3.5 h-3.5 text-priva-muted mr-1 shrink-0" />
          {filterOptions.map((opt) => (
            <button
              key={opt}
              onClick={() => setFilterType(opt)}
              className={`px-2.5 py-1 rounded text-xs font-mono transition-colors shrink-0 ${
                filterType === opt
                  ? 'bg-priva-primary text-white font-medium'
                  : 'bg-priva-card hover:bg-priva-cardHover text-priva-muted border border-priva-border'
              }`}
            >
              {opt}
            </button>
          ))}
        </div>
        <span className="text-xs font-mono text-priva-muted">
          Showing {filteredEntities.length} of {entities.length} items
        </span>
      </div>

      {/* Entities Table */}
      <div className="border border-priva-border rounded-xl bg-priva-card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full min-w-[550px] text-left text-sm">
            <thead className="bg-priva-bg/60 border-b border-priva-border text-[11px] font-mono text-priva-muted uppercase">
              <tr>
                <th className="py-3 px-4">Entity Type</th>
                <th className="py-3 px-4">Masked Preview</th>
                <th className="py-3 px-4">Confidence</th>
                <th className="py-3 px-4">Risk Level</th>
                <th className="py-3 px-4">Location</th>
                <th className="py-3 px-4 text-right">Signals</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-priva-border/60">
              {filteredEntities.length === 0 ? (
                <tr>
                  <td colSpan={6} className="py-8 text-center text-priva-muted">
                    No matching sensitive entities in this category.
                  </td>
                </tr>
              ) : (
                filteredEntities.map((entity) => {
                  const isSelected = selectedEntityId === entity.id;
                  return (
                    <tr
                      key={entity.id}
                      onClick={() => onSelectEntity && onSelectEntity(entity)}
                      className={`hover:bg-priva-bg/50 transition-colors cursor-pointer ${
                        isSelected ? 'bg-priva-primary/10 border-l-2 border-priva-primary' : ''
                      }`}
                    >
                      <td className="py-3 px-4 font-mono font-semibold text-white">
                        <span className="px-2 py-0.5 rounded text-xs bg-slate-800 border border-slate-700">
                          {entity.entity_type}
                        </span>
                      </td>
                      <td className="py-3 px-4 font-mono text-slate-200">
                        {entity.masked_preview}
                      </td>
                      <td className="py-3 px-4 font-mono">
                        <span className="text-priva-accent font-medium">
                          {Math.round(entity.confidence * 100)}%
                        </span>
                      </td>
                      <td className="py-3 px-4">
                        <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold uppercase border ${getRiskBadgeColor(entity.risk_level)}`}>
                          {entity.risk_level}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-xs text-priva-muted font-mono">
                        {entity.sheet_name
                          ? `${entity.sheet_name}`
                          : `Page ${entity.page_number}`}
                        {entity.location_data?.col_name && ` (${entity.location_data.col_name})`}
                      </td>
                      <td className="py-3 px-4 text-right">
                        <button
                          type="button"
                          onClick={(e) => {
                            e.stopPropagation();
                            setActiveSignalEntity(entity);
                          }}
                          className="p-1 rounded hover:bg-priva-bg text-priva-muted hover:text-white transition-colors"
                          title="View Detection Signals"
                        >
                          <Info className="w-4 h-4 text-priva-accent" />
                        </button>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Detection Signals Modal / Overlay */}
      {activeSignalEntity && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-3 sm:p-4">
          <div className="bg-priva-card border border-priva-border rounded-xl max-w-md w-full p-4 sm:p-6 space-y-4 shadow-2xl max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between border-b border-priva-border pb-3">
              <div className="flex items-center gap-2">
                <ShieldAlert className="w-5 h-5 text-priva-primary" />
                <h3 className="font-semibold text-white">Detection Evidence Signals</h3>
              </div>
              <button
                onClick={() => setActiveSignalEntity(null)}
                className="text-priva-muted hover:text-white text-sm"
              >
                ✕
              </button>
            </div>

            <div className="space-y-3">
              <div>
                <p className="text-xs text-priva-muted">Entity / Identifier</p>
                <p className="font-mono text-white text-sm font-semibold">
                  {activeSignalEntity.entity_type} ({activeSignalEntity.masked_preview})
                </p>
              </div>

              <div>
                <p className="text-xs text-priva-muted mb-1.5">Verification Signals Passed</p>
                <div className="space-y-1.5">
                  {activeSignalEntity.detection_source?.map((src, i) => (
                    <div key={i} className="flex items-center gap-2 text-xs text-slate-200">
                      <CheckCircle2 className="w-4 h-4 text-priva-low shrink-0" />
                      <span className="font-mono capitalize">{src} analysis passed</span>
                    </div>
                  ))}
                  {activeSignalEntity.location_data?.col_name && (
                    <div className="flex items-center gap-2 text-xs text-slate-200">
                      <CheckCircle2 className="w-4 h-4 text-priva-low shrink-0" />
                      <span className="font-mono">Header semantic match: "{activeSignalEntity.location_data.col_name}"</span>
                    </div>
                  )}
                </div>
              </div>

              <div className="p-3 rounded bg-priva-bg border border-priva-border/80 text-xs text-priva-muted">
                Confidence: <strong className="text-white">{Math.round(activeSignalEntity.confidence * 100)}%</strong> derived from pattern structure, algorithmic verification, and document context.
              </div>
            </div>

            <div className="pt-2 text-right">
              <button
                onClick={() => setActiveSignalEntity(null)}
                className="px-4 py-1.5 rounded-lg bg-priva-primary hover:bg-priva-primaryHover text-white text-xs font-medium"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
