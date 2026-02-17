
import React, { useState, useRef, useEffect } from 'react';
import { Plus, X, ArrowRight, Activity, Zap, AlertCircle, Info, RefreshCw, Search, Upload, FileImage, Trash2 } from 'lucide-react';
import { DRUG_SUGGESTIONS } from '../../constants.tsx';
import { PredictionResult, RiskLevel } from '../../types.ts';

interface AnalysisViewProps {
  onAnalyze: (drugs: string[]) => void;
  loading: boolean;
  prediction: PredictionResult | null;
  onReset: () => void;
  onViewReasoning: () => void;
}

export const AnalysisView: React.FC<AnalysisViewProps> = ({ onAnalyze, loading, prediction, onReset, onViewReasoning }) => {
  const [drugs, setDrugs] = useState<string[]>(['', '']);
  const [focusedIndex, setFocusedIndex] = useState<number | null>(null);
  const [inputMode, setInputMode] = useState<'text' | 'image'>('text');
  const [selectedImages, setSelectedImages] = useState<File[]>([]);
  const [imagePreviews, setImagePreviews] = useState<string[]>([]);
  const [dragActive, setDragActive] = useState(false);
  const [imageAnalyzing, setImageAnalyzing] = useState(false);
  const suggestionRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const addField = () => setDrugs([...drugs, '']);
  const removeField = (index: number) => {
    const next = drugs.filter((_, i) => i !== index);
    setDrugs(next);
  };
  const updateField = (index: number, val: string) => {
    const next = [...drugs];
    next[index] = val;
    setDrugs(next);
  };

  const getFilteredSuggestions = (input: string) => {
    if (!input.trim()) return [];
    return DRUG_SUGGESTIONS.filter(s =>
      s.toLowerCase().includes(input.toLowerCase())
    ).slice(0, 8);
  };

  const getRiskBadge = (level: RiskLevel) => {
    switch (level) {
      case 'HIGH': return 'bg-red-500 text-white ring-4 ring-red-100 dark:ring-red-900/20';
      case 'MODERATE': return 'bg-amber-500 text-white ring-4 ring-amber-100 dark:ring-amber-900/20';
      case 'LOW': return 'bg-emerald-500 text-white ring-4 ring-emerald-100 dark:ring-emerald-900/20';
      case 'CONTRAINDICATED': return 'bg-slate-900 text-white ring-4 ring-slate-100 dark:ring-slate-800';
      default: return 'bg-slate-400 text-white';
    }
  };

  const handleImageSelect = (files: FileList | null) => {
    if (!files) return;

    const fileArray = Array.from(files);
    const currentCount = selectedImages.length;
    const newCount = currentCount + fileArray.length;

    // Validate total count
    if (newCount > 5) {
      alert(`Maximum 5 images allowed. You currently have ${currentCount} image(s). You can add ${5 - currentCount} more.`);
      return;
    }

    // Validate each file
    const validFiles: File[] = [];
    for (const file of fileArray) {
      if (!file.type.match(/^image\/(jpeg|jpg|png)$/)) {
        alert(`${file.name} is not a valid image. Only JPG and PNG are supported.`);
        continue;
      }

      if (file.size > 10 * 1024 * 1024) {
        alert(`${file.name} is too large. Maximum size is 10MB per image.`);
        continue;
      }

      validFiles.push(file);
    }

    if (validFiles.length === 0) return;

    // Add to selected images
    const updatedImages = [...selectedImages, ...validFiles];
    setSelectedImages(updatedImages);

    // Create previews for new files
    const newPreviews: string[] = [];
    validFiles.forEach(file => {
      const reader = new FileReader();
      reader.onloadend = () => {
        newPreviews.push(reader.result as string);
        if (newPreviews.length === validFiles.length) {
          setImagePreviews([...imagePreviews, ...newPreviews]);
        }
      };
      reader.readAsDataURL(file);
    });
  };

  const removeImage = (index: number) => {
    setSelectedImages(selectedImages.filter((_, i) => i !== index));
    setImagePreviews(imagePreviews.filter((_, i) => i !== index));
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files) {
      handleImageSelect(e.dataTransfer.files);
    }
  };

  const handleImageAnalysis = async () => {
    if (selectedImages.length < 2) {
      alert('Please upload at least 2 images for analysis.');
      return;
    }

    setImageAnalyzing(true);
    const formData = new FormData();

    // Append all images
    selectedImages.forEach((image) => {
      formData.append('files', image);
    });

    try {
      const token = typeof window !== 'undefined'
        ? window.localStorage.getItem('ddips_auth_token')
        : null;

      const headers: Record<string, string> = {};
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      const response = await fetch('http://localhost:8000/analyze-image', {
        method: 'POST',
        headers,
        body: formData,
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Image analysis failed');
      }

      const result = await response.json();
      const drugs = result.analyzed_drugs || [];
      onAnalyze(drugs);

    } catch (error: any) {
      alert(error.message || 'Image analysis failed. Please try again.');
    } finally {
      setImageAnalyzing(false);
    }
  };

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (suggestionRef.current && !suggestionRef.current.contains(event.target as Node)) {
        setFocusedIndex(null);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  return (
    <div className="grid lg:grid-cols-2 gap-10 items-start">
      {/* Input Side */}
      <div className="glass-panel p-8 rounded-[32px] border border-white dark:border-slate-800 space-y-8 shadow-xl">
        <div>
          <h2 className="text-2xl font-bold text-slate-900 dark:text-white mb-2">Patient Medication Profile</h2>
          <p className="text-sm text-slate-500 dark:text-slate-400">Analyze interactions between multiple compounds for comprehensive safety profiling.</p>
        </div>

        {/* Segmented Toggle */}
        <div className="flex items-center gap-1 p-1 bg-slate-100 dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700">
          <button
            onClick={() => setInputMode('text')}
            className={`flex-1 px-4 py-2.5 rounded-lg font-bold text-sm transition-all ${inputMode === 'text'
                ? 'bg-white dark:bg-slate-900 text-slate-900 dark:text-white shadow-sm'
                : 'text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-300'
              }`}
          >
            Text Entry
          </button>
          <button
            onClick={() => setInputMode('image')}
            className={`flex-1 px-4 py-2.5 rounded-lg font-bold text-sm transition-all ${inputMode === 'image'
                ? 'bg-white dark:bg-slate-900 text-slate-900 dark:text-white shadow-sm'
                : 'text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-300'
              }`}
          >
            Image Upload
          </button>
        </div>

        {/* TEXT MODE */}
        {inputMode === 'text' && (
          <>
            <div className="space-y-4" ref={suggestionRef}>
              {drugs.map((drug, index) => {
                const suggestions = getFilteredSuggestions(drug);
                const isShowingSuggestions = focusedIndex === index && suggestions.length > 0;

                return (
                  <div key={index} className="relative flex gap-3 animate-in slide-in-from-left-2 duration-300">
                    <div className="relative flex-1">
                      <div className="absolute left-5 top-1/2 -translate-y-1/2 text-slate-400 dark:text-slate-500 pointer-events-none transition-colors">
                        <Search size={18} className={focusedIndex === index ? 'text-blue-500' : ''} />
                      </div>
                      <input
                        type="text"
                        value={drug}
                        onFocus={() => setFocusedIndex(index)}
                        onChange={(e) => updateField(index, e.target.value)}
                        placeholder={`Drug name #${index + 1}`}
                        className={`w-full bg-slate-50 dark:bg-slate-800 border transition-all font-medium text-slate-700 dark:text-slate-200 placeholder:text-slate-400 dark:placeholder:text-slate-500 rounded-2xl pl-12 pr-6 py-4 outline-none
                          ${focusedIndex === index ? 'border-blue-400 ring-4 ring-blue-100 dark:ring-blue-900/30' : 'border-slate-200 dark:border-slate-700'}`}
                      />

                      {isShowingSuggestions && (
                        <div className="absolute z-[50] w-full mt-2 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl shadow-2xl overflow-hidden animate-in fade-in zoom-in-95 duration-200">
                          <div className="p-2 bg-slate-50 dark:bg-slate-800/50 border-b border-slate-100 dark:border-slate-800">
                            <p className="text-[10px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-widest px-2">Clinical Database Matches</p>
                          </div>
                          <div className="max-h-60 overflow-y-auto custom-scrollbar">
                            {suggestions.map((s, sIndex) => (
                              <button
                                key={sIndex}
                                type="button"
                                onClick={() => {
                                  updateField(index, s);
                                  setFocusedIndex(null);
                                }}
                                className="w-full text-left px-5 py-3.5 hover:bg-blue-50 dark:hover:bg-blue-900/30 transition-colors flex items-center justify-between group border-b border-slate-50 dark:border-slate-800 last:border-0"
                              >
                                <span className="text-sm font-bold text-slate-700 dark:text-slate-200 group-hover:text-blue-600 dark:group-hover:text-blue-400">{s}</span>
                                <ArrowRight size={14} className="text-slate-300 opacity-0 group-hover:opacity-100 group-hover:translate-x-1 transition-all" />
                              </button>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                    {drugs.length > 2 && (
                      <button
                        onClick={() => removeField(index)}
                        className="p-4 text-slate-400 dark:text-slate-500 hover:text-red-500 dark:hover:text-red-400 transition-colors bg-slate-50 dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 hover:border-red-200 dark:hover:border-red-900/50"
                      >
                        <X size={20} />
                      </button>
                    )}
                  </div>
                );
              })}

              <button
                onClick={addField}
                className="w-full flex items-center justify-center gap-2 py-4 border-2 border-dashed border-slate-200 dark:border-slate-700 rounded-2xl text-slate-400 dark:text-slate-500 hover:border-blue-400 dark:hover:border-blue-500 hover:text-blue-600 dark:hover:text-blue-400 transition-all font-bold text-sm"
              >
                <Plus size={18} />
                Add Medication
              </button>
            </div>

            <button
              disabled={drugs.some(d => !d) || loading}
              onClick={() => onAnalyze(drugs)}
              className={`w-full py-5 rounded-2xl font-bold text-lg shadow-xl transition-all flex items-center justify-center gap-3
                ${(drugs.some(d => !d) || loading)
                  ? 'bg-slate-100 dark:bg-slate-800 text-slate-400 dark:text-slate-600 cursor-not-allowed shadow-none'
                  : 'bg-gradient-to-r from-blue-600 to-teal-500 text-white shadow-blue-200 dark:shadow-blue-900/40 hover:shadow-blue-400 dark:hover:shadow-blue-500 hover:-translate-y-1 active:scale-95'}`}
            >
              {loading ? (
                <div className="flex items-center gap-3">
                  <RefreshCw className="animate-spin" size={22} />
                  Refining Neural Profile...
                </div>
              ) : (
                <>Run Full Polypharmacy Analysis <Zap size={20} /></>
              )}
            </button>
          </>
        )}

        {/* IMAGE MODE */}
        {inputMode === 'image' && (
          <>
            <input
              ref={fileInputRef}
              type="file"
              accept="image/jpeg,image/jpg,image/png"
              multiple
              onChange={(e) => handleImageSelect(e.target.files)}
              className="hidden"
            />

            {/* Upload Area */}
            {selectedImages.length < 5 && (
              <div
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
                onClick={() => fileInputRef.current?.click()}
                className={`relative border-2 border-dashed rounded-2xl p-8 transition-all cursor-pointer ${dragActive
                    ? 'border-blue-400 bg-blue-50 dark:bg-blue-900/20'
                    : 'border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/50 hover:border-blue-300 dark:hover:border-blue-700'
                  }`}
              >
                <div className="text-center space-y-4">
                  <div className="w-16 h-16 mx-auto bg-blue-100 dark:bg-blue-900/30 rounded-full flex items-center justify-center">
                    <Upload size={28} className="text-blue-600 dark:text-blue-400" />
                  </div>
                  <div>
                    <p className="text-slate-700 dark:text-slate-200 font-bold mb-1">
                      {selectedImages.length === 0
                        ? 'Upload prescription images (2-5 required)'
                        : `Add more images (${selectedImages.length}/5 uploaded)`}
                    </p>
                    <p className="text-sm text-slate-500 dark:text-slate-400">Drag and drop or click to browse • JPG, PNG • Max 10MB each</p>
                  </div>
                </div>
              </div>
            )}

            {/* Image Previews */}
            {selectedImages.length > 0 && (
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <p className="text-sm font-bold text-slate-600 dark:text-slate-300">
                    {selectedImages.length} image{selectedImages.length !== 1 ? 's' : ''} selected
                    {selectedImages.length < 2 && <span className="text-red-500 ml-2">(minimum 2 required)</span>}
                  </p>
                  <button
                    onClick={() => {
                      setSelectedImages([]);
                      setImagePreviews([]);
                    }}
                    className="text-xs text-red-500 hover:text-red-600 dark:text-red-400 dark:hover:text-red-300 font-bold flex items-center gap-1"
                  >
                    <Trash2 size={12} />
                    Clear All
                  </button>
                </div>
                <div className="grid grid-cols-2 gap-3">
                  {imagePreviews.map((preview, idx) => (
                    <div key={idx} className="relative group">
                      <div className="relative w-full h-32 rounded-xl overflow-hidden bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-slate-700">
                        <img src={preview} alt={`Preview ${idx + 1}`} className="w-full h-full object-cover" />
                        <div className="absolute inset-0 bg-black/0 group-hover:bg-black/40 transition-all flex items-center justify-center">
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              removeImage(idx);
                            }}
                            className="opacity-0 group-hover:opacity-100 transition-opacity bg-red-500 hover:bg-red-600 text-white p-2 rounded-full"
                          >
                            <X size={16} />
                          </button>
                        </div>
                      </div>
                      <p className="text-xs text-slate-500 dark:text-slate-400 mt-1 truncate">{selectedImages[idx]?.name}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <button
              disabled={selectedImages.length < 2 || imageAnalyzing}
              onClick={handleImageAnalysis}
              className={`w-full py-5 rounded-2xl font-bold text-lg shadow-xl transition-all flex items-center justify-center gap-3
                ${(selectedImages.length < 2 || imageAnalyzing)
                  ? 'bg-slate-100 dark:bg-slate-800 text-slate-400 dark:text-slate-600 cursor-not-allowed shadow-none'
                  : 'bg-gradient-to-r from-purple-600 to-blue-500 text-white shadow-purple-200 dark:shadow-purple-900/40 hover:shadow-purple-400 dark:hover:shadow-purple-500 hover:-translate-y-1 active:scale-95'}`}
            >
              {imageAnalyzing ? (
                <div className="flex items-center gap-3">
                  <RefreshCw className="animate-spin" size={22} />
                  Analyzing {selectedImages.length} Images with Gemini Vision...
                </div>
              ) : (
                <>Run AI Image Analysis ({selectedImages.length} images) <Zap size={20} /></>
              )}
            </button>
          </>
        )}
      </div>

      {/* Result Side */}
      <div className="space-y-8 min-h-[500px]">
        {!prediction && !loading && !imageAnalyzing && (
          <div className="h-full flex flex-col items-center justify-center text-center p-10 bg-slate-100/30 dark:bg-slate-800/20 rounded-[32px] border-2 border-dashed border-slate-200 dark:border-slate-800">
            <div className="w-16 h-16 bg-white dark:bg-slate-800 rounded-full flex items-center justify-center text-slate-300 dark:text-slate-600 mb-6 shadow-sm">
              <Activity size={32} />
            </div>
            <h3 className="text-xl font-bold text-slate-900 dark:text-white mb-2">Awaiting Analysis</h3>
            <p className="text-slate-500 dark:text-slate-400 max-w-xs text-sm">Enter a patient medication profile on the left to start the interaction analysis engine.</p>
          </div>
        )}

        {(loading || imageAnalyzing) && (
          <div className="space-y-6">
            {[1, 2, 3].map(i => (
              <div key={i} className="h-24 bg-slate-100 dark:bg-slate-900 rounded-[28px] animate-pulse"></div>
            ))}
            <div className="h-64 bg-slate-100 dark:bg-slate-900 rounded-[32px] animate-pulse"></div>
          </div>
        )}

        {prediction && (
          <div className="animate-in fade-in slide-in-from-right-4 duration-500 space-y-6">
            <div className={`p-8 rounded-[32px] border flex flex-col md:flex-row items-center justify-between gap-6 shadow-xl overflow-hidden relative
              ${prediction.riskLevel === 'HIGH' ? 'risk-gradient-high border-red-200 dark:border-red-900/30' :
                prediction.riskLevel === 'MODERATE' ? 'risk-gradient-mod border-amber-200 dark:border-amber-900/30' :
                  'risk-gradient-low border-emerald-200 dark:border-emerald-900/30'}`}>

              <div className="relative z-10 text-center md:text-left">
                <div className="flex items-center justify-center md:justify-start gap-3 mb-4">
                  <span className={`px-4 py-1.5 rounded-full text-xs font-black uppercase tracking-widest ${getRiskBadge(prediction.riskLevel)}`}>
                    {prediction.riskLevel} RISK
                  </span>
                  <span className="text-[11px] font-bold text-slate-400 dark:text-slate-500 bg-white/60 dark:bg-slate-900/60 px-3 py-1 rounded-full uppercase">
                    Severity: {prediction.severity}
                  </span>
                </div>
                <h3 className="text-2xl md:text-3xl font-bold text-slate-900 dark:text-white leading-tight">
                  {prediction.drugs.slice(0, 3).join(" + ")}{prediction.drugs.length > 3 ? "..." : ""}
                </h3>
                <div className="mt-4 flex items-center justify-center md:justify-start gap-6">
                  <div className="text-center md:text-left">
                    <p className="text-[10px] text-slate-400 dark:text-slate-500 font-bold uppercase">Confidence</p>
                    <p className="text-xl font-bold text-slate-900 dark:text-white">{(prediction.confidenceScore * 100).toFixed(0)}%</p>
                  </div>
                  <div className="w-[1px] h-8 bg-slate-200 dark:bg-slate-700"></div>
                  <div className="text-center md:text-left">
                    <p className="text-[10px] text-slate-400 dark:text-slate-500 font-bold uppercase">Refined By</p>
                    <p className="text-sm font-bold text-blue-600 dark:text-blue-400">Gemini 3 Pro</p>
                  </div>
                </div>
              </div>

              <button
                onClick={onReset}
                className="bg-white dark:bg-slate-800 px-6 py-4 rounded-2xl font-bold text-slate-700 dark:text-slate-200 shadow-lg hover:shadow-xl dark:border dark:border-slate-700 transition-all active:scale-95 flex items-center gap-2"
              >
                Clear Results <X size={18} />
              </button>
            </div>

            <div className="glass-panel p-8 rounded-[32px] border border-white dark:border-slate-800 space-y-6 shadow-xl transition-colors">
              <div className="flex items-center gap-2 text-xs font-bold text-slate-400 dark:text-slate-500 uppercase tracking-[0.15em] mb-2">
                <Info size={14} className="text-blue-500 dark:text-blue-400" />
                Mechanism Analysis
              </div>
              <p className="text-slate-700 dark:text-slate-300 leading-relaxed font-medium">
                {prediction.explanation}
              </p>

              <div className="pt-6 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between">
                <button
                  onClick={onViewReasoning}
                  className="text-blue-600 dark:text-blue-400 font-bold text-sm flex items-center gap-2 hover:underline"
                >
                  View Full Clinical Reasoning <ArrowRight size={16} />
                </button>
                <div className="flex gap-2">
                  <div className="w-8 h-8 rounded-full bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center text-blue-600 dark:text-blue-400"><AlertCircle size={16} /></div>
                  <div className="w-8 h-8 rounded-full bg-teal-100 dark:bg-teal-900/30 flex items-center justify-center text-teal-600 dark:text-teal-400"><Zap size={16} /></div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
