export default function PropertyCard({ property }) {
  return (
    <div className="bg-white border border-gray-200 rounded-xl p-4 shadow-sm hover:-translate-y-0.5 hover:shadow-md transition-all duration-200">
      <h3 className="font-semibold text-gray-900">{property.title}</h3>
      <p className="text-sm text-gray-500 mt-0.5">
        {property.district}, {property.city}
      </p>
      <p className="text-xl font-bold text-gold mt-2">
        {property.price.toLocaleString()} {property.price_unit}
      </p>
      <div className="flex items-center gap-4 text-sm text-gray-600 mt-2">
        <span>🛏 {property.bedrooms} bed</span>
        <span>🚿 {property.bathrooms} bath</span>
        <span>📐 {property.area_sqm} sqm</span>
      </div>
      <div className="flex flex-wrap gap-2 mt-3">
        <span className="text-xs px-2 py-1 rounded-full bg-gray-100 text-gray-700">
          {property.furnishing}
        </span>
        <span
          className={`text-xs px-2 py-1 rounded-full ${
            property.parking
              ? 'bg-green-100 text-green-700'
              : 'bg-gray-100 text-gray-500'
          }`}
        >
          {property.parking ? 'Parking ✓' : 'No parking'}
        </span>
        <span className="text-xs px-2 py-1 rounded-full bg-navy/10 text-navy">
          {property.property_type}
        </span>
      </div>
      <hr className="my-3 border-gray-100" />
      <p className="text-sm text-gray-600 italic">{property.reasons}</p>
    </div>
  )
}
