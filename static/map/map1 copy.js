(g => {
        var h, a, k, p = "The Google Maps JavaScript API",
            c = "google", l = "importLibrary", q = "__ib__",
            m = document, b = window; b = b[c] || (b[c] = {});
        var d = b.maps || (b.maps = {}), r = new Set,
            e = new URLSearchParams, u = () => h || (h = new Promise(async (f, n) => {
                await (a = m.createElement("script"));
                e.set("libraries", [...r] + "");
                for (k in g) e.set(k.replace(/[A-Z]/g, t => "_" + t[0].toLowerCase()), g[k]);
                e.set("callback", c + ".maps." + q);
                a.src = `https://maps.${c}apis.com/maps/api/js?` + e;
                d[q] = f; a.onerror = () => h = n(Error(p + " could not load."));
                a.nonce = m.querySelector("script[nonce]")?.nonce || "";
                m.head.append(a)
            }));
        d[l] ? console.warn(p + " only loads once. Ignoring:", g) : d[l] = (f, ...n) => r.add(f) && u().then(() => d[l](f, ...n))
    })({
        key: "{{ google_maps_key }}",
        v: "weekly",
        // Add libraries you need here:
        libraries: "marker"
    });

   let map;

async function initMap() {
  const position = STATIC_URLS.default_position || { lat: -8.552320, lng: 125.541782 };
  const { Map } = await google.maps.importLibrary("maps");
  const { AdvancedMarkerElement } = await google.maps.importLibrary("marker");

  map = new Map(document.getElementById("map"), {
    zoom: 10,
    center: position,
  });

  // Now that map is ready, call supporting functions
  fetchAndDisplayShops();
  map.addListener("zoom_changed", updateVisibleMarkers);
  map.addListener("dragend", updateVisibleMarkers);
}


    function fetchAndDisplayShops(municipalityId = "", autoOpenPanel = false) {
  const url = municipalityId
    ? `/api/shops/?municipality_id=${municipalityId}`
    : `/api/shops/`;

  fetch(url)
    .then((res) => res.json())
    .then((shops) => {
      allMarkers = [];
      activeMarkers.forEach((m) => m.setMap(null));
      activeMarkers = [];

      shops.forEach((shop) => {
        if (shop.latitude && shop.longitude) {
          const marker = new google.maps.Marker({
            position: { lat: parseFloat(shop.latitude), lng: parseFloat(shop.longitude) },
            map: null,
            icon: customIcon,
            title: shop.name,
          });
          marker.shop = shop;
          allMarkers.push(marker);

          marker.addListener("click", () => showShopDetail(shop));
        }
      });

      updateVisibleMarkers();
      updateShopList(shops);

      if (autoOpenPanel) {
        shopListPanel.classList.add("show");
        toggleBtn.textContent = "Hide List";
      }
    });
}