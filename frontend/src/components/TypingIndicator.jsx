export default function TypingIndicator() {
  return (
    <div className="flex justify-start mb-4">
      <div className="bg-white border border-gray-200 rounded-2xl rounded-bl-md px-4 py-3 shadow-sm">
        <div className="flex items-center gap-1.5">
          <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce-dot" />
          <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce-dot animate-bounce-dot-delay-1" />
          <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce-dot animate-bounce-dot-delay-2" />
        </div>
      </div>
    </div>
  )
}
