"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { FiSend, FiEdit, FiCopy, FiCheck, FiMail, FiUser, FiMessageSquare, FiBarChart, FiType, FiTarget, FiTag } from "react-icons/fi";

interface CreatorProfile {
  name: string;
  platform: string;
  content_style: string;
}

interface CampaignBrief {
  brand_name: string;
  campaign_name: string;
  goal: string;
}

interface OutreachRequest {
  creator_profile: CreatorProfile;
  campaign_brief: CampaignBrief;
  message_type: "initial_outreach" | "follow_up" | "partnership_proposal";
}

interface OutreachResponse {
  message: string;
  tone: string;
  suggested_subject?: string;
  personalization_notes?: string[];
}

export default function OutreachGeneration() {
  const [formData, setFormData] = useState<OutreachRequest>({
    creator_profile: {
      name: "",
      platform: "",
      content_style: "",
    },
    campaign_brief: {
      brand_name: "",
      campaign_name: "",
      goal: "",
    },
    message_type: "initial_outreach",
  });
  const [formErrors, setFormErrors] = useState<Record<string, string>>({});
  const [formSubmitted, setFormSubmitted] = useState(false);

  const [generatedMessage, setGeneratedMessage] =
    useState<OutreachResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);
  const [activeTab, setActiveTab] = useState<"form" | "preview">("form");
  
  // For small screens we'll switch between tabs
  // For larger screens both will be visible

  const validateForm = () => {
    const errors: Record<string, string> = {};
    
    // Validate creator profile fields
    if (!formData.creator_profile.name.trim()) {
      errors['creator_profile.name'] = 'Creator name is required';
    }
    
    if (!formData.creator_profile.platform) {
      errors['creator_profile.platform'] = 'Platform is required';
    }
    
    if (!formData.creator_profile.content_style.trim()) {
      errors['creator_profile.content_style'] = 'Content style is required';
    }
    
    // Validate campaign brief fields
    if (!formData.campaign_brief.brand_name.trim()) {
      errors['campaign_brief.brand_name'] = 'Brand name is required';
    }
    
    if (!formData.campaign_brief.campaign_name.trim()) {
      errors['campaign_brief.campaign_name'] = 'Campaign name is required';
    }
    
    if (!formData.campaign_brief.goal.trim()) {
      errors['campaign_brief.goal'] = 'Campaign goal is required';
    }
    
    return errors;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormSubmitted(true);
    
    const validationErrors = validateForm();
    setFormErrors(validationErrors);
    
    if (Object.keys(validationErrors).length > 0) {
      return; // Don't proceed if there are validation errors
    }
    
    setLoading(true);
    setError(null);

    try {
      const response = await fetch("http://localhost:8000/communication/generate-outreach", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        throw new Error("Failed to generate outreach message");
      }

      const data = await response.json();
      setGeneratedMessage(data);
      setActiveTab("preview");
    } catch (err) {
      setError("An error occurred while generating the outreach message. Please try again.");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };
  
  const handleCopyToClipboard = () => {
    if (generatedMessage) {
      navigator.clipboard.writeText(generatedMessage.message);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const getFieldError = (section: string, field: string) => {
    const errorKey = `${section}.${field}`;
    return formSubmitted ? formErrors[errorKey] : undefined;
  };

  const renderErrorMessage = (error?: string) => {
    if (!error) return null;
    return (
      <p className="mt-1 text-sm text-rose-600 flex items-center">
        <svg xmlns="http://www.w3.org/2000/svg" className="h-3.5 w-3.5 mr-1.5 flex-shrink-0" viewBox="0 0 20 20" fill="currentColor">
          <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
        </svg>
        {error}
      </p>
    );
  };

  const handleInputChange = (section: keyof OutreachRequest, field: string, value: string) => {
    if (formSubmitted) {
      setFormErrors(prev => {
        const newErrors = { ...prev };
        const errorKey = `${section}.${field}`;
        if (newErrors[errorKey]) {
          delete newErrors[errorKey];
        }
        return newErrors;
      });
    }
    
    if (section === "creator_profile" || section === "campaign_brief") {
      setFormData({
        ...formData,
        [section]: {
          ...formData[section],
          [field]: value,
        },
      });
    } else {
      setFormData({
        ...formData,
        [field]: value,
      });
    }
  };

  return (
    <div className="py-8">
      <div className="container mx-auto px-4 max-w-7xl">
        {/* Page Header */}
        <motion.div 
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="mb-8 flex items-start gap-3"
        >
          <div className="bg-indigo-100 p-2 rounded-lg mt-1">
            <FiMail className="h-6 w-6 text-indigo-600" />
          </div>
          <div>
            <h1 className="text-3xl font-bold text-gray-900 tracking-tight">Outreach Message Generator</h1>
            <p className="mt-1 text-gray-600 text-sm">Create personalized outreach messages for your influencer campaigns</p>
          </div>
        </motion.div>
        
        {/* Mobile Tab Navigation */}
        <div className="sm:hidden mb-6">
          <div className="flex rounded-lg shadow-md overflow-hidden">
            <button
              onClick={() => setActiveTab("form")}
              className={`flex-1 py-2.5 px-4 text-center text-sm font-medium flex items-center justify-center gap-2 transition-all duration-200 ${activeTab === "form" ? "bg-gradient-to-r from-indigo-500 to-indigo-600 text-white" : "bg-white text-gray-700 hover:text-gray-900 hover:bg-gray-50"} rounded-l-lg`}
            >
              <FiEdit className="h-4 w-4" />
              Form
            </button>
            <button
              onClick={() => setActiveTab("preview")}
              className={`flex-1 py-2.5 px-4 text-center text-sm font-medium flex items-center justify-center gap-2 transition-all duration-200 ${activeTab === "preview" ? "bg-gradient-to-r from-indigo-500 to-indigo-600 text-white" : "bg-white text-gray-700 hover:text-gray-900 hover:bg-gray-50"} rounded-r-lg`}
            >
              <FiMessageSquare className="h-4 w-4" />
              Preview
            </button>
          </div>
        </div>

        <div className="grid md:grid-cols-2 gap-8">
          {/* Form Section */}
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: activeTab === "form" || window.innerWidth >= 768 ? 1 : 0, y: 0 }}
            transition={{ duration: 0.4 }}
            className={`bg-white shadow-xl rounded-xl p-6 border border-gray-100 relative overflow-hidden ${activeTab !== "form" && "md:block hidden"}`}
          >
            <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-indigo-400 to-purple-500"></div>
            <form onSubmit={handleSubmit} className="space-y-6">
              <div>
                <h2 className="text-xl font-semibold text-gray-800 mb-4 flex items-center gap-2">
                  <span className="bg-indigo-100 p-1.5 rounded-md">
                    <FiUser className="h-5 w-5 text-indigo-600" />
                  </span>
                  Creator Profile
                </h2>
                </div>
                <div className="space-y-4">
                  <div>
                    <label htmlFor="creatorName" className="block text-sm font-medium text-gray-700 mb-1">
                      Creator Name
                    </label>
                    <div className="relative">
                      <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                        <FiUser className="h-4 w-4 text-gray-400" />
                      </div>
                      <input
                        type="text"
                        id="creatorName"
                        value={formData.creator_profile.name}
                        onChange={(e) =>
                          handleInputChange(
                            "creator_profile",
                            "name",
                            e.target.value
                          )
                        }
                        className={`w-full pl-10 px-4 py-2.5 border rounded-lg shadow-sm hover:bg-white focus:bg-white transition-all duration-200 focus:outline-none focus:ring-2 ${
                          getFieldError('creator_profile', 'name')
                            ? 'border-rose-500 bg-rose-50 focus:border-rose-500 focus:ring-rose-500'
                            : 'border-gray-200 bg-gray-50 focus:border-indigo-500 focus:ring-indigo-500'
                        }`}
                        placeholder="e.g. Sarah Smith"
                        required
                    />
                  </div>
                  {renderErrorMessage(getFieldError('creator_profile', 'name'))}
                  <div>
                    <label htmlFor="platform" className="block text-sm font-medium text-gray-700 mb-1">
                      Platform
                    </label>
                    <div className="relative">
                      <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                        <FiMessageSquare className="h-4 w-4 text-gray-400" />
                      </div>
                      <select
                        id="platform"
                        value={formData.creator_profile.platform}
                        onChange={(e) =>
                          handleInputChange(
                            "creator_profile",
                            "platform",
                            e.target.value
                          )
                        }
                        className={`w-full pl-10 px-4 py-2.5 border rounded-lg shadow-sm hover:bg-white focus:bg-white transition-all duration-200 focus:outline-none focus:ring-2 appearance-none ${
                          getFieldError('creator_profile', 'platform')
                            ? 'border-rose-500 bg-rose-50 focus:border-rose-500 focus:ring-rose-500'
                            : 'border-gray-200 bg-gray-50 focus:border-indigo-500 focus:ring-indigo-500'
                        }`}
                        required
                      >
                      <option value="">Select Platform</option>
                      <option value="Instagram">Instagram</option>
                      <option value="TikTok">TikTok</option>
                      <option value="YouTube">YouTube</option>
                      <option value="Twitter">Twitter</option>
                      <option value="Twitch">Twitch</option>
                      </select>
                    </div>
                    {renderErrorMessage(getFieldError('creator_profile', 'platform'))}
                  </div>
                  <div>
                    <label htmlFor="contentStyle" className="block text-sm font-medium text-gray-700 mb-1">
                      Content Style
                    </label>
                    <div className="relative">
                      <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                        <FiTag className="h-4 w-4 text-gray-400" />
                      </div>
                      <input
                        type="text"
                        id="contentStyle"
                        value={formData.creator_profile.content_style}
                        onChange={(e) =>
                          handleInputChange(
                            "creator_profile",
                            "content_style",
                            e.target.value
                          )
                        }
                        className={`w-full pl-10 px-4 py-2.5 border rounded-lg shadow-sm hover:bg-white focus:bg-white transition-all duration-200 focus:outline-none focus:ring-2 ${
                          getFieldError('creator_profile', 'content_style')
                            ? 'border-rose-500 bg-rose-50 focus:border-rose-500 focus:ring-rose-500'
                            : 'border-gray-200 bg-gray-50 focus:border-indigo-500 focus:ring-indigo-500'
                        }`}
                        placeholder="e.g. Lifestyle, Beauty, Gaming"
                        required
                      />
                    </div>
                    {renderErrorMessage(getFieldError('creator_profile', 'content_style'))}
                  </div>
                </div>
              </div>

              <div>
                <h2 className="text-xl font-semibold text-gray-800 mb-4 flex items-center gap-2">
                  <span className="bg-indigo-100 p-1.5 rounded-md">
                    <FiTarget className="h-5 w-5 text-indigo-600" />
                  </span>
                  Campaign Brief
                </h2>
                <div className="space-y-4">
                  <div>
                    <label htmlFor="brandName" className="block text-sm font-medium text-gray-700 mb-1">
                      Brand Name
                    </label>
                    <div className="relative">
                      <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                        <FiBarChart className="h-4 w-4 text-gray-400" />
                      </div>
                      <input
                        type="text"
                        id="brandName"
                        value={formData.campaign_brief.brand_name}
                        onChange={(e) =>
                          handleInputChange(
                            "campaign_brief",
                            "brand_name",
                            e.target.value
                          )
                        }
                        className={`w-full pl-10 px-4 py-2.5 border rounded-lg shadow-sm hover:bg-white focus:bg-white transition-all duration-200 focus:outline-none focus:ring-2 ${
                          getFieldError('campaign_brief', 'brand_name')
                            ? 'border-rose-500 bg-rose-50 focus:border-rose-500 focus:ring-rose-500'
                            : 'border-gray-200 bg-gray-50 focus:border-indigo-500 focus:ring-indigo-500'
                        }`}
                        placeholder="e.g. Acme Corporation"
                        required
                      />
                    </div>
                    {renderErrorMessage(getFieldError('campaign_brief', 'brand_name'))}
                  </div>
                  <div>
                    <label htmlFor="campaignName" className="block text-sm font-medium text-gray-700 mb-1">
                      Campaign Name
                    </label>
                    <div className="relative">
                      <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                        <FiType className="h-4 w-4 text-gray-400" />
                      </div>
                      <input
                        type="text"
                        id="campaignName"
                        value={formData.campaign_brief.campaign_name}
                        onChange={(e) =>
                          handleInputChange(
                            "campaign_brief",
                            "campaign_name",
                            e.target.value
                          )
                        }
                        className={`w-full pl-10 px-4 py-2.5 border rounded-lg shadow-sm hover:bg-white focus:bg-white transition-all duration-200 focus:outline-none focus:ring-2 ${
                          getFieldError('campaign_brief', 'campaign_name')
                            ? 'border-rose-500 bg-rose-50 focus:border-rose-500 focus:ring-rose-500'
                            : 'border-gray-200 bg-gray-50 focus:border-indigo-500 focus:ring-indigo-500'
                        }`}
                        placeholder="e.g. Summer Collection Launch"
                        required
                      />
                    </div>
                    {renderErrorMessage(getFieldError('campaign_brief', 'campaign_name'))}
                  </div>
                  <div>
                    <label htmlFor="goal" className="block text-sm font-medium text-gray-700 mb-1">
                      Campaign Goal
                    </label>
                    <div className="relative">
                      <div className="absolute top-3 left-0 pl-3 flex items-start pointer-events-none">
                        <FiTarget className="h-4 w-4 text-gray-400" />
                      </div>
                      <textarea
                        id="goal"
                        value={formData.campaign_brief.goal}
                        onChange={(e) =>
                          handleInputChange(
                            "campaign_brief",
                            "goal",
                            e.target.value
                          )
                        }
                        className={`w-full pl-10 px-4 py-3 border rounded-lg shadow-sm hover:bg-white focus:bg-white transition-all duration-200 focus:outline-none focus:ring-2 ${
                          getFieldError('campaign_brief', 'goal')
                            ? 'border-rose-500 bg-rose-50 focus:border-rose-500 focus:ring-rose-500'
                            : 'border-gray-200 bg-gray-50 focus:border-indigo-500 focus:ring-indigo-500'
                        }`}
                        placeholder="Describe the main goals of your campaign..."
                        rows={3}
                        required
                      ></textarea>
                    </div>
                    {renderErrorMessage(getFieldError('campaign_brief', 'goal'))}
                  </div>
                </div>
              </div>

              <div>
                <h2 className="text-xl font-semibold text-gray-800 mb-4 flex items-center gap-2">
                  <span className="bg-indigo-100 p-1.5 rounded-md">
                    <FiType className="h-5 w-5 text-indigo-600" />
                  </span>
                  Message Type
                </h2>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                  <label className={`flex items-center p-3.5 rounded-lg border shadow-sm transition-all duration-200 ${
                    formData.message_type === "initial_outreach"
                      ? "border-indigo-500 bg-gradient-to-r from-indigo-50 to-purple-50 shadow-md"
                      : "border-gray-200 bg-gray-50 hover:bg-white hover:border-indigo-300 hover:shadow"
                  } cursor-pointer`}>
                    <input
                      type="radio"
                      name="messageType"
                      value="initial_outreach"
                      checked={formData.message_type === "initial_outreach"}
                      onChange={() =>
                        setFormData({
                          ...formData,
                          message_type: "initial_outreach",
                        })
                      }
                      className="sr-only"
                    />
                    <span className={`flex h-6 w-6 rounded-full border ${
                      formData.message_type === "initial_outreach"
                        ? "border-indigo-600"
                        : "border-gray-300"
                    } items-center justify-center mr-3`}>
                      {formData.message_type === "initial_outreach" && (
                        <span className="h-3 w-3 rounded-full bg-indigo-600" />
                      )}
                    </span>
                    <div>
                      <span className="block text-sm font-medium">
                        Initial Outreach
                      </span>
                      <span className="block text-xs text-gray-500 mt-0.5">
                        First contact
                      </span>
                    </div>
                  </label>
                  
                  <label className={`flex items-center p-3.5 rounded-lg border shadow-sm transition-all duration-200 ${
                    formData.message_type === "follow_up"
                      ? "border-indigo-500 bg-gradient-to-r from-indigo-50 to-purple-50 shadow-md"
                      : "border-gray-200 bg-gray-50 hover:bg-white hover:border-indigo-300 hover:shadow"
                  } cursor-pointer`}>
                    <input
                      type="radio"
                      name="messageType"
                      value="follow_up"
                      checked={formData.message_type === "follow_up"}
                      onChange={() =>
                        setFormData({
                          ...formData,
                          message_type: "follow_up",
                        })
                      }
                      className="sr-only"
                    />
                    <span className={`flex h-6 w-6 rounded-full border ${
                      formData.message_type === "follow_up"
                        ? "border-indigo-600"
                        : "border-gray-300"
                    } items-center justify-center mr-3`}>
                      {formData.message_type === "follow_up" && (
                        <span className="h-3 w-3 rounded-full bg-indigo-600" />
                      )}
                    </span>
                    <div>
                      <span className="block text-sm font-medium">Follow Up</span>
                      <span className="block text-xs text-gray-500 mt-0.5">
                        Reminder
                      </span>
                    </div>
                  </label>
                  
                  <label className={`flex items-center p-3.5 rounded-lg border shadow-sm transition-all duration-200 ${
                    formData.message_type === "partnership_proposal"
                      ? "border-indigo-500 bg-gradient-to-r from-indigo-50 to-purple-50 shadow-md"
                      : "border-gray-200 bg-gray-50 hover:bg-white hover:border-indigo-300 hover:shadow"
                  } cursor-pointer`}>
                    <input
                      type="radio"
                      name="messageType"
                      value="partnership_proposal"
                      checked={formData.message_type === "partnership_proposal"}
                      onChange={() =>
                        setFormData({
                          ...formData,
                          message_type: "partnership_proposal",
                        })
                      }
                      className="sr-only"
                    />
                    <span className={`flex h-6 w-6 rounded-full border ${
                      formData.message_type === "partnership_proposal"
                        ? "border-indigo-600"
                        : "border-gray-300"
                    } items-center justify-center mr-3`}>
                      {formData.message_type === "partnership_proposal" && (
                        <span className="h-3 w-3 rounded-full bg-indigo-600" />
                      )}
                    </span>
                    <div>
                      <span className="block text-sm font-medium">
                        Partnership
                      </span>
                      <span className="block text-xs text-gray-500 mt-0.5">
                        Formal proposal
                      </span>
                    </div>
                  </label>
                </div>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full bg-gradient-to-r from-indigo-600 to-indigo-700 text-white py-3.5 px-6 rounded-lg hover:from-indigo-700 hover:to-indigo-800 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:opacity-50 font-medium text-sm transition-all duration-200 shadow-md hover:shadow-lg flex items-center justify-center"
              >
                {loading ? (
                  <>
                    <div className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent"></div>
                    Generating...
                  </>
                ) : (
                  <>
                    <FiSend className="mr-2" />
                    Generate Outreach Message
                  </>
                )}
              </button>
            </form>
          </motion.div>

          {/* Preview Section */}
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: activeTab === "preview" || window.innerWidth >= 768 ? 1 : 0 }}
            className={`${activeTab !== "preview" && "md:block hidden"}`}
          >
            {error && (
              <motion.div 
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                className="bg-rose-50 border border-rose-200 text-rose-700 px-5 py-4 rounded-lg mb-5 shadow-sm flex items-start gap-3"
              >
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-rose-500 flex-shrink-0 mt-0.5" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                </svg>
                <div>
                  <p className="font-medium mb-1">Error</p>
                  <p className="text-sm text-rose-600">{error}</p>
                </div>
              </motion.div>
            )}

            {generatedMessage ? (
              <div className="space-y-6">
                {generatedMessage.suggested_subject && (
                  <motion.div 
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.1 }}
                    className="bg-white shadow-xl rounded-xl p-6 border border-gray-100"
                  >
                    <div className="flex justify-between mb-3">
                      <h3 className="text-sm font-medium text-gray-700 flex items-center gap-2">
                        <span className="bg-indigo-100 p-1.5 rounded-md">
                          <FiType className="h-4 w-4 text-indigo-600" />
                        </span>
                        Subject Line
                      </h3>
                      <button
                        onClick={() => {
                          navigator.clipboard.writeText(generatedMessage.suggested_subject!);
                          setCopied(true);
                          setTimeout(() => setCopied(false), 2000);
                        }}
                        className="text-xs bg-indigo-50 text-indigo-600 hover:bg-indigo-100 hover:text-indigo-800 transition-all duration-200 px-2.5 py-1.5 rounded-md flex items-center gap-1.5 shadow-sm"
                      >
                        {copied ? <FiCheck className="h-3.5 w-3.5 text-green-600" /> : <FiCopy className="h-3.5 w-3.5" />}
                        {copied ? 'Copied!' : 'Copy'}
                      </button>
                    </div>
                    <div className="bg-gray-50 p-3 rounded-md font-medium text-gray-900 border border-gray-200">
                      {generatedMessage.suggested_subject}
                    </div>
                  </motion.div>
                )}

                <motion.div 
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.2 }}
                  className="bg-white shadow-xl rounded-xl p-6 border border-gray-100"
                >
                  <div className="flex justify-between mb-3">
                    <h3 className="text-sm font-medium text-gray-700 flex items-center gap-2">
                      <span className="bg-indigo-100 p-1.5 rounded-md">
                        <FiMessageSquare className="h-4 w-4 text-indigo-600" />
                      </span>
                      Message Content
                    </h3>
                    <button
                      onClick={handleCopyToClipboard}
                      className="text-xs bg-indigo-50 text-indigo-600 hover:bg-indigo-100 hover:text-indigo-800 transition-all duration-200 px-2.5 py-1.5 rounded-md flex items-center gap-1.5 shadow-sm"
                    >
                      {copied ? <FiCheck className="h-3.5 w-3.5 text-green-600" /> : <FiCopy className="h-3.5 w-3.5" />}
                      {copied ? "Copied!" : "Copy"}
                    </button>
                  </div>
                  <div className="bg-gray-50 p-6 rounded-lg whitespace-pre-wrap text-gray-900 border border-gray-200 hover:border-indigo-200 transition-colors shadow-sm">
                    {generatedMessage.message}
                  </div>
                </motion.div>

                {generatedMessage.personalization_notes && (
                  <motion.div 
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.3 }}
                    className="bg-white shadow-xl rounded-xl p-6 border border-gray-100"
                  >
                    <div className="flex items-center gap-2 mb-3">
                      <span className="bg-indigo-100 p-1.5 rounded-md">
                        <FiEdit className="h-4 w-4 text-indigo-600" />
                      </span>
                      <h3 className="text-sm font-medium text-gray-700">
                        Personalization Notes
                      </h3>
                    </div>
                    <ul className="space-y-3">
                      {generatedMessage.personalization_notes.map(
                        (note, index) => (
                          <li key={index} className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg border border-gray-200 hover:border-indigo-200 transition-colors shadow-sm">
                            <span className="inline-block h-6 w-6 rounded-full bg-gradient-to-r from-indigo-500 to-purple-500 text-white flex items-center justify-center text-xs font-medium shadow-sm">{index + 1}</span>
                            <span className="text-sm text-gray-700">{note}</span>
                          </li>
                        )
                      )}
                    </ul>
                  </motion.div>
                )}

                <motion.div 
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 0.4 }}
                  className="mt-6 flex justify-between items-center pt-4 border-t border-gray-100"
                >
                  <div className="text-sm text-gray-500">
                    Message type: <span className="font-medium text-gray-700 capitalize">{formData.message_type.replace("_", " ")}</span>
                  </div>
                  <div className="flex space-x-2">
                    <button
                      onClick={() => setActiveTab("form")}  
                      className="md:hidden text-sm text-gray-600 hover:text-gray-900 px-3 py-1 rounded border border-gray-200 hover:border-gray-300 transition-colors"
                    >
                      Edit
                    </button>
                    
                    <button
                      onClick={handleCopyToClipboard}
                      className="text-sm text-indigo-600 hover:text-indigo-800 flex items-center gap-1 px-3 py-1 rounded border border-indigo-200 hover:border-indigo-300 transition-colors"
                    >
                      <FiCopy className="h-4 w-4" />
                      {copied ? "Copied!" : "Copy All"}
                    </button>
                  </div>
                </motion.div>
              </div>
            ) : (
              <div className="text-gray-500 text-center py-12 flex flex-col items-center justify-center h-64 bg-white shadow-xl rounded-xl p-6 border border-gray-100">
                {loading ? (
                  <div className="flex flex-col items-center space-y-4">
                    <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-indigo-600"></div>
                    <p className="text-indigo-600 font-medium">Crafting your perfect outreach message...</p>
                  </div>
                ) : (
                  <>
                    <FiMessageSquare className="h-12 w-12 text-gray-300 mb-4" />
                    <p className="mb-2 text-lg font-medium text-gray-600">Ready to create your outreach</p>
                    <p className="max-w-sm text-gray-500">Fill out the form and generate a personalized outreach message to connect with your target creators</p>
                    <button 
                      onClick={() => setActiveTab("form")} 
                      className="mt-6 px-4 py-2 text-sm text-indigo-600 bg-indigo-50 rounded-md hover:bg-indigo-100 transition-colors md:hidden"
                    >
                      Go to Form
                    </button>
                  </>
                )}
              </div>
            )}
          </motion.div>
        </div>
      </div>
    </div>
  );
}
