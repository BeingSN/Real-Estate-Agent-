import PropertyCard from './PropertyCard'

function CriteriaPills({ criteria }) {
  if (!criteria || criteria.is_unclear) return null

  const pills = []
  if (criteria.city) pills.push(`City: ${criteria.city}`)
  if (criteria.district) pills.push(`District: ${criteria.district}`)
  if (criteria.property_type) pills.push(`Type: ${criteria.property_type}`)
  if (criteria.purpose) pills.push(criteria.purpose)
  if (criteria.max_price)
    pills.push(`Budget: ≤${criteria.max_price.toLocaleString()} SAR`)
  if (criteria.min_bedrooms) pills.push(`${criteria.min_bedrooms}+ beds`)
  if (criteria.furnishing) pills.push(criteria.furnishing)
  if (criteria.parking_required) pills.push('Parking required')

  if (pills.length === 0) return null

  return (
    <div className="flex flex-wrap gap-1.5 mt-2">
      {pills.map((pill) => (
        <span
          key={pill}
          className="text-xs px-2 py-0.5 rounded-full bg-gray-100 text-gray-500"
        >
          {pill}
        </span>
      ))}
    </div>
  )
}

export default function MessageBubble({ message }) {
  const isUser = message.role === 'user'

  if (isUser) {
    return (
      <div className="flex justify-end mb-4">
        <div className="bg-navy text-white rounded-2xl rounded-br-md px-4 py-3 max-w-[75%] shadow-sm">
          <p className="text-sm whitespace-pre-wrap">{message.content}</p>
        </div>
      </div>
    )
  }

  return (
    <div className="flex justify-start mb-4">
      <div className="max-w-[85%]">
        <div className="bg-white border border-gray-200 rounded-2xl rounded-bl-md px-4 py-3 shadow-sm">
          <p className="text-sm text-gray-800 whitespace-pre-wrap">
            {message.content}
          </p>
          <CriteriaPills criteria={message.extractedCriteria} />
        </div>
        {message.recommendations?.length > 0 && (
          <div className="grid gap-3 mt-3">
            {message.recommendations.map((property) => (
              <PropertyCard key={property.id} property={property} />
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
