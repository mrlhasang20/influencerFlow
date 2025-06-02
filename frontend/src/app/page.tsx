import Link from "next/link";

export default function Home() {
  return (
    <main className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="text-center">
        <h1 className="text-4xl font-bold tracking-tight text-gray-900 sm:text-6xl">
          InfluencerFlow
        </h1>
        <p className="mt-6 text-lg leading-8 text-gray-600">
          Create and manage your influencer marketing campaigns with ease
        </p>
        <div className="mt-10 flex items-center justify-center gap-x-6">
          <Link
            href="/campaigns/create"
            className="rounded-md bg-indigo-600 px-3.5 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
          >
            Create Campaign
          </Link>
          <Link
            href="/campaigns"
            className="text-sm font-semibold leading-6 text-gray-900"
          >
            View Campaigns <span aria-hidden="true">→</span>
          </Link>
        </div>
      </div>
    </main>
  );
}
// app/page.tsx
export default function Home() {
  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold">Welcome to InfluencerFlow</h1>
      <p className="mt-4 text-gray-600">
        Manage your influencer marketing campaigns efficiently.
      </p>
    </div>
  );
}