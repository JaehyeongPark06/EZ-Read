import PDFUpload from "@/components/PDFUpload";

export default function Home() {
  return (
    <main className="w-[90%] flex flex-col justify-center items-center px-4 pt-4 pb-16 max-w-screen-xl m-auto">
      <div className="custom-gradient absolute -top-48 z-10 h-28 w-3/4 max-w-5xl opacity-80 blur-[150px]" />
      <div className="w-full flex flex-col justify-center items-center gap-8">
        <h1 className="text-4xl font-bold gradient-text -skew-x-6 mt-12">
          EZ Read
        </h1>
        <PDFUpload />
      </div>
    </main>
  );
}
