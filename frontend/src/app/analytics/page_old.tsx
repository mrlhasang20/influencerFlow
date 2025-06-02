"use client";

import { useState } from "react";

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
      rate: number;
      trend: number;
    };
    revenue?: {
      total: number;
      average_order_value: number;
      trend: number;
    };
  };
  summary: {
    best_performing_content: string[];
    audience_demographics: {
      age_groups: Record<string, number>;
      locations: Record<string, number>;
      interests: string[];
    };
    recommendations: string[];
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

  const [analyticsResponse, setAnalyticsResponse] =
    useState<AnalyticsResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<
    "overview" | "details" | "recommendations" | "prediction"
  >("overview");

  const [predictionRequest, setPredictionRequest] = useState<PredictionRequest>(
    {
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
    }
  );

  const [predictionResponse, setPredictionResponse] =
    useState<PredictionResponse | null>(null);
  const [predictionLoading, setPredictionLoading] = useState(false);
  const [predictionError, setPredictionError] = useState<string | null>(null);

  const handleInputChange = (
    field: keyof AnalyticsRequest,
    value:
      | string
      | AnalyticsRequest["metrics"]
      | AnalyticsRequest["time_period"]
  ) => {
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
        [metric]: !prev.metrics[metric],
      },
    }));
  };

  const handleAnalyze = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

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
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setLoading(false);
    }
  };

  const handlePredictionInputChange = (
    section: "creator_profile" | "campaign_details",
    field: string,
    value: string | number | string[]
  ) => {
    setPredictionRequest((prev) => ({
      ...prev,
      [section]: {
        ...prev[section],
        [field]: value,
      },
    }));
  };

  const handlePredict = async (e: React.FormEvent) => {
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
    } catch (err) {
      setPredictionError(
        err instanceof Error ? err.message : "An error occurred"
      );
    } finally {
      setPredictionLoading(false);
    }
  };

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
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-8">Campaign Analytics</h1>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Form Section */}
        <div className="lg:col-span-1">
          <div className="bg-white shadow-md rounded-lg p-6">
            <form onSubmit={handleAnalyze} className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Campaign ID
                </label>
                <input
                  type="text"
                  value={analyticsRequest.campaign_id}
                  onChange={(e) =>
                    handleInputChange("campaign_id", e.target.value)
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Metrics to Analyze
                </label>
                <div className="space-y-2">
                  {Object.entries(analyticsRequest.metrics).map(
                    ([metric, enabled]) => (
                      <label
                        key={metric}
                        className="flex items-center space-x-2"
                      >
                        <input
                          type="checkbox"
                          checked={enabled}
                          onChange={() =>
                            handleMetricChange(
                              metric as keyof AnalyticsRequest["metrics"]
                            )
                          }
                          className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                        />
                        <span className="text-sm text-gray-700 capitalize">
                          {metric.replace(/_/g, " ")}
                        </span>
                      </label>
                    )
                  )}
                </div>
              </div>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Start Date
                  </label>
                  <input
                    type="date"
                    value={analyticsRequest.time_period.start_date}
                    onChange={(e) =>
                      handleInputChange("time_period", {
                        ...analyticsRequest.time_period,
                        start_date: e.target.value,
                      })
                    }
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    End Date
                  </label>
                  <input
                    type="date"
                    value={analyticsRequest.time_period.end_date}
                    onChange={(e) =>
                      handleInputChange("time_period", {
                        ...analyticsRequest.time_period,
                        end_date: e.target.value,
                      })
                    }
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    required
                  />
                </div>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50"
              >
                {loading ? "Analyzing..." : "Analyze Campaign"}
              </button>
            </form>
          </div>
        </div>

        {/* Results Section */}
        <div className="lg:col-span-2">
          <div className="bg-white shadow-md rounded-lg">
            {error ? (
              <div className="p-6">
                <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md">
                  {error}
                </div>
              </div>
            ) : analyticsResponse ? (
              <div>
                {/* Tabs */}
                <div className="border-b border-gray-200">
                  <nav className="flex space-x-8 px-6" aria-label="Tabs">
                    <button
                      onClick={() => setActiveTab("overview")}
                      className={`${
                        activeTab === "overview"
                          ? "border-blue-500 text-blue-600"
                          : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
                      } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
                    >
                      Overview
                    </button>
                    <button
                      onClick={() => setActiveTab("details")}
                      className={`${
                        activeTab === "details"
                          ? "border-blue-500 text-blue-600"
                          : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
                      } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
                    >
                      Detailed Metrics
                    </button>
                    <button
                      onClick={() => setActiveTab("recommendations")}
                      className={`${
                        activeTab === "recommendations"
                          ? "border-blue-500 text-blue-600"
                          : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
                      } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
                    >
                      Recommendations
                    </button>
                    <button
                      onClick={() => setActiveTab("prediction")}
                      className={`${
                        activeTab === "prediction"
                          ? "border-blue-500 text-blue-600"
                          : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
                      } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
                    >
                      Performance Prediction
                    </button>
                  </nav>
                </div>

                <div className="p-6">
                  {activeTab === "overview" && (
                    <div className="space-y-6">
                      <div>
                        <h2 className="text-xl font-semibold text-gray-800 mb-2">
                          {analyticsResponse.campaign_name}
                        </h2>
                        <p className="text-sm text-gray-500">
                          Period:{" "}
                          {new Date(
                            analyticsResponse.period.start_date
                          ).toLocaleDateString()}{" "}
                          -{" "}
                          {new Date(
                            analyticsResponse.period.end_date
                          ).toLocaleDateString()}
                        </p>
                      </div>

                      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        {analyticsResponse.metrics.reach && (
                          <div className="bg-gray-50 p-4 rounded-lg">
                            <h3 className="text-sm font-medium text-gray-500">
                              Total Reach
                            </h3>
                            <p className="mt-1 text-2xl font-semibold text-gray-900">
                              {formatNumber(
                                analyticsResponse.metrics.reach.total
                              )}
                            </p>
                            <p
                              className={`mt-1 text-sm ${
                                analyticsResponse.metrics.reach.trend >= 0
                                  ? "text-green-600"
                                  : "text-red-600"
                              }`}
                            >
                              {formatPercentage(
                                analyticsResponse.metrics.reach.trend
                              )}
                            </p>
                          </div>
                        )}

                        {analyticsResponse.metrics.engagement && (
                          <div className="bg-gray-50 p-4 rounded-lg">
                            <h3 className="text-sm font-medium text-gray-500">
                              Engagement Rate
                            </h3>
                            <p className="mt-1 text-2xl font-semibold text-gray-900">
                              {analyticsResponse.metrics.engagement.engagement_rate.toFixed(
                                2
                              )}
                              %
                            </p>
                            <p
                              className={`mt-1 text-sm ${
                                analyticsResponse.metrics.engagement.trend >= 0
                                  ? "text-green-600"
                                  : "text-red-600"
                              }`}
                            >
                              {formatPercentage(
                                analyticsResponse.metrics.engagement.trend
                              )}
                            </p>
                          </div>
                        )}

                        {analyticsResponse.metrics.conversions && (
                          <div className="bg-gray-50 p-4 rounded-lg">
                            <h3 className="text-sm font-medium text-gray-500">
                              Conversion Rate
                            </h3>
                            <p className="mt-1 text-2xl font-semibold text-gray-900">
                              {analyticsResponse.metrics.conversions.rate.toFixed(
                                2
                              )}
                              %
                            </p>
                            <p
                              className={`mt-1 text-sm ${
                                analyticsResponse.metrics.conversions.trend >= 0
                                  ? "text-green-600"
                                  : "text-red-600"
                              }`}
                            >
                              {formatPercentage(
                                analyticsResponse.metrics.conversions.trend
                              )}
                            </p>
                          </div>
                        )}
                      </div>

                      <div className="mt-6">
                        <h3 className="text-lg font-medium text-gray-900 mb-3">
                          Best Performing Content
                        </h3>
                        <ul className="space-y-2">
                          {analyticsResponse.summary.best_performing_content.map(
                            (content, index) => (
                              <li
                                key={index}
                                className="flex items-start space-x-3 text-sm text-gray-600"
                              >
                                <span className="flex-shrink-0 w-5 h-5 flex items-center justify-center bg-blue-100 text-blue-600 rounded-full">
                                  {index + 1}
                                </span>
                                <span>{content}</span>
                              </li>
                            )
                          )}
                        </ul>
                      </div>
                    </div>
                  )}

                  {activeTab === "details" && (
                    <div className="space-y-6">
                      {analyticsResponse.metrics.reach && (
                        <div>
                          <h3 className="text-lg font-medium text-gray-900 mb-3">
                            Reach Metrics
                          </h3>
                          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                            <div className="bg-gray-50 p-4 rounded-lg">
                              <h4 className="text-sm font-medium text-gray-500">
                                Organic Reach
                              </h4>
                              <p className="mt-1 text-xl font-semibold text-gray-900">
                                {formatNumber(
                                  analyticsResponse.metrics.reach.organic
                                )}
                              </p>
                            </div>
                            <div className="bg-gray-50 p-4 rounded-lg">
                              <h4 className="text-sm font-medium text-gray-500">
                                Paid Reach
                              </h4>
                              <p className="mt-1 text-xl font-semibold text-gray-900">
                                {formatNumber(
                                  analyticsResponse.metrics.reach.paid
                                )}
                              </p>
                            </div>
                          </div>
                        </div>
                      )}

                      {analyticsResponse.metrics.engagement && (
                        <div>
                          <h3 className="text-lg font-medium text-gray-900 mb-3">
                            Engagement Metrics
                          </h3>
                          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                            <div className="bg-gray-50 p-4 rounded-lg">
                              <h4 className="text-sm font-medium text-gray-500">
                                Likes
                              </h4>
                              <p className="mt-1 text-xl font-semibold text-gray-900">
                                {formatNumber(
                                  analyticsResponse.metrics.engagement.likes
                                )}
                              </p>
                            </div>
                            <div className="bg-gray-50 p-4 rounded-lg">
                              <h4 className="text-sm font-medium text-gray-500">
                                Comments
                              </h4>
                              <p className="mt-1 text-xl font-semibold text-gray-900">
                                {formatNumber(
                                  analyticsResponse.metrics.engagement.comments
                                )}
                              </p>
                            </div>
                            <div className="bg-gray-50 p-4 rounded-lg">
                              <h4 className="text-sm font-medium text-gray-500">
                                Shares
                              </h4>
                              <p className="mt-1 text-xl font-semibold text-gray-900">
                                {formatNumber(
                                  analyticsResponse.metrics.engagement.shares
                                )}
                              </p>
                            </div>
                            <div className="bg-gray-50 p-4 rounded-lg">
                              <h4 className="text-sm font-medium text-gray-500">
                                Saves
                              </h4>
                              <p className="mt-1 text-xl font-semibold text-gray-900">
                                {formatNumber(
                                  analyticsResponse.metrics.engagement.saves
                                )}
                              </p>
                            </div>
                          </div>
                        </div>
                      )}

                      <div>
                        <h3 className="text-lg font-medium text-gray-900 mb-3">
                          Audience Demographics
                        </h3>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                          <div>
                            <h4 className="text-sm font-medium text-gray-500 mb-2">
                              Age Groups
                            </h4>
                            <div className="space-y-2">
                              {Object.entries(
                                analyticsResponse.summary.audience_demographics
                                  .age_groups
                              ).map(([age, percentage]) => (
                                <div key={age} className="flex items-center">
                                  <div className="w-24 text-sm text-gray-600">
                                    {age}
                                  </div>
                                  <div className="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden">
                                    <div
                                      className="h-full bg-blue-600 rounded-full"
                                      style={{ width: `${percentage}%` }}
                                    />
                                  </div>
                                  <div className="w-12 text-sm text-gray-600 text-right">
                                    {percentage}%
                                  </div>
                                </div>
                              ))}
                            </div>
                          </div>
                          <div>
                            <h4 className="text-sm font-medium text-gray-500 mb-2">
                              Top Locations
                            </h4>
                            <div className="space-y-2">
                              {Object.entries(
                                analyticsResponse.summary.audience_demographics
                                  .locations
                              )
                                .slice(0, 5)
                                .map(([location, percentage]) => (
                                  <div
                                    key={location}
                                    className="flex items-center"
                                  >
                                    <div className="flex-1 text-sm text-gray-600">
                                      {location}
                                    </div>
                                    <div className="w-12 text-sm text-gray-600 text-right">
                                      {percentage}%
                                    </div>
                                  </div>
                                ))}
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  )}

                  {activeTab === "recommendations" && (
                    <div className="space-y-6">
                      <div>
                        <h3 className="text-lg font-medium text-gray-900 mb-3">
                          Campaign Recommendations
                        </h3>
                        <ul className="space-y-4">
                          {analyticsResponse.summary.recommendations.map(
                            (recommendation, index) => (
                              <li
                                key={index}
                                className="flex items-start space-x-3"
                              >
                                <span className="flex-shrink-0 w-6 h-6 flex items-center justify-center bg-blue-100 text-blue-600 rounded-full">
                                  {index + 1}
                                </span>
                                <p className="text-gray-600">
                                  {recommendation}
                                </p>
                              </li>
                            )
                          )}
                        </ul>
                      </div>

                      <div>
                        <h3 className="text-lg font-medium text-gray-900 mb-3">
                          Audience Interests
                        </h3>
                        <div className="flex flex-wrap gap-2">
                          {analyticsResponse.summary.audience_demographics.interests.map(
                            (interest, index) => (
                              <span
                                key={index}
                                className="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm"
                              >
                                {interest}
                              </span>
                            )
                          )}
                        </div>
                      </div>
                    </div>
                  )}

                  {activeTab === "prediction" && (
                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                      {/* Prediction Form */}
                      <div className="lg:col-span-1">
                        <div className="bg-white shadow-md rounded-lg p-6">
                          <form onSubmit={handlePredict} className="space-y-6">
                            <div>
                              <h3 className="text-lg font-medium text-gray-900 mb-4">
                                Creator Profile
                              </h3>
                              <div className="space-y-4">
                                <div>
                                  <label className="block text-sm font-medium text-gray-700">
                                    Creator ID
                                  </label>
                                  <input
                                    type="text"
                                    value={
                                      predictionRequest.creator_profile
                                        .creator_id
                                    }
                                    onChange={(e) =>
                                      handlePredictionInputChange(
                                        "creator_profile",
                                        "creator_id",
                                        e.target.value
                                      )
                                    }
                                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                                    required
                                  />
                                </div>
                                <div>
                                  <label className="block text-sm font-medium text-gray-700">
                                    Name
                                  </label>
                                  <input
                                    type="text"
                                    value={
                                      predictionRequest.creator_profile.name
                                    }
                                    onChange={(e) =>
                                      handlePredictionInputChange(
                                        "creator_profile",
                                        "name",
                                        e.target.value
                                      )
                                    }
                                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                                    required
                                  />
                                </div>
                                <div>
                                  <label className="block text-sm font-medium text-gray-700">
                                    Platform
                                  </label>
                                  <select
                                    value={
                                      predictionRequest.creator_profile.platform
                                    }
                                    onChange={(e) =>
                                      handlePredictionInputChange(
                                        "creator_profile",
                                        "platform",
                                        e.target.value
                                      )
                                    }
                                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                                    required
                                  >
                                    <option value="Instagram">Instagram</option>
                                    <option value="TikTok">TikTok</option>
                                    <option value="YouTube">YouTube</option>
                                    <option value="Pinterest">Pinterest</option>
                                  </select>
                                </div>
                                <div>
                                  <label className="block text-sm font-medium text-gray-700">
                                    Followers
                                  </label>
                                  <input
                                    type="number"
                                    value={
                                      predictionRequest.creator_profile
                                        .followers
                                    }
                                    onChange={(e) =>
                                      handlePredictionInputChange(
                                        "creator_profile",
                                        "followers",
                                        parseInt(e.target.value)
                                      )
                                    }
                                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                                    required
                                  />
                                </div>
                                <div>
                                  <label className="block text-sm font-medium text-gray-700">
                                    Engagement Rate (%)
                                  </label>
                                  <input
                                    type="number"
                                    step="0.1"
                                    value={
                                      predictionRequest.creator_profile
                                        .engagement_rate
                                    }
                                    onChange={(e) =>
                                      handlePredictionInputChange(
                                        "creator_profile",
                                        "engagement_rate",
                                        parseFloat(e.target.value)
                                      )
                                    }
                                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                                    required
                                  />
                                </div>
                              </div>
                            </div>

                            <div>
                              <h3 className="text-lg font-medium text-gray-900 mb-4">
                                Campaign Details
                              </h3>
                              <div className="space-y-4">
                                <div>
                                  <label className="block text-sm font-medium text-gray-700">
                                    Campaign ID
                                  </label>
                                  <input
                                    type="text"
                                    value={
                                      predictionRequest.campaign_details
                                        .campaign_id
                                    }
                                    onChange={(e) =>
                                      handlePredictionInputChange(
                                        "campaign_details",
                                        "campaign_id",
                                        e.target.value
                                      )
                                    }
                                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                                    required
                                  />
                                </div>
                                <div>
                                  <label className="block text-sm font-medium text-gray-700">
                                    Brand Name
                                  </label>
                                  <input
                                    type="text"
                                    value={
                                      predictionRequest.campaign_details
                                        .brand_name
                                    }
                                    onChange={(e) =>
                                      handlePredictionInputChange(
                                        "campaign_details",
                                        "brand_name",
                                        e.target.value
                                      )
                                    }
                                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                                    required
                                  />
                                </div>
                                <div>
                                  <label className="block text-sm font-medium text-gray-700">
                                    Campaign Name
                                  </label>
                                  <input
                                    type="text"
                                    value={
                                      predictionRequest.campaign_details
                                        .campaign_name
                                    }
                                    onChange={(e) =>
                                      handlePredictionInputChange(
                                        "campaign_details",
                                        "campaign_name",
                                        e.target.value
                                      )
                                    }
                                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                                    required
                                  />
                                </div>
                                <div>
                                  <label className="block text-sm font-medium text-gray-700">
                                    Target Audience
                                  </label>
                                  <textarea
                                    value={
                                      predictionRequest.campaign_details
                                        .target_audience
                                    }
                                    onChange={(e) =>
                                      handlePredictionInputChange(
                                        "campaign_details",
                                        "target_audience",
                                        e.target.value
                                      )
                                    }
                                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                                    rows={3}
                                    required
                                  />
                                </div>
                                <div>
                                  <label className="block text-sm font-medium text-gray-700">
                                    Budget Range
                                  </label>
                                  <input
                                    type="text"
                                    value={
                                      predictionRequest.campaign_details
                                        .budget_range
                                    }
                                    onChange={(e) =>
                                      handlePredictionInputChange(
                                        "campaign_details",
                                        "budget_range",
                                        e.target.value
                                      )
                                    }
                                    placeholder="$3000-7000"
                                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                                    required
                                  />
                                </div>
                                <div>
                                  <label className="block text-sm font-medium text-gray-700">
                                    Timeline
                                  </label>
                                  <input
                                    type="text"
                                    value={
                                      predictionRequest.campaign_details
                                        .timeline
                                    }
                                    onChange={(e) =>
                                      handlePredictionInputChange(
                                        "campaign_details",
                                        "timeline",
                                        e.target.value
                                      )
                                    }
                                    placeholder="30 days"
                                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                                    required
                                  />
                                </div>
                                <div>
                                  <label className="block text-sm font-medium text-gray-700">
                                    Platforms
                                  </label>
                                  <select
                                    multiple
                                    value={
                                      predictionRequest.campaign_details
                                        .platforms
                                    }
                                    onChange={(e) =>
                                      handlePredictionInputChange(
                                        "campaign_details",
                                        "platforms",
                                        Array.from(
                                          e.target.selectedOptions,
                                          (option) => option.value
                                        )
                                      )
                                    }
                                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                                    required
                                  >
                                    <option value="Instagram">Instagram</option>
                                    <option value="TikTok">TikTok</option>
                                    <option value="YouTube">YouTube</option>
                                    <option value="Pinterest">Pinterest</option>
                                  </select>
                                </div>
                                <div>
                                  <label className="block text-sm font-medium text-gray-700">
                                    Content Types
                                  </label>
                                  <select
                                    multiple
                                    value={
                                      predictionRequest.campaign_details
                                        .content_types
                                    }
                                    onChange={(e) =>
                                      handlePredictionInputChange(
                                        "campaign_details",
                                        "content_types",
                                        Array.from(
                                          e.target.selectedOptions,
                                          (option) => option.value
                                        )
                                      )
                                    }
                                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                                    required
                                  >
                                    <option value="unboxing">Unboxing</option>
                                    <option value="outfit_ideas">
                                      Outfit Ideas
                                    </option>
                                    <option value="sustainability_tips">
                                      Sustainability Tips
                                    </option>
                                    <option value="tutorial">Tutorial</option>
                                    <option value="review">Review</option>
                                  </select>
                                </div>
                                <div>
                                  <label className="block text-sm font-medium text-gray-700">
                                    Campaign Goals
                                  </label>
                                  <select
                                    multiple
                                    value={
                                      predictionRequest.campaign_details
                                        .campaign_goals
                                    }
                                    onChange={(e) =>
                                      handlePredictionInputChange(
                                        "campaign_details",
                                        "campaign_goals",
                                        Array.from(
                                          e.target.selectedOptions,
                                          (option) => option.value
                                        )
                                      )
                                    }
                                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                                    required
                                  >
                                    <option value="brand_awareness">
                                      Brand Awareness
                                    </option>
                                    <option value="social_engagement">
                                      Social Engagement
                                    </option>
                                    <option value="website_traffic">
                                      Website Traffic
                                    </option>
                                    <option value="sales">Sales</option>
                                    <option value="lead_generation">
                                      Lead Generation
                                    </option>
                                  </select>
                                </div>
                              </div>
                            </div>

                            <button
                              type="submit"
                              disabled={predictionLoading}
                              className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50"
                            >
                              {predictionLoading
                                ? "Predicting..."
                                : "Predict Performance"}
                            </button>
                          </form>
                        </div>
                      </div>

                      {/* Prediction Results */}
                      <div className="lg:col-span-2">
                        <div className="bg-white shadow-md rounded-lg p-6">
                          {predictionError ? (
                            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md">
                              {predictionError}
                            </div>
                          ) : predictionResponse ? (
                            <div className="space-y-6">
                              <div>
                                <h3 className="text-lg font-medium text-gray-900 mb-4">
                                  Performance Predictions
                                </h3>
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                  {predictionResponse.predictions.map(
                                    (prediction, index) => (
                                      <div
                                        key={index}
                                        className="bg-gray-50 p-4 rounded-lg"
                                      >
                                        <h4 className="text-sm font-medium text-gray-500 capitalize">
                                          {prediction.metric.replace(/_/g, " ")}
                                        </h4>
                                        <p className="mt-1 text-2xl font-semibold text-gray-900">
                                          {formatNumber(
                                            prediction.predicted_value
                                          )}
                                        </p>
                                        <p className="mt-1 text-sm text-gray-600">
                                          Confidence:{" "}
                                          {(
                                            prediction.confidence_score * 100
                                          ).toFixed(1)}
                                          %
                                        </p>
                                        <div className="mt-2">
                                          <p className="text-xs text-gray-500">
                                            Factors Considered:
                                          </p>
                                          <ul className="mt-1 space-y-1">
                                            {prediction.factors_considered.map(
                                              (factor, i) => (
                                                <li
                                                  key={i}
                                                  className="text-xs text-gray-600"
                                                >
                                                  • {factor}
                                                </li>
                                              )
                                            )}
                                          </ul>
                                        </div>
                                      </div>
                                    )
                                  )}
                                </div>
                              </div>

                              <div>
                                <h3 className="text-lg font-medium text-gray-900 mb-4">
                                  Recommendations
                                </h3>
                                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                  <div>
                                    <h4 className="text-sm font-medium text-gray-500 mb-2">
                                      Content Strategy
                                    </h4>
                                    <ul className="space-y-2">
                                      {predictionResponse.recommendations.content_strategy.map(
                                        (rec, index) => (
                                          <li
                                            key={index}
                                            className="text-sm text-gray-600"
                                          >
                                            • {rec}
                                          </li>
                                        )
                                      )}
                                    </ul>
                                  </div>
                                  <div>
                                    <h4 className="text-sm font-medium text-gray-500 mb-2">
                                      Audience Targeting
                                    </h4>
                                    <ul className="space-y-2">
                                      {predictionResponse.recommendations.audience_targeting.map(
                                        (rec, index) => (
                                          <li
                                            key={index}
                                            className="text-sm text-gray-600"
                                          >
                                            • {rec}
                                          </li>
                                        )
                                      )}
                                    </ul>
                                  </div>
                                  <div>
                                    <h4 className="text-sm font-medium text-gray-500 mb-2">
                                      Budget Allocation
                                    </h4>
                                    <ul className="space-y-2">
                                      {predictionResponse.recommendations.budget_allocation.map(
                                        (rec, index) => (
                                          <li
                                            key={index}
                                            className="text-sm text-gray-600"
                                          >
                                            • {rec}
                                          </li>
                                        )
                                      )}
                                    </ul>
                                  </div>
                                </div>
                              </div>
                            </div>
                          ) : (
                            <div className="text-center text-gray-500">
                              {predictionLoading ? (
                                <div className="flex items-center justify-center">
                                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                                </div>
                              ) : (
                                "Fill out the form to predict campaign performance"
                              )}
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            ) : (
              <div className="p-6 text-center text-gray-500">
                {loading ? (
                  <div className="flex items-center justify-center">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                  </div>
                ) : (
                  "Fill out the form to analyze campaign performance"
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
