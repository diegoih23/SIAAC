import { useEffect } from "react";
import { MapContainer, Marker, TileLayer, useMap, useMapEvents } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

const DEFAULT_CENTER = [-3.99313, -79.20422]; // Loja, Ecuador
const markerIcon = L.divIcon({
  className: "siaac-map-marker",
  html: "<span></span>",
  iconSize: [24, 24],
  iconAnchor: [12, 12],
});

function MapClickHandler({ onSelect }) {
  useMapEvents({
    click: (event) => onSelect(event.latlng.lat, event.latlng.lng),
  });
  return null;
}

function MapPosition({ position }) {
  const map = useMap();
  useEffect(() => {
    if (position) map.setView(position, Math.max(map.getZoom(), 15));
  }, [map, position]);
  return null;
}

export default function LocationPicker({ latitude, longitude, onChange }) {
  const position = latitude !== "" && longitude !== ""
    ? [Number(latitude), Number(longitude)]
    : null;
  const center = position || DEFAULT_CENTER;

  const useCurrentLocation = () => {
    if (!navigator.geolocation) return;
    navigator.geolocation.getCurrentPosition(({ coords }) => {
      onChange(coords.latitude.toFixed(6), coords.longitude.toFixed(6));
    });
  };

  return (
    <div className="location-picker form-field-wide">
      <div className="location-picker-heading">
        <div>
          <strong>Ubicación de la zona</strong>
          <small>Haz clic en el mapa o arrastra el marcador para elegir la ubicación exacta.</small>
        </div>
        <button type="button" className="btn btn-ghost" onClick={useCurrentLocation}>
          Usar mi ubicación
        </button>
      </div>
      <MapContainer center={center} zoom={position ? 15 : 12} scrollWheelZoom className="location-map">
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <MapClickHandler onSelect={(lat, lng) => onChange(lat.toFixed(6), lng.toFixed(6))} />
        <MapPosition position={position} />
        {position && (
          <Marker
            position={position}
            icon={markerIcon}
            draggable
            eventHandlers={{
              dragend: (event) => {
                const marker = event.target.getLatLng();
                onChange(marker.lat.toFixed(6), marker.lng.toFixed(6));
              },
            }}
          />
        )}
      </MapContainer>
      <div className="location-coordinates">
        <span>Latitud: <strong>{latitude || "Selecciona un punto"}</strong></span>
        <span>Longitud: <strong>{longitude || "Selecciona un punto"}</strong></span>
      </div>
    </div>
  );
}
