{% load static %}
// var map = L.map('map').setView([-8.5586, 125.5736], 13);

// map tipe
var osm = L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
  // attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
  maxZoom: 19,
  attribution: "© OpenStreetMap",
});

var esw = L.tileLayer(
  "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
  {
    maxZoom: 19,
    attribution:
      "Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community",
  }
);

var gom = L.tileLayer("http://{s}.google.com/vt/lyrs=m&x={x}&y={y}&z={z}", {
  maxZoom: 20,
  subdomains: ["mt0", "mt1", "mt2", "mt3"],
});

var map = L.map("map", {
  center: [-8.5586, 125.5736],
  zoom: 10,
  layers: osm,
  zoomControl: false,
});

var baseLayers = {
  OpenStreetMap: osm,
  EsriWorldImagery: esw,
  GoogleMaps: gom,
};

L.control
  .zoom({
    position: "topright", // Move zoom buttons to top-right
  })
  .addTo(map);

const layerControl = L.control.layers(baseLayers).addTo(map);

var customIcon = L.icon({
  iconUrl: '{% static "leaflet/images/kiosk.png" %}',
  iconSize: [32, 32],
  iconAnchor: [16, 32],
  popupAnchor: [0, -32],
});

fetch("/api/shops/")
  .then((response) => response.json())
  .then((shops) => {
    shops.forEach((shop) => {
      if (shop.latitude && shop.longitude) {
        const marker = L.marker([shop.latitude, shop.longitude], {
          icon: customIcon,
        }).addTo(map);

        marker.on("click", () => {
          // Show the table div
          document.getElementById("shop-details").style.display = "block";
          const panel = document.getElementById("shop-details");
          panel.classList.add("show");

          const locationParts = [
            shop.municipality || "",
            shop.administrativepost || "",
            shop.village || "",
            shop.aldeia || "",
          ]
            .filter((part) => part)
            .join(", ");
          // Fill table fields with shop info
          // document.getElementById('detail-name').textContent = shop.name;
          document.getElementById("detail-owner").textContent =
            shop.owner || "---";
          document.getElementById("detail-name-title").textContent =
            shop.name || "Shop Information";
          document.getElementById("detail-contact").textContent =
            shop.contact || "---";

          document.getElementById("detail-location").textContent =
            locationParts || "---";
          document.getElementById(
            "detail-gmaps"
          ).href = `https://maps.google.com/?q=${shop.latitude},${shop.longitude}`;
          const container = document.getElementById("shop-images");
          container.innerHTML = ""; // clear previous

          if (shop.images && shop.images.length > 0) {
            shop.images.forEach((img) => {
              const imgEl = document.createElement("img");
              imgEl.src = img.url;
              imgEl.style.height = "150px";
              // imgEl.style.border = img.is_primary ? '3px solid green' : '1px solid gray'; // highlight primary
              imgEl.style.objectFit = "cover";
              imgEl.className = "img-fluid mx-1";
              imgEl.style.width = "100%";
              imgEl.style.minWidth = "100%";
              imgEl.style.scrollSnapAlign = "center";
              container.appendChild(imgEl);
            });
          } else {
            // No image, show default placeholder
            const defaultImg = document.createElement("img");
            defaultImg.src = '{% static "img/default.png" %}'; // 👈 Replace with your actual path
            defaultImg.alt = "No Image Available";
            defaultImg.style.height = "150px";
            // defaultImg.className = 'img-fluid';
            // defaultImg.style.border = '1px solid #ccc';
            defaultImg.className = "img-fluid mx-1";
            defaultImg.style.width = "100%";
            defaultImg.style.minWidth = "100%";
            defaultImg.style.objectFit = "cover";
            container.appendChild(defaultImg);
          }
        });

        map.on("click", () => {
          const panel = document.getElementById("shop-details");
          panel.classList.remove("show");
        });
      }
    });
  });
