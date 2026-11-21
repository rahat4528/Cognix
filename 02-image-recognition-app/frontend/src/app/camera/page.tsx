'use client';

import React, { useRef, useState, useEffect } from 'react';
import { Video, VideoOff, ShieldAlert, Sliders, Activity } from 'lucide-react';
import { processLiveCameraFrame } from '@/lib/api';

export default function CameraStudio() {
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const [cameraActive, setCameraActive] = useState<boolean>(false);
  const [scoreThreshold, setScoreThreshold] = useState<number>(0.35);
  const [latency, setLatency] = useState<number>(0);
  const [fps, setFps] = useState<number>(0);
  const [detectedCount, setDetectedCount] = useState<number>(0);
  const [classCounts, setClassCounts] = useState<Record<string, number>>({});
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const activeStreamRef = useRef<MediaStream | null>(null);
  const loopTimeoutRef = useRef<any>(null);

  const startCamera = async () => {
    setErrorMessage(null);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { width: { ideal: 640 }, height: { ideal: 480 }, frameRate: { ideal: 15 } }
      });
      activeStreamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        videoRef.current.play();
      }
      setCameraActive(true);
    } catch (err: any) {
      setErrorMessage(err.message || 'Failed to access camera.');
      setCameraActive(false);
    }
  };

  const stopCamera = () => {
    if (activeStreamRef.current) {
      activeStreamRef.current.getTracks().forEach((t) => t.stop());
      activeStreamRef.current = null;
    }
    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }
    if (loopTimeoutRef.current) {
      clearTimeout(loopTimeoutRef.current);
    }
    setCameraActive(false);
  };

  useEffect(() => {
    return () => {
      stopCamera();
    };
  }, []);

  // Frame processing loop throttled to ~4 FPS (every 250ms) to ensure low latency and avoid server overload
  useEffect(() => {
    if (!cameraActive) return;

    let isProcessing = false;
    let lastTime = performance.now();

    const processLoop = async () => {
      if (!cameraActive || !videoRef.current || !canvasRef.current) return;

      const video = videoRef.current;
      const canvas = canvasRef.current;
      if (video.videoWidth === 0 || video.videoHeight === 0) {
        loopTimeoutRef.current = setTimeout(processLoop, 200);
        return;
      }

      if (!isProcessing) {
        isProcessing = true;
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        const ctx = canvas.getContext('2d');
        if (ctx) {
          ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

          canvas.toBlob(async (blob) => {
            if (blob) {
              try {
                const t0 = performance.now();
                const res = await processLiveCameraFrame(blob, scoreThreshold);
                const totalElapsed = performance.now() - t0;
                setLatency(Math.round(res.inference_latency_ms || totalElapsed));
                setDetectedCount(res.total_objects_count || 0);
                setClassCounts(res.class_counts || {});

                // Draw overlay boxes
                ctx.lineWidth = 3;
                ctx.font = 'bold 13px Inter, sans-serif';
                res.detected_objects.forEach((det: any) => {
                  const [x1, y1, x2, y2] = det.bbox_pixels;
                  ctx.strokeStyle = '#10b981';
                  ctx.fillStyle = '#10b981';
                  ctx.strokeRect(x1, y1, x2 - x1, y2 - y1);

                  const tag = `${det.label} ${(det.score * 100).toFixed(0)}%`;
                  ctx.fillRect(x1, Math.max(0, y1 - 18), ctx.measureText(tag).width + 8, 18);
                  ctx.fillStyle = '#ffffff';
                  ctx.fillText(tag, x1 + 4, Math.max(13, y1 - 4));
                });

                const now = performance.now();
                setFps(Math.round(1000 / (now - lastTime)));
                lastTime = now;
              } catch (e) {
                // Ignore transient frame drop
              }
            }
            isProcessing = false;
          }, 'image/jpeg', 0.7);
        }
      }

      loopTimeoutRef.current = setTimeout(processLoop, 220);
    };

    loopTimeoutRef.current = setTimeout(processLoop, 250);

    return () => {
      if (loopTimeoutRef.current) clearTimeout(loopTimeoutRef.current);
    };
  }, [cameraActive, scoreThreshold]);

  return (
    <div className="space-y-8">
      {/* Title & Privacy Badge */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-white tracking-tight">Live Edge Camera Stream</h2>
          <p className="text-sm text-slate-400 mt-1">
            Real-time deep learning bounding box localization with client-side frame rate throttling.
          </p>
        </div>

        {/* Persistent pulsating camera privacy indicator */}
        {cameraActive && (
          <div className="flex items-center space-x-2 px-3.5 py-1.5 rounded-full bg-red-500/20 text-red-400 border border-red-500/40 text-xs font-bold animate-pulse">
            <span className="w-2.5 h-2.5 rounded-full bg-red-500" />
            <span>CAMERA ACTIVE</span>
          </div>
        )}
      </div>

      {/* Control bar */}
      <div className="bg-surface border border-surfaceBorder rounded-xl p-4 flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center space-x-3">
          {!cameraActive ? (
            <button
              onClick={startCamera}
              className="flex items-center space-x-1.5 px-4 py-2 bg-primary hover:bg-primaryHover text-white rounded-lg text-xs font-semibold transition shadow-md shadow-primary/20"
            >
              <Video className="w-4 h-4" />
              <span>Start Camera</span>
            </button>
          ) : (
            <button
              onClick={stopCamera}
              className="flex items-center space-x-1.5 px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg text-xs font-semibold transition shadow-md shadow-red-600/20"
            >
              <VideoOff className="w-4 h-4" />
              <span>Stop Camera</span>
            </button>
          )}

          <div className="flex items-center space-x-3 text-xs text-slate-300 border-l border-surfaceBorder pl-4">
            <Sliders className="w-3.5 h-3.5 text-primary" />
            <span>Confidence Threshold:</span>
            <input
              type="range"
              min="0.15"
              max="0.85"
              step="0.05"
              value={scoreThreshold}
              onChange={(e) => setScoreThreshold(parseFloat(e.target.value))}
              className="w-24 h-1 bg-slate-700 rounded appearance-none cursor-pointer accent-primary"
            />
            <span className="font-mono text-white font-semibold">{(scoreThreshold * 100).toFixed(0)}%</span>
          </div>
        </div>

        {/* Live Metrics */}
        {cameraActive && (
          <div className="flex items-center space-x-4 text-xs font-mono text-slate-300">
            <span className="flex items-center space-x-1">
              <Activity className="w-3.5 h-3.5 text-accent" />
              <span>Latency:</span>
              <strong className="text-white">{latency} ms</strong>
            </span>
            <span>
              FPS: <strong className="text-white">{fps}</strong>
            </span>
            <span>
              Objects: <strong className="text-accent">{detectedCount}</strong>
            </span>
          </div>
        )}
      </div>

      {errorMessage && (
        <div className="bg-red-500/10 border border-red-500/30 text-red-400 text-xs p-3 rounded-lg">
          {errorMessage}
        </div>
      )}

      {/* Stream Viewport */}
      <div className="relative border border-surfaceBorder rounded-xl overflow-hidden bg-black/60 flex items-center justify-center min-h-[480px]">
        {/* Hidden source video for capture */}
        <video ref={videoRef} playsInline muted className="hidden" />

        {/* Display Canvas with overlaid bounding boxes */}
        <canvas
          ref={canvasRef}
          className={`max-w-full max-h-[540px] rounded object-contain ${
            cameraActive ? 'block' : 'hidden'
          }`}
        />

        {!cameraActive && (
          <div className="text-center p-12 space-y-3">
            <div className="w-16 h-16 rounded-full bg-slate-800/80 text-slate-400 flex items-center justify-center mx-auto">
              <Video className="w-8 h-8" />
            </div>
            <div>
              <p className="text-sm font-semibold text-slate-200">Camera Feed Idle</p>
              <p className="text-xs text-slate-500 mt-1 max-w-sm">
                Click "Start Camera" to grant browser webcam access. Frame capture is throttled and privacy protected.
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Detected objects breakdown */}
      {cameraActive && Object.keys(classCounts).length > 0 && (
        <div className="bg-surface border border-surfaceBorder rounded-xl p-4 flex flex-wrap items-center gap-2 text-xs">
          <span className="text-slate-400 font-semibold mr-2">Live Class Counts:</span>
          {Object.entries(classCounts).map(([label, count]) => (
            <span
              key={label}
              className="px-2.5 py-1 rounded-full bg-slate-800 text-slate-200 border border-slate-700 font-medium"
            >
              {label}: <strong className="text-accent">{count}</strong>
            </span>
          ))}
        </div>
      )}
    </div>
  );
}
