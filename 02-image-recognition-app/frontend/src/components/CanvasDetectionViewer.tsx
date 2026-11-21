'use client';

import React, { useRef, useEffect, useState, useMemo } from 'react';
import { DetectedObject } from '@/lib/types';
import { Download, Sliders, Eye, EyeOff, Layers } from 'lucide-react';

interface CanvasDetectionViewerProps {
  imageUrl: string;
  originalWidth: number;
  originalHeight: number;
  detections: DetectedObject[];
  filename?: string;
}

// Deterministic bright colors for object classes
const COLOR_PALETTE = [
  '#ef4444', '#f97316', '#f59e0b', '#10b981', '#06b6d4',
  '#3b82f6', '#6366f1', '#8b5cf6', '#ec4899', '#14b8a6'
];

function getClassColor(label: string): string {
  let hash = 0;
  for (let i = 0; i < label.length; i++) {
    hash = label.charCodeAt(i) + ((hash << 5) - hash);
  }
  const index = Math.abs(hash) % COLOR_PALETTE.length;
  return COLOR_PALETTE[index];
}

export default function CanvasDetectionViewer({
  imageUrl,
  originalWidth,
  originalHeight,
  detections,
  filename = 'detections'
}: CanvasDetectionViewerProps) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const containerRef = useRef<HTMLDivElement | null>(null);
  const [scoreThreshold, setScoreThreshold] = useState<number>(0.25);
  const [selectedClassFilter, setSelectedClassFilter] = useState<Record<string, boolean>>({});
  const [hoveredBox, setHoveredBox] = useState<DetectedObject | null>(null);
  const [hoverCoords, setHoverCoords] = useState<{ x: number; y: number } | null>(null);
  const [imageLoaded, setImageLoaded] = useState(false);
  const imageElementRef = useRef<HTMLImageElement | null>(null);

  // Available unique classes
  const uniqueClasses = useMemo(() => {
    return Array.from(new Set(detections.map(d => d.label)));
  }, [detections]);

  // Filtered detections based on threshold and class toggles
  const activeDetections = useMemo(() => {
    return detections.filter(d => {
      if (d.score < scoreThreshold) return false;
      if (selectedClassFilter[d.label] === false) return false;
      return true;
    });
  }, [detections, scoreThreshold, selectedClassFilter]);

  // Load image
  useEffect(() => {
    const img = new Image();
    img.crossOrigin = 'anonymous';
    img.src = imageUrl;
    img.onload = () => {
      imageElementRef.current = img;
      setImageLoaded(true);
    };
  }, [imageUrl]);

  // Render canvas
  useEffect(() => {
    if (!imageLoaded || !imageElementRef.current || !canvasRef.current) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const img = imageElementRef.current;
    canvas.width = img.naturalWidth || originalWidth;
    canvas.height = img.naturalHeight || originalHeight;

    // Draw background image
    ctx.drawImage(img, 0, 0, canvas.width, canvas.height);

    // Draw bounding boxes
    activeDetections.forEach((det) => {
      const isHovered = hoveredBox === det;
      const [x1, y1, x2, y2] = det.bbox_pixels;
      const w = x2 - x1;
      const h = y2 - y1;
      const color = getClassColor(det.label);

      ctx.save();
      ctx.lineWidth = isHovered ? 4 : 2.5;
      ctx.strokeStyle = color;
      ctx.fillStyle = color;

      // Draw box rectangle
      ctx.strokeRect(x1, y1, w, h);

      // Semi-transparent overlay on hover
      if (isHovered) {
        ctx.fillStyle = `${color}33`; // 20% alpha
        ctx.fillRect(x1, y1, w, h);
      }

      // Draw label pill tag
      const labelText = `${det.label} ${(det.score * 100).toFixed(1)}%`;
      ctx.font = 'bold 12px Inter, sans-serif';
      const textWidth = ctx.measureText(labelText).width;
      const textHeight = 18;

      ctx.fillStyle = color;
      ctx.fillRect(x1, Math.max(0, y1 - textHeight), textWidth + 10, textHeight);

      ctx.fillStyle = '#ffffff';
      ctx.fillText(labelText, x1 + 5, Math.max(13, y1 - 4));

      ctx.restore();
    });
  }, [imageLoaded, activeDetections, hoveredBox, originalWidth, originalHeight]);

  // Mouse move handler for interactive bounding box hover tooltips
  const handleMouseMove = (e: React.MouseEvent<HTMLCanvasElement>) => {
    if (!canvasRef.current) return;
    const canvas = canvasRef.current;
    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;

    const mouseX = (e.clientX - rect.left) * scaleX;
    const mouseY = (e.clientY - rect.top) * scaleY;

    // Find any box containing mouse coords (search in reverse to pick top layered box)
    let matched: DetectedObject | null = null;
    for (let i = activeDetections.length - 1; i >= 0; i--) {
      const d = activeDetections[i];
      const [x1, y1, x2, y2] = d.bbox_pixels;
      if (mouseX >= x1 && mouseX <= x2 && mouseY >= y1 && mouseY <= y2) {
        matched = d;
        break;
      }
    }

    setHoveredBox(matched);
    if (matched) {
      setHoverCoords({ x: e.clientX, y: e.clientY });
    } else {
      setHoverCoords(null);
    }
  };

  const handleMouseLeave = () => {
    setHoveredBox(null);
    setHoverCoords(null);
  };

  // Toggle class visibility
  const toggleClass = (label: string) => {
    setSelectedClassFilter(prev => ({
      ...prev,
      [label]: prev[label] === false ? true : false
    }));
  };

  // Export COCO format JSON
  const exportCOCOJson = () => {
    const cocoData = {
      info: {
        description: "Exported from Cognix CV Workbench",
        year: 2026,
        date_created: new Date().toISOString()
      },
      images: [
        {
          id: 1,
          width: originalWidth,
          height: originalHeight,
          file_name: filename
        }
      ],
      annotations: activeDetections.map((d, index) => {
        const [x1, y1, x2, y2] = d.bbox_pixels;
        return {
          id: index + 1,
          image_id: 1,
          category_id: d.class_id,
          category_name: d.label,
          bbox: [x1, y1, x2 - x1, y2 - y1],
          score: d.score,
          area: (x2 - x1) * (y2 - y1)
        };
      })
    };

    const blob = new Blob([JSON.stringify(cocoData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${filename}_coco_annotations.json`;
    link.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="flex flex-col space-y-4">
      {/* Control Toolbar */}
      <div className="bg-surface border border-surfaceBorder rounded-xl p-4 flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2 text-sm text-slate-300">
            <Sliders className="w-4 h-4 text-primary" />
            <span>Score Threshold:</span>
            <span className="font-semibold text-white font-mono">{(scoreThreshold * 100).toFixed(0)}%</span>
          </div>
          <input
            type="range"
            min="0.05"
            max="0.95"
            step="0.05"
            value={scoreThreshold}
            onChange={(e) => setScoreThreshold(parseFloat(e.target.value))}
            className="w-36 h-1.5 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-primary"
          />
        </div>

        <div className="flex items-center space-x-3 text-sm">
          <span className="text-slate-400">
            Detected: <strong className="text-white">{activeDetections.length}</strong> / {detections.length}
          </span>
          <button
            onClick={exportCOCOJson}
            className="flex items-center space-x-1.5 px-3 py-1.5 text-xs font-medium rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Export COCO</span>
          </button>
        </div>
      </div>

      {/* Class toggles bar */}
      {uniqueClasses.length > 0 && (
        <div className="flex flex-wrap items-center gap-2 text-xs">
          <span className="text-slate-400 flex items-center space-x-1 mr-1">
            <Layers className="w-3.5 h-3.5" />
            <span>Filter Classes:</span>
          </span>
          {uniqueClasses.map((cls) => {
            const isVisible = selectedClassFilter[cls] !== false;
            const color = getClassColor(cls);
            return (
              <button
                key={cls}
                onClick={() => toggleClass(cls)}
                className={`flex items-center space-x-1.5 px-2.5 py-1 rounded-full border transition ${
                  isVisible
                    ? 'bg-slate-800 text-white border-slate-600'
                    : 'bg-slate-900/60 text-slate-500 border-slate-800'
                }`}
              >
                <span
                  className="w-2.5 h-2.5 rounded-full"
                  style={{ backgroundColor: isVisible ? color : '#64748b' }}
                />
                <span>{cls}</span>
                {isVisible ? <Eye className="w-3 h-3 text-slate-400" /> : <EyeOff className="w-3 h-3" />}
              </button>
            );
          })}
        </div>
      )}

      {/* Canvas Viewport */}
      <div
        ref={containerRef}
        className="relative border border-surfaceBorder rounded-xl overflow-hidden bg-black/40 flex items-center justify-center p-2"
      >
        <canvas
          ref={canvasRef}
          onMouseMove={handleMouseMove}
          onMouseLeave={handleMouseLeave}
          className="max-w-full max-h-[600px] object-contain rounded cursor-crosshair shadow-lg"
        />

        {/* Hover Tooltip */}
        {hoveredBox && hoverCoords && (
          <div
            className="fixed z-50 pointer-events-none bg-slate-900/95 border border-primary/50 text-white text-xs p-2.5 rounded-lg shadow-xl backdrop-blur-md space-y-1 transform -translate-x-1/2 -translate-y-full mb-2"
            style={{ left: hoverCoords.x, top: hoverCoords.y - 12 }}
          >
            <div className="flex items-center justify-between space-x-3">
              <span className="font-bold text-primary">{hoveredBox.label}</span>
              <span className="text-accent font-mono font-semibold">{(hoveredBox.score * 100).toFixed(1)}%</span>
            </div>
            <div className="text-slate-400 font-mono text-[10px]">
              Box: [{hoveredBox.bbox_pixels.join(', ')}] px
            </div>
            <div className="text-slate-400 font-mono text-[10px]">
              Norm: [{hoveredBox.bbox_normalized.join(', ')}]
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
