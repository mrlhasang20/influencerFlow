"use client";

import { useState, useEffect } from "react";
import { FiBarChart2, FiActivity, FiTrendingUp, FiUsers, FiCalendar, FiFilter, FiAlertCircle, FiMap } from "react-icons/fi";
import { motion } from "framer-motion";
import JourneyMap from "@/components/JourneyMap";

// API Request/Response Interfaces
interface AnalyticsRequest {
  campaign_id: string;
  metrics: {
    reach: boolean;
    engagement: boolean;
    impressions?: boolean;
    clicks?: boolean;
    conversions?: boolean;
    revenue?: boolean;
  };
  time_period: {
    start_date: string;
    end_date: string;
  };
}

interface AnalyticsResponse {
  campaign_id: string;
  campaign_name: string;
  period: {
    start_date: string;
    end_date: string;
  };
  metrics: {
    reach?: {
      total: number;
      organic: number;
      paid: number;
      trend: number; // percentage change
    };
    engagement?: {
      likes: number;
      comments: number;
      shares: number;
      saves: number;
      engagement_rate: number;
      trend: number;
    };
    impressions?: {
      total: number;
      unique: number;
      trend: number;
    };
    clicks?: {
      total: number;
      unique: number;
      ctr: number; // click-through rate
      trend: number;
    };
    conversions?: {
      total: number;
      conversion_rate: number;
      trend: number;
    };
    revenue?: {
      total: number;
      roi: number; // return on investment
      trend: number;
    };
  };
}

interface PredictionRequest {
  creator_profile: {
    creator_id: string;
    name: string;
    platform: string;
    followers: number;
    engagement_rate: number;
  };
  campaign_details: {
    campaign_id: string;
    brand_name: string;
    campaign_name: string;
    target_audience: string;
    budget_range: string;
    timeline: string;
    platforms: string[];
    content_types: string[];
    campaign_goals: string[];
  };
  historical_data?: Array<{
    metric: string;
    predicted_value: number;
    confidence_score: number;
    factors_considered: string[];
  }>;
}

interface PredictionResponse {
  campaign_id: string;
  predictions: {
    metric: string;
    predicted_value: number;
    confidence_score: number;
    factors_considered: string[];
  }[];
  recommendations: {
    content_strategy: string[];
    audience_targeting: string[];
    budget_allocation: string[];
  };
}

