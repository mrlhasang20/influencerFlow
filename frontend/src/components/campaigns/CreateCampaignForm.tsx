"use client";

import { Formik, Form, Field, FieldArray } from "formik";
import * as Yup from "yup";
import axios from "axios";
import toast from "react-hot-toast";
import { useState } from "react";
import { PlusIcon, TrashIcon } from "@heroicons/react/24/outline";

const PLATFORM_OPTIONS = [
  "Instagram",
  "TikTok",
  "Pinterest",
  "YouTube",
  "Twitter",
];
const CONTENT_TYPE_OPTIONS = [
  "unboxing",
  "outfit_ideas",
  "sustainability_tips",
  "tutorial",
  "review",
];
const CAMPAIGN_GOAL_OPTIONS = [
  "brand_awareness",
  "social_engagement",
  "website_traffic",
  "sales",
  "lead_generation",
];
const BUDGET_RANGES = [
  "Under $1,000",
  "$1,000 - $5,000",
  "$5,000 - $10,000",
  "$10,000 - $25,000",
  "$25,000+",
];

const validationSchema = Yup.object().shape({
  brand_name: Yup.string().required("Brand name is required"),
  campaign_name: Yup.string().required("Campaign name is required"),
  target_audience: Yup.string().required("Target audience is required"),
  budget_range: Yup.string().required("Budget range is required"),
  timeline: Yup.string().required("Timeline is required"),
  platforms: Yup.array().min(1, "Select at least one platform"),
  content_types: Yup.array().min(1, "Select at least one content type"),
  campaign_goals: Yup.array().min(1, "Select at least one campaign goal"),
  deliverables: Yup.array()
    .of(
      Yup.object().shape({
        type: Yup.string().required("Type is required"),
        description: Yup.string().required("Description is required"),
        quantity: Yup.number()
          .required("Quantity is required")
          .min(1, "Quantity must be at least 1"),
        due_date: Yup.date().required("Due date is required"),
      })
    )
    .min(1, "Add at least one deliverable"),
  start_date: Yup.date().required("Start date is required"),
  end_date: Yup.date()
    .required("End date is required")
    .min(Yup.ref("start_date"), "End date must be after start date"),
});

const initialValues = {
  brand_name: "",
  campaign_name: "",
  target_audience: "",
  budget_range: "",
  timeline: "",
  platforms: [],
  content_types: [],
  campaign_goals: [],
  deliverables: [{ type: "", description: "", quantity: 1, due_date: "" }],
  start_date: "",
  end_date: "",
};

