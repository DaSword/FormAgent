import { FileUpload } from "@/components/FileUpload";

export default function Home() {
  return (
    <main className="min-h-screen bg-gray-50 flex flex-col items-center justify-center p-4">
      <div className="text-center mb-8">
        <h1 className="text-4xl font-extrabold text-gray-900 tracking-tight mb-2">
          FormFiller Agent
        </h1>
        <p className="text-lg text-gray-600">
          Upload your documents (Invoices, Contracts) to extract structured data.
        </p>
      </div>

      <FileUpload />
    </main>
  );
}