export default function AnalyticsPage() {
  // State for campaign analysis
  const [analyticsRequest, setAnalyticsRequest] = useState<AnalyticsRequest>({
    campaign_id: "",
    metrics: {
      reach: true,
      engagement: true,
      impressions: false,
      clicks: false,
      conversions: false,
      revenue: false,
    },
    time_period: {
      start_date: "",
      end_date: "",
    },
  });
  const [analyticsResponse, setAnalyticsResponse] = useState<AnalyticsResponse | null>(null);
  const [analyticsLoading, setAnalyticsLoading] = useState(false);
  const [analyticsError, setAnalyticsError] = useState<string | null>(null);

  // State for performance prediction
  const [predictionRequest, setPredictionRequest] = useState<PredictionRequest>({
    creator_profile: {
      creator_id: "",
      name: "",
      platform: "Instagram",
      followers: 0,
      engagement_rate: 0,
    },
    campaign_details: {
      campaign_id: "",
      brand_name: "",
      campaign_name: "",
      target_audience: "",
      budget_range: "",
      timeline: "",
      platforms: ["Instagram"],
      content_types: [],
      campaign_goals: [],
    },
  });
  const [predictionResponse, setPredictionResponse] = useState<PredictionResponse | null>(null);
  const [predictionLoading, setPredictionLoading] = useState(false);
  const [predictionError, setPredictionError] = useState<string | null>(null);

  // UI state
  const [activeTab, setActiveTab] = useState<"analyze" | "predict" | "journey">("analyze");
  const [analyzeView, setAnalyzeView] = useState<"form" | "results">("form");
  const [predictView, setPredictView] = useState<"form" | "results">("form");

  // Campaign data for journey map
  const [campaignForJourney, setCampaignForJourney] = useState<{ id: string; name: string } | null>(null);

  // Mock campaigns for select dropdown (In a real app, these would come from an API)
  const mockCampaigns = [
    { id: "camp-001", name: "Summer Collection Launch" },
    { id: "camp-002", name: "Holiday Season Promotion" },
    { id: "camp-003", name: "Brand Awareness Campaign" },
    { id: "camp-004", name: "Product Launch - Fitness Series" },
  ];

  // Event handlers for analytics
  const handleAnalyticsInputChange = (field: keyof AnalyticsRequest, value: any) => {
    setAnalyticsRequest((prev) => ({
      ...prev,
      [field]: value,
    }));
  };

  const handleMetricChange = (metric: keyof AnalyticsRequest["metrics"]) => {
    setAnalyticsRequest((prev) => ({
      ...prev,
      metrics: {
        ...prev.metrics,
        [metric]: !prev.metrics[metric as keyof typeof prev.metrics],
      },
    }));
  };

  const handleTimePeriodChange = (field: string, value: string) => {
    setAnalyticsRequest((prev) => ({
      ...prev,
      time_period: {
        ...prev.time_period,
        [field]: value,
      },
    }));
  };

  // Event handlers for prediction
  const handlePredictionInputChange = (
    section: "creator_profile" | "campaign_details",
    field: string,
    value: any
  ) => {
    setPredictionRequest((prev) => ({
      ...prev,
      [section]: {
        ...prev[section],
        [field]: value,
      },
    }));
  };

  const handlePlatformChange = (platform: string) => {
    setPredictionRequest((prev) => {
      const currentPlatforms = [...prev.campaign_details.platforms];
      const index = currentPlatforms.indexOf(platform);

      if (index === -1) {
        currentPlatforms.push(platform);
      } else {
        currentPlatforms.splice(index, 1);
      }

      return {
        ...prev,
        campaign_details: {
          ...prev.campaign_details,
          platforms: currentPlatforms,
        },
      };
    });
  };

  const handleContentTypeChange = (contentType: string) => {
    setPredictionRequest((prev) => {
      const currentTypes = [...prev.campaign_details.content_types];
      const index = currentTypes.indexOf(contentType);

      if (index === -1) {
        currentTypes.push(contentType);
      } else {
        currentTypes.splice(index, 1);
      }

      return {
        ...prev,
        campaign_details: {
          ...prev.campaign_details,
          content_types: currentTypes,
        },
      };
    });
  };

  const handleGoalChange = (goal: string) => {
    setPredictionRequest((prev) => {
      const currentGoals = [...prev.campaign_details.campaign_goals];
      const index = currentGoals.indexOf(goal);

      if (index === -1) {
        currentGoals.push(goal);
      } else {
        currentGoals.splice(index, 1);
      }

      return {
        ...prev,
        campaign_details: {
          ...prev.campaign_details,
          campaign_goals: currentGoals,
        },
      };
    });
  };

  // API calls
  const analyzeCampaign = async (e: React.FormEvent) => {
    e.preventDefault();
    setAnalyticsLoading(true);
    setAnalyticsError(null);

    try {
      const response = await fetch("/api/analytics/analyze-campaign", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(analyticsRequest),
      });

      if (!response.ok) {
        throw new Error("Failed to analyze campaign");
      }

      const data = await response.json();
      setAnalyticsResponse(data);
      setAnalyzeView("results");
    } catch (err) {
      setAnalyticsError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setAnalyticsLoading(false);
    }
  };

  const predictPerformance = async (e: React.FormEvent) => {
    e.preventDefault();
    setPredictionLoading(true);
    setPredictionError(null);

    try {
      const response = await fetch("/api/analytics/predict-performance", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(predictionRequest),
      });

      if (!response.ok) {
        throw new Error("Failed to predict performance");
      }

      const data = await response.json();
      setPredictionResponse(data);
      setPredictView("results");
    } catch (err) {
      setPredictionError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setPredictionLoading(false);
    }
  };

  // Helper functions
  const formatNumber = (num: number): string => {
    if (num >= 1000000) {
      return `${(num / 1000000).toFixed(1)}M`;
    }
    if (num >= 1000) {
      return `${(num / 1000).toFixed(1)}K`;
    }
    return num.toLocaleString();
  };

  const formatPercentage = (num: number): string => {
    return `${num >= 0 ? "+" : ""}${num.toFixed(1)}%`;
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-7xl">
      <h1 className="text-4xl font-bold bg-gradient-to-r from-indigo-500 to-purple-600 bg-clip-text text-transparent mb-8">
        Campaign Analytics Dashboard
      </h1>

      {/* Tabs Navigation */}
      <div className="flex border-b border-gray-200 mb-8">
        <button
          onClick={() => setActiveTab("analyze")}
          className={`flex items-center py-4 px-6 ${activeTab === "analyze" ? "border-b-2 border-indigo-500 text-indigo-600" : "text-gray-500 hover:text-gray-700"}`}
        >
          <FiBarChart2 className="mr-2" />
          Analyze Campaign
        </button>
        <button
          onClick={() => setActiveTab("predict")}
          className={`flex items-center py-4 px-6 ${activeTab === "predict" ? "border-b-2 border-indigo-500 text-indigo-600" : "text-gray-500 hover:text-gray-700"}`}
        >
          <FiTrendingUp className="mr-2" />
          Predict Performance
        </button>
        <button
          onClick={() => setActiveTab("journey")}
          className={`flex items-center py-4 px-6 ${activeTab === "journey" ? "border-b-2 border-indigo-500 text-indigo-600" : "text-gray-500 hover:text-gray-700"}`}
        >
          <FiMap className="mr-2" />
          Journey Map
        </button>
      </div>

      {/* Main Content Area */}
      <div className="main-content">
        {activeTab === "analyze" ? (
          <div className="analyze-tab">
            {analyzeView === "form" ? (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5 }}
                className="bg-white rounded-xl shadow-lg p-6 mb-8"
              >
                <h2 className="text-2xl font-semibold mb-6 text-gray-800">Campaign Analysis</h2>

                {analyticsError && (
                  <div className="mb-6 p-4 bg-red-50 border-l-4 border-red-500 rounded-md">
                    <div className="flex items-center">
                      <FiAlertCircle className="text-red-500 mr-3 flex-shrink-0" />
                      <p className="text-red-700">{analyticsError}</p>
                    </div>
                  </div>
                )}

                <form onSubmit={analyzeCampaign} className="space-y-6">
                  {/* Campaign Selection */}
                  <div>
                    <label htmlFor="campaign_id" className="block text-sm font-medium text-gray-700 mb-1">
                      Select Campaign
                    </label>
                    <select
                      id="campaign_id"
                      value={analyticsRequest.campaign_id}
                      onChange={(e) => handleAnalyticsInputChange("campaign_id", e.target.value)}
                      className="w-full p-3 bg-gray-50 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all"
                      required
                    >
                      <option value="">Select a campaign</option>
                      {mockCampaigns.map((campaign) => (
                        <option key={campaign.id} value={campaign.id}>
                          {campaign.name}
                        </option>
                      ))}
                    </select>
                  </div>

                  {/* Metrics Selection */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Metrics to Analyze
                    </label>
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                      {Object.entries(analyticsRequest.metrics).map(([metric, enabled]) => (
                        <div
                          key={metric}
                          className={`flex items-center p-3 rounded-lg border cursor-pointer transition-all ${
                            enabled
                              ? "bg-indigo-50 border-indigo-300"
                              : "bg-white border-gray-200 hover:bg-gray-50"
                          }`}
                          onClick={() => handleMetricChange(metric as keyof AnalyticsRequest["metrics"])}
                        >
                          <div
                            className={`w-5 h-5 rounded mr-3 flex items-center justify-center ${
                              enabled ? "bg-indigo-600" : "bg-gray-200"
                            }`}
                          >
                            {enabled && (
                              <svg
                                xmlns="http://www.w3.org/2000/svg"
                                className="h-3 w-3 text-white"
                                viewBox="0 0 20 20"
                                fill="currentColor"
                              >
                                <path
                                  fillRule="evenodd"
                                  d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                                  clipRule="evenodd"
                                />
                              </svg>
                            )}
                          </div>
                          <span className="text-sm font-medium capitalize">
                            {metric.replace(/_/g, " ")}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Time Period Selection */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <label htmlFor="start_date" className="block text-sm font-medium text-gray-700 mb-1">
                        Start Date
                      </label>
                      <div className="relative">
                        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                          <FiCalendar className="text-gray-500" />
                        </div>
                        <input
                          id="start_date"
                          type="date"
                          value={analyticsRequest.time_period.start_date}
                          onChange={(e) => handleTimePeriodChange("start_date", e.target.value)}
                          className="w-full pl-10 p-3 bg-gray-50 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all"
                          required
                        />
                      </div>
                    </div>
                    <div>
                      <label htmlFor="end_date" className="block text-sm font-medium text-gray-700 mb-1">
                        End Date
                      </label>
                      <div className="relative">
                        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                          <FiCalendar className="text-gray-500" />
                        </div>
                        <input
                          id="end_date"
                          type="date"
                          value={analyticsRequest.time_period.end_date}
                          onChange={(e) => handleTimePeriodChange("end_date", e.target.value)}
                          className="w-full pl-10 p-3 bg-gray-50 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all"
                          required
                        />
                      </div>
                    </div>
                  </div>

                  {/* Submit Button */}
                  <div className="flex justify-end">
                    <button
                      type="submit"
                      disabled={analyticsLoading}
                      className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white py-3 px-6 rounded-md shadow-md hover:from-indigo-700 hover:to-purple-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 transition-all disabled:opacity-70 disabled:cursor-not-allowed flex items-center"
                    >
                      {analyticsLoading ? (
                        <>
                          <svg
                            className="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
                            xmlns="http://www.w3.org/2000/svg"
                            fill="none"
                            viewBox="0 0 24 24"
                          >
                            <circle
                              className="opacity-25"
                              cx="12"
                              cy="12"
                              r="10"
                              stroke="currentColor"
                              strokeWidth="4"
                            ></circle>
                            <path
                              className="opacity-75"
                              fill="currentColor"
                              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                            ></path>
                          </svg>
                          Processing...
                        </>
                      ) : (
                        <>
                          <FiActivity className="mr-2" />
                          Analyze Campaign
                        </>
                      )}
                    </button>
                  </div>
                </form>
              </motion.div>
            ) : (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5 }}
              >
                {analyticsResponse && (
                  <>
                    <div className="flex justify-between items-center mb-6">
                      <h2 className="text-2xl font-semibold text-gray-800">
                        {analyticsResponse.campaign_name} Analysis
                      </h2>
                      <button
                        onClick={() => setAnalyzeView("form")}
                        className="text-indigo-600 hover:text-indigo-800 flex items-center text-sm font-medium"
                      >
                        <FiFilter className="mr-1" />
                        Change Parameters
                      </button>
                    </div>

                    <p className="text-gray-600 mb-8">
                      Analysis Period: {new Date(analyticsResponse.period.start_date).toLocaleDateString()} -{" "}
                      {new Date(analyticsResponse.period.end_date).toLocaleDateString()}
                    </p>

                    {/* Metrics Grid */}
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
                      {/* Reach Metrics */}
                      {analyticsResponse.metrics.reach && (
                        <div className="bg-white rounded-xl shadow-md p-6 border border-gray-100 hover:shadow-lg transition-all">
                          <div className="flex justify-between items-start mb-4">
                            <h3 className="text-lg font-semibold text-gray-800">Reach</h3>
                            <span className={`text-sm font-bold px-2 py-1 rounded-full ${
                              analyticsResponse.metrics.reach.trend >= 0
                                ? "bg-green-100 text-green-800"
                                : "bg-red-100 text-red-800"
                            }`}>
                              {formatPercentage(analyticsResponse.metrics.reach.trend)}
                            </span>
                          </div>

                          <div className="text-3xl font-bold text-gray-900 mb-4">
                            {formatNumber(analyticsResponse.metrics.reach.total)}
                          </div>

                          <div className="grid grid-cols-2 gap-2">
                            <div className="bg-indigo-50 rounded-lg p-3">
                              <p className="text-xs text-indigo-700 font-medium mb-1">Organic</p>
                              <p className="text-lg font-semibold text-indigo-900">
                                {formatNumber(analyticsResponse.metrics.reach.organic)}
                              </p>
                            </div>
                            <div className="bg-purple-50 rounded-lg p-3">
                              <p className="text-xs text-purple-700 font-medium mb-1">Paid</p>
                              <p className="text-lg font-semibold text-purple-900">
                                {formatNumber(analyticsResponse.metrics.reach.paid)}
                              </p>
                            </div>
                          </div>
                        </div>
                      )}

                      {/* Engagement Metrics */}
                      {analyticsResponse.metrics.engagement && (
                        <div className="bg-white rounded-xl shadow-md p-6 border border-gray-100 hover:shadow-lg transition-all">
                          <div className="flex justify-between items-start mb-4">
                            <h3 className="text-lg font-semibold text-gray-800">Engagement</h3>
                            <span className={`text-sm font-bold px-2 py-1 rounded-full ${
                              analyticsResponse.metrics.engagement.trend >= 0
                                ? "bg-green-100 text-green-800"
                                : "bg-red-100 text-red-800"
                            }`}>
                              {formatPercentage(analyticsResponse.metrics.engagement.trend)}
                            </span>
                          </div>

                          <div className="flex items-baseline mb-4">
                            <span className="text-3xl font-bold text-gray-900">
                              {analyticsResponse.metrics.engagement.engagement_rate.toFixed(2)}%
                            </span>
                            <span className="text-sm text-gray-500 ml-2">Engagement Rate</span>
                          </div>

                          <div className="grid grid-cols-2 gap-2">
                            <div className="bg-blue-50 rounded-lg p-3">
                              <p className="text-xs text-blue-700 font-medium mb-1">Likes</p>
                              <p className="text-lg font-semibold text-blue-900">
                                {formatNumber(analyticsResponse.metrics.engagement.likes)}
                              </p>
                            </div>
                            <div className="bg-indigo-50 rounded-lg p-3">
                              <p className="text-xs text-indigo-700 font-medium mb-1">Comments</p>
                              <p className="text-lg font-semibold text-indigo-900">
                                {formatNumber(analyticsResponse.metrics.engagement.comments)}
                              </p>
                            </div>
                            <div className="bg-purple-50 rounded-lg p-3 mt-2">
                              <p className="text-xs text-purple-700 font-medium mb-1">Shares</p>
                              <p className="text-lg font-semibold text-purple-900">
                                {formatNumber(analyticsResponse.metrics.engagement.shares)}
                              </p>
                            </div>
                            <div className="bg-pink-50 rounded-lg p-3 mt-2">
                              <p className="text-xs text-pink-700 font-medium mb-1">Saves</p>
                              <p className="text-lg font-semibold text-pink-900">
                                {formatNumber(analyticsResponse.metrics.engagement.saves)}
                              </p>
                            </div>
                          </div>
                        </div>
                      )}

                      {/* Impressions Metrics */}
                      {analyticsResponse.metrics.impressions && (
                        <div className="bg-white rounded-xl shadow-md p-6 border border-gray-100 hover:shadow-lg transition-all">
                          <div className="flex justify-between items-start mb-4">
                            <h3 className="text-lg font-semibold text-gray-800">Impressions</h3>
                            <span className={`text-sm font-bold px-2 py-1 rounded-full ${
                              analyticsResponse.metrics.impressions.trend >= 0
                                ? "bg-green-100 text-green-800"
                                : "bg-red-100 text-red-800"
                            }`}>
                              {formatPercentage(analyticsResponse.metrics.impressions.trend)}
                            </span>
                          </div>

                          <div className="text-3xl font-bold text-gray-900 mb-4">
                            {formatNumber(analyticsResponse.metrics.impressions.total)}
                          </div>

                          <div className="bg-indigo-50 rounded-lg p-3">
                            <p className="text-xs text-indigo-700 font-medium mb-1">Unique Impressions</p>
                            <p className="text-lg font-semibold text-indigo-900">
                              {formatNumber(analyticsResponse.metrics.impressions.unique)}
                            </p>
                          </div>
                        </div>
                      )}

                      {/* Clicks Metrics */}
                      {analyticsResponse.metrics.clicks && (
                        <div className="bg-white rounded-xl shadow-md p-6 border border-gray-100 hover:shadow-lg transition-all">
                          <div className="flex justify-between items-start mb-4">
                            <h3 className="text-lg font-semibold text-gray-800">Clicks</h3>
                            <span className={`text-sm font-bold px-2 py-1 rounded-full ${
                              analyticsResponse.metrics.clicks.trend >= 0
                                ? "bg-green-100 text-green-800"
                                : "bg-red-100 text-red-800"
                            }`}>
                              {formatPercentage(analyticsResponse.metrics.clicks.trend)}
                            </span>
                          </div>

                          <div className="text-3xl font-bold text-gray-900 mb-4">
                            {formatNumber(analyticsResponse.metrics.clicks.total)}
                          </div>

                          <div className="grid grid-cols-2 gap-2">
                            <div className="bg-indigo-50 rounded-lg p-3">
                              <p className="text-xs text-indigo-700 font-medium mb-1">Unique Clicks</p>
                              <p className="text-lg font-semibold text-indigo-900">
                                {formatNumber(analyticsResponse.metrics.clicks.unique)}
                              </p>
                            </div>
                            <div className="bg-purple-50 rounded-lg p-3">
                              <p className="text-xs text-purple-700 font-medium mb-1">CTR</p>
                              <p className="text-lg font-semibold text-purple-900">
                                {analyticsResponse.metrics.clicks.ctr.toFixed(2)}%
                              </p>
                            </div>
                          </div>
                        </div>
                      )}

                      {/* Conversions Metrics */}
                      {analyticsResponse.metrics.conversions && (
                        <div className="bg-white rounded-xl shadow-md p-6 border border-gray-100 hover:shadow-lg transition-all">
                          <div className="flex justify-between items-start mb-4">
                            <h3 className="text-lg font-semibold text-gray-800">Conversions</h3>
                            <span className={`text-sm font-bold px-2 py-1 rounded-full ${
                              analyticsResponse.metrics.conversions.trend >= 0
                                ? "bg-green-100 text-green-800"
                                : "bg-red-100 text-red-800"
                            }`}>
                              {formatPercentage(analyticsResponse.metrics.conversions.trend)}
                            </span>
                          </div>

                          <div className="text-3xl font-bold text-gray-900 mb-4">
                            {formatNumber(analyticsResponse.metrics.conversions.total)}
                          </div>

                          <div className="bg-indigo-50 rounded-lg p-3">
                            <p className="text-xs text-indigo-700 font-medium mb-1">Conversion Rate</p>
                            <p className="text-lg font-semibold text-indigo-900">
                              {analyticsResponse.metrics.conversions.conversion_rate.toFixed(2)}%
                            </p>
                          </div>
                        </div>
                      )}

                      {/* Revenue Metrics */}
                      {analyticsResponse.metrics.revenue && (
                        <div className="bg-white rounded-xl shadow-md p-6 border border-gray-100 hover:shadow-lg transition-all">
                          <div className="flex justify-between items-start mb-4">
                            <h3 className="text-lg font-semibold text-gray-800">Revenue</h3>
                            <span className={`text-sm font-bold px-2 py-1 rounded-full ${
                              analyticsResponse.metrics.revenue.trend >= 0
                                ? "bg-green-100 text-green-800"
                                : "bg-red-100 text-red-800"
                            }`}>
                              {formatPercentage(analyticsResponse.metrics.revenue.trend)}
                            </span>
                          </div>

                          <div className="text-3xl font-bold text-gray-900 mb-4">
                            ${formatNumber(analyticsResponse.metrics.revenue.total)}
                          </div>

                          <div className="bg-indigo-50 rounded-lg p-3">
                            <p className="text-xs text-indigo-700 font-medium mb-1">ROI</p>
                            <p className="text-lg font-semibold text-indigo-900">
                              {analyticsResponse.metrics.revenue.roi.toFixed(2)}x
                            </p>
                          </div>
                        </div>
                      )}
                    </div>
                  </>
                )}
              </motion.div>
            )}
          </div>
        ) : activeTab === "predict" ? (
          <div className="predict-tab">
            {predictView === "form" ? (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5 }}
                className="bg-white rounded-xl shadow-lg p-6 mb-8"
              >
                <h2 className="text-2xl font-semibold mb-6 text-gray-800">Performance Prediction</h2>

                {predictionError && (
                  <div className="mb-6 p-4 bg-red-50 border-l-4 border-red-500 rounded-md">
                    <div className="flex items-center">
                      <FiAlertCircle className="text-red-500 mr-3 flex-shrink-0" />
                      <p className="text-red-700">{predictionError}</p>
                    </div>
                  </div>
                )}

                <form onSubmit={predictPerformance} className="space-y-8">
                  {/* Creator Profile Section */}
                  <div className="border border-gray-100 rounded-lg p-5 bg-gray-50">
                    <h3 className="text-xl font-medium mb-4 text-gray-800">Creator Profile</h3>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div>
                        <label htmlFor="creator_id" className="block text-sm font-medium text-gray-700 mb-1">
                          Creator ID
                        </label>
                        <input
                          id="creator_id"
                          type="text"
                          value={predictionRequest.creator_profile.creator_id}
                          onChange={(e) => handlePredictionInputChange("creator_profile", "creator_id", e.target.value)}
                          className="w-full p-3 bg-white border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all"
                          placeholder="e.g. cr-12345"
                          required
                        />
                      </div>

                      <div>
                        <label htmlFor="creator_name" className="block text-sm font-medium text-gray-700 mb-1">
                          Creator Name
                        </label>
                        <input
                          id="creator_name"
                          type="text"
                          value={predictionRequest.creator_profile.name}
                          onChange={(e) => handlePredictionInputChange("creator_profile", "name", e.target.value)}
                          className="w-full p-3 bg-white border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all"
                          placeholder="e.g. Jane Smith"
                          required
                        />
                      </div>

                      <div>
                        <label htmlFor="platform" className="block text-sm font-medium text-gray-700 mb-1">
                          Primary Platform
                        </label>
                        <select
                          id="platform"
                          value={predictionRequest.creator_profile.platform}
                          onChange={(e) => handlePredictionInputChange("creator_profile", "platform", e.target.value)}
                          className="w-full p-3 bg-white border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all"
                          required
                        >
                          <option value="">Select a platform</option>
                          <option value="Instagram">Instagram</option>
                          <option value="TikTok">TikTok</option>
                          <option value="YouTube">YouTube</option>
                          <option value="Twitter">Twitter</option>
                          <option value="Twitch">Twitch</option>
                        </select>
                      </div>

                      <div>
                        <label htmlFor="followers" className="block text-sm font-medium text-gray-700 mb-1">
                          Followers Count
                        </label>
                        <input
                          id="followers"
                          type="number"
                          min="0"
                          value={predictionRequest.creator_profile.followers}
                          onChange={(e) => handlePredictionInputChange("creator_profile", "followers", Number(e.target.value))}
                          className="w-full p-3 bg-white border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all"
                          placeholder="e.g. 50000"
                          required
                        />
                      </div>

                      <div className="md:col-span-2">
                        <label htmlFor="engagement_rate" className="block text-sm font-medium text-gray-700 mb-1">
                          Average Engagement Rate (%)
                        </label>
                        <input
                          id="engagement_rate"
                          type="number"
                          step="0.01"
                          min="0"
                          max="100"
                          value={predictionRequest.creator_profile.engagement_rate}
                          onChange={(e) => handlePredictionInputChange("creator_profile", "engagement_rate", Number(e.target.value))}
                          className="w-full p-3 bg-white border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all"
                          placeholder="e.g. 3.5"
                          required
                        />
                      </div>
                    </div>
                  </div>

                  {/* Campaign Details Section */}
                  <div className="border border-gray-100 rounded-lg p-5 bg-gray-50">
                    <h3 className="text-xl font-medium mb-4 text-gray-800">Campaign Details</h3>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div>
                        <label htmlFor="campaign_id" className="block text-sm font-medium text-gray-700 mb-1">
                          Campaign ID
                        </label>
                        <input
                          id="campaign_id_predict"
                          type="text"
                          value={predictionRequest.campaign_details.campaign_id}
                          onChange={(e) => handlePredictionInputChange("campaign_details", "campaign_id", e.target.value)}
                          className="w-full p-3 bg-white border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all"
                          placeholder="e.g. camp-001"
                          required
                        />
                      </div>

                      <div>
                        <label htmlFor="brand_name" className="block text-sm font-medium text-gray-700 mb-1">
                          Brand Name
                        </label>
                        <input
                          id="brand_name"
                          type="text"
                          value={predictionRequest.campaign_details.brand_name}
                          onChange={(e) => handlePredictionInputChange("campaign_details", "brand_name", e.target.value)}
                          className="w-full p-3 bg-white border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all"
                          placeholder="e.g. Acme Inc."
                          required
                        />
                      </div>

                      <div className="md:col-span-2">
                        <label htmlFor="campaign_name" className="block text-sm font-medium text-gray-700 mb-1">
                          Campaign Name
                        </label>
                        <input
                          id="campaign_name"
                          type="text"
                          value={predictionRequest.campaign_details.campaign_name}
                          onChange={(e) => handlePredictionInputChange("campaign_details", "campaign_name", e.target.value)}
                          className="w-full p-3 bg-white border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all"
                          placeholder="e.g. Summer Product Launch"
                          required
                        />
                      </div>

                      <div className="md:col-span-2">
                        <label htmlFor="target_audience" className="block text-sm font-medium text-gray-700 mb-1">
                          Target Audience
                        </label>
                        <input
                          id="target_audience"
                          type="text"
                          value={predictionRequest.campaign_details.target_audience}
                          onChange={(e) => handlePredictionInputChange("campaign_details", "target_audience", e.target.value)}
                          className="w-full p-3 bg-white border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all"
                          placeholder="e.g. Males/Females 18-34, interested in fitness"
                          required
                        />
                      </div>

                      <div>
                        <label htmlFor="budget_range" className="block text-sm font-medium text-gray-700 mb-1">
                          Budget Range
                        </label>
                        <select
                          id="budget_range"
                          value={predictionRequest.campaign_details.budget_range}
                          onChange={(e) => handlePredictionInputChange("campaign_details", "budget_range", e.target.value)}
                          className="w-full p-3 bg-white border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all"
                          required
                        >
                          <option value="">Select budget range</option>
                          <option value="$1,000 - $5,000">$1,000 - $5,000</option>
                          <option value="$5,000 - $10,000">$5,000 - $10,000</option>
                          <option value="$10,000 - $25,000">$10,000 - $25,000</option>
                          <option value="$25,000 - $50,000">$25,000 - $50,000</option>
                          <option value="$50,000+">$50,000+</option>
                        </select>
                      </div>

                      <div>
                        <label htmlFor="timeline" className="block text-sm font-medium text-gray-700 mb-1">
                          Campaign Timeline
                        </label>
                        <select
                          id="timeline"
                          value={predictionRequest.campaign_details.timeline}
                          onChange={(e) => handlePredictionInputChange("campaign_details", "timeline", e.target.value)}
                          className="w-full p-3 bg-white border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all"
                          required
                        >
                          <option value="">Select timeline</option>
                          <option value="1-2 weeks">1-2 weeks</option>
                          <option value="2-4 weeks">2-4 weeks</option>
                          <option value="1-3 months">1-3 months</option>
                          <option value="3-6 months">3-6 months</option>
                          <option value="6+ months">6+ months</option>
                        </select>
                      </div>
                    </div>
                  </div>

                  {/* Platforms, Content Types, and Goals */}
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div className="border border-gray-100 rounded-lg p-5 bg-gray-50">
                      <h3 className="text-base font-medium mb-3 text-gray-800">Platforms</h3>

                      <div className="space-y-2">
                        {["", "Instagram", "TikTok", "YouTube", "Twitter", "Twitch"].map((platform) =>
                          platform ? (
                            <div
                              key={platform}
                              className={`flex items-center p-2 rounded-md cursor-pointer transition-all ${
                                predictionRequest.campaign_details.platforms.includes(platform)
                                  ? "bg-indigo-50 border border-indigo-200"
                                  : "bg-white border border-gray-200 hover:bg-gray-50"
                              }`}
                              onClick={() => handlePlatformChange(platform)}
                            >
                              <div
                                className={`w-4 h-4 rounded-sm mr-2 flex items-center justify-center ${
                                  predictionRequest.campaign_details.platforms.includes(platform)
                                    ? "bg-indigo-600"
                                    : "bg-gray-200"
                                }`}
                              >
                                {predictionRequest.campaign_details.platforms.includes(platform) && (
                                  <svg
                                    xmlns="http://www.w3.org/2000/svg"
                                    className="h-3 w-3 text-white"
                                    viewBox="0 0 20 20"
                                    fill="currentColor"
                                  >
                                    <path
                                      fillRule="evenodd"
                                      d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                                      clipRule="evenodd"
                                    />
                                  </svg>
                                )}
                              </div>
                              <span className="text-sm">{platform}</span>
                            </div>
                          ) : null
                        )}
                      </div>
                    </div>

                    <div className="border border-gray-100 rounded-lg p-5 bg-gray-50">
                      <h3 className="text-base font-medium mb-3 text-gray-800">Content Types</h3>

                      <div className="space-y-2">
                        {["", "Photo Post", "Video", "Story", "Reel", "Live Stream", "Blog"].map((type) =>
                          type ? (
                            <div
                              key={type}
                              className={`flex items-center p-2 rounded-md cursor-pointer transition-all ${
                                predictionRequest.campaign_details.content_types.includes(type)
                                  ? "bg-indigo-50 border border-indigo-200"
                                  : "bg-white border border-gray-200 hover:bg-gray-50"
                              }`}
                              onClick={() => handleContentTypeChange(type)}
                            >
                              <div
                                className={`w-4 h-4 rounded-sm mr-2 flex items-center justify-center ${
                                  predictionRequest.campaign_details.content_types.includes(type)
                                    ? "bg-indigo-600"
                                    : "bg-gray-200"
                                }`}
                              >
                                {predictionRequest.campaign_details.content_types.includes(type) && (
                                  <svg
                                    xmlns="http://www.w3.org/2000/svg"
                                    className="h-3 w-3 text-white"
                                    viewBox="0 0 20 20"
                                    fill="currentColor"
                                  >
                                    <path
                                      fillRule="evenodd"
                                      d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                                      clipRule="evenodd"
                                    />
                                  </svg>
                                )}
                              </div>
                              <span className="text-sm">{type}</span>
                            </div>
                          ) : null
                        )}
                      </div>
                    </div>

                    <div className="border border-gray-100 rounded-lg p-5 bg-gray-50">
                      <h3 className="text-base font-medium mb-3 text-gray-800">Campaign Goals</h3>

                      <div className="space-y-2">
                        {["", "Brand Awareness", "Engagement", "Traffic", "Lead Generation", "Sales/Conversions", "App Installs"].map(
                          (goal) =>
                            goal ? (
                              <div
                                key={goal}
                                className={`flex items-center p-2 rounded-md cursor-pointer transition-all ${
                                  predictionRequest.campaign_details.campaign_goals.includes(goal)
                                    ? "bg-indigo-50 border border-indigo-200"
                                    : "bg-white border border-gray-200 hover:bg-gray-50"
                                }`}
                                onClick={() => handleGoalChange(goal)}
                              >
                                <div
                                  className={`w-4 h-4 rounded-sm mr-2 flex items-center justify-center ${
                                    predictionRequest.campaign_details.campaign_goals.includes(goal)
                                      ? "bg-indigo-600"
                                      : "bg-gray-200"
                                  }`}
                                >
                                  {predictionRequest.campaign_details.campaign_goals.includes(goal) && (
                                    <svg
                                      xmlns="http://www.w3.org/2000/svg"
                                      className="h-3 w-3 text-white"
                                      viewBox="0 0 20 20"
                                      fill="currentColor"
                                    >
                                      <path
                                        fillRule="evenodd"
                                        d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                                        clipRule="evenodd"
                                      />
                                    </svg>
                                  )}
                                </div>
                                <span className="text-sm">{goal}</span>
                              </div>
                            ) : null
                        )}
                      </div>
                    </div>
                  </div>

                  {/* Submit Button */}
                  <div className="flex justify-end">
                    <button
                      type="submit"
                      disabled={predictionLoading}
                      className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white py-3 px-6 rounded-md shadow-md hover:from-indigo-700 hover:to-purple-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 transition-all disabled:opacity-70 disabled:cursor-not-allowed flex items-center"
                    >
                      {predictionLoading ? (
                        <>
                          <svg
                            className="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
                            xmlns="http://www.w3.org/2000/svg"
                            fill="none"
                            viewBox="0 0 24 24"
                          >
                            <circle
                              className="opacity-25"
                              cx="12"
                              cy="12"
                              r="10"
                              stroke="currentColor"
                              strokeWidth="4"
                            ></circle>
                            <path
                              className="opacity-75"
                              fill="currentColor"
                              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                            ></path>
                          </svg>
                          Processing...
                        </>
                      ) : (
                        <>
                          <FiTrendingUp className="mr-2" />
                          Predict Performance
                        </>
                      )}
                    </button>
                  </div>
                </form>
              </motion.div>
            ) : (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5 }}
              >
                {predictionResponse && (
                  <>
                    <div className="flex justify-between items-center mb-6">
                      <h2 className="text-2xl font-semibold text-gray-800">
                        Performance Prediction Results
                      </h2>
                      <button
                        onClick={() => setPredictView("form")}
                        className="text-indigo-600 hover:text-indigo-800 flex items-center text-sm font-medium"
                      >
                        <FiFilter className="mr-1" />
                        Modify Parameters
                      </button>
                    </div>

                    <div className="bg-white rounded-xl shadow-md p-6 border border-gray-100 mb-8">
                      <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-6">
                        <div>
                          <h3 className="text-xl font-semibold text-gray-800 mb-1">
                            Campaign ID: {predictionResponse.campaign_id}
                          </h3>
                          <p className="text-gray-600">
                            Creator: {predictionRequest.creator_profile.name} ({predictionRequest.creator_profile.platform})
                          </p>
                        </div>
                        <div className="mt-4 md:mt-0 bg-indigo-50 rounded-lg px-4 py-2">
                          <p className="text-sm text-indigo-700">
                            <span className="font-medium">Followers:</span> {formatNumber(predictionRequest.creator_profile.followers)}
                          </p>
                        </div>
                      </div>

                      {/* Metrics Predictions */}
                      <h4 className="text-lg font-medium text-gray-800 mb-4">Performance Predictions</h4>

                      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
                        {predictionResponse.predictions.map((prediction, index) => (
                          <div
                            key={index}
                            className="bg-gradient-to-br from-white to-gray-50 rounded-xl shadow-sm p-5 border border-gray-100 relative overflow-hidden"
                          >
                            {/* Confidence Indicator */}
                            <div
                              className="absolute top-0 right-0 h-1"
                              style={{
                                width: `${prediction.confidence_score * 100}%`,
                                backgroundColor: `${
                                  prediction.confidence_score >= 0.7
                                    ? "#4ade80"
                                    : prediction.confidence_score >= 0.4
                                    ? "#facc15"
                                    : "#f87171"
                                }`,
                              }}
                            />

                            <h5 className="text-base font-medium text-gray-800 mb-3 capitalize">
                              {prediction.metric.replace(/_/g, " ")}
                            </h5>

                            <div className="text-2xl font-bold text-gray-900 mb-4">
                              {prediction.metric.includes("rate") || prediction.metric.includes("percentage")
                                ? `${prediction.predicted_value.toFixed(2)}%`
                                : prediction.metric.includes("revenue") || prediction.metric.includes("cost")
                                ? `$${formatNumber(prediction.predicted_value)}`
                                : formatNumber(prediction.predicted_value)}
                            </div>

                            <div className="flex items-center justify-between">
                              <div className="text-xs font-medium text-gray-500">
                                Confidence Score:
                              </div>
                              <div
                                className={`text-xs font-bold px-2 py-1 rounded-full ${
                                  prediction.confidence_score >= 0.7
                                    ? "bg-green-100 text-green-800"
                                    : prediction.confidence_score >= 0.4
                                    ? "bg-yellow-100 text-yellow-800"
                                    : "bg-red-100 text-red-800"
                                }`}
                              >
                                {(prediction.confidence_score * 100).toFixed(0)}%
                              </div>
                            </div>

                            <div className="mt-4 pt-3 border-t border-gray-100">
                              <p className="text-xs font-medium text-gray-500 mb-2">
                                Factors Considered:
                              </p>
                              <div className="flex flex-wrap gap-2">
                                {prediction.factors_considered.map((factor, i) => (
                                  <span
                                    key={i}
                                    className="text-xs bg-indigo-50 text-indigo-600 px-2 py-1 rounded-full"
                                  >
                                    {factor}
                                  </span>
                                ))}
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Recommendations Section */}
                    <div className="bg-white rounded-xl shadow-md p-6 border border-gray-100">
                      <h3 className="text-xl font-semibold text-gray-800 mb-6">
                        Recommendations
                      </h3>

                      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                        {/* Content Strategy */}
                        <div className="bg-gradient-to-br from-indigo-50 to-indigo-100 rounded-xl p-5">
                          <h4 className="text-lg font-medium text-indigo-800 mb-4 flex items-center">
                            <svg
                              xmlns="http://www.w3.org/2000/svg"
                              className="h-5 w-5 mr-2"
                              viewBox="0 0 20 20"
                              fill="currentColor"
                            >
                              <path
                                fillRule="evenodd"
                                d="M4 3a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V5a2 2 0 00-2-2H4zm12 12H4l4-8 3 6 2-4 3 6z"
                                clipRule="evenodd"
                              />
                            </svg>
                            Content Strategy
                          </h4>
                          <ul className="space-y-3">
                            {predictionResponse.recommendations.content_strategy.map((item, index) => (
                              <li key={index} className="flex items-start">
                                <svg
                                  xmlns="http://www.w3.org/2000/svg"
                                  className="h-5 w-5 text-indigo-600 mr-2 flex-shrink-0 mt-0.5"
                                  viewBox="0 0 20 20"
                                  fill="currentColor"
                                >
                                  <path
                                    fillRule="evenodd"
                                    d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                                    clipRule="evenodd"
                                  />
                                </svg>
                                <span className="text-sm text-indigo-900">{item}</span>
                              </li>
                            ))}
                          </ul>
                        </div>

                        {/* Audience Targeting */}
                        <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-xl p-5">
                          <h4 className="text-lg font-medium text-purple-800 mb-4 flex items-center">
                            <svg
                              xmlns="http://www.w3.org/2000/svg"
                              className="h-5 w-5 mr-2"
                              viewBox="0 0 20 20"
                              fill="currentColor"
                            >
                              <path d="M13 6a3 3 0 11-6 0 3 3 0 016 0zM18 8a2 2 0 11-4 0 2 2 0 014 0zM14 15a4 4 0 00-8 0v3h8v-3zM6 8a2 2 0 11-4 0 2 2 0 014 0zM16 18v-3a5.972 5.972 0 00-.75-2.906A3.005 3.005 0 0119 15v3h-3zM4.75 12.094A5.973 5.973 0 004 15v3H1v-3a3 3 0 013.75-2.906z" />
                            </svg>
                            Audience Targeting
                          </h4>
                          <ul className="space-y-3">
                            {predictionResponse.recommendations.audience_targeting.map((item, index) => (
                              <li key={index} className="flex items-start">
                                <svg
                                  xmlns="http://www.w3.org/2000/svg"
                                  className="h-5 w-5 text-purple-600 mr-2 flex-shrink-0 mt-0.5"
                                  viewBox="0 0 20 20"
                                  fill="currentColor"
                                >
                                  <path
                                    fillRule="evenodd"
                                    d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                                    clipRule="evenodd"
                                  />
                                </svg>
                                <span className="text-sm text-purple-900">{item}</span>
                              </li>
                            ))}
                          </ul>
                        </div>

                        {/* Budget Allocation */}
                        <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl p-5">
                          <h4 className="text-lg font-medium text-blue-800 mb-4 flex items-center">
                            <svg
                              xmlns="http://www.w3.org/2000/svg"
                              className="h-5 w-5 mr-2"
                              viewBox="0 0 20 20"
                              fill="currentColor"
                            >
                              <path
                                fillRule="evenodd"
                                d="M4 4a2 2 0 00-2 2v4a2 2 0 002 2V6h10a2 2 0 00-2-2H4zm2 6a2 2 0 012-2h8a2 2 0 012 2v4a2 2 0 01-2 2H8a2 2 0 01-2-2v-4zm6 4a2 2 0 100-4 2 2 0 000 4z"
                                clipRule="evenodd"
                              />
                            </svg>
                            Budget Allocation
                          </h4>
                          <ul className="space-y-3">
                            {predictionResponse.recommendations.budget_allocation.map((item, index) => (
                              <li key={index} className="flex items-start">
                                <svg
                                  xmlns="http://www.w3.org/2000/svg"
                                  className="h-5 w-5 text-blue-600 mr-2 flex-shrink-0 mt-0.5"
                                  viewBox="0 0 20 20"
                                  fill="currentColor"
                                >
                                  <path
                                    fillRule="evenodd"
                                    d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                                    clipRule="evenodd"
                                  />
                                </svg>
                                <span className="text-sm text-blue-900">{item}</span>
                              </li>
                            ))}
                          </ul>
                        </div>
                      </div>
                    </div>
                  </>
                )}
              </motion.div>
            )}
          </div>
        ) : activeTab === "journey" ? (
          <div className="py-6">
            {campaignForJourney ? (
              <JourneyMap campaignId={campaignForJourney.id} campaignName={campaignForJourney.name} />
            ) : (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5 }}
                className="bg-white rounded-xl shadow-md p-6 border border-gray-100"
              >
                <h2 className="text-lg font-semibold text-gray-800 mb-6">Select a Campaign</h2>
                <p className="text-gray-600 mb-4">
                  View the customer journey map for your campaign to understand touchpoints, conversions, and drop-offs.
                </p>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mt-6">
                  {/* Sample campaign cards - in a real app, these would be fetched from an API */}
                  {[
                    { id: "camp-001", name: "Summer Collection Launch" },
                    { id: "camp-002", name: "Holiday Season Promotion" },
                    { id: "camp-003", name: "Back to School Campaign" },
                    { id: "camp-004", name: "Product Awareness Drive" },
                    { id: "camp-005", name: "Brand Loyalty Program" },
                    { id: "camp-006", name: "New Market Expansion" },
                  ].map((campaign) => (
                    <div
                      key={campaign.id}
                      onClick={() => setCampaignForJourney(campaign)}
                      className="bg-gray-50 hover:bg-indigo-50 border border-gray-100 hover:border-indigo-100 rounded-lg p-4 cursor-pointer transition-colors duration-200"
                    >
                      <h3 className="text-gray-800 font-medium">{campaign.name}</h3>
                      <p className="text-xs text-gray-500 mt-1">ID: {campaign.id}</p>
                      <div className="flex justify-between items-center mt-3">
                        <span className="text-xs text-indigo-600 font-medium">View Journey Map</span>
                        <FiMap className="text-indigo-600" />
                      </div>
                    </div>
                  ))}
                </div>
              </motion.div>
            )}
          </div>
        ) : null}
      </div>

      {/* Go back button for Journey Map */}
      {activeTab === "journey" && campaignForJourney && (
        <div className="absolute top-6 right-6">
          <button
            onClick={() => setCampaignForJourney(null)}
            className="text-sm font-medium text-indigo-600 hover:text-indigo-800 flex items-center"
          >
            <FiFilter className="mr-1" />
            Change Campaign
          </button>
        </div>
      )}
    </div>
  );
};