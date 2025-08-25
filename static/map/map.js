// var map = L.map('map').setView([-8.5586, 125.5736], 13);

// map tipe
var osm = L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
  attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
  maxZoom: 19,
  // attribution: "© OpenStreetMap",
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
  iconUrl: STATIC_URLS.kioskIcon,
  iconSize: [32, 32],
  iconAnchor: [16, 32],
  popupAnchor: [0, -32],
});
var markerLG = L.icon({
  iconUrl: STATIC_URLS.markerLG,
  iconSize: [20, 30],
  iconAnchor: [10, 30],
  popupAnchor: [0, -30],
});
var markerSM = L.icon({
  iconUrl: STATIC_URLS.markerSM,
  iconSize: [20, 30],
  iconAnchor: [10, 30],
  popupAnchor: [0, -30],
});
var markerNa = L.icon({
  iconUrl: STATIC_URLS.markerNA,
  iconSize: [20, 30],
  iconAnchor: [10, 30],
  popupAnchor: [0, -30],
});

const iconMarker = {
  "Big banner with frame": markerLG,
  "Small Banner": markerSM,
};

let allMarkers = [];
let activeMarkers = [];

const pixelThreshold = 50;

const toggleBtn = document.getElementById("toggle-shop-list");
const shopListPanel = document.getElementById("shop-list-panel");
const closeShopListBtn = document.getElementById("close-shop-list");

toggleBtn.addEventListener("click", () => {
  const isVisible = shopListPanel.classList.contains("show");
  shopListPanel.classList.toggle("show");
  toggleBtn.textContent = isVisible ? "Show List" : "Hide List";
});

closeShopListBtn.addEventListener("click", () => {
  shopListPanel.classList.remove("show");
  toggleBtn.textContent = "Show List";
});

function fetchAndDisplayShops(
  municipalityId = "",
  kindOfBanner = "",
  autoOpenPanel = false
) {
  // const url = municipalityId
  //   ? `/api/shops/?municipality_id=${municipalityId}`
  //   : `/api/shops/`;
  const params = new URLSearchParams();
  if (municipalityId) params.append("municipality_id", municipalityId);
  if (kindOfBanner) params.append("kind_of_banner", kindOfBanner);
  const url = `/api/shops/?${params.toString()}`;

  fetch(url)
    .then((res) => res.json())
    .then((shops) => {
      // Clear existing marker arrays
      allMarkers = [];
      activeMarkers.forEach((m) => map.removeLayer(m));
      activeMarkers = [];

      // Add new markers
      shops.forEach((shop) => {
        if (shop.latitude && shop.longitude) {
          const marker = L.marker([shop.latitude, shop.longitude], {
            icon: iconMarker[shop.kind_of_banner] || markerNa,
          });
          marker.shop = shop;

          marker.bindTooltip(shop.name || "Unnamed Shop", {
            permanent: false,
            direction: "top",
            offset: [0, -10],
            opacity: 0.9,
          });

          allMarkers.push(marker);
          marker.on("click", () => showShopDetail(shop));
        }
      });

      updateVisibleMarkers();
      updateShopList(shops);
      // updateLegend(shops);
      if (autoOpenPanel) {
        shopListPanel.classList.add("show");
        toggleBtn.textContent = "Hide List";
      }
      map.on("zoomend moveend", updateVisibleMarkers);
    });
}

function updateVisibleMarkers() {
  // Remove current
  activeMarkers.forEach((m) => map.removeLayer(m));
  activeMarkers = [];

  const projected = allMarkers.map((m) => {
    const latlng = m.getLatLng();
    return {
      marker: m,
      point: map.latLngToContainerPoint(latlng),
    };
  });

  const shown = [];

  projected.forEach(({ marker, point }) => {
    const isTooClose = shown.some(({ point: other }) => {
      return point.distanceTo(other) < pixelThreshold;
    });

    if (!isTooClose) {
      shown.push({ marker, point });
    }
  });

  shown.forEach(({ marker }) => {
    marker.addTo(map);
    activeMarkers.push(marker);
  });
}

