"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { FiUser, FiDollarSign, FiCalendar, FiPackage, FiFileText, FiCopy, FiDownload, FiRefreshCw, FiClipboard, FiBriefcase, FiBox, FiAlertCircle } from "react-icons/fi";

interface Deliverable {
  type: string;
  description: string;
  quantity: number;
  due_date: string;
}

interface DealTerms {
  brand_name: string;
  influencer_name: string;
  platform: string;
  campaign_name: string;
  total_fee: number;
  deliverables: Deliverable[];
  start_date: string;
  end_date: string;
}

interface ContractResponse {
  contract_text: string;
  contract_id: string;
  status: "draft" | "final";
  generated_at: string;
}

export default function ContractPage() {
  const [dealTerms, setDealTerms] = useState<DealTerms>({
    brand_name: "",
    influencer_name: "",
    platform: "",
    campaign_name: "",
    total_fee: 0,
    deliverables: [
      {
        type: "",
        description: "",
        quantity: 1,
        due_date: "",
      },
    ],
    start_date: "",
    end_date: "",
  });

  const [contractResponse, setContractResponse] =
    useState<ContractResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeSection, setActiveSection] = useState<"editor" | "preview">(
    "editor"
  );
  const [validationErrors, setValidationErrors] = useState<Partial<Record<keyof DealTerms, string>>>({});
  const [formSubmitted, setFormSubmitted] = useState(false);

  const resetForm = () => {
    setDealTerms({
      brand_name: "",
      influencer_name: "",
      platform: "",
      campaign_name: "",
      total_fee: 0,
      deliverables: [
        {
          type: "",
          description: "",
          quantity: 1,
          due_date: "",
        },
      ],
      start_date: "",
      end_date: "",
    });
    setValidationErrors({});
    setFormSubmitted(false);
  };

  const handleInputChange = (
    field: keyof DealTerms,
    value: string | number | Deliverable[]
  ) => {
    setDealTerms((prev) => ({
      ...prev,
      [field]: value,
    }));
  };

  const handleDeliverableChange = (
    index: number,
    field: keyof Deliverable,
    value: string | number
  ) => {
    const newDeliverables = [...dealTerms.deliverables];
    newDeliverables[index] = {
      ...newDeliverables[index],
      [field]: value,
    };
    handleInputChange("deliverables", newDeliverables);
  };

  const addDeliverable = () => {
    setDealTerms((prev) => ({
      ...prev,
      deliverables: [
        ...prev.deliverables,
        {
          type: "",
          description: "",
          quantity: 1,
          due_date: "",
        },
      ],
    }));
  };

  const removeDeliverable = (index: number) => {
    setDealTerms((prev) => ({
      ...prev,
      deliverables: prev.deliverables.filter((_, i) => i !== index),
    }));
  };

  // Validate form fields before submission
  const validateForm = () => {
    const errors: Partial<Record<keyof DealTerms, string>> = {};
    
    // Check required text fields
    if (!dealTerms.brand_name.trim()) errors.brand_name = "Brand name is required";
    if (!dealTerms.influencer_name.trim()) errors.influencer_name = "Influencer name is required";
    if (!dealTerms.platform.trim()) errors.platform = "Platform is required";
    if (!dealTerms.campaign_name.trim()) errors.campaign_name = "Campaign name is required";
    
    // Check dates
    if (!dealTerms.start_date) errors.start_date = "Start date is required";
    if (!dealTerms.end_date) errors.end_date = "End date is required";
    
    // Validate dates are logical
    if (dealTerms.start_date && dealTerms.end_date) {
      const start = new Date(dealTerms.start_date);
      const end = new Date(dealTerms.end_date);
      if (start > end) {
        errors.end_date = "End date must be after start date";
      }
    }
    
    // Check total fee
    if (dealTerms.total_fee <= 0) errors.total_fee = "Total fee must be greater than zero";
    
    // Validate deliverables
    if (dealTerms.deliverables.length === 0) {
      errors.deliverables = "At least one deliverable is required";
    } else {
      // Check if any deliverable has missing information
      const hasInvalidDeliverable = dealTerms.deliverables.some(
        (d) => !d.type.trim() || !d.description.trim() || !d.due_date || d.quantity <= 0
      );
      
      if (hasInvalidDeliverable) {
        errors.deliverables = "All deliverables must have complete information";
      }
    }
    
    return errors;
  };

  const handleGenerateContract = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormSubmitted(true);
    
    // Validate form
    const errors = validateForm();
    setValidationErrors(errors);
    
    // If there are validation errors, don't proceed
    if (Object.keys(errors).length > 0) {
      return;
    }
    
    setLoading(true);
    setError(null);

    try {
      const response = await fetch("/api/contract/generate", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ deal_terms: dealTerms }),
      });

      if (!response.ok) {
        throw new Error("Failed to generate contract");
      }

      const data = await response.json();
      setContractResponse(data);
      setActiveSection("preview");
      setFormSubmitted(false); // Reset form submission state
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <motion.div 
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
        className="mb-8"
      >
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-6">
          <div>
            <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-indigo-500 to-purple-600">
              Contract Generator
            </h1>
            <p className="text-gray-600 mt-1">
              Create professional, customized contracts for your influencer partnerships
            </p>
          </div>
          
          <div className="bg-white shadow-md rounded-[16px] p-1 flex">
            <button
              onClick={() => setActiveSection("editor")}
              className={`px-5 py-2.5 rounded-[12px] font-medium transition-all duration-200 flex items-center gap-2 ${
                activeSection === "editor"
                  ? "bg-gradient-to-r from-indigo-500 to-purple-600 text-white shadow-md"
                  : "bg-white text-gray-700 hover:bg-gray-50"
              }`}
            >
              <FiClipboard className="h-4 w-4" />
              <span>Editor</span>
            </button>
            <button
              onClick={() => setActiveSection("preview")}
              className={`px-5 py-2.5 rounded-[12px] font-medium transition-all duration-200 flex items-center gap-2 ${
                activeSection === "preview"
                  ? "bg-gradient-to-r from-indigo-500 to-purple-600 text-white shadow-md"
                  : "bg-white text-gray-700 hover:bg-gray-50"
              }`}
              disabled={!contractResponse}
            >
              <FiFileText className="h-4 w-4" />
              <span>Preview</span>
            </button>
          </div>
        </div>
      </motion.div>

      {activeSection === "editor" ? (
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
          className="bg-white shadow-lg rounded-[20px] overflow-hidden"
        >
          <div className="bg-gradient-to-r from-indigo-500 to-purple-600 h-2"></div>
          <form onSubmit={handleGenerateContract} className="p-8 space-y-8">
            {/* Validation Summary */}
            {formSubmitted && Object.keys(validationErrors).length > 0 && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3 }}
                className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg"
              >
                <h3 className="text-red-700 font-medium flex items-center gap-2 mb-2">
                  <FiAlertCircle />
                  <span>Please fix the following errors:</span>
                </h3>
                <ul className="ml-6 list-disc text-red-600 text-sm space-y-1">
                  {Object.entries(validationErrors).map(([field, message]) => (
                    <li key={field}>{message}</li>
                  ))}
                </ul>
              </motion.div>
            )}
            
            {/* Basic Information */}
            <div>
              <h2 className="text-xl font-semibold text-gray-800 mb-4 flex items-center gap-2">
                <FiBriefcase className="text-indigo-500" />
                <span>Basic Information</span>
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Brand Name
                  </label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                      <FiBriefcase className={`h-5 w-5 ${formSubmitted && validationErrors.brand_name ? "text-red-400" : "text-gray-400"}`} />
                    </div>
                    <input
                      type="text"
                      value={dealTerms.brand_name}
                      onChange={(e) => {
                        handleInputChange("brand_name", e.target.value);
                        if (formSubmitted) {
                          // Clear validation error when user starts typing
                          setValidationErrors(prev => ({...prev, brand_name: undefined}));
                        }
                      }}
                      className={`w-full pl-10 px-4 py-2.5 border rounded-lg shadow-sm hover:bg-white focus:bg-white transition-all duration-200 focus:outline-none focus:ring-2 bg-gray-50 ${
                        formSubmitted && validationErrors.brand_name
                          ? "border-red-300 bg-red-50 focus:border-red-500 focus:ring-red-500"
                          : "border-gray-200 focus:border-indigo-500 focus:ring-indigo-500"
                      }`}
                      placeholder="e.g. Acme Corporation"
                      required
                    />
                    {formSubmitted && validationErrors.brand_name && (
                      <p className="mt-1 text-sm text-red-600">{validationErrors.brand_name}</p>
                    )}
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Influencer Name
                  </label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                      <FiUser className={`h-5 w-5 ${formSubmitted && validationErrors.influencer_name ? "text-red-400" : "text-gray-400"}`} />
                    </div>
                    <input
                      type="text"
                      value={dealTerms.influencer_name}
                      onChange={(e) => {
                        handleInputChange("influencer_name", e.target.value);
                        if (formSubmitted) {
                          setValidationErrors(prev => ({...prev, influencer_name: undefined}));
                        }
                      }}
                      className={`w-full pl-10 px-4 py-2.5 border rounded-lg shadow-sm hover:bg-white focus:bg-white transition-all duration-200 focus:outline-none focus:ring-2 bg-gray-50 ${
                        formSubmitted && validationErrors.influencer_name
                          ? "border-red-300 bg-red-50 focus:border-red-500 focus:ring-red-500"
                          : "border-gray-200 focus:border-indigo-500 focus:ring-indigo-500"
                      }`}
                      placeholder="e.g. John Smith"
                      required
                    />
                    {formSubmitted && validationErrors.influencer_name && (
                      <p className="mt-1 text-sm text-red-600">{validationErrors.influencer_name}</p>
                    )}
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Platform
                  </label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                      <FiBox className={`h-5 w-5 ${formSubmitted && validationErrors.platform ? "text-red-400" : "text-gray-400"}`} />
                    </div>
                    <select
                      value={dealTerms.platform}
                      onChange={(e) => {
                        handleInputChange("platform", e.target.value);
                        if (formSubmitted) {
                          setValidationErrors(prev => ({...prev, platform: undefined}));
                        }
                      }}
                      className={`w-full pl-10 px-4 py-2.5 border rounded-lg shadow-sm hover:bg-white focus:bg-white transition-all duration-200 focus:outline-none focus:ring-2 bg-gray-50 appearance-none ${
                        formSubmitted && validationErrors.platform
                          ? "border-red-300 bg-red-50 focus:border-red-500 focus:ring-red-500"
                          : "border-gray-200 focus:border-indigo-500 focus:ring-indigo-500"
                      }`}
                      required
                    >
                      <option value="">Select Platform</option>
                      <option value="Instagram">Instagram</option>
                      <option value="YouTube">YouTube</option>
                      <option value="TikTok">TikTok</option>
                      <option value="Twitter">Twitter</option>
                    </select>
                    <div className="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none">
                      <svg className="h-5 w-5 text-gray-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                        <path fillRule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clipRule="evenodd" />
                      </svg>
                    </div>
                    {formSubmitted && validationErrors.platform && (
                      <p className="mt-1 text-sm text-red-600">{validationErrors.platform}</p>
                    )}
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Campaign Name
                  </label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                      <FiPackage className={`h-5 w-5 ${formSubmitted && validationErrors.campaign_name ? "text-red-400" : "text-gray-400"}`} />
                    </div>
                    <input
                      type="text"
                      value={dealTerms.campaign_name}
                      onChange={(e) => {
                        handleInputChange("campaign_name", e.target.value);
                        if (formSubmitted) {
                          setValidationErrors(prev => ({...prev, campaign_name: undefined}));
                        }
                      }}
                      className={`w-full pl-10 px-4 py-2.5 border rounded-lg shadow-sm hover:bg-white focus:bg-white transition-all duration-200 focus:outline-none focus:ring-2 bg-gray-50 ${
                        formSubmitted && validationErrors.campaign_name
                          ? "border-red-300 bg-red-50 focus:border-red-500 focus:ring-red-500"
                          : "border-gray-200 focus:border-indigo-500 focus:ring-indigo-500"
                      }`}
                      placeholder="e.g. Summer Collection 2025"
                      required
                    />
                    {formSubmitted && validationErrors.campaign_name && (
                      <p className="mt-1 text-sm text-red-600">{validationErrors.campaign_name}</p>
                    )}
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Total Fee ($)
                  </label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                      <FiDollarSign className={`h-5 w-5 ${formSubmitted && validationErrors.total_fee ? "text-red-400" : "text-gray-400"}`} />
                    </div>
                    <input
                      type="number"
                      value={dealTerms.total_fee}
                      onChange={(e) => {
                        // Handle empty string case to prevent NaN
                        const value = e.target.value === "" ? 0 : parseInt(e.target.value);
                        handleInputChange("total_fee", value);
                        if (formSubmitted) {
                          setValidationErrors(prev => ({...prev, total_fee: undefined}));
                        }
                      }}
                      className={`w-full pl-10 px-4 py-2.5 border rounded-lg shadow-sm hover:bg-white focus:bg-white transition-all duration-200 focus:outline-none focus:ring-2 bg-gray-50 ${
                        formSubmitted && validationErrors.total_fee
                          ? "border-red-300 bg-red-50 focus:border-red-500 focus:ring-red-500"
                          : "border-gray-200 focus:border-indigo-500 focus:ring-indigo-500"
                      }`}
                      placeholder="e.g. 5000"
                      min="0"
                      required
                    />
                    {formSubmitted && validationErrors.total_fee && (
                      <p className="mt-1 text-sm text-red-600">{validationErrors.total_fee}</p>
                    )}
                  </div>
                </div>
              </div>
            </div>
            {/* Campaign Dates */}
            <div>
              <h2 className="text-xl font-semibold text-gray-800 mb-4 flex items-center gap-2">
                <FiCalendar className="text-indigo-500" />
                <span>Campaign Timeline</span>
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Start Date
                  </label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                      <FiCalendar className={`h-5 w-5 ${formSubmitted && validationErrors.start_date ? "text-red-400" : "text-gray-400"}`} />
                    </div>
                    <input
                      type="date"
                      value={dealTerms.start_date}
                      onChange={(e) => {
                        handleInputChange("start_date", e.target.value);
                        if (formSubmitted) {
                          setValidationErrors(prev => {
                            // Also check if end_date error was due to start_date > end_date
                            if (prev.end_date && dealTerms.end_date) {
                              const start = new Date(e.target.value);
                              const end = new Date(dealTerms.end_date);
                              if (start <= end) {
                                return {...prev, start_date: undefined, end_date: undefined};
                              }
                            }
                            return {...prev, start_date: undefined};
                          });
                        }
                      }}
                      className={`w-full pl-10 px-4 py-2.5 border rounded-lg shadow-sm hover:bg-white focus:bg-white transition-all duration-200 focus:outline-none focus:ring-2 bg-gray-50 ${
                        formSubmitted && validationErrors.start_date
                          ? "border-red-300 bg-red-50 focus:border-red-500 focus:ring-red-500"
                          : "border-gray-200 focus:border-indigo-500 focus:ring-indigo-500"
                      }`}
                      required
                    />
                    {formSubmitted && validationErrors.start_date && (
                      <p className="mt-1 text-sm text-red-600">{validationErrors.start_date}</p>
                    )}
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    End Date
                  </label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                      <FiCalendar className={`h-5 w-5 ${formSubmitted && validationErrors.end_date ? "text-red-400" : "text-gray-400"}`} />
                    </div>
                    <input
                      type="date"
                      value={dealTerms.end_date}
                      onChange={(e) => {
                        handleInputChange("end_date", e.target.value);
                        if (formSubmitted) {
                          setValidationErrors(prev => {
                            // Check if dates are logical
                            if (dealTerms.start_date) {
                              const start = new Date(dealTerms.start_date);
                              const end = new Date(e.target.value);
                              if (start > end) {
                                return {...prev, end_date: "End date must be after start date"};
                              }
                            }
                            return {...prev, end_date: undefined};
                          });
                        }
                      }}
                      className={`w-full pl-10 px-4 py-2.5 border rounded-lg shadow-sm hover:bg-white focus:bg-white transition-all duration-200 focus:outline-none focus:ring-2 bg-gray-50 ${
                        formSubmitted && validationErrors.end_date
                          ? "border-red-300 bg-red-50 focus:border-red-500 focus:ring-red-500"
                          : "border-gray-200 focus:border-indigo-500 focus:ring-indigo-500"
                      }`}
                      required
                    />
                    {formSubmitted && validationErrors.end_date && (
                      <p className="mt-1 text-sm text-red-600">{validationErrors.end_date}</p>
                    )}
                  </div>
                </div>
              </div>
            </div>

            {/* Deliverables */}
            <div>
              {formSubmitted && validationErrors.deliverables && (
                <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
                  <p className="text-sm text-red-600 flex items-center">
                    <FiAlertCircle className="mr-2" />
                    {validationErrors.deliverables}
                  </p>
                </div>
              )}
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-xl font-semibold text-gray-800 flex items-center gap-2">
                  <FiPackage className="text-indigo-500" />
                  <span>Deliverables</span>
                </h2>
                <button
                  type="button"
                  onClick={addDeliverable}
                  className="px-4 py-2.5 bg-gradient-to-r from-indigo-500 to-purple-600 text-white rounded-lg hover:shadow-md transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 flex items-center gap-2"
                >
                  <FiPackage className="h-4 w-4" />
                  <span>Add Deliverable</span>
                </button>
              </div>

              <div className="space-y-4">
                {dealTerms.deliverables.map((deliverable, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.3 }}
                    className="p-6 border border-gray-200 bg-white rounded-lg shadow-sm space-y-4 hover:shadow-md transition-all duration-200"
                  >
                    <div className="flex justify-between items-start">
                      <h3 className="text-lg font-medium text-gray-800 flex items-center gap-2">
                        <span className="inline-flex items-center justify-center w-6 h-6 rounded-full bg-indigo-100 text-indigo-600 text-sm font-semibold">{index + 1}</span>
                        <span>Deliverable {index + 1}</span>
                      </h3>
                      {dealTerms.deliverables.length > 1 && (
                        <button
                          type="button"
                          onClick={() => removeDeliverable(index)}
                          className="text-gray-400 hover:text-red-600 transition-colors duration-200 p-1 rounded-full hover:bg-gray-100"
                        >
                          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                          </svg>
                        </button>
                      )}
                    </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-5 mt-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Type
                      </label>
                      <div className="relative">
                        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                          <FiPackage className={`h-5 w-5 ${formSubmitted && validationErrors.deliverables && !deliverable.type.trim() ? "text-red-400" : "text-gray-400"}`} />
                        </div>
                        <input
                          type="text"
                          value={deliverable.type}
                          onChange={(e) => {
                            handleDeliverableChange(index, "type", e.target.value);
                            if (formSubmitted && validationErrors.deliverables) {
                              // Clear validation errors when user types
                              const hasInvalidDeliverable = dealTerms.deliverables.some(
                                (d, i) => (i === index ? !e.target.value.trim() : !d.type.trim()) || !d.description.trim() || !d.due_date || d.quantity <= 0
                              );
                              
                              if (!hasInvalidDeliverable) {
                                setValidationErrors(prev => ({...prev, deliverables: undefined}));
                              }
                            }
                          }}
                          className={`w-full pl-10 px-4 py-2.5 border rounded-lg shadow-sm hover:bg-white focus:bg-white transition-all duration-200 focus:outline-none focus:ring-2 bg-gray-50 ${
                            formSubmitted && validationErrors.deliverables && !deliverable.type.trim()
                              ? "border-red-300 bg-red-50 focus:border-red-500 focus:ring-red-500"
                              : "border-gray-200 focus:border-indigo-500 focus:ring-indigo-500"
                          }`}
                          placeholder="e.g., Instagram Post, YouTube Video"
                          required
                        />
                      </div>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Quantity
                      </label>
                      <div className="relative">
                        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                          <FiBox className={`h-5 w-5 ${formSubmitted && validationErrors.deliverables && deliverable.quantity <= 0 ? "text-red-400" : "text-gray-400"}`} />
                        </div>
                        <input
                          type="number"
                          value={deliverable.quantity}
                          onChange={(e) => {
                            // Handle empty string case to prevent NaN
                            const value = e.target.value === "" ? 0 : parseInt(e.target.value);
                            handleDeliverableChange(index, "quantity", value);
                            
                            if (formSubmitted && validationErrors.deliverables) {
                              // Clear validation errors when user types valid value
                              const hasInvalidDeliverable = dealTerms.deliverables.some(
                                (d, i) => !d.type.trim() || !d.description.trim() || !d.due_date || (i === index ? value <= 0 : d.quantity <= 0)
                              );
                              
                              if (!hasInvalidDeliverable) {
                                setValidationErrors(prev => ({...prev, deliverables: undefined}));
                              }
                            }
                          }}
                          className={`w-full pl-10 px-4 py-2.5 border rounded-lg shadow-sm hover:bg-white focus:bg-white transition-all duration-200 focus:outline-none focus:ring-2 bg-gray-50 ${
                            formSubmitted && validationErrors.deliverables && deliverable.quantity <= 0
                              ? "border-red-300 bg-red-50 focus:border-red-500 focus:ring-red-500"
                              : "border-gray-200 focus:border-indigo-500 focus:ring-indigo-500"
                          }`}
                          min="1"
                          placeholder="e.g., 1"
                          required
                        />
                      </div>
                    </div>
                    <div className="md:col-span-2">
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Description
                      </label>
                      <div className="relative">
                        <textarea
                          value={deliverable.description}
                          onChange={(e) => {
                            handleDeliverableChange(index, "description", e.target.value);
                            
                            if (formSubmitted && validationErrors.deliverables) {
                              // Clear validation errors when user types valid value
                              const hasInvalidDeliverable = dealTerms.deliverables.some(
                                (d, i) => !d.type.trim() || (i === index ? !e.target.value.trim() : !d.description.trim()) || !d.due_date || d.quantity <= 0
                              );
                              
                              if (!hasInvalidDeliverable) {
                                setValidationErrors(prev => ({...prev, deliverables: undefined}));
                              }
                            }
                          }}
                          className={`w-full px-4 py-2.5 border rounded-lg shadow-sm hover:bg-white focus:bg-white transition-all duration-200 focus:outline-none focus:ring-2 bg-gray-50 ${
                            formSubmitted && validationErrors.deliverables && !deliverable.description.trim()
                              ? "border-red-300 bg-red-50 focus:border-red-500 focus:ring-red-500"
                              : "border-gray-200 focus:border-indigo-500 focus:ring-indigo-500"
                          }`}
                          rows={3}
                          placeholder="Describe the deliverable in detail..."
                          required
                        />
                      </div>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Due Date
                      </label>
                      <div className="relative">
                        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                          <FiCalendar className={`h-5 w-5 ${formSubmitted && validationErrors.deliverables && !deliverable.due_date ? "text-red-400" : "text-gray-400"}`} />
                        </div>
                        <input
                          type="date"
                          value={deliverable.due_date}
                          onChange={(e) => {
                            handleDeliverableChange(index, "due_date", e.target.value);
                            
                            if (formSubmitted && validationErrors.deliverables) {
                              // Clear validation errors when user selects a date
                              const hasInvalidDeliverable = dealTerms.deliverables.some(
                                (d, i) => !d.type.trim() || !d.description.trim() || (i === index ? !e.target.value : !d.due_date) || d.quantity <= 0
                              );
                              
                              if (!hasInvalidDeliverable) {
                                setValidationErrors(prev => ({...prev, deliverables: undefined}));
                              }
                            }
                          }}
                          className={`w-full pl-10 px-4 py-2.5 border rounded-lg shadow-sm hover:bg-white focus:bg-white transition-all duration-200 focus:outline-none focus:ring-2 bg-gray-50 ${
                            formSubmitted && validationErrors.deliverables && !deliverable.due_date
                              ? "border-red-300 bg-red-50 focus:border-red-500 focus:ring-red-500"
                              : "border-gray-200 focus:border-indigo-500 focus:ring-indigo-500"
                          }`}
                          required
                        />
                      </div>
                    </div>
                  </div>
                  </motion.div>
                ))}
              </div>
            </div>

            <div className="flex justify-end space-x-4 mt-8">
              <button
                type="button"
                onClick={resetForm}
                className="px-5 py-2.5 bg-gray-100 text-gray-700 rounded-lg shadow-sm hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 transition-all duration-200 flex items-center gap-2"
              >
                <FiRefreshCw className="h-4 w-4" />
                <span>Reset</span>
              </button>
              <button
                type="submit"
                disabled={loading || (formSubmitted && Object.keys(validationErrors).length > 0)}
                className="px-5 py-2.5 bg-gradient-to-r from-indigo-500 to-purple-600 text-white rounded-lg hover:shadow-md transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <FiFileText className="h-4 w-4" />
                <span>
                  {loading 
                    ? "Generating..." 
                    : formSubmitted && Object.keys(validationErrors).length > 0 
                      ? "Please Fix Errors" 
                      : "Generate Contract"}
                </span>
              </button>
            </div>
          </form>
        </motion.div>
      ) : (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
          className="bg-white shadow-lg rounded-[20px] overflow-hidden"
        >
          <div className="bg-gradient-to-r from-indigo-500 to-purple-600 h-2"></div>
          <div className="p-8 space-y-8">
            {error ? (
              <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg flex items-center gap-2 animate-fade-in">
                <svg className="w-5 h-5 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span>{error}</span>
              </div>
            ) : contractResponse ? (
              <div className="space-y-6">
                <div className="flex justify-between items-center">
                  <div>
                    <h2 className="text-xl font-semibold bg-clip-text text-transparent bg-gradient-to-r from-indigo-500 to-purple-600">
                      Generated Contract
                    </h2>
                    <p className="text-sm text-gray-500">
                      Contract ID: {contractResponse.contract_id}
                    </p>
                  </div>
                  <span
                    className={`px-3 py-1 rounded-full text-sm font-medium ${
                      contractResponse.status === "final"
                        ? "bg-green-100 text-green-800"
                        : "bg-yellow-100 text-yellow-800"
                    }`}
                  >
                    {contractResponse.status.toUpperCase()}
                  </span>
                </div>

                <div className="prose max-w-none">
                  <div className="whitespace-pre-wrap font-mono text-sm bg-gray-50 p-6 rounded-lg shadow-sm border border-gray-100">
                    {contractResponse.contract_text}
                  </div>
                </div>

                <div className="flex justify-end space-x-4">
                  <button
                    onClick={() => {
                      if (contractResponse) {
                        navigator.clipboard.writeText(
                          contractResponse.contract_text
                        );
                      }
                    }}
                    className="px-5 py-2.5 bg-gray-100 text-gray-700 rounded-lg shadow-sm hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 transition-all duration-200 flex items-center gap-2"
                  >
                    <FiCopy className="h-4 w-4" />
                    <span>Copy to Clipboard</span>
                  </button>
                  <button
                    onClick={() => {
                      const blob = new Blob([contractResponse.contract_text], {
                        type: "text/plain",
                      });
                      const url = URL.createObjectURL(blob);
                      const a = document.createElement("a");
                      a.href = url;
                      a.download = `contract-${contractResponse.contract_id}.txt`;
                      document.body.appendChild(a);
                      a.click();
                      document.body.removeChild(a);
                      URL.revokeObjectURL(url);
                    }}
                    className="px-5 py-2.5 bg-gradient-to-r from-indigo-500 to-purple-600 text-white rounded-lg hover:shadow-md transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 flex items-center gap-2"
                  >
                    <FiDownload className="h-4 w-4" />
                    <span>Download</span>
                  </button>
                </div>
              </div>
            ) : (
              <div className="text-center py-12 text-gray-500 flex flex-col items-center">
                <FiFileText className="h-12 w-12 mb-3 text-gray-300" />
                <p>Generate a contract to see the preview</p>
              </div>
            )}
          </div>
        </motion.div>
      )}
    </div>
  );
}
