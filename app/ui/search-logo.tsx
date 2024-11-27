import { DocumentMagnifyingGlassIcon } from '@heroicons/react/24/outline';


export default function SearchLogo() {
  return (
    <div
      className={`flex flex-row items-center leading-none text-white`}
    >
    <DocumentMagnifyingGlassIcon className="h-12 w-12" />
      <p className="text-[44px]">Search</p>
    </div>
  );
}
