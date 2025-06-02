"use client";

import { useState } from "react";
import { motion } from "framer-motion";

interface CreatorProfile {
  name: string;
  platform: string;
  followers: number | string;
}

interface CampaignBrief {
  brand_name: string;
  campaign_name: string;
  goal: string;
}

interface BrandConstraints {
  max_budget: number | string;
}

interface NegotiationStartRequest {
  creator_profile: CreatorProfile;
  campaign_brief: CampaignBrief;
  brand_constraints: BrandConstraints;
}

interface NegotiationResponseRequest {
  negotiation_id: string;
  creator_response: {
    message: string;
  };
  creator_profile: CreatorProfile;
  campaign_brief: CampaignBrief;
  brand_constraints: BrandConstraints;
}

interface NegotiationResponse {
  response_message: string;
  suggested_actions: string[];
  negotiation_status: "pending" | "accepted" | "rejected" | "counter_offer";
  next_steps?: string[];
}

export default function NegotiationPage() {
  // Tab state
  const [activeTab, setActiveTab] = useState<"start" | "respond">("start");

  // Form states
  const [startFormData, setStartFormData] = useState<NegotiationStartRequest>({
    creator_profile: {
      name: "",
      platform: "",
      followers: "", // This is allowed now that we've updated the interface
    },
    campaign_brief: {
      brand_name: "",
      campaign_name: "",
      goal: "",
    },
    brand_constraints: {
      max_budget: "", // This is allowed now that we've updated the interface
    },
  });

  const [respondFormData, setRespondFormData] = useState<NegotiationResponseRequest>({
    negotiation_id: "",
    creator_response: {
      message: "",
    },
    creator_profile: {
      name: "",
      platform: "",
      followers: "", // This is allowed now that we've updated the interface
    },
    campaign_brief: {
      brand_name: "",
      campaign_name: "",
      goal: "",
    },
    brand_constraints: {
      max_budget: "", // This is allowed now that we've updated the interface
    },
  });

  // Response states
  const [negotiationResponse, setNegotiationResponse] = useState<NegotiationResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [formErrors, setFormErrors] = useState<{
    start: Record<string, string>;
    respond: Record<string, string>;
  }>({
    start: {},
    respond: {},
  });

  const [formSubmitted, setFormSubmitted] = useState(false);

  type StartFormSection = keyof NegotiationStartRequest;
  type RespondFormSection = keyof NegotiationResponseRequest;

  type FormFieldValue = string | number;
  type FormSection = Record<string, FormFieldValue>;

  const validateStartForm = () => {
    const errors: Record<string, string> = {};
    const { creator_profile, campaign_brief, brand_constraints } = startFormData;
    
    // Validate creator profile
    if (!creator_profile.name) errors['creator_profile.name'] = 'Creator name is required';
    if (!creator_profile.platform) errors['creator_profile.platform'] = 'Platform is required';
    if (!creator_profile.followers) errors['creator_profile.followers'] = 'Follower count is required';
    
    // Validate campaign brief
    if (!campaign_brief.brand_name) errors['campaign_brief.brand_name'] = 'Brand name is required';
    if (!campaign_brief.campaign_name) errors['campaign_brief.campaign_name'] = 'Campaign name is required';
    if (!campaign_brief.goal) errors['campaign_brief.goal'] = 'Campaign goal is required';
    
    // Validate brand constraints
    if (!brand_constraints.max_budget) errors['brand_constraints.max_budget'] = 'Budget is required';
    
    return errors;
  };
  
  const validateRespondForm = () => {
    const errors: Record<string, string> = {};
    const { creator_profile, campaign_brief, brand_constraints, negotiation_id, creator_response } = respondFormData;
    
    // Validate negotiation ID
    if (!negotiation_id) errors['negotiation_id'] = 'Negotiation ID is required';
    
    // Validate creator response
    if (!creator_response.message) errors['creator_response.message'] = 'Response message is required';
    
    // Validate creator profile
    if (!creator_profile.name) errors['creator_profile.name'] = 'Creator name is required';
    if (!creator_profile.platform) errors['creator_profile.platform'] = 'Platform is required';
    if (!creator_profile.followers) errors['creator_profile.followers'] = 'Follower count is required';
    
    // Validate campaign brief
    if (!campaign_brief.brand_name) errors['campaign_brief.brand_name'] = 'Brand name is required';
    if (!campaign_brief.campaign_name) errors['campaign_brief.campaign_name'] = 'Campaign name is required';
    if (!campaign_brief.goal) errors['campaign_brief.goal'] = 'Campaign goal is required';
    
    // Validate brand constraints
    if (!brand_constraints.max_budget) errors['brand_constraints.max_budget'] = 'Budget is required';
    
    return errors;
  };

  const handleStartNegotiation = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormSubmitted(true);
    
    // Validate form
    const validationErrors = validateStartForm();
    setFormErrors(prev => ({ ...prev, start: validationErrors }));
    
    // If there are errors, don't submit
    if (Object.keys(validationErrors).length > 0) {
      return;
    }
    
    setLoading(true);
    setError(null);

    try {
      const response = await fetch("http://localhost:8000/negotiation/start", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(startFormData),
      });

      if (!response.ok) {
        throw new Error("Failed to start negotiation");
      }

      const data = await response.json();
      setNegotiationResponse(data);
      setFormSubmitted(false); // Reset form submitted state after successful submission
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setLoading(false);
    }
  };

  const handleRespondToNegotiation = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormSubmitted(true);
    
    // Validate form
    const validationErrors = validateRespondForm();
    setFormErrors(prev => ({ ...prev, respond: validationErrors }));
    
    // If there are errors, don't submit
    if (Object.keys(validationErrors).length > 0) {
      return;
    }
    
    setLoading(true);
    setError(null);

    try {
      const response = await fetch("http://localhost:8000/negotiation/respond", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(respondFormData),
      });

      if (!response.ok) {
        throw new Error("Failed to respond to negotiation");
      }

      const data = await response.json();
      setNegotiationResponse(data);
      setFormSubmitted(false); // Reset form submitted state after successful submission
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (
    form: "start" | "respond",
    section: StartFormSection | RespondFormSection,
    field: string,
    value: FormFieldValue
  ) => {
    // Reset error for this field when user types
    if (formSubmitted) {
      setFormErrors((prev) => {
        const newErrors = { ...prev };
        const errorKey = `${section}.${field}`;
        if (newErrors[form][errorKey]) {
          delete newErrors[form][errorKey];
        }
        return newErrors;
      });
    }

    if (form === "start") {
      setStartFormData((prev) => ({
        ...prev,
        [section]: {
          ...prev[section as StartFormSection] as unknown as Record<string, FormFieldValue>,
          [field]: value,
        },
      }));
    } else {
      setRespondFormData((prev) => ({
        ...prev,
        [section]: {
          ...prev[section as RespondFormSection] as unknown as Record<string, FormFieldValue>,
          [field]: value,
        },
      }));
    }
  };

  // Helper function to get field error
  const getFieldError = (form: "start" | "respond", section: string, field: string) => {
    const errorKey = `${section}.${field}`;
    return formSubmitted ? formErrors[form][errorKey] : undefined;
  };

  // Helper function to render error message
  const renderErrorMessage = (error?: string) => {
    if (!error) return null;

    return (
      <p className="mt-1 text-sm text-rose-600 flex items-center">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="w-3.5 h-3.5 mr-1 flex-shrink-0">
          <path fillRule="evenodd" d="M10 18a8 8 0 1 0 0-16 8 8 0 0 0 0 16ZM8.28 7.22a.75.75 0 0 0-1.06 1.06L8.94 10l-1.72 1.72a.75.75 0 1 0 1.06 1.06L10 11.06l1.72 1.72a.75.75 0 1 0 1.06-1.06L11.06 10l1.72-1.72a.75.75 0 0 0-1.06-1.06L10 8.94 8.28 7.22Z" clipRule="evenodd" />
        </svg>
        {error}
      </p>
    );
  };

  return (
    <div className="py-8 bg-gradient-to-b from-gray-50 to-white min-h-screen">
      <div className="container mx-auto px-4 max-w-7xl">
        <motion.div 
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="mb-8"
        >
          <div className="flex items-center space-x-3 mb-2">
            <div className="h-8 w-8 rounded-full bg-gradient-to-br from-indigo-500 to-pink-500 flex items-center justify-center shadow-md">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-4 h-4 text-white">
                <path d="M10.5 1.875a1.125 1.125 0 0 1 2.25 0v8.219c.517.384.975.892 1.307 1.486a.75.75 0 0 1-.122.847l-3.236 3.236a.75.75 0 0 1-1.06 0l-3.236-3.236a.75.75 0 0 1-.122-.847c.332-.594.79-1.102 1.307-1.486V1.875Z" />
                <path d="M15.75 15a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z" />
              </svg>
            </div>
            <h1 className="text-3xl font-bold text-gray-900 tracking-tight">Negotiation Hub</h1>
          </div>
          <p className="mt-1 text-gray-600 ml-11">Create and manage influencer collaborations with AI-powered negotiation</p>
        </motion.div>

        {/* Tab Navigation */}
        <div className="bg-white shadow-lg rounded-xl mb-8 p-1.5 flex border border-gray-100">
          <button
            onClick={() => setActiveTab("start")}
            className={`flex-1 text-center py-3.5 px-4 rounded-lg transition-all duration-200 flex items-center justify-center gap-2 ${
              activeTab === "start"
                ? "bg-gradient-to-r from-indigo-50 to-pink-50 text-indigo-700 shadow-sm"
                : "text-gray-600 hover:text-gray-900 hover:bg-gray-50"
            }`}
          >
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-5 h-5">
              <path fillRule="evenodd" d="M12 2.25c-5.385 0-9.75 4.365-9.75 9.75s4.365 9.75 9.75 9.75 9.75-4.365 9.75-9.75S17.385 2.25 12 2.25ZM12.75 9a.75.75 0 0 0-1.5 0v2.25H9a.75.75 0 0 0 0 1.5h2.25V15a.75.75 0 0 0 1.5 0v-2.25H15a.75.75 0 0 0 0-1.5h-2.25V9Z" clipRule="evenodd" />
            </svg>
            <span className="font-medium">Start Negotiation</span>
          </button>
          <button
            onClick={() => setActiveTab("respond")}
            className={`flex-1 text-center py-3.5 px-4 rounded-lg transition-all duration-200 flex items-center justify-center gap-2 ${
              activeTab === "respond"
                ? "bg-gradient-to-r from-indigo-50 to-pink-50 text-indigo-700 shadow-sm"
                : "text-gray-600 hover:text-gray-900 hover:bg-gray-50"
            }`}
          >
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-5 h-5">
              <path fillRule="evenodd" d="M4.848 2.771A49.144 49.144 0 0 1 12 2.25c2.43 0 4.817.178 7.152.52 1.978.292 3.348 2.024 3.348 3.97v6.02c0 1.946-1.37 3.678-3.348 3.97a48.901 48.901 0 0 1-3.476.383.39.39 0 0 0-.297.17l-2.755 4.133a.75.75 0 0 1-1.248 0l-2.755-4.133a.39.39 0 0 0-.297-.17 48.9 48.9 0 0 1-3.476-.384c-1.978-.29-3.348-2.024-3.348-3.97V6.741c0-1.946 1.37-3.68 3.348-3.97ZM6.75 8.25a.75.75 0 0 1 .75-.75h9a.75.75 0 0 1 0 1.5h-9a.75.75 0 0 1-.75-.75Zm.75 2.25a.75.75 0 0 0 0 1.5H12a.75.75 0 0 0 0-1.5H7.5Z" clipRule="evenodd" />
            </svg>
            <span className="font-medium">Respond to Negotiation</span>
          </button>
        </div>

        <div className="grid lg:grid-cols-2 gap-8">
          {/* Form Section */}
          <div>
            {activeTab === "start" ? (
              <motion.form 
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 0.3 }}
                onSubmit={handleStartNegotiation} 
                className="bg-white shadow-xl rounded-xl p-8 border border-gray-100 space-y-6 relative overflow-hidden"
              >
                <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-indigo-500 to-pink-500"></div>
                <h2 className="text-xl font-semibold text-gray-800 mb-4">
                  Start a New Negotiation
                </h2>
                
                <div className="space-y-5">
                  <h3 className="text-lg font-medium text-gray-700 flex items-center gap-2">
                    <span className="inline-flex items-center justify-center h-6 w-6 rounded-full bg-indigo-100 text-indigo-800 text-sm font-medium">
                      1
                    </span>
                    Creator Profile
                  </h3>
                  <div className="space-y-4 pl-8">
                    <div>
                      <label
                        htmlFor="creator-name"
                        className="block text-sm font-medium text-gray-700 mb-1"
                      >
                        Creator Name
                      </label>
                      <input
                        type="text"
                        id="creator-name"
                        value={startFormData.creator_profile.name}
                        onChange={(e) =>
                          handleInputChange(
                            "start",
                            "creator_profile",
                            "name",
                            e.target.value
                          )
                        }
                        className={`w-full px-4 py-2.5 border rounded-lg transition-all duration-200 bg-gray-50 hover:bg-white focus:bg-white shadow-sm ${getFieldError("start", "creator_profile", "name") 
                          ? "border-rose-300 focus:ring-2 focus:ring-rose-500 focus:border-rose-500 bg-rose-50" 
                          : "border-gray-200 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"}`}
                        placeholder="e.g. Sarah Smith"
                      />
                      {renderErrorMessage(getFieldError("start", "creator_profile", "name"))}
                    </div>
                    <div>
                      <label
                        htmlFor="creator-platform"
                        className="block text-sm font-medium text-gray-700 mb-1"
                      >
                        Platform
                      </label>
                      <select
                        id="creator-platform"
                        value={startFormData.creator_profile.platform}
                        onChange={(e) =>
                          handleInputChange(
                            "start",
                            "creator_profile",
                            "platform",
                            e.target.value
                          )
                        }
                        className={`w-full px-4 py-2.5 border rounded-lg transition-all duration-200 bg-gray-50 hover:bg-white focus:bg-white shadow-sm ${getFieldError("start", "creator_profile", "platform") 
                          ? "border-rose-300 focus:ring-2 focus:ring-rose-500 focus:border-rose-500 bg-rose-50" 
                          : "border-gray-200 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"}`}
                      >
                        <option value="">Select a platform</option>
                        <option value="instagram">Instagram</option>
                        <option value="youtube">YouTube</option>
                        <option value="tiktok">TikTok</option>
                        <option value="twitter">Twitter</option>
                      </select>
                      {renderErrorMessage(getFieldError("start", "creator_profile", "platform"))}
                    </div>
                    <div>
                      <label
                        htmlFor="creator-followers"
                        className="block text-sm font-medium text-gray-700 mb-1"
                      >
                        Followers Count
                      </label>
                      <input
                        type="number"
                        id="creator-followers"
                        value={startFormData.creator_profile.followers}
                        onChange={(e) =>
                          handleInputChange(
                            "start",
                            "creator_profile",
                            "followers",
                            e.target.value === '' ? '' : parseInt(e.target.value) || 0
                          )
                        }
                        className={`w-full px-4 py-2.5 border rounded-lg transition-all duration-200 bg-gray-50 hover:bg-white focus:bg-white shadow-sm ${getFieldError("start", "creator_profile", "followers") 
                          ? "border-rose-300 focus:ring-2 focus:ring-rose-500 focus:border-rose-500 bg-rose-50" 
                          : "border-gray-200 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"}`}
                        placeholder="e.g. 50000"
                        min="0"
                      />
                      {renderErrorMessage(getFieldError("start", "creator_profile", "followers"))}
                    </div>
                  </div>
                </div>

                <div className="space-y-5">
                  <h3 className="text-lg font-medium text-gray-700 flex items-center gap-2">
                    <span className="inline-flex items-center justify-center h-6 w-6 rounded-full bg-indigo-100 text-indigo-800 text-sm font-medium">
                      2
                    </span>
                    Campaign Brief
                  </h3>
                  <div className="space-y-4 pl-8">
                    <div>
                      <label
                        htmlFor="brand-name"
                        className="block text-sm font-medium text-gray-700 mb-1"
                      >
                        Brand Name
                      </label>
                      <input
                        type="text"
                        id="brand-name"
                        value={startFormData.campaign_brief.brand_name}
                        onChange={(e) =>
                          handleInputChange(
                            "start",
                            "campaign_brief",
                            "brand_name",
                            e.target.value
                          )
                        }
                        className={`w-full px-4 py-2.5 border rounded-lg transition-all duration-200 bg-gray-50 hover:bg-white focus:bg-white shadow-sm ${getFieldError("start", "campaign_brief", "brand_name") 
                          ? "border-rose-300 focus:ring-2 focus:ring-rose-500 focus:border-rose-500 bg-rose-50" 
                          : "border-gray-200 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"}`}
                        placeholder="e.g. Eco Cosmetics"
                      />
                      {renderErrorMessage(getFieldError("start", "campaign_brief", "brand_name"))}
                    </div>
                    <div>
                      <label
                        htmlFor="campaign-name"
                        className="block text-sm font-medium text-gray-700 mb-1"
                      >
                        Campaign Name
                      </label>
                      <input
                        type="text"
                        id="campaign-name"
                        value={startFormData.campaign_brief.campaign_name}
                        onChange={(e) =>
                          handleInputChange(
                            "start",
                            "campaign_brief",
                            "campaign_name",
                            e.target.value
                          )
                        }
                        className={`w-full px-4 py-2.5 border rounded-lg transition-all duration-200 bg-gray-50 hover:bg-white focus:bg-white shadow-sm ${getFieldError("start", "campaign_brief", "campaign_name") 
                          ? "border-rose-300 focus:ring-2 focus:ring-rose-500 focus:border-rose-500 bg-rose-50" 
                          : "border-gray-200 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"}`}
                        placeholder="e.g. Summer Collection Launch"
                      />
                      {renderErrorMessage(getFieldError("start", "campaign_brief", "campaign_name"))}
                    </div>
                    <div>
                      <label
                        htmlFor="campaign-goal"
                        className="block text-sm font-medium text-gray-700 mb-1"
                      >
                        Campaign Goal
                      </label>
                      <select
                        id="campaign-goal"
                        value={startFormData.campaign_brief.goal}
                        onChange={(e) =>
                          handleInputChange(
                            "start",
                            "campaign_brief",
                            "goal",
                            e.target.value
                          )
                        }
                        className={`w-full px-4 py-2.5 border rounded-lg transition-all duration-200 bg-gray-50 hover:bg-white focus:bg-white shadow-sm ${getFieldError("start", "campaign_brief", "goal") 
                          ? "border-rose-300 focus:ring-2 focus:ring-rose-500 focus:border-rose-500 bg-rose-50" 
                          : "border-gray-200 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"}`}
                      >
                        <option value="">Select Goal</option>
                        <option value="Brand Awareness">Brand Awareness</option>
                        <option value="Product Launch">Product Launch</option>
                        <option value="Sales">Sales</option>
                        <option value="Engagement">Engagement</option>
                        <option value="Community Building">Community Building</option>
                      </select>
                      {renderErrorMessage(getFieldError("start", "campaign_brief", "goal"))}
                    </div>
                  </div>
                </div>

                <div className="space-y-5">
                  <h3 className="text-lg font-medium text-gray-700 flex items-center gap-2">
                    <span className="inline-flex items-center justify-center h-6 w-6 rounded-full bg-indigo-100 text-indigo-800 text-sm font-medium">
                      3
                    </span>
                    Budget Constraints
                  </h3>
                  <div className="space-y-4 pl-8">
                    <div>
                      <label
                        htmlFor="max-budget"
                        className="block text-sm font-medium text-gray-700 mb-1"
                      >
                        Maximum Budget ($)
                      </label>
                      <input
                        type="number"
                        id="max-budget"
                        value={startFormData.brand_constraints.max_budget}
                        onChange={(e) =>
                          handleInputChange(
                            "start",
                            "brand_constraints",
                            "max_budget",
                            e.target.value === '' ? '' : parseInt(e.target.value) || 0
                          )
                        }
                        className={`w-full px-4 py-2.5 border rounded-lg transition-all duration-200 bg-gray-50 hover:bg-white focus:bg-white shadow-sm ${getFieldError("start", "brand_constraints", "max_budget") 
                          ? "border-rose-300 focus:ring-2 focus:ring-rose-500 focus:border-rose-500 bg-rose-50" 
                          : "border-gray-200 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"}`}
                        min="0"
                      />
                      {renderErrorMessage(getFieldError("start", "brand_constraints", "max_budget"))}
                    </div>
                  </div>
                </div>

                <button
                  type="submit"
                  disabled={loading}
                  className="w-full bg-gradient-to-r from-indigo-600 to-indigo-700 text-white py-3.5 px-6 rounded-lg hover:from-indigo-700 hover:to-indigo-800 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:opacity-50 font-medium text-sm transition-all duration-200 shadow-md hover:shadow-lg flex items-center justify-center relative overflow-hidden group"
                >
                  <span className="absolute right-0 top-0 h-full w-12 translate-x-12 transform bg-white opacity-10 transition-all duration-1000 group-hover:translate-x-[-180px]"></span>
                  {loading ? (
                    <>
                      <div className="mr-2 h-5 w-5 animate-spin rounded-full border-2 border-white border-t-transparent"></div>
                      <span>Initiating Negotiation...</span>
                    </>
                  ) : (
                    <>
                      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-5 h-5 mr-2">
                        <path fillRule="evenodd" d="M12 2.25c-5.385 0-9.75 4.365-9.75 9.75s4.365 9.75 9.75 9.75 9.75-4.365 9.75-9.75S17.385 2.25 12 2.25ZM12.75 9a.75.75 0 0 0-1.5 0v2.25H9a.75.75 0 0 0 0 1.5h2.25V15a.75.75 0 0 0 1.5 0v-2.25H15a.75.75 0 0 0 0-1.5h-2.25V9Z" clipRule="evenodd" />
                      </svg>
                      <span>Start Negotiation</span>
                    </>
                  )}
                </button>
              </motion.form>
            ) : (
              <motion.form 
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 0.3 }}
                onSubmit={handleRespondToNegotiation} 
                className="bg-white shadow-xl rounded-xl p-8 border border-gray-100 space-y-6 relative overflow-hidden"
              >
                <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-indigo-500 to-pink-500"></div>
                <h2 className="text-xl font-semibold text-gray-800 mb-4">
                  Respond to a Negotiation
                </h2>

                <div className="space-y-4">
                  <div>
                    <label
                      htmlFor="negotiation-id"
                      className="block text-sm font-medium text-gray-700 mb-1"
                    >
                      Negotiation ID
                    </label>
                    <input
                      type="text"
                      id="negotiation-id"
                      value={respondFormData.negotiation_id}
                      onChange={(e) =>
                        handleInputChange(
                          "respond",
                          "negotiation_id",
                          "",
                          e.target.value
                        )
                      }
                      className={`w-full px-4 py-2.5 border rounded-lg transition-all duration-200 bg-gray-50 hover:bg-white focus:bg-white shadow-sm ${getFieldError("respond", "negotiation_id", "") 
                        ? "border-rose-300 focus:ring-2 focus:ring-rose-500 focus:border-rose-500 bg-rose-50" 
                        : "border-gray-200 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"}`}
                      placeholder="Enter the negotiation ID"
                    />
                    {renderErrorMessage(getFieldError("respond", "negotiation_id", ""))}
                  </div>

                  <div>
                    <label
                      htmlFor="response-message"
                      className="block text-sm font-medium text-gray-700 mb-1"
                    >
                      Your Response
                    </label>
                    <textarea
                      id="response-message"
                      value={respondFormData.creator_response.message}
                      onChange={(e) =>
                        handleInputChange(
                          "respond",
                          "creator_response",
                          "message",
                          e.target.value
                        )
                      }
                      className={`w-full px-4 py-2.5 border rounded-lg transition-all duration-200 bg-gray-50 hover:bg-white focus:bg-white shadow-sm h-32 ${getFieldError("respond", "creator_response", "message") 
                        ? "border-rose-300 focus:ring-2 focus:ring-rose-500 focus:border-rose-500 bg-rose-50" 
                        : "border-gray-200 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"}`}
                      placeholder="Write your response to the negotiation"
                    />
                    {renderErrorMessage(getFieldError("respond", "creator_response", "message"))}
                  </div>
                </div>

                <div className="space-y-5">
                  <h3 className="text-lg font-medium text-gray-700 mb-2">
                    Creator Profile
                  </h3>
                  <div className="space-y-4 pl-4">
                    <div>
                      <label
                        htmlFor="respond-creator-name"
                        className="block text-sm font-medium text-gray-700 mb-1"
                      >
                        Creator Name
                      </label>
                      <input
                        type="text"
                        id="respond-creator-name"
                        value={respondFormData.creator_profile.name}
                        onChange={(e) =>
                          handleInputChange(
                            "respond",
                            "creator_profile",
                            "name",
                            e.target.value
                          )
                        }
                        className={`w-full px-4 py-2.5 border rounded-lg transition-all duration-200 bg-gray-50 hover:bg-white focus:bg-white shadow-sm ${getFieldError("respond", "creator_profile", "name") 
                          ? "border-rose-300 focus:ring-2 focus:ring-rose-500 focus:border-rose-500 bg-rose-50" 
                          : "border-gray-200 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"}`}
                        placeholder="e.g. Sarah Smith"
                      />
                      {renderErrorMessage(getFieldError("respond", "creator_profile", "name"))}
                    </div>
                    <div>
                      <label
                        htmlFor="respond-platform"
                        className="block text-sm font-medium text-gray-700 mb-1"
                      >
                        Platform
                      </label>
                      <select
                        id="respond-platform"
                        value={respondFormData.creator_profile.platform}
                        onChange={(e) =>
                          handleInputChange(
                            "respond",
                            "creator_profile",
                            "platform",
                            e.target.value
                          )
                        }
                        className={`w-full px-4 py-2.5 border rounded-lg transition-all duration-200 bg-gray-50 hover:bg-white focus:bg-white shadow-sm ${getFieldError("respond", "creator_profile", "platform") 
                          ? "border-rose-300 focus:ring-2 focus:ring-rose-500 focus:border-rose-500 bg-rose-50" 
                          : "border-gray-200 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"}`}
                      >
                        <option value="">Select Platform</option>
                        <option value="instagram">Instagram</option>
                        <option value="youtube">YouTube</option>
                        <option value="tiktok">TikTok</option>
                        <option value="twitter">Twitter</option>
                        <option value="twitch">Twitch</option>
                      </select>
                      {renderErrorMessage(getFieldError("respond", "creator_profile", "platform"))}
                    </div>
                    <div>
                      <label
                        htmlFor="respond-creator-followers"
                        className="block text-sm font-medium text-gray-700 mb-1"
                      >
                        Followers Count
                      </label>
                      <input
                        type="number"
                        id="respond-creator-followers"
                        value={respondFormData.creator_profile.followers}
                        onChange={(e) =>
                          handleInputChange(
                            "respond",
                            "creator_profile",
                            "followers",
                            e.target.value === '' ? '' : parseInt(e.target.value) || 0
                          )
                        }
                        className={`w-full px-4 py-2.5 border rounded-lg transition-all duration-200 bg-gray-50 hover:bg-white focus:bg-white shadow-sm ${getFieldError("respond", "creator_profile", "followers") 
                          ? "border-rose-300 focus:ring-2 focus:ring-rose-500 focus:border-rose-500 bg-rose-50" 
                          : "border-gray-200 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"}`}
                        min="0"
                      />
                      {renderErrorMessage(getFieldError("respond", "creator_profile", "followers"))}
                    </div>
                    <div>
                      <label
                        htmlFor="respond-max-budget"
                        className="block text-sm font-medium text-gray-700 mb-1"
                      >
                        Maximum Budget ($)
                      </label>
                      <input
                        type="number"
                        id="respond-max-budget"
                        value={respondFormData.brand_constraints.max_budget}
                        onChange={(e) =>
                          handleInputChange(
                            "respond",
                            "brand_constraints",
                            "max_budget",
                            e.target.value === '' ? '' : parseInt(e.target.value) || 0
                          )
                        }
                        className={`w-full px-4 py-2.5 border rounded-lg transition-all duration-200 bg-gray-50 hover:bg-white focus:bg-white shadow-sm ${getFieldError("respond", "brand_constraints", "max_budget") 
                          ? "border-rose-300 focus:ring-2 focus:ring-rose-500 focus:border-rose-500 bg-rose-50" 
                          : "border-gray-200 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"}`}
                        min="0"
                      />
                      {renderErrorMessage(getFieldError("respond", "brand_constraints", "max_budget"))}
                    </div>
                  </div>
                </div>

                <div className="space-y-5">
                  <h3 className="text-lg font-medium text-gray-700 mb-2">
                    Campaign Brief
                  </h3>
                  <div className="space-y-4 pl-4">
                    <div>
                      <label
                        htmlFor="respond-brand-name"
                        className="block text-sm font-medium text-gray-700 mb-1"
                      >
                        Brand Name
                      </label>
                      <input
                        type="text"
                        id="respond-brand-name"
                        value={respondFormData.campaign_brief.brand_name}
                        onChange={(e) =>
                          handleInputChange(
                            "respond",
                            "campaign_brief",
                            "brand_name",
                            e.target.value
                          )
                        }
                        className={`w-full px-4 py-2.5 border rounded-lg transition-all duration-200 bg-gray-50 hover:bg-white focus:bg-white shadow-sm ${getFieldError("respond", "campaign_brief", "brand_name") 
                          ? "border-rose-300 focus:ring-2 focus:ring-rose-500 focus:border-rose-500 bg-rose-50" 
                          : "border-gray-200 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"}`}
                        placeholder="e.g. Eco Cosmetics"
                      />
                      {renderErrorMessage(getFieldError("respond", "campaign_brief", "brand_name"))}
                    </div>
                    <div>
                      <label
                        htmlFor="respond-campaign-name"
                        className="block text-sm font-medium text-gray-700 mb-1"
                      >
                        Campaign Name
                      </label>
                      <input
                        type="text"
                        id="respond-campaign-name"
                        value={respondFormData.campaign_brief.campaign_name}
                        onChange={(e) =>
                          handleInputChange(
                            "respond",
                            "campaign_brief",
                            "campaign_name",
                            e.target.value
                          )
                        }
                        className={`w-full px-4 py-2.5 border rounded-lg transition-all duration-200 bg-gray-50 hover:bg-white focus:bg-white shadow-sm ${getFieldError("respond", "campaign_brief", "campaign_name") 
                          ? "border-rose-300 focus:ring-2 focus:ring-rose-500 focus:border-rose-500 bg-rose-50" 
                          : "border-gray-200 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"}`}
                        placeholder="e.g. Summer Collection Launch"
                      />
                      {renderErrorMessage(getFieldError("respond", "campaign_brief", "campaign_name"))}
                    </div>
                    <div>
                      <label
                        htmlFor="respond-campaign-goal"
                        className="block text-sm font-medium text-gray-700 mb-1"
                      >
                        Campaign Goal
                      </label>
                      <select
                        id="respond-campaign-goal"
                        value={respondFormData.campaign_brief.goal}
                        onChange={(e) =>
                          handleInputChange(
                            "respond",
                            "campaign_brief",
                            "goal",
                            e.target.value
                          )
                        }
                        className={`w-full px-4 py-2.5 border rounded-lg transition-all duration-200 bg-gray-50 hover:bg-white focus:bg-white shadow-sm ${getFieldError("respond", "campaign_brief", "goal") 
                          ? "border-rose-300 focus:ring-2 focus:ring-rose-500 focus:border-rose-500 bg-rose-50" 
                          : "border-gray-200 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"}`}
                      >
                        <option value="">Select Goal</option>
                        <option value="Brand Awareness">Brand Awareness</option>
                        <option value="Product Launch">Product Launch</option>
                        <option value="Sales">Sales</option>
                        <option value="Engagement">Engagement</option>
                        <option value="Community Building">Community Building</option>
                      </select>
                      {renderErrorMessage(getFieldError("respond", "campaign_brief", "goal"))}
                    </div>
                  </div>
                </div>

                <button
                  type="submit"
                  disabled={loading}
                  className="w-full bg-gradient-to-r from-indigo-600 to-indigo-700 text-white py-3.5 px-6 rounded-lg hover:from-indigo-700 hover:to-indigo-800 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:opacity-50 font-medium text-sm transition-all duration-200 shadow-md hover:shadow-lg flex items-center justify-center relative overflow-hidden group"
                >
                  <span className="absolute right-0 top-0 h-full w-12 translate-x-12 transform bg-white opacity-10 transition-all duration-1000 group-hover:translate-x-[-180px]"></span>
                  {loading ? (
                    <>
                      <div className="mr-2 h-5 w-5 animate-spin rounded-full border-2 border-white border-t-transparent"></div>
                      <span>Processing Response...</span>
                    </>
                  ) : (
                    <>
                      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-5 h-5 mr-2">
                        <path d="M4.913 2.658c2.075-.27 4.19-.408 6.337-.408 2.147 0 4.262.139 6.337.408 1.922.25 3.291 1.861 3.405 3.727a4.403 4.403 0 0 0-1.032-.211 50.89 50.89 0 0 0-8.42 0c-2.358.196-4.04 2.19-4.04 4.434v4.286a4.47 4.47 0 0 0 2.433 3.984L7.28 21.53A.75.75 0 0 1 6 21v-4.03a48.527 48.527 0 0 1-1.087-.128C2.905 16.58 1.5 14.833 1.5 12.862V6.638c0-1.97 1.405-3.718 3.413-3.979Z" />
                        <path d="M15.75 7.5c-1.376 0-2.739.057-4.086.169C10.124 7.797 9 9.103 9 10.609v4.285c0 1.507 1.128 2.814 2.67 2.94 1.243.102 2.5.157 3.768.165l2.782 2.781a.75.75 0 0 0 1.28-.53v-2.39l.33-.026c1.542-.125 2.67-1.433 2.67-2.94v-4.286c0-1.505-1.125-2.811-2.664-2.94A49.392 49.392 0 0 0 15.75 7.5Z" />
                      </svg>
                      <span>Respond to Negotiation</span>
                    </>
                  )}
                </button>
              </motion.form>
            )}
          </div>

          {/* Response Section */}
          <div className="bg-white shadow-xl rounded-xl p-8 border border-gray-100 relative overflow-hidden">
            <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-indigo-500 to-pink-500"></div>
            <div className="flex items-center space-x-3 mb-6">
              <div className="h-8 w-8 rounded-full bg-gradient-to-br from-indigo-400 to-indigo-600 flex items-center justify-center shadow-md">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-4 h-4 text-white">
                  <path fillRule="evenodd" d="M4.848 2.771A49.144 49.144 0 0 1 12 2.25c2.43 0 4.817.178 7.152.52 1.978.292 3.348 2.024 3.348 3.97v6.02c0 1.946-1.37 3.678-3.348 3.97a48.901 48.901 0 0 1-3.476.383.39.39 0 0 0-.297.17l-2.755 4.133a.75.75 0 0 1-1.248 0l-2.755-4.133a.39.39 0 0 0-.297-.17 48.9 48.9 0 0 1-3.476-.384c-1.978-.29-3.348-2.024-3.348-3.97V6.741c0-1.946 1.37-3.68 3.348-3.97Z" clipRule="evenodd" />
                </svg>
              </div>
              <h2 className="text-xl font-semibold text-gray-800">Negotiation Response</h2>
            </div>

            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md mb-4">
                {error}
              </div>
            )}

            {negotiationResponse ? (
              <motion.div 
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 0.3 }}
                className="space-y-6"
              >
                <div className="bg-gradient-to-r from-gray-50 to-white p-6 rounded-lg border border-gray-200 shadow-sm">
                  <div className="flex items-center mb-3">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-5 h-5 text-indigo-600 mr-2">
                      <path fillRule="evenodd" d="M4.804 21.644A6.707 6.707 0 0 0 6 21.75a6.721 6.721 0 0 0 3.583-1.029c.774.182 1.584.279 2.417.279 5.322 0 9.75-3.97 9.75-9 0-5.03-4.428-9-9.75-9s-9.75 3.97-9.75 9c0 2.409 1.025 4.587 2.674 6.192.232.226.277.428.254.543a3.73 3.73 0 0 1-.814 1.686.75.75 0 0 0 .44 1.223ZM8.25 10.875a1.125 1.125 0 1 0 0 2.25 1.125 1.125 0 0 0 0-2.25ZM10.875 12a1.125 1.125 0 1 1 2.25 0 1.125 1.125 0 0 1-2.25 0Zm4.875-1.125a1.125 1.125 0 1 0 0 2.25 1.125 1.125 0 0 0 0-2.25Z" clipRule="evenodd" />
                    </svg>
                    <h3 className="text-sm font-medium text-gray-700">
                      Response Message
                    </h3>
                  </div>
                  <div className="whitespace-pre-wrap text-gray-900 bg-white p-5 rounded-lg shadow-sm border border-gray-100 font-medium leading-relaxed">
                    {negotiationResponse.response_message}
                  </div>
                </div>

                {negotiationResponse.suggested_actions && (
                  <div className="bg-gradient-to-r from-indigo-50 to-indigo-100/50 p-6 rounded-lg border border-indigo-100 shadow-sm">
                    <div className="flex items-center mb-4">
                      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-5 h-5 text-indigo-600 mr-2">
                        <path d="M5.625 3.75a2.625 2.625 0 1 0 0 5.25h12.75a2.625 2.625 0 0 0 0-5.25H5.625ZM3.75 11.25a.75.75 0 0 0 0 1.5h16.5a.75.75 0 0 0 0-1.5H3.75ZM3 15.75a.75.75 0 0 1 .75-.75h16.5a.75.75 0 0 1 0 1.5H3.75a.75.75 0 0 1-.75-.75ZM3.75 18.75a.75.75 0 0 0 0 1.5h16.5a.75.75 0 0 0 0-1.5H3.75Z" />
                      </svg>
                      <h3 className="text-sm font-medium text-indigo-700">
                        Suggested Actions
                      </h3>
                    </div>
                    <ul className="space-y-3">
                      {negotiationResponse.suggested_actions.map(
                        (action, index) => (
                          <li key={index} className="flex items-start gap-3 bg-white p-3 rounded-lg border border-indigo-100 shadow-sm">
                            <span className="inline-block h-6 w-6 rounded-full bg-gradient-to-br from-indigo-500 to-indigo-600 text-white flex items-center justify-center text-xs font-bold mt-0.5">{index + 1}</span>
                            <span className="text-sm text-indigo-900 font-medium">{action}</span>
                          </li>
                        )
                      )}
                    </ul>
                  </div>
                )}

                <div className="mt-6 flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-gray-500 font-medium">STATUS:</span>
                    <span
                      className={`inline-flex items-center px-3 py-1.5 rounded-full text-xs font-bold shadow-sm ${
                        negotiationResponse.negotiation_status === "accepted"
                          ? "bg-gradient-to-r from-green-500 to-emerald-600 text-white"
                          : negotiationResponse.negotiation_status === "rejected"
                          ? "bg-gradient-to-r from-red-500 to-rose-600 text-white"
                          : negotiationResponse.negotiation_status === "counter_offer"
                          ? "bg-gradient-to-r from-amber-400 to-amber-500 text-amber-900"
                          : "bg-gradient-to-r from-blue-500 to-indigo-600 text-white"
                      }`}
                    >
                      {negotiationResponse.negotiation_status
                        .replace("_", " ")
                        .toUpperCase()}
                    </span>
                  </div>
                  
                  <button
                    onClick={() => {
                      navigator.clipboard.writeText(negotiationResponse.response_message);
                      // Show a toast or feedback here
                      const button = document.activeElement as HTMLButtonElement;
                      const originalText = button.innerText;
                      button.innerText = "Copied!";
                      setTimeout(() => {
                        button.innerText = originalText;
                      }, 2000);
                    }}
                    className="text-sm bg-white text-indigo-600 hover:text-indigo-800 flex items-center gap-1.5 px-4 py-1.5 rounded-lg border border-indigo-200 hover:border-indigo-300 transition-all duration-200 shadow-sm hover:shadow font-medium"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-4 h-4">
                      <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 17.25v3.375c0 .621-.504 1.125-1.125 1.125h-9.75a1.125 1.125 0 0 1-1.125-1.125V7.875c0-.621.504-1.125 1.125-1.125H6.75a9.06 9.06 0 0 1 1.5.124m7.5 10.376h3.375c.621 0 1.125-.504 1.125-1.125V11.25c0-4.46-3.243-8.161-7.5-8.876a9.06 9.06 0 0 0-1.5-.124H9.375c-.621 0-1.125.504-1.125 1.125v3.5" />
                    </svg>
                    Copy Message
                  </button>
                </div>

                {negotiationResponse.next_steps && (
                  <div className="mt-4 bg-gradient-to-r from-gray-50 to-white p-6 rounded-lg border border-gray-200 shadow-sm">
                    <div className="flex items-center mb-4">
                      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-5 h-5 text-gray-700 mr-2">
                        <path fillRule="evenodd" d="M12.97 3.97a.75.75 0 0 1 1.06 0l7.5 7.5a.75.75 0 0 1 0 1.06l-7.5 7.5a.75.75 0 1 1-1.06-1.06l6.22-6.22H3a.75.75 0 0 1 0-1.5h16.19l-6.22-6.22a.75.75 0 0 1 0-1.06Z" clipRule="evenodd" />
                      </svg>
                      <h3 className="text-sm font-medium text-gray-700">
                        Next Steps
                      </h3>
                    </div>
                    <ul className="space-y-3">
                      {negotiationResponse.next_steps.map((step, index) => (
                        <li key={index} className="flex items-start gap-3 bg-white p-3 rounded-lg border border-gray-200 shadow-sm hover:shadow-md transition-all duration-200">
                          <span className="inline-block h-6 w-6 rounded-full bg-gradient-to-br from-gray-600 to-gray-800 text-white flex items-center justify-center text-xs font-bold mt-0.5">{index + 1}</span>
                          <span className="text-sm text-gray-700 font-medium">{step}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </motion.div>
            ) : (
              <div className="text-gray-500 text-center py-16 flex flex-col items-center justify-center">
                {loading ? (
                  <div className="flex flex-col items-center space-y-4">
                    <div className="relative">
                      <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-indigo-600"></div>
                      <div className="absolute inset-0 flex items-center justify-center">
                        <div className="h-8 w-8 rounded-full bg-white"></div>
                      </div>
                    </div>
                    <p className="text-indigo-600 font-medium mt-4">Processing negotiation...</p>
                    <p className="text-gray-500 text-sm max-w-xs">We're generating an AI-powered response based on your inputs</p>
                  </div>
                ) : (
                  <div className="bg-white p-8 rounded-xl shadow-lg border border-gray-100 max-w-md mx-auto">
                    <div className="bg-indigo-50 rounded-full p-4 w-20 h-20 mx-auto mb-6 flex items-center justify-center">
                      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-10 h-10 text-indigo-500">
                        <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 12c0-1.232-.046-2.453-.138-3.662a4.006 4.006 0 0 0-3.7-3.7 48.678 48.678 0 0 0-7.324 0 4.006 4.006 0 0 0-3.7 3.7c-.017.22-.032.441-.046.662M19.5 12l3-3m-3 3-3-3m-12 3c0 1.232.046 2.453.138 3.662a4.006 4.006 0 0 0 3.7 3.7 48.656 48.656 0 0 0 7.324 0 4.006 4.006 0 0 0 3.7-3.7c.017-.22.032-.441.046-.662M4.5 12l3 3m-3-3-3 3" />
                      </svg>
                    </div>
                    <h3 className="mb-2 text-xl font-bold text-gray-800">No Active Negotiation</h3>
                    <p className="mb-6 text-gray-600">Fill out the form to start a new negotiation or respond to an existing one</p>
                    
                    <div className="space-y-4 text-left">
                      <div className="flex items-start gap-3">
                        <div className="bg-indigo-100 rounded-full p-1 mt-0.5">
                          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="w-4 h-4 text-indigo-600">
                            <path fillRule="evenodd" d="M10 18a8 8 0 1 0 0-16 8 8 0 0 0 0 16Zm3.857-9.809a.75.75 0 0 0-1.214-.882l-3.483 4.79-1.88-1.88a.75.75 0 1 0-1.06 1.061l2.5 2.5a.75.75 0 0 0 1.137-.089l4-5.5Z" clipRule="evenodd" />
                          </svg>
                        </div>
                        <p className="text-sm text-gray-600">Create personalized outreach to influencers</p>
                      </div>
                      <div className="flex items-start gap-3">
                        <div className="bg-indigo-100 rounded-full p-1 mt-0.5">
                          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="w-4 h-4 text-indigo-600">
                            <path fillRule="evenodd" d="M10 18a8 8 0 1 0 0-16 8 8 0 0 0 0 16Zm3.857-9.809a.75.75 0 0 0-1.214-.882l-3.483 4.79-1.88-1.88a.75.75 0 1 0-1.06 1.061l2.5 2.5a.75.75 0 0 0 1.137-.089l4-5.5Z" clipRule="evenodd" />
                          </svg>
                        </div>
                        <p className="text-sm text-gray-600">Get AI-powered negotiation suggestions</p>
                      </div>
                      <div className="flex items-start gap-3">
                        <div className="bg-indigo-100 rounded-full p-1 mt-0.5">
                          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="w-4 h-4 text-indigo-600">
                            <path fillRule="evenodd" d="M10 18a8 8 0 1 0 0-16 8 8 0 0 0 0 16Zm3.857-9.809a.75.75 0 0 0-1.214-.882l-3.483 4.79-1.88-1.88a.75.75 0 1 0-1.06 1.061l2.5 2.5a.75.75 0 0 0 1.137-.089l4-5.5Z" clipRule="evenodd" />
                          </svg>
                        </div>
                        <p className="text-sm text-gray-600">Track negotiation status and next steps</p>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