export function CreateCampaignForm() {
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (values: typeof initialValues) => {
    setIsSubmitting(true);
    try {
      await axios.post("http://localhost:8000/api/v1/campaigns", values);
      toast.success("Campaign created successfully!");
      // Reset form or redirect here
    } catch (error) {
      toast.error("Failed to create campaign. Please try again.");
      console.error("Error creating campaign:", error);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Formik
      initialValues={initialValues}
      validationSchema={validationSchema}
      onSubmit={handleSubmit}
    >
      {({ values, errors, touched }) => (
        <Form className="space-y-8 divide-y divide-gray-200 bg-white p-6 rounded-lg shadow">
          {/* General Information Section */}
          <div className="space-y-6">
            <h2 className="text-xl font-semibold text-gray-900">
              General Information
            </h2>
            <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
              <div>
                <label
                  htmlFor="brand_name"
                  className="block text-sm font-medium text-gray-700"
                >
                  Brand Name
                </label>
                <Field
                  type="text"
                  name="brand_name"
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                />
                {errors.brand_name && touched.brand_name && (
                  <div className="mt-1 text-sm text-red-600">
                    {errors.brand_name}
                  </div>
                )}
              </div>

              <div>
                <label
                  htmlFor="campaign_name"
                  className="block text-sm font-medium text-gray-700"
                >
                  Campaign Name
                </label>
                <Field
                  type="text"
                  name="campaign_name"
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                />
                {errors.campaign_name && touched.campaign_name && (
                  <div className="mt-1 text-sm text-red-600">
                    {errors.campaign_name}
                  </div>
                )}
              </div>

              <div className="sm:col-span-2">
                <label
                  htmlFor="target_audience"
                  className="block text-sm font-medium text-gray-700"
                >
                  Target Audience
                </label>
                <Field
                  as="textarea"
                  name="target_audience"
                  rows={3}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                />
                {errors.target_audience && touched.target_audience && (
                  <div className="mt-1 text-sm text-red-600">
                    {errors.target_audience}
                  </div>
                )}
              </div>

              <div>
                <label
                  htmlFor="budget_range"
                  className="block text-sm font-medium text-gray-700"
                >
                  Budget Range
                </label>
                <Field
                  as="select"
                  name="budget_range"
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                >
                  <option value="">Select a budget range</option>
                  {BUDGET_RANGES.map((range) => (
                    <option key={range} value={range}>
                      {range}
                    </option>
                  ))}
                </Field>
                {errors.budget_range && touched.budget_range && (
                  <div className="mt-1 text-sm text-red-600">
                    {errors.budget_range}
                  </div>
                )}
              </div>

              <div>
                <label
                  htmlFor="timeline"
                  className="block text-sm font-medium text-gray-700"
                >
                  Timeline
                </label>
                <Field
                  type="text"
                  name="timeline"
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                />
                {errors.timeline && touched.timeline && (
                  <div className="mt-1 text-sm text-red-600">
                    {errors.timeline}
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Campaign Details Section */}
          <div className="pt-8 space-y-6">
            <h2 className="text-xl font-semibold text-gray-900">
              Campaign Details
            </h2>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Platforms
                </label>
                <div className="mt-2 space-y-2">
                  {PLATFORM_OPTIONS.map((platform) => (
                    <label
                      key={platform}
                      className="inline-flex items-center mr-4"
                    >
                      <Field
                        type="checkbox"
                        name="platforms"
                        value={platform}
                        className="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
                      />
                      <span className="ml-2 text-sm text-gray-700">
                        {platform}
                      </span>
                    </label>
                  ))}
                </div>
                {errors.platforms && touched.platforms && (
                  <div className="mt-1 text-sm text-red-600">
                    {errors.platforms}
                  </div>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Content Types
                </label>
                <div className="mt-2 space-y-2">
                  {CONTENT_TYPE_OPTIONS.map((type) => (
                    <label key={type} className="inline-flex items-center mr-4">
                      <Field
                        type="checkbox"
                        name="content_types"
                        value={type}
                        className="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
                      />
                      <span className="ml-2 text-sm text-gray-700">
                        {type.replace("_", " ")}
                      </span>
                    </label>
                  ))}
                </div>
                {errors.content_types && touched.content_types && (
                  <div className="mt-1 text-sm text-red-600">
                    {errors.content_types}
                  </div>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Campaign Goals
                </label>
                <div className="mt-2 space-y-2">
                  {CAMPAIGN_GOAL_OPTIONS.map((goal) => (
                    <label key={goal} className="inline-flex items-center mr-4">
                      <Field
                        type="checkbox"
                        name="campaign_goals"
                        value={goal}
                        className="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
                      />
                      <span className="ml-2 text-sm text-gray-700">
                        {goal.replace("_", " ")}
                      </span>
                    </label>
                  ))}
                </div>
                {errors.campaign_goals && touched.campaign_goals && (
                  <div className="mt-1 text-sm text-red-600">
                    {errors.campaign_goals}
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Deliverables Section */}
          <div className="pt-8 space-y-6">
            <h2 className="text-xl font-semibold text-gray-900">
              Deliverables
            </h2>
            <FieldArray name="deliverables">
              {({ push, remove }) => (
                <div className="space-y-4">
                  {values.deliverables.map((_, index) => (
                    <div
                      key={index}
                      className="p-4 border rounded-lg bg-gray-50"
                    >
                      <div className="flex justify-between items-center mb-4">
                        <h3 className="text-lg font-medium text-gray-900">
                          Deliverable {index + 1}
                        </h3>
                        {index > 0 && (
                          <button
                            type="button"
                            onClick={() => remove(index)}
                            className="text-red-600 hover:text-red-800"
                          >
                            <TrashIcon className="h-5 w-5" />
                          </button>
                        )}
                      </div>
                      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                        <div>
                          <label className="block text-sm font-medium text-gray-700">
                            Type
                          </label>
                          <Field
                            type="text"
                            name={`deliverables.${index}.type`}
                            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                          />
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700">
                            Quantity
                          </label>
                          <Field
                            type="number"
                            name={`deliverables.${index}.quantity`}
                            min="1"
                            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                          />
                        </div>
                        <div className="sm:col-span-2">
                          <label className="block text-sm font-medium text-gray-700">
                            Description
                          </label>
                          <Field
                            as="textarea"
                            name={`deliverables.${index}.description`}
                            rows={2}
                            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                          />
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700">
                            Due Date
                          </label>
                          <Field
                            type="date"
                            name={`deliverables.${index}.due_date`}
                            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                          />
                        </div>
                      </div>
                    </div>
                  ))}
                  <button
                    type="button"
                    onClick={() =>
                      push({
                        type: "",
                        description: "",
                        quantity: 1,
                        due_date: "",
                      })
                    }
                    className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-indigo-700 bg-indigo-100 hover:bg-indigo-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                  >
                    <PlusIcon className="h-5 w-5 mr-2" />
                    Add Deliverable
                  </button>
                </div>
              )}
            </FieldArray>
          </div>

          {/* Timeline Section */}
          <div className="pt-8 space-y-6">
            <h2 className="text-xl font-semibold text-gray-900">
              Campaign Timeline
            </h2>
            <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
              <div>
                <label
                  htmlFor="start_date"
                  className="block text-sm font-medium text-gray-700"
                >
                  Start Date
                </label>
                <Field
                  type="date"
                  name="start_date"
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                />
                {errors.start_date && touched.start_date && (
                  <div className="mt-1 text-sm text-red-600">
                    {errors.start_date}
                  </div>
                )}
              </div>

              <div>
                <label
                  htmlFor="end_date"
                  className="block text-sm font-medium text-gray-700"
                >
                  End Date
                </label>
                <Field
                  type="date"
                  name="end_date"
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                />
                {errors.end_date && touched.end_date && (
                  <div className="mt-1 text-sm text-red-600">
                    {errors.end_date}
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Submit Button */}
          <div className="pt-8">
            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full flex justify-center py-3 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isSubmitting ? "Creating Campaign..." : "Create Campaign"}
            </button>
          </div>
        </Form>
      )}
    </Formik>
  );
}