function showShopDetail(shop) {
  document.getElementById("shop-details").style.display = "block";
  const panel = document.getElementById("shop-details");
  panel.classList.add("show");

  const locationParts = [
    shop.municipality || "",
    shop.administrativepost || "",
    shop.village || "",
    shop.aldeia || "",
  ]
    .filter(Boolean)
    .join(", ");

  document.getElementById("detail-name-title").textContent =
    shop.name || "Shop Information";
  document.getElementById("detail-owner").textContent = shop.owner || "---";
  document.getElementById("detail-contact").textContent = shop.contact || "---";
  document.getElementById("detail-center").textContent = shop.center || "---";
  document.getElementById("detail-location").textContent =
    locationParts || "---";
  document.getElementById(
    "detail-gmaps"
  ).href = `https://maps.google.com/?q=${shop.latitude},${shop.longitude}`;
  document.getElementById("kind-banner-display").textContent = shop.kind_of_banner || "---";

  document.getElementById("dimension-banner").textContent =
    shop.dimension || "---";
  document.getElementById("kind-channel").textContent =
    shop.kind_of_channel || "---";
  document.getElementById("latitude").textContent = shop.latitude || "---";
  document.getElementById("longitude").textContent = shop.longitude || "---";

  // const container = document.getElementById("shop-images");
  const container = document.getElementById("shop-carousel-inner");

  // container.className = "image-scroll";
  container.innerHTML = "";
  const panelCount = document.getElementById("image-count-panel");
  const panelTypeCount = document.getElementById("image-type");
  const panelTimeCount = document.getElementById("image-time");
  if (shop.images && shop.images.length > 0) {
    shop.images.forEach((img, index) => {
      const carouselItem = document.createElement("div");
      carouselItem.className = "carousel-item" + (index === 0 ? " active" : "");

      const imgEl = document.createElement("img");
      imgEl.src = img.url;
      // imgEl.className = "img-fluid mx-1";
      imgEl.className = "d-block w-100";
      imgEl.style.height = "150px";
      imgEl.style.width = "100%";
      imgEl.style.objectFit = "cover";
      // imgEl.style.scrollSnapAlign = "center";
      imgEl.alt = shop.name + " image" || "Shop image";
      imgEl.addEventListener("click", () => {
        openImageModal(shop.images, index); // Pass all images and current index
      });
      // panelCount.textContent = `${shop.images.index + 1} of ${shop.images.length} image${shop.images.length > 1 ? "s" : ""}`;
      carouselItem.appendChild(imgEl);
      container.appendChild(carouselItem);
    });
    // Set initial image count and type
    panelCount.textContent = `1 of ${shop.images.length} image${
      shop.images.length > 1 ? "s" : ""
    }`;
    panelTypeCount.textContent = shop.images[0].image_type ? `${shop.images[0].image_type} Image` : "";

    const dt = new Date(shop.images[0].update_time);
    const formattedDate = `Last updated on ${String(dt.getDate()).padStart(2, '0')}-${String(dt.getMonth() + 1).padStart(2, '0')}-${dt.getFullYear()} ${String(dt.getHours()).padStart(2, '0')}:${String(dt.getMinutes()).padStart(2, '0')}`;
    panelTimeCount.textContent = shop.images[0].update_time
      ? formattedDate
      : "";

    const shopCarousel = document.getElementById("shopCarousel");
    shopCarousel.addEventListener("slid.bs.carousel", function (event) {
      const currentIndex = event.to + 1;
      const total = shop.images.length;
      const currentImage = shop.images[event.to];
      panelCount.textContent = `${currentIndex} of ${total} image${
        total > 1 ? "s" : ""
      }`;
      panelTypeCount.textContent = currentImage.image_type ? `${currentImage.image_type} Image` : "";
      const dt = new Date(currentImage.update_time);
      const formattedDate = `Last updated on ${String(dt.getDate()).padStart(2, '0')}-${String(dt.getMonth() + 1).padStart(2, '0')}-${dt.getFullYear()} ${String(dt.getHours()).padStart(2, '0')}:${String(dt.getMinutes()).padStart(2, '0')}`;
      panelTimeCount.textContent = currentImage.update_time
        ? formattedDate
        : "";
    });
  } else {
    container.innerHTML = `
    <div class="carousel-item active">
      <img src="${STATIC_URLS.defaultImage}" class="d-block w-100" style="height: 150px; object-fit: cover;" alt="No Image">
    </div>
  `;

    panelCount.textContent = `0 image`;
    panelTypeCount.textContent = "";
    panelTimeCount.textContent = "";
  }
}

function updateShopList(shops) {
  const shopList = document.getElementById("shop-list");
  shopList.innerHTML = "";

  if (shops.length === 0) {
    shopList.innerHTML = "<li class='list-group-item'>No shops found.</li>";
    return;
  }

  shops.forEach((shop) => {
    const item = document.createElement("li");
    item.className = "list-group-item list-group-item-action";
    item.textContent = shop.name;
    item.dataset.name = shop.name.toLowerCase();
    item.style.cursor = "pointer";
    item.onclick = () => {
      map.setView([shop.latitude, shop.longitude], 17);
      showShopDetail(shop);
    };
    shopList.appendChild(item);
  });
}

map.on("click", () => {
  document.getElementById("shop-details").classList.remove("show");
});
// function showShopDetail(shop) {
//   const panel = document.getElementById("shop-details");
//   panel.style.display = "block";
// }

const bannerMap = {
  big_banner_frame: "Big banner with frame",
  small_banner: "Small Banner",
  no_info: "No banner information",
};

document
  .getElementById("shop-filter-form")
  .addEventListener("submit", function (e) {
    e.preventDefault();
    const municipalityId = document.getElementById("shop-filter").value;
    const kindOfBannerRaw = document.getElementById("kind-banner").value;
    const kindOfBanner = bannerMap[kindOfBannerRaw] || "";
    fetchAndDisplayShops(municipalityId, kindOfBanner, true);
  });

// Load all on page load
document.addEventListener("DOMContentLoaded", () => {
  fetchAndDisplayShops();
  const searchInput = document.getElementById("shop-search-input");

  searchInput.addEventListener("input", (e) => {
    const query = e.target.value.toLowerCase();
    const items = document.querySelectorAll("#shop-list li"); // Updated selector

    items.forEach((item) => {
      const name = item.dataset.name;
      item.style.display = name.includes(query) ? "" : "none";
    });
  });
});
