import { NextResponse } from "next/server";

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

function formatDate(dateString: string): string {
  return new Date(dateString).toLocaleDateString("en-US", {
    year: "numeric",
    month: "long",
    day: "numeric",
  });
}

function generateContractText(dealTerms: DealTerms): string {
  const {
    brand_name,
    influencer_name,
    platform,
    campaign_name,
    total_fee,
    deliverables,
    start_date,
    end_date,
  } = dealTerms;

  const formattedStartDate = formatDate(start_date);
  const formattedEndDate = formatDate(end_date);

  const deliverablesList = deliverables
    .map(
      (deliverable, index) => `
${index + 1}. ${deliverable.type} (Quantity: ${deliverable.quantity})
   Description: ${deliverable.description}
   Due Date: ${formatDate(deliverable.due_date)}`
    )
    .join("\n");

  return `INFLUENCER MARKETING AGREEMENT

This Agreement is made and entered into on ${formattedStartDate} by and between:

${brand_name} ("Brand")
and
${influencer_name} ("Influencer")

WHEREAS, Brand desires to engage Influencer for marketing services related to the campaign "${campaign_name}" on the ${platform} platform;

NOW, THEREFORE, in consideration of the mutual promises and covenants contained herein, the parties agree as follows:

1. CAMPAIGN DETAILS
   Campaign Name: ${campaign_name}
   Platform: ${platform}
   Campaign Period: ${formattedStartDate} to ${formattedEndDate}
   Total Compensation: $${total_fee.toLocaleString()}

2. DELIVERABLES
   The Influencer agrees to provide the following deliverables:
${deliverablesList}

3. COMPENSATION
   The Brand agrees to pay the Influencer a total fee of $${total_fee.toLocaleString()} for the services rendered under this Agreement.
   Payment Schedule:
   - 50% ($${(total_fee * 0.5).toLocaleString()}) upon signing of this Agreement
   - 50% ($${(
     total_fee * 0.5
   ).toLocaleString()}) upon completion of all deliverables

4. CONTENT GUIDELINES
   - All content must be original and created specifically for this campaign
   - Content must comply with ${platform}'s terms of service
   - Brand reserves the right to review and approve all content before posting
   - Influencer must disclose the sponsored nature of the content as per FTC guidelines

5. INTELLECTUAL PROPERTY
   - Brand grants Influencer a limited license to use Brand's trademarks and materials for the campaign
   - Influencer retains ownership of their content, but grants Brand a perpetual license to use the content
   - Brand may repurpose the content for marketing purposes with proper attribution

6. CONFIDENTIALITY
   - Influencer agrees to keep all campaign details and Brand information confidential
   - This obligation survives the termination of this Agreement

7. TERMINATION
   - Either party may terminate this Agreement with 30 days written notice
   - Brand may terminate immediately for breach of content guidelines
   - Upon termination, Influencer will be compensated for completed deliverables

8. GOVERNING LAW
   This Agreement shall be governed by and construed in accordance with the laws of the state of [State], without regard to its conflict of law principles.

IN WITNESS WHEREOF, the parties have executed this Agreement as of the date first written above.

BRAND:
${brand_name}
By: ________________________
Date: ${formattedStartDate}

INFLUENCER:
${influencer_name}
By: ________________________
Date: ${formattedStartDate}

Contract ID: ${generateContractId()}
Generated on: ${new Date().toISOString()}`;
}

function generateContractId(): string {
  const timestamp = Date.now().toString(36);
  const randomStr = Math.random().toString(36).substring(2, 8);
  return `CONTRACT-${timestamp}-${randomStr}`.toUpperCase();
}

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const { deal_terms } = body as { deal_terms: DealTerms };

    // Validate required fields
    if (
      !deal_terms.brand_name ||
      !deal_terms.influencer_name ||
      !deal_terms.platform
    ) {
      return NextResponse.json(
        { error: "Missing required fields" },
        { status: 400 }
      );
    }

    // Validate dates
    const startDate = new Date(deal_terms.start_date);
    const endDate = new Date(deal_terms.end_date);
    if (isNaN(startDate.getTime()) || isNaN(endDate.getTime())) {
      return NextResponse.json(
        { error: "Invalid date format" },
        { status: 400 }
      );
    }
    if (endDate < startDate) {
      return NextResponse.json(
        { error: "End date must be after start date" },
        { status: 400 }
      );
    }

    // Validate deliverables
    if (!deal_terms.deliverables.length) {
      return NextResponse.json(
        { error: "At least one deliverable is required" },
        { status: 400 }
      );
    }

    // Validate deliverable dates
    for (const deliverable of deal_terms.deliverables) {
      const dueDate = new Date(deliverable.due_date);
      if (isNaN(dueDate.getTime())) {
        return NextResponse.json(
          { error: "Invalid deliverable due date" },
          { status: 400 }
        );
      }
      if (dueDate < startDate || dueDate > endDate) {
        return NextResponse.json(
          { error: "Deliverable due date must be within campaign period" },
          { status: 400 }
        );
      }
    }

    // Generate contract
    const contractId = generateContractId();
    const contractText = generateContractText(deal_terms);

    const response: ContractResponse = {
      contract_text: contractText,
      contract_id: contractId,
      status: "draft", // Initially set as draft, can be updated to final after review
      generated_at: new Date().toISOString(),
    };

    return NextResponse.json(response);
  } catch (error) {
    console.error("Contract generation error:", error);
    return NextResponse.json(
      { error: "Failed to generate contract" },
      { status: 500 }
    );
  }
}
